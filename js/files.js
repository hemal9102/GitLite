const tableBody = document.getElementById("fileTableBody");
const uploadBtn = document.getElementById("uploadBtn");
const fileInput = document.getElementById("fileInput");

// small set of mock commit-like metadata to make the UI look GitHub-ish
const mockCommits = [
  { message: "Initial upload", author: "you", date: "3 weeks ago" },
  { message: "Update content", author: "you", date: "2 weeks ago" },
  { message: "Rename file", author: "you", date: "last month" },
];

async function loadFiles() {
  tableBody.innerHTML = "";
  const files = await fetchFiles();

  files.forEach((file, idx) => {
    const tr = document.createElement("tr");
    const commit = mockCommits[idx % mockCommits.length];

    tr.innerHTML = `
      <td>${file.id}</td>
      <td>
        <span class="file-icon">${getFileIcon(file.filename)}</span>
        <a href="#" onclick="handleDownload(${file.id});return false;">${
      file.filename || "unknown"
    }</a>
      </td>
      <td>${file.content_type || "-"}</td>
      <td>
        <button class="btn" onclick="handleDownload(${file.id})">Download</button>
        <button class="btn" onclick="handleDelete(${file.id})">Delete</button>
      </td>
    `;

    tableBody.appendChild(tr);
  });
}

function getFileIcon(filename) {
  if (!filename) return "📄";
  const ext = filename.split(".").pop().toLowerCase();
  switch (ext) {
    case "png":
    case "jpg":
    case "jpeg":
    case "gif":
      return "🖼️";
    case "pdf":
      return "📄";
    case "py":
      return "🐍";
    case "js":
      return "💻";
    case "css":
      return "🎨";
    case "md":
      return "📘";
    case "zip":
    case "rar":
      return "📦";
    default:
      return "📄";
  }
}

async function handleDelete(id) {
  if (!confirm("Delete this file?")) return;
  await deleteFile(id);
  loadFiles();
}

async function handleDownload(id) {
  try {
    await downloadFile(id);
  } catch (err) {
    alert("Download failed: " + (err.message || err));
  }
}

uploadBtn?.addEventListener("click", async () => {
  if (!fileInput.files.length) {
    alert("Select a file first");
    return;
  }

  await uploadFile(fileInput.files[0]);
  fileInput.value = "";
  loadFiles();
});

loadFiles();
