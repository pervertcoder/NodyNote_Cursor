# NodyNote 資料表規格

對應 [spec.md](spec.md) 第 8 節（Session 驗證）與協作筆記功能。

**修訂：** 2026-05-26（`users.email`）；2026-05-23（`users.color`；ID 欄位改 `INT UNSIGNED`）

---

## 1. 總覽

| 項目 | 說明 |
|------|------|
| 資料庫 | MySQL |
| 存取方式 | 同步 I/O（`mysql-connector-python`），手寫 SQL，依領域分檔 |
| 表名慣例 | 複數（`users`, `sessions`, `notes`, `note_permissions`） |

**四張表：**

| 表 | 用途 |
|----|------|
| `users` | 使用者帳號 |
| `sessions` | 登入 Session（Cookie `session_id` 對應） |
| `notes` | 筆記內容 |
| `note_permissions` | 筆記協作權限（被分享的使用者） |

**程式分層（建議）：**

| 檔案 | 職責 |
|------|------|
| `db.py`（或 `database.py`） | 連線、`get_connection`、建表初始化 |
| `user_func.py` | `users` / `sessions` 的 SQL |
| `note_func.py` | `notes` / `note_permissions` 的 SQL |
| `overview_func.py` | 總覽列表（JOIN 或呼叫 note 查詢） |

連線設定放 `.env`，不提交版控（例：`DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`）。

API 路由若呼叫同步 DB，建議使用 `def` 路由，避免在 `async def` 內阻塞事件迴圈。

---

## 2. 權限模型（定案：模型 A）

- `notes.owner_id` = 建立者（擁有者）
- `note_permissions` 只記錄「被分享」的使用者（不含 owner 亦可）
- **能否存取某筆 note：**
  - `owner_id` = 當前 `user_id`
  - **或** 存在 `note_permissions` 列 `(note_id, user_id)`

**角色 `role`（`note_permissions.role`）：**

| 角色 | 說明 |
|------|------|
| `editor` | 可讀寫 `title`、`content` |
| `viewer` | 唯讀 |
| `owner` | 語意上等同 `notes.owner_id`；可不寫入 `note_permissions` |

刪除筆記、管理成員：**僅 owner**（`notes.owner_id`）。

---

## 3. 資料表定義

### 3.1 `users`（使用者）

| 欄位 | 型別 | 約束 | 說明 |
|------|------|------|------|
| `id` | `INT UNSIGNED` | PK, AUTO_INCREMENT | |
| `username` | `VARCHAR(64)` | NOT NULL, UNIQUE | 登入帳號 |
| `email` | `VARCHAR(255)` | NOT NULL, UNIQUE | 聯絡／註冊用信箱 |
| `password_hash` | `VARCHAR(255)` | NOT NULL | bcrypt，不存明文 |
| `color` | `VARCHAR(7)` | NOT NULL, DEFAULT `'#000000'` | 使用者代表色，Hex；預設黑色 |
| `created_at` | `DATETIME` | NOT NULL, DEFAULT CURRENT_TIMESTAMP | |

**索引：** `PRIMARY KEY (id)`、`UNIQUE KEY uk_users_username (username)`、`UNIQUE KEY uk_users_email (email)`

**說明：**

- 註冊：`INSERT users`（含 `username`、`email`），password 先 bcrypt 再寫入 `password_hash`；未指定 `color` 時由資料庫預設 `#000000`（黑）
- 登入：`SELECT` 依 `username` 取列，比對 `password_hash`（不以 `email` 登入）
- `GET /api/user/me` 可回傳 `username`、`email`、`color`，供頭像、協作成員列表等 UI 辨識

### 3.2 `sessions`（登入 Session）

| 欄位 | 型別 | 約束 | 說明 |
|------|------|------|------|
| `session_id` | `VARCHAR(64)` | PK | `secrets` 隨機字串 |
| `user_id` | `INT UNSIGNED` | NOT NULL, FK → `users(id)` | |
| `expires_at` | `DATETIME` | NOT NULL | |
| `created_at` | `DATETIME` | NOT NULL, DEFAULT CURRENT_TIMESTAMP | |
| `user_agent` | `VARCHAR(512)` | NULL | 可選，多裝置除錯 |

**索引：** `PRIMARY KEY (session_id)`、`idx_sessions_user_id`、`idx_sessions_expires_at`

**外鍵：** `FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE`

**說明：**

- Cookie 名稱：`session_id`（與 spec 8.4 一致）
- 有效登入：`session_id` 存在且 `expires_at > NOW()`
- 多裝置：同一 `user_id` 可多筆 session 並存
- 登出：`DELETE` 該 `session_id`
- 單一登入（若日後要）：登入成功時 `DELETE` 同 `user_id` 其餘 sessions

### 3.3 `notes`（筆記）

| 欄位 | 型別 | 約束 | 說明 |
|------|------|------|------|
| `id` | `INT UNSIGNED` | PK, AUTO_INCREMENT | |
| `owner_id` | `INT UNSIGNED` | NOT NULL, FK → `users(id)` | 建立者 |
| `title` | `VARCHAR(255)` | NOT NULL, DEFAULT `''` | |
| `content` | `MEDIUMTEXT` | NULL | 正文 |
| `created_at` | `DATETIME` | NOT NULL, DEFAULT CURRENT_TIMESTAMP | |
| `updated_at` | `DATETIME` | NOT NULL, ON UPDATE CURRENT_TIMESTAMP | |

**索引：** `PRIMARY KEY (id)`、`idx_notes_owner_id`、`idx_notes_updated_at`

**外鍵：** `FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE RESTRICT`  
（若刪除使用者時要一併刪除其筆記，可改 `CASCADE`）

**說明：**

- URL：`/note/{note_id}` 對應 `notes.id`
- 建立：`INSERT notes`，`owner_id` = 當前登入使用者
- 總覽排序：常用 `updated_at DESC`

### 3.4 `note_permissions`（筆記協作權限）

| 欄位 | 型別 | 約束 | 說明 |
|------|------|------|------|
| `note_id` | `INT UNSIGNED` | NOT NULL, FK → `notes(id)` | |
| `user_id` | `INT UNSIGNED` | NOT NULL, FK → `users(id)` | |
| `role` | `ENUM('editor','viewer')` | NOT NULL | |
| `created_at` | `DATETIME` | NOT NULL, DEFAULT CURRENT_TIMESTAMP | |

**索引：** `PRIMARY KEY (note_id, user_id)`、`idx_note_permissions_user_id`

**外鍵：**

- `note_id` → `notes(id) ON DELETE CASCADE`
- `user_id` → `users(id) ON DELETE CASCADE`

**說明：**

- 同一 `(note_id, user_id)` 僅一筆（複合主鍵）
- 分享：`INSERT`，`role` 為 `editor` 或 `viewer`
- 取消分享：`DELETE` 該列
- 不可與 `owner_id` 重複分享給自己（業務層檢查）

---

## 4. MySQL 建表 DDL（參考）

```sql
-- 需先建立資料庫並設定 charset
-- CREATE DATABASE nodynote CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

CREATE TABLE users (
  id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  username VARCHAR(64) NOT NULL,
  email VARCHAR(255) NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  color VARCHAR(7) NOT NULL DEFAULT '#000000',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_users_username (username),
  UNIQUE KEY uk_users_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 若 users 表已存在，可改用：
-- ALTER TABLE users ADD COLUMN email VARCHAR(255) NOT NULL AFTER username, ADD UNIQUE KEY uk_users_email (email);
-- ALTER TABLE users ADD COLUMN color VARCHAR(7) NOT NULL DEFAULT '#000000' AFTER password_hash;

CREATE TABLE sessions (
  session_id VARCHAR(64) NOT NULL,
  user_id INT UNSIGNED NOT NULL,
  expires_at DATETIME NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  user_agent VARCHAR(512) NULL,
  PRIMARY KEY (session_id),
  KEY idx_sessions_user_id (user_id),
  KEY idx_sessions_expires_at (expires_at),
  CONSTRAINT fk_sessions_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE notes (
  id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  owner_id INT UNSIGNED NOT NULL,
  title VARCHAR(255) NOT NULL DEFAULT '',
  content MEDIUMTEXT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY idx_notes_owner_id (owner_id),
  KEY idx_notes_updated_at (updated_at),
  CONSTRAINT fk_notes_owner FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE note_permissions (
  note_id INT UNSIGNED NOT NULL,
  user_id INT UNSIGNED NOT NULL,
  role ENUM('editor','viewer') NOT NULL,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (note_id, user_id),
  KEY idx_note_permissions_user_id (user_id),
  CONSTRAINT fk_np_note FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE,
  CONSTRAINT fk_np_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

## 5. 常用查詢（業務邏輯參考）

**驗證 Session，取得 user_id**

```sql
SELECT user_id FROM sessions
WHERE session_id = %s AND expires_at > NOW();
```

**總覽：我擁有的 + 我被分享的筆記**

```sql
SELECT n.id, n.title, n.updated_at, n.owner_id,
       CASE WHEN n.owner_id = %s THEN 'owner' ELSE np.role END AS my_role
FROM notes n
LEFT JOIN note_permissions np ON np.note_id = n.id AND np.user_id = %s
WHERE n.owner_id = %s OR np.user_id IS NOT NULL
ORDER BY n.updated_at DESC;
```

**是否可讀取 note（viewer 以上）**

```sql
SELECT 1 FROM notes n
LEFT JOIN note_permissions np ON np.note_id = n.id AND np.user_id = %s
WHERE n.id = %s AND (n.owner_id = %s OR np.user_id = %s)
LIMIT 1;
```

**是否可編輯 note（owner 或 editor）**

```sql
SELECT 1 FROM notes n
LEFT JOIN note_permissions np ON np.note_id = n.id AND np.user_id = %s AND np.role = 'editor'
WHERE n.id = %s AND (n.owner_id = %s OR np.user_id IS NOT NULL)
LIMIT 1;
```

---

## 6. 與 API / spec 對照

| 情境 | 涉及資料表 |
|------|------------|
| `POST /api/user/register` | `users` |
| `POST /api/user/login` | `users`, `sessions` |
| `POST /api/user/logout` | `sessions` |
| `GET /api/user/me` | `sessions`, `users` |
| `GET /api/overview` | `notes`, `note_permissions` |
| `GET/PUT /api/note/{id}` | `notes`, `note_permissions` + 權限檢查 |
| WebSocket（預留） | `sessions` + note 權限（同 REST） |

詳細流程見 [spec.md](spec.md) 第 8 節。

---

## 7. 待產品確認（實作前可再改）

- [x] 登入帳號欄位固定為 `username`；`email` 僅註冊／個人資料用
- [ ] 刪除使用者時：`notes` RESTRICT 或 CASCADE
- [ ] Session 有效期限（例如 7 天、30 天）
- [ ] 是否需軟刪除 notes（`deleted_at`）
- [ ] 分享時是否允許 viewer（目前已納入 ENUM）
