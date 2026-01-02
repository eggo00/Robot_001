# Zeabur 部署指引

## 準備工作

### 1. 確認 GitHub Repository

確保你的程式碼已經推送到 GitHub 的 **Private Repository**。

```bash
# 如果還沒有推送，執行以下指令
git add .
git commit -m "準備部署到 Zeabur"
git push origin main
```

**重要：** 確認 `.env` 文件沒有被上傳（已在 `.gitignore` 中）。

---

## Zeabur 部署步驟

### 1. 登入 Zeabur

前往 [https://zeabur.com](https://zeabur.com) 並登入（可使用 GitHub 登入）。

### 2. 建立新專案

1. 點擊「Create Project」
2. 選擇「Deploy from GitHub」
3. 選擇你的 Repository：`Robot_001`

### 3. 設定環境變數

在 Zeabur 專案中，點擊「Environment Variables」，新增以下變數：

| 變數名稱 | 值 | 說明 |
|---------|-----|------|
| `CHANNEL_ACCESS_TOKEN` | 你的 Line Channel Access Token | 從 .env 複製 |
| `CHANNEL_SECRET` | 你的 Line Channel Secret | 從 .env 複製 |
| `OPENAI_API_KEY` | 你的 OpenAI API Key | 從 .env 複製 |
| `NOTION_TOKEN` | 你的 Notion Token | 從 .env 複製 |
| `NOTION_DATABASE_ID` | 你的 Notion Database ID | 從 .env 複製 |

**如何取得這些值：**
- 開啟本地的 `.env` 文件
- 複製每個變數的值到 Zeabur

### 4. 部署

1. Zeabur 會自動偵測為 Python 應用
2. 點擊「Deploy」開始部署
3. 等待部署完成（約 2-3 分鐘）

### 5. 取得部署 URL

部署完成後：
1. 在 Zeabur 專案頁面找到你的服務 URL
2. 例如：`https://your-app.zeabur.app`

---

## 更新 Line Webhook URL

### 1. 前往 Line Developer Console

前往 [https://developers.line.biz/console/](https://developers.line.biz/console/)

### 2. 更新 Webhook URL

1. 選擇你的 Messaging API Channel
2. 進入「Messaging API」分頁
3. 在「Webhook URL」欄位填入：
   ```
   https://your-app.zeabur.app/callback
   ```
   （將 `your-app.zeabur.app` 替換為你的實際 Zeabur URL）

4. 點擊「Verify」測試連線（應該顯示成功）
5. 確認「Use webhook」開關是**啟用**的

---

## 測試

1. 傳送文字訊息給你的 Line bot（應該會 echo 回覆）
2. 傳送 `/a` 開頭的訊息測試文字摘要功能
3. 傳送語音訊息測試語音轉文字和摘要功能

---

## 查看 Logs

如果遇到問題：
1. 在 Zeabur 專案頁面
2. 點擊你的服務
3. 查看「Logs」分頁來診斷問題

---

## 更新程式碼

當你修改程式碼後：

```bash
git add .
git commit -m "更新功能"
git push origin main
```

Zeabur 會自動重新部署！

---

## 安全性檢查清單

- ✅ `.env` 文件已在 `.gitignore` 中
- ✅ GitHub Repository 設為 Private
- ✅ 所有敏感資訊都在 Zeabur 環境變數中
- ✅ 程式碼中使用 `os.getenv()` 讀取環境變數
- ✅ Debug 模式已關閉（production）

---

## 常見問題

**Q: 部署後 bot 沒有回應？**
- 檢查 Zeabur Logs 是否有錯誤
- 確認所有環境變數都已正確設定
- 確認 Line Webhook URL 正確

**Q: 如何停止服務？**
- 在 Zeabur 專案頁面點擊「Pause」或「Delete」

**Q: 費用如何計算？**
- Zeabur 提供免費額度
- 查看 [Zeabur 定價](https://zeabur.com/pricing) 了解詳情
