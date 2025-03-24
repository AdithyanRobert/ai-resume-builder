import streamlit as st
import json
import requests
from io import StringIO


st.set_page_config(page_title="AI Resume Builder", layout="wide")
st.title("Thunderbolt Resume builder")
st.title("NOTE:This application is underdevelopement")


if 'resume' not in st.session_state:
    st.session_state.resume = {
        'name': '',
        'email': '',
        'phone': '',
        'summary': '',
        'experience': [{'job': '', 'company': '', 'years': '', 'details': ''}],
        'education': [{'degree': '', 'school': '', 'years': ''}],
        'skills': []
    }
with st.sidebar:
    st.header("AI Settings")
    hf_api_key = st.text_input("Hugging Face API Key (optional)", type="password", key="hf_api_key_input")
    st.markdown("[Get your free API key](https://huggingface.co/settings/tokens)")
   
def get_ai_suggestion(prompt, context=""):
    if not hf_api_key:
        return "Please add your Hugging Face API key to enable suggestions"
    
    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
    headers = {"Authorization": f"Bearer {hf_api_key}"}
    
    try:
        response = requests.post(API_URL, headers=headers, json={
            "inputs": f"{context}\n\n{prompt}",
            "parameters": {"max_new_tokens": 200}
        })
        return response.json()[0]['generated_text'].split(prompt)[-1].strip()
    except Exception as e:
        return f"AI suggestion failed: {str(e)}"

# Personal Information
st.header("1. Personal Information")
col1, col2 = st.columns(2)
with col1:
    st.session_state.resume['name'] = st.text_input("Full Name", st.session_state.resume['name'], key="name_input")
    st.session_state.resume['email'] = st.text_input("Email", st.session_state.resume['email'], key="email_input")
with col2:
    st.session_state.resume['phone'] = st.text_input("Phone", st.session_state.resume['phone'], key="phone_input")
st.header("2. Professional Summary")
summary = st.text_area("Tell us about yourself", st.session_state.resume['summary'], height=100, key="summary_textarea")

if st.button("Get AI Suggestion for Summary", key="summary_suggestion_btn"):
    suggestion = get_ai_suggestion(
        "Write a professional resume summary for someone with this information:",
        f"Name: {st.session_state.resume['name']}\nCurrent summary: {summary}"
    )
    if suggestion and not suggestion.startswith("AI suggestion failed"):
        st.session_state.resume['summary'] = suggestion
        st.rerun()

st.session_state.resume['summary'] = summary

st.header("3. Work Experience")
for i, exp in enumerate(st.session_state.resume['experience']):
    st.subheader(f"Job {i+1}")
    cols = st.columns([2, 2, 1])
    with cols[0]:
        st.session_state.resume['experience'][i]['job'] = st.text_input(
            f"Job Title {i+1}", 
            exp['job'],
            key=f"job_title_{i}"
        )
    with cols[1]:
        st.session_state.resume['experience'][i]['company'] = st.text_input(
            f"Company {i+1}", 
            exp['company'],
            key=f"company_{i}"
        )
    with cols[2]:
        st.session_state.resume['experience'][i]['years'] = st.text_input(
            f"Years {i+1}", 
            exp['years'],
            key=f"exp_years_{i}"
        )
    
    details = st.text_area(
        f"Job Details {i+1}", 
        exp['details'], 
        height=80,
        key=f"job_details_{i}"
    )
    
    if st.button(f"Improve Job Description {i+1}", key=f"improve_job_{i}"):
        suggestion = get_ai_suggestion(
            "Improve this job description for a resume:",
            f"Job: {st.session_state.resume['experience'][i]['job']} at {st.session_state.resume['experience'][i]['company']}\nCurrent description: {details}"
        )
        if suggestion and not suggestion.startswith("AI suggestion failed"):
            st.session_state.resume['experience'][i]['details'] = suggestion
            st.rerun()
    
    st.session_state.resume['experience'][i]['details'] = details
    st.markdown("---")

if st.button("➕ Add Another Job", key="add_job_btn"):
    st.session_state.resume['experience'].append({'job': '', 'company': '', 'years': '', 'details': ''})
    st.rerun()
st.header("4. Education")
for i, edu in enumerate(st.session_state.resume['education']):
    cols = st.columns([2, 2, 1])
    with cols[0]:
        st.session_state.resume['education'][i]['degree'] = st.text_input(
            f"Degree {i+1}", 
            edu['degree'],
            key=f"degree_{i}"
        )
    with cols[1]:
        st.session_state.resume['education'][i]['school'] = st.text_input(
            f"School {i+1}", 
            edu['school'],
            key=f"school_{i}"
        )
    with cols[2]:
        st.session_state.resume['education'][i]['years'] = st.text_input(
            f"Years {i+1}", 
            edu['years'],
            key=f"edu_years_{i}"
        )
    st.markdown("---")

if st.button("+ Add Another Education", key="add_edu_btn"):
    st.session_state.resume['education'].append({'degree': '', 'school': '', 'years': ''})
    st.rerun()


st.header("5. Skills")
skills = st.text_input(
    "List your skills (comma separated)", 
    ", ".join(st.session_state.resume['skills']),
    key="skills_input"
)
st.session_state.resume['skills'] = [s.strip() for s in skills.split(",") if s.strip()]

if st.button("Suggest Relevant Skills", key="skills_suggestion_btn"):
    context = f"Job roles: {', '.join([exp['job'] for exp in st.session_state.resume['experience'] if exp['job']])}"
    suggestion = get_ai_suggestion("Suggest 10 relevant skills for this work experience:", context)
    if suggestion and not suggestion.startswith("AI suggestion failed"):
        st.session_state.resume['skills'] = [s.strip() for s in suggestion.split(",")[:10]]
        st.rerun()


def generate_html_file(resume_data):
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{resume_data['name']} - Resume</title>
    <style>
        body {{
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }}
        .resume-container {{
            background-color: white;
            padding: 30px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        h2 {{
            color: #2c3e50;
            border-bottom: 1px solid #3498db;
            padding-bottom: 5px;
            margin-top: 25px;
        }}
        .contact-info {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
            font-size: 16px;
        }}
        .job {{
            margin-bottom: 20px;
        }}
        .job-header {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
        }}
        .job-title {{
            font-weight: bold;
            font-size: 18px;
        }}
        .job-years {{
            color: #7f8c8d;
        }}
        .company {{
            font-style: italic;
            color: #3498db;
            margin-bottom: 10px;
        }}
        .job-description {{
            margin-left: 15px;
        }}
        .skills-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 10px;
        }}
        .skill {{
            background-color: #e8f4fc;
            padding: 5px 15px;
            border-radius: 15px;
            font-size: 14px;
        }}
        .education-item {{
            margin-bottom: 15px;
        }}
        .education-header {{
            display: flex;
            justify-content: space-between;
        }}
        .summary {{
            font-size: 16px;
            line-height: 1.5;
        }}
    </style>
</head>
<body>
    <div class="resume-container">
        <h1>{resume_data['name']}</h1>
        
        <div class="contact-info">
            <div>📧 {resume_data['email']}</div>
            <div>📱 {resume_data['phone']}</div>
        </div>
        
        <h2>Professional Summary</h2>
        <div class="summary">{resume_data['summary']}</div>
        
        <h2>Work Experience</h2>
"""
    
    for exp in resume_data['experience']:
        if exp['job'] or exp['company'] or exp['details']:
            html_content += f"""
        <div class="job">
            <div class="job-header">
                <div class="job-title">{exp['job']}</div>
                <div class="job-years">{exp['years']}</div>
            </div>
            <div class="company">{exp['company']}</div>
            <div class="job-description">{exp['details']}</div>
        </div>
            """
    
    html_content += """
        <h2>Education</h2>
"""
    
    for edu in resume_data['education']:
        if edu['degree'] or edu['school']:
            html_content += f"""
        <div class="education-item">
            <div class="education-header">
                <div class="degree">{edu['degree']}</div>
                <div class="years">{edu['years']}</div>
            </div>
            <div class="school">{edu['school']}</div>
        </div>
            """
    
    if resume_data['skills']:
        html_content += """
        <h2>Skills</h2>
        <div class="skills-container">
"""
        for skill in resume_data['skills']:
            html_content += f"""
            <div class="skill">{skill}</div>
"""
        html_content += """
        </div>
"""
    
    html_content += """
    </div>
</body>
</html>
"""
    return html_content

st.header("Download Resume")

if st.button("Generate HTML Resume"):
    html_content = generate_html_file(st.session_state.resume)
    
    # Create a download button for the HTML file
    st.download_button(
        label="⬇️ Download HTML Resume",
        data=html_content,
        file_name="resume.html",
        mime="text/html",
        key="download_html_btn"
    )
    
    st.success("Your HTML resume is ready. Click the download button above to save it.")
    st.info("After downloading, open the file in any web browser to view your resume.and you will convert it into pdf and its under developement")
