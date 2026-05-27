-- users 新增 email（放在 username 之後）
-- 若表內已有資料，請先為每筆填寫唯一 email 再執行 NOT NULL / UNIQUE

ALTER TABLE users
  ADD COLUMN email VARCHAR(255) NOT NULL AFTER username,
  ADD UNIQUE KEY uk_users_email (email);
