#!/system/bin/sh
# ============================================================
# AETHER APK BUILDER — ONE SHOT
# 1) เช็ค / ติดตั้ง SDK
# 2) Build APK
# 3) แจ้งผลสำเร็จ / Error
# ============================================================

set -e

GREEN='\033[92m'; YELLOW='\033[93m'; RED='\033[91m'; CYAN='\033[96m'; NC='\033[0m'

echo "${CYAN}"
echo "╔══════════════════════════════════════════╗"
echo "║     🔧 AETHER APK BUILDER — ONE SHOT    ║"
echo "║     ติดตั้ง SDK + Build APK ในครั้งเดียว  ║"
echo "╚══════════════════════════════════════════╝"
echo "${NC}"

SDK_DIR="$HOME/android-sdk"
TMP_DIR="$HOME/.cache/aether_build"
mkdir -p "$TMP_DIR"

# ============================================================
# STEP 0
# ============================================================
step_0() {
    echo ""
    echo "━━━ [0/5] ตรวจสอบเครื่องมือพื้นฐาน ━━━"

    if command -v curl >/dev/null 2>&1; then echo "  ✅ curl"; else pkg install -y curl; fi
    if command -v unzip >/dev/null 2>&1; then echo "  ✅ unzip"; else pkg install -y unzip; fi
    if command -v java >/dev/null 2>&1; then
        JV=$(java -version 2>&1 | head -1)
        echo "  ✅ Java: $JV"
    else
        echo "  ⚠️  ติดตั้ง Java 17..."
        pkg install -y openjdk-17
    fi
}

# ============================================================
# STEP 1
# ============================================================
step_1() {
    echo ""
    echo "━━━ [1/5] ติดตั้ง Android SDK + NDK ━━━"

    SDK_BIN="$SDK_DIR/cmdline-tools/latest/bin/sdkmanager"
    if [ -f "$SDK_BIN" ]; then
        echo "  ✅ SDK มีอยู่แล้ว"
        export PATH="$PATH:$SDK_DIR/cmdline-tools/latest/bin"
        export ANDROID_HOME="$SDK_DIR"
        return
    fi

    echo "  📥 ดาวน์โหลด commandline tools (~100MB)..."
    mkdir -p "$SDK_DIR"
    cd "$TMP_DIR"

    curl -L -o cmdline-tools.zip \
      "https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip"

    if [ ! -f cmdline-tools.zip ]; then
        echo "  ❌ ดาวน์โหลดไม่สำเร็จ — เช็คอินเทอร์เน็ต"
        exit 1
    fi

    unzip -q cmdline-tools.zip
    mkdir -p "$SDK_DIR/cmdline-tools"
    mv cmdline-tools "$SDK_DIR/cmdline-tools/latest"
    rm -f cmdline-tools.zip

    export PATH="$PATH:$SDK_DIR/cmdline-tools/latest/bin"
    export ANDROID_HOME="$SDK_DIR"

    echo "  ✅ Accept licenses..."
    yes | sdkmanager --licenses >/dev/null 2>&1 || true
}

# ============================================================
# STEP 2
# ============================================================
step_2() {
    echo ""
    echo "━━━ [2/5] ติดตั้ง SDK Components ━━━"

    export PATH="$PATH:$SDK_DIR/cmdline-tools/latest/bin"
    export ANDROID_HOME="$SDK_DIR"

    if [ ! -d "$SDK_DIR/platforms/android-34" ]; then
        echo "  📥 Android SDK 34..."
        sdkmanager "platforms;android-34" >/dev/null 2>&1 || echo "  ⚠️ SDK 34 อาจติดไม่สมบูรณ์"
    else
        echo "  ✅ Android SDK 34"
    fi

    if [ ! -d "$SDK_DIR/build-tools/34.0.0" ]; then
        echo "  📥 Build Tools 34.0.0..."
        sdkmanager "build-tools;34.0.0" >/dev/null 2>&1 || echo "  ⚠️ Build Tools อาจติดไม่สมบูรณ์"
    else
        echo "  ✅ Build Tools 34.0.0"
    fi

    if [ ! -d "$SDK_DIR/ndk/26.1.10909125" ]; then
        echo "  📥 NDK 26.1.10909125..."
        sdkmanager "ndk;26.1.10909125" >/dev/null 2>&1 || echo "  ⚠️ NDK อาจติดไม่สมบูรณ์"
    else
        echo "  ✅ NDK 26.1.10909125"
    fi

    if [ ! -d "$SDK_DIR/cmake/3.22.1" ]; then
        echo "  📥 CMake 3.22.1..."
        sdkmanager "cmake;3.22.1" >/dev/null 2>&1 || echo "  ⚠️ CMake อาจติดไม่สมบูรณ์"
    else
        echo "  ✅ CMake 3.22.1"
    fi
}

# ============================================================
# STEP 3
# ============================================================
step_3() {
    echo ""
    echo "━━━ [3/5] โหลด Project ━━━"

    cd ~
    if [ ! -d "aether-mind-v3" ]; then
        echo "  📥 โหลด project..."
        git clone https://github.com/Ticker27/aether-mind-v3.git
    else
        echo "  ✅ Project มีแล้ว"
        cd aether-mind-v3
        git pull 2>/dev/null || true
    fi

    mkdir -p ~/.gradle
    cat > ~/.gradle/gradle.properties << 'EOF'
org.gradle.jvmargs=-Xmx2g -XX:MaxMetaspaceSize=512m
org.gradle.parallel=true
android.useAndroidX=true
android.enableJetifier=true
EOF
    echo "  ✅ Gradle properties"
}

# ============================================================
# STEP 4
# ============================================================
step_4() {
    echo ""
    echo "━━━ [4/5] Build APK ━━━"

    cd ~/aether-mind-v3/Aether

    export JAVA_HOME=/usr/lib/jvm/java-17-openjdk
    export ANDROID_HOME="$SDK_DIR"
    export PATH="$PATH:$SDK_DIR/cmdline-tools/latest/bin"

    chmod +x gradlew
    echo "  🔨 กำลัง Build APK (รอ ~5-10 นาที)..."
    echo ""

    ./gradlew assembleDebug --no-daemon --console=plain 2>&1
}

# ============================================================
# STEP 5
# ============================================================
step_5() {
    echo ""
    echo "━━━ [5/5] ตรวจสอบผลลัพธ์ ━━━"

    APK_PATH="$HOME/aether-mind-v3/Aether/app/build/outputs/apk/debug/app-debug.apk"

    if [ -f "$APK_PATH" ]; then
        SIZE=$(ls -lh "$APK_PATH" | awk '{print $5}')
        echo ""
        echo "╔══════════════════════════════════════════╗"
        echo "║        ✅ BUILD SUCCESSFUL!              ║"
        echo "╚══════════════════════════════════════════╝"
        echo ""
        echo "  📦 APK: $APK_PATH"
        echo "  📏 Size: $SIZE"
        echo ""
        echo "  📲 ติดตั้ง: adb install -r \"$APK_PATH\""
    else
        echo ""
        echo "╔══════════════════════════════════════════╗"
        echo "║        ❌ BUILD FAILED                    ║"
        echo "╚══════════════════════════════════════════╝"
        echo ""
        echo "  ดู Error ด้านบน—แคปหน้าจอมาให้ผมดู"
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
echo "${CYAN}  เสร็จสิ้น${NC}"
echo "${CYAN}══════════════════════════════════════════${NC}"