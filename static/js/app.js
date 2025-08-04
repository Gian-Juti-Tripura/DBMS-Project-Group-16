// PharmaCare Analytics Dashboard - Main JavaScript Application

class PharmaCareApp {
    constructor() {
        this.currentPage = 1;
        this.perPage = 10;
        this.currentData = [];
        this.isSearchActive = false;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupDragAndDrop();
    }

    setupEventListeners() {
        // File input change
        document.getElementById('fileInput').addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFileSelection(e.target.files[0]);
            }
        });

        // Upload button
        document.getElementById('uploadBtn').addEventListener('click', () => {
            this.uploadFile();
        });

        // Load sample data button
        document.getElementById('loadSampleBtn').addEventListener('click', () => {
            this.loadSampleData();
        });

        // Search functionality
        document.getElementById('searchBtn').addEventListener('click', () => {
            this.performSearch();
        });

        document.getElementById('searchInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.performSearch();
            }
        });

        // Clear filters
        document.getElementById('clearFilters').addEventListener('click', () => {
            this.clearFilters();
        });

        // Category filter change
        document.getElementById('categoryFilter').addEventListener('change', () => {
            if (this.isSearchActive) {
                this.performSearch();
            }
        });
    }

    setupDragAndDrop() {
        const uploadArea = document.getElementById('uploadArea');

        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileSelection(files[0]);
            }
        });

        uploadArea.addEventListener('click', () => {
            document.getElementById('fileInput').click();
        });
    }

    handleFileSelection(file) {
        const allowedTypes = ['text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'];
        
        if (!allowedTypes.includes(file.type)) {
            this.showAlert('Please select a CSV or Excel file.', 'danger');
            return;
        }

        if (file.size > 16 * 1024 * 1024) { // 16MB
            this.showAlert('File size must be less than 16MB.', 'danger');
            return;
        }

        document.getElementById('uploadBtn').disabled = false;
        document.getElementById('uploadBtn').innerHTML = `<i class="fas fa-upload me-2"></i>Upload ${file.name}`;
        this.selectedFile = file;
    }

    async uploadFile() {
        if (!this.selectedFile) {
            this.showAlert('Please select a file first.', 'warning');
            return;
        }

        const formData = new FormData();
        formData.append('file', this.selectedFile);

        this.showLoading(true);
        
        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (response.ok) {
                this.showAlert(result.message, 'success');
                this.updateDataInfo(result.data_info);
                this.loadData();
                this.loadAnalytics();
            } else {
                this.showAlert(result.error, 'danger');
            }
        } catch (error) {
            this.showAlert('Error uploading file: ' + error.message, 'danger');
        } finally {
            this.showLoading(false);
        }
    }

    async loadSampleData() {
        this.showLoading(true);
        
        try {
            const response = await fetch('/load_sample');
            const result = await response.json();

            if (response.ok) {
                this.showAlert(result.message, 'success');
                this.updateDataInfo(result.data_info);
                this.loadData();
                this.loadAnalytics();
            } else {
                this.showAlert(result.error, 'danger');
            }
        } catch (error) {
            this.showAlert('Error loading sample data: ' + error.message, 'danger');
        } finally {
            this.showLoading(false);
        }
    }

    updateDataInfo(dataInfo) {
        // Show overview cards
        document.getElementById('overviewCards').style.display = 'block';
        document.getElementById('searchSection').style.display = 'block';
        document.getElementById('dataSection').style.display = 'block';
        document.getElementById('analyticsSection').style.display = 'block';

        // Update overview cards
        document.getElementById('totalRecords').textContent = dataInfo.rows;
        
        // Show sections with animation
        this.animateSection('overviewCards');
        this.animateSection('searchSection');
        this.animateSection('dataSection');
        this.animateSection('analyticsSection');
    }

    animateSection(sectionId) {
        const section = document.getElementById(sectionId);
        section.classList.add('fade-in');
    }

    async loadData(page = 1) {
        try {
            const response = await fetch(`/api/data?page=${page}&per_page=${this.perPage}`);
            const result = await response.json();

            if (response.ok) {
                this.currentData = result.data;
                this.renderTable(result.data);
                this.renderPagination(result);
                document.getElementById('resultCount').textContent = `${result.total_rows} results`;
            } else {
                this.showAlert(result.error, 'danger');
            }
        } catch (error) {
            this.showAlert('Error loading data: ' + error.message, 'danger');
        }
    }

    async performSearch() {
        const query = document.getElementById('searchInput').value.trim();
        const category = document.getElementById('categoryFilter').value;

        if (!query) {
            this.clearFilters();
            return;
        }

        this.showLoading(true);
        this.isSearchActive = true;

        try {
            const response = await fetch(`/api/search?query=${encodeURIComponent(query)}&category=${category}`);
            const result = await response.json();

            if (response.ok) {
                this.currentData = result.data;
                this.renderTable(result.data);
                document.getElementById('resultCount').textContent = `${result.total_results} results`;
                document.getElementById('paginationNav').style.display = 'none';
            } else {
                this.showAlert(result.error, 'danger');
            }
        } catch (error) {
            this.showAlert('Error searching data: ' + error.message, 'danger');
        } finally {
            this.showLoading(false);
        }
    }

    clearFilters() {
        document.getElementById('searchInput').value = '';
        document.getElementById('categoryFilter').value = 'all';
        this.isSearchActive = false;
        document.getElementById('paginationNav').style.display = 'block';
        this.loadData(1);
    }

    renderTable(data) {
        if (!data || data.length === 0) {
            document.getElementById('tableBody').innerHTML = '<tr><td colspan="100%" class="text-center">No data available</td></tr>';
            return;
        }

        // Create table headers
        const headers = Object.keys(data[0]);
        const headerRow = document.getElementById('tableHeader');
        headerRow.innerHTML = headers.map(header => 
            `<th>${this.formatHeader(header)}</th>`
        ).join('');

        // Create table rows
        const tableBody = document.getElementById('tableBody');
        tableBody.innerHTML = data.map(row => {
            return `<tr>${headers.map(header => 
                `<td>${this.formatCellValue(row[header])}</td>`
            ).join('')}</tr>`;
        }).join('');
    }

    renderPagination(result) {
        const pagination = document.getElementById('pagination');
        const totalPages = result.total_pages;
        const currentPage = result.page;

        if (totalPages <= 1) {
            pagination.innerHTML = '';
            return;
        }

        let paginationHTML = '';

        // Previous button
        if (currentPage > 1) {
            paginationHTML += `<li class="page-item">
                <a class="page-link" href="#" onclick="app.loadData(${currentPage - 1})">Previous</a>
            </li>`;
        }

        // Page numbers
        for (let i = Math.max(1, currentPage - 2); i <= Math.min(totalPages, currentPage + 2); i++) {
            paginationHTML += `<li class="page-item ${i === currentPage ? 'active' : ''}">
                <a class="page-link" href="#" onclick="app.loadData(${i})">${i}</a>
            </li>`;
        }

        // Next button
        if (currentPage < totalPages) {
            paginationHTML += `<li class="page-item">
                <a class="page-link" href="#" onclick="app.loadData(${currentPage + 1})">Next</a>
            </li>`;
        }

        pagination.innerHTML = paginationHTML;
    }

    async loadAnalytics() {
        try {
            // Load all analytics in parallel
            const [drugAnalytics, trialAnalytics, sideEffectAnalytics] = await Promise.all([
                fetch('/api/analytics/drugs').then(r => r.json()),
                fetch('/api/analytics/clinical_trials').then(r => r.json()),
                fetch('/api/analytics/side_effects').then(r => r.json())
            ]);

            // Render charts
            this.renderDrugCategoriesChart(drugAnalytics.drug_categories);
            this.renderCompaniesChart(drugAnalytics.top_companies);
            this.renderDiseaseCategoriesChart(drugAnalytics.disease_categories);
            this.renderSideEffectsChart(sideEffectAnalytics.top_side_effects);
            
            if (trialAnalytics.trial_status) {
                this.renderTrialStatusChart(trialAnalytics.trial_status);
                this.renderParticipantsChart(trialAnalytics.participants_by_status);
            }

            // Update overview cards with actual data
            this.updateOverviewCards(drugAnalytics);

        } catch (error) {
            console.error('Error loading analytics:', error);
        }
    }

    updateOverviewCards(analytics) {
        if (analytics.drug_categories) {
            document.getElementById('drugCategories').textContent = analytics.drug_categories.labels.length;
        }
        if (analytics.top_companies) {
            document.getElementById('companies').textContent = analytics.top_companies.labels.length;
        }
    }

    renderDrugCategoriesChart(data) {
        if (!data || !data.labels || !data.values) return;

        const trace = {
            labels: data.labels,
            values: data.values,
            type: 'pie',
            marker: {
                colors: ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe']
            }
        };

        const layout = {
            title: '',
            showlegend: true,
            margin: { t: 30, r: 30, b: 30, l: 30 }
        };

        Plotly.newPlot('drugCategoriesChart', [trace], layout, {responsive: true});
    }

    renderCompaniesChart(data) {
        if (!data || !data.labels || !data.values) return;

        const trace = {
            x: data.labels,
            y: data.values,
            type: 'bar',
            marker: {
                color: 'rgba(102, 126, 234, 0.8)',
                line: {
                    color: 'rgba(102, 126, 234, 1.0)',
                    width: 1
                }
            }
        };

        const layout = {
            title: '',
            xaxis: { title: 'Companies' },
            yaxis: { title: 'Number of Drugs' },
            margin: { t: 30, r: 30, b: 100, l: 50 }
        };

        Plotly.newPlot('companiesChart', [trace], layout, {responsive: true});
    }

    renderDiseaseCategoriesChart(data) {
        if (!data || !data.labels || !data.values) return;

        const trace = {
            labels: data.labels,
            values: data.values,
            type: 'doughnut',
            hole: 0.4,
            marker: {
                colors: ['#56ab2f', '#a8e6cf', '#3498db', '#85c1e9', '#f39c12', '#f7dc6f']
            }
        };

        const layout = {
            title: '',
            showlegend: true,
            margin: { t: 30, r: 30, b: 30, l: 30 }
        };

        Plotly.newPlot('diseaseCategoriesChart', [trace], layout, {responsive: true});
    }

    renderSideEffectsChart(data) {
        if (!data || !data.labels || !data.values) return;

        const trace = {
            x: data.values,
            y: data.labels,
            type: 'bar',
            orientation: 'h',
            marker: {
                color: 'rgba(243, 156, 18, 0.8)',
                line: {
                    color: 'rgba(243, 156, 18, 1.0)',
                    width: 1
                }
            }
        };

        const layout = {
            title: '',
            xaxis: { title: 'Frequency' },
            yaxis: { title: 'Side Effects' },
            margin: { t: 30, r: 30, b: 50, l: 150 }
        };

        Plotly.newPlot('sideEffectsChart', [trace], layout, {responsive: true});
    }

    renderTrialStatusChart(data) {
        if (!data || !data.labels || !data.values) return;

        const trace = {
            labels: data.labels,
            values: data.values,
            type: 'pie',
            marker: {
                colors: ['#28a745', '#ffc107', '#dc3545', '#17a2b8']
            }
        };

        const layout = {
            title: '',
            showlegend: true,
            margin: { t: 30, r: 30, b: 30, l: 30 }
        };

        Plotly.newPlot('trialStatusChart', [trace], layout, {responsive: true});
    }

    renderParticipantsChart(data) {
        if (!data || !data.labels || !data.values) return;

        const trace = {
            x: data.labels,
            y: data.values,
            type: 'bar',
            marker: {
                color: 'rgba(23, 162, 184, 0.8)',
                line: {
                    color: 'rgba(23, 162, 184, 1.0)',
                    width: 1
                }
            }
        };

        const layout = {
            title: '',
            xaxis: { title: 'Trial Status' },
            yaxis: { title: 'Total Participants' },
            margin: { t: 30, r: 30, b: 50, l: 50 }
        };

        Plotly.newPlot('participantsChart', [trace], layout, {responsive: true});
    }

    formatHeader(header) {
        return header.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    formatCellValue(value) {
        if (value === null || value === undefined || value === '') {
            return '<span class="text-muted">-</span>';
        }
        
        if (typeof value === 'string' && value.length > 50) {
            return `<span title="${value}">${value.substring(0, 50)}...</span>`;
        }
        
        return value;
    }

    showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.getElementById('uploadStatus').innerHTML = '';
        document.getElementById('uploadStatus').appendChild(alertDiv);

        // Auto-hide success messages
        if (type === 'success') {
            setTimeout(() => {
                alertDiv.remove();
            }, 5000);
        }
    }

    showLoading(show) {
        const modal = new bootstrap.Modal(document.getElementById('loadingModal'));
        if (show) {
            modal.show();
        } else {
            modal.hide();
        }
    }
}

// Initialize the application when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new PharmaCareApp();
});

// Handle navigation clicks
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('nav-link')) {
        e.preventDefault();
        const targetId = e.target.getAttribute('href').substring(1);
        
        // Remove active class from all nav links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        
        // Add active class to clicked link
        e.target.classList.add('active');
        
        // Scroll to target section
        const targetElement = document.getElementById(targetId);
        if (targetElement) {
            targetElement.scrollIntoView({ behavior: 'smooth' });
        }
    }
});