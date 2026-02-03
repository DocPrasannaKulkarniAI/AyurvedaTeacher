"""
COMPLETE DATA IMPORT - Reads YOUR Excel File
All columns: A3-J3
Location: import_data.py
"""

import pandas as pd
import json
import re
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))
from database import Database

def clean_text(text):
    """Clean text"""
    if pd.isna(text):
        return None
    return str(text).strip()

def parse_list(text):
    """Parse comma/slash separated items"""
    if pd.isna(text) or not text:
        return []
    items = re.split(r'[,;/()]', str(text))
    return [item.strip() for item in items if item.strip() and len(item.strip()) > 1]

def import_excel(excel_path, db):
    """Import from YOUR Excel file"""
    
    print("="*60)
    print("IMPORTING FROM YOUR EXCEL FILE")
    print("="*60)
    
    xl = pd.ExcelFile(excel_path)
    
    # Subject mapping
    subjects = {
        'LMS1_KS': ('AyUG-KS', 'Kriya Sharir', 1),
        'LMS1_PV': ('AyUG-PV', 'Padartha Vigyan', 1),
        'LMS1_RS': ('AyUG-RS', 'Rachana Sharir', 1),
        'LMS1_SA1': ('AyUG-SA1', 'Sanskrit', 1),
        'LMS1_AI': ('AyUG-AI', 'Ayurveda Itihas', 1),
        'LMS2_AT': ('AyUG-AT', 'Agad Tantra', 2),
        'LMS2_DG': ('AyUG-DG', 'Dravyaguna', 2),
        'LMS2_RSBK': ('AyUG-RSBK', 'Rasashastra & Bhaishajya Kalpana', 2),
        'LMS2_RN': ('AyUG-RN', 'Roga Nidan', 2),
        'LMS2_SA2': ('AyUG-SA2', 'Sanskrit', 2),
        'LMS2_SW': ('AyUG-SW', 'Swasthavritta', 2),
        'LMS3_PK': ('AyUG-PK', 'Prasuti & Stree Roga', 3),
        'LMS3_KB': ('AyUG-KB', 'Kaumarbhritya', 3),
        'LMS3_EM': ('AyUG-EM', 'Emergency Medicine', 3),
        'LMS3_KC': ('AyUG-KC', 'Kayachikitsa', 3),
        'LMS3_PTSR': ('AyUG-PTSR', 'Panchakarma & Shalyatantra', 3),
        'LMS3_RMBS': ('AyUG-RMBS', 'Research Methodology & Biostatistics', 3),
        'LMS3_SA3': ('AyUG-SA3', 'Sanskrit', 3),
        'LMS3_SL': ('AyUG-SL', 'Shalakya Tantra', 3),
        'LMS3_ST': ('AyUG-ST', 'Shalya Tantra', 3),
    }
    
    conn = db.get_connection()
    cursor = conn.cursor()
    total_imported = 0
    
    for sheet_name in xl.sheet_names:
        if sheet_name not in subjects:
            continue
        
        code, name, year = subjects[sheet_name]
        print(f"\n📚 {name} ({code})")
        
        df = pd.read_excel(excel_path, sheet_name=sheet_name)
        
        # Find header (row with "A3 Course outcome")
        header_row = None
        for idx in range(30):
            if idx >= len(df):
                break
            row_str = ' '.join([str(v) for v in df.iloc[idx] if pd.notna(v)])
            if 'A3' in row_str and 'Course outcome' in row_str:
                header_row = idx
                break
        
        if header_row is None:
            print("  ⚠️ Header not found")
            continue
        
        # Set columns
        df.columns = df.iloc[header_row]
        df = df.iloc[header_row + 1:].reset_index(drop=True)
        
        # Column mapping
        col_map = {}
        for col in df.columns:
            col_str = str(col).lower()
            if 'a3' in col_str or 'course outcome' in col_str:
                col_map['A3'] = col
            elif 'b3' in col_str or 'learning objective' in col_str:
                col_map['B3'] = col
            elif 'c3' in col_str or 'domain' in col_str:
                col_map['C3'] = col
            elif 'd3' in col_str or 'must' in col_str:
                col_map['D3'] = col
            elif 'e3' in col_str or 'level' in col_str:
                col_map['E3'] = col
            elif 'f3' in col_str or 't-l' in col_str:
                col_map['F3'] = col
            elif 'g3' in col_str or ('assessment' in col_str and 'formative' not in col_str):
                col_map['G3'] = col
            elif 'h3' in col_str or 'formative' in col_str:
                col_map['H3'] = col
            elif 'i3' in col_str or col_str.strip() == 'term':
                col_map['I3'] = col
            elif 'j3' in col_str or 'integration' in col_str:
                col_map['J3'] = col
        
        if 'B3' not in col_map:
            print("  ⚠️ Learning objective column not found")
            continue
        
        count = 0
        current_topic = None
        current_topic_full = None  # Store full topic name
        
        # Process rows
        for idx, row in df.iterrows():
            # Check for topic - store FULL name
            a3_val = clean_text(row.get(col_map.get('A3')))
            if a3_val:
                if 'Topic' in a3_val:
                    # Full topic like "Topic 1 Swastha and Swasthya"
                    parts = a3_val.split()
                    if len(parts) >= 2:
                        current_topic = f"{parts[0]} {parts[1]}"  # "Topic 1"
                    else:
                        current_topic = parts[0] if parts else a3_val  # Just "Topic"
                    current_topic_full = a3_val  # Full name
                elif a3_val.startswith('CO'):
                    current_topic = a3_val
                    if not current_topic_full:
                        current_topic_full = a3_val
            
            # Get learning objective
            lo = clean_text(row.get(col_map.get('B3')))
            if not lo or len(lo) < 10:
                continue
            if 'learning objective' in lo.lower():
                continue
            
            # Parse all fields
            # C3: Domain
            c3_raw = clean_text(row.get(col_map.get('C3')))
            domain_code, domain_full = 'CC', 'Cognitive / Comprehension'
            if c3_raw:
                c3_lower = c3_raw.lower()
                if 'recall' in c3_lower or 'knowledge' in c3_lower:
                    domain_code, domain_full = 'CK', 'Cognitive / Knowledge'
                elif 'application' in c3_lower:
                    domain_code, domain_full = 'CAP', 'Cognitive / Application'
                elif 'analysis' in c3_lower:
                    domain_code, domain_full = 'CAN', 'Cognitive / Analysis'
                elif 'psychomotor' in c3_lower:
                    domain_code, domain_full = 'PSY-MEC', 'Psychomotor / Mechanism'
                elif 'affective' in c3_lower:
                    domain_code, domain_full = 'AFT-RES', 'Affective / Responding'
            
            # D3: Priority
            d3_raw = clean_text(row.get(col_map.get('D3')))
            priority, priority_full = 'Mk', 'Must know'
            if d3_raw:
                if 'Dk' in d3_raw or 'Desirable' in d3_raw:
                    priority, priority_full = 'Dk', 'Desirable to know'
                elif 'Nk' in d3_raw or 'Nice' in d3_raw:
                    priority, priority_full = 'Nk', 'Nice to know'
            
            # E3: Competency
            e3_raw = clean_text(row.get(col_map.get('E3')))
            comp, comp_full = 'Kh', 'Knows How'
            if e3_raw:
                if 'D' == e3_raw or 'Does' in e3_raw:
                    comp, comp_full = 'D', 'Does'
                elif 'Sh' in e3_raw or 'Shows' in e3_raw:
                    comp, comp_full = 'Sh', 'Shows How'
                elif e3_raw == 'K' or 'Know ' in e3_raw:
                    comp, comp_full = 'K', 'Knows'
            
            # F3: Teaching methods
            f3_raw = clean_text(row.get(col_map.get('F3')))
            f3_list = parse_list(f3_raw) if f3_raw else ['Lecture']
            
            # G3: Assessment
            g3_raw = clean_text(row.get(col_map.get('G3')))
            g3_list = parse_list(g3_raw) if g3_raw else ['Written']
            
            # H3: Assessment type
            h3_raw = clean_text(row.get(col_map.get('H3')))
            assess_type, assess_type_full = 'F & S', 'Formative & Summative'
            if h3_raw:
                if 'S' == h3_raw:
                    assess_type, assess_type_full = 'S', 'Summative'
                elif 'F' == h3_raw:
                    assess_type, assess_type_full = 'F', 'Formative'
            
            # I3: Term
            i3_raw = clean_text(row.get(col_map.get('I3')))
            term = i3_raw if i3_raw in ['I', 'II', 'III'] else 'I'
            
            # J3: Integration
            j3_raw = clean_text(row.get(col_map.get('J3')))
            j3_list = parse_list(j3_raw) if j3_raw else []
            
            # Insert
            try:
                cursor.execute('''
                    INSERT INTO syllabus_master (
                        subject_code, subject_name, year, topic_number,
                        learning_objective_text,
                        domain_code, domain_full,
                        priority_level, priority_full,
                        competency_level, competency_full,
                        teaching_methods_codes, teaching_methods_full,
                        assessment_methods_codes, assessment_methods_full,
                        assessment_type, assessment_type_full,
                        term, integration_codes, integration_full,
                        course_outcome, programme_outcome
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    code, name, year, current_topic_full or 'Topic 1',
                    lo,
                    domain_code, domain_full,
                    priority, priority_full,
                    comp, comp_full,
                    json.dumps(f3_list[:3]), json.dumps(f3_list[:3]),
                    json.dumps(g3_list[:3]), json.dumps(g3_list[:3]),
                    assess_type, assess_type_full,
                    term, json.dumps(j3_list), json.dumps(j3_list),
                    current_topic or 'CO 1', 'PO1, PO2'
                ))
                count += 1
            except Exception as e:
                print(f"  Error row {idx}: {e}")
        
        print(f"  ✅ Imported {count} SLOs")
        total_imported += count
    
    conn.commit()
    conn.close()
    
    print(f"\n{'='*60}")
    print(f"✅ TOTAL IMPORTED: {total_imported} SLOs")
    print(f"{'='*60}\n")
    
    return total_imported

if __name__ == "__main__":
    print("AYURVEDA TEACHER'S APP - DATA IMPORT")
    print("="*60)
    
    db = Database()
    
    # UPDATE THIS PATH TO YOUR EXCEL FILE
    excel_path = r'D:\SKAMC\LMS\syllabus_data\LMS_All_Sheets_Combined.xlsx'
    
    if not os.path.exists(excel_path):
        print(f"❌ Excel file not found: {excel_path}")
        print("\nPlease update the excel_path in this script!")
        input("Press Enter to exit...")
    else:
        total = import_excel(excel_path, db)
        print(f"\n✅ SUCCESS! {total} SLOs imported")
        print("\nRun: streamlit run app.py")
        input("\nPress Enter to exit...")
