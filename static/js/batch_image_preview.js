document.addEventListener('DOMContentLoaded', () => {
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('id_images');
  const preview = document.getElementById('preview');
  let files = [];

  dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
  });

  dropzone.addEventListener('dragleave', () => {
    dropzone.classList.remove('dragover');
  });

  dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    handleFiles(e.dataTransfer.files);
  });

  dropzone.addEventListener('click', () => fileInput.click());
  fileInput.addEventListener('change', () => handleFiles(fileInput.files));

  function handleFiles(fileList) {
    files = Array.from(fileList);
    renderPreviews();
  }

  function renderPreviews() {
    preview.innerHTML = '';
    files.forEach((file, index) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const wrapper = document.createElement('div');
        wrapper.className = 'image-wrapper';
        wrapper.draggable = true;
        wrapper.dataset.index = index;

        const img = document.createElement('img');
        img.src = e.target.result;
        img.alt = file.name;

        const captionInput = document.createElement('input');
        captionInput.type = 'text';
        captionInput.name = 'image_captions';
        captionInput.placeholder = 'Caption';
        captionInput.className = 'caption-input';

        const hiddenFile = document.createElement('input');
        hiddenFile.type = 'hidden';
        hiddenFile.name = 'image_order';
        hiddenFile.value = index;

        wrapper.appendChild(img);
        wrapper.appendChild(captionInput);
        wrapper.appendChild(hiddenFile);
        preview.appendChild(wrapper);
      };
      reader.readAsDataURL(file);
    });

    enableReordering();
  }

  function enableReordering() {
    let dragged;

    preview.addEventListener('dragstart', (e) => {
      dragged = e.target;
      e.dataTransfer.effectAllowed = 'move';
    });

    preview.addEventListener('dragover', (e) => {
      e.preventDefault();
      const target = e.target.closest('.image-wrapper');
      if (target && target !== dragged) {
        const children = Array.from(preview.children);
        const draggedIndex = children.indexOf(dragged);
        const targetIndex = children.indexOf(target);
        if (draggedIndex < targetIndex) {
          preview.insertBefore(dragged, target.nextSibling);
        } else {
          preview.insertBefore(dragged, target);
        }
      }
    });

    preview.addEventListener('dragend', () => {
      updateOrderInputs();
    });
  }

  function updateOrderInputs() {
    const wrappers = preview.querySelectorAll('.image-wrapper');
    wrappers.forEach((wrapper, index) => {
      const orderInput = wrapper.querySelector('input[name="image_order"]');
      orderInput.value = index;
    });
  }
});

