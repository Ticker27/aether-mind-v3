# 📄 Technical Context Brief: Background AI Service for 8 Ball Pool

**Document Version:** 1.0
**Project:** 8 Ball Pool Human-like AI Assistant
**Target Team:** Android APK Development
**Date:** 2026-06-12

---

## 🎯 1. Objective (วัตถุประสงค์)

สร้าง APK ที่ทำงานเป็น **Headless Background Service** (ไม่มี UI, ไม่สามารถเปิดแอปได้) เพื่อทำหน้าที่เป็น "ตาและมือ" ให้กับ Core AI Engine ที่ประมวลผลอยู่ที่ฝั่งอื่น (หรือ local engine)

**Core Principle:**
- ✅ **Vision-Only** — จับภาพหน้าจอเท่านั้น ไม่ยุ่งกับ memory, packet, หรือ game code
- ✅ **Stealth Mode** — ไร้ UI, ไร้ icon ใน launcher (optional), ทำงานเงียบเมื่อเกมถูกเปิด
- ✅ **Lightweight** — ไม่กิน CPU/RAM/thermal จนกระทบ performance ของเกม
- ✅ **Human-like Execution** — จำลองการสัมผัสหน้าจอแบบมนุษย์ 100%

---

## 🏗️ 2. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    ANDROID DEVICE                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐      ┌──────────────────────────────┐   │
│  │  8 Ball Pool │      │  Background AI Service (APK) │   │
│  │   (Game)     │◄────►│                              │   │
│  └──────────────┘      │  ┌────────────────────────┐  │   │
│         ▲              │  │  Screen Capture Module │  │   │
│         │              │  │  (MediaProjection API) │  │   │
│         │              │  └────────────┬───────────┘  │   │
│         │              │               │              │   │
│         │              │  ┌────────────▼───────────┐  │   │
│         │              │  │  Vision Bridge (IPC)   │──┼───┼──► Core AI Engine
│         │              │  │  (gRPC / WebSocket /   │  │   │   (MobileNetV3 + Physics)
│         │              │  │   Shared Memory)       │  │   │
│         │              │  └────────────▲───────────┘  │   │
│         │              │               │              │   │
│         │              │  ┌────────────┴───────────┐  │   │
│         │              │  │  Touch Execution       │  │   │
│         │              │  │  (Accessibility /      │  │   │
│         │              │  │   Instrumentation /    │  │   │
│         │              │  │   Virtual Input)       │  │   │
│         │              │  └────────────┬───────────┘  │   │
│         │              │               │              │   │
│         │              │  ┌────────────┴───────────┐  │   │
│         │              │  │  Core AI Integration    │  │   │
│         │              │  │  (gRPC / WebSocket)   │  │   │
│         │              │  └────────────┬───────────┘  │   │
│         │              │               │              │   │
│         └──────────────┼───────────────┼──────────────┘   │
│                         │               │                  │
└─────────────────────────┼───────────────┼──────────────────┘
                         └───────────────┘
                         Touch Events Injection
```


---

## 📦 3. APK Requirements (สิ่งที่ทีม APK ต้องทำ)

### 3.1 Service Behavior
- **Auto-Start on Game Launch:** ใช้ `UsageStatsManager` หรือ `AccessibilityService` ตรวจจับเมื่อ `com.miniclip.eightballpool` ถูกเปิด
- **No Launcher Icon:** ซ่อน icon ออกจาก app drawer (ใช้ `<category android:name="android.intent.category.LAUNCHER" />` ลบออก หรือใช้ `PackageManager.setComponentEnabledSetting`)
- **Foreground Service:** ใช้ Notification แบบ low-priority (silent) เพื่อป้องกัน Android kill service
- **Auto-Stop:** หยุดทำงานเมื่อเกมถูกปิด หรือ device ล็อกหน้าจอ

### 3.2 Screen Capture Module
- **API:** ใช้ `MediaProjection API` (Android 5.0+)
- **Resolution:** Capture ที่ native resolution ของ device หรือ downscale เพื่อลด overhead
- **FPS Target:** 15-30 FPS (เพียงพอสำหรับ AI ที่ interpolate ได้)
- **ROI (Region of Interest):** crop เฉพาะ area ที่จำเป็น (โต๊ะพูล, UI elements) เพื่อลด data size
- **Format:** RGB_565 หรือ NV21 (compressed) ส่งผ่าน IPC

### 3.3 Touch Execution Module
- **Method Options:**
  1. **AccessibilityService** (แนะนำ) — ปลอดภัยที่สุด, ไม่ต้อง root
 2. **InputDevice Injection** — ต้อง root, แต่ latency ต่ำสุด
 3. **Virtual Touch via ADB** — สำหรับ testing
- **Capabilities ที่ต้องรองรับ:**
  - `touch(x, y)` — tap
  - `swipe(x1, y1, x2, y2, duration)` — drag
  - `multiTouch()` — สำหรับ spin (ถ้าเกมรองรับ)
  - `pressure variation` — จำลองน้ำหนักกด
- **Timing Precision:** ต้องแม่นยำระดับ ±5ms เพื่อ sync กับ Core AI

### 3.4 Communication Protocol (IPC)
**แนะนำ: gRPC over Unix Domain Socket** หรือ **WebSocket**

**Data Flow:**
```
APK ──(Screen Frame)──► Core AI
Core AI ──(Touch Command)──► APK
```

**Message Schema ตัวอย่าง:**
```protobuf
// Frame from APK
message ScreenFrame {
  int64 timestamp = 1;
  bytes image_data = 2;  // compressed JPEG/NV21
  int32 width = 3;
  int32 height = 4;
  string game_state = 5;  // "playing", "menu", "loading"
}

// Command from Core AI
message TouchCommand {
  enum ActionType {
    TAP = 0;
    SWIPE = 1;
    MULTI_TOUCH = 2;
  }
  ActionType type = 1;
  float start_x = 2;
  float start_y = 3;
  float end_x = 4;
  float end_y = 5;
  int32 duration_ms = 6;
  float pressure = 7;
  int32 delay_ms = 8;  // wait before execute
  bool humanize = 9;   // add noise/jitter
}
```

---

## ⚙️ 4. Technical Constraints & Optimization

### 4.1 Performance Budget
| Resource | Limit |
|----------|-------|
| CPU Usage | < 15% (single core) |
| RAM | < 80MB |
| Battery Drain | < 5% per hour |
| Latency (Capture → IPC) | < 50ms |
| Latency (IPC → Touch) | < 20ms |

### 4.2 Thermal Management
- Monitor `ThermalService` หรือ `/sys/class/thermal/`
- ถ้า temperature > 40°C → ลด capture FPS เป็น 10 FPS
- ถ้า > 45°C → pause service ชั่วคราว

### 4.3 Anti-Detection Considerations
- **Randomize Timing:** อย่าส่ง frame ทุก 33ms เป๊ะๆ → สุ่ม ±5-15ms
- **Avoid Perfect Patterns:** touch coordinates ควรมี noise เล็กน้อย
- **Device Fingerprint:** ใช้ random device ID ใน logs (ถ้ามี)
- **No Root Required:** เพื่อลด risk ในการถูก scan

---

## 🛠️ 5. Tech Stack Recommendation

| Component | Recommended Tech |
|-----------|------------------|
| Language | Kotlin (primary), Java (fallback) |
| Min SDK | Android 7.0 (API 24) |
| Screen Capture | MediaProjection API + ImageReader |
| IPC | gRPC (io.grpc:grpc-okhttp) หรือ WebSocket (OkHttp) |
| Touch Injection | AccessibilityService |
| DI | Hilt / Dagger |
| Async | Coroutines + Flow |
| Logging | Timber (disable ใน production) |

---

## 📋 6. Required Permissions (AndroidManifest.xml)

```xml
<uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_MEDIA_PROJECTION" />
<uses-permission android:name="android.permission.SYSTEM_ALERT_WINDOW" />
<uses-permission android:name="android.permission.BIND_ACCESSIBILITY_SERVICE" 
    tools:ignore="ProtectedPermissions" />
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.WAKE_LOCK" />
<uses-permission android:name="android.permission.REQUEST_IGNORE_BATTERY_OPTIMIZATIONS" />
```

---

## 📌 7. Integration Checklist

- [ ] APK สามารถ capture screen ของ 8 Ball Pool ได้
- [ ] ส่ง frame data ผ่าน IPC ได้ < 50ms latency
- [ ] รับ TouchCommand และ execute ได้แม่นยำ
- [ ] Auto-start เมื่อเกมเปิด, auto-stop เมื่อเกมปิด
- [ ] ไม่กิน CPU/RAM เกิน budget
- [ ] Thermal throttling ทำงาน
- [ ] ไม่มี UI, ไม่มี launcher icon
- [ ] รันเป็น Foreground Service ได้โดยไม่ถูก kill

---

## 📞 8. Next Steps

1. **ทีม APK:** Review brief นี้ → ถามข้อสงสัย (ถ้ามี)
2. **ทีม AI Core:** เตรียม IPC server + message schema
3. **Joint Testing:** ทดสอบ capture + touch injection ด้วย dummy data
4. **Integration:** เชื่อมต่อ Core AI กับ APK จริง

---

## 🎯 Success Criteria

✅ APK รันเป็น background service ได้โดยไม่ถูก Android kill
✅ Latency end-to-end (capture → AI → touch) < 150ms
✅ ไม่กระทบ FPS ของเกม (ยังคง 60 FPS)
✅ Touch execution ดูเป็นธรรมชาติ (มี noise, hesitation)
✅ ใช้งานต่อเนื่องได้ > 2 ชั่วโมงโดยไม่ overheat

---