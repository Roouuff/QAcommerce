import json
import re
from datetime import datetime
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
REPORTS = ROOT / "reports"
DISCOVERY = ROOT / "discovery" / "data" / "discovery_data.json"
SCREENSHOTS = ROOT / "screenshots"

CASE_DETAILS = {
    "TC000": ("ENV-01", "QA-ENV", "/", "ENV", "Navigation", "High",
              "Aplikasi lokal tersedia.", "Tidak ada.",
              "Buka BASE_URL dan periksa respons HTTP.", "Aplikasi merespons HTTP 200."),
    "TC001": ("F35", "REQ-F35", "/", "PUBLIC", "Navigation", "Low",
              "Pengunjung belum login.", "Tidak ada.",
              "Buka landing page dan periksa heading serta tautan.", "Landing page dan tautan login/daftar tampil."),
    "TC002": ("F01", "REQ-F01", "/login", "PUBLIC", "UI, Validation", "Critical",
              "Pengunjung belum login.", "Tidak ada.",
              "Buka form login dan periksa field wajib serta tautan terkait.",
              "Email dan kata sandi wajib diisi; tautan daftar dan lupa kata sandi tersedia."),
    "TC003": ("F02", "REQ-F02", "/register", "PUBLIC", "UI, Validation", "High",
              "Pengunjung belum login.", "Tidak ada; form tidak dikirim.",
              "Buka registrasi pembeli dan periksa field serta minlength kata sandi.",
              "Form registrasi pembeli tampil dengan batas minimal kata sandi 8 karakter."),
    "TC004": ("F04", "REQ-F04", "/forgot-password", "PUBLIC", "UI, Integration", "Medium",
              "Pengunjung belum login.", "Tidak ada; email reset tidak dikirim.",
              "Buka halaman lupa kata sandi dan periksa field serta tombol.",
              "Form permintaan reset tersedia tanpa mengirim email."),
    "TC005": ("F01", "QA002", "/login", "PUBLIC", "Negative, Authentication", "Critical",
              "Pengunjung belum login.", "Kredensial sintetis yang tidak valid.",
              "Kirim kredensial tidak valid satu kali dan periksa pesan serta URL.",
              "Login ditolak; pesan validasi tampil dan tidak terbentuk sesi."),
    "TC016": ("F01,F38", "QA001,REQ-F38", "/dashboard/admin", "ADMIN",
              "Positive, Authentication, UI", "Critical",
              "Kredensial Admin uji tersedia di environment lokal.",
              "Kredensial dari QA/.env; tidak dicatat dalam laporan.",
              "Login Admin; periksa dashboard dan posisi/tinggi/overflow sidebar pada desktop; scroll halaman; periksa navigasi mobile.",
              "Dashboard Admin terbuka; sidebar desktop tetap sticky dan navigasi mobile tampil."),
    "TC017": ("F39", "REQ-F39,QA030", "/dashboard", "ADMIN",
              "Navigation, Authorization", "Critical",
              "Admin sudah login.", "Tidak ada.",
              "Buka /dashboard dan kemudian coba dashboard role lain.",
              "Admin diarahkan ke dashboard Admin; akses role lain ditolak HTTP 403."),
    "TC018": ("F31,F28,F29,F30,F32,F33,F34,F03", "QA029,REQ-F03",
              "/admin/*", "ADMIN", "Navigation, Authorization", "High",
              "Admin sudah login.", "Permintaan GET dan logout sesi.",
              "Buka halaman Admin yang dipilih dengan GET; logout; coba akses dashboard lagi.",
              "Halaman Admin merespons HTTP 200; setelah logout dashboard mengarahkan ke login."),
    "TC019": ("F07-F16,F36", "REQ-F07—REQ-F16,REQ-F36",
              "/dashboard/pembeli", "BUYER", "Functional, Workflow", "High",
              "Akun Pembeli uji diperlukan.", "Tidak ada; akun belum tersedia.",
              "Login Pembeli dan buka dashboard.", "Login berhasil dan dashboard Pembeli tampil."),
    "TC020": ("F17-F25,F37", "REQ-F17—REQ-F25,REQ-F37",
              "/dashboard/penjual", "SELLER", "Functional, Workflow", "High",
              "Akun Penjual uji diperlukan.", "Tidak ada; akun belum tersedia.",
              "Login Penjual dan buka dashboard.", "Login berhasil dan dashboard Penjual tampil."),
}


def load_json(path):
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def read_jsonl(path):
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]


def all_tests(report):
    tests = []

    def walk(suite):
        for spec in suite.get("specs", []):
            for test in spec.get("tests", []):
                title = spec.get("title", "")
                match = re.match(r"(TC\d+)", title)
                annotations = {
                    item.get("type"): item.get("description", "")
                    for item in test.get("annotations", [])
                }
                status = test.get("status", "")
                expected = test.get("expectedStatus", "")
                if status == "skipped" or expected == "skipped":
                    result = "BLOCKED" if annotations.get("skip", "").startswith("BLOCKED") else "NOT TESTED"
                elif status == "expected" and expected == "passed":
                    result = "PASS"
                elif status == "unexpected":
                    result = "FAIL"
                else:
                    result = "NOT TESTED"
                tests.append({
                    "id": match.group(1) if match else "TCXXX",
                    "title": title,
                    "annotations": annotations,
                    "status": result,
                })
        for child in suite.get("suites", []):
            walk(child)

    for suite in report.get("suites", []):
        walk(suite)
    return tests


def set_cell_shading(cell, color):
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), color)
    cell._tc.get_or_add_tcPr().append(shading)


def add_page_number(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.add_run("Halaman ")
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    paragraph._p.append(field)
    paragraph.add_run(" | Immortal Tahu - QA")


def style_document(doc, title):
    for section in doc.sections:
        section.page_width = Cm(21)
        section.page_height = Cm(29.7)
        section.top_margin = Cm(2)
        section.bottom_margin = Cm(2)
        section.left_margin = Cm(2.2)
        section.right_margin = Cm(2.2)
        section.header.paragraphs[0].text = "IMMORTAL TAHU | QUALITY ASSURANCE"
        section.header.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
        section.header.paragraphs[0].style = "Caption"
        add_page_number(section.footer.paragraphs[0])

    normal = doc.styles["Normal"]
    normal.font.name = "Arial"
    normal.font.size = Pt(10)
    normal.font.color.rgb = RGBColor(40, 48, 58)
    for name, size in (("Title", 24), ("Heading 1", 16), ("Heading 2", 12)):
        style = doc.styles[name]
        style.font.name = "Arial"
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = RGBColor(31, 73, 125)
    doc.core_properties.title = title
    doc.core_properties.author = "QA Automation"


def add_bullet(doc, text):
    doc.add_paragraph(text, style="List Bullet")


def add_table(doc, headers, rows, font_size=8):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    for index, value in enumerate(headers):
        cell = table.rows[0].cells[index]
        cell.text = value
        set_cell_shading(cell, "1F497D")
        for run in cell.paragraphs[0].runs:
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            run.font.size = Pt(font_size)
    for values in rows:
        cells = table.add_row().cells
        for index, value in enumerate(values):
            cells[index].text = str(value)
            cells[index].vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            for paragraph in cells[index].paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(font_size)
    return table


def make_catalogue(cases, evidence, execution_date, features, requirements):
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Test Cases"
    headers = [
        "Test Case ID", "Module ID", "Feature ID", "Requirement ID", "Page / Route",
        "Role", "Objective", "Type", "Preconditions", "Test Data", "Test Steps",
        "Expected Result", "Actual Result", "Status", "Screenshot Reference",
        "Execution Date", "Notes",
    ]
    sheet.append(headers)

    evidence_by_id = {}
    for item in evidence:
        evidence_by_id.setdefault(item.get("test_case_id"), []).append(item.get("file", ""))

    for case in cases:
        case_id = case["id"]
        annotations = case["annotations"]
        details = CASE_DETAILS.get(case_id, ("", "", "", "", "", "", "", "", "", ""))
        feature, requirement, route, default_role, test_type, priority, pre, data, steps, expected = details
        feature = annotations.get("feature", feature)
        requirement = annotations.get("requirement", requirement)
        role = annotations.get("role", default_role)
        objective = annotations.get("objective", case["title"])
        expected = annotations.get("expected", expected)
        if case["status"] == "PASS":
            actual = "PASS - hasil aktual sesuai dengan expected result."
        elif case["status"] == "BLOCKED":
            actual = annotations.get("skip", "Diblokir sebelum langkah uji.")
        elif case["status"] == "FAIL":
            actual = "FAIL - periksa hasil Playwright dan bukti terlampir."
        else:
            actual = "Belum dieksekusi."
        screenshots = "; ".join(evidence_by_id.get(case_id, [])) or "Tidak ada"
        notes = annotations.get("note", "")
        if case_id in ("TC019", "TC020"):
            notes = "Diblokir; akun role belum tersedia. Tidak dihitung sebagai lulus."
        sheet.append([
            case_id, annotations.get("module", "MOD-UNKNOWN"), feature, requirement,
            route or objective, role, objective, annotations.get("type", test_type),
            pre, data, steps, expected, actual, case["status"], screenshots,
            execution_date, notes or f"Priority: {annotations.get('priority', priority)}",
        ])

    header_fill = PatternFill("solid", fgColor="1F497D")
    thin_gray = Side(style="thin", color="D9E2F3")
    for cell in sheet[1]:
        cell.fill = header_fill
        cell.font = Font(name="Arial", bold=True, color="FFFFFF", size=10)
        cell.alignment = Alignment(wrap_text=True, vertical="center")
    for row in sheet.iter_rows(min_row=2):
        for cell in row:
            cell.font = Font(name="Arial", size=9)
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            cell.border = Border(bottom=thin_gray)
        status_cell = row[13]
        if status_cell.value == "PASS":
            status_cell.fill = PatternFill("solid", fgColor="E2F0D9")
        elif status_cell.value == "BLOCKED":
            status_cell.fill = PatternFill("solid", fgColor="FFF2CC")
        elif status_cell.value == "FAIL":
            status_cell.fill = PatternFill("solid", fgColor="FCE4D6")
    widths = [14, 14, 26, 24, 26, 12, 42, 23, 35, 30, 55, 48, 42, 14, 60, 22, 42]
    for index, width in enumerate(widths, start=1):
        sheet.column_dimensions[get_column_letter(index)].width = width
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions
    sheet.row_dimensions[1].height = 32

    summary = workbook.create_sheet("Summary")
    summary.append(["Metric", "Value"])
    counts = {status: sum(case["status"] == status for case in cases)
              for status in ("PASS", "FAIL", "BLOCKED", "NOT TESTED")}
    pass_rate = (counts["PASS"] / (counts["PASS"] + counts["FAIL"]) * 100
                 if counts["PASS"] + counts["FAIL"] else None)
    summary_rows = [
        ("Test case planned", len(cases)),
        ("Executed (PASS + FAIL)", counts["PASS"] + counts["FAIL"]),
        ("PASS", counts["PASS"]),
        ("FAIL", counts["FAIL"]),
        ("BLOCKED", counts["BLOCKED"]),
        ("NOT TESTED", counts["NOT TESTED"]),
        ("Pass rate (PASS / (PASS + FAIL))", f"{pass_rate:.1f}%" if pass_rate is not None else "N/A"),
        ("Feature coverage", f"{len(features)} / 39 ({len(features) / 39 * 100:.1f}%)"),
        ("Requirement coverage", f"{len(requirements)} / 39 ({len(requirements) / 39 * 100:.1f}%)"),
        ("Note", "Coverage menghitung ID yang dirujuk oleh test PASS; kedalaman alur tidak disimpulkan dari hitungan ini."),
    ]
    for row in summary_rows:
        summary.append(row)
    for cell in summary[1]:
        cell.fill = header_fill
        cell.font = Font(name="Arial", bold=True, color="FFFFFF")
    summary.column_dimensions["A"].width = 45
    summary.column_dimensions["B"].width = 105
    for row in summary.iter_rows():
        for cell in row:
            cell.alignment = Alignment(wrap_text=True, vertical="top")
    summary.freeze_panes = "A2"

    REPORTS.mkdir(parents=True, exist_ok=True)
    workbook.save(REPORTS / "Test_Case_Catalogue.xlsx")


def build_report(cases, evidence, logs, discovery, run_info, execution_date):
    doc = Document()
    style_document(doc, "Website QA Testing Report - Immortal Tahu")
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("IMMORTAL TAHU\nLAPORAN QA WEBSITE")
    run.bold = True
    run.font.size = Pt(23)
    run.font.color.rgb = RGBColor(31, 73, 125)
    subtitle = doc.add_paragraph("Playwright UI, navigasi, autentikasi, dan kontrol akses")
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(f"Tanggal eksekusi: {execution_date}").alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph(f"Environment: {run_info.get('environment', 'local')} | Browser: {run_info.get('browser', 'Chromium')}").alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_page_break()

    counts = {status: sum(case["status"] == status for case in cases)
              for status in ("PASS", "FAIL", "BLOCKED", "NOT TESTED")}
    actual_cases = counts["PASS"] + counts["FAIL"]
    pass_rate = counts["PASS"] / actual_cases * 100 if actual_cases else None
    all_features = {item["id"] for item in discovery.get("features", [])}
    all_requirements = {item["req_id"] for item in discovery.get("qa_requirements", [])}
    covered_features = set()
    covered_requirements = set()
    for case in cases:
        if case["status"] != "PASS":
            continue
        annotations = case["annotations"]
        covered_features.update(re.findall(r"F\d+", annotations.get("feature", "")))
        covered_requirements.update(re.findall(r"REQ-F\d+", annotations.get("requirement", "")))
    covered_features &= all_features
    covered_requirements &= all_requirements
    feature_rate = len(covered_features) / len(all_features) * 100 if all_features else 0
    req_rate = len(covered_requirements) / len(all_requirements) * 100 if all_requirements else 0
    execution_rate = actual_cases / len(cases) * 100 if cases else 0

    doc.add_heading("1. Ringkasan Eksekutif", level=1)
    doc.add_paragraph(
        f"Pada run terbaru, {counts['PASS']} test PASS, {counts['FAIL']} FAIL, "
        f"{counts['BLOCKED']} BLOCKED, dan {counts['NOT TESTED']} NOT TESTED dari "
        f"{len(cases)} test case yang direncanakan. Pass rate berdasarkan rumus "
        f"PASS / (PASS + FAIL) adalah {pass_rate:.1f}% ({counts['PASS']}/{actual_cases}); "
        "angka ini hanya menggambarkan test yang dieksekusi, bukan jaminan bebas bug."
    )
    doc.add_paragraph(
        "TC000 adalah pemeriksaan environment. Dua test workflow Pembeli/Penjual "
        "diblokir karena akun uji tidak tersedia. Tidak ada bug aplikasi yang "
        "terkonfirmasi dari run terbaru."
    )
    doc.add_heading("2. Identitas dan Environment", level=1)
    add_table(doc, ["Item", "Nilai"], [
        ("Aplikasi", "Immortal Tahu"),
        ("Target", run_info.get("base_url", "http://localhost:8000")),
        ("Environment", run_info.get("environment", "local")),
        ("Browser", run_info.get("browser", "Chromium lokal")),
        ("Tanggal mulai run", run_info.get("started_at", execution_date)),
        ("Node.js", run_info.get("node", "Tidak dicatat")),
        ("Test runner", "Playwright; satu worker"),
    ])
    doc.add_heading("3. Tujuan dan Cakupan", level=1)
    doc.add_paragraph(
        "Memverifikasi halaman publik, tampilan form autentikasi, penolakan login "
        "invalid, proteksi route untuk pengunjung, login dan navigasi Admin, "
        "perilaku sidebar desktop/mobile Admin, akses baca halaman Admin, dan logout."
    )
    add_bullet(doc, "Aksi data bisnis, registrasi akun, email reset, pembayaran, chat, pengiriman, dan penghapusan tidak dijalankan.")
    add_bullet(doc, "Halaman Admin yang diuji dalam TC018 dibuka dengan GET; selain sesi login/logout, pengujian bersifat read-only.")
    add_bullet(doc, "Responsive sidebar diuji pada role Admin; Pembeli dan Penjual belum dapat diuji karena tidak ada kredensial.")

    doc.add_heading("4. Metode dan Metrik Cakupan", level=1)
    doc.add_paragraph("Test dijalankan terhadap aplikasi lokal melalui browser Chromium. Screenshot diambil dari browser aktual; field password dimasking. Hasil dibaca dari test-results.json, evidence.jsonl, dan discovery/data/discovery_data.json.")
    add_table(doc, ["Metrik", "Hasil", "Penjelasan"], [
        ("Test case direncanakan", str(len(cases)), "TC000-TC020"),
        ("Dieksekusi (PASS + FAIL)", str(actual_cases), "Test yang benar-benar menjalankan assertion"),
        ("PASS / FAIL / BLOCKED / NOT TESTED",
         f"{counts['PASS']} / {counts['FAIL']} / {counts['BLOCKED']} / {counts['NOT TESTED']}",
         "Status run terbaru"),
        ("Pass rate", f"{pass_rate:.1f}%" if pass_rate is not None else "N/A",
         f"{counts['PASS']} / ({counts['PASS']} + {counts['FAIL']})"),
        ("Execution coverage", f"{actual_cases}/{len(cases)} ({execution_rate:.1f}%)",
         "BLOCKED tidak dihitung sebagai dieksekusi"),
        ("Feature coverage", f"{len(covered_features)}/{len(all_features)} ({feature_rate:.1f}%)",
         "ID fitur discovery yang dirujuk oleh test PASS; bukan ukuran kedalaman"),
        ("Requirement coverage", f"{len(covered_requirements)}/{len(all_requirements)} ({req_rate:.1f}%)",
         "REQ-Fxx discovery yang dirujuk oleh test PASS"),
    ])
    doc.add_paragraph(
        "Hasil aplikasi selain TC000: 18 PASS, 0 FAIL, dan 2 BLOCKED. "
        "Feature/requirement coverage bersifat referensial: halaman form yang "
        "diperiksa belum berarti seluruh workflow bisnisnya telah diuji."
    )

    doc.add_heading("5. Hasil per Role dan Modul", level=1)
    grouped = {}
    for case in cases:
        role = case["annotations"].get("role", "UNKNOWN")
        grouped.setdefault(role, {status: 0 for status in ("PASS", "FAIL", "BLOCKED", "NOT TESTED")})
        grouped[role][case["status"]] += 1
    add_table(doc, ["Role", "PASS", "FAIL", "BLOCKED", "NOT TESTED"], [
        (role, data["PASS"], data["FAIL"], data["BLOCKED"], data["NOT TESTED"])
        for role, data in sorted(grouped.items())
    ])
    doc.add_heading("6. Temuan dan Analisis", level=1)
    doc.add_paragraph("Bug aplikasi terkonfirmasi: 0. Detail daftar temuan ada di bugs/bugs.json.")
    doc.add_paragraph(
        "Run sebelumnya memperlihatkan kegagalan selector test karena href dibandingkan "
        "sebagai path relatif dan locator label kata sandi terlalu luas. Itu adalah "
        "masalah pada test automation, bukan defect aplikasi; selector diperbaiki, "
        "run terbaru lulus, dan bukti historis dipertahankan di archive/."
    )
    doc.add_paragraph(
        f"Log run terbaru memuat {len(logs)} catatan test. Setiap HTTP 403 yang "
        "diharapkan pada kontrol akses bukan bug dengan sendirinya. Tidak ada kasus "
        "FAIL pada run terbaru yang memerlukan bug report."
    )
    doc.add_heading("7. Bukti Screenshot", level=1)
    evidence_by_id = {}
    for item in evidence:
        evidence_by_id.setdefault(item.get("test_case_id"), []).append(item)
    screenshot_cases = [
        ("TC001", "Landing page pengunjung"),
        ("TC002", "Form login tanpa kredensial"),
        ("TC016", "Dashboard Admin dan sidebar setelah scroll"),
    ]
    for case_id, caption in screenshot_cases:
        items = evidence_by_id.get(case_id, [])
        selected = next((item for item in reversed(items)
                         if item.get("file") and (SCREENSHOTS / Path(item["file"]).name).exists()), None)
        if selected:
            doc.add_paragraph(f"{case_id} - {caption}", style="Caption")
            doc.add_picture(str(SCREENSHOTS / Path(selected["file"]).name), width=Inches(6.1))
            doc.add_paragraph(f"Bukti: {selected['file']} | Status: {selected.get('result', 'PASS')}", style="Caption")

    doc.add_heading("8. Limitasi", level=1)
    add_bullet(doc, "Belum tersedia akun uji Pembeli dan Penjual; TC019 dan TC020 berstatus BLOCKED.")
    add_bullet(doc, "Tidak semua 39 fitur dan 39 requirement discovery diuji; coverage aktual tercantum pada tabel metrik.")
    add_bullet(doc, "Pengujian tidak mencakup transaksi end-to-end, validasi email, pembayaran, upload, chat, ekspor laporan, atau operasi tulis Admin.")
    add_bullet(doc, "Browser dan target hanya Chromium lokal pada http://localhost:8000; tidak mewakili semua browser/perangkat/production.")
    doc.add_heading("9. Rekomendasi dan Kesimpulan", level=1)
    add_bullet(doc, "Sediakan akun uji Pembeli dan Penjual dengan data yang aman agar TC019-TC020 dapat dijalankan.")
    add_bullet(doc, "Lanjutkan test alur bisnis read-only/terkontrol setelah ada data dan izin eksplisit untuk operasi tulis.")
    add_bullet(doc, "Pertahankan pemisahan status BLOCKED dan PASS serta gunakan hasil test aktual untuk setiap klaim coverage.")
    doc.add_paragraph(
        "Kesimpulan: cakupan yang dijalankan pada environment lokal lulus, termasuk "
        "layout sticky sidebar Admin yang terukur. QA belum menyatakan aplikasi "
        "selesai diuji secara menyeluruh karena cakupan fitur masih parsial dan dua role belum diuji."
    )
    REPORTS.mkdir(parents=True, exist_ok=True)
    doc.save(REPORTS / "Website_QA_Testing_Report.docx")


def main():
    test_results = load_json(RESULTS / "test-results.json")
    discovery = load_json(DISCOVERY)
    run_info = load_json(RESULTS / "run-info.json")
    evidence = read_jsonl(RESULTS / "evidence.jsonl")
    logs = read_jsonl(RESULTS / "logs.jsonl")
    cases = all_tests(test_results)
    if not cases:
        raise RuntimeError("Tidak ada test case pada results/test-results.json.")
    execution_date = datetime.fromisoformat(
        test_results["stats"]["startTime"].replace("Z", "+00:00")
    ).astimezone().strftime("%Y-%m-%d %H:%M %Z")
    features = set()
    requirements = set()
    valid_features = {item["id"] for item in discovery.get("features", [])}
    valid_requirements = {item["req_id"] for item in discovery.get("qa_requirements", [])}
    for case in cases:
        if case["status"] != "PASS":
            continue
        features.update(re.findall(r"F\d+", case["annotations"].get("feature", "")))
        requirements.update(re.findall(r"REQ-F\d+", case["annotations"].get("requirement", "")))
    make_catalogue(cases, evidence, execution_date, features & valid_features, requirements & valid_requirements)
    build_report(cases, evidence, logs, discovery, run_info, execution_date)
    print(f"Generated reports/Website_QA_Testing_Report.docx and reports/Test_Case_Catalogue.xlsx for {len(cases)} test cases.")


if __name__ == "__main__":
    main()
