const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("fileInput");
const fileNameDisplay = document.getElementById("fileName");
const modeSelect = document.getElementById("modeSelect");
const resizeBtn = document.getElementById("resizeBtn");
const statusText = document.getElementById("status");

const panels = {
  preset: document.getElementById("presetControls"),
  custom: document.getElementById("customControls"),
  dimensions: document.getElementById("dimensionControls"),
  target: document.getElementById("targetControls"),
};

let selectedFile = null;
let lastDownloadUrl = null;

// Show the relevant control panel when the resize mode changes
modeSelect.addEventListener("change", () => {
  Object.values(panels).forEach((p) => {
    if (p) p.hidden = true;
  });
  if (panels[modeSelect.value]) {
    panels[modeSelect.value].hidden = false;
  }
});

// Range slider value update
const scaleSlider = document.getElementById("scaleSlider");
const qualitySlider = document.getElementById("qualitySlider");

if (scaleSlider) {
  scaleSlider.addEventListener("input", (e) => {
    document.getElementById("sVal").innerText = e.target.value;
  });
}

if (qualitySlider) {
  qualitySlider.addEventListener("input", (e) => {
    document.getElementById("qVal").innerText = e.target.value;
  });
}

// Dropzone click & drag-and-drop events
dropZone.addEventListener("click", () => fileInput.click());

fileInput.addEventListener("change", (e) => {
  if (e.target.files.length > 0) {
    handleFileSelect(e.target.files[0]);
  }
});

dropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropZone.style.background = "#e2eeff";
});

dropZone.addEventListener("dragleave", () => {
  dropZone.style.background = "#f8fbff";
});

dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropZone.style.background = "#f8fbff";
  if (e.dataTransfer.files.length > 0) {
    handleFileSelect(e.dataTransfer.files[0]);
  }
});

function handleFileSelect(file) {
  if (!file) return;
  selectedFile = file;
  const sizeKb = (file.size / 1024).toFixed(1);
  fileNameDisplay.innerHTML = `Selected: <strong>${file.name}</strong> (${sizeKb} KB)`;
  statusText.innerText = "";
}

// Resize & Download button click handler
resizeBtn.addEventListener("click", async (e) => {
  e.preventDefault();

  if (!selectedFile) {
    alert("Please select a file first.");
    return;
  }

  // Revoke the previous object URL to free up memory if it exists
  if (lastDownloadUrl) {
    window.URL.revokeObjectURL(lastDownloadUrl);
    lastDownloadUrl = null;
  }

  statusText.style.color = "#1f2937";
  statusText.innerText = "Compressing & resizing file, please wait...";
  resizeBtn.disabled = true;
  resizeBtn.innerText = "Processing...";

  const formData = new FormData();
  formData.append("file", selectedFile);

  const mode = modeSelect.value;

  if (mode === "preset") {
    const level = document.getElementById("presetLevel").value;
    const presets = {
      light: { scale: 0.9, quality: 85 },
      medium: { scale: 0.7, quality: 70 },
      strong: { scale: 0.5, quality: 55 },
    };
    formData.append("scale", presets[level].scale);
    formData.append("quality", presets[level].quality);
  } else if (mode === "custom") {
    formData.append("scale", scaleSlider.value / 100);
    formData.append("quality", qualitySlider.value);
  } else if (mode === "dimensions") {
    const w = document.getElementById("maxWidth").value;
    const h = document.getElementById("maxHeight").value;
    if (w) formData.append("max_width", w);
    if (h) formData.append("max_height", h);
    formData.append("quality", 80);
  } else if (mode === "target") {
    const kb = document.getElementById("targetKb").value;
    if (!kb || Number(kb) <= 0) {
      statusText.style.color = "#dc2626";
      statusText.innerText = "Please enter a valid target size in KB.";
      resizeBtn.disabled = false;
      resizeBtn.innerText = "Resize & Download";
      return;
    }
    formData.append("target_kb", kb);
  }

  try {
    // Using the relative path "/api/resize" works best when served from a FastAPI server
    const response = await fetch("/api/resize", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      let errorMsg = "Resize failed on server.";
      try {
        const errData = await response.json();
        errorMsg = errData.detail || errorMsg;
      } catch (_) {}
      throw new Error(errorMsg);
    }

    const blob = await response.blob();
    const oldKb = (selectedFile.size / 1024).toFixed(1);
    const newKb = (blob.size / 1024).toFixed(1);
    const savedPct = (((selectedFile.size - blob.size) / selectedFile.size) * 100).toFixed(0);

    lastDownloadUrl = window.URL.createObjectURL(blob);
    const downloadName = `resized_${selectedFile.name}`;

    // Automatic download trigger
    const a = document.createElement("a");
    a.style.display = "none";
    a.href = lastDownloadUrl;
    a.download = downloadName;
    document.body.appendChild(a);
    a.click();

    // Status + Manual fallback download link
    statusText.style.color = "#059669";
    statusText.innerHTML = `
      Done! <strong>${oldKb} KB → ${newKb} KB</strong> (${savedPct > 0 ? savedPct + "% smaller" : "optimized"})<br>
      <a href="${lastDownloadUrl}" download="${downloadName}" style="display:inline-block; margin-top:8px; color:#2563eb; text-decoration:underline; font-weight:600;">
        Click here if download didn't start automatically
      </a>
    `;
  } catch (error) {
    statusText.style.color = "#dc2626";
    statusText.innerText = `Error: ${error.message}`;
  } finally {
    resizeBtn.disabled = false;
    resizeBtn.innerText = "Resize & Download";
  }
});