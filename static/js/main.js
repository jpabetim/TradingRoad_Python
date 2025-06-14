// TradingRoad - JavaScript principal

document.addEventListener('DOMContentLoaded', function() {
    console.log('TradingRoad iniciado');
    
    // Inicialización de tooltips para Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    if (tooltipTriggerList.length > 0) {
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Inicialización de popovers para Bootstrap
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    if (popoverTriggerList.length > 0) {
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }
    
    // Funcionalidad para tema oscuro/claro (si se implementa)
    const themeToggler = document.getElementById('theme-toggle');
    if (themeToggler) {
        themeToggler.addEventListener('click', function() {
            document.body.classList.toggle('light-theme');
            const isLightTheme = document.body.classList.contains('light-theme');
            localStorage.setItem('theme', isLightTheme ? 'light' : 'dark');
        });
        
        // Cargar tema guardado
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'light') {
            document.body.classList.add('light-theme');
        }
    }
    
    // Manejo de notificaciones
    function showNotification(message, type = 'info') {
        const container = document.getElementById('notification-container') || createNotificationContainer();
        
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show`;
        notification.role = 'alert';
        
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        container.appendChild(notification);
        
        // Auto-cerrar después de 5 segundos
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                notification.remove();
            }, 150);
        }, 5000);
    }
    
    function createNotificationContainer() {
        const container = document.createElement('div');
        container.id = 'notification-container';
        container.style.position = 'fixed';
        container.style.top = '20px';
        container.style.right = '20px';
        container.style.zIndex = '1050';
        document.body.appendChild(container);
        return container;
    }
    
    // Exportar función para uso global
    window.showNotification = showNotification;
    
    // Función auxiliar para peticiones fetch a la API
    async function apiRequest(endpoint, options = {}) {
        // Configuración por defecto
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'same-origin'
        };
        
        // Obtener token de localStorage si existe
        const token = localStorage.getItem('token');
        if (token) {
            defaultOptions.headers['Authorization'] = `Bearer ${token}`;
        }
        
        // Combinar opciones
        const fetchOptions = {...defaultOptions, ...options};
        
        try {
            // Realizar petición
            const response = await fetch(`/api/v1${endpoint}`, fetchOptions);
            
            // Si la respuesta no es OK
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || `Error ${response.status}: ${response.statusText}`);
            }
            
            // Devolver datos si hay respuesta
            if (response.status !== 204) { // No content
                return await response.json();
            }
            
            return true;
        } catch (error) {
            console.error('API Error:', error);
            showNotification(error.message, 'danger');
            throw error;
        }
    }
    
    // Exportar función para uso global
    window.apiRequest = apiRequest;
    
    // Función para formatear números de precios
    window.formatPrice = function(price, decimals = 2) {
        return new Intl.NumberFormat('es-ES', {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        }).format(price);
    };
    
    // Función para formatear fechas
    window.formatDate = function(dateStr) {
        const date = new Date(dateStr);
        return new Intl.DateTimeFormat('es-ES', {
            dateStyle: 'medium',
            timeStyle: 'short'
        }).format(date);
    };
    
    // Cargar datos de mercado en la página principal si existe el elemento
    const marketSummaryElement = document.getElementById('market-summary');
    if (marketSummaryElement) {
        // Simular carga de datos de mercado para la página principal
        setTimeout(() => {
            marketSummaryElement.innerHTML = `
                <div class="row">
                    <div class="col-md-3 mb-3">
                        <div class="card card-dashboard">
                            <div class="card-body">
                                <h6 class="card-subtitle mb-2 text-muted">BTC/USDT</h6>
                                <h4 class="card-title text-success">$68,245.00</h4>
                                <p class="card-text text-success">+2.34%</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3 mb-3">
                        <div class="card card-dashboard">
                            <div class="card-body">
                                <h6 class="card-subtitle mb-2 text-muted">ETH/USDT</h6>
                                <h4 class="card-title text-success">$3,472.80</h4>
                                <p class="card-text text-success">+1.56%</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3 mb-3">
                        <div class="card card-dashboard">
                            <div class="card-body">
                                <h6 class="card-subtitle mb-2 text-muted">SOL/USDT</h6>
                                <h4 class="card-title text-danger">$142.65</h4>
                                <p class="card-text text-danger">-0.78%</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3 mb-3">
                        <div class="card card-dashboard">
                            <div class="card-body">
                                <h6 class="card-subtitle mb-2 text-muted">XRP/USDT</h6>
                                <h4 class="card-title text-success">$0.5720</h4>
                                <p class="card-text text-success">+3.45%</p>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }, 1000);
    }
});
