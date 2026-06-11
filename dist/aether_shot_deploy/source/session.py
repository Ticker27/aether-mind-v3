"""
AETHER SHOT — Layer 3: Ephemeral Session State
==============================================
Session state ที่อยู่ใน RAM เท่านั้น
ไม่มีไฟล์เขียนลง disk (Zero Disk Footprint)
เมื่อปิด session → state หายทั้งหมด (Zero Trace)
"""

import time
import uuid
import numpy as np


class EphemeralSession:
    """
    Session state ใน RAM ล้วน
    
    - ถูกสร้างเมื่อเริ่ม prediction
    - ถูกทำลายเมื่อ session จบ
    - ไม่มี trace บน disk
    """
    
    def __init__(self):
        self.session_id = str(uuid.uuid4())[:8]
        self.created_at = time.time()
        self.last_active = self.created_at
        
        # All state in RAM
        self._shots = []
        self._frames = []
        self._predictions = []
        self._player_patterns = {}
        
        self._active = True
    
    def record_shot(self, cue_pos, target_pos, prediction, result):
        """บันทึก shot ที่ทำไป"""
        if not self._active:
            return
        
        self._shots.append({
            'time': time.time() - self.created_at,
            'cue': cue_pos,
            'target': target_pos,
            'prediction': prediction,
            'result': result
        })
        self.last_active = time.time()
    
    def record_frame(self, frame_data):
        """บันทึก frame (optional — เก็บใน RAM เท่านั้น)"""
        if not self._active:
            return
        if len(self._frames) < 100:  # limit RAM usage
            self._frames.append(frame_data)
    
    def get_stats(self):
        """ดึงสถิติ session"""
        if not self._shots:
            return {'shots': 0, 'accuracy': 0}
        
        total = len(self._shots)
        success = sum(1 for s in self._shots if s.get('result', {}).get('success'))
        
        return {
            'session_id': self.session_id,
            'duration': time.time() - self.created_at,
            'shots': total,
            'successful_shots': success,
            'accuracy': success / total if total > 0 else 0,
            'ram_frames': len(self._frames)
        }
    
    def destroy(self):
        """ทำลาย session — ล้าง RAM"""
        self._shots.clear()
        self._frames.clear()
        self._predictions.clear()
        self._player_patterns.clear()
        self._active = False


class SessionManager:
    """
    Manage multiple ephemeral sessions
    """
    
    def __init__(self):
        self._sessions = {}
        self._max_sessions = 10
    
    def create_session(self):
        """สร้าง session ใหม่"""
        session = EphemeralSession()
        self._sessions[session.session_id] = session
        return session
    
    def get_session(self, session_id):
        """ดึง session ตาม ID"""
        return self._sessions.get(session_id)
    
    def destroy_session(self, session_id):
        """ทำลาย session"""
        if session_id in self._sessions:
            self._sessions[session_id].destroy()
            del self._sessions[session_id]
    
    def destroy_all(self):
        """ทำลายทุก session — Zero Trace"""
        for sid, session in self._sessions.items():
            session.destroy()
        self._sessions.clear()
    
    def cleanup_old(self, max_age_seconds=3600):
        """ลบ session ที่เก่า"""
        now = time.time()
        to_delete = [
            sid for sid, s in self._sessions.items()
            if now - s.last_active > max_age_seconds
        ]
        for sid in to_delete:
            self.destroy_session(sid)


session_manager = SessionManager()
