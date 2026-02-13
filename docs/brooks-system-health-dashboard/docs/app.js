// BrooksRunning.com System Health Dashboard

class BrooksHealthDashboard {
    constructor() {
        this.systems = [];
        this.activeChart = null;
        this.init();
    }

    async init() {
        await this.loadData();
        this.setupEventListeners();
        this.render();
        this.updateSummary();
    }

    async loadData() {
        try {
            const response = await fetch('data/brooks_health.json');
            this.systems = await response.json();
            
            // Generate performance data for each system
            this.systems.forEach(system => {
                if (!system.performanceData || system.performanceData.length === 0) {
                    system.performanceData = this.generatePerformanceData(system.latency, system.status);
                }
            });
        } catch (error) {
            console.error('Error loading data:', error);
            this.systems = [];
        }
    }

    generatePerformanceData(baseLatency, status) {
        const data = [];
        const now = Date.now();
        const variance = status === 'healthy' ? 50 : status === 'degraded' ? 100 : 300;

        for (let i = 30; i >= 0; i--) {
            const timestamp = now - (i * 60000); // 1 minute intervals
            const value = baseLatency + (Math.random() - 0.5) * variance;
            data.push({
                timestamp: timestamp,
                value: Math.max(0, value)
            });
        }

        return data;
    }

    setupEventListeners() {
        const refreshBtn = document.getElementById('refreshBtn');
        refreshBtn.addEventListener('click', () => this.refresh());

        const overlay = document.getElementById('drawerOverlay');
        overlay.addEventListener('click', () => this.closeDrawer());

        const closeBtn = document.getElementById('drawerClose');
        closeBtn.addEventListener('click', () => this.closeDrawer());

        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') this.closeDrawer();
        });
    }

    render() {
        const grid = document.getElementById('systemsGrid');
        grid.innerHTML = '';

        this.systems.forEach(system => {
            const card = this.createSystemCard(system);
            grid.appendChild(card);
        });

        this.updateLastUpdated();
    }

    createSystemCard(system) {
        const card = document.createElement('div');
        card.className = 'system-card';
        card.addEventListener('click', () => this.openDrawer(system));

        const statusIcon = this.getStatusIcon(system.status);
        const typeIcon = this.getTypeIcon(system.type);

        // Determine if this is critical e-commerce infrastructure
        const isCritical = ['brooks-cart-api', 'brooks-order-api', 'brooks-checkout-start', 'brooks-checkout-shipping'].includes(system.id);

        card.innerHTML = `
            <div class="system-card-header">
                <div class="system-info">
                    <h3>
                        ${typeIcon} ${system.name}
                        ${isCritical ? '<span class="critical-badge">Critical</span>' : ''}
                    </h3>
                    <div class="system-type">${system.type} • ${system.endpoint}</div>
                </div>
                <div class="status-icon ${system.status}">
                    ${statusIcon}
                </div>
            </div>
            <div class="system-metrics">
                <div class="metric">
                    <div class="metric-label">Latency</div>
                    <div class="metric-value">
                        ${Math.round(system.latency)}
                        <span class="metric-unit">ms</span>
                    </div>
                </div>
                <div class="metric">
                    <div class="metric-label">Availability</div>
                    <div class="metric-value">
                        ${system.availability.toFixed(2)}
                        <span class="metric-unit">%</span>
                    </div>
                </div>
            </div>
            ${this.renderBusinessMetricPreview(system)}
        `;

        return card;
    }

    renderBusinessMetricPreview(system) {
        if (!system.businessMetrics) return '';

        const metrics = system.businessMetrics;
        let preview = '';

        // Show most critical metric based on system type
        if (system.id === 'brooks-order-api' && metrics.orderFailureRate) {
            preview = `
                <div class="business-metric-preview ${metrics.orderFailureRate > 2 ? 'warning' : ''}">
                    <span class="metric-icon">💳</span>
                    <span>Order Failure: ${metrics.orderFailureRate.toFixed(1)}%</span>
                </div>
            `;
        } else if (system.id === 'brooks-search' && metrics.searchSuccessRate) {
            preview = `
                <div class="business-metric-preview ${metrics.searchSuccessRate < 95 ? 'warning' : ''}">
                    <span class="metric-icon">🔍</span>
                    <span>Success Rate: ${metrics.searchSuccessRate.toFixed(1)}%</span>
                </div>
            `;
        } else if (system.id === 'brooks-cart-api' && metrics.cartErrorRate) {
            preview = `
                <div class="business-metric-preview ${metrics.cartErrorRate > 1 ? 'warning' : ''}">
                    <span class="metric-icon">🛒</span>
                    <span>Error Rate: ${metrics.cartErrorRate.toFixed(1)}%</span>
                </div>
            `;
        } else if (metrics.pageLoadTime) {
            preview = `
                <div class="business-metric-preview">
                    <span class="metric-icon">⚡</span>
                    <span>Load Time: ${Math.round(metrics.pageLoadTime)}ms</span>
                </div>
            `;
        }

        return preview;
    }

    getStatusIcon(status) {
        const icons = {
            healthy: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>',
            degraded: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>',
            down: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>'
        };
        return icons[status] || icons.healthy;
    }

    getTypeIcon(type) {
        const icons = {
            'Web Page': '🌐',
            'API': '⚡',
            'Database': '🗄️',
            'Service': '⚙️'
        };
        return icons[type] || '📊';
    }

    openDrawer(system) {
        const drawer = document.getElementById('drawerPanel');
        const overlay = document.getElementById('drawerOverlay');
        const title = document.getElementById('drawerTitle');
        const content = document.getElementById('drawerContent');

        title.textContent = system.name;
        content.innerHTML = this.renderDrawerContent(system);

        drawer.classList.add('active');
        overlay.classList.add('active');
        document.body.style.overflow = 'hidden';

        setTimeout(() => this.renderChart(system), 100);
    }

    closeDrawer() {
        const drawer = document.getElementById('drawerPanel');
        const overlay = document.getElementById('drawerOverlay');

        drawer.classList.remove('active');
        overlay.classList.remove('active');
        document.body.style.overflow = '';

        if (this.activeChart) {
            this.activeChart.destroy();
            this.activeChart = null;
        }
    }

    renderDrawerContent(system) {
        const statusConfig = this.getStatusConfig(system.status);
        
        return `
            <!-- Current Status -->
            <div class="drawer-section">
                <h3>Current Status</h3>
                <div class="status-card ${system.status}">
                    <div class="status-card-icon ${system.status}">
                        ${this.getStatusIcon(system.status)}
                    </div>
                    <div class="status-card-content">
                        <div class="status-card-title ${system.status}">${statusConfig.text}</div>
                        <div class="status-card-time">Last checked ${this.formatTime(new Date(system.lastCheck))}</div>
                        <div class="status-card-endpoint">${system.endpoint}</div>
                    </div>
                </div>
            </div>

            <!-- Performance Metrics -->
            <div class="drawer-section">
                <h3>Performance Metrics</h3>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-card-header">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
                            </svg>
                            <span>Latency</span>
                        </div>
                        <div class="metric-card-value-wrapper">
                            <span class="metric-card-value">${Math.round(system.latency)}</span>
                            <span class="metric-card-unit">ms</span>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-card-header">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline>
                            </svg>
                            <span>Availability</span>
                        </div>
                        <div class="metric-card-value-wrapper">
                            <span class="metric-card-value">${system.availability.toFixed(2)}</span>
                            <span class="metric-card-unit">%</span>
                        </div>
                    </div>
                </div>
            </div>

            ${this.renderBusinessMetrics(system)}

            <!-- Performance Chart -->
            <div class="drawer-section">
                <h3>Latency Trend (30 min)</h3>
                <div class="chart-container">
                    <canvas id="performanceChart"></canvas>
                </div>
            </div>

            <!-- Diagnostic Summary -->
            <div class="drawer-section">
                <h3>Diagnostic Summary</h3>
                <div class="diagnostic-card">
                    <p>${system.diagnostic}</p>
                </div>
            </div>

            <!-- Recent Incidents -->
            <div class="drawer-section">
                <h3>Recent Incidents ${system.incidents && system.incidents.length > 0 ? `(${system.incidents.length})` : ''}</h3>
                ${!system.incidents || system.incidents.length === 0 ? `
                    <div class="no-incidents">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="20 6 9 17 4 12"></polyline>
                        </svg>
                        <p>No incidents in the last 24 hours</p>
                    </div>
                ` : `
                    <div class="incidents-list">
                        ${system.incidents.map(incident => `
                            <div class="incident-card">
                                <div class="incident-header">
                                    <div class="incident-icon ${incident.severity}">
                                        ${this.getIncidentIcon(incident.severity)}
                                    </div>
                                    <div class="incident-content">
                                        <div class="incident-message">${incident.message}</div>
                                        <div class="incident-time">${this.formatDate(new Date(incident.timestamp))}</div>
                                    </div>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                `}
            </div>
        `;
    }

    renderBusinessMetrics(system) {
        if (!system.businessMetrics) return '';

        const metrics = system.businessMetrics;
        let metricsHTML = '<div class="drawer-section"><h3>Business Metrics</h3><div class="business-metrics-grid">';

        // Order API specific metrics
        if (system.id === 'brooks-order-api') {
            metricsHTML += `
                <div class="business-metric-card ${metrics.orderFailureRate > 2 ? 'warning' : ''}">
                    <div class="business-metric-label">Order Failure Rate</div>
                    <div class="business-metric-value">${metrics.orderFailureRate?.toFixed(1)}%</div>
                </div>
                <div class="business-metric-card">
                    <div class="business-metric-label">Payment Processing</div>
                    <div class="business-metric-value">${Math.round(metrics.paymentProcessingTime)}ms</div>
                </div>
                <div class="business-metric-card ${metrics.timeoutRate > 2 ? 'critical' : ''}">
                    <div class="business-metric-label">Timeout Rate</div>
                    <div class="business-metric-value">${metrics.timeoutRate?.toFixed(1)}%</div>
                </div>
                <div class="business-metric-card ${metrics.revenueImpact > 5000 ? 'critical' : ''}">
                    <div class="business-metric-label">Revenue Impact</div>
                    <div class="business-metric-value">$${metrics.revenueImpact?.toLocaleString()}</div>
                </div>
            `;
        }
        
        // Search specific metrics
        else if (system.id === 'brooks-search') {
            metricsHTML += `
                <div class="business-metric-card ${metrics.searchSuccessRate < 95 ? 'warning' : ''}">
                    <div class="business-metric-label">Search Success Rate</div>
                    <div class="business-metric-value">${metrics.searchSuccessRate?.toFixed(1)}%</div>
                </div>
                <div class="business-metric-card">
                    <div class="business-metric-label">Results Accuracy</div>
                    <div class="business-metric-value">${metrics.resultsAccuracy?.toFixed(1)}%</div>
                </div>
                <div class="business-metric-card">
                    <div class="business-metric-label">Autocomplete Speed</div>
                    <div class="business-metric-value">${Math.round(metrics.autocompleteSpeed)}ms</div>
                </div>
                <div class="business-metric-card ${metrics.zeroResultsRate > 10 ? 'warning' : ''}">
                    <div class="business-metric-label">Zero Results Rate</div>
                    <div class="business-metric-value">${metrics.zeroResultsRate?.toFixed(1)}%</div>
                </div>
            `;
        }
        
        // Cart API specific metrics
        else if (system.id === 'brooks-cart-api') {
            metricsHTML += `
                <div class="business-metric-card">
                    <div class="business-metric-label">Add to Cart Success</div>
                    <div class="business-metric-value">${metrics.addToCartSuccessRate?.toFixed(1)}%</div>
                </div>
                <div class="business-metric-card ${metrics.cartErrorRate > 1 ? 'warning' : ''}">
                    <div class="business-metric-label">Cart Error Rate</div>
                    <div class="business-metric-value">${metrics.cartErrorRate?.toFixed(1)}%</div>
                </div>
                <div class="business-metric-card">
                    <div class="business-metric-label">Avg Cart Value</div>
                    <div class="business-metric-value">$${metrics.averageCartValue?.toFixed(2)}</div>
                </div>
                <div class="business-metric-card">
                    <div class="business-metric-label">Abandonment Rate</div>
                    <div class="business-metric-value">${metrics.cartAbandonmentRate?.toFixed(1)}%</div>
                </div>
            `;
        }
        
        // Checkout specific metrics
        else if (system.id.includes('checkout')) {
            metricsHTML += `
                <div class="business-metric-card">
                    <div class="business-metric-label">Page Load Time</div>
                    <div class="business-metric-value">${Math.round(metrics.pageLoadTime)}ms</div>
                </div>
                <div class="business-metric-card ${metrics.checkoutErrorRate > 2 ? 'warning' : ''}">
                    <div class="business-metric-label">Error Rate</div>
                    <div class="business-metric-value">${(metrics.checkoutErrorRate || metrics.addressErrorRate)?.toFixed(1)}%</div>
                </div>
            `;
            if (metrics.addressValidationTime) {
                metricsHTML += `
                    <div class="business-metric-card">
                        <div class="business-metric-label">Address Validation</div>
                        <div class="business-metric-value">${Math.round(metrics.addressValidationTime)}ms</div>
                    </div>
                `;
            }
            if (metrics.shippingRateCalculation) {
                metricsHTML += `
                    <div class="business-metric-card">
                        <div class="business-metric-label">Shipping Calculation</div>
                        <div class="business-metric-value">${Math.round(metrics.shippingRateCalculation)}ms</div>
                    </div>
                `;
            }
        }
        
        // Product/Category pages
        else if (system.id === 'brooks-pdp') {
            metricsHTML += `
                <div class="business-metric-card">
                    <div class="business-metric-label">Add to Cart Success</div>
                    <div class="business-metric-value">${metrics.addToCartSuccessRate?.toFixed(1)}%</div>
                </div>
                <div class="business-metric-card">
                    <div class="business-metric-label">Size Availability</div>
                    <div class="business-metric-value">${metrics.sizeAvailability?.toFixed(1)}%</div>
                </div>
                <div class="business-metric-card">
                    <div class="business-metric-label">Image Carousel</div>
                    <div class="business-metric-value">${Math.round(metrics.imageCarouselLoad)}ms</div>
                </div>
            `;
        }

        // Generic page load metrics for other pages
        else if (metrics.pageLoadTime) {
            metricsHTML += `
                <div class="business-metric-card">
                    <div class="business-metric-label">Page Load Time</div>
                    <div class="business-metric-value">${Math.round(metrics.pageLoadTime)}ms</div>
                </div>
            `;
            if (metrics.conversionRate) {
                metricsHTML += `
                    <div class="business-metric-card">
                        <div class="business-metric-label">Conversion Rate</div>
                        <div class="business-metric-value">${metrics.conversionRate?.toFixed(1)}%</div>
                    </div>
                `;
            }
        }

        metricsHTML += '</div></div>';
        return metricsHTML;
    }

    getStatusConfig(status) {
        const configs = {
            healthy: { text: 'Healthy', color: '#16a34a' },
            degraded: { text: 'Degraded', color: '#d97706' },
            down: { text: 'Down', color: '#dc2626' }
        };
        return configs[status] || configs.healthy;
    }

    getIncidentIcon(severity) {
        const icons = {
            critical: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>',
            warning: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>',
            info: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>'
        };
        return icons[severity] || icons.info;
    }

    renderChart(system) {
        const canvas = document.getElementById('performanceChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const statusConfig = this.getStatusConfig(system.status);

        if (this.activeChart) {
            this.activeChart.destroy();
        }

        this.activeChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: system.performanceData.map(d => new Date(d.timestamp)),
                datasets: [{
                    label: 'Latency (ms)',
                    data: system.performanceData.map(d => d.value),
                    borderColor: statusConfig.color,
                    backgroundColor: statusConfig.color + '20',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            title: (items) => {
                                const date = new Date(items[0].parsed.x);
                                return date.toLocaleTimeString();
                            },
                            label: (item) => {
                                return `${Math.round(item.parsed.y)} ms`;
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'minute',
                            displayFormats: {
                                minute: 'HH:mm'
                            }
                        },
                        grid: {
                            color: '#e5e7eb'
                        },
                        ticks: {
                            color: '#6b7280',
                            font: {
                                size: 11
                            }
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: '#e5e7eb'
                        },
                        ticks: {
                            color: '#6b7280',
                            font: {
                                size: 11
                            },
                            callback: (value) => value + ' ms'
                        }
                    }
                },
                interaction: {
                    mode: 'nearest',
                    axis: 'x',
                    intersect: false
                }
            }
        });
    }

    updateSummary() {
        const counts = {
            healthy: 0,
            degraded: 0,
            down: 0
        };

        this.systems.forEach(system => {
            counts[system.status]++;
        });

        document.getElementById('healthyCount').textContent = `${counts.healthy} Healthy`;
        document.getElementById('degradedCount').textContent = `${counts.degraded} Degraded`;
        document.getElementById('downCount').textContent = `${counts.down} Down`;
    }

    updateLastUpdated() {
        const now = new Date();
        const timeString = now.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
        document.getElementById('lastUpdated').textContent = `Last updated: ${timeString}`;
    }

    async refresh() {
        const btn = document.getElementById('refreshBtn');
        btn.classList.add('loading');
        btn.disabled = true;

        await new Promise(resolve => setTimeout(resolve, 1000));

        await this.loadData();
        this.render();
        this.updateSummary();

        btn.classList.remove('loading');
        btn.disabled = false;
    }

    formatTime(date) {
        return date.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    }

    formatDate(date) {
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);

        if (diffMins < 60) {
            return `${diffMins} minutes ago`;
        } else if (diffHours < 24) {
            return `${diffHours} hours ago`;
        } else {
            return date.toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        }
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new BrooksHealthDashboard();
});
