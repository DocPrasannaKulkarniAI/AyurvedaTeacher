import streamlit as st
import json

def get_abbr_full(code, type='priority'):
    """Get full form of abbreviation"""
    mappings = {
        'priority': {'Mk': 'Must to know', 'Dk': 'Desirable to know', 'Nk': 'Nice to know'},
        'domain': {
            'CK': 'Cognitive-Knowledge', 'CC': 'Cognitive-Comprehension',
            'CAP': 'Cognitive-Application', 'CAN': 'Cognitive-Analysis',
            'PSY-MEC': 'Psychomotor-Mechanism', 'AFT-RES': 'Affective-Responding'
        },
        'competency': {'K': 'Knows', 'Kh': 'Knows How', 'Sh': 'Shows How', 'D': 'Does'}
    }
    return mappings.get(type, {}).get(code, code)

def show(db, teacher_id, academic_year):
    st.markdown("# 📖 Browse SLOs with Planning")
    
    selected_code = st.session_state.get('selected_subject_code')
    if not selected_code:
        st.warning("No subject selected")
        return
    
    st.info(f"**Subject:** {st.session_state.get('selected_subject_name')}")
    
    # TERM FILTER - NEW!
    col1, col2 = st.columns([1, 3])
    with col1:
        term_filter = st.selectbox("📅 Filter by Term", ["All Terms", "Term I", "Term II", "Term III"])
    
    term_val = None if term_filter == "All Terms" else term_filter.split()[1]
    
    # Get SLOs
    filters = {}
    if term_val:
        filters['term'] = term_val
    
    slos = db.get_syllabus_by_subject(selected_code, filters)
    
    if not slos:
        st.error("No SLOs found!")
        return
    
    st.success(f"📚 {len(slos)} SLOs available" + (f" (Term {term_val})" if term_val else ""))
    
    # Group by topic - REMOVE invalid entries
    topics = {}
    for slo in slos:
        t = slo.get('topic_number', 'General')
        # Skip if topic contains unwanted text
        if 'Q3 LAQ' in t or 'Must know' in t:
            continue
        if t not in topics:
            topics[t] = []
        topics[t].append(slo)
    
    if not topics:
        st.error("No topics found!")
        return
    
    st.markdown("---")
    
    # Topic selection
    topic_list = list(topics.keys())
    topic = st.selectbox("📑 Select Topic", topic_list)
    
    st.markdown(f"### {len(topics[topic])} SLOs in {topic}")
    
    # STATISTICS - NEW!
    mk = len([s for s in topics[topic] if s.get('priority_level') == 'Mk'])
    dk = len([s for s in topics[topic] if s.get('priority_level') == 'Dk'])
    nk = len([s for s in topics[topic] if s.get('priority_level') == 'Nk'])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🔴 Must Know", mk)
    with col2:
        st.metric("🟡 Desirable", dk)
    with col3:
        st.metric("🟢 Nice to Know", nk)
    
    st.markdown("---")
    
    # Display SLOs
    for idx, slo in enumerate(topics[topic], 1):
        with st.expander(f"📝 SLO {idx}: {slo['learning_objective_text'][:100]}..."):
            st.info(slo['learning_objective_text'])
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**🎯 Classification:**")
                domain_code = slo.get('domain_code', 'CC')
                st.markdown(f"**C3:** {domain_code} - {get_abbr_full(domain_code, 'domain')}")
                
                priority = slo.get('priority_level', 'Mk')
                icons = {'Mk': '🔴', 'Dk': '🟡', 'Nk': '🟢'}
                st.markdown(f"**D3:** {icons.get(priority)} {priority} - {get_abbr_full(priority, 'priority')}")
                
                comp = slo.get('competency_level', 'Kh')
                st.markdown(f"**E3:** {comp} - {get_abbr_full(comp, 'competency')}")
                
                st.markdown(f"**I3:** Term {slo.get('term')}")
            
            with col2:
                st.markdown("**📚 Teaching & Assessment:**")
                methods = json.loads(slo.get('teaching_methods_codes', '[]'))
                st.markdown(f"**F3:** {', '.join(methods) if methods else 'Lecture'}")
                
                assess = json.loads(slo.get('assessment_methods_codes', '[]'))
                st.markdown(f"**G3:** {', '.join(assess) if assess else 'Written'}")
                
                st.markdown(f"**H3:** {slo.get('assessment_type_full')}")
            
            with col3:
                st.markdown("**📊 Integration & Outcomes:**")
                integ = json.loads(slo.get('integration_codes', '[]')) if slo.get('integration_codes') else []
                st.markdown(f"**J3:** {', '.join(integ) if integ else 'None'}")
                
                st.markdown(f"**CO:** {slo.get('course_outcome')}")
                st.markdown(f"**PO:** {slo.get('programme_outcome')}")
            
            st.markdown("---")
            
            # PLANNING BUTTONS - NEW!
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                if st.button(f"📅 Select for Today's Class", key=f"today_{slo['syllabus_id']}"):
                    conn = db.get_connection()
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT OR REPLACE INTO planned_slos 
                        (teacher_id, subject_code, syllabus_id, plan_type, plan_date)
                        VALUES (?, ?, ?, 'today', date('now'))
                    ''', (teacher_id, selected_code, slo['syllabus_id']))
                    conn.commit()
                    conn.close()
                    st.success("✅ Added to today's plan!")
            
            with col_b:
                if st.button(f"📆 Select for Next Month", key=f"next_{slo['syllabus_id']}"):
                    conn = db.get_connection()
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT OR REPLACE INTO planned_slos 
                        (teacher_id, subject_code, syllabus_id, plan_type, plan_date)
                        VALUES (?, ?, ?, 'next_month', date('now'))
                    ''', (teacher_id, selected_code, slo['syllabus_id']))
                    conn.commit()
                    conn.close()
                    st.success("✅ Added to next month's plan!")
            
            with col_c:
                if st.button(f"✅ Mark Complete", key=f"complete_{slo['syllabus_id']}"):
                    conn = db.get_connection()
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT OR IGNORE INTO syllabus_coverage_log 
                        (teacher_id, subject_code, syllabus_id, coverage_date, coverage_status)
                        VALUES (?, ?, ?, date('now'), 'completed')
                    ''', (teacher_id, selected_code, slo['syllabus_id']))
                    conn.commit()
                    conn.close()
                    st.success("✅ Marked complete!")
