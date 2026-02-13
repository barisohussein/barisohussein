# 🏥 System Health Dashboard

An enterprise-grade system health monitoring dashboard with real-time status updates, performance charts, and detailed diagnostics.

![Dashboard Preview](https://img.shields.io/badge/status-operational-brightgreen)

## ✨ Features

- **🎨 Modern UI**: Clean, professional interface with drawer-based detail panels
- **📊 Real-time Charts**: Interactive latency trend charts using Chart.js
- **🔍 Detailed Diagnostics**: Comprehensive system health information
- **📱 Responsive Design**: Works seamlessly on desktop and mobile
- **⚡ Auto-refresh**: Configurable automatic health checks
- **🚨 Incident Tracking**: Historical incident logging and display
- **📈 Availability Metrics**: Track system uptime over time
- **🎯 Status Indicators**: At-a-glance health status with color coding

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/system-health-dashboard.git
   cd system-health-dashboard
   ```

2. **Open the dashboard**
   ```bash
   # Simply open docs/index.html in your browser
   open docs/index.html
   
   # Or use a local server (recommended)
   npx serve docs
   ```

3. **Configure your endpoints**
   Edit `scripts/healthCheck.js` to add your system endpoints:
   ```javascript
   const CONFIG = {
       endpoints: [
           {
               id: 'sys-001',
               name: 'Your API',
               type: 'API',
               url: 'https://your-api.com/health',
               method: 'GET',
               timeout: 5000,
               expectedStatus: 200
           },
           // Add more endpoints...
       ]
   };
   ```

4. **Run health checks**
   ```bash
   node scripts/healthCheck.js
   ```

## 📁 Project Structure

```
brooks-system-health-dashboard/
├── docs/                      # Web dashboard (GitHub Pages ready)
│   ├── index.html            # Main dashboard page
│   ├── styles.css            # Enterprise styling
│   ├── app.js                # Dashboard logic & interactions
│   └── data/
│       ├── system_health.json     # Current health status
│       └── health_history.json    # Historical data
├── scripts/
│   └── healthCheck.js        # Health check automation
├── .github/
│   └── workflows/
│       └── health.yml        # CI/CD automation
└── README.md
```

## 🎯 Health Check Automation

### GitHub Actions (Recommended)

The included workflow automatically:
- Runs health checks every 5 minutes
- Commits updated data to the repository
- Deploys the dashboard to GitHub Pages
- Sends notifications on failures
- Creates status badges

Enable it by:
1. Enabling GitHub Pages in repository settings (use `docs` folder)
2. Adding secrets if using Slack notifications:
   - `SLACK_WEBHOOK_URL`: Your Slack webhook URL

### Manual Execution

```bash
# Run a single health check
node scripts/healthCheck.js

# Schedule with cron (Linux/Mac)
*/5 * * * * cd /path/to/dashboard && node scripts/healthCheck.js
```

## 🎨 Dashboard Features

### Status Overview
- **Healthy** (Green): System operating normally (latency < 100ms)
- **Degraded** (Yellow): Elevated response times (100-500ms)
- **Down** (Red): Service unavailable or critical issues (>500ms)

### Detail Panel
Click any system card to open the detail panel with:
- Current status and last check time
- Performance metrics (latency & availability)
- 30-minute latency trend chart
- Diagnostic summary
- Recent incident history

### Interactive Charts
- Real-time latency trends
- Color-coded by health status
- Hover for exact values
- Responsive to window size

## ⚙️ Configuration

### Health Check Thresholds

Edit `scripts/healthCheck.js`:

```javascript
determineStatus(response, endpoint, latency) {
    if (response.statusCode !== endpoint.expectedStatus) {
        return 'down';
    }
    
    // Customize these thresholds
    if (latency > 500) return 'down';
    if (latency > 100) return 'degraded';
    
    return 'healthy';
}
```

### Refresh Interval

Edit `.github/workflows/health.yml`:

```yaml
schedule:
  - cron: '*/5 * * * *'  # Every 5 minutes
  # Change to '*/15 * * * *' for every 15 minutes
```

### Custom Styling

Edit `docs/styles.css` to match your brand:

```css
:root {
    --primary-color: #3b82f6;
    --success-color: #16a34a;
    --warning-color: #d97706;
    --danger-color: #dc2626;
}
```

## 🔔 Notifications

### Slack Integration

1. Create a Slack webhook URL
2. Add it as a repository secret: `SLACK_WEBHOOK_URL`
3. Notifications will be sent automatically on failures

### Email Notifications

Add to your workflow:

```yaml
- name: Send email
  uses: dawidd6/action-send-mail@v3
  with:
    server_address: smtp.gmail.com
    server_port: 465
    username: ${{secrets.MAIL_USERNAME}}
    password: ${{secrets.MAIL_PASSWORD}}
    subject: System Health Alert
    body: One or more systems are experiencing issues
    to: team@example.com
    from: monitoring@example.com
```

## 📊 Data Format

### system_health.json
```json
[
  {
    "id": "sys-001",
    "name": "API Gateway",
    "type": "API",
    "status": "healthy",
    "latency": 45.3,
    "availability": 99.98,
    "lastCheck": "2026-02-01T12:00:00Z",
    "diagnostic": "All systems operating normally",
    "performanceData": [...],
    "incidents": [...]
  }
]
```

## 🛠️ Development

### Prerequisites
- Node.js 18+ (for health check script)
- Modern browser (for dashboard)

### Testing Locally

```bash
# Test health check
node scripts/healthCheck.js

# Serve dashboard
npx serve docs

# Or use Python
python3 -m http.server 8000 --directory docs
```

### Adding New Systems

1. Add endpoint to `scripts/healthCheck.js`
2. Run health check to generate data
3. Refresh dashboard to see new system

## 🚢 Deployment

### GitHub Pages (Automated)
1. Push to main branch
2. GitHub Actions will automatically deploy
3. Access at `https://yourusername.github.io/repo-name`

### Manual Deployment
1. Copy `docs/` folder to your web server
2. Ensure `data/system_health.json` is accessible
3. Set up cron job for `healthCheck.js`

### Docker (Optional)

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY . .
RUN npm install -g serve
EXPOSE 3000
CMD ["serve", "docs", "-p", "3000"]
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- Design inspired by modern SaaS dashboards
- Built with vanilla JavaScript for maximum compatibility
- Charts powered by [Chart.js](https://www.chartjs.org/)

## 📞 Support

- 📧 Email: support@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/repo/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/repo/discussions)

---

Made with ❤️ for system reliability
