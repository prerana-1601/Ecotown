# Biomarker Time Series Visualization Dashboard

**EcoTown Health Tech Internship Assignment**

An interactive web dashboard for visualizing biomarker trends over time, featuring lipid profiles, kidney function, vitamin levels, and diabetes markers with clinical range indicators and automated insights.

## 🎯 Project Overview

This dashboard extracts biomarker data from health reports and creates interactive time series visualizations to help healthcare professionals track patient health trends and identify areas requiring attention.

### Key Features

- ✅ **Interactive Time Series Charts** - Multi-series line charts with zoom and pan functionality
- ✅ **Clinical Range Indicators** - Color-coded normal/abnormal zones based on medical standards
- ✅ **Responsive Design** - Mobile and desktop optimized layout
- ✅ **Data Extraction** - Python script for PDF biomarker extraction
- ✅ **Export Functionality** - PNG export for charts
- ✅ **Clinical Insights** - Automated health recommendations
- ✅ **Real-time Filtering** - Date range and biomarker group selection

## 🏗️ Technology Stack

### Frontend
- **HTML5/CSS3** - Semantic markup with Tailwind CSS
- **JavaScript (ES6+)** - Modern vanilla JS with classes
- **Chart.js** - Interactive charting library
- **Responsive Design** - Mobile-first approach

### Backend
- **Node.js/Express** - Web server for hosting
- **Python 3** - Data extraction scripts
- **JSON** - Data storage format

### Libraries & Tools
- **PyPDF2** - PDF text extraction
- **Pandas** - Data processing
- **Helmet** - Security middleware
- **CORS** - Cross-origin resource sharing

## 📊 Biomarkers Tracked

| Biomarker | Unit | Normal Range | Clinical Significance |
|-----------|------|--------------|----------------------|
| **Total Cholesterol** | mmol/L | <5.2 | Cardiovascular risk indicator |
| **LDL Cholesterol** | mmol/L | <2.6 | "Bad" cholesterol |
| **HDL Cholesterol** | mmol/L | >1.53 | "Good" cholesterol |
| **Triglycerides** | mmol/L | <1.69 | Fat metabolism indicator |
| **Creatinine** | μmol/L | 70-120 | Kidney function marker |
| **Vitamin D** | ng/mL | 30-100 | Bone health and immunity |
| **Vitamin B12** | pg/mL | 400-900 | Neurological function |
| **HbA1c** | % | <6.0 | Diabetes management |

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- Python 3.8+
- Modern web browser

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd biomarker-dashboard
   ```

2. **Install Node.js dependencies**
   ```bash
   npm install
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the development server**
   ```bash
   npm start
   ```

5. **Open the dashboard**
   Navigate to `http://localhost:3000` in your browser

## 📁 Project Structure

```
biomarker-dashboard/
├── index.html                 # Main dashboard page
├── server.js                 # Express server
├── package.json              # Node.js dependencies
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── data/
│   └── sample_biomarker_data.json  # Sample dataset
├── static/
│   ├── css/
│   │   └── dashboard.css     # Custom styles
│   └── js/
│       └── dashboard.js      # Dashboard logic
└── scripts/
    └── extract_biomarkers.py # PDF extraction script
```

## 💻 Usage Guide

### Dashboard Navigation

1. **Overview Cards** - Quick status of key biomarkers
2. **Main Chart** - Large time series visualization with type selector
3. **Individual Charts** - Detailed views by biomarker category
4. **Clinical Insights** - Automated health recommendations
5. **Date Range Filter** - Adjust time period displayed
6. **Export Function** - Download charts as PNG files

### Data Extraction

To extract biomarker data from PDF health reports:

```bash
python scripts/extract_biomarkers.py /path/to/pdf/reports /path/to/output.json
```

**Example:**
```bash
python scripts/extract_biomarkers.py ./sample_reports ./data/my_data.json
```

The script will:
- Extract biomarker values using regex patterns
- Handle unit conversions (mg/dL ↔ mmol/L, etc.)
- Parse dates and patient information
- Generate dashboard-ready JSON format

### Supported PDF Formats

The extraction script recognizes various biomarker naming conventions:
- Total Cholesterol, T.Chol, Cholesterol Total
- LDL, Low Density Lipoprotein, LDL Cholesterol
- HDL, High Density Lipoprotein, HDL Cholesterol
- Triglycerides, TG, Trigs
- Creatinine, Creat, Serum Creatinine
- Vitamin D, 25(OH)D, Vit D
- Vitamin B12, B12, Cobalamin
- HbA1c, Hemoglobin A1c, A1c

## 🎨 Dashboard Features

### Interactive Charts
- **Line Charts** with smooth animations
- **Multi-axis support** for different units
- **Hover tooltips** with clinical status
- **Zoom and pan** for detailed analysis
- **Legend toggling** to focus on specific biomarkers

### Clinical Range Visualization
- **Green zones** - Optimal/Normal ranges
- **Yellow zones** - Borderline/Warning ranges  
- **Red zones** - High risk/Abnormal ranges
- **Real-time status updates** on value changes

### Responsive Design
- **Mobile optimization** with touch-friendly controls
- **Tablet layout** with grid adjustments
- **Desktop experience** with full feature set
- **Print-friendly** styling for reports

## 🔬 Clinical Interpretations

The dashboard provides automated insights based on:

### Risk Assessment
- **Cardiovascular risk** from lipid profiles
- **Diabetes progression** from HbA1c trends
- **Kidney function** monitoring via creatinine
- **Nutritional status** through vitamin levels

### Trend Analysis
- **Improving trends** highlighted in green
- **Deteriorating trends** flagged with warnings
- **Stable values** marked appropriately
- **Intervention recommendations** when needed

### Professional Guidance
All clinical interpretations include disclaimers directing users to consult healthcare professionals for medical decisions.

## 🌐 Deployment Options

### Option 1: Replit (Recommended for Demo)
1. Import project to Replit
2. Install dependencies automatically
3. Run with built-in hosting
4. Share public URL

### Option 2: Vercel (Production Ready)
1. Connect GitHub repository
2. Configure build settings
3. Deploy with automatic SSL
4. Custom domain support

### Option 3: Heroku (Full Stack)
1. Create Heroku app
2. Configure Procfile
3. Deploy via Git
4. Scale as needed

### Environment Variables
- `PORT` - Server port (default: 3000)
- `NODE_ENV` - Environment (development/production)

## 🔒 Security Considerations

### Data Privacy
- **No PHI storage** - sample data only
- **Client-side processing** for data visualization
- **Secure headers** via Helmet.js
- **HTTPS enforcement** in production

### Input Validation
- **File type checking** for PDF uploads
- **Sanitized regex patterns** for extraction
- **Error handling** for malformed data
- **Rate limiting** for API endpoints

## 🧪 Testing Guide

### Manual Testing Scenarios

1. **Data Loading**
   - Verify all biomarkers load correctly
   - Check date parsing accuracy
   - Validate clinical range assignments

2. **Visualization**
   - Test all chart types render properly
   - Verify interactive features work
   - Check responsive layout across devices

3. **Filtering**
   - Test date range filtering
   - Verify chart type switching
   - Check export functionality

4. **Clinical Insights**
   - Validate risk assessments
   - Check trend calculations
   - Verify recommendation accuracy

### Performance Benchmarks
- **Initial load time** < 2 seconds
- **Chart rendering** < 500ms
- **Filter updates** < 100ms
- **Mobile responsiveness** maintained

## 📈 Future Enhancements

### Phase 2 Features
- [ ] **Multiple patient support**
- [ ] **Advanced analytics** (correlations, predictions)
- [ ] **PDF report generation**
- [ ] **Email notifications** for critical values
- [ ] **Data synchronization** with EHR systems

### Technical Improvements
- [ ] **Database integration** (PostgreSQL/MongoDB)
- [ ] **User authentication** and authorization
- [ ] **API rate limiting** and caching
- [ ] **Automated testing** suite
- [ ] **Docker containerization**

### Clinical Extensions
- [ ] **Additional biomarkers** (inflammatory markers, hormones)
- [ ] **Risk calculators** (Framingham, ASCVD)
- [ ] **Treatment recommendations** based on guidelines
- [ ] **Population health analytics**

## 🏥 Clinical Accuracy

All clinical ranges and interpretations are based on:
- **International clinical guidelines**
- **Peer-reviewed medical literature**
- **Healthcare institution standards**
- **Regulatory compliance** (FDA, Health Canada)

### References
- National Cholesterol Education Program ATP III
- American Diabetes Association Guidelines
- National Kidney Disease Education Program
- World Health Organization Standards

## 📞 Support & Contact

### Issues & Bug Reports
Please create detailed issue reports including:
- Browser version and OS
- Steps to reproduce
- Expected vs actual behavior
- Console error messages

### Feature Requests
Submit enhancement ideas with:
- Clinical use case description
- Expected user benefit
- Technical feasibility assessment

### Documentation
- **API Documentation** - Available at `/api/docs`
- **Developer Guide** - See `docs/developer.md`
- **Clinical Guide** - See `docs/clinical-reference.md`

## 📄 License

This project is developed as part of the EcoTown Health Tech internship assignment and is intended for educational and demonstration purposes.

### Disclaimer
This dashboard is for informational purposes only and should not replace professional medical advice, diagnosis, or treatment. Always consult qualified healthcare providers for medical decisions.

---

**Developed with ❤️ for EcoTown Health Tech**

*Demonstrating the intersection of technology and healthcare through innovative data visualization.*