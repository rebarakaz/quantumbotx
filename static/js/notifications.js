document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('notifications-container');

    const formatTimestamp = (isoString) => {
        const date = new Date(isoString);
        return date.toLocaleString('id-ID', {
            day: '2-digit', month: 'short', year: 'numeric',
            hour: '2-digit', minute: '2-digit'
        });
    };

    const getNotificationAppearance = (message) => {
        if (message.toLowerCase().includes('berhasil') || message.toLowerCase().includes('dibuka')) {
            return {
                icon: 'fa-check-circle',
                color: 'green'
            };
        }
        if (message.toLowerCase().includes('gagal')) {
            return {
                icon: 'fa-exclamation-triangle',
                color: 'red'
            };
        }
        if (message.toLowerCase().includes('ditutup')) {
            return {
                icon: 'fa-flag-checkered',
                color: 'blue'
            };
        }
        return { icon: 'fa-info-circle', color: 'gray' }; // Default
    };

    async function fetchNotifications() {
        try {
            const response = await fetch('/api/notifications');
            if (!response.ok) throw new Error('Gagal memuat notifikasi');
            const notifications = await response.json();

            container.innerHTML = ''; // Kosongkan pesan "Memuat..."

            if (notifications.length === 0) {
                container.innerHTML = '<p class="p-6 text-center text-gray-500">Tidak ada notifikasi.</p>';
                return;
            }

            notifications.forEach(notif => {
                const appearance = getNotificationAppearance(notif.message);
                const notifElement = `
                    <div class="p-4 flex items-start hover:bg-gray-50 cursor-pointer">
                        <div class="w-10 h-10 rounded-full bg-${appearance.color}-100 flex items-center justify-center text-${appearance.color}-600 mr-4 flex-shrink-0"><i class="fas ${appearance.icon}"></i></div>
                        <div>
                            <p class="text-sm text-gray-800">${notif.message}</p>
                            <p class="text-xs text-gray-500 mt-1">${formatTimestamp(notif.timestamp)}</p>
                        </div>
                    </div>`;
                container.innerHTML += notifElement;
            });
        } catch (error) {
            console.error("Error fetching notifications:", error);
            container.innerHTML = `<p class="p-6 text-center text-red-500">Gagal memuat notifikasi: ${error.message}</p>`;
        }
    }

    fetchNotifications();

    // Setelah memuat notifikasi, tandai semua sebagai sudah dibaca
    fetch('/api/notifications/mark-as-read', {
        method: 'POST'
    }).then(response => response.json())
      .then(data => console.log(data.message))
      .catch(error => console.error('Gagal menandai notifikasi:', error));

});