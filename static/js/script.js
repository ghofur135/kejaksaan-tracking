document.addEventListener('DOMContentLoaded', function() {
    const editableCells = document.querySelectorAll('.editable');
    const dateCells = document.querySelectorAll('.date-cell');
    const dateModal = document.getElementById('dateModal');
    const modalInput = document.getElementById('modalDateInput');
    const saveBtn = document.getElementById('saveDateBtn');
    const cancelBtn = document.getElementById('cancelDateBtn');

    // Delete Modal Elements
    const deleteModal = document.getElementById('deleteModal');
    const deleteMessage = document.getElementById('deleteMessage');
    const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
    const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');
    const deleteButtons = document.querySelectorAll('.btn-delete');
    
    // Pagination Elements
    const perPageSelect = document.getElementById('perPageSelect');

    let currentCell = null;
    let currentDeleteId = null;

    // Handle Per Page Change
    if (perPageSelect) {
        perPageSelect.addEventListener('change', function() {
            const urlParams = new URLSearchParams(window.location.search);
            urlParams.set('per_page', this.value);
            urlParams.set('page', '1'); // Reset to first page
            window.location.search = urlParams.toString();
        });
    }

    // Handle ContentEditable (Text areas)
    editableCells.forEach(cell => {
        let originalContent = cell.innerText;
        cell.addEventListener('focus', function() { originalContent = cell.innerText; });
        cell.addEventListener('blur', function() {
            const newContent = cell.innerText.trim();
            if (newContent !== originalContent) {
                saveData(cell.dataset.id, cell.dataset.field, newContent);
            }
        });
        cell.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') { e.preventDefault(); cell.blur(); }
        });
    });

    // Handle Date Cells - Open Modal
    dateCells.forEach(cell => {
        cell.addEventListener('click', function() {
            currentCell = cell;
            const currentVal = cell.dataset.value;
            
            // Try to parse existing value to ISO format for input
            // Format in DB might be '2025-07-09 00:00:00', input needs '2025-07-09T00:00'
            let isoValue = '';
            if (currentVal && currentVal.length > 5) {
                // simple heuristic replace space with T
                isoValue = currentVal.replace(' ', 'T').substring(0, 16);
            }
            
            modalInput.value = isoValue;
            dateModal.style.display = 'flex';
        });
    });

    // Modal Actions
    cancelBtn.addEventListener('click', function() {
        dateModal.style.display = 'none';
        currentCell = null;
    });

    saveBtn.addEventListener('click', function() {
        if (!currentCell) return;
        
        const newValue = modalInput.value; // YYYY-MM-DDTHH:MM
        // Format nicely for display (optional, backend can do it, but let's keep it raw text for now)
        // Or better: convert T back to space
        const displayValue = newValue.replace('T', ' ');
        
        // Save to backend
        saveData(currentCell.dataset.id, currentCell.dataset.field, displayValue, true);
        
        dateModal.style.display = 'none';
    });

    // Handle Delete Buttons
    deleteButtons.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            currentDeleteId = this.dataset.id;
            const caseName = this.dataset.name;
            deleteMessage.textContent = `Apakah Anda yakin ingin menghapus data "${caseName}"?`;
            deleteModal.style.display = 'flex';
        });
    });

    // Delete Modal Actions
    cancelDeleteBtn.addEventListener('click', function() {
        deleteModal.style.display = 'none';
        currentDeleteId = null;
    });

    confirmDeleteBtn.addEventListener('click', function() {
        if (!currentDeleteId) return;
        
        fetch(`/delete_case/${currentDeleteId}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                deleteModal.style.display = 'none';
                window.location.reload();
            } else {
                alert('Gagal menghapus: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Kesalahan koneksi');
        });
    });

    function saveData(id, field, value, reload = false) {
        fetch('/update_cell', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id: id, field: field, value: value })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                if (reload) {
                    window.location.reload();
                } else if (!reload) {
                    // Update UI manually if not reloading
                    // currentCell.innerText = value; // simple update
                }
            } else {
                alert('Gagal menyimpan: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Kesalahan koneksi');
        });
    }
});
