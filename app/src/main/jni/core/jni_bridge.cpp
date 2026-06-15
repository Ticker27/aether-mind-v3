#include <jni.h>
#include <android/log.h>
#include "brain/brain.h"

#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, "AetherJNI", __VA_ARGS__)

static aether::SkillConfig g_config = {0.5f, 0.02f, 150, 0.1f, 0.95f, 0.15f, 0.8f};
static JavaVM* g_jvm = nullptr;

extern "C" {

JNIEXPORT jint JNICALL JNI_OnLoad(JavaVM* vm, void*) {
    g_jvm = vm;
    return JNI_VERSION_1_6;
}

// Set skill level (0=easy, 1=medium, 2=hard)
JNIEXPORT void JNICALL
Java_com_aetherlab_billiards_ai_visionagent_ai_AetherEngine_nativeSetSkill(
    JNIEnv*, jclass, jint level) {
    switch (level) {
        case 0: // Easy
            g_config = {4.0f, 0.15f, 800, 0.7f, 0.3f, 0.5f, 0.3f};
            break;
        case 1: // Medium
            g_config = {1.5f, 0.06f, 400, 0.3f, 0.6f, 0.3f, 0.5f};
            break;
        default: // Hard/Pro
            g_config = {0.5f, 0.02f, 150, 0.1f, 0.95f, 0.15f, 0.8f};
            break;
    }
    LOGI("Skill set to level %d", level);
}

// Analyze shot from ball positions
JNIEXPORT jfloatArray JNICALL
Java_com_aetherlab_billiards_ai_visionagent_ai_AetherEngine_nativeAnalyzeShot(
    JNIEnv* env, jclass, jfloatArray ballData) {
    // ballData format: [cueX, cueY, b1X, b1Y, type1, isPotted1, b2X, b2Y, ...]
    jsize len = env->GetArrayLength(ballData);
    jfloat* data = env->GetFloatArrayElements(ballData, nullptr);
    
    std::vector<aether::Ball> balls;
    balls.push_back({{data[0], data[1]}, 0, false}); // cue
    
    for (int i = 2; i < len; i += 4) {
        if (i + 3 >= len) break;
        aether::Ball b = {{data[i], data[i+1]}, (int)data[i+2], data[i+3] > 0.5f};
        balls.push_back(b);
    }
    
    auto shot = aether::AetherBrain::think(balls, g_config);
    aether::AetherBrain::humanize(shot, g_config);
    
    env->ReleaseFloatArrayElements(ballData, data, 0);
    
    // Return: [targetBall, targetPocket, aimAngle, power, confidence, canPot]
    jfloatArray result = env->NewFloatArray(6);
    jfloat vals[6] = {
        (float)shot.targetBall,
        (float)shot.targetPocket,
        shot.aimAngle,
        shot.power,
        shot.confidence,
        shot.canPot ? 1.0f : 0.0f
    };
    env->SetFloatArrayRegion(result, 0, 6, vals);
    return result;
}

} // extern "C"
