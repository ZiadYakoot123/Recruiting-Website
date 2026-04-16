const API = localStorage.getItem("apiBase") || "http://127.0.0.1:8000";

function token() { return localStorage.getItem("token"); }
function authHeaders() {
  const t = token();
  return t ? { Authorization: `Bearer ${t}` } : {};
}
async function request(path, opts = {}) {
  const res = await fetch(`${API}${path}`, {
    ...opts,
    headers: { "Content-Type": "application/json", ...(opts.headers || {}), ...authHeaders() },
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(body.detail || body.message || "Request failed");
  return body;
}
function show(id, msg, isError = false) {
  const el = document.getElementById(id);
  if (!el) return;
  el.className = isError ? "error" : "small";
  el.textContent = msg;
}
