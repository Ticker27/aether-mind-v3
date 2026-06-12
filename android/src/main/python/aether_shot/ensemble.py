"""
AETHER SHOT — Layer 2: Polymorphic Predictor Ensemble
=====================================================
Multiple prediction strategies that vote for the best shot.
แต่ละรอบ ตำแหน่ง prediction เปลี่ยน (Polymorphic)

Strategies:
1. Physics Deterministic — ใช้ Physics Mirror คำนวณ trajectory จริง
2. Heuristic Rules — กฎจากผู้เล่นจริง
3. Tiny ML — ถ้ามี trained model (optional)
"""

import sys
import math
import random
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from aether_shot.physics_mirror import mirror


class HeuristicPredictor:
    """
    Strategy 2: Heuristic Rules
    ใช้ความรู้จากผู้เล่นบิลเลียดจริง
    """
    
    @staticmethod
    def predict(cue_pos, ball_positions):
        """ทำนาย shot จากกฏ heuristics"""
        targets = [b for b in ball_positions if b[3]]
        
        if not targets:
            return None
        
        # Find easiest shot
        best = None
        best_score = -float('inf')
        
        for target in targets:
            tid, tx, ty = target[0], target[1], target[2]
            
            # Distance from cue to target
            dist = math.sqrt((tx - cue_pos[0])**2 + (ty - cue_pos[1])**2)
            
            # Each pocket
            for pid, (px, py) in enumerate(mirror.POCKETS):
                # Distance from target to pocket
                pocket_dist = math.sqrt((px - tx)**2 + (py - ty)**2)
                
                # Easy shot = short distance + target near pocket
                score = 100 - pocket_dist / 20 - dist / 30
                
                # Bonus for near-center pocket
                if pid in [1, 4]:
                    score += 10
                
                if score > best_score:
                    best_score = score
                    
                    # Calculate angle
                    dx = px - tx
                    dy = py - ty
                    pocket_angle = math.degrees(math.atan2(dy, dx))
                    
                    cdx = tx - cue_pos[0]
                    cdy = ty - cue_pos[1]
                    shot_angle = math.degrees(math.atan2(cdy, cdx))
                    
                    # Recommend power based on distance
                    power = min(8.0, max(2.0, dist / 50))
                    
                    best = {
                        'target_ball': tid,
                        'target_pocket': pid,
                        'angle': shot_angle,
                        'power': power,
                        'score': best_score
                    }
        
        return best


class TinyMLPredictor:
    """
    Strategy 3: Tiny ML (ถ้ามี trained model)
    ปัจจุบันใช้ fallback เป็น heuristic จนกว่าจะมี model
    """
    
    def __init__(self):
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """พยายามโหลด model ถ้ามี"""
        try:
            model_path = Path(__file__).parent / 'models' / 'qshot_model.pkl'
            if model_path.exists():
                from joblib import load
                self.model = load(str(model_path))
        except Exception:
            self.model = None
    
    def predict(self, cue_pos, ball_positions):
        """ใช้ ML predict หรือ fallback"""
        if self.model:
            try:
                features = self._extract_features(cue_pos, ball_positions)
                pred = self.model.predict([features])[0]
                return {
                    'target_ball': int(pred[0]),
                    'target_pocket': int(pred[1]),
                    'angle': float(pred[2]),
                    'power': float(pred[3]),
                    'score': 50.0
                }
            except Exception:
                pass
        
        # Fallback
        return None
    
    def _extract_features(self, cue_pos, ball_positions):
        feats = [cue_pos[0], cue_pos[1]]
        for b in ball_positions[:15]:
            feats.extend([b[1], b[2]])
        while len(feats) < 32:
            feats.append(0.0)
        return feats


class PolymorphicEnsemble:
    """
    Polymorphic ensemble predictor.
    ใช้ 3 strategies พร้อมกัน → เลือกคำตอบที่ดีที่สุด
    """
    
    def __init__(self):
        self.strategies = {
            'physics': self._predict_physics,
            'heuristic': self._predict_heuristic,
            'ml': self._predict_ml
        }
        
        # Randomize strategy order each session (Polymorphic)
        self.strategy_order = list(self.strategies.keys())
        random.shuffle(self.strategy_order)
        
        self.heuristic = HeuristicPredictor()
        self.ml = TinyMLPredictor()
        
        # Strategy weights (can adapt over time)
        self.weights = {
            'physics': 0.5,
            'heuristic': 0.3,
            'ml': 0.2
        }
    
    def predict(self, cue_pos, ball_positions):
        """
        Predict best shot using ensemble voting
        
        Returns:
            dict with predictions from all strategies + voted result
        """
        results = {}
        scores = []
        
        # Shuffle order each call (Polymorphic)
        order = list(self.strategy_order)
        random.shuffle(order)
        
        for name in order:
            try:
                result = self.strategies[name](cue_pos, ball_positions)
                if result:
                    weight = self.weights.get(name, 0.33)
                    result['strategy'] = name
                    result['weight'] = weight
                    results[name] = result
                    scores.append((result['score'] * weight, result))
            except Exception:
                continue
        
        # Vote: pick highest weighted score
        if scores:
            best = max(scores, key=lambda x: x[0])
            voted = best[1].copy()
            voted['ensemble_votes'] = len(scores)
            voted['strategies_used'] = list(results.keys())
            voted['consensus'] = len(scores) / len(self.strategies)
        else:
            voted = None
        
        return {
            'voted': voted,
            'all_results': results
        }
    
    def _predict_physics(self, cue_pos, ball_positions):
        """Strategy 1: Physics deterministic"""
        # Simplify — find best via physics mirror
        result = mirror.find_best_shot(cue_pos, ball_positions)
        return result
    
    def _predict_heuristic(self, cue_pos, ball_positions):
        """Strategy 2: Heuristic rules"""
        return self.heuristic.predict(cue_pos, ball_positions)
    
    def _predict_ml(self, cue_pos, ball_positions):
        """Strategy 3: ML (ถ้ามี)"""
        return self.ml.predict(cue_pos, ball_positions)
    
    def update_weights(self, strategy_name, success):
        """ปรับน้ำหนักตามผลลัพธ์ (Adaptive)"""
        if success:
            self.weights[strategy_name] = min(1.0, self.weights[strategy_name] + 0.05)
        else:
            self.weights[strategy_name] = max(0.1, self.weights[strategy_name] - 0.02)


ensemble = PolymorphicEnsemble()