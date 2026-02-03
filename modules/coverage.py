import streamlit as st

def show(db, teacher_id, academic_year):
    st.markdown("# 📊 Coverage Tracker")
    
    # Get selected subject
    selected_code = st.session_state.get('selected_subject_code')
    selected_name = st.session_state.get('selected_subject_name')
    
    if not selected_code:
        st.warning("No subject selected.")
        return
    
    st.info(f"**Subject:** {selected_name}")
    
    # Get stats
    stats = db.get_coverage_stats(teacher_id, selected_code)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total SLOs", stats['total'])
    with col2:
        st.metric("Completed", stats['covered'])
    with col3:
        st.metric("Coverage", f"{stats['percentage']}%")
    
    st.progress(stats['percentage'] / 100)
    
    if stats.get('by_priority'):
        st.markdown("---")
        st.markdown("### By Priority")
        for pri, data in stats['by_priority'].items():
            pct = round((data['covered'] / data['total'] * 100) if data['total'] > 0 else 0, 1)
            icons = {'Mk': '🔴', 'Dk': '🟡', 'Nk': '🟢'}
            st.markdown(f"{icons.get(pri, '⚪')} **{pri}:** {data['covered']}/{data['total']} ({pct}%)")
            st.progress(pct / 100)
