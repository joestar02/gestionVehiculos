document.addEventListener('DOMContentLoaded', function() {
    // Only run if we're on the vehicle detail page
    if (!document.getElementById('historyTabs')) return;

    // Handle filter all checkbox
    const filterAll = document.getElementById('filterAll');
    const eventFilters = document.querySelectorAll('.event-filter');
    
    if (filterAll) {
        filterAll.addEventListener('change', function() {
            const isChecked = this.checked;
            eventFilters.forEach(filter => {
                filter.checked = isChecked;
            });
        });
    }
    
    // Handle individual filter changes
    eventFilters.forEach(filter => {
        filter.addEventListener('change', function() {
            if (!this.checked) {
                if (filterAll) filterAll.checked = false;
            } else {
                // Check if all filters are checked
                const allChecked = Array.from(eventFilters).every(f => f.checked);
                if (filterAll) filterAll.checked = allChecked;
            }
        });
    });
    
    // Apply filters
    const applyFiltersBtn = document.getElementById('applyFilters');
    if (applyFiltersBtn) {
        applyFiltersBtn.addEventListener('click', function() {
            const dateFrom = document.getElementById('dateFrom')?.value;
            const dateTo = document.getElementById('dateTo')?.value;
            const activeTab = document.querySelector('#historyTabs .nav-link.active')?.getAttribute('data-bs-target');
            
            // Get all history items in the active tab
            const activePane = document.querySelector(activeTab || '#all');
            if (!activePane) return;
            
            const historyItems = activePane.querySelectorAll('.list-group-item');
            
            historyItems.forEach(item => {
                let showItem = true;
                const dateElement = item.querySelector('small.text-muted');
                if (!dateElement) return;
                
                const dateText = dateElement.textContent.trim();
                const [day, month, year] = dateText.split('/').map(Number);
                const itemDate = new Date(year, month - 1, day);
                
                // Filter by date
                if (dateFrom) {
                    const [fromYear, fromMonth, fromDay] = dateFrom.split('-').map(Number);
                    const fromDate = new Date(fromYear, fromMonth - 1, fromDay);
                    if (itemDate < fromDate) showItem = false;
                }
                
                if (dateTo) {
                    const [toYear, toMonth, toDay] = dateTo.split('-').map(Number);
                    const toDate = new Date(toYear, toMonth - 1, toDay);
                    toDate.setHours(23, 59, 59, 999); // End of the day
                    if (itemDate > toDate) showItem = false;
                }
                
                // Apply visibility
                item.style.display = showItem ? 'block' : 'none';
            });
            
            // Close modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('historyFilters'));
            if (modal) modal.hide();
        });
    }
    
    // Reset filters when showing the modal
    const historyFiltersModal = document.getElementById('historyFilters');
    if (historyFiltersModal) {
        historyFiltersModal.addEventListener('show.bs.modal', function() {
            const form = document.getElementById('historyFiltersForm');
            if (form) form.reset();
            if (filterAll) filterAll.checked = true;
            eventFilters.forEach(filter => {
                filter.checked = true;
            });
        });
    }
    
    // Handle tab changes to reset filters
    const tabLinks = document.querySelectorAll('#historyTabs .nav-link');
    tabLinks.forEach(link => {
        link.addEventListener('shown.bs.tab', function() {
            // Show all items when changing tabs
            const tabContent = document.querySelector(this.getAttribute('data-bs-target'));
            if (tabContent) {
                tabContent.querySelectorAll('.list-group-item').forEach(item => {
                    item.style.display = 'block';
                });
            }
        });
    });
});
