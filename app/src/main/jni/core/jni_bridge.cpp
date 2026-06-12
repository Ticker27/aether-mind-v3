#include <jni.h><android/log.h>
#include "agent.h"
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO,"JNI",__VA_ARGS__)
extern "C" {
JNIEXPORT void JNICALL Java_com_aetherlab_billiards_ai_visionagent_MainActivity_nativeInit(JNIEnv* e,jclass,jstring p,jint w,jint h){
    const char* s=e->GetStringUTFChars(p,0);
    aether::GhostAgent::Instance().Init(s,w,h);
    e->ReleaseStringUTFChars(p,s);
}
JNIEXPORT void JNICALL Java_com_aetherlab_billiards_ai_visionagent_MainActivity_nativeProcessFrame(JNIEnv* e,jclass,jlong,jint w,jint h,jbyteArray a){
    jbyte* d=e->GetByteArrayElements(a,0);
    aether::GhostAgent::Instance().ProcessFrame((uint8_t*)d,w,h);
    e->ReleaseByteArrayElements(a,d,JNI_ABORT);
}
JNIEXPORT void JNICALL Java_com_aetherlab_billiards_ai_visionagent_MainActivity_nativeSetAutoPlay(JNIEnv*,jclass,jboolean aim,jboolean shoot,jboolean hide){
    aether::GhostAgent::Instance().SetAutoPlay(aim,shoot,hide);
}
JNIEXPORT void JNICALL Java_com_aetherlab_billiards_ai_visionagent_MainActivity_nativeSetSkill(JNIEnv*,jclass,jfloat s){aether::GhostAgent::Instance().SetSkill(s);}
JNIEXPORT void JNICALL Java_com_aetherlab_billiards_ai_visionagent_MainActivity_nativeSetDelay(JNIEnv*,jclass,jfloat d){aether::GhostAgent::Instance().SetDelay(d);}
JNIEXPORT void JNICALL Java_com_aetherlab_billiards_ai_visionagent_MainActivity_nativeForceShoot(JNIEnv*,jclass){aether::GhostAgent::Instance().ForceShoot();}
JNIEXPORT void JNICALL Java_com_aetherlab_billiards_ai_visionagent_MainActivity_nativeDestroy(JNIEnv*,jclass){aether::GhostAgent::Instance().Shutdown();}
}
