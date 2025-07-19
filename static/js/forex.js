document.addEventListener('DOMContentLoaded', function() {
    fetchForexData();

    // Opsional: Refresh data setiap 30 detik
    // setInterval(fetchForexData, 30000); 
});

function fetchForexData() {
    fetch('/api/forex-data') // Mengambil data dari endpoint API yang sudah kita perbaiki
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            const container = document.getElementById('forex-pairs-container');
            if (!container) {
                console.error('Container element #forex-pairs-container not found.');
                return;
            }

            container.innerHTML = ''; // Kosongkan container sebelum mengisi data baru

            // 'data' adalah objek besar, kita ambil 'keys'-nya (misal: "EURUSD", "GBPUSD")
            const symbols = Object.keys(data);

            if (symbols.length === 0) {
                container.innerHTML = '<p class="text-center">Tidak ada data forex yang tersedia saat ini.</p>';
                return;
            }

            symbols.forEach(symbolKey => {
                const pair = data[symbolKey]; // 'pair' adalah objek detailnya
                
                // Buat elemen card untuk setiap pasangan mata uang
                const card = document.createElement('div');
                card.className = 'col-sm-6 col-md-4 col-lg-3 mb-4';

                card.innerHTML = `
                    <div class="card bg-dark text-light h-100">
                        <div class="card-body d-flex flex-column">
                            <h5 class="card-title">${pair.name}</h5>
                            <p class="card-text flex-grow-1">
                                <span class="d-block">Bid: ${pair.bid}</span>
                                <span class="d-block">Ask: ${pair.ask}</span>
                                <span class="d-block">Spread: ${pair.spread}</span>
                            </p>
                            <a href="#" class="btn btn-primary mt-auto">Trade</a>
                        </div>
                    </div>
                `;
                container.appendChild(card);
            });
        })
        .catch(error => {
            console.error('Error fetching forex data:', error);
            const container = document.getElementById('forex-pairs-container');
            if (container) {
                container.innerHTML = '<p class="text-center text-danger">Gagal memuat data Forex.</p>';
            }
        });
}