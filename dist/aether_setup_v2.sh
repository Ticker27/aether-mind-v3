#!/system/bin/sh
# ============================================================
# AETHER TERMUX SETUP v2
# เช็คก่อน มี = ข้าม, ไม่มี = อัปเดต
# ใช้เวอร์ชันที่เสถียรที่สุด
# ============================================================

set -e

GREEN='\033[92m'
YELLOW='\033[93m'
RED='\033[91m'
CYAN='\033[96m'
NC='\033[0m'

echo "${CYAN}"
echo "=========================================="
echo "  🔧 AETHER TERMUX SETUP v2"
echo "  เช็คก่อน → มีแล้วข้าม → ไม่มีติดตั้ง"
echo "=========================================="
echo "${NC}"
echo ""

# SDK & NDK เวอร์ชันเสถียรที่สุด (ทดสอบแล้ว)
SDK_VERSION="platforms;android-34"
BUILD_TOOLS="build-tools;34.0.0"
NDK_VERSION="ndk;26.1.10909125"
CMAKE_VERSION="cmake;3.22.1"
JAVA_VERSION="17"
GRADLE_VERSION="8.5"

SDK_DIR="$HOME/android-sdk"
CHECKPASS=0
CHECKFAIL=0
INSTALLED=0

check() {
    if [ "$1" = true ]; then
        echo "  ${GREEN}✅ $2${NC}"
        CHECKPASS=$((CHECKPASS + 1))
    else
        echo "  ${YELLOW}⚠️  $3${NC}"
        CHECKFAIL=$((CHECKFAIL + 1))
    fi
}

install_sdk() {
    echo ""
    echo "📥 กำลังติดตั้ง $1..."
    sdkmanager "$1" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "  ${GREEN}✅ ติดตั้ง $1 สำเร็จ${NC}"
        INSTALLED=$((INSTALLED + 1))
    else
        echo "  ${RED}❌ ติดตั้ง $1 ล้มเหลว${NC}"
    fi
}

# ============================================
# 1. ตรวจสอบ Java
# ============================================
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " ☕ ตรวจสอบ Java"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

JAVA_PATH="/usr/lib/jvm/java-${JAVA_VERSION}-openjdk/bin/java"
if [ -f "$JAVA_PATH" ]; then
    JAVA_VER=$("$JAVA_PATH" -version 2>&1 | head -1 | grep -o "version \"[^\"]*\"" | tr -d '"version')
    check true "Java $JAVA_VER พร้อม" ""
else
    check false "" "Java $JAVA_VERSION — กำลังติดตั้ง..."
    pkg install -y openjdk-${JAVA_VERSION}
fi

# ============================================
# 2. ตรวจสอบ Android SDK
# ============================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " 📱 ตรวจสอบ Android SDK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ตรวจสอบว่ามี sdkmanager หรือไม่
if command -v sdkmanager >/dev/null 2>&1; then
    check true "sdkmanager พร้อม" ""
else
    # ตรวจสอบ SDK directory
    if [ -d "$SDK_DIR/cmdline-tools/latest/bin" ]; then
        export PATH="$PATH:$SDK_DIR/cmdline-tools/latest/bin"
        export ANDROID_HOME="$SDK_DIR"
        check true "sdkmanager (PATH ถูกตั้งค่า)" ""
    else
        check false "" "Android SDK — กำลังติดตั้ง commandline tools..."
        mkdir -p "$SDK_DIR"
        cd /tmp
        curl -L -o cmdline-tools.zip "https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip" 2>/dev/null
        unzip -q cmdline-tools.zip 2>/dev/null
        mkdir -p "$SDK_DIR/cmdline-tools"
        mv cmdline-tools "$SDK_DIR/cmdline-tools/latest" 2>/dev/null
        rm -f cmdline-tools.zip
        export PATH="$PATH:$SDK_DIR/cmdline-tools/latest/bin"
        export ANDROID_HOME="$SDK_DIR"
        yes | sdkmanager --licenses >/dev/null 2>&1 || true
        echo "  ${GREEN}✅ ติดตั้ง sdkmanager สำเร็จ${NC}"
        INSTALLED=$((INSTALLED + 1))
    fi
fi

# ============================================
# 3. ตรวจสอบ Platform SDK
# ============================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " 🏗️  ตรวจสอบ SDK Components"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Platform SDK
if [ -d "$SDK_DIR/platforms/android-34" ]; then
    check true "Android SDK 34 (platforms)" ""
else
    check false "" "Android SDK 34 — กำลังติดตั้ง..."
    install_sdk "$SDK_VERSION"
fi

# Build Tools
if [ -d "$SDK_DIR/build-tools/34.0.0" ]; then
    check true "Build Tools 34.0.0" ""
else
    check false "" "Build Tools 34.0.0 — กำลังติดตั้ง..."
    install_sdk "$BUILD_TOOLS"
fi

# NDK
if [ -d "$SDK_DIR/ndk/26.1.10909125" ]; then
    check true "NDK 26.1.10909125 (เสถียร)" ""
else
    check false "" "NDK 26.1.10909125 — กำลังติดตั้ง..."
    install_sdk "$NDK_VERSION"
fi

# CMake
if [ -d "$SDK_DIR/cmake/3.22.1" ]; then
    check true "CMake 3.22.1 (เสถียร)" ""
else
    check false "" "CMake 3.22.1 — กำลังติดตั้ง..."
    install_sdk "$CMAKE_VERSION"
fi

# ============================================
# 4. ตรวจสอบ Gradle Wrapper
# ============================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " 🏗️  ตรวจสอบ Build Project"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd ~
if [ -d "aether-mind-v3" ]; then
    check true "Project aether-mind-v3 พร้อม" ""
    cd aether-mind-v3
    git pull 2>/dev/null || true
else
    check false "" "Project — กำลังโหลด..."
    git clone https://github.com/Ticker27/aether-mind-v3.git
    cd aether-mind-v3
fi

if [ -f "Aether/gradle/wrapper/gradle-wrapper.jar" ]; then
    check true "Gradle Wrapper พร้อม" ""
else
    check false "" "Gradle Wrapper — กำลังสร้าง..."
    cd Aether
    gradle wrapper --gradle-version $GRADLE_VERSION 2>/dev/null || true
    cd ..
fi

# ============================================
# 5. ตั้งค่า environment variables
# ============================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " ⚙️  ตั้งค่า Environment"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# เขียน gradle.properties
mkdir -p ~/.gradle
cat > ~/.gradle/gradle.properties << 'EOF'
org.gradle.jvmargs=-Xmx2g -XX:MaxMetaspaceSize=512m
org.gradle.parallel=true
android.useAndroidX=true
android.enableJetifier=true
EOF
check true "Gradle properties ตั้งค่าแล้ว" ""

# เพิ่ม PATH ถ้ายังไม่มี
grep -q "ANDROID_HOME" ~/.bashrc 2>/dev/null || {
    cat >> ~/.bashrc << EOF

# AETHER SDK
export ANDROID_HOME=\$HOME/android-sdk
export PATH=\$PATH:\$ANDROID_HOME/cmdline-tools/latest/bin
export PATH=\$PATH:\$ANDROID_HOME/platform-tools
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk
EOF
    check true "PATH ตั้งค่าแล้ว (bashrc)" ""
}

# ============================================
# สรุปผล
# ============================================
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " 📊 สรุปผล"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  ${GREEN}✅ มีอยู่แล้ว: $CHECKPASS${NC}"
echo "  ${YELLOW}⚠️  ติดตั้งเพิ่ม: $INSTALLED${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "${GREEN}✅ SETUP COMPLETE!${NC}"
echo ""
echo "🚀 Build APK:"
echo ""
echo "   cd ~/aether-mind-v3/Aether"
echo "   export JAVA_HOME=/usr/lib/jvm/java-17-openjdk"
echo "   export ANDROID_HOME=\$HOME/android-sdk"
echo "   ./gradlew assembleDebug --no-daemon --console=plain"
echo ""
echo "📦 APK: app/build/outputs/apk/debug/app-debug.apk"