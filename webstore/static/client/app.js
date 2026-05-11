const statusEl = document.getElementById("status");

const usersListEl = document.getElementById("users-list");
const productsListEl = document.getElementById("products-list");
const ordersListEl = document.getElementById("orders-list");

const userForm = document.getElementById("user-form");
const productForm = document.getElementById("product-form");
const orderForm = document.getElementById("order-form");
const tabButtons = document.querySelectorAll(".tab-btn");
const tabPanels = document.querySelectorAll(".tab-panel");

function setStatus(message, isError = false) {
  statusEl.textContent = message;
  statusEl.style.color = isError ? "#b91c1c" : "#0f766e";
}

function activateTab(tabName) {
  for (const button of tabButtons) {
    button.classList.toggle("active", button.dataset.tab === tabName);
  }
  for (const panel of tabPanels) {
    panel.classList.toggle("active", panel.dataset.panel === tabName);
  }
}

async function apiRequest(url, options = {}) {
  const response = await fetch(url, options);
  const text = await response.text();
  let data = null;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = null;
    }
  }
  if (!response.ok) {
    const errorMessage = data?.["@error"]?.["@messages"]?.[0] || `HTTP ${response.status}`;
    throw new Error(errorMessage);
  }
  return data;
}

function renderUsers(users) {
  usersListEl.innerHTML = "";
  for (const user of users) {
    const item = document.createElement("div");
    item.className = "item";
    item.innerHTML = `
      <p><strong>#${user.id}</strong> ${user.name}</p>
      <p>${user.email}</p>
      <div class="actions">
        <button class="muted" data-action="edit">Edit</button>
        <button class="danger" data-action="delete">Delete</button>
      </div>
    `;

    item.querySelector('[data-action="edit"]').addEventListener("click", async () => {
      const newName = prompt("New name", user.name);
      const newEmail = prompt("New email", user.email);
      if (!newName || !newEmail) return;
      try {
        await apiRequest(`/api/users/${user.id}/`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name: newName, email: newEmail })
        });
        setStatus("User updated");
        await loadAll();
      } catch (error) {
        setStatus(error.message, true);
      }
    });

    item.querySelector('[data-action="delete"]').addEventListener("click", async () => {
      if (!confirm(`Delete user ${user.name}?`)) return;
      try {
        await apiRequest(`/api/users/${user.id}/`, { method: "DELETE" });
        setStatus("User deleted");
        await loadAll();
      } catch (error) {
        setStatus(error.message, true);
      }
    });

    usersListEl.appendChild(item);
  }
}

function renderProducts(products) {
  productsListEl.innerHTML = "";
  for (const product of products) {
    const item = document.createElement("div");
    item.className = "item";
    item.innerHTML = `
      <p><strong>#${product.id}</strong> ${product.product_name}</p>
      <p>SKU: ${product.sku} | Price: ${product.price} | Stock: ${product.stock_quantity}</p>
      <p>${product.description || ""}</p>
      <div class="actions">
        <button class="muted" data-action="edit">Edit</button>
        <button class="danger" data-action="delete">Delete</button>
      </div>
    `;

    item.querySelector('[data-action="edit"]').addEventListener("click", async () => {
      const newName = prompt("New product name", product.product_name);
      const newPrice = prompt("New price", product.price);
      const newStock = prompt("New stock", product.stock_quantity);
      const newDescription = prompt("New description", product.description || "");
      if (!newName || newPrice === null || newStock === null) return;
      try {
        await apiRequest(`/api/products/${product.id}/`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            sku: product.sku,
            product_name: newName,
            description: newDescription,
            price: Number(newPrice),
            stock_quantity: Number(newStock)
          })
        });
        setStatus("Product updated");
        await loadAll();
      } catch (error) {
        setStatus(error.message, true);
      }
    });

    item.querySelector('[data-action="delete"]').addEventListener("click", async () => {
      if (!confirm(`Delete product ${product.product_name}?`)) return;
      try {
        await apiRequest(`/api/products/${product.id}/`, { method: "DELETE" });
        setStatus("Product deleted");
        await loadAll();
      } catch (error) {
        setStatus(error.message, true);
      }
    });

    productsListEl.appendChild(item);
  }
}

function renderOrders(orders) {
  ordersListEl.innerHTML = "";
  for (const order of orders) {
    const item = document.createElement("div");
    item.className = "item";
    item.innerHTML = `
      <p><strong>#${order.id}</strong> user:${order.user_id} product:${order.product_id}</p>
      <p>Qty: ${order.quantity} | Status: ${order.status}</p>
      <div class="actions">
        <select data-action="status-select">
          <option value="placed" ${order.status === "placed" ? "selected" : ""}>placed</option>
          <option value="paid" ${order.status === "paid" ? "selected" : ""}>paid</option>
          <option value="cancelled" ${order.status === "cancelled" ? "selected" : ""}>cancelled</option>
        </select>
        <button class="muted" data-action="status-save">Save status</button>
        <button class="danger" data-action="delete">Delete</button>
      </div>
    `;

    item.querySelector('[data-action="status-save"]').addEventListener("click", async () => {
      const newStatus = item.querySelector('[data-action="status-select"]').value;
      try {
        await apiRequest(`/api/orders/${order.id}/`, {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            user_id: order.user_id,
            product_id: order.product_id,
            quantity: order.quantity,
            status: newStatus
          })
        });
        setStatus("Order updated");
        await loadAll();
      } catch (error) {
        setStatus(error.message, true);
      }
    });

    item.querySelector('[data-action="delete"]').addEventListener("click", async () => {
      if (!confirm(`Delete order #${order.id}?`)) return;
      try {
        await apiRequest(`/api/orders/${order.id}/`, { method: "DELETE" });
        setStatus("Order deleted");
        await loadAll();
      } catch (error) {
        setStatus(error.message, true);
      }
    });

    ordersListEl.appendChild(item);
  }
}

async function loadAll() {
  try {
    const usersData = await apiRequest("/api/users/");
    const productsData = await apiRequest("/api/products/");
    const ordersData = await apiRequest("/api/orders/");

    renderUsers(usersData.users || []);
    renderProducts(productsData.products || []);
    renderOrders(ordersData.orders || []);
  } catch (error) {
    setStatus(error.message, true);
  }
}

userForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(userForm);
  const payload = {
    email: formData.get("email"),
    name: formData.get("name")
  };
  try {
    await apiRequest("/api/users/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    userForm.reset();
    setStatus("User added");
    await loadAll();
  } catch (error) {
    setStatus(error.message, true);
  }
});

productForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(productForm);
  const payload = {
    sku: formData.get("sku"),
    product_name: formData.get("product_name"),
    price: Number(formData.get("price")),
    stock_quantity: Number(formData.get("stock_quantity")),
    description: formData.get("description") || null
  };
  try {
    await apiRequest("/api/products/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    productForm.reset();
    setStatus("Product added");
    await loadAll();
  } catch (error) {
    setStatus(error.message, true);
  }
});

orderForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(orderForm);
  const payload = {
    user_id: Number(formData.get("user_id")),
    product_id: Number(formData.get("product_id")),
    quantity: Number(formData.get("quantity")),
    status: formData.get("status")
  };
  try {
    await apiRequest("/api/orders/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    orderForm.reset();
    setStatus("Order created");
    await loadAll();
  } catch (error) {
    setStatus(error.message, true);
  }
});

for (const button of tabButtons) {
  button.addEventListener("click", () => activateTab(button.dataset.tab));
}

activateTab("users");
loadAll();
