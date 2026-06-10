#!/bin/bash
# NEXUS ULTRA - Build Script
# ===========================
# สร้าง APK จริงด้วย Gradle

set -e

echo "========================================"
echo "🛠️ NEXUS ULTRA - APK Build Script"
echo "========================================"

cd "$(dirname "$0")"

# 1. ตรวจสอบ prerequisites
echo ""
echo "📦 Checking prerequisites..."
if ! command -v java &> /dev/null; then
    echo "❌ Java not found. Please install JDK 17+"
    exit 1
fi
echo "   ✅ Java: $(java -version 2>&1 | head -1)"

if [ ! -f "android/gradlew" ]; then
    echo "❌ gradlew not found"
    exit 1
fi
chmod +x android/gradlew
echo "   ✅ Gradle wrapper ready"

# 2. Clean build
echo ""
echo "🧹 Cleaning previous build..."
rm -rf android/build/outputs
rm -rf android/build/intermediates
rm -rf android/.gradle

# 3. Build APK
echo ""
echo "🔨 Building APK..."
cd android
./gradlew assembleDebug --no-daemon --console=plain

# 4. Find APK
echo ""
echo "📦 Looking for APK..."
APK_PATH=$(find build/outputs/apk -name "*.apk" -type f 2>/dev/null | head -1)

if [ -n "$APK_PATH" ]; then
    echo "   ✅ APK found: $APK_PATH"
    ls -lh "$APK_PATH"
    
    # Copy to build directory
    cp "$APK_PATH" build/nexus_ultra.apk
    echo "   ✅ Copied to build/nexus_ultra.apk"
    
    # Show info
    echo ""
    echo "📊 APK Information:"
    ls -lh build/nexus_ultra.apk
    echo ""
    echo "✅ BUILD SUCCESSFUL!"
    echo "   APK: android/build/nexus_ultra.apk"
else
    echo "   ❌ APK not found!"
    echo "   Build may have failed."
    exit 1
fi

echo ""
echo "========================================"
echo "🎉 Build Complete!"
echo "========================================"