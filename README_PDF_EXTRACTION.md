# 🔬 PDF Biomarker Extraction Guide

## Overview

This enhanced PDF extractor is designed to handle real health report PDFs with multiple extraction methods and robust pattern matching for biomarkers.

## 📋 Supported Biomarkers

| Biomarker | Common Names | Units | Extraction Patterns |
|-----------|--------------|-------|-------------------|
| **Total Cholesterol** | TC, Chol Total, Cholesterol Total | mmol/L, mg/dL | ✅ Multiple formats |
| **LDL Cholesterol** | LDL, L.D.L., Low Density Lipoprotein | mmol/L, mg/dL | ✅ Multiple formats |
| **HDL Cholesterol** | HDL, H.D.L., High Density Lipoprotein | mmol/L, mg/dL | ✅ Multiple formats |
| **Triglycerides** | TG, Trigs, Triglyceride | mmol/L, mg/dL | ✅ Multiple formats |
| **Creatinine** | Creat, Crea, Serum Creatinine | μmol/L, mg/dL | ✅ Multiple formats |
| **Vitamin D** | Vit D, 25(OH)D, 25-Hydroxyvitamin D | ng/mL, nmol/L | ✅ Multiple formats |
| **Vitamin B12** | B12, Cobalamin, Cyanocobalamin | pg/mL, pmol/L | ✅ Multiple formats |
| **HbA1c** | A1c, Hemoglobin A1c, Glycated Hb | % | ✅ Multiple formats |

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Basic Usage

```bash
# Process a single PDF
python scripts/enhanced_pdf_extractor.py your_health_report.pdf

# Process multiple PDFs in a directory
python scripts/enhanced_pdf_extractor.py ./health_reports/

# Save results to specific file
python scripts/enhanced_pdf_extractor.py report.pdf extracted_data.json

# Analyze PDF structure (debugging)
python scripts/enhanced_pdf_extractor.py report.pdf --analyze
```

## 📊 Extraction Methods

The extractor uses multiple methods in priority order:

### 1. **PDFPlumber** (Recommended)
- ✅ Best for structured tables
- ✅ Handles complex layouts
- ✅ Extracts table data accurately
- 🎯 **Use for**: Lab reports with tabular data

### 2. **PyMuPDF (Fitz)**
- ✅ Good layout preservation
- ✅ Fast extraction
- ✅ Handles text positioning
- 🎯 **Use for**: Well-formatted text reports

### 3. **PyPDF2** (Fallback)
- ✅ Basic text extraction
- ✅ Widely compatible
- ⚠️ Limited formatting support
- 🎯 **Use for**: Simple text-based reports

### 4. **OCR (Tesseract)** (Last Resort)
- ✅ Handles scanned documents
- ✅ Works with image-based PDFs
- ⚠️ Slower processing
- 🎯 **Use for**: Scanned or image-based reports

## 🔍 Pattern Matching Examples

The extractor recognizes various biomarker formats:

### Total Cholesterol
- `Total Cholesterol: 5.2 mmol/L`
- `Cholesterol Total 201 mg/dL`
- `TC: 5.8 mmol/L`
- `Cholesterol (Total): 195 mg/dL`

### LDL Cholesterol
- `LDL: 3.2 mmol/L`
- `Low Density Lipoprotein 125 mg/dL`
- `LDL Cholesterol: 2.8 mmol/L`
- `Cholesterol (LDL): 110 mg/dL`

### Creatinine
- `Creatinine: 95 μmol/L`
- `Serum Creatinine 1.1 mg/dL`
- `Creat: 88 umol/L`

### Vitamin D
- `Vitamin D: 45 ng/mL`
- `25(OH)D: 112 nmol/L`
- `25-Hydroxyvitamin D: 38 ng/mL`

## 🧪 Example Usage with Your PDFs

Once you provide your PDF files, here's how to use the extractor:

### Step 1: Place Your PDFs
```bash
# Create a directory for your health reports
mkdir my_health_reports
# Copy your 2 PDFs there
cp report1.pdf report2.pdf my_health_reports/
```

### Step 2: Extract Data
```bash
# Process both PDFs and create dashboard data
python scripts/enhanced_pdf_extractor.py my_health_reports/ data/my_biomarker_data.json
```

### Step 3: View Results
```bash
# Check what was extracted
cat data/my_biomarker_data.json
```

### Step 4: Update Dashboard
```bash
# Replace the sample data with your real data
cp data/my_biomarker_data.json data/sample_biomarker_data.json

# Start the dashboard
npm start
```

## 🔧 Advanced Features

### Unit Conversion
Automatic conversion between common units:
- **Cholesterol**: mg/dL ↔ mmol/L
- **Triglycerides**: mg/dL ↔ mmol/L  
- **Creatinine**: mg/dL ↔ μmol/L
- **Vitamin D**: nmol/L ↔ ng/mL
- **Vitamin B12**: pmol/L ↔ pg/mL

### Data Validation
- **Range checking** for reasonable values
- **Unit detection** and automatic conversion
- **Duplicate filtering** for multiple matches
- **Date parsing** with multiple formats

### Debug Mode
```bash
# Analyze PDF structure
python scripts/enhanced_pdf_extractor.py report.pdf --analyze

# Verbose output
python scripts/enhanced_pdf_extractor.py report.pdf --verbose
```

## 🎯 Optimization Tips

### For Best Results:
1. **Use high-quality PDFs** (not scanned if possible)
2. **Ensure text is selectable** in the PDF
3. **Check file size** (< 10MB recommended)
4. **Verify biomarker names** match common patterns

### If Extraction Fails:
1. **Try analysis mode**: `--analyze` flag
2. **Check text extraction**: Look at raw text sample
3. **Manual preprocessing**: Convert to text-searchable PDF
4. **OCR option**: Install Tesseract for scanned documents

## 📁 Output Format

The extractor creates JSON files compatible with the dashboard:

```json
{
  "patient_info": {
    "name": "John Doe",
    "age": "45",
    "gender": "Male",
    "patient_id": "P001"
  },
  "biomarkers": [
    {
      "date": "2024-01-15",
      "total_cholesterol": 5.8,
      "ldl": 3.2,
      "hdl": 1.2,
      "triglycerides": 1.8,
      "creatinine": 95,
      "vitamin_d": 45,
      "vitamin_b12": 380,
      "hba1c": 5.2
    }
  ],
  "clinical_ranges": { /* Clinical reference ranges */ },
  "extraction_summary": {
    "total_files_processed": 2,
    "total_records": 2,
    "date_range": {
      "earliest": "2024-01-15",
      "latest": "2024-02-15"
    }
  }
}
```

## 🚨 Troubleshooting

### Common Issues:

#### "No biomarkers found"
- **Check PDF format**: Ensure text is extractable
- **Verify naming**: Look for standard biomarker names
- **Try analysis mode**: `--analyze` to see extracted text

#### "Unit conversion errors"
- **Check units**: Ensure standard units (mmol/L, mg/dL, etc.)
- **Format consistency**: Numbers should be properly formatted

#### "Date parsing issues"
- **Standard formats**: Use DD/MM/YYYY or MM/DD/YYYY
- **Include keywords**: "Date:", "Test Date:", "Report Date:"

#### "OCR not working"
- **Install Tesseract**: `apt-get install tesseract-ocr` (Linux)
- **Install PyTesseract**: Already in requirements.txt
- **Check image quality**: Higher resolution = better OCR

## 📞 Need Help?

If you encounter issues with your specific PDF formats:

1. **Run analysis**: `python scripts/enhanced_pdf_extractor.py your_report.pdf --analyze`
2. **Check the output**: Look at extracted text samples
3. **Share the analysis**: Provide the structure analysis for debugging

## 🎉 Ready to Process Your PDFs!

Once you provide your 2 health report PDFs, I can:
1. **Analyze their structure**
2. **Optimize extraction patterns** for your specific format
3. **Extract the biomarker data**
4. **Generate dashboard-ready JSON**
5. **Update the visualization** with your real data

Just upload your PDFs and let's get started! 🚀