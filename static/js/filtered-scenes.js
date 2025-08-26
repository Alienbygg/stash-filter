/**
 * Filtered Scenes Management JavaScript
 * Handles all frontend interactions for the filtered scenes page
 */

class FilteredScenesManager {
    constructor() {
        this.currentPage = 1;
        this.perPage = 20;
        this.currentFilters = {};
        this.selectedScenes = new Set();
        this.stats = {};
        
        this.init();
    }
    
    async init() {
        this.bindEvents();
        await this.loadStats();
        await this.loadFilteredScenes();
        this.setupAutoRefresh();
    }
    
    bindEvents() {
        // Form submission
        document.getElementById('filter-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.applyFilters();
        });
        
        // Exception type change
        document.getElementById('exception-type').addEventListener('change', (e) => {
            this.toggleExpirationField(e.target.value);
        });
        
        // Bulk exception type change
        const bulkTypeSelect = document.querySelector('#bulk-exception-form select[name="type"]');
        if (bulkTypeSelect) {
            bulkTypeSelect.addEventListener('change', (e) => {
                this.toggleBulkExpirationField(e.target.value);
            });
        }
        
        // Real-time search
        let searchTimeout;
        document.getElementById('search').addEventListener('input', (e) => {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                this.applyFilters();
            }, 500);
        });
        
        // Filter changes
        ['filter-reason', 'exception-status', 'date-from', 'date-to'].forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.addEventListener('change', () => {
                    this.applyFilters();
                });
            }
        });
    }
    
    async loadStats() {
        try {
            const response = await fetch('/api/filtered-scenes/stats');
            const data = await response.json();
            
            if (data.status === 'success') {
                this.stats = data;
                this.updateStatsDisplay();
            } else {
                console.error('Failed to load stats:', data.message);
            }
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }
    
    updateStatsDisplay() {
        document.getElementById('total-filtered').textContent = this.stats.total_filtered || 0;
        document.getElementById('total-exceptions').textContent = this.stats.total_exceptions || 0;
        document.getElementById('exception-rate').textContent = this.stats.exception_rate + '%' || '0%';
        
        // Update top filter reason
        if (this.stats.filter_reasons && this.stats.filter_reasons.length > 0) {
            const topReason = this.stats.filter_reasons[0];
            document.getElementById('top-filter-reason').textContent = this.formatFilterReason(topReason.reason);
            document.getElementById('top-filter-count').textContent = `${topReason.count} scenes`;
        } else {
            document.getElementById('top-filter-reason').textContent = 'None';
            document.getElementById('top-filter-count').textContent = 'No data';
        }
    }
    
    async loadFilteredScenes(page = 1) {
        this.currentPage = page;
        
        try {
            this.showLoading();
            
            // Build query parameters
            const params = new URLSearchParams({
                page: page,
                per_page: this.perPage,
                ...this.currentFilters
            });
            
            const response = await fetch(`/api/filtered-scenes?${params}`);
            const data = await response.json();
            
            if (data.status === 'success') {
                this.renderScenesTable(data.scenes);
                this.renderPagination(data.pagination);
                document.getElementById('scene-count').textContent = data.pagination.total;
            } else {
                this.showError('Failed to load filtered scenes: ' + data.message);
            }
        } catch (error) {
            console.error('Error loading filtered scenes:', error);
            this.showError('Failed to load filtered scenes');
        } finally {
            this.hideLoading();
        }
    }
    
    renderScenesTable(scenes) {
        const tbody = document.getElementById('scenes-table');
        
        if (scenes.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="9" class="text-center py-4 text-muted">
                        <i class="fas fa-search fa-2x mb-3"></i>
                        <div>No filtered scenes found matching your criteria</div>
                        <small>Try adjusting your filters or search terms</small>
                    </td>
                </tr>
            `;
            return;
        }
        
        tbody.innerHTML = scenes.map(scene => this.renderSceneRow(scene)).join('');
    }
    
    renderSceneRow(scene) {
        const filteredDate = new Date(scene.filtered_date).toLocaleDateString();
        const performers = scene.performers ? scene.performers.slice(0, 2).join(', ') : 'Unknown';
        const remainingCount = scene.performers ? Math.max(0, scene.performers.length - 2) : 0;
        
        return `
            <tr data-scene-id="${scene.id}" ${this.selectedScenes.has(scene.id) ? 'class="table-active"' : ''}>
                <td>
                    <input type="checkbox" class="form-check-input scene-checkbox" 
                           value="${scene.id}" onchange="filteredScenesManager.toggleSceneSelection(${scene.id})">
                </td>
                <td>
                    ${scene.thumbnail_url ? 
                        `<img src="${scene.thumbnail_url}" alt="Thumbnail" class="scene-thumbnail">` :
                        `<div class="scene-thumbnail-placeholder"><i class="fas fa-image"></i></div>`
                    }
                </td>
                <td>
                    <div class="fw-semibold">${this.escapeHtml(scene.title)}</div>
                    ${scene.duration_minutes ? `<small class="text-muted">${scene.duration_minutes}min</small>` : ''}
                </td>
                <td>
                    <div class="performers-list" title="${scene.performers ? scene.performers.join(', ') : ''}">
                        ${performers}
                        ${remainingCount > 0 ? `<small class="text-muted"> +${remainingCount} more</small>` : ''}
                    </div>
                </td>
                <td>
                    <span class="text-muted">${scene.studio || 'Unknown'}</span>
                </td>
                <td>
                    <span class="badge filter-reason-badge ${this.getFilterReasonClass(scene.filter_reason)}">
                        ${this.formatFilterReason(scene.filter_reason)}
                    </span>
                </td>
                <td>
                    <small class="text-muted">${filteredDate}</small>
                </td>
                <td>
                    ${scene.is_exception ? 
                        `<span class="badge bg-success exception-status">
                            <i class="fas fa-check"></i> Exception
                         </span>` :
                        `<span class="badge bg-secondary exception-status">
                            <i class="fas fa-times"></i> Filtered
                         </span>`
                    }
                </td>
                <td>
                    <div class="btn-group btn-group-sm" role="group">
                        <button type="button" class="btn btn-outline-info" title="View Details"
                                onclick="filteredScenesManager.showSceneDetails(${scene.id})">
                            <i class="fas fa-eye"></i>
                        </button>
                        ${!scene.is_exception ? `
                            <button type="button" class="btn btn-outline-success" title="Create Exception"
                                    onclick="filteredScenesManager.showExceptionModal(${scene.id})">
                                <i class="fas fa-check"></i>
                            </button>
                        ` : `
                            <button type="button" class="btn btn-outline-warning" title="Manage Exception"
                                    onclick="filteredScenesManager.manageException(${scene.id})">
                                <i class="fas fa-cog"></i>
                            </button>
                        `}
                        <button type="button" class="btn btn-outline-danger" title="Delete"
                                onclick="filteredScenesManager.deleteFilteredScene(${scene.id})">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }
    
    renderPagination(pagination) {
        const paginationEl = document.getElementById('pagination');
        
        if (pagination.pages <= 1) {
            paginationEl.innerHTML = '';
            return;
        }
        
        let html = '';
        
        // Previous button
        html += `
            <li class="page-item ${!pagination.has_prev ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="filteredScenesManager.loadFilteredScenes(${pagination.page - 1})">
                    <i class="fas fa-chevron-left"></i>
                </a>
            </li>
        `;
        
        // Page numbers
        const startPage = Math.max(1, pagination.page - 2);
        const endPage = Math.min(pagination.pages, pagination.page + 2);
        
        if (startPage > 1) {
            html += `<li class="page-item"><a class="page-link" href="#" onclick="filteredScenesManager.loadFilteredScenes(1)">1</a></li>`;
            if (startPage > 2) {
                html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
        }
        
        for (let i = startPage; i <= endPage; i++) {
            html += `
                <li class="page-item ${i === pagination.page ? 'active' : ''}">
                    <a class="page-link" href="#" onclick="filteredScenesManager.loadFilteredScenes(${i})">${i}</a>
                </li>
            `;
        }
        
        if (endPage < pagination.pages) {
            if (endPage < pagination.pages - 1) {
                html += `<li class="page-item disabled"><span class="page-link">...</span></li>`;
            }
            html += `<li class="page-item"><a class="page-link" href="#" onclick="filteredScenesManager.loadFilteredScenes(${pagination.pages})">${pagination.pages}</a></li>`;
        }
        
        // Next button
        html += `
            <li class="page-item ${!pagination.has_next ? 'disabled' : ''}">
                <a class="page-link" href="#" onclick="filteredScenesManager.loadFilteredScenes(${pagination.page + 1})">
                    <i class="fas fa-chevron-right"></i>
                </a>
            </li>
        `;
        
        paginationEl.innerHTML = html;
    }
    
    applyFilters() {
        const form = document.getElementById('filter-form');
        const formData = new FormData(form);
        
        this.currentFilters = {};
        for (let [key, value] of formData.entries()) {
            if (value.trim()) {
                this.currentFilters[key] = value;
            }
        }
        
        this.loadFilteredScenes(1);
    }
    
    clearFilters() {
        document.getElementById('filter-form').reset();
        this.currentFilters = {};
        this.loadFilteredScenes(1);
    }
    
    toggleSceneSelection(sceneId) {
        if (this.selectedScenes.has(sceneId)) {
            this.selectedScenes.delete(sceneId);
        } else {
            this.selectedScenes.add(sceneId);
        }
        
        this.updateBulkActionsDisplay();
        this.updateSceneRowHighlight(sceneId);
    }
    
    toggleSelectAll() {
        const checkbox = document.getElementById('select-all-checkbox');
        const sceneCheckboxes = document.querySelectorAll('.scene-checkbox');
        
        if (checkbox.checked) {
            sceneCheckboxes.forEach(cb => {
                const sceneId = parseInt(cb.value);
                this.selectedScenes.add(sceneId);
                cb.checked = true;
            });
        } else {
            this.selectedScenes.clear();
            sceneCheckboxes.forEach(cb => cb.checked = false);
        }
        
        this.updateBulkActionsDisplay();
        this.updateAllSceneRowHighlights();
    }
    
    deselectAll() {
        this.selectedScenes.clear();
        document.querySelectorAll('.scene-checkbox').forEach(cb => cb.checked = false);
        document.getElementById('select-all-checkbox').checked = false;
        this.updateBulkActionsDisplay();
        this.updateAllSceneRowHighlights();
    }
    
    updateBulkActionsDisplay() {
        const bulkActions = document.getElementById('bulk-actions');
        const selectedCount = document.getElementById('selected-count');
        
        selectedCount.textContent = this.selectedScenes.size;
        
        if (this.selectedScenes.size > 0) {
            bulkActions.style.display = 'block';
        } else {
            bulkActions.style.display = 'none';
        }
    }
    
    updateSceneRowHighlight(sceneId) {
        const row = document.querySelector(`tr[data-scene-id="${sceneId}"]`);
        if (row) {
            if (this.selectedScenes.has(sceneId)) {
                row.classList.add('table-active');
            } else {
                row.classList.remove('table-active');
            }
        }
    }
    
    updateAllSceneRowHighlights() {
        document.querySelectorAll('tr[data-scene-id]').forEach(row => {
            const sceneId = parseInt(row.getAttribute('data-scene-id'));
            if (this.selectedScenes.has(sceneId)) {
                row.classList.add('table-active');
            } else {
                row.classList.remove('table-active');
            }
        });
    }
    
    showExceptionModal(sceneId) {
        document.getElementById('exception-scene-id').value = sceneId;
        document.getElementById('exception-type').value = 'permanent';
        document.getElementById('expires-section').style.display = 'none';
        document.getElementById('exception-form').reset();
        
        const modal = new bootstrap.Modal(document.getElementById('exceptionModal'));
        modal.show();
    }
    
    toggleExpirationField(type) {
        const expiresSection = document.getElementById('expires-section');
        const expiresInput = document.getElementById('expires-at');
        
        if (type === 'temporary') {
            expiresSection.style.display = 'block';
            expiresInput.required = true;
            
            // Set default expiration to 30 days from now
            const futureDate = new Date();
            futureDate.setDate(futureDate.getDate() + 30);
            expiresInput.value = futureDate.toISOString().slice(0, 16);
        } else {
            expiresSection.style.display = 'none';
            expiresInput.required = false;
        }
    }
    
    toggleBulkExpirationField(type) {
        const expiresSection = document.getElementById('bulk-expires-section');
        const expiresInput = document.querySelector('#bulk-expires-section input[name="expires_at"]');
        
        if (type === 'temporary') {
            expiresSection.style.display = 'block';
            expiresInput.required = true;
            
            // Set default expiration to 30 days from now
            const futureDate = new Date();
            futureDate.setDate(futureDate.getDate() + 30);
            expiresInput.value = futureDate.toISOString().slice(0, 16);
        } else {
            expiresSection.style.display = 'none';
            expiresInput.required = false;
        }
    }
    
    async createException() {
        const form = document.getElementById('exception-form');
        const formData = new FormData(form);
        const sceneId = formData.get('scene_id');
        
        const data = {
            type: formData.get('type'),
            reason: formData.get('reason'),
            add_to_whisparr: formData.has('add_to_whisparr')
        };
        
        if (data.type === 'temporary') {
            data.expires_at = formData.get('expires_at');
        }
        
        try {
            const response = await fetch(`/api/filtered-scenes/${sceneId}/exception`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                this.showSuccess(result.message);
                bootstrap.Modal.getInstance(document.getElementById('exceptionModal')).hide();
                await this.loadFilteredScenes(this.currentPage);
                await this.loadStats();
            } else {
                this.showError('Failed to create exception: ' + result.message);
            }
        } catch (error) {
            console.error('Error creating exception:', error);
            this.showError('Failed to create exception');
        }
    }
    
    showBulkExceptionModal() {
        if (this.selectedScenes.size === 0) {
            this.showError('Please select at least one scene');
            return;
        }
        
        document.getElementById('bulk-scene-count').textContent = this.selectedScenes.size;
        document.getElementById('bulk-exception-form').reset();
        document.getElementById('bulk-expires-section').style.display = 'none';
        
        const modal = new bootstrap.Modal(document.getElementById('bulkExceptionModal'));
        modal.show();
    }
    
    async createBulkExceptions() {
        if (this.selectedScenes.size === 0) {
            this.showError('No scenes selected');
            return;
        }
        
        const form = document.getElementById('bulk-exception-form');
        const formData = new FormData(form);
        
        const data = {
            scene_ids: Array.from(this.selectedScenes),
            type: formData.get('type'),
            reason: formData.get('reason'),
            add_to_whisparr: formData.has('add_to_whisparr')
        };
        
        if (data.type === 'temporary') {
            data.expires_at = formData.get('expires_at');
        }
        
        try {
            const response = await fetch('/api/filtered-scenes/bulk-exception', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                this.showSuccess(`${result.created_count} exceptions created successfully`);
                if (result.errors.length > 0) {
                    console.warn('Bulk exception errors:', result.errors);
                }
                
                bootstrap.Modal.getInstance(document.getElementById('bulkExceptionModal')).hide();
                this.deselectAll();
                await this.loadFilteredScenes(this.currentPage);
                await this.loadStats();
            } else {
                this.showError('Failed to create bulk exceptions: ' + result.message);
            }
        } catch (error) {
            console.error('Error creating bulk exceptions:', error);
            this.showError('Failed to create bulk exceptions');
        }
    }
    
    async showSceneDetails(sceneId) {
        try {
            const response = await fetch(`/api/filtered-scenes/${sceneId}`);
            const data = await response.json();
            
            if (data.status === 'success') {
                this.renderSceneDetails(data.scene);
                const modal = new bootstrap.Modal(document.getElementById('sceneDetailsModal'));
                modal.show();
            } else {
                this.showError('Failed to load scene details: ' + data.message);
            }
        } catch (error) {
            console.error('Error loading scene details:', error);
            this.showError('Failed to load scene details');
        }
    }
    
    renderSceneDetails(scene) {
        const content = document.getElementById('scene-details-content');
        const performers = scene.performers ? scene.performers.join(', ') : 'Unknown';
        const tags = scene.tags ? scene.tags.join(', ') : 'None';
        
        content.innerHTML = `
            <div class="row">
                <div class="col-md-4">
                    ${scene.thumbnail_url ? 
                        `<img src="${scene.thumbnail_url}" alt="Thumbnail" class="img-fluid rounded mb-3">` :
                        `<div class="bg-light rounded d-flex align-items-center justify-content-center mb-3" style="height: 200px;">
                            <i class="fas fa-image fa-3x text-muted"></i>
                         </div>`
                    }
                </div>
                <div class="col-md-8">
                    <h5>${this.escapeHtml(scene.title)}</h5>
                    
                    <dl class="row">
                        <dt class="col-sm-3">Performers:</dt>
                        <dd class="col-sm-9">${performers}</dd>
                        
                        <dt class="col-sm-3">Studio:</dt>
                        <dd class="col-sm-9">${scene.studio || 'Unknown'}</dd>
                        
                        <dt class="col-sm-3">Duration:</dt>
                        <dd class="col-sm-9">${scene.duration_minutes ? scene.duration_minutes + ' minutes' : 'Unknown'}</dd>
                        
                        <dt class="col-sm-3">Release Date:</dt>
                        <dd class="col-sm-9">${scene.release_date || 'Unknown'}</dd>
                        
                        <dt class="col-sm-3">Tags:</dt>
                        <dd class="col-sm-9">${tags}</dd>
                        
                        <dt class="col-sm-3">Filter Reason:</dt>
                        <dd class="col-sm-9">
                            <span class="badge ${this.getFilterReasonClass(scene.filter_reason)}">
                                ${this.formatFilterReason(scene.filter_reason)}
                            </span>
                        </dd>
                        
                        <dt class="col-sm-3">Filtered Date:</dt>
                        <dd class="col-sm-9">${new Date(scene.filtered_date).toLocaleString()}</dd>
                        
                        <dt class="col-sm-3">Exception Status:</dt>
                        <dd class="col-sm-9">
                            ${scene.is_exception ? 
                                `<span class="badge bg-success"><i class="fas fa-check"></i> Has Exception</span>` :
                                `<span class="badge bg-secondary"><i class="fas fa-times"></i> Filtered</span>`
                            }
                        </dd>
                    </dl>
                    
                    ${scene.scene_url ? 
                        `<div class="mt-3">
                            <a href="${scene.scene_url}" target="_blank" class="btn btn-primary btn-sm">
                                <i class="fas fa-external-link-alt"></i> View on Source
                            </a>
                         </div>` : ''
                    }
                </div>
            </div>
            
            ${scene.exceptions && scene.exceptions.length > 0 ? `
                <hr>
                <h6>Exceptions:</h6>
                <div class="table-responsive">
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Type</th>
                                <th>Reason</th>
                                <th>Created</th>
                                <th>Expires</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${scene.exceptions.map(exc => `
                                <tr>
                                    <td><span class="badge bg-info">${exc.exception_type}</span></td>
                                    <td>${exc.reason || 'No reason provided'}</td>
                                    <td>${new Date(exc.created_at).toLocaleDateString()}</td>
                                    <td>${exc.expires_at ? new Date(exc.expires_at).toLocaleDateString() : 'Never'}</td>
                                    <td>
                                        <span class="badge ${exc.is_active ? 'bg-success' : 'bg-secondary'}">
                                            ${exc.is_active ? 'Active' : 'Inactive'}
                                        </span>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            ` : ''}
        `;
    }
    
    async deleteFilteredScene(sceneId) {
        if (!confirm('Are you sure you want to delete this filtered scene? This action cannot be undone.')) {
            return;
        }
        
        try {
            // Note: This would need to be implemented as a DELETE endpoint
            this.showInfo('Delete functionality would be implemented here');
        } catch (error) {
            console.error('Error deleting scene:', error);
            this.showError('Failed to delete scene');
        }
    }
    
    showCleanupModal() {
        const modal = new bootstrap.Modal(document.getElementById('cleanupModal'));
        modal.show();
    }
    
    async performCleanup() {
        const form = document.getElementById('cleanup-form');
        const formData = new FormData(form);
        
        const data = {
            days_to_keep: parseInt(formData.get('days_to_keep'))
        };
        
        try {
            const response = await fetch('/api/filtered-scenes/cleanup', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.status === 'success') {
                this.showSuccess(result.message);
                bootstrap.Modal.getInstance(document.getElementById('cleanupModal')).hide();
                await this.loadFilteredScenes(this.currentPage);
                await this.loadStats();
            } else {
                this.showError('Cleanup failed: ' + result.message);
            }
        } catch (error) {
            console.error('Error during cleanup:', error);
            this.showError('Cleanup failed');
        }
    }
    
    async exportData() {
        try {
            // Build export parameters
            const params = new URLSearchParams(this.currentFilters);
            params.append('export', 'true');
            
            // Create download link
            const link = document.createElement('a');
            link.href = `/api/filtered-scenes?${params}`;
            link.download = `filtered-scenes-${new Date().toISOString().split('T')[0]}.csv`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            this.showSuccess('Export started. The file will download shortly.');
        } catch (error) {
            console.error('Error exporting data:', error);
            this.showError('Failed to export data');
        }
    }
    
    async refreshData() {
        const refreshBtn = document.getElementById('refresh-btn');
        const originalContent = refreshBtn.innerHTML;
        
        refreshBtn.innerHTML = '<i class="fas fa-spin fa-sync-alt"></i> Refreshing...';
        refreshBtn.disabled = true;
        
        try {
            await Promise.all([
                this.loadStats(),
                this.loadFilteredScenes(this.currentPage)
            ]);
            
            this.showSuccess('Data refreshed successfully');
        } catch (error) {
            this.showError('Failed to refresh data');
        } finally {
            refreshBtn.innerHTML = originalContent;
            refreshBtn.disabled = false;
        }
    }
    
    setupAutoRefresh() {
        // Auto-refresh stats every 5 minutes
        setInterval(() => {
            this.loadStats();
        }, 5 * 60 * 1000);
    }
    
    // Utility methods
    formatFilterReason(reason) {
        const reasons = {
            'already_downloaded': 'Already Downloaded',
            'unwanted_tags': 'Unwanted Tags',
            'studio_filter': 'Studio Filter',
            'date_range': 'Date Range',
            'duration_filter': 'Duration Filter',
            'rating_filter': 'Rating Filter',
            'custom_rules': 'Custom Rules'
        };
        return reasons[reason] || reason;
    }
    
    getFilterReasonClass(reason) {
        const classes = {
            'already_downloaded': 'bg-info',
            'unwanted_tags': 'bg-warning',
            'studio_filter': 'bg-secondary',
            'date_range': 'bg-primary',
            'duration_filter': 'bg-success',
            'rating_filter': 'bg-danger',
            'custom_rules': 'bg-dark'
        };
        return classes[reason] || 'bg-secondary';
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    showLoading() {
        const tbody = document.getElementById('scenes-table');
        tbody.classList.add('loading');
        document.getElementById('loading-text').textContent = 'Loading filtered scenes...';
    }
    
    hideLoading() {
        const tbody = document.getElementById('scenes-table');
        tbody.classList.remove('loading');
    }
    
    showSuccess(message) {
        this.showAlert(message, 'success');
    }
    
    showError(message) {
        this.showAlert(message, 'danger');
    }
    
    showInfo(message) {
        this.showAlert(message, 'info');
    }
    
    showAlert(message, type = 'info') {
        // Use the global showAlert function from base template
        if (typeof showAlert === 'function') {
            showAlert(message, type);
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }
}

// Initialize the manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.filteredScenesManager = new FilteredScenesManager();
});

// Global functions for HTML onclick handlers
function refreshData() {
    filteredScenesManager.refreshData();
}

function showCleanupModal() {
    filteredScenesManager.showCleanupModal();
}

function performCleanup() {
    filteredScenesManager.performCleanup();
}

function exportData() {
    filteredScenesManager.exportData();
}

function clearFilters() {
    filteredScenesManager.clearFilters();
}

function saveFilterPreset() {
    // This could be implemented to save filter combinations
    filteredScenesManager.showInfo('Filter presets feature coming soon!');
}

function createException() {
    filteredScenesManager.createException();
}

function createBulkExceptions() {
    filteredScenesManager.createBulkExceptions();
}
