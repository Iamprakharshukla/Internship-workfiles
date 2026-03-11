/* ================= PDF.JS SETUP ================= */
pdfjsLib.GlobalWorkerOptions.workerSrc =
  "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";

/* ================= STATE ================= */
let pdfDoc = null;
let currentPage = 1;
let totalPages = 0;
let scale = 1.3;
let currentFile = "";

/* ================= DOM READY ================= */
document.addEventListener("DOMContentLoaded", () => {
  const canvas = document.getElementById("pdfCanvas");
  const ctx = canvas.getContext("2d");

  const pageInput = document.getElementById("pageInput");
  const totalPagesEl = document.getElementById("totalPages");
  const zoomLevel = document.getElementById("zoomLevel");

  const loadingEl = document.getElementById("pdfLoading");
  const errorEl = document.getElementById("pdfError");

  /* ================= YEAR TABS ================= */
  document.querySelectorAll(".year-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".year-tab").forEach(t =>
        t.classList.remove("active")
      );
      tab.classList.add("active");

      currentPage = 1;
      scale = 1.3;

      loadPDF(tab.dataset.file);
    });
  });

  /* ================= TOOLBAR ================= */
  document.getElementById("prevBtn").onclick = () => {
    if (currentPage > 1) {
      currentPage--;
      pageInput.value = currentPage;
      renderPage(currentPage);
    }
  };

  document.getElementById("nextBtn").onclick = () => {
    if (currentPage < totalPages) {
      currentPage++;
      pageInput.value = currentPage;
      renderPage(currentPage);
    }
  };

  pageInput.onchange = () => {
    const page = parseInt(pageInput.value);
    if (page >= 1 && page <= totalPages) {
      currentPage = page;
      renderPage(currentPage);
    }
  };

  document.getElementById("zoomIn").onclick = () => {
    scale += 0.2;
    renderPage(currentPage);
  };

  document.getElementById("zoomOut").onclick = () => {
    if (scale > 0.6) {
      scale -= 0.2;
      renderPage(currentPage);
    }
  };

  document.getElementById("downloadBtn").onclick = () => {
    if (!currentFile) return;
    const a = document.createElement("a");
    a.href = currentFile;
    a.download = currentFile.split("/").pop();
    a.click();
  };

  document.getElementById("fullscreenBtn").onclick = () => {
    const viewer = document.getElementById("reportViewer");
    if (!document.fullscreenElement) {
      viewer.requestFullscreen();
    } else {
      document.exitFullscreen();
    }
  };

  /* ================= LOAD FIRST PDF ================= */
  const firstTab = document.querySelector(".year-tab.active");
  if (firstTab) {
    loadPDF(firstTab.dataset.file);
  }

  /* ================= FUNCTIONS ================= */

  async function loadPDF(file) {
    currentFile = file;
    showLoading(true);
    hideError();

    try {
      pdfDoc = await pdfjsLib.getDocument(file).promise;
      totalPages = pdfDoc.numPages;

      totalPagesEl.textContent = totalPages;
      pageInput.value = 1;
      pageInput.max = totalPages;

      renderPage(currentPage);
    } catch (err) {
      console.error("PDF load error:", err);
      showError();
    } finally {
      showLoading(false);
    }
  }

  async function renderPage(pageNum) {
    if (!pdfDoc) return;

    const page = await pdfDoc.getPage(pageNum);
    const viewport = page.getViewport({ scale });

    canvas.width = viewport.width;
    canvas.height = viewport.height;

    await page.render({
      canvasContext: ctx,
      viewport
    }).promise;

    zoomLevel.textContent = Math.round(scale * 100) + "%";
  }

  function showLoading(show) {
    loadingEl.style.display = show ? "flex" : "none";
  }

  function showError() {
    errorEl.style.display = "flex";
  }

  function hideError() {
    errorEl.style.display = "none";
  }
});
