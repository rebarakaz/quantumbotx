// static/js/portfolio.js

document.addEventListener('DOMContentLoaded', function() {
    // --- Variabel Global ---
    const portfolioTableBody = document.getElementById('portfolio-table-body');
    const portfolioSummary = document.getElementById('portfolio-summary');
    let pnlChart = null; // Variabel untuk menyimpan objek grafik
    let previousTotalProfit = 0; // Untuk melacak tren P/L

    // Data awal untuk grafik
    const chartData = {
        labels: [],
        datasets: [{
            label: 'Total P/L ($)',
            data: [],
            borderColor: 'rgba(59, 130, 246, 1)',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            fill: true,
            tension: 0.4,
            pointRadius: 0 // Sembunyikan titik agar grafik lebih mulus
        }]
    };
    const MAX_CHART_POINTS = 60; // Hanya tampilkan 60 data point terakhir (sekitar 5 menit)

    // --- Fungsi Helper ---
    function initChart() {
        const ctx = document.getElementById('pnlChart').getContext('2d');
        pnlChart = new Chart(ctx, {
            type: 'line',
            data: chartData,
            options: {
                responsive: true, maintainAspectRatio: false,
                scales: { x: { type: 'time', time: { unit: 'minute', displayFormats: { minute: 'HH:mm:ss' } } } },
                plugins: { legend: { display: false }, tooltip: { mode: 'index', intersect: false } }
            }
        });
    }
    const formatCurrency = (value) => {
        const sign = value >= 0 ? '+' : '-';
        return `${sign}$${Math.abs(value).toFixed(2)}`;
    };
    
    async function fetchOpenPositions() {
        try {
            // PERBAIKAN: Menggunakan URL API yang benar
            const response = await fetch('/api/portfolio/open-positions'); // Ini sudah benar
            if (!response.ok) throw new Error('Gagal memuat data portfolio');
            const positions = await response.json();
            
            portfolioTableBody.innerHTML = ''; // Kosongkan tabel
            
            let totalProfit = 0;

            if (positions.length === 0) {
                // PERBAIKAN: colspan disesuaikan menjadi 6 kolom
                portfolioTableBody.innerHTML = '<tr><td colspan="6" class="p-4 text-center text-gray-500">Tidak ada posisi yang sedang terbuka.</td></tr>';
                // Tetap update summary dan chart ke 0
            } else {
                positions.forEach(pos => {
                    totalProfit += pos.profit;
                    const profitClass = pos.profit >= 0 ? 'text-green-600' : 'text-red-600';
                    const typeClass = pos.type === 0 ? 'text-blue-600' : 'text-orange-600';
                    const dealType = pos.type === 0 ? 'BUY' : 'SELL';

                    const row = `
                        <tr class="hover:bg-gray-50">
                            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${pos.symbol}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm font-semibold ${typeClass}">${dealType}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${pos.volume}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${pos.price_open.toFixed(5)}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm font-semibold ${profitClass}">${formatCurrency(pos.profit)}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${pos.magic}</td>
                        </tr>
                    `;
                    portfolioTableBody.innerHTML += row;
                });
            }

            // Update summary total P/L
            const totalProfitClass = totalProfit >= 0 ? 'text-green-600' : 'text-red-600';
            // Tentukan ikon tren
            let trendIcon = '<i class="fas fa-minus text-gray-400"></i>'; // Netral
            if (totalProfit > previousTotalProfit) {
                trendIcon = '<i class="fas fa-arrow-up text-green-500"></i>';
            } else if (totalProfit < previousTotalProfit) {
                trendIcon = '<i class="fas fa-arrow-down text-red-500"></i>';
            }

            portfolioSummary.innerHTML = `
                <p class="text-sm text-gray-500">Total P/L Terbuka</p>
                <p class="text-2xl font-bold ${totalProfitClass}">
                    ${formatCurrency(totalProfit)}
                    <span class="ml-2 text-lg">${trendIcon}</span>
                </p>
            `;
            previousTotalProfit = totalProfit;

            // --- Update Grafik ---
            if (pnlChart) {
                const now = new Date();
                chartData.labels.push(now);
                chartData.datasets[0].data.push(totalProfit);

                // Batasi jumlah data point agar grafik tidak terlalu padat
                if (chartData.labels.length > MAX_CHART_POINTS) {
                    chartData.labels.shift();
                    chartData.datasets[0].data.shift();
                }
                pnlChart.update('none'); // 'none' untuk animasi yang lebih halus
            }

        } catch (error) {
            console.error("Gagal mengambil data portfolio:", error);
            portfolioTableBody.innerHTML = `<tr><td colspan="6" class="p-4 text-center text-red-500">Gagal memuat data: ${error.message}</td></tr>`;
        }
    }

    // Panggil pertama kali, lalu refresh setiap 5 detik agar terasa real-time
    initChart();
    fetchOpenPositions();
    setInterval(fetchOpenPositions, 5000); 
});
