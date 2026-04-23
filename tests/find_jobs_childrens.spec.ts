import { test, chromium } from '@playwright/test';
import fs from 'fs';
import path from 'path';
import nodemailer from 'nodemailer';

test('Seattle Children Resident jobs → CSV + alerts', async () => {
  test.setTimeout(120000);

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  const url =
    'https://careers.seattlechildrens.org/us/en/search-results?keywords=Resident';

  console.log('🌐 Navigating...');
  await page.goto(url);

  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(4000);

  const jobLinks = page.getByRole('link', {
    name: /Resident/i,
  });

  const count = await jobLinks.count();
  console.log(`✅ Found ${count} jobs`);

  const jobs: { title: string; link: string }[] = [];

  for (let i = 0; i < count; i++) {
    const el = jobLinks.nth(i);

    const title = (await el.innerText()).trim();
    let link = await el.getAttribute('href');

    if (link && !link.startsWith('http')) {
      link = `https://careers.seattlechildrens.org${link}`;
    }

    jobs.push({ title, link: link || '' });
  }

  // 📄 Save current CSV
  const filePath = path.resolve(
    __dirname,
    'seattle_childrens_jobs.csv'
  );

  const oldFilePath = path.resolve(
    __dirname,
    'seattle_childrens_jobs_old.csv'
  );

  const csv = [
    'Title,Link',
    ...jobs.map(j =>
      `"${j.title.replace(/"/g, '""')}","${j.link}"`
    ),
  ].join('\n');

  fs.writeFileSync(filePath, csv);

  // 🔥 COMPARE WITH OLD RUN
  let newJobs: string[] = [];

  if (fs.existsSync(oldFilePath)) {
    const old = new Set(
      fs.readFileSync(oldFilePath, 'utf-8').split('\n')
    );

    newJobs = csv
      .split('\n')
      .filter(line => !old.has(line) && line !== 'Title,Link');
  }

  console.log(`🚨 New jobs: ${newJobs.length}`);

  // 📧 EMAIL ALERT
  if (newJobs.length > 0) {
    const transporter = nodemailer.createTransport({
      service: 'gmail',
      auth: {
        user: process.env.EMAIL_USER!,
        pass: process.env.EMAIL_APP_PASSWORD!,
      },
    });

    await transporter.sendMail({
      from: process.env.EMAIL_USER!,
      to: process.env.EMAIL_USER!,
      subject:
        '🚨 New Seattle Children RN Resident Jobs!',
      text: newJobs.join('\n'),
    });

    console.log('📧 Email sent');
  }

  // 💾 update baseline
  fs.copyFileSync(filePath, oldFilePath);

  await browser.close();
});