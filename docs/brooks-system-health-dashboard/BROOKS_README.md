# 🏃 BrooksRunning.com System Health Dashboard

A production-ready e-commerce monitoring dashboard specifically built for BrooksRunning.com infrastructure with real-time status updates, business metrics, and performance analytics.

![Status](https://img.shields.io/badge/status-operational-brightgreen) ![E-commerce](https://img.shields.io/badge/platform-e--commerce-blue)

## 🎯 Overview

This dashboard monitors critical BrooksRunning.com systems including:
- **Web Pages**: Homepage, Product Detail, Category, Search, Account
- **E-commerce APIs**: Cart, Order, Promotions
- **Checkout Flow**: Guest checkout start and shipping stages

Each system displays comprehensive health metrics and business KPIs specific to e-commerce operations.

## ✨ Key Features

### 📊 E-Commerce Specific Monitoring
- **Order API**: Order failure rate, payment processing time, revenue impact
- **Cart API**: Add-to-cart success rate, cart errors, average cart value
- **Search**: Success rate, zero results rate, autocomplete speed
- **Checkout**: Error rates, address validation, shipping calculation
- **Product Pages**: Add-to-cart success, size availability, image load times

### 🎨 Modern Dashboard UI
- React-style drawer panel for detailed system views
- Interactive Chart.js latency trend graphs
- Color-coded status indicators (Green/Yellow/Red)
- Critical system badges for revenue-impacting services
- Real-time business metric previews on cards

### 📈 Business Intelligence
- **Revenue Impact Tracking**: Automatically calculates lost revenue during outages
- **Conversion Metrics**: Bounce rate, conversion rate, checkout completion
- **Performance KPIs**: Page load times, API latency, success rates
- **Customer Experience**: Cart abandonment, search accuracy, error rates

## 🚀 Quick Start

### View the Dashboard

```bash
# Option 1: Direct file open
open docs/index.html

# Option 2: Local server (recommended)
cd brooks-system-health-dashboard
npx serve docs
# Opens at http://localhost:3000

# Option 3: Python server
python3 -m http.server 8000 --directory docs
```

### Run Health Checks

```bash
# Single check
node scripts/healthCheck.js

# Continuous monitoring (every 5 minutes via GitHub Actions)
# Push to GitHub and enable Actions
```

## 📁 Monitored Systems

### Critical E-Commerce Infrastructure 🔴

| System | Endpoint | Critical? | Metrics |
|--------|----------|-----------|---------|
| **Cart API** | `/s/-/dw/data/v23_3/baskets/` | ✅ Critical | Add-to-cart success, cart errors, avg cart value |
| **Order API** | `/s/-/dw/data/v23_3/orders/` | ✅ Critical | Order failure rate, payment time, revenue impact |
| **Checkout Start** | `/en_us/check-out/check-out-process/` | ✅ Critical | Checkout errors, guest checkout rate |
| **Checkout Shipping** | `/en_us/check-out/...?stage=shipping` | ✅ Critical | Address validation, shipping calculation |

### Customer-Facing Pages

| System | Endpoint | Business Metrics |
|--------|----------|------------------|
| **Homepage** | `/` | Bounce rate, conversion rate, hero image load |
| **Product Detail** | `/en_us/products/<product-id>/` | Add-to-cart success, size availability |
| **Category Pages** | `/en_us/c/<category-id>/` | Product grid load, filter performance |
| **Search** | `/en_us/search?q=<term>` | Search success rate, zero results rate |
| **Account** | `/en_us/account` | Login success, profile updates, order history load |

### Supporting APIs

| System | Endpoint | Function |
|--------|----------|----------|
| **Promotions API** | `/s/-/dw/data/v23_3/promotions` | Promo code validation, discount calculation |

## 📊 Status Thresholds

### APIs (Cart, Order, Promotions)
- 🟢 **Healthy**: < 200ms latency
- 🟡 **Degraded**: 200-1000ms latency
- 🔴 **Down**: > 1000ms or connection failure

### Web Pages
- 🟢 **Healthy**: < 500ms latency
- 🟡 **Degraded**: 500-2000ms latency
- 🔴 **Down**: > 2000ms or connection failure

## 💼 Business Metrics Explained

### Order API Metrics
- **Order Failure Rate**: % of failed order submissions (target: < 1%)
- **Payment Processing Time**: Average time to process payment (target: < 500ms)
- **Timeout Rate**: % of order API timeouts (target: < 1%)
- **Revenue Impact**: Estimated lost revenue during downtime

### Cart API Metrics
- **Add-to-Cart Success Rate**: % of successful cart additions (target: > 99%)
- **Cart Error Rate**: % of cart operation failures (target: < 1%)
- **Average Cart Value**: Mean cart value across all sessions
- **Cart Abandonment Rate**: % of carts not converted to orders

### Search Metrics
- **Search Success Rate**: % of searches returning results (target: > 95%)
- **Results Accuracy**: Relevance score of search results
- **Zero Results Rate**: % of searches with no results (target: < 10%)
- **Autocomplete Speed**: Time to show autocomplete suggestions

### Checkout Metrics
- **Checkout Error Rate**: % of checkout failures (target: < 2%)
- **Address Validation Time**: Time to validate shipping address
- **Shipping Rate Calculation**: Time to fetch shipping options
- **Guest Checkout Rate**: % using guest vs. account checkout

## 🎨 Dashboard Features

### System Cards
- **Status Indicators**: Color-coded health status at a glance
- **Latency Display**: Current response time in milliseconds
- **Availability %**: Historical uptime percentage
- **Business Preview**: Most critical metric shown on card
- **Critical Badges**: Flagged for revenue-impacting systems

### Detail Drawer
Click any system card to see:
- ✅ Current status with last check time
- 📊 Performance metrics (latency & availability)
- 💼 **Business metrics grid** with all KPIs
- 📈 30-minute latency trend chart
- 📝 Diagnostic summary
- 🚨 Recent incidents (last 24 hours)

### Color Coding
- **Green**: System healthy, all metrics normal
- **Yellow**: Degraded performance, monitoring required
- **Red**: System down or critical issues
- **Critical Badge**: Revenue-impacting system requires immediate attention

## ⚙️ Configuration

### Customize Endpoints

Edit `scripts/healthCheck.js`:

```javascript
const CONFIG = {
    endpoints: [
        {
            id: 'brooks-homepage',
            name: 'Homepage',
            type: 'Web Page',
            url: 'https://www.brooksrunning.com/',
            method: 'GET',
            timeout: 10000,
            expectedStatus: 200
        },
        // Add or modify endpoints...
    ]
};
```

### Adjust Latency Thresholds

In `scripts/healthCheck.js`, modify the `determineStatus` method:

```javascript
determineStatus(response, endpoint, latency) {
    if (endpoint.isApi) {
        if (latency > 1000) return 'down';      // API down threshold
        if (latency > 200) return 'degraded';   // API degraded threshold
    } else {
        if (latency > 2000) return 'down';      // Page down threshold
        if (latency > 500) return 'degraded';   // Page degraded threshold
    }
    return 'healthy';
}
```

### Customize Business Metrics

Edit the `generateBusinessMetrics` method in `scripts/healthCheck.js` to add or modify KPIs for each endpoint.

## 🤖 Automated Monitoring

### GitHub Actions Setup

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial BrooksRunning dashboard"
   git remote add origin https://github.com/your-org/brooks-health-dashboard.git
   git push -u origin main
   ```

2. **Enable GitHub Pages**:
   - Go to repository Settings → Pages
   - Source: "Deploy from a branch"
   - Branch: main
   - Folder: /docs
   - Save

3. **Configure Secrets** (optional):
   - `SLACK_WEBHOOK_URL`: For Slack notifications

The workflow automatically:
- ✅ Runs health checks every 5 minutes
- ✅ Updates `brooks_health.json` with latest data
- ✅ Commits changes to repository
- ✅ Deploys to GitHub Pages
- ✅ Sends alerts on critical failures

### Manual Monitoring

```bash
# Run single health check
node scripts/healthCheck.js

# View results
cat docs/data/brooks_health.json

# Watch mode (check every 60 seconds)
watch -n 60 node scripts/healthCheck.js
```

## 📊 Understanding the Data

### Sample Health Data Structure

```json
{
  "id": "brooks-order-api",
  "name": "Order API",
  "type": "API",
  "endpoint": "/s/-/dw/data/v23_3/orders/<order_no>",
  "status": "healthy",
  "latency": 156.3,
  "availability": 99.94,
  "businessMetrics": {
    "orderFailureRate": 0.8,
    "paymentProcessingTime": 234,
    "timeoutRate": 0.3,
    "revenueImpact": 0
  },
  "incidents": []
}
```

## 🚨 Alert Strategy

### Critical Alerts (Immediate Action)
- **Order API Down**: Revenue blocked, escalate to on-call
- **Cart API Down**: Cannot add to cart, high priority
- **Checkout Down**: Cannot complete purchases, critical

### Warning Alerts (Monitor)
- **Search Degraded**: Monitor search performance
- **Product Pages Slow**: May impact conversion
- **High Cart Abandonment**: Investigate user experience

### Info Alerts
- **Promotions API Slow**: Non-critical but worth monitoring
- **Account Page Issues**: Important but not revenue-blocking

## 📈 Metrics & Reporting

### Daily Health Report
The dashboard shows:
- Overall system health percentage
- Count of healthy/degraded/down systems
- Recent incidents in last 24 hours
- Business metric trends

### Historical Data
- Last 100 health checks stored in `health_history.json`
- 30-minute latency trends on detail views
- Incident timeline for troubleshooting

## 🔧 Troubleshooting

### Dashboard Not Loading
```bash
# Check if data file exists
ls -la docs/data/brooks_health.json

# Regenerate data
node scripts/healthCheck.js

# Check browser console for errors
```

### Health Check Failing
```bash
# Test individual endpoint
curl -I https://www.brooksrunning.com/

# Check network connectivity
ping www.brooksrunning.com

# Verify timeout settings in healthCheck.js
```

### Charts Not Rendering
- Ensure Chart.js is loading (check browser Network tab)
- Wait 2-3 seconds after opening drawer
- Refresh the page

## 🎯 Best Practices

1. **Critical System Monitoring**: Focus on Order, Cart, and Checkout APIs
2. **Business Metrics**: Track conversion impact of performance issues
3. **Alert Fatigue**: Set realistic thresholds to avoid false positives
4. **Regular Testing**: Run manual checks during deployments
5. **Historical Analysis**: Use trend data to identify patterns

## 🔐 Security Notes

- Health check script uses read-only GET requests
- No authentication credentials stored in code
- Safe to run from CI/CD without exposing secrets
- Consider rate limiting if running frequent checks

## 📞 Support & Escalation

### Critical Issues (Revenue Impact)
1. Check dashboard for affected systems
2. Review incident details in drawer
3. Escalate to on-call engineer
4. Document in incident log

### Performance Degradation
1. Monitor trend charts
2. Check if issue is widespread or isolated
3. Review business metrics for customer impact
4. Consider scaling or optimization

## 🎓 Understanding E-Commerce Impact

### High Impact Issues
- **Order API Down**: Direct revenue loss
- **Cart API Failing**: Cannot add products
- **Checkout Errors**: Abandoned purchases

### Medium Impact Issues
- **Search Degraded**: Harder to find products
- **Product Pages Slow**: May increase bounce rate
- **Category Slow**: Navigation frustration

### Low Impact Issues
- **Account Page Slow**: Affects logged-in users only
- **Promotions Slow**: Discounts still apply, just slower

## 📝 License

MIT License - Built for BrooksRunning.com infrastructure monitoring

---

**🏃 Built with ❤️ for BrooksRunning.com reliability**

*Monitoring keeps runners running*
