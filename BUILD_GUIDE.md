# 🛠️ AETHER SHOT — OFFICIAL BUILD GUIDE

**Project:** AETHER MIND v3.0 (AETHER SHOT Module)  
**Version:** 1.0.0  
**Goal:** Build a fully functional, stealthy, and AI-powered Android APK.

---

## ⚠️ IMPORTANT: THE CORE PRINCIPLE
This project uses **ChaquoPy** to embed a full Python environment into the APK. Do NOT attempt to run the Python files standalone on Android; they must be bundled within the APK through the Gradle build process.

---

## 🚀 METHOD 1: AUTOMATIC BUILD (GitHub Actions) - RECOMMENDED
*The fastest way to get a signed APK without installing Android Studio.*

1. **Fork/Clone** the repository to your own GitHub account.
2. **Go to the 'Actions' tab** in your repository.
3. **Select 'Android CI'** (or the build workflow) from the left sidebar.
4. **Click 'Run workflow'** $\rightarrow$ **'Run workflow'**.
5. **Wait 5-10 minutes.** Once complete, the APK will be available in the **'Artifacts'** section of the run.
6. **Download `aether_shot_v1.0.0.apk`** and install it on your device.

---

## 💻 METHOD 2: MANUAL BUILD (Android Studio)
*For developers who want full control and debugging.*

### 1. Environment Setup
- **Install Android Studio** (Latest Flamingo or Giraffe version).
- **Install JDK 17** (Required for Gradle 8.0+).
- **Android SDK:** Install SDK Platform 34 and Build-Tools 34.0.0.

### 2. Importing the Project
- Open Android Studio $\rightarrow$ `Open` $\rightarrow$ Navigate to `/var/minis/workspace/aether-mind-v3/android`.
- Wait for Gradle to sync. If prompted to install a Gradle version, click **OK**.

### 3. Configuration Check
Ensure `android/build.gradle` contains the ChaquoPy plugin:
```gradle
plugins {
    id 'com.android.application'
    id 'com.chaquo.python'
}
```

### 4. Build Process
- **Clean Project:** `Build` $\rightarrow$ `Clean Project`.
- **Assemble APK:** `Build` $\rightarrow$ `Build Bundle(s) / APK(s)` $\rightarrow$ `Build APK(s)`.
- **Locate APK:** Find the resulting file in:  
  `android/build/outputs/apk/debug/app-debug.apk`

---

## 📲 INSTALLATION & ACTIVATION (CRITICAL)

Since this is a **Stealth APK**, it has no icon and no UI. You must use ADB or a file manager to install and activate it.

### 1. Install via ADB
```bash
adb install -r aether_shot_v1.0.0.apk
```

### 2. Enable Accessibility Service (MANDATORY)
The AI cannot move the cue ball without this permission.
- **Settings** $\rightarrow$ **Accessibility** $\rightarrow$ **Installed Apps/Services** $\rightarrow$ **Aether Shot** $\rightarrow$ **Enable**.

### 3. Grant Media Projection Permission
- The first time the service starts, a system popup will appear asking for **"Screen Recording"** permission.
- Select **"Start Now"**.

### 4. Verify Status
Use ADB to check if the service is running:
```bash
adb shell dumpsys activity services | grep AetherService
```

---

## 🛡️ TROUBLESHOOTING

| Issue | Solution |
|-------|-----------|
| `Gradle sync failed` | Check if `JAVA_HOME` is set to JDK 17. |
| `App crashes on start` | Ensure Accessibility Service is enabled. |
| `No frames captured` | Check if `MediaProjection` permission was granted. |
| `Build error: Python not found` | Ensure `buildPython` in `build.gradle` points to your local python3 path. |

---

## 🏁 SUCCESS CRITERIA
- [ ] APK installed successfully.
- [ ] Accessibility Service enabled.
- [ ] Media Projection permission granted.
- [ ] Logcat shows: `AETHER SHOT AI Core loaded`.
