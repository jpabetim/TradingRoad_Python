/**
 * TradingChart - Componente para gráficos de trading usando TradingView Lightweight Charts
 */
class TradingChart {
    /**
     * Inicializa un nuevo gráfico de trading
     * @param {string} containerId - ID del contenedor HTML para el gráfico
     * @param {Object} options - Opciones de configuración
     */
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        this.options = Object.assign({
            // Opciones por defecto
            theme: 'dark',
            autosize: true,
            timeScale: {
                timeVisible: true,
                secondsVisible: false,
                borderColor: '#2B2B43',
                textColor: '#D9D9D9',
                tickMarkFormatter: (time) => {
                    const date = new Date(time * 1000);
                    return date.getHours() + ':' + date.getMinutes().toString().padStart(2, '0');
                }
            },
            rightPriceScale: {
                borderColor: '#2B2B43',
                textColor: '#D9D9D9',
            },
            layout: {
                background: { color: '#131722' },
                textColor: '#D9D9D9',
            },
            grid: {
                horzLines: { color: '#363C4E' },
                vertLines: { color: '#363C4E' },
            },
        }, options);

        // Series y chart
        this.chart = null;
        this.candlestickSeries = null;
        this.volumeSeries = null;
        this.indicatorSeries = {};

        this.initializeChart();
    }

    /**
     * Inicializa el gráfico con la configuración básica
     */
    initializeChart() {
        if (!this.container) {
            console.error(`Contenedor ${this.containerId} no encontrado`);
            return;
        }

        // Crear instancia del gráfico
        this.chart = LightweightCharts.createChart(this.container, this.options);

        // Hacer responsivo
        this.makeResponsive();
    }

    /**
     * Hace que el gráfico sea responsivo
     */
    makeResponsive() {
        const resizeObserver = new ResizeObserver(entries => {
            if (entries.length === 0 || entries[0].target !== this.container) {
                return;
            }
            const newRect = entries[0].contentRect;
            this.chart.applyOptions({ height: newRect.height, width: newRect.width });
        });

        resizeObserver.observe(this.container);
    }

    /**
     * Cambia el tema del gráfico
     * @param {string} theme - 'light' o 'dark'
     */
    setTheme(theme) {
        const isDark = theme === 'dark';
        this.chart.applyOptions({
            layout: {
                background: { color: isDark ? '#131722' : '#FFFFFF' },
                textColor: isDark ? '#D9D9D9' : '#191919',
            },
            grid: {
                horzLines: { color: isDark ? '#363C4E' : '#F0F3FA' },
                vertLines: { color: isDark ? '#363C4E' : '#F0F3FA' },
            },
            rightPriceScale: {
                borderColor: isDark ? '#2B2B43' : '#E0E3EB',
                textColor: isDark ? '#D9D9D9' : '#191919',
            },
            timeScale: {
                borderColor: isDark ? '#2B2B43' : '#E0E3EB',
                textColor: isDark ? '#D9D9D9' : '#191919',
            }
        });
    }

    /**
     * Crea o actualiza la serie de velas
     * @param {Array} data - Datos OHLCV para mostrar
     */
    renderCandlestickSeries(data) {
        if (!this.chart) return;
        
        if (this.candlestickSeries) {
            // Actualizar datos en serie existente
            this.candlestickSeries.setData(data);
        } else {
            // Crear nueva serie
            this.candlestickSeries = this.chart.addCandlestickSeries({
                upColor: '#26A69A', 
                downColor: '#EF5350',
                borderUpColor: '#26A69A', 
                borderDownColor: '#EF5350',
                wickUpColor: '#26A69A', 
                wickDownColor: '#EF5350',
                priceFormat: {
                    type: 'price',
                    precision: 2,
                    minMove: 0.01,
                }
            });
            this.candlestickSeries.setData(data);
        }
        
        // Ajustar escala de visualización
        this.chart.timeScale().fitContent();
    }

    /**
     * Actualiza el último punto de la serie de velas
     * @param {Object} lastBar - Última barra a actualizar
     */
    updateLastCandle(lastBar) {
        if (this.candlestickSeries) {
            this.candlestickSeries.update(lastBar);
        }
    }

    /**
     * Renderiza serie de volumen
     * @param {Array} data - Datos de volumen
     */
    renderVolumeSeries(data) {
        if (!this.chart) return;
        
        if (!this.volumeSeries) {
            this.volumeSeries = this.chart.addHistogramSeries({
                color: '#26A69A',
                priceFormat: {
                    type: 'volume',
                },
                priceScaleId: 'volume',
                scaleMargins: {
                    top: 0.8,
                    bottom: 0,
                },
            });
        }
        
        // Preparar datos de volumen con colores
        const volumeData = data.map(item => ({
            time: item.time,
            value: item.volume,
            color: item.close >= item.open ? '#26A69A' : '#EF5350'
        }));
        
        this.volumeSeries.setData(volumeData);
    }

    /**
     * Oculta o muestra la serie de volumen
     * @param {boolean} visible - Indica si la serie debe ser visible
     */
    toggleVolumeSeries(visible) {
        if (this.volumeSeries) {
            this.volumeSeries.applyOptions({
                visible: visible
            });
        }
    }

    /**
     * Actualiza el último volumen
     * @param {Object} lastBar - Última barra con datos de volumen
     */
    updateLastVolume(lastBar) {
        if (this.volumeSeries) {
            this.volumeSeries.update({
                time: lastBar.time,
                value: lastBar.volume,
                color: lastBar.close >= lastBar.open ? '#26A69A' : '#EF5350'
            });
        }
    }

    /**
     * Renderiza medias móviles
     * @param {Array} smaData - Datos de SMA organizados por período
     */
    renderSMA(smaData) {
        if (!this.chart || !smaData || !Array.isArray(smaData)) return;
        
        // Colores para SMA por periodo
        const colors = {
            20: '#2196F3',  // Azul
            50: '#FF9800',  // Naranja
            200: '#E91E63'  // Rosa
        };
        
        // Renderizar cada SMA como una línea
        smaData.forEach(sma => {
            const period = sma.period;
            const seriesId = `sma${period}`;
            const color = colors[period] || '#2196F3';
            
            // Crear o actualizar serie
            if (!this.indicatorSeries[seriesId]) {
                this.indicatorSeries[seriesId] = this.chart.addLineSeries({
                    color: color,
                    lineWidth: 2,
                    priceLineVisible: false,
                    lastValueVisible: true,
                    lineType: 0,
                    title: `SMA ${period}`,
                });
            }
            
            this.indicatorSeries[seriesId].setData(sma.series);
        });
    }

    /**
     * Renderiza bandas de Bollinger
     * @param {Object} data - Datos de bandas de Bollinger
     */
    renderBollingerBands(data) {
        if (!this.chart || !data) return;
        
        // Crear o actualizar serie de banda media
        if (!this.indicatorSeries.bollingerMiddle) {
            this.indicatorSeries.bollingerMiddle = this.chart.addLineSeries({
                color: '#9C27B0',  // Púrpura
                lineWidth: 2,
                title: 'BB Middle',
            });
        }
        this.indicatorSeries.bollingerMiddle.setData(data.middle);
        
        // Crear o actualizar banda superior
        if (!this.indicatorSeries.bollingerUpper) {
            this.indicatorSeries.bollingerUpper = this.chart.addLineSeries({
                color: '#9C27B0',  // Púrpura
                lineWidth: 1,
                lineStyle: 1,  // Linea punteada
                title: 'BB Upper',
            });
        }
        this.indicatorSeries.bollingerUpper.setData(data.upper);
        
        // Crear o actualizar banda inferior
        if (!this.indicatorSeries.bollingerLower) {
            this.indicatorSeries.bollingerLower = this.chart.addLineSeries({
                color: '#9C27B0',  // Púrpura
                lineWidth: 1,
                lineStyle: 1,  // Linea punteada
                title: 'BB Lower',
            });
        }
        this.indicatorSeries.bollingerLower.setData(data.lower);
    }

    /**
     * Oculta o muestra las bandas de Bollinger
     * @param {boolean} visible - Indica si las bandas deben ser visibles
     */
    toggleBollingerBands(visible) {
        ['bollingerMiddle', 'bollingerUpper', 'bollingerLower'].forEach(id => {
            if (this.indicatorSeries[id]) {
                this.indicatorSeries[id].applyOptions({ visible });
            }
        });
    }

    /**
     * Oculta o muestra las medias móviles
     * @param {boolean} visible - Indica si las SMA deben ser visibles
     */
    toggleSMA(visible) {
        Object.keys(this.indicatorSeries).forEach(id => {
            if (id.startsWith('sma')) {
                this.indicatorSeries[id].applyOptions({ visible });
            }
        });
    }

    /**
     * Limpia todos los indicadores técnicos
     */
    clearIndicators() {
        Object.keys(this.indicatorSeries).forEach(id => {
            if (this.indicatorSeries[id]) {
                this.chart.removeSeries(this.indicatorSeries[id]);
                delete this.indicatorSeries[id];
            }
        });
    }

    /**
     * Limpia completamente el gráfico y lo reinicia
     */
    clear() {
        if (this.chart) {
            // Eliminar todas las series
            if (this.candlestickSeries) {
                this.chart.removeSeries(this.candlestickSeries);
                this.candlestickSeries = null;
            }
            
            if (this.volumeSeries) {
                this.chart.removeSeries(this.volumeSeries);
                this.volumeSeries = null;
            }
            
            this.clearIndicators();
        }
    }

    /**
     * Renderiza un gráfico de RSI en un contenedor separado
     * @param {string} containerId - ID del contenedor para el gráfico RSI
     * @param {Array} data - Datos de RSI
     */
    renderRSIChart(containerId, data) {
        const container = document.getElementById(containerId);
        
        if (!container) {
            console.error(`Contenedor para RSI ${containerId} no encontrado`);
            return;
        }
        
        // Si ya existe un gráfico, eliminarlo
        if (this.rsiChart) {
            this.rsiChart.remove();
            this.rsiChart = null;
            this.rsiSeries = null;
        }
        
        // Crear gráfico RSI
        this.rsiChart = LightweightCharts.createChart(container, {
            height: container.offsetHeight,
            width: container.offsetWidth,
            autoSize: true,
            layout: {
                background: { color: '#131722' },
                textColor: '#D9D9D9',
            },
            grid: {
                horzLines: { color: '#363C4E' },
                vertLines: { color: '#363C4E' },
            },
            timeScale: {
                borderColor: '#2B2B43',
                timeVisible: true,
                secondsVisible: false,
            },
            rightPriceScale: {
                borderColor: '#2B2B43',
            },
        });
        
        // Crear serie RSI
        this.rsiSeries = this.rsiChart.addLineSeries({
            color: '#FF9800',
            lineWidth: 2,
            title: 'RSI',
            priceFormat: {
                type: 'price',
                precision: 2,
                minMove: 0.01,
            },
        });
        
        // Añadir datos
        this.rsiSeries.setData(data);
        
        // Añadir líneas horizontales para niveles de sobrecompra/sobreventa
        const overboughtSeries = this.rsiChart.addLineSeries({
            color: '#EF5350', // Rojo
            lineWidth: 1,
            lineStyle: 1,
            title: 'Overbought',
        });
        
        const oversoldSeries = this.rsiChart.addLineSeries({
            color: '#26A69A', // Verde
            lineWidth: 1,
            lineStyle: 1,
            title: 'Oversold',
        });
        
        // Crear puntos para líneas horizontales en todo el rango de tiempo
        if (data.length > 0) {
            const timePoints = data.map(point => point.time);
            const min = Math.min(...timePoints);
            const max = Math.max(...timePoints);
            
            const overboughtData = [
                { time: min, value: 70 },
                { time: max, value: 70 }
            ];
            
            const oversoldData = [
                { time: min, value: 30 },
                { time: max, value: 30 }
            ];
            
            overboughtSeries.setData(overboughtData);
            oversoldSeries.setData(oversoldData);
        }
        
        // Sincronizar escala de tiempo con el gráfico principal
        this.chart.timeScale().subscribeVisibleTimeRangeChange((timeRange) => {
            if (this.rsiChart && timeRange) {
                this.rsiChart.timeScale().setVisibleRange(timeRange);
            }
        });
        
        // Hacer responsivo
        const resizeObserver = new ResizeObserver(entries => {
            if (entries.length === 0 || entries[0].target !== container) {
                return;
            }
            const newRect = entries[0].contentRect;
            this.rsiChart.resize(newRect.width, newRect.height);
        });
        
        resizeObserver.observe(container);
    }

    /**
     * Muestra u oculta el gráfico de RSI
     * @param {boolean} visible - Indica si el RSI debe ser visible
     */
    toggleRSI(visible) {
        const container = document.getElementById('rsiChart');
        if (container) {
            container.style.display = visible ? 'block' : 'none';
        }
    }

    /**
     * Actualiza la última barra de RSI
     * @param {Object} point - Punto con tiempo y valor
     */
    updateLastRSI(point) {
        if (this.rsiSeries) {
            this.rsiSeries.update(point);
        }
    }

    /**
     * Destruye el gráfico y limpia recursos
     */
    destroy() {
        if (this.chart) {
            this.chart.remove();
            this.chart = null;
        }
        
        if (this.rsiChart) {
            this.rsiChart.remove();
            this.rsiChart = null;
        }
        
        this.candlestickSeries = null;
        this.volumeSeries = null;
        this.indicatorSeries = {};
        this.rsiSeries = null;
    }
}
