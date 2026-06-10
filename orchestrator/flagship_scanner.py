#!/usr/bin/env python3
"""
AETHER MIND — Flagship Model Scanner (Optimized)
=================================================
สแกนหาโมเดลเรือธง (Flagship) จาก API จริง
ทดสอบ benchmark: speed, accuracy, capability
จัดอันดับและเลือก flagship สำหรับแต่ละหน้าที่

Optimized: ทดสอบเฉพาะ top candidates จากแต่ละหมวด
"""

import os
import json
import time
import requests
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict

# Import from shared config
from config_loader import Config
from dashscope_client import DashScopeClient


@dataclass
class BenchmarkResult:
    """ผลการทดสอบโมเดล"""
    model_id: str
    model_name: str
    source: str
    category: str
    
    # Performance metrics
    avg_latency_ms: float = 0.0
    tokens_per_second: float = 0.0
    
    # Capability scores (0-100)
    reasoning_score: float = 0.0
    coding_score: float = 0.0
    general_score: float = 0.0
    
    # Overall
    overall_score: float = 0.0
    rank: int = 0
    
    # Metadata
    context_window: Optional[int] = None
    modalities: List[str] = None
    test_timestamp: str = ""
    
    def __post_init__(self):
        if self.modalities is None:
            self.modalities = []


class FlagshipScanner:
    """สแกนหาโมเดลเรือธง — optimized version"""
    
    def __init__(self):
        # Auto-load from shared config
        api_key = Config.get_dashscope_key()
        self.client = DashScopeClient(api_key)
        self.results: List[BenchmarkResult] = []
        
        # Test prompts สำหรับแต่ละ capability
        self.test_prompts = {
            "reasoning": [
                "อธิบายทฤษฎีสัมพัทธภาพพิเศษของไอน์สไตน์ใน 3 ประโยค",
                "แก้สมการ: x² + 5x + 6 = 0 พร้อมแสดงวิธีทำ"
            ],
            "coding": [
                "เขียน Python function สำหรับ binary search พร้อม type hints",
                "สร้าง class สำหรับ linked list ใน Python"
            ],
            "general": [
                "อธิบายวิธีทำข้าวผัดกะเพรา",
                "แปลประโยคนี้: 'The quick brown fox jumps over the lazy dog' เป็นภาษาไทย"
            ]
        }
    
    def test_latency(self, model_id: str, prompt: str, num_tests: int = 2) -> Tuple[float, float]:
        """ทดสอบความเร็วของโมเดล"""
        latencies = []
        total_tokens = 0
        
        for _ in range(num_tests):
            start = time.time()
            
            try:
                result = self.client.chat(
                    model=model_id,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=100,
                    temperature=0.7
                )
                
                end = time.time()
                latency_ms = (end - start) * 1000
                latencies.append(latency_ms)
                
                content = result.get("content", "")
                total_tokens += len(content) // 4
                
            except Exception as e:
                print(f"  ⚠️  {model_id} failed: {e}")
                return 0.0, 0.0
        
        avg_latency = sum(latencies) / len(latencies)
        total_time = sum(latencies) / 1000
        tokens_per_sec = total_tokens / total_time if total_time > 0 else 0
        
        return avg_latency, tokens_per_sec
    
    def test_capability(self, model_id: str, capability: str) -> float:
        """ทดสอบความสามารถเฉพาะด้าน"""
        prompts = self.test_prompts.get(capability, [])
        if not prompts:
            return 0.0
        
        total_score = 0.0
        num_tests = 0
        
        for prompt in prompts[:1]:  # Test 1 prompt per capability (optimized)
            try:
                result = self.client.chat(
                    model=model_id,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200,
                    temperature=0.7
                )
                
                content = result.get("content", "")
                score = self._score_response(content, capability)
                total_score += score
                num_tests += 1
                
            except Exception as e:
                print(f"  ⚠️  {model_id} {capability} failed: {e}")
        
        return total_score / num_tests if num_tests > 0 else 0.0
    
    def _score_response(self, response: str, capability: str) -> float:
        """ให้คะแนนคำตอบ (แบบง่าย)"""
        if not response:
            return 0.0
        
        score = 0.0
        
        # Length score
        length = len(response)
        if length > 50:
            score += 20
        if length > 200:
            score += 20
        
        # Structure score
        if "\n" in response:
            score += 10
        if "- " in response or "* " in response:
            score += 10
        
        # Capability-specific
        if capability == "reasoning":
            if any(word in response.lower() for word in ["เพราะ", "ดังนั้น", "สรุป"]):
                score += 20
        
        elif capability == "coding":
            if "def " in response or "class " in response:
                score += 20
            if "```" in response:
                score += 20
        
        elif capability == "general":
            if len(response) > 100:
                score += 20
        
        return min(score, 100.0)
    
    def benchmark_model(self, model_id: str, model_name: str, source: str, category: str) -> BenchmarkResult:
        """ทดสอบโมเดลแบบเต็มรูปแบบ"""
        print(f"   Testing {model_name} ({category})...")
        
        result = BenchmarkResult(
            model_id=model_id,
            model_name=model_name,
            source=source,
            category=category,
            test_timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # Test latency
        avg_latency, tokens_per_sec = self.test_latency(
            model_id,
            "ตอบสั้นๆ: 1+1 เท่ากับเท่าไหร่?"
        )
        result.avg_latency_ms = avg_latency
        result.tokens_per_second = tokens_per_sec
        
        # Test capabilities (only relevant ones for category)
        if category in ["reasoning", "general"]:
            result.reasoning_score = self.test_capability(model_id, "reasoning")
        
        if category in ["coding", "general"]:
            result.coding_score = self.test_capability(model_id, "coding")
        
        result.general_score = self.test_capability(model_id, "general")
        
        # Calculate overall score
        result.overall_score = (
            result.reasoning_score * 0.3 +
            result.coding_score * 0.3 +
            result.general_score * 0.2 +
            (100 - min(result.avg_latency_ms / 10, 100)) * 0.2
        )
        
        print(f"    ✅ Latency: {avg_latency:.0f}ms | Score: {result.overall_score:.1f}")
        
        return result
    
    def scan_flagships(self, category: str, model_ids: List[str], source: str = "dashscope", max_models: int = 5) -> List[BenchmarkResult]:
        """สแกนหาโมเดลเรือธงจากหมวดหมู่"""
        print(f"\n🔍 Scanning {category} category ({len(model_ids)} candidates)...")
        print(f"   Will test top {max_models} models\n")
        
        models_to_test = model_ids[:max_models]
        results = []
        
        for model_id in models_to_test:
            try:
                result = self.benchmark_model(model_id, model_id, source, category)
                results.append(result)
            except Exception as e:
                print(f"  ❌ Failed to test {model_id}: {e}")
        
        results.sort(key=lambda r: r.overall_score, reverse=True)
        
        for i, result in enumerate(results, 1):
            result.rank = i
        
        print(f"✅ Tested {len(results)} models from {category}")
        
        return results
    
    def save_results(self, output_file: str):
        """บันทึกผลการทดสอบ"""
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "scan_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_tested": len(self.results),
            "flagships": [asdict(r) for r in self.results]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Results saved to: {output_file}")


def main():
    """Main entry point"""
    print("=" * 80)
    print("🧬 AETHER MIND — Flagship Model Scanner (Optimized)")
    print("=" * 80)
    print()
    
    # Initialize scanner
    scanner = FlagshipScanner()
    
    # Load model registry
    registry_file = Path(__file__).parent.parent / "docs" / "unified_model_registry.json"
    
    if not registry_file.exists():
        print("❌ Registry not found. Run unified_model_registry.py first.")
        return
    
    with open(registry_file, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    
    # Test top models from key categories
    categories_to_test = ["reasoning", "coding", "general"]
    
    for category in categories_to_test:
        cat_info = registry.get("categories", {}).get(category, {})
        models = cat_info.get("models", [])
        
        if not models:
            continue
        
        # Get top 5 from this category
        model_ids = [m["id"] for m in models[:5]]
        source = models[0].get("source", "dashscope")
        
        results = scanner.scan_flagships(category, model_ids, source, max_models=3)
        scanner.results.extend(results)
    
    # Save results
    output_file = Path(__file__).parent.parent / "docs" / "flagship_benchmarks.json"
    scanner.save_results(str(output_file))
    
    # Print top flagships
    print("\n" + "=" * 80)
    print("🏆 TOP FLAGSHIP MODELS")
    print("=" * 80)
    print()
    
    for i, result in enumerate(scanner.results[:10], 1):
        print(f"{i:2}. {result.model_name:40} Score: {result.overall_score:5.1f} | Latency: {result.avg_latency_ms:6.0f}ms")
        print(f"    [{result.category}] Reasoning: {result.reasoning_score:5.1f} | Coding: {result.coding_score:5.1f} | General: {result.general_score:5.1f}")
    
    print()
    print("✅ Flagship scanning complete!")
    print(f"📖 Full results: docs/flagship_benchmarks.json")


if __name__ == "__main__":
    main()
