# Simulasi Pasar saat Perang

Simulasi skenario (bukan prediksi, bukan saran investasi): bagaimana harga minyak, gas, gandum, emas, S&P 500, dan 12 mata uang bergerak selama 365 hari bila konflik di 10 titik panas meningkat. Globe 3D WebGL, model Monte Carlo, ID/EN.

## Struktur
- `index.html` — seluruh aplikasi (satu berkas, tanpa build).
- `news.json` — daftar "Berita terbaru" per titik; dibaca halaman lewat `fetch('news.json')`.
- `scripts/update_news.py` — mengambil berita dari GDELT DOC API (gratis, tanpa kunci), hanya library standar Python.
- `.github/workflows/update-news.yml` — menjalankan skrip tiap Senin dan meng-commit `news.json` bila berubah.

## Deploy
1. Push ke GitHub, aktifkan **Settings → Pages → Deploy from branch** (`main`, folder root).
2. Tab **Actions → Perbarui berita → Run workflow** untuk uji sekali secara manual.
3. Pastikan **Settings → Actions → General → Workflow permissions** = *Read and write*.

## Catatan
- Berita otomatis berupa judul asli dari sumber (bahasa Inggris) plus tautan; tidak ada ringkasan.
- Bila satu titik gagal atau kosong, entri lamanya dipertahankan. Bila semua gagal, file tidak diubah.
- Mengubah `QUERIES` di skrip akan mengubah berita yang muncul. Filter GDELT bisa membawa berita yang kurang relevan; periksa hasilnya sesekali.
