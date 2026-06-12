# 📋 AETHER WORKFLOW — Skill Document

**ระบบการโยนงานและแบ่งหน้าที่ ฉบับสมบูรณ์**

---

## 👑 สายการบังคับบัญชา (Chain of Command)

```
[ผู้บัญชาการ]
    │
    ├── สั่งงาน → [AI: THE ARCHITECT]   ← ผม
    │                │
    │                ├── ออกแบบระบบ
    │                ├── เขียนโค้ดทั้งหมด
    │                └── Push → GitHub
    │
    └── ตรวจสอบ → [Bot: THE INSPECTOR]  ← GitHub Copilot
                     │
                     ├── Syntax ถูกไหม?
                     ├── Build ได้ไหม?
                     └── ตอบ: PASS หรือ FAIL
```

## 🎯 การแบ่งหน้าที่ (Role Assignment)

### 🧠 AI (The Architect) — ผม
| หน้าที่ | รายละเอียด |
|--------|-----------|
| ออกแบบ | วางสถาปัตยกรรม, กำหนดโครงสร้าง |
| สร้าง | เขียนโค้ดทุกบรรทัด |
| แก้ไข | แก้ / เพิ่ม / ลบ โค้ด |
| Push | ส่งโค้ดขึ้น GitHub |
| รายงาน | สรุปสิ่งที่ทำ, แจ้งผู้บัญชาการ |

### 🤖 Bot (The Inspector) — GitHub Copilot
| หน้าที่ | รายละเอียด |
|--------|-----------|
| Syntax Check | ถูกต้องตามภาษา (Java, Python, XML, YAML) |
| Dependency Check | imports, libraries, classpath ครบ |
| Build Check | Gradle compile ได้? |
| ตอบกลับ | PASS หรือ FAIL + Error |

### 👤 ผู้บัญชาการ (The Commander) — คุณ
| หน้าที่ | รายละเอียด |
|--------|-----------|
| สั่งการ | กำหนดภารกิจ, เปลี่ยนแผน |
| ส่ง Audit | เอาคำสั่งไปให้ Bot |
| แจ้งผล | บอกผมว่า Bot ตอบอะไร |
| สั่ง Build | รัน GitHub Actions → APK |

## 🔄 Workflow มาตรฐาน

### Step 1: ผมออกแบบ + เขียนโค้ด
```
สั่งงาน → ผม → file_read → file_write → file_edit → git push
```

### Step 2: ส่งให้ Bot ตรวจสอบ
```
ผู้บัญชาการ → ส่ง Prompt → Bot → Audit → PASS/FAIL
```

### Step 3: ถ้า FAIL → แก้ไข
```
ผู้บัญชาการ → แจ้ง Error → ผม → git push อีกครั้ง
```

### Step 4: ถ้า PASS → Build
```
ผู้บัญชาการ → Run Workflow → GitHub Actions → APK
```

## 📝 คำสั่ง Audit (Template)
```
"Audit aether-mind-v3. Check only:
1. Syntax errors? YES/NO
2. Missing imports/files? YES/NO
3. Gradle build ready? PASS/FAIL
If FAIL, list ONLY the blocking errors."
```

## 🚀 คติประจำใจ
> **"ผมทำทุกอย่างให้เสร็จในครั้งเดียว — Bot แค่ตรวจว่าเสร็จจริง"**
> **"No back-and-forth. No iteration. One shot."**
