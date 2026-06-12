#!/system/bin/sh
# ============================================================
# AETHER APK BUILDER — ONE SHOT
# 1) เช็ค / ติดตั้ง SDK
# 2) Build APK
# 3) แจ้งผลสำเร็จ / Error
# ============================================================

# หยุดทันทีถ้า error (เพื่อให้เห็นจุดพัง)
set -e

GREEN='\033[92m'; YELLOW='\033[93m'; RED='\033[91m'; CYAN='\033[96m'; NC='\033[0m'

echo "${CYAN}"
echo "╔══════════════════════════════════════════╗"
echo "║     🔧 AETHER APK BUILDER — ONE SHOT    ║"
echo "║     ติดตั้ง SDK + Build APK ในครั้งเดียว  ║"
echo "╚══════════════════════════════════════════╝"
echo "${NC}"

SDK_DIR="$HOME/android-sdk"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# ============================================================
# STEP 0: ตรวจสอบเครื่องมือพื้นฐาน
# ============================================================
step_0() {
    echo ""
    echo "━━━ [0/5] ตรวจสอบเครื่องมือพื้นฐาน ━━━"

    if command -v curl >/dev/null 2>&1; then echo "${GREEN}  ✅ curl${NC}"; else pkg install -y curl; fi
    if command -v unzip >/dev/null 2>&1; then echo "${GREEN}  ✅ unzip${NC}"; else pkg install -y unzip; fi
    if command -v java >/dev/null 2>&1; then
        JV=$(java -version 2>&1 | head -1)
        echo "${GREEN}  ✅ Java: $JV${NC}"
    else
        echo "${YELLOW}  ⚠️  ติดตั้ง Java 17...${NC}"
        pkg install -y openjdk-17
    fi
}

# ============================================================
# STEP 1: ติดตั้ง Android SDK + NDK
# ============================================================
step_1() {
    echo ""
    echo "━━━ [1/5] ติดตั้ง Android SDK + NDK ━━━"

    if [ -f "$SDK_DIR/cmdline-tools/latest/bin/sdkmanager" ]; then
        echo "${GREEN}  ✅ SDK มีอยู่แล้ว${NC}"
        return
    fi

    echo "${YELLOW}  📥 ดาวน์โหลด commandline tools (~100MB)...${NC}"
    mkdir -p "$SDK_DIR"
    cd /tmp
    curl -L -o cmdline-tools.zip \
      "https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip" \
      --progress-bar 2>&1
    unzip -q cmdline-tools.zip
    mkdir -p "$SDK_DIR/cmdline-tools"
    mv cmdline-tools "$SDK_DIR/cmdline-tools/latest"
    rm -f cmdline-tools.zip

    export PATH="$PATH:$SDK_DIR/cmdline-tools/latest/bin"
    export ANDROID_HOME="$SDK_DIR"

    echo "${YELLOW}  ✅ Accept licenses...${NC}"
    yes | sdkmanager --licenses >/dev/null 2>&1 || true
}

# ============================================================
# STEP 2: ติดตั้ง SDK Components
# ============================================================
step_2() {
    echo ""
    echo "━━━ [2/5] ติดตั้ง SDK Components ━━━"

    export PATH="$PATH:$SDK_DIR/cmdline-tools/latest/bin"
    export ANDROID_HOME="$SDK_DIR"

    if [ ! -d "$SDK_DIR/platforms/android-34" ]; then
        echo "${YELLOW}  📥 Android SDK 34...${NC}"
        sdkmanager "platforms;android-34" 2>&1 | tail -1
    else
        echo "${GREEN}  ✅ Android SDK 34${NC}"
    fi

    if [ ! -d "$SDK_DIR/build-tools/34.0.0" ]; then
        echo "${YELLOW}  📥 Build Tools 34.0.0...${NC}"
        sdkmanager "build-tools;34.0.0" 2>&1 | tail -1
    else
        echo "${GREEN}  ✅ Build Tools 34.0.0${NC}"
    fi

    if [ ! -d "$SDK_DIR/ndk/26.1.10909125" ]; then
        echo "${YELLOW}  📥 NDK 26.1.10909125...${NC}"
        sdkmanager "ndk;26.1.10909125" 2>&1 | tail -1
    else
        echo "${GREEN}  ✅ NDK 26.1.10909125${NC}"
    fi

    if [ ! -d "$SDK_DIR/cmake/3.22.1" ]; then
        echo "${YELLOW}  📥 CMake 3.22.1...${NC}"
        sdkmanager "cmake;3.22.1" 2>&1 | tail -1
    else
        echo "${GREEN}  ✅ CMake 3.22.1${NC}"
    fi
}

# ============================================================
# STEP 3: Clone / Pull Project & ตั้งค่า Gradle
# ============================================================
step_3() {
    echo ""
    echo "━━━ [3/5] โหลด Project ━━━"

    cd ~
    if [ ! -d "aether-mind-v3" ]; then
        echo "${YELLOW}  📥 โหลด project...${NC}"
        git clone https://github.com/Ticker27/aether-mind-v3.git
    else
        echo "${GREEN}  ✅ Project มีแล้ว${NC}"
        cd aether-mind-v3
        git pull 2>/dev/null || true
    fi

    # ตั้งค่า Gradle properties
    mkdir -p ~/.gradle
    cat > ~/.gradle/gradle.properties << 'EOF'
org.gradle.jvmargs=-Xmx2g -XX:MaxMetaspaceSize=512m
org.gradle.parallel=true
android.useAndroidX=true
android.enableJetifier=true
EOF
    echo "${GREEN}  ✅ Gradle properties${NC}"
}

# ============================================================
# STEP 4: Build APK
# ============================================================
step_4() {
    echo ""
    echo "━━━ [4/5] Build APK ━━━"

    cd ~/aether-mind-v3/Aether

    export JAVA_HOME=/usr/lib/jvm/java-17-openjdk
    export ANDROID_HOME="$SDK_DIR"
    export PATH="$PATH:$SDK_DIR/cmdline-tools/latest/bin"
    export PATH="$PATH:$SDK_DIR/platform-tools"

    chmod +x gradlew
    echo "${YELLOW}  🔨 กำลัง Build APK (รอ ~5-10 นาที)...${NC}"
    echo ""

    ./gradlew assembleDebug --no-daemon --console=plain 2>&1
}

# ============================================================
# STEP 5: ตรวจสอบผลลัพธ์
# ============================================================
step_5() {
    echo ""
    echo "━━━ [5/5] ตรวจสอบผลลัพธ์ ━━━"

    APK_PATH="$HOME/aether-mind-v3/Aether/app/build/outputs/apk/debug/app-debug.apk"

    if [ -f "$APK_PATH" ]; then
        SIZE=$(ls -lh "$APK_PATH" | awk '{print $5}')
        echo ""
        echo "${GREEN}"
        echo "╔══════════════════════════════════════════╗"
        echo "║        ✅ BUILD SUCCESSFUL!              ║"
        echo "╚══════════════════════════════════════════╝"
        echo "${NC}"
        echo "  📦 APK: $APK_PATH"
        echo "  📏 Size: $SIZE"
        echo ""
        echo "  📲 ติดตั้ง: adb install -r \"$APK_PATH\""
        echo "  หรือกดที่ไฟล์ใน File Manager"
    else
        echo ""
        echo "${RED}"
        echo "╔══════════════════════════════════════════╗"
        echo "║        ❌ BUILD FAILED                    ║"
        echo "╚══════════════════════════════════════════╝"
        echo "${NC}"
        echo "  ดู Error ด้านบนเพื่อหาสาเหตุ"
        echo "  หรือแคปหน้าจอมาให้ผมดู"
    fi
}

# ============================================================
# EXECUTE
# ============================================================
step_0
step_1
step_2
step_3
step_4
step_5

echo ""
echo "${CYAN}══════════════════════════════════════════${NC}"
echo "${CYAN}  เสร็จสิ้น — ขอบคุณที่ใช้ AETHER BUILDER${NC}"
echo "${CYAN}══════════════════════════════════════════${NC}"