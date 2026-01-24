# Nubilum - Project Summary

## Overview

Nubilum is a production-ready HL7 v2 message anonymization tool built for HL7 Portugal. It provides a web-based interface for anonymizing patient identifiable information in HL7 messages while preserving message structure and clinical context.

## Project Structure

```
nubilum/
├── nubilum/                    # Main Python package
│   ├── __init__.py            # Package initialization (version: 1.0.0)
│   ├── app.py                 # Flask application with API endpoints
│   ├── anonymizer.py          # HL7 anonymization engine
│   ├── static/                # Frontend static files
│   │   ├── index.html         # Main HTML page
│   │   ├── app.jsx            # React application
│   │   ├── styles.css         # CSS styling
│   │   └── hl7pt_logo.png     # HL7 Portugal logo (placeholder)
│   └── templates/             # Flask templates (currently empty)
├── docker/                     # Docker configuration files
│   ├── nginx.conf             # Nginx reverse proxy config
│   └── supervisord.conf       # Supervisor process manager config
├── Dockerfile                  # Multi-stage Docker build
├── docker-compose.yml          # Docker Compose configuration
├── pyproject.toml             # Python project metadata and dependencies
├── setup.py                   # Setup script
├── MANIFEST.in                # Package manifest for wheel building
├── requirements.txt           # Python dependencies
├── build.sh                   # Build script for wheel generation
├── run_dev.sh                 # Development mode runner
├── README.md                  # Complete documentation
├── QUICKSTART.md              # Quick start guide
├── LICENSE                    # MIT License
└── .gitignore / .dockerignore # Ignore files
```

## Technology Stack

### Backend
- **Python 3.11**: Core programming language
- **Flask**: Web framework
- **Flask-CORS**: Cross-origin resource sharing
- **hl7apy**: HL7 message parsing library
- **Gunicorn**: WSGI HTTP server

### Frontend
- **React 18**: UI framework (via CDN)
- **Babel Standalone**: JSX transformation
- **Vanilla CSS**: Styling with gradients and animations

### Infrastructure
- **Nginx**: Reverse proxy and static file serving
- **Supervisor**: Process management
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration

## Key Features

### 1. Comprehensive Anonymization

The anonymizer handles multiple HL7 segments:

- **PID**: Patient Identification (primary target)
  - Patient ID, names, DOB, addresses, phone numbers, SSN, account numbers
- **NK1**: Next of Kin information
- **PV1/PV2**: Patient Visit data (doctors, visit numbers, additional info)
- **PD1**: Patient Demographics
- **ORC/OBR**: Order segments (order numbers, providers)
- **OBX**: Observation results (observers)
- **SCH**: Scheduling Activity Information (appointment IDs, placer contacts)
- **AIG/AIL/AIP**: Appointment resources (personnel, locations)
- **TXA**: Transcription Document Header (document creators, authenticators, transcriptionists)
- **IN1/IN2/IN3**: Insurance Information
- **GT1**: Guarantor Information
- **ROL**: Role Information
- **CTI**: Clinical Trial Identification
- **DG1**: Diagnosis Information
- **PR1**: Procedures
- **EVN**: Generic user/operator fields

### 2. Smart Pseudo-Generation

- **Deterministic hashing**: Same input always generates same output
- **Purpose-indicating names**: Generated names indicate field purpose
  - Patient names: "Doe42", "John37"
  - Doctor names: "DrSmith23"
  - IDs: "PID######", "ACCT######", "VISIT######"
- **Format preservation**: Maintains HL7 composite field structure (^-separated)

### 3. User-Friendly Interface

- **Color-coded segments**: Each segment type has a distinct color
- **Field name tooltips**: Hover over any field to see its HL7 standard name (version-aware)
- **Multi-message support**: Process multiple HL7 messages in a single request
- **Message validation**: Validate messages using HL7 Portugal validator API
- **Collapsible validation badges**: Red/green indicators with expandable details
- **Inline editing**: Click any field to edit it
- **Copy to clipboard**: One-click copying of anonymized messages
- **Character counter**: Shows message length
- **Example loader**: Built-in example messages
- **Clear all**: Quick reset of input and output

### 4. Privacy & Security

- **No data persistence**: Messages never stored
- **No external connections**: Fully offline operation
- **Audit logging**: All requests logged (without message content)
- **Size limits**: 1MB maximum to prevent abuse
- **Disclaimer**: Clear privacy notice displayed

### 5. Production-Ready Deployment

- **Multi-stage Docker build**: Optimized image size
- **Nginx reverse proxy**: Efficient static file serving
- **Supervisor**: Automatic process restart
- **Health checks**: Docker health monitoring
- **Logging**: Comprehensive file-based logging
- **Scalable**: Multiple Gunicorn workers

## API Endpoints

### GET /api/health
Health check endpoint returning status and version.

### GET /api/version
Returns application name and version.

### POST /api/anonymize
Anonymizes one or more HL7 messages (supports multiple messages).

**Request:**
```json
{
  "message": "MSH|^~\\&|..."
}
```

**Response:**
```json
{
  "success": true,
  "anonymized_message": "MSH|^~\\&|...",
  "message_count": 1
}
```

### POST /api/validate
Validates HL7 messages using HL7 Portugal validator API.

**Request:**
```json
{
  "message": "MSH|^~\\&|..."
}
```

**Response:**
```json
{
  "success": true,
  "validator_url": "https://version2.hl7.pt/",
  "message_count": 1,
  "results": [{"message_number": 1, "valid": true, "message": "...", "details": {...}}]
}
```

### GET /api/field-name
Returns the HL7 standard name for a specific field.

**Query Parameters:**
- `segment`: Segment type (e.g., "PID", "MSH")
- `field`: Field index (0-based)
- `version`: HL7 version (optional, defaults to "2.5")

**Response:**
```json
{
  "success": true,
  "field_name": "Patient Identifier List",
  "segment": "PID",
  "field_index": 3,
  "version": "2.5"
}
```

### GET /api/usage/statistics
Returns usage statistics for anonymization events.

**Query Parameters:**
- `days`: Number of days to look back (optional)

**Response:**
```json
{
  "success": true,
  "period": "last 7 days",
  "statistics": {
    "total_anonymizations": 145,
    "successful_anonymizations": 143,
    "success_rate": 98.62,
    "message_types": {...},
    "segments_processed": {...}
  }
}
```

## Build Process

### Wheel Package

```bash
./build.sh
# Generates: dist/nubilum-1.0.0-py3-none-any.whl
```

The wheel includes:
- Python package (nubilum)
- Static files (HTML, CSS, JS)
- Dependencies metadata

### Docker Image

```bash
docker build -t nubilum:1.0.0 .
```

Build process:
1. **Builder stage**: Builds wheel package
2. **Final stage**: Installs wheel, nginx, supervisor
3. **Configuration**: Copies nginx and supervisor configs
4. **Result**: ~200MB production-ready image

## Deployment Options

### 1. Docker Compose (Recommended)
```bash
docker-compose up -d
```
Access at: http://localhost:8080

### 2. Docker
```bash
docker run -d -p 8080:80 nubilum:1.0.0
```

### 3. Manual Installation
```bash
pip install dist/nubilum-1.0.0-py3-none-any.whl
gunicorn nubilum.app:app
```

### 4. Development Mode
```bash
./run_dev.sh
```
Access at: http://localhost:5000

## Configuration

### Environment Variables

- `NUBILUM_LOG_DIR`: Log directory path (default: `/var/log/nubilum`)

### Docker Volumes

- `/var/log/nubilum`: Application logs
- `/etc/nginx/sites-available/nubilum`: Nginx config override

### Flask Configuration

- `MAX_CONTENT_LENGTH`: 1MB
- `DEBUG`: False (production)

## Logging

Log files location: `$NUBILUM_LOG_DIR/`

- `nubilum_YYYYMMDD.log`: Application logs
- `access.log`: Gunicorn access logs
- `error.log`: Gunicorn error logs
- Nginx logs: `/var/log/nginx/`
- Supervisor logs: `/var/log/supervisor/`

## Testing

Example test messages included in README.md:
- ADT^A01: Admit/Discharge/Transfer
- ORM^O01: Order Message
- Various segment combinations

## Future Enhancements

Potential improvements:
- Unit tests with pytest
- Support for HL7 v2.x versions (2.3, 2.4, 2.5.1, 2.6, etc.)
- XML format support (HL7 v2 XML encoding)
- Batch message processing
- Custom anonymization rules
- API authentication
- Metrics and monitoring
- Multi-language support

## Dependencies

### Runtime
- flask>=3.0.0
- flask-cors>=4.0.0
- hl7apy>=1.3.4
- python-dateutil>=2.8.2
- gunicorn>=21.2.0
- requests>=2.31.0 (for validation API)

### Build
- setuptools>=65.0
- wheel
- build

### System (Docker)
- nginx
- supervisor
- curl (for health checks)

## Version Information

- **Current Version**: 1.0.0
- **Python Version**: 3.9+
- **HL7 Support**: v2.x (ER7 format)
- **License**: MIT

## Important Notes

1. **Logo Placeholder**: Replace `nubilum/static/hl7pt_logo.png` with actual HL7 Portugal logo
2. **No Data Storage**: Application is stateless - no database required
3. **Authorization**: Users must have proper authorization to process PHI
4. **Format Support**: Only ER7 format supported (pipe-delimited)
5. **Production Use**: Review security settings before production deployment

## Support

For issues, questions, or contributions:
- Documentation: See README.md
- Quick Start: See QUICKSTART.md
- HL7 Portugal: https://hl7.pt

---

**Built with ❤️ for HL7 Portugal**
**Version 1.0.0 - January 2025**
