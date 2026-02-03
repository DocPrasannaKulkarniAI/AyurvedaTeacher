import streamlit as st

def show(db, teacher_id, academic_year):
    st.markdown("# 🏠 Dashboard")
    
    # Get selected subject
    selected_code = st.session_state.get('selected_subject_code')
    selected_name = st.session_state.get('selected_subject_name')
    
    if not selected_code:
        st.warning("No subject selected.")
        # Show total database info
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM syllabus_master")
        total = cursor.fetchone()[0]
        conn.close()
        st.success(f"📚 {total:,} SLOs available in database")
        return
    
    st.info(f"**Your Subject:** {selected_name}")
    
    # Get stats
    stats = db.get_coverage_stats(teacher_id, selected_code)
    
    # Quick metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📚 Total SLOs", stats['total'])
    with col2:
        st.metric("✅ Completed", stats['covered'])
    with col3:
        st.metric("📊 Coverage", f"{stats['percentage']}%")
    with col4:
        pending = stats['total'] - stats['covered']
        st.metric("⏳ Pending", pending)
    
    st.markdown("---")
    
    # Progress bar
    st.markdown("### Overall Progress")
    st.progress(stats['percentage'] / 100)
    
    st.markdown("---")
    
    # By priority
    if stats.get('by_priority'):
        st.markdown("### Progress by Priority")
        
        for pri, data in stats['by_priority'].items():
            pct = round((data['covered'] / data['total'] * 100) if data['total'] > 0 else 0, 1)
            
            icons = {'Mk': '🔴', 'Dk': '🟡', 'Nk': '🟢'}
            names = {'Mk': 'Must Know', 'Dk': 'Desirable', 'Nk': 'Nice to Know'}
            
            st.markdown(f"#### {icons.get(pri, '⚪')} {names.get(pri, pri)}")
            st.markdown(f"{data['covered']} / {data['total']} SLOs ({pct}%)")
            st.progress(pct / 100)
            st.markdown("")
