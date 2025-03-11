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
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to extract text from PDF

def extract_text_from_pdf(file_path):
    # try:
    with pdfplumber.open(file_path) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
    return text.strip() if text else "No text found in the PDF."
    # except Exception as e:
    #     return f"Error reading PDF: {e}"

# Function to extract text from DOCX

# def extract_text_from_docx(file_path):
def extract_text_from_docx(file_path):
    print("yes")
    
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
        prompt = f"""
        List the key skills, technologies, and programming languages typically required in the field of {domain}.
        """
        response = genai.GenerativeModel(model_name="gemini-pro").generate_content(prompt)
        skills = response.text.strip().split(",") if response.text else []
        return [skill.strip() for skill in skills]
    except Exception as e:
        return []

# Function to evaluate ATS friendliness
def evaluate_ats_friendly(resume_text, extracted_skills):
    return "Resume is ATS-friendly" if len(extracted_skills) >= 5 else "Consider adding more relevant skills."

# Function to calculate match percentage
def calculate_match_percentage(job_keywords, resume_text):
    resume_words = set(resume_text.split())
    job_words = set(job_keywords)
    common_words = resume_words.intersection(job_words)
    return round((len(common_words) / len(job_words)) * 100, 2) if job_words else 0

# Django View to handle file upload
def upload_resume(request):
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

        resume_text_cleaned = preprocess_text(resume_text)
        domain_skills = extract_skills_based_on_domain(domain)
        ats_status = evaluate_ats_friendly(resume_text_cleaned, domain_skills)
        match_percentage = calculate_match_percentage(domain_skills, resume_text_cleaned)

        result = {
            "File Name": uploaded_file.name,
            "Match Percentage": f"{match_percentage}%",
            "Domain Skills": ", ".join(domain_skills),
            "ATS Evaluation": ats_status,
        }
        return JsonResponse(result)
    return render(request, "upload.html")

file_path = r"C:/Users/Sheona/Downloads/FAANGPath_Simple_Template__1___Copy___Copy_.pdf"
text = extract_text_from_pdf(file_path)
print("text",text)