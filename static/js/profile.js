        document.getElementById('sidebar-toggle').addEventListener('click', function() {
            document.getElementById('sidebar').classList.toggle('collapsed');
        });

        document.addEventListener('DOMContentLoaded', function() {
            const profileForm = document.getElementById('profile-form');
            const profileNameInput = document.getElementById('profile-name');
            const profileEmailInput = document.getElementById('profile-email');
            const profilePasswordInput = document.getElementById('profile-password');
            const displayName = document.getElementById('profile-display-name');
            const joinDate = document.getElementById('profile-join-date');

            // Fungsi untuk memuat data profil
            const loadProfile = async () => {
                try {
                    const response = await fetch('/api/profile');
                    if (!response.ok) throw new Error('Gagal memuat data profil');
                    const user = await response.json();
                    
                    // Isi form dan tampilan dengan data dari API
                    profileNameInput.value = user.name;
                    profileEmailInput.value = user.email;
                    displayName.textContent = user.name;
                    joinDate.textContent = `Bergabung sejak: ${user.join_date}`;
                } catch (error) {
                    console.error('Error:', error);
                    alert('Tidak dapat memuat profil.');
                }
            };

            // Fungsi untuk menyimpan perubahan profil
            const saveProfile = async (e) => {
                e.preventDefault(); // Mencegah reload halaman

                const name = profileNameInput.value;
                const password = profilePasswordInput.value;

                const dataToUpdate = { name };
                if (password) {
                    dataToUpdate.password = password;
                }

                try {
                    const response = await fetch('/api/profile', {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(dataToUpdate),
                    });
                    const result = await response.json();
                    if (!response.ok) throw new Error(result.error || 'Gagal memperbarui profil');
                    alert(result.message);
                    profilePasswordInput.value = ''; // Kosongkan field password setelah berhasil
                    loadProfile(); // Muat ulang data untuk menampilkan nama baru
                } catch (error) {
                    alert('Gagal memperbarui profil: ' + error.message);
                }
            };

            profileForm.addEventListener('submit', saveProfile);
            loadProfile();
        });