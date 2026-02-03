import streamlit as st
import pandas as pd

def show(db, teacher_id, academic_year):
    st.markdown("# 📚 Abbreviations Reference")
    st.markdown("Complete list of all abbreviations used in the system")
    
    # Define all abbreviations
    abbreviations = {
        "Priority Levels": {
            "Mk": "Must to know",
            "Dk": "Desirable to know",
            "Nk": "Nice to know"
        },
        "Bloom's Taxonomy (Domain)": {
            "CK": "Cognitive - Knowledge",
            "CC": "Cognitive - Comprehension",
            "CAP": "Cognitive - Application",
            "CAN": "Cognitive - Analysis",
            "CS": "Cognitive - Synthesis",
            "CE": "Cognitive - Evaluation",
            "PSY-MEC": "Psychomotor - Mechanism",
            "AFT-RES": "Affective - Responding"
        },
        "Miller's Pyramid (Competency)": {
            "K": "Knows",
            "Kh": "Knows How",
            "Sh": "Shows How",
            "D": "Does"
        },
        "Teaching Methods": {
            "L": "Lecture",
            "DIS": "Discussion",
            "PBL": "Problem Based Learning",
            "CBL": "Case Based Learning",
            "D": "Demonstration",
            "TUT": "Tutorial",
            "SY": "Symposium",
            "SIM": "Simulation",
            "RP": "Role Play",
            "SDL": "Self Directed Learning",
            "FC": "Flipped Classroom",
            "BS": "Brain Storming",
            "TPW": "Team Project Work"
        },
        "Assessment Methods": {
            "T-MEQs": "Theory - Modified Essay Questions",
            "VV-Viva": "Viva Voce",
            "OSPE": "Objective Structured Practical Examination",
            "DOPS": "Direct Observation of Procedural Skills",
            "P-VIVA": "Practical Viva",
            "SA": "Situational Assessment",
            "T-CS": "Theory - Case Study",
            "OSCE": "Objective Structured Clinical Examination",
            "Mini-CEX": "Mini Clinical Evaluation Exercise",
            "CBA": "Case Based Assessment",
            "MCQ": "Multiple Choice Questions",
            "SAQ": "Short Answer Questions",
            "LAQ": "Long Answer Questions"
        },
        "Course & Program": {
            "CO": "Course Outcome",
            "PO": "Programme Outcome",
            "LH": "Lecture Hours",
            "NLHT": "Non-Lecture Hours Theory",
            "NLHP": "Non-Lecture Hours Practical"
        }
    }
    
    # Display in expandable sections
    for category, abbr_dict in abbreviations.items():
        with st.expander(f"📖 {category}", expanded=True):
            df = pd.DataFrame(list(abbr_dict.items()), columns=['Abbreviation', 'Full Form'])
            st.table(df)
    
    st.markdown("---")
    st.info("💡 **Tip:** These abbreviations are now shown with their full forms throughout the app!")
