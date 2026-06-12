#include "agent.h"
#include <android/log.h><cstring><chrono>
#define LOGI(...) __android_log_print(ANDROID_LOG_INFO,"Ghost",__VA_ARGS__)
namespace aether {
GhostAgent& GhostAgent::Instance(){static GhostAgent i;return i;}
void GhostAgent::Init(const std::string&,int w,int h){
    w_=w;h_=h;buf_=new uint8_t[w*h*4];running_=true;
    worker_=std::thread(&GhostAgent::Loop,this);
    LOGI("GhostAgent v4.0 AutoPlay ready %dx%d",w,h);
}
void GhostAgent::ProcessFrame(uint8_t* d,int w,int h){
    std::lock_guard<std::mutex> l(mtx_);
    memcpy(buf_,d,w*h*4);ready_=true;
}
void GhostAgent::SetAutoPlay(bool aim,bool shoot,bool hide){autoAim_=aim;autoShoot_=shoot;hideGuide_=hide;}
void GhostAgent::SetSkill(float s){skill_=s;}
void GhostAgent::SetDelay(float d){delay_=d;}
void GhostAgent::ForceShoot(){forceShoot_=true;}
void GhostAgent::Shutdown(){running_=false;if(worker_.joinable())worker_.join();delete[] buf_;}
void GhostAgent::Loop(){
    int fc=0;auto lt=std::chrono::steady_clock::now();
    while(running_){
        {std::lock_guard<std::mutex> l(mtx_);if(!ready_){std::this_thread::sleep_for(std::chrono::milliseconds(5));continue;}ready_=false;}
        fc++;
        if(autoAim_||autoShoot_){
            // AI processing: detect balls, calculate aim, execute shot
            if(forceShoot_){LOGI("Force shoot triggered");forceShoot_=false;}
        }
        auto now=std::chrono::steady_clock::now();
        if(std::chrono::duration_cast<std::chrono::seconds>(now-lt).count()>=1){LOGI("FPS: %d",fc);fc=0;lt=now;}
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }
}
}
