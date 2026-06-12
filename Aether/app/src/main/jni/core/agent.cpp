#include "agent.h"
#include "../brain/physics_engine.h"
#include <android/log.h>
#include <cstring>
#include <cmath>

#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, "Aether", __VA_ARGS__)

namespace aether {

AgentCore& AgentCore::Instance() {
    static AgentCore inst;
    return inst;
}

void AgentCore::Initialize(const std::string& modelPath, int sw, int sh) {
    screenW_ = sw; screenH_ = sh;
    frameBuffer_ = new uint8_t[sw * sh * 4];
    running_ = true;
    workerThread_ = std::thread(&AgentCore::MainLoop, this);
    LOGI("Aether Agent initialized %dx%d", sw, sh);
    
    // Test physics engine
    PhysicsEngine phys;
    phys.setup_balls();
    ShotResult result = phys.find_best_shot(400, 800);
    if (result.success) {
        LOGI("Best shot: ball %d -> pocket %d (%s), success=%d", 
             result.pocketed_ball, result.pocket_id, 
             PhysicsEngine::POCKET_NAMES[result.pocket_id], result.success);
    } else {
        LOGI("No valid shot found");
    }
}

void AgentCore::ProcessFrame(uint8_t* rgba, int w, int h) {
    std::lock_guard<std::mutex> lock(frameMutex_);
    memcpy(frameBuffer_, rgba, w * h * 4);
    frameReady_ = true;
}

void AgentCore::Shutdown() {
    running_ = false;
    if (workerThread_.joinable()) workerThread_.join();
    delete[] frameBuffer_;
    LOGI("Aether Agent shutdown");
}

void AgentCore::MainLoop() {
    LOGI("Aether MainLoop started");
    
    // Initialize physics engine
    PhysicsEngine phys;
    phys.setup_balls();
    
    int frame_count = 0;
    while (running_) {
        if (!frameReady_) {
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
            continue;
        }
        
        frame_count++;
        {
            std::lock_guard<std::mutex> lock(frameMutex_);
            frameReady_ = false;
            
            // Process frame: detect balls and find best shot
            // In full implementation, detect ball positions from frameBuffer_
            
            if (frame_count % 30 == 0) {  // Every 30 frames
                // Update ball positions from vision (placeholder)
                // For now, use default positions
                
                ShotResult result = phys.find_best_shot(400, 800);
                if (result.success) {
                    LOGI("[Frame %d] Shot: ball %d -> %s (steps=%d)", 
                         frame_count, result.pocketed_ball,
                         PhysicsEngine::POCKET_NAMES[result.pocket_id], result.steps);
                }
            }
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(5));
    }
}

} // namespace aether