# Internationalization (i18n) Guide for Nubilum

This document describes the internationalization implementation in Nubilum, following the same approach as the [hl7v2validator-hl7pt](https://github.com/hl7-pt/hl7v2validator-hl7pt) project.

## Overview

Nubilum supports multiple languages using:
- **Backend**: Flask-Babel for Python/Flask internationalization
- **Frontend**: Custom JavaScript i18n implementation for React components
- **Supported Languages**: English (en) and Portuguese (pt)

## Architecture

### Backend (Flask-Babel)

The backend uses Flask-Babel to translate server-side messages and API responses.

#### Configuration

In `nubilum/app.py`:
```python
from flask_babel import Babel, gettext, lazy_gettext

# Alias for translation functions
_ = gettext
_l = lazy_gettext

# Configure Babel
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
```

#### Translation Markers

Wrap translatable strings with `_()` or `_l()`:
```python
# For immediate translation
error_message = _('Message is required')

# For lazy translation (e.g., in class definitions)
field_label = _l('Input Message')
```

### Frontend (JavaScript/React)

The frontend uses a custom i18n system defined in `nubilum/static/i18n.js`.

#### Translation Files

All translations are stored in `i18n.js`:
```javascript
const translations = {
    en: {
        appTitle: "Nubilum - HL7 Portugal Message Anonymizer",
        anonymize: "Anonymize",
        // ...
    },
    pt: {
        appTitle: "Nubilum - Anonimizador de Mensagens HL7 Portugal",
        anonymize: "Anonimizar",
        // ...
    }
};
```

#### Usage in React Components

```javascript
// Import the translation function
// t(key, lang) is available globally

function MyComponent() {
    const [currentLanguage, setCurrentLanguage] = useState(getCurrentLanguage());

    return (
        <div>
            <h1>{t('appTitle', currentLanguage)}</h1>
            <button>{t('anonymize', currentLanguage)}</button>
        </div>
    );
}
```

## Directory Structure

```
nubilum/
├── translations/              # Backend translations
│   ├── messages.pot          # Translation template
│   └── pt/                   # Portuguese translations
│       └── LC_MESSAGES/
│           ├── messages.po   # Translation source
│           └── messages.mo   # Compiled translations
├── static/
│   └── i18n.js              # Frontend translations
├── babel.cfg                # Babel extraction config
└── manage_translations.py   # Translation management script
```

## Language Detection

The application detects the user's preferred language in this order:

1. **User Selection**: Language chosen via the UI selector
2. **Session Storage**: Previously selected language (stored in Flask session)
3. **Local Storage**: Browser localStorage (frontend only)
4. **Browser Language**: Accept-Language header
5. **Default**: English (en)

## Translation Management

### Using the Management Script

The `manage_translations.py` script provides commands for managing translations:

#### Extract Translatable Strings
```bash
python manage_translations.py extract
```

#### Initialize a New Language
```bash
python manage_translations.py init <language_code>
# Example: python manage_translations.py init es
```

#### Update Existing Translations
```bash
python manage_translations.py update
```

#### Compile Translations
```bash
python manage_translations.py compile
```

### Manual Commands

You can also use pybabel directly:

#### Extract strings from source code
```bash
pybabel extract -F babel.cfg -k _ -k _l -o nubilum/translations/messages.pot .
```

#### Initialize a new language
```bash
pybabel init -i nubilum/translations/messages.pot -d nubilum/translations -l pt
```

#### Update existing translations
```bash
pybabel update -i nubilum/translations/messages.pot -d nubilum/translations -l pt
```

#### Compile translations
```bash
pybabel compile -d nubilum/translations
```

## Adding a New Language

### Backend

1. **Initialize the language**:
   ```bash
   python manage_translations.py init <lang_code>
   ```

2. **Edit the translation file**:
   Open `nubilum/translations/<lang_code>/LC_MESSAGES/messages.po` and add translations:
   ```po
   #: nubilum/app.py:140
   msgid "Language not supported"
   msgstr "Idioma no compatible"  # Add your translation here
   ```

3. **Compile translations**:
   ```bash
   python manage_translations.py compile
   ```

4. **Update app configuration**:
   Add the language code to `BABEL_SUPPORTED_LOCALES` in `nubilum/app.py`:
   ```python
   app.config['BABEL_SUPPORTED_LOCALES'] = ['en', 'pt', 'es']  # Add 'es'
   ```

### Frontend

1. **Add translations to `i18n.js`**:
   ```javascript
   const translations = {
       en: { /* ... */ },
       pt: { /* ... */ },
       es: {  // Add new language
           appTitle: "Nubilum - Anonimizador de Mensajes HL7 Portugal",
           anonymize: "Anonimizar",
           // ... add all keys
       }
   };
   ```

2. **Update language selector**:
   Add the language option in `app.jsx`:
   ```javascript
   const languages = [
       { code: 'en', name: t('english', currentLang), flag: '🇬🇧' },
       { code: 'pt', name: t('portuguese', currentLang), flag: '🇵🇹' },
       { code: 'es', name: t('spanish', currentLang), flag: '🇪🇸' }  // Add
   ];
   ```

## Workflow for Updating Translations

When you add new translatable strings to the code:

1. **Mark strings for translation**:
   - Backend: Wrap with `_()` or `_l()`
   - Frontend: Add to `i18n.js` translations object

2. **Extract strings** (backend only):
   ```bash
   python manage_translations.py extract
   ```

3. **Update catalogs**:
   ```bash
   python manage_translations.py update
   ```

4. **Edit translation files**:
   Open `nubilum/translations/<lang>/LC_MESSAGES/messages.po` and add translations

5. **Compile translations**:
   ```bash
   python manage_translations.py compile
   ```

6. **Test in the application**:
   - Start the application
   - Switch languages using the selector
   - Verify all strings are translated

## API Endpoints

### Get Current Language
```http
GET /api/language
```

Response:
```json
{
    "language": "pt",
    "supported_languages": ["en", "pt"]
}
```

### Set Language
```http
POST /api/language
Content-Type: application/json

{
    "language": "pt"
}
```

Response:
```json
{
    "success": true,
    "language": "pt"
}
```

## Best Practices

1. **Always mark user-facing strings for translation**
   - Don't: `return "Error: Invalid message"`
   - Do: `return _("Error: Invalid message")`

2. **Use lazy translation for class-level strings**
   ```python
   class MyForm:
       label = _l('Field Label')  # Use _l() for lazy evaluation
   ```

3. **Avoid string concatenation**
   - Don't: `_("Hello") + " " + name`
   - Do: `_("Hello %(name)s") % {'name': name}`

4. **Keep translations consistent**
   - Use the same terminology across the application
   - Maintain a glossary for technical terms

5. **Test all languages**
   - Verify layout doesn't break with longer translations
   - Check for missing translations
   - Test language switching functionality

## Troubleshooting

### Translations not appearing

1. **Check if translations are compiled**:
   ```bash
   ls -la nubilum/translations/pt/LC_MESSAGES/messages.mo
   ```

2. **Verify Flask-Babel is installed**:
   ```bash
   pip show flask-babel
   ```

3. **Check locale detection**:
   Add logging to `get_locale()` function

### New strings not extracted

1. **Verify babel.cfg includes the file patterns**
2. **Check if strings are properly marked with `_()` or `_l()`**
3. **Run extract command with verbose output**

### Frontend translations not working

1. **Check if i18n.js is loaded before app.jsx**
2. **Verify translation keys exist in the translations object**
3. **Check browser console for errors**

## References

- [Flask-Babel Documentation](https://python-babel.github.io/flask-babel/)
- [Babel Documentation](http://babel.pocoo.org/)
- [hl7v2validator-hl7pt i18n implementation](https://github.com/hl7-pt/hl7v2validator-hl7pt)
