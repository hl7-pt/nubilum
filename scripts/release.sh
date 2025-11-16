#!/bin/bash
set -e

# Nubilum Release Script
# This script automates the release process:
# 1. Builds the Python wheel
# 2. Creates a git tag
# 3. Pushes tag to upstream
# 4. Creates GitHub release
# 5. Uploads wheel to release
# 6. Builds and pushes Docker container to GitHub Container Registry

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
REPO="hl7-pt/nubilum"
REGISTRY="ghcr.io"

# Function to print colored messages
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to show usage
usage() {
    cat << EOF
Usage: $0 <version> [options]

Arguments:
  version           Version number (e.g., 1.0.1, 2.0.0)

Options:
  --skip-build      Skip building the wheel
  --skip-docker     Skip building and pushing Docker container
  --skip-gh         Skip creating GitHub release
  --draft           Create release as draft
  -h, --help        Show this help message

Examples:
  $0 1.0.1
  $0 1.1.0 --draft
  $0 1.0.2 --skip-docker

Requirements:
  - git
  - python3 with build module (pip install build)
  - gh CLI (authenticated)
  - docker (for container publishing)
  - write access to $REPO
EOF
    exit 1
}

# Parse arguments
if [ $# -eq 0 ]; then
    usage
fi

VERSION=$1
shift

SKIP_BUILD=false
SKIP_DOCKER=false
SKIP_GH=false
DRAFT_FLAG=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        --skip-docker)
            SKIP_DOCKER=true
            shift
            ;;
        --skip-gh)
            SKIP_GH=true
            shift
            ;;
        --draft)
            DRAFT_FLAG="--draft"
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            ;;
    esac
done

# Validate version format
if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    print_error "Invalid version format: $VERSION"
    print_error "Version must follow semantic versioning (e.g., 1.0.0)"
    exit 1
fi

TAG="v$VERSION"

print_info "Starting release process for version $VERSION"

# Check if we're on main branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
    print_warning "You are not on the main branch (current: $CURRENT_BRANCH)"
    read -p "Continue anyway? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for uncommitted changes
if ! git diff-index --quiet HEAD --; then
    print_error "You have uncommitted changes. Please commit or stash them first."
    exit 1
fi

# Update version in pyproject.toml
print_info "Updating version in pyproject.toml to $VERSION"
sed -i "s/^version = .*/version = \"$VERSION\"/" pyproject.toml

# Commit version change
git add pyproject.toml
git commit -m "Bump version to $VERSION" || print_warning "Version already at $VERSION or no changes to commit"

# Build the wheel
if [ "$SKIP_BUILD" = false ]; then
    print_info "Building Python wheel..."
    rm -rf dist/
    python3 -m build

    WHEEL_FILE="dist/nubilum-${VERSION}-py3-none-any.whl"
    if [ ! -f "$WHEEL_FILE" ]; then
        print_error "Wheel file not found: $WHEEL_FILE"
        exit 1
    fi
    print_info "Wheel built successfully: $WHEEL_FILE"
else
    print_warning "Skipping wheel build"
    WHEEL_FILE="dist/nubilum-${VERSION}-py3-none-any.whl"
fi

# Create and push git tag
print_info "Creating git tag $TAG"
if git rev-parse "$TAG" >/dev/null 2>&1; then
    print_warning "Tag $TAG already exists"
    read -p "Delete and recreate? [y/N] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git tag -d "$TAG"
        git push upstream --delete "$TAG" 2>/dev/null || true
    else
        print_error "Aborted"
        exit 1
    fi
fi

git tag -a "$TAG" -m "Release version $VERSION"
print_info "Pushing tag to upstream..."
git push upstream "$TAG"

# Create GitHub release
if [ "$SKIP_GH" = false ]; then
    print_info "Creating GitHub release..."

    RELEASE_NOTES=$(cat <<EOF
# Nubilum $TAG - HL7 Portugal Message Anonymization Tool

## Features

- **Comprehensive Anonymization**: Support for multiple HL7 segments (PID, PV1, NK1, IN1, GT1, SCH, AIG, AIL, AIP)
- **Field-level Control**: Individual field selection with visual highlighting
- **Validation**: Real-time HL7 message validation
- **Example Messages**: Pre-loaded examples for testing
- **HL7 Portugal Branding**: Official color scheme and logo integration
- **User-friendly Interface**: Clean, intuitive design with tooltips

## Installation

### Using pip
\`\`\`bash
pip install nubilum==$VERSION
\`\`\`

### Using Docker
\`\`\`bash
docker pull $REGISTRY/$REPO:$VERSION
docker run -p 5000:5000 $REGISTRY/$REPO:$VERSION
\`\`\`

## Technical Details

- Built with modern web technologies
- Client-side processing for data privacy
- Responsive design
EOF
)

    gh release create "$TAG" \
        --repo "$REPO" \
        --title "Nubilum $TAG" \
        --notes "$RELEASE_NOTES" \
        $DRAFT_FLAG

    # Upload wheel to release
    if [ -f "$WHEEL_FILE" ]; then
        print_info "Uploading wheel to GitHub release..."
        gh release upload "$TAG" "$WHEEL_FILE" --repo "$REPO"
    fi
else
    print_warning "Skipping GitHub release creation"
fi

# Build and push Docker container
if [ "$SKIP_DOCKER" = false ]; then
    print_info "Building Docker container..."

    IMAGE_TAG="$REGISTRY/$REPO:$VERSION"
    IMAGE_LATEST="$REGISTRY/$REPO:latest"

    docker build -t "$IMAGE_TAG" -t "$IMAGE_LATEST" .

    print_info "Logging into GitHub Container Registry..."

    # Try different authentication methods
    if [ -n "$GITHUB_TOKEN" ] && [ -n "$GITHUB_ACTOR" ]; then
        echo "$GITHUB_TOKEN" | docker login "$REGISTRY" -u "$GITHUB_ACTOR" --password-stdin 2>/dev/null
        LOGIN_STATUS=$?
    else
        print_warning "GITHUB_TOKEN or GITHUB_ACTOR not set, trying gh CLI..."
        gh auth token | docker login "$REGISTRY" -u "$(gh api user --jq .login)" --password-stdin 2>/dev/null
        LOGIN_STATUS=$?
    fi

    if [ $LOGIN_STATUS -ne 0 ]; then
        print_error "Docker login failed!"
        print_warning "To publish Docker images, you need a Personal Access Token with 'write:packages' scope"
        print_info "Create one at: https://github.com/settings/tokens/new?scopes=write:packages,read:packages"
        print_info "Then set: export GITHUB_TOKEN=<your-token>"
        print_info ""
        print_info "Skipping Docker push. You can manually push later with:"
        echo "  docker push $IMAGE_TAG"
        echo "  docker push $IMAGE_LATEST"
    else
        print_info "Pushing Docker images..."
        if docker push "$IMAGE_TAG" && docker push "$IMAGE_LATEST"; then
            print_info "Docker images published:"
            echo "  - $IMAGE_TAG"
            echo "  - $IMAGE_LATEST"
        else
            print_error "Docker push failed! You may need to:"
            print_info "1. Create a PAT with 'write:packages' scope at https://github.com/settings/tokens"
            print_info "2. Enable package write permissions for the repository"
            print_info "3. Re-run: export GITHUB_TOKEN=<your-token> && ./scripts/release.sh $VERSION --skip-build --skip-gh"
        fi
    fi
else
    print_warning "Skipping Docker build and push"
fi

print_info "Release $TAG completed successfully!"
echo ""
echo "Summary:"
echo "  - Version: $VERSION"
echo "  - Tag: $TAG"
echo "  - GitHub Release: https://github.com/$REPO/releases/tag/$TAG"
[ "$SKIP_DOCKER" = false ] && echo "  - Docker Image: $REGISTRY/$REPO:$VERSION"
echo ""
print_info "Next steps:"
echo "  1. Verify the release at https://github.com/$REPO/releases"
[ "$SKIP_DOCKER" = false ] && echo "  2. Test the Docker image: docker run -p 5000:5000 $REGISTRY/$REPO:$VERSION"
echo "  3. Push to main: git push upstream main"
