#!/bin/bash
# ============================================
# Cookbook 一键停服务
# ============================================

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

stopped=0
for port in 5000 10086; do
  pids=$(lsof -ti:$port 2>/dev/null)
  if [ -n "$pids" ]; then
    kill -9 $pids 2>/dev/null
    echo -e "${GREEN}✓${NC} 端口 $port 已清理 (PID: $pids)"
    stopped=1
  fi
done

if [ $stopped -eq 0 ]; then
  echo -e "${RED}没有运行中的服务${NC}"
else
  echo -e "${GREEN}全部停止${NC}"
fi
