#!/usr/bin/env python3
"""
Biomarker Data Extraction Script
EcoTown Health Tech Internship Assignment

This script extracts biomarker data from health report PDFs and converts
them into structured JSON format for the dashboard.
"""

import json
import re
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
import PyPDF2
import pandas as pd
from pathlib import Path

class BiomarkerExtractor:
    """Extract biomarker data from health report PDFs."""
    
    def __init__(self):
        self.biomarker_patterns = {
            'total_cholesterol': [
                r'total\s+cholesterol[:\s]+(\d+\.?\d*)\s*(mmol/l|mg/dl)',
                r'cholesterol\s+total[:\s]+(\d+\.?\d*)\s*(mmol/l|mg/dl)',
                r't\.?\s*chol[:\s]+(\d+\.?\d*)\s*(mmol/l|mg/dl)'
            ],
            'ldl': [
                r'ldl[:\s]+(\d+\.?\d*)\s*(mmol/l|mg/dl)',
                r'low\s+density\s+lipoprotein[:\s]+(\d+\.?\d*)\s*(mmol/l|mg/dl)',
                r'ldl\s+cholesterol[:\s]+(\d+\.?\d*)\s*(mmol/l|mg/dl)'
            ],
            'hdl': [
                r'hdl[:\s]+(\d+\.?\d*)\s*(mmol/l|mg/dl)',
                r'high\s+density\s+lipoprotein[:\s]+(\d+\.?\d*)\s*(mmol/l|mg/dl)',
                r'hdl\s+cholesterol[:\s]+(\d+\.?\d*)\s*(mmol/l|mg/dl)'
            ],
            'triglycerides': [
                r'triglycerides?[:\s]+(\d+\.?\d*)\s*(mmol/l|mg/dl)',
                r'tg[:\s]+(\d+\.?\d*)\s*(mmol/l|mg/dl)',
                r'trigs?[:\s]+(\d+\.?\d*)\s*(mmol/l|mg/dl)'
            ],
            'creatinine': [
                r'creatinine[:\s]+(\d+\.?\d*)\s*(μmol/l|umol/l|mg/dl)',
                r'creat[:\s]+(\d+\.?\d*)\s*(μmol/l|umol/l|mg/dl)',
                r'serum\s+creatinine[:\s]+(\d+\.?\d*)\s*(μmol/l|umol/l|mg/dl)'
            ],
            'vitamin_d': [
                r'vitamin\s+d[:\s]+(\d+\.?\d*)\s*(ng/ml|nmol/l)',
                r'25\s*\(\s*oh\s*\)\s*d[:\s]+(\d+\.?\d*)\s*(ng/ml|nmol/l)',
                r'vit\s*d[:\s]+(\d+\.?\d*)\s*(ng/ml|nmol/l)',
                r'25\s+hydroxyvitamin\s+d[:\s]+(\d+\.?\d*)\s*(ng/ml|nmol/l)'
            ],
            'vitamin_b12': [
                r'vitamin\s+b12[:\s]+(\d+\.?\d*)\s*(pg/ml|pmol/l)',
                r'b12[:\s]+(\d+\.?\d*)\s*(pg/ml|pmol/l)',
                r'cobalamin[:\s]+(\d+\.?\d*)\s*(pg/ml|pmol/l)',
                r'cyanocobalamin[:\s]+(\d+\.?\d*)\s*(pg/ml|pmol/l)'
            ],
            'hba1c': [
                r'hba1c[:\s]+(\d+\.?\d*)\s*%?',
                r'hemoglobin\s+a1c[:\s]+(\d+\.?\d*)\s*%?',
                r'glycated\s+h[ae]moglobin[:\s]+(\d+\.?\d*)\s*%?',
                r'a1c[:\s]+(\d+\.?\d*)\s*%?'
            ]
        }
        
        self.unit_conversions = {
            'cholesterol_mg_to_mmol': lambda x: x * 0.02586,
            'triglycerides_mg_to_mmol': lambda x: x * 0.01129,
            'creatinine_mg_to_umol': lambda x: x * 88.4,
            'vitamin_d_nmol_to_ng': lambda x: x * 0.4,
            'vitamin_b12_pmol_to_pg': lambda x: x * 1.355
        }

    def extract_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Extract biomarker data from a PDF file."""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
                
                return self.parse_text(text, pdf_path)
                
        except Exception as e:
            print(f"Error reading PDF {pdf_path}: {e}")
            return {}

    def parse_text(self, text: str, source_file: str) -> Dict[str, Any]:
        """Parse biomarker values from extracted text."""
        text = text.lower()
        
        # Extract date
        date = self.extract_date(text)
        
        # Extract biomarkers
        biomarkers = {}
        for biomarker, patterns in self.biomarker_patterns.items():
            value = self.extract_biomarker(text, patterns, biomarker)
            if value is not None:
                biomarkers[biomarker] = value
        
        # Extract patient info if available
        patient_info = self.extract_patient_info(text)
        
        result = {
            'date': date,
            'source_file': source_file,
            'biomarkers': biomarkers,
            'patient_info': patient_info
        }
        
        return result

    def extract_date(self, text: str) -> str:
        """Extract test date from text."""
        date_patterns = [
            r'date[:\s]+(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})',
            r'test\s+date[:\s]+(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})',
            r'report\s+date[:\s]+(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})',
            r'(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    date_str = match.group(1)
                    # Try to parse the date
                    for fmt in ['%m/%d/%Y', '%d/%m/%Y', '%m-%d-%Y', '%d-%m-%Y', 
                               '%m.%d.%Y', '%d.%m.%Y', '%m/%d/%y', '%d/%m/%y']:
                        try:
                            parsed_date = datetime.strptime(date_str, fmt)
                            return parsed_date.strftime('%Y-%m-%d')
                        except ValueError:
                            continue
                except:
                    pass
        
        # Return current date if no date found
        return datetime.now().strftime('%Y-%m-%d')

    def extract_biomarker(self, text: str, patterns: List[str], biomarker: str) -> Optional[float]:
        """Extract a specific biomarker value from text."""
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    value = float(match.group(1))
                    unit = match.group(2).lower() if len(match.groups()) > 1 else ''
                    
                    # Convert units if necessary
                    value = self.convert_units(value, unit, biomarker)
                    
                    return value
                except (ValueError, IndexError):
                    continue
        
        return None

    def convert_units(self, value: float, unit: str, biomarker: str) -> float:
        """Convert biomarker values to standard units."""
        unit = unit.lower().replace(' ', '')
        
        # Cholesterol conversions (mg/dL to mmol/L)
        if biomarker in ['total_cholesterol', 'ldl', 'hdl'] and 'mg/dl' in unit:
            return self.unit_conversions['cholesterol_mg_to_mmol'](value)
        
        # Triglycerides conversions (mg/dL to mmol/L)
        if biomarker == 'triglycerides' and 'mg/dl' in unit:
            return self.unit_conversions['triglycerides_mg_to_mmol'](value)
        
        # Creatinine conversions (mg/dL to μmol/L)
        if biomarker == 'creatinine' and 'mg/dl' in unit:
            return self.unit_conversions['creatinine_mg_to_umol'](value)
        
        # Vitamin D conversions (nmol/L to ng/mL)
        if biomarker == 'vitamin_d' and 'nmol/l' in unit:
            return self.unit_conversions['vitamin_d_nmol_to_ng'](value)
        
        # Vitamin B12 conversions (pmol/L to pg/mL)
        if biomarker == 'vitamin_b12' and 'pmol/l' in unit:
            return self.unit_conversions['vitamin_b12_pmol_to_pg'](value)
        
        return value

    def extract_patient_info(self, text: str) -> Dict[str, str]:
        """Extract patient information from text."""
        patient_info = {}
        
        # Name patterns
        name_patterns = [
            r'patient[:\s]+([a-z\s,\.]+)(?:\n|dob|age)',
            r'name[:\s]+([a-z\s,\.]+)(?:\n|dob|age)',
            r'mr\.?\s+([a-z\s]+)(?:\n|dob|age)',
            r'ms\.?\s+([a-z\s]+)(?:\n|dob|age)'
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                if len(name) > 2 and len(name) < 50:
                    patient_info['name'] = name.title()
                    break
        
        # Age patterns
        age_patterns = [
            r'age[:\s]+(\d{1,3})',
            r'(\d{1,3})\s+years?\s+old',
            r'dob[:\s]+\d{1,2}[/\-\.]\d{1,2}[/\-\.](\d{2,4})'
        ]
        
        for pattern in age_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                age = match.group(1)
                if pattern.endswith(r'(\d{2,4})'):  # DOB pattern
                    try:
                        birth_year = int(age)
                        if birth_year < 100:
                            birth_year += 2000 if birth_year < 50 else 1900
                        age = str(datetime.now().year - birth_year)
                    except:
                        continue
                
                if 0 < int(age) < 150:
                    patient_info['age'] = age
                    break
        
        # Gender patterns
        gender_patterns = [
            r'gender[:\s]+(male|female|m|f)',
            r'sex[:\s]+(male|female|m|f)',
            r'\b(male|female)\b'
        ]
        
        for pattern in gender_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                gender = match.group(1).lower()
                if gender in ['m', 'male']:
                    patient_info['gender'] = 'Male'
                elif gender in ['f', 'female']:
                    patient_info['gender'] = 'Female'
                break
        
        return patient_info

    def process_multiple_files(self, pdf_directory: str, output_file: str) -> None:
        """Process multiple PDF files and create consolidated JSON output."""
        pdf_dir = Path(pdf_directory)
        all_results = []
        
        for pdf_file in pdf_dir.glob("*.pdf"):
            print(f"Processing {pdf_file.name}...")
            result = self.extract_from_pdf(str(pdf_file))
            
            if result and result.get('biomarkers'):
                all_results.append(result)
                print(f"  Extracted {len(result['biomarkers'])} biomarkers")
            else:
                print(f"  No biomarkers found in {pdf_file.name}")
        
        # Create consolidated dataset
        consolidated = self.consolidate_results(all_results)
        
        # Save to JSON
        with open(output_file, 'w') as f:
            json.dump(consolidated, f, indent=2)
        
        print(f"\nConsolidated data saved to {output_file}")
        print(f"Total records: {len(consolidated.get('biomarkers', []))}")

    def consolidate_results(self, results: List[Dict]) -> Dict[str, Any]:
        """Consolidate multiple extraction results into dashboard format."""
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
        
        # Add clinical ranges (from our previous definition)
        clinical_ranges = self.get_clinical_ranges()
        
        return {
            'patient_info': patient_info,
            'biomarkers': biomarkers,
            'clinical_ranges': clinical_ranges
        }

    def get_clinical_ranges(self) -> Dict[str, Any]:
        """Return clinical ranges for biomarkers."""
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


def main():
    """Main function to run the extraction script."""
    if len(sys.argv) < 2:
        print("Usage: python extract_biomarkers.py <pdf_directory> [output_file]")
        print("Example: python extract_biomarkers.py ./sample_reports ./data/extracted_data.json")
        return
    
    pdf_directory = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else './data/extracted_biomarkers.json'
    
    extractor = BiomarkerExtractor()
    
    try:
        extractor.process_multiple_files(pdf_directory, output_file)
        print(f"\n✅ Extraction completed successfully!")
        print(f"📁 Output saved to: {output_file}")
        print(f"🎯 Ready for dashboard import!")
        
    except Exception as e:
        print(f"❌ Error during extraction: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())