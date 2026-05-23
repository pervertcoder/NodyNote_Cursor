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
| `user_router` | `/api/user` | `user` | 註冊、登入、登出、Session／身分驗證 |
| `overview_router` | `/api/overview` | `overview` | 總覽頁列表、篩選、聚合資料 |
| `note_router` | `/api/note` | `note` | 單筆筆記 CRUD、內容讀寫 |

**實作位置**

- `routers/user_router/user.py`、`user_func.py`
- `routers/overview_router/overview.py`、`overview_func.py`
- `routers/note_router/note.py`、`note_func.py`

---

## 8. 註冊順序（main.py）

1. `user_router`
2. `overview_router`
3. `note_router`

---

## 9. 開發與協作約定

- 改碼前先閱讀 `README.md`、`main.py`、本 `spec.md`。
- 僅修改與當前功能相關的檔案。
- 敏感設定放在 `.env`，不得提交至版本庫。
- 新增模組時遵循第 2 節命名約定。

---

## 10. 功能實作狀態

| 區塊 | 狀態 |
|------|------|
| 目錄與 router 骨架 | 已完成 |
| 命名統一 | 已完成 |
| `user` / `overview` / `note` API 端點 | 待實作 |
| `*_func.py` 業務邏輯 | 待實作 |
| 各頁前端 UI 與互動 | 待實作 |

---

## 11. 修訂紀錄

| 日期 | 說明 |
|------|------|
| 2026-05-23 | 初版：依現有架構撰寫 |
| 2026-05-23 | 命名統一：`view` → `overview`、`router` → `routers`、`login_regist_page` → `login_registpage`、URL `/login&regist` → `/login_regist` |
