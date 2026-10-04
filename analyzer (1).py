import re
from datetime import datetime
from typing import Dict, List, Any, Set, Tuple

# Comprehensive tech and professional skill dictionary with aliases/synonyms
SKILL_TAXONOMY = {
    "python": ["python", "python3", "py"],
    "javascript": ["javascript", "js", "ecmascript"],
    "typescript": ["typescript", "ts"],
    "react": ["react", "react.js", "reactjs"],
    "next.js": ["next.js", "nextjs", "next"],
    "vue": ["vue", "vue.js", "vuejs"],
    "angular": ["angular", "angularjs"],
    "node.js": ["node", "node.js", "nodejs"],
    "express": ["express", "express.js", "expressjs"],
    "fastapi": ["fastapi"],
    "django": ["django"],
    "flask": ["flask"],
    "java": ["java", "spring", "spring boot", "springboot"],
    "c++": ["c++", "cpp"],
    "c#": ["c#", "csharp", ".net", "dotnet"],
    "golang": ["golang", "go"],
    "rust": ["rust"],
    "sql": ["sql", "mysql", "postgresql", "postgres", "sqlite", "mssql", "oracle"],
    "nosql": ["nosql", "mongodb", "mongo", "cassandra", "couchdb", "dynamodb"],
    "redis": ["redis"],
    "docker": ["docker", "containerization"],
    "kubernetes": ["kubernetes", "k8s"],
    "aws": ["aws", "amazon web services", "ec2", "s3", "lambda"],
    "azure": ["azure", "microsoft azure"],
    "gcp": ["gcp", "google cloud", "google cloud platform"],
    "git": ["git", "github", "gitlab", "version control"],
    "ci/cd": ["ci/cd", "github actions", "jenkins", "gitlab ci", "circleci"],
    "machine learning": ["machine learning", "ml", "scikit-learn", "sklearn"],
    "deep learning": ["deep learning", "neural networks", "pytorch", "tensorflow", "keras"],
    "nlp": ["nlp", "natural language processing", "spacy", "nltk", "transformers", "llm", "rag"],
    "computer vision": ["computer vision", "opencv"],
    "data science": ["data science", "pandas", "numpy", "matplotlib", "seaborn"],
    "graphql": ["graphql"],
    "rest api": ["rest", "restful", "rest api", "apis"],
    "microservices": ["microservices"],
    "linux": ["linux", "unix", "bash", "shell scripting"],
    "cybersecurity": ["cybersecurity", "infosec", "penetration testing", "owasp"],
    "agile": ["agile", "scrum", "kanban", "jira"],
    "html/css": ["html", "css", "html5", "css3", "tailwind", "bootstrap", "sass"]
}

DEGREE_PATTERNS = [
    r"\b(ph\.?d\.?|doctor of philosophy)\b",
    r"\b(m\.?s\.?|m\.?tech|master(?:'?s)?(?:\s+of\s+science|\s+of\s+technology)?)\b",
    r"\b(b\.?s\.?|b\.?tech|b\.?e\.?|bachelor(?:'?s)?(?:\s+of\s+science|\s+of\s+technology|\s+of\s+engineering)?)\b",
    r"\b(bca|mca|bba|mba)\b",
    r"\b(diploma|associate(?:'?s)?)\b"
]

def extract_email(text: str) -> str:
    match = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
    return match.group(0) if match else "Not found"

def extract_phone(text: str) -> str:
    match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    return match.group(0) if match else "Not found"

def extract_name(text: str, filename: str = "") -> str:
    """Heuristic extraction of candidate name."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines[:5]:
        # Filter out obvious non-name headers
        if re.search(r'(resume|curriculum|vitae|page|contact|email|phone|http|github|linkedin|profile)', line, re.IGNORECASE):
            continue
        # If line is 2 to 4 capitalized words, good candidate
        words = line.split()
        if 2 <= len(words) <= 4 and all(w[0].isupper() or w in ["de", "van", "von"] for w in words if w.isalpha()):
            return line
    # Fallback to filename
    if filename:
        clean_name = re.sub(r'[\-_]', ' ', re.sub(r'\.(pdf|docx|txt)$', '', filename, flags=re.IGNORECASE))
        return clean_name.title()
    return "Candidate"

def extract_skills_from_text(text: str) -> Tuple[Set[str], Dict[str, List[str]]]:
    """Finds standardized skills present in the text."""
    text_lower = text.lower()
    found_skills = set()
    skill_evidence = {}

    for standard_skill, aliases in SKILL_TAXONOMY.items():
        matched_aliases = []
        for alias in aliases:
            pattern = r'(?<![a-zA-Z0-9])' + re.escape(alias) + r'(?![a-zA-Z0-9])'
            if re.search(pattern, text_lower):
                matched_aliases.append(alias)
        if matched_aliases:
            found_skills.add(standard_skill)
            skill_evidence[standard_skill] = matched_aliases

    return found_skills, skill_evidence

def extract_experience_years(text: str) -> float:
    """Calculates approximate years of experience from explicit mentions and date ranges."""
    # 1. Direct mentions like "5+ years of experience" or "4 years exp"
    explicit_matches = re.findall(r'(\d+(?:\.\d+)?)\+?\s*(?:years?|yrs?)(?:\s+of)?(?:\s+experience|\s+exp)?', text, re.IGNORECASE)
    explicit_years = [float(y) for y in explicit_matches if float(y) < 45]

    # 2. Date ranges like "2019 - 2023" or "Jan 2021 - Present"
    current_year = datetime.now().year
    year_ranges = re.findall(r'\b(20\d\d|19\d\d)\s*(?:-|–|to)\s*(20\d\d|present|current|now)\b', text, re.IGNORECASE)
    
    range_years = 0.0
    for start_str, end_str in year_ranges:
        start_yr = int(start_str)
        end_yr = current_year if end_str.lower() in ["present", "current", "now"] else int(end_str)
        if 1980 <= start_yr <= end_yr <= current_year + 1:
            diff = max(0.5, float(end_yr - start_yr))
            range_years += diff

    # Deduplicate / blend
    if explicit_years and range_years > 0:
        return max(max(explicit_years), min(range_years, 35.0))
    elif explicit_years:
        return max(explicit_years)
    elif range_years > 0:
        return min(range_years, 35.0)
    return 1.0  # Default assumption for entry-level if not specified

def extract_education(text: str) -> List[str]:
    """Finds education qualifications and degrees."""
    degrees_found = []
    for pattern in DEGREE_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            deg = match.group(0).upper()
            if deg not in degrees_found:
                degrees_found.append(deg)
    return degrees_found if degrees_found else ["Degree/Education mentioned"]

def detect_contradictions_and_fraud(text: str, candidate_info: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    INNOVATION / BONUS FEATURE (per Algothon'26 PS ALG-AI-01):
    Detect unsupported or contradictory claims instead of blindly rewarding keyword matches.
    """
    alerts = []
    text_lower = text.lower()
    current_year = datetime.now().year

    # Check 1: Timeline Contradiction (Graduation vs Claimed Experience)
    grad_years = re.findall(r'(?:graduated|graduation|batch\s+of|completed|class\s+of|degree)?\s*(?:in\s+)?(20[12]\d)', text, re.IGNORECASE)
    if grad_years:
        latest_grad_yr = max(int(y) for y in grad_years if int(y) <= current_year)
        years_since_grad = max(0, current_year - latest_grad_yr)
        claimed_exp = candidate_info.get("years_of_experience", 0)

        # If claiming 5+ years of experience but graduated 1-2 years ago
        if claimed_exp >= (years_since_grad + 3) and years_since_grad < 4:
            alerts.append({
                "severity": "HIGH",
                "type": "Timeline Contradiction",
                "message": f"Candidate claims ~{claimed_exp:.1f} years experience, but graduation record indicates completion in {latest_grad_yr} ({years_since_grad} years ago)."
            })

    # Check 2: Keyword Stuffing / Buzzword Wall
    # Check if more than 22 skills are listed in an isolated block without contextual sentences
    skill_mentions = candidate_info.get("skills", set())
    if len(skill_mentions) >= 20:
        word_count = max(1, len(text.split()))
        density = len(skill_mentions) / (word_count / 100)
        # Flag if extreme density (e.g. >15% of all words are distinct buzzwords)
        if density > 15.0 or (len(skill_mentions) >= 28 and density > 8.0):
            alerts.append({
                "severity": "MEDIUM",
                "type": "Keyword Stuffing",
                "message": f"High buzzword density detected ({len(skill_mentions)} distinct skills in {word_count} words). Potential ATS keyword stuffing."
            })

    # Check 3: Unsubstantiated Skill Claims (Skills in header/list that are never mentioned in project descriptions)
    # If the resume has a "Projects" or "Experience" section, verify if claimed top skills appear there
    sections = re.split(r'\n(?=[A-Z\s]{4,}:|\b(?:EXPERIENCE|PROJECTS|WORK HISTORY|EMPLOYMENT)\b)', text, flags=re.IGNORECASE)
    if len(sections) > 1:
        experience_text = " ".join(sections[1:]).lower()
        unsubstantiated = []
        for s in list(skill_mentions)[:6]:  # Test top skills
            if s not in experience_text:
                unsubstantiated.append(s)
        if len(unsubstantiated) >= 3:
            alerts.append({
                "severity": "LOW",
                "type": "Unsubstantiated Skills",
                "message": f"Skills listed in summary ({', '.join(unsubstantiated)}) do not appear in detailed project/work history bullets."
            })

    # Check 4: Future or Invalid Date Ranges
    future_dates = re.findall(r'\b(20[3-9]\d)\b', text)
    if future_dates:
        alerts.append({
            "severity": "MEDIUM",
            "type": "Invalid Date",
            "message": f"Resume contains future year ({future_dates[0]}), possibly a typo or synthetic profile."
        })

    return alerts

def parse_job_description(jd_text: str) -> Dict[str, Any]:
    """Parses a job description to extract required skills, min years, and education."""
    skills, _ = extract_skills_from_text(jd_text)
    
    # Required experience
    exp_matches = re.findall(r'(\d+)(?:\+|-|\s+to\s+\d+)?\s*(?:years?|yrs?)', jd_text, re.IGNORECASE)
    min_exp = float(exp_matches[0]) if exp_matches else 2.0

    # Required education
    edu = extract_education(jd_text)

    return {
        "required_skills": skills,
        "min_experience_years": min_exp,
        "required_education": edu,
        "word_count": len(jd_text.split())
    }

def analyze_resume(resume_text: str, filename: str, jd_data: Dict[str, Any]) -> Dict[str, Any]:
    """Scores and explains match between a single resume and the job description."""
    candidate_skills, evidence = extract_skills_from_text(resume_text)
    exp_years = extract_experience_years(resume_text)
    education = extract_education(resume_text)
    name = extract_name(resume_text, filename)
    email = extract_email(resume_text)
    phone = extract_phone(resume_text)

    candidate_info = {
        "name": name,
        "filename": filename,
        "email": email,
        "phone": phone,
        "skills": candidate_skills,
        "skill_evidence": evidence,
        "years_of_experience": exp_years,
        "education": education
    }

    # 1. Skills Match Calculation
    req_skills = jd_data.get("required_skills", set())
    if req_skills:
        matched_skills = candidate_skills.intersection(req_skills)
        missing_skills = req_skills.difference(candidate_skills)
        skills_score = (len(matched_skills) / len(req_skills)) * 100.0
    else:
        # If JD has no recognized skills, use candidate skill richness
        matched_skills = candidate_skills
        missing_skills = set()
        skills_score = min(100.0, len(candidate_skills) * 10)

    # 2. Experience Score Calculation
    req_exp = jd_data.get("min_experience_years", 2.0)
    if exp_years >= req_exp:
        exp_score = 100.0
    else:
        exp_score = max(20.0, (exp_years / max(1.0, req_exp)) * 100.0)

    # 3. Education Score
    edu_score = 90.0 if education else 70.0

    # 4. Overall Weighted Composite Score
    # 60% Skills, 30% Experience, 10% Education
    composite_score = (0.60 * skills_score) + (0.30 * exp_score) + (0.10 * edu_score)
    
    # 5. Contradiction & Fraud Checks (Bonus Feature!)
    fraud_alerts = detect_contradictions_and_fraud(resume_text, candidate_info)
    
    # Apply reasonable penalty if high-severity fraud/contradiction detected
    has_high_fraud = any(a["severity"] == "HIGH" for a in fraud_alerts)
    if has_high_fraud:
        composite_score = max(10.0, composite_score * 0.85)

    # 6. Natural Language Explainability Breakdown
    explanation_points = []
    if matched_skills:
        explanation_points.append(f"Strong match on {len(matched_skills)} core skills: {', '.join(sorted(list(matched_skills))[:5])}.")
    if missing_skills:
        explanation_points.append(f"Missing critical requirements: {', '.join(sorted(list(missing_skills))[:4])}.")
    
    if exp_years >= req_exp:
        explanation_points.append(f"Experience aligns well: candidate has ~{exp_years:.1f} years (role requires {req_exp:.0f}+ years).")
    else:
        explanation_points.append(f"Experience gap: candidate has ~{exp_years:.1f} years against {req_exp:.0f}+ years required.")

    if fraud_alerts:
        explanation_points.append(f"⚠️ Flagged for recruiter review: {len(fraud_alerts)} credibility warning(s) detected.")

    return {
        "candidate_info": candidate_info,
        "match_score": round(composite_score, 1),
        "skills_score": round(skills_score, 1),
        "experience_score": round(exp_score, 1),
        "education_score": round(edu_score, 1),
        "matched_skills": sorted(list(matched_skills)),
        "missing_skills": sorted(list(missing_skills)),
        "all_candidate_skills": sorted(list(candidate_skills)),
        "fraud_alerts": fraud_alerts,
        "explanation": " ".join(explanation_points)
    }
