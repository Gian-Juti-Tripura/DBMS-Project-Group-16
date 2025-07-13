/**
 * Main JavaScript file for Database Normalization and ER Diagram Generator
 * Contains utility functions and client-side functionality
 */

// Global variables
let currentAnalysisData = null;
let currentFileData = null;

// Utility functions
const Utils = {
    // Show loading spinner
    showLoading: function(elementId, message = 'Loading...') {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = `
                <div class="d-flex justify-content-center align-items-center p-3">
                    <div class="spinner-border text-primary me-2" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <span>${message}</span>
                </div>
            `;
        }
    },

    // Hide loading spinner
    hideLoading: function(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = '';
        }
    },

    // Show success message
    showSuccess: function(message) {
        this.showAlert(message, 'success');
    },

    // Show error message
    showError: function(message) {
        this.showAlert(message, 'danger');
    },

    // Show alert message
    showAlert: function(message, type = 'info') {
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        
        // Find or create alerts container
        let alertContainer = document.getElementById('alerts-container');
        if (!alertContainer) {
            alertContainer = document.createElement('div');
            alertContainer.id = 'alerts-container';
            document.querySelector('main').insertBefore(alertContainer, document.querySelector('main').firstChild);
        }
        
        alertContainer.innerHTML = alertHtml;
        
        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            const alert = alertContainer.querySelector('.alert');
            if (alert) {
                alert.classList.remove('show');
                setTimeout(() => alert.remove(), 150);
            }
        }, 5000);
    },

    // Format file size
    formatFileSize: function(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    // Copy text to clipboard
    copyToClipboard: function(text) {
        navigator.clipboard.writeText(text).then(() => {
            this.showSuccess('Copied to clipboard!');
        }).catch(err => {
            console.error('Failed to copy: ', err);
            this.showError('Failed to copy to clipboard');
        });
    },

    // Download file
    downloadFile: function(url, filename) {
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    },

    // Validate CSV file
    validateCSVFile: function(file) {
        const maxSize = 16 * 1024 * 1024; // 16MB
        const allowedTypes = ['text/csv', 'application/csv'];
        
        if (file.size > maxSize) {
            return { valid: false, message: 'File size must be less than 16MB' };
        }
        
        if (!allowedTypes.includes(file.type) && !file.name.toLowerCase().endsWith('.csv')) {
            return { valid: false, message: 'Please upload a CSV file' };
        }
        
        return { valid: true };
    },

    // Format functional dependency for display
    formatFD: function(fd) {
        if (Array.isArray(fd) && fd.length === 2) {
            const [left, right] = fd;
            const leftStr = Array.isArray(left) ? left.join(', ') : left;
            return `${leftStr} → ${right}`;
        }
        return fd;
    },

    // Format candidate key for display
    formatCandidateKey: function(key) {
        if (Array.isArray(key)) {
            return `{${key.join(', ')}}`;
        }
        return key;
    },

    // Animate counter
    animateCounter: function(element, start, end, duration = 1000) {
        const startTime = performance.now();
        
        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const current = Math.floor(progress * (end - start) + start);
            element.textContent = current;
            
            if (progress < 1) {
                requestAnimationFrame(update);
            }
        }
        
        requestAnimationFrame(update);
    },

    // Debounce function
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Throttle function
    throttle: function(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
};

// API functions
const API = {
    // Base URL for API calls
    baseURL: '',

    // Upload file
    uploadFile: function(file, onProgress = null) {
        return new Promise((resolve, reject) => {
            const formData = new FormData();
            formData.append('file', file);

            const xhr = new XMLHttpRequest();

            // Handle progress
            if (onProgress) {
                xhr.upload.addEventListener('progress', (e) => {
                    if (e.lengthComputable) {
                        const percentComplete = (e.loaded / e.total) * 100;
                        onProgress(percentComplete);
                    }
                });
            }

            xhr.addEventListener('load', () => {
                if (xhr.status === 200) {
                    resolve(JSON.parse(xhr.responseText));
                } else {
                    reject(new Error(`HTTP ${xhr.status}: ${xhr.statusText}`));
                }
            });

            xhr.addEventListener('error', () => {
                reject(new Error('Network error'));
            });

            xhr.open('POST', this.baseURL + '/upload');
            xhr.send(formData);
        });
    },

    // Analyze data
    analyzeData: function() {
        return fetch(this.baseURL + '/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        }).then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        });
    },

    // Generate schema
    generateSchema: function(type) {
        return fetch(this.baseURL + '/generate_schema', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ type: type })
        }).then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        });
    },

    // Get relations
    getRelations: function(type) {
        return fetch(this.baseURL + `/api/relations/${type}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            });
    },

    // Get FD details
    getFDDetails: function() {
        return fetch(this.baseURL + '/api/fd_details')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            });
    },

    // Get schema comparison
    getSchemaComparison: function() {
        return fetch(this.baseURL + '/api/schema_comparison')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return response.json();
            });
    }
};

// UI components
const UI = {
    // Create progress bar
    createProgressBar: function(percentage, type = 'primary') {
        return `
            <div class="progress">
                <div class="progress-bar bg-${type}" role="progressbar" 
                     style="width: ${percentage}%" 
                     aria-valuenow="${percentage}" 
                     aria-valuemin="0" 
                     aria-valuemax="100">
                    ${percentage}%
                </div>
            </div>
        `;
    },

    // Create badge
    createBadge: function(text, type = 'primary') {
        return `<span class="badge bg-${type}">${text}</span>`;
    },

    // Create list group
    createListGroup: function(items, formatter = null) {
        const listItems = items.map(item => {
            const displayText = formatter ? formatter(item) : item;
            return `<li class="list-group-item">${displayText}</li>`;
        }).join('');
        
        return `<ul class="list-group">${listItems}</ul>`;
    },

    // Create table
    createTable: function(headers, rows, classes = 'table table-striped') {
        const headerRow = headers.map(header => `<th>${header}</th>`).join('');
        const dataRows = rows.map(row => {
            const cells = row.map(cell => `<td>${cell}</td>`).join('');
            return `<tr>${cells}</tr>`;
        }).join('');
        
        return `
            <table class="${classes}">
                <thead>
                    <tr>${headerRow}</tr>
                </thead>
                <tbody>
                    ${dataRows}
                </tbody>
            </table>
        `;
    },

    // Create card
    createCard: function(title, content, headerClass = 'bg-primary text-white') {
        return `
            <div class="card">
                <div class="card-header ${headerClass}">
                    <h5 class="card-title mb-0">${title}</h5>
                </div>
                <div class="card-body">
                    ${content}
                </div>
            </div>
        `;
    },

    // Create metric card
    createMetricCard: function(label, value, icon = null) {
        const iconHtml = icon ? `<i class="${icon} text-primary mb-2"></i>` : '';
        return `
            <div class="metric-card">
                ${iconHtml}
                <div class="metric-value">${value}</div>
                <div class="metric-label">${label}</div>
            </div>
        `;
    }
};

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(() => {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            if (alert.classList.contains('show')) {
                alert.classList.remove('show');
                setTimeout(() => alert.remove(), 150);
            }
        });
    }, 5000);

    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });

    // Handle file drag and drop
    const fileInput = document.getElementById('csvFile');
    if (fileInput) {
        const dropZone = fileInput.closest('.card-body');
        
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, preventDefaults, false);
        });
        
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, highlight, false);
        });
        
        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, unhighlight, false);
        });
        
        dropZone.addEventListener('drop', handleDrop, false);
        
        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }
        
        function highlight(e) {
            dropZone.classList.add('drag-over');
        }
        
        function unhighlight(e) {
            dropZone.classList.remove('drag-over');
        }
        
        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files.length > 0) {
                fileInput.files = files;
                fileInput.dispatchEvent(new Event('change'));
            }
        }
    }

    console.log('Database Normalization and ER Diagram Generator initialized');
});

// Export for use in other files
window.Utils = Utils;
window.API = API;
window.UI = UI;