import streamlit as st
import pandas as pd
from datetime import datetime, date
from io import BytesIO

def show(db, teacher_id, academic_year):
    st.markdown("# 📅 Monthly Reports")
    
    selected_code = st.session_state.get('selected_subject_code')
    selected_name = st.session_state.get('selected_subject_name')
    
    if not selected_code:
        st.warning("No subject selected")
        return
    
    st.info(f"**Subject:** {selected_name}")
    
    # Month selection
    col1, col2 = st.columns(2)
    with col1:
        month = st.selectbox("Select Month", [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ], index=datetime.now().month - 1)
    with col2:
        year = st.number_input("Year", 2020, 2030, datetime.now().year)
    
    month_num = ["January", "February", "March", "April", "May", "June",
                 "July", "August", "September", "October", "November", "December"].index(month) + 1
    
    # Get completed SLOs for the month
    conn = db.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT sm.*, scl.coverage_date
        FROM syllabus_coverage_log scl
        JOIN syllabus_master sm ON scl.syllabus_id = sm.syllabus_id
        WHERE scl.teacher_id = ? AND scl.subject_code = ?
        AND strftime('%Y', scl.coverage_date) = ?
        AND strftime('%m', scl.coverage_date) = ?
        ORDER BY scl.coverage_date
    ''', (teacher_id, selected_code, str(year), f"{month_num:02d}"))
    
    completed = [dict(r) for r in cursor.fetchall()]
    conn.close()
    
    if not completed:
        st.warning(f"📝 No SLOs completed in {month} {year}")
        return
    
    st.success(f"✅ {len(completed)} SLOs completed in {month} {year}")
    
    # Statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        mk = len([s for s in completed if s.get('priority_level') == 'Mk'])
        st.metric("🔴 Must Know", mk)
    with col2:
        dk = len([s for s in completed if s.get('priority_level') == 'Dk'])
        st.metric("🟡 Desirable", dk)
    with col3:
        nk = len([s for s in completed if s.get('priority_level') == 'Nk'])
        st.metric("🟢 Nice to Know", nk)
    
    st.markdown("---")
    
    # Export buttons
    df = pd.DataFrame(completed)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Excel export
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Completed SLOs')
        buffer.seek(0)
        
        st.download_button(
            "📥 Download Excel",
            buffer,
            f"monthly_report_{month}_{year}_{selected_code}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    with col2:
        # CSV export
        csv = df.to_csv(index=False)
        st.download_button(
            "📥 Download CSV",
            csv,
            f"monthly_report_{month}_{year}_{selected_code}.csv",
            "text/csv",
            use_container_width=True
        )
    
    st.markdown("---")
    
    # Show completed SLOs
    st.markdown("### Completed SLOs:")
    for idx, slo in enumerate(completed, 1):
        st.markdown(f"**{idx}. [{slo['coverage_date']}] {slo['topic_number']}**")
        st.markdown(f"{slo['learning_objective_text']}")
        st.markdown("")
