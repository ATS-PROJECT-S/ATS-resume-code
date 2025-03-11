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

# Load environment variables
# load_dotenv()

# Configure Google Gemini API
genai.configure(api_key="AIzaSyBlvSnJrKGwFoBLN2ft0jvcrebXJZHDCWU")

# Function to extract text from PDF

def extract_text_from_pdf(file_path):
    try:
        with pdfplumber.open(file_path) as pdf:
            text_content = "".join(page.extract_text() or "" for page in pdf.pages)
        return text_content.strip()
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
    # resume_words = set(resume_text.split())
    # print("resume_words",resume_words)
    # job_words = set(job_keywords)
    # print("job_words",job_words)
    # common_words = resume_words.intersection(job_words)
    # print("common_words",common_words)
    count = 0
    for key in job_keywords:
        if key in resume_text:
            count += 1

    return round((count / len(job_keywords)) * 100, 2) if job_keywords else 0

def home(request):
    return render(request, "upload.html")

# Django View to handle file upload
def upload_resume(request):
    print("request",request.POST)
    print("resume",request.FILES['resume'])
    if request.method == "POST" and request.FILES.get("resume"):
        domain = request.POST.get("domain", "")
        uploaded_file = request.FILES["resume"]
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
        # print("resume_text",resume_text)
        resume_text_cleaned = preprocess_text(resume_text)
        # print("resume_text_cleaned",resume_text_cleaned)
        print("domain",domain)
        domain_skills = extract_skills_based_on_domain(domain)
        print("domain_skills",domain_skills)
        ats_status = evaluate_ats_friendly(resume_text_cleaned, domain_skills)
        print("ats_status",ats_status)
        match_percentage = calculate_match_percentage(domain_skills, resume_text_cleaned)
        print("match_percentage",match_percentage)

        result = {
            "File Name": uploaded_file.name,
            "Match Percentage": f"{match_percentage}%",
            "Domain Skills": ", ".join(domain_skills),
            "ATS Evaluation": ats_status,
        }
        return JsonResponse(result)
    return render(request, "upload.html")
