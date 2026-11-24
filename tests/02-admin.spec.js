const { test, expect } = require('../lib/fixtures');
const { credentials, env } = require('../lib/env');

const hasBuyerCredentials = Boolean(env('BUYER_USER') && env('BUYER_PASS'));
const hasSellerCredentials = Boolean(env('SELLER_USER') && env('SELLER_PASS'));

async function loginAsAdmin(page) {
  await loginAsRole(page, 'ADMIN', '/dashboard/admin');
}

async function loginAsRole(page, role, destination) {
  const { user, pass } = credentials(role);
  await page.goto('/login');
  await page.getByLabel('Email').fill(user);
  await page.locator('input[name="password"]').fill(pass);
  await page.getByRole('button', { name: 'Masuk ke dashboard' }).click();
  await page.waitForURL(`**${destination}`);
}

test('TC016 Admin login, dashboard, dan sidebar desktop/mobile', async ({ page, tc, evidence }) => {
  tc({
    module: 'MOD-01',
    feature: 'F01,F38',
    featureName: 'ADMIN_DASHBOARD_NAV',
    requirement: 'QA001,REQ-F38',
    role: 'ADMIN',
    type: 'Positive, Authentication',
    priority: 'Critical',
    objective: 'Memastikan akun Admin uji dapat masuk',
    expected: 'Login mengarah ke Dashboard Admin; sidebar desktop sticky dan navigasi mobile tersedia',
  });

  await loginAsAdmin(page);
  await expect(page).toHaveTitle('Dashboard Admin · Immortal Tahu');
  await expect(page.getByRole('heading', { name: 'Ringkasan platform' })).toBeVisible();
  await evidence.snap('Dashboard Admin; area data pengguna dan identitas akun di-mask', {
    fullPage: false,
    mask: [page.locator('main'), page.locator('header div.text-right')],
  });
  const sidebar = page.locator('aside');
  await expect(sidebar).toBeVisible();

  const initialStyle = await sidebar.evaluate((element) => {
    const style = getComputedStyle(element);
    return {
      position: style.position,
      top: style.top,
      height: element.getBoundingClientRect().height,
      overflowY: style.overflowY,
      viewportHeight: window.innerHeight,
      documentHeight: document.documentElement.scrollHeight,
    };
  });
  expect(initialStyle.position).toBe('sticky');
  expect(initialStyle.top).toBe('0px');
  expect(initialStyle.height).toBe(initialStyle.viewportHeight);
  expect(initialStyle.overflowY).toBe('auto');
  expect(initialStyle.documentHeight).toBeGreaterThan(initialStyle.viewportHeight);

  await page.evaluate(() => window.scrollTo(0, document.documentElement.scrollHeight));
  await page.waitForTimeout(100);
  const sidebarTop = await sidebar.evaluate((element) => element.getBoundingClientRect().top);
  expect(sidebarTop).toBeGreaterThanOrEqual(-1);
  expect(sidebarTop).toBeLessThanOrEqual(1);
  await evidence.snap('Sidebar Admin tetap di sisi kiri setelah halaman digulir', {
    fullPage: false,
    mask: [page.locator('header'), page.locator('main')],
  });

  await page.setViewportSize({ width: 390, height: 844 });
  await expect(page.locator('aside')).toBeHidden();
  await expect(page.getByRole('navigation', { name: 'Navigasi admin' })).toBeVisible();
});

test('TC017 Dashboard role dan kontrol akses Admin', async ({ page, tc }) => {
  tc({
    module: 'MOD-ACCESS',
    feature: 'F39',
    featureName: 'ROLE_DASHBOARD_REDIRECT',
    requirement: 'REQ-F39,QA030',
    role: 'ADMIN',
    type: 'Navigation, Authorization',
    priority: 'Critical',
    objective: 'Memastikan pengarah dashboard bekerja dan role lain ditolak',
    expected: 'Admin diarahkan ke dashboard Admin; dashboard Pembeli/Penjual menghasilkan HTTP 403',
  });

  await loginAsAdmin(page);
  await page.goto('/dashboard');
  await expect(page).toHaveURL(/\/dashboard\/admin$/);
  for (const route of ['/dashboard/pembeli', '/dashboard/penjual']) {
    const response = await page.goto(route);
    expect(response.status(), `Akses Admin ke ${route}`).toBe(403);
  }
});

test('TC018 Halaman Admin read-only dapat dibuka dan sesi dapat diakhiri', async ({ page, tc, evidence }) => {
  tc({
    module: 'MOD-10',
    feature: 'F31,F28,F29,F30,F32,F33,F34,F03',
    featureName: 'ADMIN_READ_ONLY_PAGES',
    requirement: 'QA029,REQ-F03',
    role: 'ADMIN',
    type: 'Navigation, Authorization',
    priority: 'High',
    objective: 'Memastikan halaman modul Admin utama dapat diakses akun Admin',
    expected: 'Halaman pengguna, produk, pesanan, keuangan, dan jasa kirim merespons HTTP 200',
    note: 'Hanya GET; aksi yang mengubah data tidak dijalankan',
  });

  const pages = [
    ['/admin/pengguna', 'Manajemen Pengguna'],
    ['/admin/validasi-produk', 'Validasi Produk'],
    ['/admin/produk', 'Master Produk & Stok'],
    ['/admin/pesanan', 'Monitoring Pesanan'],
    ['/admin/keuangan', 'Audit Keuangan'],
    ['/admin/jasa-kirim', 'Kelola Jasa Kirim'],
  ];

  await loginAsAdmin(page);
  for (const [route, title] of pages) {
    const response = await page.goto(route);
    expect(response.status(), `HTTP status ${route}`).toBe(200);
    await expect(page).toHaveTitle(`${title} · Immortal Tahu`);
  }
  await page.getByRole('button', { name: 'Keluar' }).click();
  await expect(page).toHaveURL(/\/login$/);
  await page.goto('/dashboard/admin');
  await expect(page).toHaveURL(/\/login$/);
  await evidence.snap('Sesi Admin berakhir setelah logout');
});

test('TC019 Dashboard Pembeli menunggu akun uji', async ({ page, tc }) => {
  tc({
    module: 'MOD-03',
    feature: 'F07-F16,F36',
    featureName: 'BUYER_WORKFLOWS',
    requirement: 'REQ-F07—REQ-F16,REQ-F36',
    role: 'BUYER',
    type: 'Functional, Workflow',
    priority: 'High',
    objective: 'Memastikan dashboard Pembeli tersedia untuk akun uji',
    expected: 'Login Pembeli berhasil dan dashboard Pembeli tampil',
  });

  test.skip(!hasBuyerCredentials, 'BLOCKED: BUYER_USER/BUYER_PASS belum tersedia di QA/.env.');
  await loginAsRole(page, 'BUYER', '/dashboard/pembeli');
  await expect(page).toHaveTitle('Beranda · Immortal Tahu');
  await expect(page.getByRole('heading', { name: /Selamat datang/ })).toBeVisible();
});

test('TC020 Dashboard Penjual menunggu akun uji', async ({ page, tc }) => {
  tc({
    module: 'MOD-05',
    feature: 'F17-F25,F37',
    featureName: 'SELLER_WORKFLOWS',
    requirement: 'REQ-F17—REQ-F25,REQ-F37',
    role: 'SELLER',
    type: 'Functional, Workflow',
    priority: 'High',
    objective: 'Memastikan dashboard Penjual tersedia untuk akun uji',
    expected: 'Login Penjual berhasil dan dashboard Penjual tampil',
  });

  test.skip(!hasSellerCredentials, 'BLOCKED: SELLER_USER/SELLER_PASS belum tersedia di QA/.env.');
  await loginAsRole(page, 'SELLER', '/dashboard/penjual');
  await expect(page).toHaveTitle('Dashboard Penjual · Immortal Tahu');
  await expect(page.getByRole('heading', { name: /Halo,/ })).toBeVisible();
});
