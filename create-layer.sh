#!/bin/bash

# AWS Lambda Layer Creation Script for DevStandup AI

set -e

LAYER_NAME="devstandup-ai-dependencies"
REGION=${1:-us-east-1}
PYTHON_VERSION="python3.11"

echo "🚀 Creating AWS Lambda Layer: $LAYER_NAME"
echo "📍 Region: $REGION"
echo "🐍 Python Version: $PYTHON_VERSION"

# Create temporary directory
TEMP_DIR=$(mktemp -d)
LAYER_DIR="$TEMP_DIR/python"

echo "📁 Working directory: $TEMP_DIR"

# Create python directory for Lambda layer
mkdir -p "$LAYER_DIR"

# Install all packages for ARM64
echo "📦 Installing all packages for ARM64..."
pip install -r requirements-layer.txt -t "$LAYER_DIR" \
    --index-url https://pypi.org/simple/ \
    --trusted-host pypi.org \
    --platform manylinux2014_aarch64 \
    --python-version 3.11 \
    --implementation cp \
    --only-binary=:all:

# Remove unnecessary files to reduce size
echo "🧹 Cleaning up unnecessary files..."
find "$LAYER_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$LAYER_DIR" -name "*.pyc" -delete 2>/dev/null || true
find "$LAYER_DIR" -name "*.pyo" -delete 2>/dev/null || true
find "$LAYER_DIR" -name "*.dist-info" -exec rm -rf {} + 2>/dev/null || true
find "$LAYER_DIR" -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

# Create zip file
echo "📦 Creating layer zip file..."
cd "$TEMP_DIR"
zip -r9 layer.zip python/

# Get zip file size
ZIP_SIZE=$(du -h layer.zip | cut -f1)
echo "📏 Layer size: $ZIP_SIZE"

# Publish layer to AWS
echo "☁️  Publishing layer to AWS..."
LAYER_ARN=$(aws lambda publish-layer-version \
    --layer-name "$LAYER_NAME" \
    --description "DevStandup AI Python dependencies" \
    --zip-file fileb://layer.zip \
    --compatible-runtimes python3.11 python3.12 \
    --region "$REGION" \
    --query 'LayerVersionArn' \
    --output text)

echo "✅ Layer created successfully!"
echo "🔗 Layer ARN: $LAYER_ARN"

# Update serverless.yml with layer ARN
echo ""
echo "📝 Add this to your serverless.yml:"
echo ""
echo "provider:"
echo "  layers:"
echo "    - $LAYER_ARN"
echo ""
echo "# Or for all functions:"
echo "functions:"
echo "  yourFunction:"
echo "    layers:"
echo "      - $LAYER_ARN"

# Cleanup
rm -rf "$TEMP_DIR"

echo ""
echo "🎉 Layer creation complete!"
echo "💡 Remember to update your serverless.yml with the layer ARN above"