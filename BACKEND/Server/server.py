from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class MatchRequest(BaseModel):
    resume_text: str
    jd: str

class MatchResponse(BaseModel):
    match_score: str

class HealthResponse(BaseModel):
    status: str

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

def generate_with_openai(prompt: str) -> str:
    try:
        response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content #type:ignore
    except Exception as e:
        return f"Error: {str(e)}"

@app.get("/", response_model=HealthResponse)
async def root():
    return HealthResponse(status="Hello, I am live!")

@app.post("/match", response_model=MatchResponse)
async def match_score(req: MatchRequest):
    print("Request received. Sending to OpenAI...")
    final_prompt = PROMPT_TEMPLATE.format(resume=req.resume_text, description=req.jd)
    score = generate_with_openai(final_prompt)
    print("Match Score:", score)
    return MatchResponse(match_score=score)
