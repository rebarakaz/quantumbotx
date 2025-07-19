        document.getElementById('sidebar-toggle').addEventListener('click', function() {
            document.getElementById('sidebar').classList.toggle('collapsed');
        });
        async function fetchCryptoData() {
            try {
                const response = await fetch('/api/crypto');
                const cryptos = await response.json();
                const tableBody = document.querySelector('tbody');
                tableBody.innerHTML = ''; // Kosongkan data lama

                cryptos.forEach(crypto => {
                    const row = `
                        <tr>
                            <td class="px-6 py-4 whitespace-nowrap"><div class="flex items-center"><div class="font-medium text-gray-900">${crypto.name}</div><div class="text-sm text-gray-500 ml-2">${crypto.symbol}</div></div></td>
                            <td class="px-6 py-4 whitespace-nowrap font-medium">${crypto.price}</td>
                            <td class="px-6 py-4 whitespace-nowrap ${crypto.change.startsWith('+') ? 'text-green-600' : 'text-red-600'} font-medium">${crypto.change}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${crypto.market_cap}</td>
                            <td class="px-6 py-4 whitespace-nowrap text-right"><button class="bg-blue-600 text-white py-1 px-3 rounded-md text-sm font-medium hover:bg-blue-700">Trade</button></td>
                        </tr>
                    `;
                    tableBody.innerHTML += row;
                });
            } catch (error) {
                console.error('Gagal mengambil data crypto:', error);
            }
        }

        document.addEventListener('DOMContentLoaded', fetchCryptoData);
        setInterval(fetchCryptoData, 15000); // Kita perlama intervalnya