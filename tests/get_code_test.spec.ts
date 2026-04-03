import { execSync } from 'child_process';
import path from 'path';

try {
  // Resolve the Python script path relative to this TS file
  const pythonScriptPath = path.join(__dirname, 'get_gmail_code.py');

  // Call the Python script and get its output
  const output = execSync(`python3 "${pythonScriptPath}"`, { stdio: 'pipe' })
  .toString()
  .trim();
  if (output) {
    console.log("✅ Python script ran successfully. Retrieved code:", output);
  } else {
    console.log("⚠️ Python script ran but did not return a code.");
  }
} catch (err) {
  console.error("❌ Failed to run Python script:", err);
}