from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from openai import OpenAI
from dotenv import load_dotenv
import os
import fitz  
from together import Together

load_dotenv()
# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
client = Together()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prompt Template
PROMPT_TEMPLATE = '''
You are an intelligent assistant that compares a candidate’s resume with a job description to assess skill match.

Resume: {resume}

Job Description: {description}

Instructions:
1. Extract all relevant skills (explicit and inferred) from the resume.
2. Extract all required skills from the job description.
3. Compare the two sets of skills thoroughly.
4. Based on the overlap, coverage, and relevance, return only the final match score.

Output:
Return only a single integer between 0 and 100 representing the match score. Do not include any explanation, label, or punctuation — only the number.
'''

# Extract text from PDF
def extract_text_from_pdf(file: UploadFile) -> str:
    text = ""
    pdf = fitz.open(stream=file.file.read(), filetype="pdf")
    for page in pdf:
        text += page.get_text() #type:ignore
    return text.strip()

# LLM Call
def generate_with_openai(prompt: str) -> str:
    try:
        # response = client.chat.completions.create(
        #     model="gpt-3.5-turbo",
        #     messages=[{"role": "user", "content": prompt}]
        # )
        # return response.choices[0].message.content.strip()  # type: ignore
        response = client.chat.completions.create(
            model="Qwen/Qwen2.5-Coder-32B-Instruct",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            stream=False  
        )
        if hasattr(response, 'choices'):
            return response.choices[0].message.content #type:ignore
        return "Unable to generate a response."
    except Exception as e:
        return f"Error: {str(e)}"

@app.get("/")
async def root():
    return {"message":"Hello, I am live"}

@app.post("/match")
async def match_score(
    resume_file: UploadFile = File(None),
    jd_file: UploadFile = File(None),
    resume_text: str = Form(""),
    jd_text: str = Form("")
):
    try:
        resume_data = extract_text_from_pdf(resume_file) if resume_file else resume_text
        jd_data = extract_text_from_pdf(jd_file) if jd_file else jd_text

        if not resume_data or not jd_data:
            return JSONResponse(
                status_code=400,
                content={"error": "Both resume and job description are required (either as text or PDF)."}
            )

        print("📥 Request received. Sending to OpenAI...")
        final_prompt = PROMPT_TEMPLATE.format(resume=resume_data, description=jd_data)
        score = generate_with_openai(final_prompt)
        print("✅ Match Score:", score)

        return {"match_score": score}

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Internal Server Error: {str(e)}"}
        )
