"""
QA Discovery Documentation Generator
Aplikasi: Immortal Tahu (E-Tofu Immortal)
Dibuat berdasarkan skill: application-discovery-qa-documentation
"""

import json
import os
from datetime import date
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

BASE = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE, "documents")
DATA_DIR = os.path.join(BASE, "data")
os.makedirs(DOCS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

TODAY = date.today().strftime("%d %B %Y")
APP_NAME = "Immortal Tahu"
VERSION = "1.0"
SOURCE_STATUS = "Documented from source; not runtime verified"

# ─────────────────────────────────────────────
# SHARED HELPERS
# ─────────────────────────────────────────────

def set_cell_bg(cell, hex_color):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tcPr.append(shd)

def add_page_number(doc):
    section = doc.sections[0]
    footer = section.footer
    para = footer.paragraphs[0]
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = para.add_run("Halaman ")
    fldChar1 = OxmlElement("w:fldChar")
    fldChar1.set(qn("w:fldCharType"), "begin")
    instrText = OxmlElement("w:instrText")
    instrText.text = "PAGE"
    fldChar2 = OxmlElement("w:fldChar")
    fldChar2.set(qn("w:fldCharType"), "end")
    run._r.append(fldChar1)
    run._r.append(instrText)
    run._r.append(fldChar2)
    para.add_run(f" — {APP_NAME} QA Discovery {TODAY}")

def apply_doc_style(doc, title_text, subtitle_text):
    """Apply consistent document styles and cover."""
    # Margins
    for section in doc.sections:
        section.top_margin = Cm(2.5)
        section.bottom_margin = Cm(2.5)
        section.left_margin = Cm(3)
        section.right_margin = Cm(2.5)
    # Normal style
    normal = doc.styles["Normal"]
    normal.font.name = "Calibri"
    normal.font.size = Pt(11)
    # Heading 1
    h1 = doc.styles["Heading 1"]
    h1.font.name = "Calibri"
    h1.font.size = Pt(16)
    h1.font.bold = True
    h1.font.color.rgb = RGBColor(0x1F, 0x49, 0x7D)
    # Heading 2
    h2 = doc.styles["Heading 2"]
    h2.font.name = "Calibri"
    h2.font.size = Pt(13)
    h2.font.bold = True
    h2.font.color.rgb = RGBColor(0x2E, 0x74, 0xB5)
    # Heading 3
    h3 = doc.styles["Heading 3"]
    h3.font.name = "Calibri"
    h3.font.size = Pt(11)
    h3.font.bold = True
    h3.font.color.rgb = RGBColor(0x2E, 0x74, 0xB5)
    # Cover page
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(APP_NAME.upper())
    run.bold = True
    run.font.size = Pt(26)
    run.font.color.rgb = RGBColor(0x1F, 0x49, 0x7D)
    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = p2.add_run(title_text)
    r2.font.size = Pt(18)
    r2.bold = True
    p3 = doc.add_paragraph()
    p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r3 = p3.add_run(subtitle_text)
    r3.font.size = Pt(12)
    r3.italic = True
    p4 = doc.add_paragraph()
    p4.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r4 = p4.add_run(f"Tanggal: {TODAY}  |  Versi: {VERSION}")
    r4.font.size = Pt(10)
    doc.add_page_break()
    add_page_number(doc)

def tbl_header_row(table, headers, bg="1F497D"):
    row = table.rows[0]
    for i, h in enumerate(headers):
        cell = row.cells[i]
        cell.text = h
        cell.paragraphs[0].runs[0].bold = True
        cell.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        cell.paragraphs[0].runs[0].font.size = Pt(10)
        set_cell_bg(cell, bg)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER

def add_tbl_row(table, values, font_size=10):
    row = table.add_row()
    for i, v in enumerate(values):
        cell = row.cells[i]
        cell.text = str(v)
        cell.paragraphs[0].runs[0].font.size = Pt(font_size)
    return row


def load_public_discovery():
    path = os.path.join(DATA_DIR, "discovery-public.json")
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as file:
        return json.load(file)


# ─────────────────────────────────────────────
# DATA DEFINITIONS
# ─────────────────────────────────────────────

PAGES = [
    # (page_id, name, url, module, roles, purpose, main_components, available_actions, status)
    ("P00", "Landing Page / Login Redirect", "/", "Autentikasi", "Publik", "Halaman utama: tampilkan landing page untuk publik, redirect dashboard untuk user terlogin", "Konten landing, tombol Login", "Login, Register", "Observed"),
    ("P01", "Login", "/login", "Autentikasi", "Publik (guest)", "Autentikasi pengguna dengan email dan password", "Form email & password, checkbox remember me, link lupa password", "Submit login, Navigasi ke Register, Navigasi ke Forgot Password", "Observed"),
    ("P02", "Register", "/register", "Autentikasi", "Publik (guest)", "Pendaftaran akun baru sebagai Pembeli", "Form nama, email, password, konfirmasi password", "Submit register (otomatis role Pembeli)", "Observed"),
    ("P03", "Forgot Password", "/forgot-password", "Autentikasi", "Publik (guest)", "Permintaan tautan reset kata sandi via email", "Form email", "Submit email", "Observed"),
    ("P04", "Reset Password", "/reset-password/{token}", "Autentikasi", "Publik (via link email)", "Form baru kata sandi dengan token validasi", "Form password baru, konfirmasi password", "Submit reset password", "Observed"),
    ("P05", "Dashboard Pembeli", "/dashboard/pembeli", "Dashboard", "Pembeli", "Halaman utama pembeli: ringkasan dan navigasi fitur", "Statistik pesanan, link navigasi cepat", "Navigasi ke fitur pembeli", "Observed"),
    ("P06", "Katalog Produk", "/pembeli/produk", "Belanja", "Pembeli", "Melihat seluruh produk yang disetujui dan aktif, filter kategori", "Grid/list produk, filter Matang/Mentah, tombol tambah ke keranjang, badge stok", "Filter kategori, Tambah ke keranjang, Lihat detail produk", "Observed"),
    ("P07", "Keranjang Belanja", "/pembeli/keranjang", "Belanja", "Pembeli", "Kelola item keranjang sebelum checkout", "Tabel item (nama, qty, harga, subtotal), tombol ubah qty, hapus, total, tombol checkout", "Ubah jumlah item, Hapus item, Lanjut ke checkout", "Observed"),
    ("P08", "Checkout", "/pembeli/checkout", "Belanja", "Pembeli", "Proses pembuatan pesanan: pilih alamat, kurir, metode bayar", "Form alamat, dropdown kurir (dengan kalkulasi ongkir), dropdown metode bayar, ringkasan pesanan, tombol pesan", "Pilih kurir, Pilih metode bayar, Submit pesanan", "Observed"),
    ("P09", "Daftar Pesanan Pembeli", "/pembeli/pesanan", "Pesanan", "Pembeli", "Melihat semua pesanan milik pembeli dengan status terkini", "Tabel pesanan (ID, tanggal, status, total), filter status, tombol aksi per pesanan", "Upload bukti bayar, Konfirmasi barang diterima, Lihat bukti pembayaran", "Observed"),
    ("P10", "Pusat Bantuan Pembeli", "/pembeli/bantuan", "Customer Service", "Pembeli", "Tiket bantuan: buka percakapan baru atau lanjutkan dengan admin", "Percakapan CS, form kirim pesan, status open/closed", "Kirim pesan ke admin, Lihat balasan admin", "Observed"),
    ("P11", "Chat Pesanan Pembeli", "/pembeli/chat", "Komunikasi", "Pembeli", "Chat dengan penjual terkait pesanan", "Daftar pesanan yang bisa di-chat, kotak pesan, badge unread", "Kirim pesan, Lihat riwayat pesan", "Observed"),
    ("P12", "Profil Pengguna", "/profile", "Profil", "Semua (login)", "Edit data diri: nama, alamat, telepon, foto profil", "Form nama, email (readonly), telepon, alamat, upload foto", "Update profil", "Observed"),
    ("P13", "Dashboard Penjual", "/dashboard/penjual", "Dashboard", "Penjual", "Halaman utama penjual: ringkasan pesanan, stok, dan navigasi", "Statistik pesanan, ringkasan stok, navigasi cepat, badge pesanan baru", "Navigasi ke fitur penjual", "Observed"),
    ("P14", "Daftar Produk Penjual", "/penjual/produk", "Produk", "Penjual", "Kelola semua produk milik penjual: lihat, tambah, edit, stok", "Tabel produk (nama, kategori, harga, stok, status approval), form tambah produk, form edit, form stok", "Tambah produk, Edit produk, Kelola stok (mutasi masuk/keluar/sesuaikan)", "Observed"),
    ("P15", "Daftar Pesanan Penjual", "/penjual/pesanan", "Pesanan", "Penjual", "Proses pesanan dari pembeli: verifikasi bayar, kirim barang", "Tabel pesanan (ID, pembeli, produk, status, metode bayar), tombol aksi per status", "Verifikasi pembayaran (lunas/gagal), Input resi & bukti kirim, Advance status", "Observed"),
    ("P16", "Transaksi Penjual", "/penjual/transaksi", "Keuangan", "Penjual", "Lihat semua transaksi dan ekspor laporan", "Tabel transaksi (ID, pesanan, total, metode, status, tanggal), filter, tombol ekspor", "Filter transaksi, Ekspor Excel, Ekspor PDF", "Observed"),
    ("P17", "Metode Pembayaran Penjual", "/penjual/metode-pembayaran", "Pengaturan", "Penjual", "Kelola metode pembayaran yang ditampilkan ke pembeli saat checkout", "Tabel metode bayar (nama, kode, nomor, pemilik rekening, status), form tambah, form edit", "Tambah metode bayar, Edit metode bayar, Aktif/nonaktif metode bayar, Hapus metode bayar", "Observed"),
    ("P18", "Pusat Bantuan Penjual", "/penjual/bantuan", "Customer Service", "Penjual", "Tiket bantuan penjual ke admin", "Percakapan CS, form kirim pesan, status open/closed", "Kirim pesan ke admin, Lihat balasan admin", "Observed"),
    ("P19", "Chat Pesanan Penjual", "/penjual/chat", "Komunikasi", "Penjual", "Chat dengan pembeli terkait pesanan", "Daftar pesanan yang bisa di-chat, kotak pesan, badge unread", "Kirim pesan, Lihat riwayat pesan", "Observed"),
    ("P20", "Dashboard Admin", "/dashboard/admin", "Dashboard", "Admin", "Ringkasan seluruh sistem: pengguna, produk, pesanan, transaksi, CS", "Kartu statistik (jumlah pengguna, produk, pesanan, dsb.), navigasi ke semua modul admin", "Navigasi ke semua modul admin", "Observed"),
    ("P21", "Manajemen Pengguna", "/admin/pengguna", "Pengguna", "Admin", "Kelola akun pengguna: lihat, ubah role, aktif/nonaktif, kirim link reset", "Tabel pengguna (nama, email, role, status, tanggal daftar), dropdown role, toggle status, tombol reset password", "Ubah role pengguna, Aktifkan/nonaktifkan akun, Kirim link reset password", "Observed"),
    ("P22", "Validasi Produk", "/admin/validasi-produk", "Produk", "Admin", "Review pengajuan produk baru dari penjual: approve/reject", "Tabel produk pending (nama, penjual, kategori, harga), form catatan admin, tombol setujui/tolak", "Setujui produk, Tolak produk dengan catatan", "Observed"),
    ("P23", "Manajemen Produk Admin", "/admin/produk", "Produk", "Admin", "Lihat semua produk, aktif/nonaktif, ubah harga", "Tabel semua produk (nama, penjual, kategori, harga, status approval, is_active), toggle aktif, form ubah harga", "Aktifkan/nonaktifkan produk, Ubah harga produk", "Observed"),
    ("P24", "Pesanan Admin", "/admin/pesanan", "Pesanan", "Admin", "Monitor semua pesanan, proses pengembalian dana", "Tabel semua pesanan (ID, pembeli, penjual, status, total, metode bayar), form refund", "Lihat detail pesanan, Proses refund", "Observed"),
    ("P25", "Laporan Keuangan", "/admin/keuangan", "Keuangan", "Admin", "Laporan keuangan dengan filter dan ekspor", "Ringkasan total transaksi, tabel transaksi, filter tanggal/status, tombol ekspor", "Filter laporan, Ekspor Excel, Ekspor PDF", "Observed"),
    ("P26", "Jasa Kirim", "/admin/jasa-kirim", "Pengaturan", "Admin", "Kelola daftar jasa pengiriman yang tersedia", "Tabel jasa kirim (nama, kode, tarif/kg, is_active), form tambah, form edit", "Tambah jasa kirim, Edit jasa kirim", "Observed"),
    ("P27", "Pusat Bantuan Admin", "/admin/pusat-bantuan", "Customer Service", "Admin", "Kelola semua tiket bantuan dari penjual dan pembeli", "Tabel percakapan CS (pengguna, role, status, pesan terakhir, badge unread), panel balas, tombol buka/tutup tiket", "Lihat percakapan, Balas pesan, Tutup percakapan, Buka kembali percakapan", "Observed"),
    ("P28", "Pengarah Dashboard Berdasarkan Role", "/dashboard", "Navigasi", "Semua (login)", "Meneruskan pengguna terautentikasi ke dashboard sesuai role", "Tidak ada komponen halaman; respons redirect", "Redirect ke dashboard Pembeli, Penjual, atau Admin", "Documented"),
]

FEATURES = [
    # (feat_id, name, module, page_ref, actor, trigger, input, process, output, validation, priority, status)
    ("F01", "Login", "Autentikasi", "P01", "Publik (guest)", "Submit form login", "Email, Password, Remember Me", "Validasi credential + is_active, Auth::attempt, session regenerate, redirect ke dashboard sesuai role", "Redirect ke dashboard role-specific atau pesan error", "Email required, Password required, is_active harus true", "Critical", "Verified"),
    ("F02", "Register Akun Pembeli", "Autentikasi", "P02", "Publik (guest)", "Submit form register", "Nama, Email, Password, Konfirmasi Password", "Validasi unique email, buat User dengan role=pembeli, login otomatis, redirect dashboard pembeli", "Akun baru, session aktif, redirect dashboard pembeli", "Nama max 255, Email unique, Password min 8, confirmed", "High", "Verified"),
    ("F03", "Logout", "Autentikasi", "P01", "Semua (login)", "Klik tombol logout", "-", "Auth::logout, session invalidate, token regenerate", "Redirect ke halaman login", "-", "High", "Verified"),
    ("F04", "Forgot Password", "Autentikasi", "P03", "Publik (guest)", "Submit email", "Email", "Kirim link reset ke email (via mailer log di local)", "Flash message konfirmasi pengiriman", "Email required, email harus ada di DB", "Medium", "Observed"),
    ("F05", "Reset Password", "Autentikasi", "P04", "Publik (via link)", "Submit form reset", "Token (dari URL), Password baru, Konfirmasi", "Validasi token, update password user", "Password diupdate, redirect login", "Password min 8, confirmed, token valid", "Medium", "Observed"),
    ("F06", "Edit Profil", "Profil", "P12", "Semua (login)", "Submit form profil", "Nama, Telepon, Alamat, Foto (opsional)", "Update data user, simpan foto ke storage", "Data profil diperbarui", "Nama required, Foto max 5MB jpg/jpeg/png/webp", "Medium", "Observed"),
    ("F07", "Lihat Katalog Produk", "Belanja", "P06", "Pembeli", "Akses halaman produk", "Filter kategori (Matang/Mentah)", "Query produk status=disetujui & is_active=true milik penjual", "Grid produk dengan info harga, stok, kategori", "-", "High", "Observed"),
    ("F08", "Tambah ke Keranjang", "Belanja", "P06", "Pembeli", "Klik tombol tambah ke keranjang", "Produk ID, Jumlah, Kategori", "Validasi stok, cek produk aktif & disetujui, buat/update BuyerCartItem dalam transaksi DB", "Item ditambahkan ke keranjang, flash message", "Jumlah min 1 max 1000, jumlah + existing <= stok, produk harus disetujui & aktif", "High", "Verified"),
    ("F09", "Ubah Jumlah Keranjang", "Belanja", "P07", "Pembeli", "Submit form ubah qty di keranjang", "Line key (produk_id-kategori), Jumlah baru", "Validasi stok baru, update BuyerCartItem", "Jumlah diperbarui, total berubah", "Jumlah min 1 max 1000, tidak melebihi stok, produk masih aktif", "Medium", "Verified"),
    ("F10", "Hapus Item Keranjang", "Belanja", "P07", "Pembeli", "Klik hapus item", "Line key", "Delete BuyerCartItem", "Item dihapus dari keranjang", "-", "Medium", "Verified"),
    ("F11", "Checkout & Buat Pesanan", "Belanja", "P08", "Pembeli", "Submit form checkout", "Alamat pengiriman, Kurir, Metode bayar", "Validasi stok (lock), hitung ongkir (ShippingCalculator), buat Pesanan + DetailPesanan + Transaksi + MutasiStok dalam transaksi DB atomik, hapus item keranjang", "Pesanan baru dibuat, redirect ke daftar pesanan", "Semua item harus tersedia, stok cukup, kurir aktif, metode bayar valid, satu toko per pesanan", "Critical", "Verified"),
    ("F12", "Upload Bukti Pembayaran", "Pesanan", "P09", "Pembeli", "Submit form upload", "Pesanan ID, File foto bukti", "Simpan bukti ke storage, update transaksi.bukti_pembayaran", "Bukti tersimpan, penjual dapat verifikasi", "File required, image jpg/jpeg/png/webp max 5MB", "High", "Observed"),
    ("F13", "Konfirmasi Barang Diterima", "Pesanan", "P09", "Pembeli", "Klik tombol konfirmasi", "Pesanan ID", "Validasi status=dikirim & pembayaran lunas, update status=selesai, update tanggal_selesai, untuk COD update transaksi=lunas", "Status pesanan menjadi selesai", "Status pesanan harus dikirim, pembayaran valid", "High", "Verified"),
    ("F14", "Lihat Bukti Pembayaran", "Pesanan", "P09", "Pembeli, Penjual", "Klik link lihat bukti", "Pesanan ID", "Show/download file bukti dari storage", "Tampilkan/unduh file bukti pembayaran", "-", "Medium", "Observed"),
    ("F15", "Chat Pesanan (Pembeli↔Penjual)", "Komunikasi", "P11,P19", "Pembeli, Penjual", "Kirim pesan di chat pesanan", "Pesanan ID, Isi pesan", "Buat OrderMessage, throttle 10/menit", "Pesan terkirim, badge unread diperbarui", "Pesan tidak boleh kosong, max (tbd), throttle 10/menit", "Medium", "Observed"),
    ("F16", "Pusat Bantuan (Buka/Kirim Pesan)", "Customer Service", "P10,P18", "Pembeli, Penjual", "Kirim pesan di CS", "Isi pesan", "Buat/update CustomerServiceConversation + Message, throttle 10/menit", "Pesan terkirim ke admin, status percakapan open", "Throttle 10/menit", "Medium", "Observed"),
    ("F17", "Tambah Produk Baru (Penjual)", "Produk", "P14", "Penjual", "Submit form tambah produk", "Nama, Kategori (matang/mentah), Harga, Stok Awal, Deskripsi, Gambar", "Buat Produk (status=menunggu), buat Stok, buat MutasiStok jika stok_awal>0", "Produk baru dengan status menunggu validasi", "Semua field required, Harga min 1 max 100jt, Stok max 100rb, Gambar max 5MB", "High", "Verified"),
    ("F18", "Edit Produk (Penjual)", "Produk", "P14", "Penjual", "Submit form edit produk", "Nama, Kategori, Harga, Deskripsi, Gambar (opsional)", "Update Produk, catat RiwayatHarga jika harga berubah, jika status=ditolak → resubmit ke menunggu", "Produk diperbarui, riwayat harga tercatat", "Hanya produk milik penjual, validasi sama dengan tambah produk", "High", "Verified"),
    ("F19", "Kelola Stok — Mutasi (Penjual)", "Produk", "P14", "Penjual", "Submit form mutasi stok", "Produk ID, Kategori, Jenis (masuk/keluar), Jumlah, Catatan", "Validasi keluar ≤ stok, update Stok, buat MutasiStok", "Stok diperbarui, mutasi tercatat", "Keluar tidak boleh > stok, Jumlah min 1 max 100rb", "High", "Verified"),
    ("F20", "Kelola Stok — Sesuaikan (Penjual)", "Produk", "P14", "Penjual", "Submit form sesuaikan stok", "Produk ID, Kategori, Jumlah baru", "Hitung selisih, update Stok, buat MutasiStok otomatis masuk/keluar", "Stok disesuaikan, mutasi tercatat", "Jumlah min 0 max 100rb", "Medium", "Verified"),
    ("F21", "Verifikasi Pembayaran (Penjual)", "Pesanan", "P15", "Penjual", "Submit form verifikasi", "Pesanan ID, Status pembayaran (lunas/gagal), Catatan", "Validasi status pesanan=menunggu & bukti ada & bukan COD, update Transaksi + status pesanan jika lunas", "Pembayaran dikonfirmasi/ditolak, pesanan diproses jika lunas", "Status pesanan harus menunggu, bukan COD, bukti ada", "Critical", "Verified"),
    ("F22", "Input Resi & Kirim Pesanan (Penjual)", "Pesanan", "P15", "Penjual", "Submit form kirim", "Pesanan ID, Nomor Resi, Foto Bukti Pengiriman", "Validasi status=diproses & pembayaran lunas/cod, simpan foto, update status=dikirim + resi", "Status pesanan menjadi dikirim, resi dan bukti tersimpan", "Status harus diproses, pembayaran valid, resi required, foto max 5MB", "Critical", "Verified"),
    ("F23", "Advance Status COD (Penjual)", "Pesanan", "P15", "Penjual", "Klik tombol lanjutkan", "Pesanan ID", "Validasi COD: status=menunggu → diproses langsung tanpa verifikasi bayar", "Status pesanan menjadi diproses", "Hanya untuk COD atau jika sudah diverifikasi", "High", "Verified"),
    ("F24", "Lihat & Ekspor Transaksi (Penjual)", "Keuangan", "P16", "Penjual", "Lihat tabel / klik ekspor", "Filter (opsional)", "Query transaksi milik produk penjual, generate Excel/PDF", "Tabel transaksi, file unduhan", "-", "Medium", "Observed"),
    ("F25", "Kelola Metode Pembayaran (Penjual)", "Pengaturan", "P17", "Penjual", "Submit form tambah/edit/hapus/toggle", "Nama metode, Kode, Nomor rekening, Nama pemilik, Status aktif", "CRUD SellerPaymentMethod", "Metode diperbarui, tampil di checkout pembeli", "Nama required, Nomor required", "Medium", "Observed"),
    ("F26", "Balas CS Admin (Admin)", "Customer Service", "P27", "Admin", "Submit form balas", "Conversation ID, Isi pesan", "Buat CustomerServiceMessage, throttle 20/menit", "Pesan terkirim ke user", "Throttle 20/menit", "Medium", "Observed"),
    ("F27", "Kelola Percakapan CS (Admin)", "Customer Service", "P27", "Admin", "Klik tutup/buka tiket", "Conversation ID", "Update status percakapan open/closed, catat closed_at", "Status tiket berubah", "-", "Medium", "Observed"),
    ("F28", "Validasi Produk (Admin)", "Produk", "P22", "Admin", "Submit form approval", "Produk ID, Status (disetujui/ditolak), Catatan admin", "Validasi status produk=menunggu, update status + catatan_admin", "Produk disetujui/ditolak, tampil/tidak di katalog", "Status produk harus menunggu, catatan wajib jika ditolak", "Critical", "Verified"),
    ("F29", "Aktif/Nonaktif Produk (Admin)", "Produk", "P23", "Admin", "Toggle is_active", "Produk ID, is_active boolean", "Update produk.is_active", "Produk tampil/tidak di katalog pembeli", "-", "High", "Observed"),
    ("F30", "Ubah Harga Produk (Admin)", "Produk", "P23", "Admin", "Submit form ubah harga", "Produk ID, Harga baru", "Update harga, catat RiwayatHarga jika berbeda", "Harga diperbarui, riwayat tercatat", "Harga min 1 max 100jt", "Medium", "Verified"),
    ("F31", "Kelola Pengguna (Admin)", "Pengguna", "P21", "Admin", "Toggle/dropdown ubah role/status atau klik reset", "User ID, Role atau Status baru", "Update user.role / user.is_active, atau kirim email reset", "Data pengguna diperbarui, atau email terkirim", "Tidak bisa ubah/nonaktif akun sendiri, penjual hanya 1, admin aktif terakhir tidak bisa dicopot", "High", "Verified"),
    ("F32", "Proses Refund (Admin)", "Pesanan", "P24", "Admin", "Submit form refund", "Pesanan ID, Alasan refund", "Buat PengembalianDana, catat admin_id", "Refund tercatat", "-", "High", "Observed"),
    ("F33", "Laporan Keuangan & Ekspor (Admin)", "Keuangan", "P25", "Admin", "Lihat laporan / klik ekspor", "Filter tanggal, status", "Query transaksi semua penjual, generate Excel/PDF", "Tabel laporan keuangan, file unduhan", "-", "Medium", "Observed"),
    ("F34", "Kelola Jasa Kirim (Admin)", "Pengaturan", "P26", "Admin", "Submit form tambah/edit", "Nama, Kode, Tarif per kg, Status aktif", "CRUD JasaKirim", "Jasa kirim tersedia di checkout pembeli", "Nama required, Kode required, Tarif min 0", "Medium", "Observed"),
    ("F35", "Lihat Landing Page", "Navigasi", "P00", "Publik (guest)", "Buka halaman root", "URL /", "Tampilkan informasi usaha dan tautan login/registrasi", "Landing page tersedia untuk pengunjung", "-", "Low", "Documented"),
    ("F36", "Lihat Dashboard Pembeli", "Dashboard", "P05", "Pembeli", "Buka dashboard pembeli", "Sesi Pembeli", "Tampilkan ringkasan akun dan tautan belanja/pesanan", "Ringkasan pesanan, katalog, dan keranjang", "-", "Medium", "Documented"),
    ("F37", "Lihat Dashboard Penjual", "Dashboard", "P13", "Penjual", "Buka dashboard penjual", "Sesi Penjual", "Tampilkan indikator toko dan pesanan mendesak", "Ringkasan penjualan, pesanan, produk aktif, pengajuan produk", "-", "Medium", "Documented"),
    ("F38", "Lihat Dashboard Admin", "Dashboard", "P20", "Admin", "Buka dashboard admin", "Sesi Admin", "Tampilkan statistik platform dan ringkasan antrean", "Statistik pengguna, validasi produk, transaksi, CS", "-", "Medium", "Documented"),
    ("F39", "Pengarah Dashboard Berdasarkan Role", "Navigasi", "P28", "Semua (login)", "Akses /dashboard", "Sesi pengguna terautentikasi", "Pilih dashboard berdasarkan role akun", "Redirect ke dashboard khusus role", "Pengguna harus login dan akun aktif", "High", "Documented"),
]

BUSINESS_RULES = [
    ("BR01", "Stok satu baris per produk", "Produk", "Setiap produk memiliki tepat satu baris stok. Stok tidak dibagi per varian.", "Verified"),
    ("BR02", "Kategori produk eksklusif", "Produk", "Produk matang dan mentah adalah entitas terpisah dengan stok masing-masing.", "Verified"),
    ("BR03", "Produk harus disetujui admin", "Produk", "Produk dengan status bukan 'disetujui' tidak muncul di katalog pembeli.", "Verified"),
    ("BR04", "Stok kosong = tombol dinonaktifkan", "Produk/Belanja", "Tombol tambah ke keranjang dinonaktifkan jika stok = 0. Server juga memvalidasi saat add dan checkout.", "Verified"),
    ("BR05", "Satu toko per checkout", "Belanja", "Checkout hanya bisa dilakukan untuk produk dari satu penjual dalam satu pesanan.", "Verified"),
    ("BR06", "Checkout atomik", "Belanja", "Pengurangan stok, pembuatan pesanan, detail, transaksi, dan mutasi dilakukan dalam satu transaksi DB.", "Verified"),
    ("BR07", "Register = role Pembeli", "Autentikasi", "Pendaftaran publik selalu menghasilkan akun dengan role Pembeli. Role tidak bisa dipilih.", "Verified"),
    ("BR08", "Login cek is_active", "Autentikasi", "Login gagal jika akun dinonaktifkan (is_active=false), meskipun kredensial benar.", "Verified"),
    ("BR09", "Throttle login/register", "Autentikasi", "Login dan register dibatasi 5 request per menit untuk mencegah brute force.", "Verified"),
    ("BR10", "Alur status pesanan berurutan", "Pesanan", "menunggu → diproses → dikirim → selesai. Tidak bisa skip atau mundur.", "Verified"),
    ("BR11", "Transfer harus ada bukti sebelum verifikasi", "Pesanan", "Penjual tidak bisa verifikasi pembayaran transfer tanpa bukti dari pembeli.", "Verified"),
    ("BR12", "COD bypass verifikasi transfer", "Pesanan", "Pesanan COD bisa langsung diproses tanpa upload bukti bayar.", "Verified"),
    ("BR13", "Resi wajib saat kirim", "Pesanan", "Penjual wajib isi nomor resi dan upload foto saat mengubah status ke dikirim.", "Verified"),
    ("BR14", "COD lunas saat konfirmasi", "Pesanan", "Untuk pesanan COD, status pembayaran menjadi lunas saat pembeli konfirmasi barang diterima.", "Verified"),
    ("BR15", "Penjual hanya satu", "Pengguna", "Sistem hanya boleh memiliki satu akun dengan role penjual.", "Verified"),
    ("BR16", "Admin aktif terakhir dilindungi", "Pengguna", "Admin aktif terakhir tidak bisa dinonaktifkan atau dicabut rolenya.", "Verified"),
    ("BR17", "Riwayat harga dicatat", "Produk", "Setiap perubahan harga produk (oleh penjual atau admin) dicatat ke riwayat_harga_produk.", "Verified"),
    ("BR18", "Produk ditolak bisa diajukan ulang", "Produk", "Penjual bisa mengedit dan resubmit produk yang ditolak; status kembali ke menunggu.", "Verified"),
    ("BR19", "Stok keluar tidak boleh negatif", "Stok", "Mutasi keluar tidak diizinkan jika jumlah > stok tersedia.", "Verified"),
    ("BR20", "Email reset via log di local", "Autentikasi", "Di environment local, email reset ditulis ke log aplikasi, bukan dikirim ke kotak masuk.", "Documented"),
]

QA_REQS = [
    # (req_id, feat_id, description, priority, test_types)
    ("QA001", "F01", "Verifikasi login berhasil dengan kredensial valid untuk tiap role (admin, penjual, pembeli)", "Critical", "Functional, Auth"),
    ("QA002", "F01", "Verifikasi login gagal dengan password salah", "Critical", "Functional, Negative"),
    ("QA003", "F01", "Verifikasi login ditolak untuk akun nonaktif (is_active=false)", "Critical", "Auth, Security"),
    ("QA004", "F01", "Verifikasi redirect sesuai role setelah login berhasil", "High", "Functional"),
    ("QA005", "F01", "Verifikasi throttle login (lebih dari 5 request/menit ditolak)", "High", "Security"),
    ("QA006", "F02", "Verifikasi register berhasil dengan data valid, otomatis role pembeli", "High", "Functional"),
    ("QA007", "F02", "Verifikasi register gagal dengan email duplikat", "High", "Functional, Negative"),
    ("QA008", "F02", "Verifikasi validasi form register (password min 8, confirmed)", "High", "Validation"),
    ("QA009", "F07", "Verifikasi katalog hanya menampilkan produk status=disetujui dan is_active=true", "High", "Functional, Auth"),
    ("QA010", "F08", "Verifikasi tambah ke keranjang berhasil dengan jumlah valid", "High", "Functional"),
    ("QA011", "F08", "Verifikasi tambah ke keranjang gagal jika jumlah melebihi stok", "High", "Functional, Negative"),
    ("QA012", "F08", "Verifikasi produk nonaktif/belum disetujui tidak bisa ditambahkan ke keranjang", "High", "Auth, Negative"),
    ("QA013", "F11", "Verifikasi checkout berhasil membuat pesanan, detail, transaksi, dan mengurangi stok", "Critical", "Functional, Integration"),
    ("QA014", "F11", "Verifikasi checkout gagal jika stok habis di saat checkout", "Critical", "Functional, Negative, Concurrency"),
    ("QA015", "F11", "Verifikasi checkout hanya bisa untuk satu toko", "High", "Business Rule"),
    ("QA016", "F12", "Verifikasi upload bukti pembayaran berhasil disimpan", "High", "Functional"),
    ("QA017", "F13", "Verifikasi konfirmasi barang diterima mengubah status menjadi selesai", "High", "Functional"),
    ("QA018", "F17", "Verifikasi tambah produk oleh penjual, status awal menunggu", "High", "Functional"),
    ("QA019", "F18", "Verifikasi edit produk ditolak bisa diajukan ulang ke status menunggu", "High", "Functional, Business Rule"),
    ("QA020", "F19", "Verifikasi mutasi stok keluar tidak bisa melebihi stok tersedia", "High", "Functional, Validation"),
    ("QA021", "F21", "Verifikasi verifikasi pembayaran transfer lunas mengubah status pesanan ke diproses", "Critical", "Functional"),
    ("QA022", "F21", "Verifikasi verifikasi pembayaran transfer gagal tidak mengubah status pesanan", "High", "Functional, Negative"),
    ("QA023", "F22", "Verifikasi input resi dan upload bukti kirim mengubah status ke dikirim", "Critical", "Functional"),
    ("QA024", "F28", "Verifikasi admin menyetujui produk menampilkan produk di katalog", "Critical", "Functional"),
    ("QA025", "F28", "Verifikasi admin menolak produk dengan catatan, produk tidak tampil di katalog", "High", "Functional"),
    ("QA026", "F31", "Verifikasi admin tidak bisa ubah/nonaktif akunnya sendiri", "High", "Security, Business Rule"),
    ("QA027", "F31", "Verifikasi admin aktif terakhir tidak bisa dinonaktifkan", "High", "Security, Business Rule"),
    ("QA028", "F31", "Verifikasi sistem tidak bisa punya lebih dari satu penjual", "High", "Business Rule"),
    ("QA029", "F01-F39", "Verifikasi akses URL yang memerlukan autentikasi tanpa login ditolak atau diarahkan ke login", "Critical", "Auth, Security"),
    ("QA030", "F01-F39", "Verifikasi akses URL role tertentu dengan role yang tidak sesuai ditolak", "Critical", "Auth, Security"),
]


def _feature_page_ids(feature):
    return [page_id.strip() for page_id in feature[3].split(",")]


def _feature_role_access(actor):
    actor_lower = actor.lower()
    roles = []
    if "publik" in actor_lower or "guest" in actor_lower or "via link" in actor_lower:
        roles.append("Publik")
    if "semua (login)" in actor_lower:
        roles.extend(["Pembeli", "Penjual", "Admin"])
    else:
        roles.extend(role for role in ("Pembeli", "Penjual", "Admin") if role.lower() in actor_lower)
    return roles


def build_feature_qa_requirements():
    requirements = []
    for feature in FEATURES:
        feature_id, name, module, page_ref, actor, trigger, inputs, process, output, validation, priority, _status = feature
        requirements.append({
            "req_id": f"REQ-{feature_id}",
            "feature_id": feature_id,
            "page_ref": page_ref,
            "requirement": f"Sistem harus mendukung fitur {name} sesuai alur dan validasi yang terdokumentasi.",
            "expected_behavior": output,
            "preconditions": f"Aktor: {actor}. Siapkan data yang diperlukan oleh alur fitur; kredensial pengujian hanya dikelola melalui QA/.env.",
            "test_conditions": f"Pemicu: {trigger}. Input: {inputs}.",
            "positive_scenario": f"Jalankan pemicu dengan input valid dan verifikasi hasil: {output}.",
            "negative_scenario": (
                f"Uji penolakan input yang melanggar aturan: {validation}. "
                "Periksa bahwa perubahan yang tidak sah tidak tersimpan."
                if validation != "-"
                else "Belum dijelaskan pada source; tentukan skenario negatif saat test planning."
            ),
            "boundary_scenario": (
                f"Uji batas yang dinyatakan pada source: {validation}."
                if any(term in validation.lower() for term in ("min", "max", "maks", "minimal", "minimal"))
                else "Tidak ada batas numerik yang dinyatakan pada source."
            ),
            "permission_scenario": (
                f"Pastikan akses fitur sesuai aktor yang ditetapkan: {actor}; bandingkan dengan middleware route."
            ),
            "integration_scenario": f"Periksa efek/alur yang dinyatakan pada source: {process}.",
            "priority": priority,
            "evidence_ref": f"{page_ref}; fitur {feature_id}; routes/web.php dan implementasi terkait. Perilaku runtime belum diverifikasi.",
        })
    return requirements


FEATURE_QA_REQUIREMENTS = build_feature_qa_requirements()

PERMISSION_FEATURES = [
    (feature[0], feature[1], feature[4], _feature_role_access(feature[4]))
    for feature in FEATURES
]

ORDER_FLOW = """
stateDiagram-v2
    [*] --> Menunggu : Pembeli checkout
    Menunggu --> Diproses : Penjual verifikasi bayar (transfer lunas) ATAU Penjual advance (COD)
    Menunggu --> Menunggu : Pembeli upload bukti bayar
    Diproses --> Dikirim : Penjual input resi + bukti kirim
    Dikirim --> Selesai : Pembeli konfirmasi barang diterima
    Selesai --> [*]
    Menunggu --> Refund : Admin proses refund
    Diproses --> Refund : Admin proses refund
    Dikirim --> Refund : Admin proses refund
"""

PRODUCT_FLOW = """
flowchart TD
    A[Penjual ajukan produk baru] --> B[Status: Menunggu]
    B --> C{Admin validasi}
    C -->|Setujui| D[Status: Disetujui]
    C -->|Tolak + catatan| E[Status: Ditolak]
    E -->|Penjual edit & ajukan ulang| B
    D --> F[Tampil di katalog pembeli]
    D --> G{Admin / Penjual ubah harga}
    G --> H[Catat riwayat harga]
    D --> I{Admin toggle is_active}
    I -->|Nonaktif| J[Tidak tampil di katalog]
    I -->|Aktif| F
"""


# ─────────────────────────────────────────────
# 1. DISCOVERY DATA JSON
# ─────────────────────────────────────────────

def generate_json():
    public_discovery = load_public_discovery()
    data = {
        "project": {
            "name": APP_NAME,
            "type": "E-Commerce / Marketplace (B2C) — Single Vendor",
            "purpose": "Platform jual-beli produk tahu online antara penjual tahu dan pembeli",
            "url": "http://localhost:8000",
            "tech_stack": "PHP 8.4, Laravel 13, MySQL, Vite 7, Tailwind CSS 4, Laravel Excel, Laravel DomPDF",
            "discovery_date": TODAY,
            "discovery_method": "Source code analysis plus Playwright read-only crawl for publicly linked pages",
            "evidence_level": SOURCE_STATUS,
        },
        "roles": [
            {"id": "R01", "name": "Publik", "description": "Pengunjung tanpa login", "auth": False},
            {"id": "R02", "name": "Pembeli", "description": "Pengguna yang berbelanja", "auth": True},
            {"id": "R03", "name": "Penjual", "description": "Pengelola toko dan produk", "auth": True},
            {"id": "R04", "name": "Admin", "description": "Administrator sistem", "auth": True},
        ],
        "pages": [{
            "id": p[0], "name": p[1], "url": p[2], "module": p[3],
            "roles": p[4], "purpose": p[5], "components": p[6],
            "actions": p[7], "status": SOURCE_STATUS,
        } for p in PAGES],
        "features": [{
            "id": f[0], "name": f[1], "module": f[2], "page": f[3],
            "actor": f[4], "trigger": f[5], "input": f[6],
            "process": f[7], "output": f[8], "validation": f[9],
            "priority": f[10], "status": SOURCE_STATUS,
        } for f in FEATURES],
        "business_rules": [{
            "id": r[0], "name": r[1], "module": r[2],
            "rule": r[3], "status": SOURCE_STATUS,
        } for r in BUSINESS_RULES],
        "qa_requirements": FEATURE_QA_REQUIREMENTS,
        "qa_scenarios": [{
            "id": q[0], "feature": q[1], "description": q[2],
            "priority": q[3], "test_types": q[4],
        } for q in QA_REQS],
        "public_browser_discovery": public_discovery,
        "permission_matrix": [{
            "feature_id": feature_id,
            "feature": name,
            "roles": {role: role in allowed_roles for role in ("Publik", "Pembeli", "Penjual", "Admin")},
        } for feature_id, name, _actor, allowed_roles in PERMISSION_FEATURES],
        "discovery_limitations": [
            "Discovery mendalam untuk halaman yang memerlukan login dilakukan melalui source code, bukan sesi browser tiap role",
            "Status halaman dan fitur pada inventaris tidak menyatakan eksekusi fungsional atau verifikasi runtime",
            "Alur pesanan yang bergantung pada data aktual (pesanan, stok) tidak dapat diverifikasi tanpa data demo yang lengkap",
            "Integrasi email (forgot password) tidak terverifikasi karena mailer=log di environment local",
            "Perilaku UI interaktif (modal, AJAX, badge real-time) hanya di-infer dari kode, belum diobservasi langsung",
        ],
    }
    path = os.path.join(DATA_DIR, "discovery_data.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"JSON: {path}")


# ─────────────────────────────────────────────
# 2. APPLICATION OVERVIEW DOCX
# ─────────────────────────────────────────────

def generate_overview_docx():
    doc = Document()
    apply_doc_style(doc, "Application Overview & Discovery Report", "QA Discovery — PHASE 0–5")

    doc.add_heading("1. Profil Aplikasi", 1)
    table = doc.add_table(rows=1, cols=2)
    table.style = "Table Grid"
    tbl_header_row(table, ["Parameter", "Nilai"])
    rows = [
        ("Nama Aplikasi", APP_NAME),
        ("Tipe Aplikasi", "E-Commerce / Marketplace (B2C) — Single Vendor"),
        ("Tujuan Utama", "Platform jual-beli produk tahu online antara penjual dan pembeli"),
        ("URL Target", "http://localhost:8000"),
        ("Tanggal Discovery", TODAY),
        ("Technology Stack", "PHP 8.4, Laravel 13, MySQL, Vite 7, Tailwind CSS 4"),
        ("Library Tambahan", "Laravel Excel (ekspor spreadsheet), Laravel DomPDF (ekspor PDF)"),
        ("Authentication", "Session-based Laravel Auth (email + password)"),
        ("Authorization", "Role-based Middleware (RoleMiddleware) + EnsureAccountIsActive"),
        ("Deployment", "Local — Laragon (http://localhost:8000)"),
        ("Metode Discovery", "Analisis routes, views, controllers, models, migrations; environment check publik"),
        ("Evidence Level", SOURCE_STATUS),
    ]
    for r in rows:
        add_tbl_row(table, r)

    doc.add_heading("2. Role Pengguna", 1)
    table2 = doc.add_table(rows=1, cols=4)
    table2.style = "Table Grid"
    tbl_header_row(table2, ["Role ID", "Nama Role", "Deskripsi", "Akun Uji"])
    role_rows = [
        ("R01", "Publik", "Pengunjung tanpa login: landing, login, register, dan pemulihan kata sandi", "Tidak diperlukan"),
        ("R02", "Pembeli", "Berbelanja produk: katalog, keranjang, checkout, pesanan, chat, dan CS", "Dikelola melalui QA/.env"),
        ("R03", "Penjual", "Kelola produk, stok, pesanan, transaksi, metode pembayaran, dan CS", "Dikelola melalui QA/.env"),
        ("R04", "Admin", "Administrasi produk, pengguna, pesanan, keuangan, kurir, dan CS", "Dikelola melalui QA/.env"),
    ]
    for r in role_rows:
        add_tbl_row(table2, r)

    doc.add_heading("3. Modul Utama", 1)
    modules = [
        ("MOD-01", "Autentikasi", "Login, Register, Logout, Forgot/Reset Password", "Semua"),
        ("MOD-02", "Profil", "Edit data diri (nama, foto, telepon, alamat)", "Semua (login)"),
        ("MOD-03", "Belanja", "Katalog produk, Keranjang, Checkout", "Pembeli"),
        ("MOD-04", "Pesanan Pembeli", "Lihat pesanan, Upload bukti bayar, Konfirmasi diterima", "Pembeli"),
        ("MOD-05", "Produk Penjual", "Tambah/edit produk, Kelola stok (mutasi & sesuaikan)", "Penjual"),
        ("MOD-06", "Pesanan Penjual", "Verifikasi bayar, Input resi & bukti kirim", "Penjual"),
        ("MOD-07", "Keuangan Penjual", "Lihat & ekspor transaksi (Excel/PDF)", "Penjual"),
        ("MOD-08", "Metode Pembayaran", "Kelola metode bayar yang tampil di checkout", "Penjual"),
        ("MOD-09", "Dashboard Admin", "Ringkasan statistik sistem", "Admin"),
        ("MOD-10", "Manajemen Pengguna", "Ubah role, aktif/nonaktif, kirim link reset password", "Admin"),
        ("MOD-11", "Validasi Produk", "Approve/reject pengajuan produk dari penjual", "Admin"),
        ("MOD-12", "Manajemen Produk Admin", "Aktif/nonaktif produk, ubah harga", "Admin"),
        ("MOD-13", "Pesanan Admin", "Monitor semua pesanan, proses refund", "Admin"),
        ("MOD-14", "Laporan Keuangan", "Filter & ekspor laporan keuangan (Excel/PDF)", "Admin"),
        ("MOD-15", "Jasa Kirim", "CRUD kurir untuk pilihan checkout", "Admin"),
        ("MOD-16", "Chat Pesanan", "Chat real-time antara pembeli dan penjual per pesanan", "Pembeli, Penjual"),
        ("MOD-17", "Pusat Bantuan (CS)", "Tiket bantuan: pembeli/penjual ke admin", "Semua (login)"),
    ]
    table3 = doc.add_table(rows=1, cols=4)
    table3.style = "Table Grid"
    tbl_header_row(table3, ["ID Modul", "Nama Modul", "Deskripsi", "Role"])
    for m in modules:
        add_tbl_row(table3, m)

    doc.add_heading("4. Alur Status Pesanan", 1)
    doc.add_paragraph(
        "Pesanan mengikuti alur status berurutan yang tidak dapat dibalik:\n"
        "menunggu → diproses → dikirim → selesai\n\n"
        "Trigger transisi:\n"
        "• menunggu: Dibuat otomatis saat pembeli checkout\n"
        "• diproses: Penjual verifikasi pembayaran transfer (lunas) ATAU advance status pesanan COD\n"
        "• dikirim: Penjual isi nomor resi + upload foto bukti pengiriman\n"
        "• selesai: Pembeli konfirmasi barang sudah diterima\n"
        "• refund: Admin dapat memproses pengembalian dana di status apapun"
    )

    doc.add_heading("5. Alur Status Produk", 1)
    doc.add_paragraph(
        "Produk mengikuti alur approval sebelum tampil di katalog:\n"
        "menunggu → disetujui / ditolak\n\n"
        "• Penjual mengajukan produk baru → status = menunggu\n"
        "• Admin menyetujui → status = disetujui → tampil di katalog\n"
        "• Admin menolak (dengan catatan) → status = ditolak → tidak tampil\n"
        "• Penjual edit produk ditolak dan submit ulang → status kembali ke menunggu\n"
        "• Admin / penjual bisa ubah harga; riwayat harga selalu dicatat\n"
        "• Admin bisa toggle is_active untuk nonaktifkan produk tanpa mengubah status approval"
    )

    doc.add_heading("6. Entitas Data Utama", 1)
    entities = [
        ("users", "Akun pengguna", "id, name, email, password, role (admin/penjual/pembeli), is_active, no_telepon, alamat, foto"),
        ("produk", "Katalog produk", "id, seller_id, nama_produk, kategori (matang/mentah), harga, deskripsi, gambar, status (menunggu/disetujui/ditolak), is_active, catatan_admin"),
        ("stok", "Stok produk (1 baris per produk)", "id, produk_id, kategori, jumlah, tanggal_update"),
        ("buyer_cart_items", "Item keranjang belanja pembeli", "id, user_id, produk_id, kategori, jumlah"),
        ("pesanan", "Pesanan dari pembeli", "id, user_id, tanggal_pesanan, total_harga, alamat_pengiriman, status, jasa_kirim_id, berat_gram, ongkir, nomor_resi, bukti_pengiriman, tanggal_selesai"),
        ("detail_pesanan", "Rincian item dalam pesanan", "id, pesanan_id, produk_id, kategori, jumlah, harga_satuan, subtotal"),
        ("transaksi", "Transaksi pembayaran", "id, pesanan_id, total_bayar, metode_pembayaran, status_pembayaran (pending/lunas/gagal), bukti_pembayaran, payment_account_*, verified_at, catatan_verifikasi"),
        ("mutasi_stok", "Riwayat perubahan stok", "id, user_id, produk_id, kategori, jenis (masuk/keluar), jumlah, catatan"),
        ("order_messages", "Pesan chat per pesanan", "id, pesanan_id, sender_id, message, read_at"),
        ("customer_service_conversations", "Tiket bantuan CS", "id, user_id, status (open/closed), closed_at"),
        ("customer_service_messages", "Pesan dalam tiket CS", "id, conversation_id, sender_id, message, read_at"),
        ("seller_payment_methods", "Metode pembayaran toko", "id, seller_id, name, code, account_number, account_holder, is_active"),
        ("jasa_kirim", "Data kurir/jasa pengiriman", "id, nama, kode, tarif_per_kg, is_active"),
        ("pengembalian_dana", "Refund yang diproses admin", "id, pesanan_id, admin_id, alasan, nominal, ..."),
        ("riwayat_harga_produk", "Log perubahan harga produk", "id, produk_id, user_id, harga_lama, harga_baru, created_at"),
    ]
    table4 = doc.add_table(rows=1, cols=3)
    table4.style = "Table Grid"
    tbl_header_row(table4, ["Tabel", "Deskripsi", "Field Utama"])
    for e in entities:
        add_tbl_row(table4, e, font_size=9)

    doc.add_heading("7. Keterbatasan Discovery", 1)
    public_discovery = load_public_discovery()
    if public_discovery:
        doc.add_heading("Bukti Browser Publik", 2)
        doc.add_paragraph(
            f"Playwright crawler read-only mengunjungi {len(public_discovery.get('pages', []))} halaman publik. "
            "Crawler tidak mengisi atau mengirim formulir."
        )
        browser_table = doc.add_table(rows=1, cols=4)
        browser_table.style = "Table Grid"
        tbl_header_row(browser_table, ["URL", "Judul", "HTTP", "Screenshot"], "2E74B5")
        for page in public_discovery.get("pages", []):
            add_tbl_row(browser_table, (
                page.get("final_url") or page.get("requested_url"),
                page.get("title", "-"),
                page.get("http_status", "-"),
                page.get("screenshot", "-"),
            ), font_size=9)

    limitations = [
        "Halaman yang memerlukan login ditelusuri melalui source code; screenshot browser yang ada hanya menjadi bukti environment publik",
        "Inventaris ini mendokumentasikan rancangan/implementasi sumber dan bukan hasil verifikasi fungsional runtime",
        "Alur pesanan yang bergantung pada data aktual (pesanan berjalan, stok habis) belum diverifikasi end-to-end",
        "Integrasi email (forgot password) tidak terverifikasi — mailer=log di environment local",
        "Perilaku UI interaktif (modal, AJAX, badge real-time, kalkulasi ongkir client-side) di-infer dari kode, belum diobservasi langsung",
        "Halaman yang memerlukan data terkait pesanan aktif (chat, bukti bayar) tidak dapat dieksplorasi secara dinamis",
    ]
    for lim in limitations:
        doc.add_paragraph(f"• {lim}")

    path = os.path.join(DOCS_DIR, "01_Application_Overview.docx")
    doc.save(path)
    print(f"DOCX: {path}")


# ─────────────────────────────────────────────
# 3. FEATURE INVENTORY XLSX
# ─────────────────────────────────────────────

def generate_feature_xlsx():
    wb = openpyxl.Workbook()

    # ── Sheet 1: Page Inventory ──
    ws1 = wb.active
    ws1.title = "Page Inventory"
    headers1 = ["Page ID", "Nama Halaman", "URL", "Modul", "Role", "Tujuan", "Komponen", "Aksi", "Status Bukti"]
    _apply_xlsx_header(ws1, headers1, "1F497D")
    for p in PAGES:
        ws1.append([p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], SOURCE_STATUS])
    _auto_width(ws1)
    ws1.freeze_panes = "A2"
    ws1.auto_filter.ref = ws1.dimensions

    # ── Sheet 2: Feature Inventory ──
    ws2 = wb.create_sheet("Feature Inventory")
    headers2 = ["Feature ID", "Nama Fitur", "Modul", "Page Ref", "Aktor", "Trigger", "Input", "Proses", "Output", "Validasi", "Prioritas", "Status"]
    _apply_xlsx_header(ws2, headers2, "1F497D")
    for f in FEATURES:
        ws2.append([*f[:11], SOURCE_STATUS])
    _auto_width(ws2)
    ws2.freeze_panes = "A2"
    ws2.auto_filter.ref = ws2.dimensions

    # ── Sheet 3: Page-to-feature traceability ──
    ws3 = wb.create_sheet("Page Feature Map")
    headers3 = ["Page ID", "Nama Halaman", "Feature ID", "Nama Fitur", "Aktor", "Trigger", "Input", "Output", "Validasi"]
    _apply_xlsx_header(ws3, headers3, "375623")
    page_by_id = {page[0]: page for page in PAGES}
    for feature in FEATURES:
        for page_id in _feature_page_ids(feature):
            page = page_by_id.get(page_id)
            if page:
                ws3.append([page_id, page[1], feature[0], feature[1], feature[4], feature[5], feature[6], feature[8], feature[9]])
    _auto_width(ws3)
    ws3.freeze_panes = "A2"
    ws3.auto_filter.ref = ws3.dimensions

    # ── Sheet 4: Business Rules ──
    ws4 = wb.create_sheet("Business Rules")
    headers4 = ["Rule ID", "Nama", "Modul", "Aturan Bisnis", "Status Evidence"]
    _apply_xlsx_header(ws4, headers4, "375623")
    for r in BUSINESS_RULES:
        ws4.append([*r[:4], SOURCE_STATUS])
    _auto_width(ws4)
    ws4.freeze_panes = "A2"
    ws4.auto_filter.ref = ws4.dimensions

    # ── Sheet 5: Role Permission Matrix ──
    ws5 = wb.create_sheet("Permission Matrix")
    roles_col = ["Feature ID", "Fitur", "Aktor", "Publik", "Pembeli", "Penjual", "Admin"]
    _apply_xlsx_header(ws5, roles_col, "7B2C2C")
    for feature_id, name, actor, allowed_roles in PERMISSION_FEATURES:
        ws5.append([feature_id, name, actor, *[
            "✓" if role in allowed_roles else "✗"
            for role in ("Publik", "Pembeli", "Penjual", "Admin")
        ]])
        for col_idx in range(4, 8):
            cell = ws5.cell(row=ws5.max_row, column=col_idx)
            if cell.value == "✓":
                cell.fill = PatternFill("solid", fgColor="C6EFCE")
                cell.font = Font(bold=True, color="375623")
            else:
                cell.fill = PatternFill("solid", fgColor="FFCCCC")
                cell.font = Font(color="9C0006")
            cell.alignment = Alignment(horizontal="center")
    _auto_width(ws5)
    ws5.freeze_panes = "D2"
    ws5.auto_filter.ref = ws5.dimensions

    # ── Sheet 6: Requirements for every feature ──
    ws6 = wb.create_sheet("QA Requirements")
    requirement_headers = [
        "Req ID", "Feature ID", "Page Ref", "Requirement", "Expected Behavior",
        "Preconditions", "Test Conditions", "Positive Scenario", "Negative Scenario",
        "Boundary Scenario", "Permission Scenario", "Integration Scenario", "Priority", "Evidence Ref",
    ]
    requirement_keys = [
        "req_id", "feature_id", "page_ref", "requirement", "expected_behavior",
        "preconditions", "test_conditions", "positive_scenario", "negative_scenario",
        "boundary_scenario", "permission_scenario", "integration_scenario", "priority", "evidence_ref",
    ]
    _apply_xlsx_header(ws6, requirement_headers, "1F497D")
    for requirement in FEATURE_QA_REQUIREMENTS:
        ws6.append([requirement[key] for key in requirement_keys])
        priority_cell = ws6.cell(row=ws6.max_row, column=13)
        if priority_cell.value == "Critical":
            priority_cell.fill = PatternFill("solid", fgColor="FF0000")
            priority_cell.font = Font(bold=True, color="FFFFFF")
        elif priority_cell.value == "High":
            priority_cell.fill = PatternFill("solid", fgColor="FF7F00")
            priority_cell.font = Font(bold=True, color="FFFFFF")
    _auto_width(ws6)
    ws6.freeze_panes = "A2"
    ws6.auto_filter.ref = ws6.dimensions

    # ── Sheet 7: Detailed supplementary scenarios ──
    ws7 = wb.create_sheet("QA Scenarios")
    headers7 = ["Scenario ID", "Feature ID", "Deskripsi Skenario", "Prioritas", "Jenis Pengujian", "Status"]
    _apply_xlsx_header(ws7, headers7, "1F497D")
    for q in QA_REQS:
        ws7.append([*q, "Proposed; not executed"])
        cell = ws7.cell(row=ws7.max_row, column=4)
        if cell.value == "Critical":
            cell.fill = PatternFill("solid", fgColor="FF0000")
            cell.font = Font(bold=True, color="FFFFFF")
        elif cell.value == "High":
            cell.fill = PatternFill("solid", fgColor="FF7F00")
            cell.font = Font(bold=True, color="FFFFFF")
    _auto_width(ws7)
    ws7.freeze_panes = "A2"
    ws7.auto_filter.ref = ws7.dimensions

    path = os.path.join(DOCS_DIR, "02_Feature_Inventory.xlsx")
    wb.save(path)
    print(f"XLSX: {path}")


def _apply_xlsx_header(ws, headers, bg_hex):
    ws.append(headers)
    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_idx)
        cell.font = Font(bold=True, color="FFFFFF", size=11)
        cell.fill = PatternFill("solid", fgColor=bg_hex)
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[1].height = 25

def _auto_width(ws):
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            try:
                val = str(cell.value or "")
                max_len = max(max_len, len(val))
            except Exception:
                pass
            cell.alignment = Alignment(vertical="top", wrap_text=True)
        ws.column_dimensions[col_letter].width = min(max_len + 4, 60)


# ─────────────────────────────────────────────
# 4. FUNCTIONAL SPEC & QA REQUIREMENT DOCX
# ─────────────────────────────────────────────

def generate_functional_docx():
    doc = Document()
    apply_doc_style(doc, "Functional Specification & QA Requirements", "PHASE 4–6 — Spesifikasi Fungsional & Kebutuhan Pengujian")

    doc.add_heading("1. Deskripsi Fungsi per Modul", 1)

    # Group features by module
    modules_map = {}
    for f in FEATURES:
        m = f[2]
        modules_map.setdefault(m, []).append(f)

    for mod, feats in modules_map.items():
        doc.add_heading(f"Modul: {mod}", 2)
        for f in feats:
            doc.add_heading(f"{f[0]} — {f[1]}", 3)
            tbl = doc.add_table(rows=1, cols=2)
            tbl.style = "Table Grid"
            tbl_header_row(tbl, ["Atribut", "Nilai"], "2E74B5")
            attrs = [
                ("Aktor", f[4]),
                ("Trigger", f[5]),
                ("Input", f[6]),
                ("Proses", f[7]),
                ("Output", f[8]),
                ("Validasi", f[9]),
                ("Prioritas", f[10]),
                ("Status Bukti", SOURCE_STATUS),
            ]
            for a in attrs:
                add_tbl_row(tbl, a)
            doc.add_paragraph()

    doc.add_heading("2. Aturan Bisnis", 1)
    tbl_br = doc.add_table(rows=1, cols=5)
    tbl_br.style = "Table Grid"
    tbl_header_row(tbl_br, ["Rule ID", "Nama", "Modul", "Aturan Bisnis", "Evidence"])
    for r in BUSINESS_RULES:
        add_tbl_row(tbl_br, (*r[:4], SOURCE_STATUS), font_size=9)

    doc.add_heading("3. Kebutuhan QA per Fitur", 1)
    doc.add_paragraph(
        "Setiap fitur memiliki satu requirement dasar yang dapat ditelusuri ke halaman dan source terkait. "
        "Skenario di bawah merupakan rancangan berbasis source, bukan hasil eksekusi."
    )
    for requirement in FEATURE_QA_REQUIREMENTS:
        doc.add_heading(f"{requirement['req_id']} — {requirement['feature_id']} ({requirement['priority']})", 3)
        requirement_table = doc.add_table(rows=1, cols=2)
        requirement_table.style = "Table Grid"
        tbl_header_row(requirement_table, ["Atribut", "Kebutuhan"], "2E74B5")
        for label, key in [
            ("Halaman", "page_ref"),
            ("Requirement", "requirement"),
            ("Expected behavior", "expected_behavior"),
            ("Preconditions", "preconditions"),
            ("Test conditions", "test_conditions"),
            ("Skenario positif", "positive_scenario"),
            ("Skenario negatif", "negative_scenario"),
            ("Boundary", "boundary_scenario"),
            ("Permission", "permission_scenario"),
            ("Integration", "integration_scenario"),
            ("Evidence reference", "evidence_ref"),
        ]:
            add_tbl_row(requirement_table, (label, requirement[key]), font_size=9)

    doc.add_heading("4. Skenario QA Tambahan", 1)
    tbl_qa = doc.add_table(rows=1, cols=5)
    tbl_qa.style = "Table Grid"
    tbl_header_row(tbl_qa, ["Scenario ID", "Feature ID", "Deskripsi", "Prioritas", "Jenis Pengujian"])
    for q in QA_REQS:
        add_tbl_row(tbl_qa, q, font_size=9)

    doc.add_heading("5. Risiko dan Prioritas Pengujian", 1)
    risk_items = [
        ("Critical", "Checkout atomik (F11)", "Kegagalan menyebabkan pesanan tanpa stok dikurangi atau stok minus"),
        ("Critical", "Verifikasi pembayaran (F21)", "Penjual bisa memproses pesanan tanpa pembayaran valid"),
        ("Critical", "Input resi & kirim (F22)", "Barang dikirim tanpa resi tercatat"),
        ("Critical", "Login & akses kontrol (F01, QA029-030)", "Akses tidak sah ke data/fitur sensitif"),
        ("Critical", "Validasi produk (F28)", "Produk tidak tervalidasi tampil di katalog"),
        ("High", "Tambah ke keranjang race condition (F08)", "Dua pembeli bisa memborong stok terakhir bersamaan"),
        ("High", "Stok tidak boleh negatif (BR19, F19)", "Kesalahan bisnis: stok minus menyebabkan unfulfillable order"),
        ("High", "Penjual hanya satu (BR15)", "Duplikasi akun penjual menyebabkan konflik data"),
        ("High", "Admin aktif terakhir dilindungi (BR16)", "Sistem tanpa admin aktif tidak bisa dikelola"),
        ("Medium", "Ekspor Excel/PDF (F24, F33)", "Format data salah atau file corrupt"),
        ("Medium", "Notifikasi badge unread", "Badge tidak update menyebabkan CS tidak terlayani"),
        ("Low", "Responsive UI", "Tampilan tidak optimal di mobile"),
    ]
    tbl_risk = doc.add_table(rows=1, cols=3)
    tbl_risk.style = "Table Grid"
    tbl_header_row(tbl_risk, ["Prioritas Risiko", "Fitur/Area", "Dampak Jika Gagal"])
    for r in risk_items:
        row = add_tbl_row(tbl_risk, r, font_size=9)
        if r[0] == "Critical":
            set_cell_bg(row.cells[0], "FF0000")
            row.cells[0].paragraphs[0].runs[0].font.color.rgb = RGBColor(255, 255, 255)

    path = os.path.join(DOCS_DIR, "03_Functional_Spec_QA_Requirements.docx")
    doc.save(path)
    print(f"DOCX: {path}")


# ─────────────────────────────────────────────
# 5. DIAGRAMS (Mermaid text files)
# ─────────────────────────────────────────────

def generate_diagrams():
    diag_dir = os.path.join(BASE, "diagrams")
    os.makedirs(diag_dir, exist_ok=True)

    application_flow = """flowchart TD
    A([Mulai]) --> B[Landing Page]
    B --> C{Sudah login?}
    C -->|Belum| D[Login atau registrasi Pembeli]
    D --> E{Autentikasi berhasil?}
    E -->|Tidak| D
    E -->|Ya| F{Role}
    C -->|Sudah| F
    F -->|Pembeli| G[Dashboard Pembeli]
    F -->|Penjual| H[Dashboard Penjual]
    F -->|Admin| I[Dashboard Admin]
    G --> J[Katalog → Keranjang → Checkout]
    J --> K[Pesanan dan komunikasi]
    H --> L[Produk dan stok]
    H --> M[Pesanan, transaksi, pembayaran]
    L --> N{Validasi Admin}
    I --> N
    N -->|Disetujui| J
    N -->|Ditolak| L
    M --> K
    I --> O[Pengguna, keuangan, kurir, Customer Service]
    K --> P[Profil atau logout]
    L --> P
    M --> P
    O --> P
    P --> Q([Selesai])"""

    with open(os.path.join(diag_dir, "application_flow.mmd"), "w", encoding="utf-8") as f:
        f.write(application_flow.strip())
    print("Diagram: application_flow.mmd")

    # Order flow state diagram
    with open(os.path.join(diag_dir, "order_status_flow.mmd"), "w", encoding="utf-8") as f:
        f.write(ORDER_FLOW.strip())
    print("Diagram: order_status_flow.mmd")

    # Product approval flow
    with open(os.path.join(diag_dir, "product_approval_flow.mmd"), "w", encoding="utf-8") as f:
        f.write(PRODUCT_FLOW.strip())
    print("Diagram: product_approval_flow.mmd")

    # User journey — Pembeli
    journey_pembeli = """flowchart TD
    A([Pembeli buka browser]) --> B[Landing Page]
    B --> C{Sudah punya akun?}
    C -->|Tidak| D[Register]
    D --> E[Dashboard Pembeli]
    C -->|Ya| F[Login]
    F --> E
    E --> G[Lihat Katalog Produk]
    G --> H{Filter Matang/Mentah}
    H --> I[Tambah ke Keranjang]
    I --> J[Lihat Keranjang]
    J --> K{Stok & produk OK?}
    K -->|Tidak| L[Edit/hapus item]
    L --> J
    K -->|Ya| M[Checkout: Pilih alamat, kurir, metode bayar]
    M --> N[Submit Pesanan]
    N --> O{Metode bayar}
    O -->|Transfer| P[Upload Bukti Pembayaran]
    O -->|COD| Q[Tunggu penjual konfirmasi]
    P --> R[Tunggu verifikasi penjual]
    R --> S{Verifikasi}
    S -->|Lunas| T[Pesanan Diproses]
    S -->|Gagal| P
    Q --> T
    T --> U[Penjual input resi & kirim]
    U --> V[Status: Dikirim]
    V --> W[Pembeli konfirmasi barang diterima]
    W --> X([Pesanan Selesai])"""

    with open(os.path.join(diag_dir, "user_journey_pembeli.mmd"), "w", encoding="utf-8") as f:
        f.write(journey_pembeli.strip())
    print("Diagram: user_journey_pembeli.mmd")

    # Data ERD (simplified)
    erd = """erDiagram
    users ||--o{ pesanan : "membuat"
    users ||--o{ buyer_cart_items : "punya"
    users ||--o{ produk : "menjual (seller_id)"
    users ||--o| customer_service_conversations : "membuka"
    users ||--o{ seller_payment_methods : "mendaftarkan"
    produk ||--|| stok : "punya"
    produk ||--o{ detail_pesanan : "termasuk dalam"
    produk ||--o{ riwayat_harga_produk : "dicatat harganya"
    pesanan ||--o{ detail_pesanan : "terdiri dari"
    pesanan ||--|| transaksi : "memiliki"
    pesanan ||--o| pengembalian_dana : "bisa di-refund"
    pesanan ||--o{ order_messages : "punya chat"
    pesanan }o--|| jasa_kirim : "dikirim via"
    customer_service_conversations ||--o{ customer_service_messages : "berisi"
    buyer_cart_items }o--|| produk : "berisi"
    mutasi_stok }o--|| produk : "mencatat stok"
    mutasi_stok }o--|| users : "dilakukan oleh"
    """

    with open(os.path.join(diag_dir, "entity_relationship.mmd"), "w", encoding="utf-8") as f:
        f.write(erd.strip())
    print("Diagram: entity_relationship.mmd")


# ─────────────────────────────────────────────
# 6. QA HANDOVER DOCX
# ─────────────────────────────────────────────

def generate_handover_docx():
    doc = Document()
    apply_doc_style(doc, "QA Handover Document", "GATE 5 — Acuan untuk QA Automation (website-qa-automation-architect)")

    doc.add_heading("1. Ringkasan untuk QA Automation", 1)
    doc.add_paragraph(
        "Dokumen ini merupakan output final dari skill application-discovery-qa-documentation "
        "dan menjadi input wajib bagi skill website-qa-automation-architect. "
        "QA Automation harus memvalidasi perilaku aktual aplikasi terhadap expected behavior di bawah. "
        "Jika perilaku aktual berbeda, buat discrepancy report."
    )

    doc.add_heading("2. Fitur Siap Diuji (Test-Ready Features)", 1)
    doc.add_paragraph("Daftar berikut mencakup fitur yang terdokumentasi dari source; belum dieksekusi sebagai test fungsional.")
    ready = FEATURES
    tbl = doc.add_table(rows=1, cols=5)
    tbl.style = "Table Grid"
    tbl_header_row(tbl, ["Feature ID", "Nama", "Aktor", "Prioritas", "Status Bukti"])
    for f in ready:
        add_tbl_row(tbl, (f[0], f[1], f[4], f[10], SOURCE_STATUS))

    doc.add_heading("3. Preconditions untuk Test Execution", 1)
    preconditions = [
        "Aplikasi Laravel berjalan di http://localhost:8000",
        "Database sudah di-migrate dan di-seed (php artisan migrate --seed)",
        "Storage link sudah dibuat (php artisan storage:link)",
        "Akun uji untuk role yang diperlukan dikonfigurasi melalui QA/.env; jangan menaruh kredensial dalam dokumen atau log",
        "File QA/.env tersedia dengan BASE_URL dan credential yang benar",
        "Playwright dan Chromium sudah terinstall (npm run setup di folder QA/)",
        "Minimal ada satu produk disetujui dan aktif dengan stok > 0 untuk test belanja",
        "Minimal ada satu metode pembayaran penjual aktif",
        "Minimal ada satu jasa kirim aktif",
    ]
    for p in preconditions:
        doc.add_paragraph(f"• {p}")

    doc.add_heading("4. User Journey yang Harus Diuji", 1)
    journeys = [
        ("J01", "Autentikasi", "Publik → Login → Redirect dashboard sesuai role → Logout"),
        ("J02", "Register & Profil", "Publik → Register (role pembeli) → Edit profil"),
        ("J03", "Belanja End-to-End (Transfer)", "Pembeli → Katalog → Keranjang → Checkout (transfer) → Upload bukti → Penjual verifikasi → Penjual kirim → Pembeli konfirmasi"),
        ("J04", "Belanja End-to-End (COD)", "Pembeli → Katalog → Keranjang → Checkout (COD) → Penjual advance → Penjual kirim → Pembeli konfirmasi"),
        ("J05", "Approval Produk", "Penjual ajukan produk → Admin validasi (approve/reject) → Produk tampil/tidak di katalog"),
        ("J06", "Kelola Stok", "Penjual → Kelola stok: mutasi masuk, mutasi keluar, sesuaikan"),
        ("J07", "Manajemen Pengguna", "Admin → Ubah role pengguna → Aktif/nonaktif akun → Kirim link reset password"),
        ("J08", "Laporan Keuangan", "Admin → Filter laporan → Ekspor Excel → Ekspor PDF"),
        ("J09", "Customer Service", "Pembeli/Penjual → Kirim pesan CS → Admin balas → Admin tutup tiket"),
        ("J10", "Chat Pesanan", "Pembeli kirim pesan ke penjual via chat pesanan, penjual membalas"),
    ]
    tbl_j = doc.add_table(rows=1, cols=3)
    tbl_j.style = "Table Grid"
    tbl_header_row(tbl_j, ["Journey ID", "Nama", "Alur"])
    for j in journeys:
        add_tbl_row(tbl_j, j)

    doc.add_heading("5. Skenario Negatif & Boundary Prioritas", 1)
    negative = [
        ("NEG01", "Login dengan password salah", "Error message, tidak masuk"),
        ("NEG02", "Login dengan akun nonaktif", "Error message, tidak masuk"),
        ("NEG03", "Register dengan email duplikat", "Validation error email sudah terdaftar"),
        ("NEG04", "Tambah ke keranjang melebihi stok", "Error stok tidak cukup"),
        ("NEG05", "Checkout stok habis di saat submit", "Validasi server menolak, stok tidak dikurangi"),
        ("NEG06", "Verifikasi bayar tanpa bukti", "Error: belum ada bukti transfer"),
        ("NEG07", "Input resi tanpa foto bukti kirim", "Validation error file required"),
        ("NEG08", "Pembeli akses URL penjual", "HTTP 403"),
        ("NEG09", "Penjual akses URL admin", "HTTP 403"),
        ("NEG10", "Publik akses URL login-required", "Redirect ke login"),
        ("NEG11", "Admin nonaktifkan diri sendiri", "HTTP 422 / error"),
        ("NEG12", "Admin tambah penjual kedua", "Validation error penjual sudah ada"),
        ("NEG13", "Mutasi stok keluar > stok tersedia", "Validation error"),
        ("NEG14", "Upload file bukan gambar (mis. PDF)", "Validation error MIME type"),
        ("NEG15", "Konfirmasi barang diterima saat status bukan dikirim", "Validation error status"),
    ]
    tbl_neg = doc.add_table(rows=1, cols=3)
    tbl_neg.style = "Table Grid"
    tbl_header_row(tbl_neg, ["ID", "Skenario Negatif", "Expected Result"])
    for n in negative:
        add_tbl_row(tbl_neg, n, font_size=9)

    doc.add_heading("6. Permission Scenarios", 1)
    doc.add_paragraph(
        "Setiap endpoint yang memerlukan role atau autentikasi harus diuji dengan:\n"
        "• Tanpa token/session (guest) → redirect /login\n"
        "• Dengan role yang salah → HTTP 403\n"
        "• Dengan akun nonaktif → HTTP 403\n"
        "• Dengan role yang benar → response normal\n\n"
        "Endpoint yang harus diuji akses kontrol:\n"
        "• /dashboard/admin (admin only)\n"
        "• /dashboard/penjual (penjual only)\n"
        "• /dashboard/pembeli (pembeli only)\n"
        "• /admin/* (admin only)\n"
        "• /penjual/* (penjual only)\n"
        "• /pembeli/* (pembeli only)"
    )

    doc.add_heading("7. Keterbatasan Discovery (untuk QA Automation)", 1)
    doc.add_paragraph(
        "QA Automation harus memvalidasi hal-hal berikut yang belum ter-verify penuh:\n"
        "• Seluruh fitur pada inventaris didokumentasikan dari source; belum dieksekusi sebagai test fungsional\n"
        "• Badge unread di navbar (chat & CS) — perilaku real-time\n"
        "• Kalkulasi ongkir client-side (ShippingCalculator) — perlu verifikasi angka\n"
        "• Tampilan modal konfirmasi (delete, approve, refund)\n"
        "• Responsif mobile (viewport < 768px)\n"
        "• Perilaku AJAX tambah keranjang (JSON response)\n"
        "• Reset password via link email (memerlukan inspeksi log)"
    )

    doc.add_heading("8. File Discovery yang Dihasilkan", 1)
    files = [
        ("discovery/documents/01_Application_Overview.docx", "Profil aplikasi, modul, entitas data"),
        ("discovery/documents/02_Feature_Inventory.xlsx", "Page inventory, feature inventory, permission matrix, QA requirements"),
        ("discovery/documents/03_Functional_Spec_QA_Requirements.docx", "Spesifikasi fungsional per modul, aturan bisnis, kebutuhan QA, risiko"),
        ("discovery/documents/04_QA_Handover.docx", "Dokumen ini — acuan untuk QA Automation"),
        ("discovery/data/discovery_data.json", "Data discovery terstruktur (JSON)"),
        ("discovery/diagrams/application_flow.mmd", "Application flow lintas role"),
        ("discovery/diagrams/order_status_flow.mmd", "Diagram state alur status pesanan"),
        ("discovery/diagrams/product_approval_flow.mmd", "Diagram alur approval produk"),
        ("discovery/diagrams/user_journey_pembeli.mmd", "Flowchart user journey pembeli"),
        ("discovery/diagrams/entity_relationship.mmd", "Entity Relationship Diagram"),
    ]
    tbl_f = doc.add_table(rows=1, cols=2)
    tbl_f.style = "Table Grid"
    tbl_header_row(tbl_f, ["File", "Isi"])
    for fi in files:
        add_tbl_row(tbl_f, fi, font_size=9)

    path = os.path.join(DOCS_DIR, "04_QA_Handover.docx")
    doc.save(path)
    print(f"DOCX: {path}")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print(f"QA Discovery - {APP_NAME}")
    print("Generating all documentation...")
    print("=" * 60)

    generate_json()
    generate_overview_docx()
    generate_feature_xlsx()
    generate_functional_docx()
    generate_diagrams()
    generate_handover_docx()

    print("=" * 60)
    print("Semua dokumen berhasil dibuat.")
    print(f"   Documents: {DOCS_DIR}")
    print(f"   Data: {DATA_DIR}")
    print(f"   Diagrams: {os.path.join(BASE, 'diagrams')}")
    print("=" * 60)
