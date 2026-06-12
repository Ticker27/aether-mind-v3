#!/system/bin/sh
# AETHER TERMUX SETUP FINAL
# เช็คก่อนติดตั้ง ใช้เวอร์ชันเสถียร

GREEN='\033[92m'; YELLOW='\033[93m'; RED='\033[91m'; CYAN='\033[96m'; NC='\033[0m'
SDK_DIR="$HOME/android-sdk"
PASS=0; FAIL=0; INST=0

ok() { echo "  ${GREEN}✅ $1${NC}"; PASS=$((PASS+1)); }
warn() { echo "  ${YELLOW}⚠️  $1${NC}"; FAIL=$((FAIL+1)); }
inst() { echo "  ${GREEN}✅ ติดตั้ง $1 สำเร็จ${NC}"; INST=$((INST+1)); }

echo "${CYAN}══════════════════════════════════════════════════${NC}"
echo "${CYAN}  🔧 AETHER TERMUX SETUP — FINAL${NC}"
echo "${CYAN}  เช็คก่อน มีแล้วข้าม ไม่มีติดตั้ง${NC}"
echo "${CYAN}══════════════════════════════════════════════════${NC}"
echo ""

# 1. JAVA
echo "━━━ ☕ Java ━━━"
JAVA_PATH="/usr/lib/jvm/java-17-openjdk/bin/java"
if [ -f "$JAVA_PATH" ]; then
    JV=$("$JAVA_PATH" -version 2>&1 | head -1 | grep -oP 'version "\K[^"]+')
    ok "Java $JV"
else
    warn "กำลังติดตั้ง Java 17..."
    pkg install -y openjdk-17 2>/dev/null && inst "Java 17"
fi

# 2. ANDROID SDK
echo ""; echo "━━━ 📱 Android SDK ━━━"
if [ -d "$SDK_DIR/platforms" ] || [ -d "$PREFIX/lib/android-sdk" ]; then
    ok "Android SDK $([ -d "$PREFIX/lib/android-sdk" ] && echo '(via pkg)' || echo '(manual)')"
    [ ! -d "$SDK_DIR" ] && [ -d "$PREFIX/lib/android-sdk" ] && ln -sf "$PREFIX/lib/android-sdk" "$SDK_DIR" 2>/dev/null
else
    warn "กำลังติดตั้ง Android SDK (Termux mirror)..."
    pkg install -y android-sdk 2>/dev/null
    if [ -d "$PREFIX/lib/android-sdk" ]; then
        ln -sf "$PREFIX/lib/android-sdk" "$SDK_DIR" 2>/dev/null
        ok "Android SDK (pkg)"
    else
        warn "Android SDK ติดตั้งไม่สมบูรณ์ — ลอง: pkg install android-sdk"
    fi
fi

# 3. SDK COMPONENTS
echo ""; echo "━━━ 🏗️ SDK Components ━━━"
# ทดสอบ sdkmanager
CMDS=""
if command -v sdkmanager >/dev/null 2>&1; then
    CMDS="sdkmanager"
elif [ -f "$SDK_DIR/cmdline-tools/latest/bin/sdkmanager" ]; then
    CMDS="$SDK_DIR/cmdline-tools/latest/bin/sdkmanager"
fi

install_comp() {
    NAME=$1; PACKAGE=$2; DIR=$3
    if [ -d "$DIR" ]; then
        ok "$NAME"
    else
        warn "กำลังติดตั้ง $NAME..."
        if [ -n "$CMDS" ]; then
            yes | $CMDS "$PACKAGE" 2>/dev/null && inst "$NAME"
        else
            warn "ไม่มี sdkmanager — ลอง: sdkmanager $PACKAGE"
        fi
    fi
}

install_comp "Android SDK 34" "platforms;android-34" "$SDK_DIR/platforms/android-34"
install_comp "Build Tools 34.0.0" "build-tools;34.0.0" "$SDK_DIR/build-tools/34.0.0"
install_comp "NDK 26.1.10909125" "ndk;26.1.10909125" "$SDK_DIR/ndk/26.1.10909125"
install_comp "CMake 3.22.1" "cmake;3.22.1" "$SDK_DIR/cmake/3.22.1"

# 4. GRADLE WRAPPER
echo ""; echo "━━━ 📦 Project ━━━"
cd ~
if [ ! -d "aether-mind-v3" ]; then
    warn "กำลังโหลด project..."
    git clone https://github.com/Ticker27/aether-mind-v3.git 2>/dev/null && ok "Project cloned"
else
    ok "Project aether-mind-v3"
    cd aether-mind-v3 && git pull 2>/dev/null || true
fi

if [ -f "aether-mind-v3/Aether/gradle/wrapper/gradle-wrapper.jar" ]; then
    ok "Gradle wrapper"
else
    warn "Gradle wrapper มาไม่สมบูรณ์ — โปรดตรวจสอบไฟล์ gradle-wrapper.jar"
fi

# 5. ENV SETUP
echo ""; echo "━━━ ⚙️ Config ━━━"
mkdir -p ~/.gradle
cat > ~/.gradle/gradle.properties << 'ENVEOF'
org.gradle.jvmargs=-Xmx2g -XX:MaxMetaspaceSize=512m
org.gradle.parallel=true
android.useAndroidX=true
android.enableJetifier=true
ENVEOF
ok "Gradle properties"

grep -q "ANDROID_HOME" ~/.bashrc 2>/dev/null || {
    echo "export ANDROID_HOME=\$HOME/android-sdk" >> ~/.bashrc
    echo "export PATH=\$PATH:\$ANDROID_HOME/platform-tools" >> ~/.bashrc
    echo "export JAVA_HOME=/usr/lib/jvm/java-17-openjdk" >> ~/.bashrc
    ok "PATH ตั้งค่าใน bashrc"
}

# SUMMARY
echo ""; echo "${CYAN}══════════════════════════════════════════════════${NC}"
echo "  ✅ มีอยู่แล้ว: $PASS"
echo "  📦 ติดตั้งเพิ่ม: $INST"
echo "  ⚠️  ที่ต้องตรวจสอบ: $FAIL"
echo "${CYAN}══════════════════════════════════════════════════${NC}"
echo ""; echo "🚀 Build: cd ~/aether-mind-v3/Aether && JAVA_HOME=/usr/lib/jvm/java-17-openjdk ./gradlew assembleDebug"
echo "📦 APK: app/build/outputs/apk/debug/app-debug.apk"
