#pragma once
#include <memory>
#include <atomic>
#include <thread>
#include <vector>

namespace aether {

struct BallState {
    float x, y;
    float radius;
    int type;
};

struct GameState {
    std::vector<BallState> balls;
    float cueX, cueY;
    float aimAngle;
    bool isMyTurn;
};

struct Action {
    float aimAngle;
    float power;
    float topSpin;
    float sideSpin;
    float thinkTime;
};

class AgentCore {
public:
    static AgentCore& Instance();
    void Initialize(const std::string& modelPath, int screenW, int screenH);
    void ProcessFrame(uint8_t* rgbaData, int width, int height);
    void Shutdown();

private:
    AgentCore() = default;
    void MainLoop();
    std::atomic<bool> running_{false};
    std::thread workerThread_;
    uint8_t* frameBuffer_ = nullptr;
    int screenW_ = 0, screenH_ = 0;
    std::mutex frameMutex_;
    bool frameReady_ = false;
};

}
