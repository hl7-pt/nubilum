const { useState, useEffect } = React;

// Cache for field names to avoid repeated API calls
const fieldNameCache = {};

// Language Selector Component - Simple button style matching hl7.pt
function LanguageSelector({ currentLang, onLanguageChange }) {
    const handleLanguageSelect = async (langCode) => {
        try {
            // Update backend session
            await fetch('/api/language', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ language: langCode })
            });

            // Store preference locally
            setStoredLanguage(langCode);

            // Update document language
            document.documentElement.lang = langCode;

            // Notify parent component
            onLanguageChange(langCode);
        } catch (error) {
            console.error('Failed to change language:', error);
        }
    };

    return (
        <div className="language-selector">
            <button
                className={`language-btn ${currentLang === 'en' ? 'active' : ''}`}
                onClick={() => handleLanguageSelect('en')}
                aria-label="English"
            >
                EN
            </button>
            <button
                className={`language-btn ${currentLang === 'pt' ? 'active' : ''}`}
                onClick={() => handleLanguageSelect('pt')}
                aria-label="Português"
            >
                PT
            </button>
        </div>
    );
}

// HL7 Message Display Component with inline editing
function HL7MessageDisplay({ message, originalMessage = '' }) {
    const [fieldNameTooltip, setFieldNameTooltip] = useState(null);
    const [tooltipPosition, setTooltipPosition] = useState({ x: 0, y: 0 });
    const [hl7Version, setHl7Version] = useState('2.5');

    // Extract HL7 version from MSH segment
    useEffect(() => {
        if (message && message.trim() !== '') {
            const lines = message.split('\n');
            const mshLine = lines.find(line => line.trim().startsWith('MSH|'));
            if (mshLine) {
                const fields = mshLine.split('|');
                // MSH-12 is the version ID (field index 11 in 0-based, but MSH is special)
                // In MSH: field[0]=MSH, field[1]=|, field[2]=^~\&, field[3]=sending app, ...
                // Version is typically in field[11] (MSH-12)
                if (fields.length > 11 && fields[11]) {
                    const versionField = fields[11].split('^')[0]; // Get first component
                    if (versionField) {
                        setHl7Version(versionField);
                    }
                }
            }
        }
    }, [message]);

    // Fetch field name from API
    const fetchFieldName = async (segmentType, fieldIndex) => {
        const cacheKey = `${segmentType}-${fieldIndex}-${hl7Version}`;

        // Check cache first
        if (fieldNameCache[cacheKey]) {
            return fieldNameCache[cacheKey];
        }

        try {
            const response = await fetch(`/api/field-name?segment=${segmentType}&field=${fieldIndex}&version=${encodeURIComponent(hl7Version)}`);
            const data = await response.json();

            if (data.success) {
                const displayName = `${segmentType}-${fieldIndex}: ${data.field_name}`;
                fieldNameCache[cacheKey] = displayName;
                return displayName;
            }
        } catch (error) {
            console.error('Error fetching field name:', error);
        }

        // Fallback
        const fallback = `${segmentType}-${fieldIndex}`;
        fieldNameCache[cacheKey] = fallback;
        return fallback;
    };

    // Handle mouse enter on field
    const handleFieldMouseEnter = async (e, segmentType, fieldIndex) => {
        const rect = e.currentTarget.getBoundingClientRect();
        const fieldName = await fetchFieldName(segmentType, fieldIndex);

        setFieldNameTooltip(fieldName);
        setTooltipPosition({
            x: rect.left + rect.width / 2,
            y: rect.top - 10
        });
    };

    // Handle mouse leave
    const handleFieldMouseLeave = () => {
        setFieldNameTooltip(null);
    };

    // Parse a message into a structured format for comparison
    const parseMessage = (msg) => {
        if (!msg || msg.trim() === '') return [];
        const lines = msg.split('\n').filter(line => line.trim() !== '');
        return lines.map(line => {
            const fields = line.split('|');
            return fields.map(field => field.split('^'));
        });
    };

    // Check if a component has changed by comparing with original
    const hasComponentChanged = (lineIndex, fieldIndex, compIndex, component) => {
        if (!originalMessage || originalMessage.trim() === '') return false;

        const originalParsed = parseMessage(originalMessage);

        if (lineIndex >= originalParsed.length) return false;
        if (fieldIndex >= originalParsed[lineIndex].length) return false;
        if (compIndex >= originalParsed[lineIndex][fieldIndex].length) return false;

        const originalComponent = originalParsed[lineIndex][fieldIndex][compIndex];
        return originalComponent !== component;
    };

    if (!message || message.trim() === '') {
        return (
            <div className="hl7-message" style={{ color: '#a0aec0', fontStyle: 'italic' }}>
                Anonymized message will appear here...
            </div>
        );
    }

    const lines = message.split('\n').filter(line => line.trim() !== '');

    return (
        <div className="hl7-message">
            {fieldNameTooltip && (
                <div
                    className="field-tooltip"
                    style={{
                        left: `${tooltipPosition.x}px`,
                        top: `${tooltipPosition.y}px`,
                        transform: 'translate(-50%, -100%)'
                    }}
                >
                    {fieldNameTooltip}
                </div>
            )}
            {lines.map((line, lineIndex) => {
                const fields = line.split('|');
                const segmentType = fields[0];
                const segmentClass = `hl7-segment hl7-segment-${segmentType.toLowerCase()}`;

                return (
                    <div key={lineIndex} className={segmentClass}>
                        {fields.map((field, fieldIndex) => (
                            <React.Fragment key={fieldIndex}>
                                {fieldIndex > 0 && (
                                    <span className="field-separator">|</span>
                                )}
                                <span
                                    className="hl7-field"
                                    onMouseEnter={(e) => handleFieldMouseEnter(e, segmentType, fieldIndex)}
                                    onMouseLeave={handleFieldMouseLeave}
                                >
                                    {field.split('^').map((component, compIndex) => {
                                        const componentChanged = hasComponentChanged(lineIndex, fieldIndex, compIndex, component);
                                        return (
                                            <React.Fragment key={compIndex}>
                                                {compIndex > 0 && (
                                                    <span className="component-separator">^</span>
                                                )}
                                                <span className={componentChanged ? 'hl7-field-anonymized' : ''}>
                                                    {component}
                                                </span>
                                            </React.Fragment>
                                        );
                                    })}
                                </span>
                            </React.Fragment>
                        ))}
                    </div>
                );
            })}
        </div>
    );
}

// Alert Component
function Alert({ type, message, onClose }) {
    useEffect(() => {
        const timer = setTimeout(() => {
            if (onClose) onClose();
        }, 5000);
        return () => clearTimeout(timer);
    }, [onClose]);

    return (
        <div className={`alert alert-${type}`}>
            <span>{type === 'success' ? '✓' : type === 'error' ? '✗' : 'ℹ'}</span>
            <span>{message}</span>
        </div>
    );
}

// Example Messages Modal Component
function ExampleModal({ isOpen, onClose, onSelect }) {
    if (!isOpen) return null;

    const handleSelect = (example) => {
        onSelect(example.message);
        onClose();
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h2>Select Example HL7 Message</h2>
                    <button className="modal-close" onClick={onClose}>×</button>
                </div>
                <div className="modal-body">
                    <div className="example-list">
                        {HL7_EXAMPLES.map((example) => (
                            <div
                                key={example.id}
                                className="example-item"
                                onClick={() => handleSelect(example)}
                            >
                                <div className="example-header">
                                    <span className="example-name">{example.name}</span>
                                    <span className="example-version">v{example.version}</span>
                                </div>
                                <div className="example-description">{example.description}</div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}

// Main App Component
function App() {
    const [inputMessage, setInputMessage] = useState('');
    const [outputMessage, setOutputMessage] = useState('');
    const [loading, setLoading] = useState(false);
    const [validating, setValidating] = useState(false);
    const [version, setVersion] = useState('');
    const [alert, setAlert] = useState(null);
    const [showExampleModal, setShowExampleModal] = useState(false);
    const [validationResult, setValidationResult] = useState(null);
    const [expandedValidations, setExpandedValidations] = useState({});
    const [currentLanguage, setCurrentLanguage] = useState(getCurrentLanguage());

    useEffect(() => {
        // Fetch version on load
        fetch('/api/version')
            .then(res => res.json())
            .then(data => setVersion(data.version))
            .catch(err => console.error('Failed to fetch version:', err));
    }, []);

    const handleAnonymize = async () => {
        if (!inputMessage.trim()) {
            setAlert({ type: 'error', message: t('enterMessageToAnonymize', currentLanguage) });
            return;
        }

        setLoading(true);
        setAlert(null);

        try {
            const response = await fetch('/api/anonymize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: inputMessage }),
            });

            const data = await response.json();

            if (data.success) {
                setOutputMessage(data.anonymized_message);
                const successMsg = data.message_count === 1
                    ? t('messageAnonymizedSuccess', currentLanguage)
                    : `${data.message_count} ${t('messagesAnonymizedSuccess', currentLanguage)}`;
                setAlert({ type: 'success', message: successMsg });
            } else {
                setAlert({ type: 'error', message: data.error || t('anonymizationFailed', currentLanguage) });
            }
        } catch (error) {
            setAlert({ type: 'error', message: t('failedToConnect', currentLanguage) });
        } finally {
            setLoading(false);
        }
    };

    const handleClear = () => {
        setInputMessage('');
        setOutputMessage('');
        setValidationResult(null);
        setExpandedValidations({});
        setAlert({ type: 'info', message: t('messagesCleared', currentLanguage) });
    };

    const handleCopy = async () => {
        if (!outputMessage) {
            setAlert({ type: 'error', message: t('noMessageToCopy', currentLanguage) });
            return;
        }

        try {
            await navigator.clipboard.writeText(outputMessage);
            setAlert({ type: 'success', message: t('copiedToClipboard', currentLanguage) });
        } catch (error) {
            setAlert({ type: 'error', message: t('failedToCopy', currentLanguage) });
        }
    };

    const handleLoadExample = () => {
        setShowExampleModal(true);
    };

    const handleSelectExample = (exampleMessage) => {
        setInputMessage(exampleMessage);
        setOutputMessage('');  // Clear previous output
        setValidationResult(null);  // Clear validation result
        setExpandedValidations({});  // Clear expanded state
        setAlert({ type: 'info', message: t('exampleMessageLoaded', currentLanguage) });
    };

    const toggleValidationExpand = (messageNumber) => {
        setExpandedValidations(prev => ({
            ...prev,
            [messageNumber]: !prev[messageNumber]
        }));
    };

    const handleValidate = async () => {
        if (!inputMessage.trim()) {
            setAlert({ type: 'error', message: t('enterMessageToValidate', currentLanguage) });
            return;
        }

        setValidating(true);
        setValidationResult(null);
        setAlert(null);

        try {
            const response = await fetch('/api/validate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: inputMessage }),
            });

            const data = await response.json();

            if (data.success) {
                setValidationResult({
                    validatorUrl: data.validator_url,
                    messageCount: data.message_count,
                    results: data.results
                });

                // Count valid and invalid messages
                const validCount = data.results.filter(r => r.valid).length;
                const invalidCount = data.results.length - validCount;

                if (invalidCount === 0) {
                    setAlert({
                        type: 'success',
                        message: data.message_count === 1
                            ? t('messageValidated', currentLanguage)
                            : `${data.message_count} ${t('messagesValidated', currentLanguage)}`
                    });
                } else {
                    setAlert({
                        type: 'error',
                        message: data.message_count === 1
                            ? t('messageFailedValidation', currentLanguage)
                            : `${invalidCount} ${t('messagesFailedValidation', currentLanguage)}`
                    });
                }
            } else {
                setAlert({ type: 'error', message: data.error || t('validationFailed', currentLanguage) });
            }
        } catch (error) {
            console.error('Validation error:', error);
            setAlert({ type: 'error', message: t('failedToValidate', currentLanguage) });
        } finally {
            setValidating(false);
        }
    };

    return (
        <div className="app-container">
            <ExampleModal
                isOpen={showExampleModal}
                onClose={() => setShowExampleModal(false)}
                onSelect={handleSelectExample}
            />

            <header className="header">
                <div className="header-left">
                    <img
                        src="hl7pt_logo.png"
                        alt="HL7 Portugal Logo"
                        className="logo"
                        onError={(e) => {
                            e.target.style.display = 'none';
                        }}
                    />
                    <div className="header-text">
                        <h1>Nubilum</h1>
                        <p>{t('appDescription', currentLanguage)}</p>
                    </div>
                </div>
                <div className="header-right">
                    <LanguageSelector
                        currentLang={currentLanguage}
                        onLanguageChange={setCurrentLanguage}
                    />
                    {version && <div className="version">v{version}</div>}
                </div>
            </header>

            <div className="disclaimer">
                <span className="disclaimer-icon">⚠️</span>
                <div className="disclaimer-content">
                    <h3>{t('privacyNotice', currentLanguage)}</h3>
                    <p>{t('privacyText', currentLanguage)}</p>
                </div>
            </div>

            {alert && (
                <Alert
                    type={alert.type}
                    message={alert.message}
                    onClose={() => setAlert(null)}
                />
            )}

            <div className="legend">
                <h3>{t('segmentColorLegend', currentLanguage)}</h3>
                <div className="legend-items">
                    <div className="legend-item">
                        <div className="legend-color" style={{ background: 'rgba(47, 90, 174, 0.12)' }}></div>
                        <span>MSH - Message Header</span>
                    </div>
                    <div className="legend-item">
                        <div className="legend-color" style={{ background: 'rgba(236, 34, 39, 0.12)' }}></div>
                        <span>PID - Patient Identification</span>
                    </div>
                    <div className="legend-item">
                        <div className="legend-color" style={{ background: 'rgba(148, 99, 174, 0.12)' }}></div>
                        <span>PV1 - Patient Visit</span>
                    </div>
                    <div className="legend-item">
                        <div className="legend-color" style={{ background: 'rgba(47, 90, 174, 0.18)' }}></div>
                        <span>OBR - Observation Request</span>
                    </div>
                    <div className="legend-item">
                        <div className="legend-color" style={{ background: 'rgba(148, 99, 174, 0.18)' }}></div>
                        <span>OBX - Observation Result</span>
                    </div>
                    <div className="legend-item">
                        <div className="legend-color" style={{ background: 'rgba(236, 34, 39, 0.18)' }}></div>
                        <span>NK1 - Next of Kin</span>
                    </div>
                </div>
            </div>

            <div className="main-content">
                <div className="panel">
                    <div className="panel-header">
                        <h2>{t('inputMessage', currentLanguage)}</h2>
                        <button
                            className="btn btn-secondary"
                            onClick={handleLoadExample}
                            style={{ padding: '6px 12px', fontSize: '13px' }}
                        >
                            {t('loadExample', currentLanguage)}
                        </button>
                    </div>
                    <div className="textarea-container">
                        <textarea
                            className="message-input"
                            value={inputMessage}
                            onChange={(e) => setInputMessage(e.target.value)}
                            placeholder={t('pasteMessage', currentLanguage)}
                        />
                        <div className="char-counter">{inputMessage.length} characters</div>
                    </div>
                    <div className="button-group">
                        <button
                            className="btn btn-validate"
                            onClick={handleValidate}
                            disabled={validating || !inputMessage.trim()}
                        >
                            {validating ? (
                                <>
                                    <div className="spinner"></div>
                                    <span>{t('processing', currentLanguage)}</span>
                                </>
                            ) : (
                                <>
                                    <span>✓</span>
                                    <span>{t('validateButton', currentLanguage)}</span>
                                </>
                            )}
                        </button>
                        <button
                            className="btn btn-primary"
                            onClick={handleAnonymize}
                            disabled={loading || !inputMessage.trim()}
                        >
                            {loading ? (
                                <>
                                    <div className="spinner"></div>
                                    <span>{t('processing', currentLanguage)}</span>
                                </>
                            ) : (
                                <>
                                    <span>🔒</span>
                                    <span>{t('anonymizeButton', currentLanguage)}</span>
                                </>
                            )}
                        </button>
                    </div>
                </div>

                {validationResult && (
                    <div className="validation-middle-panel">
                        {validationResult.results.map((result, idx) => {
                            const isValid = result.valid;
                            const isExpanded = expandedValidations[result.message_number];
                            const hasDetails = !isValid && result.details?.details && result.details.details.length > 0;

                            return (
                                <div key={idx} className="validation-badge-container">
                                    <div
                                        className={`validation-badge ${isValid ? 'validation-badge-success' : 'validation-badge-error'} ${hasDetails ? 'clickable' : ''}`}
                                        onClick={() => hasDetails && toggleValidationExpand(result.message_number)}
                                        title={hasDetails ? 'Click to view details' : result.message}
                                    >
                                        <div className="validation-badge-content">
                                            {validationResult.messageCount > 1 && (
                                                <span className="validation-badge-number">Msg {result.message_number}</span>
                                            )}
                                            <span className="validation-badge-icon">
                                                {isValid ? '✓' : '✗'}
                                            </span>
                                            <span className="validation-badge-text">
                                                {isValid ? t('valid', currentLanguage) : t('invalid', currentLanguage)}
                                            </span>
                                            {hasDetails && (
                                                <span className="validation-badge-arrow">
                                                    {isExpanded ? '▼' : '▶'}
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                    {hasDetails && isExpanded && (
                                        <div className="validation-details">
                                            <div className="validation-details-message">
                                                {result.message}
                                            </div>
                                            <div className="validation-errors">
                                                {result.details.details.slice(0, 5).map((detail, detailIdx) => (
                                                    <div key={detailIdx} className="validation-error-item">
                                                        <span className="validation-error-level">{detail.level}:</span>
                                                        <span>{detail.message}</span>
                                                    </div>
                                                ))}
                                                {result.details.details.length > 5 && (
                                                    <div className="validation-more">
                                                        +{result.details.details.length - 5} {t('moreErrors', currentLanguage)}
                                                    </div>
                                                )}
                                            </div>
                                            <a
                                                href={validationResult.validatorUrl}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="validation-details-link"
                                            >
                                                {t('viewFullDetails', currentLanguage)}
                                            </a>
                                        </div>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                )}

                <div className="panel">
                    <div className="panel-header">
                        <h2>{t('anonymizedOutput', currentLanguage)}</h2>
                    </div>
                    <HL7MessageDisplay
                        message={outputMessage}
                        originalMessage={inputMessage}
                    />
                    <div className="button-group">
                        <button
                            className="btn btn-copy"
                            onClick={handleCopy}
                            disabled={!outputMessage}
                        >
                            <span>📋</span>
                            <span>{t('copyToClipboard', currentLanguage)}</span>
                        </button>
                        <button
                            className="btn btn-clear"
                            onClick={handleClear}
                            disabled={!inputMessage && !outputMessage}
                        >
                            <span>🗑️</span>
                            <span>{t('clearAll', currentLanguage)}</span>
                        </button>
                    </div>
                </div>
            </div>

            <footer className="footer">
                <p>
                    &copy; 2025 HL7 Portugal - Nubilum v{version} |
                    <a href="https://hl7.pt" target="_blank" rel="noopener noreferrer"> HL7 Portugal Website</a>
                </p>
            </footer>
        </div>
    );
}

// Render the app
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
