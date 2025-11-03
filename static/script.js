const API_BASE = "/api/books";

const tbody = document.getElementById("books-tbody");
const listError = document.getElementById("list-error");

const form = document.getElementById("book-form");
const formError = document.getElementById("form-error");

const fieldId = document.getElementById("book-id");
const fieldTitle = document.getElementById("title");
const fieldAuthor = document.getElementById("author");
const fieldPrice = document.getElementById("price");
const fieldYear = document.getElementById("published_year");
const fieldDesc = document.getElementById("description");

const resetBtn = document.getElementById("reset-btn");

function toggleFormDisabled(disabled) {
  [fieldTitle, fieldAuthor, fieldPrice, fieldYear, fieldDesc, resetBtn].forEach(
    (el) => el && (el.disabled = disabled)
  );
  const saveBtn = document.getElementById("save-btn");
  if (saveBtn) saveBtn.disabled = disabled;
}

async function loadBooks() {
  listError.textContent = "";
  tbody.innerHTML = "";
  try {
    const res = await fetch(API_BASE);
    if (res.status === 401) {
      listError.textContent = "Please log in to access books.";
      return;
    }
    if (!res.ok) throw new Error("Failed to load books");
    const data = await res.json();
    data.forEach((b) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${b.id}</td>
        <td><strong>${b.title}</strong><br/><em>${b.author}</em></td>
        <td>${b.price}</td>
        <td>${b.published_year}</td>
        <td>${b.description ?? ""}</td>
        <td>
          <button data-action="edit" data-id="${b.id}">Edit</button>
          <button data-action="delete" data-id="${b.id}">Delete</button>
        </td>
      `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error(err);
    listError.textContent = "Cannot load books.";
  }
}

function fillForm(book) {
  fieldId.value = book.id || "";
  fieldTitle.value = book.title || "";
  fieldAuthor.value = book.author || "";
  fieldPrice.value = book.price || "";
  fieldYear.value = book.published_year || "";
  fieldDesc.value = book.description || "";
}

function resetForm() {
  fillForm({});
  formError.textContent = "";
}

tbody.addEventListener("click", async (e) => {
  const btn = e.target.closest("button");
  if (!btn) return;
  const id = btn.getAttribute("data-id");
  const action = btn.getAttribute("data-action");

  if (action === "edit") {
    try {
      const res = await fetch(`${API_BASE}/${id}`);
      if (res.status === 401) {
        listError.textContent = "Please log in to access books.";
        return;
      }
      if (!res.ok) throw new Error("Not found");
      const book = await res.json();
      fillForm(book);
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (err) {
      console.error(err);
      listError.textContent = "Cannot load selected book.";
    }
  }

  if (action === "delete") {
    if (!confirm("Delete this book?")) return;
    try {
      const res = await fetch(`${API_BASE}/${id}`, { method: "DELETE" });
      if (res.status === 401) {
        listError.textContent = "Please log in to delete books.";
        return;
      }
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || "Delete failed");
      }
    } catch (err) {
      console.error(err);
      listError.textContent = "Delete failed.";
    }
    await loadBooks();
    resetForm();
  }
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  formError.textContent = "";
  const payload = {
    title: fieldTitle.value.trim(),
    author: fieldAuthor.value.trim(),
    price: fieldPrice.value,
    published_year: fieldYear.value,
    description: fieldDesc.value.trim(),
  };
  const idVal = fieldId.value;
  const isEdit = idVal !== "";

  try {
    let res;
    if (isEdit) {
      res = await fetch(`${API_BASE}/${idVal}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    } else {
      res = await fetch(API_BASE, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    }
    if (res.status === 401) {
      formError.textContent = "Please log in first.";
      return;
    }
    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.error || "Request failed");
    }
    await loadBooks();
    resetForm();
  } catch (err) {
    console.error(err);
    formError.textContent = err.message;
  }
});

resetBtn.addEventListener("click", resetForm);

/* ===== AUTH SECTION ===== */
const AUTH_BASE = "/api/auth";
const authStatus = document.getElementById("auth-status");
const authError = document.getElementById("auth-error");
const regForm = document.getElementById("register-form");
const loginForm = document.getElementById("login-form");
const logoutBtn = document.getElementById("logout-btn");

function setToken(token) {
  if (token) localStorage.setItem("token", token);
  else localStorage.removeItem("token");
  renderAuthStatus();
}

function getToken() {
  return localStorage.getItem("token");
}

const _origFetch = window.fetch;
window.fetch = (input, init = {}) => {
  const token = getToken();
  init.headers = init.headers || {};
  if (token) init.headers.Authorization = `Bearer ${token}`;
  return _origFetch(input, init);
};

async function renderAuthStatus() {
  const token = getToken();
  if (!token) {
    if (authStatus) authStatus.textContent = "Not logged in";
    tbody.innerHTML = "";
    toggleFormDisabled(true);
    return;
  }
  try {
    const res = await fetch(`${AUTH_BASE}/me`);
    if (!res.ok) throw new Error("unauth");
    const data = await res.json();
    if (authStatus) authStatus.textContent = `Logged in as ${data.user.email}`;
    toggleFormDisabled(false);
    await loadBooks();
  } catch {
    setToken(null);
    if (authStatus) authStatus.textContent = "Not logged in";
    tbody.innerHTML = "";
    toggleFormDisabled(true);
  }
}

regForm?.addEventListener("submit", async (e) => {
  e.preventDefault();
  if (authError) authError.textContent = "";
  try {
    const email = document.getElementById("reg-email").value.trim();
    const password = document.getElementById("reg-pass").value;
    const res = await fetch(`${AUTH_BASE}/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Register failed");
    setToken(data.token);
  } catch (err) {
    if (authError) authError.textContent = err.message;
  }
});

loginForm?.addEventListener("submit", async (e) => {
  e.preventDefault();
  if (authError) authError.textContent = "";
  try {
    const email = document.getElementById("login-email").value.trim();
    const password = document.getElementById("login-pass").value;
    const res = await fetch(`${AUTH_BASE}/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Login failed");
    setToken(data.token);
  } catch (err) {
    if (authError) authError.textContent = err.message;
  }
});

logoutBtn?.addEventListener("click", () => setToken(null));

toggleFormDisabled(true);
renderAuthStatus();
