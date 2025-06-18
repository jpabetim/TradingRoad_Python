/**
 * Cliente API para comunicarse con el backend de TradingRoad
 */
class TradingRoadAPI {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
        this.wsBaseUrl = baseUrl.replace('http://', 'ws://').replace('https://', 'wss://');
        this.activeSockets = {};
    }

    /**
     * Obtiene datos OHLCV para un símbolo y timeframe específicos
     * @param {string} symbol - Par de trading (ej: BTC/USDT)
     * @param {string} interval - Intervalo de tiempo (ej: 1m, 5m, 1h, 1d)
     * @param {number} limit - Cantidad de velas a obtener
     * @param {string} exchange - ID del exchange
     * @returns {Promise<Object>} - Datos OHLCV
     */
    async getKlines(symbol, interval = '1h', limit = 100, exchange = 'binance') {
        try {
            const url = `${this.baseUrl}/api/v1/klines?symbol=${encodeURIComponent(symbol)}&interval=${interval}&limit=${limit}&exchange=${exchange}`;
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`Error API: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error obteniendo klines:', error);
            throw error;
        }
    }

    /**
     * Obtiene todos los indicadores técnicos para un símbolo
     * @param {string} symbol - Par de trading (ej: BTC/USDT)
     * @param {string} interval - Intervalo de tiempo (ej: 1m, 5m, 1h, 1d)
     * @param {string} exchange - ID del exchange
     * @returns {Promise<Object>} - Indicadores técnicos
     */
    async getAllIndicators(symbol, interval = '1h', exchange = 'binance') {
        try {
            const url = `${this.baseUrl}/api/v1/indicators/all?symbol=${encodeURIComponent(symbol)}&interval=${interval}&exchange=${exchange}`;
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`Error API: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error obteniendo indicadores:', error);
            throw error;
        }
    }

    /**
     * Obtiene datos de medias móviles para un símbolo
     * @param {string} symbol - Par de trading (ej: BTC/USDT)
     * @param {string} interval - Intervalo de tiempo (ej: 1m, 5m, 1h, 1d)
     * @param {number[]} periods - Períodos para las medias móviles
     * @param {string} exchange - ID del exchange
     * @returns {Promise<Object>} - Datos de medias móviles
     */
    async getSMA(symbol, interval = '1h', periods = [20, 50, 200], exchange = 'binance') {
        try {
            const periodsParam = periods.join(',');
            const url = `${this.baseUrl}/api/v1/indicators/sma?symbol=${encodeURIComponent(symbol)}&interval=${interval}&periods=${periodsParam}&exchange=${exchange}`;
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`Error API: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error obteniendo SMA:', error);
            throw error;
        }
    }

    /**
     * Obtiene datos de RSI para un símbolo
     * @param {string} symbol - Par de trading (ej: BTC/USDT)
     * @param {string} interval - Intervalo de tiempo (ej: 1m, 5m, 1h, 1d)
     * @param {number} period - Período para RSI
     * @param {string} exchange - ID del exchange
     * @returns {Promise<Object>} - Datos de RSI
     */
    async getRSI(symbol, interval = '1h', period = 14, exchange = 'binance') {
        try {
            const url = `${this.baseUrl}/api/v1/indicators/rsi?symbol=${encodeURIComponent(symbol)}&interval=${interval}&period=${period}&exchange=${exchange}`;
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`Error API: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error obteniendo RSI:', error);
            throw error;
        }
    }

    /**
     * Obtiene bandas de Bollinger para un símbolo
     * @param {string} symbol - Par de trading (ej: BTC/USDT)
     * @param {string} interval - Intervalo de tiempo (ej: 1m, 5m, 1h, 1d)
     * @param {number} period - Período para Bollinger
     * @param {number} stdDev - Desviaciones estándar
     * @param {string} exchange - ID del exchange
     * @returns {Promise<Object>} - Datos de bandas de Bollinger
     */
    async getBollingerBands(symbol, interval = '1h', period = 20, stdDev = 2.0, exchange = 'binance') {
        try {
            const url = `${this.baseUrl}/api/v1/indicators/bands?symbol=${encodeURIComponent(symbol)}&interval=${interval}&period=${period}&std_dev=${stdDev}&exchange=${exchange}`;
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`Error API: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error obteniendo bandas de Bollinger:', error);
            throw error;
        }
    }

    /**
     * Obtiene lista de exchanges disponibles
     * @returns {Promise<Object>} - Lista de exchanges
     */
    async getExchanges() {
        try {
            const url = `${this.baseUrl}/api/v1/exchanges`;
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`Error API: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error obteniendo exchanges:', error);
            throw error;
        }
    }

    /**
     * Obtiene pares de trading disponibles para un exchange
     * @param {string} exchange - ID del exchange
     * @returns {Promise<Object>} - Lista de pares disponibles
     */
    async getExchangePairs(exchange = 'binance') {
        try {
            const url = `${this.baseUrl}/api/v1/exchanges/${exchange}/pairs`;
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`Error API: ${response.status} ${response.statusText}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`Error obteniendo pares para ${exchange}:`, error);
            throw error;
        }
    }

    /**
     * Conecta vía WebSocket para recibir actualizaciones en tiempo real de un símbolo
     * @param {string} symbol - Par de trading (ej: BTC/USDT)
     * @param {string} exchange - ID del exchange
     * @param {function} onMessage - Función callback para mensajes recibidos
     * @param {function} onError - Función callback para errores
     * @param {function} onClose - Función callback para cierre de conexión
     * @returns {WebSocket} - Instancia de WebSocket
     */
    connectToSymbol(symbol, exchange, onMessage, onError, onClose) {
        // Si ya existe una conexión para este símbolo, cerrarla primero
        if (this.activeSockets[symbol]) {
            this.activeSockets[symbol].close();
        }
        
        // Crear nueva conexión WebSocket
        const wsUrl = `${this.wsBaseUrl}/ws/klines/${encodeURIComponent(symbol)}?exchange=${exchange}`;
        const socket = new WebSocket(wsUrl);
        
        // Configurar callbacks
        socket.onopen = () => {
            console.log(`WebSocket conectado para ${symbol}`);
            // Enviar ping cada 30 segundos para mantener la conexión
            socket.pingInterval = setInterval(() => {
                if (socket.readyState === WebSocket.OPEN) {
                    socket.send('ping');
                }
            }, 30000);
        };
        
        socket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (onMessage) onMessage(data);
            } catch (error) {
                console.error('Error procesando mensaje WebSocket:', error);
            }
        };
        
        socket.onerror = (error) => {
            console.error(`Error WebSocket para ${symbol}:`, error);
            if (onError) onError(error);
        };
        
        socket.onclose = (event) => {
            console.log(`WebSocket cerrado para ${symbol}:`, event.code, event.reason);
            // Limpiar el intervalo de ping
            if (socket.pingInterval) {
                clearInterval(socket.pingInterval);
            }
            // Eliminar de sockets activos
            delete this.activeSockets[symbol];
            if (onClose) onClose(event);
        };
        
        // Guardar referencia al socket
        this.activeSockets[symbol] = socket;
        
        return socket;
    }

    /**
     * Desconecta WebSocket para un símbolo específico
     * @param {string} symbol - Par de trading a desconectar
     */
    disconnectFromSymbol(symbol) {
        if (this.activeSockets[symbol]) {
            this.activeSockets[symbol].close();
            delete this.activeSockets[symbol];
        }
    }

    /**
     * Desconecta todos los WebSockets activos
     */
    disconnectAll() {
        Object.keys(this.activeSockets).forEach(symbol => {
            this.activeSockets[symbol].close();
        });
        this.activeSockets = {};
    }
}
