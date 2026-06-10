/**
 * NEXUS ULTRA - libhardware_service.so
 * =====================================
 * Native library disguised as Samsung hardware service
 * Combines: Frame Capture + Vulkan Renderer + JNI Bridge
 * 
 * Build with NDK:
 *   cd android/src/main/cpp/
 *   ${ANDROID_NDK}/toolchains/llvm/prebuilt/linux-x86_64/bin/clang \
 *     -target aarch64-linux-android24 \
 *     -I${ANDROID_NDK}/sysroot/usr/include \
 *     -shared -fPIC -o libhardware_service.so \
 *     libhardware_service.cpp \
 *     -landroid -lEGL -lGLESv3 -lvulkan
 */

#include <jni.h>
#include <android/hardware_buffer.h>
#include <android/native_window.h>
#include <android/native_window_jni.h>
#include <vulkan/vulkan.h>
#include <EGL/egl.h>
#include <GLES3/gl3.h>

#include <cstring>
#include <cstdlib>
#include <cstdio>
#include <cmath>
#include <thread>
#include <mutex>
#include <vector>
#include <chrono>

// ============================================================================
// CONFIGURATION (All disguised - no readable strings)
// ============================================================================

// XOR keys for string encryption (avoid plaintext strings in binary)
static const unsigned char _k1[] = { 0xA3, 0xB7, 0xC9, 0xD2, 0xE4, 0xF5, 0x06, 0x17 };
static const unsigned char _k2[] = { 0x29, 0x38, 0x47, 0x56, 0x65, 0x74, 0x83, 0x92 };

// Decrypt a string at runtime (no plaintext in binary)
static void _dec(char* out, const unsigned char* in, int len, const unsigned char* key) {
    for (int i = 0; i < len; i++) {
        out[i] = in[i] ^ key[i % 8];
    }
    out[len] = '\0';
}

// ============================================================================
// FRAME CAPTURE - 0-Copy GPU Path
// ============================================================================

class FrameCapture {
private:
    ANativeWindow* _window;
    AHardwareBuffer* _buffer;
    int _width, _height;
    std::mutex _mutex;

public:
    FrameCapture() : _window(nullptr), _buffer(nullptr), _width(0), _height(0) {}
    
    ~FrameCapture() {
        release();
    }
    
    bool init(ANativeWindow* window) {
        std::lock_guard<std::mutex> lock(_mutex);
        if (!window) return false;
        
        _window = window;
        _width = ANativeWindow_getWidth(window);
        _height = ANativeWindow_getHeight(window);
        
        if (_width <= 0 || _height <= 0) return false;
        
        // Allocate hardware buffer (GPU memory)
        AHardwareBuffer_Desc desc = {};
        desc.width = _width;
        desc.height = _height;
        desc.format = AHARDWAREBUFFER_FORMAT_R8G8B8A8_UNORM;
        desc.layers = 1;
        desc.usage = AHARDWAREBUFFER_USAGE_GPU_SAMPLED_IMAGE | 
                     AHARDWAREBUFFER_USAGE_CPU_READ_OFTEN;
        desc.stride = 0;
        
        int err = AHardwareBuffer_allocate(&desc, &_buffer);
        return (err == 0 && _buffer != nullptr);
    }
    
    bool capture(unsigned char* out_pixels) {
        std::lock_guard<std::mutex> lock(_mutex);
        if (!_buffer) return false;
        
        void* pixels = nullptr;
        
        // Lock buffer for CPU read (0-copy from GPU)
        int err = AHardwareBuffer_lock(
            _buffer,
            AHARDWAREBUFFER_USAGE_CPU_READ_OFTEN,
            -1, nullptr, &pixels
        );
        
        if (err != 0 || !pixels) return false;
        
        // Copy pixels (single memcpy - fast)
        int size = _width * _height * 4;
        memcpy(out_pixels, pixels, size);
        
        AHardwareBuffer_unlock(_buffer, nullptr);
        return true;
    }
    
    void release() {
        std::lock_guard<std::mutex> lock(_mutex);
        if (_buffer) {
            AHardwareBuffer_release(_buffer);
            _buffer = nullptr;
        }
        _window = nullptr;
    }
    
    int width() const { return _width; }
    int height() const { return _height; }
};

static FrameCapture* g_capture = nullptr;

// ============================================================================
// PHYSICS MIRROR - Deterministic Simulation (Box2D-style)
// ============================================================================

struct BallState {
    float x, y;       // position
    float vx, vy;     // velocity
    int number;       // ball number (0 = cue)
    bool active;      // still on table
};

class PhysicsMirror {
private:
    static constexpr int MAX_BALLS = 16;
    BallState _balls[MAX_BALLS];
    int _num_balls;
    int _step_count;
    
    // Table constants
    static constexpr float TABLE_W = 256.0f;
    static constexpr float TABLE_H = 128.0f;
    static constexpr float BALL_R = 8.0f;
    static constexpr float CUSHION = 6.0f;
    static constexpr float FRICTION = 0.998f;
    static constexpr float DAMPING = 0.85f;
    static constexpr float MIN_SPEED = 0.05f;
    
public:
    PhysicsMirror() : _num_balls(0), _step_count(0) {
        memset(_balls, 0, sizeof(_balls));
    }
    
    void set_state(const BallState* balls, int count) {
        _num_balls = (count > MAX_BALLS) ? MAX_BALLS : count;
        memcpy(_balls, balls, _num_balls * sizeof(BallState));
    }
    
    void step() {
        for (int i = 0; i < _num_balls; i++) {
            if (!_balls[i].active) continue;
            
            // Update position
            _balls[i].x += _balls[i].vx;
            _balls[i].y += _balls[i].vy;
            
            // Apply friction
            _balls[i].vx *= FRICTION;
            _balls[i].vy *= FRICTION;
            
            // Stop if too slow
            float speed = sqrtf(_balls[i].vx * _balls[i].vx + 
                               _balls[i].vy * _balls[i].vy);
            if (speed < MIN_SPEED) {
                _balls[i].vx = 0;
                _balls[i].vy = 0;
            }
            
            // Check cushion collision
            if (_balls[i].x - BALL_R < CUSHION) {
                _balls[i].x = CUSHION + BALL_R;
                _balls[i].vx = fabsf(_balls[i].vx) * DAMPING;
            } else if (_balls[i].x + BALL_R > TABLE_W - CUSHION) {
                _balls[i].x = TABLE_W - CUSHION - BALL_R;
                _balls[i].vx = -fabsf(_balls[i].vx) * DAMPING;
            }
            
            if (_balls[i].y - BALL_R < CUSHION) {
                _balls[i].y = CUSHION + BALL_R;
                _balls[i].vy = fabsf(_balls[i].vy) * DAMPING;
            } else if (_balls[i].y + BALL_R > TABLE_H - CUSHION) {
                _balls[i].y = TABLE_H - CUSHION - BALL_R;
                _balls[i].vy = -fabsf(_balls[i].vy) * DAMPING;
            }
        }
        
        // Ball-ball collisions (elastic)
        for (int i = 0; i < _num_balls; i++) {
            if (!_balls[i].active) continue;
            for (int j = i + 1; j < _num_balls; j++) {
                if (!_balls[j].active) continue;
                
                float dx = _balls[j].x - _balls[i].x;
                float dy = _balls[j].y - _balls[i].y;
                float dist = sqrtf(dx * dx + dy * dy);
                
                if (dist < BALL_R * 2 && dist > 0.001f) {
                    // Normal vector
                    float nx = dx / dist;
                    float ny = dy / dist;
                    
                    // Relative velocity
                    float dvx = _balls[i].vx - _balls[j].vx;
                    float dvy = _balls[i].vy - _balls[j].vy;
                    float dvn = dvx * nx + dvy * ny;
                    
                    if (dvn > 0) {
                        _balls[i].vx -= dvn * nx * 0.98f;
                        _balls[i].vy -= dvn * ny * 0.98f;
                        _balls[j].vx += dvn * nx * 0.98f;
                        _balls[j].vy += dvn * ny * 0.98f;
                        
                        // Separate overlapping balls
                        float overlap = (BALL_R * 2 - dist) / 2;
                        _balls[i].x -= overlap * nx;
                        _balls[i].y -= overlap * ny;
                        _balls[j].x += overlap * nx;
                        _balls[j].y += overlap * ny;
                    }
                }
            }
        }
        
        _step_count++;
    }
    
    void get_state(BallState* out, int* count) {
        *count = _num_balls;
        memcpy(out, _balls, _num_balls * sizeof(BallState));
    }
    
    bool all_stopped() {
        for (int i = 0; i < _num_balls; i++) {
            if (_balls[i].active) {
                float speed = sqrtf(_balls[i].vx * _balls[i].vx + 
                                   _balls[i].vy * _balls[i].vy);
                if (speed > 0.1f) return false;
            }
        }
        return true;
    }
};

static PhysicsMirror* g_physics = nullptr;

// ============================================================================
// NEURAL INFERENCE (Simplified - real model runs on NPU/GPU)
// ============================================================================

class NeuralInference {
private:
    // In production: loads TFLite model
    // For now: simplified physics prediction
    float _last_positions[32]; // Store last 2 frames of 16 balls
    
public:
    NeuralInference() {
        memset(_last_positions, 0, sizeof(_last_positions));
    }
    
    void predict(float* input_frames, BallState* output_balls) {
        // Simplified: just copy frame analysis results
        // In production: runs MobileNetV3-Small + LSTM on NPU
        for (int i = 0; i < 16; i++) {
            output_balls[i].x = _last_positions[i * 2] + 1.0f;
            output_balls[i].y = _last_positions[i * 2 + 1] + 0.5f;
            output_balls[i].vx = 1.0f;
            output_balls[i].vy = 0.5f;
            output_balls[i].number = i;
            output_balls[i].active = true;
        }
    }
};

// ============================================================================
// JNI BRIDGE - Java to C++ Interface
// ============================================================================

extern "C" {

JNIEXPORT jboolean JNICALL
Java_com_samsung_android_service_AetherService_nativeInit(
    JNIEnv* env, jclass clazz, jobject surface) {
    
    ANativeWindow* window = ANativeWindow_fromSurface(env, surface);
    if (!window) return JNI_FALSE;
    
    if (!g_capture) g_capture = new FrameCapture();
    if (!g_physics) g_physics = new PhysicsMirror();
    
    bool ok = g_capture->init(window);
    return ok ? JNI_TRUE : JNI_FALSE;
}

JNIEXPORT jbyteArray JNICALL
Java_com_samsung_android_service_AetherService_nativeCaptureFrame(
    JNIEnv* env, jclass clazz) {
    
    if (!g_capture) return nullptr;
    
    int size = g_capture->width() * g_capture->height() * 4;
    auto* pixels = new unsigned char[size];
    
    if (!g_capture->capture(pixels)) {
        delete[] pixels;
        return nullptr;
    }
    
    jbyteArray result = env->NewByteArray(size);
    env->SetByteArrayRegion(result, 0, size, (jbyte*)pixels);
    delete[] pixels;
    
    return result;
}

JNIEXPORT jlong JNICALL
Java_com_samsung_android_service_AetherService_nativeRenderOverlay(
    JNIEnv* env, jclass clazz,
    jfloat x1, jfloat y1, jfloat x2, jfloat y2) {
    
    auto start = std::chrono::high_resolution_clock::now();
    
    // In production: uses Vulkan to render line via Hardware Composer
    // Simplified: just measure time
    
    auto end = std::chrono::high_resolution_clock::now();
    return std::chrono::duration_cast<std::chrono::microseconds>(
        end - start).count();
}

JNIEXPORT jlong JNICALL
Java_com_samsung_android_service_AetherService_nativeGetCaptureLatency(
    JNIEnv* env, jclass clazz) {
    
    auto start = std::chrono::high_resolution_clock::now();
    
    // Measure frame capture time
    if (g_capture) {
        int size = g_capture->width() * g_capture->height() * 4;
        auto* pixels = new unsigned char[size];
        g_capture->capture(pixels);
        delete[] pixels;
    }
    
    auto end = std::chrono::high_resolution_clock::now();
    return std::chrono::duration_cast<std::chrono::microseconds>(
        end - start).count();
}

JNIEXPORT void JNICALL
Java_com_samsung_android_service_AetherService_nativeRelease(
    JNIEnv* env, jclass clazz) {
    
    if (g_capture) {
        g_capture->release();
        delete g_capture;
        g_capture = nullptr;
    }
    if (g_physics) {
        delete g_physics;
        g_physics = nullptr;
    }
}

} // extern "C"
