#!/usr/bin/env python3
"""
AETHER SHOT — DEPLOY TOOL
=========================
สร้างแพคเกจที่พร้อม deploy สำหรับ Android
"""

import os
import sys
import json
import shutil
import zipfile
import hashlib
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent
AETHER_SHOT_DIR = PROJECT_ROOT / "aether_shot"
DIST_DIR = PROJECT_ROOT / "dist"
DEPLOY_DIR = DIST_DIR / "aether_shot_deploy"

def build_deploy_package():
    """สร้าง deploy package"""
    print("=" * 50)
    print("  🚀 AETHER SHOT DEPLOY")
    print("=" * 50)
    
    # Clean dist
    if DEPLOY_DIR.exists():
        shutil.rmtree(DEPLOY_DIR)
    
    DEPLOY_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Collect source files
    print("\n📦 Collecting source files...")
    source_files = {}
    
    for f in sorted(AETHER_SHOT_DIR.rglob("*.py")):
        rel_path = f.relative_to(AETHER_SHOT_DIR)
        print(f"   + {rel_path}")
        
        dest = DEPLOY_DIR / "source" / rel_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, dest)
        
        with open(f, 'rb') as fh:
            content = fh.read()
            h = hashlib.sha256(content).hexdigest()
            source_files[str(rel_path)] = {
                'size': len(content),
                'sha256': h
            }
    
    # 2. Create manifest
    print("\n📋 Creating deploy manifest...")
    manifest = {
        'package': 'aether_shot',
        'version': '1.0.0',
        'build_date': datetime.now().isoformat(),
        'architecture': '5-layer physics AI engine',
        'principles': [
            'Zero Disk — RAM only',
            'Polymorphic — every execution changes',
            'Multi-Layer — 3 strategies + voting',
            'Active Defense — not hide, fight back',
            'Ephemeral — born in RAM, die on exit'
        ],
        'layers': {
            '1_physics_mirror': 'Deterministic physics engine',
            '2_polymorphic_ensemble': '3-strategy voting system',
            '3_ephemeral_session': 'RAM-only zero trace session',
            '4_adaptive_learning': 'Real-time player pattern learning',
            '5_serverless_offload': 'Cloud function bridge'
        },
        'files': source_files,
        'total_size': sum(f['size'] for f in source_files.values())
    }
    
    manifest_path = DEPLOY_DIR / "manifest.json"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"   + manifest.json ({os.path.getsize(manifest_path)} bytes)")
    
    # 3. Create README
    readme = """# AETHER SHOT — Deploy Package

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
"""
    
    readme_path = DEPLOY_DIR / "README.md"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme)
    
    # 4. Create zip archive
    print("\n🗜️ Creating zip archive...")
    zip_path = DIST_DIR / "aether_shot_v1.0.0.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in DEPLOY_DIR.rglob("*"):
            arcname = str(f.relative_to(DEPLOY_DIR))
            zf.write(f, arcname)
    
    zip_size = os.path.getsize(zip_path)
    print(f"   ✅ Created: {zip_path.name} ({zip_size / 1024:.0f} KB)")
    
    # 5. Summary
    print("\n" + "=" * 50)
    print("  ✅ DEPLOY READY")
    print("=" * 50)
    print(f"   📦 Package: {zip_path}")
    print(f"   📏 Size:    {zip_size / 1024:.1f} KB")
    print(f"   📁 Files:   {len(source_files)} Python files")
    print(f"   🔢 SHA256:  {hashlib.sha256(open(zip_path, 'rb').read()).hexdigest()[:16]}...")
    print(f"\n   To deploy on device:")
    print(f"   1. Copy {zip_path.name} to device")
    print(f"   2. Extract: unzip {zip_path.name}")
    print(f"   3. Run: python3 -m aether_shot")

if __name__ == "__main__":
    build_deploy_package()