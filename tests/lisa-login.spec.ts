import { test, expect, chromium } from '@playwright/test';
import { execSync } from 'child_process';
import path from 'path';
import nodemailer from 'nodemailer';

const lisaEmail = process.env.LISA_EMAIL!;
const lisaPassword = process.env.LISA_PASSWORD!;
const emailUser = process.env.EMAIL_USER!;
const emailPass = process.env.EMAIL_APP_PASSWORD!;

test('Login and check shift availability', async () => {
  test.setTimeout(2000000);

  const browser = await chromium.launch({
    headless: true,
    slowMo: 500,
  });

  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // 1️⃣ Go to login page
    await page.goto('https://lisa.aus.com/');

    // 2️⃣ Fill login
    await page.getByRole('textbox', { name: 'Email' }).fill(lisaEmail);
    await page.getByRole('textbox', { name: 'Password' }).fill(lisaPassword);

    // 3️⃣ Click sign in and wait for navigation
    await Promise.all([
      page.waitForNavigation({ waitUntil: 'networkidle' }),
      page.getByRole('button', { name: 'Sign In' }).click(),
    ]);

    console.log('✅ Logged in');

    // 4️⃣ Wait for dashboard to stabilize
    await page.waitForLoadState('networkidle');

    // 5️⃣ Run Python script to get verification code
    let code: string;

    try {
      const pythonScriptPath = path.resolve(__dirname, 'get_gmail_code.py');

      const output = execSync(`python3 "${pythonScriptPath}"`, {
        stdio: 'pipe',
      })
        .toString()
        .trim();

      if (!output) throw new Error('No verification code received');

      code = output;
      console.log('✅ Code retrieved:', code);
    } catch (err) {
      console.error('❌ Failed to fetch code:', err);
      await browser.close();
      return;
    }

    // 6️⃣ Enter verification code
    await page.locator('input').first().fill(code);

    await page.getByRole('button', { name: 'Submit' }).click();

    console.log('✅ Verification complete');

    // 7️⃣ Go to shift page
    await page.goto('https://lisa.aus.com/my-shift-offers');
    await page.waitForLoadState('networkidle');

    // 8️⃣ Check for "no shifts" message
    const noShiftsCount = await page
      .locator('text=There are no remaining shift offers.')
      .count();

    const shiftsAvailable = noShiftsCount === 0;

    console.log('Shift message count:', noShiftsCount);

    if (!shiftsAvailable) {
      console.log('❌ No shifts available.');
      await browser.close();
      return;
    }

    console.log('🚨 Shifts available! Sending email...');

    // 9️⃣ Send email alert
    try {
      const transporter = nodemailer.createTransport({
        service: 'gmail',
        auth: {
          user: emailUser,
          pass: emailPass,
        },
      });

      await transporter.sendMail({
        from: emailUser,
        to: lisaEmail,
        subject: '🚨 LISA Shifts Available!',
        text: 'Shifts are available! Log in and claim them now.',
      });

      console.log('✅ Email sent successfully!');
    } catch (err) {
      console.error('❌ Email failed:', err);
    }

    // 10️⃣ Optional debug pause
    await page.pause();
  } catch (err) {
    console.error('❌ Script failed:', err);
  } finally {
    await browser.close();
  }
});
