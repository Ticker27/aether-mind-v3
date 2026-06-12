#!/system/bin/sh
# ============================================================
# AETHER FORGE v4.0 — Unified Build Script
# ============================================================
# รวม: BUILD SYSTEM (เขา) + PHYSICS ENGINE (เรา) + UI CONTROL (เขา)
# ============================================================

set -e
trap 'echo -e "\033[0;31m[ERROR]\033[0m Forge failed at line $LINENO"; exit 1' ERR

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; NC='\033[0m'
log() { echo -e "${GREEN}[✓]${NC} $1"; }
step() { echo -e "\n${CYAN}[PHASE]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }

PROJECT="AetherForge"
PROJECT_DIR="$HOME/$PROJECT"
SDK_DIR="$HOME/android-sdk"
TMP="$HOME/.cache/aether_build"
PACKAGE="com/aetherlab/billiards/ai/visionagent"
PACKAGE_NAME="com.aetherlab.billiards.ai.visionagent"
NDK_VER="26.1.10909125"
BT_VER="34.0.0"
CMAK_VER="3.22.1"

mkdir -p "$TMP"

# ─── PHASE 1: ENVIRONMENT ───
step "Setting up environment..."
pkg update -y -qq 2>/dev/null; pkg upgrade -y -qq 2>/dev/null
for p in git curl unzip openjdk-17 cmake ninja; do
    pkg install -y "$p" 2>/dev/null || true
done

export JAVA_HOME="/data/data/com.termux/files/usr/lib/jvm/java-17-openjdk"
export PATH="$JAVA_HOME/bin:$PATH"

# SDK
if [ ! -f "$SDK_DIR/cmdline-tools/latest/bin/sdkmanager" ]; then
    mkdir -p "$SDK_DIR/cmdline-tools" && cd "$SDK_DIR/cmdline-tools"
    curl -L -o cmdline-tools.zip "https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip" --progress-bar
    unzip -qo cmdline-tools.zip 2>/dev/null; mv cmdline-tools latest 2>/dev/null || true; rm -f cmdline-tools.zip
fi
export ANDROID_HOME="$SDK_DIR"
export PATH="$SDK_DIR/cmdline-tools/latest/bin:$PATH"
yes | sdkmanager --licenses >/dev/null 2>&1 || true
for comp in "platforms;android-34" "build-tools;${BT_VER}" "ndk;${NDK_VER}" "cmake;${CMAK_VER}"; do
    sdkmanager --install "$comp" 2>/dev/null || true
done
log "Environment ready"

# ─── PHASE 2: CREATE PROJECT ───
step "Creating AetherForge project..."
rm -rf "$PROJECT_DIR"

DIRS=(
    "app/src/main/java/$PACKAGE/services"
    "app/src/main/java/$PACKAGE/ai"
    "app/src/main/jni/core" "app/src/main/jni/brain"
    "app/src/main/res/layout" "app/src/main/res/values" "app/src/main/res/xml"
    "app/src/main/assets" "gradle/wrapper"
)
for d in "${DIRS[@]}"; do mkdir -p "$PROJECT_DIR/$d"; done

# ─── BUILD FILES ───
cat > "$PROJECT_DIR/settings.gradle" << 'EOF'
pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }
dependencyResolutionManagement { repositoriesMode.set(RepositoriesMode.PREFER_SETTINGS); repositories { google(); mavenCentral() } }
rootProject.name = "AetherForge"; include ':app'
EOF

cat > "$PROJECT_DIR/build.gradle" << 'EOF'
plugins { id 'com.android.application' version '8.1.0' apply false }
EOF

cat > "$PROJECT_DIR/gradle.properties" << 'EOF'
org.gradle.jvmargs=-Xmx2048m
android.useAndroidX=true
android.nonTransitiveRClass=true
EOF

cat > "$PROJECT_DIR/gradle/wrapper/gradle-wrapper.properties" << 'EOF'
distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\://services.gradle.org/distributions/gradle-8.4-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
EOF

cat > "$PROJECT_DIR/app/build.gradle" << 'EOF'
plugins { id 'com.android.application' }
android {
    namespace 'com.aetherlab.billiards.ai.visionagent'; compileSdk 34
    defaultConfig {
        applicationId "com.aetherlab.billiards.ai.visionagent"; minSdk 26; targetSdk 34
        versionCode 4; versionName "4.0.0"
        externalNativeBuild { cmake { cppFlags "-std=c++17 -O3"; arguments "-DANDROID_STL=c++_shared" } }
        ndk { abiFilters 'arm64-v8a' }
    }
    buildTypes { release { minifyEnabled false }; debug { debuggable true } }
    externalNativeBuild { cmake { path "src/main/jni/CMakeLists.txt"; version "3.22.1" } }
    compileOptions { sourceCompatibility JavaVersion.VERSION_11; targetCompatibility JavaVersion.VERSION_11 }
}
dependencies { implementation 'androidx.appcompat:appcompat:1.6.1'; implementation 'com.google.android.material:material:1.9.0' }
EOF

# ─── ANDROID MANIFEST ───
cat > "$PROJECT_DIR/app/src/main/AndroidManifest.xml" << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.SYSTEM_ALERT_WINDOW" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <uses-permission android:name="android.permission.BIND_ACCESSIBILITY_SERVICE" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
    <uses-permission android:name="android.permission.INTERNET" />
    <application android:allowBackup="false" android:label="Aether Forge"
        android:supportsRtl="true" android:theme="@style/Theme.AppCompat.Light.NoActionBar">
        <activity android:name=".MainActivity" android:exported="true"
            android:screenOrientation="portrait">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
        <service android:name=".services.TouchService" android:exported="true"
            android:permission="android.permission.BIND_ACCESSIBILITY_SERVICE">
            <intent-filter>
                <action android:name="android.accessibilityservice.AccessibilityService" />
            </intent-filter>
            <meta-data android:name="android.accessibilityservice" android:resource="@xml/accessibility_config" />
        </service>
        <service android:name=".services.AutoPlayService" android:exported="false"
            android:foregroundServiceType="specialUse" />
    </application>
</manifest>
EOF

# ─── RESOURCES ───
cat > "$PROJECT_DIR/app/src/main/res/values/strings.xml" << 'EOF'
<resources>
    <string name="app_name">Aether Forge</string>
    <string name="accessibility_desc">AI touch simulation</string>
</resources>
EOF

cat > "$PROJECT_DIR/app/src/main/res/xml/accessibility_config.xml" << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<accessibility-service xmlns:android="http://schemas.android.com/apk/res/android"
    android:accessibilityEventTypes="typeAllMask" android:accessibilityFeedbackType="feedbackGeneric"
    android:canPerformGestures="true" android:canRetrieveWindowContent="true"
    android:description="@string/accessibility_desc" android:notificationTimeout="100" />
EOF

# ─── LAYOUT: Main Activity ───
cat > "$PROJECT_DIR/app/src/main/res/layout/activity_main.xml" << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:orientation="vertical" android:layout_width="match_parent"
    android:layout_height="match_parent" android:gravity="center"
    android:padding="20dp">
    <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
        android:text="Aether Forge v4.0" android:textSize="24sp"
        android:textStyle="bold" android:layout_marginBottom="10dp"/>
    <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
        android:text="Physics Engine + Auto Play" android:textSize="14sp"
        android:layout_marginBottom="30dp"/>
    <Button android:id="@+id/btn_start" android:layout_width="wrap_content"
        android:layout_height="wrap_content" android:text="Start Auto Play"
        android:layout_marginBottom="10dp"/>
    <Button android:id="@+id/btn_stop" android:layout_width="wrap_content"
        android:layout_height="wrap_content" android:text="Stop"/>
</LinearLayout>
EOF

# ─── JAVA: MainActivity ───
cat > "$PROJECT_DIR/app/src/main/java/$PACKAGE/MainActivity.java" << 'JAVAEOF'
package com.aetherlab.billiards.ai.visionagent;

import android.app.Activity;
import android.content.Intent;
import android.media.projection.MediaProjectionManager;
import android.os.Bundle;
import android.provider.Settings;
import android.widget.Button;
import android.widget.Toast;

public class MainActivity extends Activity {
    private static final int REQUEST_CODE = 1001;
    private MediaProjectionManager mpm;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        mpm = (MediaProjectionManager) getSystemService(MEDIA_PROJECTION_SERVICE);

        findViewById(R.id.btn_start).setOnClickListener(v -> {
            // Start Accessibility first
            if (!isAccessibilityEnabled()) {
                startActivity(new Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS));
                Toast.makeText(this, "Enable TouchService in Accessibility", Toast.LENGTH_LONG).show();
                return;
            }
            // Request screen capture
            startActivityForResult(mpm.createScreenCaptureIntent(), REQUEST_CODE);
        });

        findViewById(R.id.btn_stop).setOnClickListener(v -> {
            stopService(new Intent(this, services.AutoPlayService.class));
            Toast.makeText(this, "Stopped", Toast.LENGTH_SHORT).show();
        });
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == REQUEST_CODE && resultCode == RESULT_OK) {
            // Store projection data then start AutoPlayService
            Intent svc = new Intent(this, services.AutoPlayService.class);
            svc.putExtra("code", resultCode);
            svc.putExtra("data", data);
            startForegroundService(svc);
            Toast.makeText(this, "AutoPlay Active", Toast.LENGTH_SHORT).show();
        }
    }

    private boolean isAccessibilityEnabled() {
        String svc = getPackageName() + "/" + services.TouchService.class.getCanonicalName();
        try {
            int enabled = Settings.Secure.getInt(getContentResolver(), Settings.Secure.ACCESSIBILITY_ENABLED, 0);
            if (enabled == 1) {
                String services = Settings.Secure.getString(getContentResolver(), Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES);
                return services != null && services.contains(svc);
            }
        } catch (Exception ignored) {}
        return false;
    }
}
JAVAEOF

# ─── JAVA: TouchService ───
cat > "$PROJECT_DIR/app/src/main/java/$PACKAGE/services/TouchService.java" << 'JAVAEOF'
package com.aetherlab.billiards.ai.visionagent.services;

import android.accessibilityservice.AccessibilityService;
import android.accessibilityservice.GestureDescription;
import android.graphics.Path;
import android.util.Log;
import android.view.accessibility.AccessibilityEvent;

public class TouchService extends AccessibilityService {
    private static final String TAG = "AetherTouch";
    private static TouchService instance;
    public static TouchService getInstance() { return instance; }

    @Override public void onServiceConnected() { super.onServiceConnected(); instance = this; Log.i(TAG, "TouchService ready"); }
    @Override public void onAccessibilityEvent(AccessibilityEvent e) {}
    @Override public void onInterrupt() {}
    @Override public void onDestroy() { instance = null; }

    public boolean executeDrag(float[] x, float[] y, long[] ts) {
        if (x == null || y == null || x.length < 2) return false;
        Path path = new Path(); path.moveTo(x[0], y[0]);
        GestureDescription.Builder builder = new GestureDescription.Builder();
        long cum = 0;
        for (int i = 1; i < x.length; i++) {
            path.lineTo(x[i], y[i]);
            long dur = Math.max(1, ts[i] - ts[i-1]);
            builder.addStroke(new GestureDescription.StrokeDescription(path, cum, dur));
            cum += dur;
        }
        return dispatchGesture(builder.build(), null, null);
    }
}
JAVAEOF

# ─── C++: CMakeLists ───
cat > "$PROJECT_DIR/app/src/main/jni/CMakeLists.txt" << 'CMAKE_EOF'
cmake_minimum_required(VERSION 3.18.1)
project("aether_agent")
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3")
find_library(log-lib log)
find_library(android-lib android)
set(SOURCES core/agent.cpp)
add_library(aether_agent SHARED ${SOURCES})
target_include_directories(aether_agent PRIVATE ${CMAKE_SOURCE_DIR})
target_link_libraries(aether_agent ${log-lib} ${android-lib})
CMAKE_EOF

# ─── C++: PHYSICS ENGINE (AETHER SHOT) ───
cat > "$PROJECT_DIR/app/src/main/jni/brain/physics_engine.h" << 'PHYEOF'
#pragma once
#include <vector>
#include <cmath>
#include <algorithm>

namespace aether {

struct Ball {
    int id = 0; float x = 0, y = 0; float vx = 0, vy = 0;
    bool active = true, pocketed = false;
    static constexpr float RADIUS = 28.575f, MASS = 0.170f;
};

struct ShotResult {
    bool success = false; int pocketed_ball = -1; int pocket_id = -1;
    bool scratch = false; int steps = 0;
    float aim_angle = 0, power = 0;
};

class PhysicsEngine {
public:
    static constexpr float TABLE_W = 2540, TABLE_H = 1270;
    static constexpr float POCKET_R = 50, FRICTION = 0.985f;
    static constexpr float RESTITUTION = 0.9f, WALL_REST = 0.7f;

    static constexpr float POCKETS[6][2] = {
        {0,0}, {TABLE_W/2,0}, {TABLE_W,0},
        {0,TABLE_H}, {TABLE_W/2,TABLE_H}, {TABLE_W,TABLE_H}
    };
    static constexpr const char* PNAME[6] = {
        "TL","TC","TR","BL","BC","BR"
    };

    std::vector<Ball> balls;

    void setup() {
        balls.clear();
        // Cue + 15 balls in standard rack
        float rack_x = TABLE_W * 0.72f, rack_y = TABLE_H * 0.5f;
        float spacing = TABLE_W * 0.025f;
        int rack[15] = {1,11,2,12,3,8,13,4,14,5,15,6,10,7,9};
        balls.push_back({0, TABLE_W*0.25f, TABLE_H*0.5f, 0,0, true,false});
        int idx = 0;
        for (int row = 0; row < 5; row++) {
            for (int col = 0; col <= row; col++) {
                float x = rack_x + row * spacing * 1.5f;
                float y = rack_y + (col - row/2.0f) * spacing * 1.75f;
                if (idx < 15) balls.push_back({rack[idx++], x, y, 0,0, true,false});
            }
        }
    }

    void apply_shot(float angle_deg, float power) {
        if (balls.empty()) return;
        float rad = angle_deg * M_PI / 180.0f;
        float f = power * 120.0f;
        balls[0].vx = f * cos(rad) / Ball::MASS;
        balls[0].vy = f * sin(rad) / Ball::MASS;
    }

    ShotResult simulate(int max = 800) {
        ShotResult r;
        for (int s = 0; s < max; s++) {
            for (auto& b : balls) {
                if (!b.active || b.pocketed) continue;
                b.x += b.vx * 0.005f; b.y += b.vy * 0.005f;
                b.vx *= FRICTION; b.vy *= FRICTION;
                if (b.x - Ball::RADIUS < 0) { b.x = Ball::RADIUS; b.vx = -b.vx * WALL_REST; }
                if (b.x + Ball::RADIUS > TABLE_W) { b.x = TABLE_W - Ball::RADIUS; b.vx = -b.vx * WALL_REST; }
                if (b.y - Ball::RADIUS < 0) { b.y = Ball::RADIUS; b.vy = -b.vy * WALL_REST; }
                if (b.y + Ball::RADIUS > TABLE_H) { b.y = TABLE_H - Ball::RADIUS; b.vy = -b.vy * WALL_REST; }
                for (int p = 0; p < 6; p++) {
                    float dx = b.x - POCKETS[p][0], dy = b.y - POCKETS[p][1];
                    if (dx*dx + dy*dy < POCKET_R*POCKET_R) {
                        b.pocketed = true; b.vx = 0; b.vy = 0;
                        if (b.id == 0) r.scratch = true;
                        else { r.pocketed_ball = b.id; r.pocket_id = p; }
                        break;
                    }
                }
            }
            // Ball-ball
            for (size_t i = 0; i < balls.size(); i++)
                for (size_t j = i+1; j < balls.size(); j++) {
                    auto& b1 = balls[i], &b2 = balls[j];
                    if (!b1.active||b1.pocketed||!b2.active||b2.pocketed) continue;
                    float dx = b2.x-b1.x, dy = b2.y-b1.y, dist = sqrt(dx*dx+dy*dy);
                    float min_d = Ball::RADIUS*2;
                    if (dist < min_d && dist > 0.001f) {
                        float ov = (min_d-dist)/2, nx = dx/dist, ny = dy/dist;
                        b1.x -= nx*ov; b1.y -= ny*ov; b2.x += nx*ov; b2.y += ny*ov;
                        float dvx = b1.vx-b2.vx, dvy = b1.vy-b2.vy, dvn = dvx*nx + dvy*ny;
                        if (dvn > 0) {
                            float imp = 2*dvn / (Ball::MASS+Ball::MASS);
                            b1.vx -= imp*Ball::MASS*nx*RESTITUTION;
                            b1.vy -= imp*Ball::MASS*ny*RESTITUTION;
                            b2.vx += imp*Ball::MASS*nx*RESTITUTION;
                            b2.vy += imp*Ball::MASS*ny*RESTITUTION;
                        }
                    }
                }
            bool stopped = true;
            for (auto& b : balls)
                if (b.active && !b.pocketed && (fabs(b.vx)>0.5f||fabs(b.vy)>0.5f)) { stopped=false; break; }
            if (stopped && s > 30) { r.steps = s; r.success = r.pocketed_ball > 0 && !r.scratch; break; }
            r.steps = s;
        }
        return r;
    }

    ShotResult best_shot() {
        ShotResult best;
        float best_score = -9999;
        float cx = balls.empty() ? 400 : balls[0].x;
        float cy = balls.empty() ? 800 : balls[0].y;

        for (size_t i = 1; i < balls.size(); i++) {
            if (!balls[i].active || balls[i].pocketed) continue;
            float tx = balls[i].x, ty = balls[i].y;
            float ctd = sqrt((tx-cx)*(tx-cx)+(ty-cy)*(ty-cy));
            float ang = atan2(ty-cy, tx-cx) * 180 / M_PI;

            for (int p = 0; p < 6; p++) {
                float ttd = sqrt((POCKETS[p][0]-tx)*(POCKETS[p][0]-tx)+(POCKETS[p][1]-ty)*(POCKETS[p][1]-ty));
                float pa = atan2(POCKETS[p][1]-ty, POCKETS[p][0]-tx) * 180 / M_PI;
                float diff = pa - ang; if (diff > 180) diff -= 360; if (diff < -180) diff += 360;
                if (fabs(diff) > 90) continue;
                float sc = max(0.0f, 1.0f-fabs(diff)/90.0f) * 50.0f + max(0.0f, 1.0f-ttd/(TABLE_W*0.7f)) * 40.0f + 10.0f;
                if (sc > best_score) {
                    best_score = sc;
                    float pw = min(8.0f, max(3.0f, ctd/300.0f+ttd/500.0f));
                    auto saved = balls;
                    apply_shot(ang, pw);
                    ShotResult sim = simulate();
                    balls = saved;
                    if (sim.success && sim.pocketed_ball == (int)i) {
                        aim_angle = ang; power = pw;
                        return sim;
                    }
                }
            }
        }
        return best;
    }
};

} // namespace aether
PHYEOF

# ─── C++: Agent Core (AETHER SHOT physics) ───
cat > "$PROJECT_DIR/app/src/main/jni/core/agent.cpp" << 'CPPEOF'
#include <jni.h>
#include <android/log.h>
#include "../brain/physics_engine.h"
#include <thread>
#include <atomic>
#include <chrono>
#include <cstring>

#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, "AetherCore", __VA_ARGS__)

static std::atomic<bool> running{false};
static std::atomic<bool> auto_aim{true}, auto_shoot{true}, force_shot{false};
static std::atomic<float> skill_level{0.88f}, think_delay{1.5f};
static std::thread worker;
static uint8_t* frame_buf = nullptr;
static int w = 0, h = 0;

void process_loop() {
    aether::PhysicsEngine phys;
    phys.setup();
    int fc = 0;
    LOGI("Aether Physics Engine started");
    while (running) {
        fc++;
        if (auto_aim || auto_shoot) {
            if (fc % 30 == 0) { // every 30 frames (~1 sec)
                aether::ShotResult sr = phys.best_shot();
                if (sr.success) {
                    LOGI("Best: ball %d -> %s (%.1f deg, %.1f power)",
                         sr.pocketed_ball, phys.PNAME[sr.pocket_id],
                         sr.aim_angle, sr.power);
                }
                if (force_shot) {
                    LOGI("Force shot triggered");
                    force_shot = false;
                    // Convert physics to screen coordinates
                    float screen_w = 1080, screen_h = 1920;
                    float scale_x = screen_w / phys.TABLE_W;
                    float scale_y = screen_h / phys.TABLE_H;

                    float cue_sx = phys.balls[0].x * scale_x;
                    float cue_sy = phys.balls[0].y * scale_y;
                    float rad = sr.aim_angle * M_PI / 180.0f;
                    float drag_len = sr.power * 40.0f;
                    float end_x = cue_sx + cos(rad) * drag_len;
                    float end_y = cue_sy + sin(rad) * drag_len;

                    // Call Java TouchService
                    JNIEnv* env = nullptr;
                    // In production, cache JavaVM and call through JNI
                }
            }
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(5));
    }
}

extern "C" {

JNIEXPORT void JNICALL
Java_com_aetherlab_billiards_ai_visionagent_MainActivity_nativeInit(JNIEnv*, jclass, jstring, jint sw, jint sh) {
    w = sw; h = sh;
    frame_buf = new uint8_t[w * h * 4];
    running = true;
    worker = std::thread(process_loop);
    LOGI("Aether Forge v4.0 initialized");
}

JNIEXPORT void JNICALL
Java_com_aetherlab_billiards_ai_visionagent_MainActivity_nativeSetAutoPlay(JNIEnv*, jclass, jboolean aim, jboolean shoot, jboolean) {
    auto_aim = aim; auto_shoot = shoot;
}

JNIEXPORT void JNICALL
Java_com_aetherlab_billiards_ai_visionagent_MainActivity_nativeSetSkill(JNIEnv*, jclass, jfloat s) {
    skill_level = s;
}

JNIEXPORT void JNICALL
Java_com_aetherlab_billiards_ai_visionagent_MainActivity_nativeSetDelay(JNIEnv*, jclass, jfloat d) {
    think_delay = d;
}

JNIEXPORT void JNICALL
Java_com_aetherlab_billiards_ai_visionagent_MainActivity_nativeForceShoot(JNIEnv*, jclass) {
    force_shot = true;
}

JNIEXPORT void JNICALL
Java_com_aetherlab_billiards_ai_visionagent_MainActivity_nativeDestroy(JNIEnv*, jclass) {
    running = false;
    if (worker.joinable()) worker.join();
    delete[] frame_buf;
    LOGI("Aether Forge destroyed");
}

} // extern "C"
CPPEOF

touch "$PROJECT_DIR/app/proguard-rules.pro"
log "All project files created!"

# ─── PHASE 3: BUILD ───
step "Building APK..."
cd "$PROJECT_DIR"

export JAVA_HOME="/data/data/com.termux/files/usr/lib/jvm/java-17-openjdk"
export ANDROID_HOME="$SDK_DIR"
export ANDROID_NDK_HOME="$SDK_DIR/ndk/$NDK_VER"
export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$JAVA_HOME/bin:$PATH"

log "Starting Gradle build..."
./gradlew assembleDebug --no-daemon 2>&1

APK="$PROJECT_DIR/app/build/outputs/apk/debug/app-debug.apk"
if [ -f "$APK" ]; then
    echo ""
    echo "${GREEN}╔══════════════════════════════════════╗${NC}"
    echo "${GREEN}║   ✅ BUILD SUCCESSFUL!               ║${NC}"
    echo "${GREEN}╚══════════════════════════════════════╝${NC}"
    echo "  📦 $(ls -lh "$APK" | awk '{print $5}')"
    echo "  📲 adb install -r \"$APK\""
else
    echo ""
    echo "${RED}╔══════════════════════════════════════╗${NC}"
    echo "${RED}║   ❌ BUILD FAILED                     ║${NC}"
    echo "${RED}╚══════════════════════════════════════╝${NC}"
    echo "  ดู Error ด้านบน — แคปให้ผมนะ"
fi
