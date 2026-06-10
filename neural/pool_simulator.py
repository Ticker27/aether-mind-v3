"""
NEXUS ULTRA - 8 Ball Pool Physics Simulator
============================================
สร้าง synthetic training data สำหรับ Neural Core
- จำลองฟิสิกส์ลูกบิลเลียด (Newtonian deterministic)
- Render frames เป็นภาพ grayscale 128x256
- บันทึกตำแหน่ง + ความเร็วลูกทุกตัว

Usage:
    sim = PoolSimulator()
    game_data = sim.generate_game()  # returns frames + ball states
"""

import numpy as np
import cv2
import math
import random
from typing import List, Dict, Tuple
from dataclasses import dataclass, field


@dataclass
class Ball:
    x: float
    y: float
    vx: float = 0.0
    vy: float = 0.0
    radius: float = 15.0
    color: Tuple[int, int, int] = (255, 255, 255)
    active: bool = True
    number: int = 0
    is_cue: bool = False


@dataclass
class Table:
    width: int = 256
    height: int = 128
    cushion_width: float = 8.0
    friction: float = 0.998
    cushion_damping: float = 0.85
    min_speed: float = 0.1


class PoolSimulator:
    """8-ball pool physics simulator with frame rendering"""

    # Ball colors for 8-ball pool
    BALL_COLORS = {
        0: (255, 255, 255),   # Cue ball
        1: (255, 255, 0),     # Yellow (solid)
        2: (0, 0, 255),       # Blue (solid)
        3: (255, 0, 0),       # Red (solid)
        4: (128, 0, 128),     # Purple (solid)
        5: (255, 128, 0),     # Orange (solid)
        6: (0, 128, 0),       # Green (solid)
        7: (128, 0, 0),       # Maroon (solid)
        8: (0, 0, 0),         # Black (8-ball)
        9: (255, 255, 0),     # Yellow (stripe)
        10: (0, 0, 255),      # Blue (stripe)
        11: (255, 0, 0),      # Red (stripe)
        12: (128, 0, 128),    # Purple (stripe)
        13: (255, 128, 0),    # Orange (stripe)
        14: (0, 128, 0),      # Green (stripe)
        15: (128, 0, 0),      # Maroon (stripe)
    }

    def __init__(self):
        self.table = Table()
        self.balls: List[Ball] = []
        self.frame_count = 0

    def setup_rack(self):
        """จัดลูกบิลเลียดแบบ 8-ball triangle rack"""
        self.balls = []

        # Cue ball
        cue = Ball(
            x=self.table.width * 0.25,
            y=self.table.height * 0.5,
            number=0,
            is_cue=True,
            color=self.BALL_COLORS[0]
        )
        self.balls.append(cue)

        # Rack positions (triangle)
        rack_x = self.table.width * 0.72
        rack_y = self.table.height * 0.5
        ball_spacing = self.table.width * 0.025

        # Standard 8-ball rack: 8 in center
        rack_positions = [
            (0, 0),    # Front
            (-1, 1), (-1, -1),  # Second row
            (-2, 2), (-2, 0), (-2, -2),  # Third row (8 in middle)
            (-3, 3), (-3, 1), (-3, -1), (-3, -3),  # Fourth row
            (-4, 4), (-4, 2), (-4, 0), (-4, -2), (-4, -4),  # Fifth row
        ]

        # Assign numbers (8 must be in center of 3rd row = index 4)
        numbers = list(range(1, 16))
        numbers.remove(8)
        random.shuffle(numbers)
        numbers.insert(4, 8)  # 8-ball in center

        for i, (dx, dy) in enumerate(rack_positions):
            x = rack_x + dx * ball_spacing
            y = rack_y + dy * ball_spacing * 0.866  # sin(60)
            num = numbers[i] if i < 15 else 1
            ball = Ball(
                x=x, y=y,
                number=num,
                color=self.BALL_COLORS[num]
            )
            self.balls.append(ball)

    def apply_cue_shot(self, angle_deg: float, power: float = 5.0):
        """ยิงลูกขาวด้วยมุมและพลังที่กำหนด"""
        cue_ball = self.balls[0]
        angle_rad = math.radians(angle_deg)
        cue_ball.vx = power * math.cos(angle_rad)
        cue_ball.vy = power * math.sin(angle_rad)

    def detect_collision(self, b1: Ball, b2: Ball) -> bool:
        """ตรวจ collision ระหว่างลูก 2 ลูก"""
        dx = b2.x - b1.x
        dy = b2.y - b1.y
        dist = math.sqrt(dx * dx + dy * dy)
        return dist < (b1.radius + b2.radius)

    def resolve_collision(self, b1: Ball, b2: Ball):
        """แก้ปัญหา collision แบบ elastic"""
        dx = b2.x - b1.x
        dy = b2.y - b1.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist == 0:
            return

        # Normal vector
        nx = dx / dist
        ny = dy / dist

        # Relative velocity
        dvx = b1.vx - b2.vx
        dvy = b1.vy - b2.vy

        # Relative velocity along normal
        dvn = dvx * nx + dvy * ny

        # Don't resolve if separating
        if dvn < 0:
            return

        # Update velocities (equal mass)
        b1.vx -= dvn * nx * 0.98  # slight energy loss
        b1.vy -= dvn * ny * 0.98
        b2.vx += dvn * nx * 0.98
        b2.vy += dvn * ny * 0.98

        # Separate overlapping balls
        overlap = (b1.radius + b2.radius - dist) / 2
        b1.x -= overlap * nx
        b1.y -= overlap * ny
        b2.x += overlap * nx
        b2.y += overlap * ny

    def check_cushion(self, ball: Ball):
        """ตรวจขอบโต๊ะและสะท้อน"""
        cw = self.table.cushion_width
        damping = self.table.cushion_damping

        if ball.x - ball.radius < cw:
            ball.x = cw + ball.radius
            ball.vx = abs(ball.vx) * damping
        elif ball.x + ball.radius > self.table.width - cw:
            ball.x = self.table.width - cw - ball.radius
            ball.vx = -abs(ball.vx) * damping

        if ball.y - ball.radius < cw:
            ball.y = cw + ball.radius
            ball.vy = abs(ball.vy) * damping
        elif ball.y + ball.radius > self.table.height - cw:
            ball.y = self.table.height - cw - ball.radius
            ball.vy = -abs(ball.vy) * damping

    def step(self):
        """จำลอง 1 step (ประมาณ 1/60 วินาที)"""
        for ball in self.balls:
            if not ball.active:
                continue

            # Update position
            ball.x += ball.vx
            ball.y += ball.vy

            # Apply friction
            ball.vx *= self.table.friction
            ball.vy *= self.table.friction

            # Stop if too slow
            speed = math.sqrt(ball.vx ** 2 + ball.vy ** 2)
            if speed < self.table.min_speed:
                ball.vx = 0
                ball.vy = 0

            # Check cushion
            self.check_cushion(ball)

        # Check ball-ball collisions
        for i in range(len(self.balls)):
            for j in range(i + 1, len(self.balls)):
                if self.balls[i].active and self.balls[j].active:
                    if self.detect_collision(self.balls[i], self.balls[j]):
                        self.resolve_collision(self.balls[i], self.balls[j])

        self.frame_count += 1

    def render_frame(self, grayscale=True) -> np.ndarray:
        """Render เฟรมปัจจุบันเป็น image"""
        frame = np.zeros((self.table.height, self.table.width, 3), dtype=np.uint8)

        # Draw table (dark green felt)
        cw = int(self.table.cushion_width)
        frame[cw:-cw, cw:-cw] = (34, 60, 34)  # BGR for green felt

        # Draw cushion
        cv2.rectangle(frame, (0, 0),
                      (self.table.width - 1, self.table.height - 1),
                      (80, 60, 40), cw)

        # Draw pockets
        pocket_r = 6
        for px, py in [(cw, cw), (self.table.width // 2, cw),
                       (self.table.width - cw, cw), (cw, self.table.height - cw),
                       (self.table.width // 2, self.table.height - cw),
                       (self.table.width - cw, self.table.height - cw)]:
            cv2.circle(frame, (px, py), pocket_r, (0, 0, 0), -1)

        # Draw balls
        for ball in self.balls:
            if not ball.active:
                continue
            color = ball.color
            cv2.circle(frame, (int(ball.x), int(ball.y)),
                      int(ball.radius), color, -1)
            # Ball outline
            cv2.circle(frame, (int(ball.x), int(ball.y)),
                      int(ball.radius), (200, 200, 200), 1)
            # Stripe indicator for 9-15
            if ball.number >= 9 and ball.number != 0:
                cv2.line(frame,
                        (int(ball.x - ball.radius * 0.5), int(ball.y)),
                        (int(ball.x + ball.radius * 0.5), int(ball.y)),
                        (255, 255, 255), 2)

        if grayscale:
            return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return frame

    def get_ball_states(self) -> List[Dict]:
        """คืนค่าตำแหน่ง + ความเร็วลูกทุกตัว"""
        states = []
        for ball in self.balls:
            states.append({
                'number': ball.number,
                'x': ball.x,
                'y': ball.y,
                'vx': ball.vx,
                'vy': ball.vy,
                'active': ball.active
            })
        return states

    def is_stopped(self) -> bool:
        """เช็คว่าลูกทั้งหมดหยุดแล้ว"""
        for ball in self.balls:
            if ball.active and (abs(ball.vx) > 0.01 or abs(ball.vy) > 0.01):
                return False
        return True

    def generate_game(self, max_frames: int = 300) -> Dict:
        """
        สร้าง game scenario 1 เกม
        Returns: dict with frames, states, metadata
        """
        self.setup_rack()

        # Random shot
        angle = random.uniform(-30, 30)
        power = random.uniform(3.0, 8.0)
        self.apply_cue_shot(angle, power)

        frames = []
        states = []

        for i in range(max_frames):
            frame = self.render_frame(grayscale=True)
            state = self.get_ball_states()
            frames.append(frame)
            states.append(state)

            self.step()

            if self.is_stopped() and i > 30:
                break

        return {
            'frames': np.array(frames),
            'states': states,
            'num_frames': len(frames),
            'shot_angle': angle,
            'shot_power': power
        }


if __name__ == "__main__":
    print("🎱 8-Ball Pool Simulator Test")
    sim = PoolSimulator()
    game = sim.generate_game()
    print(f"   Frames generated: {game['num_frames']}")
    print(f"   Frame shape: {game['frames'][0].shape}")
    print(f"   Shot angle: {game['shot_angle']:.1f}°")
    print(f"   Shot power: {game['shot_power']:.1f}")

    # Save sample frames
    import os
    os.makedirs('/var/minis/workspace/aether_mind/train_data/sample', exist_ok=True)
    for i in range(0, min(10, game['num_frames']), 2):
        path = f'/var/minis/workspace/aether_mind/train_data/sample/frame_{i:04d}.png'
        cv2.imwrite(path, game['frames'][i])
    print(f"   Sample frames saved to train_data/sample/")

    # Print first 3 ball states
    print(f"\n   Ball states (frame 0):")
    for s in game['states'][0][:5]:
        print(f"     Ball {s['number']}: ({s['x']:.1f}, {s['y']:.1f}) v=({s['vx']:.2f}, {s['vy']:.2f})")
