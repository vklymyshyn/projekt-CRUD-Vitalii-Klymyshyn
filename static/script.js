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

async function loadBooks() {
  listError.textContent = "";
  tbody.innerHTML = "";

  try {
    const res = await fetch(API_BASE);
    if (!res.ok) {
      throw new Error("Failed to load books");
    }
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
                    <button data-action="delete" data-id="${
                      b.id
                    }">Delete</button>
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
      const res = await fetch(`${API_BASE}/${id}`, {
        method: "DELETE",
      });
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

loadBooks();
