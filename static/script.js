const API_BASE = "/api/books";

const tbody = document.getElementById("books-tbody");

async function loadBooks() {
  tbody.innerHTML = "";

  try {
    const res = await fetch(API_BASE);
    if (!res.ok) {
      throw new Error("błąd przy pobieraniu książek");
    }

    const data = await res.json();

    data.forEach((b) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `
                <td>${b.id}</td>
                <td>${b.title}</td>
                <td>${b.author}</td>
                <td>${b.price}</td>
                <td>${b.published_year}</td>
            `;
      tbody.appendChild(tr);
    });
  } catch (err) {
    console.error(err);
  }
}

loadBooks();
