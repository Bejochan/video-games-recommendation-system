# VibePlay - Marketplace & Game Recommendation System

[![Deploy Frontend](https://img.shields.io/badge/Frontend-Vercel-black?style=for-the-badge&logo=vercel&logoColor=white)](https://vibeplay-six.vercel.app/)
[![Deploy Backend](https://img.shields.io/badge/Backend-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://vibeplay-4jk1.onrender.com/)
[![Tech Stack](https://img.shields.io/badge/Python%20%7C%20Flask%20%7C%20JS-blue?style=for-the-badge&logo=python&logoColor=white)](#)

Proyek ini adalah **Sistem Rekomendasi Video Game** berbasis web interaktif bertema **Marketplace Game (Storefront)**. Dibuat menggunakan pendekatan **Hybrid Recommendation System** (Content-Based Filtering + Playstyle DNA) untuk memenuhi tugas mata kuliah Sistem Rekomendasi (Sains Data Terapan) dengan identitas resmi **VibePlay** .

Aplikasi ini membantu calon pembeli di marketplace menemukan game yang paling cocok berdasarkan:
1. **Preferensi Genre** eksplisit.
2. **Playstyle DNA** yang didapatkan dari kuesioner psikografis interaktif.
3. **Mood Bermain** saat ini secara dinamis (*Mood-Adjusted DNA*).
4. **Marketplace Budget** (Filter Harga & Diskon).

---

## 🏷️ Filosofi Nama & Identitas "VibePlay"

Nama **VibePlay** dipilih sebagai representasi inti dari keunikan inovasi sistem rekomendasi ini:
* **"Vibe" (Mood/Perasaan):** Mewakili fitur utama *Mood-Adjusted DNA*, di mana sistem tidak hanya merekomendasikan game secara statis, melainkan dinamis mengikuti suasana hati atau *vibe* emosional pengguna saat itu secara *real-time* (seperti *Relaxed, Competitive, Immersive, Focused*).
* **"Play" (Bermain/Game):** Mewakili ranah objek domain dari sistem rekomendasi ini, yaitu video game.

Dengan demikian, **VibePlay** membawa visi akademis untuk menghadirkan pengalaman belanja di marketplace game yang sangat personal, di mana game yang ditawarkan benar-benar pas dengan *vibe* perasaan dan kapasitas finansial pengguna.

---

## 🚀 Fitur Utama & Nilai Tambah Akademik

### 1. Kuesioner Psikografis Non-Direktif (12 Pertanyaan)
Kuesioner ini dirancang secara situasional tanpa menanyakan genre secara langsung, melainkan mengevaluasi preferensi psikologis pengguna untuk memetakan koordinat DNA bermain mereka pada tiga dimensi:
* **Casual vs Hardcore** (0.0 - 1.0)
* **Simpel vs Kompleks** (0.0 - 1.0)
* **Calming vs Adrenaline** (0.0 - 1.0)

### 2. Mood-Adjusted Playstyle DNA
Pengguna dapat memilih mood bermain mereka (*Santai, Kompetitif, Imersif, Fokus*). Pilihan mood ini secara dinamis memodifikasi bobot DNA dasar pengguna sebesar 15% s/d 35% untuk mencerminkan keinginan sesaat pengguna tanpa merusak profil DNA dasar mereka.

### 3. Kontrol Bobot Multi-Aspek (Weighted Aspect Slider)
Pengguna memiliki kontrol penuh untuk mempersonalisasi perhitungan rekomendasi dengan mengatur slider bobot untuk:
* **Genre Match** (Kecocokan Genre)
* **Playstyle DNA** (Kecocokan Gaya Bermain)
* **Rating & Review** (Reputasi Game di RAWG & Metacritic)
* **Harga & Value** (Rentang Budget & Sinergi Diskon)

### 4. Dua Sesi Rekomendasi (Dual Session)
* **Sesi 1 (Balanced Match):** Rekomendasi linear murni berdasarkan bobot aspek yang disesuaikan pengguna.
* **Sesi 2 (High Rating Priority):** Rekomendasi yang memberikan bobot lebih tinggi pada game dengan reputasi luar biasa (Metacritic/Rating tinggi).

### 5. Integrasi Marketplace & Informasi Harga
Semua game disinkronisasikan menggunakan data harga Rupiah asli (`games_with_prices.csv`) hasil penarikan dari Steam Web API dan RAWG API. Menampilkan visualisasi coretan harga asli, persentase diskon hijau (gaya Steam), dan tombol tautan langsung ke halaman pembelian Steam.

---

## 🛠️ Arsitektur Teknologi & Struktur Folder

Aplikasi ini dirancang dengan arsitektur **Clean & Minimalist 2-File Frontend** didekopel dari Flask Backend:

```
Rekomendasi Game/
│
├── backend/
│   ├── data/
│   │   ├── games.csv                  # Dataset mentah awal (24.080 game, unfiltered)
│   │   └── games_with_prices.csv      # Dataset bersih hasil filter (15.784 game siap pakai)
│   │
│   ├── app.py                         # API Backend Flask & Algoritma Hybrid Recommendation
│   ├── fetch_data.py                  # Skrip crawling data RAWG + Steam API (Data Gathering)
│   ├── filter_prices.py               # Skrip preprocessing / data cleaning (Filter harga)
│   ├── config.py                      # Konfigurasi server
│   ├── .env                           # Kunci API lokal (diabaikan oleh git)
│   └── requirements.txt               # Library python backend
│
├── frontend/
│   ├── index.html                     # UI Utama (CSS Premium Glassmorphism)
│   └── app.js                         # Logika UI (Vanilla JS + Chart.js Radar Chart)
│
├── .gitignore                         # Pengaturan Git
└── README.md                          # Dokumentasi Proyek
```

---

## 💻 Cara Menjalankan Aplikasi di Lokal

### 1. Jalankan Backend Flask
Pastikan Python 3.12+ sudah terpasang. Jalankan perintah berikut di direktori proyek:
```bash
# Aktifkan virtual environment Anda
venv\Scripts\activate

# Jalankan server Flask
python backend/app.py
```
Server akan berjalan di `http://127.0.0.1:5000`.

### 2. Jalankan Frontend
Buka berkas `frontend/index.html` secara langsung di browser Anda (Klik ganda berkas tersebut atau gunakan ekstensi "Live Server" di editor Anda).

---

## 📊 Detail Algoritma Rekomendasi (Pertanggungjawaban Akademik)

Sistem rekomendasi dihitung secara hybrid menggunakan formula:

$$\text{Final Score} = (w_{\text{genre}} \times S_{\text{genre}}) + (w_{\text{dna}} \times S_{\text{dna}}) + (w_{\text{rating}} \times S_{\text{rating}}) + (w_{\text{price}} \times S_{\text{price}})$$

* **$S_{\text{genre}}$ (Genre Score):** Dihitung menggunakan persentase irisan antara list genre game dengan list genre preferensi pengguna.
* **$S_{\text{dna}}$ (DNA Score):** Dihitung berdasarkan jarak Euclidean di ruang 3D antara vektor DNA pengguna $\vec{U} = (ch_u, sc_u, ca_u)$ dan vektor DNA game $\vec{G} = (ch_g, sc_g, ca_g)$:
  $$S_{\text{dna}} = 1.0 - \frac{||\vec{G} - \vec{U}||}{\sqrt{3}}$$
* **$S_{\text{rating}}$ (Rating Score):** Normalisasi nilai gabungan RAWG Rating dan Metacritic Score (60% Metacritic + 40% RAWG).
* **$S_{\text{price}}$ (Price Score):** Bernilai $1.0$ (ditambah bonus diskon kecil) jika harga game di bawah budget pengguna. Jika melebihi budget, nilai didepresiasi secara linier hingga bernilai $0$ pada batas 2x budget.
