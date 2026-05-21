// Konfigurasi URL Backend FastAPI kamu
const API_BASE_URL = "http://127.0.0.1:8000/api";

// Elemen DOM
const genreContainer = document.getElementById("genre-container");
const btnRecommend = document.getElementById("btn-recommend");
const resultsContainer = document.getElementById("results-container");
const loadingIndicator = document.getElementById("loading");
const emptyState = document.getElementById("empty-state");

// 1. Saat halaman dimuat, ambil daftar genre dari Backend
document.addEventListener("DOMContentLoaded", async () => {
    try {
        const response = await fetch(`${API_BASE_URL}/genres`);
        const data = await response.json();
        
        // Bersihkan tulisan "Memuat..."
        genreContainer.innerHTML = ""; 
        
        // Buat checkbox untuk setiap genre
        data.genres.forEach(genre => {
            const div = document.createElement("div");
            div.className = "flex items-center";
            div.innerHTML = `
                <input type="checkbox" id="genre_${genre}" value="${genre}" class="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500 focus:ring-2">
                <label for="genre_${genre}" class="ml-2 text-sm font-medium text-gray-300 cursor-pointer hover:text-white">${genre}</label>
            `;
            genreContainer.appendChild(div);
        });
    } catch (error) {
        console.error("Gagal memuat genre:", error);
        genreContainer.innerHTML = `<p class="text-red-400 text-sm">Gagal terhubung ke server Backend. Pastikan Uvicorn menyala.</p>`;
    }
});

// 2. Logika saat tombol "Cari Rekomendasi" diklik
btnRecommend.addEventListener("click", async () => {
    // Kumpulkan genre yang dicentang
    const checkboxes = document.querySelectorAll('#genre-container input[type="checkbox"]:checked');
    const selectedGenres = Array.from(checkboxes).map(cb => cb.value);

    // Atur tampilan UI ke mode Loading
    emptyState.classList.add("hidden");
    resultsContainer.innerHTML = "";
    loadingIndicator.classList.remove("hidden");
    btnRecommend.disabled = true;
    btnRecommend.classList.add("opacity-50", "cursor-not-allowed");

    try {
        // Kirim data ke Backend (POST Request)
        const response = await fetch(`${API_BASE_URL}/recommend`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ genres: selectedGenres })
        });

        const data = await response.json();
        
        // Sembunyikan loading
        loadingIndicator.classList.add("hidden");

        // Tampilkan hasil (Generate HTML untuk setiap kartu game)
        data.recommendations.forEach(game => {
            // Tentukan warna progress bar berdasarkan skor
            let barColor = "bg-green-500";
            if (game.match_score < 70) barColor = "bg-yellow-500";
            if (game.match_score < 50) barColor = "bg-red-500";

            const card = document.createElement("div");
            // Kelas fade-in ditambahkan di baris ini
            card.className = "bg-gray-800 rounded-xl overflow-hidden shadow-lg border border-gray-700 hover:border-blue-500 transition duration-300 transform hover:-translate-y-1 fade-in";
            card.innerHTML = `
                <div class="h-48 overflow-hidden relative">
                    <img src="${game.image_url}" alt="${game.title}" class="w-full h-full object-cover">
                    <div class="absolute top-2 right-2 bg-gray-900 bg-opacity-80 px-2 py-1 rounded text-xs font-bold text-green-400 border border-green-500/50">
                        ${game.match_score}% MATCH
                    </div>
                </div>
                <div class="p-4">
                    <h3 class="font-bold text-lg leading-tight mb-3 text-gray-100 truncate" title="${game.title}">${game.title}</h3>
                    
                    <!-- Progress Bar -->
                    <div class="w-full bg-gray-700 rounded-full h-2.5 mb-1">
                        <div class="${barColor} h-2.5 rounded-full" style="width: ${game.match_score}%"></div>
                    </div>
                    <p class="text-xs text-gray-400 text-right">Skor Kecocokan ML</p>
                </div>
            `;
            resultsContainer.appendChild(card);
        });

    } catch (error) {
        console.error("Gagal memuat rekomendasi:", error);
        loadingIndicator.classList.add("hidden");
        emptyState.classList.remove("hidden");
        emptyState.innerHTML = `<h3 class="text-2xl text-red-400">Terjadi Kesalahan Server</h3><p class="text-gray-400">Pastikan Backend FastAPI menyala.</p>`;
    } finally {
        // Kembalikan tombol ke kondisi semula
        btnRecommend.disabled = false;
        btnRecommend.classList.remove("opacity-50", "cursor-not-allowed");
    }
});