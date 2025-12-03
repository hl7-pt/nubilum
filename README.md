# Nubilum - HL7 Portugal Message Anonymization Tool

![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

Nubilum is a web-based tool for anonymizing HL7 v2 messages in ER7 format. It provides a user-friendly interface to quickly anonymize patient identifiable information while preserving the message structure and clinical context.

## Features

- **Full PID Segment Anonymization**: Comprehensive anonymization of patient identification data
- **Multi-Segment Support**: Anonymizes PID, NK1, PV1, OBX, ORC, OBR, SCH, AIG, AIL, AIP, and other segments
- **Multi-Message Processing**: Handles multiple HL7 messages in a single request (separated by blank lines or multiple MSH segments)
- **HL7 Message Validation**: Validates messages using HL7 Portugal validator API with collapsible result badges
- **Multi-Language Support**: Full internationalization with English and Portuguese (i18n via Flask-Babel)
- **Language Auto-Detection**: Automatic language detection from browser preferences
- **Field Name Tooltips**: Hover over any field to see its HL7 standard name (version-aware using hl7apy)
- **Smart Pseudo-Generation**: Generates consistent pseudo-names and IDs that indicate field purpose
- **Real-Time Processing**: No storage of messages - all processing is done in real-time
- **Interactive Display**: Color-coded segments with inline editing capabilities
- **Easy Copy/Paste**: One-click copying of anonymized messages
- **Docker-Ready**: Complete containerization with nginx reverse proxy
- **Comprehensive Logging**: File-based logging for audit and debugging
- **Usage Statistics**: Track anonymization usage patterns via REST API

## Privacy & Security

**IMPORTANT**: This tool does NOT store any messages. All anonymization happens in real-time, and no data is persisted on the server. However, users must ensure they have proper authorization to process HL7 messages containing personal health information.

## Installation

### Quick Start with Docker

Nubilum provides two Docker deployment options:

#### Option 1: Full Stack with Nginx (Recommended for Production)

The default `Dockerfile` includes nginx as a reverse proxy serving static files and proxying API requests.

1. **Build the Docker image:**

```bash
docker build -t nubilum:1.1.0 .
```

2. **Run the container:**

```bash
docker run -d \
  --name nubilum \
  -p 8080:80 \
  -v $(pwd)/logs:/var/log/nubilum \
  nubilum:1.1.0
```

3. **Access the application:**

Open your browser and navigate to `http://localhost:8080`

#### Option 2: Standalone with External Reverse Proxy

Use `Dockerfile.standalone` when you have an external nginx or other reverse proxy.

1. **Build the standalone image:**

```bash
docker build -f Dockerfile.standalone -t nubilum:1.1.0-standalone .
```

2. **Run the container:**

```bash
docker run -d \
  --name nubilum \
  -p 5000:5000 \
  -v $(pwd)/logs:/var/log/nubilum \
  nubilum:1.1.0-standalone
```

3. **Configure your reverse proxy:**

Point your nginx/reverse proxy to `http://localhost:5000` for API requests and serve static files from the container or your own location.

**Example nginx configuration:**

```nginx
server {
    listen 80;
    server_name nubilum.yourdomain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Manual Installation

1. **Build the wheel package:**

```bash
./build.sh
```

2. **Install the package:**

```bash
pip install dist/nubilum-1.1.0-py3-none-any.whl
```

3. **Run the application:**

```bash
# Set log directory (optional)
export NUBILUM_LOG_DIR=/var/log/nubilum

# Run with Gunicorn (recommended for production)
gunicorn --bind 0.0.0.0:5000 --workers 4 nubilum.app:app

# Or run with Flask development server
python -m nubilum.app
```

## Usage Examples

### Example 1: Basic ADT Message Anonymization

**Input Message:**

```
MSH|^~\&|SENDING_APP|SENDING_FACILITY|RECEIVING_APP|RECEIVING_FACILITY|20250107120000||ADT^A01|MSG00001|P|2.5
PID|1||123456789^^^HOSPITAL^MR||Doe^John^Robert||19800515|M|||123 Main Street^Apt 4B^Lisbon^Lisboa^1000-001^PT||+351912345678|+351213456789|EN|M|CAT|987654321^^^HOSPITAL^AN||123-45-6789
PV1|1|I|ICU^101^01^HOSPITAL|||DOC123^Johnson^Michael^^^Dr.|||SUR||||2|||DOC123^Johnson^Michael^^^Dr.|INP|VISIT123456|||||||||||||||||||HOSPITAL||REG|||20250107110000
```

**Anonymized Output:**

```
MSH|^~\&|SENDING_APP|SENDING_FACILITY|RECEIVING_APP|RECEIVING_FACILITY|20250107120000||ADT^A01|MSG00001|P|2.5
PID|1||PID123456^^^HOSPITAL^MR||Doe42^John37^Robert||19800530|M|||Street23^Apt 4B^City^Lisboa^12345^PT||+351123456789|+351987654321|EN|M|CAT|ACCT987654^^^HOSPITAL^AN||SSN123456
PV1|1|I|ICU^101^01^HOSPITAL|||DrDoe12^John45^^^Dr.|||SUR||||2|||DrDoe12^John45^^^Dr.|INP|VISIT789012|||||||||||||||||||HOSPITAL||REG|||20250107110000
```

### Example 2: ORM Order Message with Patient Demographics

**Input Message:**

```
MSH|^~\&|LAB_SYSTEM|HOSPITAL|EMR|HOSPITAL|20250107143000||ORM^O01|MSG00002|P|2.5
PID|1||987654321^^^HOSPITAL^MR||Silva^Maria^Teresa||19750823|F|||456 Oak Avenue^^Porto^^4000-001^PT||+351917654321||PT|S|
NK1|1|Silva^Jose^||HUSBAND|456 Oak Avenue^^Porto^^4000-001^PT|+351918765432
ORC|NW|ORDER789|FILLER123||SC||^^^^^R||20250107143000|NURSE789^Anderson^Lisa
OBR|1|ORDER789|FILLER123|CBC^Complete Blood Count^L|||20250107143000|||TECH456^Martinez^Carlos
```

**Anonymized Output:**

```
MSH|^~\&|LAB_SYSTEM|HOSPITAL|EMR|HOSPITAL|20250107143000||ORM^O01|MSG00002|P|2.5
PID|1||PID987654^^^HOSPITAL^MR||Smith78^Jane12^Test||19750912|F|||Street89^Apt 4B^City^^12345^PT||+351234567890||PT|S|
NK1|1|Sample34^Demo56^||HUSBAND|Street12^^City^^12345^PT|+351345678901
ORC|NW|ORDER789012|FILLER456789||SC||^^^^^R||20250107143000|DrSmith23^John67
OBR|1|ORDER789012|FILLER456789|CBC^Complete Blood Count^L|||20250107143000|||DrDoe89^Test45
```

### Example 3: Using the Web Interface

1. **Load the application** in your browser
2. **Paste your HL7 message(s)** into the left input panel (multiple messages supported)
3. **Click "Anonymize Message"** button
4. **Optional: Click "Validate Message"** to check HL7 compliance using HL7 Portugal validator
5. **Review the color-coded output** in the right panel:
   - MSH segments are highlighted in blue
   - PID segments are highlighted in red
   - PV1 segments are highlighted in purple
   - OBR/OBX segments are highlighted in blue/purple
6. **Hover over fields** to see their HL7 standard names (e.g., "Patient ID" for PID-3)
7. **Edit any field** by clicking on it in the output panel
8. **Copy the result** using the "Copy to Clipboard" button

### Example 4: API Usage

You can also use the API directly:

**Anonymize Messages:**
```bash
curl -X POST http://localhost:8080/api/anonymize \
  -H "Content-Type: application/json" \
  -d '{
    "message": "MSH|^~\\&|APP|FACILITY|REC|FAC|20250107||ADT^A01|MSG001|P|2.5\nPID|1||123456||Doe^John||19800515|M"
  }'
```

**Response:**
```json
{
  "success": true,
  "anonymized_message": "MSH|^~\\&|APP|FACILITY|REC|FAC|20250107||ADT^A01|MSG001|P|2.5\nPID|1||PID123456||Doe42^John37||19800530|M",
  "message_count": 1
}
```

**Validate Messages:**
```bash
curl -X POST http://localhost:8080/api/validate \
  -H "Content-Type: application/json" \
  -d '{
    "message": "MSH|^~\\&|APP|FACILITY|REC|FAC|20250107||ADT^A01|MSG001|P|2.5\nPID|1||123456||Doe^John||19800515|M"
  }'
```

**Get Field Name:**
```bash
curl "http://localhost:8080/api/field-name?segment=PID&field=3&version=2.5"
```

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

## Anonymization Rules

### PID Segment (Patient Identification)

| Field | Description | Anonymization Method |
|-------|-------------|---------------------|
| PID-3 | Patient ID | Generates pseudo ID: `PID######` |
| PID-5 | Patient Name | Generates pseudo names: `LastName##^FirstName##` |
| PID-6 | Mother's Maiden Name | Generates pseudo name |
| PID-7 | Date of Birth | Shifts date by consistent offset |
| PID-9 | Patient Alias | Generates pseudo name |
| PID-11 | Patient Address | Replaces with generic address |
| PID-13/14 | Phone Numbers | Generates pseudo phone: `+351#########` |
| PID-18 | Account Number | Generates pseudo ID: `ACCT######` |
| PID-19 | SSN | Generates pseudo ID: `SSN######` |

### NK1 Segment (Next of Kin)

- **Name**: Pseudo-anonymized
- **Address**: Generic address
- **Phone**: Pseudo phone number

### PV1 Segment (Patient Visit)

- **Attending/Referring/Consulting Doctors**: Pseudo-anonymized with "Dr" prefix
- **Visit Number**: Generates pseudo ID: `VISIT######`

### ORC/OBR Segments (Orders)

- **Placer/Filler Order Numbers**: Generates pseudo ID: `ORDER######`
- **Ordering Provider**: Pseudo-anonymized with "Dr" prefix

## Configuration

### Environment Variables

- `NUBILUM_LOG_DIR`: Directory for log files (default: `/var/log/nubilum`)

### Docker Volume Mounts

- `/var/log/nubilum`: Application logs
- `/etc/nginx/sites-available/nubilum`: Custom nginx configuration

## Development

### Running Tests

```bash
pip install -e ".[dev]"
pytest
```

### Building from Source

```bash
# Install build dependencies
pip install build

# Build wheel
python -m build

# Install locally
pip install dist/nubilum-1.1.0-py3-none-any.whl
```

### Creating a Release

Nubilum includes an automated release script that handles version bumping, building, tagging, and publishing to GitHub and Docker registries.

**Requirements:**
- `git`
- `python3` with `build` module (`pip install build`)
- `gh` CLI tool ([GitHub CLI](https://cli.github.com/)) - authenticated
- `docker` (for container publishing)
- Write access to the repository

**Basic Usage:**

```bash
# Create a new release
./scripts/release.sh 1.2.0

# Create a draft release (for review before publishing)
./scripts/release.sh 1.2.0 --draft

# Skip Docker build (for faster releases during development)
./scripts/release.sh 1.2.0 --skip-docker

# Skip GitHub release creation (only build and tag)
./scripts/release.sh 1.2.0 --skip-gh
```

**What the release script does:**

1. ✅ Updates version in `pyproject.toml`
2. ✅ Commits the version change
3. ✅ Builds Python wheel package
4. ✅ Creates and pushes git tag (e.g., `v1.2.0`)
5. ✅ Creates GitHub release with release notes
6. ✅ Uploads wheel to GitHub release
7. ✅ Builds Docker images (both full stack and standalone variants)
8. ✅ Pushes Docker images to GitHub Container Registry
   - `ghcr.io/hl7-pt/nubilum:VERSION` (full stack with nginx)
   - `ghcr.io/hl7-pt/nubilum:latest` (full stack with nginx)
   - `ghcr.io/hl7-pt/nubilum:VERSION-standalone` (standalone without nginx)
   - `ghcr.io/hl7-pt/nubilum:latest-standalone` (standalone without nginx)

**Docker Authentication:**

To publish Docker images, you need a GitHub Personal Access Token with `write:packages` scope:

```bash
# Create a token at: https://github.com/settings/tokens/new?scopes=write:packages,read:packages
# Then set it as an environment variable:
export GITHUB_TOKEN=your_token_here

# Run the release
./scripts/release.sh 1.2.0
```

**All Options:**

```bash
./scripts/release.sh <version> [options]

Options:
  --skip-build      Skip building the wheel
  --skip-docker     Skip building and pushing Docker container
  --skip-gh         Skip creating GitHub release
  --draft           Create release as draft
  -h, --help        Show help message
```

## Architecture

```
┌─────────────────┐
│   Web Browser   │
└────────┬────────┘
         │ HTTP :80
         ▼
┌─────────────────┐
│     Nginx       │  (Reverse Proxy)
│  Static Files   │
└────────┬────────┘
         │ /api/*
         ▼
┌─────────────────┐
│  Flask + CORS   │  (Python Backend)
│   Gunicorn      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  HL7Anonymizer  │  (Anonymization Engine)
│   HL7apy Lib    │
└─────────────────┘
```

## Supported HL7 Segments

- **MSH**: Message Header
- **EVN**: Event Type
- **PID**: Patient Identification (Primary anonymization target)
- **NK1**: Next of Kin
- **PV1**: Patient Visit
- **PV2**: Patient Visit - Additional Info
- **ORC**: Common Order
- **OBR**: Observation Request
- **OBX**: Observation Result
- **SCH**: Scheduling Activity Information
- **AIG**: Appointment Information - General Resource
- **AIL**: Appointment Information - Location Resource
- **AIP**: Appointment Information - Personnel Resource

## Logging

Logs are written to files in the configured log directory:

- `nubilum_YYYYMMDD.log`: Application logs
- `usage_log.jsonl`: Usage tracking log (JSONL format)
- `access.log`: HTTP access logs (when using Gunicorn)
- `error.log`: Error logs

## Usage Tracking

Nubilum automatically tracks anonymization usage to help administrators monitor tool adoption and usage patterns. **No message content is stored** - only metadata about each anonymization event.

### Tracked Information

For each anonymization event, the following is recorded:

- **Timestamp**: Date and time of anonymization
- **Message Type**: HL7 message type (e.g., `ADT^A01`, `ORU^R01`)
- **Segment Counts**: Number of each segment type (PID, OBR, etc.)
- **Total Segments**: Total number of segments in message
- **Message Length**: Size of the message in characters
- **Success/Failure**: Whether anonymization succeeded
- **Error Message**: If failed, the error description

### Viewing Usage Statistics

Access usage statistics via the REST API:

```bash
# Get all-time statistics
curl http://localhost:8080/api/usage/statistics

# Get statistics for last 7 days
curl http://localhost:8080/api/usage/statistics?days=7

# Get statistics for last 30 days
curl http://localhost:8080/api/usage/statistics?days=30
```

**Example Response:**

```json
{
  "success": true,
  "period": "last 7 days",
  "statistics": {
    "total_anonymizations": 145,
    "successful_anonymizations": 143,
    "failed_anonymizations": 2,
    "success_rate": 98.62,
    "message_types": {
      "ADT^A01": 56,
      "ORU^R01": 42,
      "ORM^O01": 28,
      "SIU^S12": 19
    },
    "segments_processed": {
      "MSH": 145,
      "PID": 145,
      "PV1": 98,
      "OBR": 70,
      "OBX": 312,
      "NK1": 23
    },
    "total_segments": 1023,
    "average_segments_per_message": 7.1,
    "total_message_length": 234567,
    "average_message_length": 1618,
    "daily_counts": {
      "2025-01-07": 42,
      "2025-01-08": 38,
      "2025-01-09": 65
    },
    "hourly_distribution": {
      "9": 12,
      "10": 23,
      "11": 18,
      "14": 31,
      "15": 27,
      "16": 19
    }
  }
}
```

### Usage Log Format

The usage log is stored in JSONL (JSON Lines) format at `/var/log/nubilum/usage_log.jsonl`. Each line is a valid JSON object:

```json
{"timestamp": "2025-01-07T14:23:45.123456", "date": "2025-01-07", "time": "14:23:45", "message_type": "ADT^A01", "segment_counts": {"MSH": 1, "EVN": 1, "PID": 1, "PV1": 1}, "total_segments": 4, "message_length": 512, "success": true, "error": null}
```

### Privacy Considerations

- **No PHI Stored**: Original message content is never written to the usage log
- **Metadata Only**: Only counts, types, and timestamps are recorded
- **HIPAA Compliant**: Usage tracking does not compromise patient privacy
- **Audit Trail**: Provides accountability without storing sensitive data

## Security Considerations

1. **No Data Persistence**: Messages are never stored on disk or in memory beyond request processing
2. **No External Connections**: Tool operates completely offline
3. **Audit Logging**: All anonymization requests are logged (without message content)
4. **Size Limits**: Maximum message size is 1MB to prevent memory issues
5. **CORS Enabled**: For development; configure appropriately for production

## Troubleshooting

### Container won't start

Check logs:
```bash
docker logs nubilum
```

### Anonymization fails

- Ensure message is in valid ER7 format
- Check that segment separators are `|`
- Verify message is not corrupted

### Frontend not loading

- Check nginx logs: `docker exec nubilum tail /var/log/nginx/nubilum_error.log`
- Verify static files are present in the package

## Contributing

Contributions are welcome! Please ensure:

1. Code follows PEP 8 style guidelines
2. All tests pass
3. New features include tests
4. Documentation is updated

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Acknowledgments

- HL7 Portugal for supporting this project
- HL7apy library for HL7 parsing capabilities
- Flask and React communities

## Contact

For issues, questions, or contributions, please visit:
- HL7 Portugal: https://hl7.pt
- Project Repository: [Add your repository URL here]

---

## Internationalization

Nubilum supports multiple languages with automatic browser language detection:

- **English (en)**: Default language
- **Portuguese (pt)**: Full translation coverage

### Changing Language

Users can change the language using the language selector in the header (flag icon). The selected language is stored in the browser and persists across sessions.

### Adding New Languages

See [I18N_GUIDE.md](I18N_GUIDE.md) for detailed instructions on:
- Adding new languages
- Managing translations
- Translation workflow
- API endpoints for language management

**Version**: 1.1.0
**Last Updated**: December 2025
**Maintained by**: HL7 Portugal
