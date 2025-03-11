from django.shortcuts import render

# Create your views here.
import os
import re
import json
import pdfplumber
import docx2txt as Document
# from dotenv import load_dotenv
import google.generativeai as genai
from django.shortcuts import render
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from atsapp.models import *

# Load environment variables
# load_dotenv()

# Configure Google Gemini API
genai.configure(api_key="AIzaSyBlvSnJrKGwFoBLN2ft0jvcrebXJZHDCWU")

# Function to extract text from PDF

def extract_text_from_pdf(file_path):
    try:
        with pdfplumber.open(file_path) as pdf:
            text_content = "".join(page.extract_text() or "" for page in pdf.pages)
        return text_content.strip().lower()
    except Exception as e:
        return f"Error reading PDF: {e}"

# Function to extract text from DOCX

def extract_text_from_docx(file_path):
    try:
        return Document.process(file_path).strip()
    except Exception as e:
        return f"Error reading DOCX: {e}"

# Function to preprocess text
def preprocess_text(text):
    text = re.sub(r"\s+", " ", text)  # Replace multiple spaces
    text = re.sub(r"[^\w\s]", "", text)  # Remove special characters
    return text.lower() 

# Function to extract skills using Google Gemini
def extract_skills_based_on_domain(domain):
    try:
        # prompt = f"""
        # List the key skills, technologies, and programming languages typically required in the field of {domain} in single words.
        # """
        # response = genai.GenerativeModel(model_name="gemini-pro").generate_content(prompt)
        data_dict = {
            "Software Development":["python", "sql", "Git", "html", "css"],
            "Data Science":["python", "excel", "powerbi", "tableau", "pandas"],
            "Marketing":["Communication","Project management","Critical thinking","Innovation"],
            "Cyber security":["Python","Communication skills","operating systems","ethical hacking"]
        }
        

        skills = data_dict[domain]
        return skills
    except Exception as e:
        return []

# Function to evaluate ATS friendliness
def evaluate_ats_friendly(resume_text, extracted_skills):
    return "Resume is ATS-friendly" if len(extracted_skills) >= 1 else "Consider adding more relevant skills."

# Function to calculate match percentage
def calculate_match_percentage(job_keywords, resume_text):
    print("job_keywords",job_keywords)
    print("resume_text",resume_text)
    count = 0
    for key in job_keywords:
        if key in resume_text:
            count += 1
    print("count",count)
    return round((count / len(job_keywords)) * 100, 2) if job_keywords else 0

def home(request):
    return render(request, "upload.html")

# Django View to handle file upload
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt  # Allow POST requests without CSRF token for testing (remove in production)
def upload_resume(request):
    print("request",request.POST)
    if request.method == "POST" and request.FILES.getlist("resumes"):
        domain = request.POST.get("domain", "")
        selected_skills = json.loads(request.POST.get("selectedSkills", "[]"))
        additional_skills = json.loads(request.POST.get("additionalSkills", "[]"))
        uploaded_files = request.FILES.getlist("resumes")

        all_results = []
        print("uploaded_files",uploaded_files)
        for uploaded_file in uploaded_files:
            fs = FileSystemStorage()
            file_path = fs.save(uploaded_file.name, uploaded_file)
            full_file_path = fs.path(file_path)

            # Extract resume text
            if uploaded_file.name.endswith(".pdf"):
                resume_text = extract_text_from_pdf(full_file_path)
            elif uploaded_file.name.endswith(".docx"):
                resume_text = extract_text_from_docx(full_file_path)
            else:
                return JsonResponse({"error": "Unsupported file format"})

            # Clean and process resume text
            resume_text_cleaned = preprocess_text(resume_text)
            # domain_skills = extract_skills_based_on_domain(domain)
            print('resume_text_cleaned',resume_text_cleaned)
            # Combine domain and additional skills
            all_skills = set(selected_skills + additional_skills)
            all_skills = [skill.lower() for skill in all_skills]
            print('all_skills',all_skills)
            # ATS analysis
            # ats_status = evaluate_ats_friendly(resume_text_cleaned, all_skills)
            match_percentage = calculate_match_percentage(all_skills, resume_text_cleaned)

            opj=CategoryWiseResumesScore(
                job_description=domain,
                file_name=uploaded_file.name,
                score=match_percentage,
            ).save()

            result = {
                "File_Name": uploaded_file.name,
                "Match_Percentage": f"{match_percentage}%",
                "Domain_Skills": list(all_skills),
                "ATS_Evaluation": 'ats_status',
            }

            all_results.append(result)
        context = {"results": all_results}
        print("in")
        # return render(request, "response.html", context)
        return render(request=request, template_name="response.html", context=context)
    print("out")
    return render(request, "upload.html")

