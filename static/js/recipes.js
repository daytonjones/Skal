document.addEventListener('DOMContentLoaded', () => {
  const addBtn = document.getElementById('add-ingredient');
  if (!addBtn) return;

  addBtn.addEventListener('click', e => {
    e.preventDefault();

    // Find how many forms are currently rendered
    const totalFormsInput = document.querySelector('input[name$="-TOTAL_FORMS"]');
    const total = parseInt(totalFormsInput.value, 10);

    // Grab the hidden template row
    const emptyRow = document.getElementById('empty-form-row');
    const newRow = emptyRow.cloneNode(true);
    newRow.removeAttribute('id');
    newRow.style.display = '';

    // Rename each input inside the clone from "__prefix__" → the new index
    newRow.querySelectorAll('input').forEach(input => {
      if (input.name) {
        input.name = input.name.replace('__prefix__', total);
      }
      if (input.id) {
        input.id = input.id.replace('__prefix__', total);
      }
      // clear any value/checked state
      if (input.type === 'checkbox') {
        input.checked = false;
      } else {
        input.value = '';
      }
    });

    // Append into our <tbody id="ingredient-rows">
    const tbody = document.getElementById('ingredient-rows');
    tbody.appendChild(newRow);

    // Tell Django there's one more form now
    totalFormsInput.value = total + 1;
  });
});

