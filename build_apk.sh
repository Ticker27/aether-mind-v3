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
JAVA_HOME=/usr/lib/jvm/java-17-openjdk
export JAVA_HOME
export _JAVA_OPTIONS="-Xshare:off -Xint"
JAVA_CMD="$JAVA_HOME/bin/java"

if ! $JAVA_CMD -version &>/dev/null; then
    echo "❌ Java not found at $JAVA_CMD"
    exit 1
fi
echo "   ✅ Java: $($JAVA_CMD -version 2>&1 | head -1)"

if [ -f "android/gradlew" ]; then
    chmod +x android/gradlew
    echo "   ✅ Gradle wrapper ready"
fi

# 2. Install Android SDK if needed
echo ""
echo "📱 Checking Android SDK..."
ANDROID_SDK_ROOT="/var/minis/workspace/aether-mind-v3/android_sdk"
if [ ! -d "$ANDROID_SDK_ROOT" ]; then
    echo "   Installing Android SDK command-line tools..."
    mkdir -p "$ANDROID_SDK_ROOT"
    cd /tmp
    curl -sL -o cmdline-tools.zip https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip
    unzip -q cmdline-tools.zip
    mv cmdline-tools "$ANDROID_SDK_ROOT/"
    cd "$ANDROID_SDK_ROOT/cmdline-tools"
    mkdir latest
    mv * latest/ 2>/dev/null || true
    # Accept licenses
    yes | "$ANDROID_SDK_ROOT/cmdline-tools/latest/bin/sdkmanager" --licenses >/dev/null 2>&1 || true
fi
export ANDROID_SDK_ROOT
export ANDROID_HOME="$ANDROID_SDK_ROOT"
echo "   ✅ Android SDK: $ANDROID_SDK_ROOT"

# 3. Clean build
echo ""
echo "🧹 Cleaning previous build..."
rm -rf android/build/outputs
rm -rf android/build/intermediates
rm -rf android/.gradle
rm -rf "$ANDROID_SDK_ROOT/temp"

# 4. Build APK
echo ""
echo "🔨 Building APK..."
cd android
JAVA_HOME=$JAVA_HOME ./gradlew assembleDebug --no-daemon --console=plain 2>&1 || {
    echo "⚠️ Gradle build failed — creating Python APK builder instead"
    cd ..
    python3 android/apk_builder.py 2>&1
}

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