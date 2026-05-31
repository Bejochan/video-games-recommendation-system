// Auto-detect local vs production server:
const API_URL = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' || window.location.protocol === 'file:')
    ? 'http://127.0.0.1:5000'
    : 'https://vibeplay-4jk1.onrender.com';

class VibePlayApp {
    constructor() {
        this.userId = this.getOrCreateUserId();
        this.currentView = 'landing';
        
        // Quiz State
        this.currentQuestionIdx = 0;
        this.quizAnswers = {};
        this.selectedGenres = [];
        this.quizQuestions = this.getQuestions();
        
        // Recommendation Weights and Filter State
        this.mood = 'none';
        this.maxBudget = 1000000;
        this.searchBudget = 1000000;
        this.weights = {
            genre: 30,
            dna: 30,
            rating: 20,
            price: 20
        };
        
        // Recommendation API Results
        this.recommendationResults = null;
        this.userDna = { hardcore: 0.5, complex: 0.5, adrenaline: 0.5 };
        
        // Chart Instance
        this.radarChart = null;
        
        // Initialize
        this.init();
    }

    getOrCreateUserId() {
        let id = localStorage.getItem('vibeplay_user_id');
        if (!id) {
            id = 'user_' + Math.random().toString(36).substring(2, 11);
            localStorage.setItem('vibeplay_user_id', id);
        }
        return id;
    }

    init() {
        // Show landing view by default
        this.showView('landing');
        this.updateSliderLabels();
        this.startHeroCarousel();
        this.warmUpBackend();
    }

    warmUpBackend() {
        // Silently ping the backend to wake it up from sleep (Render free tier)
        fetch(`${API_URL}/`)
            .then(res => res.json())
            .then(data => console.log('Backend warmed up:', data.status))
            .catch(err => console.log('Warm up ping failed (might be waking up or offline)'));
    }

    startHeroCarousel() {
        const images = document.querySelectorAll('.carousel-image');
        if (images.length === 0) return;
        
        let currentIdx = 0;
        setInterval(() => {
            images[currentIdx].classList.remove('active');
            currentIdx = (currentIdx + 1) % images.length;
            images[currentIdx].classList.add('active');
        }, 3000);
    }

    showView(viewName) {
        this.currentView = viewName;
        document.querySelectorAll('.view-section').forEach(section => {
            section.classList.remove('active');
        });
        document.querySelectorAll('nav ul li button').forEach(btn => {
            btn.classList.remove('active');
        });

        const activeSection = document.getElementById(`${viewName}-view`);
        if (activeSection) activeSection.classList.add('active');

        const activeNav = document.getElementById(`nav-${viewName}`);
        if (activeNav) activeNav.classList.add('active');

        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });

        // Special actions on view load
        if (viewName === 'search') {
            this.performSearch();
        }
    }

    // 12 Non-Directive, Situational, and Engaging Questions
    getQuestions() {
        return [
            // WOULD YOU RATHER (2 Opsi) - Q1 s/d Q3
            {
                id: 'q1',
                type: 'wyr',
                focus: 'hardcore',
                text: 'Saat bermain game di akhir pekan, manakah sesi bermain ideal Anda?',
                options: [
                    { value: 1, text: 'Sesi singkat 15-30 menit sambil santai rebahan untuk melepas lelah.', icon: 'fa-couch' },
                    { value: 5, text: 'Sesi mendalam beberapa jam penuh konsentrasi untuk menaklukkan tantangan berat.', icon: 'fa-gamepad' }
                ]
            },
            {
                id: 'q2',
                type: 'wyr',
                focus: 'complex',
                text: 'Ketika disuguhi mekanik game baru, gaya bermain seperti apa yang Anda inginkan?',
                options: [
                    { value: 1, text: 'Mekanik instan dan intuitif yang langsung seru dimainkan dalam 2 menit.', icon: 'fa-bolt' },
                    { value: 5, text: 'Sistem berlapis dengan banyak pohon skill dan manajemen sumber daya taktis.', icon: 'fa-sitemap' }
                ]
            },
            {
                id: 'q3',
                type: 'wyr',
                focus: 'adrenaline',
                text: 'Suasana dunia game manakah yang paling Anda cari dalam petualangan?',
                options: [
                    { value: 1, text: 'Pemandangan indah nan damai yang diiringi musik akustik menenangkan.', icon: 'fa-leaf' },
                    { value: 5, text: 'Ketegangan konstan berkecepatan tinggi yang memacu adrenalin.', icon: 'fa-fire' }
                ]
            },
            // PILIHAN GANDA (4 Opsi) - Q4 s/d Q12
            {
                id: 'q4',
                type: 'mcq',
                focus: 'hardcore',
                text: 'Bagaimana reaksi spontan Anda saat karakter game Anda kalah berkali-kali di titik rintangan yang sama?',
                options: [
                    { value: 1, label: 'A', text: 'Langsung menutup game. Saya bermain untuk senang-senang, bukan untuk stres.' },
                    { value: 2, label: 'B', text: 'Mencari petunjuk di internet atau menurunkan tingkat kesulitan jika tersedia.' },
                    { value: 4, label: 'C', text: 'Istirahat sejenak, lalu mencoba kembali dengan strategi yang sedikit berbeda.' },
                    { value: 5, label: 'D', text: 'Menolak menyerah! Saya akan menganalisis pola kesalahan saya sampai berhasil melewatinya.' }
                ]
            },
            {
                id: 'q5',
                type: 'mcq',
                focus: 'complex',
                text: 'Desain antarmuka (UI) game seperti apa yang paling membuat Anda merasa nyaman?',
                options: [
                    { value: 1, label: 'A', text: 'Sangat minimalis, tanpa angka statistik atau tabel menu yang rumit.' },
                    { value: 2, label: 'B', text: 'Cukup menampilkan bar nyawa, indikator peluru, dan mini-map dasar.' },
                    { value: 4, label: 'C', text: 'Inventaris lengkap yang menampilkan status efek buff/debuff karakter saya.' },
                    { value: 5, label: 'D', text: 'Penuh informasi detail: statistik persentase atribut, pohon teknologi bercabang, dan jurnal log.' }
                ]
            },
            {
                id: 'q6',
                type: 'mcq',
                focus: 'adrenaline',
                text: 'Jenis latar suara (soundtrack) seperti apa yang ingin Anda dengar saat bermain?',
                options: [
                    { value: 1, label: 'A', text: 'Kicauan alam alami, petikan gitar akustik, atau instrumen piano ambient lembut.' },
                    { value: 2, label: 'B', text: 'Naratif suara mendalam diiringi musik latar simfoni orkestra sinematik.' },
                    { value: 4, label: 'C', text: 'Efek ledakan keras, dentuman senjata, dan musik elektro-synthwave bersemangat.' },
                    { value: 5, label: 'D', text: 'Musik distorsi gitar metal berkecepatan tinggi yang menggelegar di tengah aksi laga.' }
                ]
            },
            {
                id: 'q7',
                type: 'mcq',
                focus: 'hardcore',
                text: 'Apa arti kata "kemenangan" atau "pencapaian" yang sesungguhnya bagi Anda?',
                options: [
                    { value: 1, label: 'A', text: 'Menikmati perjalanan cerita yang indah dan menyentuh hingga selesai.' },
                    { value: 2, label: 'B', text: 'Berhasil menyelesaikan misi utama dan bersenang-senang mengumpulkan item.' },
                    { value: 4, label: 'C', text: 'Mengalahkan bos tersembunyi tersulit dan membuka semua achievement langka.' },
                    { value: 5, label: 'D', text: 'Menguasai taktik permainan tingkat tinggi dan memuncaki klasemen skor global.' }
                ]
            },
            {
                id: 'q8',
                type: 'mcq',
                focus: 'complex',
                text: 'Sebelum melakukan aksi serang atau pergerakan besar, bagaimana cara Anda mempersiapkan diri?',
                options: [
                    { value: 1, label: 'A', text: 'Tanpa rencana! Saya langsung melompat masuk dan menyerang secara spontan.' },
                    { value: 2, label: 'B', text: 'Mengikuti gaya bermain standar yang paling mudah dan umum dilakukan.' },
                    { value: 4, label: 'C', text: 'Mengkombinasikan skill aktif dan perlengkapan karakter untuk sinergi taktis terbaik.' },
                    { value: 5, label: 'D', text: 'Menghitung secara detail sinergi "build" optimal karakter saya dengan perhitungan matang.' }
                ]
            },
            {
                id: 'q9',
                type: 'mcq',
                focus: 'adrenaline',
                text: 'Bila Anda dilempar ke dunia petualangan fantasi, aktivitas santai apa yang paling menarik bagi Anda?',
                options: [
                    { value: 1, label: 'A', text: 'Memancing di danau sunyi, berkebun, atau merancang dekorasi gubuk hangat saya.' },
                    { value: 2, label: 'B', text: 'Menjelajahi bukit hijau tersembunyi dan bertegur sapa dengan penduduk lokal.' },
                    { value: 4, label: 'C', text: 'Memburu monster raksasa liar di area luar bersama rekan petualang.' },
                    { value: 5, label: 'D', text: 'Menyerbu sarang bandit dengan rentetan jebakan tak terduga dan aksi kejar-kejaran.' }
                ]
            },
            {
                id: 'q10',
                type: 'mcq',
                focus: 'adrenaline',
                text: 'Tempo atau irama pergerakan permainan (gameplay loop) mana yang paling Anda nikmati?',
                options: [
                    { value: 1, label: 'A', text: 'Sistem giliran (turn-based) di mana saya bebas merenungkan langkah tanpa batasan waktu.' },
                    { value: 2, label: 'B', text: 'Langkah bertualang santai-sedang yang memberikan cukup waktu untuk menikmati suasana.' },
                    { value: 4, label: 'C', text: 'Aksi cepat yang menuntut refleks mata dan ketepatan koordinasi jemari.' },
                    { value: 5, label: 'D', text: 'Sangat cepat dan sibuk (hectic), memaksa saya mengambil keputusan krusial dalam milidetik.' }
                ]
            },
            {
                id: 'q11',
                type: 'mcq',
                focus: 'complex',
                text: 'Bagaimana pandangan Anda mengenai game dengan porsi narasi cerita yang panjang dan padat?',
                options: [
                    { value: 1, label: 'A', text: 'Saya tidak suka teks panjang. Saya lebih suka game tanpa cerita yang langsung berfokus pada aksi.' },
                    { value: 2, label: 'B', text: 'Boleh ada dialog, asalkan singkat, padat, dan tidak mengganggu keseruan bermain.' },
                    { value: 4, label: 'C', text: 'Sangat suka narasi mendalam di mana pilihan dialog saya menentukan jalannya nasib cerita.' },
                    { value: 5, label: 'D', text: 'Sangat menyukai bacaan lore sejarah dunia fantasi yang tebal dan kompleks layaknya novel epik.' }
                ]
            },
            {
                id: 'q12',
                type: 'mcq',
                focus: 'adrenaline',
                text: 'Jika Anda dibekali satu alat utama untuk bertahan hidup dalam sebuah game aksi, apa pilihan Anda?',
                options: [
                    { value: 1, label: 'A', text: 'Tongkat sihir penyembuh luka atau jaring penangkap kupu-kupu.' },
                    { value: 2, label: 'B', text: 'Pedang pusaka warisan petualang atau tali kait untuk memanjat tebing.' },
                    { value: 4, label: 'C', text: 'Senjata otomatis futuristik berdaya hancur tinggi dengan bidik presisi.' },
                    { value: 5, label: 'D', text: 'Sepasang belati senyap berlapis racun atau peluncur roket penghancur massal.' }
                ]
            }
        ];
    }

    startQuiz() {
        this.currentQuestionIdx = 0;
        this.quizAnswers = {};
        this.selectedGenres = [];
        this.showView('quiz');
        this.renderQuestion();
    }

    renderQuestion() {
        const totalSteps = this.quizQuestions.length + 1; // +1 step untuk preferensi genre
        const stepNum = this.currentQuestionIdx + 1;
        const progressPct = Math.round(((stepNum - 1) / totalSteps) * 100);

        document.getElementById('quiz-progress-step').innerText = stepNum;
        document.getElementById('quiz-progress-percent').innerText = `${progressPct}%`;
        document.getElementById('quiz-progress-fill').style.width = `${progressPct}%`;

        // Hide/Show Back Button
        const prevBtn = document.getElementById('btn-quiz-prev');
        if (this.currentQuestionIdx > 0) {
            prevBtn.style.visibility = 'visible';
        } else {
            prevBtn.style.visibility = 'hidden';
        }

        const nextBtn = document.getElementById('btn-quiz-next');
        nextBtn.innerHTML = 'Lanjut <i class="fa-solid fa-arrow-right"></i>';

        const qBox = document.getElementById('question-box');
        qBox.innerHTML = '';

        // TAHAP 1-12: KUESIONER DNA
        if (this.currentQuestionIdx < this.quizQuestions.length) {
            const q = this.quizQuestions[this.currentQuestionIdx];
            nextBtn.disabled = this.quizAnswers[q.id] === undefined;

            const qTitle = document.createElement('h2');
            qTitle.innerText = q.text;
            qBox.appendChild(qTitle);

            if (q.type === 'wyr') {
                const wyrContainer = document.createElement('div');
                wyrContainer.className = 'option-wyr-container';

                q.options.forEach(opt => {
                    const optDiv = document.createElement('div');
                    optDiv.className = `option-wyr ${this.quizAnswers[q.id] === opt.value ? 'selected' : ''}`;
                    optDiv.onclick = () => this.selectWyrOption(q.id, opt.value, optDiv);

                    const icon = document.createElement('i');
                    icon.className = `fa-solid ${opt.icon}`;
                    
                    const textSpan = document.createElement('span');
                    textSpan.innerText = opt.text;

                    optDiv.appendChild(icon);
                    optDiv.appendChild(textSpan);
                    wyrContainer.appendChild(optDiv);
                });

                qBox.appendChild(wyrContainer);
            } else if (q.type === 'mcq') {
                const mcqContainer = document.createElement('div');
                mcqContainer.className = 'option-mcq-container';

                q.options.forEach(opt => {
                    const optDiv = document.createElement('div');
                    optDiv.className = `option-mcq ${this.quizAnswers[q.id] === opt.value ? 'selected' : ''}`;
                    optDiv.onclick = () => this.selectMcqOption(q.id, opt.value, optDiv);

                    const badge = document.createElement('div');
                    badge.className = 'option-badge';
                    badge.innerText = opt.label;

                    const textSpan = document.createElement('span');
                    textSpan.innerText = opt.text;

                    optDiv.appendChild(badge);
                    optDiv.appendChild(textSpan);
                    mcqContainer.appendChild(optDiv);
                });

                qBox.appendChild(mcqContainer);
            }
        } 
        // TAHAP AKHIR: PREFERENSI GENRE
        else {
            nextBtn.disabled = this.selectedGenres.length === 0;
            nextBtn.innerHTML = 'Kirim DNA & Dapatkan Rekomendasi <i class="fa-solid fa-paper-plane"></i>';
            
            const qTitle = document.createElement('h2');
            qTitle.innerText = 'Pilih beberapa Genre Game yang paling ingin Anda temukan saat ini di Marketplace:';
            qBox.appendChild(qTitle);

            const genres = ['Action', 'Adventure', 'RPG', 'Strategy', 'Shooter', 'Casual', 'Puzzle', 'Racing', 'Sports', 'Simulation', 'Indie'];
            const genreContainer = document.createElement('div');
            genreContainer.className = 'genre-grid';

            genres.forEach(g => {
                const gDiv = document.createElement('div');
                gDiv.className = `genre-item ${this.selectedGenres.includes(g) ? 'selected' : ''}`;
                gDiv.innerText = g;
                gDiv.onclick = () => this.toggleGenreSelection(g, gDiv);
                genreContainer.appendChild(gDiv);
            });

            qBox.appendChild(genreContainer);
        }
    }

    selectWyrOption(qId, val, element) {
        // Toggle selected styling
        document.querySelectorAll('.option-wyr').forEach(el => el.classList.remove('selected'));
        element.classList.add('selected');
        
        this.quizAnswers[qId] = val;
        document.getElementById('btn-quiz-next').disabled = false;
        
        // Auto-advance for would you rather questions
        setTimeout(() => this.nextQuestion(), 200);
    }

    selectMcqOption(qId, val, element) {
        document.querySelectorAll('.option-mcq').forEach(el => el.classList.remove('selected'));
        element.classList.add('selected');

        this.quizAnswers[qId] = val;
        document.getElementById('btn-quiz-next').disabled = false;

        // Auto-advance for multiple choice questions
        setTimeout(() => this.nextQuestion(), 200);
    }

    toggleGenreSelection(genre, element) {
        const idx = this.selectedGenres.indexOf(genre);
        if (idx > -1) {
            this.selectedGenres.splice(idx, 1);
            element.classList.remove('selected');
        } else {
            this.selectedGenres.push(genre);
            element.classList.add('selected');
        }
        
        const nextBtn = document.getElementById('btn-quiz-next');
        nextBtn.disabled = this.selectedGenres.length === 0;
    }

    nextQuestion() {
        if (this.currentQuestionIdx <= this.quizQuestions.length) {
            this.currentQuestionIdx++;
            
            if (this.currentQuestionIdx > this.quizQuestions.length) {
                // Selesai kuesioner, submit ke backend!
                this.submitQuizAnswers();
            } else {
                this.renderQuestion();
            }
        }
    }

    prevQuestion() {
        if (this.currentQuestionIdx > 0) {
            this.currentQuestionIdx--;
            this.renderQuestion();
        }
    }

    // Mengirim Kuesioner ke Backend
    async submitQuizAnswers() {
        try {
            this.showToast('Menganalisis DNA bermain Anda...');
            
            const payload = {
                user_id: this.userId,
                answers: this.quizAnswers,
                preferred_genres: this.selectedGenres
            };

            const response = await fetch(`${API_URL}/api/quiz`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const data = await response.json();
            if (data.success) {
                this.userDna = data.dna;
                this.showToast('DNA Bermain Terbentuk! Memuat Rekomendasi Marketplace...');
                
                // Pindah ke View Hasil
                this.showView('results');
                
                // Tarik rekomendasi pertama kali
                await this.fetchRecommendations();
            } else {
                alert('Gagal menganalisis kuesioner. Coba lagi.');
            }
        } catch (error) {
            console.error('Submit Quiz Error:', error);
            this.showToast('Gagal terhubung ke backend. Pastikan Flask server aktif.', true);
        }
    }

    // Mengambil Rekomendasi Game Toko
    async fetchRecommendations() {
        try {
            const payload = {
                user_id: this.userId,
                mood: this.mood,
                max_budget: this.maxBudget,
                weight_genre: this.weights.genre,
                weight_dna: this.weights.dna,
                weight_rating: this.weights.rating,
                weight_price: this.weights.price
            };

            const response = await fetch(`${API_URL}/api/recommendations`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            const data = await response.json();
            this.recommendationResults = data;
            
            // Render Radar Chart dengan DNA terbaru (Mood-adjusted)
            this.renderRadarChart(data.user_dna);

            // Render Product Cards
            this.renderProductGrid('balanced-grid', data.balanced);
            this.renderProductGrid('rating-grid', data.high_rating);
        } catch (error) {
            console.error('Fetch Recommendations Error:', error);
            this.showToast('Gagal memuat rekomendasi game.', true);
        }
    }

    // Render Product Cards
    renderProductGrid(containerId, products) {
        const container = document.getElementById(containerId);
        container.innerHTML = '';

        if (!products || products.length === 0) {
            container.innerHTML = `
                <div class="blank-state" style="grid-column: 1/-1;">
                    <i class="fa-solid fa-face-frown"></i>
                    <p>Tidak ada game yang cocok dalam range budget ini di Toko.</p>
                </div>`;
            return;
        }

        products.forEach(p => {
            const card = document.createElement('div');
            card.className = 'product-card';

            // Rupiah Formatting
            const formatRupiah = (val) => {
                if (val === 0) return 'Gratis';
                return 'Rp ' + val.toLocaleString('id-ID');
            };

            // Image placeholder fallback
            const imageUrl = p.cover_url || 'https://images.unsplash.com/photo-1542751371-adc38448a05e?q=80&w=640';
            
            // Steam URL construction
            const steamLink = p.steam_appid ? `https://store.steampowered.com/app/${p.steam_appid}` : `https://store.steampowered.com/search/?term=${encodeURIComponent(p.title)}`;

            // Price section
            let priceHtml = '';
            if (p.price_idr === 0) {
                priceHtml = `<span class="price-free">GRATIS</span>`;
            } else if (p.discount_percent > 0) {
                priceHtml = `
                    <div class="price-tag">
                        <span class="discount-pct">-${Math.round(p.discount_percent)}%</span>
                        <div class="price-details">
                            <span class="original-price">${formatRupiah(p.original_price_idr)}</span>
                            <span class="final-price">${formatRupiah(p.price_idr)}</span>
                        </div>
                    </div>`;
            } else {
                priceHtml = `
                    <div class="price-tag">
                        <div class="price-details" style="padding: 6px 12px;">
                            <span class="final-price">${formatRupiah(p.price_idr)}</span>
                        </div>
                    </div>`;
            }

            // Metacritic / Star Rating
            const ratingHtml = p.metacritic > 0 
                ? `<span><i class="fa-solid fa-star"></i> ${p.rating.toFixed(1)} <small style="color: var(--text-dark);">|</small> MC: <strong style="color: #a3d026;">${p.metacritic}</strong></span>`
                : `<span><i class="fa-solid fa-star"></i> ${p.rating.toFixed(1)}</span>`;

            card.innerHTML = `
                <div class="product-image-container">
                    <img class="product-image" src="${imageUrl}" alt="${p.title}" loading="lazy">
                    <div class="match-badge ${p.match_class}">${p.match_score}% Cocok</div>
                </div>
                <div class="product-info">
                    <div class="product-genres">${p.genres || 'Katalog Game'}</div>
                    <div class="product-title" title="${p.title}">${p.title}</div>
                    <div class="product-meta">
                        ${ratingHtml}
                        <span style="font-size: 11px;"><i class="fa-solid fa-laptop-code" style="color: var(--secondary);"></i> ${p.platforms.split(',')[0]}</span>
                    </div>
                    <div class="price-buy-section">
                        ${priceHtml}
                        <a href="${steamLink}" target="_blank" class="btn-buy">
                            <i class="fa-brands fa-steam"></i> Beli
                        </a>
                    </div>
                </div>
            `;
            container.appendChild(card);
        });
    }

    // Render Diagram Radar DNA
    renderRadarChart(dna) {
        const ctx = document.getElementById('radarChart').getContext('2d');
        
        if (this.radarChart) {
            this.radarChart.destroy();
        }

        const data = {
            labels: ['Hardcore', 'Kompleks', 'Adrenalin', 'Casual', 'Simpel', 'Santai (Calming)'],
            datasets: [{
                label: 'DNA Karakter Bermain Anda',
                data: [
                    dna.hardcore * 100,
                    dna.complex * 100,
                    dna.adrenaline * 100,
                    (1.0 - dna.hardcore) * 100,
                    (1.0 - dna.complex) * 100,
                    (1.0 - dna.adrenaline) * 100
                ],
                backgroundColor: 'rgba(99, 102, 241, 0.2)',
                borderColor: '#6366f1',
                borderWidth: 2,
                pointBackgroundColor: '#ffffff',
                pointBorderColor: '#6366f1',
                pointHoverBackgroundColor: '#6366f1',
                pointHoverBorderColor: '#fff',
                pointRadius: 4
            }]
        };

        const config = {
            type: 'radar',
            data: data,
            options: {
                scales: {
                    r: {
                        min: 0,
                        max: 100,
                        ticks: {
                            stepSize: 20,
                            display: false
                        },
                        grid: {
                            color: 'rgba(255, 255, 255, 0.08)'
                        },
                        angleLines: {
                            color: 'rgba(255, 255, 255, 0.08)'
                        },
                        pointLabels: {
                            color: '#9ca3af',
                            font: {
                                family: 'Inter',
                                size: 11,
                                weight: '500'
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                },
                responsive: true,
                maintainAspectRatio: false
            }
        };

        this.radarChart = new Chart(ctx, config);
    }

    // Dynamic controls & Sliders handling
    updateBudget(val) {
        this.maxBudget = parseFloat(val);
        const lbl = document.getElementById('lbl-budget');
        if (this.maxBudget === 1000000) {
            lbl.innerText = 'Rp 1.000.000+';
        } else {
            lbl.innerText = 'Rp ' + this.maxBudget.toLocaleString('id-ID');
        }
        
        // Debounce / Trigger refresh
        if (this.budgetTimeout) clearTimeout(this.budgetTimeout);
        this.budgetTimeout = setTimeout(() => this.fetchRecommendations(), 350);
    }

    updateSearchBudget(val) {
        this.searchBudget = parseFloat(val);
        const lbl = document.getElementById('lbl-search-budget');
        if (this.searchBudget === 1000000) {
            lbl.innerText = 'Rp 1.000.000+';
        } else {
            lbl.innerText = 'Rp ' + this.searchBudget.toLocaleString('id-ID');
        }
        
        if (this.searchBudgetTimeout) clearTimeout(this.searchBudgetTimeout);
        this.searchBudgetTimeout = setTimeout(() => this.performSearch(), 350);
    }

    updateMood(moodName) {
        this.mood = moodName;
        document.querySelectorAll('.mood-btn').forEach(btn => btn.classList.remove('active'));
        document.getElementById(`mood-${moodName}`).classList.add('active');
        this.showToast(`Mood disesuaikan: ${moodName.toUpperCase()}`);
        this.fetchRecommendations();
    }

    updateWeight(aspect, val) {
        this.weights[aspect] = parseInt(val);
        document.getElementById(`lbl-w-${aspect}`).innerText = `${val}%`;

        if (this.weightTimeout) clearTimeout(this.weightTimeout);
        this.weightTimeout = setTimeout(() => this.fetchRecommendations(), 350);
    }

    updateSliderLabels() {
        document.getElementById('lbl-w-genre').innerText = `${this.weights.genre}%`;
        document.getElementById('lbl-w-dna').innerText = `${this.weights.dna}%`;
        document.getElementById('lbl-w-rating').innerText = `${this.weights.rating}%`;
        document.getElementById('lbl-w-price').innerText = `${this.weights.price}%`;
    }

    switchSession(sessionNum) {
        document.querySelectorAll('.session-tabs button').forEach((btn, idx) => {
            if (idx + 1 === sessionNum) btn.classList.add('active');
            else btn.classList.remove('active');
        });

        if (sessionNum === 1) {
            document.getElementById('session-balanced').classList.add('active');
            document.getElementById('session-rating').classList.remove('active');
        } else {
            document.getElementById('session-balanced').classList.remove('active');
            document.getElementById('session-rating').classList.add('active');
        }
    }

    // Manual Catalog Search
    async performSearch() {
        const query = document.getElementById('txt-search-query').value;
        const genre = document.getElementById('sel-search-genre').value;
        const rating = document.getElementById('sel-search-rating').value;
        const loader = document.getElementById('search-loader');
        const grid = document.getElementById('search-grid');

        loader.style.display = 'block';
        grid.style.opacity = '0.4';

        try {
            let url = `${API_URL}/api/search?q=${encodeURIComponent(query)}&genre=${genre}&min_rating=${rating}`;
            if (this.searchBudget < 1000000) {
                url += `&max_price=${this.searchBudget}`;
            }

            const response = await fetch(url);
            const data = await response.json();
            
            // Format search results (same card structure but no match score)
            grid.innerHTML = '';
            if (!data || data.length === 0) {
                grid.innerHTML = `
                    <div class="blank-state" style="grid-column: 1/-1;">
                        <i class="fa-solid fa-face-frown-open"></i>
                        <p>Game tidak ditemukan. Coba kurangi filter pencarian Anda.</p>
                    </div>`;
            } else {
                data.forEach(p => {
                    const card = document.createElement('div');
                    card.className = 'product-card';

                    const formatRupiah = (val) => {
                        if (val === 0) return 'Gratis';
                        return 'Rp ' + val.toLocaleString('id-ID');
                    };

                    const imageUrl = p.cover_url || 'https://images.unsplash.com/photo-1542751371-adc38448a05e?q=80&w=640';
                    const steamLink = p.steam_appid ? `https://store.steampowered.com/app/${p.steam_appid}` : `https://store.steampowered.com/search/?term=${encodeURIComponent(p.title)}`;

                    let priceHtml = '';
                    if (p.price_idr === 0) {
                        priceHtml = `<span class="price-free">GRATIS</span>`;
                    } else if (p.discount_percent > 0) {
                        priceHtml = `
                            <div class="price-tag">
                                <span class="discount-pct">-${Math.round(p.discount_percent)}%</span>
                                <div class="price-details">
                                    <span class="original-price">${formatRupiah(p.original_price_idr)}</span>
                                    <span class="final-price">${formatRupiah(p.price_idr)}</span>
                                </div>
                            </div>`;
                    } else {
                        priceHtml = `
                            <div class="price-tag">
                                <div class="price-details" style="padding: 6px 12px;">
                                    <span class="final-price">${formatRupiah(p.price_idr)}</span>
                                </div>
                            </div>`;
                    }

                    const ratingHtml = p.metacritic > 0 
                        ? `<span><i class="fa-solid fa-star"></i> ${p.rating.toFixed(1)} <small style="color: var(--text-dark);">|</small> MC: <strong style="color: #a3d026;">${p.metacritic}</strong></span>`
                        : `<span><i class="fa-solid fa-star"></i> ${p.rating.toFixed(1)}</span>`;

                    card.innerHTML = `
                        <div class="product-image-container">
                            <img class="product-image" src="${imageUrl}" alt="${p.title}" loading="lazy">
                        </div>
                        <div class="product-info">
                            <div class="product-genres">${p.genres || 'Katalog Game'}</div>
                            <div class="product-title" title="${p.title}">${p.title}</div>
                            <div class="product-meta">
                                ${ratingHtml}
                                <span style="font-size: 11px;"><i class="fa-solid fa-laptop-code" style="color: var(--secondary);"></i> ${p.platforms.split(',')[0]}</span>
                            </div>
                            <div class="price-buy-section">
                                ${priceHtml}
                                <a href="${steamLink}" target="_blank" class="btn-buy">
                                    <i class="fa-brands fa-steam"></i> Beli
                                </a>
                            </div>
                        </div>
                    `;
                    grid.appendChild(card);
                });
            }
        } catch (error) {
            console.error('Catalog Search Error:', error);
            this.showToast('Gagal memuat katalog toko.', true);
        } finally {
            loader.style.display = 'none';
            grid.style.opacity = '1';
        }
    }

    // Success and Alert Toast Popup
    showToast(message, isError = false) {
        const toast = document.getElementById('toast');
        const icon = toast.querySelector('i');
        
        if (isError) {
            toast.style.background = '#7f1d1d';
            toast.style.borderColor = '#ef4444';
            icon.className = 'fa-solid fa-circle-exclamation';
            icon.style.color = '#ef4444';
        } else {
            toast.style.background = '#1e1b4b';
            toast.style.borderColor = '#6366f1';
            icon.className = 'fa-solid fa-circle-check';
            icon.style.color = '#6366f1';
        }

        document.getElementById('toast-message').innerText = message;
        toast.classList.add('show');

        if (this.toastTimeout) clearTimeout(this.toastTimeout);
        this.toastTimeout = setTimeout(() => {
            toast.classList.remove('show');
        }, 3000);
    }
}

// Instantiate App
let app;
window.addEventListener('DOMContentLoaded', () => {
    app = new VibePlayApp();
});
