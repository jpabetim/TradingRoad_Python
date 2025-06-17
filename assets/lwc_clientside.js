window.lwc = {
    chartInstance: null,
    candlestickSeries: null,
    volumeSeries: null,

    updateChart: function(data, themeData, containerId) {
        if (!data || !data.ohlcv || !document.getElementById(containerId)) {
            return ''; // No data or container not ready
        }

        const chartOptions = {
            layout: {
                background: { type: 'solid', color: themeData.theme === 'dark' ? '#131722' : '#FFFFFF' },
                textColor: themeData.theme === 'dark' ? 'rgba(210, 210, 210, 0.9)' : 'rgba(0, 0, 0, 0.9)',
            },
            grid: {
                vertLines: { color: themeData.theme === 'dark' ? 'rgba(70, 70, 70, 0.5)' : 'rgba(220, 220, 220, 0.5)' },
                horzLines: { color: themeData.theme === 'dark' ? 'rgba(70, 70, 70, 0.5)' : 'rgba(220, 220, 220, 0.5)' },
            },
            crosshair: {
                mode: LightweightCharts.CrosshairMode.Normal,
            },
            rightPriceScale: {
                borderColor: themeData.theme === 'dark' ? 'rgba(197, 203, 206, 0.4)' : 'rgba(100, 100, 100, 0.4)',
            },
            timeScale: {
                borderColor: themeData.theme === 'dark' ? 'rgba(197, 203, 206, 0.4)' : 'rgba(100, 100, 100, 0.4)',
                timeVisible: true,
                secondsVisible: false,
            },
            //localization: { locale: 'es-ES' }, // Example for Spanish localization
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

        if (!window.lwc.chartInstance) {
            const chartContainer = document.getElementById(containerId);
            if (!chartContainer) return '';
            chartContainer.innerHTML = ''; // Clear previous if any (though instance check should prevent this)
            window.lwc.chartInstance = LightweightCharts.createChart(chartContainer, chartOptions);
            
            window.lwc.candlestickSeries = window.lwc.chartInstance.addCandlestickSeries({
                upColor: themeData.theme === 'dark' ? '#26a69a' : '#089981',
                downColor: themeData.theme === 'dark' ? '#ef5350' : '#f23645',
                borderDownColor: themeData.theme === 'dark' ? '#ef5350' : '#f23645',
                borderUpColor: themeData.theme === 'dark' ? '#26a69a' : '#089981',
                wickDownColor: themeData.theme === 'dark' ? '#ef5350' : '#f23645',
                wickUpColor: themeData.theme === 'dark' ? '#26a69a' : '#089981',
            });

            window.lwc.volumeSeries = window.lwc.chartInstance.addHistogramSeries({
                color: '#26a69a', // Default color, will be overridden by data
                priceFormat: {
                    type: 'volume',
                },
                priceScaleId: '', // Set to '' to overlay on main price scale, or create a new one
                // To put volume on a separate pane, you'd set a different priceScaleId
                // and adjust its options. For now, let's assume it's on a separate scale (though not configured yet)
                // For overlay on bottom, often a priceScale with height percentage is used.
            });
            // Example: make volume appear on its own scale at the bottom
            window.lwc.chartInstance.priceScale('').applyOptions({ scaleMargins: { top: 0.8, bottom: 0 } });
            window.lwc.volumeSeries.priceScale().applyOptions({ scaleMargins: { top: 0.8, bottom: 0 } });

        } else {
            // Update existing chart options if theme changed
            window.lwc.chartInstance.applyOptions(chartOptions);
            window.lwc.candlestickSeries.applyOptions({
                upColor: themeData.theme === 'dark' ? '#26a69a' : '#089981',
                downColor: themeData.theme === 'dark' ? '#ef5350' : '#f23645',
                borderDownColor: themeData.theme === 'dark' ? '#ef5350' : '#f23645',
                borderUpColor: themeData.theme === 'dark' ? '#26a69a' : '#089981',
                wickDownColor: themeData.theme === 'dark' ? '#ef5350' : '#f23645',
                wickUpColor: themeData.theme === 'dark' ? '#26a69a' : '#089981',
            });
        }

        window.lwc.candlestickSeries.setData(data.ohlcv);
        
        // Prepare volume data with colors
        const volumeWithColors = data.ohlcv.map((d, i) => ({
            time: d.time,
            value: data.volume[i] ? data.volume[i].value : 0, // Ensure volume data aligns
            color: d.close >= d.open ? (themeData.theme === 'dark' ? 'rgba(38, 166, 154, 0.5)' : 'rgba(8, 153, 129, 0.5)') 
                                    : (themeData.theme === 'dark' ? 'rgba(239, 83, 80, 0.5)' : 'rgba(242, 54, 69, 0.5)'),
        }));
        window.lwc.volumeSeries.setData(volumeWithColors);
        
        // Fit content after setting data
        // window.lwc.chartInstance.timeScale().fitContent();

        return ''; // Dash clientside callbacks expect a return value
    }
};
