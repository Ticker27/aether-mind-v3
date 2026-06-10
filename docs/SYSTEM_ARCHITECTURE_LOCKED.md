#  AETHER MIND — System Architecture (Locked)

> **สถานะ:** ล็อคแล้ว — ทีมทำงานอัตโนมัติ 100%
> **Minis Role:** Command Center เท่านั้น (สื่อสาร + สั่งงาน)

---

##  Configuration Lock Status

### API Configuration
```json
{
  "dashscope": {
    "api_key": "sk-ws-...ljvZ",
    "base_url": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    "status": "active",
    "locked": true,
    "locked_at": "2026-06-10T15:30:00"
  }
}
```

**ไฟล์:** `config/api_keys.json`
**สถานะ:** ✅ ล็อคแล้ว — สคริปต์ทั้งหมดอ่านจากไฟล์นี้

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MINIS APP (Command Center)               │
│  ─────────────────────────────────────────────────────┐   │
│  │  User Interface                                      │   │
│  │  • ส่งคำสั่ง: "เริ่ม Phase 1"                        │   │
│  │  • ดูสถานะ: "เช็ค progress"                          │   │
│  │  • รับรายงาน: ผลลัพธ์จากทีม                          │   │
│  ─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ คำสั่ง (text)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              ORCHESTRATOR (Team Manager)                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  config_loader.py                                    │   │
│  │  • โหลด API key อัตโนมัติ                           │   │
│  │  • Singleton pattern — โหลดครั้งเดียว                │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  dashscope_client.py                                 │   │
│  │  • เชื่อมต่อ DashScope API                           │   │
│  │  • อ่าน config จาก config_loader                     │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  unified_model_registry.py                           │   │
│  │  • จัดกลุ่ม 206 โมเดล                                │   │
│  │  • แบ่ง 7 หมวดหมู่                                   │   │
│  └─────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  flagship_scanner.py                                 │   │
│  │  • ทดสอบ benchmark โมเดลเรือธง                      │   │
│  │  • จัดอันดับ + แนะนำสำหรับแต่ละ Phase                │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ API Calls
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              DASHSCOPE API (Cloud)                          │
│  • 146 โมเดล                                                 │
│  • OpenAI-compatible format                                  │
│  • Endpoint: https://dashscope-intl.aliyuncs.com/...        │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Model Registry (Locked)

### Total: 206 Models
- **DashScope:** 146 โมเดล
- **Minis:** 60 โมเดล

### Categories (7 หมวดหมู่)

| Category | จำนวน | Use Case |
|:---|:---|:---|
| **CODING** | 28 | เขียนโค้ด, debug, refactor |
| **FAST** | 48 | งานด่วน, real-time inference |
| **GENERAL** | 77 | งานทั่วไป, conversation |
| **MULTIMODAL** | 7 | audio, video, speech |
| **REASONING** | 8 | คิดวิเคราะห์ลึก |
| **SPECIALIZED** | 6 | translate, embedding, math |
| **VISION** | 32 | วิเคราะห์ภาพ, OCR |

---

## 🏆 Flagship Models (Benchmarked & Locked)

### Top 3 Flagships

| Rank | Model | Category | Score | Latency | Status |
|:---|:---|:---|:---|:---|:---|
|  | `qwen3.7-max-2026-06-08` | General | 61.0 | 4.8s | ✅ Active |
| 🥈 | `qwen3-coder-next` | Coding | 44.5 | 0.9s | ✅ Active |
| 🥉 | `qwq-plus` | Reasoning | 0.0 | 6.6s | ✅ Active |

### Recommended for Each Phase

| Phase | Recommended Model | Reason |
|:---|:---|:---|
| **P1: Neural Oracle** | `qwq-plus` | Deep reasoning |
| **P2: Physics Engine** | `qwq-plus` | Complex problem solving |
| **P3: Frame Capture** | `qwen3-vl-flash` | Vision analysis (fast) |
| **P4: Stealth Layer** | `qwen3-coder-next` | Code obfuscation |
| **P5: Android APK** | `qwen3.7-max-2026-06-08` | General purpose (highest) |
| **Fast Inference** | `deepseek-v4-flash` | Fastest (1M context) |

---

## 📁 File Structure (Locked)

```
/var/minis/workspace/aether_mind/
├── config/
│   └── api_keys.json              ✅ ล็อคแล้ว (API key + status)
├── orchestrator/
│   ├── config_loader.py           ✅ Shared config (singleton)
│   ├── dashscope_client.py        ✅ API client (auto-load config)
│   ├── unified_model_registry.py  ✅ จัดกลุ่ม 206 โมเดล
│   ├── flagship_scanner.py        ✅ Benchmark + ranking
│   ├── discover_models.py         ✅ Model discovery
│   └── orchestrator.py            ✅ Main orchestrator
├── docs/
│   ├── TEAM_MISSION_BRIEF.md      ✅ คู่มือทีม
│   ├── unified_model_registry.json ✅ Registry 206 โมเดล
│   ├── flagship_benchmarks.json   ✅ Benchmark results (locked)
│   ── AETHER_MIND_v3_Architecture.md ✅ สถาปัตยกรรม
└── lock/
    └── state.json                 ✅ สถานะปัจจุบัน
```

---

## 🔄 Workflow (Autonomous)

### 1. User สั่งงานผ่าน Minis
```
"เริ่ม Phase 1: Neural Oracle Core"
```

### 2. Orchestrator รับคำสั่ง
```bash
python3 orchestrator/orchestrator.py phase 1
```

### 3. Team ทำงานอัตโนมัติ
- ✅ อ่าน config จาก `config_loader.py`
- ✅ ใช้ API key จาก `config/api_keys.json`
- ✅ เลือกโมเดลจาก `docs/flagship_benchmarks.json`
- ✅ ทำงาน (เขียนโค้ด, train model, etc.)
- ✅ Commit progress

### 4. รายงานผลลัพธ์
```
✅ Phase 1 complete
📊 Accuracy: 95.3%
⏱️  Latency: 8ms
📝 Commit: abc123
```

---

## ⚠️ Important Notes

### Minis App Role
- ✅ ส่งคำสั่ง (text)
- ✅ ดูสถานะ (read logs)
- ✅ รับรายงาน (results)
- ❌ ไม่ทำงานหนัก (no heavy processing)
- ❌ ไม่เรียก API โดยตรง (let scripts handle it)

### Team Autonomy
- ✅ อ่าน config อัตโนมัติ
- ✅ เลือกโมเดลเอง (จาก benchmark)
- ✅ จัดการ API calls เอง
- ✅ Commit progress เอง
- ✅ รายงานผลลัพธ์เอง

### No Overlapping
- ✅ Config อ่านจากไฟล์เดียว (`config/api_keys.json`)
- ✅ State จัดการโดย `lock/state.json`
- ✅ Models จัดกลุ่มชัดเจน (7 หมวดหมู่)
- ✅ Flagships ล็อคแล้ว (3 โมเดล)

---

## 🚀 Quick Commands

### สำหรับ User (ผ่าน Minis)
```bash
# เริ่มระบบ
python3 orchestrator/orchestrator.py start

# ดูสถานะ
python3 orchestrator/orchestrator.py status

# เริ่ม Phase
python3 orchestrator/orchestrator.py phase 1

# Commit progress
python3 orchestrator/orchestrator.py commit "Phase 1 started"
```

### สำหรับ Team (อัตโนมัติ)
```bash
# โหลด config
from config_loader import Config
api_key = Config.get_dashscope_key()

# ใช้ API
from dashscope_client import DashScopeClient
client = DashScopeClient(api_key)

# อ่าน registry
import json
with open('docs/unified_model_registry.json') as f:
    registry = json.load(f)

# อ่าน flagship
with open('docs/flagship_benchmarks.json') as f:
    flagships = json.load(f)
```

---

## ✅ System Status

| Component | Status | Locked |
|:---|:---|:---|
| API Key | ✅ Active | ✅ Yes |
| Config Loader | ✅ Working | ✅ Yes |
| Model Registry | ✅ 206 models | ✅ Yes |
| Flagship Benchmarks | ✅ 3 models | ✅ Yes |
| Orchestrator | ✅ Ready | ✅ Yes |

---

## 🎯 Next Steps

1. **Phase 1: Neural Oracle Core**
   - ใช้โมเดล: `qwq-plus` (reasoning)
   - หน้าที่: Train neural network สำหรับ ball trajectory prediction

2. **Phase 2: Physics Engine**
   - ใช้โมเดล: `qwq-plus` (reasoning)
   - หน้าที่: สร้าง physics engine (beyond Newtonian)

3. **Phase 3: Frame Capture**
   - ใช้โมเดล: `qwen3-vl-flash` (vision)
   - หน้าที่: จับภาพเกม (zero-trace)

4. **Phase 4: Stealth Layer**
   - ใช้โมเดล: `qwen3-coder-next` (coding)
   - หน้าที่: สร้าง stealth system (polymorphic code)

5. **Phase 5: Android APK**
   - ใช้โมเดล: `qwen3.7-max-2026-06-08` (general)
   - หน้าที่: Package เป็น APK

---

## 📞 Communication Protocol

### User → Team
```
"เริ่ม Phase X"
"ใช้โมเดล Y สำหรับงาน Z"
"ตรวจสอบผลลัพธ์"
```

### Team → User
```
✅ Phase X complete
📊 Metrics: ...
⏱️  Performance: ...
📝 Commit: ...
```

---

**ระบบพร้อมใช้งาน — ล็อคสถานะเรียบร้อย!** 🚀

**Minis = Command Center**
**Team = Autonomous Workers**
**No Overlapping — Clear Responsibilities**
