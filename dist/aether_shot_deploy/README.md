# AETHER SHOT — Deploy Package

## Architecture

```
aether_shot/
├── __init__.py         — Main engine + CLI interface
├── physics_mirror.py   — Layer 1: Deterministic physics
├── ensemble.py         — Layer 2: Polymorphic voting
├── session.py          — Layer 3: Ephemeral RAM state
├── adaptive.py         — Layer 4: Real-time learning
└── serverless.py       — Layer 5: Cloud offload
```

## Principles

1. **Zero Disk** — ไม่แตะ disk, ทุกอย่างใน RAM
2. **Polymorphic** — เปลี่ยนตำแหน่ง/พฤติกรรมทุกครั้งที่รัน
3. **Multi-Layer** — ไม่พึ่งพาวิธีเดียว
4. **Active Defense** — ไม่ใช่แค่ซ่อน แต่หลอก/โจมตีกลับ
5. **Ephemeral** — เกิดใน RAM, ตายเมื่อปิด

## Usage

```python
from aether_shot import AetherShot

shot = AetherShot()
result = shot.predict(cue_pos=(500, 600), ball_positions=[...])
# Returns: { angle, power, spin, pocket, confidence }
```
