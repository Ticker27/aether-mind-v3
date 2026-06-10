"""
NEXUS ULTRA - Phase 3: Physics Mirror (Box2D Integration)
==========================================================
Deterministic physics simulation that tracks ball movement
without needing to look at frames every cycle.

Architecture:
- Neural Net predicts initial state every 5 frames (80ms)
- Physics Mirror simulates at 120fps (8ms per step)
- Self-correction: Neural Net checks drift every 5 frames

Why it's smooth:
- Physics Mirror: 120fps (8ms)
- Neural Net: 12fps (80ms)
- 90% of time uses simulation, not vision
"""

import math
import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class PhysicsBall:
    """Ball state in physics simulation"""
    x: float
    y: float
    vx: float
    vy: float
    radius: float = 15.0
    mass: float = 1.0
    active: bool = True
    number: int = 0


@dataclass
class PhysicsConfig:
    """Physics simulation parameters"""
    friction: float = 0.998
    cushion_damping: float = 0.85
    min_speed: float = 0.1
    table_width: int = 256
    table_height: int = 128
    cushion_width: float = 8.0
    timestep: float = 1.0 / 120.0  # 120fps


class PhysicsMirror:
    """
    Deterministic physics simulation
    Runs at 120fps between Neural Net corrections
    """

    def __init__(self, config: PhysicsConfig = None):
        self.config = config or PhysicsConfig()
        self.balls: List[PhysicsBall] = []
        self.step_count = 0
        self.correction_count = 0

    def set_initial_state(self, ball_states: List[Dict]):
        """
        Set initial ball states from Neural Net prediction
        Called every 5 frames (80ms)
        """
        self.balls = []
        for state in ball_states:
            ball = PhysicsBall(
                x=state['x'],
                y=state['y'],
                vx=state['vx'],
                vy=state['vy'],
                number=state.get('number', 0),
                active=state.get('active', True)
            )
            self.balls.append(ball)

    def step(self):
        """Run one physics step (8ms at 120fps)"""
        for ball in self.balls:
            if not ball.active:
                continue

            # Update position
            ball.x += ball.vx * self.config.timestep * 60
            ball.y += ball.vy * self.config.timestep * 60

            # Apply friction
            ball.vx *= self.config.friction
            ball.vy *= self.config.friction

            # Stop if too slow
            speed = math.sqrt(ball.vx ** 2 + ball.vy ** 2)
            if speed < self.config.min_speed:
                ball.vx = 0
                ball.vy = 0

            # Check cushion collision
            self._check_cushion(ball)

        # Check ball-ball collisions
        for i in range(len(self.balls)):
            for j in range(i + 1, len(self.balls)):
                if self.balls[i].active and self.balls[j].active:
                    self._resolve_collision(self.balls[i], self.balls[j])

        self.step_count += 1

    def _check_cushion(self, ball: PhysicsBall):
        """Handle cushion bounce"""
        cw = self.config.cushion_width
        damping = self.config.cushion_damping

        if ball.x - ball.radius < cw:
            ball.x = cw + ball.radius
            ball.vx = abs(ball.vx) * damping
        elif ball.x + ball.radius > self.config.table_width - cw:
            ball.x = self.config.table_width - cw - ball.radius
            ball.vx = -abs(ball.vx) * damping

        if ball.y - ball.radius < cw:
            ball.y = cw + ball.radius
            ball.vy = abs(ball.vy) * damping
        elif ball.y + ball.radius > self.config.table_height - cw:
            ball.y = self.config.table_height - cw - ball.radius
            ball.vy = -abs(ball.vy) * damping

    def _resolve_collision(self, b1: PhysicsBall, b2: PhysicsBall):
        """Elastic collision between two balls"""
        dx = b2.x - b1.x
        dy = b2.y - b1.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist == 0 or dist >= (b1.radius + b2.radius):
            return

        nx = dx / dist
        ny = dy / dist

        dvx = b1.vx - b2.vx
        dvy = b1.vy - b2.vy
        dvn = dvx * nx + dvy * ny

        if dvn < 0:
            return

        b1.vx -= dvn * nx * 0.98
        b1.vy -= dvn * ny * 0.98
        b2.vx += dvn * nx * 0.98
        b2.vy += dvn * ny * 0.98

        overlap = (b1.radius + b2.radius - dist) / 2
        b1.x -= overlap * nx
        b1.y -= overlap * ny
        b2.x += overlap * nx
        b2.y += overlap * ny

    def get_states(self) -> List[Dict]:
        """Get current ball states"""
        return [
            {
                'number': ball.number,
                'x': ball.x,
                'y': ball.y,
                'vx': ball.vx,
                'vy': ball.vy,
                'active': ball.active
            }
            for ball in self.balls
        ]

    def correct_from_neural(self, neural_states: List[Dict], threshold=5.0):
        """
        Self-correction: Compare with Neural Net prediction
        Adjust if drift exceeds threshold
        """
        self.correction_count += 1

        for i, (sim_ball, neural_state) in enumerate(
            zip(self.balls, neural_states)
        ):
            if not sim_ball.active:
                continue

            dx = neural_state['x'] - sim_ball.x
            dy = neural_state['y'] - sim_ball.y
            drift = math.sqrt(dx * dx + dy * dy)

            if drift > threshold:
                correction_weight = 0.3
                sim_ball.x = sim_ball.x * (1 - correction_weight) + neural_state['x'] * correction_weight
                sim_ball.y = sim_ball.y * (1 - correction_weight) + neural_state['y'] * correction_weight

                dvx = neural_state['vx'] - sim_ball.vx
                dvy = neural_state['vy'] - sim_ball.vy
                v_drift = math.sqrt(dvx * dvx + dvy * dvy)

                if v_drift > 0.5:
                    sim_ball.vx = sim_ball.vx * 0.7 + neural_state['vx'] * 0.3
                    sim_ball.vy = sim_ball.vy * 0.7 + neural_state['vy'] * 0.3

    def is_stopped(self) -> bool:
        """Check if all balls have stopped"""
        for ball in self.balls:
            if ball.active and (abs(ball.vx) > 0.01 or abs(ball.vy) > 0.01):
                return False
        return True

    def get_stats(self) -> Dict:
        """Get simulation statistics"""
        return {
            'step_count': self.step_count,
            'correction_count': self.correction_count,
            'active_balls': sum(1 for b in self.balls if b.active),
            'total_balls': len(self.balls)
        }


class PhysicsMirrorManager:
    """
    Manages the interaction between Neural Net and Physics Mirror
    - Neural Net runs every 5 frames (80ms)
    - Physics Mirror runs every frame (8ms at 120fps)
    """

    def __init__(self):
        self.physics = PhysicsMirror()
        self.frame_count = 0
        self.neural_interval = 5

    def update(self, neural_states: List[Dict] = None):
        """
        Update physics simulation
        If neural_states provided, apply correction
        """
        self.frame_count += 1

        # Run physics step
        self.physics.step()

        # Apply neural correction if provided
        if neural_states:
            self.physics.correct_from_neural(neural_states)