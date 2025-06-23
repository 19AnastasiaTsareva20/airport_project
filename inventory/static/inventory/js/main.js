document.addEventListener('DOMContentLoaded', function() {
    // Инициализация функционала
    initializeToasts();
    initializeAjaxForms();
    initializeRefreshButtons();
    initializeLowStockAlerts();
    
    // Auto-refresh для главной страницы каждые 30 секунд
    if (window.location.pathname === '/') {
        setInterval(refreshDashboardStats, 30000);
    }
});

// Система уведомлений
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toastId = 'toast-' + Date.now();
    const toastHTML = `
        <div class="toast align-items-center text-bg-${type} border-0" role="alert" id="${toastId}">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement);
    toast.show();
    
    // Удаляем toast после скрытия
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    document.body.appendChild(container);
    return container;
}

function initializeToasts() {
    // Показываем toast для Django messages
    const messages = document.querySelectorAll('.django-message');
    messages.forEach(function(message) {
        const type = message.dataset.type || 'info';
        showToast(message.textContent, type);
        message.remove();
    });
}

// AJAX обновление статистики на главной странице
function refreshDashboardStats() {
    fetch('/ajax/dashboard-stats/')
        .then(response => response.json())
        .then(data => {
            // Обновляем карточки статистики
            updateStatCard('total-products', data.total_products);
            updateStatCard('active-orders', data.active_orders);
            updateStatCard('total-sales', data.total_sales);
            updateStatCard('low-stock-count', data.low_stock_count);
            
            // Показываем уведомление об обновлении
            showToast('Статистика обновлена', 'success');
        })
        .catch(error => {
            console.error('Ошибка обновления статистики:', error);
            showToast('Ошибка обновления статистики', 'danger');
        });
}

function updateStatCard(elementId, value) {
    const element = document.getElementById(elementId);
    if (element) {
        // Анимация изменения значения
        element.style.transform = 'scale(1.1)';
        setTimeout(() => {
            element.textContent = value;
            element.style.transform = 'scale(1)';
        }, 150);
    }
}

// Обработка AJAX форм
function initializeAjaxForms() {
    const ajaxForms = document.querySelectorAll('.ajax-form');
    ajaxForms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            submitAjaxForm(form);
        });
    });
}

function submitAjaxForm(form) {
    const formData = new FormData(form);
    const url = form.action || window.location.pathname;
    
    showLoadingOverlay();
    
    fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        hideLoadingOverlay();
        if (data.success) {
            showToast(data.message || 'Операция выполнена успешно', 'success');
            if (data.redirect) {
                window.location.href = data.redirect;
            }
        } else {
            showToast(data.message || 'Произошла ошибка', 'danger');
        }
    })
    .catch(error => {
        hideLoadingOverlay();
        console.error('Ошибка:', error);
        showToast('Произошла ошибка при выполнении запроса', 'danger');
    });
}

// Показать/скрыть overlay загрузки
function showLoadingOverlay() {
    const overlay = document.createElement('div');
    overlay.id = 'loading-overlay';
    overlay.className = 'loading-overlay';
    overlay.innerHTML = '<div class="spinner"></div>';
    document.body.appendChild(overlay);
}

function hideLoadingOverlay() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.remove();
    }
}

// Кнопки обновления
function initializeRefreshButtons() {
    const refreshButtons = document.querySelectorAll('.refresh-btn');
    refreshButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            window.location.reload();
        });
    });
}

// Предупреждения о низком запасе
function initializeLowStockAlerts() {
    const stockCells = document.querySelectorAll('.stock-quantity');
    stockCells.forEach(function(cell) {
        const quantity = parseInt(cell.textContent);
        if (quantity <= 5) {
            cell.classList.add('low-stock');
            cell.title = 'Критически низкий запас!';
        } else if (quantity <= 15) {
            cell.classList.add('medium-stock');
            cell.title = 'Низкий запас';
        } else {
            cell.classList.add('high-stock');
        }
    });
}

// Экспорт данных
function exportData(format, type) {
    const currentUrl = new URL(window.location);
    currentUrl.searchParams.set('export', format);
    
    showToast(`Начинается экспорт в формате ${format.toUpperCase()}...`, 'info');
    
    // Создаем скрытую ссылку для скачивания
    const link = document.createElement('a');
    link.href = currentUrl.toString();
    link.download = '';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    setTimeout(() => {
        showToast('Файл готов к скачиванию', 'success');
    }, 1000);
}

// Функции для работы с фильтрами
function clearFilters() {
    const form = document.querySelector('.filter-form form');
    if (form) {
        form.reset();
        form.submit();
    }
}

// Автоматическая отправка формы при изменении фильтров
document.addEventListener('change', function(e) {
    if (e.target.matches('.auto-submit')) {
        e.target.closest('form').submit();
    }
});

// Подтверждение удаления
function confirmDelete(message = 'Вы уверены, что хотите удалить этот элемент?') {
    return confirm(message);
}
