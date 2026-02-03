"""
Database Module for Ayurveda Teacher's Syllabus Management App
Handles all database operations using SQLite
FIXED VERSION - Windows Compatible
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import pandas as pd

class Database:
    def __init__(self, db_path=None):
        """Initialize database with auto-path creation"""
        # Auto-create database path if not provided
        if db_path is None:
            # Get the directory where this script is located
            try:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            except:
                base_dir = os.getcwd()
            
            data_dir = os.path.join(base_dir, 'data')
            
            # Create data directory if it doesn't exist
            os.makedirs(data_dir, exist_ok=True)
            
            db_path = os.path.join(data_dir, 'ayurveda_syllabus.db')
        
        # SET db_path BEFORE calling other methods
        self.db_path = db_path
        print(f"✓ Database path: {self.db_path}")
        
        # Now create tables and populate lookups
        self.create_tables()
        self.populate_lookup_tables()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def create_tables(self):
        """Create all database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 1. Teachers Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teachers (
                teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                designation TEXT,
                department TEXT,
                profile_image TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 2. Syllabus Master Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS syllabus_master (
                syllabus_id INTEGER PRIMARY KEY AUTOINCREMENT,
                subject_code TEXT NOT NULL,
                subject_name TEXT NOT NULL,
                year INTEGER NOT NULL,
                paper_number TEXT,
                part TEXT,
                topic_number TEXT,
                topic_name TEXT,
                learning_objective_id TEXT,
                learning_objective_text TEXT NOT NULL,
                domain_code TEXT,
                domain_full TEXT,
                priority_level TEXT,
                priority_full TEXT,
                competency_level TEXT,
                competency_full TEXT,
                teaching_methods_codes TEXT,
                teaching_methods_full TEXT,
                assessment_methods_codes TEXT,
                assessment_methods_full TEXT,
                assessment_type TEXT,
                assessment_type_full TEXT,
                term TEXT,
                lecture_hours REAL,
                non_lecture_hours_theory REAL,
                non_lecture_hours_practical REAL,
                course_outcome TEXT,
                programme_outcome TEXT,
                integration_codes TEXT,
                integration_full TEXT,
                marks_weightage INTEGER,
                mcq_allowed INTEGER DEFAULT 1,
                saq_allowed INTEGER DEFAULT 1,
                laq_allowed INTEGER DEFAULT 1,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 3. Teacher Subject Assignments
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teacher_subject_assignments (
                assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id INTEGER NOT NULL,
                subject_code TEXT NOT NULL,
                year INTEGER NOT NULL,
                academic_year TEXT NOT NULL,
                section TEXT,
                assigned_date DATE DEFAULT CURRENT_DATE,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id)
            )
        ''')
        
        # 4. Lesson Plans
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lesson_plans (
                lesson_plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id INTEGER NOT NULL,
                subject_code TEXT NOT NULL,
                academic_year TEXT NOT NULL,
                lesson_number INTEGER,
                term TEXT,
                planned_date DATE,
                month TEXT,
                class_section TEXT,
                lesson_title TEXT,
                lesson_description TEXT,
                status TEXT DEFAULT 'draft',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id)
            )
        ''')
        
        # 5. Lesson Plan Details (LH/NLHT/NLHP breakdown)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lesson_plan_details (
                detail_id INTEGER PRIMARY KEY AUTOINCREMENT,
                lesson_plan_id INTEGER NOT NULL,
                syllabus_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                duration_hours REAL,
                teaching_method_code TEXT,
                teaching_method_full TEXT,
                assessment_plan TEXT,
                learning_resources TEXT,
                order_in_lesson INTEGER,
                FOREIGN KEY (lesson_plan_id) REFERENCES lesson_plans(lesson_plan_id) ON DELETE CASCADE,
                FOREIGN KEY (syllabus_id) REFERENCES syllabus_master(syllabus_id)
            )
        ''')
        
        # 6. Teaching Diary
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teaching_diary (
                diary_id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id INTEGER NOT NULL,
                lesson_plan_id INTEGER,
                entry_date DATE NOT NULL,
                month TEXT,
                term TEXT,
                subject_code TEXT,
                class_section TEXT,
                period_number INTEGER,
                time_slot TEXT,
                status TEXT,
                competency_certified TEXT,
                formative_assessment TEXT,
                pa_tt TEXT,
                improvement_actions TEXT,
                previous_lesson_status TEXT,
                remarks TEXT,
                staff_signature TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id),
                FOREIGN KEY (lesson_plan_id) REFERENCES lesson_plans(lesson_plan_id)
            )
        ''')
        
        # 7. Teaching Diary Details (LH/NLHT/NLHP breakdown)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teaching_diary_details (
                diary_detail_id INTEGER PRIMARY KEY AUTOINCREMENT,
                diary_id INTEGER NOT NULL,
                syllabus_id INTEGER NOT NULL,
                category TEXT NOT NULL,
                actual_duration_hours REAL,
                teaching_method_used TEXT,
                domain_code TEXT,
                competency_level TEXT,
                depth TEXT,
                course_outcome TEXT,
                programme_outcome TEXT,
                teaching_effectiveness INTEGER,
                notes TEXT,
                FOREIGN KEY (diary_id) REFERENCES teaching_diary(diary_id) ON DELETE CASCADE,
                FOREIGN KEY (syllabus_id) REFERENCES syllabus_master(syllabus_id)
            )
        ''')
        
        # 8. Coverage Log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS syllabus_coverage_log (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id INTEGER NOT NULL,
                subject_code TEXT NOT NULL,
                syllabus_id INTEGER NOT NULL,
                diary_id INTEGER,
                category TEXT,
                coverage_date DATE NOT NULL,
                coverage_status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id),
                FOREIGN KEY (syllabus_id) REFERENCES syllabus_master(syllabus_id),
                FOREIGN KEY (diary_id) REFERENCES teaching_diary(diary_id)
            )
        ''')
        
        # 9. Planned SLOs (NEW)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS planned_slos (
                plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                teacher_id INTEGER NOT NULL,
                subject_code TEXT NOT NULL,
                syllabus_id INTEGER NOT NULL,
                plan_type TEXT NOT NULL,
                plan_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id),
                FOREIGN KEY (syllabus_id) REFERENCES syllabus_master(syllabus_id),
                UNIQUE(teacher_id, syllabus_id, plan_type)
            )
        ''')
        
        # 9. Academic Calendar
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS academic_calendar (
                calendar_id INTEGER PRIMARY KEY AUTOINCREMENT,
                academic_year TEXT NOT NULL,
                term TEXT NOT NULL,
                term_start_date DATE NOT NULL,
                term_end_date DATE NOT NULL,
                total_teaching_days INTEGER,
                holidays TEXT,
                special_events TEXT
            )
        ''')
        
        # Lookup Tables
        
        # 10. Domain Master
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS domain_master (
                domain_code TEXT PRIMARY KEY,
                domain_full TEXT NOT NULL,
                domain_category TEXT,
                display_order INTEGER
            )
        ''')
        
        # 11. Teaching Methods Master
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS teaching_methods_master (
                method_code TEXT PRIMARY KEY,
                method_full TEXT NOT NULL,
                method_category TEXT,
                display_order INTEGER
            )
        ''')
        
        # 12. Assessment Methods Master
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS assessment_methods_master (
                method_code TEXT PRIMARY KEY,
                method_full TEXT NOT NULL,
                method_category TEXT,
                display_order INTEGER
            )
        ''')
        
        # 13. Integration Master
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS integration_master (
                integration_code TEXT PRIMARY KEY,
                integration_full TEXT NOT NULL,
                integration_type TEXT,
                display_order INTEGER
            )
        ''')
        
        # 14. Priority Master
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS priority_master (
                priority_code TEXT PRIMARY KEY,
                priority_full TEXT NOT NULL,
                display_order INTEGER
            )
        ''')
        
        # 15. Competency Master
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS competency_master (
                competency_code TEXT PRIMARY KEY,
                competency_full TEXT NOT NULL,
                display_order INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✓ Database tables created")
    
    def populate_lookup_tables(self):
        """Populate lookup tables with NCISM abbreviations"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if already populated
        cursor.execute("SELECT COUNT(*) FROM domain_master")
        if cursor.fetchone()[0] > 0:
            conn.close()
            print("✓ Lookup tables already populated")
            return
        
        print("Populating lookup tables...")
        
        # Domain Master Data
        domains = [
            ('CK', 'Cognitive / Knowledge', 'Cognitive', 1),
            ('CC', 'Cognitive / Comprehension', 'Cognitive', 2),
            ('CAP', 'Cognitive / Application', 'Cognitive', 3),
            ('CAN', 'Cognitive / Analysis', 'Cognitive', 4),
            ('CS', 'Cognitive / Synthesis', 'Cognitive', 5),
            ('CE', 'Cognitive / Evaluation', 'Cognitive', 6),
            ('PSY-PER', 'Psychomotor / Perception', 'Psychomotor', 7),
            ('PSY-SET', 'Psychomotor / Set', 'Psychomotor', 8),
            ('PSY-GUD', 'Psychomotor / Guided response', 'Psychomotor', 9),
            ('PSY-MEC', 'Psychomotor / Mechanism', 'Psychomotor', 10),
            ('PSY-COR', 'Psychomotor / Complex Overt Response', 'Psychomotor', 11),
            ('PSY-ADT', 'Psychomotor / Adaptation', 'Psychomotor', 12),
            ('PSY-ORG', 'Psychomotor / Origination', 'Psychomotor', 13),
            ('AFT-REC', 'Affective / Receiving', 'Affective', 14),
            ('AFT-RES', 'Affective / Responding', 'Affective', 15),
            ('AFT-VAL', 'Affective / Valuing', 'Affective', 16),
            ('AFT-SET', 'Affective / Organization', 'Affective', 17),
            ('AFT-CHR', 'Affective / Characterization', 'Affective', 18),
        ]
        cursor.executemany('INSERT OR IGNORE INTO domain_master VALUES (?, ?, ?, ?)', domains)
        
        # Teaching Methods Master Data
        teaching_methods = [
            ('L', 'Lecture', 'Lecture-Based', 1),
            ('DIS', 'Discussions', 'Discussion & Group', 2),
            ('PBL', 'Problem-Based Learning', 'Active Learning', 3),
            ('CBL', 'Case-Based Learning', 'Active Learning', 4),
            ('D', 'Demonstration', 'Practical & Clinical', 5),
            ('TUT', 'Tutorial', 'Discussion & Group', 6),
            ('SY', 'Symposium', 'Discussion & Group', 7),
            ('SIM', 'Simulation', 'Student-Centered', 8),
            ('RP', 'Role Plays', 'Student-Centered', 9),
            ('SDL', 'Self-directed learning', 'Student-Centered', 10),
            ('FC', 'Flipped Classroom', 'Student-Centered', 11),
            ('BS', 'Brainstorming', 'Discussion & Group', 12),
            ('TPW', 'Team Project Work', 'Student-Centered', 13),
            ('PER', 'Presentations', 'Discussion & Group', 14),
            ('W', 'Workshops', 'Other Methods', 15),
            ('FV', 'Field Visit', 'Other Methods', 16),
            ('REC', 'Recitation', 'Other Methods', 17),
            ('D-BED', 'Demonstration Bedside', 'Practical & Clinical', 18),
            ('ECE', 'Early Clinical Exposure', 'Practical & Clinical', 19),
            ('L&GD', 'Lecture & Group Discussion', 'Lecture-Based', 20),
        ]
        cursor.executemany('INSERT OR IGNORE INTO teaching_methods_master VALUES (?, ?, ?, ?)', teaching_methods)
        
        # Assessment Methods Master Data
        assessment_methods = [
            ('T-MEQs', 'Theory MEQs (Modified Essay Questions)', 'Theory', 1),
            ('VV-Viva', 'Viva', 'General', 2),
            ('OSPE', 'Observed Structured Practical Examination', 'Clinical', 3),
            ('DOPS', 'Direct observation of procedural skills', 'Clinical', 4),
            ('P-VIVA', 'Practical Viva', 'Practical', 5),
            ('SA', 'Self-assessment', 'Other', 6),
            ('T-CS', 'Theory case study', 'Theory', 7),
            ('OSCE', 'Observed Structured Clinical Examination', 'Clinical', 8),
            ('Mini-CEX', 'Mini Clinical Evaluation Exercise', 'Clinical', 9),
            ('CBA', 'Case Based Assessment', 'Other', 10),
            ('P-PRF', 'Practical Performance', 'Practical', 11),
            ('T-OBT', 'Theory open book test', 'Theory', 12),
        ]
        cursor.executemany('INSERT OR IGNORE INTO assessment_methods_master VALUES (?, ?, ?, ?)', assessment_methods)
        
        # Priority Master Data
        priorities = [
            ('Mk', 'Must know', 1),
            ('Dk', 'Desirable to know', 2),
            ('Nk', 'Nice to know', 3),
        ]
        cursor.executemany('INSERT OR IGNORE INTO priority_master VALUES (?, ?, ?)', priorities)
        
        # Competency Master Data
        competencies = [
            ('K', 'Knows', 1),
            ('Kh', 'Knows How', 2),
            ('Sh', 'Shows How', 3),
            ('D', 'Does', 4),
        ]
        cursor.executemany('INSERT OR IGNORE INTO competency_master VALUES (?, ?, ?)', competencies)
        
        # Integration Master Data
        integrations = [
            ('H-RS', 'Rachana Sharir', 'Horizontal', 1),
            ('V-KC', 'Kayachikitsa', 'Vertical', 2),
            ('H-DG', 'Dravyaguna', 'Horizontal', 3),
            ('V-RN', 'Roga Nidana', 'Vertical', 4),
            ('H-SW', 'Swasthavritta', 'Horizontal', 5),
            ('V-KS', 'Kriya Sharir', 'Vertical', 6),
        ]
        cursor.executemany('INSERT OR IGNORE INTO integration_master VALUES (?, ?, ?, ?)', integrations)
        
        conn.commit()
        conn.close()
        print("✓ Lookup tables populated")
    
    # Teacher Management Methods
    
    def create_teacher(self, username: str, password: str, full_name: str, **kwargs) -> int:
        """Create a new teacher"""
        import hashlib
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO teachers (username, password_hash, full_name, email, phone, designation, department)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (username, password_hash, full_name, kwargs.get('email'), kwargs.get('phone'),
              kwargs.get('designation'), kwargs.get('department')))
        
        teacher_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return teacher_id
    
    def authenticate_teacher(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate teacher login"""
        import hashlib
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM teachers 
            WHERE username = ? AND password_hash = ? AND status = 'active'
        ''', (username, password_hash))
        
        teacher = cursor.fetchone()
        conn.close()
        
        if teacher:
            return dict(teacher)
        return None
    
    def get_teacher_by_id(self, teacher_id: int) -> Optional[Dict]:
        """Get teacher details by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM teachers WHERE teacher_id = ?', (teacher_id,))
        teacher = cursor.fetchone()
        conn.close()
        
        if teacher:
            return dict(teacher)
        return None
    
    # Subject Assignment Methods
    
    def assign_subject_to_teacher(self, teacher_id: int, subject_code: str, year: int, academic_year: str, section: str = None):
        """Assign a subject to a teacher"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO teacher_subject_assignments (teacher_id, subject_code, year, academic_year, section)
            VALUES (?, ?, ?, ?, ?)
        ''', (teacher_id, subject_code, year, academic_year, section))
        
        conn.commit()
        conn.close()
    
    def get_teacher_subjects(self, teacher_id: int, academic_year: str = None) -> List[Dict]:
        """Get all subjects assigned to a teacher"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if academic_year:
            cursor.execute('''
                SELECT DISTINCT tsa.*, sm.subject_name
                FROM teacher_subject_assignments tsa
                JOIN syllabus_master sm ON tsa.subject_code = sm.subject_code
                WHERE tsa.teacher_id = ? AND tsa.academic_year = ? AND tsa.status = 'active'
            ''', (teacher_id, academic_year))
        else:
            cursor.execute('''
                SELECT DISTINCT tsa.*, sm.subject_name
                FROM teacher_subject_assignments tsa
                JOIN syllabus_master sm ON tsa.subject_code = sm.subject_code
                WHERE tsa.teacher_id = ? AND tsa.status = 'active'
            ''', (teacher_id,))
        
        subjects = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return subjects
    
    # Syllabus Methods
    
    def get_syllabus_by_subject(self, subject_code: str, filters: Dict = None) -> List[Dict]:
        """Get syllabus objectives for a subject with optional filters"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM syllabus_master WHERE subject_code = ? AND status = "active"'
        params = [subject_code]
        
        if filters:
            if filters.get('term'):
                query += ' AND term = ?'
                params.append(filters['term'])
            if filters.get('priority'):
                query += ' AND priority_level = ?'
                params.append(filters['priority'])
            if filters.get('paper'):
                query += ' AND paper_number = ?'
                params.append(filters['paper'])
        
        query += ' ORDER BY paper_number, topic_number, syllabus_id'
        
        cursor.execute(query, params)
        objectives = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return objectives
    
    def get_syllabus_by_id(self, syllabus_id: int) -> Optional[Dict]:
        """Get a single syllabus objective by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM syllabus_master WHERE syllabus_id = ?', (syllabus_id,))
        objective = cursor.fetchone()
        conn.close()
        
        if objective:
            return dict(objective)
        return None
    
    def search_syllabus(self, subject_code: str, search_term: str) -> List[Dict]:
        """Search syllabus objectives by text"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM syllabus_master 
            WHERE subject_code = ? AND status = 'active'
            AND (learning_objective_text LIKE ? OR topic_name LIKE ?)
            ORDER BY paper_number, topic_number, syllabus_id
        ''', (subject_code, f'%{search_term}%', f'%{search_term}%'))
        
        objectives = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return objectives
    
    # Lookup Methods
    
    def get_all_domains(self) -> Dict[str, str]:
        """Get all domain codes and descriptions"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT domain_code, domain_full FROM domain_master ORDER BY display_order')
        domains = {row['domain_code']: row['domain_full'] for row in cursor.fetchall()}
        conn.close()
        
        return domains
    
    def get_all_teaching_methods(self) -> Dict[str, str]:
        """Get all teaching method codes and descriptions"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT method_code, method_full FROM teaching_methods_master ORDER BY display_order')
        methods = {row['method_code']: row['method_full'] for row in cursor.fetchall()}
        conn.close()
        
        return methods
    
    def get_all_assessment_methods(self) -> Dict[str, str]:
        """Get all assessment method codes and descriptions"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT method_code, method_full FROM assessment_methods_master ORDER BY display_order')
        methods = {row['method_code']: row['method_full'] for row in cursor.fetchall()}
        conn.close()
        
        return methods
    
    def get_all_priorities(self) -> Dict[str, str]:
        """Get all priority codes and descriptions"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT priority_code, priority_full FROM priority_master ORDER BY display_order')
        priorities = {row['priority_code']: row['priority_full'] for row in cursor.fetchall()}
        conn.close()
        
        return priorities
    
    def get_all_competencies(self) -> Dict[str, str]:
        """Get all competency codes and descriptions"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT competency_code, competency_full FROM competency_master ORDER BY display_order')
        competencies = {row['competency_code']: row['competency_full'] for row in cursor.fetchall()}
        conn.close()
        
        return competencies
    
    # Coverage Statistics
    
    def get_coverage_stats(self, teacher_id: int, subject_code: str) -> Dict:
        """Get coverage statistics for a subject"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total objectives
        cursor.execute('''
            SELECT COUNT(*) as total FROM syllabus_master 
            WHERE subject_code = ? AND status = 'active'
        ''', (subject_code,))
        total = cursor.fetchone()['total']
        
        # Covered objectives
        cursor.execute('''
            SELECT COUNT(DISTINCT syllabus_id) as covered 
            FROM syllabus_coverage_log
            WHERE teacher_id = ? AND subject_code = ?
        ''', (teacher_id, subject_code))
        covered = cursor.fetchone()['covered']
        
        # By priority
        cursor.execute('''
            SELECT 
                sm.priority_level,
                COUNT(*) as total,
                COUNT(DISTINCT scl.syllabus_id) as covered
            FROM syllabus_master sm
            LEFT JOIN syllabus_coverage_log scl 
                ON sm.syllabus_id = scl.syllabus_id 
                AND scl.teacher_id = ?
            WHERE sm.subject_code = ? AND sm.status = 'active'
            GROUP BY sm.priority_level
        ''', (teacher_id, subject_code))
        
        by_priority = {row['priority_level']: {'total': row['total'], 'covered': row['covered']} 
                      for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            'total': total,
            'covered': covered,
            'percentage': round((covered / total * 100) if total > 0 else 0, 1),
            'by_priority': by_priority
        }
