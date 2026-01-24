# Changelog

All notable changes to Nubilum will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-01-24

### Added
- TXA (Transcription Document Header) segment anonymization support
  - Anonymizes document originators, authenticators, and transcriptionists
  - Anonymizes activity date/time fields

### Fixed
- Fixed critical bug where anonymization was only properly applied to the first message when processing multiple messages
  - Each message now gets its own anonymizer instance to ensure independent anonymization
  - Previously, subsequent messages would reuse pseudo-IDs and names from the first message

### Changed
- Updated documentation to include TXA segment in supported segments list
- Enhanced README.md with complete list of supported HL7 segments

## [1.1.0] - 2025-01-XX

### Added
- Portuguese translations (i18n support)
- Usage tracking and statistics API
- Multi-language support with automatic browser detection
- Field name tooltips with HL7 version awareness

## [1.0.0] - 2025-01-XX

### Added
- Initial release
- HL7 v2 message anonymization in ER7 format
- Support for PID, NK1, PV1, PV2, PD1, ORC, OBR, OBX, and other segments
- Web-based interface with React
- Docker deployment with nginx
- Message validation using HL7 Portugal validator API
- Real-time processing with no data persistence
- Comprehensive logging and audit trail
