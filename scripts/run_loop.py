#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""三省六部 · 跨平台数据刷新循环

用法:
  python scripts/run_loop.py [间隔秒数] [巡检间隔秒数]

参数:
  间隔秒数: 数据刷新频率，默认 15 秒
  巡检间隔秒数: 自动重试卡住任务的频率，默认 120 秒
"""
from __future__ import annotations

import atexit
import os
import signal
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
INTERVAL = int(sys.argv[1]) if len(sys.argv) > 1 else 15
SCAN_INTERVAL = int(sys.argv[2]) if len(sys.argv) > 2 else 120
SCRIPT_TIMEOUT = 30
MAX_LOG_SIZE = 10 * 1024 * 1024  # 10MB

RUNTIME_DIR = Path(tempfile.gettempdir())
LOG = RUNTIME_DIR / "sansheng_liubu_refresh.log"
PIDFILE = RUNTIME_DIR / "sansheng_liubu_refresh.pid"

SCRIPTS = [
    "sync_from_openclaw_runtime.py",
    "sync_agent_config.py",
    "apply_model_changes.py",
    "sync_officials_stats.py",
    "refresh_live_data.py",
]


def console(message: str) -> None:
    print(message, flush=True)


def log_line(message: str, also_console: bool = False) -> None:
    timestamp = time.strftime("%H:%M:%S")
    line = f"{timestamp} [loop] {message}"
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
    if also_console:
        console(line)


def rotate_log() -> None:
    if LOG.exists() and LOG.stat().st_size > MAX_LOG_SIZE:
        backup = LOG.with_suffix(LOG.suffix + ".1")
        if backup.exists():
            backup.unlink()
        LOG.replace(backup)
        with LOG.open("w", encoding="utf-8") as f:
            f.write(f"{time.strftime('%H:%M:%S')} [loop] 日志已轮转\n")


def cleanup(*_args: object) -> None:
    try:
        log_line("收到退出信号，清理中...", also_console=True)
    except Exception:
        pass
    try:
        if PIDFILE.exists():
            PIDFILE.unlink()
    finally:
        raise SystemExit(0)


def pid_exists_windows(pid: int) -> bool:
    result = subprocess.run(
        ["tasklist", "/FI", f"PID eq {pid}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        encoding="utf-8",
        check=False,
    )
    return str(pid) in result.stdout


def ensure_single_instance() -> None:
    if PIDFILE.exists():
        try:
            old_pid = int(PIDFILE.read_text(encoding="utf-8").strip())
        except Exception:
            old_pid = None

        if old_pid:
            try:
                running = pid_exists_windows(old_pid) if os.name == "nt" else True
                if os.name != "nt":
                    os.kill(old_pid, 0)
                if running:
                    console(f"❌ 已有实例运行中 (PID={old_pid})，退出")
                    raise SystemExit(1)
            except OSError:
                pass

        try:
            PIDFILE.unlink()
        except Exception:
            pass

    PIDFILE.write_text(str(os.getpid()), encoding="utf-8")


def safe_run(script_name: str) -> None:
    script_path = SCRIPT_DIR / script_name
    if not script_path.exists():
        log_line(f"⚠️ 缺少脚本: {script_path}", also_console=True)
        return

    cmd = [sys.executable, str(script_path)]
    log_line(f"开始执行: {script_path.name}", also_console=True)
    try:
        result = subprocess.run(
            cmd,
            cwd=str(SCRIPT_DIR.parent),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            timeout=SCRIPT_TIMEOUT,
            check=False,
        )
        if result.stdout:
            with LOG.open("a", encoding="utf-8") as f:
                f.write(result.stdout)
        if result.returncode != 0:
            log_line(f"⚠️ 脚本返回非零退出码({result.returncode}): {script_path.name}", also_console=True)
        else:
            log_line(f"完成执行: {script_path.name}")
    except subprocess.TimeoutExpired as e:
        if e.stdout:
            timeout_output = e.stdout.decode("utf-8", errors="replace") if isinstance(e.stdout, (bytes, bytearray)) else str(e.stdout)
            with LOG.open("a", encoding="utf-8") as f:
                f.write(timeout_output)
        log_line(f"⚠️ 脚本超时({SCRIPT_TIMEOUT}s): {script_path.name}", also_console=True)
    except Exception as e:
        log_line(f"⚠️ 执行失败 {script_path.name}: {e}", also_console=True)


def scheduler_scan() -> None:
    req = urllib.request.Request(
        "http://127.0.0.1:7891/api/scheduler-scan",
        data=b'{"thresholdSec":180}',
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            if body:
                with LOG.open("a", encoding="utf-8") as f:
                    f.write(body + "\n")
        log_line("完成 scheduler-scan")
    except Exception as e:
        log_line(f"scheduler-scan 调用失败: {e}", also_console=True)


def main() -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    LOG.touch(exist_ok=True)
    ensure_single_instance()
    atexit.register(lambda: PIDFILE.exists() and PIDFILE.unlink())

    if hasattr(signal, "SIGINT"):
        signal.signal(signal.SIGINT, cleanup)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, cleanup)

    console(f"🏛️  三省六部数据刷新循环启动 (PID={os.getpid()})")
    console(f"   脚本目录: {SCRIPT_DIR}")
    console(f"   间隔: {INTERVAL}s")
    console(f"   巡检间隔: {SCAN_INTERVAL}s")
    console(f"   脚本超时: {SCRIPT_TIMEOUT}s")
    console(f"   日志: {LOG}")
    console(f"   PID文件: {PIDFILE}")
    console("   按 Ctrl+C 停止")

    log_line("刷新循环已启动")

    scan_counter = 0
    while True:
        rotate_log()
        for script in SCRIPTS:
            safe_run(script)

        scan_counter += INTERVAL
        if scan_counter >= SCAN_INTERVAL:
            scan_counter = 0
            scheduler_scan()

        time.sleep(INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:
        console(f"❌ run_loop.py 启动失败: {e}")
        try:
            log_line(f"启动失败: {e}", also_console=False)
        except Exception:
            pass
        raise
