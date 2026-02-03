"""
ENHANCED AYURVEDA TEACHER'S APP
With: Lesson Planning, Monthly Reports, Abbreviations, Term Filtering
Auto-imports data on first run (for Streamlit Cloud)
"""

import streamlit as st
import sys
import os
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))
from database import Database

# Page config
st.set_page_config(
    page_title="Ayurveda Teacher's App",
    page_icon="📚",
    layout="wide"
)

# Initialize
@st.cache_resource
def init_db():
    return Database()

db = init_db()

# Check if database has data, if not trigger import
@st.cache_resource
def check_and_import_data():
    """Check if database has subjects, if not import from Excel"""
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM syllabus_master")
    count = cursor.fetchone()[0]
    conn.close()
    
    if count == 0:
        # Database is empty, try to import
        excel_path = os.path.join(os.path.dirname(__file__), 'LMS_All_Sheets_Combined.xlsx')
        if os.path.exists(excel_path):
            st.info("🔄 First-time setup: Importing data...")
            from import_data import import_excel
            total = import_excel(excel_path, db)
            if total > 0:
                st.success(f"✅ Imported {total} SLOs successfully!")
                return True
            else:
                return False
        else:
            return False
    return True

# Session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'teacher_id' not in st.session_state:
    st.session_state.teacher_id = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Dashboard'

def login_page():
    """Login with subject selection"""
    
    # Check if data needs to be imported
    data_ready = check_and_import_data()
    
    if not data_ready:
        st.error("""
        ❌ **Database is empty!**
        
        **For local deployment:**
        Run: `python import_data.py`
        
        **For Streamlit Cloud:**
        Upload `LMS_All_Sheets_Combined.xlsx` to your repository root folder.
        """)
        return
    
    st.markdown("# 🎓 Ayurveda Teacher's App")
    st.markdown("### Welcome!")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Get all subjects
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DISTINCT subject_code, subject_name, year, COUNT(*) as cnt
            FROM syllabus_master
            GROUP BY subject_code
            ORDER BY year, subject_code
        ''')
        all_subjects = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        with st.form("login"):
            st.markdown("### 🔐 Login")
            username = st.text_input("Username", value="demo")
            password = st.text_input("Password", type="password", value="demo123")
            
            st.markdown("---")
            st.markdown("### 📚 Select Your Subject")
            
            if all_subjects:
                subject_labels = [f"Year {s['year']} | {s['subject_code']} - {s['subject_name']} ({s['cnt']} SLOs)" 
                                 for s in all_subjects]
                
                selected_subject_label = st.selectbox(
                    "Choose the subject you teach",
                    subject_labels,
                    help="Select your teaching subject"
                )
                
                selected_idx = subject_labels.index(selected_subject_label)
                selected_subject = all_subjects[selected_idx]
                selected_subject_code = selected_subject['subject_code']
                selected_subject_name = selected_subject['subject_name']
            else:
                st.error("No subjects in database! Run import_data.py first!")
                selected_subject_code = None
                selected_subject_name = None
            
            if st.form_submit_button("Login", use_container_width=True):
                if not all_subjects:
                    st.error("Please import data first!")
                    return
                
                teacher = db.authenticate_teacher(username, password)
                
                if not teacher:
                    try:
                        db.create_teacher('demo', 'demo123', 'Dr. Demo Teacher')
                        teacher = db.authenticate_teacher('demo', 'demo123')
                    except:
                        teacher = db.authenticate_teacher('demo', 'demo123')
                
                if teacher:
                    st.session_state.logged_in = True
                    st.session_state.teacher_id = teacher['teacher_id']
                    st.session_state.teacher_name = teacher['full_name']
                    st.session_state.selected_subject_code = selected_subject_code
                    st.session_state.selected_subject_name = selected_subject_name
                    
                    # Auto-assign
                    conn = db.get_connection()
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT OR IGNORE INTO teacher_subject_assignments 
                        (teacher_id, subject_code, year, academic_year, status)
                        VALUES (?, ?, ?, '2025-26', 'active')
                    ''', (teacher['teacher_id'], selected_subject_code, selected_subject['year']))
                    conn.commit()
                    conn.close()
                    
                    st.success(f"✅ Logged in to {selected_subject_name}!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")

def main_app():
    """Main application"""
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.teacher_name}")
        st.markdown(f"**Subject:** {st.session_state.get('selected_subject_name', 'Not selected')}")
        st.markdown("**Academic Year:** 2025-26")
        st.markdown("---")
        
        menu = {
            "🏠 Dashboard": "Dashboard",
            "📖 Browse SLOs": "Browse SLOs",
            "📝 My Planned SLOs": "My Planned SLOs",
            "📓 Teaching Diary": "Teaching Diary",
            "📊 Coverage": "Coverage",
            "📅 Monthly Reports": "Monthly Reports",
            "📥 Export Reports": "Export Reports",
            "📚 Abbreviations": "Abbreviations"
        }
        
        for label, page in menu.items():
            if st.button(label, use_container_width=True):
                st.session_state.current_page = page
                st.rerun()
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
        
        st.markdown("---")
        st.markdown("""
        <small><i>A Technological Initiative from<br>Prof.(Dr.) Prasanna Kulkarni</i></small>
        """, unsafe_allow_html=True)
    
    # Main content
    page = st.session_state.current_page
    
    if page == "Dashboard":
        from dashboard import show as show_dashboard
        show_dashboard(db, st.session_state.teacher_id, '2025-26')
    elif page == "Browse SLOs":
        from slo_browser_enhanced import show as show_browser
        show_browser(db, st.session_state.teacher_id, '2025-26')
    elif page == "My Planned SLOs":
        from planned_slos import show as show_planned
        show_planned(db, st.session_state.teacher_id, '2025-26')
    elif page == "Teaching Diary":
        from teaching_diary import show as show_diary
        show_diary(db, st.session_state.teacher_id, '2025-26')
    elif page == "Coverage":
        from coverage import show as show_coverage
        show_coverage(db, st.session_state.teacher_id, '2025-26')
    elif page == "Monthly Reports":
        from monthly_reports import show as show_monthly
        show_monthly(db, st.session_state.teacher_id, '2025-26')
    elif page == "Export Reports":
        from reports import show as show_reports
        show_reports(db, st.session_state.teacher_id, '2025-26')
    elif page == "Abbreviations":
        from abbreviations import show as show_abbr
        show_abbr(db, st.session_state.teacher_id, '2025-26')

if __name__ == "__main__":
    if not st.session_state.logged_in:
        login_page()
    else:
        main_app()
