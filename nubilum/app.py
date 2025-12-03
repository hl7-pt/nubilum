"""Flask application for Nubilum HL7 anonymization service."""

import logging
import os
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
from flask_babel import Babel, gettext, lazy_gettext
from nubilum.anonymizer import HL7Anonymizer
from nubilum.usage_tracker import UsageTracker
from nubilum import __version__

# Alias for translation functions
_ = gettext
_l = lazy_gettext

# Configure logging
log_dir = os.environ.get('NUBILUM_LOG_DIR', '/var/log/nubilum')
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, f'nubilum_{datetime.now().strftime("%Y%m%d")}.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# Configure Flask
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # 1MB max message size
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Configure Babel for internationalization
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_SUPPORTED_LOCALES'] = ['en', 'pt']

babel = Babel(app)


def get_locale():
    """Determine the best locale for the user."""
    # 1. Try to get language from session
    if 'language' in session:
        return session['language']

    # 2. Try to get language from URL parameter
    lang = request.args.get('lang')
    if lang in app.config['BABEL_SUPPORTED_LOCALES']:
        session['language'] = lang
        return lang

    # 3. Try to get language from request headers (browser preference)
    return request.accept_languages.best_match(app.config['BABEL_SUPPORTED_LOCALES'])


babel.init_app(app, locale_selector=get_locale)

# Initialize usage tracker
usage_log_file = os.path.join(log_dir, 'usage_log.jsonl')
usage_tracker = UsageTracker(usage_log_file)


def split_messages(text: str) -> list:
    """
    Split input text into individual HL7 messages.
    Messages are separated by blank lines or multiple MSH segments.
    """
    messages = []
    current_message = []

    lines = text.split('\n')

    for line in lines:
        stripped = line.strip()

        # If we encounter a new MSH and we already have content, save the current message
        if stripped.startswith('MSH|') and current_message:
            messages.append('\n'.join(current_message))
            current_message = [line]
        # If line is not empty, add to current message
        elif stripped:
            current_message.append(line)
        # If line is empty and we have content, it might be a message separator
        elif not stripped and current_message:
            # Check if next non-empty line is MSH (message separator)
            # For now, just continue building the message
            pass

    # Add the last message
    if current_message:
        messages.append('\n'.join(current_message))

    return messages


@app.route('/')
def index():
    """Serve the main application page."""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'version': __version__,
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/api/version', methods=['GET'])
def version():
    """Return application version."""
    return jsonify({
        'version': __version__,
        'name': 'Nubilum'
    })


@app.route('/api/language', methods=['GET', 'POST'])
def language():
    """Get or set the current language."""
    if request.method == 'POST':
        data = request.get_json()
        lang = data.get('language')

        if lang not in app.config['BABEL_SUPPORTED_LOCALES']:
            return jsonify({
                'success': False,
                'error': _('Language not supported')
            }), 400

        session['language'] = lang
        return jsonify({
            'success': True,
            'language': lang
        })
    else:
        current_lang = get_locale()
        return jsonify({
            'language': current_lang,
            'supported_languages': app.config['BABEL_SUPPORTED_LOCALES']
        })


@app.route('/api/usage/statistics', methods=['GET'])
def usage_statistics():
    """
    Get usage statistics.

    Query parameters:
    - days: Number of days to look back (optional, default: all time)

    Returns statistics about anonymization usage.
    """
    try:
        days = request.args.get('days', type=int)

        stats = usage_tracker.get_statistics(days=days)

        return jsonify({
            'success': True,
            'statistics': stats,
            'period': f'last {days} days' if days else 'all time'
        })

    except Exception as e:
        logger.error(f"Error getting usage statistics: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve statistics: {str(e)}'
        }), 500


@app.route('/api/validate', methods=['POST'])
def validate():
    """
    Validate one or more HL7 messages using HL7 Portugal validator API.

    Expected JSON payload:
    {
        "message": "MSH|^~\\&|..."
    }

    Returns:
    {
        "success": true,
        "validator_url": "https://version2.hl7.pt/",
        "results": [
            {
                "message_number": 1,
                "valid": true/false,
                "message": "validation message",
                "details": {...}
            },
            ...
        ]
    }
    """
    try:
        import requests

        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': _('No data provided')
            }), 400

        input_text = data.get('message', '')

        if not input_text or input_text.strip() == '':
            return jsonify({
                'success': False,
                'error': _('Message is required')
            }), 400

        # Split into individual messages
        messages = split_messages(input_text)

        if not messages:
            return jsonify({
                'success': False,
                'error': _('No valid messages found')
            }), 400

        logger.info(f"Validating {len(messages)} message(s)")

        validator_url = 'https://version2.hl7.pt/api/hl7/v1/validate/'
        results = []

        for idx, message in enumerate(messages, 1):
            try:
                response = requests.post(
                    validator_url,
                    json={'data': message},
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )

                if response.status_code == 200:
                    validation_result = response.json()
                    status_code = validation_result.get('statusCode', '')
                    is_valid = status_code.lower() == 'ok' or status_code.lower() == 'success'

                    results.append({
                        'message_number': idx,
                        'valid': is_valid,
                        'message': validation_result.get('message', ''),
                        'details': validation_result
                    })
                    logger.info(f"Message {idx} validation: {is_valid}")
                else:
                    results.append({
                        'message_number': idx,
                        'valid': False,
                        'message': f'Validator returned status code {response.status_code}',
                        'details': None
                    })
                    logger.error(f"Message {idx} validator error: {response.status_code}")

            except requests.Timeout:
                results.append({
                    'message_number': idx,
                    'valid': False,
                    'message': 'Validation service timeout',
                    'details': None
                })
                logger.error(f"Message {idx} validation timeout")

            except requests.RequestException as e:
                results.append({
                    'message_number': idx,
                    'valid': False,
                    'message': f'Failed to connect to validation service: {str(e)}',
                    'details': None
                })
                logger.error(f"Message {idx} validation error: {str(e)}")

        return jsonify({
            'success': True,
            'validator_url': 'https://version2.hl7.pt/',
            'message_count': len(messages),
            'results': results
        })

    except Exception as e:
        logger.error(f"Error during validation: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Validation failed: {str(e)}'
        }), 500


@app.route('/api/field-name', methods=['GET'])
def field_name():
    """
    Get the name of a specific HL7 field.

    Query parameters:
    - segment: Segment type (e.g., 'PID', 'MSH')
    - field: Field index (0-based)
    - version: HL7 version (optional, defaults to '2.5')

    Returns the human-readable field name.
    """
    try:
        from hl7apy.core import Field

        segment_type = request.args.get('segment', '').upper()
        field_index = request.args.get('field', type=int)
        hl7_version = request.args.get('version', '2.5')

        # Normalize version format for hl7apy (e.g., "2.5" or "2.5.1")
        if hl7_version:
            hl7_version = hl7_version.strip()

        if not segment_type or field_index is None:
            return jsonify({
                'success': False,
                'error': _('Both segment and field parameters are required')
            }), 400

        # HL7 field numbering is special for MSH
        # In the message: MSH|^~\&|SendApp|SendFac|...
        # After split by |: [0]=MSH, [1]=^~\&, [2]=SendApp, [3]=SendFac, ...
        # But in HL7 spec: MSH-1=|, MSH-2=^~\&, MSH-3=SendApp, MSH-4=SendFac, ...
        # So field_index 0 = MSH-0 (segment ID), field_index 1 = MSH-2, field_index 2 = MSH-3, etc.

        if segment_type == 'MSH':
            if field_index == 0:
                return jsonify({
                    'success': True,
                    'field_name': 'Segment ID',
                    'segment': segment_type,
                    'field_index': field_index,
                    'version': hl7_version
                })
            elif field_index == 1:
                # This is the encoding characters field (MSH-2 in HL7 spec)
                return jsonify({
                    'success': True,
                    'field_name': 'Encoding Characters',
                    'segment': segment_type,
                    'field_index': field_index,
                    'version': hl7_version
                })
            else:
                # For MSH fields after encoding chars, add 1 to the index
                # field_index 2 -> MSH-3, field_index 3 -> MSH-4, etc.
                hl7apy_index = field_index + 1
        else:
            # For other segments, field 0 is segment ID
            if field_index == 0:
                return jsonify({
                    'success': True,
                    'field_name': 'Segment ID',
                    'segment': segment_type,
                    'field_index': field_index,
                    'version': hl7_version
                })
            hl7apy_index = field_index

        try:
            # Try to get field information from hl7apy with specified version
            field = Field(f'{segment_type}_{hl7apy_index}', version=hl7_version)
            field_name = field.long_name.replace('_', ' ').title()

            return jsonify({
                'success': True,
                'field_name': field_name,
                'segment': segment_type,
                'field_index': field_index,
                'version': hl7_version
            })

        except Exception as field_error:
            # If field is not found or version not supported, try default version
            try:
                field = Field(f'{segment_type}_{hl7apy_index}', version='2.5')
                field_name = field.long_name.replace('_', ' ').title()

                return jsonify({
                    'success': True,
                    'field_name': field_name,
                    'segment': segment_type,
                    'field_index': field_index,
                    'version': '2.5',
                    'note': f'Using v2.5 definitions (v{hl7_version} not available)'
                })
            except:
                # If still fails, return a generic name
                return jsonify({
                    'success': True,
                    'field_name': f'{segment_type}-{field_index}',
                    'segment': segment_type,
                    'field_index': field_index,
                    'version': hl7_version,
                    'note': 'Field definition not found'
                })

    except Exception as e:
        logger.error(f"Error getting field name: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Failed to get field name: {str(e)}'
        }), 500


@app.route('/api/anonymize', methods=['POST'])
def anonymize():
    """
    Anonymize one or more HL7 messages.

    Expected JSON payload:
    {
        "message": "MSH|^~\\&|..."
    }

    Returns:
    {
        "success": true,
        "anonymized_message": "MSH|^~\\&|...",
        "message_count": 2
    }
    """
    try:
        data = request.get_json()

        if not data:
            logger.warning("No JSON data provided")
            return jsonify({
                'success': False,
                'error': _('No data provided')
            }), 400

        input_text = data.get('message', '')

        if not input_text or input_text.strip() == '':
            logger.warning("Empty message provided")
            return jsonify({
                'success': False,
                'error': _('Message is required')
            }), 400

        # Split into individual messages
        messages = split_messages(input_text)

        if not messages:
            return jsonify({
                'success': False,
                'error': _('No valid messages found')
            }), 400

        logger.info(f"Received {len(messages)} message(s) for anonymization")

        # Create anonymizer instance
        anonymizer = HL7Anonymizer()
        anonymized_messages = []

        for idx, message in enumerate(messages, 1):
            try:
                # Anonymize the message
                anonymized = anonymizer.anonymize_message(message)
                anonymized_messages.append(anonymized)

                logger.info(f"Message {idx} anonymized successfully")

                # Track successful anonymization
                usage_tracker.track_anonymization(message, success=True)

            except Exception as anon_error:
                # Track failed anonymization
                usage_tracker.track_anonymization(message, success=False, error=str(anon_error))
                logger.error(f"Message {idx} anonymization failed: {str(anon_error)}")
                raise

        # Join all anonymized messages with double newline
        combined_output = '\n\n'.join(anonymized_messages)

        logger.info(f"All {len(messages)} message(s) anonymized successfully")

        return jsonify({
            'success': True,
            'anonymized_message': combined_output,
            'message_count': len(messages)
        })

    except Exception as e:
        logger.error(f"Error during anonymization: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'Anonymization failed: {str(e)}'
        }), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large errors."""
    logger.warning("Message too large")
    return jsonify({
        'success': False,
        'error': _('Message too large. Maximum size is 1MB.')
    }), 413


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'success': False,
        'error': _('Endpoint not found')
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors."""
    logger.error(f"Internal server error: {str(error)}", exc_info=True)
    return jsonify({
        'success': False,
        'error': _('Internal server error')
    }), 500


def create_app():
    """Application factory."""
    return app


if __name__ == '__main__':
    logger.info(f"Starting Nubilum v{__version__}")
    app.run(host='0.0.0.0', port=5000, debug=False)
