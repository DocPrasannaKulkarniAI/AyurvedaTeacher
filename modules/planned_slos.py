import streamlit as st

def show(db, teacher_id, academic_year):
    st.markdown("# 📝 My Planned SLOs")
    st.markdown("SLOs you've selected for teaching")
    
    selected_code = st.session_state.get('selected_subject_code')
    if not selected_code:
        st.warning("No subject selected")
        return
    
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Get today's plans
    cursor.execute('''
        SELECT ps.*, sm.learning_objective_text, sm.topic_number
        FROM planned_slos ps
        JOIN syllabus_master sm ON ps.syllabus_id = sm.syllabus_id
        WHERE ps.teacher_id = ? AND ps.subject_code = ? AND ps.plan_type = 'today'
        ORDER BY ps.plan_date DESC
    ''', (teacher_id, selected_code))
    today_plans = [dict(r) for r in cursor.fetchall()]
    
    # Get next month plans
    cursor.execute('''
        SELECT ps.*, sm.learning_objective_text, sm.topic_number
        FROM planned_slos ps
        JOIN syllabus_master sm ON ps.syllabus_id = sm.syllabus_id
        WHERE ps.teacher_id = ? AND ps.subject_code = ? AND ps.plan_type = 'next_month'
        ORDER BY ps.plan_date DESC
    ''', (teacher_id, selected_code))
    next_plans = [dict(r) for r in cursor.fetchall()]
    
    conn.close()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📅 Today's Class")
        if today_plans:
            for idx, plan in enumerate(today_plans, 1):
                st.markdown(f"**{idx}. {plan['topic_number']}**")
                st.info(plan['learning_objective_text'][:150] + "...")
                st.markdown("---")
        else:
            st.info("No SLOs planned for today")
    
    with col2:
        st.markdown("### 📆 Next Month")
        if next_plans:
            for idx, plan in enumerate(next_plans, 1):
                st.markdown(f"**{idx}. {plan['topic_number']}**")
                st.info(plan['learning_objective_text'][:150] + "...")
                st.markdown("---")
        else:
            st.info("No SLOs planned for next month")
