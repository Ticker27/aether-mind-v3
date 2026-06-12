# AETHER — Auto Play Ghost v4.0

Physics Engine (C++) + Floating UI Control + Auto Play

## Structure
```
app/
├── src/main/
│   ├── java/.../visionagent/
│   │   ├── MainActivity.java       — Entry point + license
│   │   ├── ai/AutoPlayEngine.java   — AI engine
│   │   └── services/
│   │       ├── AutoPlayService.java — Floating bubble + control
│   │       ├── TouchService.java    — Accessibility touch
│   │       └── GhostGestureService.java
│   ├── jni/core/
│   │   └── agent.cpp                — C++ native loop
│   ├── jni/brain/
│   │   └── physics_engine.h         — OUR physics engine
│   └── res/layout/
│       ├── autoplay_bubble.xml      — Floating bubble UI
│       └── autoplay_panel.xml       — Control panel UI
└── build.gradle
```

## Build
```bash
./gradlew assembleDebug
```
