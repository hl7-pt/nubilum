// i18n.js - Internationalization for Nubilum frontend

const translations = {
    en: {
        // Application title and header
        appTitle: "Nubilum - HL7 Portugal Message Anonymizer",
        appDescription: "HL7 Portugal Message Anonymization Tool",

        // Privacy Notice
        privacyNotice: "Privacy Notice",
        privacyText: "This tool does NOT store any messages. All anonymization is performed in real-time, and no data is retained on our servers. However, please ensure you have the proper authorization to process any HL7 messages containing personal health information.",

        // Legend
        segmentColorLegend: "Segment Color Legend",

        // Input section
        inputMessage: "Input Message",
        pasteMessage: "Paste your HL7 message here...",
        loadExample: "Load Example",
        clear: "Clear",
        anonymizeButton: "Anonymize Message",
        validateButton: "Validate Message",

        // Output section
        anonymizedOutput: "Anonymized Output",
        validationResult: "Validation Result",

        // Buttons
        copyToClipboard: "Copy to Clipboard",
        clearAll: "Clear All",

        // Alert messages
        messageAnonymizedSuccess: "Message anonymized successfully!",
        messagesAnonymizedSuccess: "messages anonymized successfully!",
        enterMessageToAnonymize: "Please enter an HL7 message to anonymize.",
        enterMessageToValidate: "Please enter an HL7 message to validate.",
        messagesCleared: "Messages cleared.",
        noMessageToCopy: "No message to copy.",
        copiedToClipboard: "Message copied to clipboard!",
        failedToCopy: "Failed to copy message.",
        exampleMessageLoaded: "Example message loaded.",
        failedToConnect: "Failed to connect to the server.",
        failedToValidate: "Failed to connect to validation service.",

        // Validation
        messageValidated: "Message validated successfully!",
        messagesValidated: "messages validated successfully!",
        messageFailedValidation: "Message validation failed.",
        messagesFailedValidation: "message(s) failed validation.",
        validationDetails: "Validation Details",
        viewFullDetails: "View full details at HL7 PT Validator →",
        moreErrors: "more errors",
        valid: "Valid",
        invalid: "Invalid",

        // Example modal
        selectExample: "Select an HL7 Example Message",
        close: "Close",

        // Language selector
        language: "Language",
        selectLanguage: "Select Language",
        english: "English",
        portuguese: "Portuguese",
    },
    pt: {
        // Application title and header
        appTitle: "Nubilum - Anonimizador de Mensagens HL7 Portugal",
        appDescription: "Ferramenta de Anonimização de Mensagens HL7 Portugal",

        // Privacy Notice
        privacyNotice: "Aviso de Privacidade",
        privacyText: "Esta ferramenta NÃO armazena nenhuma mensagem. Toda a anonimização é realizada em tempo real e nenhum dado é retido nos nossos servidores. No entanto, certifique-se de que tem a devida autorização para processar quaisquer mensagens HL7 contendo informações de saúde pessoais.",

        // Legend
        segmentColorLegend: "Legenda de Cores dos Segmentos",

        // Input section
        inputMessage: "Mensagem de Entrada",
        pasteMessage: "Cole a sua mensagem HL7 aqui...",
        loadExample: "Carregar Exemplo",
        clear: "Limpar",
        anonymizeButton: "Anonimizar Mensagem",
        validateButton: "Validar Mensagem",

        // Output section
        anonymizedOutput: "Resultado Anonimizado",
        validationResult: "Resultado da Validação",

        // Buttons
        copyToClipboard: "Copiar para Área de Transferência",
        clearAll: "Limpar Tudo",

        // Alert messages
        messageAnonymizedSuccess: "Mensagem anonimizada com sucesso!",
        messagesAnonymizedSuccess: "mensagens anonimizadas com sucesso!",
        enterMessageToAnonymize: "Por favor, insira uma mensagem HL7 para anonimizar.",
        enterMessageToValidate: "Por favor, insira uma mensagem HL7 para validar.",
        messagesCleared: "Mensagens limpas.",
        noMessageToCopy: "Nenhuma mensagem para copiar.",
        copiedToClipboard: "Mensagem copiada para a área de transferência!",
        failedToCopy: "Falha ao copiar mensagem.",
        exampleMessageLoaded: "Mensagem de exemplo carregada.",
        failedToConnect: "Falha ao conectar ao servidor.",
        failedToValidate: "Falha ao conectar ao serviço de validação.",

        // Validation
        messageValidated: "Mensagem validada com sucesso!",
        messagesValidated: "mensagens validadas com sucesso!",
        messageFailedValidation: "Validação da mensagem falhou.",
        messagesFailedValidation: "mensagem(ns) falharam a validação.",
        validationDetails: "Detalhes da Validação",
        viewFullDetails: "Ver detalhes completos no Validador HL7 PT →",
        moreErrors: "mais erros",
        valid: "Válido",
        invalid: "Inválido",

        // Example modal
        selectExample: "Selecione uma Mensagem HL7 de Exemplo",
        close: "Fechar",

        // Language selector
        language: "Idioma",
        selectLanguage: "Selecionar Idioma",
        english: "Inglês",
        portuguese: "Português",
    }
};

// Translation function
function t(key, lang = 'en') {
    return translations[lang]?.[key] || translations['en'][key] || key;
}

// Get browser language
function getBrowserLanguage() {
    const browserLang = navigator.language || navigator.userLanguage;
    // Check if browser language starts with 'pt'
    if (browserLang.toLowerCase().startsWith('pt')) {
        return 'pt';
    }
    return 'en';
}

// Get stored language preference
function getStoredLanguage() {
    return localStorage.getItem('nubilum_language');
}

// Store language preference
function setStoredLanguage(lang) {
    localStorage.setItem('nubilum_language', lang);
}

// Get current language (stored preference or browser default)
function getCurrentLanguage() {
    return getStoredLanguage() || getBrowserLanguage();
}
