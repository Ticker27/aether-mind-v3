"""
NEXUS ULTRA — Human Touch Layer
=================================
Integrates human-like behavior into Neural Core
Combines: Accuracy of AI + Natural feel of human

Key Philosophy:
  "อย่าทำให้ AI เล่นเก่งที่สุด — ทำให้ AI เล่นเหมือนมนุษย์เก่ง"
  
Architecture:
  Neural Core (predicts trajectory) 
    → Decision Engine (chooses best HUMAN shot)
    → Timing Engine (adds human delay)
    → Movement Simulator (natural cue motion)
    → Error Injection (human mistakes)
"""

import random
import math
import time
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field


# ============================================================================
# 1. TIMING ENGINE (จังหวะเหมือนมนุษย์)
# ============================================================================

@dataclass
class ShotTiming:
    """Timing parameters for a single shot"""
    difficulty: str           # easy, medium, hard, impossible
    aim_delay: float         # หน่วงเวลา "คิด" (วินาที)
    cue_wiggle: int          # จำนวนครั้งที่ขยับไม้
    wiggle_duration: float   # เวลาขยับไม้ทั้งหมด
    pause_before: float      # หยุดค้างก่อนยิง (วินาที)
    pull_back: float         # เวลาดึงไม้ถอยหลัง (วินาที)
    total_time: float        # เวลารวมทั้งหมด
    confidence: float        # ความมั่นใจ 0.0-1.0


class HumanTimingEngine:
    """
    จำลองจังหวะการยิงของมนุษย์
    - ช็อตรง่าย: คิดเร็ว, ขยับน้อย, ยิงเร็ว
    - ช็อตยาก: คิดนาน, ขยับมาก, ยิงช้า
    """
    
    # Timing pool based on shot difficulty (from real player analysis)
    TIMING_POOL = {
        'easy': {
            'aim_delay': (0.5, 1.2),
            'cue_wiggle': (1, 3),
            'wiggle_gap': (0.15, 0.3),
            'pause_before': (0.1, 0.2),
            'pull_back': (0.3, 0.6),
            'confidence': (0.85, 0.99)
        },
        'medium': {
            'aim_delay': (1.0, 2.5),
            'cue_wiggle': (2, 4),
            'wiggle_gap': (0.2, 0.4),
            'pause_before': (0.15, 0.3),
            'pull_back': (0.5, 1.0),
            'confidence': (0.6, 0.85)
        },
        'hard': {
            'aim_delay': (2.0, 4.0),
            'cue_wiggle': (3, 6),
            'wiggle_gap': (0.25, 0.5),
            'pause_before': (0.2, 0.4),
            'pull_back': (0.8, 1.5),
            'confidence': (0.3, 0.6)
        },
        'impossible': {
            'aim_delay': (3.0, 6.0),
            'cue_wiggle': (4, 8),
            'wiggle_gap': (0.3, 0.6),
            'pause_before': (0.25, 0.5),
            'pull_back': (1.0, 2.0),
            'confidence': (0.1, 0.3)
        }
    }
    
    def __init__(self, skill_level: float = 0.5):
        """
        skill_level: 0.0 = มือใหม่, 1.0 = มือโปร
        """
        self.skill_level = max(0.0, min(1.0, skill_level))
        # skill factor: มือใหม่ช้ากว่า 20%, มือโปรเร็วกว่า 20%
        self.skill_factor = 0.8 + (self.skill_level * 0.4)
    
    def classify_difficulty(self, angle: float, distance: float, 
                           ball_count: int) -> str:
        """
         classify ความยากของช็อต
        """
        # มุมยิ่งแคบ = ยิ่งยาก
        angle_diff = abs(angle - 90)  # 0 = ตรง, 90 = ฉาก
        angle_score = angle_diff / 90  # 0.0 = ตรง, 1.0 = ฉาก
        
        # ระยะยิ่งไกล = ยิ่งยาก
        dist_score = min(1.0, distance / 200)
        
        # ลูกกีดขวางยิ่งเยอะ = ยิ่งยาก
        ball_score = min(1.0, ball_count / 5)
        
        # Composite difficulty score
        difficulty = (angle_score * 0.4) + (dist_score * 0.3) + (ball_score * 0.3)
        
        if difficulty < 0.25:
            return 'easy'
        elif difficulty < 0.5:
            return 'medium'
        elif difficulty < 0.75:
            return 'hard'
        else:
            return 'impossible'
    
    def get_timing(self, difficulty: str) -> ShotTiming:
        """Generate timing parameters for a shot"""
        base = self.TIMING_POOL[difficulty]
        
        aim = random.uniform(*base['aim_delay']) * self.skill_factor
        wiggles = random.randint(*base['cue_wiggle'])
        wiggle_time = wiggles * random.uniform(*base['wiggle_gap'])
        pause = random.uniform(*base['pause_before'])
        pull = random.uniform(*base['pull_back']) * (1.0 / self.skill_factor)
        confidence = random.uniform(*base['confidence'])
        
        total = aim + wiggle_time + pause + pull
        
        return ShotTiming(
            difficulty=difficulty,
            aim_delay=aim,
            cue_wiggle=wiggles,
            wiggle_duration=wiggle_time,
            pause_before=pause,
            pull_back=pull,
            total_time=total,
            confidence=confidence
        )


# ============================================================================
# 2. CUE MOVEMENT SIMULATOR (การขยับไม้เหมือนคน)
# ============================================================================

@dataclass
class CuePosition:
    x: float
    y: float
    time_gap: float
    speed: float
    is_pull_back: bool = False


class CueMovementSimulator:
    """
    จำลองการขยับไม้คิวแบบมนุษย์
    - มี jitter (สั่น) เล็กน้อย
    - convergence เข้าใกล้เป้าหมาย
    - speed curve: ช้า→เร็ว→ช้า
    """
    
    @staticmethod
    def simulate_wiggle(start_x: float, start_y: float,
                       target_x: float, target_y: float,
                       wiggle_count: int) -> List[CuePosition]:
        """จำลองการขยับไม้ขึ้น-ลงก่อนยิง"""
        positions = []
        
        for i in range(wiggle_count):
            progress = i / max(1, wiggle_count - 1)
            
            # Jitter ลดลงเมื่อเข้าใกล้ (มนุษย์เริ่มนิ่ง)
            jitter_x = random.gauss(0, 5 * (1 - progress))
            jitter_y = random.gauss(0, 5 * (1 - progress))
            
            # Interpolate + jitter
            x = (1 - progress) * start_x + progress * target_x + jitter_x
            y = (1 - progress) * start_y + progress * target_y + jitter_y
            
            # เวลาไม่สม่ำเสมอ (มนุษย์ไม่ steady)
            time_gap = random.uniform(0.15, 0.4)
            speed = random.uniform(0.8, 1.2)
            
            positions.append(CuePosition(x, y, time_gap, speed))
        
        return positions
    
    @staticmethod
    def simulate_pull_back(angle: float, max_distance: float) -> Dict:
        """จำลองการดีงไม้ถอยหลัง"""
        pull_dist = max_distance * random.uniform(0.7, 0.8)
        
        # Speed curve: ease in-out
        curve = [
            (0.0, 0.3),   # 0-30%: ช้า (เริ่มดึง)
            (0.3, 0.7),   # 30-70%: เร็ว (มั่นใจ)
            (0.7, 1.0),   # 70-100%: ช้าลง (ตั้งใจ)
        ]
        
        return {
            'pull_distance': pull_dist,
            'pull_duration': random.uniform(0.3, 0.8),
            'speed_curve': curve,
            'angle_jitter': random.uniform(-0.5, 0.5)
        }


# ============================================================================
# 3. DECISION ENGINE (เลือกช็อตแบบมนุษย์)
# ============================================================================

@dataclass
class ShotOption:
    pocket: Tuple[float, float]
    target_ball: int
    cue_ball: Tuple[float, float]
    difficulty: float
    reward: float
    risk: float
    score: float = 0.0


class DecisionEngine:
    """
    ระบบตัดสินใจเลือกช็อตที่ "มนุษย์น่าจะเลือก"
    ไม่ใช่ช็อตที่ดีที่สุดทางคณิตศาสตร์
    
    Factors:
    - ความยาก (คนชอบช็อตง่าย)
    - ความคุ้มค่า (ได้อะไรต่อ)
    - ความเสี่ยง (scratch risk)
    - Human Factor (visual simplicity)
    - Play Style (aggressive vs conservative)
    """
    
    def __init__(self, aggressiveness: float = 0.5):
        self.aggressiveness = max(0.0, min(1.0, aggressiveness))
    
    def calculate_difficulty(self, pocket: Tuple, ball: Tuple, 
                            cue: Tuple) -> float:
        """คำนวณความยากของช็อต"""
        dx_target = pocket[0] - ball[0]
        dy_target = pocket[1] - ball[1]
        dx_cue = ball[0] - cue[0]
        dy_cue = ball[1] - cue[1]
        
        angle = abs(math.degrees(math.atan2(dy_target, dx_target) - 
                                 math.atan2(dy_cue, dx_cue)))
        distance = math.sqrt(dx_cue**2 + dy_cue**2)
        
        # Normalize
        angle_score = min(1.0, angle / 45)
        dist_score = min(1.0, distance / 300)
        
        return (angle_score * 0.5) + (dist_score * 0.5)
    
    def calculate_risk(self, cue: Tuple, target: Tuple, 
                      pocket: Tuple) -> float:
        """ประเมินความเสี่ยง (ลูกขาวตกหลุม)"""
        # Simplified: risk based on cue ball path
        dx = pocket[0] - cue[0]
        dy = pocket[1] - cue[1]
        dist = math.sqrt(dx**2 + dy**2)
        
        # ยิ่งลูกขาวอยู่ใกล้หลุม = ยิ่งเสี่ยง
        return max(0.0, 1.0 - (dist / 200))
    
    def evaluate_shot(self, shot: ShotOption) -> float:
        """ให้คะแนนแต่ละช็อตด้วยมุมมองมนุษย์"""
        score = 0.0
        
        # 1. ความยาก (มนุษย์ชอบง่าย)
        score -= shot.difficulty * 0.3
        
        # 2. ความคุ้มค่า (ได้อะไรต่อ)
        score += shot.reward * 0.4
        
        # 3. ความเสี่ยง (กลัวเสีย)
        score -= shot.risk * 0.5
        
        # 4. Aggressive bonus
        score += self.aggressiveness * 0.1 * shot.reward
        
        return score
    
    def select_shot(self, shots: List[ShotOption]) -> ShotOption:
        """
        เลือกช็อตแบบมนุษย์: ไม่ได้เลือกอันดับ 1 ทุกครั้ง!
        Humans pick from top-3 based on 'feeling'
        """
        for shot in shots:
            shot.score = self.evaluate_shot(shot)
        
        # Rank
        ranked = sorted(shots, key=lambda x: x.score, reverse=True)
        
        # Select from top-3 with weighted probability
        top_3 = ranked[:min(3, len(ranked))]
        weights = [max(0.3, s.score - ranked[2].score + 0.1) for s in top_3]
        
        chosen = random.choices(top_3, weights=weights, k=1)[0]
        return chosen


# ============================================================================
# 4. NEXUS HUMAN TOUCH — Integrated Layer
# ============================================================================

class NexusHumanTouch:
    """
    รวมทุกอย่างเข้าด้วยกัน:
    Neural Core (accuracy) + Human Touch (natural)
    """
    
    def __init__(self, skill_level: float = 0.5, 
                 aggressiveness: float = 0.5):
        self.timing = HumanTimingEngine(skill_level)
        self.movement = CueMovementSimulator()
        self.decision = DecisionEngine(aggressiveness)
        
        # Self-learning: ปรับ skill ตามผลการเล่น
        self.shot_history: List[Dict] = []
    
    def execute_shot_sequence(self, shots: List[ShotOption],
                             cue_pos: Tuple[float, float]) -> Dict:
        """
        Full shot execution pipeline
        """
        # 1. NEURAL CORE (ในที่นี้ใช้ Decision Engine)
        chosen = self.decision.select_shot(shots)
        
        # 2. Classify difficulty
        difficulty = self.timing.classify_difficulty(
            angle=random.uniform(0, 90),  # Simplified
            distance=random.uniform(10, 200),
            ball_count=random.randint(0, 5)
        )
        
        # 3. Generate timing
        timing = self.timing.get_timing(difficulty)
        
        # 4. Simulate cue movement
        target_x = chosen.pocket[0] + random.gauss(0, 2)
        target_y = chosen.pocket[1] + random.gauss(0, 2)
        
        wiggle_positions = self.movement.simulate_wiggle(
            cue_pos[0], cue_pos[1],
            target_x, target_y,
            timing.cue_wiggle
        )
        
        pull_back = self.movement.simulate_pull_back(
            angle=random.uniform(0, 360),
            max_distance=random.uniform(50, 100)
        )
        
        # 5. Add human errors
        power_error = random.gauss(0, 0.02)  # ±2%
        angle_error = random.gauss(0, 0.3)   # ±0.3°
        
        sequence = {
            'chosen_shot': {
                'pocket': chosen.pocket,
                'target_ball': chosen.target_ball,
                'score': chosen.score,
                'confidence': timing.confidence
            },
            'timing': {
                'difficulty': difficulty,
                'aim_delay': timing.aim_delay,
                'wiggle': timing.cue_wiggle,
                'pause': timing.pause_before,
                'pull_back': timing.pull_back,
                'total': timing.total_time
            },
            'movement': {
                'wiggle_positions': wiggle_positions,
                'pull_back': pull_back
            },
            'errors': {
                'power': power_error,
                'angle': angle_error
            }
        }
        
        # Record for self-learning
        self.shot_history.append(sequence)
        
        return sequence
    
    def get_stats(self) -> Dict:
        """Get shot statistics"""
        if not self.shot_history:
            return {'total_shots': 0}
        
        confidences = [s['chosen_shot']['confidence'] for s in self.shot_history]
        avg_time = sum(s['timing']['total'] for s in self.shot_history) / len(self.shot_history)
        
        return {
            'total_shots': len(self.shot_history),
            'avg_confidence': sum(confidences) / len(confidences),
            'avg_response_time': avg_time,
            'difficulty_distribution': {
                'easy': sum(1 for s in self.shot_history if s['timing']['difficulty'] == 'easy'),
                'medium': sum(1 for s in self.shot_history if s['timing']['difficulty'] == 'medium'),
                'hard': sum(1 for s in self.shot_history if s['timing']['difficulty'] == 'hard'),
                'impossible': sum(1 for s in self.shot_history if s['timing']['difficulty'] == 'impossible')
            }
        }


if __name__ == "__main__":
    print("🧬 NEXUS HUMAN TOUCH — Test")
    print("=" * 50)
    
    # Test with different skill levels
    for skill in [0.0, 0.5, 1.0]:
        print(f"\n🎯 Skill Level: {skill}")
        nexus = NexusHumanTouch(skill_level=skill, aggressiveness=0.5)
        
        # Create test shots
        shots = [
            ShotOption((250, 100), 1, (50, 64), 0.2, 0.8, 0.1, 0.0),
            ShotOption((50, 200), 3, (50, 64), 0.5, 0.6, 0.3, 0.0),
            ShotOption((150, 50), 5, (50, 64), 0.8, 0.9, 0.6, 0.0),
        ]
        
        # Execute 5 shots
        for i in range(5):
            result = nexus.execute_shot_sequence(shots, (50, 64))
            print(f"   Shot {i+1}: {result['timing']['difficulty']:10s} | "
                  f"delay={result['timing']['aim_delay']:.2f}s | "
                  f"wiggle={result['timing']['wiggle']} | "
                  f"conf={result['chosen_shot']['confidence']:.2f}")
        
        stats = nexus.get_stats()
        print(f"   📊 avg_time={stats['avg_response_time']:.2f}s | "
              f"conf={stats['avg_confidence']:.2f}")
    
    print("\n✅ HUMAN TOUCH integrated with NEXUS ULTRA!")
