from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
SCREENSHOTS = ROOT / "screenshots"


def add_page_number(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.add_run("Halaman ")
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    paragraph._p.append(field)
    paragraph.add_run(" | Immortal Tahu - Panduan Pengguna")


def prepare_document():
    doc = Document()
    for section in doc.sections:
        section.page_width = Cm(21)
        section.page_height = Cm(29.7)
        section.top_margin = Cm(2)
        section.bottom_margin = Cm(2)
        section.left_margin = Cm(2.2)
        section.right_margin = Cm(2.2)
        section.header.paragraphs[0].text = "IMMORTAL TAHU | PANDUAN PENGGUNA"
        section.header.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
        section.header.paragraphs[0].style = "Caption"
        add_page_number(section.footer.paragraphs[0])

    doc.styles["Normal"].font.name = "Arial"
    doc.styles["Normal"].font.size = Pt(10)
    for name, size in (("Title", 24), ("Heading 1", 16), ("Heading 2", 12)):
        style = doc.styles[name]
        style.font.name = "Arial"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor(31, 73, 125)
    doc.core_properties.title = "Website User Tutorial - Immortal Tahu"
    doc.core_properties.author = "QA Automation"
    return doc


def add_steps(doc, steps):
    for step in steps:
        doc.add_paragraph(step, style="List Number")


def add_screenshot(doc, filename, caption):
    path = SCREENSHOTS / filename
    if not path.exists():
        return
    paragraph = doc.add_paragraph(caption, style="Caption")
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_picture(str(path), width=Inches(6.1))


def main():
    REPORTS.mkdir(parents=True, exist_ok=True)
    doc = prepare_document()
    cover = doc.add_paragraph()
    cover.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = cover.add_run("IMMORTAL TAHU\nPANDUAN PENGGUNA")
    run.bold = True
    run.font.size = Pt(23)
    run.font.color.rgb = RGBColor(31, 73, 125)
    subtitle = doc.add_paragraph("Panduan berdasarkan discovery dan pengujian UI aktual")
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    date_line = doc.add_paragraph("Environment uji: lokal | Alamat: http://localhost:8000")
    date_line.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_page_break()

    doc.add_heading("Cara membaca panduan", level=1)
    doc.add_paragraph(
        "Langkah berlabel Teruji berasal dari run Playwright aktual. Langkah berlabel "
        "Belum diverifikasi berasal dari discovery source dan belum dijalankan pada "
        "browser. Jangan menganggap langkah yang belum diverifikasi sebagai hasil QA."
    )
    doc.add_paragraph(
        "Jangan membagikan kata sandi. Gunakan akun pribadi yang disediakan oleh "
        "administrator; panduan dan screenshot ini tidak memuat kredensial."
    )

    doc.add_heading("1. Pengunjung", level=1)
    doc.add_paragraph("Status: landing page dan tampilan form login/registrasi/reset diuji. Submit registrasi dan permintaan reset tidak dijalankan.")
    doc.add_heading("Membuka halaman utama", level=2)
    add_steps(doc, [
        "Buka http://localhost:8000/ pada browser.",
        "Gunakan tombol Daftar Akun untuk menuju registrasi atau Masuk ke akun untuk menuju login.",
    ])
    add_screenshot(doc, "TC001_PUBLIC_LANDING_PAGE_STEP01_PASS.png", "Gambar 1. Landing page pengunjung (TC001).")
    doc.add_heading("Masuk ke akun", level=2)
    add_steps(doc, [
        "Buka halaman /login dan isi email serta kata sandi dari akun yang diberikan.",
        "Pilih Masuk ke dashboard. Arah dashboard mengikuti role akun.",
        "Jika kredensial tidak sesuai, periksa pesan validasi dan hubungi administrator bila akun seharusnya aktif.",
    ])
    doc.add_paragraph("Teruji: form dan penolakan kredensial invalid. Login sukses hanya diverifikasi menggunakan akun Admin uji.")
    add_screenshot(doc, "TC002_PUBLIC_LOGIN_STEP01_PASS.png", "Gambar 2. Form login kosong; tidak ada kredensial pada bukti (TC002).")
    doc.add_heading("Daftar akun atau reset kata sandi", level=2)
    add_steps(doc, [
        "Registrasi Pembeli tersedia di /register; kata sandi minimal 8 karakter.",
        "Permintaan reset tersedia di /forgot-password.",
        "Ikuti petunjuk di layar. Pengiriman formulir, pembuatan akun, dan email reset belum diuji.",
    ])

    doc.add_heading("2. Admin", level=1)
    doc.add_paragraph(
        "Status: login Admin, dashboard, sidebar desktop/mobile, halaman read-only, "
        "dan logout diuji. Screenshot dashboard menutupi area data utama."
    )
    doc.add_heading("Masuk dan menggunakan navigasi", level=2)
    add_steps(doc, [
        "Buka /login dan masuk dengan kredensial Admin yang dikelola aman oleh tim.",
        "Di desktop, gunakan sidebar kiri untuk berpindah modul. Sidebar tetap menempel saat halaman digulir; bila daftar menu melampaui layar, area sidebar dapat digulir sendiri.",
        "Pada layar sempit, gunakan navigasi Admin versi mobile.",
        "Gunakan menu sesuai kebutuhan: Dashboard, Manajemen Pengguna, Validasi Produk, Manajemen Produk, Pesanan, Keuangan, Jasa Kirim, atau Pusat Bantuan.",
    ])
    add_screenshot(doc, "TC016_ADMIN_ADMIN_DASHBOARD_NAV_STEP02_PASS.png", "Gambar 3. Sidebar Admin setelah halaman digulir (TC016).")
    doc.add_heading("Halaman Admin yang diperiksa", level=2)
    doc.add_paragraph(
        "TC018 memeriksa respons halaman pengguna, validasi produk, produk, pesanan, "
        "keuangan, dan jasa kirim. Pemeriksaan dilakukan dengan membuka halaman saja; "
        "perubahan data, persetujuan produk, refund, ekspor, dan pengiriman pesan belum diuji."
    )
    doc.add_heading("Keluar", level=2)
    add_steps(doc, [
        "Pilih tombol Keluar pada dashboard.",
        "Setelah diarahkan ke login, akses dashboard memerlukan autentikasi kembali.",
    ])

    doc.add_heading("3. Pembeli", level=1)
    doc.add_paragraph(
        "Status: BELUM DIVERIFIKASI. Akun uji Pembeli tidak tersedia sehingga TC019 "
        "diblokir. Bagian ini bersumber dari discovery, bukan hasil browser."
    )
    doc.add_paragraph(
        "Discovery mencatat dashboard Pembeli, katalog produk, keranjang, checkout, "
        "pesanan, pusat bantuan, chat, dan profil. Akses route /dashboard/pembeli "
        "dan workflow bisnis belum dijalankan untuk role ini. Screenshot role Pembeli "
        "belum tersedia."
    )

    doc.add_heading("4. Penjual", level=1)
    doc.add_paragraph(
        "Status: BELUM DIVERIFIKASI. Akun uji Penjual tidak tersedia sehingga TC020 "
        "diblokir. Bagian ini bersumber dari discovery, bukan hasil browser."
    )
    doc.add_paragraph(
        "Discovery mencatat dashboard Penjual, produk dan stok, pesanan, transaksi, "
        "metode pembayaran, pusat bantuan, dan chat. Akses route /dashboard/penjual "
        "dan workflow bisnis belum dijalankan untuk role ini. Screenshot role Penjual "
        "belum tersedia."
    )

    doc.add_heading("5. Pemecahan masalah", level=1)
    doc.add_paragraph("Jika tidak dapat masuk, pastikan alamat email dan kata sandi benar dan akun aktif. Jangan mengirim kredensial melalui laporan atau screenshot.")
    doc.add_paragraph("Pengunjung yang membuka route terlindungi diarahkan ke halaman login. Akun dengan role yang tidak sesuai dapat menerima akses ditolak; hubungi Admin jika akses diperlukan.")
    doc.add_paragraph("Jika menu tidak terlihat pada mobile, gunakan navigasi mobile. Untuk isu yang berulang, catat route, role, waktu, dan screenshot yang tidak memuat data sensitif.")

    doc.save(REPORTS / "Website_User_Tutorial.docx")
    print("Generated reports/Website_User_Tutorial.docx.")


if __name__ == "__main__":
    main()
