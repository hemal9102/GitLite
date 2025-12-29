async function fetchFiles() {
  const res = await fetch(`${API_BASE}/files/`, {
    headers: authHeaders(),
  });
  if (res.status === 401) logout();
  return res.json();
}

async function uploadFile(file) {
  const formData = new FormData();
  // backend expects the form field to be named 'file'
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/files/`, {
    method: "POST",
    headers: authHeaders(),
    body: formData,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "Upload failed");
  }
}

async function deleteFile(id) {
  const res = await fetch(`${API_BASE}/files/${id}`, {
    method: "DELETE",
    headers: authHeaders(),
  });

  if (!res.ok) throw new Error("Delete failed");
}
