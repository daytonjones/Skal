// static/js/batches.js

// Checklist date auto-fill
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll('input[id$="_done"]').forEach(function(chk) {
    chk.addEventListener('change', function() {
      const dateId = this.id.replace(/_done$/, '_date');
      const dateInput = document.getElementById(dateId);
      if (!dateInput) return;
      if (this.checked) {
        if (!dateInput.value) {
          dateInput.value = new Date().toISOString().split('T')[0];
        }
      } else {
        dateInput.value = '';
      }
    });
  });
});

// Image preview and drag-to-reorder
document.addEventListener("DOMContentLoaded", () => {
  const fileInput = document.getElementById("id_images");
  const container = document.getElementById("image-preview-container");

  if (!fileInput || !container) return;

  fileInput.addEventListener("change", handleFiles);

  function handleFiles() {
    const files = Array.from(fileInput.files);
    container.innerHTML = "";

    files.forEach((file, index) => {
      const reader = new FileReader();
      reader.onload = function (e) {
        const preview = document.createElement("div");
        preview.classList.add("image-preview");
        preview.setAttribute("draggable", "true");
        preview.dataset.index = index;

        preview.innerHTML = `
          <img src="${e.target.result}" alt="Image Preview" style="max-width:100%; border-radius:6px;">
          <label>Caption:</label>
          <input type="text" name="caption_${index}" class="caption-input" placeholder="Optional caption" />
        `;

        addDragHandlers(preview);
        container.appendChild(preview);
      };
      reader.readAsDataURL(file);
    });
  }

  function addDragHandlers(element) {
    element.addEventListener("dragstart", dragStart);
    element.addEventListener("dragover", dragOver);
    element.addEventListener("drop", drop);
  }

  function dragStart(e) {
    e.dataTransfer.setData("text/plain", e.target.dataset.index);
    e.target.classList.add("dragging");
  }

  function dragOver(e) {
    e.preventDefault();
    const dragging = document.querySelector(".dragging");
    const target = e.currentTarget;
    if (dragging && dragging !== target) {
      const children = Array.from(container.children);
      const dragIndex = children.indexOf(dragging);
      const targetIndex = children.indexOf(target);
      if (dragIndex < targetIndex) {
        container.insertBefore(dragging, target.nextSibling);
      } else {
        container.insertBefore(dragging, target);
      }
    }
  }

  function drop(e) {
    e.preventDefault();
    document.querySelectorAll(".dragging").forEach(el => el.classList.remove("dragging"));
  }
});

