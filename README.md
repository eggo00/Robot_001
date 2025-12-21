# Line Echo Bot

這是一個簡單的 Line Echo Bot，會將使用者傳送的訊息原封不動地回傳。

## 功能

- 接收使用者訊息
- 將訊息原封不動回傳（Echo）

## 環境需求

- Python 3.9+
- UV 套件管理工具

## 安裝步驟

1. 複製 `.env.example` 為 `.env` 並填入你的 Line Bot 憑證：

```bash
cp .env.example .env
```

2. 編輯 `.env` 檔案，填入你的 Channel Access Token 和 Channel Secret：

```
CHANNEL_ACCESS_TOKEN=your_actual_channel_access_token
CHANNEL_SECRET=your_actual_channel_secret
```

3. 安裝依賴套件（如果尚未安裝）：

```bash
uv sync
```

## 如何取得 Line Bot 憑證

1. 前往 [Line Developers Console](https://developers.line.biz/console/)
2. 建立 Provider（如果還沒有）
3. 建立 Messaging API Channel
4. 在 Channel 設定頁面中找到：
   - Channel Secret（在 Basic settings 頁籤）
   - Channel Access Token（在 Messaging API 頁籤，需要先 Issue）

## 執行方式

```bash
uv run main.py
```

伺服器會在 `http://localhost:5000` 啟動。

## 設定 Webhook URL

1. 使用 ngrok 或其他工具將本地伺服器公開到網路：

```bash
ngrok http 5000
```

2. 將 ngrok 提供的 HTTPS URL 加上 `/callback` 設定到 Line Developers Console 的 Webhook URL
   - 例如：`https://your-ngrok-url.ngrok.io/callback`

3. 啟用 Webhook 並關閉自動回應訊息

## 專案結構

```
.
├── main.py              # 主程式
├── pyproject.toml       # UV 專案設定檔
├── .env.example         # 環境變數範例檔
├── .env                 # 環境變數檔（需自行建立）
└── README.md            # 說明文件
```

## 使用的套件

- `line-bot-sdk`: Line Bot SDK for Python
- `flask`: Web 框架
- `python-dotenv`: 環境變數管理
