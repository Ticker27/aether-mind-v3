#pragma once
#include <vector>
#include <cmath>
#include <algorithm>

namespace aether {

struct Ball {
    int id = 0;
    float x = 0, y = 0;
    float vx = 0, vy = 0;
    bool active = true;
    bool pocketed = false;
    static constexpr float RADIUS = 28.575f;
    static constexpr float MASS = 0.170f;
};

struct ShotResult {
    bool success = false;
    int pocketed_ball = -1;
    int pocket_id = -1;
    bool scratch = false;
    int steps = 0;
    float final_x = 0, final_y = 0;
};

class PhysicsEngine {
public:
    static constexpr float TABLE_W = 2540.0f;
    static constexpr float TABLE_H = 1270.0f;
    static constexpr float POCKET_R = 50.0f;
    static constexpr float FRICTION = 0.985f;
    static constexpr float RESTITUTION = 0.9f;
    static constexpr float WALL_RESTITUTION = 0.7f;

    static constexpr float POCKETS[6][2] = {
        {0, 0}, {TABLE_W / 2, 0}, {TABLE_W, 0},
        {0, TABLE_H}, {TABLE_W / 2, TABLE_H}, {TABLE_W, TABLE_H}
    };
    static constexpr const char* POCKET_NAMES[6] = {
        "top-left", "top-center", "top-right",
        "bottom-left", "bottom-center", "bottom-right"
    };

    std::vector<Ball> balls;

    void setup_balls() {
        balls.clear();
        balls.push_back({0, 400, 800, 0, 0, true, false}); // cue
        balls.push_back({1, 900, 750, 0, 0, true, false}); // target 1
        balls.push_back({2, 1200, 500, 0, 0, true, false});
        balls.push_back({3, 1400, 600, 0, 0, true, false});
        balls.push_back({4, 1600, 800, 0, 0, true, false});
        balls.push_back({5, 1300, 700, 0, 0, true, false});
        balls.push_back({6, 1100, 850, 0, 0, true, false});
        balls.push_back({7, 1700, 650, 0, 0, true, false});
        balls.push_back({8, 1800, 750, 0, 0, true, false});
        // fill rest
        for (int i = 9; i < 16; i++)
            balls.push_back({i, 1000 + (float)(i*30), 600 + (float)((i%3-1)*30), 0, 0, true, false});
    }

    void apply_shot(float angle_deg, float power) {
        if (balls.empty() || !balls[0].active) return;
        float angle_rad = angle_deg * M_PI / 180.0f;
        float force = power * 120.0f;
        balls[0].vx = force * std::cos(angle_rad) / Ball::MASS;
        balls[0].vy = force * std::sin(angle_rad) / Ball::MASS;
    }

    ShotResult simulate(int max_steps = 800) {
        ShotResult result;
        for (int step = 0; step < max_steps; step++) {
            // update positions
            for (auto& b : balls) {
                if (!b.active || b.pocketed) continue;
                b.x += b.vx * 0.005f;
                b.y += b.vy * 0.005f;
                b.vx *= FRICTION;
                b.vy *= FRICTION;

                // cushion bounce
                if (b.x - Ball::RADIUS < 0) { b.x = Ball::RADIUS; b.vx = -b.vx * WALL_RESTITUTION; }
                if (b.x + Ball::RADIUS > TABLE_W) { b.x = TABLE_W - Ball::RADIUS; b.vx = -b.vx * WALL_RESTITUTION; }
                if (b.y - Ball::RADIUS < 0) { b.y = Ball::RADIUS; b.vy = -b.vy * WALL_RESTITUTION; }
                if (b.y + Ball::RADIUS > TABLE_H) { b.y = TABLE_H - Ball::RADIUS; b.vy = -b.vy * WALL_RESTITUTION; }

                // pocket check
                for (int p = 0; p < 6; p++) {
                    float dx = b.x - POCKETS[p][0];
                    float dy = b.y - POCKETS[p][1];
                    if (dx*dx + dy*dy < POCKET_R * POCKET_R) {
                        b.pocketed = true;
                        b.vx = 0; b.vy = 0;
                        if (b.id == 0) result.scratch = true;
                        else { result.pocketed_ball = b.id; result.pocket_id = p; }
                        break;
                    }
                }
            }

            // ball-ball collision
            for (size_t i = 0; i < balls.size(); i++) {
                for (size_t j = i + 1; j < balls.size(); j++) {
                    auto& b1 = balls[i];
                    auto& b2 = balls[j];
                    if (!b1.active || b1.pocketed || !b2.active || b2.pocketed) continue;
                    float dx = b2.x - b1.x;
                    float dy = b2.y - b1.y;
                    float dist = std::sqrt(dx*dx + dy*dy);
                    float min_dist = Ball::RADIUS * 2;
                    if (dist < min_dist && dist > 0.001f) {
                        // separate
                        float overlap = min_dist - dist;
                        float nx = dx / dist, ny = dy / dist;
                        b1.x -= nx * overlap / 2;
                        b1.y -= ny * overlap / 2;
                        b2.x += nx * overlap / 2;
                        b2.y += ny * overlap / 2;
                        // impulse
                        float dvx = b1.vx - b2.vx, dvy = b1.vy - b2.vy;
                        float dvn = dvx * nx + dvy * ny;
                        if (dvn > 0) {
                            float imp = 2 * dvn / (Ball::MASS + Ball::MASS);
                            b1.vx -= imp * Ball::MASS * nx * RESTITUTION;
                            b1.vy -= imp * Ball::MASS * ny * RESTITUTION;
                            b2.vx += imp * Ball::MASS * nx * RESTITUTION;
                            b2.vy += imp * Ball::MASS * ny * RESTITUTION;
                        }
                    }
                }
            }

            // check if all stopped
            bool all_stopped = true;
            for (auto& b : balls) {
                if (b.active && !b.pocketed && (std::abs(b.vx) > 0.5f || std::abs(b.vy) > 0.5f)) {
                    all_stopped = false;
                    break;
                }
            }
            if (all_stopped && step > 30) {
                result.steps = step;
                result.success = result.pocketed_ball > 0 && !result.scratch;
                break;
            }
            result.steps = step;
        }
        return result;
    }

    ShotResult find_best_shot(float cue_x, float cue_y) {
        ShotResult best;
        float best_score = -9999;

        for (size_t i = 1; i < balls.size(); i++) {
            if (!balls[i].active || balls[i].pocketed) continue;
            float tx = balls[i].x, ty = balls[i].y;
            float ctd = std::sqrt((tx-cue_x)*(tx-cue_x) + (ty-cue_y)*(ty-cue_y));
            if (ctd < 5) continue;

            float cue_angle = std::atan2(ty - cue_y, tx - cue_x) * 180.0f / M_PI;

            for (int p = 0; p < 6; p++) {
                float px = POCKETS[p][0], py = POCKETS[p][1];
                float ttd = std::sqrt((px-tx)*(px-tx) + (py-ty)*(py-ty));
                float pocket_angle = std::atan2(py - ty, px - tx) * 180.0f / M_PI;

                float diff = pocket_angle - cue_angle;
                if (diff > 180) diff -= 360;
                if (diff < -180) diff += 360;
                if (std::abs(diff) > 90) continue;

                float align = std::max(0.0f, 1.0f - std::abs(diff) / 90.0f);
                float score = align * 50.0f + std::max(0.0f, 1.0f - ttd / (TABLE_W * 0.7f)) * 40.0f + 10.0f;

                if (score > best_score) {
                    best_score = score;
                    float power = std::min(8.0f, std::max(3.0f, ctd / 300.0f + ttd / 500.0f));

                    // verify with physics
                    setup_balls();
                    balls[0].x = cue_x; balls[0].y = cue_y;
                    apply_shot(cue_angle, power);
                    ShotResult sim = simulate();
                    if (sim.success && sim.pocketed_ball == (int)i) {
                        best = sim;
                        return best;
                    }
                }
            }
        }
        return best;
    }
};

} // namespace aether