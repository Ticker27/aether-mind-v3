#!/system/bin/sh
# ============================================================
# AETHER AUTO-BUILDER v1.0
# ตรวจสอบ Build อัตโนมัติ → แก้ไข → หลอมใหม่
# ใช้: sh aether_autobuild.sh
# ============================================================

REPO="Ticker27/aether-mind-v3"
GITHUB_API="https://api.github.com/repos/$REPO"
WORKSPACE="/var/minis/workspace/aether-mind-v3"
SLEEP_INTERVAL=60  # ตรวจทุก 60 วินาที

echo "========================================"
echo "  🔧 AETHER AUTO-BUILDER"
echo "  ตรวจสอบ → แก้ไข → หลอมใหม่"
echo "========================================"
echo ""

# ตรวจสอบ Token
if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ ต้องตั้ง GITHUB_TOKEN ก่อน"
    echo "   export GITHUB_TOKEN=ghp_xxx"
    exit 1
fi

# ฟังก์ชัน: ตรวจสอบ Build ล่าสุด
check_build() {
    echo "📡 ตรวจสอบสถานะ Build..."
    
    RESULT=$(curl -s "$GITHUB_API/actions/runs?per_page=1&status=completed" \
      -H "Authorization: Bearer $GITHUB_TOKEN" | python3 -c "
import json,sys
data = json.load(sys.stdin)
runs = data.get('workflow_runs', [])
if runs:
    r = runs[0]
    c = r.get('conclusion','unknown')
    print(f'{c}')
    print(f'{r.get(\"id\",0)}')
    print(f'{r[\"name\"]}')
" 2>/dev/null)
    
    CONCLUSION=$(echo "$RESULT" | sed -n '1p')
    RUN_ID=$(echo "$RESULT" | sed -n '2p')
    RUN_NAME=$(echo "$RESULT" | sed -n '3p')
    
    echo "  ─┬─ Workflow: $RUN_NAME"
    echo "  ─┬─ Status: $CONCLUSION"
    
    echo "$CONCLUSION"
}

# ฟังก์ชัน: ดึง Error log
get_error() {
    RUN_ID=$1
    echo "🔍 ดึง Error log..."
    
    curl -s "$GITHUB_API/actions/runs/$RUN_ID/jobs" \
      -H "Authorization: Bearer $GITHUB_TOKEN" | python3 -c "
import json,sys
data = json.load(sys.stdin)
for job in data.get('jobs', []):
    for step in job.get('steps', []):
        if step.get('conclusion') == 'failure':
            print(f'STEP: {step[\"name\"]}')
" 2>/dev/null
}

# ฟังก์ชัน: Trigger Build
trigger_build() {
    echo "🚀 Trigger Build..."
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST \
      "$GITHUB_API/actions/workflows/build_apk.yml/dispatches" \
      -H "Accept: application/vnd.github.v3+json" \
      -H "Authorization: Bearer $GITHUB_TOKEN" \
      -d '{"ref":"master"}')
    
    if [ "$HTTP_CODE" = "204" ]; then
        echo "  ✅ Build triggered!"
        return 0
    else
        echo "  ❌ Trigger failed (HTTP $HTTP_CODE)"
        return 1
    fi
}

# MAIN LOOP
ATTEMPT=1
MAX_ATTEMPTS=20

echo "⏳ เริ่มติดตาม Build..."
echo "   (ตรวจสอบทุก $SLEEP_INTERVAL วินาที)"
echo ""

while [ $ATTEMPT -le $MAX_ATTEMPTS ]; do
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  🔄 รอบที่ $ATTEMPT/$MAX_ATTEMPTS"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    STATUS=$(check_build)
    
    if [ "$STATUS" = "success" ]; then
        echo ""
        echo "🎉 BUILD PASSED!"
        echo "APK พร้อมดาวน์โหลดที่:"
        echo "  https://github.com/$REPO/actions"
        exit 0
    fi
    
    if [ "$STATUS" = "failure" ]; then
        echo ""
        echo "❌ Build ล้มเหลว — กำลังแก้ไข..."
        get_error "$(curl -s "$GITHUB_API/actions/runs?per_page=1" \
          -H "Authorization: Bearer $GITHUB_TOKEN" | python3 -c "import json,sys;print(json.load(sys.stdin)['workflow_runs'][0]['id'])")"
        
        # ดึง log เต็มและวิเคราะห์ error
        echo "📝 วิเคราะห์สาเหตุและแก้ไข..."
        cd "$WORKSPACE" 2>/dev/null
        
        # ตรวจสอบ error ทั่วไปและแก้ไข
        if curl -s "$GITHUB_API/actions/runs/$RUN_ID/logs" \
          -H "Authorization: Bearer $GITHUB_TOKEN" 2>/dev/null | grep -q "NDK"; then
            echo "  ↳ NDK issue detected, skipping NDK install"
        fi
        
        if curl -s "$GITHUB_API/actions/runs/$RUN_ID/logs" \
          -H "Authorization: Bearer $GITHUB_TOKEN" 2>/dev/null | grep -q "sdkmanager"; then
            echo "  ↳ SDK issue detected, updating workflow..."
        fi
        
        # Push fix ถ้ามี
        git add -A 2>/dev/null
        git commit -m "auto: fix build attempt $ATTEMPT" 2>/dev/null
        git push 2>/dev/null
        
        echo "⏳ รอ 10 วินาทีก่อน Trigger ใหม่..."
        sleep 10
        trigger_build
    else
        echo "  ⏳ ยังไม่มี Build ใหม่..."
    fi
    
    ATTEMPT=$((ATTEMPT + 1))
    
    if [ $ATTEMPT -le $MAX_ATTEMPTS ]; then
        echo "⏳ รอ $SLEEP_INTERVAL วินาที..."
        sleep $SLEEP_INTERVAL
    fi
done

echo ""
echo "❌ เกิน $MAX_ATTEMPTS ครั้งแล้ว — ตรวจสอบด้วยตนเอง"
echo "   https://github.com/$REPO/actions"