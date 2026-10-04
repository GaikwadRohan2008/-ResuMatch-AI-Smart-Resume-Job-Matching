import streamlit as st
import pandas as pd
import os
import io
from extractor import extract_text
from analyzer import parse_job_description, analyze_resume

st.set_page_config(
    page_title="ResuMatch AI | Algothon'26",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for modern hackathon presentation
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
    }
    .badge-green {
        background-color: #DCFCE7;
        color: #166534;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-right: 4px;
        margin-bottom: 4px;
        display: inline-block;
    }
    .badge-red {
        background-color: #FEE2E2;
        color: #991B1B;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-right: 4px;
        margin-bottom: 4px;
        display: inline-block;
    }
    .badge-alert {
        background-color: #FEF3C7;
        color: #92400E;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.82rem;
        font-weight: 600;
        display: inline-block;
    }
    .candidate-card {
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 18px;
        background-color: #FFFFFF;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    #MainMenu {visibility: hidden; display: none !important;}
    footer {visibility: hidden; display: none !important;}
    header {visibility: hidden; display: none !important;}
    div[data-testid="stToolbar"] {visibility: hidden; display: none !important;}
    div[data-testid="stDecoration"] {visibility: hidden; display: none !important;}
    div[data-testid="stStatusWidget"] {visibility: hidden; display: none !important;}
    #stDecoration {visibility: hidden; display: none !important;}
    .stDeployButton {display: none !important;}
    [data-testid="manage-app-button"] {display: none !important;}
    .viewerBadge_container__1QSob {display: none !important;}
    .viewerBadge_link__1QSob {display: none !important;}
    a[href*="streamlit.io"] {display: none !important;}
    footer:after {content: ""; display: none !important;}
</style>
""", unsafe_allow_html=True)

# Application Header
col_logo, col_header = st.columns([1, 10])
with col_header:
    st.markdown('<div class="main-title">🎯 ResuMatch AI — Smart Resume & Job Matching</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title"><b>Algothon’26 | PS ID: ALG-AI-01</b> • AI-Powered Candidate Ranking, Explainability & Fraud Detection</div>', unsafe_allow_html=True)

# Helper function to get sample paths
SAMPLES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samples")

# Initialize session state for inputs
if "jd_text" not in st.session_state:
    st.session_state.jd_text = ""
if "loaded_demo" not in st.session_state:
    st.session_state.loaded_demo = False
if "demo_resumes" not in st.session_state:
    st.session_state.demo_resumes = []

def load_demo_data():
    jd_path = os.path.join(SAMPLES_DIR, "job_description.txt")
    if os.path.exists(jd_path):
        with open(jd_path, "r", encoding="utf-8") as f:
            st.session_state.jd_text = f.read()
    
    sample_files = [
        "Alex_Rivera_Senior_FullStack.txt",
        "Samantha_Chen_Junior_Developer.txt",
        "Kevin_Vance_Contradiction_Alert.txt",
        "Maria_Gonzalez_Marketing_Lead.txt"
    ]
    st.session_state.demo_resumes = []
    for sf in sample_files:
        p = os.path.join(SAMPLES_DIR, sf)
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                st.session_state.demo_resumes.append({
                    "name": sf,
                    "content": f.read()
                })
    st.session_state.loaded_demo = True

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.header("⚡ Quick Controls")
    
    if st.button("🚀 Load 1-Click Demo Suite", type="primary", use_container_width=True):
        load_demo_data()
        st.success("Loaded Sample JD and 4 Test Resumes!")
        st.rerun()

    st.markdown("---")
    st.header("🔍 Filters & Ranking")
    min_score_filter = st.slider("Minimum Match Score (%)", min_value=0, max_value=100, value=0, step=5)
    min_exp_filter = st.slider("Minimum Experience (Years)", min_value=0.0, max_value=15.0, value=0.0, step=0.5)
    flagged_only = st.checkbox("Show Only Credibility Flagged Resumes ⚠️", value=False)
    
    st.markdown("---")
    st.subheader("ℹ️ Algothon'26 PS Details")
    st.caption("**Domain:** AI / Machine Learning")
    st.caption("**Challenge ID:** ALG-AI-01")
    st.caption("**Bonus Track:** Contradiction & Keyword Stuffing Detection")
    st.caption("**Reliability Engine:** Fallback rule-based NLP + Regex Extraction (100% Offline Capable)")

# --- MAIN INPUT SECTION ---
input_col1, input_col2 = st.columns([1, 1])

with input_col1:
    st.subheader("1. Job Description")
    jd_input = st.text_area(
        "Paste Job Description here:",
        value=st.session_state.jd_text,
        height=220,
        placeholder="e.g. Seeking Full Stack Python Developer with 3+ years experience in React, FastAPI, SQL..."
    )
    if jd_input != st.session_state.jd_text:
        st.session_state.jd_text = jd_input

with input_col2:
    st.subheader("2. Upload Resumes")
    uploaded_files = st.file_uploader(
        "Upload Resumes (PDF, DOCX, or TXT)",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True
    )
    
    if st.session_state.loaded_demo and not uploaded_files:
        st.info(f"Loaded {len(st.session_state.demo_resumes)} sample resumes from the Demo Suite.")

# --- ANALYSIS TRIGGER ---
has_resumes = (uploaded_files is not None and len(uploaded_files) > 0) or (len(st.session_state.demo_resumes) > 0)
has_jd = len(st.session_state.jd_text.strip()) > 20

st.markdown("---")

if not has_jd or not has_resumes:
    st.info("👋 **Get Started:** Click **'🚀 Load 1-Click Demo Suite'** in the sidebar to populate instant test cases, or upload your own Job Description and Resumes above.")
else:
    # Run Analysis
    with st.spinner("Analyzing candidate resumes against job criteria..."):
        jd_data = parse_job_description(st.session_state.jd_text)
        
        results = []
        
        # Process user uploaded files
        if uploaded_files:
            for uf in uploaded_files:
                text = extract_text(uf, uf.name)
                res = analyze_resume(text, uf.name, jd_data)
                results.append(res)
        # Or process loaded demo resumes
        elif st.session_state.demo_resumes:
            for dr in st.session_state.demo_resumes:
                res = analyze_resume(dr["content"], dr["name"], jd_data)
                results.append(res)

        # Sort by match score descending
        results = sorted(results, key=lambda x: x["match_score"], reverse=True)

    # Filter results based on sidebar
    filtered_results = []
    for r in results:
        if r["match_score"] < min_score_filter:
            continue
        if r["candidate_info"]["years_of_experience"] < min_exp_filter:
            continue
        if flagged_only and len(r["fraud_alerts"]) == 0:
            continue
        filtered_results.append(r)

    # --- TABS FOR RESULTS & EXPLAINABILITY ---
    tab_rankings, tab_jd, tab_bonus, tab_architecture = st.tabs([
        "📊 Ranked Candidates", 
        "📋 Job Profile Insights", 
        "🛡️ Fraud & Contradiction Engine", 
        "🏗️ Architecture & Rubric"
    ])

    with tab_rankings:
        # KPI Metrics Row
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1:
            st.metric("Total Resumes Analyzed", len(results))
        with kpi2:
            top_score = f"{results[0]['match_score']}%" if results else "N/A"
            top_cand = results[0]['candidate_info']['name'] if results else "N/A"
            st.metric("Top Ranked Match", top_score, delta=top_cand)
        with kpi3:
            avg_score = round(sum(r["match_score"] for r in results) / max(1, len(results)), 1)
            st.metric("Average Score", f"{avg_score}%")
        with kpi4:
            total_flags = sum(len(r["fraud_alerts"]) for r in results)
            st.metric("Credibility Alerts", total_flags, delta_color="inverse")

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader(f"Ranked Leaderboard ({len(filtered_results)} Candidates)")

        if not filtered_results:
            st.warning("No candidates match your current filter settings. Adjust sliders in the sidebar.")
        else:
            for rank_idx, cand in enumerate(filtered_results, 1):
                score = cand["match_score"]
                info = cand["candidate_info"]
                fraud_count = len(cand["fraud_alerts"])

                # Determine badge color
                score_color = "#16A34A" if score >= 80 else ("#D97706" if score >= 50 else "#DC2626")

                with st.container():
                    st.markdown(f"""
                    <div class="candidate-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="font-size: 1.25rem; font-weight: 700; color: #1E293B;">#{rank_idx} {info['name']}</span>
                                <span style="color: #64748B; margin-left: 10px; font-size: 0.9rem;">📄 {info['filename']}</span>
                            </div>
                            <div style="font-size: 1.5rem; font-weight: 800; color: {score_color};">
                                {score}% Match
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    c_left, c_right = st.columns([2, 1])
                    with c_left:
                        st.markdown(f"**Email:** `{info['email']}` | **Phone:** `{info['phone']}` | **Experience:** ~{info['years_of_experience']:.1f} yrs")
                        st.markdown(f"**Education:** {', '.join(info['education'])}")

                        # Matched Skills
                        if cand["matched_skills"]:
                            matched_badges = "".join([f'<span class="badge-green">✓ {s}</span>' for s in cand["matched_skills"]])
                            st.markdown(f"**Matched Skills:**<br>{matched_badges}", unsafe_allow_html=True)

                        # Missing Skills
                        if cand["missing_skills"]:
                            missing_badges = "".join([f'<span class="badge-red">✗ {s}</span>' for s in cand["missing_skills"]])
                            st.markdown(f"**Missing Skills:**<br>{missing_badges}", unsafe_allow_html=True)

                    with c_right:
                        st.caption("Score Breakdown")
                        st.progress(cand["skills_score"] / 100, text=f"Skills Overlap: {cand['skills_score']}%")
                        st.progress(cand["experience_score"] / 100, text=f"Experience Match: {cand['experience_score']}%")

                    # Fraud Warnings if present
                    if fraud_count > 0:
                        for alert in cand["fraud_alerts"]:
                            st.warning(f"⚠️ **{alert['type']} ({alert['severity']} Severity):** {alert['message']}")

                    # Explainability drop-down
                    with st.expander(f"🔍 View Full Explainability & Match Evidence for {info['name']}"):
                        st.markdown(f"**Evaluation Analysis:** {cand['explanation']}")
                        st.markdown(f"**All Extracted Candidate Skills ({len(cand['all_candidate_skills'])}):** `{', '.join(cand['all_candidate_skills'])}`")

                    st.markdown("---")

            # CSV Export feature
            export_rows = []
            for r in filtered_results:
                export_rows.append({
                    "Candidate Name": r["candidate_info"]["name"],
                    "Match Score (%)": r["match_score"],
                    "Skills Score (%)": r["skills_score"],
                    "Experience (Years)": r["candidate_info"]["years_of_experience"],
                    "Matched Skills": ", ".join(r["matched_skills"]),
                    "Missing Skills": ", ".join(r["missing_skills"]),
                    "Credibility Flags": len(r["fraud_alerts"]),
                    "Email": r["candidate_info"]["email"]
                })
            df_export = pd.DataFrame(export_rows)
            st.download_button(
                "📥 Export Filtered Rankings as CSV",
                data=df_export.to_csv(index=False).encode('utf-8'),
                file_name="resumatch_rankings.csv",
                mime="text/csv"
            )

    with tab_jd:
        st.subheader("Extracted Job Requirements")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Total Skills Required", len(jd_data["required_skills"]))
        with c2:
            st.metric("Min Experience Required", f"{jd_data['min_experience_years']:.0f}+ Years")
        with c3:
            st.metric("Education Baseline", ", ".join(jd_data["required_education"]))

        st.markdown("**Required Skills Extracted from Job Description:**")
        if jd_data["required_skills"]:
            badges = "".join([f'<span class="badge-green">{s}</span>' for s in sorted(list(jd_data["required_skills"]))])
            st.markdown(badges, unsafe_allow_html=True)
        else:
            st.info("No standardized technical skills detected in the job description.")

    with tab_bonus:
        st.subheader("🛡️ Algothon'26 Innovation Track: Anti-Fraud & Contradiction Detection")
        st.markdown("""
        **Challenge Requirement (Slide 4):**
        > *"Detect unsupported or contradictory claims instead of blindly rewarding keyword matches."*
        
        ### How Our Innovation Works:
        Standard ATS (Applicant Tracking Systems) blindly reward resumes that pack 50 keywords into white text or summaries. **ResuMatch AI** runs 4 verification filters:
        """)
        
        b1, b2 = st.columns(2)
        with b1:
            st.markdown("""
            1. **Timeline Contradiction Check:**  
               Compares the graduation year with total claimed experience. If a candidate claims 8 years experience but graduated in 2023, a **HIGH SEVERITY** flag is generated.
            2. **Keyword Stuffing & Density Check:**  
               Flags candidates who list an unnatural density of buzzwords without corresponding descriptions.
            """)
        with b2:
            st.markdown("""
            3. **Unsubstantiated Skill Claims:**  
               Detects skills placed in the header that never appear in actual job bullets or accomplishments.
            4. **Impossible / Future Date Filter:**  
               Flags anomalous dates like 2030 or start dates after end dates.
            """)

        flagged_candidates = [r for r in results if len(r["fraud_alerts"]) > 0]
        st.markdown("#### Currently Flagged Candidates in Dataset:")
        if flagged_candidates:
            for fc in flagged_candidates:
                st.error(f"🚩 **{fc['candidate_info']['name']}** ({fc['candidate_info']['filename']})")
                for fa in fc["fraud_alerts"]:
                    st.write(f"- **{fa['type']}**: {fa['message']}")
        else:
            st.success("No fraud or contradiction anomalies detected in current candidates.")

    with tab_architecture:
        st.subheader("Project Documentation & Rubric Alignment")
        st.markdown("""
        ### System Architecture
        ```
        [ Resume Files: PDF / DOCX / TXT ]  ──>  [ Universal Extractor (pypdf, python-docx) ]
                                                                 │
        [ Job Description Input ]          ──>  [ Skill & Requirement Parser ]
                                                                 │
                                                                 ▼
                                                  [ Dual Matching Engine ]
                                                  • Semantic Skills Overlap
                                                  • Experience Range Normalizer
                                                  • Anti-Fraud Contradiction Filter
                                                                 │
                                                                 ▼
                                                  [ Recruiter Dashboard ]
                                                  • Ranked Leaderboard
                                                  • Explainability Cards
                                                  • CSV Export & Filters
        ```
        
        ### Algothon'26 100% Evaluation Rubric Checklist:
        - [x] **Functionality & Completion (30%):** End-to-end multi-resume upload, extraction, scoring, ranking, and export.
        - [x] **Technical Implementation (20%):** Modular Python architecture (`extractor.py`, `analyzer.py`, `app.py`).
        - [x] **Innovation & Problem Understanding (20%):** Automated detection of timeline contradictions & keyword stuffing.
        - [x] **Testing, Edge Cases & Reliability (15%):** Fallback parser for messy resumes, zero-network crash resistance, sample test cases provided.
        - [x] **User Experience & Presentation (15%):** Clean, responsive web dashboard with color-coded badges, KPI cards, and instant 1-click demo suite.
        """)
