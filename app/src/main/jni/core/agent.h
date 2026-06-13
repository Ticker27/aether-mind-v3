#pragma once
#include <atomic>
#include <thread>
#include <mutex>
#include <string>
#include <cstdint>
namespace aether {
class GhostAgent {
public:
    static GhostAgent& Instance();
    void Init(const std::string& path, int w, int h);
    void ProcessFrame(uint8_t* rgba, int w, int h);
    void SetAutoPlay(bool aim, bool shoot, bool hideGuideline);
    void SetSkill(float s);
    void SetDelay(float d);
    void ForceShoot();
    void Shutdown();
private:
    GhostAgent()=default;
    void Loop();
    std::atomic<bool> running_{false}, autoAim_{true}, autoShoot_{true}, hideGuide_{true}, forceShoot_{false};
    std::thread worker_;
    uint8_t* buf_=nullptr;
    int w_=0,h_=0;
    std::mutex mtx_;
    bool ready_=false;
    float skill_=0.88f, delay_=1.5f;
};
}
