from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
from together import Together
from dotenv import load_dotenv
import os

load_dotenv()

os.environ["TOGETHER_API_KEY"] = os.getenv("TOGETHER_API_KEY") #type:ignore

client = Together()

class Request(Model):
    resume_text:str
    jd:str

class Response(Model):
    match_score:str

class ASI1miniRequest(Model):
    query: str

class ASI1miniResponse(Model):
    response: str

agent=Agent(name="Resume JD Match", seed="ResumeJd", port=8080, endpoint="https://localhost:8080/submit")

# llm_agent='agent1qvn0t4u5jeyewp9l544mykv639szuhq8dhmatrgfuwqphx20n8jn78m9paa'

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
        # final_prompt=GENERATE_PROMPT_STRING.format(query=query, language=language)
        response = client.chat.completions.create(
            model="Qwen/Qwen2.5-Coder-32B-Instruct",
            messages=[
                {
                    "role": "user",
                    "content": final_prompt
                }
            ],
            stream=False  
        )
        if hasattr(response, 'choices'):
            return response.choices[0].message.content #type:ignore
        return "Unable to generate a response."
    except Exception as e:
        return f"Error occurred: {str(e)}"

@agent.on_rest_post("/match", Request, Response)
async def match(ctx:Context, msg:Request)->Response:
    ctx.logger.info("Data Received. Sending it to Qwen for evaluating.")
    final_query = prompt.format(resume=msg.resume_text, description= msg.jd)
    res = generate_with_together(final_query)
    ctx.logger.info(f"Data Received from Qwen: {res}")
    return Response(match_score=res)

if __name__=="__main__":
    agent.run()