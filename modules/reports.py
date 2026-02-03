import streamlit as st
import pandas as pd
from datetime import datetime

def show(db, teacher_id, academic_year):
    st.markdown("# 📥 Export Reports")
    
    # Get selected subject
    selected_code = st.session_state.get('selected_subject_code')
    selected_name = st.session_state.get('selected_subject_name')
    
    if not selected_code:
        st.warning("No subject selected.")
        return
    
    st.info(f"**Subject:** {selected_name}")
    st.markdown("---")
    
    # Get completed SLOs
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT sm.*, scl.coverage_date
        FROM syllabus_coverage_log scl
        JOIN syllabus_master sm ON scl.syllabus_id = sm.syllabus_id
        WHERE scl.teacher_id = ? AND scl.subject_code = ?
        ORDER BY scl.coverage_date DESC
    ''', (teacher_id, selected_code))
    
    completed = [dict(r) for r in cursor.fetchall()]
    conn.close()
    
    if not completed:
        st.warning("📝 No completed SLOs yet. Start logging in Teaching Diary!")
        return
    
    st.success(f"✅ {len(completed)} SLOs completed")
    
    # Export button
    df = pd.DataFrame(completed)
    csv = df.to_csv(index=False)
    
    st.download_button(
        "📥 Download All Completed SLOs (CSV)",
        csv,
        f"completed_{selected_code}_{datetime.now().strftime('%Y%m%d')}.csv",
        "text/csv",
        use_container_width=True
    )
    
    st.markdown("---")
    
    # By term
    st.markdown("### Export by Term")
    col1, col2, col3 = st.columns(3)
    
    for idx, term in enumerate(['I', 'II', 'III']):
        term_slos = [s for s in completed if s.get('term') == term]
        with [col1, col2, col3][idx]:
            if term_slos:
                df_term = pd.DataFrame(term_slos)
                csv_term = df_term.to_csv(index=False)
                st.download_button(
                    f"Term {term} ({len(term_slos)})",
                    csv_term,
                    f"term_{term}_{selected_code}.csv",
                    "text/csv",
                    use_container_width=True
                )
            else:
                st.info(f"Term {term}: 0 SLOs")
