// static/js/bot_detail.js
document.addEventListener('DOMContentLoaded', function() {
    // --- Elemen Global ---
    const botNameHeader = document.getElementById('bot-name-header');
    const botMarketHeader = document.getElementById('bot-market-header');
    const botStatusBadge = document.getElementById('bot-status-badge');
    const paramsContainer = document.getElementById('bot-parameters-container');
    const fundamentalsSection = document.getElementById('fundamentals-section');
    const analysisContainer = document.getElementById('bot-analysis-container');
    const analysisSignal = document.getElementById('analysis-signal');
    const historyContainer = document.getElementById('history-log-container');

    // --- State & Helper ---
    const pathParts = window.location.pathname.split('/');
    const botId = pathParts[pathParts.length - 1];
    let botData = null; // Gunakan objek untuk menyimpan semua data bot, bukan hanya strategi

    const formatTimestamp = (iso) =>
        new Date(iso).toLocaleString('id-ID', {
            day: '2-digit', month: 'short', year: 'numeric',
            hour: '2-digit', minute: '2-digit', second: '2-digit'
        });

    // --- Fungsi Pengambil Data ---

    async function fetchBotDetails() {
        try {
            const res = await fetch(`/api/bots/${botId}`);
            if (!res.ok) throw new Error('Gagal memuat detail bot dari server.');
            botData = await res.json();
            if (botData.error) throw new Error(botData.error);

            // Render detail bot
            botNameHeader.textContent = botData.name;
            botMarketHeader.textContent = `Pasar: ${botData.market} | Timeframe: ${botData.timeframe}`;
            
            botStatusBadge.textContent = botData.status;
            botStatusBadge.className = `px-3 py-1 text-xs font-medium rounded-full ${
                botData.status === 'Aktif' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
            }`;

            if (botData.strategy.includes('MERCY') || botData.strategy.includes('PULSE')) {
                const aiBadge = document.createElement('span');
                aiBadge.textContent = 'AI';
                aiBadge.className = 'ml-2 px-2 py-1 text-xs bg-purple-100 text-purple-800 rounded-full';
                botStatusBadge.appendChild(aiBadge);
            }

            paramsContainer.innerHTML = `
                <div class="grid grid-cols-2 gap-4">
                    <div><p class="text-gray-500">Lot Size</p><p class="font-semibold text-gray-800">${botData.lot_size}</p></div>
                    <div><p class="text-gray-500">Stop Loss</p><p class="font-semibold text-gray-800">${botData.sl_pips} pips</p></div>
                    <div><p class="text-gray-500">Take Profit</p><p class="font-semibold text-gray-800">${botData.tp_pips} pips</p></div>
                    <div><p class="text-gray-500">Interval</p><p class="font-semibold text-gray-800">${botData.check_interval_seconds}s</p></div>
                    <div><p class="text-gray-500">Strategi</p><p class="font-semibold text-gray-800">${botData.strategy}</p></div>
                </div>
            `;

            if (!botData.market.includes('/')) fetchBotFundamentals();
            
            // ** PERBAIKAN RACE CONDITION **
            // Panggil fetchBotAnalysis HANYA SETELAH detail bot berhasil didapat.
            await fetchBotAnalysis();

        } catch (e) {
            console.error('Error fetching bot details:', e);
            botNameHeader.textContent = 'Gagal Memuat';
            botStatusBadge.textContent = 'Error';
            botStatusBadge.className = 'px-3 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800';
        }
    }
    
    async function fetchBotFundamentals() {
        try {
            const res = await fetch(`/api/bots/${botId}/fundamentals`);
            const data = await res.json();

            if (data.recommendations) {
                const r = data.recommendations;
                fundamentalsSection.innerHTML = `
                    <div class="bg-white rounded-lg shadow p-4 mt-6">
                        <h3 class="text-lg font-semibold text-gray-800 border-b pb-2 mb-3">Konsensus Analis</h3>
                        <div class="flex justify-around text-center text-xs">
                            <div><p class="text-xl font-bold text-green-600">${r.strongBuy}</p><p>Strong Buy</p></div>
                            <div><p class="text-xl font-bold text-green-500">${r.buy}</p><p>Buy</p></div>
                            <div><p class="text-xl font-bold text-gray-500">${r.hold}</p><p>Hold</p></div>
                            <div><p class="text-xl font-bold text-red-500">${r.sell}</p><p>Sell</p></div>
                            <div><p class="text-xl font-bold text-red-700">${r.strongSell}</p><p>Strong Sell</p></div>
                        </div>
                    </div>
                `;
            }
        } catch (e) {
            console.error("Gagal mengambil data fundamental:", e);
        }
    }

    async function fetchBotHistory() {
        try {
            const res = await fetch(`/api/bots/${botId}/history`);
            const history = await res.json();
            historyContainer.innerHTML = '';

            if (history.length === 0) {
                historyContainer.innerHTML = '<p class="text-gray-500 p-4 text-center">Belum ada aktivitas.</p>';
                return;
            }

            history.forEach(log => {
                let icon = 'fa-info-circle text-blue-500';
                if (log.action.includes('BELI')) icon = 'fa-arrow-up text-green-500';
                if (log.action.includes('JUAL')) icon = 'fa-arrow-down text-red-500';

                historyContainer.innerHTML += `
                    <div class="flex items-start p-3 border-b border-gray-100">
                        <i class="fas ${icon} mt-1 mr-3"></i>
                        <div class="flex-1">
                            <p class="text-sm text-gray-800">${log.details}</p>
                            <p class="text-xs text-gray-400 mt-1">${formatTimestamp(log.timestamp)}</p>
                        </div>
                    </div>`;
            });
        } catch (e) {
            console.error('Error fetching history:', e);
        }
    }

    // ** FUNGSI INI DIBUAT JAUH LEBIH KUAT (ROBUST) **
    async function fetchBotAnalysis() {
        if (!botData) { // Jangan jalankan jika detail bot belum ada
            console.log("Menunggu detail bot sebelum mengambil analisis...");
            return;
        }

        try {
            const res = await fetch(`/api/bots/${botId}/analysis`);
            if (!res.ok) throw new Error('Gagal memuat data analisis dari server.');
            const analysis = await res.json();
            if (analysis.error) throw new Error(analysis.error);

            analysisContainer.innerHTML = ""; // Bersihkan kontainer
            const botStrategy = botData.strategy;

            // ** PERBAIKAN KODE RAPUH (FRAGILE CODE) **
            // Gunakan optional chaining (?.) untuk mengakses properti dengan aman.
            // Gunakan nullish coalescing (??) untuk memberikan nilai default jika data tidak ada.
            
            if (botStrategy === "MA_CROSSOVER") {
                analysisContainer.innerHTML = `
                    <p><strong>Harga:</strong> ${analysis.price?.toFixed(5) ?? 'N/A'}</p>
                    <p><strong>MA Fast:</strong> ${analysis.ma_fast?.toFixed(5) ?? 'N/A'}</p>
                    <p><strong>MA Slow:</strong> ${analysis.ma_slow?.toFixed(5) ?? 'N/A'}</p>`;
            } else if (botStrategy === "RSI_BREAKOUT") {
                analysisContainer.innerHTML = `
                    <p><strong>Harga:</strong> ${analysis.price?.toFixed(5) ?? 'N/A'}</p>
                    <p><strong>RSI (14):</strong> ${analysis.rsi?.toFixed(2) ?? 'N/A'}</p>`;
            } else if (botStrategy === "MERCY_EDGE" || botStrategy === "FULL_MERCY") {
                analysisContainer.innerHTML = `
                    <p><strong>Harga:</strong> ${analysis.price?.toFixed(5) ?? 'N/A'}</p>
                    <p><strong>MACD Hist D1:</strong> ${analysis.D1_MACDh?.toFixed(5) ?? 'N/A'}</p>
                    <p><strong>MACD Hist H1:</strong> ${analysis.H1_MACDh?.toFixed(5) ?? 'N/A'}</p>
                    <p><strong>Stoch %K:</strong> ${analysis.H1_STOCHk?.toFixed(2) ?? 'N/A'} | <strong>%D:</strong> ${analysis.H1_STOCHd?.toFixed(2) ?? 'N/A'}</p>`;
            } 
            // Tambahkan strategi lain yang Anda buat di sini
            else { 
                // Fallback untuk strategi yang tidak dikenal, tampilkan semua data yang ada
                for (const [key, value] of Object.entries(analysis)) {
                    if (key !== 'signal' && value !== null) {
                        const formattedValue = typeof value === 'number' ? value.toFixed(5) : value;
                        analysisContainer.innerHTML += `<p><strong>${key}:</strong> ${formattedValue}</p>`;
                    }
                }
            }

            // Update sinyal
            analysisSignal.textContent = analysis.signal || "TAHAN";
            let color = 'bg-gray-200 text-gray-800';
            if (analysis.signal?.includes('BUY') || analysis.signal?.includes('BULLISH')) color = 'bg-green-100 text-green-800';
            if (analysis.signal?.includes('SELL') || analysis.signal?.includes('BEARISH')) color = 'bg-red-100 text-red-800';
            analysisSignal.className = `mt-4 text-center font-bold text-lg p-2 rounded-md ${color}`;

        } catch (e) {
            console.error('Error fetching bot analysis:', e);
            analysisSignal.textContent = e.message || 'Error Analisis';
            analysisSignal.className = 'mt-4 text-center font-bold text-lg p-2 rounded-md bg-yellow-100 text-yellow-800';
            analysisContainer.innerHTML = '<p class="text-center text-gray-500">- Gagal memuat data -</p>';
        }
    }

    // --- Pusat Kontrol ---
    // HANYA panggil DUA fungsi ini di awal. fetchBotAnalysis akan dipanggil oleh fetchBotDetails.
    fetchBotDetails();
    fetchBotHistory();

    // Set interval seperti biasa
    setInterval(fetchBotHistory, 10000);
    // PERBAIKAN: Interval analisis sekarang juga memanggil fetchBotDetails
    // agar data bot (misal strateginya diedit) ikut ter-update.
    setInterval(fetchBotDetails, 5000); 
});