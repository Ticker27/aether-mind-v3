#pragma once
#include <vector>
#include <cmath>
#include <algorithm>

namespace aether {

struct Ball {
    int id = 0; float x = 0, y = 0; float vx = 0, vy = 0;
    bool active = true, pocketed = false;
    static constexpr float RADIUS = 28.575f, MASS = 0.170f;
};

struct ShotResult {
    bool success = false; int pocketed_ball = -1; int pocket_id = -1;
    bool scratch = false; int steps = 0;
};

class PhysicsEngine {
public:
    static constexpr float TABLE_W = 2540, TABLE_H = 1270;
    static constexpr float POCKET_R = 50, FRICTION = 0.985f;
    static constexpr float RESTITUTION = 0.9f, WALL_REST = 0.7f;

    static constexpr float POCKETS[6][2] = {
        {0,0}, {TABLE_W/2,0}, {TABLE_W,0},
        {0,TABLE_H}, {TABLE_W/2,TABLE_H}, {TABLE_W,TABLE_H}
    };
    static constexpr const char* PNAME[6] = {"TL","TC","TR","BL","BC","BR"};

    std::vector<Ball> balls;

    void setup() {
        balls.clear();
        float rack_x = TABLE_W * 0.72f, rack_y = TABLE_H * 0.5f;
        float spacing = TABLE_W * 0.025f;
        int rack[15] = {1,11,2,12,3,8,13,4,14,5,15,6,10,7,9};
        balls.push_back({0, TABLE_W*0.25f, TABLE_H*0.5f, 0,0, true,false});
        int idx = 0;
        for (int row = 0; row < 5; row++)
            for (int col = 0; col <= row; col++) {
                float x = rack_x + row * spacing * 1.5f;
                float y = rack_y + (col - row/2.0f) * spacing * 1.75f;
                if (idx < 15) balls.push_back({rack[idx++], x, y, 0,0, true,false});
            }
    }

    void apply_shot(float angle_deg, float power) {
        if (balls.empty()) return;
        float rad = angle_deg * M_PI / 180.0f;
        float f = power * 120.0f;
        balls[0].vx = f * cos(rad) / Ball::MASS;
        balls[0].vy = f * sin(rad) / Ball::MASS;
    }

    ShotResult simulate(int max = 800) {
        ShotResult r;
        for (int s = 0; s < max; s++) {
            for (auto& b : balls) {
                if (!b.active || b.pocketed) continue;
                b.x += b.vx * 0.005f; b.y += b.vy * 0.005f;
                b.vx *= FRICTION; b.vy *= FRICTION;
                if (b.x - Ball::RADIUS < 0) { b.x = Ball::RADIUS; b.vx = -b.vx * WALL_REST; }
                if (b.x + Ball::RADIUS > TABLE_W) { b.x = TABLE_W - Ball::RADIUS; b.vx = -b.vx * WALL_REST; }
                if (b.y - Ball::RADIUS < 0) { b.y = Ball::RADIUS; b.vy = -b.vy * WALL_REST; }
                if (b.y + Ball::RADIUS > TABLE_H) { b.y = TABLE_H - Ball::RADIUS; b.vy = -b.vy * WALL_REST; }
                for (int p = 0; p < 6; p++) {
                    float dx = b.x - POCKETS[p][0], dy = b.y - POCKETS[p][1];
                    if (dx*dx + dy*dy < POCKET_R*POCKET_R) {
                        b.pocketed = true; b.vx = 0; b.vy = 0;
                        if (b.id == 0) r.scratch = true;
                        else { r.pocketed_ball = b.id; r.pocket_id = p; }
                    }
                }
            }
            for (size_t i = 0; i < balls.size(); i++)
                for (size_t j = i+1; j < balls.size(); j++) {
                    auto& b1 = balls[i], &b2 = balls[j];
                    if (!b1.active||b1.pocketed||!b2.active||b2.pocketed) continue;
                    float dx = b2.x-b1.x, dy = b2.y-b1.y, dist = sqrt(dx*dx+dy*dy);
                    float min_d = Ball::RADIUS*2;
                    if (dist < min_d && dist > 0.001f) {
                        float ov = (min_d-dist)/2, nx = dx/dist, ny = dy/dist;
                        b1.x -= nx*ov; b1.y -= ny*ov; b2.x += nx*ov; b2.y += ny*ov;
                        float dvx = b1.vx-b2.vx, dvy = b1.vy-b2.vy, dvn = dvx*nx + dvy*ny;
                        if (dvn > 0) {
                            float imp = 2*dvn / (Ball::MASS+Ball::MASS);
                            b1.vx -= imp*Ball::MASS*nx*RESTITUTION;
                            b1.vy -= imp*Ball::MASS*ny*RESTITUTION;
                            b2.vx += imp*Ball::MASS*nx*RESTITUTION;
                            b2.vy += imp*Ball::MASS*ny*RESTITUTION;
                        }
                    }
                }
            bool stopped = true;
            for (auto& b : balls)
                if (b.active && !b.pocketed && (fabs(b.vx)>0.5f||fabs(b.vy)>0.5f)) { stopped=false; break; }
            if (stopped && s > 30) { r.steps = s; r.success = r.pocketed_ball > 0 && !r.scratch; break; }
            r.steps = s;
        }
        return r;
    }

    ShotResult best_shot() {
        ShotResult best; float best_score = -9999;
        float cx = balls.empty() ? 400 : balls[0].x;
        float cy = balls.empty() ? 800 : balls[0].y;
        for (size_t i = 1; i < balls.size(); i++) {
            if (!balls[i].active || balls[i].pocketed) continue;
            float tx = balls[i].x, ty = balls[i].y;
            float ctd = sqrt((tx-cx)*(tx-cx)+(ty-cy)*(ty-cy));
            float ang = atan2(ty-cy, tx-cx) * 180 / M_PI;
            for (int p = 0; p < 6; p++) {
                float ttd = sqrt((POCKETS[p][0]-tx)*(POCKETS[p][0]-tx)+(POCKETS[p][1]-ty)*(POCKETS[p][1]-ty));
                float pa = atan2(POCKETS[p][1]-ty, POCKETS[p][0]-tx) * 180 / M_PI;
                float diff = pa - ang;
                if (diff > 180) diff -= 360; if (diff < -180) diff += 360;
                if (fabs(diff) > 90) continue;
                float sc = std::max(0.0f, 1.0f-fabs(diff)/90.0f)*50.0f + std::max(0.0f, 1.0f-ttd/(TABLE_W*0.7f))*40.0f + 10.0f;
                if (sc > best_score) {
                    best_score = sc;
                    float pw = std::min(8.0f, std::max(3.0f, ctd/300.0f+ttd/500.0f));
                    apply_shot(ang, pw);
                    ShotResult sim = simulate();
                    setup();
                    if (sim.success && sim.pocketed_ball == (int)i) return sim;
                }
            }
        }
        return best;
    }
};

} // namespace aether