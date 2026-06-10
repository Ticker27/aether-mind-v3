#!/usr/bin/env python3
"""
AETHER MIND — Unified Model Registry
=====================================
รวมโมเดลจาก DashScope (146) + Minis (24) = 170 โมเดล
จัดกลุ่มตามความสามารถสำหรับ AETHER MIND project
"""

import json
import os
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

# Import DashScope client
import sys
sys.path.insert(0, str(Path(__file__).parent))
from dashscope_client import DashScopeClient


@dataclass
class UnifiedModel:
    """Unified model representation from all sources"""
    id: str
    name: str
    source: str  # "dashscope" or "minis"
    category: str
    subcategory: Optional[str] = None
    context_window: Optional[int] = None
    modalities: List[str] = None
    parameters: Optional[str] = None
    recommended_for: List[str] = None
    
    def __post_init__(self):
        if self.modalities is None:
            self.modalities = []
        if self.recommended_for is None:
            self.recommended_for = []


class ModelCategorizer:
    """Categorize models based on name patterns and capabilities"""
    
    # Category definitions with keywords
    CATEGORIES = {
        "coding": {
            "keywords": ["coder", "code", "dev", "instruct"],
            "subcategory": None,
            "description": "Code generation, debugging, refactoring"
        },
        "vision": {
            "keywords": ["vl", "vision", "image", "ocr"],
            "subcategory": {
                "analysis": ["vl", "vision", "ocr"],
                "generation": ["image-2.0", "image-edit", "image-max", "wan2.7"],
                "understanding": ["vl-max", "vl-plus", "vl-flash"]
            },
            "description": "Image analysis, OCR, visual understanding, image generation"
        },
        "reasoning": {
            "keywords": ["thinking", "reason", "r1", "qwq"],
            "subcategory": None,
            "description": "Deep reasoning, complex problem solving"
        },
        "fast": {
            "keywords": ["flash", "turbo", "fast", "quick", "lite"],
            "subcategory": None,
            "description": "Fast inference, real-time applications"
        },
        "general": {
            "keywords": ["max", "plus", "pro"],
            "subcategory": {
                "pro": ["pro", "max"],
                "standard": ["plus", "medium"],
                "lite": ["lite", "mini", "small"]
            },
            "description": "General purpose conversation and tasks"
        },
        "multimodal": {
            "keywords": ["omni", "audio", "video", "speech", "tts", "asr"],
            "subcategory": {
                "audio": ["audio", "speech", "tts", "asr"],
                "video": ["video"],
                "omni": ["omni"]
            },
            "description": "Multi-modal: text, audio, video, speech"
        },
        "specialized": {
            "keywords": ["translate", "embed", "rerank", "math", "glm", "kimi"],
            "subcategory": {
                "translation": ["translate", "mt-"],
                "embedding": ["embed", "rerank"],
                "math": ["math"],
                "other": ["glm", "kimi", "deepseek"]
            },
            "description": "Specialized tasks: translation, embedding, math, etc"
        }
    }
    
    @classmethod
    def categorize(cls, model_id: str, model_name: str) -> tuple[str, Optional[str]]:
        """
        Categorize a model based on its ID and name
        
        Returns:
            (category, subcategory) tuple
        """
        text = f"{model_id} {model_name}".lower()
        
        # Check each category
        for category, config in cls.CATEGORIES.items():
            keywords = config["keywords"]
            if any(kw in text for kw in keywords):
                # Check for subcategory
                subcategory = None
                if config.get("subcategory"):
                    for subcat, sub_keywords in config["subcategory"].items():
                        if any(skw in text for skw in sub_keywords):
                            subcategory = subcat
                            break
                
                return category, subcategory
        
        # Default to general
        return "general", None


class UnifiedModelRegistry:
    """Unified registry for all models from DashScope and Minis"""
    
    def __init__(self):
        self.models: List[UnifiedModel] = []
        self.categorizer = ModelCategorizer()
    
    def load_dashscope_models(self) -> int:
        """Load models from DashScope API"""
        print("🔍 Loading DashScope models...")
        
        try:
            client = DashScopeClient()
            dashscope_models = client.list_models()
            
            for m in dashscope_models:
                category, subcategory = self.categorizer.categorize(m.id, m.name)
                
                unified = UnifiedModel(
                    id=m.id,
                    name=m.name,
                    source="dashscope",
                    category=category,
                    subcategory=subcategory,
                    context_window=m.context_window,
                    modalities=m.modalities
                )
                self.models.append(unified)
            
            print(f"  ✅ Loaded {len(dashscope_models)} models from DashScope")
            return len(dashscope_models)
            
        except Exception as e:
            print(f"  ❌ Failed to load DashScope models: {e}")
            return 0
    
    def load_minis_models(self) -> int:
        """Load models from Minis (minis-model-use list)"""
        print("🔍 Loading Minis models...")
        
        try:
            result = subprocess.run(
                ["minis-model-use", "list"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                print(f"  ❌ minis-model-use failed: {result.stderr}")
                return 0
            
            # Parse JSON output (skip proot info lines)
            lines = result.stdout.split('\n')
            json_lines = []
            in_json = False
            for line in lines:
                if line.strip().startswith('{'):
                    in_json = True
                if in_json:
                    json_lines.append(line)
            
            json_str = '\n'.join(json_lines)
            data = json.loads(json_str)
            
            minis_models = data.get("models", [])
            
            for m in minis_models:
                model_id = m.get("model_id", "")
                display_name = m.get("display_name", model_id)
                context_window = m.get("context_window")
                modalities = m.get("modalities", [])
                
                category, subcategory = self.categorizer.categorize(model_id, display_name)
                
                unified = UnifiedModel(
                    id=model_id,
                    name=display_name,
                    source="minis",
                    category=category,
                    subcategory=subcategory,
                    context_window=context_window,
                    modalities=modalities
                )
                self.models.append(unified)
            
            print(f"  ✅ Loaded {len(minis_models)} models from Minis")
            return len(minis_models)
            
        except Exception as e:
            print(f"  ❌ Failed to load Minis models: {e}")
            return 0
    
    def get_categories_summary(self) -> Dict[str, Dict]:
        """Get summary of all categories"""
        summary = {}
        
        for model in self.models:
            cat = model.category
            if cat not in summary:
                summary[cat] = {
                    "description": self.categorizer.CATEGORIES.get(cat, {}).get("description", ""),
                    "count": 0,
                    "dashscope": 0,
                    "minis": 0,
                    "models": []
                }
            
            summary[cat]["count"] += 1
            if model.source == "dashscope":
                summary[cat]["dashscope"] += 1
            else:
                summary[cat]["minis"] += 1
            
            summary[cat]["models"].append({
                "id": model.id,
                "name": model.name,
                "source": model.source,
                "subcategory": model.subcategory,
                "context_window": model.context_window,
                "modalities": model.modalities
            })
        
        return summary
    
    def recommend_for_phases(self) -> Dict[str, List[str]]:
        """Recommend models for each AETHER MIND phase"""
        recommendations = {
            "phase1_neural_oracle": [],
            "phase2_physics_engine": [],
            "phase3_frame_capture": [],
            "phase4_stealth_layer": [],
            "phase5_android_apk": [],
            "fast_inference": []
        }
        
        # Phase 1: Neural Oracle - needs reasoning + coding
        for model in self.models:
            if model.category in ["reasoning", "coding"]:
                if model.category == "reasoning" or "coder" in model.id.lower():
                    recommendations["phase1_neural_oracle"].append(model.id)
        
        # Phase 2: Physics Engine - needs reasoning
        for model in self.models:
            if model.category == "reasoning":
                recommendations["phase2_physics_engine"].append(model.id)
        
        # Phase 3: Frame Capture - needs vision
        for model in self.models:
            if model.category == "vision" and "vl" in model.id.lower():
                recommendations["phase3_frame_capture"].append(model.id)
        
        # Phase 4: Stealth Layer - needs coding
        for model in self.models:
            if model.category == "coding":
                recommendations["phase4_stealth_layer"].append(model.id)
        
        # Phase 5: Android APK - needs coding + general
        for model in self.models:
            if model.category in ["coding", "general"]:
                if model.subcategory in ["pro", "standard"]:
                    recommendations["phase5_android_apk"].append(model.id)
        
        # Fast inference - needs fast models
        for model in self.models:
            if model.category == "fast":
                recommendations["fast_inference"].append(model.id)
        
        # Limit to top 5 per phase
        for phase in recommendations:
            recommendations[phase] = recommendations[phase][:5]
        
        return recommendations
    
    def save_registry(self, output_file: str):
        """Save registry to JSON file"""
        registry = {
            "total_models": len(self.models),
            "sources": {
                "dashscope": sum(1 for m in self.models if m.source == "dashscope"),
                "minis": sum(1 for m in self.models if m.source == "minis")
            },
            "categories": self.get_categories_summary(),
            "recommendations": self.recommend_for_phases()
        }
        
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(registry, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 Registry saved to: {output_file}")


def print_summary(registry: UnifiedModelRegistry):
    """Print summary of registry"""
    print("\n" + "=" * 80)
    print("🎯 AETHER MIND — Unified Model Registry Summary")
    print("=" * 80)
    print(f"\n📊 Total Models: {len(registry.models)}")
    print(f"  • DashScope: {sum(1 for m in registry.models if m.source == 'dashscope')}")
    print(f"  • Minis: {sum(1 for m in registry.models if m.source == 'minis')}")
    
    summary = registry.get_categories_summary()
    
    print("\n📋 Categories:")
    for cat, info in sorted(summary.items()):
        print(f"\n  ### {cat.upper()} ({info['count']} models)")
        print(f"  {info['description']}")
        print(f"  Sources: DashScope={info['dashscope']}, Minis={info['minis']}")
        
        # Show top 3 models
        for i, m in enumerate(info['models'][:3], 1):
            ctx = f"({m['context_window']:,} ctx)" if m.get('context_window') else ""
            print(f"    {i}. {m['name']} [{m['source']}] {ctx}")
        
        if len(info['models']) > 3:
            print(f"    ... and {len(info['models']) - 3} more")
    
    # Recommendations
    recs = registry.recommend_for_phases()
    print("\n\n🚀 Recommended Models for AETHER MIND Phases:")
    print("=" * 80)
    
    phase_names = {
        "phase1_neural_oracle": "Phase 1: Neural Oracle Core",
        "phase2_physics_engine": "Phase 2: Physics Engine",
        "phase3_frame_capture": "Phase 3: Frame Capture & Vision",
        "phase4_stealth_layer": "Phase 4: Stealth Layer",
        "phase5_android_apk": "Phase 5: Android APK",
        "fast_inference": "Fast Inference (Real-time)"
    }
    
    for phase, model_ids in recs.items():
        print(f"\n### {phase_names.get(phase, phase)}")
        if model_ids:
            for i, mid in enumerate(model_ids, 1):
                print(f"  {i}. {mid}")
        else:
            print("  (No recommendations)")


def main():
    """Main entry point"""
    print("🧬 AETHER MIND — Unified Model Registry Builder")
    print()
    
    registry = UnifiedModelRegistry()
    
    # Load from both sources
    dashscope_count = registry.load_dashscope_models()
    minis_count = registry.load_minis_models()
    
    print(f"\n✅ Total: {len(registry.models)} models ({dashscope_count} DashScope + {minis_count} Minis)")
    
    # Save registry
    output_file = Path(__file__).parent.parent / "docs" / "unified_model_registry.json"
    registry.save_registry(str(output_file))
    
    # Print summary
    print_summary(registry)
    
    print("\n\n✅ Registry building complete!")
    print(f"📖 Full registry: docs/unified_model_registry.json")


if __name__ == "__main__":
    main()
