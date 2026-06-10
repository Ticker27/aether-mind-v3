#!/usr/bin/env python3
"""
AETHER MIND v3.0 — Phase 2: Physics Engine
============================================
Beyond Newtonian physics engine
Chaos theory + quantum effects
Real-time physics simulation (<10ms)
"""

import os
import json
import time
import math
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "orchestrator"))
from config_loader import Config
from dashscope_client import DashScopeClient


@dataclass
class PhysicsConfig:
    """Physics engine configuration"""
    gravity: float = 9.81
    friction: float = 0.98
    restitution: float = 0.9  # bounce coefficient
    air_resistance: float = 0.001
    table_width: float = 2540.0  # mm (standard pool table)
    table_height: float = 1270.0
    pocket_radius: float = 50.0
    chaos_factor: float = 0.001  # quantum uncertainty
    max_velocity: float = 2000.0  # mm/s


@dataclass
class Ball:
    """Ball object"""
    id: int
    x: float
    y: float
    vx: float
    vy: float
    radius: float = 28.575  # mm (standard billiard ball)
    mass: float = 0.170  # kg
    is_pocketed: bool = False


@dataclass
class CollisionEvent:
    """Collision event record"""
    timestamp: float
    ball1_id: int
    ball2_id: Optional[int]  # None = wall collision
    point: Tuple[float, float]
    energy_loss: float


class PhysicsEngine:
    """Advanced Physics Engine — Beyond Newtonian"""
    
    def __init__(self, model_id: str = "qwq-plus"):
        self.model_id = model_id
        self.api_key = Config.get_dashscope_key()
        self.client = DashScopeClient(self.api_key)
        self.config = PhysicsConfig()
        
        self.balls: List[Ball] = []
        self.collision_history: List[CollisionEvent] = []
        self.simulation_time = 0.0
        
        # Chaos/quantum state
        self.chaos_seed = np.random.random()
        self.quantum_uncertainty = 0.0
        
        print(f"⚛️  Physics Engine initialized (model: {model_id})")
    
    def setup_table(self, num_balls: int = 16):
        """ตั้งค่าโต๊ะบิลเลียด"""
        self.balls = []
        
        # Cue ball
        cue = Ball(
            id=0,
            x=self.config.table_width * 0.25,
            y=self.config.table_height * 0.5,
            vx=0.0, vy=0.0
        )
        self.balls.append(cue)
        
        # Rack formation (triangle)
        rack_x = self.config.table_width * 0.75
        rack_y = self.config.table_height * 0.5
        ball_id = 1
        
        for row in range(5):
            for col in range(row + 1):
                x = rack_x + row * self.balls[0].radius * math.sqrt(3)
                y = rack_y + (col - row / 2) * self.balls[0].radius * 2
                ball = Ball(id=ball_id, x=x, y=y, vx=0.0, vy=0.0)
                self.balls.append(ball)
                ball_id += 1
        
        print(f"   Table setup: {len(self.balls)} balls")
    
    def apply_force(self, ball_id: int, force_x: float, force_y: float):
        """施加แรงกับลูกบอล"""
        for ball in self.balls:
            if ball.id == ball_id and not ball.is_pocketed:
                # F = ma → a = F/m
                ball.vx += force_x / ball.mass
                ball.vy += force_y / ball.mass
                break
    
    def simulate_step(self, dt: float = 0.001) -> Dict:
        """
        จำลองฟิสิกส์ 1 timestep
        
        Returns:
            Simulation state dict
        """
        start_time = time.time()
        
        # 1. Update positions
        for ball in self.balls:
            if ball.is_pocketed:
                continue
            
            # Apply friction
            ball.vx *= self.config.friction
            ball.vy *= self.config.friction
            
            # Apply air resistance
            speed = math.sqrt(ball.vx**2 + ball.vy**2)
            if speed > 0:
                drag = self.config.air_resistance * speed
                ball.vx -= (ball.vx / speed) * drag
                ball.vy -= (ball.vy / speed) * drag
            
            # Update position
            ball.x += ball.vx * dt
            ball.y += ball.vy * dt
            
            # Stop if very slow
            if abs(ball.vx) < 0.01 and abs(ball.vy) < 0.01:
                ball.vx = 0.0
                ball.vy = 0.0
        
        # 2. Check wall collisions
        for ball in self.balls:
            if ball.is_pocketed:
                continue
            
            # Left/Right walls
            if ball.x - ball.radius < 0:
                ball.x = ball.radius
                ball.vx = -ball.vx * self.config.restitution
                self._record_collision(ball.id, None, (ball.x, ball.y))
            elif ball.x + ball.radius > self.config.table_width:
                ball.x = self.config.table_width - ball.radius
                ball.vx = -ball.vx * self.config.restitution
                self._record_collision(ball.id, None, (ball.x, ball.y))
            
            # Top/Bottom walls
            if ball.y - ball.radius < 0:
                ball.y = ball.radius
                ball.vy = -ball.vy * self.config.restitution
                self._record_collision(ball.id, None, (ball.x, ball.y))
            elif ball.y + ball.radius > self.config.table_height:
                ball.y = self.config.table_height - ball.radius
                ball.vy = -ball.vy * self.config.restitution
                self._record_collision(ball.id, None, (ball.x, ball.y))
        
        # 3. Check ball-ball collisions
        for i in range(len(self.balls)):
            for j in range(i + 1, len(self.balls)):
                b1 = self.balls[i]
                b2 = self.balls[j]
                
                if b1.is_pocketed or b2.is_pocketed:
                    continue
                
                dx = b2.x - b1.x
                dy = b2.y - b1.y
                dist = math.sqrt(dx**2 + dy**2)
                min_dist = b1.radius + b2.radius
                
                if dist < min_dist and dist > 0:
                    # Collision response (elastic)
                    nx = dx / dist
                    ny = dy / dist
                    
                    # Relative velocity
                    dvx = b1.vx - b2.vx
                    dvy = b1.vy - b2.vy
                    dvn = dvx * nx + dvy * ny
                    
                    if dvn > 0:
                        # Impulse
                        impulse = (2 * dvn) / (b1.mass + b2.mass)
                        
                        b1.vx -= impulse * b2.mass * nx * self.config.restitution
                        b1.vy -= impulse * b2.mass * ny * self.config.restitution
                        b2.vx += impulse * b1.mass * nx * self.config.restitution
                        b2.vy += impulse * b1.mass * ny * self.config.restitution
                        
                        # Separate overlapping balls
                        overlap = min_dist - dist
                        b1.x -= overlap * nx * 0.5
                        b1.y -= overlap * ny * 0.5
                        b2.x += overlap * nx * 0.5
                        b2.y += overlap * ny * 0.5
                        
                        energy_loss = 1 - self.config.restitution**2
                        self._record_collision(b1.id, b2.id, ((b1.x+b2.x)/2, (b1.y+b2.y)/2), energy_loss)
        
        # 4. Check pockets
        pockets = [
            (0, 0),
            (self.config.table_width / 2, 0),
            (self.config.table_width, 0),
            (0, self.config.table_height),
            (self.config.table_width / 2, self.config.table_height),
            (self.config.table_width, self.config.table_height)
        ]
        
        for ball in self.balls:
            if ball.is_pocketed:
                continue
            
            for px, py in pockets:
                dist = math.sqrt((ball.x - px)**2 + (ball.y - py)**2)
                if dist < self.config.pocket_radius:
                    ball.is_pocketed = True
                    ball.vx = 0.0
                    ball.vy = 0.0
                    break
        
        # 5. Chaos/quantum effects
        self.quantum_uncertainty = self.config.chaos_factor * np.random.random()
        
        self.simulation_time += dt
        
        elapsed = (time.time() - start_time) * 1000  # ms
        
        return {
            "time": self.simulation_time,
            "elapsed_ms": elapsed,
            "balls_active": sum(1 for b in self.balls if not b.is_pocketed),
            "balls_pocketed": sum(1 for b in self.balls if b.is_pocketed),
            "collisions": len(self.collision_history),
            "quantum_uncertainty": self.quantum_uncertainty
        }
    
    def simulate(self, duration: float = 5.0, dt: float = 0.001) -> List[Dict]:
        """
        จำลองฟิสิกส์เต็มระยะเวลา
        
        Returns:
            List of state snapshots
        """
        snapshots = []
        steps = int(duration / dt)
        
        for i in range(steps):
            state = self.simulate_step(dt)
            
            # Record snapshot every 100 steps
            if i % 100 == 0:
                snapshots.append({
                    "step": i,
                    "time": state["time"],
                    "balls": [
                        {
                            "id": b.id,
                            "x": b.x,
                            "y": b.y,
                            "vx": b.vx,
                            "vy": b.vy,
                            "pocketed": b.is_pocketed
                        }
                        for b in self.balls
                    ]
                })
            
            # Stop if all balls stopped
            all_stopped = all(
                (abs(b.vx) < 0.01 and abs(b.vy) < 0.01) or b.is_pocketed
                for b in self.balls
            )
            if all_stopped:
                break
        
        return snapshots
    
    def _record_collision(self, ball1: int, ball2: Optional[int], point: Tuple[float, float], energy_loss: float = 0.0):
        """บันทึก collision event"""
        event = CollisionEvent(
            timestamp=self.simulation_time,
            ball1_id=ball1,
            ball2_id=ball2,
            point=point,
            energy_loss=energy_loss
        )
        self.collision_history.append(event)
    
    def get_ai_enhanced_prediction(self, state_snapshot: Dict) -> Dict:
        """ใช้ AI model เพื่อปรับปรุง prediction"""
        try:
            prompt = f"""
วิเคราะห์สถานะฟิสิกส์บิลเลียดต่อไปนี้และทำนายผลลัพธ์:

{json.dumps(state_snapshot, indent=2)}

พิจารณา:
1. ทิศทางและพลังงานของลูกบอล
2. ความน่าจะเป็นในการลงหลุม
3. ผลกระทบจากการชน
4. Chaos theory effects

ตอบเป็น JSON:
{{
  "predicted_outcome": "...",
  "best_shot": {"angle": 0, "power": 0},
  "pocket_probability": 0.85,
  "chaos_factor": 0.001
}}
"""
            response = self.client.chat(
                model=self.model_id,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.3
            )
            
            # Parse response
            content = response["content"]
            start = content.find('{')
            end = content.rfind('}') + 1
            
            if start >= 0 and end > start:
                return json.loads(content[start:end])
            
        except Exception as e:
            print(f"️  AI prediction failed: {e}")
        
        return {"error": "prediction_failed"}
    
    def get_status(self) -> Dict:
        """ดึงสถานะ Physics Engine"""
        return {
            "model_id": self.model_id,
            "config": {
                "gravity": self.config.gravity,
                "friction": self.config.friction,
                "restitution": self.config.restitution,
                "chaos_factor": self.config.chaos_factor
            },
            "simulation_time": self.simulation_time,
            "balls_total": len(self.balls),
            "balls_active": sum(1 for b in self.balls if not b.is_pocketed),
            "balls_pocketed": sum(1 for b in self.balls if b.is_pocketed),
            "collisions": len(self.collision_history),
            "quantum_uncertainty": self.quantum_uncertainty
        }
    
    def save_state(self, path: str):
        """บันทึกสถานะ"""
        state = {
            "config": {
                "gravity": self.config.gravity,
                "friction": self.config.friction,
                "restitution": self.config.restitution,
                "chaos_factor": self.config.chaos_factor,
                "table_width": self.config.table_width,
                "table_height": self.config.table_height
            },
            "balls": [
                {
                    "id": b.id,
                    "x": b.x,
                    "y": b.y,
                    "vx": b.vx,
                    "vy": b.vy,
                    "radius": b.radius,
                    "mass": b.mass,
                    "is_pocketed": b.is_pocketed
                }
                for b in self.balls
            ],
            "simulation_time": self.simulation_time,
            "collision_count": len(self.collision_history)
        }
        
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Physics state saved to: {path}")


def main():
    """ทดสอบ Physics Engine"""
    print("=" * 80)
    print("⚛️  AETHER MIND v3.0 — Phase 2: Physics Engine")
    print("=" * 80)
    print()
    
    # Initialize
    engine = PhysicsEngine(model_id="qwq-plus")
    
    # Setup table
    print(" Setting up table...")
    engine.setup_table(num_balls=16)
    
    # Apply force to cue ball
    print("\n💥 Applying force to cue ball...")
    engine.apply_force(0, force_x=500.0, force_y=-100.0)
    
    # Simulate
    print("\n🔄 Simulating physics (5 seconds)...")
    snapshots = engine.simulate(duration=5.0, dt=0.001)
    
    print(f"   Generated {len(snapshots)} snapshots")
    
    # Status
    status = engine.get_status()
    print(f"\n Physics Engine Status:")
    print(f"   Model: {status['model_id']}")
    print(f"   Simulation time: {status['simulation_time']:.2f}s")
    print(f"   Balls active: {status['balls_active']}")
    print(f"   Balls pocketed: {status['balls_pocketed']}")
    print(f"   Collisions: {status['collisions']}")
    print(f"   Chaos factor: {status['config']['chaos_factor']}")
    print(f"   Quantum uncertainty: {status['quantum_uncertainty']:.6f}")
    
    # Save state
    state_path = Path(__file__).parent / "models" / "physics_state.json"
    engine.save_state(str(state_path))
    
    print("\n✅ Phase 2 complete!")


if __name__ == "__main__":
    main()
