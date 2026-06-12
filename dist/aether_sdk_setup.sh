#!/system/bin/sh
# ============================================================
# AETHER SDK SETUP — ตั้งค่า Termux สำหรับ Build APK
# รันครั้งเดียว รอจนจบ (~10-15 นาที)
# ============================================================

set -e

echo "=========================================="
echo "  🔧 AETHER SDK SETUP"
echo "  ติดตั้ง Android SDK + NDK สำหรับ Build APK"
echo "=========================================="
echo ""

# 0. ติดตั้งพื้นฐาน
echo "📦 ติดตั้ง packages พื้นฐาน..."
pkg update -y
pkg upgrade -y
pkg install -y x11-repo
pkg install -y git wget curl zip unzip openjdk-17

# 1. ติดตั้ง Android SDK
echo ""
echo "📱 ติดตั้ง Android SDK..."
SDK_DIR="$HOME/android-sdk"
mkdir -p "$SDK_DIR"

# ดาวน์โหลด commandline tools
cd /tmp
curl -L -o cmdline-tools.zip "https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip"
unzip -q cmdline-tools.zip
mkdir -p "$SDK_DIR/cmdline-tools"
mv cmdline-tools "$SDK_DIR/cmdline-tools/latest"

# ตั้งค่า PATH
export ANDROID_HOME="$SDK_DIR"
export PATH="$PATH:$ANDROID_HOME/cmdline-tools/latest/bin"

# Accept licenses
yes | sdkmanager --licenses > /dev/null 2>&1 || true

# 2. ติดตั้ง SDK components
echo ""
echo "📦 ติดตั้ง SDK components..."
sdkmanager "platforms;android-34" "build-tools;34.0.0" "ndk;26.1.10909125" "cmake;3.22.1"

# 3. สร้าง gradle.properties
echo ""
echo "⚙️  ตั้งค่า Gradle..."
mkdir -p ~/.gradle
cat > ~/.gradle/gradle.properties << 'EOF'
org.gradle.jvmargs=-Xmx2g -XX:MaxMetaspaceSize=512m
org.gradle.parallel=true
android.useAndroidX=true
android.enableJetifier=true
EOF

# 4. เพิ่ม PATH ไปยัง ~/.bashrc
echo "
# Android SDK
export ANDROID_HOME=\$HOME/android-sdk
export PATH=\$PATH:\$ANDROID_HOME/cmdline-tools/latest/bin
export PATH=\$PATH:\$ANDROID_HOME/platform-tools
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk
" >> ~/.bashrc

# 5. Clone project
echo ""
echo "📥 ดาวน์โหลด AETHER project..."
cd ~
if [ -d "aether-mind-v3" ]; then
    cd aether-mind-v3 && git pull
else
    git clone https://github.com/Ticker27/aether-mind-v3.git
fi

echo ""
echo "=========================================="
echo "  ✅ SETUP COMPLETE!"
echo "=========================================="
echo ""
echo "🚀 วิธี Build APK:"
echo ""
echo "   cd ~/aether-mind-v3/Aether"
echo "   export JAVA_HOME=/usr/lib/jvm/java-17-openjdk"
echo "   chmod +x gradlew"
echo "   ./gradlew assembleDebug"
echo ""
echo "📦 APK จะอยู่ที่:"
echo "   app/build/outputs/apk/debug/app-debug.apk"
echo ""
echo "💡 หรือรันครั้งเดียว:"
echo "   sh ~/aether-mind-v3/build_apk.sh"