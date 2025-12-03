# Nubilum - Quick Start Guide

## Fastest Way to Run (Docker Compose)

1. **Start the application:**

```bash
docker-compose up -d
```

2. **Access the application:**

Open your browser and go to: `http://localhost:8080`

3. **Stop the application:**

```bash
docker-compose down
```

## Alternative: Build and Run with Docker

### Option 1: Full Stack with Nginx (Recommended for Production)

This option includes nginx as a reverse proxy and is the simplest deployment option.

```bash
# Build
docker build -t nubilum:1.1.0 .

# Run
docker run -d --name nubilum -p 8080:80 nubilum:1.1.0

# View logs
docker logs -f nubilum

# Stop
docker stop nubilum
docker rm nubilum
```

### Option 2: Standalone with External Reverse Proxy

Use this option if you already have nginx or another reverse proxy running externally.

```bash
# Build
docker build -f Dockerfile.standalone -t nubilum:1.1.0-standalone .

# Run (exposes port 5000)
docker run -d --name nubilum -p 5000:5000 nubilum:1.1.0-standalone

# View logs
docker logs -f nubilum

# Stop
docker stop nubilum
docker rm nubilum
```

**Note:** The standalone option runs gunicorn directly on port 5000. Configure your external reverse proxy to forward requests to this port.

## Development Mode (No Docker)

```bash
# Quick start
./run_dev.sh

# Or manually
python3 -m venv venv
source venv/bin/activate
pip install -e .
python -m nubilum.app
```

Access at: `http://localhost:5000`

## First Time Usage

1. **Load the example message** by clicking the "Load Example" button
2. **Click "Anonymize Message"** to see the anonymization in action
3. **Notice the color-coded segments** in the output
4. **Try editing fields** by clicking on them
5. **Copy the result** using the "Copy to Clipboard" button

## Test HL7 Message

```
MSH|^~\&|SENDING_APP|HOSPITAL|RECEIVING_APP|HOSPITAL|20250107120000||ADT^A01|MSG00001|P|2.5
PID|1||123456789^^^HOSPITAL^MR||Doe^John^Robert||19800515|M|||123 Main Street^^Lisbon^^1000-001^PT||+351912345678
```

Paste this into the input panel and click "Anonymize Message" to see it in action!

## Important Notes

- **No data is stored** - All processing happens in real-time
- **Maximum message size**: 1MB
- **Supported format**: HL7 v2.x ER7 format only
- **Color legend**: Each segment type has a different background color for easy identification

## Need Help?

See the full [README.md](README.md) for detailed documentation.
