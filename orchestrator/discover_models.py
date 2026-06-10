#!/usr/bin/env python3
"""
AETHER MIND — Model Discovery & Categorization
===============================================
Query DashScope API and categorize models for AETHER MIND project
"""

import os
import sys
import json
from typing import Dict, List, Tuple
from dashscope_client import DashScopeClient, Model

# Model categorization rules
MODEL_CATEGORIES = {
    "code_specialist": {
        "keywords": ["coder", "code", "dev"],
        "description": "โมเดลเชี่ยวชาญด้านโค้ด",
        "use_case": "เขียนโค้ด, debug, refactor"
    },
    "vision": {
        "keywords": ["vision", "vl", "image"],
        "description": "โมเดลวิเคราะห์ภาพ",
        "use_case": "วิเคราะห์ screenshot, OCR, visual understanding"
    },
    "long_context": {
        "keywords": ["long", "128k", "1000k", "2m"],
        "min_context": 100000,
        "description": "โมเดล context ยาว",
        "use_case": "วิเคราะห์เอกสารยาว, codebase ใหญ่"
    },
    "thinking": {
        "keywords": ["thinking", "reason", "r1"],
        "description": "โมเดลคิดวิเคราะห์ลึก",
        "use_case": "วางแผน architecture, problem solving"
    },
    "fast": {
        "keywords": ["flash", "fast", "turbo", "quick"],
        "description": "โมเดลเร็ว",
        "use_case": "งานด่วน, real-time inference"
    },
    "general": {
        "keywords": [],
        "description": "โมเดลทั่วไป",
        "use_case": "งานทั่วไป, conversation"
    }
}


def categorize_model(model: Model) -> str:
    """
    Categorize a model based on its ID and capabilities
    
    Args:
        model: Model object
        
    Returns:
        Category name (code_specialist, vision, long_context, thinking, fast, general)
    """
    model_id_lower = model.id.lower()
    model_name_lower = model.name.lower()
    
    # Check each category
    for category, rules in MODEL_CATEGORIES.items():
        # Check keywords
        keywords = rules.get("keywords", [])
        for keyword in keywords:
            if keyword in model_id_lower or keyword in model_name_lower:
                return category
        
        # Check context window
        min_context = rules.get("min_context", 0)
        if min_context > 0 and model.context_window and model.context_window >= min_context:
            return category
    
    # Default to general
    return "general"


def discover_and_categorize_models() -> Dict[str, List[Model]]:
    """
    Discover all available models and categorize them
    
    Returns:
        Dict mapping category names to lists of models
    """
    # Initialize client
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        print("❌ Error: DASHSCOPE_API_KEY not set")
        print("\n📝 Please set your API key:")
        print("   export DASHSCOPE_API_KEY='your-api-key-here'")
        print("\n   Or get one from: https://dashscope.console.aliyun.com/apiKey")
        sys.exit(1)
    
    client = DashScopeClient(api_key)
    
    # Get all models
    print("🔍 Discovering models from DashScope API...")
    try:
        all_models = client.list_models()
    except Exception as e:
        print(f"❌ Failed to fetch models: {e}")
        sys.exit(1)
    
    print(f"✅ Found {len(all_models)} models\n")
    
    # Categorize
    categorized = {cat: [] for cat in MODEL_CATEGORIES.keys()}
    
    for model in all_models:
        category = categorize_model(model)
        categorized[category].append(model)
    
    # Sort by name within each category
    for category in categorized:
        categorized[category].sort(key=lambda m: m.name)
    
    return categorized


def print_categorized_models(categorized: Dict[str, List[Model]]):
    """
    Print categorized models in a nice format
    """
    print("=" * 80)
    print("🎯 AETHER MIND — Model Recommendations")
    print("=" * 80)
    print()
    
    total_models = sum(len(models) for models in categorized.values())
    print(f"📊 Total Models: {total_models}")
    print()
    
    # Print each category
    for category, rules in MODEL_CATEGORIES.items():
        models = categorized[category]
        
        if not models:
            continue
        
        print(f"### {rules['description']} ({len(models)} models)")
        print(f"📌 Use case: {rules['use_case']}")
        print()
        
        for i, model in enumerate(models, 1):
            ctx_info = f"({model.context_window:,} ctx)" if model.context_window else ""
            mods_info = ", ".join(model.modalities) if model.modalities else "text"
            
            print(f"  {i}. {model.name}")
            print(f"     ID: {model.id}")
            if model.context_window:
                print(f"     Context: {ctx_info}")
            print(f"     Modalities: {mods_info}")
            print()
        
        print("-" * 80)
        print()


def save_model_registry(categorized: Dict[str, List[Model]], output_file: str):
    """
    Save model registry to JSON file
    """
    registry = {
        "total_models": sum(len(models) for models in categorized.values()),
        "categories": {}
    }
    
    for category, models in categorized.items():
        registry["categories"][category] = {
            "description": MODEL_CATEGORIES[category]["description"],
            "use_case": MODEL_CATEGORIES[category]["use_case"],
            "models": [
                {
                    "id": model.id,
                    "name": model.name,
                    "context_window": model.context_window,
                    "modalities": model.modalities
                }
                for model in models
            ]
        }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Model registry saved to: {output_file}")


def recommend_models_for_aether_mind(categorized: Dict[str, List[Model]]) -> Dict[str, str]:
    """
    Recommend specific models for AETHER MIND phases
    
    Returns:
        Dict mapping phase to recommended model ID
    """
    recommendations = {}
    
    # Phase 1: Neural Oracle (needs thinking + code)
    thinking_models = categorized.get("thinking", [])
    code_models = categorized.get("code_specialist", [])
    
    if thinking_models:
        recommendations["neural_oracle"] = thinking_models[0].id
    elif code_models:
        recommendations["neural_oracle"] = code_models[0].id
    
    # Phase 2: Physics Engine (needs thinking)
    if thinking_models:
        recommendations["physics_engine"] = thinking_models[0].id
    
    # Phase 3: Frame Capture Analysis (needs vision)
    vision_models = categorized.get("vision", [])
    if vision_models:
        recommendations["frame_capture"] = vision_models[0].id
    
    # Phase 4: Stealth Layer (needs code)
    if code_models:
        recommendations["stealth_layer"] = code_models[0].id
    
    # Phase 5: Integration (needs long context)
    long_context_models = categorized.get("long_context", [])
    if long_context_models:
        recommendations["integration"] = long_context_models[0].id
    
    # Fast inference (needs fast model)
    fast_models = categorized.get("fast", [])
    if fast_models:
        recommendations["fast_inference"] = fast_models[0].id
    
    return recommendations


def print_recommendations(recommendations: Dict[str, str]):
    """
    Print model recommendations
    """
    print()
    print("=" * 80)
    print("🚀 AETHER MIND — Recommended Models for Each Phase")
    print("=" * 80)
    print()
    
    phase_names = {
        "neural_oracle": "Phase 1: Neural Oracle Core",
        "physics_engine": "Phase 2: Physics Engine",
        "frame_capture": "Phase 3: Frame Capture & Vision",
        "stealth_layer": "Phase 4: Stealth Layer",
        "integration": "Phase 5: Integration",
        "fast_inference": "Fast Inference (Real-time)"
    }
    
    for phase, model_id in recommendations.items():
        phase_name = phase_names.get(phase, phase)
        print(f"### {phase_name}")
        print(f"🎯 Recommended: {model_id}")
        print()
    
    print("-" * 80)


def main():
    """Main entry point"""
    print("🧬 AETHER MIND v3.0 — Model Discovery")
    print()
    
    # Discover and categorize
    categorized = discover_and_categorize_models()
    
    # Print categorized models
    print_categorized_models(categorized)
    
    # Save registry
    registry_file = os.path.join(os.path.dirname(__file__), "..", "docs", "model_registry.json")
    os.makedirs(os.path.dirname(registry_file), exist_ok=True)
    save_model_registry(categorized, registry_file)
    
    # Recommend models
    recommendations = recommend_models_for_aether_mind(categorized)
    print_recommendations(recommendations)
    
    # Save recommendations
    rec_file = os.path.join(os.path.dirname(__file__), "..", "docs", "model_recommendations.json")
    with open(rec_file, 'w', encoding='utf-8') as f:
        json.dump(recommendations, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Recommendations saved to: {rec_file}")
    
    print()
    print("✅ Model discovery complete!")
    print("📖 Check docs/model_registry.json for full model list")
    print("🎯 Check docs/model_recommendations.json for phase recommendations")


if __name__ == "__main__":
    main()
