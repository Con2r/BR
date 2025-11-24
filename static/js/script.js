// Brainrot Academy - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    const popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert.classList.contains('show')) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    });

    // Add loading states to buttons
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"], input[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Загрузка...';
                submitBtn.disabled = true;
            }
        });
    });

    // Enhanced form validation
    document.querySelectorAll('.needs-validation').forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Real-time character counter for textareas
    document.querySelectorAll('textarea[data-max-length]').forEach(textarea => {
        const maxLength = textarea.getAttribute('data-max-length');
        const counter = document.createElement('div');
        counter.className = 'form-text text-end';
        textarea.parentNode.appendChild(counter);
        
        function updateCounter() {
            const remaining = maxLength - textarea.value.length;
            counter.textContent = `${remaining} символов осталось`;
            counter.className = `form-text text-end ${remaining < 20 ? 'text-warning' : 'text-muted'}`;
        }
        
        textarea.addEventListener('input', updateCounter);
        updateCounter();
    });

    // Dark mode toggle (future feature)
    const darkModeToggle = document.getElementById('darkModeToggle');
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', function() {
            document.body.classList.toggle('light-mode');
            localStorage.setItem('darkMode', document.body.classList.contains('light-mode') ? 'false' : 'true');
        });
    }

    // Check for saved dark mode preference
    if (localStorage.getItem('darkMode') === 'false') {
        document.body.classList.add('light-mode');
    }
});

// Utility functions
const BrainrotUtils = {
    // Format date
    formatDate: (dateString) => {
        const options = { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        return new Date(dateString).toLocaleDateString('ru-RU', options);
    },

    // Debounce function for search inputs
    debounce: (func, wait) => {
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

    // Copy to clipboard
    copyToClipboard: (text) => {
        navigator.clipboard.writeText(text).then(() => {
            // Show success message
            const toast = document.createElement('div');
            toast.className = 'alert alert-success position-fixed top-0 end-0 m-3';
            toast.style.zIndex = '1060';
            toast.textContent = 'Скопировано в буфер обмена!';
            document.body.appendChild(toast);
            
            setTimeout(() => {
                toast.remove();
            }, 2000);
        }).catch(err => {
            console.error('Ошибка копирования: ', err);
        });
    },

    // Show notification
    showNotification: (message, type = 'info') => {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
        notification.style.zIndex = '1060';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    },

    // Format file size
    formatFileSize: (bytes) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
};

// API helper functions
const BrainrotAPI = {
    // Generic API call
    call: async (endpoint, options = {}) => {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
        };

        try {
            const response = await fetch(endpoint, { ...defaultOptions, ...options });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API call failed:', error);
            BrainrotUtils.showNotification('Ошибка при обращении к серверу', 'danger');
            throw error;
        }
    },

    // Get student progress
    getStudentProgress: async (studentId) => {
        return await BrainrotAPI.call(`/api/student/progress`);
    },

    // Submit challenge
    submitChallenge: async (level, code) => {
        return await BrainrotAPI.call(`/api/challenge/${level}/submit`, {
            method: 'POST',
            body: JSON.stringify({ code })
        });
    },

    // Get mood analytics
    getMoodAnalytics: async (studentId, days = 7) => {
        return await BrainrotAPI.call(`/api/mood/analytics/${studentId}?days=${days}`);
    },

    // Record mood
    recordMood: async (studentId, moodValue, notes = '') => {
        return await BrainrotAPI.call('/api/mood/record', {
            method: 'POST',
            body: JSON.stringify({ student_id: studentId, mood_value: moodValue, notes })
        });
    }
};

// Export for global use
window.BrainrotUtils = BrainrotUtils;
window.BrainrotAPI = BrainrotAPI;