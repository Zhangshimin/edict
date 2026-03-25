#!/bin/bash
# 太子任务检查脚本 - 定期检查已完成任务并回传

KANBAN_FILE="/root/.openclaw/workspace-taizi/data/tasks_source.json"
LAST_CHECK_FILE="/tmp/taizi_last_check.txt"

# 获取上次检查时间
if [ -f "$LAST_CHECK_FILE" ]; then
    LAST_TIME=$(cat "$LAST_CHECK_FILE")
else
    LAST_TIME="0"
fi

NOW=$(date +%s)

# 查找新完成的任务（JJC开头，state=Done，且flow_log最后一条是给皇上的）
python3 << PYEOF
import json

with open("$KANBAN_FILE") as f:
    tasks = json.load(f)

for t in tasks:
    if not t.get("id", "").startswith("JJC-"):
        continue
    if t.get("state") != "Done":
        continue
    
    flow_log = t.get("flow_log", [])
    if not flow_log:
        continue
    
    # 检查是否已经回传过
    last_flow = flow_log[-1]
    if last_flow.get("to") == "太子" and "回传" in last_flow.get("remark", ""):
        continue  # 已回传
    
    # 检查是否是尚书省完成的任务
    if last_flow.get("from") in ["尚书省", "六部"] and last_flow.get("to") == "尚书省":
        # 输出任务信息
        print(f"ID: {t.get('id')}")
        print(f"Title: {t.get('title')}")
        print(f"Output: {t.get('output', '')[:200]}")
        print(f"Summary: {last_flow.get('remark', '')}")
        print("---")
PYEOF

# 更新检查时间
echo "$NOW" > "$LAST_CHECK_FILE"
