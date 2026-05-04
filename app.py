from flask import Flask, render_template, request, redirect, session
import sqlite3
import requests
import html
import random

app = Flask(__name__)
app.secret_key = 'secretkey'

CATEGORIES = {
    "umum": {
        "id": 9, "name": "Pengetahuan Umum", "icon": "🌍",
        "desc": "Wawasan luas dari berbagai bidang", "color": "#00f5c4", "group": "Umum",
        "api_url": "https://opentdb.com/api.php?amount={amount}&category=9&type=multiple"
    },
    "matematika": {
        "id": 19, "name": "Matematika", "icon": "🔢",
        "desc": "Angka, logika, dan perhitungan", "color": "#7b61ff", "group": "Sains & Akademik",
        "api_url": "https://opentdb.com/api.php?amount={amount}&category=19&type=multiple"
    },
    "sains": {
        "id": 17, "name": "Ilmu Sains & Alam", "icon": "🔬",
        "desc": "Fisika, kimia, biologi & alam", "color": "#00c2ff", "group": "Sains & Akademik",
        "api_url": "https://opentdb.com/api.php?amount={amount}&category=17&type=multiple"
    },
    "ipa": {
        "id": None, "name": "IPA (Fisika, Kimia, Bio)", "icon": "⚗️",
        "desc": "Soal IPA tingkat SMP/SMA", "color": "#26de81", "group": "Sains & Akademik",
        "api_url": None
    },
    "komputer": {
        "id": 18, "name": "Komputer & IT", "icon": "💻",
        "desc": "Teknologi, coding, dan digital", "color": "#ff9f43", "group": "Teknologi",
        "api_url": "https://opentdb.com/api.php?amount={amount}&category=18&type=multiple"
    },
    "ilkomputer": {
        "id": None, "name": "Ilmu Komputer", "icon": "🖥️",
        "desc": "Algoritma, struktur data, OS", "color": "#fd9644", "group": "Teknologi",
        "api_url": None
    },
    "toefl": {
        "id": None, "name": "TOEFL / Bahasa Inggris", "icon": "🇺🇸",
        "desc": "Vocabulary, grammar, reading", "color": "#fc5c65", "group": "Bahasa",
        "api_url": None
    },
    "bahasa": {
        "id": 16, "name": "Bahasa & Sastra", "icon": "📚",
        "desc": "Tata bahasa, kata, dan sastra", "color": "#55efc4", "group": "Bahasa",
        "api_url": "https://opentdb.com/api.php?amount={amount}&category=16&type=multiple"
    },
    "sejarah": {
        "id": 23, "name": "Sejarah", "icon": "📜",
        "desc": "Peristiwa bersejarah dunia", "color": "#feca57", "group": "IPS & Sosial",
        "api_url": "https://opentdb.com/api.php?amount={amount}&category=23&type=multiple"
    },
    "geografi": {
        "id": 22, "name": "Geografi", "icon": "🗺️",
        "desc": "Negara, benua, dan peta dunia", "color": "#48dbfb", "group": "IPS & Sosial",
        "api_url": "https://opentdb.com/api.php?amount={amount}&category=22&type=multiple"
    },
    "politik": {
        "id": 24, "name": "Politik & Pemerintahan", "icon": "🏛️",
        "desc": "Sistem pemerintahan & politik", "color": "#a29bfe", "group": "IPS & Sosial",
        "api_url": "https://opentdb.com/api.php?amount={amount}&category=24&type=multiple"
    },
    "olahraga": {
        "id": 21, "name": "Olahraga", "icon": "⚽",
        "desc": "Serba-serbi dunia olahraga", "color": "#ff6b6b", "group": "Hiburan",
        "api_url": "https://opentdb.com/api.php?amount={amount}&category=21&type=multiple"
    },
    "film": {
        "id": 11, "name": "Film & Hiburan", "icon": "🎬",
        "desc": "Trivia seputar film dan TV", "color": "#fd79a8", "group": "Hiburan",
        "api_url": "https://opentdb.com/api.php?amount={amount}&category=11&type=multiple"
    },
    "musik": {
        "id": 12, "name": "Musik", "icon": "🎵",
        "desc": "Lagu, band, dan musisi dunia", "color": "#a29bfe", "group": "Hiburan",
        "api_url": "https://opentdb.com/api.php?amount={amount}&category=12&type=multiple"
    },
    "anime": {
        "id": 31, "name": "Anime & Manga", "icon": "🎌",
        "desc": "Trivia anime, manga, Jepang", "color": "#ff7675", "group": "Hiburan",
        "api_url": "https://opentdb.com/api.php?amount={amount}&category=31&type=multiple"
    },
    "videogame": {
        "id": 15, "name": "Video Game", "icon": "🎮",
        "desc": "Konsol, PC, mobile gaming", "color": "#6c5ce7", "group": "Hiburan",
        "api_url": "https://opentdb.com/api.php?amount={amount}&category=15&type=multiple"
    },
}

FALLBACK_QUESTIONS = {
    "umum": [
        {"question": "Apa ibu kota Indonesia?", "options": ["Jakarta", "Bandung", "Surabaya", "Medan"], "correct_answer": "Jakarta"},
        {"question": "Berapa jumlah provinsi di Indonesia (2024)?", "options": ["34", "36", "37", "38"], "correct_answer": "38"},
        {"question": "Gunung tertinggi di Indonesia adalah?", "options": ["Semeru", "Puncak Jaya", "Rinjani", "Kerinci"], "correct_answer": "Puncak Jaya"},
        {"question": "Siapa presiden pertama Indonesia?", "options": ["Soekarno", "Soeharto", "Habibie", "Megawati"], "correct_answer": "Soekarno"},
        {"question": "Indonesia merdeka pada tanggal?", "options": ["17 Agustus 1945", "17 Agustus 1944", "17 Agustus 1946", "18 Agustus 1945"], "correct_answer": "17 Agustus 1945"},
        {"question": "Mata uang resmi Indonesia adalah?", "options": ["Dollar", "Rupiah", "Ringgit", "Baht"], "correct_answer": "Rupiah"},
        {"question": "Planet terbesar di tata surya adalah?", "options": ["Saturnus", "Uranus", "Jupiter", "Neptunus"], "correct_answer": "Jupiter"},
        {"question": "Bahasa resmi PBB ada berapa?", "options": ["4", "5", "6", "7"], "correct_answer": "6"},
        {"question": "Siapa penemu telepon?", "options": ["Edison", "Bell", "Tesla", "Newton"], "correct_answer": "Bell"},
        {"question": "Pulau terbesar di Indonesia adalah?", "options": ["Jawa", "Kalimantan", "Sumatera", "Sulawesi"], "correct_answer": "Kalimantan"},
        {"question": "Benua terluas di dunia adalah?", "options": ["Afrika", "Amerika", "Asia", "Eropa"], "correct_answer": "Asia"},
        {"question": "Negara dengan penduduk terbanyak di dunia adalah?", "options": ["Amerika", "India", "Cina", "Indonesia"], "correct_answer": "India"},
        {"question": "Olimpiade pertama modern diadakan di kota?", "options": ["Paris", "London", "Athena", "Roma"], "correct_answer": "Athena"},
        {"question": "Berapa warna dalam pelangi?", "options": ["5", "6", "7", "8"], "correct_answer": "7"},
        {"question": "Presiden Amerika pertama adalah?", "options": ["Lincoln", "Jefferson", "Washington", "Adams"], "correct_answer": "Washington"},
        {"question": "Apa nama organisasi kesehatan dunia?", "options": ["WTO", "WHO", "UNESCO", "UNICEF"], "correct_answer": "WHO"},
        {"question": "Berapa jam dalam satu minggu?", "options": ["148", "160", "168", "172"], "correct_answer": "168"},
        {"question": "Hewan yang dikenal sebagai raja hutan?", "options": ["Harimau", "Singa", "Gajah", "Beruang"], "correct_answer": "Singa"},
        {"question": "Siapa pelukis Mona Lisa?", "options": ["Michelangelo", "Raphael", "Da Vinci", "Picasso"], "correct_answer": "Da Vinci"},
        {"question": "Negara terluas di dunia adalah?", "options": ["Kanada", "Amerika", "China", "Rusia"], "correct_answer": "Rusia"},
    ],
    "matematika": [
        {"question": "Berapakah 15 × 8?", "options": ["110", "120", "125", "130"], "correct_answer": "120"},
        {"question": "Hasil dari √144 adalah?", "options": ["10", "11", "12", "13"], "correct_answer": "12"},
        {"question": "Berapakah 25% dari 200?", "options": ["40", "50", "55", "60"], "correct_answer": "50"},
        {"question": "Jika x + 5 = 12, berapakah x?", "options": ["5", "6", "7", "8"], "correct_answer": "7"},
        {"question": "Berapakah 2³ + 3²?", "options": ["15", "16", "17", "18"], "correct_answer": "17"},
        {"question": "Berapa luas persegi dengan sisi 7 cm?", "options": ["42 cm²", "49 cm²", "56 cm²", "14 cm²"], "correct_answer": "49 cm²"},
        {"question": "Berapakah FPB dari 12 dan 18?", "options": ["3", "4", "6", "9"], "correct_answer": "6"},
        {"question": "Jika 3x = 21, maka x = ?", "options": ["6", "7", "8", "9"], "correct_answer": "7"},
        {"question": "Berapakah 1000 ÷ 25?", "options": ["35", "40", "45", "50"], "correct_answer": "40"},
        {"question": "Nilai π (pi) kira-kira?", "options": ["3.14", "3.41", "3.12", "3.21"], "correct_answer": "3.14"},
        {"question": "Keliling lingkaran jari-jari 7 (π=22/7)?", "options": ["22", "44", "14", "28"], "correct_answer": "44"},
        {"question": "Berapakah 5! (5 faktorial)?", "options": ["100", "120", "60", "25"], "correct_answer": "120"},
        {"question": "Jumlah sudut dalam segitiga adalah?", "options": ["90°", "180°", "270°", "360°"], "correct_answer": "180°"},
        {"question": "Berapakah 0.5 × 0.5?", "options": ["0.1", "0.25", "0.5", "1.0"], "correct_answer": "0.25"},
        {"question": "Akar pangkat 3 dari 27 adalah?", "options": ["2", "3", "4", "9"], "correct_answer": "3"},
        {"question": "KPK dari 4 dan 6 adalah?", "options": ["8", "12", "16", "24"], "correct_answer": "12"},
        {"question": "Volume kubus dengan sisi 3 cm?", "options": ["9 cm³", "18 cm³", "27 cm³", "81 cm³"], "correct_answer": "27 cm³"},
        {"question": "Sudut segitiga 50° dan 70°, sudut ketiga?", "options": ["50°", "60°", "70°", "80°"], "correct_answer": "60°"},
        {"question": "Berapakah 7² - 3²?", "options": ["38", "40", "42", "44"], "correct_answer": "40"},
        {"question": "Luas persegi panjang 6×4?", "options": ["10 cm²", "20 cm²", "24 cm²", "48 cm²"], "correct_answer": "24 cm²"},
    ],
    "sains": [
        {"question": "Simbol kimia untuk air?", "options": ["HO", "H2O", "H2O2", "OH"], "correct_answer": "H2O"},
        {"question": "Planet terbesar di tata surya?", "options": ["Saturnus", "Uranus", "Jupiter", "Neptunus"], "correct_answer": "Jupiter"},
        {"question": "Kecepatan cahaya sekitar berapa km/s?", "options": ["200.000", "300.000", "400.000", "500.000"], "correct_answer": "300.000"},
        {"question": "Jumlah kromosom manusia normal?", "options": ["44", "46", "48", "42"], "correct_answer": "46"},
        {"question": "Proses tumbuhan membuat makanan?", "options": ["Respirasi", "Fotosintesis", "Fertilisasi", "Transpirasi"], "correct_answer": "Fotosintesis"},
        {"question": "Simbol kimia untuk emas?", "options": ["Gd", "Go", "Au", "Ag"], "correct_answer": "Au"},
        {"question": "Jumlah tulang manusia dewasa?", "options": ["196", "206", "216", "226"], "correct_answer": "206"},
        {"question": "Gas terbanyak di atmosfer bumi?", "options": ["Oksigen", "CO2", "Nitrogen", "Argon"], "correct_answer": "Nitrogen"},
        {"question": "Satuan listrik untuk tegangan?", "options": ["Ampere", "Watt", "Ohm", "Volt"], "correct_answer": "Volt"},
        {"question": "DNA terdiri dari berapa rantai?", "options": ["1", "2", "3", "4"], "correct_answer": "2"},
        {"question": "Siapa yang menemukan teori relativitas?", "options": ["Newton", "Einstein", "Bohr", "Darwin"], "correct_answer": "Einstein"},
        {"question": "Titik didih air pada tekanan normal?", "options": ["90°C", "95°C", "100°C", "110°C"], "correct_answer": "100°C"},
        {"question": "Organ terbesar dalam tubuh manusia?", "options": ["Hati", "Paru-paru", "Kulit", "Otak"], "correct_answer": "Kulit"},
        {"question": "Planet paling dekat ke matahari?", "options": ["Venus", "Mars", "Merkurius", "Bumi"], "correct_answer": "Merkurius"},
        {"question": "Perubahan cair ke gas disebut?", "options": ["Kondensasi", "Evaporasi", "Sublimasi", "Kristalisasi"], "correct_answer": "Evaporasi"},
        {"question": "Satuan massa dalam SI?", "options": ["Gram", "Kilogram", "Pon", "Ton"], "correct_answer": "Kilogram"},
        {"question": "Bunyi tidak dapat merambat melalui?", "options": ["Udara", "Air", "Besi", "Hampa udara"], "correct_answer": "Hampa udara"},
        {"question": "Proses pembelahan sel disebut?", "options": ["Mitosis", "Meiosis", "Keduanya benar", "Fotosintesis"], "correct_answer": "Mitosis"},
        {"question": "Senyawa yang terbentuk dari ion positif dan negatif?", "options": ["Kovalen", "Ionik", "Logam", "Hidrogen"], "correct_answer": "Ionik"},
        {"question": "Bintang terdekat dari Bumi (selain Matahari)?", "options": ["Sirius", "Proxima Centauri", "Vega", "Betelgeuse"], "correct_answer": "Proxima Centauri"},
    ],
    "ipa": [
        {"question": "Hukum Newton I menyatakan benda diam tetap diam jika?", "options": ["Ada gaya luar", "Tidak ada resultan gaya", "Ada gaya gesek", "Ada momentum"], "correct_answer": "Tidak ada resultan gaya"},
        {"question": "Rumus gaya menurut Newton II adalah?", "options": ["F = m/a", "F = m × a", "F = a/m", "F = m + a"], "correct_answer": "F = m × a"},
        {"question": "Fotosintesis adalah proses?", "options": ["Bernapas", "Membuat makanan dari cahaya", "Pembelahan sel", "Pencernaan"], "correct_answer": "Membuat makanan dari cahaya"},
        {"question": "Zat mempercepat reaksi kimia tanpa ikut bereaksi?", "options": ["Inhibitor", "Reaktan", "Katalis", "Pelarut"], "correct_answer": "Katalis"},
        {"question": "Nomor atom karbon (C) adalah?", "options": ["4", "6", "8", "12"], "correct_answer": "6"},
        {"question": "Satuan tekanan dalam SI adalah?", "options": ["Newton", "Pascal", "Joule", "Watt"], "correct_answer": "Pascal"},
        {"question": "Organel sel tumbuhan yang tidak ada di sel hewan?", "options": ["Mitokondria", "Ribosom", "Kloroplas", "Nukleus"], "correct_answer": "Kloroplas"},
        {"question": "Gelombang cahaya termasuk gelombang?", "options": ["Mekanik", "Longitudinal", "Transversal", "Bunyi"], "correct_answer": "Transversal"},
        {"question": "Asam memiliki pH?", "options": ["Lebih dari 7", "Sama dengan 7", "Kurang dari 7", "Sama dengan 14"], "correct_answer": "Kurang dari 7"},
        {"question": "Pembakaran sempurna menghasilkan?", "options": ["CO dan H2", "CO2 dan H2O", "CH4 dan O2", "C dan H"], "correct_answer": "CO2 dan H2O"},
        {"question": "Fungsi hemoglobin dalam darah?", "options": ["Membunuh kuman", "Membawa oksigen", "Membekukan darah", "Menghasilkan energi"], "correct_answer": "Membawa oksigen"},
        {"question": "Energi tidak dapat diciptakan/dimusnahkan adalah hukum?", "options": ["Newton I", "Termodinamika I", "Archimedes", "Bernoulli"], "correct_answer": "Termodinamika I"},
        {"question": "Benda yang dapat ditarik magnet kuat disebut?", "options": ["Diamagnetik", "Paramagnetik", "Ferromagnetik", "Elektromagnetik"], "correct_answer": "Ferromagnetik"},
        {"question": "Tabel periodik disusun oleh?", "options": ["Einstein", "Mendeleev", "Darwin", "Lavoisier"], "correct_answer": "Mendeleev"},
        {"question": "Enzim pepsin dihasilkan oleh?", "options": ["Usus halus", "Lambung", "Mulut", "Pankreas"], "correct_answer": "Lambung"},
        {"question": "Rumus kimia garam dapur?", "options": ["KCl", "NaCl", "CaCl2", "MgCl2"], "correct_answer": "NaCl"},
        {"question": "Cahaya dibiaskan ketika?", "options": ["Mengenai cermin", "Berpindah medium", "Mengenai benda opak", "Diserap benda"], "correct_answer": "Berpindah medium"},
        {"question": "Organisme yang menguraikan sisa makhluk hidup?", "options": ["Produsen", "Konsumen", "Dekomposer", "Parasit"], "correct_answer": "Dekomposer"},
        {"question": "Daya listrik dirumuskan sebagai?", "options": ["P = V/I", "P = V × I", "P = I/R", "P = V × R"], "correct_answer": "P = V × I"},
        {"question": "Tempat pertukaran gas di paru-paru?", "options": ["Trakea", "Bronkus", "Alveolus", "Diafragma"], "correct_answer": "Alveolus"},
    ],
    "toefl": [
        {"question": "Which sentence is grammatically correct?", "options": ["She don't like it", "She doesn't likes it", "She doesn't like it", "She not like it"], "correct_answer": "She doesn't like it"},
        {"question": "Synonym of 'ABUNDANT':", "options": ["Scarce", "Plentiful", "Empty", "Rare"], "correct_answer": "Plentiful"},
        {"question": "'BENEVOLENT' means:", "options": ["Kind-hearted", "Evil", "Lazy", "Strict"], "correct_answer": "Kind-hearted"},
        {"question": "Antonym of 'ANCIENT':", "options": ["Old", "Historic", "Modern", "Classic"], "correct_answer": "Modern"},
        {"question": "She _____ to the library every day.", "options": ["go", "goes", "going", "gone"], "correct_answer": "goes"},
        {"question": "Passive voice of 'They built the house':", "options": ["The house was built by them", "The house built by them", "The house is built by them", "The house were built"], "correct_answer": "The house was built by them"},
        {"question": "Which word means 'to make something better'?", "options": ["Worsen", "Improve", "Ignore", "Decline"], "correct_answer": "Improve"},
        {"question": "I have been studying English _____ 5 years.", "options": ["since", "for", "during", "while"], "correct_answer": "for"},
        {"question": "Synonym of 'VERBOSE':", "options": ["Brief", "Silent", "Wordy", "Clear"], "correct_answer": "Wordy"},
        {"question": "If he _____ harder, he would pass the exam.", "options": ["study", "studies", "studied", "studying"], "correct_answer": "studied"},
        {"question": "TENACIOUS means:", "options": ["Weak", "Persistent", "Generous", "Curious"], "correct_answer": "Persistent"},
        {"question": "She is good _____ mathematics.", "options": ["in", "at", "on", "with"], "correct_answer": "at"},
        {"question": "Antonym of 'LOQUACIOUS':", "options": ["Talkative", "Cheerful", "Reserved", "Active"], "correct_answer": "Reserved"},
        {"question": "Present perfect tense:", "options": ["I eat lunch", "I ate lunch", "I have eaten lunch", "I was eating lunch"], "correct_answer": "I have eaten lunch"},
        {"question": "EPHEMERAL means:", "options": ["Eternal", "Short-lived", "Colorful", "Heavy"], "correct_answer": "Short-lived"},
        {"question": "She insisted _____ going alone.", "options": ["in", "at", "on", "by"], "correct_answer": "on"},
        {"question": "MITIGATE means:", "options": ["Worsen", "Lessen", "Ignore", "Celebrate"], "correct_answer": "Lessen"},
        {"question": "Neither he nor she _____ the answer.", "options": ["know", "knows", "knowing", "known"], "correct_answer": "knows"},
        {"question": "Antonym of 'LUCID':", "options": ["Clear", "Bright", "Confused", "Logical"], "correct_answer": "Confused"},
        {"question": "By the time she arrived, he _____ already left.", "options": ["has", "have", "had", "was"], "correct_answer": "had"},
        {"question": "PRAGMATIC means:", "options": ["Idealistic", "Practical", "Artistic", "Emotional"], "correct_answer": "Practical"},
        {"question": "The report _____ by the manager tomorrow.", "options": ["will write", "will be written", "is writing", "writes"], "correct_answer": "will be written"},
        {"question": "Antonym of 'FRUGAL':", "options": ["Thrifty", "Economical", "Extravagant", "Careful"], "correct_answer": "Extravagant"},
        {"question": "AMBIGUOUS means:", "options": ["Clear", "Uncertain", "Confident", "Exact"], "correct_answer": "Uncertain"},
        {"question": "They _____ the project before the deadline.", "options": ["complete", "completed", "had completed", "completing"], "correct_answer": "had completed"},
    ],
    "ilkomputer": [
        {"question": "Kepanjangan CPU?", "options": ["Central Processing Unit", "Computer Personal Unit", "Central Program Unit", "Core Processing Unit"], "correct_answer": "Central Processing Unit"},
        {"question": "Struktur data LIFO adalah?", "options": ["Queue", "Stack", "Tree", "Graph"], "correct_answer": "Stack"},
        {"question": "Pencarian paling efisien untuk data terurut?", "options": ["Linear Search", "Binary Search", "Bubble Sort", "DFS"], "correct_answer": "Binary Search"},
        {"question": "Kepanjangan RAM?", "options": ["Read Access Memory", "Random Access Memory", "Rapid Access Mode", "Read And Modify"], "correct_answer": "Random Access Memory"},
        {"question": "Sistem bilangan 0 dan 1 disebut?", "options": ["Oktal", "Desimal", "Biner", "Heksadesimal"], "correct_answer": "Biner"},
        {"question": "Variabel yang nilainya tidak dapat diubah?", "options": ["Variable", "Constant", "Array", "Pointer"], "correct_answer": "Constant"},
        {"question": "Fungsi git commit?", "options": ["Menghapus file", "Menyimpan ke repo lokal", "Mengirim ke server", "Membuat branch baru"], "correct_answer": "Menyimpan ke repo lokal"},
        {"question": "Kompleksitas waktu Binary Search?", "options": ["O(n)", "O(n²)", "O(log n)", "O(1)"], "correct_answer": "O(log n)"},
        {"question": "Kepanjangan HTML?", "options": ["HyperText Markup Language", "High Tech Modern Language", "HyperText Making Layout", "Home Tool Markup Language"], "correct_answer": "HyperText Markup Language"},
        {"question": "Struktur data FIFO adalah?", "options": ["Stack", "Queue", "Heap", "Tree"], "correct_answer": "Queue"},
        {"question": "Kernel adalah?", "options": ["Aplikasi browser", "Inti sistem operasi", "Bahasa pemrograman", "Tipe database"], "correct_answer": "Inti sistem operasi"},
        {"question": "Alamat IPv4 terdiri dari berapa bit?", "options": ["16 bit", "32 bit", "64 bit", "128 bit"], "correct_answer": "32 bit"},
        {"question": "Kepanjangan OOP?", "options": ["Object Oriented Program", "Object Oriented Programming", "Only One Process", "Open Object Protocol"], "correct_answer": "Object Oriented Programming"},
        {"question": "Bahasa pemrograman dikembangkan oleh Google?", "options": ["Swift", "Kotlin", "Go", "Rust"], "correct_answer": "Go"},
        {"question": "Sorting dengan worst case O(n²)?", "options": ["Merge Sort", "Quick Sort", "Bubble Sort", "Heap Sort"], "correct_answer": "Bubble Sort"},
        {"question": "Protokol mengamankan komunikasi web?", "options": ["HTTP", "FTP", "HTTPS", "SMTP"], "correct_answer": "HTTPS"},
        {"question": "Perintah SQL untuk mengambil data?", "options": ["INSERT", "UPDATE", "DELETE", "SELECT"], "correct_answer": "SELECT"},
        {"question": "Recursion dalam pemrograman adalah?", "options": ["Loop biasa", "Fungsi yang memanggil dirinya sendiri", "Tipe data khusus", "Algoritma sorting"], "correct_answer": "Fungsi yang memanggil dirinya sendiri"},
        {"question": "Unit terkecil dalam komputasi?", "options": ["Byte", "Nibble", "Bit", "Kilobyte"], "correct_answer": "Bit"},
        {"question": "Framework JavaScript dibuat oleh Facebook?", "options": ["Vue.js", "Angular", "React", "Svelte"], "correct_answer": "React"},
        {"question": "Apa itu deadlock dalam OS?", "options": ["Program berjalan cepat", "Dua proses saling menunggu", "Memory penuh", "CPU overhead"], "correct_answer": "Dua proses saling menunggu"},
        {"question": "DNS singkatan dari?", "options": ["Dynamic Network System", "Domain Name System", "Data Node Server", "Digital Network Service"], "correct_answer": "Domain Name System"},
        {"question": "Basis data relasional menggunakan bahasa?", "options": ["HTML", "Python", "SQL", "Java"], "correct_answer": "SQL"},
        {"question": "Stack overflow terjadi ketika?", "options": ["RAM penuh", "Rekursi tanpa base case", "CPU terlalu panas", "Network putus"], "correct_answer": "Rekursi tanpa base case"},
        {"question": "Protokol transfer email adalah?", "options": ["HTTP", "FTP", "SMTP", "SSH"], "correct_answer": "SMTP"},
    ],
}
FALLBACK_QUESTIONS["komputer"] = FALLBACK_QUESTIONS["ilkomputer"]

def get_db():
    return sqlite3.connect('database.db')

def init_db():
    db = get_db()
    db.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT
    )''')
    db.execute('''CREATE TABLE IF NOT EXISTS quiz_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER, score INTEGER, total INTEGER DEFAULT 5,
        category TEXT DEFAULT 'umum',
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    db.commit()

init_db()
for col in ["total INTEGER DEFAULT 5", "category TEXT DEFAULT 'umum'"]:
    try:
        get_db().execute(f"ALTER TABLE quiz_results ADD COLUMN {col}")
        get_db().commit()
    except: pass

@app.route('/')
def home():
    return redirect('/login')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        db = get_db()
        existing = db.execute("SELECT * FROM users WHERE username=?", (request.form['username'],)).fetchone()
        if existing:
            return render_template('register.html', error="Username sudah dipakai!")
        db.execute("INSERT INTO users (username, password) VALUES (?,?)",
                   (request.form['username'], request.form['password']))
        db.commit()
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username=? AND password=?",
                          (request.form['username'], request.form['password'])).fetchone()
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect('/dashboard')
        return render_template('login.html', error="Username atau password salah!")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    db = get_db()
    stats = db.execute("""
        SELECT COUNT(*) as total_quiz,
               COALESCE(MAX(CAST(score AS FLOAT) * 100 / total), 0) as best_pct
        FROM quiz_results WHERE user_id=?
    """, (session['user_id'],)).fetchone()
    recent = db.execute("""
        SELECT score, total, category, date FROM quiz_results
        WHERE user_id=? ORDER BY date DESC LIMIT 3
    """, (session['user_id'],)).fetchall()
    return render_template('dashboard.html', stats=stats, recent=recent, categories=CATEGORIES)

@app.route('/pilih')
def pilih():
    if 'user_id' not in session:
        return redirect('/login')
    groups = {}
    for key, cat in CATEGORIES.items():
        g = cat.get('group', 'Lainnya')
        if g not in groups:
            groups[g] = []
        groups[g].append((key, cat))
    return render_template('pilih.html', categories=CATEGORIES, groups=groups)

@app.route('/quiz')
def quiz():
    if 'user_id' not in session:
        return redirect('/login')

    cat_key = request.args.get('kategori', 'umum')
    amount  = int(request.args.get('jumlah', 5))

    if cat_key not in CATEGORIES:
        cat_key = 'umum'
    if amount not in [5, 10, 15]:
        amount = 5

    cat = CATEGORIES[cat_key]

    # ── SISTEM ANTI-REPEAT ──────────────────────────────────────────────────
    seen_key = f'seen_{cat_key}'
    seen_questions = set(session.get(seen_key, []))

    questions = []

    # Coba API (ambil 3x lipat biar bisa filter yang sudah pernah muncul)
    if cat.get('api_url'):
        api_url = cat['api_url'].format(amount=min(amount * 3, 50))
        try:
            response = requests.get(api_url, timeout=5)
            data = response.json()
            questions_raw = data.get('results', [])
            for q in questions_raw:
                question_text = html.unescape(q['question'])
                if question_text in seen_questions:
                    continue
                correct = html.unescape(q['correct_answer'])
                incorrect = [html.unescape(ans) for ans in q['incorrect_answers']]
                options = incorrect + [correct]
                random.shuffle(options)
                questions.append({"question": question_text, "options": options, "correct_answer": correct})
                if len(questions) >= amount:
                    break
        except:
            questions = []

    # Fallback lokal jika kurang
    if len(questions) < amount:
        fallback_pool = FALLBACK_QUESTIONS.get(cat_key, FALLBACK_QUESTIONS.get('umum', []))
        fresh_pool = [q for q in fallback_pool if q['question'] not in seen_questions]

        # Reset jika semua soal sudah pernah muncul
        if not fresh_pool:
            seen_questions = set()
            session[seen_key] = []
            fresh_pool = list(fallback_pool)
            random.shuffle(fresh_pool)

        needed = amount - len(questions)
        extra  = random.sample(fresh_pool, min(needed, len(fresh_pool)))
        questions.extend(extra)

    # Shuffle opsi untuk soal fallback yang belum di-shuffle
    for q in questions:
        if 'options' in q:
            random.shuffle(q['options'])

    # Tandai soal sebagai sudah dilihat
    for q in questions:
        seen_questions.add(q['question'])
    session[seen_key] = list(seen_questions)

    session['quiz_category'] = cat_key
    session['quiz_total'] = len(questions)

    return render_template('quiz.html', questions=questions, cat=cat, cat_key=cat_key)

@app.route('/submit', methods=['POST'])
def submit():
    if 'user_id' not in session:
        return redirect('/login')

    score = 0
    review = []

    for key in request.form:
        if key.startswith("question_"):
            q_num = key.split("_")[1]
            question       = request.form.get(f"text_{q_num}")
            user_answer    = request.form.get(key)
            correct_answer = request.form.get(f"correct_{q_num}")
            is_correct     = user_answer == correct_answer
            if is_correct:
                score += 1
            review.append({
                "question": question, "user_answer": user_answer,
                "correct_answer": correct_answer, "is_correct": is_correct
            })

    total   = session.get('quiz_total', len(review))
    cat_key = session.get('quiz_category', 'umum')
    cat     = CATEGORIES.get(cat_key, CATEGORIES['umum'])

    db = get_db()
    db.execute("INSERT INTO quiz_results (user_id, score, total, category) VALUES (?,?,?,?)",
               (session['user_id'], score, total, cat_key))
    db.commit()

    return render_template('result.html', score=score, total=total, review=review, cat=cat, cat_key=cat_key)

@app.route('/leaderboard')
def leaderboard():
    if 'user_id' not in session:
        return redirect('/login')
    db = get_db()
    data = db.execute("""
        SELECT users.username, quiz_results.score, quiz_results.total,
               quiz_results.category, quiz_results.date
        FROM quiz_results
        JOIN users ON users.id = quiz_results.user_id
        ORDER BY (CAST(quiz_results.score AS FLOAT) * 100 / quiz_results.total) DESC, quiz_results.date DESC
        LIMIT 20
    """).fetchall()
    return render_template('leaderboard.html', data=data, categories=CATEGORIES)

if __name__ == '__main__':
    app.run(debug=True)
