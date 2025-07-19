document.addEventListener('DOMContentLoaded', function() {
    const tableBody = document.getElementById('bots-table-body');
    const createBotBtn = document.getElementById('create-bot-btn');

    const fetchBots = async () => {
        try {
            const response = await fetch('/api/bots');
            const bots = await response.json();
            tableBody.innerHTML = '';

            if (bots.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="5" class="text-center p-6 text-gray-500">Belum ada bot yang dibuat.</td></tr>';
                return;
            }

            bots.forEach(bot => {
                const statusClass = bot.status === 'Aktif' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800';
                const startStopButton = bot.status === 'Aktif'
                    ? `<button data-action="stop" data-id="${bot.id}" class="text-yellow-600 hover:text-yellow-900"><i class="fas fa-pause-circle fa-lg"></i></button>`
                    : `<button data-action="start" data-id="${bot.id}" class="text-green-600 hover:text-green-900"><i class="fas fa-play-circle fa-lg"></i></button>`;

                const row = `
                    <tr>
                        <td class="px-4 py-4">
                            <div class="font-medium text-gray-900">${bot.name}</div>
                            <div class="text-sm text-gray-500">${bot.market}</div>
                        </td>
                        <td class="px-4 py-4 text-sm text-gray-500">
                            <div>Lot: ${bot.lot_size}</div>
                            <div>SL: ${bot.sl_pips} | TP: ${bot.tp_pips}</div>
                        </td>
                        <td class="px-4 py-4 text-sm text-gray-500">
                            <div>Strategy: ${bot.strategy}</div>
                            <div>TF: ${bot.timeframe} | Interval: ${bot.check_interval_seconds}s</div>
                        </td>
                        <td class="px-4 py-4">
                            <span class="px-2 py-1 rounded-full text-xs font-semibold ${statusClass}">${bot.status}</span>
                        </td>
                        <td class="px-4 py-4 text-center">
                            <div class="flex justify-center gap-3">
                                ${startStopButton}
                                <a href="/bots/${bot.id}" class="text-blue-600 hover:text-blue-900"><i class="fas fa-chart-line"></i></a>
                                <button data-action="delete" data-id="${bot.id}" class="text-red-600 hover:text-red-900"><i class="fas fa-trash"></i></button>
                            </div>
                        </td>
                    </tr>
                `;
                tableBody.innerHTML += row;
            });
        } catch (err) {
            console.error("Gagal memuat bot:", err);
        }
    };

    fetchBots();
    setInterval(fetchBots, 10000);
});