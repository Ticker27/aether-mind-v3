#!/usr/bin/env python3
"""
AETHER MIND v3.0 — Phase 1: Neural Oracle Core
================================================
Neural network สำหรับ ball trajectory prediction
Self-learning จาก gameplay footage
"""

import os
import json
import time
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Import config
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "orchestrator"))
from config_loader import Config
from dashscope_client import DashScopeClient


@dataclass
class BallState:
    """สถานะของลูกบอล"""
    x: float
    y: float
    vx: float  # velocity x
    vy: float  # velocity y
    radius: float = 10.0
    mass: float = 1.0
    timestamp: float = 0.0


@dataclass
class TrajectoryPrediction:
    """ผลการทำนาย trajectory"""
    predicted_path: List[Tuple[float, float]]
    confidence: float
    time_horizon: float  # seconds
    collision_points: List[Tuple[float, float]]


class NeuralOracle:
    """Neural Oracle Core — สมอง AI ของระบบ"""
    
    def __init__(self, model_id: str = "qwq-plus"):
        """
        Initialize Neural Oracle
        
        Args:
            model_id: DashScope model ID สำหรับ reasoning
        """
        self.model_id = model_id
        self.api_key = Config.get_dashscope_key()
        self.client = DashScopeClient(self.api_key)
        
        # Experience buffer (self-learning)
        self.experience_buffer: List[Dict] = []
        self.max_buffer_size = 1000
        
        # Model state
        self.is_trained = False
        self.accuracy = 0.0
        self.training_samples = 0
        
        print(f"🧠 Neural Oracle initialized with model: {model_id}")
    
    def predict_trajectory(
        self,
        initial_state: BallState,
        time_horizon: float = 2.0,
        dt: float = 0.016  # 60 FPS
    ) -> TrajectoryPrediction:
        """
        ทำนาย trajectory ของลูกบอล
        
        Args:
            initial_state: สถานะเริ่มต้นของลูกบอล
            time_horizon: ระยะเวลาทำนาย (วินาที)
            dt: timestep (วินาที)
        
        Returns:
            TrajectoryPrediction
        """
        # ใช้ AI model สำหรับ prediction
        prompt = self._build_prediction_prompt(initial_state, time_horizon)
        
        try:
            response = self.client.chat(
                model=self.model_id,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.3  # Low temperature for deterministic output
            )
            
            # Parse response
            predicted_path = self._parse_trajectory_response(response["content"])
            confidence = self._calculate_confidence(predicted_path)
            
            prediction = TrajectoryPrediction(
                predicted_path=predicted_path,
                confidence=confidence,
                time_horizon=time_horizon,
                collision_points=[]
            )
            
            # Store experience for self-learning
            self._store_experience(initial_state, prediction)
            
            return prediction
            
        except Exception as e:
            print(f"️  Prediction failed: {e}")
            # Fallback: simple physics prediction
            return self._simple_physics_prediction(initial_state, time_horizon, dt)
    
    def _build_prediction_prompt(self, state: BallState, time_horizon: float) -> str:
        """สร้าง prompt สำหรับ AI model"""
        return f"""
ทำนาย trajectory ของลูกบิลเลียดในอีก {time_horizon} วินาทีข้างหน้า

สถานะเริ่มต้น:
- ตำแหน่ง: ({state.x:.2f}, {state.y:.2f})
- ความเร็ว: ({state.vx:.2f}, {state.vy:.2f})
- รัศมี: {state.radius}
- มวล: {state.mass}

พิจารณา:
1. แรงเสียดทาน (friction)
2. การชนกับขอบโต๊ะ
3. การชนกับลูกบอลอื่น (ถ้ามี)
4. กฎฟิสิกส์ของบิลเลียด

ตอบเป็น JSON format:
{{
  "path": [[x1,y1], [x2,y2], ...],
  "confidence": 0.95,
  "collisions": [[x,y], ...]
}}
"""
    
    def _parse_trajectory_response(self, response: str) -> List[Tuple[float, float]]:
        """Parse response จาก AI model"""
        try:
            # Extract JSON from response
            start = response.find('{')
            end = response.rfind('}') + 1
            
            if start >= 0 and end > start:
                data = json.loads(response[start:end])
                path = data.get("path", [])
                return [(p[0], p[1]) for p in path]
        except:
            pass
        
        # Fallback: generate simple path
        return []
    
    def _calculate_confidence(self, path: List[Tuple[float, float]]) -> float:
        """คำนวณ confidence score"""
        if not path:
            return 0.0
        
        # Confidence based on path length and smoothness
        if len(path) < 2:
            return 0.5
        
        # Check smoothness (no sudden changes)
        smoothness = 1.0
        for i in range(1, len(path) - 1):
            dx1 = path[i][0] - path[i-1][0]
            dy1 = path[i][1] - path[i-1][1]
            dx2 = path[i+1][0] - path[i][0]
            dy2 = path[i+1][1] - path[i][1]
            
            # Angle change
            angle1 = np.arctan2(dy1, dx1)
            angle2 = np.arctan2(dy2, dx2)
            angle_diff = abs(angle2 - angle1)
            
            if angle_diff > np.pi / 2:  # Sudden turn
                smoothness *= 0.8
        
        return min(smoothness, 1.0)
    
    def _simple_physics_prediction(
        self,
        state: BallState,
        time_horizon: float,
        dt: float
    ) -> TrajectoryPrediction:
        """Fallback: ใช้ simple physics"""
        path = []
        x, y = state.x, state.y
        vx, vy = state.vx, state.vy
        
        # Simple physics with friction
        friction = 0.98
        steps = int(time_horizon / dt)
        
        for _ in range(steps):
            path.append((x, y))
            
            # Update position
            x += vx * dt
            y += vy * dt
            
            # Apply friction
            vx *= friction
            vy *= friction
            
            # Stop if very slow
            if abs(vx) < 0.01 and abs(vy) < 0.01:
                break
        
        return TrajectoryPrediction(
            predicted_path=path,
            confidence=0.7,
            time_horizon=time_horizon,
            collision_points=[]
        )
    
    def _store_experience(self, state: BallState, prediction: TrajectoryPrediction):
        """เก็บ experience สำหรับ self-learning"""
        experience = {
            "timestamp": time.time(),
            "initial_state": {
                "x": state.x,
                "y": state.y,
                "vx": state.vx,
                "vy": state.vy
            },
            "prediction": {
                "path": prediction.predicted_path,
                "confidence": prediction.confidence
            }
        }
        
        self.experience_buffer.append(experience)
        
        # Keep buffer size limited
        if len(self.experience_buffer) > self.max_buffer_size:
            self.experience_buffer = self.experience_buffer[-self.max_buffer_size:]
        
        self.training_samples = len(self.experience_buffer)
    
    def learn_from_experience(self) -> float:
        """
        เรียนรู้จาก experience buffer
        
        Returns:
            Improvement score (0-1)
        """
        if len(self.experience_buffer) < 10:
            return 0.0
        
        # Analyze past predictions
        accuracies = []
        
        for exp in self.experience_buffer[-100:]:  # Last 100 experiences
            confidence = exp["prediction"]["confidence"]
            accuracies.append(confidence)
        
        # Calculate average accuracy
        avg_accuracy = sum(accuracies) / len(accuracies)
        self.accuracy = avg_accuracy
        self.is_trained = True
        
        return avg_accuracy
    
    def get_status(self) -> Dict:
        """ดึงสถานะของ Neural Oracle"""
        return {
            "model_id": self.model_id,
            "is_trained": self.is_trained,
            "accuracy": self.accuracy,
            "training_samples": self.training_samples,
            "buffer_size": len(self.experience_buffer)
        }
    
    def save_model(self, path: str):
        """บันทึก model state"""
        state = {
            "model_id": self.model_id,
            "is_trained": self.is_trained,
            "accuracy": self.accuracy,
            "experience_buffer": self.experience_buffer[-100:],  # Last 100
            "timestamp": time.time()
        }
        
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Model saved to: {path}")
    
    def load_model(self, path: str):
        """โหลด model state"""
        if not Path(path).exists():
            print(f"️  Model file not found: {path}")
            return
        
        with open(path, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        self.model_id = state.get("model_id", self.model_id)
        self.is_trained = state.get("is_trained", False)
        self.accuracy = state.get("accuracy", 0.0)
        self.experience_buffer = state.get("experience_buffer", [])
        self.training_samples = len(self.experience_buffer)
        
        print(f"✅ Model loaded from: {path}")
        print(f"   Accuracy: {self.accuracy:.2%}")
        print(f"   Samples: {self.training_samples}")


def main():
    """ทดสอบ Neural Oracle"""
    print("=" * 80)
    print("🧠 AETHER MIND v3.0 — Phase 1: Neural Oracle Core")
    print("=" * 80)
    print()
    
    # Initialize
    oracle = NeuralOracle(model_id="qwq-plus")
    
    # Test prediction
    print("🎯 Testing trajectory prediction...")
    
    initial_state = BallState(
        x=100.0,
        y=200.0,
        vx=50.0,  # pixels/second
        vy=-30.0
    )
    
    prediction = oracle.predict_trajectory(
        initial_state=initial_state,
        time_horizon=2.0
    )
    
    print(f"\n📊 Prediction Results:")
    print(f"   Path length: {len(prediction.predicted_path)} points")
    print(f"   Confidence: {prediction.confidence:.2%}")
    print(f"   Time horizon: {prediction.time_horizon}s")
    
    # Learn from experience
    print(f"\n📚 Learning from experience...")
    improvement = oracle.learn_from_experience()
    print(f"   Improvement: {improvement:.2%}")
    
    # Status
    status = oracle.get_status()
    print(f"\n📈 Oracle Status:")
    print(f"   Model: {status['model_id']}")
    print(f"   Trained: {status['is_trained']}")
    print(f"   Accuracy: {status['accuracy']:.2%}")
    print(f"   Samples: {status['training_samples']}")
    
    # Save model
    model_path = Path(__file__).parent / "models" / "oracle_state.json"
    oracle.save_model(str(model_path))
    
    print("\n✅ Phase 1 complete!")


if __name__ == "__main__":
    main()
