// Biomarker Dashboard JavaScript
class BiomarkerDashboard {
    constructor() {
        this.data = null;
        this.charts = {};
        this.clinicalRanges = null;
        this.currentDateRange = 6; // months
        
        this.init();
    }

    async init() {
        try {
            await this.loadData();
            this.setupEventListeners();
            this.updatePatientInfo();
            this.createCharts();
            this.updateOverviewCards();
            this.generateClinicalInsights();
            this.hideLoading();
        } catch (error) {
            console.error('Failed to initialize dashboard:', error);
            this.showError('Failed to load biomarker data. Please try again.');
        }
    }

    async loadData() {
        // Simulate API call - in production, this would fetch from a real API
        const response = await fetch('./data/sample_biomarker_data.json');
        this.data = await response.json();
        this.clinicalRanges = this.data.clinical_ranges;
    }

    setupEventListeners() {
        // Date range selector
        document.getElementById('date-range').addEventListener('change', (e) => {
            this.currentDateRange = e.target.value;
            this.updateChartsWithDateRange();
        });

        // Chart type selector
        document.getElementById('chart-type').addEventListener('change', (e) => {
            this.updateMainChart(e.target.value);
        });

        // Export button
        document.getElementById('export-btn').addEventListener('click', () => {
            this.exportChart();
        });

        // Responsive chart resize
        window.addEventListener('resize', () => {
            this.resizeCharts();
        });
    }

    updatePatientInfo() {
        const patient = this.data.patient_info;
        document.getElementById('patient-name').textContent = patient.name;
        document.getElementById('patient-info').textContent = 
            `${patient.gender}, Age ${patient.age} | ID: ${patient.patient_id}`;
    }

    getFilteredData() {
        if (this.currentDateRange === 'all') {
            return this.data.biomarkers;
        }
        
        const months = parseInt(this.currentDateRange);
        const cutoffDate = new Date();
        cutoffDate.setMonth(cutoffDate.getMonth() - months);
        
        return this.data.biomarkers.filter(entry => 
            new Date(entry.date) >= cutoffDate
        );
    }

    createCharts() {
        this.createMainChart();
        this.createLipidChart();
        this.createKidneyChart();
        this.createVitaminChart();
        this.createDiabetesChart();
    }

    createMainChart(type = 'lipid') {
        const ctx = document.getElementById('main-chart').getContext('2d');
        const filteredData = this.getFilteredData();
        
        if (this.charts.main) {
            this.charts.main.destroy();
        }

        const datasets = this.getMainChartDatasets(type, filteredData);
        
        this.charts.main = new Chart(ctx, {
            type: 'line',
            data: {
                labels: filteredData.map(d => new Date(d.date).toLocaleDateString()),
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: this.getYAxisLabel(type)
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: this.getChartTitle(type)
                    },
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            afterLabel: (context) => {
                                return this.getTooltipInfo(context, type);
                            }
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

    getMainChartDatasets(type, data) {
        const colors = {
            total_cholesterol: '#3b82f6',
            ldl: '#ef4444',
            hdl: '#22c55e',
            triglycerides: '#f59e0b',
            creatinine: '#8b5cf6',
            vitamin_d: '#f59e0b',
            vitamin_b12: '#06b6d4',
            hba1c: '#dc2626'
        };

        switch (type) {
            case 'lipid':
                return [
                    {
                        label: 'Total Cholesterol',
                        data: data.map(d => d.total_cholesterol),
                        borderColor: colors.total_cholesterol,
                        backgroundColor: colors.total_cholesterol + '20',
                        tension: 0.1
                    },
                    {
                        label: 'LDL',
                        data: data.map(d => d.ldl),
                        borderColor: colors.ldl,
                        backgroundColor: colors.ldl + '20',
                        tension: 0.1
                    },
                    {
                        label: 'HDL',
                        data: data.map(d => d.hdl),
                        borderColor: colors.hdl,
                        backgroundColor: colors.hdl + '20',
                        tension: 0.1
                    },
                    {
                        label: 'Triglycerides',
                        data: data.map(d => d.triglycerides),
                        borderColor: colors.triglycerides,
                        backgroundColor: colors.triglycerides + '20',
                        tension: 0.1
                    }
                ];
            case 'kidney':
                return [{
                    label: 'Creatinine',
                    data: data.map(d => d.creatinine),
                    borderColor: colors.creatinine,
                    backgroundColor: colors.creatinine + '20',
                    tension: 0.1
                }];
            case 'vitamins':
                return [
                    {
                        label: 'Vitamin D',
                        data: data.map(d => d.vitamin_d),
                        borderColor: colors.vitamin_d,
                        backgroundColor: colors.vitamin_d + '20',
                        tension: 0.1,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Vitamin B12',
                        data: data.map(d => d.vitamin_b12),
                        borderColor: colors.vitamin_b12,
                        backgroundColor: colors.vitamin_b12 + '20',
                        tension: 0.1,
                        yAxisID: 'y1'
                    }
                ];
            case 'diabetes':
                return [{
                    label: 'HbA1c',
                    data: data.map(d => d.hba1c),
                    borderColor: colors.hba1c,
                    backgroundColor: colors.hba1c + '20',
                    tension: 0.1
                }];
            case 'all':
                return Object.keys(colors).map(key => ({
                    label: this.formatBiomarkerName(key),
                    data: data.map(d => d[key]),
                    borderColor: colors[key],
                    backgroundColor: colors[key] + '20',
                    tension: 0.1,
                    hidden: key === 'vitamin_b12' // Hide B12 by default as it has different scale
                }));
            default:
                return [];
        }
    }

    createLipidChart() {
        const ctx = document.getElementById('lipid-chart').getContext('2d');
        const filteredData = this.getFilteredData();
        
        if (this.charts.lipid) {
            this.charts.lipid.destroy();
        }

        this.charts.lipid = new Chart(ctx, {
            type: 'line',
            data: {
                labels: filteredData.map(d => new Date(d.date).toLocaleDateString()),
                datasets: [
                    {
                        label: 'Total Cholesterol',
                        data: filteredData.map(d => d.total_cholesterol),
                        borderColor: '#3b82f6',
                        backgroundColor: '#3b82f620',
                        tension: 0.1
                    },
                    {
                        label: 'LDL',
                        data: filteredData.map(d => d.ldl),
                        borderColor: '#ef4444',
                        backgroundColor: '#ef444420',
                        tension: 0.1
                    },
                    {
                        label: 'HDL',
                        data: filteredData.map(d => d.hdl),
                        borderColor: '#22c55e',
                        backgroundColor: '#22c55e20',
                        tension: 0.1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: 'mmol/L'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                }
            }
        });
    }

    createKidneyChart() {
        const ctx = document.getElementById('kidney-chart').getContext('2d');
        const filteredData = this.getFilteredData();
        
        if (this.charts.kidney) {
            this.charts.kidney.destroy();
        }

        this.charts.kidney = new Chart(ctx, {
            type: 'line',
            data: {
                labels: filteredData.map(d => new Date(d.date).toLocaleDateString()),
                datasets: [{
                    label: 'Creatinine',
                    data: filteredData.map(d => d.creatinine),
                    borderColor: '#8b5cf6',
                    backgroundColor: '#8b5cf620',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: 'μmol/L'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                }
            }
        });
    }

    createVitaminChart() {
        const ctx = document.getElementById('vitamin-chart').getContext('2d');
        const filteredData = this.getFilteredData();
        
        if (this.charts.vitamin) {
            this.charts.vitamin.destroy();
        }

        this.charts.vitamin = new Chart(ctx, {
            type: 'line',
            data: {
                labels: filteredData.map(d => new Date(d.date).toLocaleDateString()),
                datasets: [
                    {
                        label: 'Vitamin D',
                        data: filteredData.map(d => d.vitamin_d),
                        borderColor: '#f59e0b',
                        backgroundColor: '#f59e0b20',
                        tension: 0.1,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Vitamin B12',
                        data: filteredData.map(d => d.vitamin_b12),
                        borderColor: '#06b6d4',
                        backgroundColor: '#06b6d420',
                        tension: 0.1,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: 'Vitamin D (ng/mL)'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Vitamin B12 (pg/mL)'
                        },
                        grid: {
                            drawOnChartArea: false,
                        },
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                }
            }
        });
    }

    createDiabetesChart() {
        const ctx = document.getElementById('diabetes-chart').getContext('2d');
        const filteredData = this.getFilteredData();
        
        if (this.charts.diabetes) {
            this.charts.diabetes.destroy();
        }

        this.charts.diabetes = new Chart(ctx, {
            type: 'line',
            data: {
                labels: filteredData.map(d => new Date(d.date).toLocaleDateString()),
                datasets: [{
                    label: 'HbA1c',
                    data: filteredData.map(d => d.hba1c),
                    borderColor: '#dc2626',
                    backgroundColor: '#dc262620',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: '%'
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                }
            }
        });
    }

    updateOverviewCards() {
        const latestData = this.data.biomarkers[this.data.biomarkers.length - 1];
        
        // Update cholesterol card
        document.getElementById('current-cholesterol').textContent = 
            `${latestData.total_cholesterol} mmol/L`;
        this.updateStatusIndicator('cholesterol-status', 'total_cholesterol', latestData.total_cholesterol);
        
        // Update creatinine card
        document.getElementById('current-creatinine').textContent = 
            `${latestData.creatinine} μmol/L`;
        this.updateStatusIndicator('creatinine-status', 'creatinine', latestData.creatinine);
        
        // Update vitamin D card
        document.getElementById('current-vitamin-d').textContent = 
            `${latestData.vitamin_d} ng/mL`;
        this.updateStatusIndicator('vitamin-d-status', 'vitamin_d', latestData.vitamin_d);
        
        // Update HbA1c card
        document.getElementById('current-hba1c').textContent = 
            `${latestData.hba1c}%`;
        this.updateStatusIndicator('hba1c-status', 'hba1c', latestData.hba1c);

        // Update individual biomarker values
        this.updateBiomarkerValues(latestData);
    }

    updateBiomarkerValues(data) {
        document.getElementById('lipid-total').textContent = `${data.total_cholesterol} mmol/L`;
        document.getElementById('lipid-ldl').textContent = `${data.ldl} mmol/L`;
        document.getElementById('lipid-hdl').textContent = `${data.hdl} mmol/L`;
        document.getElementById('lipid-triglycerides').textContent = `${data.triglycerides} mmol/L`;
        document.getElementById('kidney-creatinine').textContent = `${data.creatinine} μmol/L`;
        document.getElementById('vitamin-d-value').textContent = `${data.vitamin_d} ng/mL`;
        document.getElementById('vitamin-b12-value').textContent = `${data.vitamin_b12} pg/mL`;
        document.getElementById('diabetes-hba1c').textContent = `${data.hba1c}%`;
    }

    updateStatusIndicator(elementId, biomarker, value) {
        const element = document.getElementById(elementId);
        const status = this.getBiomarkerStatus(biomarker, value);
        
        element.className = `ml-2 flex items-baseline text-sm font-semibold status-${status.level}`;
        element.textContent = status.text;
    }

    getBiomarkerStatus(biomarker, value) {
        const ranges = this.clinicalRanges[biomarker].ranges;
        
        for (const [level, range] of Object.entries(ranges)) {
            if (value >= range.min && value <= range.max) {
                return {
                    level: level === 'optimal' || level === 'normal' || level === 'sufficient' ? 'optimal' :
                           level === 'borderline' || level === 'near_optimal' || level === 'insufficient' ? 'borderline' :
                           'high',
                    text: level.replace('_', ' ').toUpperCase()
                };
            }
        }
        
        return { level: 'high', text: 'HIGH' };
    }

    generateClinicalInsights() {
        const latestData = this.data.biomarkers[this.data.biomarkers.length - 1];
        const previousData = this.data.biomarkers[this.data.biomarkers.length - 2];
        const insights = [];

        // Cholesterol insights
        if (latestData.total_cholesterol > 6.1) {
            insights.push({
                type: 'critical',
                title: 'Total Cholesterol Elevated',
                message: 'Your total cholesterol is above the recommended level. Consider dietary changes and consult your physician about treatment options.'
            });
        } else if (latestData.total_cholesterol > 5.2) {
            insights.push({
                type: 'warning',
                title: 'Borderline High Cholesterol',
                message: 'Your cholesterol is in the borderline range. Monitor through diet and exercise.'
            });
        }

        // LDL insights
        if (latestData.ldl > 3.4) {
            insights.push({
                type: 'warning',
                title: 'LDL Cholesterol Attention',
                message: 'LDL cholesterol is above optimal. Focus on reducing saturated fats and increasing fiber intake.'
            });
        }

        // HDL insights
        if (latestData.hdl < 1.03) {
            insights.push({
                type: 'warning',
                title: 'Low HDL Cholesterol',
                message: 'HDL cholesterol is below recommended levels. Regular exercise can help increase HDL.'
            });
        }

        // Vitamin D insights
        if (latestData.vitamin_d < 30) {
            insights.push({
                type: latestData.vitamin_d < 20 ? 'critical' : 'warning',
                title: 'Vitamin D Deficiency',
                message: 'Vitamin D levels are below optimal. Consider supplementation and increased sun exposure.'
            });
        }

        // HbA1c insights
        if (latestData.hba1c >= 6.5) {
            insights.push({
                type: 'critical',
                title: 'Diabetes Range HbA1c',
                message: 'HbA1c indicates diabetes range. Immediate medical consultation recommended.'
            });
        } else if (latestData.hba1c >= 6.0) {
            insights.push({
                type: 'warning',
                title: 'Prediabetes Range',
                message: 'HbA1c is in prediabetes range. Lifestyle modifications can help prevent progression.'
            });
        }

        // Trend insights
        if (previousData) {
            const cholesterolTrend = latestData.total_cholesterol - previousData.total_cholesterol;
            if (cholesterolTrend > 0.5) {
                insights.push({
                    type: 'warning',
                    title: 'Rising Cholesterol Trend',
                    message: 'Your cholesterol has increased significantly since the last test. Review your diet and exercise routine.'
                });
            } else if (cholesterolTrend < -0.5) {
                insights.push({
                    type: 'optimal',
                    title: 'Improving Cholesterol',
                    message: 'Great progress! Your cholesterol levels are trending downward.'
                });
            }
        }

        // Add positive insights if no issues
        if (insights.length === 0) {
            insights.push({
                type: 'optimal',
                title: 'Overall Good Health',
                message: 'Your biomarkers are within healthy ranges. Continue your current lifestyle and regular monitoring.'
            });
        }

        this.renderClinicalInsights(insights);
    }

    renderClinicalInsights(insights) {
        const container = document.getElementById('clinical-insights');
        container.innerHTML = insights.map(insight => `
            <div class="insight-card insight-${insight.type}">
                <h4 class="font-semibold text-gray-900">${insight.title}</h4>
                <p class="text-sm text-gray-700 mt-1">${insight.message}</p>
            </div>
        `).join('');
    }

    updateMainChart(type) {
        this.createMainChart(type);
    }

    updateChartsWithDateRange() {
        this.createCharts();
        this.updateOverviewCards();
    }

    resizeCharts() {
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.resize();
        });
    }

    exportChart() {
        const canvas = document.getElementById('main-chart');
        const link = document.createElement('a');
        link.download = 'biomarker-chart.png';
        link.href = canvas.toDataURL();
        link.click();
    }

    getChartTitle(type) {
        const titles = {
            lipid: 'Lipid Profile Trends',
            kidney: 'Kidney Function Trends',
            vitamins: 'Vitamin Level Trends',
            diabetes: 'Diabetes Marker Trends',
            all: 'All Biomarker Trends'
        };
        return titles[type] || 'Biomarker Trends';
    }

    getYAxisLabel(type) {
        const labels = {
            lipid: 'Concentration (mmol/L)',
            kidney: 'Creatinine (μmol/L)',
            vitamins: 'Concentration',
            diabetes: 'HbA1c (%)',
            all: 'Values'
        };
        return labels[type] || 'Values';
    }

    getTooltipInfo(context, type) {
        const biomarker = context.dataset.label.toLowerCase().replace(' ', '_');
        const value = context.parsed.y;
        const status = this.getBiomarkerStatus(biomarker, value);
        return `Status: ${status.text}`;
    }

    formatBiomarkerName(key) {
        const names = {
            total_cholesterol: 'Total Cholesterol',
            ldl: 'LDL',
            hdl: 'HDL',
            triglycerides: 'Triglycerides',
            creatinine: 'Creatinine',
            vitamin_d: 'Vitamin D',
            vitamin_b12: 'Vitamin B12',
            hba1c: 'HbA1c'
        };
        return names[key] || key;
    }

    hideLoading() {
        document.getElementById('loading-overlay').style.display = 'none';
    }

    showError(message) {
        const overlay = document.getElementById('loading-overlay');
        overlay.innerHTML = `
            <div class="bg-white p-6 rounded-lg shadow-lg">
                <div class="flex items-center space-x-3">
                    <div class="text-red-600">⚠️</div>
                    <span class="text-gray-700">${message}</span>
                </div>
            </div>
        `;
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new BiomarkerDashboard();
});