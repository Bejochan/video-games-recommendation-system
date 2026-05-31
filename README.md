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

## 📊 Landasan Teoretis & Metodologi Sistem Rekomendasi (VibePlay)

Sistem rekomendasi pada **VibePlay** dibangun menggunakan fondasi ilmiah gabungan dari beberapa paradigma rekomendasi modern. Pendekatan **Hybrid Recommendation System** diterapkan untuk menutupi kelemahan masing-masing paradigma tunggal (seperti *Cold Start Problem* atau *Sparsity*) serta menghadirkan personalisasi dinamis yang adaptif.

Berikut adalah penjelasan teoretis dari pilar keilmuan rekomendasi sistem yang diimplementasikan pada proyek ini:

### 1. Hybrid Recommendation System (Sistem Rekomendasi Hibrida)
VibePlay menggunakan teknik **Weighted Hybrid Recommendation** yang menggabungkan empat kriteria keputusan berbeda secara proporsional. Secara akademis, pendekatan ini memanfaatkan konsep **Multi-Criteria Decision Making (MCDM)** untuk menghasilkan skor kecocokan tunggal terintegrasi.

Formula utama penggabungan linear terbobot adalah:

$$
\text{Final Score} = (w_{\text{genre}} \times S_{\text{genre}}) + (w_{\text{dna}} \times S_{\text{dna}}) + (w_{\text{rating}} \times S_{\text{rating}}) + (w_{\text{price}} \times S_{\text{price}})
$$

Di mana parameter bobot ditentukan secara dinamis oleh pengguna melalui *Weighted Sliders* di antarmuka dengan syarat formal:

$$
\sum_{i=1}^{n} w_i = 1.0 \quad \text{dan} \quad w_i \geq 0
$$

---

### 2. Content-Based Filtering (Penyaringan Berbasis Konten)
Metode ini merekomendasikan item yang serupa dengan preferensi eksplisit yang dinyatakan oleh pengguna. Pada VibePlay, aspek ini direpresentasikan oleh *S_genre* (Skor Genre):
* **Representasi Vektor:** Profil preferensi pengguna (*U_g*) dan karakteristik game (*G_g*) dipetakan ke dalam bentuk himpunan kategori genre.
* **Perhitungan Skor (*S_genre*):** Menggunakan nilai proporsi irisan antara genre yang disukai pengguna dengan genre yang dimiliki game:

$$
S_{\text{genre}} = \frac{|G_g \cap U_g|}{|U_g|}
$$

Hal ini memberikan nilai kecocokan linear 1.0 jika seluruh genre pilihan pengguna terkandung dalam game tersebut.

---

### 3. Psychographic Profiling & Playstyle DNA (Pemetaan Geometris 3D)
Alih-alih mengandalkan data demografis yang kaku, VibePlay mengadopsi model **Psikografis (Psychographic Profiling)** untuk memetakan perilaku dan kepribadian bermain pengguna ke dalam **Playstyle DNA**.
* **Ruang Vektor Metrik:** VibePlay memetakan pengguna (**U**) dan game (**G**) sebagai titik koordinat di dalam **Ruang Vektor Metrik 3 Dimensi** [0.0, 1.0]³ yang mewakili tiga dimensi independen gaya bermain:
  
  * Dimensi 1 (*ch*): *Casual* vs *Hardcore*
  * Dimensi 2 (*sc*): *Simple* vs *Complex*
  * Dimensi 3 (*ca*): *Calming* vs *Adrenaline*

  Koordinat lengkap didefinisikan sebagai:

$$
\vec{U} = (ch_u, sc_u, ca_u) \quad \text{and} \quad \vec{G} = (ch_g, sc_g, ca_g)
$$

* **Dynamic Mood Vector Transformation:** Sebelum pencocokan jarak dilakukan, koordinat dasar DNA pengguna (*U_base*) ditransformasikan secara dinamis menggunakan **Vektor Pengubah Mood (*M*)** yang dipilih secara *real-time*:

$$
\vec{U} = f(\vec{U}_{\text{base}}, \vec{M})
$$

* **Pengukuran Jarak (Euclidean Distance):** Kemiripan gaya bermain dihitung menggunakan **Jarak Euclidean (L₂ Norm)** antara titik koordinat pengguna dan game:

$$
d(\vec{G}, \vec{U}) = \sqrt{(ch_g - ch_u)^2 + (sc_g - sc_u)^2 + (ca_g - ca_u)^2}
$$

* **Normalisasi Jarak ke Similarity (*S_dna*):** Karena koordinat berada di dalam unit cube 3D, jarak Euclidean maksimum adalah $\sqrt{3} \approx 1.732$. Skor similarity dinormalisasi ke rentang [0, 1] sebagai berikut:

$$
S_{\text{dna}} = 1.0 - \frac{d(\vec{G}, \vec{U})}{\sqrt{3}}
$$

Metode ini memberikan landasan akademis yang sangat kuat karena memodelkan selera bermain sebagai jarak spasial geometris.

---

### 4. Constraint-Based & Value-Based Filtering (Penyaringan Berbasis Batasan & Nilai)
Pada platform marketplace, batasan finansial pengguna merupakan *Hard Constraint* (batasan mutlak). Namun, untuk menghindari hilangnya opsi game potensial yang harganya hanya sedikit di atas budget, VibePlay menerapkan **Soft Constraint dengan Penalti Depresiasi Linear**:
* **Kalkulasi Skor Harga (*S_price*):**
  * Jika harga game (*P*) lebih kecil atau sama dengan budget maksimal pengguna (*B*), game mendapatkan nilai sempurna dengan tambahan bonus proporsional diskon (*D_pct*) sebagai indikator *Value Deal*:

$$
S_{\text{price}} = \min\left(1.0, \ 0.9 + \left(\frac{D_{\text{pct}}}{100} \times 0.1\right)\right) \quad \text{jika } P \leq B
$$

  * Jika harga game (*P*) melebihi budget (*B*), skor didepresiasi secara linier terhadap budget, dan bernilai 0 jika harga mencapai 2 x B:

$$
S_{\text{price}} = \max\left(0.0, \ 1.0 - \frac{P - B}{B}\right) \quad \text{jika } P > B
$$
