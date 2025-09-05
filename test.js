const { chromium } = require('playwright');
const nodemailer = require('nodemailer');

async function sendFailureEmail(error) {
  const transporter = nodemailer.createTransport({
    service: 'gmail',
    auth: {
      user: process.env.EMAIL_ADDRESS,   // set in GitHub Secrets
      pass: process.env.EMAIL_PASSWORD   // app password recommended
    }
  });

  const mailOptions = {
    from: process.env.EMAIL_ADDRESS,
    to: process.env.EMAIL_TO || process.env.EMAIL_ADDRESS,
    subject: 'Playwright Test Failed – BrooksRunning.com',
    text: `The weekly Playwright test failed:\n\n${error}`
  };

  await transporter.sendMail(mailOptions);
}

(async () => {
  let browser;
  try {
    browser = await chromium.launch({ headless: true }); // headless for CI
    const page = await browser.newPage();

    await page.goto('https://www.brooksrunning.com', { waitUntil: 'domcontentloaded' });

    const title = await page.title();
    if (!title.includes('Brooks')) throw new Error(`Title check failed: ${title}`);

    await page.click('span:has-text("Women")');
    await page.waitForTimeout(2000);

    console.log('✅ All tests passed');
  } catch (error) {
    console.error('❌ Test failed:', error);
    await sendFailureEmail(error);
    process.exit(1); // fail the workflow
  } finally {
    if (browser) await browser.close();
  }
})();
