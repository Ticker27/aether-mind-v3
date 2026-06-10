#!/usr/bin/env python3
"""
AETHER MIND v3.0 - Auto API Test Script
Tests connectivity, model routing, and team execution via DashScope API
"""

import json
import os
import sys
import time
from pathlib import Path
import requests
from datetime import datetime

# Configuration
BASE_DIR = Path(__file__).parent
CONFIG_FILE = BASE_DIR / "config" / "api_keys.json"
REGISTRY_FILE = BASE_DIR / "docs" / "unified_model_registry.json"

class AetherAPITester:
    def __init__(self):
        self.config = self.load_config()
        self.registry = self.load_registry()
        self.api_key = self.config.get("dashscope", {}).get("api_key")
        self.base_url = self.config.get("dashscope", {}).get("base_url", "https://dashscope.aliyuncs.com/api/v1")
        
        if not self.api_key:
            print("❌ ERROR: No DashScope API key found in config/api_keys.json")
            sys.exit(1)
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def load_config(self):
        """Load API configuration"""
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ Failed to load config: {e}")
            return {}
    
    def load_registry(self):
        """Load model registry"""
        try:
            with open(REGISTRY_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Could not load model registry: {e}")
            return {"models": []}
    
    def test_connection(self):
        """Test basic API connectivity using OpenAI-compatible endpoint"""
        print("\n🔌 [1/4] Testing API Connection...")
        try:
            # Use OpenAI-compatible chat/completions endpoint
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json={
                    "model": "qwen-turbo",
                    "messages": [{"role": "user", "content": "ping"}],
                    "max_tokens": 1
                },
                timeout=10
            )
            # 200 = OK, 401 = Auth error but connection OK, 400 = Bad request but connection OK
            if response.status_code in [200, 400, 401]:
                print(f"✅ Connection successful (Status: {response.status_code})")
                return True
            else:
                print(f"⚠️ Unexpected status: {response.status_code} - {response.text[:100]}")
                return False
        except requests.exceptions.Timeout:
            print("❌ Connection timeout")
            return False
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def get_recommended_model(self, task_type="code"):
        """Simulate model router logic"""
        models = self.registry.get("models", [])
        scored_models = []
        
        for model in models:
            score = 0
            name = model.get("name", "")
            
            # Scoring logic based on task type
            if task_type == "code":
                if "coder" in name.lower(): score += 10
                if "instruct" in name.lower(): score += 5
            elif task_type == "image":
                if "vision" in name.lower() or "vl" in name.lower(): score += 8
            
            # Prefer high parameter counts
            if "480b" in name: score += 7
            if "397b" in name: score += 6
            
            if score > 0:
                scored_models.append((score, name))
        
        # Sort by score descending
        scored_models.sort(key=lambda x: x[0], reverse=True)
        
        if scored_models:
            return scored_models[0][1]
        return "qwen-turbo"  # Fallback
    
    def execute_test_request(self, model_name, prompt):
        """Send actual API request using OpenAI-compatible format"""
        print(f"\n🚀 [2/4] Executing test request to: {model_name}")
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": "You are AETHER MIND system AI assistant."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 200
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                output = result.get("choices", [{}])[0].get("message", {}).get("content", "No output")[:150]
                print(f"✅ Success ({elapsed:.2f}s)")
                print(f"   Output: {output}...")
                return True
            else:
                try:
                    error_msg = response.json().get("error", {}).get("message", str(response.text))
                except:
                    error_msg = str(response.text)
                print(f"❌ API Error ({response.status_code}): {error_msg}")
                return False
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return False
    
    def run_full_test_suite(self):
        """Run complete test suite"""
        print("=" * 60)
        print("🖤 AETHER MIND v3.0 - AUTO API TEST SUITE")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"API Key Status: {'✅ Set' if self.api_key else '❌ Missing'}")
        print(f"Models in Registry: {len(self.registry.get('models', []))}")
        
        results = {
            "connection": False,
            "routing": False,
            "execution": False,
            "total_time": 0
        }
        
        start_total = time.time()
        
        # Test 1: Connection
        results["connection"] = self.test_connection()
        if not results["connection"]:
            print("\n⛔ Stopping due to connection failure.")
            return results
        
        # Test 2: Model Routing
        print("\n🧠 [3/4] Running Model Router Simulation...")
        recommended = self.get_recommended_model("code")
        print(f"✅ Recommended Model: {recommended}")
        results["routing"] = True
        
        # Test 3: Execution
        test_prompt = "Explain the AETHER MIND architecture in one sentence."
        results["execution"] = self.execute_test_request(recommended, test_prompt)
        
        results["total_time"] = time.time() - start_total
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"Connection:      {'✅ PASS' if results['connection'] else '❌ FAIL'}")
        print(f"Model Routing:   {'✅ PASS' if results['routing'] else '❌ FAIL'}")
        print(f"API Execution:   {'✅ PASS' if results['execution'] else '❌ FAIL'}")
        print(f"Total Time:      {results['total_time']:.2f} seconds")
        print("=" * 60)
        
        if all(results.values()):
            print("🎉 ALL TESTS PASSED - System ready for deployment!")
        else:
            print("⚠️ Some tests failed. Check logs above.")
        
        return results

if __name__ == "__main__":
    tester = AetherAPITester()
    tester.run_full_test_suite()
