# QA Workspace — Sistem Immortal Tahu

Workspace Quality Assurance (QA) berbasis **Playwright (Chromium)** dan **Automated Discovery** untuk memverifikasi fungsionalitas, keamanan kontrol akses, responsivitas antarmuka, serta pelaporan otomatis pada platform web **Sistem Immortal Tahu**.

---

## 📌 Ringkasan Eksekusi Pengujian Terkini

Berdasarkan eksekusi automated test suite Playwright pada sistem lokal:

| Parameter | Metrik | Keterangan |
| :--- | :---: | :--- |
| **Total Test Case Terdaftar** | **21** | Terbagi dalam modul environment, publik, dan admin |
| **Test Case Passed (Lulus)** | **19** | Memenuhi seluruh assertion dan lolos verifikasi bukti |
| **Test Case Skipped (Tertunda)** | **2** | `TC019` & `TC020` (menunggu penyediaan akun uji Pembeli & Penjual) |
| **Test Case Failed (Gagal)** | **0** | Tidak ada kegagalan fungsional yang belum teratasi |
| **Tingkat Keberhasilan Eksekusi** | **100%** | Dari seluruh test case yang siap dieksekusi |
| **Status Temuan Bug** | **Terselesaikan** | Perbaikan selector & verifikasi rute selesai, tercatat di `bugs/bugs.json` |

---

## 🗂️ Struktur Direktori QA

```text
QA/
├── discovery/                     # Tahap 1: Hasil Discovery Aplikasi
│   ├── data/                      # discovery_data.json, discovery-public.json
│   ├── diagrams/                  # Diagram Mermaid (application flow, order status, user journey)
│   └── documents/                 # Dokumen Word/Excel inventaris fitur & spesifikasi QA
├── tests/                         # Tahap 2: Skrip Uji Otomasi Playwright
│   ├── 00-environment.spec.js     # Validasi ketersediaan server & HTTP status
│   ├── 01-public.spec.js          # Pengujian landing page, auth (login/reg), & guest access control
│   └── 02-admin.spec.js           # Pengujian dashboard admin, sticky sidebar, & proteksi rute internal
├── reports/                       # Dokumen Laporan Akhir Resmi
│   ├── Website_QA_Testing_Report.pdf   # Laporan lengkap hasil testing QA (PDF)
│   ├── Website_QA_Testing_Report.docx  # Laporan lengkap hasil testing QA (Word)
│   ├── Website_User_Tutorial.pdf       # Panduan pengguna sistem berbasis screenshot nyata (PDF)
│   ├── Website_User_Tutorial.docx      # Panduan pengguna sistem berbasis screenshot nyata (Word)
│   ├── Application_Discovery_Report.pdf# Dokumen arsitektur dan discovery aplikasi
│   └── Test_Case_Catalogue.xlsx        # Katalog seluruh test case beserta kriteria verifikasi
├── screenshots/                   # Bukti visual otomatis (Evidence) setiap step pengujian
├── results/                       # Hasil output runner Playwright (test-results.json, logs, html)
├── bugs/                          # Analisis dan catatan bug aplikasi (bugs.json)
├── scripts/                       # Skrip generator dokumen & otomatisasi
│   ├── build_report.py            # Generator laporan testing docx/xlsx
│   ├── build_tutorial.py          # Generator user tutorial docx
│   ├── generate_pdf_reports.js    # Konversi dokumen laporan ke PDF
│   └── clean.js                   # Pembersih direktori hasil run
├── lib/                           # Framework helper (fixtures, masking data sensitif, env loader)
├── .env                           # Konfigurasi URL dan kredensial akun uji
└── playwright.config.js           # Konfigurasi runner Playwright
```

---

## 🧪 Katalog Test Case (Traceability)

| ID | Modul / Fitur | Role Target | Tipe Uji | Objektif & Cakupan Pengujian | Status |
| :---: | :--- | :---: | :---: | :--- | :---: |
| **TC000** | Environment | Public | Environment | Memastikan server `BASE_URL` merespons status HTTP < 400 | **PASS** |
| **TC001** | Landing Page | Public | Navigation | Memastikan heading utama, branding, dan tautan masuk/daftar tampil | **PASS** |
| **TC002** | Login Form | Public | UI, Validation | Memeriksa ketersediaan form login, field required, dan link forgot password | **PASS** |
| **TC003** | Registrasi Pembeli | Public | UI, Validation | Memastikan batas minimal password (8 karakter) dan form input pembeli | **PASS** |
| **TC004** | Reset Password | Public | UI, Integration | Memeriksa ketersediaan form permohonan pemulihan kata sandi | **PASS** |
| **TC005** | Validasi Login | Public | Negative | Memastikan sistem menolak kredensial invalid dan menampilkan pesan error | **PASS** |
| **TC006** | Guest Access Control | Public | Security | Pengunjung tanpa login ditolak dari Dashboard Administrator | **PASS** |
| **TC007** | Guest Access Control | Public | Security | Pengunjung tanpa login ditolak dari Manajemen Pengguna | **PASS** |
| **TC008** | Guest Access Control | Public | Security | Pengunjung tanpa login ditolak dari Validasi Produk | **PASS** |
| **TC009** | Guest Access Control | Public | Security | Pengunjung tanpa login ditolak dari Manajemen Produk Admin | **PASS** |
| **TC010** | Guest Access Control | Public | Security | Pengunjung tanpa login ditolak dari Monitoring Pesanan Admin | **PASS** |
| **TC011** | Guest Access Control | Public | Security | Pengunjung tanpa login ditolak dari Laporan Keuangan Admin | **PASS** |
| **TC012** | Guest Access Control | Public | Security | Pengunjung tanpa login ditolak dari Pengaturan Jasa Kirim | **PASS** |
| **TC013** | Guest Access Control | Public | Security | Pengunjung tanpa login ditolak dari Pusat Bantuan Admin | **PASS** |
| **TC014** | Guest Access Control | Public | Security | Pengunjung tanpa login ditolak dari Dashboard Pembeli | **PASS** |
| **TC015** | Guest Access Control | Public | Security | Pengunjung tanpa login ditolak dari Dashboard Penjual | **PASS** |
| **TC016** | Admin Dashboard & Nav | Admin | Positive, UI | Verifikasi login Admin, sticky sidebar desktop, dan toggle navigasi mobile | **PASS** |
| **TC017** | Admin Authorization | Admin | Security | Verifikasi rute khusus Admin dan penolakan saat mencoba akses role lain | **PASS** |
| **TC018** | Admin Read-Only & Sesi | Admin | Navigation | Membuka modul baca-saja Admin dan validasi pengakhiran sesi (logout) | **PASS** |
| **TC019** | Dashboard Pembeli | Pembeli | E2E | Verifikasi fungsional dashboard pembeli (*menunggu kredensial uji*) | **SKIP** |
| **TC020** | Dashboard Penjual | Penjual | E2E | Verifikasi fungsional dashboard penjual (*menunggu kredensial uji*) | **SKIP** |

---

## 🚀 Panduan Menjalankan Pengujian

### 1. Persiapan Environment

Pastikan dependensi Node.js dan browser Chromium sudah terpasang:

```bash
cd QA
npm install
npx playwright install chromium
```

Pastikan file `QA/.env` sudah memuat URL target aplikasi lokal dan akun uji yang diperlukan:

```env
BASE_URL=http://sistem_immortal_tahu.test
ADMIN_USER=admin@immortaltahu.com
ADMIN_PASS=password_admin_anda

# Opsional untuk mengaktifkan TC019 & TC020:
BUYER_USER=buyer@immortaltahu.com
BUYER_PASS=password_buyer
SELLER_USER=seller@immortaltahu.com
SELLER_PASS=password_seller
```

### 2. Eksekusi Pengujian

*   **Validasi Kesiapan Environment:**
    ```bash
    npm run test:env
    ```

*   **Menjalankan Seluruh Test Suite (Headless):**
    ```bash
    npm test
    ```

*   **Menjalankan Test dengan Tampilan Browser (Headed Mode):**
    ```bash
    npm run test:headed
    ```

*   **Menjalankan Spesifik Modul:**
    ```bash
    npx playwright test tests/01-public.spec.js
    npx playwright test tests/02-admin.spec.js
    ```

---

## 📊 Laporan dan Bukti Pengujian

1.  **Laporan Interaktif HTML Playwright:**
    ```bash
    npm run report:html
    ```
    Membuka antarmuka laporan lengkap dengan trace visual kegagalan jika ada.

2.  **Laporan Formal DOCX & PDF:**
    *   Laporan pengujian dan panduan pengguna tersimpan di folder [`reports/`](./reports/):
        *   `reports/Website_QA_Testing_Report.docx` & `.pdf`
        *   `reports/Website_User_Tutorial.docx` & `.pdf`
        *   `reports/Test_Case_Catalogue.xlsx`
    *   Untuk menghasilkan ulang laporan setelah penambahan test case baru:
        ```bash
        python scripts/build_report.py
        python scripts/build_tutorial.py
        npm run report:pdf
        ```

3.  **Screenshot Bukti (Evidence):**
    Setiap step pengujian mengambil screenshot yang tersimpan otomatis di direktori [`screenshots/`](./screenshots/) dengan format penamaan standar:
    `TC{NOMOR}_{ROLE}_{FEATURE}_STEP{LANGKAH}_{STATUS}.png`
    *(Area data sensitif pengguna dan email telah di-masking secara otomatis demi privasi data).*

---

## 🧹 Pembersihan Hasil Run

Untuk mereset direktori hasil testing sebelum pengujian baru:

```bash
npm run clean
```
