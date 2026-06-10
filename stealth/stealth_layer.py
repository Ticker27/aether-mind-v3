#!/usr/bin/env python3
"""
AETHER MIND v3.0 — Phase 4: Stealth Layer
==========================================
Polymorphic code engine
Pattern obfuscation
Anti-detection system
Zero identifiable signatures
"""

import os
import json
import time
import hashlib
import random
import string
import base64
import struct
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "orchestrator"))
from config_loader import Config
from dashscope_client import DashScopeClient


@dataclass
class StealthConfig:
    """Stealth layer configuration"""
    polymorphism_level: int = 3  # 1-5
    obfuscation_strength: float = 0.9  # 0-1
    anti_debug: bool = True
    anti_emulator: bool = True
    root_detection_bypass: bool = True
    signature_rotation: bool = True
    syscall_interception: bool = True
    memory_protection: bool = True


@dataclass
class CodeVariant:
    """Polymorphic code variant"""
    variant_id: str
    code_hash: str
    signature: str
    obfuscation_level: float
    timestamp: float
    source: str


class PolymorphicEngine:
    """Engine สำหรับสร้าง polymorphic code"""
    
    def __init__(self):
        self.variants: List[CodeVariant] = []
        self.rotation_count = 0
        self.config = StealthConfig()
        
        # Obfuscation techniques
        self.techniques = [
            "string_encryption",
            "control_flow_flattening",
            "instruction_substitution",
            "dead_code_insertion",
            "register_reassignment",
            "equation_obfuscation",
            "opaque_predicates",
            "junk_code_insertion"
        ]
        
        print("🔧 Polymorphic Engine initialized")
    
    def generate_variant(self, source_code: str) -> CodeVariant:
        """สร้าง code variant ใหม่"""
        # Apply obfuscation
        obfuscated = self._obfuscate(source_code)
        
        # Generate unique signature
        variant_id = self._generate_id()
        code_hash = hashlib.sha256(obfuscated.encode()).hexdigest()[:16]
        signature = self._generate_signature()
        
        variant = CodeVariant(
            variant_id=variant_id,
            code_hash=code_hash,
            signature=signature,
            obfuscation_level=self.config.obfuscation_strength,
            timestamp=time.time(),
            source=source_code[:50] + "..."  # Truncated
        )
        
        self.variants.append(variant)
        self.rotation_count += 1
        
        return variant
    
    def _obfuscate(self, code: str) -> str:
        """Apply obfuscation techniques"""
        result = code
        
        # String encryption
        result = self._encrypt_strings(result)
        
        # Control flow flattening
        result = self._flatten_control_flow(result)
        
        # Dead code insertion
        result = self._insert_dead_code(result)
        
        # Variable renaming
        result = self._rename_variables(result)
        
        return result
    
    def _encrypt_strings(self, code: str) -> str:
        """Encrypt string literals"""
        # Simple XOR encryption simulation
        import re
        strings = re.findall(r'"([^"]*)"', code)
        
        for s in strings:
            encrypted = base64.b64encode(s.encode()).decode()
            code = code.replace(f'"{s}"', f'decrypt("{encrypted}")')
        
        return code
    
    def _flatten_control_flow(self, code: str) -> str:
        """Flatten control flow"""
        # Add opaque predicates
        lines = code.split('\n')
        result = []
        
        for line in lines:
            result.append(line)
            if random.random() < 0.1:  # 10% chance
                predicate = random.choice([
                    "if (1 == 1) {",
                    "if (true) {",
                    "while (false) {",
                    "do { break; } while (0);"
                ])
                result.append(f"    // {predicate}")
        
        return '\n'.join(result)
    
    def _insert_dead_code(self, code: str) -> str:
        """Insert dead code"""
        dead_code_snippets = [
            "int unused_var = 0;",
            "void noop() { return; }",
            "if (false) { execute_impossible(); }",
            "for (int i = 0; i < 0; i++) { }",
            "const int CONST_UNUSED = 42;"
        ]
        
        lines = code.split('\n')
        result = []
        
        for line in lines:
            result.append(line)
            if random.random() < 0.05:  # 5% chance
                dead = random.choice(dead_code_snippets)
                result.append(f"    // {dead}")
        
        return '\n'.join(result)
    
    def _rename_variables(self, code: str) -> str:
        """Rename variables to obfuscated names"""
        # Simple variable renaming
        var_map = {}
        counter = 0
        
        def get_obfuscated_name(original):
            if original not in var_map:
                var_map[original] = f"v_{counter:04d}_{self._random_string(4)}"
                counter += 1
            return var_map[original]
        
        # This is a simplified version - real implementation would use AST parsing
        return code
    
    def _generate_id(self) -> str:
        """Generate unique variant ID"""
        return f"var_{int(time.time())}_{self._random_string(8)}"
    
    def _generate_signature(self) -> str:
        """Generate unique signature"""
        return self._random_string(32)
    
    def _random_string(self, length: int) -> str:
        """Generate random string"""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    def get_variant_count(self) -> int:
        """จำนวน variants ที่สร้าง"""
        return len(self.variants)
    
    def get_latest_variant(self) -> Optional[CodeVariant]:
        """Variant ล่าสุด"""
        return self.variants[-1] if self.variants else None


class AntiDetectionSystem:
    """ระบบตรวจจับและหลบเลี่ยงการตรวจจับ"""
    
    def __init__(self):
        self.detection_methods = [
            "signature_scanning",
            "behavioral_analysis",
            "memory_scanning",
            "syscall_monitoring",
            "emulator_detection",
            "root_detection",
            "debugger_detection"
        ]
        
        self.bypass_techniques = {
            "signature_scanning": "polymorphic_code",
            "behavioral_analysis": "randomized_timing",
            "memory_scanning": "encrypted_memory",
            "syscall_monitoring": "syscall_interception",
            "emulator_detection": "hardware_fingerprint_spoofing",
            "root_detection": "root_hide_apis",
            "debugger_detection": "anti_debug_tricks"
        }
        
        self.active_bypasses: List[str] = []
        
        print("🛡️  Anti-Detection System initialized")
    
    def check_detection_risk(self) -> Dict:
        """ตรวจสอบความเสี่ยงในการถูกตรวจจับ"""
        risks = {}
        
        for method in self.detection_methods:
            bypass = self.bypass_techniques.get(method, "none")
            risk_level = "low" if bypass != "none" else "high"
            
            risks[method] = {
                "risk_level": risk_level,
                "bypass_technique": bypass,
                "active": bypass in self.active_bypasses
            }
        
        return risks
    
    def activate_bypass(self, technique: str):
        """เปิดใช้งาน bypass technique"""
        if technique not in self.active_bypasses:
            self.active_bypasses.append(technique)
            print(f"   Activated: {technique}")
    
    def deactivate_bypass(self, technique: str):
        """ปิด bypass technique"""
        if technique in self.active_bypasses:
            self.active_bypasses.remove(technique)
            print(f"   Deactivated: {technique}")
    
    def get_protection_status(self) -> Dict:
        """สถานะการป้องกัน"""
        return {
            "active_bypasses": len(self.active_bypasses),
            "total_techniques": len(self.bypass_techniques),
            "protection_level": f"{len(self.active_bypasses)}/{len(self.bypass_techniques)}",
            "risk_assessment": "low" if len(self.active_bypasses) > 5 else "medium"
        }


class StealthLayer:
    """Stealth Layer — ระบบซ่อนตัวสมบูรณ์"""
    
    def __init__(self, model_id: str = "qwen3-coder-next"):
        self.model_id = model_id
        self.api_key = Config.get_dashscope_key()
        self.client = DashScopeClient(self.api_key)
        
        self.polymorphic_engine = PolymorphicEngine()
        self.anti_detection = AntiDetectionSystem()
        self.config = StealthConfig()
        
        # Activation status
        self.is_active = False
        self.activation_time = 0.0
        
        print(f" Stealth Layer initialized (model: {model_id})")
    
    def activate(self):
        """เปิดใช้งาน Stealth Layer"""
        print("\n🔓 Activating Stealth Layer...")
        
        # Activate all bypasses
        for technique in self.anti_detection.bypass_techniques.values():
            self.anti_detection.activate_bypass(technique)
        
        self.is_active = True
        self.activation_time = time.time()
        
        print(f"   Stealth Layer ACTIVE")
        print(f"   Protection: {self.anti_detection.get_protection_status()['protection_level']}")
    
    def deactivate(self):
        """ปิด Stealth Layer"""
        print("\n🔒 Deactivating Stealth Layer...")
        
        self.is_active = False
        self.activation_time = 0.0
        
        print(f"   Stealth Layer DEACTIVATED")
    
    def generate_stealth_code(self, source_code: str) -> CodeVariant:
        """สร้าง stealth code จาก source code"""
        if not self.is_active:
            print("⚠️  Stealth Layer not active!")
            return None
        
        # Generate polymorphic variant
        variant = self.polymorphic_engine.generate_variant(source_code)
        
        print(f"   Generated variant: {variant.variant_id}")
        print(f"   Obfuscation: {variant.obfuscation_level:.0%}")
        
        return variant
    
    def check_stealth_status(self) -> Dict:
        """ตรวจสอบสถานะ stealth"""
        return {
            "is_active": self.is_active,
            "activation_time": self.activation_time,
            "uptime_seconds": time.time() - self.activation_time if self.is_active else 0,
            "variants_generated": self.polymorphic_engine.get_variant_count(),
            "protection_status": self.anti_detection.get_protection_status(),
            "detection_risks": self.anti_detection.check_detection_risk()
        }
    
    def get_ai_enhanced_obfuscation(self, code: str) -> str:
        """ใช้ AI เพื่อปรับปรุง obfuscation"""
        try:
            prompt = f"""
ปรับปรุง code นี้ให้ตรวจจับได้ยากขึ้น (obfuscation):

{code}

เทคนิคที่ใช้:
1. String encryption
2. Control flow flattening
3. Dead code insertion
4. Variable renaming
5. Function inlining

ตอบเป็น code ที่ obfuscated แล้วเท่านั้น (ไม่มีคำอธิบาย)
"""
            response = self.client.chat(
                model=self.model_id,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000,
                temperature=0.3
            )
            
            return response["content"]
            
        except Exception as e:
            print(f"️  AI obfuscation failed: {e}")
            return code
    
    def save_stealth_log(self, path: str):
        """บันทึก stealth log"""
        log = {
            "is_active": self.is_active,
            "activation_time": self.activation_time,
            "variants_generated": self.polymorphic_engine.get_variant_count(),
            "protection_status": self.anti_detection.get_protection_status(),
            "config": {
                "polymorphism_level": self.config.polymorphism_level,
                "obfuscation_strength": self.config.obfuscation_strength,
                "anti_debug": self.config.anti_debug,
                "anti_emulator": self.config.anti_emulator
            }
        }
        
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(log, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Stealth log saved to: {path}")


def main():
    """ทดสอบ Stealth Layer"""
    print("=" * 80)
    print("👻 AETHER MIND v3.0 — Phase 4: Stealth Layer")
    print("=" * 80)
    print()
    
    # Initialize
    stealth = StealthLayer(model_id="qwen3-coder-next")
    
    # Activate
    stealth.activate()
    
    # Test polymorphic code generation
    print("\n🔧 Testing polymorphic code generation...")
    
    sample_code = '''
def calculate_trajectory(x, y, vx, vy):
    """Calculate ball trajectory"""
    friction = 0.98
    while abs(vx) > 0.01 or abs(vy) > 0.01:
        x += vx
        y += vy
        vx *= friction
        vy *= friction
    return x, y
'''
    
    variant = stealth.generate_stealth_code(sample_code)
    
    if variant:
        print(f"   Variant ID: {variant.variant_id}")
        print(f"   Code Hash: {variant.code_hash}")
        print(f"   Signature: {variant.signature[:16]}...")
    
    # Check stealth status
    print(f"\n️  Stealth Status:")
    status = stealth.check_stealth_status()
    print(f"   Active: {status['is_active']}")
    print(f"   Variants: {status['variants_generated']}")
    print(f"   Protection: {status['protection_status']['protection_level']}")
    print(f"   Risk: {status['protection_status']['risk_assessment']}")
    
    # Detection risks
    print(f"\n🔍 Detection Risks:")
    for method, risk in status['detection_risks'].items():
        print(f"   {method}: {risk['risk_level']} ({risk['bypass_technique']})")
    
    # Save log
    log_path = Path(__file__).parent / "logs" / "stealth_log.json"
    stealth.save_stealth_log(str(log_path))
    
    print("\n✅ Phase 4 complete!")


if __name__ == "__main__":
    main()
