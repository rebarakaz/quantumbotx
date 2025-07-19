// Simpan ini sebagai static/js/bot_detail.js
document.addEventListener('DOMContentLoaded', function() {
    const botNameHeader = document.getElementById('bot-name-header');
    const botMarketHeader = document.getElementById('bot-market-header');
    const botStatusBadge = document.getElementById('bot-status-badge');
    const paramsContainer = document.getElementById('bot-parameters-container');
    const fundamentalsSection = document.getElementById('fundamentals-section');
    const analysisContainer = document.getElementById('bot-analysis-container');
    const analysisSignal = document.getElementById('analysis-signal');
    const historyContainer = document.getElementById('history-log-container');

    const pathParts = window.location.pathname.split('/');
    const botId = pathParts[pathParts.length - 1];
    let botStrategy = "";

    const formatTimestamp = (iso) =>
        new Date(iso).toLocaleString('id-ID', {
            day: '2-digit', month: 'short', year: 'numeric',
            hour: '2-digit', minute: '2-digit', second: '2-digit'
        });

    async function fetchBotDetails() {
        try {
            const res = await fetch(`/api/bots/${botId}`);
            const bot = await res.json();
            if (bot.error) throw new Error(bot.error);

            botNameHeader.textContent = bot.name;
            botMarketHeader.textContent = `Pasar: ${bot.market} | Timeframe: ${bot.timeframe}`;
            botStrategy = bot.strategy;

            botStatusBadge.textContent = bot.status;
            botStatusBadge.className = `px-3 py-1 text-xs font-medium rounded-full ${
                bot.status === 'Aktif' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
            }`;

            if (bot.strategy === 'MERCY_EDGE') {
                const aiBadge = document.createElement('span');
                aiBadge.textContent = 'AI';
                aiBadge.className = 'ml-2 px-2 py-1 text-xs bg-purple-100 text-purple-800 rounded-full';
                botStatusBadge.appendChild(aiBadge);
            }

            paramsContainer.innerHTML = `
                <div class="grid grid-cols-2 gap-4">
                    <div><p class="text-gray-500">Lot Size</p><p class="font-semibold text-gray-800">${bot.lot_size}</p></div>
                    <div><p class="text-gray-500">Stop Loss</p><p class="font-semibold text-gray-800">${bot.sl_pips} pips</p></div>
                    <div><p class="text-gray-500">Take Profit</p><p class="font-semibold text-gray-800">${bot.tp_pips} pips</p></div>
                    <div><p class="text-gray-500">Interval</p><p class="font-semibold text-gray-800">${bot.check_interval_seconds}s</p></div>
                    <div><p class="text-gray-500">Strategi</p><p class="font-semibold text-gray-800">${bot.strategy}</p></div>
                </div>
            `;

            if (!bot.market.includes('/')) fetchBotFundamentals();
        } catch (e) {
            console.error('Error fetching bot details:', e);
            botNameHeader.textContent = 'Gagal Memuat';
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

    async function fetchBotAnalysis() {
        try {
            const res = await fetch(`/api/bots/${botId}/analysis`);
            const analysis = await res.json();
            if (analysis.error) throw new Error(analysis.error);

            analysisContainer.innerHTML = "";

            if (botStrategy === "MA_CROSSOVER") {
                analysisContainer.innerHTML = `
                    <p><strong>Harga:</strong> ${analysis.price.toFixed(4)}</p>
                    <p><strong>MA7:</strong> ${analysis.ma7.toFixed(4)}</p>
                    <p><strong>MA25:</strong> ${analysis.ma25.toFixed(4)}</p>`;
            } else if (botStrategy === "RSI_BREAKOUT") {
                analysisContainer.innerHTML = `
                    <p><strong>Harga:</strong> ${analysis.price.toFixed(4)}</p>
                    <p><strong>RSI:</strong> ${analysis.rsi.toFixed(2)}</p>`;
            } else if (botStrategy === "MERCY_EDGE") {
                analysisContainer.innerHTML = `
                    <p><strong>MACD:</strong> ${analysis.macd.toFixed(4)}</p>
                    <p><strong>STOCH %K:</strong> ${analysis.stoch_k.toFixed(2)} | %D: ${analysis.stoch_d.toFixed(2)}</p>`;
            } else if (botStrategy === "PULSE_SYNC") {
                analysisContainer.innerHTML = `
                    <p><strong>AI Signal:</strong> ${analysis.ai_decision}</p>
                    <p><strong>Confidence:</strong> ${analysis.confidence}%</p>`;
            } else {
                for (const [k, v] of Object.entries(analysis)) {
                    if (k !== 'signal') {
                        analysisContainer.innerHTML += `<p><strong>${k}:</strong> ${v}</p>`;
                    }
                }
            }

            // Update sinyal
            analysisSignal.textContent = analysis.signal || "-";
            let color = 'bg-gray-200 text-gray-800';
            if (analysis.signal?.includes('BELI')) color = 'bg-green-100 text-green-800';
            if (analysis.signal?.includes('JUAL')) color = 'bg-red-100 text-red-800';
            analysisSignal.className = `mt-4 text-center font-bold text-lg p-2 rounded-md ${color}`;

        } catch (e) {
            analysisSignal.textContent = e.message;
            analysisSignal.className = 'mt-4 text-center font-bold text-lg p-2 rounded-md bg-yellow-100 text-yellow-800';
        }
    }

    fetchBotDetails();
    fetchBotHistory();
    fetchBotAnalysis();
    setInterval(fetchBotHistory, 10000);
    setInterval(fetchBotAnalysis, 5000);
});
