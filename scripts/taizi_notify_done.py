#!/usr/bin/env python3
"""太子任务回传检查脚本 - 检测尚书省完成的任务并通知用户"""
import json
import os
import sys

KANBAN_FILE = "/root/.openclaw/workspace-taizi/data/tasks_source.json"
LAST_FILE = "/tmp/taizi_notify_done_last.txt"

def load_last_check():
    if os.path.exists(LAST_FILE):
        with open(LAST_FILE) as f:
            return set(json.load(f))
    return set()

def save_last_check(ids):
    with open(LAST_FILE, 'w') as f:
        json.dump(list(ids), f)

def check_and_notify():
    last_ids = load_last_check()
    current_ids = set()
    new_notifications = []
    
    with open(KANBAN_FILE) as f:
        tasks = json.load(f)
    
    for t in tasks:
        tid = t.get('id', '')
        if not tid.startswith('JJC-'):
            continue
        
        current_ids.add(tid)
        
        # 检查是否是刚完成的任务
        if t.get('state') != 'Done':
            continue
        
        if tid in last_ids:
            continue
        
        flow_log = t.get('flow_log', [])
        if not flow_log:
            continue
        
        # 找最后一条给皇上的记录
        for f in reversed(flow_log):
            if f.get('to') == '皇上' and f.get('from') in ['尚书省', '六部']:
                title = t.get('title', '')
                remark = f.get('remark', '')
                output = t.get('output', '')[:150]
                new_notifications.append({
                    'id': tid,
                    'title': title,
                    'remark': remark,
                    'output': output
                })
                break
    
    save_last_check(current_ids)
    return new_notifications

if __name__ == '__main__':
    notifications = check_and_notify()
    for n in notifications:
        print(f"✅ {n['id']}: {n['title']}")
        print(f"   {n['remark']}")
        if n['output']:
            print(f"   输出: {n['output']}")
        print()
    
    if notifications:
        sys.exit(0)  # 有新通知
    sys.exit(1)  # 无新通知
