#!/system/bin/sh
# AETHER SDK FIX — ติดตั้ง Android SDK + NDK + CMake
# ใช้ commandline tools ของ Google โดยตรง (เสถียรที่สุด)
# ดาวน์โหลด ~150MB, ใช้เวลา ~5-10 นาที

set -e

GREEN='\033[92m'; YELLOW='\033[93m'; RED='\033[91m'; CYAN='\033[96m'; NC='\033[0m'

echo "${CYAN}══════════════════════════════════════════${NC}"
echo "${CYAN}  🔧 AETHER SDK FIX${NC}"
echo "${CYAN}  ติดตั้ง Android SDK โดยตรงจาก Google${NC}"
echo "${CYAN}══════════════════════════════════════════${NC}"
echo ""

SDK_DIR="$HOME/android-sdk"
mkdir -p "$SDK_DIR"

# 1. Download commandline tools
echo "📥 ดาวน์โหลด commandline tools..."
cd /tmp
curl -L -o cmdline-tools.zip \
  "https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip" \
  --progress-bar

# 2. Extract
echo "📦 แตกไฟล์..."
unzip -q cmdline-tools.zip
mkdir -p "$SDK_DIR/cmdline-tools"
mv cmdline-tools "$SDK_DIR/cmdline-tools/latest"
rm -f cmdline-tools.zip

# 3. Setup sdkmanager
export PATH="$PATH:$SDK_DIR/cmdline-tools/latest/bin"
export ANDROID_HOME="$SDK_DIR"

# 4. Accept licenses
echo "✅ Accept licenses..."
yes | sdkmanager --licenses >/dev/null 2>&1 || true

# 5. Install SDK components
echo ""
echo "📦 ติดตั้ง SDK components..."
echo "   (รอ ~3-5 นาที)"

sdkmanager "platforms;android-34" >/dev/null 2>&1
echo "   ✅ Android SDK 34"

sdkmanager "build-tools;34.0.0" >/dev/null 2>&1
echo "   ✅ Build Tools 34.0.0"

sdkmanager "ndk;26.1.10909125" >/dev/null 2>&1
echo "   ✅ NDK 26.1.10909125"

sdkmanager "cmake;3.22.1" >/dev/null 2>&1
echo "   ✅ CMake 3.22.1"

# 6. Add to PATH
grep -q "ANDROID_HOME" ~/.bashrc 2>/dev/null || {
    echo "" >> ~/.bashrc
    echo "# Android SDK" >> ~/.bashrc
    echo "export ANDROID_HOME=\$HOME/android-sdk" >> ~/.bashrc
    echo "export PATH=\$PATH:\$ANDROID_HOME/cmdline-tools/latest/bin" >> ~/.bashrc
    echo "export PATH=\$PATH:\$ANDROID_HOME/platform-tools" >> ~/.bashrc
    echo "export JAVA_HOME=/usr/lib/jvm/java-17-openjdk" >> ~/.bashrc
}

# 7. Test
echo ""
echo "━━━ 📊 ตรวจสอบการติดตั้ง ━━━"
echo ""
if [ -d "$SDK_DIR/platforms/android-34" ]; then echo "${GREEN}✅ Android SDK 34${NC}"; else echo "${RED}❌ Android SDK 34${NC}"; fi
if [ -d "$SDK_DIR/build-tools/34.0.0" ]; then echo "${GREEN}✅ Build Tools 34.0.0${NC}"; else echo "${RED}❌ Build Tools 34.0.0${NC}"; fi
if [ -d "$SDK_DIR/ndk/26.1.10909125" ]; then echo "${GREEN}✅ NDK 26.1.10909125${NC}"; else echo "${RED}❌ NDK 26.1.10909125${NC}"; fi
if [ -d "$SDK_DIR/cmake/3.22.1" ]; then echo "${GREEN}✅ CMake 3.22.1${NC}"; else echo "${RED}❌ CMake 3.22.1${NC}"; fi
if command -v sdkmanager >/dev/null 2>&1; then echo "${GREEN}✅ sdkmanager พร้อม${NC}"; else echo "${RED}❌ sdkmanager${NC}"; fi
if command -v java >/dev/null 2>&1; then echo "${GREEN}✅ Java พร้อม${NC}"; else echo "${RED}❌ Java${NC}"; fi

echo ""
echo "${GREEN}══════════════════════════════════════════${NC}"
echo "${GREEN}  ✅ SDK FIX COMPLETE!${NC}"
echo "${GREEN}══════════════════════════════════════════${NC}"
echo ""
echo "🚀 Build APK:"
echo ""
echo "   cd ~/aether-mind-v3/Aether"
echo "   export JAVA_HOME=/usr/lib/jvm/java-17-openjdk"
echo "   export ANDROID_HOME=\$HOME/android-sdk"
echo "   ./gradlew assembleDebug --no-daemon --console=plain"