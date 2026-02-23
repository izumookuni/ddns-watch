# DDNS IP 监测工具

一个基于 GitHub Actions 的 DDNS IP 变化监测工具，当域名 IP 发生变化时自动发送邮件通知。

## 功能特点

- 🔄 每小时自动检测域名IP变化
- 🔒 IP地址加密存储，保护隐私安全
- 📧 IP变化时自动发送邮件通知
- ⚡ 支持手动触发执行

## 工作原理

1. 通过 DNS 查询获取域名当前指向的 IP 地址
2. 读取之前存储的 IP 地址（加密存储）
3. 对比两者，如果发生变化：
   - 发送邮件通知到指定邮箱
   - 更新存储的 IP 地址

## 使用方法

### 1. Fork 本仓库

点击右上角 Fork 按钮，将仓库 Fork 到你的账户下。

### 2. 配置 GitHub Secrets

进入你 Fork 的仓库，依次点击 **Settings** → **Secrets and variables** → **Actions** → **New repository secret**，添加以下密钥：

| Secret 名称 | 说明 | 示例 |
|------------|------|------|
| `HOST_NAME` | 需要监测的域名 | `example.ddns.net` |
| `SMTP_URL` | SMTP 服务器地址 | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP 端口 | `587` |
| `SMTP_USER` | SMTP 用户名（邮箱） | `your-email@gmail.com` |
| `SMTP_PASSWORD` | SMTP 密码/应用专用密码 | `your-app-password` |
| `RECEIVE_MAIL` | 接收通知的邮箱 | `receiver@example.com` |
| `SECRET_KEY` | 加密密钥（自定义字符串） | `my-secret-key-123` |

### 3. 移除仓库存在的current_ip文件

删除 `current_ip` 文件，否则程序将无法判断 IP 是否变化。

### 4. 启用 GitHub Actions

进入 **Actions** 标签页，如果提示需要启用，点击 **I understand my workflows, go ahead and enable them**。

### 5. 手动测试（可选）

在 **Actions** 标签页，选择 **DDNS IP Monitor** 工作流，点击 **Run workflow** 可以手动触发一次测试。

## 常用 SMTP 配置

### Gmail

```
SMTP_URL: smtp.gmail.com
SMTP_PORT: 587
```

> 注意：Gmail 需要使用[应用专用密码](https://support.google.com/accounts/answer/185833)，而非账户密码。

### QQ邮箱

```
SMTP_URL: smtp.qq.com
SMTP_PORT: 587
```

> 注意：QQ邮箱需要使用授权码，在邮箱设置中获取。

### 163邮箱

```
SMTP_URL: smtp.163.com
SMTP_PORT: 587
```

> 注意：163邮箱需要使用授权码，在邮箱设置中获取。

### Outlook/Hotmail

```
SMTP_URL: smtp-mail.outlook.com
SMTP_PORT: 587
```

## 文件说明

```
ddns-watch/
├── .github/
│   └── workflows/
│       └── ddns-watch.yml    # GitHub Actions 工作流配置
├── main.py                   # 主程序
├── requirements.txt          # Python 依赖
├── current_ip               # 存储的IP文件（自动生成，加密存储）
└── README.md                # 说明文档
```

## 注意事项

1. **加密密钥**：`SECRET_KEY` 用于加密存储的 IP 地址，请妥善保管，更换密钥后之前存储的 IP 将无法解密。

2. **执行频率**：默认每8小时执行一次，可在 `.github/workflows/ddns-watch.yml` 中修改 `cron` 表达式调整频率。

3. **GitHub Actions 限制**：免费账户每月有 Actions 运行时间限制，本工具每8小时执行一次，每月约执行90次，在免费额度内。

4. **IP 文件提交**：当 IP 变化时，程序会自动提交更新后的 `current_ip` 文件到仓库。

## 故障排查

### Actions 执行失败

1. 检查所有 Secrets 是否正确配置
2. 查看 Actions 日志获取详细错误信息
3. 确认 SMTP 配置正确，特别是端口和密码

### 邮件发送失败

1. 确认 SMTP 服务器地址和端口正确
2. 确认使用的是应用专用密码/授权码（而非登录密码）
3. 检查邮箱是否开启了 SMTP 服务

## License

MIT License
