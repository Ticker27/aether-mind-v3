#!/usr/bin/env python3
"""
AETHER MIND — Main Orchestrator
================================
ระบบจัดการทีม AI/Crown อัตโนมัติ

Usage:
    python3 orchestrator.py start          # เริ่มระบบ
    python3 orchestrator.py status         # ดูสถานะ
    python3 orchestrator.py phase <N>      # เริ่ม phase
    python3 orchestrator.py commit         # Commit progress
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
DOCS_DIR = PROJECT_ROOT / "docs"
LOCK_DIR = PROJECT_ROOT / "lock"
STATE_FILE = LOCK_DIR / "state.json"

# Colors
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RED = '\033[91m'
RESET = '\033[0m'


def print_header():
    """Print AETHER MIND header"""
    print(f"{BLUE}")
    print("=" * 70)
    print("  🧬 AETHER MIND v3.0 — Main Orchestrator")
    print("=" * 70)
    print(f"{RESET}")


def load_api_keys():
    """Load API keys from config"""
    api_keys_file = CONFIG_DIR / "api_keys.json"
    
    if not api_keys_file.exists():
        print(f"{RED}❌ Error: config/api_keys.json not found{RESET}")
        print(f"\n📝 Please create {api_keys_file} with your API keys")
        sys.exit(1)
    
    with open(api_keys_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def check_api_keys(api_keys):
    """Check if API keys are configured"""
    print(f"{YELLOW}🔑 Checking API keys...{RESET}\n")
    
    configured = []
    
    for provider, config in api_keys.items():
        if provider == "notes":
            continue
        
        api_key = config.get("api_key", "")
        
        if api_key and api_key != f"YOUR_{provider.upper()}_API_KEY_HERE":
            print(f"  ✅ {provider}: Configured")
            configured.append(provider)
        else:
            print(f"  ❌ {provider}: Not configured")
    
    print()
    
    if not configured:
        print(f"{RED}❌ No API keys configured!{RESET}")
        print(f"\n📝 Edit {CONFIG_DIR / 'api_keys.json'} and add your API keys")
        return False
    
    print(f"{GREEN}✅ {len(configured)} provider(s) configured{RESET}\n")
    return True


def load_state():
    """Load current state"""
    if not STATE_FILE.exists():
        return {
            "project": "AETHER MIND v3.0",
            "status": "initialized",
            "current_phase": 0,
            "phases": {
                "1": {"name": "Neural Oracle Core", "status": "pending"},
                "2": {"name": "Physics Engine", "status": "pending"},
                "3": {"name": "Frame Capture", "status": "pending"},
                "4": {"name": "Stealth Layer", "status": "pending"},
                "5": {"name": "Android APK", "status": "pending"}
            },
            "created": datetime.now().isoformat(),
            "last_update": datetime.now().isoformat()
        }
    
    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_state(state):
    """Save current state"""
    LOCK_DIR.mkdir(exist_ok=True)
    state["last_update"] = datetime.now().isoformat()
    
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def print_status():
    """Print current status"""
    print(f"{YELLOW}📊 Current Status{RESET}\n")
    
    state = load_state()
    
    print(f"  Project: {state['project']}")
    print(f"  Status: {state['status']}")
    print(f"  Current Phase: {state['current_phase']}")
    print()
    
    print(f"  {BLUE}Phases:{RESET}")
    for phase_num, phase_info in state['phases'].items():
        status_emoji = {
            'pending': '⏳',
            'in_progress': '🔄',
            'complete': '✅'
        }.get(phase_info['status'], '❓')
        
        print(f"    {status_emoji} Phase {phase_num}: {phase_info['name']}")
    
    print()
    print(f"  Last Update: {state['last_update']}")
    print()


def start_system():
    """Start the orchestrator system"""
    print(f"{GREEN}🚀 Starting AETHER MIND System...{RESET}\n")
    
    # Load and check API keys
    api_keys = load_api_keys()
    if not check_api_keys(api_keys):
        return
    
    # Load state
    state = load_state()
    print_status()
    
    # Check if model registry exists
    registry_file = DOCS_DIR / "model_registry.json"
    
    if not registry_file.exists():
        print(f"{YELLOW}📋 Model registry not found. Running discovery...{RESET}\n")
        
        # Set API key environment variable
        dashscope_key = api_keys.get("dashscope", {}).get("api_key", "")
        if dashscope_key and dashscope_key != "YOUR_DASHSCOPE_API_KEY_HERE":
            os.environ["DASHSCOPE_API_KEY"] = dashscope_key
            
            # Run discovery
            discover_script = Path(__file__).parent / "discover_models.py"
            if discover_script.exists():
                subprocess.run([sys.executable, str(discover_script)], check=True)
                print()
    
    print(f"{GREEN}✅ System ready!{RESET}")
    print(f"\n{BLUE}Next steps:{RESET}")
    print(f"  1. Review docs/model_registry.json")
    print(f"  2. Start Phase 1: {sys.argv[0]} phase 1")
    print(f"  3. Check status: {sys.argv[0]} status")
    print()


def start_phase(phase_num):
    """Start a specific phase"""
    state = load_state()
    
    if phase_num not in state['phases']:
        print(f"{RED}❌ Invalid phase: {phase_num}{RESET}")
        return
    
    phase_name = state['phases'][phase_num]['name']
    print(f"{GREEN}🚀 Starting Phase {phase_num}: {phase_name}{RESET}\n")
    
    # Update state
    state['current_phase'] = phase_num
    state['phases'][phase_num]['status'] = 'in_progress'
    state['status'] = f"phase_{phase_num}_in_progress"
    save_state(state)
    
    print(f"{YELLOW}📋 Phase {phase_num} Requirements:{RESET}")
    
    phase_requirements = {
        "1": [
            "Neural network architecture design",
            "Training data collection (game footage)",
            "Model training (trajectory prediction)",
            "Accuracy testing (>95%)",
            "Self-learning implementation"
        ],
        "2": [
            "Physics engine implementation",
            "Beyond Newtonian calculations",
            "Chaos theory integration",
            "Real-time simulation (<10ms)",
            "Validation against real gameplay"
        ],
        "3": [
            "Frame capture mechanism",
            "Zero-copy buffer access",
            "No memory reading",
            "Latency optimization (<5ms)",
            "Anti-detection testing"
        ],
        "4": [
            "Code polymorphism",
            "Pattern obfuscation",
            "Anti-detection system",
            "Stealth validation",
            "Security audit"
        ],
        "5": [
            "Android project setup",
            "APK packaging",
            "Permission minimization",
            "Integration testing",
            "Real device testing"
        ]
    }
    
    for req in phase_requirements.get(phase_num, []):
        print(f"  • {req}")
    
    print()
    print(f"{BLUE}🛠️  Team Instructions:{RESET}")
    print(f"  1. Review requirements above")
    print(f"  2. Use appropriate models (see docs/model_recommendations.json)")
    print(f"  3. Commit progress regularly")
    print(f"  4. Update lock/state.json when complete")
    print()


def commit_progress(message):
    """Commit current progress"""
    print(f"{YELLOW}📦 Committing progress...{RESET}\n")
    
    try:
        # Git add
        subprocess.run(["git", "add", "."], cwd=PROJECT_ROOT, check=True)
        
        # Git commit
        subprocess.run(
            ["git", "commit", "-m", message],
            cwd=PROJECT_ROOT,
            check=True
        )
        
        print(f"{GREEN}✅ Committed: {message}{RESET}\n")
        
    except subprocess.CalledProcessError as e:
        print(f"{RED}❌ Commit failed: {e}{RESET}\n")


def main():
    """Main entry point"""
    print_header()
    
    if len(sys.argv) < 2:
        print(f"{RED}❌ No command specified{RESET}\n")
        print(f"Usage:")
        print(f"  python3 {sys.argv[0]} start          # Start system")
        print(f"  python3 {sys.argv[0]} status         # Show status")
        print(f"  python3 {sys.argv[0]} phase <N>      # Start phase N")
        print(f"  python3 {sys.argv[0]} commit <msg>   # Commit progress")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "start":
        start_system()
    
    elif command == "status":
        print_status()
    
    elif command == "phase":
        if len(sys.argv) < 3:
            print(f"{RED}❌ Phase number required{RESET}")
            sys.exit(1)
        start_phase(sys.argv[2])
    
    elif command == "commit":
        if len(sys.argv) < 3:
            message = f"Progress update: {datetime.now().isoformat()}"
        else:
            message = " ".join(sys.argv[2:])
        commit_progress(message)
    
    else:
        print(f"{RED}❌ Unknown command: {command}{RESET}")
        sys.exit(1)


if __name__ == "__main__":
    main()
