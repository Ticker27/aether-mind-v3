#!/bin/bash
# AETHER MIND - Final APK Assembler
# ==================================

set -e

echo "========================================"
echo "🚀 AETHER ASSEMBLY - FINAL BUILD"
echo "========================================"

cd "$(dirname "$0")"

# 1. Clean build artifacts
echo ""
echo "🧹 Cleaning build artifacts..."
rm -rf android/build/
rm -rf android/.gradle/

# 2. Execute Gradle Build (with ChaquoPy)
echo ""
echo "🔨 Executing Gradle Build (with ChaquoPy)..."
cd android
./gradlew assembleDebug --no-daemon --console=plain

# 3. Verify build
echo ""
echo "🔍 Verifying APK..."
if [ -f "build/outputs/apk/debug/app-debug.apk" ]; then
    echo "   ✅ APK built successfully: build/outputs/apk/debug/app-debug.apk"
    cp build/outputs/apk/debug/app-debug.apk ../dist/aether_shot_v1.0.0.apk
else
    echo "   ❌ APK build failed"
    exit 1
fi

# 4. Generate build manifest
echo ""
echo "📝 Generating build manifest..."
{
    echo "{"
    echo "  \"apk\": \"$(pwd)/../dist/aether_shot_v1.0.0.apk\","
    echo "  \"size\": \"$(stat -c%s ../dist/aether_shot_v1.0.0.apk)\","
    echo "  \"sha256\": \"$(sha256sum ../dist/aether_shot_v1.0.0.apk | awk '{print $1}')\","
    echo "  \"package\": \"com.aether.shot\","
    echo "  \"version\": \"1.0.0\","
    echo "  \"build_date\": \"$(date -u +'%Y-%m-%dT%H:%M:%S.%NZ')\""
    echo "}"
} > ../dist/build_manifest.json

echo "   ✅ Build manifest generated: ../dist/build_manifest.json"

# 5. Commit and push build artifacts
echo ""
echo "💾 Committing build artifacts..."
git add ../dist/aether_shot_v1.0.0.apk ../dist/build_manifest.json
git commit -m "build: AETHER SHOT APK v1.0.0 (built by GitHub Actions)"
git push
