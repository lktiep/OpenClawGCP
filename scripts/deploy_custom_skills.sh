#!/bin/bash
# Deploy custom skills from GitHub into OpenClaw container
# Run this after container recreation: docker compose up -d
# Usage: ./deploy_custom_skills.sh

CONTAINER="openclaw-openclaw-gateway-1"
REPO_URL="https://raw.githubusercontent.com/lktiep/OpenClawGCP/main"

SKILLS=(
  "skills/mcp-client/SKILL.md"
  "skills/mcp-client/servers.json"
  "skills/mcp-client/scripts/mcp_call.py"
  "skills/r2-upload/SKILL.md"
  "skills/r2-upload/scripts/upload.py"
  "skills/imgur-upload/SKILL.md"
  "skills/imgur-upload/scripts/upload.py"
)

echo "🔌 Deploying custom skills into $CONTAINER..."

for skill in "${SKILLS[@]}"; do
  dir=$(dirname "/app/$skill")
  docker exec "$CONTAINER" mkdir -p "$dir" 2>/dev/null
  curl -sL "$REPO_URL/$skill" | docker exec -i "$CONTAINER" bash -c "cat > /app/$skill"
  echo "  ✅ $skill"
done

echo "🎉 Done! All custom skills deployed."
