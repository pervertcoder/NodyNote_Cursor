# NodyNote 專案規格

## 1. 專案概述

NodyNote 為協作筆記 Web 應用，後端以 **FastAPI** 提供 REST API 與靜態頁面入口，前端以多頁 HTML / CSS / JS 組成，靜態資源集中於 `statics/`。

開發原則：**一次只實作一個功能**，依本規格之模組邊界逐步擴充，避免無關大重構。

---

## 2. 命名約定

| 類型 | 規則 | 範例 |
|------|------|------|
| 後端套件 | `routers/` | `from routers.user_router.user import router` |
| API Router 目錄 | `{領域}_router/` | `user_router`、`overview_router`、`note_router` |
| API Prefix | `/api/{領域}` | `/api/user`、`/api/overview`、`/api/note` |
| 業務邏輯檔 | `{領域}_func.py` | `user_func.py`、`overview_func.py` |
| 靜態頁資料夾 | `{領域}page/` | `homepage`、`login_registpage`、`overviewpage`、`notepage` |
| 靜態頁檔名 | 與領域名稱一致（首頁除外） | `overview.html`、`note.js` |
| 頁面 URL | `/{領域}` 或 `/{領域}/{參數}` | `/overview`、`/note/{note_id}` |

---

## 3. 技術棧

| 層級 | 技術 |
|------|------|
| 後端框架 | FastAPI |
| 靜態檔案 | `fastapi.staticfiles.StaticFiles` |
| 頁面回傳 | `fastapi.responses.FileResponse` |
| 前端 | 原生 HTML / CSS / JavaScript（每頁一資料夾） |

---

## 4. 目錄結構

```
NodyNote_Cursor/
├── main.py
├── spec.md
├── README.md
├── routers/
│   ├── user_router/
│   │   ├── user.py
│   │   └── user_func.py
│   ├── overview_router/
│   │   ├── overview.py
│   │   └── overview_func.py
│   └── note_router/
│       ├── note.py
│       └── note_func.py
└── statics/
    ├── homepage/
    │   ├── index.html
    │   ├── index.js
    │   └── style.css
    ├── login_registpage/
    │   ├── login_regist.html
    │   ├── login_regist.js
    │   └── login_regist.css
    ├── overviewpage/
    │   ├── overview.html
    │   ├── overview.js
    │   └── overview.css
    └── notepage/
        ├── note.html
        ├── note.js
        └── note.css
```

---

## 5. 架構分層

| 層級 | 位置 | 職責 |
|------|------|------|
| 入口層 | `main.py` | 建立 `FastAPI` 實例、註冊 API router、掛載 `/statics`、定義 HTML 頁面路由 |
| 路由層 | `routers/*_router/*.py` | 宣告 `APIRouter`、URL prefix、tags；註冊各 API 端點 |
| 業務層 | `routers/*_router/*_func.py` | 實作具體邏輯，由路由層呼叫 |
| 展示層 | `statics/{領域}page/` | 各頁 UI；透過 `/statics/...` 載入 css / js |

### 5.1 路由與邏輯分離

- `user.py` / `overview.py` / `note.py`：只負責 **API 路由定義**。
- `user_func.py` / `overview_func.py` / `note_func.py`：負責 **業務函式**。
- 新增 API 時：先在 `*_func.py` 實作邏輯，再在對應 `*.py` 掛路由。

---

## 6. 頁面路由（前端）

| URL | 回傳檔案 | 用途 |
|-----|----------|------|
| `GET /` | `statics/homepage/index.html` | 首頁 |
| `GET /login_regist` | `statics/login_registpage/login_regist.html` | 登入與註冊 |
| `GET /overview` | `statics/overviewpage/overview.html` | 筆記總覽 |
| `GET /note/{note_id}` | `statics/notepage/note.html` | 單一筆記編輯 |

### 6.1 靜態資源引用

- 公開前綴：`/statics`
- 範例：`/statics/overviewpage/overview.js`、`/statics/notepage/note.css`

### 6.2 前端約定

- 動態參數 `note_id` 由前端自 URL 解析，再呼叫 `/api/note` 相關 API。

---

## 7. API Router（後端）

| Router 模組 | Prefix | OpenAPI Tag | 職責範圍 |
|-------------|--------|-------------|----------|
| `user_router` | `/api/user` | `user` | 註冊、登入、登出、Session／身分驗證（見第 8 節） |
| `overview_router` | `/api/overview` | `overview` | 總覽頁列表、篩選、聚合資料 |
| `note_router` | `/api/note` | `note` | 單筆筆記 CRUD、內容讀寫 |

**實作位置**

- `routers/user_router/user.py`、`user_func.py`
- `routers/overview_router/overview.py`、`overview_func.py`
- `routers/note_router/note.py`、`note_func.py`

---

## 8. 身分驗證（Session + HttpOnly Cookie + Depends）

採 **伺服器端 Session**，憑證以 **HttpOnly Cookie** 傳遞；身分是否有效由 **後端查表** 決定，受保護的 API 以 FastAPI **`Depends(get_current_user)`** 驗證。不使用 JWT 存於 `localStorage`；不以全域 Middleware 取代路由層驗證。

### 8.1 原則

| 項目 | 約定 |
|------|------|
| 誰算已登入 | 僅後端：Cookie 內 `session_id` 能在 `sessions` 表查到且未過期 |
| 密碼 | 只存 **hash**（如 bcrypt）；註冊時 `hashpw` 寫入，登入時 `checkpw(明文, password_hash)` 比對，不回傳明文 |
| 登入識別 | 以 **`email`** 查 `users`；`username` 僅註冊與顯示用 |
| Session ID | 登入成功後以 `secrets` 產生足夠長的隨機字串，**不**在 JSON body 回傳給前端自行儲存 |
| 授權邊界 | `/api/overview`、`/api/note` 等需登入的端點一律掛 `Depends`；HTML 頁路由可不驗證，但資料仍由 API 擋住 |
| 敏感設定 | `SECRET_KEY` 等放 `.env`，不提交版控 |

### 8.2 流程

**註冊**

1. `POST /api/user/register`：建立 `users` 一筆（`username`、`email`、密碼等），密碼寫入 hash。
2. 預設註冊後**不自動登入**（若產品改為註冊即登入，仍須走登入流程建立 session）。

**登入**

1. `POST /api/user/login`：驗證帳密。
2. 成功：寫入 `sessions`（`session_id` ↔ `user_id`、過期時間等），回應 **`Set-Cookie`**（HttpOnly）。
3. 失敗：401，不發 Cookie。

**後續 API**

1. 瀏覽器自動帶 Cookie。
2. `get_current_user` 讀 Cookie → 查 `sessions` → 取得 `user_id` → 載入使用者；無效則 401。
3. 路由函式透過 `Depends(get_current_user)` 取得當前使用者，**不再**要求每次傳密碼。

**目前使用者**

- `GET /api/user/me`：供前端判斷是否登入；回傳 `username`、`email`、`color` 等公開欄位；同樣經 `Depends` 驗證。

**登出**

1. `POST /api/user/logout`：刪除對應 `sessions` 列，回應 **Clear-Cookie**。

### 8.3 資料表（概念）

| 表 | 主要欄位 | 說明 |
|----|----------|------|
| `users` | `id`, `username`, `email`, `password_hash`, `color`, `created_at` | 使用者帳號；**登入以 `email` 為準**，`username` 為顯示／辨識用 |
| `sessions` | `session_id`, `user_id`, `expires_at`, … | 可選：`created_at`、`user_agent` 供除錯／裝置列表 |

**多裝置**：預設**允許**同一帳號多筆 session 並存（手機、電腦各一 Cookie）。若日後改為「單一登入」，在登入成功時刪除該 `user_id` 其餘 session 即可，仍用同一套 Session 機制。

### 8.4 Cookie 設定

| 屬性 | 開發環境 | 上線 |
|------|----------|------|
| `HttpOnly` | 是 | 是 |
| `SameSite` | `Lax`（或依需求 `Strict`） | 同左 |
| `Secure` | 本機 `http` 可暫不設 | **必須**（僅 HTTPS） |
| 名稱 | 專案內統一（如 `session_id`） | 同左 |

傳輸：上線 API 與頁面須走 **HTTPS**，避免 Cookie、密碼在網路上明文傳送。

### 8.5 程式分層

| 位置 | 職責 |
|------|------|
| `user_func.py` | 註冊、登入（建 session）、登出（刪 session）、查 session |
| `user.py` 或共用模組（如 `auth.py`） | `get_current_user(request)`，供 `Depends` 使用 |
| `overview.py` / `note.py` | 需保護的路由參數：`user=Depends(get_current_user)` |

不為「僅部分 API 要登入」而優先採全域 Middleware；驗證邏輯集中在 `get_current_user` 以利測試與重用。

### 8.6 前端約定

- 呼叫需帶 Cookie 的 API：`fetch(url, { credentials: 'include' })`。
- **不**將 `session_id` 存入 `localStorage` / `sessionStorage`。
- 收到 **401 / 403**：導向 `/login_regist`（UX）；真正安全仍靠後端 API。
- 進入 `/overview`、`/note/{note_id}` 等頁時，可選先打 `/api/user/me` 檢查登入狀態。

### 8.7 WebSocket（預留）

WebSocket 為**另一條連線**，「先 REST 拉筆記再開 WS」僅為使用順序，**不能**取代 WS 端驗證。

- 同源握手時，瀏覽器通常會帶與 REST **相同的 Session Cookie**。
- 在 **`websocket.accept` 之前**：以與 REST 相同方式查 `session_id` → `user_id`，並確認對該 `note_id` 有權限；失敗則拒絕連線。
- 連線建立後，訊息處理以伺服器已驗證的 `user_id` 為準，**不信任** client 自行傳送的 `user_id`。
- 登出或 session 刪除後，已建立的 WS 可於後續版本以心跳重驗或主動斷線（實作時再定）。

### 8.8 User API 端點（草案）

| 方法 | 路徑 | 需登入 | 說明 |
|------|------|--------|------|
| POST | `/api/user/register` | 否 | 註冊（body：`username`、`email`、`password`；可選 `color`） |
| POST | `/api/user/login` | 否 | 登入（body：`email`、`password`），Set-Cookie |
| POST | `/api/user/logout` | 是 | 登出，Clear-Cookie |
| GET | `/api/user/me` | 是 | 回傳目前使用者公開資訊 |

`overview`、`note` 之 CRUD 端點實作時，預設 **需** `Depends(get_current_user)`，除非規格另有註明為公開 API。

---

## 9. 註冊順序（main.py）

1. `user_router`
2. `overview_router`
3. `note_router`

---

## 10. 開發與協作約定

- 改碼前先閱讀 `README.md`、`main.py`、本 `spec.md`。
- 僅修改與當前功能相關的檔案。
- 敏感設定放在 `.env`，不得提交至版本庫。
- 新增模組時遵循第 2 節命名約定。

---

## 11. 功能實作狀態

| 區塊 | 狀態 |
|------|------|
| 目錄與 router 骨架 | 已完成 |
| 命名統一 | 已完成 |
| 身分驗證規格（第 8 節） | 已完成 |
| `user` / `overview` / `note` API 端點 | 待實作 |
| Session／Cookie／`Depends` 程式實作 | 待實作 |
| `*_func.py` 業務邏輯 | 待實作 |
| 各頁前端 UI 與互動 | 待實作 |

---

## 12. 修訂紀錄

| 日期 | 說明 |
|------|------|
| 2026-05-23 | 初版：依現有架構撰寫 |
| 2026-05-23 | 命名統一：`view` → `overview`、`router` → `routers`、`login_regist_page` → `login_registpage`、URL `/login&regist` → `/login_regist` |
| 2026-05-23 | 新增第 8 節：Session + HttpOnly Cookie + Depends 身分驗證；章節 9–12 順延 |
| 2026-05-26 | `users` 新增 `email`（`VARCHAR(255)` NOT NULL UNIQUE） |
| 2026-05-27 | 登入改以 **`email`** 為準（`username` 僅註冊／顯示） |
