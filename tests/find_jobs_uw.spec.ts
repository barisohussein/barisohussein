import { test, chromium } from '@playwright/test';
import fs from 'fs';
import path from 'path';
import nodemailer from 'nodemailer';

test('UW Resident jobs → CSV + alerts', async () => {
  test.setTimeout(180000);

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  await page.goto(
    'https://wd5.myworkdaysite.com/recruiting/uw/UWHires?q=RN+resident'
  );

  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(4000);

  const jobs: { title: string; link: string }[] = [];

  while (true) {
    const jobLinks = page.getByRole('link', { name: /Nurse/i });

    const count = await jobLinks.count();
    console.log(`Found ${count} jobs`);

    for (let i = 0; i < count; i++) {
      const el = jobLinks.nth(i);

      const title = (await el.innerText()).trim();
      let link = await el.getAttribute('href');

      if (link && !link.startsWith('http')) {
        link = `https://wd5.myworkdaysite.com${link}`;
      }

      jobs.push({ title, link: link || '' });
    }

    const nextBtn = page.getByRole('button', { name: /next/i });

    if (await nextBtn.isVisible()) {
      await nextBtn.click();
      await page.waitForTimeout(3000);
    } else {
      break;
    }
  }

  // 🧹 dedupe
  const uniqueJobs = Array.from(
    new Map(jobs.map(j => [j.link, j])).values()
  );

  console.log(`Total jobs: ${uniqueJobs.length}`);

  const filePath = path.resolve(__dirname, 'uw_jobs.csv');
  const oldFilePath = path.resolve(__dirname, 'uw_jobs_old.csv');

  const csv = [
    'Title,Link',
    ...uniqueJobs.map(j =>
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

  console.log(`🚨 New jobs found: ${newJobs.length}`);

  // 📧 EMAIL ALERT (same style as your LISA script)
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
      subject: '🚨 New UW Nursing Jobs Found!',
      text: newJobs.join('\n'),
    });

    console.log('📧 Email sent');
  }

  // 💾 update baseline
  fs.copyFileSync(filePath, oldFilePath);

  await browser.close();
});