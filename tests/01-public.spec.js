const { test, expect } = require('../lib/fixtures');
const { BASE_URL } = require('../lib/env');

test('TC001 Pengunjung membuka landing page', async ({ page, tc, evidence }) => {
  tc({
    module: 'MOD-00',
    feature: 'F35',
    featureName: 'LANDING_PAGE',
    requirement: 'REQ-F35',
    role: 'PUBLIC',
    type: 'Navigation',
    priority: 'Low',
    objective: 'Memastikan halaman publik tersedia',
    expected: 'Landing page dan tautan masuk/daftar tampil',
  });

  const response = await page.goto('/');
  expect(response.status()).toBe(200);
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('Kebaikan lokal dalam setiap sajian.');
  await expect(page.getByRole('link', { name: 'Daftar Akun' })).toHaveAttribute('href', `${BASE_URL}/register`);
  await expect(page.getByRole('link', { name: 'Masuk ke akun' })).toHaveAttribute('href', `${BASE_URL}/login`);
  await evidence.snap('Landing page untuk pengunjung');
});

test('TC002 Form login tersedia dengan field wajib', async ({ page, tc, evidence }) => {
  tc({
    module: 'MOD-01',
    feature: 'F01',
    featureName: 'LOGIN',
    requirement: 'REQ-F01',
    role: 'PUBLIC',
    type: 'UI, Validation',
    priority: 'Critical',
    objective: 'Memeriksa struktur form login tanpa mengirim data',
    expected: 'Email dan kata sandi wajib diisi; tautan daftar dan lupa kata sandi tersedia',
  });

  const response = await page.goto('/login');
  expect(response.status()).toBe(200);
  await expect(page).toHaveTitle('Masuk · Immortal Tahu');
  await expect(page.getByLabel('Email')).toHaveAttribute('required', '');
  await expect(page.locator('input[name="password"]')).toHaveAttribute('required', '');
  await expect(page.getByRole('link', { name: 'Lupa kata sandi?' })).toHaveAttribute('href', `${BASE_URL}/forgot-password`);
  await evidence.snap('Form login kosong; tidak ada kredensial yang diisikan');
});

test('TC003 Form registrasi pembeli menampilkan batas kata sandi', async ({ page, tc, evidence }) => {
  tc({
    module: 'MOD-01',
    feature: 'F02',
    featureName: 'REGISTRASI',
    requirement: 'REQ-F02',
    role: 'PUBLIC',
    type: 'UI, Validation',
    priority: 'High',
    objective: 'Memeriksa field registrasi tanpa membuat akun',
    expected: 'Form khusus pembeli tersedia dengan kata sandi minimum 8 karakter',
  });

  const response = await page.goto('/register');
  expect(response.status()).toBe(200);
  await expect(page.getByRole('heading', { name: 'Buat akun pembeli' })).toBeVisible();
  await expect(page.getByLabel('Nama lengkap')).toHaveAttribute('required', '');
  await expect(page.getByLabel('Email')).toHaveAttribute('required', '');
  await expect(page.locator('input[name="password"]')).toHaveAttribute('minlength', '8');
  await expect(page.locator('input[name="password_confirmation"]')).toHaveAttribute('minlength', '8');
  await evidence.snap('Form registrasi; tidak dikirim agar tidak membuat akun baru');
});

test('TC004 Form permintaan reset kata sandi tersedia', async ({ page, tc, evidence }) => {
  tc({
    module: 'MOD-01',
    feature: 'F04',
    featureName: 'RESET_PASSWORD_REQUEST',
    requirement: 'REQ-F04',
    role: 'PUBLIC',
    type: 'UI, Integration',
    priority: 'Medium',
    objective: 'Memeriksa halaman reset tanpa mengirim email',
    expected: 'Field email dan tombol kirim tautan reset tersedia',
  });

  const response = await page.goto('/forgot-password');
  expect(response.status()).toBe(200);
  await expect(page.getByRole('heading', { name: 'Lupa kata sandi?' })).toBeVisible();
  await expect(page.getByLabel('Email')).toHaveAttribute('required', '');
  await expect(page.getByRole('button', { name: 'Kirim tautan reset' })).toBeVisible();
  await evidence.snap('Form reset kata sandi; tidak ada email yang dikirim');
});

test('TC005 Login menolak kredensial tidak valid', async ({ page, tc, evidence }) => {
  tc({
    module: 'MOD-01',
    feature: 'F01',
    featureName: 'LOGIN_INVALID',
    requirement: 'QA002',
    role: 'PUBLIC',
    type: 'Negative, Authentication',
    priority: 'Critical',
    objective: 'Memastikan kredensial tidak valid tidak membuat sesi',
    expected: 'Pesan validasi tampil dan pengguna tetap berada di halaman login',
  });

  await page.goto('/login');
  await page.getByLabel('Email').fill('qa-invalid@example.invalid');
  await page.locator('input[name="password"]').fill('invalid-test-password');
  await page.getByRole('button', { name: 'Masuk ke dashboard' }).click();
  await expect(page).toHaveURL(/\/login$/);
  await expect(page.getByRole('alert')).toContainText('Email atau kata sandi tidak sesuai.');
  await evidence.snap('Kredensial tidak valid ditolak; kata sandi di-mask');
});

const guestProtectedRoutes = [
  ['/dashboard/admin', 'dashboard administrator'],
  ['/admin/pengguna', 'manajemen pengguna'],
  ['/admin/validasi-produk', 'validasi produk'],
  ['/admin/produk', 'manajemen produk admin'],
  ['/admin/pesanan', 'monitoring pesanan admin'],
  ['/admin/keuangan', 'laporan keuangan admin'],
  ['/admin/jasa-kirim', 'jasa kirim admin'],
  ['/admin/pusat-bantuan', 'pusat bantuan admin'],
  ['/dashboard/pembeli', 'dashboard pembeli'],
  ['/dashboard/penjual', 'dashboard penjual'],
];

for (const [index, [route, label]] of guestProtectedRoutes.entries()) {
  const testCaseId = `TC${String(index + 6).padStart(3, '0')}`;
  test(`${testCaseId} Pengunjung ditolak dari ${label}`, async ({ page, tc, evidence }) => {
    tc({
      module: 'MOD-ACCESS',
      feature: 'F01',
      featureName: 'GUEST_ACCESS_CONTROL',
      requirement: 'QA029',
      role: 'PUBLIC',
      type: 'Authorization',
      priority: 'Critical',
      objective: `Memastikan route ${route} memerlukan autentikasi`,
      expected: 'Pengunjung diarahkan ke halaman login',
    });

    await page.goto(route);
    await expect(page).toHaveURL(/\/login$/);
    await expect(page.getByRole('heading', { name: 'Selamat datang' })).toBeVisible();
    await evidence.snap(`Pengunjung diarahkan ke login dari ${route}`);
  });
}
