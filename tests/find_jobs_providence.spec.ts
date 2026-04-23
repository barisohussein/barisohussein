import { test, chromium } from '@playwright/test';
import fs from 'fs';
import path from 'path';
import nodemailer from 'nodemailer';

test('Scrape RN Resident jobs + alerts', async () => {
  test.setTimeout(120000);

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  const url =
    'https://providenceswedish.jobs/jobs/?q=RN+Resident';

  await page.goto(url);
  await page.waitForLoadState('networkidle');

  const jobLinks = page.getByRole('link', {
    name: /RN Resident/i,
  });

  const count = await jobLinks.count();
  console.log(`✅ Found ${count} jobs`);

  const jobs: { title: string; link: string }[] = [];

  for (let i = 0; i < count; i++) {
    const el = jobLinks.nth(i);

    const title = (await el.innerText()).trim();
    let link = await el.getAttribute('href');

    if (link && !link.startsWith('http')) {
      link = `https://providenceswedish.jobs${link}`;
    }

    jobs.push({ title, link: link || '' });
  }

  // 📄 Save current CSV
  const filePath = path.resolve(__dirname, 'rn_resident_jobs.csv');
  const oldFilePath = path.resolve(__dirname, 'rn_resident_jobs_old.csv');

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

  // 📧 EMAIL ALERT (same pattern as your LISA script)
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
      subject: '🚨 New Providence RN Resident Jobs!',
      text: newJobs.join('\n'),
    });

    console.log('📧 Email sent');
  }

  // 💾 update baseline
  fs.copyFileSync(filePath, oldFilePath);

  await browser.close();
});