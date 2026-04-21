# ZLibrary2Kindle 傻瓜式操作指南

即使你完全不懂技术，只要跟着下面的步骤做，就能把书发送到 Kindle。

---

## 第一步：准备工作（只需要做一次）

### 1.1 你需要准备

- 一个 ZLibrary 账号（免费注册：https://zh.zlib.li/ ）
- 一个美国/日本/香港的Kindle，或者Kindle App
- 一个Gmail邮箱（用来发送邮件到Kindle）

### 1.2 设置Kindle接收邮箱

> 这一步只需要做一次，之后都可以直接发送。

1. 打开 Amazon 官网，登录你的账号
2. 进入「管理内容和设备」→「首选项」
3. 找到「已认可的发件人电子邮箱列表」，把你的 Gmail 加进去
4. 记住你的 Kindle 邮箱，格式类似：`你的名字@kindle.com`

### 1.3 获取Gmail应用密码

> 如果你的Gmail开启了两步验证，就必须用应用密码。

1. Gmail → 右上角设置 → 查看所有设置 → 转至「账户」页面
2. 安全 → 应用密码 → 生成
3. 选择「邮件」和「Mac」，生成16位密码（格式：`xxxx xxxx xxxx xxxx`）
4. 复制这个密码，后面会用到

### 1.4 安装Python（如果提示找不到python）

Mac自带Python，但最好用最新版本：

```bash
# 打开「终端」，运行：
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
brew install python
```

### 1.5 安装软件

打开终端，运行：

```bash
# 进入项目目录
cd /Users/你的用户名/Git/SemiHum/ZLibrary2KindleSkill

# 安装依赖
pip install -e .
```

---

## 第二步：配置（只需要做一次）

### 2.1 配置环境变量

打开终端，运行：

```bash
# 编辑 ~/.zshrc
nano ~/.zshrc
```

按 `Ctrl+V` 跳到文件最底部，粘贴以下内容（把里面的邮箱密码替换成你自己的）：

```bash
export ZLIBRARY_EMAIL="你的ZLibrary邮箱"
export ZLIBRARY_PASSWORD="你的ZLibrary密码"
export KINDLE_EMAIL="你的Kindle邮箱"
export SENDER_EMAIL="你的Gmail邮箱"
export SENDER_PASSWORD="刚刚生成的应用密码"
```

按 `Ctrl+O` 保存，`Ctrl+X` 退出。

然后运行：
```bash
source ~/.zshrc
```

### 2.2 验证配置

运行：
```bash
python -m src.cli login
```

如果看到「Logged in successfully」就成功了！

---

## 第三步：找书、下载、发送到Kindle（每次重复）

### 3.1 搜索书籍

```bash
python -m src.cli search "书名或作者名"
```

例如搜索「三国演义」：
```bash
python -m src.cli search "三国演义"
```

会看到类似这样的结果：
```
[abc123XYZ] 三国演义 | 罗贯中
[def456UVW] 三国演义（精装版） | 罗贯中
```

方括号里的就是书的ID，复制下来。

### 3.2 下载书籍

```bash
python -m src.cli download 刚才复制的ID
```

例如：
```bash
python -m src.cli download abc123XYZ
```

下载完成后会显示保存路径，类似：
```
Downloaded: /tmp/zlibrary2kindle/downloads/三国演义.epub
```

### 3.3 发送到Kindle

```bash
python -m src.cli send 下载路径 "书名"
```

例如：
```bash
python -m src.cli send "/tmp/zlibrary2kindle/downloads/三国演义.epub" "三国演义"
```

看到「Sent successfully」就成功了！几分钟后书就会出现在你的Kindle上。

---

## 常见问题

### Q: 提示「command not found: python」
A: 试试用 `python3` 代替 `python`

### Q: 提示「No module named src」
A: 确保在项目目录下运行，或者用 `python -m src.cli`

### Q: 下载失败，提示超时
A: ZLibrary可能抽风，等几分钟再试。或者试试非headless模式：
```bash
python -m src.cli login --no-headless
```

### Q: 邮件发送失败，提示文件太大
A: PDF文件通常太大。换个EPUB版本试试，或者搜「书名 epub」

### Q: 中文在Kindle上显示乱码
A: EPUB格式中文支持更好。搜索时尽量选EPUB版本。

### Q: 每次都要输入密码很麻烦？
A: 第一次登录后，Session会保存，之后不需要再登录。
