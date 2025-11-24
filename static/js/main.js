// Auto-dismiss alerts after 5 seconds
setTimeout(() => {
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
    });
}, 5000);

// Confirm delete actions
function confirmDelete(message = 'Вы уверены, что хотите удалить эту запись?') {
    return confirm(message);
}

// Simple search functionality
function setupTableSearch(inputId, tableId) {
    const searchInput = document.getElementById(inputId);
    if (!searchInput) return;
    
    searchInput.addEventListener('input', function() {
        const searchText = this.value.toLowerCase();
        const rows = document.querySelectorAll(`#${tableId} tbody tr`);
        
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(searchText) ? '' : 'none';
        });
    });
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Initialize table searches
    setupTableSearch('searchInput', 'studentsTable');
    setupTableSearch('coursesSearch', 'coursesTable');
    setupTableSearch('groupsSearch', 'groupsTable');
});