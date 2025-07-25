#!/bin/bash
# Self-sign macOS app bundle for local development
# This reduces security warnings but doesn't eliminate them completely

set -e

APP_PATH="dist/Reporter.app"

if [ ! -d "$APP_PATH" ]; then
    echo "❌ App bundle not found at $APP_PATH"
    echo "Run 'pyinstaller reporter.spec' first"
    exit 1
fi

echo "🔐 Self-signing macOS app bundle..."

# Sign the app bundle with ad-hoc signature
codesign --deep --force --verify --verbose --sign "-" "$APP_PATH"

# Verify the signature
echo "✅ Verifying signature..."
codesign --verify --verbose=2 "$APP_PATH"

# Check Gatekeeper status (will likely fail for self-signed)
echo "🛡️ Checking Gatekeeper status..."
if spctl --assess --verbose "$APP_PATH" 2>&1; then
    echo "✅ App passes Gatekeeper checks"
else
    echo "⚠️  App will show security warnings (expected for self-signed)"
    echo ""
    echo "📋 Users will need to:"
    echo "   1. Right-click the app → 'Open'"
    echo "   2. Click 'Open' in the security dialog"
    echo "   3. Or: System Preferences → Security & Privacy → 'Open Anyway'"
fi

echo ""
echo "✅ Self-signing complete!"
echo "📦 Signed app: $APP_PATH"