import streamlit as st
from datetime import date

def show(db, teacher_id, academic_year):
    st.markdown("# 📓 Teaching Diary")
    
    # Get selected subject
    selected_code = st.session_state.get('selected_subject_code')
    selected_name = st.session_state.get('selected_subject_name')
    
    if not selected_code:
        st.warning("No subject selected. Please logout and login again.")
        return
    
    st.info(f"**Subject:** {selected_name}")
    
    with st.form("diary"):
        entry_date = st.date_input("📅 Date", date.today())
        period = st.number_input("🕐 Period", 1, 10, 1)
        term = st.selectbox("📆 Term", ["I", "II", "III"])
        
        # Get SLOs for subject
        slos = db.get_syllabus_by_subject(selected_code, {'term': term})
        
        if not slos:
            st.warning(f"No SLOs found for Term {term}")
            st.form_submit_button("Save")
            return
        
        # Group by topic
        topics = {}
        for slo in slos:
            t = slo.get('topic_number', 'General')
            if t not in topics:
                topics[t] = []
            topics[t].append(slo)
        
        topic_list = list(topics.keys())
        topic = st.selectbox("📑 Topic Covered", topic_list)
        
        # SLO selection
        slo_opts = {f"SLO {i+1}: {s['learning_objective_text'][:80]}...": s['syllabus_id'] 
                   for i, s in enumerate(topics[topic])}
        
        sel_slos = st.multiselect(
            "✅ SLOs Completed",
            list(slo_opts.keys()),
            help="Select all SLOs you completed in this class"
        )
        
        remarks = st.text_area("💭 Remarks", placeholder="Any observations or notes...")
        
        if st.form_submit_button("💾 Save Entry", use_container_width=True):
            if sel_slos:
                conn = db.get_connection()
                cursor = conn.cursor()
                
                # Mark SLOs complete
                for slo_label in sel_slos:
                    slo_id = slo_opts[slo_label]
                    cursor.execute('''
                        INSERT OR IGNORE INTO syllabus_coverage_log 
                        (teacher_id, subject_code, syllabus_id, coverage_date, coverage_status)
                        VALUES (?, ?, ?, ?, 'completed')
                    ''', (teacher_id, selected_code, slo_id, entry_date))
                
                conn.commit()
                conn.close()
                
                st.success(f"✅ {len(sel_slos)} SLOs marked complete!")
                st.balloons()
            else:
                st.warning("Please select at least one SLO")
