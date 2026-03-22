# 🪟 Windows 使用说明

> 适用于在 Windows 上运行 edict / 三省六部。

---

## 1. 前置要求

请先确认以下工具已安装：

- [OpenClaw](https://openclaw.ai)
- Python 3.9+
- Git
- （可选）Node.js 18+，用于本地重新构建前端

安装 OpenClaw 后先初始化：

```powershell
openclaw init
```

---

## 2. 克隆仓库

```powershell
git clone https://github.com/Zhangshimin/edict.git
cd edict
```

如果你使用的是自己的 fork，也可以替换成你自己的仓库地址。

---

## 3. Windows 下安装

Windows 不要使用 `install.sh`，请使用 PowerShell 版本：

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

安装脚本会自动完成：

- 创建各个 Agent 的 workspace
- 写入 `SOUL.md` / `AGENTS.md`
- 注册 Agent 到 `openclaw.json`
- 初始化数据目录
- 执行首次同步
- 尝试重启 Gateway

> 如果你刚配置完 API Key，建议再重新执行一次 `install.ps1`，让配置同步到所有 Agent。

---

## 4. 配置 API Key

如果尚未配置模型 Key，可先执行：

```powershell
openclaw agents add taizi
```

按提示输入你的模型提供商 API Key。

然后再执行一次：

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

---

## 5. Windows 下启动服务

### 5.1 启动数据刷新循环

项目已提供跨平台版本：

```powershell
python scripts/run_loop.py
```

可选参数：

```powershell
python scripts/run_loop.py 15 120
```

含义：

- 第一个参数：刷新间隔秒数（默认 15）
- 第二个参数：巡检间隔秒数（默认 120）

### 5.2 启动看板服务器

```powershell
python dashboard/server.py
```

### 5.3 打开看板

浏览器访问：

```text
http://127.0.0.1:7891
```

---

## 6. 推荐启动方式

建议开两个终端窗口：

### 窗口 1：刷新循环

```powershell
cd D:\tools\edict
python scripts/run_loop.py
```

### 窗口 2：看板服务

```powershell
cd D:\tools\edict
python dashboard/server.py
```

---

## 7. 后台运行（可选）

### 后台启动刷新循环

```powershell
Start-Process python -ArgumentList 'scripts/run_loop.py' -WorkingDirectory 'D:\tools\edict'
```

### 后台启动看板服务

```powershell
Start-Process python -ArgumentList 'dashboard/server.py' -WorkingDirectory 'D:\tools\edict'
```

---

## 8. 常见问题

### Q1：为什么不能直接用 `run_loop.sh`？

因为 `run_loop.sh` 是 Bash 脚本，主要面向 macOS / Linux。

Windows 下请改用：

```powershell
python scripts/run_loop.py
```

### Q2：`SOUL.md` 显示乱码怎么办？

请先重新执行：

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

如果仍有乱码，通常说明 `agents/*/SOUL.md` 源模板本身需要进一步修复，而不只是写入编码问题。

### Q3：看板没数据怎么办？

先确认这两个进程都在运行：

1. `python scripts/run_loop.py`
2. `python dashboard/server.py`

然后再检查 Gateway：

```powershell
openclaw gateway status
```

### Q4：Agent 不响应怎么办？

```powershell
openclaw gateway restart
```

必要时重新执行一次安装脚本：

```powershell
powershell -ExecutionPolicy Bypass -File .\install.ps1
```

---

## 9. 建议

如果你长期在 Windows 上维护这个项目，建议优先使用：

- `install.ps1`
- `scripts/run_loop.py`
- `python dashboard/server.py`

也就是说，把原来的 Unix 启动方式：

- `./install.sh`
- `bash scripts/run_loop.sh`

替换成 Windows 友好的这套命令。
