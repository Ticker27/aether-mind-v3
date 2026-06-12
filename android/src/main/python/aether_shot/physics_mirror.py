"""
AETHER SHOT — Layer 1: Physics Mirror (v3 — Self-Contained)
============================================================
Lightweight physics engine built directly into aether_shot.
ไม่มี external dependencies, ไม่ต้อง import physics/engine.py

Physics constants ปรับให้สมจริง:
- Rolling friction: μ = 0.2 → speed decay ≈ 0.14× per second
- Elastic collision: e = 0.95
- Pocket radius: 50mm
"""

import math


class Table:
    W = 2540.0      # mm (standard 9ft)
    H = 1270.0
    CUSHION = 50.0   # cushion width
    POCKET_R = 50.0


class Ball:
    def __init__(self, bid, x, y):
        self.id = bid
        self.x = x
        self.y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = 28.575  # mm
        self.mass = 0.170     # kg
        self.pocketed = False


class PhysicsMirror:
    """
    Self-contained deterministic physics engine
    No external imports needed
    """
    
    # 6 pockets
    POCKETS = [
        (Table.CUSHION, Table.CUSHION),                           # top-left
        (Table.W / 2, Table.CUSHION),                             # top-center
        (Table.W - Table.CUSHION, Table.CUSHION),                 # top-right
        (Table.CUSHION, Table.H - Table.CUSHION),                 # bottom-left
        (Table.W / 2, Table.H - Table.CUSHION),                   # bottom-center
        (Table.W - Table.CUSHION, Table.H - Table.CUSHION)        # bottom-right
    ]
    POCKET_NAMES = ["top-left", "top-center", "top-right",
                     "bottom-left", "bottom-center", "bottom-right"]
    
    # Physics
    G = 9.81        # m/s²
    MU = 0.02       # rolling friction coefficient (low for pool)
    E = 0.95        # coefficient of restitution
    WALL_E = 0.8    # wall bounce energy retention
    
    def __init__(self):
        self.balls = []
        self.step_count = 0
        
    def setup_table(self, cue_pos, ball_positions):
        """Setup balls from position data"""
        self.balls = []
        self.balls.append(Ball(0, cue_pos[0], cue_pos[1]))
        for b in ball_positions:
            bid, bx, by = b[0], b[1], b[2]
            self.balls.append(Ball(bid, bx, by))
        self.step_count = 0
    
    def step(self, dt=0.005):
        """One physics step"""
        self.step_count += 1
        
        # Update positions + apply friction
        for b in self.balls:
            if b.pocketed:
                continue
            
            speed = math.hypot(b.vx, b.vy)
            
            # Rolling friction: deceleration = mu * g
            if speed > 0:
                friction_decel = self.MU * self.G * 1000  # mm/s²
                speed_loss = friction_decel * dt
                
                if speed_loss >= speed:
                    b.vx = 0.0
                    b.vy = 0.0
                else:
                    ratio = (speed - speed_loss) / speed
                    b.vx *= ratio
                    b.vy *= ratio
            
            # Update position
            b.x += b.vx * dt
            b.y += b.vy * dt
            
            # Wall collision
            self._wall_collision(b)
        
        # Ball-ball collisions
        for i in range(len(self.balls)):
            for j in range(i + 1, len(self.balls)):
                self._ball_collision(self.balls[i], self.balls[j])
        
        # Pocket check
        for b in self.balls:
            if b.pocketed:
                continue
            for px, py in self.POCKETS:
                dx = b.x - px
                dy = b.y - py
                if math.hypot(dx, dy) < Table.POCKET_R - b.radius * 0.5:
                    b.pocketed = True
                    b.vx = 0.0
                    b.vy = 0.0
                    break
    
    def _wall_collision(self, b):
        """Bounce off walls"""
        margin = b.radius + 5
        damp = self.WALL_E
        
        if b.x < margin:
            b.x = margin
            b.vx = abs(b.vx) * damp
        elif b.x > Table.W - margin:
            b.x = Table.W - margin
            b.vx = -abs(b.vx) * damp
        
        if b.y < margin:
            b.y = margin
            b.vy = abs(b.vy) * damp
        elif b.y > Table.H - margin:
            b.y = Table.H - margin
            b.vy = -abs(b.vy) * damp
    
    def _ball_collision(self, b1, b2):
        """Elastic collision between two balls"""
        if b1.pocketed or b2.pocketed:
            return
        
        dx = b2.x - b1.x
        dy = b2.y - b1.y
        dist = math.hypot(dx, dy)
        min_dist = b1.radius + b2.radius
        
        if dist >= min_dist or dist < 0.001:
            return
        
        # Normal direction
        nx = dx / dist
        ny = dy / dist
        
        # Relative velocity along normal
        dvx = b1.vx - b2.vx
        dvy = b1.vy - b2.vy
        dvn = dvx * nx + dvy * ny
        
        if dvn < 0:  # approaching
            # Equal mass: swap velocities along normal
            impulse = dvn * self.E
            
            b1.vx -= impulse * nx
            b1.vy -= impulse * ny
            b2.vx += impulse * nx
            b2.vy += impulse * ny
            
            # Separate overlapping
            overlap = (min_dist - dist) / 2
            b1.x -= overlap * nx
            b1.y -= overlap * ny
            b2.x += overlap * nx
            b2.y += overlap * ny
    
    def simulate(self, cue_pos, angle_deg, power, ball_positions=None, max_steps=500):
        """
        Simulate a shot and return result
        
        Args:
            cue_pos: (x, y) cue ball position
            angle_deg: aim angle in degrees (0 = right, 90 = down)
            power: 0-10
            ball_positions: [(id, x, y, is_target), ...]
            max_steps: max simulation steps
            
        Returns:
            dict with result
        """
        if ball_positions:
            self.setup_table(cue_pos, ball_positions)
        else:
            self.balls = [Ball(0, cue_pos[0], cue_pos[1])]
        
        # Apply force
        cue = self.balls[0]
        angle_rad = math.radians(angle_deg)
        speed = power * 300.0  # mm/s (power 5 = 1500 mm/s ≈ realistic)
        cue.vx = speed * math.cos(angle_rad)
        cue.vy = speed * math.sin(angle_rad)
        
        # Run simulation
        trajectory = []
        for _ in range(max_steps):
            frame = [(b.id, b.x, b.y, b.vx, b.vy, b.pocketed) for b in self.balls]
            trajectory.append(frame)
            self.step(dt=0.005)
            
            # Stop if all stopped
            moving = any(not b.pocketed and (abs(b.vx) > 1 or abs(b.vy) > 1) for b in self.balls)
            if not moving and len(trajectory) > 20:
                break
        
        pocketed = [b.id for b in self.balls if b.pocketed]
        cue_pocketed = self.balls[0].pocketed
        
        return {
            'success': len(pocketed) > 0 and not cue_pocketed,
            'pocketed': pocketed,
            'cue_pocketed': cue_pocketed,
            'scratch': cue_pocketed,
            'steps': len(trajectory),
            'trajectory': trajectory
        }
    
    def find_best_shot(self, cue_pos, ball_positions):
        """
        Find the best shot given current table state
        
        Uses geometry + physics simulation to validate shots.
        """
        targets = [b for b in ball_positions if len(b) > 3 and b[3]]
        if not targets:
            return None
        
        cue_x, cue_y = cue_pos
        best = None
        best_score = -9999
        
        for target in targets:
            tid, tx, ty = target[0], target[1], target[2]
            ctd = math.hypot(tx - cue_x, ty - cue_y)
            if ctd < 5:
                continue
            cue_to_target_angle = math.degrees(math.atan2(ty - cue_y, tx - cue_x))
            
            for pid in range(6):
                px, py = self.POCKETS[pid]
                ttd = math.hypot(px - tx, py - ty)
                pocket_angle = math.degrees(math.atan2(py - ty, px - tx))
                
                # Check: cue ball must be on the correct side
                # The cue→target angle should roughly point toward the pocket
                angle_diff = pocket_angle - cue_to_target_angle
                if angle_diff > 180: angle_diff -= 360
                if angle_diff < -180: angle_diff += 360
                
                # For a cut shot, the cue doesn't point directly at pocket
                # but the closer, the better. Max usable difference ~60°
                if abs(angle_diff) > 90:
                    continue  # impossible geometry
                
                # Score based on geometry
                align = max(0, 1 - abs(angle_diff) / 90)
                dist_factor = max(0, 1 - ttd / (Table.W * 0.7))
                score = (align * 50) + (dist_factor * 40) + 10
                
                if score > best_score:
                    best_score = score
                    power = min(8, max(3, ctd / 300 + ttd / 500))
                    
                    best = {
                        'target_ball': tid,
                        'target_pocket': pid,
                        'pocket_name': self.POCKET_NAMES[pid],
                        'angle': round(cue_to_target_angle, 1),
                        'power': round(power, 1),
                        'score': round(score, 1),
                        'cut_angle': round(abs(angle_diff), 1),
                        'distance': round(ctd, 0)
                    }
        
        # If we have a candidate, verify with physics simulation
        if best:
            for pw_adjust in [0, -1, 1, -2, 2, -0.5, 0.5]:
                test_power = best['power'] + pw_adjust
                if test_power < 2 or test_power > 9:
                    continue
                r = self.simulate(cue_pos, best['angle'], test_power, ball_positions)
                if r.get('success'):
                    best['power'] = round(test_power, 1)
                    best['physics_verified'] = True
                    return best
            
            # Even if no verified shot, return best geometry with note
            best['physics_verified'] = False
        
        return best
    
    def verify_shot(self, cue_pos, angle_deg, power, ball_positions, target_ball_id):
        """Verify if a shot will pocket the target ball"""
        result = self.simulate(cue_pos, angle_deg, power, ball_positions)
        result['target_hit'] = target_ball_id in result['pocketed']
        return result


# Global singleton
mirror = PhysicsMirror()