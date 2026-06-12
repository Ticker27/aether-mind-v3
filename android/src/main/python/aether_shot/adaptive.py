"""
AETHER SHOT — Layer 4: Adaptive Learning
========================================
เรียนรู้พฤติกรรมผู้เล่นระหว่าง session แบบ real-time
ไม่มี data หลุดออกนอก RAM session

แนวคิด: "AI ที่ปรับตัวตามผู้เล่น ไม่ใช่ให้ผู้เล่นปรับตัวเข้า AI"
"""

import math
from collections import defaultdict




class PlayerProfile:
    """
    ข้อมูลผู้เล่นที่เก็บใน RAM session เท่านั้น
    เรียนรู้ pattern การเล่นแบบ real-time
    """
    
    def __init__(self):
        # Shot patterns
        self._angle_history = []
        self._power_history = []
        self._spin_history = []
        self._success_history = []
        
        # Statistics
        self.stats = {
            'total_shots': 0,
            'successful_shots': 0,
            'preferred_angle_range': (0, 0),
            'preferred_power_range': (0, 0),
            'common_mistakes': defaultdict(int),
            'favorite_pockets': defaultdict(int)
        }
    
    def record_shot_result(self, angle, power, spin, success, pocket_id=None, mistake=None):
        """บันทึกผลการยิง"""
        self._angle_history.append(angle)
        self._power_history.append(power)
        self._spin_history.append(spin)
        self._success_history.append(success)
        
        self.stats['total_shots'] += 1
        if success:
            self.stats['successful_shots'] += 1
        if pocket_id is not None:
            self.stats['favorite_pockets'][pocket_id] += 1
        if mistake:
            self.stats['common_mistakes'][mistake] += 1
        
        # Update ranges (rolling window of last 20)
        recent = self._angle_history[-20:]
        if recent:
            self.stats['preferred_angle_range'] = (min(recent), max(recent))
        recent_power = self._power_history[-20:]
        if recent_power:
            self.stats['preferred_power_range'] = (min(recent_power), max(recent_power))
    
    def get_advice(self):
        """ให้คำแนะนำตาม pattern ผู้เล่น"""
        if self.stats['total_shots'] < 3:
            return None
        
        accuracy = self.stats['successful_shots'] / max(self.stats['total_shots'], 1)
        
        advice = {
            'accuracy': accuracy,
            'preferred_angle': sum(self._angle_history[-10:]) / max(len(self._angle_history[-10:]), 1),
            'preferred_power': sum(self._power_history[-10:]) / max(len(self._power_history[-10:]), 1),
            'common_mistakes': dict(self.stats['common_mistakes']),
            'favorite_pocket': max(self.stats['favorite_pockets'], key=self.stats['favorite_pockets'].get) if self.stats['favorite_pockets'] else None
        }
        
        # Warning if power too high
        avg_power = sum(self._power_history[-5:]) / max(len(self._power_history[-5:]), 1)
        if avg_power > 7.0:
            advice['warning'] = '⚠️ พลังสูงเกินไป → เสี่ยงตกหลุม'
        elif avg_power < 3.0:
            advice['warning'] = '💡 พลังน้อยไป → ลูกไม่ถึง'
        else:
            advice['warning'] = None
        
        return advice


class AdaptiveEngine:
    """
    Adaptive engine ที่ปรับ prediction ตามผู้เล่น
    """
    
    def __init__(self):
        self.profiles = {}  # player_id → PlayerProfile
    
    def get_profile(self, player_id='default'):
        """ดึง profile ผู้เล่น (สร้างถ้ายังไม่มี)"""
        if player_id not in self.profiles:
            self.profiles[player_id] = PlayerProfile()
        return self.profiles[player_id]
    
    def learn_from_shot(self, player_id, angle, power, spin, success, pocket_id=None, mistake=None):
        """เรียนรู้จากการยิงครั้งล่าสุด"""
        profile = self.get_profile(player_id)
        profile.record_shot_result(angle, power, spin, success, pocket_id, mistake)
    
    def adjust_prediction(self, player_id, base_prediction):
        """
        ปรับ prediction ตามประวัติผู้เล่น
        
        ถ้าผู้เล่นชอบยิงมุมซ้าย → ให้ความสำคัญกับมุมซ้ายมากขึ้น
        ถ้าผู้เล่นมักพลาดตอน power สูง → แนะนำ power ต่ำลง
        """
        profile = self.get_profile(player_id)
        advice = profile.get_advice()
        
        if not advice or not base_prediction:
            return base_prediction
        
        adjusted = base_prediction.copy() if base_prediction else {}
        
        # Adjust power based on player history
        if advice['preferred_power']:
            # Blend: 70% base prediction, 30% player preference
            current_power = adjusted.get('power', 5.0)
            adjusted['power'] = current_power * 0.7 + advice['preferred_power'] * 0.3
        
        # Add player-specific warnings
        if advice['warning']:
            adjusted['warning'] = advice['warning']
        
        adjusted['player_accuracy'] = advice['accuracy']
        adjusted['adapted'] = True
        
        return adjusted
    
    def clear_all(self):
        """ลบทุก profile (Privacy by Design)"""
        self.profiles.clear()


adaptive = AdaptiveEngine()
