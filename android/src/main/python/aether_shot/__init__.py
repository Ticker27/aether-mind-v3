"""
AETHER SHOT — 8-Ball Physics AI
Adaptive Ephemeral Physics Engine

Main entry point. รวมทุก layer เข้าด้วยกัน.
"""

import sys
import json
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from aether_shot.physics_mirror import mirror
from aether_shot.ensemble import ensemble
from aether_shot.session import session_manager
from aether_shot.adaptive import adaptive
from aether_shot.serverless import offload


class AetherShot:
    """Main AETHER SHOT engine"""
    
    def __init__(self):
        self.session = session_manager.create_session()
        self.player_id = 'default'
    
    def predict(self, cue_pos, ball_positions):
        """
        Predict best shot
        
        Args:
            cue_pos: (x, y) cue ball position
            ball_positions: [(id, x, y, is_target), ...]
        
        Returns:
            dict with prediction
        """
        # Layer 2: Ensemble prediction
        ensemble_result = ensemble.predict(cue_pos, ball_positions)
        
        # Layer 4: Adaptive adjustment
        base = ensemble_result.get('voted', {})
        adjusted = adaptive.adjust_prediction(self.player_id, base)
        
        # Layer 1: Physics verification
        if adjusted and 'angle' in adjusted and 'power' in adjusted:
            angle_val = adjusted['angle']
            if isinstance(angle_val, (list, tuple)):
                angle_val = angle_val[0] if angle_val else 0.0
            power_val = adjusted['power']
            if isinstance(power_val, (list, tuple)):
                power_val = power_val[0] if power_val else 5.0
            
            target_ball = adjusted.get('target_ball')
            
            # Physics mirror already verified in find_best_shot
            physics_verified = adjusted.get('physics_verified', False)
            
            if not physics_verified:
                # Fallback: try to find a working shot
                fb = mirror.find_best_shot(cue_pos, ball_positions)
                if fb and fb.get('physics_verified'):
                    adjusted.update(fb)
                    physics_verified = True
            
            adjusted['physics_verified'] = physics_verified
            adjusted = adjusted or {}
        
        # Build response
        result = {
            'session_id': self.session.session_id,
            'input': {
                'cue_position': cue_pos,
                'balls_on_table': len(ball_positions),
                'targets': [b[0] for b in ball_positions if len(b) > 3 and b[3]]
            },
            'prediction': adjusted,
            'ensemble': {
                'strategies_used': base.get('strategies_used', []),
                'consensus': base.get('consensus', 0)
            },
            'layer_status': {
                'physics_mirror': True,
                'polymorphic_ensemble': True,
                'ephemeral_session': True,
                'adaptive_learning': True,
            }
        }
        
        # Record to session
        target_pos = (ball_positions[0][1], ball_positions[0][2]) if ball_positions else (0, 0)
        self.session.record_shot(cue_pos, target_pos, result, {})
        
        return result
    
    def feedback(self, success, mistake=None):
        """Provide feedback for adaptive learning"""
        adaptive.learn_from_shot(self.player_id, 0, 0, 0, success, mistake=mistake)
        for strategy in ['physics', 'heuristic', 'ml']:
            ensemble.update_weights(strategy, success)
    
    def get_session_stats(self):
        return self.session.get_stats()
    
    def end_session(self):
        session_manager.destroy_session(self.session.session_id)
        adaptive.clear_all()


def demo():
    """Run demonstration"""
    print("=" * 65)
    print("  🔮 AETHER SHOT — 8-Ball Physics AI")
    print("  Adaptive Ephemeral Physics Engine")
    print("=" * 65)
    print()
    
    shot = AetherShot()
    
    # Simulate table state (mm units) — realistic 8-ball layout
    # Position: straight shot into corner pocket
    cue_pos = (400, 800)    # cue ball 
    ball_positions = [
        (1, 900, 750, True),    # target ball — straight shot to bottom-right
        (3, 1400, 600, False),
        (2, 1500, 800, False),
        (8, 1700, 750, True),   # 8-ball
    ]
    
    print("🎱 Table State:")
    print(f"   Cue ball: ({cue_pos[0]}, {cue_pos[1]})")
    print(f"   Targets: ball #{ball_positions[0][0]} at ({ball_positions[0][1]}, {ball_positions[0][2]}), ball #{ball_positions[3][0]} at ({ball_positions[3][1]}, {ball_positions[3][2]})")
    print()
    
    # Predict
    print("🧠 AETHER SHOT predicting...")
    result = shot.predict(cue_pos, ball_positions)
    
    pred = result.get('prediction', {})
    if pred:
        print()
        print("🎯 BEST SHOT:")
        print(f"   ├─ Target:      Ball #{pred.get('target_ball', '?')}")
        print(f"   ├─ Pocket:      #{pred.get('target_pocket', '?')} ({pred.get('pocket_name', '?')})")
        print(f"   ├─ Angle:       {pred.get('angle', 0):.1f}°")
        print(f"   ├─ Power:       {pred.get('power', 0):.1f}/10")
        print(f"   ├─ Cut angle:   {pred.get('cut_angle', 0):.1f}°")
        print(f"   ├─ Distance:    {pred.get('distance', 0):.0f} mm")
        print(f"   └─ Physics:     {'✅ VERIFIED' if pred.get('physics_verified') else '❌ FAILED'}")
        
        if pred.get('pocketed'):
            print(f"\n   💥 Pocketed balls: #{', #'.join(str(b) for b in pred['pocketed'])}")
        if pred.get('scratch'):
            print(f"   ⚠️  SCRATCH! Cue ball fell in pocket!")
        
        if pred.get('warning'):
            print(f"\n   ⚡ {pred['warning']}")
        
        print()
        print("📊 Ensemble:")
        print(f"   ├─ Strategies:  {', '.join(result['ensemble']['strategies_used'])}")
        print(f"   └─ Consensus:   {result['ensemble']['consensus']*100:.0f}%")
        
        if pred.get('player_accuracy'):
            print(f"\n📈 Your accuracy: {pred['player_accuracy']*100:.0f}%")
    
    print()
    print("🏁 Session complete")
    stats = shot.get_session_stats()
    print(f"   ├─ Session:     {stats['session_id']}")
    print(f"   └─ Shots:       {stats['shots']}")
    
    shot.end_session()
    print("\n🧹 Session destroyed — Zero Trace\n")


if __name__ == "__main__":
    demo()