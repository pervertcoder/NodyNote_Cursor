"use strict";

// ========================
// API functions（放最上方）
// ========================

const apiFetchJson = function (url, options) {
  return fetch(url, options).then(async (res) => {
    let data = null;
    try {
      data = await res.json();
    } catch (e) {
      data = null;
    }

    if (res.ok) return data;

    const detail =
      (data && typeof data === "object" && (data.detail || data.message)) || `HTTP ${res.status}`;
    const err = new Error(String(detail));
    err.status = res.status;
    err.data = data;
    throw err;
  });
};

const apiMe = function () {
  return apiFetchJson("/api/user/me", {
    method: "GET",
    credentials: "include",
  });
};

const apiLogout = function () {
  return apiFetchJson("/api/user/logout", {
    method: "DELETE",
    credentials: "include",
  });
};

const logoutBtn = document.getElementById("logout_btn");
const logoutMsg = document.getElementById("logout_msg");

const setLogoutDisabled = function (disabled) {
  if (!logoutBtn) return;
  logoutBtn.disabled = disabled;
};

const showMsg = function (type, text) {
  if (!logoutMsg) return;
  logoutMsg.classList.remove("msg--off", "msg--ok", "msg--err");
  if (type === "ok") logoutMsg.classList.add("msg--ok");
  if (type === "err") logoutMsg.classList.add("msg--err");
  logoutMsg.textContent = text || "";
  if (!text) logoutMsg.classList.add("msg--off");
};

// 進頁先驗證是否登入，避免直接打 /overview 進入
apiMe().catch((err) => {
  if (err?.status === 401) {
    window.location.href = "/login_regist";
    return;
  }
  showMsg("err", err?.message || "驗證登入狀態失敗");
});

logoutBtn?.addEventListener("click", () => {
  showMsg("", "");
  setLogoutDisabled(true);
  apiLogout()
    .then((data) => {
      if (data && typeof data === "object" && data.message === "ok") {
        showMsg("ok", "已登出");
        window.location.href = "/login_regist";
        return;
      }
      showMsg("err", "登出回傳非 ok");
    })
    .catch((err) => {
      showMsg("err", err?.message || "登出失敗");
      if (err?.status === 401) window.location.href = "/login_regist";
    })
    .finally(() => {
      setLogoutDisabled(false);
    });
});
