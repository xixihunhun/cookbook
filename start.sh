#!/bin/bash
# ============================================
# Cookbook 一键起服务（Flask + Taro H5）
# ============================================

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

# ---------- 颜色 ----------
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

# ---------- 清端口 ----------
echo -e "${CYAN}清理旧进程...${NC}"
lsof -ti:5000 | xargs kill -9 2>/dev/null && echo -e "  ${RED}5000${NC} 已清理"
lsof -ti:10086 | xargs kill -9 2>/dev/null && echo -e "  ${RED}10086${NC} 已清理"
sleep 1

# ---------- 起 Flask ----------
echo -e "${CYAN}启动 Flask 后端...${NC}"
source venv/bin/activate
python3 run.py > /tmp/flask.log 2>&1 &
FLASK_PID=$!
deactivate 2>/dev/null
echo -e "  ${GREEN}✓${NC} Flask PID=$FLASK_PID  → http://127.0.0.1:5000"

# ---------- 起 Taro H5 ----------
echo -e "${CYAN}启动 Taro H5 前端...${NC}"
cd web && npm run dev:h5 > /tmp/taro.log 2>&1 &
TARO_PID=$!
cd "$ROOT"
echo -e "  ${GREEN}✓${NC} Taro  PID=$TARO_PID  → http://127.0.0.1:10086"

# ---------- 等服务就绪 ----------
echo -e "${CYAN}等待服务就绪...${NC}"
for i in $(seq 1 30); do
  sleep 1
  if curl -s http://127.0.0.1:5000/health > /dev/null 2>&1; then
    break
  fi
done

# ---------- 打印状态 ----------
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Cookbook 服务已启动！${NC}"
echo -e "${GREEN}============================================${NC}"
echo -e "  后端 API:  ${CYAN}http://127.0.0.1:5000${NC}"
echo -e "  H5 前端:   ${CYAN}http://127.0.0.1:10086${NC}"
echo -e "  日志:      ${CYAN}tail -f /tmp/flask.log${NC} 或  ${CYAN}tail -f /tmp/taro.log${NC}"
echo -e "  停止:      ${CYAN}./stop.sh${NC}"
echo -e "============================================"
echo ""

# ---------- 退出时清理 ----------
trap "echo '正在停止...'; kill $FLASK_PID $TARO_PID 2>/dev/null; exit" SIGINT SIGTERM
wait
