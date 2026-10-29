# Windows 使用指南

## 情况 A：学生只用 Windows 打开

不需要安装任何东西：

1. 打开老师给的地址（Tunnel URL，例如 `https://xxxx.trycloudflare.com/`）；
2. 浏览器弹出登录框：
   - 用户名：`理论力学`（若中文不兼容，用 `lilun`）
   - 密码：老师提供的密码
3. 登录后使用「问星」AI 助教。

`https://wck3069.github.io/...` 是公开静态站，没有登录，也没有完整 AI。

## 情况 B：老师在 Windows 上自己跑服务

### 1. 安装 Python

到 python.org 安装 Python 3.11/3.12，安装时勾选 **Add python.exe to PATH**。
不需要 `pip install`，服务端只用标准库。

### 2. 准备环境变量文件

创建目录 `%USERPROFILE%\.config`，新建 `tm-ai.env`（Notepad 保存为 UTF-8）：

```ini
TM_AI_BASE=https://xplt.sdu.edu.cn:4000/v1
TM_AI_MODEL=SDU-AI/DeepSeek-V4-Flash
TM_AI_KEY=<学校网关 key>
TM_AI_EFFORT_FAST=minimal
TM_AI_EFFORT_DEEP=medium
TM_AUTH_USER=理论力学
TM_AUTH_USER_ALT=lilun
TM_AUTH_PASS=<登录密码>
```

- Windows 上没有 Linux 的 Strata，如果不再跑本地模型，加一行 `TM_PIPELINE=school`（学校直答）。
- 想保留“本地起草 + 学校审核”，装 Ollama：
  ```powershell
  winget install Ollama.Ollama
  ollama pull qwen3:8b
  ```
  然后在 env 里加：
  ```ini
  TM_PIPELINE=local_review
  TM_LOCAL_BASE=http://127.0.0.1:11434/v1
  TM_LOCAL_MODEL=qwen3:8b
  TM_LOCAL_KEY=ollama
  ```

### 3. 生成静态站

```powershell
cd <repo>
powershell -NoProfile -ExecutionPolicy Bypass -File tools\export_static.ps1
```

或直接从 Linux 机器把 `dist/` 整个拷过来。

### 4. 启动

```powershell
cd <repo>
powershell -NoProfile -ExecutionPolicy Bypass -File tools\serve.ps1
```

或双击 `tools\serve.cmd`。浏览器打开：

```
http://127.0.0.1:8765/
```

登录：`理论力学` / 你设置的密码。

### 5. 公网（Cloudflare Tunnel）

```powershell
winget install Cloudflare.cloudflared
cloudflared tunnel login
cloudflared tunnel create mechanics-ai
cloudflared tunnel route dns mechanics-ai mechanics.example.com
```

`%USERPROFILE%\.cloudflared\config.yml`：

```yaml
tunnel: <TUNNEL-UUID>
credentials-file: C:\Users\<你>\.cloudflared\<TUNNEL-UUID>.json
ingress:
  - hostname: mechanics.example.com
    service: http://127.0.0.1:8765
  - service: http_status:404
```

```powershell
cloudflared tunnel run mechanics-ai
```

没有域名时，临时用：

```powershell
cloudflared tunnel --url http://127.0.0.1:8765
```

终端会打印 `https://xxxx.trycloudflare.com`；地址每次重启会变。

### 6. 防火墙

- 只在本机用：不用改。
- 局域网学生用：Windows 防火墙放行 Python/8765 的入站 TCP；启动时设 `TM_HOST=0.0.0.0`。
- 用 Cloudflare Tunnel：只需要出站，不需要开 8765 入站。

## 常见问题

- `python` 不是内部命令：重装 Python 并勾选 Add to PATH，或用 `py -3` 代替 `python`。
- 登录框不弹：确认用的是 `http://127.0.0.1:8765/`，不是 `file://`；清浏览器缓存。
- 中文用户名 401：改用 `lilun`。
- AI 503：检查 env 里的 key、`xplt.sdu.edu.cn:4000` 是否可达；看终端日志。
- 页面 404：没有 `dist/`，先跑 `export_static.ps1`。
