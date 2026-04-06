import { test, expect, chromium } from '@playwright/test';
import { execSync } from 'child_process';
import path from 'path';
import nodemailer from 'nodemailer';


const lisaEmail = process.env.LISA_EMAIL!;
const lisaPassword = process.env.LISA_PASSWORD!;
const emailUser = process.env.EMAIL_USER!;
const emailPass = process.env.EMAIL_APP_PASSWORD!;


test('Login and check Claim A Shift links in headed mode', async () => {
    test.setTimeout(2000000); // 120 seconds

  const browser = await chromium.launch({
    headless: true, // show browser window
    slowMo: 1000,   // 1 second delay between actions for visibility
  });
  const context = await browser.newContext();
  const page = await context.newPage();

  // 1️⃣ Go to the login page
  await page.goto('https://lisa.aus.com/');

  // 2️⃣ Fill in email
  await page.getByRole('textbox', { name: 'Email' }).fill('barisohussein3@gmail.com');

  // 3️⃣ Fill in password
  await page.getByRole('textbox', { name: 'Password' }).fill(lisaPassword); 
  console.log('Pass entetred');

  // 4️⃣ Click Sign In and wait for navigation
  await Promise.all([
    page.getByRole('button', { name: 'Sign In' }).click(),
  ]);


  console.log('Sign in done');

    // Wait 10 seconds before next steps
    await page.waitForTimeout(20000);

    console.log('Wait done');

  // 4️⃣ Call Python script to get the code
  let code: string;
  try {
    // Resolve the Python script path relative to this TS file
    const pythonScriptPath = path.resolve(__dirname, 'get_gmail_code.py');
//const pythonScriptPath = '/Users/barisohussein/Desktop/barisohussein/barisohussein/tests/get_gmail_code.py'

    // Use python3 (macOS/Linux) to run the script
    const output = execSync(`python3 "${pythonScriptPath}"`, { stdio: 'pipe' })
      .toString()
      .trim();

    if (!output) throw new Error("No code retrieved from Gmail");

    code = output;
    console.log("✅ Retrieved code from Gmail:", code);
  } catch (err) {
    console.error("❌ Failed to get code from Python script:", err);
    await browser.close();
    return;
  }

  // 5️⃣ Fill in the code
  await page.locator('input').first().fill(code);
  console.log('Code filled in');
  console.log(code);

console.log('Code add done');

// Click Submit
await page.getByRole('button', { name: 'Submit' }).click();

// 8️⃣ Wait a bit to ensure shifts load
await page.waitForTimeout(5000);

// 9️⃣ Look for "Claim A Shift" buttons or text
const claimButtons = await page.locator('text=Claim A Shift').count();

console.log(`🔍 Found ${claimButtons} "Claim A Shift" items`);

if (claimButtons > 0) {
  console.log('✅ Shifts available! Sending email...');

  try {
    const transporter = nodemailer.createTransport({
      service: 'gmail',
      auth: {
        user: 'barisobrooks@gmail.com',
        pass: emailPass,
      },
    });

    const mailOptions = {
      from: 'barisobrooks@gmail.com',
      to: 'barisohussein3@gmail.com',
      subject: '🚨 LISA Shifts Available!',
      text: `There are ${claimButtons} shifts available. Log in to claim them.`,
    };

    await transporter.sendMail(mailOptions);
    console.log('✅ Email sent!');
  } catch (err) {
    console.error('❌ Failed to send email:', err);
  }
} else {
  console.log('⚠️ No shifts available.');
}
}

  // 8️⃣ Keep browser open to see result (optional)
  await page.pause(); // allows you to interact manually if needed

  await browser.close();
});
