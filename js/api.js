async function fetchFiles() {
  const res = await fetch(`${API_BASE}/files/`, {
    headers: authHeaders(),
  });
  if (res.status === 401) logout();
  return res.json();
}

async function uploadFile(file) {
  const formData = new FormData();
  formData.append("uploaded_file", file);

  const res = await fetch(`${API_BASE}/files/`, {
    method: "POST",
    headers: authHeaders(),
    body: formData,
  });

  if (!res.ok) throw new Error("Upload failed");
}

async function deleteFile(id) {
  const res = await fetch(`${API_BASE}/files/${id}`, {
    method: "DELETE",
    headers: authHeaders(),
  });

  if (!res.ok) throw new Error("Delete failed");
}
