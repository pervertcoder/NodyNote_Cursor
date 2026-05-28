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

const apiRegister = function (payload) {
  return apiFetchJson("/api/user/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
};

const apiLogin = function (payload) {
  return apiFetchJson("/api/user/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    credentials: "include",
  });
};

const loginBtn = document.getElementById("submit_btn");
const registBtn = document.getElementById("regist_btn");

const errorLogin = document.querySelector(".error-login");
const errorMessageLogin = document.querySelector(".error-message-login");
const errorRegist = document.querySelector(".error-regist");
const errorMessageRegist = document.querySelector(".error-message-regist");

const tabLogin = document.getElementById("tab_login");
const tabRegister = document.getElementById("tab_register");

const emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const normalizeEmail = function (email) {
  return String(email || "").trim().toLowerCase();
};

const hideLoginError = function () {
  if (!errorLogin) return;
  errorLogin.classList.add("error--off");
  if (errorMessageLogin) errorMessageLogin.textContent = "";
};

const hideRegistError = function () {
  if (!errorRegist) return;
  errorRegist.classList.add("error--off");
  if (errorMessageRegist) errorMessageRegist.textContent = "";
};

const showLoginMessage = function (prefix, message, color) {
  if (!errorLogin || !errorMessageLogin) return;
  errorLogin.classList.remove("error--off");
  errorMessageLogin.textContent = `${prefix}:${message}`;
  errorMessageLogin.style.color = color || "red";
};

const showRegistMessage = function (prefix, message, color) {
  if (!errorRegist || !errorMessageRegist) return;
  errorRegist.classList.remove("error--off");
  errorMessageRegist.textContent = `${prefix}:${message}`;
  errorMessageRegist.style.color = color || "red";
};

const switchToLogin = function () {
  if (tabLogin) tabLogin.checked = true;
  hideRegistError();
};

const switchToRegist = function () {
  if (tabRegister) tabRegister.checked = true;
  hideLoginError();
};

registBtn?.addEventListener("click", () => {
  hideRegistError();

  const username = String(document.getElementById("name_regist")?.value || "").trim();
  const email = normalizeEmail(document.getElementById("email_regist")?.value);
  const password = String(document.getElementById("password_regist")?.value || "").trim();
  const password2 = String(document.getElementById("password_regist2")?.value || "").trim();

  if (!username || !email || !password || !password2) {
    showRegistMessage("X", "請輸入暱稱、信箱、密碼、確認密碼", "red");
    return;
  }
  if (!emailRe.test(email)) {
    showRegistMessage("X", "Email 格式不正確", "red");
    return;
  }
  if (password.length < 8) {
    showRegistMessage("X", "密碼至少 8 碼（示意規則）", "red");
    return;
  }
  if (password !== password2) {
    showRegistMessage("X", "兩次密碼不一致", "red");
    return;
  }

  const payload = {
    username: username,
    email: email,
    password: password,
  };

  setButtonsDisabled(true);
  apiRegister(payload)
    .then(() => {
      showRegistMessage("O", "Registed Done", "green");
      switchToLogin();
    })
    .catch((err) => {
      showRegistMessage("X", err?.message || "註冊失敗", "red");
    })
    .finally(() => {
      setButtonsDisabled(false);
    });
});

loginBtn?.addEventListener("click", () => {
  hideLoginError();

  const email = normalizeEmail(document.getElementById("email_login")?.value);
  const password = String(document.getElementById("password_login")?.value || "").trim();
  if (!email || !password) {
    showLoginMessage("X", "請輸入信箱、密碼", "red");
    return;
  }
  if (email.includes("@") && !emailRe.test(email)) {
    showLoginMessage("X", "Email 格式不正確", "red");
    return;
  }

  const payload = {
    email: email,
    password: password,
  };

  setButtonsDisabled(true);
  apiLogin(payload)
    .then(() => {
      showLoginMessage("O", "Login Done", "green");
      window.location.href = "/overview";
    })
    .catch((err) => {
      showLoginMessage("X", err?.message || "登入失敗", "red");
    })
    .finally(() => {
      setButtonsDisabled(false);
    });
});

// 小補強：切換頁籤時，把錯誤訊息收起來（更像 onboarding.js 的操作感）
tabLogin?.addEventListener("change", () => {
  if (tabLogin.checked) hideLoginError();
});
tabRegister?.addEventListener("change", () => {
  if (tabRegister.checked) hideRegistError();
});

const setButtonsDisabled = function (disabled) {
  if (loginBtn) loginBtn.disabled = disabled;
  if (registBtn) registBtn.disabled = disabled;
};