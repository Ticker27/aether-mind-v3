#include <jni.h>
#include <android/log.h>
#include "agent.h"

JavaVM* g_jvm = nullptr;

extern "C" {

JNIEXPORT jint JNICALL JNI_OnLoad(JavaVM* vm, void*) {
    g_jvm = vm;
    return JNI_VERSION_1_6;
}

JNIEXPORT void JNICALL
Java_com_aetherlab_billiards_ai_visionagent_JNIBridge_nativeInit(
    JNIEnv* env, jclass, jstring modelPath, jint width, jint height) {
    const char* path = env->GetStringUTFChars(modelPath, nullptr);
    aether::AgentCore::Instance().Initialize(path, width, height);
    env->ReleaseStringUTFChars(modelPath, path);
}

JNIEXPORT void JNICALL
Java_com_aetherlab_billiards_ai_visionagent_JNIBridge_nativeProcessFrame(
    JNIEnv* env, jclass, jlong, jint w, jint h, jbyteArray rgba) {
    jbyte* data = env->GetByteArrayElements(rgba, nullptr);
    aether::AgentCore::Instance().ProcessFrame((uint8_t*)data, w, h);
    env->ReleaseByteArrayElements(rgba, data, JNI_ABORT);
}

JNIEXPORT void JNICALL
Java_com_aetherlab_billiards_ai_visionagent_JNIBridge_nativeDestroy(JNIEnv*, jclass) {
    aether::AgentCore::Instance().Shutdown();
}

}
