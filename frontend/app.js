const toastEl = document.getElementById("toast");
const activityEl = document.getElementById("activity-log");
const liveStatusEl = document.getElementById("task-live-status");

let activeTaskInterval = null;

const notify = (message, tone = "info") => {
  toastEl.textContent = message;
  toastEl.style.borderColor = tone === "error" ? "var(--error)" : "var(--outline)";
  toastEl.classList.add("toast--show");
  setTimeout(() => toastEl.classList.remove("toast--show"), 2300);
};

const log = (label, detail = "") => {
  const item = document.createElement("li");
  const stamp = new Date().toLocaleTimeString();
  const strong = document.createElement("strong");
  strong.textContent = `[${stamp}] ${label}`;
  item.appendChild(strong);
  if (detail) {
    const span = document.createElement("span");
    span.textContent = ` — ${detail}`;
    item.appendChild(span);
  }
  activityEl.prepend(item);
};

const setLiveStatus = (text) => {
  liveStatusEl.textContent = text;
};

const updateResult = (containerId, message, tone = "info") => {
  const container = document.getElementById(containerId);
  container.innerHTML = "";
  const div = document.createElement("div");
  div.className = "result";
  if (tone === "error") div.classList.add("result--error");
  if (tone === "success") div.classList.add("result--success");
  div.textContent = message;
  container.appendChild(div);
};

const renderUser = (user) => {
  const target = document.getElementById("user-output");
  target.innerHTML = "";
  if (!user) {
    updateResult("user-output", "No user found", "error");
    return;
  }
  const block = document.createElement("div");
  block.className = "result result--success";
  block.innerHTML = `<strong>${user.first_name} ${user.last_name}</strong>`;
  target.appendChild(block);
};

const renderAddedUser = (user) => {
  const target = document.getElementById("add-user-output");
  target.innerHTML = "";
  const block = document.createElement("div");
  block.className = "result result--success";
  block.innerHTML = `User added: <strong>${user.first_name} ${user.last_name}</strong> (ID: ${user.id})`;
  target.appendChild(block);
};

const renderWeather = (payload) => {
  const target = document.getElementById("weather-output");
  target.innerHTML = "";
  if (!payload || typeof payload !== "object") {
    updateResult("weather-output", "No weather data returned", "error");
    return;
  }
  const city = Object.keys(payload)[0];
  const entries = payload[city] || [];
  const chip = document.createElement("div");
  chip.className = "chip";
  chip.textContent = `${city} · ${entries.length} day${entries.length === 1 ? "" : "s"}`;
  target.appendChild(chip);

  const grid = document.createElement("div");
  grid.className = "grid-forecast";
  entries.forEach((item) => {
    const card = document.createElement("div");
    card.className = "forecast";
    const title = document.createElement("h4");
    title.textContent = `${item.day} (${item.date})`;
    const desc = document.createElement("p");
    desc.textContent = item.description;
    const deg = document.createElement("p");
    deg.textContent = `${item.degree}°`;
    card.append(title, desc, deg);
    grid.appendChild(card);
  });
  target.appendChild(grid);
};

const renderTaskStatus = (taskId, state, error) => {
  const target = document.getElementById("task-output");
  target.innerHTML = "";
  const block = document.createElement("div");
  block.className = "result";
  block.textContent = `${taskId}: ${state}`;
  if (state === "SUCCESS") block.classList.add("result--success");
  if (state === "FAILURE" || state === "REVOKED") block.classList.add("result--error");
  if (error) {
    const info = document.createElement("div");
    info.className = "muted";
    info.textContent = error;
    block.appendChild(info);
  }
  target.appendChild(block);
};

const request = async (method, path, body) => {
  const opts = { method, headers: {} };
  if (body) {
    opts.headers["Content-Type"] = "application/json";
    opts.body = JSON.stringify(body);
  }
  const res = await fetch(path, opts);
  let data = null;
  try {
    data = await res.json();
  } catch (err) {
    // ignore parse errors for empty responses
  }
  if (!res.ok) {
    let detail = data?.error || data?.detail || `Request failed (${res.status})`;
    if (typeof detail === "object") {
      detail = JSON.stringify(detail);
    }
    throw new Error(detail);
  }
  return data;
};

const watchTask = (taskId, label) => {
  if (activeTaskInterval) {
    clearInterval(activeTaskInterval);
    activeTaskInterval = null;
  }
  setLiveStatus(`Tracking ${label} (${taskId})`);
  const started = Date.now();

  const poll = async () => {
    try {
      const data = await request("GET", `/tasks/${taskId}`);
      const state = data?.state || "UNKNOWN";
      renderTaskStatus(taskId, state, data?.error);
      if (["SUCCESS", "FAILURE", "REVOKED"].includes(state)) {
        const seconds = ((Date.now() - started) / 1000).toFixed(1);
        setLiveStatus(`Task ${state.toLowerCase()} in ${seconds}s`);
        clearInterval(activeTaskInterval);
        activeTaskInterval = null;
      }
    } catch (err) {
      renderTaskStatus(taskId, "ERROR", err.message);
      clearInterval(activeTaskInterval);
      activeTaskInterval = null;
    }
  };

  poll();
  activeTaskInterval = setInterval(poll, 4000);
};

// Forms

document.getElementById("form-user-add").addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = new FormData(event.target);
  const userData = {
    first_name: data.get("firstName"),
    last_name: data.get("lastName"),
    mail: data.get("mail"),
    age: Number(data.get("age"))
  };
  try {
    const res = await request("POST", "/users", userData);
    renderAddedUser(res);
    notify("User added", "success");
    log("Added user", `${res.first_name} ${res.last_name}`);
  } catch (err) {
    updateResult("add-user-output", err.message, "error");
    notify(err.message, "error");
    log("Add user failed", err.message);
  }
});

document.getElementById("form-user-queue").addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = new FormData(event.target);
  const count = Number(data.get("count"));
  const delay = Number(data.get("delay"));
  try {
    const res = await request("POST", `/users/${count}/${delay}`);
    updateResult("user-task-output", `Task queued: ${res.task_id}`);
    notify("User task queued", "success");
    log("Queued users", `${count} users, ${delay}s delay (task ${res.task_id})`);
    if (res.task_id) {
      watchTask(res.task_id, `${count} users`);
    }
  } catch (err) {
    updateResult("user-task-output", err.message, "error");
    notify(err.message, "error");
    log("Queue users failed", err.message);
  }
});

document.getElementById("form-user-get").addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = new FormData(event.target);
  const userId = Number(data.get("userId"));
  try {
    const res = await request("GET", `/users/${userId}`);
    renderUser(res);
    notify("User fetched", "success");
    log("Fetched user", `id ${userId}`);
  } catch (err) {
    updateResult("user-output", err.message, "error");
    notify(err.message, "error");
    log("Fetch user failed", err.message);
  }
});

document.getElementById("form-weather-queue").addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = new FormData(event.target);
  const city = String(data.get("city") || "").trim();
  const delay = Number(data.get("delay"));
  if (!city) return;
  try {
    const res = await request("POST", `/weathers/${encodeURIComponent(city)}/${delay}`);
    updateResult("weather-task-output", `Task queued: ${res.task_id}`);
    notify("Weather task queued", "success");
    log("Queued weather", `${city}, ${delay}s delay (task ${res.task_id})`);
    if (res.task_id) {
      watchTask(res.task_id, `${city} weather`);
    }
  } catch (err) {
    updateResult("weather-task-output", err.message, "error");
    notify(err.message, "error");
    log("Queue weather failed", err.message);
  }
});

document.getElementById("form-weather-get").addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = new FormData(event.target);
  const city = String(data.get("city") || "").trim();
  if (!city) return;
  try {
    const res = await request("GET", `/weathers/${encodeURIComponent(city)}`);
    renderWeather(res);
    notify("Weather fetched", "success");
    log("Fetched weather", city);
  } catch (err) {
    updateResult("weather-output", err.message, "error");
    notify(err.message, "error");
    log("Fetch weather failed", err.message);
  }
});

document.getElementById("form-task-status").addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = new FormData(event.target);
  const taskId = String(data.get("taskId") || "").trim();
  if (!taskId) return;
  try {
    const res = await request("GET", `/tasks/${taskId}`);
    const state = res?.state || "UNKNOWN";
    renderTaskStatus(taskId, state, res?.error);
    notify(`Task: ${state}`);
    log("Checked task", `${taskId} -> ${state}`);
  } catch (err) {
    renderTaskStatus(taskId, "ERROR", err.message);
    notify(err.message, "error");
    log("Check task failed", err.message);
  }
});

document.getElementById("clear-log").addEventListener("click", () => {
  activityEl.innerHTML = "";
});

// Greet
log("UI ready", "Use the forms to interact with the API.");

// ---------------------------------------------------------------------
// User Management Logic
// ---------------------------------------------------------------------

const usersTableBody = document.querySelector("#users-table tbody");
const refreshUsersBtn = document.getElementById("btn-refresh-users");
const editModal = document.getElementById("edit-modal");
const editForm = document.getElementById("form-user-edit");
const closeModalBtn = document.querySelector(".close-modal");
const cancelModalBtn = document.querySelector(".cancel-modal");

const fetchUsers = async () => {
  if (!usersTableBody) {
    console.error("Users table body not found in DOM");
    return;
  }
  try {
    const res = await fetch("/users");
    if (!res.ok) throw new Error("Failed to fetch users");
    const users = await res.json();
    renderUsersTable(users);
    log("Fetched users list", `${users.length} users`);
  } catch (err) {
    notify(err.message, "error");
    log("Error fetching users", err.message);
  }
};

const renderUsersTable = (users) => {
  usersTableBody.innerHTML = "";
  if (users.length === 0) {
    usersTableBody.innerHTML = "<tr><td colspan=\"6\">No users found.</td></tr>";
    return;
  }
  users.forEach((user) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${user.id}</td>
      <td>${user.first_name}</td>
      <td>${user.last_name}</td>
      <td>${user.mail}</td>
      <td>${user.age}</td>
      <td>
        <button class=\"btn-sm btn-edit\" onclick=\"openEditModal(${user.id})\">Edit</button>
        <button class=\"btn-sm btn-danger\" onclick=\"deleteUser(${user.id})\">Delete</button>
      </td>
    `;
    usersTableBody.appendChild(tr);
  });
};

const deleteUser = async (userId) => {
  if (!confirm("Are you sure you want to delete this user?")) return;
  try {
    const res = await fetch(`/users/${userId}`, { method: "DELETE" });
    if (!res.ok) throw new Error("Failed to delete user");
    notify("User deleted successfully", "success");
    log("Deleted user", `ID: ${userId}`);
    fetchUsers();
  } catch (err) {
    notify(err.message, "error");
    log("Error deleting user", err.message);
  }
};

// Expose deleteUser to global scope for onclick
window.deleteUser = deleteUser;

// Edit Modal Logic
const openEditModal = async (userId) => {
  try {
    const res = await fetch(`/users/${userId}`);
    if (!res.ok) throw new Error("Failed to fetch user details");
    const user = await res.json();
    
    editForm.id.value = user.id;
    editForm.firstName.value = user.first_name;
    editForm.lastName.value = user.last_name;
    editForm.mail.value = user.mail;
    editForm.age.value = user.age;
    
    editModal.classList.remove("hidden");
  } catch (err) {
    notify(err.message, "error");
  }
};

// Expose openEditModal to global scope
window.openEditModal = openEditModal;

const closeEditModal = () => {
  editModal.classList.add("hidden");
  editForm.reset();
};

closeModalBtn.addEventListener("click", closeEditModal);
cancelModalBtn.addEventListener("click", closeEditModal);

editForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const userId = editForm.id.value;
  const payload = {
    first_name: editForm.firstName.value,
    last_name: editForm.lastName.value,
    mail: editForm.mail.value,
    age: parseInt(editForm.age.value),
  };

  try {
    const res = await fetch(`/users/${userId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error("Failed to update user");
    
    notify("User updated successfully", "success");
    log("Updated user", `ID: ${userId}`);
    closeEditModal();
    fetchUsers();
  } catch (err) {
    notify(err.message, "error");
    log("Error updating user", err.message);
  }
});

refreshUsersBtn.addEventListener("click", fetchUsers);

// Initial fetch
fetchUsers();

