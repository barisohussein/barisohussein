# 🚀 Quick Start Guide

## Your Upgraded System Health Dashboard is Ready!

This guide will help you get your new dashboard up and running in minutes.

## 📁 What You Have

```
brooks-system-health-dashboard/
├── docs/                      # ← Open this folder in your browser!
│   ├── index.html            # Main dashboard
│   ├── styles.css            # Styling
│   ├── app.js                # Logic
│   └── data/
│       └── system_health.json
├── scripts/
│   └── healthCheck.js        # Health monitoring script
├── .github/
│   └── workflows/
│       └── health.yml        # Auto-deployment workflow
├── README.md                 # Full documentation
├── UPGRADE.md                # Before/after comparison
└── package.json
```

## ⚡ View the Dashboard (3 Options)

### Option 1: Direct File Open (Quickest)
1. Navigate to `docs/index.html`
2. Double-click to open in your browser
3. Done! 🎉

### Option 2: Local Server (Recommended)
```bash
cd brooks-system-health-dashboard
npx serve docs
# Opens at http://localhost:3000
```

### Option 3: Python Server
```bash
cd brooks-system-health-dashboard
python3 -m http.server 8000 --directory docs
# Opens at http://localhost:8000
```

## 🔧 Configure Your Systems

Edit `scripts/healthCheck.js` to add your real endpoints:

```javascript
const CONFIG = {
    endpoints: [
        {
            id: 'sys-001',
            name: 'Your API Name',          // ← Change this
            type: 'API',
            url: 'https://your-api.com/health', // ← Change this
            method: 'GET',
            timeout: 5000,
            expectedStatus: 200
        },
        // Add more systems...
    ]
};
```

## 🤖 Set Up Automation

### GitHub Pages (Recommended)
1. Create a new GitHub repo
2. Upload this folder
3. Go to Settings → Pages
4. Source: "Deploy from a branch"
5. Branch: main, Folder: /docs
6. Save and wait ~2 minutes
7. Your dashboard is now live at `https://username.github.io/repo-name`

The GitHub Action will:
- ✅ Run health checks every 5 minutes
- ✅ Update your dashboard automatically
- ✅ Keep historical data

## 🎯 Key Features

### Dashboard Features
- **Card Grid**: Click any system card for details
- **Drawer Panel**: Slides in from the right (like React apps!)
- **Live Charts**: 30-minute latency trends
- **Auto Refresh**: Click the refresh button
- **Status Summary**: Top header shows overall health

### Keyboard Shortcuts
- `ESC`: Close drawer panel
- `Click outside`: Close drawer

### Status Colors
- 🟢 **Green (Healthy)**: Latency < 100ms
- 🟡 **Yellow (Degraded)**: Latency 100-500ms
- 🔴 **Red (Down)**: Latency > 500ms or offline

## 📊 Understanding the Data

### system_health.json Structure
```json
{
  "id": "sys-001",
  "name": "API Gateway",
  "status": "healthy",          // healthy | degraded | down
  "latency": 45.3,              // milliseconds
  "availability": 99.98,        // percentage
  "performanceData": [...],     // Last 30 data points
  "incidents": [...]            // Recent issues
}
```

## 🔄 Running Health Checks

### Manual Check
```bash
cd brooks-system-health-dashboard
node scripts/healthCheck.js
```

This will:
1. Check all configured endpoints
2. Update `docs/data/system_health.json`
3. Print a summary to console

### Automated (with GitHub Actions)
Once pushed to GitHub, it runs automatically every 5 minutes!

## 🎨 Customization

### Change Colors
Edit `docs/styles.css`:
```css
/* Around line 10 */
:root {
    --primary-color: #3b82f6;    /* Blue */
    --success-color: #16a34a;    /* Green */
    --warning-color: #d97706;    /* Orange */
    --danger-color: #dc2626;     /* Red */
}
```

### Adjust Refresh Interval
Edit `.github/workflows/health.yml`:
```yaml
schedule:
  - cron: '*/5 * * * *'  # Every 5 minutes
  # Change to */15 for every 15 minutes
```

### Change Latency Thresholds
Edit `scripts/healthCheck.js`:
```javascript
determineStatus(response, endpoint, latency) {
    if (latency > 500) return 'down';      // ← Change threshold
    if (latency > 100) return 'degraded';  // ← Change threshold
    return 'healthy';
}
```

## 🐛 Troubleshooting

### Dashboard shows "Loading..."
- Check that `docs/data/system_health.json` exists
- Try refreshing the page
- Check browser console for errors

### Health check script fails
```bash
# Check Node.js is installed
node --version  # Should be 18+

# Run with more details
node scripts/healthCheck.js 2>&1
```

### Chart doesn't render
- Wait 2-3 seconds after opening drawer
- Check that Chart.js loaded (see browser console)
- Refresh the page

## 📚 Next Steps

1. ✅ View the dashboard locally
2. ✅ Customize system endpoints
3. ✅ Run a test health check
4. ✅ Push to GitHub
5. ✅ Enable GitHub Pages
6. ✅ Watch it auto-deploy!

## 💡 Pro Tips

- **Mobile Testing**: The dashboard is fully responsive
- **Browser Support**: Works in Chrome, Firefox, Safari, Edge
- **Dark Mode**: Add it yourself in styles.css (hint: use CSS variables)
- **Notifications**: Enable Slack in `.github/workflows/health.yml`

## 🆘 Need Help?

- 📖 Full docs: See `README.md`
- 🔄 Upgrade details: See `UPGRADE.md`
- 🐛 Found a bug? Check GitHub issues

## 🎉 You're All Set!

Your modern system health dashboard is ready to monitor your infrastructure like a pro. Enjoy! 🚀

---

**Quick Test Command:**
```bash
# Test everything works
cd brooks-system-health-dashboard
node scripts/healthCheck.js && npx serve docs
```

Then open http://localhost:3000 and click around!
