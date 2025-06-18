/**
 * Aplicación principal de TradingRoad
 */

// Instancia de API y gráfico
let api = null;
let tradingChart = null;
let currentSymbol = 'BTC/USDT';
let currentInterval = '1h';
let currentExchange = 'binance';
let realtimeEnabled = true;
let wsConnection = null;

// Al cargar el documento
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar API
    api = new TradingRoadAPI(getBaseUrl());
    
    // Inicializar gráfico
    tradingChart = new TradingChart('tradingChart');
    
    // Cargar datos iniciales
    loadInitialData();
    
    // Configurar eventos
    setupEventListeners();
});

/**
 * Obtiene la URL base del backend según el entorno
 */
function getBaseUrl() {
    // Para desarrollo local
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        return 'http://localhost:8000';
    }
    
    // Para producción (misma base que frontend)
    return window.location.origin;
}

/**
 * Carga los datos iniciales
 */
async function loadInitialData() {
    showLoading(true);
    
    try {
        // Cargar lista de exchanges
        const exchanges = await api.getExchanges();
        populateExchanges(exchanges);
        
        // Cargar pares disponibles
        const pairs = await api.getExchangePairs(currentExchange);
        populateSymbols(pairs);
        
        // Cargar datos OHLCV
        await loadChartData();
        
        // Iniciar conexión WebSocket si está habilitado
        if (realtimeEnabled) {
            connectWebSocket();
        }
    } catch (error) {
        console.error('Error al cargar datos iniciales:', error);
        showError('Error al cargar datos: ' + error.message);
    } finally {
        showLoading(false);
    }
}

/**
 * Carga los datos del gráfico para el símbolo y timeframe actuales
 */
async function loadChartData() {
    showLoading(true);
    updateChartTitle();
    
    try {
        // Obtener datos OHLCV
        const klinesData = await api.getKlines(currentSymbol, currentInterval, 200, currentExchange);
        
        // Formatear datos para el gráfico
        const candleData = formatCandleData(klinesData.data);
        
        // Renderizar gráfico de velas
        tradingChart.renderCandlestickSeries(candleData);
        
        // Mostrar volumen si está activado
        if (document.getElementById('volumeCheck').checked) {
            tradingChart.renderVolumeSeries(candleData);
        } else {
            tradingChart.toggleVolumeSeries(false);
        }
        
        // Cargar indicadores si están activados
        await loadIndicators();
        
        // Actualizar datos actuales
        updateCurrentData(candleData[candleData.length - 1]);
    } catch (error) {
        console.error('Error al cargar datos del gráfico:', error);
        showError('Error al cargar datos del gráfico: ' + error.message);
    } finally {
        showLoading(false);
    }
}

/**
 * Carga los indicadores técnicos
 */
async function loadIndicators() {
    try {
        // SMA
        if (document.getElementById('smaCheck').checked) {
            const smaData = await api.getSMA(currentSymbol, currentInterval, [20, 50, 200], currentExchange);
            tradingChart.renderSMA(smaData.data);
        } else {
            tradingChart.toggleSMA(false);
        }
        
        // Bandas de Bollinger
        if (document.getElementById('bollingerCheck').checked) {
            const bollinger = await api.getBollingerBands(currentSymbol, currentInterval, 20, 2.0, currentExchange);
            tradingChart.renderBollingerBands(bollinger.data);
        } else {
            tradingChart.toggleBollingerBands(false);
        }
        
        // RSI
        if (document.getElementById('rsiCheck').checked) {
            const rsiData = await api.getRSI(currentSymbol, currentInterval, 14, currentExchange);
            tradingChart.renderRSIChart('rsiChart', formatRSIData(rsiData.data));
            tradingChart.toggleRSI(true);
        } else {
            tradingChart.toggleRSI(false);
        }
    } catch (error) {
        console.error('Error al cargar indicadores:', error);
        showError('Error al cargar indicadores: ' + error.message);
    }
}

/**
 * Formatea los datos OHLCV para el gráfico
 */
function formatCandleData(data) {
    return data.map(item => ({
        time: item.time,
        open: parseFloat(item.open),
        high: parseFloat(item.high),
        low: parseFloat(item.low),
        close: parseFloat(item.close),
        volume: parseFloat(item.volume)
    }));
}

/**
 * Formatea los datos de RSI para el gráfico
 */
function formatRSIData(data) {
    return data.map(item => ({
        time: item.time,
        value: parseFloat(item.value)
    }));
}

/**
 * Configura todos los eventos
 */
function setupEventListeners() {
    // Cambio de exchange
    document.getElementById('exchangeSelect').addEventListener('change', async function() {
        currentExchange = this.value;
        const pairs = await api.getExchangePairs(currentExchange);
        populateSymbols(pairs);
        
        // Recargar datos
        disconnectWebSocket();
        await loadChartData();
        if (realtimeEnabled) {
            connectWebSocket();
        }
    });
    
    // Cambio de símbolo
    document.getElementById('symbolSelect').addEventListener('change', function() {
        currentSymbol = this.value;
        disconnectWebSocket();
        tradingChart.clear();
        loadChartData();
        if (realtimeEnabled) {
            connectWebSocket();
        }
    });
    
    // Cambio de intervalo
    document.getElementById('intervalSelect').addEventListener('change', function() {
        currentInterval = this.value;
        disconnectWebSocket();
        tradingChart.clear();
        loadChartData();
        if (realtimeEnabled) {
            connectWebSocket();
        }
    });
    
    // Cambios en indicadores
    document.getElementById('smaCheck').addEventListener('change', function() {
        if (this.checked) {
            loadIndicators();
        } else {
            tradingChart.toggleSMA(false);
        }
    });
    
    document.getElementById('bollingerCheck').addEventListener('change', function() {
        if (this.checked) {
            loadIndicators();
        } else {
            tradingChart.toggleBollingerBands(false);
        }
    });
    
    document.getElementById('rsiCheck').addEventListener('change', function() {
        if (this.checked) {
            loadIndicators();
        } else {
            tradingChart.toggleRSI(false);
        }
    });
    
    document.getElementById('volumeCheck').addEventListener('change', function() {
        tradingChart.toggleVolumeSeries(this.checked);
    });
    
    // Switch de tiempo real
    document.getElementById('realtimeSwitch').addEventListener('change', function() {
        realtimeEnabled = this.checked;
        
        if (realtimeEnabled) {
            connectWebSocket();
            document.getElementById('connectionStatus').className = 'badge bg-success';
            document.getElementById('connectionStatus').textContent = 'Conectado';
        } else {
            disconnectWebSocket();
            document.getElementById('connectionStatus').className = 'badge bg-secondary';
            document.getElementById('connectionStatus').textContent = 'Desconectado';
        }
    });
}

/**
 * Inicia la conexión WebSocket
 */
function connectWebSocket() {
    if (wsConnection) {
        disconnectWebSocket();
    }
    
    wsConnection = api.connectToSymbol(
        currentSymbol,
        currentExchange,
        handleWebSocketMessage,
        handleWebSocketError,
        handleWebSocketClose
    );
    
    document.getElementById('connectionStatus').className = 'badge bg-success';
    document.getElementById('connectionStatus').textContent = 'Conectado';
}

/**
 * Desconecta el WebSocket
 */
function disconnectWebSocket() {
    if (wsConnection) {
        api.disconnectFromSymbol(currentSymbol);
        wsConnection = null;
    }
}

/**
 * Maneja mensajes WebSocket
 */
function handleWebSocketMessage(data) {
    if (!data || !data.k) return;
    
    const kline = data.k;
    
    // Actualizar última vela
    const lastCandle = {
        time: kline.t / 1000,  // Convertir de ms a segundos
        open: parseFloat(kline.o),
        high: parseFloat(kline.h),
        low: parseFloat(kline.l),
        close: parseFloat(kline.c),
        volume: parseFloat(kline.v)
    };
    
    tradingChart.updateLastCandle(lastCandle);
    
    // Actualizar volumen
    tradingChart.updateLastVolume({
        time: lastCandle.time,
        value: lastCandle.volume,
        color: lastCandle.close >= lastCandle.open ? '#26A69A' : '#EF5350'
    });
    
    // Actualizar datos actuales
    updateCurrentData(lastCandle);
}

/**
 * Maneja errores WebSocket
 */
function handleWebSocketError(error) {
    console.error('Error WebSocket:', error);
    document.getElementById('connectionStatus').className = 'badge bg-danger';
    document.getElementById('connectionStatus').textContent = 'Error';
    
    // Reintentar conexión después de 5 segundos
    setTimeout(() => {
        if (realtimeEnabled) {
            connectWebSocket();
        }
    }, 5000);
}

/**
 * Maneja cierre WebSocket
 */
function handleWebSocketClose(event) {
    if (event.code !== 1000) {  // No es un cierre normal
        document.getElementById('connectionStatus').className = 'badge bg-warning';
        document.getElementById('connectionStatus').textContent = 'Reconectando...';
        
        // Reintentar conexión después de 3 segundos
        setTimeout(() => {
            if (realtimeEnabled) {
                connectWebSocket();
            }
        }, 3000);
    } else {
        document.getElementById('connectionStatus').className = 'badge bg-secondary';
        document.getElementById('connectionStatus').textContent = 'Desconectado';
    }
}

/**
 * Rellena la lista de exchanges
 */
function populateExchanges(exchanges) {
    const select = document.getElementById('exchangeSelect');
    select.innerHTML = '';
    
    exchanges.data.forEach(exchange => {
        const option = document.createElement('option');
        option.value = exchange.id;
        option.textContent = exchange.name;
        select.appendChild(option);
    });
    
    // Seleccionar el actual
    select.value = currentExchange;
}

/**
 * Rellena la lista de símbolos
 */
function populateSymbols(pairs) {
    const select = document.getElementById('symbolSelect');
    select.innerHTML = '';
    
    pairs.data.forEach(pair => {
        const option = document.createElement('option');
        option.value = pair;
        option.textContent = pair;
        select.appendChild(option);
    });
    
    // Si el símbolo actual no está en la lista, seleccionar el primero
    const symbolExists = Array.from(select.options).some(option => option.value === currentSymbol);
    if (!symbolExists && select.options.length > 0) {
        currentSymbol = select.options[0].value;
    }
    
    // Seleccionar el actual
    select.value = currentSymbol;
}

/**
 * Actualiza el título del gráfico
 */
function updateChartTitle() {
    document.getElementById('chartTitle').textContent = `${currentSymbol} - ${currentInterval}`;
}

/**
 * Actualiza los datos actuales del mercado
 */
function updateCurrentData(lastCandle) {
    if (!lastCandle) return;
    
    // Actualizar precio actual
    const priceElement = document.getElementById('currentPrice');
    priceElement.textContent = lastCandle.close.toFixed(2);
    
    // Calcular cambio en 24h (simulado)
    const changeElement = document.getElementById('priceChange');
    const priceChange = ((lastCandle.close - lastCandle.open) / lastCandle.open) * 100;
    changeElement.textContent = `${priceChange.toFixed(2)}%`;
    
    if (priceChange >= 0) {
        changeElement.className = 'price-up';
    } else {
        changeElement.className = 'price-down';
    }
    
    // Otros indicadores se actualizarán cuando estén disponibles
}

/**
 * Muestra u oculta el indicador de carga
 */
function showLoading(isLoading) {
    // Implementar indicador de carga si es necesario
}

/**
 * Muestra un mensaje de error
 */
function showError(message) {
    console.error(message);
    // Aquí se podría mostrar un toast o alert con el mensaje de error
}
