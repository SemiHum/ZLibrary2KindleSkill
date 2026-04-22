# ZLibrary2KindleSkill

搜索 Z-Library 书籍并发送到你的 Kindle。支持 CLI 和 Claude Code MCP 模式。

**功能：**
- 按书名、作者、ISBN 搜索 Z-Library
- 下载书籍（优先 EPUB，备选 PDF）
- 直接发送到 Kindle 邮箱
- Session cookies 持久化 — 登录一次，自动复用
- 支持两步验证的应用密码

> **语言**: [English](./README.md) | 中文

## 前置要求

- **ZLibrary 账号** — 邮箱和密码
- **Kindle 邮箱白名单** — 在 Amazon 账户设置中添加发件人
- **Gmail 应用密码** — Gmail 开启两步验证后必填

## 安装

### 1. 安装

**最简单的方式 — 无需安装：**
```bash
uvx zlibrary2kindle --help
```

**或者本地安装：**
```bash
pip install zlibrary2kindle
z2k --help
```

### 2. 配置凭证

**方法一 — `~/.zshrc`（推荐）**

在 `~/.zshrc` 中添加：

```bash
export ZLIBRARY_EMAIL="your@email.com"
export ZLIBRARY_PASSWORD="your-password"
export KINDLE_EMAIL="your-name@kindle.com"
export SENDER_EMAIL="your@email.com"
export SENDER_PASSWORD="xxxx xxxx xxxx xxxx"  # Gmail 应用密码
```

然后运行 `source ~/.zshrc`。

**方法二 — `mcp.json` env**

编辑 `mcp.json`，在 `env` 块中填写凭证。

> **安全提示**：方法一把凭证放在项目目录外，更安全。方法二将凭证明文存储在项目中。

## 步骤指南

- [Beginner Guide (English)](./SOP.md)
- [中文傻瓜指南](./SOP_CN.md)

## 快速开始

```bash
# 1. 登录（一次即可）
uvx zlibrary2kindle login

# 2. 搜索
uvx zlibrary2kindle search "莫言"

# 3. 下载（从搜索结果复制 book_id）
uvx zlibrary2kindle download <book_id>

# 4. 发送到 Kindle
uvx zlibrary2kindle send /tmp/zlibrary2kindle/downloads/书名.epub "书名"
```

本地安装后也可以用：
```bash
z2k login
z2k search "莫言"
z2k download <book_id>
z2k send /path/to/book.epub "书名"
```

## CLI 命令参考

| 命令 | 说明 |
|------|------|
| `uvx zlibrary2kindle login` | 登录 ZLibrary，Session 自动保存 |
| `uvx zlibrary2kindle search "关键词" --limit 10` | 搜索书籍，返回 `[book_id] 书名 \| 作者` |
| `uvx zlibrary2kindle download <book_id>` | 下载书籍到 `/tmp/zlibrary2kindle/downloads/` |
| `uvx zlibrary2kindle send <文件路径> "书名"` | 将文件发送到 Kindle |

## MCP 集成

加载为本地 MCP 服务器，让 AI 帮你搜书、下载、发书。支持 Claude Code、Cursor、OpenClaw。

### Claude Code

```json
// mcp.json
{
  "mcpServers": {
    "zlibrary2kindle": {
      "command": "uvx",
      "args": ["zlibrary2kindle"]
    }
  }
}
```

### Cursor

```json
// ~/.cursor/mcp.json (全局) 或 .cursor/mcp.json (项目内)
{
  "mcpServers": {
    "zlibrary2kindle": {
      "command": "uvx",
      "args": ["zlibrary2kindle"]
    }
  }
}
```

### OpenClaw

```json
// ~/.openclaw/mcp_servers.json
{
  "mcpServers": {
    "zlibrary2kindle": {
      "command": "uvx",
      "args": ["zlibrary2kindle"]
    }
  }
}
```

然后直接对 AI 说：

```
帮我下载莫言的书发送到Kindle
Search for books by 余华 and send them to my Kindle
```

AI 会自动调用 `zlibrary_login`、`zlibrary_search`、`zlibrary_download`、`kindle_send_email` 四个工具完成任务。

## 项目结构

```
src/
├── mcp_tools/          # MCP 工具定义
│   ├── zlibrary_login.py
│   ├── zlibrary_search.py
│   ├── zlibrary_download.py
│   └── kindle_send_email.py
├── services/           # 业务逻辑
│   ├── playwright_service.py    # 浏览器生命周期
│   ├── zlibrary_service.py      # ZLibrary 操作
│   └── email_service.py        # SMTP 发送
├── server.py           # MCP 服务入口
└── cli.py             # CLI 入口
```

## 常见问题

**"Session 过期"或下载失败**
: 运行 `uvx zlibrary2kindle login` 重新刷新 session cookies。

**登录页面改了 / Cloudflare 验证**
: 运行 `uvx zlibrary2kindle login --no-headless` 打开浏览器手动解决验证码。

**邮件发送失败，文件太大**
: Google/Gmail 限制附件 ~25MB，PDF 经常超标。尝试搜索 EPUB 版本。

**PDF 中文在 Kindle 上显示乱码**
: EPUB 格式中文支持更好，尽量下载 EPUB 版本。
