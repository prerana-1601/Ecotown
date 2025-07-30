#!/usr/bin/env python3
"""
Enhanced Biomarker PDF Extractor
Designed to handle real health report PDFs with robust text extraction

This version includes:
- Multiple PDF libraries for better text extraction
- Advanced pattern matching for various lab report formats
- Better handling of tables and structured data
- OCR capabilities for scanned documents
"""

import json
import re
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import logging

# PDF Processing Libraries
try:
    import PyPDF2
    import pdfplumber
    import fitz  # PyMuPDF
    HAS_ADVANCED_PDF = True
except ImportError:
    import PyPDF2
    HAS_ADVANCED_PDF = False
    print("⚠️  Install pdfplumber and PyMuPDF for better extraction: pip install pdfplumber PyMuPDF")

# OCR Support (optional)
try:
    import pytesseract
    from PIL import Image
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedBiomarkerExtractor:
    """Enhanced biomarker extractor with multiple extraction methods."""
    
    def __init__(self):
        self.biomarker_patterns = self._create_comprehensive_patterns()
        self.unit_conversions = self._create_unit_conversions()
        self.extraction_methods = ['pdfplumber', 'pymupdf', 'pypdf2']
        
    def _create_comprehensive_patterns(self) -> Dict[str, List[str]]:
        """Create comprehensive regex patterns for biomarker extraction."""
        return {
            'total_cholesterol': [
                # Standard formats
                r'total\s+cholesterol[:\s-]*(\d+\.?\d*)\s*(mmol/l|mg/dl|mg%|mmol\/l)',
                r'cholesterol\s+total[:\s-]*(\d+\.?\d*)\s*(mmol/l|mg/dl|mg%|mmol\/l)',
                r'chol\s+total[:\s-]*(\d+\.?\d*)\s*(mmol/l|mg/dl|mg%|mmol\/l)',
                r't\.?\s*chol[:\s-]*(\d+\.?\d*)\s*(mmol/l|mg/dl|mg%|mmol\/l)',
                r'tc[:\s-]*(\d+\.?\d*)\s*(mmol/l|mg/dl|mg%|mmol\/l)',
                # Table formats
                r'total\s+cholesterol\s+(\d+\.?\d*)\s*(mmol/l|mg/dl|mg%|mmol\/l)?',
                r'cholesterol,?\s+total\s+(\d+\.?\d*)\s*(mmol/l|mg/dl|mg%|mmol\/l)?',
                # Lab report formats
                r'cholesterol\s*\(\s*total\s*\)[:\s-]*(\d+\.?\d*)\s*(mmol/l|mg/dl|mg%|mmol\/l)',
            ],
            'ldl': [
                r'ldl[:\s-]*(\d+\.?\d*)\s*(mmol/l|mg/dl|mg%|mmol\/l)',
                r'low\s+density\s+lipoprotein[:\s-]*(\d+\.?\d*)\s*(mmol/l|mg/dl|mg%|mmol\/l)',
                r'ldl\s+cholesterol[:\s-]*(\d+\.?\d*)\s*(mmol/l|mg/dl|mg%|mmol\/l)',
                r'ldl\s+chol[:\s-]*(\d+\.?\d*)\s*(mmol/l|mg/dl|mg%|mmol\/l)',
                r'l\.?\s*d\.?\s*l\.?[:\s-]*(\d+\.?\d*)\s*(mmol/l|mg/dl|mg%|mmol\/l)',
                r'cholesterol\s*\(\s*ldl\s*\)[:\s-]*(\d+\.?\d*)\s*(mmol/l|mg/dl|mg%|mmol\/l)',
                r'ldl\s+(\d+\.?\d*)\s*(mmol/l|mg/dl|mg%|mmol\/l)?',
            ],
            'hdl': [
                r'hdl[:\s-]*(\d+\.?\d*)\s*(mmol/l|mg/dl|mg%|mmol\/l)',
                r'high\s+density\s+lipoprotein[:\s-]*(\d+\.?\d*)\s*(mmol/l|mg/dl|mg%|mmol\/l)',
                r'hdl\s+cholesterol[:\s-]*(\d+\.?\d*)\s*(mmol/l|mg/dl|mg%|mmol\/l)',
                r'hdl\s+chol[:\s-]*(\d+\.?\d*)\s*(mmol/l|mg/dl|mg%|mmol\/l)',
                r'h\.?\s*d\.?\s*l\.?[:\s-]*(\d+\.?\d*)\s*(mmol/l|mg/dl|mg%|mmol\/l)',
                r'cholesterol\s*\(\s*hdl\s*\)[:\s-]*(\d+\.?\d*)\s*(mmol/l|mg/dl|mg%|mmol\/l)',
                r'hdl\s+(\d+\.?\d*)\s*(mmol/l|mg/dl|mg%|mmol\/l)?',
            ],
            'triglycerides': [
                r'triglycerides?[:\s-]*(\d+\.?\d*)\s*(mmol/l|mg/dl|mg%|mmol\/l)',
                r'tg[:\s-]*(\d+\.?\d*)\s*(mmol/l|mg/dl|mg%|mmol\/l)',
                r'trigs?[:\s-]*(\d+\.?\d*)\s*(mmol/l|mg/dl|mg%|mmol\/l)',
                r'tri\s*glycerides?[:\s-]*(\d+\.?\d*)\s*(mmol/l|mg/dl|mg%|mmol\/l)',
                r'triglyceride\s+(\d+\.?\d*)\s*(mmol/l|mg/dl|mg%|mmol\/l)?',
            ],
            'creatinine': [
                r'creatinine[:\s-]*(\d+\.?\d*)\s*(μmol/l|umol/l|mg/dl|mg%|µmol/l|mmol/l)',
                r'creat[:\s-]*(\d+\.?\d*)\s*(μmol/l|umol/l|mg/dl|mg%|µmol/l|mmol/l)',
                r'serum\s+creatinine[:\s-]*(\d+\.?\d*)\s*(μmol/l|umol/l|mg/dl|mg%|µmol/l|mmol/l)',
                r'crea[:\s-]*(\d+\.?\d*)\s*(μmol/l|umol/l|mg/dl|mg%|µmol/l|mmol/l)',
                r'creatinine\s+(\d+\.?\d*)\s*(μmol/l|umol/l|mg/dl|mg%|µmol/l|mmol/l)?',
            ],
            'vitamin_d': [
                r'vitamin\s+d[:\s-]*(\d+\.?\d*)\s*(ng/ml|nmol/l|ng\/ml|nmol\/l)',
                r'25\s*\(\s*oh\s*\)\s*d[:\s-]*(\d+\.?\d*)\s*(ng/ml|nmol/l|ng\/ml|nmol\/l)',
                r'vit\s*d[:\s-]*(\d+\.?\d*)\s*(ng/ml|nmol/l|ng\/ml|nmol\/l)',
                r'25\s+hydroxyvitamin\s+d[:\s-]*(\d+\.?\d*)\s*(ng/ml|nmol/l|ng\/ml|nmol\/l)',
                r'25\s*oh\s*d[:\s-]*(\d+\.?\d*)\s*(ng/ml|nmol/l|ng\/ml|nmol\/l)',
                r'vitamin\s*d\s*3[:\s-]*(\d+\.?\d*)\s*(ng/ml|nmol/l|ng\/ml|nmol\/l)',
                r'cholecalciferol[:\s-]*(\d+\.?\d*)\s*(ng/ml|nmol/l|ng\/ml|nmol\/l)',
            ],
            'vitamin_b12': [
                r'vitamin\s+b12[:\s-]*(\d+\.?\d*)\s*(pg/ml|pmol/l|pg\/ml|pmol\/l|ng/ml)',
                r'b12[:\s-]*(\d+\.?\d*)\s*(pg/ml|pmol/l|pg\/ml|pmol\/l|ng/ml)',
                r'cobalamin[:\s-]*(\d+\.?\d*)\s*(pg/ml|pmol/l|pg\/ml|pmol\/l|ng/ml)',
                r'cyanocobalamin[:\s-]*(\d+\.?\d*)\s*(pg/ml|pmol/l|pg\/ml|pmol\/l|ng/ml)',
                r'b\s*12[:\s-]*(\d+\.?\d*)\s*(pg/ml|pmol/l|pg\/ml|pmol\/l|ng/ml)',
                r'vitamin\s*b\s*12[:\s-]*(\d+\.?\d*)\s*(pg/ml|pmol/l|pg\/ml|pmol\/l|ng/ml)',
            ],
            'hba1c': [
                r'hba1c[:\s-]*(\d+\.?\d*)\s*%?',
                r'hemoglobin\s+a1c[:\s-]*(\d+\.?\d*)\s*%?',
                r'glycated\s+h[ae]moglobin[:\s-]*(\d+\.?\d*)\s*%?',
                r'a1c[:\s-]*(\d+\.?\d*)\s*%?',
                r'hb\s*a1c[:\s-]*(\d+\.?\d*)\s*%?',
                r'haemoglobin\s+a1c[:\s-]*(\d+\.?\d*)\s*%?',
                r'glycated\s+hb[:\s-]*(\d+\.?\d*)\s*%?',
                r'hba1c\s+(\d+\.?\d*)\s*%?',
            ]
        }
    
    def _create_unit_conversions(self) -> Dict[str, callable]:
        """Create unit conversion functions."""
        return {
            'cholesterol_mg_to_mmol': lambda x: x * 0.02586,
            'cholesterol_mmol_to_mg': lambda x: x / 0.02586,
            'triglycerides_mg_to_mmol': lambda x: x * 0.01129,
            'triglycerides_mmol_to_mg': lambda x: x / 0.01129,
            'creatinine_mg_to_umol': lambda x: x * 88.4,
            'creatinine_umol_to_mg': lambda x: x / 88.4,
            'vitamin_d_nmol_to_ng': lambda x: x * 0.4,
            'vitamin_d_ng_to_nmol': lambda x: x / 0.4,
            'vitamin_b12_pmol_to_pg': lambda x: x * 1.355,
            'vitamin_b12_pg_to_pmol': lambda x: x / 1.355,
        }

    def extract_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Extract biomarker data using the best available method."""
        logger.info(f"Processing PDF: {pdf_path}")
        
        # Try different extraction methods
        for method in self.extraction_methods:
            try:
                if method == 'pdfplumber' and HAS_ADVANCED_PDF:
                    text = self._extract_with_pdfplumber(pdf_path)
                elif method == 'pymupdf' and HAS_ADVANCED_PDF:
                    text = self._extract_with_pymupdf(pdf_path)
                elif method == 'pypdf2':
                    text = self._extract_with_pypdf2(pdf_path)
                else:
                    continue
                
                if text and len(text.strip()) > 50:  # Valid extraction
                    logger.info(f"Successfully extracted text using {method}")
                    return self.parse_text(text, pdf_path, method)
                    
            except Exception as e:
                logger.warning(f"Method {method} failed: {e}")
                continue
        
        # Fallback to OCR if available
        if HAS_OCR:
            logger.info("Attempting OCR extraction...")
            try:
                text = self._extract_with_ocr(pdf_path)
                if text:
                    return self.parse_text(text, pdf_path, 'ocr')
            except Exception as e:
                logger.error(f"OCR extraction failed: {e}")
        
        logger.error(f"Failed to extract text from {pdf_path}")
        return {}

    def _extract_with_pdfplumber(self, pdf_path: str) -> str:
        """Extract text using pdfplumber (best for tables)."""
        import pdfplumber
        
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                # Extract regular text
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- Page {page_num + 1} ---\n"
                    text += page_text
                
                # Extract tables
                tables = page.extract_tables()
                for table_num, table in enumerate(tables):
                    text += f"\n--- Table {table_num + 1} on Page {page_num + 1} ---\n"
                    for row in table:
                        if row:
                            text += " | ".join(str(cell) if cell else "" for cell in row) + "\n"
        
        return text

    def _extract_with_pymupdf(self, pdf_path: str) -> str:
        """Extract text using PyMuPDF (good for layout preservation)."""
        import fitz
        
        text = ""
        doc = fitz.open(pdf_path)
        
        for page_num in range(doc.page_count):
            page = doc[page_num]
            text += f"\n--- Page {page_num + 1} ---\n"
            text += page.get_text()
        
        doc.close()
        return text

    def _extract_with_pypdf2(self, pdf_path: str) -> str:
        """Extract text using PyPDF2 (basic extraction)."""
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    text += f"\n--- Page {page_num + 1} ---\n"
                    text += page_text
        
        return text

    def _extract_with_ocr(self, pdf_path: str) -> str:
        """Extract text using OCR (for scanned documents)."""
        import fitz
        import pytesseract
        from PIL import Image
        import io
        
        text = ""
        doc = fitz.open(pdf_path)
        
        for page_num in range(doc.page_count):
            page = doc[page_num]
            
            # Convert page to image
            mat = fitz.Matrix(2.0, 2.0)  # Increase resolution
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            
            # OCR the image
            image = Image.open(io.BytesIO(img_data))
            page_text = pytesseract.image_to_string(image)
            
            if page_text.strip():
                text += f"\n--- Page {page_num + 1} (OCR) ---\n"
                text += page_text
        
        doc.close()
        return text

    def parse_text(self, text: str, source_file: str, method: str) -> Dict[str, Any]:
        """Parse biomarker values from extracted text."""
        # Clean and prepare text
        text = self._clean_text(text)
        
        # Extract components
        date = self.extract_date(text)
        patient_info = self.extract_patient_info(text)
        biomarkers = self.extract_all_biomarkers(text)
        
        # Create result
        result = {
            'date': date,
            'source_file': source_file,
            'extraction_method': method,
            'biomarkers': biomarkers,
            'patient_info': patient_info,
            'raw_text_sample': text[:500] + "..." if len(text) > 500 else text
        }
        
        logger.info(f"Extracted {len(biomarkers)} biomarkers from {source_file}")
        return result

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for better pattern matching."""
        # Convert to lowercase for pattern matching
        text = text.lower()
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Normalize punctuation
        text = re.sub(r'[:\-\s]*=\s*', ': ', text)
        text = re.sub(r'(\d+)\s*\.\s*(\d+)', r'\1.\2', text)  # Fix decimal numbers
        
        # Common replacements
        text = text.replace('μ', 'u')  # Greek mu to u
        text = text.replace('µ', 'u')  # Micro sign to u
        
        return text

    def extract_all_biomarkers(self, text: str) -> Dict[str, float]:
        """Extract all biomarkers from text."""
        biomarkers = {}
        
        for biomarker, patterns in self.biomarker_patterns.items():
            value = self.extract_biomarker(text, patterns, biomarker)
            if value is not None:
                biomarkers[biomarker] = value
                logger.debug(f"Found {biomarker}: {value}")
        
        return biomarkers

    def extract_biomarker(self, text: str, patterns: List[str], biomarker: str) -> Optional[float]:
        """Extract a specific biomarker value from text."""
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                try:
                    value = float(match.group(1))
                    unit = match.group(2).lower() if len(match.groups()) > 1 and match.group(2) else ''
                    
                    # Convert units if necessary
                    converted_value = self.convert_units(value, unit, biomarker)
                    
                    # Validate range (basic sanity check)
                    if self._is_reasonable_value(biomarker, converted_value):
                        return converted_value
                    
                except (ValueError, IndexError) as e:
                    logger.debug(f"Failed to parse match for {biomarker}: {e}")
                    continue
        
        return None

    def _is_reasonable_value(self, biomarker: str, value: float) -> bool:
        """Basic sanity check for biomarker values."""
        reasonable_ranges = {
            'total_cholesterol': (1.0, 20.0),  # mmol/L
            'ldl': (0.5, 15.0),                # mmol/L
            'hdl': (0.3, 5.0),                 # mmol/L
            'triglycerides': (0.1, 20.0),     # mmol/L
            'creatinine': (20, 1000),          # μmol/L
            'vitamin_d': (5, 300),             # ng/mL
            'vitamin_b12': (50, 5000),         # pg/mL
            'hba1c': (3.0, 20.0),            # %
        }
        
        min_val, max_val = reasonable_ranges.get(biomarker, (0, float('inf')))
        return min_val <= value <= max_val

    def convert_units(self, value: float, unit: str, biomarker: str) -> float:
        """Convert biomarker values to standard units."""
        unit = unit.lower().replace(' ', '').replace('/', '')
        
        # Cholesterol conversions
        if biomarker in ['total_cholesterol', 'ldl', 'hdl']:
            if 'mgdl' in unit or 'mg%' in unit:
                return self.unit_conversions['cholesterol_mg_to_mmol'](value)
        
        # Triglycerides conversions
        elif biomarker == 'triglycerides':
            if 'mgdl' in unit or 'mg%' in unit:
                return self.unit_conversions['triglycerides_mg_to_mmol'](value)
        
        # Creatinine conversions
        elif biomarker == 'creatinine':
            if 'mgdl' in unit or 'mg%' in unit:
                return self.unit_conversions['creatinine_mg_to_umol'](value)
        
        # Vitamin D conversions
        elif biomarker == 'vitamin_d':
            if 'nmoll' in unit:
                return self.unit_conversions['vitamin_d_nmol_to_ng'](value)
        
        # Vitamin B12 conversions
        elif biomarker == 'vitamin_b12':
            if 'pmoll' in unit:
                return self.unit_conversions['vitamin_b12_pmol_to_pg'](value)
            elif 'ngml' in unit:
                return value * 1000  # ng/mL to pg/mL
        
        return value

    def extract_date(self, text: str) -> str:
        """Extract test date from text with improved patterns."""
        date_patterns = [
            # Standard formats
            r'date[:\s-]*(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})',
            r'test\s+date[:\s-]*(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})',
            r'report\s+date[:\s-]*(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})',
            r'collected[:\s-]*(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})',
            r'sample\s+date[:\s-]*(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})',
            # ISO format
            r'(\d{4}[/\-\.]\d{1,2}[/\-\.]\d{1,2})',
            # Month name formats
            r'(\d{1,2}\s+(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{2,4})',
            # General date patterns
            r'(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    date_str = match.group(1)
                    # Try to parse the date
                    for fmt in ['%d/%m/%Y', '%m/%d/%Y', '%Y/%m/%d', 
                               '%d-%m-%Y', '%m-%d-%Y', '%Y-%m-%d',
                               '%d.%m.%Y', '%m.%d.%Y', '%Y.%m.%d',
                               '%d/%m/%y', '%m/%d/%y', '%y/%m/%d']:
                        try:
                            parsed_date = datetime.strptime(date_str, fmt)
                            return parsed_date.strftime('%Y-%m-%d')
                        except ValueError:
                            continue
                except Exception:
                    pass
        
        # Return current date if no date found
        return datetime.now().strftime('%Y-%m-%d')

    def extract_patient_info(self, text: str) -> Dict[str, str]:
        """Extract patient information with improved patterns."""
        patient_info = {}
        
        # Name patterns
        name_patterns = [
            r'patient[:\s-]+([a-z\s,\.]+?)(?:\n|dob|age|gender|sex|male|female)',
            r'name[:\s-]+([a-z\s,\.]+?)(?:\n|dob|age|gender|sex|male|female)',
            r'mr\.?\s+([a-z\s]+?)(?:\n|dob|age|gender|sex)',
            r'ms\.?\s+([a-z\s]+?)(?:\n|dob|age|gender|sex)',
            r'mrs\.?\s+([a-z\s]+?)(?:\n|dob|age|gender|sex)',
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                name = match.group(1).strip()
                name = re.sub(r'\s+', ' ', name)  # Normalize whitespace
                if 2 < len(name) < 50 and not re.search(r'\d', name):
                    patient_info['name'] = name.title()
                    break
        
        # Age patterns
        age_patterns = [
            r'age[:\s-]*(\d{1,3})',
            r'(\d{1,3})\s+years?\s+old',
            r'yrs?[:\s-]*(\d{1,3})',
            r'age\s*\(\s*years?\s*\)[:\s-]*(\d{1,3})',
        ]
        
        for pattern in age_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    age = int(match.group(1))
                    if 0 <= age <= 150:
                        patient_info['age'] = str(age)
                        break
                except ValueError:
                    continue
        
        # Gender patterns
        gender_patterns = [
            r'gender[:\s-]+(male|female|m|f)\b',
            r'sex[:\s-]+(male|female|m|f)\b',
            r'\b(male|female)\b',
            r'mr\.|mrs\.|ms\.',
        ]
        
        for pattern in gender_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                gender_text = match.group(0).lower()
                if 'male' in gender_text and 'female' not in gender_text:
                    patient_info['gender'] = 'Male'
                    break
                elif 'female' in gender_text:
                    patient_info['gender'] = 'Female'
                    break
                elif gender_text in ['m']:
                    patient_info['gender'] = 'Male'
                    break
                elif gender_text in ['f']:
                    patient_info['gender'] = 'Female'
                    break
                elif 'mr.' in gender_text:
                    patient_info['gender'] = 'Male'
                    break
                elif 'mrs.' in gender_text or 'ms.' in gender_text:
                    patient_info['gender'] = 'Female'
                    break
        
        return patient_info

    def analyze_pdf_structure(self, pdf_path: str) -> Dict[str, Any]:
        """Analyze PDF structure to help debug extraction issues."""
        analysis = {
            'file_size': os.path.getsize(pdf_path),
            'extraction_results': {},
            'text_samples': {},
            'page_count': 0
        }
        
        # Try each extraction method
        for method in self.extraction_methods:
            try:
                if method == 'pdfplumber' and HAS_ADVANCED_PDF:
                    text = self._extract_with_pdfplumber(pdf_path)
                elif method == 'pymupdf' and HAS_ADVANCED_PDF:
                    text = self._extract_with_pymupdf(pdf_path)
                elif method == 'pypdf2':
                    text = self._extract_with_pypdf2(pdf_path)
                else:
                    continue
                
                analysis['extraction_results'][method] = {
                    'success': True,
                    'text_length': len(text) if text else 0,
                    'has_content': bool(text and text.strip())
                }
                
                if text:
                    analysis['text_samples'][method] = text[:300] + "..." if len(text) > 300 else text
                    
            except Exception as e:
                analysis['extraction_results'][method] = {
                    'success': False,
                    'error': str(e)
                }
        
        return analysis

def main():
    """Main function to run the enhanced extraction."""
    if len(sys.argv) < 2:
        print("Usage: python enhanced_pdf_extractor.py <pdf_file_or_directory> [output_file]")
        print("\nExamples:")
        print("  python enhanced_pdf_extractor.py health_report.pdf")
        print("  python enhanced_pdf_extractor.py ./reports/ extracted_data.json")
        print("  python enhanced_pdf_extractor.py report.pdf --analyze")
        return 1
    
    input_path = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else None
    analyze_only = '--analyze' in sys.argv
    
    extractor = AdvancedBiomarkerExtractor()
    
    # Single file processing
    if os.path.isfile(input_path) and input_path.lower().endswith('.pdf'):
        if analyze_only:
            print(f"🔍 Analyzing PDF structure: {input_path}")
            analysis = extractor.analyze_pdf_structure(input_path)
            print(json.dumps(analysis, indent=2))
            return 0
        
        print(f"📄 Processing PDF: {input_path}")
        result = extractor.extract_from_pdf(input_path)
        
        if result and result.get('biomarkers'):
            print(f"✅ Found {len(result['biomarkers'])} biomarkers:")
            for biomarker, value in result['biomarkers'].items():
                print(f"   • {biomarker}: {value}")
            
            if output_file:
                with open(output_file, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"💾 Saved results to: {output_file}")
        else:
            print("❌ No biomarkers found")
            if '--verbose' in sys.argv and result:
                print("Raw text sample:")
                print(result.get('raw_text_sample', 'No text extracted'))
    
    # Directory processing
    elif os.path.isdir(input_path):
        pdf_files = list(Path(input_path).glob("*.pdf"))
        if not pdf_files:
            print(f"❌ No PDF files found in {input_path}")
            return 1
        
        print(f"📁 Processing {len(pdf_files)} PDF files...")
        all_results = []
        
        for pdf_file in pdf_files:
            print(f"📄 Processing: {pdf_file.name}")
            result = extractor.extract_from_pdf(str(pdf_file))
            
            if result and result.get('biomarkers'):
                all_results.append(result)
                print(f"   ✅ Found {len(result['biomarkers'])} biomarkers")
            else:
                print(f"   ⚠️  No biomarkers found")
        
        # Consolidate results
        if all_results:
            consolidated = consolidate_results(all_results)
            output_file = output_file or 'extracted_biomarkers.json'
            
            with open(output_file, 'w') as f:
                json.dump(consolidated, f, indent=2)
            
            print(f"\n✅ Processed {len(all_results)} files successfully")
            print(f"💾 Consolidated data saved to: {output_file}")
            print(f"📊 Total biomarker records: {len(consolidated.get('biomarkers', []))}")
        else:
            print("\n❌ No biomarkers extracted from any files")
    
    else:
        print(f"❌ Invalid input: {input_path}")
        print("Please provide a PDF file or directory containing PDF files")
        return 1
    
    return 0

def consolidate_results(results: List[Dict]) -> Dict[str, Any]:
    """Consolidate multiple extraction results."""
    biomarkers = []
    patient_info = {}
    
    for result in results:
        if result.get('biomarkers'):
            biomarker_entry = {
                'date': result['date'],
                **result['biomarkers']
            }
            biomarkers.append(biomarker_entry)
        
        # Use the first available patient info
        if not patient_info and result.get('patient_info'):
            patient_info = result['patient_info']
    
    # Sort by date
    biomarkers.sort(key=lambda x: x['date'])
    
    # Add default patient info if none found
    if not patient_info:
        patient_info = {
            'name': 'Patient',
            'age': 'Unknown',
            'gender': 'Unknown',
            'patient_id': 'P001'
        }
    else:
        patient_info.setdefault('patient_id', 'P001')
    
    # Add clinical ranges
    clinical_ranges = get_clinical_ranges()
    
    return {
        'patient_info': patient_info,
        'biomarkers': biomarkers,
        'clinical_ranges': clinical_ranges,
        'extraction_summary': {
            'total_files_processed': len(results),
            'total_records': len(biomarkers),
            'date_range': {
                'earliest': min([b['date'] for b in biomarkers]) if biomarkers else None,
                'latest': max([b['date'] for b in biomarkers]) if biomarkers else None
            }
        }
    }

def get_clinical_ranges() -> Dict[str, Any]:
    """Return comprehensive clinical ranges."""
    return {
        "total_cholesterol": {
            "unit": "mmol/L",
            "ranges": {
                "optimal": {"min": 0, "max": 5.2, "color": "#22c55e"},
                "borderline": {"min": 5.2, "max": 6.1, "color": "#f59e0b"},
                "high": {"min": 6.1, "max": 10, "color": "#ef4444"}
            }
        },
        "ldl": {
            "unit": "mmol/L", 
            "ranges": {
                "optimal": {"min": 0, "max": 2.6, "color": "#22c55e"},
                "near_optimal": {"min": 2.6, "max": 3.3, "color": "#84cc16"},
                "borderline": {"min": 3.4, "max": 4.1, "color": "#f59e0b"},
                "high": {"min": 4.2, "max": 4.9, "color": "#f97316"},
                "very_high": {"min": 4.9, "max": 10, "color": "#ef4444"}
            }
        },
        "hdl": {
            "unit": "mmol/L",
            "ranges": {
                "low_risk": {"min": 1.53, "max": 5, "color": "#22c55e"},
                "average_risk": {"min": 1.03, "max": 1.53, "color": "#f59e0b"},
                "high_risk": {"min": 0, "max": 1.03, "color": "#ef4444"}
            }
        },
        "triglycerides": {
            "unit": "mmol/L",
            "ranges": {
                "desirable": {"min": 0, "max": 1.69, "color": "#22c55e"},
                "borderline": {"min": 1.69, "max": 2.25, "color": "#f59e0b"},
                "high": {"min": 2.26, "max": 5.63, "color": "#f97316"},
                "very_high": {"min": 5.63, "max": 10, "color": "#ef4444"}
            }
        },
        "creatinine": {
            "unit": "μmol/L",
            "ranges": {
                "normal": {"min": 70, "max": 120, "color": "#22c55e"},
                "elevated": {"min": 120, "max": 200, "color": "#f59e0b"},
                "high": {"min": 200, "max": 500, "color": "#ef4444"}
            }
        },
        "vitamin_d": {
            "unit": "ng/mL",
            "ranges": {
                "deficient": {"min": 0, "max": 20, "color": "#ef4444"},
                "insufficient": {"min": 20, "max": 30, "color": "#f59e0b"},
                "sufficient": {"min": 30, "max": 100, "color": "#22c55e"},
                "excess": {"min": 100, "max": 200, "color": "#f97316"}
            }
        },
        "vitamin_b12": {
            "unit": "pg/mL",
            "ranges": {
                "deficient": {"min": 0, "max": 200, "color": "#ef4444"},
                "low_normal": {"min": 200, "max": 400, "color": "#f59e0b"},
                "normal": {"min": 400, "max": 900, "color": "#22c55e"},
                "high": {"min": 900, "max": 2000, "color": "#84cc16"}
            }
        },
        "hba1c": {
            "unit": "%",
            "ranges": {
                "normal": {"min": 0, "max": 6.0, "color": "#22c55e"},
                "prediabetes": {"min": 6.0, "max": 6.4, "color": "#f59e0b"},
                "diabetes": {"min": 6.5, "max": 15, "color": "#ef4444"}
            }
        }
    }

if __name__ == "__main__":
    exit(main())