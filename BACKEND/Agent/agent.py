from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
from google import genai
from dotenv import load_dotenv
import os

load_dotenv()
client=genai.Client()

class Request(Model):
    resume_text:str
    jd:str

class Response(Model):
    match_score:str

class TestResponse(Model):
    status:str

agent=Agent(name="Resume JD Match", seed="ResumeJd", port=8080, endpoint="https://localhost:8080/submit")

fund_agent_if_low(agent.wallet.address()) #type:ignore

prompt = '''
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


def generate_with_together(final_prompt:str) -> str:
    try:
        print("Sending data to Gemini")
        response=client.models.generate_content(
            model="gemini-2.5-flash",
            contents=final_prompt
        )
        print("Got a response from gemini")
        return response.text[0] #type:ignore
    except Exception as e:
        return f"Error occurred: {str(e)}"

@agent.on_rest_get("/", TestResponse)
async def check(ctx:Context)->TestResponse:
    return TestResponse(status="Hello, I am live!")

@agent.on_rest_post("/match", Request, Response)
async def match(ctx:Context, msg:Request)->Response:
    ctx.logger.info("Data Received. Sending it to Qwen for evaluating.")
    final_query = prompt.format(resume=msg.resume_text, description= msg.jd)
    res = generate_with_together(final_query)
    ctx.logger.info(f"Data Received from Qwen: {res}")
    return Response(match_score=res)

if __name__=="__main__":
    agent.run()