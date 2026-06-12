# Aether ProGuard Rules
-keep class com.aetherlab.billiards.ai.visionagent.** { *; }
-keep class **.JNIBridge { *; }
-dontwarn org.tensorflow.**
-keep class org.tensorflow.** { *; }
