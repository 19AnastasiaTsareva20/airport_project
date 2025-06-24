// ===== ИНИЦИАЛИЗАЦИЯ =====
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ JavaScript загружен для системы управления складом аэропорта!');
    
    // Инициализация всех модулей
    initializeActionButtons();
    initializeToasts();
    initializeFilters();
    initializeExportButtons();
    initializeRefreshButtons();
    
    // Приветственное сообщение для демонстрации
    setTimeout(() => {
        showToast('🏭 Система управления складом аэропорта готова к работе!', 'success');
    }, 1000);
    
    // Автообновление статистики на главной странице
    if (window.location.pathname === '/' || window.location.pathname === '/home/') {
        console.log('📊 Автообновление статистики включено');
        setInterval(refreshDashboardStats, 60000); // каждую минуту
    }
});

// ===== ОБРАБОТКА КНОПОК ДЕЙСТВИЙ =====
function initializeActionButtons() {
    console.log('🔧 Инициализация кнопок действий...');
    
    // Удаляем старые обработчики onclick
    const buttonsWithOnclick = document.querySelectorAll('[onclick]');
    buttonsWithOnclick.forEach(btn => {
        if (btn.getAttribute('onclick').includes('handleAction')) {
            btn.removeAttribute('onclick');
        }
    });
    
    // Универсальный обработчик через event delegation
    document.addEventListener('click', function(e) {
        const button = e.target.closest('.action-btn');
        if (button) {
            e.preventDefault();
            e.stopPropagation();
            
            const action = button.dataset.action;
            const type = button.dataset.type;
            const id = button.dataset.id;
            const name = button.dataset.name || '';
            
            console.log('🎯 Кнопка нажата:', { action, type, id, name });
            handleAction(action, type, id, name);
        }
    });
    
    // Дополнительная инициализация для надежности
    setTimeout(() => {
        const actionButtons = document.querySelectorAll('.action-btn');
        console.log(`🔍 Найдено ${actionButtons.length} кнопок действий`);
        
        actionButtons.forEach((button, index) => {
            if (!button.hasAttribute('data-listener-added')) {
                button.setAttribute('data-listener-added', 'true');
                
                button.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    const action = this.dataset.action;
                    const type = this.dataset.type;
                    const id = this.dataset.id;
                    const name = this.dataset.name || '';
                    
                    console.log(`🎯 Прямой обработчик кнопки ${index + 1}:`, { action, type, id, name });
                    handleAction(action, type, id, name);
                });
                
                console.log(`✅ Кнопка ${index + 1} инициализирована: ${button.dataset.action} ${button.dataset.type}`);
            }
        });
    }, 500);
}

function handleAction(action, type, id, name) {
    const typeNames = {
        'product': 'товара',
        'customer': 'клиента', 
        'order': 'заказа'
    };
    
    const typeName = typeNames[type] || type;
    const itemName = name || `#${id}`;
    
    console.log(`🎬 Выполняется действие: ${action} для ${typeName} ${itemName}`);
    
    // Добавляем визуальную обратную связь
    const button = document.querySelector(`[data-action="${action}"][data-id="${id}"]`);
    if (button) {
        button.style.transform = 'scale(0.95)';
        setTimeout(() => {
            button.style.transform = 'scale(1)';
        }, 150);
    }
    
    switch(action) {
        case 'edit':
            showToast(`🔧 Редактирование ${typeName} ${itemName}`, 'primary');
            console.log(`Здесь будет логика редактирования ${typeName} с ID: ${id}`);
            break;
            
        case 'view':
            showToast(`👀 Просмотр ${typeName} ${itemName}`, 'info');
            console.log(`Здесь будет логика просмотра ${typeName} с ID: ${id}`);
            break;
            
        case 'orders':
            showToast(`📋 Просмотр заказов клиента: ${name}`, 'info');
            console.log(`Здесь будет переход к заказам клиента с ID: ${id}`);
            break;
            
        case 'process':
            if (confirm(`Обработать заказ #${id}?`)) {
                showToast(`✅ Заказ #${id} успешно обработан`, 'success');
                console.log(`Заказ ${id} помечен как обработанный`);
                
                // Имитация обновления статуса в интерфейсе
                const statusCell = document.querySelector(`tr[data-order-id="${id}"] .badge`);
                if (statusCell) {
                    statusCell.className = 'badge bg-info';
                    statusCell.textContent = 'Обработан';
                }
            }
            break;
            
        case 'delete':
            const confirmMessage = `Вы уверены, что хотите удалить ${typeName} ${itemName}?\n\nЭто действие нельзя отменить.`;
            if (confirm(confirmMessage)) {
                showToast(`🗑️ ${typeName} ${itemName} успешно удален`, 'warning');
                console.log(`${typeName} с ID ${id} помечен для удаления`);
                
                // Имитация удаления строки из таблицы
                const row = document.querySelector(`tr[data-${type}-id="${id}"]`);
                if (row) {
                    row.style.opacity = '0.5';
                    row.style.textDecoration = 'line-through';
                }
            }
            break;
            
        default:
            showToast(`⚙️ Действие "${action}" для ${typeName} ${itemName}`, 'secondary');
            console.log(`Неизвестное действие: ${action}`);
    }
}

// ===== СИСТЕМА УВЕДОМЛЕНИЙ =====
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container') || createToastContainer();
    
    const toastId = 'toast-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
    
    const typeColors = {
        'primary': 'primary',
        'success': 'success',
        'info': 'info',
        'warning': 'warning',
        'danger': 'danger',
        'secondary': 'secondary'
    };
    
    const toastType = typeColors[type] || 'info';
    
    const toastHTML = `
        <div class="toast align-items-center text-bg-${toastType} border-0 fade-in" role="alert" id="${toastId}">
            <div class="d-flex">
                <div class="toast-body">
                    <strong>${message}</strong>
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Закрыть"></button>
            </div>
        </div>
    `;
    
    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: 4000
    });
    
    toast.show();
    
    toastElement.addEventListener('hidden.bs.toast', function() {
        if (toastElement.parentNode) {
            toastElement.remove();
        }
    });
    
    console.log(`💬 Toast показан: ${message} (${type})`);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
    console.log('📦 Контейнер для уведомлений создан');
    return container;
}

function initializeToasts() {
    // Показываем Django messages как toasts
    const messages = document.querySelectorAll('.django-message');
    messages.forEach(function(message) {
        const type = message.dataset.type || 'info';
        showToast(message.textContent.trim(), type);
        message.remove();
    });
    
    console.log(`📨 Инициализировано ${messages.length} системных сообщений`);
}

// ===== РАБОТА С ФИЛЬТРАМИ =====
function initializeFilters() {
    console.log('🔍 Инициализация системы фильтров...');
    
    // Находим и обрабатываем кнопки сброса фильтров
    const clearButtons = document.querySelectorAll('button[onclick*="clearFilters"]');
    clearButtons.forEach(button => {
        button.removeAttribute('onclick');
        button.addEventListener('click', function(e) {
            e.preventDefault();
            clearFilters();
        });
        console.log('🧹 Кнопка сброса фильтров инициализирована');
    });
    
    // Автоотправка формы при изменении select-ов с классом auto-submit
    document.addEventListener('change', function(e) {
        if (e.target.matches('.auto-submit')) {
            console.log('🔄 Автоотправка формы фильтров');
            e.target.closest('form').submit();
        }
    });
}

function clearFilters() {
    console.log('🧹 Начинается сброс фильтров...');
    
    const form = document.querySelector('.filter-form form');
    if (!form) {
        console.error('❌ Форма фильтров не найдена');
        showToast('❌ Форма фильтров не найдена', 'danger');
        return;
    }
    
    const inputs = form.querySelectorAll('input, select');
    let clearedCount = 0;
    let fieldsClearedList = [];
    
    inputs.forEach(input => {
        // Пропускаем CSRF токен
        if (input.name === 'csrfmiddlewaretoken') return;
        
        let wasCleared = false;
        
        if (input.type === 'text' || input.type === 'number' || input.type === 'date') {
            if (input.value.trim() !== '') {
                input.value = '';
                wasCleared = true;
            }
        } else if (input.tagName === 'SELECT') {
            if (input.selectedIndex > 0) {
                input.selectedIndex = 0;
                wasCleared = true;
            }
        }
        
        if (wasCleared) {
            clearedCount++;
            fieldsClearedList.push(input.name || input.id || 'поле');
            
            // Визуальная обратная связь
            input.classList.add('highlight');
            setTimeout(() => {
                input.classList.remove('highlight');
            }, 1000);
        }
    });
    
    console.log(`🧹 Очищено полей: ${clearedCount}`, fieldsClearedList);
    
    if (clearedCount > 0) {
        showToast(`🧹 Очищено ${clearedCount} фильтр(ов)`, 'info');
        
        // Отправляем форму через небольшую задержку
        setTimeout(() => {
            console.log('📤 Отправка формы с очищенными фильтрами');
            form.submit();
        }, 800);
    } else {
        showToast('ℹ️ Фильтры уже очищены', 'info');
    }
}

// ===== ОБНОВЛЕНИЕ СТАТИСТИКИ =====
function refreshDashboardStats() {
    console.log('📊 Обновление статистики дашборда...');
    showToast('🔄 Обновление статистики...', 'info');
    
    // Анимация загрузки для карточек статистики
    const statCards = document.querySelectorAll('.stats-card, .card');
    statCards.forEach((card, index) => {
        setTimeout(() => {
            card.style.transform = 'scale(1.02)';
            card.style.transition = 'transform 0.3s ease';
            
            setTimeout(() => {
                card.style.transform = 'scale(1)';
            }, 300);
        }, index * 100);
    });
    
    // Имитация обновления значений
    setTimeout(() => {
        updateRandomStats();
        showToast('📊 Статистика успешно обновлена!', 'success');
        console.log('✅ Статистика обновлена');
    }, 1500);
}

function updateRandomStats() {
    // Обновляем числовые значения с небольшими случайными изменениями
    const statElements = [
        { id: 'total-products', base: 12, variation: 3 },
        { id: 'total-customers', base: 5, variation: 2 },
        { id: 'active-orders', base: 10, variation: 5 },
        { id: 'total-sales', base: 3584, variation: 500, prefix: '$', decimals: 2 }
    ];
    
    statElements.forEach(stat => {
        const element = document.getElementById(stat.id);
        if (element) {
            const randomChange = (Math.random() - 0.5) * stat.variation;
            const newValue = stat.base + randomChange;
            
            let displayValue;
            if (stat.prefix) {
                displayValue = stat.prefix + newValue.toFixed(stat.decimals || 0);
            } else {
                displayValue = Math.round(newValue).toString();
            }
            
            // Анимация изменения
            element.style.transform = 'scale(1.1)';
            element.style.color = '#007bff';
            
            setTimeout(() => {
                element.textContent = displayValue;
                element.style.transform = 'scale(1)';
                element.style.color = '';
            }, 200);
        }
    });
}

// ===== ЭКСПОРТ ДАННЫХ =====
function initializeExportButtons() {
    console.log('📤 Инициализация кнопок экспорта...');
    
    // Находим кнопки экспорта и добавляем обработчики
    const exportButtons = document.querySelectorAll('[onclick*="exportData"]');
    exportButtons.forEach(button => {
        const onclick = button.getAttribute('onclick');
        button.removeAttribute('onclick');
        
        button.addEventListener('click', function(e) {
            e.preventDefault();
            // Парсим параметры из старого onclick
            const matches = onclick.match(/exportData\('([^']+)',\s*'([^']+)'\)/);
            if (matches) {
                exportData(matches[1], matches[2]);
            }
        });
    });
}

function exportData(format, type) {
    console.log(`📄 Экспорт данных: ${format} для ${type}`);
    showToast(`📄 Начинается экспорт в формате ${format.toUpperCase()}...`, 'info');
    
    // Имитация процесса экспорта
    setTimeout(() => {
        // Создаем ссылку для скачивания (в реальном приложении это будет настоящий файл)
        const currentUrl = new URL(window.location);
        currentUrl.searchParams.set('export', format);
        currentUrl.searchParams.set('type', type);
        
        console.log(`📁 Генерация файла: ${type}_export.${format}`);
        showToast(`✅ Файл ${type}_export.${format} готов к скачиванию!`, 'success');
        
        // В реальном приложении здесь был бы реальный download
        // window.open(currentUrl.toString(), '_blank');
    }, 2000);
}

// ===== КНОПКИ ОБНОВЛЕНИЯ =====
function initializeRefreshButtons() {
    const refreshButtons = document.querySelectorAll('[onclick*="refreshDashboardStats"]');
    refreshButtons.forEach(button => {
        button.removeAttribute('onclick');
        button.addEventListener('click', function(e) {
            e.preventDefault();
            refreshDashboardStats();
        });
    });
    
    console.log(`🔄 Инициализировано ${refreshButtons.length} кнопок обновления`);
}

// ===== ГЛОБАЛЬНЫЕ ФУНКЦИИ =====
window.clearFilters = clearFilters;
window.refreshDashboardStats = refreshDashboardStats;
window.exportData = exportData;
window.handleAction = handleAction;
window.showToast = showToast;

// ===== ОБРАБОТЧИКИ ОШИБОК =====
window.addEventListener('error', function(e) {
    console.error('💥 JavaScript Error:', e.error);
    showToast('❌ Произошла ошибка JavaScript. Проверьте консоль.', 'danger');
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('💥 Unhandled Promise Rejection:', e.reason);
    showToast('❌ Произошла ошибка в асинхронном коде.', 'danger');
});

// ===== ФИНАЛЬНАЯ ИНИЦИАЛИЗАЦИЯ =====
console.log('🎓 Система управления складом аэропорта полностью инициализирована!');
console.log('📋 Доступные функции:', {
    'clearFilters': 'Очистка фильтров',
    'refreshDashboardStats': 'Обновление статистики',
    'exportData': 'Экспорт данных',
    'handleAction': 'Обработка действий кнопок',
    'showToast': 'Показ уведомлений'
});
