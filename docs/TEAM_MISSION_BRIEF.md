# 🎯 AETHER MIND — Mission Brief for AI Team

## สถานะปัจจุบัน (Commander Report)

**Command Center:** Minis App (Android)
**สถานะ:** พร้อมสั่งการ — รอทีมเริ่มทำงาน

---

## 📋 Mission: AETHER MIND v3.0

### เป้าหมายสูงสุด
สร้าง AI system ที่มี:
1. **Learning AI** — เรียนรู้ได้เองจาก gameplay
2. **Zero-Trace** — ไม่มีร่องรอย ตรวจจับไม่ได้
3. **Frame Precognition** — ทำนายฟิสิกส์ก่อนเกมจะ render
4. **Self-Evolving** — พัฒนาตัวเองได้ตลอดเวลา

### 5 Phases ที่ต้องทำ

```
Phase 1: Neural Oracle Core (สมอง AI)
├─ Train model จาก game footage
├─ Predict ball trajectories
└─ Self-learning from gameplay

Phase 2: Physics Engine (กฎฟิสิกส์ใหม่)
├─ Beyond Newtonian physics
├─ Chaos theory + quantum effects
└─ Real-time physics simulation

Phase 3: Frame Capture (จับภาพไร้ร่องรอย)
├─ Zero-copy buffer capture
├─ No memory reading
└─ Invisible to anti-cheat

Phase 4: Stealth Layer (ซ่อนตัวสมบูรณ์)
├─ Polymorphic code
├─ No identifiable patterns
└─ Anti-detection system

Phase 5: Android APK (ตัวติดตั้ง)
├─ Package name ที่ไม่สงสัย
├─ Minimum permissions
└─ Seamless integration
```

---

## 🔑 API Configuration

### DashScope API (Primary)
- **Endpoint:** `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
- **API Key:** (ใส่ใน `config/api_keys.json`)
- **Models Available:** Qwen series, DeepSeek series

### Models ที่แนะนำ
ดู `docs/model_registry.json` สำหรับรายละเอียด

---

## 🛠️ Tools & Resources

### Orchestrator Scripts
```
orchestrator/
├─ dashscope_client.py      # DashScope API client
├─ discover_models.py       # ค้นหาและจัดกลุ่มโมเดล
├─ commander.sh             # Command center interface
├─ model_router.py          # เลือกโมเดลอัตโนมัติ
├─ team_ai.sh               # จัดการ AI team
├─ team_crown.sh            # จัดการ Crown team
└─ voting.sh                # Voting system
```

### Project Structure
```
aether_mind/
├─ android/          # Android APK code
├─ neural/           # AI models & training
├─ physics/          # Physics engine
├─ capture/          # Frame capture
├─ stealth/          # Stealth layer
├─ train_data/       # Training data
├─ docs/             # Documentation
├─ orchestrator/     # Management scripts
└─ config/           # API keys & configs
```

---

## 🎯 Team Responsibilities

### Team AI (Local Agents)
- วางแผน architecture
- ตรวจสอบ code quality
- Review และ debug
- ตัดสินใจทางเทคนิค

### Team Crown (Cloud Agents)
- เขียน code หลัก
- Train AI models
- รัน heavy computations
- Generate documentation

### Commander (You)
- สั่งงานผ่าน Minis app
- ตัดสินใจสำคัญ
- Review ผลลัพธ์
- กำหนด direction

---

## 🚀 Getting Started

### Step 1: ตั้งค่า API Keys
```bash
# แก้ไขไฟล์นี้
nano /var/minis/workspace/aether_mind/config/api_keys.json

# ใส่ API keys:
# - DashScope: sk-...
# - Anthropic: sk-... (optional)
# - OpenAI: sk-... (optional)
```

### Step 2: Discover Models
```bash
cd /var/minis/workspace/aether_mind/orchestrator
python3 discover_models.py
```

จะสร้าง:
- `docs/model_registry.json` — โมเดลทั้งหมด
- `docs/model_recommendations.json` — แนะนำสำหรับแต่ละ phase

### Step 3: เริ่ม Phase 1
```bash
# เลือกโมเดลสำหรับ Neural Oracle
./model_router.py "train neural network for ball trajectory prediction"

# เริ่ม training (ทีม Crown จะทำ)
./team_crown.sh "เริ่ม Phase 1: Neural Oracle Core" --auto
```

---

## 📊 Progress Tracking

### Git Commits
ทุกงานสำคัญต้อง commit:
```bash
git add .
git commit -m "Phase X: Description"
```

### State Tracking
ดู `lock/state.json` สำหรับสถานะปัจจุบัน

---

## ⚠️ Important Notes

1. **Command Center เท่านั้น** — Minis app ใช้สั่งงาน ไม่ใช่ทำงาน
2. **ทีมจัดการเอง** — API calls, training, coding ทำที่อื่น
3. **Zero-Trace** — ต้องไม่มีร่องรอยใน production
4. **Self-Evolving** — AI ต้องพัฒนาตัวเองได้

---

## 🎯 Success Criteria

### Phase 1 Complete เมื่อ:
- ✅ Neural model trained (>95% accuracy)
- ✅ Predict trajectories ใน <10ms
- ✅ Self-learning จาก gameplay

### Phase 2 Complete เมื่อ:
- ✅ Physics engine ทำงาน
- ✅ Beyond Newtonian predictions
- ✅ Real-time simulation

### Phase 3 Complete เมื่อ:
- ✅ Frame capture ไม่มีร่องรอย
- ✅ <5ms latency
- ✅ Invisible to detection

### Phase 4 Complete เมื่อ:
- ✅ Code polymorphic
- ✅ No identifiable patterns
- ✅ Anti-detection active

### Phase 5 Complete เมื่อ:
- ✅ APK install ได้
- ✅ ทำงานได้จริง
- ✅ ไม่ถูกตรวจจับ

---

## 📞 Communication

### Commander → Team
ใช้ Minis app สั่งงาน:
- "เริ่ม Phase X"
- "ใช้โมเดล Y สำหรับงาน Z"
- "ตรวจสอบผลลัพธ์"

### Team → Commander
รายงานผ่าน:
- Git commits
- `lock/state.json` updates
- `docs/` documentation

---

## 🎉 Let's Build The Future!

ทีมพร้อมหรือยัง? ถ้าพร้อม เริ่ม Phase 1 ได้เลย!

**Commander out.** 🚀
