#!/bin/bash
# ============================================
# Cookbook 构建微信小程序
# ============================================

cd "$(cd "$(dirname "$0")" && pwd)"

GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}构建微信小程序...${NC}"
cd web
npm run build:weapp

if [ $? -eq 0 ]; then
  echo ""
  echo -e "${GREEN}✓ 构建成功！${NC}"
  echo -e "  产物目录: ${CYAN}$(pwd)/dist${NC}"
  echo -e "  微信开发者工具 → 导入项目 → 选这个目录"
else
  echo -e "${RED}构建失败${NC}"
  exit 1
fi
