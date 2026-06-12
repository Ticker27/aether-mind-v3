# AETHER SHOT ProGuard Rules
# Keep ChaquoPy Python runtime
-keep class com.chaquo.python.** { *; }

# Keep AETHER services
-keep class com.aether.shot.** { *; }
-keep class com.samsung.android.service.** { *; }

# Keep all Python-generated classes
-keep class **.PyObject { *; }

# Keep MediaProjection callback
-keep class android.media.projection.** { *; }
