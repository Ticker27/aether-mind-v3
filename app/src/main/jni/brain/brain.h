#pragma once
// 🥔 AETHER BRAIN v4.0 — Geometry-based shot validation
// Single header — drop-in for Android APK

#include <cmath>
#include <vector>
#include <cfloat>
#include <random>

namespace aether {

// ─── Constants ───
constexpr float TABLE_W = 1.0f, TABLE_H = 0.5f;
constexpr float CUSHION = 0.02f, BALL_R = 0.015f;
constexpr float POCKET_R = 0.03f;

static const float POCKETS[6][2] = {
    {0.02f,0.02f},{0.50f,0.005f},{0.98f,0.02f},
    {0.02f,0.48f},{0.50f,0.495f},{0.98f,0.48f}
};

// ─── Types ───
struct Vec2 { float x=0, y=0; };

struct Ball {
    Vec2 pos;
    int type = 0; // 0=cue, 1=solid, 2=stripe, 8=black
    bool potted = false;
};

struct ShotResult {
    int targetBall = -1;
    int targetPocket = -1;
    float aimAngle = 0.0f;
    float power = 0.3f;
    bool canPot = false;
    bool blocked = false;
    float difficulty = 1.0f;
    float confidence = 0.0f;
};

// ─── Skill Config ───
struct SkillConfig {
    float angleJitter = 0.5f;     // degrees
    float powerJitter = 0.02f;    // fraction
    float reactionDelayMs = 150;  // ms
    float tremorIntensity = 0.1f;
    float maxDifficulty = 0.95f;
    float confidenceGate = 0.15f;
    float aggression = 0.8f;
};

// ─── AI Brain ───
class AetherBrain {
public:
    // Evaluate if a shot can pocket (geometry-based)
    static bool canPocket(const Ball& cue, const Ball& target, int pocket) {
        float px = POCKETS[pocket][0], py = POCKETS[pocket][1];
        float dx = px - target.pos.x, dy = py - target.pos.y;
        float d = std::sqrt(dx*dx + dy*dy);
        if (d < 0.001f) return false;
        
        float cx = target.pos.x - cue.pos.x, cy = target.pos.y - cue.pos.y;
        float cd = std::sqrt(cx*cx + cy*cy);
        if (cd < 0.001f) return false;
        
        float aimA = std::atan2(cy, cx);
        float pocketA = std::atan2(dy, dx);
        float diff = std::fabs(aimA - pocketA);
        if (diff > M_PI) diff = 2*M_PI - diff;
        
        float tolerance = 0.18f + d * 0.12f;
        return diff < tolerance;
    }
    
    // Check for blocking balls
    static bool isBlocked(const std::vector<Ball>& balls, const Ball& target) {
        const Ball& cue = balls[0];
        for (const auto& b : balls) {
            if (b.potted || b.type == 0) continue;
            if (std::abs(b.pos.x - target.pos.x) < 0.001f && 
                std::abs(b.pos.y - target.pos.y) < 0.001f) continue;
            
            float dx = target.pos.x - cue.pos.x, dy = target.pos.y - cue.pos.y;
            float dist = std::sqrt(dx*dx + dy*dy);
            if (dist < 0.001f) continue;
            float nx = dx/dist, ny = dy/dist;
            
            float bx = b.pos.x - cue.pos.x, by = b.pos.y - cue.pos.y;
            float proj = bx*nx + by*ny;
            if (proj < 0 || proj > dist) continue;
            float perp = std::fabs(-ny*bx + nx*by);
            if (perp < BALL_R * 2.4f) return true;
        }
        return false;
    }
    
    // Estimate difficulty
    static float difficulty(const Ball& cue, const Ball& target, int pocket) {
        float d1 = std::hypot(POCKETS[pocket][0]-target.pos.x, 
                              POCKETS[pocket][1]-target.pos.y) / 0.5f;
        float d2 = std::hypot(target.pos.x-cue.pos.x, 
                              target.pos.y-cue.pos.y) / 0.5f;
        return std::min(1.0f, d1*0.5f + d2*0.5f);
    }
    
    // Main decision: choose best shot
    static ShotResult think(const std::vector<Ball>& balls, 
                            const SkillConfig& config) {
        ShotResult best;
        best.confidence = -1.0f;
        const Ball& cue = balls[0];
        
        for (int i = 1; i < (int)balls.size(); i++) {
            if (balls[i].potted || balls[i].type == 0) continue;
            for (int p = 0; p < 6; p++) {
                if (isBlocked(balls, balls[i])) continue;
                
                float diff = difficulty(cue, balls[i], p);
                if (diff > config.maxDifficulty) continue;
                
                bool canPot = canPocket(cue, balls[i], p);
                float conf = canPot ? (1.0f - diff) : 0.0f;
                
                if (conf > best.confidence && conf > config.confidenceGate) {
                    best.targetBall = i;
                    best.targetPocket = p;
                    best.canPot = canPot;
                    best.difficulty = diff;
                    best.confidence = conf;
                }
            }
        }
        
        // Calculate aim angle for best shot
        if (best.targetBall >= 0) {
            const Ball& target = balls[best.targetBall];
            float px = POCKETS[best.targetPocket][0];
            float py = POCKETS[best.targetPocket][1];
            
            // Ghost ball
            float dx = px - target.pos.x, dy = py - target.pos.y;
            float d = std::sqrt(dx*dx + dy*dy);
            float gx = target.pos.x - (dx/d) * BALL_R * 2.0f;
            float gy = target.pos.y - (dy/d) * BALL_R * 2.0f;
            
            float adx = gx - cue.pos.x, ady = gy - cue.pos.y;
            best.aimAngle = std::atan2(ady, adx) * 180.0f / M_PI;
            if (best.aimAngle < 0) best.aimAngle += 360;
            
            best.power = std::min(0.6f, std::hypot(adx, ady) * 0.3f + 0.05f);
        }
        
        return best;
    }
    
    // Apply humanization noise (by skill level)
    static void humanize(ShotResult& shot, const SkillConfig& config) {
        static std::mt19937 rng(std::random_device{}());
        std::normal_distribution<float> angleNoise(0.0f, config.angleJitter);
        std::normal_distribution<float> powerNoise(0.0f, config.powerJitter);
        shot.aimAngle += angleNoise(rng);
        shot.power += powerNoise(rng);
        shot.power = std::max(0.05f, std::min(0.8f, shot.power));
    }
};

} // namespace aether
