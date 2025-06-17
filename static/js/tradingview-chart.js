// TradingView Lightweight Charts Implementation
document.addEventListener('DOMContentLoaded', function() {
    // Chart configuration
    const chartOptions = {
        width: document.getElementById('chart').clientWidth,
        height: document.getElementById('chart').clientHeight,
        layout: {
            background: { color: '#131722' },
            textColor: '#d1d4dc',
        },
        grid: {
            vertLines: { color: 'rgba(42, 46, 57, 0.5)' },
            horzLines: { color: 'rgba(42, 46, 57, 0.5)' },
        },
        crosshair: {
            mode: LightweightCharts.CrosshairMode.Normal,
            vertLine: {
                width: 1,
                color: '#758696',
                style: LightweightCharts.LineStyle.Solid,
                labelBackgroundColor: '#758696',
            },
            horzLine: {
                width: 1,
                color: '#758696',
                style: LightweightCharts.LineStyle.Solid,
                labelBackgroundColor: '#758696',
            },
        },
        timeScale: {
            timeVisible: true,
            secondsVisible: false,
            borderColor: '#2a2e39',
            textColor: '#758696',
        },
        rightPriceScale: {
            borderColor: '#2a2e39',
            textColor: '#758696',
        },
        handleScroll: {
            mouseWheel: true,
            pressedMouseMove: true,
        },
        handleScale: {
            axisPressedMouseMove: true,
            mouseWheel: true,
            pinch: true,
        },
    };

    // Create the chart
    const chart = LightweightCharts.createChart(document.getElementById('chart'), chartOptions);
    
    // Add candlestick series
    const candleSeries = chart.addCandlestickSeries({
        upColor: '#26a69a',
        downColor: '#ef5350',
        borderDownColor: '#ef5350',
        borderUpColor: '#26a69a',
        wickDownColor: '#ef5350',
        wickUpColor: '#26a69a',
    });
    
    // Add volume series
    const volumeSeries = chart.addHistogramSeries({
        color: '#26a69a',
        priceFormat: {
            type: 'volume',
        },
        priceScaleId: '',
        scaleMargins: {
            top: 0.8,
            bottom: 0,
        },
    });

    // Global variables
    let currentSymbol = 'ETHUSDT';
    let currentTimeframe = '5m';
    let currentExchange = 'binance_futures';
    let autoUpdate = true;
    let updateInterval = null;
    let lastUpdateTime = 0;
    let chartData = [];
    let volumeData = [];

    // Helper functions
    function formatPrice(price) {
        return '$' + parseFloat(price).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }

    function calculatePercentageChange(currentPrice, previousPrice) {
        const change = ((currentPrice - previousPrice) / previousPrice) * 100;
        const formattedChange = change.toFixed(2) + '%';
        return { change, formattedChange };
    }

    function updateChartTitle() {
        document.getElementById('chartTitle').textContent = `${currentSymbol} - ${currentTimeframe.toUpperCase()}`;
    }

    function updatePriceInfo(price, change) {
        const priceElement = document.getElementById('currentPrice');
        const changeElement = document.getElementById('priceChange');
        
        priceElement.textContent = formatPrice(price);
        changeElement.textContent = change.formattedChange;
        
        if (change.change >= 0) {
            changeElement.className = 'bullish';
            changeElement.textContent = '+' + change.formattedChange;
        } else {
            changeElement.className = 'bearish';
        }
    }

    // Convert input data to the format required by Lightweight Charts
    function preprocessChartData(data) {
        return data.map(item => ({
            time: item.time,
            open: parseFloat(item.open),
            high: parseFloat(item.high),
            low: parseFloat(item.low),
            close: parseFloat(item.close)
        }));
    }

    function preprocessVolumeData(data) {
        return data.map(item => ({
            time: item.time,
            value: parseFloat(item.volume),
            color: parseFloat(item.open) <= parseFloat(item.close) ? 'rgba(38, 166, 154, 0.5)' : 'rgba(239, 83, 80, 0.5)'
        }));
    }

    // Fetch data from the API
    async function fetchChartData() {
        try {
            const response = await fetch(`/api/v1/market/candles?symbol=${currentSymbol}&timeframe=${currentTimeframe}&exchange=${currentExchange}`);
            if (!response.ok) {
                throw new Error(`API returned ${response.status} ${response.statusText}`);
            }
            
            const data = await response.json();
            if (!data || data.length === 0) {
                console.error('No data received from API');
                return;
            }
            
            chartData = preprocessChartData(data);
            volumeData = preprocessVolumeData(data);
            
            // Update the chart with the new data
            candleSeries.setData(chartData);
            volumeSeries.setData(volumeData);
            
            // Update the UI with the latest price
            const latestCandle = chartData[chartData.length - 1];
            const previousCandle = chartData[chartData.length - 2];
            const priceChange = calculatePercentageChange(latestCandle.close, previousCandle.close);
            
            updatePriceInfo(latestCandle.close, priceChange);
            
            // Store the update time
            lastUpdateTime = Date.now();
        } catch (error) {
            console.error('Error fetching data:', error);
            
            // If API is not available, use sample data for demo purposes
            useSampleData();
        }
    }

    // Sample data for demo purposes
    function useSampleData() {
        const sampleData = generateSampleData();
        chartData = preprocessChartData(sampleData);
        volumeData = preprocessVolumeData(sampleData);
        
        candleSeries.setData(chartData);
        volumeSeries.setData(volumeData);
        
        const latestCandle = chartData[chartData.length - 1];
        const previousCandle = chartData[chartData.length - 2];
        const priceChange = calculatePercentageChange(latestCandle.close, previousCandle.close);
        
        updatePriceInfo(latestCandle.close, priceChange);
    }

    // Generate sample data for demo purposes
    function generateSampleData() {
        const data = [];
        const now = new Date();
        let price = 2550 + Math.random() * 100;
        
        for (let i = 0; i < 100; i++) {
            const time = new Date(now);
            time.setMinutes(now.getMinutes() - (100 - i) * 5);
            
            const volatility = (Math.random() * 2 - 1) * 10;
            const open = price;
            const close = price + volatility;
            const high = Math.max(open, close) + Math.random() * 5;
            const low = Math.min(open, close) - Math.random() * 5;
            const volume = Math.random() * 1000 + 500;
            
            data.push({
                time: time.toISOString().split('T')[0],
                open: open,
                high: high,
                low: low,
                close: close,
                volume: volume
            });
            
            price = close;
        }
        
        return data;
    }

    // Set up auto-update
    function setupAutoUpdate() {
        if (updateInterval) {
            clearInterval(updateInterval);
        }
        
        if (autoUpdate) {
            updateInterval = setInterval(() => {
                fetchChartData();
            }, 15000); // Update every 15 seconds
        }
    }

    // Event handlers
    document.getElementById('autoUpdateSwitch').addEventListener('change', function() {
        autoUpdate = this.checked;
        setupAutoUpdate();
    });

    document.getElementById('analyzeBtn').addEventListener('click', function() {
        // In a real implementation, this would call an AI analysis endpoint
        // For demo purposes, we'll just simulate loading
        const btn = this;
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Analyzing...';
        
        setTimeout(() => {
            btn.disabled = false;
            btn.innerHTML = '<i class="bi bi-magic"></i> Analyze (AI)';
            
            // Add sample analysis results - in a real implementation, this would come from the API
            addSampleAnalysisResults();
        }, 2000);
    });
    
    // Sample analysis results for demo
    function addSampleAnalysisResults() {
        const latestPrice = chartData[chartData.length - 1].close;
        const resistance = latestPrice + 30;
        const support = latestPrice - 50;
        
        // Update analysis panel with sample data
        document.getElementById('primaryScenario').textContent = 
            `Bajista hacia Liquidez Inferior. El precio se encuentra en un retroceso después de un movimiento bajista significativo. Se espera que continúe su movimiento bajista hacia la zona de liquidez compradora alrededor de ${support.toFixed(2)}.`;
        
        document.getElementById('invalidation').textContent = 
            `Cierre de vela de 4H por encima de ${resistance.toFixed(2)} invalidaría este escenario.`;
        
        document.getElementById('entryPrice').textContent = `$${latestPrice.toFixed(2)}`;
        
        // Add Fibonacci levels to chart
        addFibonacciLevels(chartData);
    }
    
    function addFibonacciLevels(data) {
        // Find recent high and low for Fibonacci retracement
        let high = -Infinity;
        let low = Infinity;
        let highIdx = 0;
        let lowIdx = 0;
        
        // Use last 30 candles to find swing high and low
        const startIdx = Math.max(0, data.length - 30);
        
        for (let i = startIdx; i < data.length; i++) {
            if (data[i].high > high) {
                high = data[i].high;
                highIdx = i;
            }
            if (data[i].low < low) {
                low = data[i].low;
                lowIdx = i;
            }
        }
        
        // Determine if we're in an uptrend or downtrend
        const isUptrend = highIdx > lowIdx;
        const range = isUptrend ? high - low : high - low;
        
        // Calculate Fibonacci levels
        const levels = [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1];
        const fibLines = [];
        
        // Clear any existing lines
        chart.removeSeries(fibLines);
        fibLines.length = 0;
        
        // Add Fibonacci lines
        levels.forEach(level => {
            const price = isUptrend ? high - range * level : low + range * level;
            const fibLine = chart.addLineSeries({
                color: level === 0.5 ? '#f5b041' : '#3498db',
                lineWidth: level === 0.5 ? 2 : 1,
                lineStyle: level === 0 || level === 1 ? 0 : 2,
                lastValueVisible: true,
                priceLineVisible: false,
                title: `Fib ${level * 100}%: ${price.toFixed(2)}`,
            });
            
            fibLine.setData([
                { time: data[0].time, value: price },
                { time: data[data.length - 1].time, value: price },
            ]);
            
            fibLines.push(fibLine);
        });
    }

    // Handle timeframe buttons
    document.getElementById('timeframeGroup').addEventListener('click', function(e) {
        if (e.target.tagName === 'BUTTON') {
            // Remove 'active' class from all buttons
            document.querySelectorAll('#timeframeGroup button').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Add 'active' class to clicked button
            e.target.classList.add('active');
            
            // Update timeframe and fetch new data
            currentTimeframe = e.target.dataset.timeframe;
            updateChartTitle();
            fetchChartData();
        }
    });

    // Handle trading pair input
    document.getElementById('tradingPair').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            currentSymbol = this.value.toUpperCase();
            updateChartTitle();
            fetchChartData();
        }
    });

    // Handle data source change
    document.getElementById('dataSource').addEventListener('change', function() {
        currentExchange = this.value;
        fetchChartData();
    });

    // Handle hide/show panel button
    document.getElementById('hideShowPanelBtn').addEventListener('click', function() {
        const panel = document.getElementById('analysisPanel');
        const chartCol = document.querySelector('.col-md-9');
        const icon = this.querySelector('i');
        
        if (panel.style.display === 'none') {
            panel.style.display = 'block';
            chartCol.className = 'col-md-9';
            this.textContent = ' Hide Panel';
            icon.className = 'bi bi-layout-sidebar';
            this.prepend(icon);
        } else {
            panel.style.display = 'none';
            chartCol.className = 'col-md-12';
            this.textContent = ' Show Panel';
            icon.className = 'bi bi-layout-sidebar-inset';
            this.prepend(icon);
        }
        
        // Resize the chart when the layout changes
        chart.resize(
            document.getElementById('chart').clientWidth,
            document.getElementById('chart').clientHeight
        );
    });

    // Handle light/dark mode toggle
    document.getElementById('lightModeBtn').addEventListener('click', function() {
        const isDark = document.body.style.backgroundColor === 'rgb(18, 18, 18)' || document.body.style.backgroundColor === '';
        const icon = this.querySelector('i');
        
        if (isDark) {
            // Switch to light mode
            document.body.style.backgroundColor = '#f8f9fa';
            document.body.style.color = '#212529';
            
            // Update button
            this.textContent = ' Dark Mode';
            icon.className = 'bi bi-moon';
            this.prepend(icon);
            
            // Update chart colors
            chart.applyOptions({
                layout: {
                    background: { color: '#ffffff' },
                    textColor: '#333333',
                },
                grid: {
                    vertLines: { color: '#f0f3fa' },
                    horzLines: { color: '#f0f3fa' },
                },
            });
        } else {
            // Switch to dark mode
            document.body.style.backgroundColor = '#121212';
            document.body.style.color = '#e0e0e0';
            
            // Update button
            this.textContent = ' Light Mode';
            icon.className = 'bi bi-sun';
            this.prepend(icon);
            
            // Update chart colors
            chart.applyOptions({
                layout: {
                    background: { color: '#131722' },
                    textColor: '#d1d4dc',
                },
                grid: {
                    vertLines: { color: 'rgba(42, 46, 57, 0.5)' },
                    horzLines: { color: 'rgba(42, 46, 57, 0.5)' },
                },
            });
        }
    });

    // Handle hide all drawings button
    document.getElementById('hideAllDrawings').addEventListener('click', function() {
        // In a full implementation, this would toggle visibility of all drawings
        // For now, we'll just toggle a class on the button
        this.classList.toggle('active');
    });

    // Handle window resize
    window.addEventListener('resize', function() {
        chart.resize(
            document.getElementById('chart').clientWidth,
            document.getElementById('chart').clientHeight
        );
    });

    // Initialize chart
    updateChartTitle();
    fetchChartData();
    setupAutoUpdate();

    // Make chart responsive
    chart.resize(
        document.getElementById('chart').clientWidth,
        document.getElementById('chart').clientHeight
    );

    // Add a simple SMA indicator
    const smaLine = chart.addLineSeries({
        color: '#2962FF',
        lineWidth: 2,
        title: 'SMA 20',
    });

    // Calculate SMA after data is loaded
    setTimeout(() => {
        if (chartData.length > 0) {
            const period = 20;
            const smaData = [];
            
            for (let i = 0; i < chartData.length; i++) {
                if (i >= period - 1) {
                    let sum = 0;
                    for (let j = 0; j < period; j++) {
                        sum += chartData[i - j].close;
                    }
                    smaData.push({
                        time: chartData[i].time,
                        value: sum / period
                    });
                }
            }
            
            smaLine.setData(smaData);
        }
    }, 1000);
});
