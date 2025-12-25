async function signup(email, password) {
  const res = await fetch(`${API_BASE}/auth/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Signup failed");
  alert("Signup successful. Please login.");
  window.location.href = "login.html";
}

async function login(email, password) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Login failed");

  localStorage.setItem("token", data.access_token);
  window.location.href = "files.html";
}

function logout() {
  localStorage.removeItem("token");
  window.location.href = "login.html";
}
