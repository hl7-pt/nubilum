# Release Guide for Nubilum v1.2.0

This guide will help you complete the release process for version 1.2.0.

## Current Status

✅ Code changes committed
✅ Version bumped to 1.2.0
✅ Git tag `v1.2.0` created locally
✅ CHANGELOG.md created
✅ Documentation updated
⏳ Pending: Push to GitHub and publish artifacts

## Prerequisites

Before starting, ensure you have:
- [ ] Git authentication configured (SSH key or credential helper)
- [ ] Docker installed and running
- [ ] GitHub CLI (`gh`) installed (optional but recommended)
- [ ] GitHub personal access token with `write:packages` scope (for Docker publishing)

## Step 1: Push to GitHub

First, push the commit and tag to GitHub:

```bash
# Push the main branch
git push origin main

# Push the tag
git push origin v1.2.0
```

If you encounter authentication issues, configure git credentials:
```bash
# Option A: Use SSH (recommended)
git remote set-url origin git@github.com:hl7-pt/nubilum.git

# Option B: Use credential helper
git config --global credential.helper store
```

## Step 2: Build the Python Wheel

Build the distribution package:

```bash
# Clean previous builds
rm -rf dist/ build/

# Build the wheel
python3 -m build

# Verify the wheel was created
ls -lh dist/nubilum-1.2.0-py3-none-any.whl
```

## Step 3: Create GitHub Release

### Option A: Using GitHub CLI (Recommended)

If you have `gh` CLI installed:

```bash
# Install gh CLI if needed:
# Ubuntu/Debian: sudo apt install gh
# macOS: brew install gh
# Or see: https://cli.github.com/

# Authenticate (first time only)
gh auth login

# Create the release
gh release create v1.2.0 \
  --repo hl7-pt/nubilum \
  --title "Nubilum v1.2.0" \
  --notes-file CHANGELOG.md \
  dist/nubilum-1.2.0-py3-none-any.whl
```

### Option B: Using GitHub Web Interface

1. Go to https://github.com/hl7-pt/nubilum/releases/new
2. Select tag: `v1.2.0`
3. Title: `Nubilum v1.2.0`
4. Description: Copy from CHANGELOG.md or use:

```markdown
## What's New in v1.2.0

### Fixed
- **Critical bug fix**: Multi-message anonymization now works correctly
  - Each message gets its own anonymizer instance
  - Previously, subsequent messages incorrectly reused pseudo-IDs from the first message

### Added
- **TXA segment support**: Anonymizes Transcription Document Header segments
  - Document originators, authenticators, and transcriptionists
  - Activity date/time fields

### Documentation
- Added comprehensive CHANGELOG.md
- Updated README with complete list of supported HL7 segments
- Enhanced segment documentation

## Installation

### Using pip
\`\`\`bash
pip install dist/nubilum-1.2.0-py3-none-any.whl
\`\`\`

### Using Docker
\`\`\`bash
docker pull ghcr.io/hl7-pt/nubilum:1.2.0
docker run -p 8080:80 ghcr.io/hl7-pt/nubilum:1.2.0
\`\`\`
```

5. Upload the wheel file: `dist/nubilum-1.2.0-py3-none-any.whl`
6. Click "Publish release"

## Step 4: Build and Push Docker Images

### 4.1 Login to GitHub Container Registry

```bash
# Set your GitHub username
export GITHUB_ACTOR=your-github-username

# Create a Personal Access Token at:
# https://github.com/settings/tokens/new?scopes=write:packages,read:packages
export GITHUB_TOKEN=your-personal-access-token

# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u $GITHUB_ACTOR --password-stdin
```

### 4.2 Build Docker Images

```bash
# Build full stack image (with nginx)
docker build -t ghcr.io/hl7-pt/nubilum:1.2.0 -t ghcr.io/hl7-pt/nubilum:latest .

# Build standalone image (without nginx)
docker build -f Dockerfile.standalone \
  -t ghcr.io/hl7-pt/nubilum:1.2.0-standalone \
  -t ghcr.io/hl7-pt/nubilum:latest-standalone .
```

### 4.3 Push Docker Images

```bash
# Push full stack images
docker push ghcr.io/hl7-pt/nubilum:1.2.0
docker push ghcr.io/hl7-pt/nubilum:latest

# Push standalone images
docker push ghcr.io/hl7-pt/nubilum:1.2.0-standalone
docker push ghcr.io/hl7-pt/nubilum:latest-standalone
```

## Step 5: Verify the Release

1. **GitHub Release**: Visit https://github.com/hl7-pt/nubilum/releases/tag/v1.2.0
2. **Docker Images**: Visit https://github.com/hl7-pt/nubilum/pkgs/container/nubilum
3. **Test the Docker image**:
   ```bash
   docker run -p 8080:80 ghcr.io/hl7-pt/nubilum:1.2.0
   # Open http://localhost:8080 in your browser
   ```

## Alternative: Use the Release Script

If you have all prerequisites installed, you can use the automated script:

```bash
# First, push your changes manually
git push origin main
git push origin v1.2.0

# Then run the release script (it will skip the tag creation since it exists)
./scripts/release.sh 1.2.0 --skip-build

# Or if you want to rebuild everything:
./scripts/release.sh 1.2.0
```

## Troubleshooting

### Docker Login Fails
- Ensure your Personal Access Token has `write:packages` scope
- Verify `GITHUB_ACTOR` is your GitHub username
- Try logging in directly: `docker login ghcr.io`

### Docker Push Fails with "unauthorized"
- Enable "Package write" permissions in repository settings
- Go to: https://github.com/hl7-pt/nubilum/settings/actions
- Under "Workflow permissions", enable package write access

### Git Push Requires Password
- Use SSH: `git remote set-url origin git@github.com:hl7-pt/nubilum.git`
- Or use credential helper: `git config --global credential.helper store`

## Summary Checklist

- [ ] Git changes pushed to GitHub
- [ ] Tag v1.2.0 pushed to GitHub
- [ ] Python wheel built
- [ ] GitHub release created
- [ ] Wheel uploaded to release
- [ ] Docker images built
- [ ] Docker images pushed to GHCR
- [ ] Release verified and tested

## Release Artifacts

After completion, you should have:

1. **GitHub Release**: https://github.com/hl7-pt/nubilum/releases/tag/v1.2.0
2. **Docker Images**:
   - `ghcr.io/hl7-pt/nubilum:1.2.0` (full stack)
   - `ghcr.io/hl7-pt/nubilum:latest` (full stack)
   - `ghcr.io/hl7-pt/nubilum:1.2.0-standalone`
   - `ghcr.io/hl7-pt/nubilum:latest-standalone`
3. **Python Wheel**: `nubilum-1.2.0-py3-none-any.whl`

---

**Questions?** Check the main [README.md](README.md) or open an issue on GitHub.
