const BASE = (typeof API_BASE !== 'undefined') ? API_BASE : '';

async function fetchFiles() {
  try {
    const res = await fetch(`${BASE}/files/?skip=0&limit=50`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  } catch (err) {
    console.error('fetchFiles error', err);
    throw err;
  }
}

async function uploadFile(file) {
  try {
    const formData = new FormData();
    // backend expects field name 'uploaded_file'
    formData.append("uploaded_file", file);

    const res = await fetch(`${BASE}/files/`, {
      method: "POST",
      body: formData
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  } catch (err) {
    console.error('uploadFile error', err);
    throw err;
  }
}

async function deleteFile(id) {
  try {
    const res = await fetch(`${BASE}/files/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  } catch (err) {
    console.error('deleteFile error', err);
    throw err;
  }
}

async function downloadFile(id) {
  try {
    // Use the download endpoint we added on the backend
    const url = `${BASE}/files/download/${id}`;
    // trigger browser navigation to download the file
    window.location.href = url;
  } catch (err) {
    console.error('downloadFile error', err);
    throw err;
  }
}
