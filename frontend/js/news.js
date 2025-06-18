/** 
 * NewsManager - Clase para gestionar la carga y visualización de noticias financieras,
 * análisis de sentimiento y calendario económico.
 */
class NewsManager {
    constructor() {
        // API Key para Alpha Vantage (usar 'demo' para desarrollo)
        this.apiKey = 'demo'; 
        
        // Estado de la aplicación
        this.state = {
            symbol: 'GLOBAL',
            period: '7', // Por defecto, 7 días
            topic: 'all',
            calendarWeek: 0, // 0 = semana actual, -1 = anterior, 1 = siguiente
        };
        
        // Referencias a elementos DOM
        this.elements = {
            newsSymbol: document.getElementById('news-symbol'),
            newsPeriod: document.getElementById('news-period'),
            newsTopics: document.getElementById('news-topics'),
            newsContainer: document.getElementById('news-container'),
            newsLoading: document.getElementById('news-loading'),
            refreshNewsBtn: document.getElementById('refresh-news-btn'),
            sentimentTrendChart: document.getElementById('sentiment-trend-chart'),
            sentimentDoughnutChart: document.getElementById('sentiment-doughnut-chart'),
            positivePercent: document.getElementById('positive-percent'),
            neutralPercent: document.getElementById('neutral-percent'),
            negativePercent: document.getElementById('negative-percent'),
            sentimentSourceTable: document.getElementById('sentiment-source-table')?.querySelector('tbody'),
            calendarDateRange: document.getElementById('calendar-date-range'),
            calendarEvents: document.getElementById('calendar-events'),
            calendarPrev: document.getElementById('calendar-prev'),
            calendarNext: document.getElementById('calendar-next'),
            calendarToday: document.getElementById('calendar-today'),
        };
        
        // Instancias de gráficos
        this.charts = {
            sentimentTrend: null,
            sentimentDoughnut: null
        };
    }
    
    /**
     * Inicializa la gestión de noticias
     */
    init() {
        this.setupEventListeners();
        this.loadNews();
        this.initSentimentCharts();
        this.loadCalendar();
    }
    
    /**
     * Configura los event listeners para la interacción del usuario
     */
    setupEventListeners() {
        this.elements.newsSymbol?.addEventListener('change', () => {
            this.state.symbol = this.elements.newsSymbol.value;
            this.loadNews();
            this.updateSentimentCharts();
        });
        
        this.elements.newsPeriod?.addEventListener('change', () => {
            this.state.period = this.elements.newsPeriod.value;
            this.loadNews();
        });
        
        this.elements.newsTopics?.addEventListener('change', () => {
            this.state.topic = this.elements.newsTopics.value;
            this.loadNews();
        });
        
        this.elements.refreshNewsBtn?.addEventListener('click', () => {
            this.loadNews();
            this.updateSentimentCharts();
            this.loadCalendar();
        });
        
        this.elements.calendarPrev?.addEventListener('click', () => {
            this.state.calendarWeek--;
            this.loadCalendar();
        });
        
        this.elements.calendarNext?.addEventListener('click', () => {
            this.state.calendarWeek++;
            this.loadCalendar();
        });
        
        this.elements.calendarToday?.addEventListener('click', () => {
            this.state.calendarWeek = 0;
            this.loadCalendar();
        });
        
        document.getElementById('sentiment-tab')?.addEventListener('shown.bs.tab', () => {
            this.charts.sentimentTrend?.resize();
            this.charts.sentimentDoughnut?.resize();
        });
    }

    /**
     * Carga las noticias según los filtros seleccionados
     */
    async loadNews() {
        if (!this.elements.newsContainer) return;
        
        this.elements.newsLoading.style.display = 'block';
        this.elements.newsContainer.style.display = 'none';
        
        try {
            // Construir la URL para la API del backend
            const timeFrom = this.getTimeFrom();
            const url = `/api/v1/news?topics=${this.state.topic}&time_from=${timeFrom}T0000`;
            
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`Error en la respuesta de la API: ${response.statusText}`);
            }
            const data = await response.json();

            // La API de Alpha Vantage (a través de nuestro backend) devuelve los artículos en la clave 'feed'
            this.renderNews(data.feed);

        } catch (error) {
            console.error('Error cargando noticias:', error);
            this.elements.newsContainer.innerHTML = `<div class="col-12 text-center"><div class="alert alert-danger">Error al cargar noticias desde el servidor.</div></div>`;
        } finally {
            this.elements.newsLoading.style.display = 'none';
            this.elements.newsContainer.style.display = 'flex';
        }
    }
    
    /**
     * Renderiza las tarjetas de noticias
     */
    renderNews(newsFeed) {
        const container = this.elements.newsContainer;
        container.innerHTML = '';
        
        if (!newsFeed || newsFeed.length === 0) {
            container.innerHTML = `<div class="col-12 text-center"><div class="alert alert-info">No se encontraron noticias.</div></div>`;
            return;
        }
        
        newsFeed.forEach(article => {
            const sentimentClass = this.getSentimentClass(article.overall_sentiment_score);
            const sentimentLabel = this.getSentimentLabel(article.overall_sentiment_score);
            
            const card = document.createElement('div');
            card.className = 'col-md-6 col-lg-4 mb-4';
            card.innerHTML = `
                <div class="card news-card h-100 shadow-sm">
                    <div class="card-header d-flex justify-content-between align-items-center">
                        <small class="text-muted"><i class="fas fa-globe me-1"></i> ${article.source}</small>
                        <span class="sentiment-badge ${sentimentClass}">${sentimentLabel}</span>
                    </div>
                    <div class="card-body">
                        <h5 class="card-title">${article.title}</h5>
                        <p class="card-text">${article.summary}</p>
                    </div>
                    <div class="card-footer d-flex justify-content-between align-items-center">
                        <small class="text-muted"><i class="fas fa-clock me-1"></i> ${this.formatDate(article.time_published)}</small>
                        <a href="${article.url}" target="_blank" class="btn btn-sm btn-outline-primary">
                            Leer más <i class="fas fa-external-link-alt ms-1"></i>
                        </a>
                    </div>
                </div>
            `;
            container.appendChild(card);
        });
    }
    
    getSentimentClass(score) {
        if (score > 0.25) return 'sentiment-positive';
        if (score < -0.25) return 'sentiment-negative';
        return 'sentiment-neutral';
    }
    
    getSentimentLabel(score) {
        if (score > 0.25) return 'Positivo';
        if (score < -0.25) return 'Negativo';
        return 'Neutral';
    }
    
    formatDate(isoDate) {
        if (!isoDate) return 'Fecha no disponible';
        return new Date(isoDate).toLocaleString('es-ES', { dateStyle: 'medium', timeStyle: 'short' });
    }
    
    getTimeFrom() {
        const date = new Date();
        date.setDate(date.getDate() - parseInt(this.state.period));
        return date.toISOString().split('T')[0].replace(/-/g, ''); // YYYYMMDD
    }
    
    /**
     * Inicializa y actualiza los gráficos de sentimiento
     */
    initSentimentCharts() {
        if (!this.elements.sentimentTrendChart || !this.elements.sentimentDoughnutChart) return;

        const trendCtx = this.elements.sentimentTrendChart.getContext('2d');
        this.charts.sentimentTrend = new Chart(trendCtx, {
            type: 'line',
            options: { responsive: true, maintainAspectRatio: false }
        });

        const doughnutCtx = this.elements.sentimentDoughnutChart.getContext('2d');
        this.charts.sentimentDoughnut = new Chart(doughnutCtx, {
            type: 'doughnut',
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } }
        });

        this.updateSentimentCharts();
    }

    updateSentimentCharts() {
        const positive = Math.floor(40 + Math.random() * 30);
        const negative = Math.floor(5 + Math.random() * 20);
        const neutral = 100 - positive - negative;

        this.elements.positivePercent.textContent = `${positive}%`;
        this.elements.neutralPercent.textContent = `${neutral}%`;
        this.elements.negativePercent.textContent = `${negative}%`;

        this.charts.sentimentDoughnut.data = {
            labels: ['Positivo', 'Neutral', 'Negativo'],
            datasets: [{
                data: [positive, neutral, negative],
                backgroundColor: ['#198754', '#6c757d', '#dc3545']
            }]
        };
        this.charts.sentimentDoughnut.update();

        this.charts.sentimentTrend.data = {
            labels: ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'],
            datasets: [
                {
                    label: 'Sentimiento Positivo',
                    data: Array(7).fill(0).map(() => (0.3 + Math.random() * 0.4).toFixed(2)),
                    borderColor: '#198754',
                    tension: 0.3, fill: true
                },
                {
                    label: 'Sentimiento Negativo',
                    data: Array(7).fill(0).map(() => (0.1 + Math.random() * 0.2).toFixed(2)),
                    borderColor: '#dc3545',
                    tension: 0.3, fill: true
                }
            ]
        };
        this.charts.sentimentTrend.update();
    }

    /**
     * Carga y renderiza el calendario económico
     */
    async loadCalendar() {
        if (!this.elements.calendarEvents) return;

        const today = new Date();
        const startDate = new Date(today);
        // Ajustar al inicio de la semana (Lunes) y normalizar a medianoche
        startDate.setDate(today.getDate() + (this.state.calendarWeek * 7) - today.getDay() + 1);
        startDate.setHours(0, 0, 0, 0);

        const endDate = new Date(startDate);
        endDate.setDate(startDate.getDate() + 6);

        const startStr = startDate.toLocaleDateString('es-ES', { day: 'numeric', month: 'long' });
        const endStr = endDate.toLocaleDateString('es-ES', { day: 'numeric', month: 'long', year: 'numeric' });
        this.elements.calendarDateRange.innerHTML = `<h4>${startStr} - ${endStr}</h4>`;

        try {
            const url = `/api/v1/economic_calendar`;
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`Error en la respuesta de la API: ${response.statusText}`);
            }
            const data = await response.json();
            
            const filteredEvents = this.filterCalendarEventsForWeek(data.events, startDate);
            this.renderCalendarEvents(filteredEvents);

        } catch (error) {
            console.error('Error cargando el calendario económico:', error);
            this.elements.calendarEvents.innerHTML = `<div class="alert alert-danger">Error al cargar el calendario económico desde el servidor.</div>`;
        }
    }

    filterCalendarEventsForWeek(events, weekStartDate) {
        const weekEndDate = new Date(weekStartDate);
        weekEndDate.setDate(weekStartDate.getDate() + 7);

        if (!events || !Array.isArray(events)) {
            return [];
        }

        return events.filter(event => {
            // La API devuelve fechas en formato YYYY-MM-DD.
            // Creamos la fecha como UTC para evitar problemas de zona horaria.
            const eventDate = new Date(event.date + 'T00:00:00');
            return eventDate >= weekStartDate && eventDate < weekEndDate;
        });
    }

    renderCalendarEvents(events) {
        const container = this.elements.calendarEvents;
        container.innerHTML = '';

        if (!events || events.length === 0) {
            container.innerHTML = `<div class="alert alert-info">No hay eventos para este período.</div>`;
            return;
        }

        const groupedEvents = events.reduce((acc, event) => {
            const date = event.date.split('T')[0];
            if (!acc[date]) acc[date] = [];
            acc[date].push(event);
            return acc;
        }, {});

        for (const date in groupedEvents) {
            const dateObj = new Date(date + 'T00:00:00');
            const dayHeader = document.createElement('h5');
            dayHeader.className = 'mt-4';
            dayHeader.textContent = dateObj.toLocaleDateString('es-ES', { weekday: 'long', day: 'numeric', month: 'long' });
            container.appendChild(dayHeader);

            groupedEvents[date].forEach(event => {
                const impactClass = `impact-${event.impact.toLowerCase()}`;
                const eventCard = document.createElement('div');
                eventCard.className = `card mb-2 ${impactClass}`;
                eventCard.innerHTML = `
                    <div class="card-body p-2">
                        <div class="row align-items-center">
                            <div class="col-md-1 text-center">
                                <span class="badge bg-${event.impact === 'Alto' ? 'danger' : (event.impact === 'Medio' ? 'warning' : 'info')} me-2">${event.impact}</span>
                            </div>
                            <div class="col-md-5"><strong>${event.event}</strong><br><small>${event.country}</small></div>
                            <div class="col-md-2 text-center">${event.time}</div>
                            <div class="col-md-4 row text-center">
                                <div class="col-4"><small>Actual</small><br><strong>${event.actual || '-'}</strong></div>
                                <div class="col-4"><small>Pronóstico</small><br><strong>${event.forecast || '-'}</strong></div>
                                <div class="col-4"><small>Previo</small><br><strong>${event.previous || '-'}</strong></div>
                            </div>
                        </div>
                    </div>
                `;
                container.appendChild(eventCard);
            });
        }
    }

}

// Inicializar el gestor de noticias cuando el DOM esté cargado
document.addEventListener('DOMContentLoaded', () => {
    const newsManager = new NewsManager();
    newsManager.init();
});