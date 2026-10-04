# 🦉 Tangkap Jawaban!

Game edukasi web untuk anak (± 4 tahun). Anak menunjuk jawaban yang jatuh memakai **jari telunjuk** di depan webcam. Tangan dideteksi dengan **MediaPipe Hand Landmarker**, dan semuanya berjalan di browser.

## Cara main
1. Buka halaman game, lalu klik **▶ Mulai Main!** dan izinkan kamera.
2. Soal dibacakan. Tiga kotak jawaban (A, B, C) turun pelan memakai parasut.
3. Arahkan ujung jari telunjuk ke kotak jawaban dan **tahan ±1 detik** sampai kotaknya terisi hijau.
4. Setelah semua soal selesai, muncul skor akhir dan tabel rekap.

Tanpa kamera pun bisa dimainkan: pilih **"Main pakai mouse / sentuh"**.

## 5 jenis permainan (100 soal bawaan, masing-masing 20 soal)
| Jenis | Contoh |
|---|---|
| 🔣 Enkoding Substitusi | 🍎➡️⭐ 🍌➡️🔵, lalu 🍎➡️❓ |
| 🎨 Enkoding Kombinasi | 🍎 ➕ ⚪ → mana lingkaran merah? |
| 🔢 Enumerasi Piktografik | 🐱 🐱 🐱 → ada berapa? |
| 🔐 Substitusi Kode | 1️⃣🐱 2️⃣🐶 3️⃣🐰, lalu 2️⃣➡️❓ |
| 🔁 Reproduksi Pola Sekuensial | 🔴🔵🔴🔵🔴❓ |

## Menambah soal sendiri (import Excel)
1. Unduh [`template_soal.xlsx`](template_soal.xlsx). Tombol **📄 Template Excel** di menu juga mengunduh file yang sama.
2. Isi sheet **Soal** dengan kolom: `No, Kategori, Soal, Gambar, Pilihan_A, Pilihan_B, Pilihan_C, Kunci`.
   - Isi **Soal** dengan kata-kata, karena teks ini dibacakan.
   - **Gambar** berisi emoji. Pakai `|` untuk ganti baris.
   - **Kunci** diisi `A`, `B`, atau `C`.
3. Di menu game, pilih *Tambahkan* atau *Ganti semua*, lalu klik **📥 Import Soal**. File `.csv` UTF-8 juga diterima.

Soal hasil import disimpan di browser (localStorage) perangkat itu saja.

## Teknologi
- Satu file `index.html` berisi HTML, CSS, dan vanilla JavaScript (ES module).
- Hand tracking memakai [MediaPipe Tasks Vision](https://www.npmjs.com/package/@mediapipe/tasks-vision) `1.0.1` dari CDN jsDelivr. Kursor diambil dari landmark `INDEX_FINGER_TIP` (8).
- Canvas 2D untuk soal, kotak jawaban, dan kursor.
- Web Speech API untuk membacakan soal, dan WebAudio untuk efek suara.
- [SheetJS](https://sheetjs.com/) untuk import soal dan unduh rekap Excel.

## Menjalankan secara lokal
Kamera hanya bisa dipakai di `https://` atau `localhost`:
```bash
python -m http.server 8000
# buka http://localhost:8000
```

## Membuat ulang soal bawaan
`python tools/generate_soal.py` (perlu `openpyxl`) akan menulis ulang array `SOAL_BAWAAN` di `index.html` dan file `template_soal.xlsx`.
