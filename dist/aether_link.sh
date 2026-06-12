#!/system/bin/sh
# ============================================================
# AETHER LINK v1.0 — GitHub Bridge for AETHER SHOT
# ใช้: sh aether_link.sh <command>
# ============================================================

set -e

REPO="Ticker27/aether-mind-v3"
BRANCH="master"
GITHUB_API="https://api.github.com/repos/$REPO"

echo "🌐 AETHER LINK — Authenticated to $REPO"
echo ""

case "${1:-help}" in

  # ─── ตรวจสอบสถานะการ Build ───
  status)
    echo "📡 Fetching latest workflow status..."
    curl -s "$GITHUB_API/actions/workflows" | python3 -c "
import json,sys
data = json.load(sys.stdin)
for wf in data.get('workflows', []):
    print(f\"  ─┬─ {wf['name']}\")
    print(f\"  ─┬─ State: {wf['state']}\")
    print(f\"  ─┬─ Path: {wf['path']}\")
    print()
"
    ;;

  # ─── ตรวจสอบผล Build ล่าสุด ───
  check)
    echo "🔍 Checking latest build results..."
    curl -s "$GITHUB_API/actions/runs?per_page=5&status=completed" | python3 -c "
import json,sys
data = json.load(sys.stdin)
for run in data.get('workflow_runs', []):
    conclusion = run.get('conclusion', 'unknown')
    emoji = '✅' if conclusion == 'success' else '❌' if conclusion == 'failure' else '⏳'
    print(f\"  {emoji} {run['name']}: {run['display_title'][:50]}\")
    print(f\"    Branch: {run['head_branch']} | Status: {conclusion}\")
    print(f\"    URL: {run['html_url']}\")
    print()
"
    ;;

  # ─── Trigger Workflow (สั่ง Build) ───
  build)
    echo "🔨 Triggering Android APK Build..."
    curl -s -X POST "$GITHUB_API/actions/workflows/android.yml/dispatches" \
      -H "Accept: application/vnd.github.v3+json" \
      -H "Authorization: Bearer $GITHUB_TOKEN" \
      -d "{\"ref\":\"$BRANCH\"}"
    echo "  ✅ Build triggered! Check in 5-10 minutes."
    echo "  👉 https://github.com/$REPO/actions"
    ;;

  # ─── Trigger Brain (AI Processing) ───
  brain)
    echo "🧠 Triggering Ethereal Brain..."
    echo "    (Requires screenshot_base64 input)"
    echo ""
    if [ -z "$2" ]; then
      echo "❌ Usage: sh aether_link.sh brain <screenshot_base64>"
      exit 1
    fi
    curl -s -X POST "$GITHUB_API/actions/workflows/ethereal_brain.yml/dispatches" \
      -H "Accept: application/vnd.github.v3+json" \
      -H "Authorization: Bearer $GITHUB_TOKEN" \
      -d "{\"ref\":\"$BRANCH\",\"inputs\":{\"screenshot_base64\":\"$2\",\"session_id\":\"$(date +%s)\"}}"
    echo "  ✅ Brain triggered!"
    ;;

  # ─── ดูไฟล์ล่าสุด ───
  files)
    echo "📁 Latest repository files (top-level):"
    curl -s "$GITHUB_API/contents" | python3 -c "
import json,sys
for item in json.load(sys.stdin):
    type_icon = '📁' if item['type'] == 'dir' else '📄'
    print(f\"  {type_icon} {item['name']}\")
"
    ;;

  # ─── Set GitHub Token ───
  token)
    if [ -z "$2" ]; then
      echo "❌ Usage: sh aether_link.sh token <your_github_token>"
      echo "   Token can be created at: https://github.com/settings/tokens"
      exit 1
    fi
    echo "export GITHUB_TOKEN=$2" > /tmp/.aether_token.sh
    echo "✅ Token saved for this session"
    ;;

  # ─── Auto-Fix & Push (ใช้กับ Bot ใน GitHub) ───
  push)
    echo "📤 Committing all changes and pushing..."
    if [ -d "/var/minis/workspace/aether-mind-v3" ]; then
      cd /var/minis/workspace/aether-mind-v3
      git add -A
      git commit -m "auto: update from AETHER LINK [$(date +%H:%M)]" || true
      git push 2>&1
      echo "  ✅ Pushed! Bot in GitHub will now audit."
    else
      echo "❌ Workspace not found. Run from Termux."
    fi
    ;;

  # ─── Help ───
  help|*)
    echo "╔══════════════════════════════════════════════════╗"
    echo "║         AETHER LINK — Command Reference         ║"
    echo "╚══════════════════════════════════════════════════╝"
    echo ""
    echo "  sh aether_link.sh status     — ดูสถานะ Workflow"
    echo "  sh aether_link.sh check      — ดูผล Build ล่าสุด"
    echo "  sh aether_link.sh build      — สั่ง Build APK"
    echo "  sh aether_link.sh brain <b64> — สั่ง AI Brain"
    echo "  sh aether_link.sh files      — ดูไฟล์ใน Repo"
    echo "  sh aether_link.sh token <t>  — ตั้งค่า GitHub Token"
    echo "  sh aether_link.sh push       — Push โค้ดขึ้น Repo"
    echo ""
    echo "  🔑 ต้องตั้ง Token ก่อน: sh aether_link.sh token <PAT>"
    echo "     Token: https://github.com/settings/tokens"
    echo "     ต้องมี permission: repo, workflow"
    ;;
esac