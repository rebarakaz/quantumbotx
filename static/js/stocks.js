document.addEventListener('DOMContentLoaded', function() {
    fetchStockData();
});

function fetchStockData() {
    fetch('/api/stocks')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(stocks => { // 'stocks' di sini adalah array datanya langsung
            const tableBody = document.getElementById('stocks-table-body');
            if (!tableBody) {
                console.error('Element with ID "stocks-table-body" not found.');
                return;
            }

            tableBody.innerHTML = ''; // Kosongkan isi tabel sebelum diisi data baru

            if (!stocks || stocks.length === 0) {
                // Tampilkan pesan jika tidak ada data atau data kosong
                tableBody.innerHTML = '<tr><td colspan="5" class="text-center">Tidak ada data saham yang tersedia atau gagal dimuat dari MT5.</td></tr>';
                return;
            }

            // Loop melalui setiap item saham dan buat baris tabel
            stocks.forEach(stock => {
                const row = document.createElement('tr');
                const changeClass = stock.change >= 0 ? 'text-success' : 'text-danger';
                const changeIcon = stock.change >= 0 ? '▲' : '▼';

                row.innerHTML = `
                    <td>
                        <div class="d-flex align-items-center">
                            <div class="ms-3">
                                <p class="fw-bold mb-1">${stock.symbol}</p>
                            </div>
                        </div>
                    </td>
                    <td>$${stock.last_price.toFixed(2)}</td>
                    <td class="${changeClass}">
                        ${changeIcon} ${Math.abs(stock.change)}
                    </td>
                    <td>${stock.time}</td>
                    <td>
                        <button type="button" class="btn btn-link btn-sm btn-rounded">
                            Trade
                        </button>
                    </td>
                `;
                tableBody.appendChild(row);
            });
        })
        .catch(error => {
            console.error('Error fetching stock data:', error);
            const tableBody = document.getElementById('stocks-table-body');
            if (tableBody) {
                tableBody.innerHTML = `<tr><td colspan="5" class="text-center text-danger">Gagal memuat data. Periksa konsol untuk detail.</td></tr>`;
            }
        });
}