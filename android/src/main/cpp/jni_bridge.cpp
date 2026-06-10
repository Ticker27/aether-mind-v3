/**
 * NEXUS ULTRA - JNI Bridge (C++ → Java/Python)
 * ===============================================
 * Connects native C++ modules to Android Java layer
 * 
 * Functions:
 * - nativeInit: Initialize all native modules
 * - nativeCaptureFrame: Capture frame from game surface
 * - nativeRenderOverlay: Render trajectory overlay
 * - nativePredict: Run Neural Core inference
 * - nativeRelease: Cleanup all resources
 */

#include <jni.h>
#include <android/native_window.h>
#include <android/native_window_jni.h>
#include "frame_capture.h"
#include "vulkan_renderer.h"
#include <memory>

namespace nexus {

// Global instances
static std::unique_ptr<FrameCapture> g_frameCapture;
static std::unique_ptr<VulkanRenderer> g_renderer;
static ANativeWindow* g_window = nullptr;

extern "C" {

/**
 * Initialize all native modules
 * @param env: JNI environment
 * @param clazz: Java class
 * @param surface: Android Surface object
 * @return true if initialization successful
 */
JNIEXPORT jboolean JNICALL
Java_com_system_service_helper_AetherService_nativeInit(
    JNIEnv* env, jclass clazz, jobject surface) {
    
    // Get ANativeWindow from Surface
    g_window = ANativeWindow_fromSurface(env, surface);
    if (!g_window) return JNI_FALSE;
    
    // Initialize Frame Capture
    g_frameCapture = std::make_unique<FrameCapture>();
    if (!g_frameCapture->init(g_window)) {
        return JNI_FALSE;
    }
    
    // Initialize Vulkan Renderer
    g_renderer = std::make_unique<VulkanRenderer>();
    if (!g_renderer->init(g_window)) {
        return JNI_FALSE;
    }
    
    return JNI_TRUE;
}

/**
 * Capture current frame
 * @return Frame data as byte array (or null if failed)
 */
JNIEXPORT jbyteArray JNICALL
Java_com_system_service_helper_AetherService_nativeCaptureFrame(
    JNIEnv* env, jclass clazz) {
    
    if (!g_frameCapture || !g_frameCapture->isInitialized()) {
        return nullptr;
    }
    
    AHardwareBuffer* buffer = g_frameCapture->captureFrame();
    if (!buffer) return nullptr;
    
    // Lock buffer and read pixels
    void* pixels = nullptr;
    AHardwareBuffer_lock(buffer, AHARDWAREBUFFER_USAGE_CPU_READ_OFTEN,
                        -1, nullptr, &pixels);
    
    if (!pixels) return nullptr;
    
    int width = g_frameCapture->getWidth();
    int height = g_frameCapture->getHeight();
    int size = width * height * 4; // RGBA
    
    // Create Java byte array
    jbyteArray result = env->NewByteArray(size);
    env->SetByteArrayRegion(result, 0, size, (jbyte*)pixels);
    
    AHardwareBuffer_unlock(buffer, nullptr);
    
    return result;
}

/**
 * Render trajectory overlay
 * @param x1, y1: Start point
 * @param x2, y2: End point
 * @return Render time in microseconds
 */
JNIEXPORT jlong JNICALL
Java_com_system_service_helper_AetherService_nativeRenderOverlay(
    JNIEnv* env, jclass clazz,
    jfloat x1, jfloat y1, jfloat x2, jfloat y2) {
    
    if (!g_renderer || !g_renderer->isInitialized()) {
        return -1;
    }
    
    return g_renderer->renderAimLine(x1, y1, x2, y2);
}

/**
 * Get frame capture latency
 * @return Latency in microseconds
 */
JNIEXPORT jlong JNICALL
Java_com_system_service_helper_AetherService_nativeGetCaptureLatency(
    JNIEnv* env, jclass clazz) {
    
    if (!g_frameCapture) return -1;
    return g_frameCapture->getLatencyUs();
}

/**
 * Release all native resources
 */
JNIEXPORT void JNICALL
Java_com_system_service_helper_AetherService_nativeRelease(
    JNIEnv* env, jclass clazz) {
    
    g_frameCapture.reset();
    g_renderer.reset();
    
    if (g_window) {
        ANativeWindow_release(g_window);
        g_window = nullptr;
    }
}

} // extern "C"

} // namespace nexus
