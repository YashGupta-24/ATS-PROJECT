from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low

class Request(Model):
    resume_text:str
    jd:str

class Response(Model):
    match_score:str

class ASI1miniRequest(Model):
    query: str

class ASI1miniResponse(Model):
    response: str

agent=Agent(name="Resume JD Match", seed="ResumeJd", port=8080, endpoint="http://localhost:8080/submit")

llm_agent=''

fund_agent_if_low(agent.wallet.address()) #type:ignore

prompt='''
You are an intelligent assistant that compares a candidate’s resume with a job description to assess skill match.
Resume: {resume}
Job Description: {description}

Task:
1. Extract all skills (both explicit and inferred) from the resume — including tools, technologies, programming languages, frameworks, soft skills, etc.
2. Extract required skills from the job description.
3. Compare both and calculate a match score (0–100) based on the relevance and coverage of resume skills with respect to the job description.

Output:
1. Match Score (0–100)
2. Matched Skills
3. Brief justification of the score
'''

@agent.on_rest_post("/match", Request, Response)
async def match(ctx:Context, msg:Request)->Response:
    ctx.logger.info(f"Resume text: {msg.resume_text}")
    ctx.logger.info(f"jd: {msg.jd}")
    final_query = prompt.format(resume=msg.resume_text, description= msg.jd)
    res, status = await ctx.send_and_receive(llm_agent, ASI1miniRequest(query=final_query), response_type=ASI1miniResponse)
    if res:
        output=res.response # type:ignore
        return Response(match_score=output)
    else:
        return Response(match_score="No response recieved from the agent")

if __name__=="__main__":
    agent.run()