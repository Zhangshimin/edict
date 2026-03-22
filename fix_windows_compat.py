#!/usr/bin/env python3
"""
Windows 兼容性修复脚本
修复 edict 项目在 Windows 上的兼容性问题
"""
import re
import pathlib
import json
import sys

BASE = pathlib.Path(__file__).parent
SCRIPTS = BASE / 'scripts'
DASHBOARD = BASE / 'dashboard'
DATA = BASE / 'data'

def fix_python3_calls():
    """将 python3 调用替换为 sys.executable (Windows 兼容)"""
    files_to_fix = [
        DASHBOARD / 'server.py',
        SCRIPTS / 'kanban_update.py',
        SCRIPTS / 'fetch_morning_news.py',
    ]
    
    for filepath in files_to_fix:
        if not filepath.exists():
            print(f"Skip (not found): {filepath}")
            continue
        
        content = filepath.read_text(encoding='utf-8')
        original = content
        
        # 替换 'python3' 或 "python3" 为 sys.executable
        # 但要先确保文件导入了 sys
        if "import sys" not in content:
            # 在第一个 import 后添加 sys
            content = content.replace('import json', 'import json, sys')
        
        # 替换 subprocess 调用中的 python3
        content = re.sub(r"(\s)['\"]python3['\"]", r"\1sys.executable", content)
        
        if content != original:
            filepath.write_text(content, encoding='utf-8')
            print(f"✅ Fixed: {filepath.name}")
        else:
            print(f"⚠️  No changes: {filepath.name}")


def fix_dispatch_channel():
    """修复 dispatchChannel 配置为 sharecrm"""
    config_file = DATA / 'agent_config.json'
    if not config_file.exists():
        print(f"❌ Config not found: {config_file}")
        return
    
    with open(config_file, 'r', encoding='utf-8') as f:
        cfg = json.load(f)
    
    if cfg.get('dispatchChannel') != 'sharecrm':
        cfg['dispatchChannel'] = 'sharecrm'
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
        print("✅ Updated dispatchChannel to 'sharecrm'")
    else:
        print("⚠️  dispatchChannel already set to 'sharecrm'")


def fix_dashboard_html():
    """修复 dashboard.html 中的硬编码"""
    html_file = DASHBOARD / 'dashboard.html'
    if not html_file.exists():
        print(f"❌ HTML not found: {html_file}")
        return
    
    content = html_file.read_text(encoding='utf-8')
    original = content
    
    # 替换飞书硬编码为通用文案
    content = content.replace('飞书', '消息')
    content = content.replace('飞书下旨', '发布任务')
    
    if content != original:
        html_file.write_text(content, encoding='utf-8')
        print("✅ Fixed: dashboard.html")
    else:
        print("⚠️  No changes: dashboard.html")


def main():
    import sys
    # 设置控制台编码为 UTF-8
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
    
    print("[FIX] Windows 兼容性修复工具\n")
    
    print("[1] 修复 python3 调用...")
    fix_python3_calls()
    
    print("\n[2] 修复 dispatchChannel 配置...")
    fix_dispatch_channel()
    
    print("\n[3] 修复 dashboard.html 硬编码...")
    fix_dashboard_html()
    
    print("\n[OK] 修复完成！请重启看板服务器。")


if __name__ == '__main__':
    main()
