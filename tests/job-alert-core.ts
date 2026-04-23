import fs from 'fs';
import nodemailer from 'nodemailer';

export function getNewJobs(oldFile: string, newFile: string) {
  if (!fs.existsSync(oldFile)) return [];

  const old = new Set(fs.readFileSync(oldFile, 'utf-8').split('\n'));
  const current = fs.readFileSync(newFile, 'utf-8').split('\n');

  return current.filter(line =>
    line && !old.has(line) && line !== 'Title,Link'
  );
}

export async function sendJobAlert(jobs: string[]) {
  if (jobs.length === 0) return;

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
    subject: '🚨 New Healthcare Jobs Found!',
    text: jobs.join('\n'),
  });

  console.log('📧 Job alert email sent');
}