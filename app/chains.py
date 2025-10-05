import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")

class Chain:
    def __init__(self):
        self.llm = ChatGroq(temperature=0 , groq_api_key=groq_api_key , model="llama-3.1-8b-instant")

    def extract_jobs(self , cleaned_text):
        prompt_extract = ChatPromptTemplate.from_template(
            """
            ### Instructions:
            The above text comes from a company's careers page.
            Your task is to extract ONE job posting and return it as **a single flat JSON object** with the following keys:

            - role
            - experience
            - skills
            - description

            Do NOT wrap the result in any extra key or list.
            Return only valid JSON NO COMMENTS NO PREAMBLE.
            """
        )

        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke({"page_data": cleaned_text})

        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException as e:
            print("Error parsing JSON:", e)
            res = {}
        return res
    

    def generate_cold_email(self , job_data , links):
        prompt_email = ChatPromptTemplate.from_template(
            """
          ### JOB DESCRIPTION:
            {job_data}

            ### INSTRUCTION:
            You are a Business Development Engineer at a software and data solutions company specializing in
            Data Engineering, Artificial Intelligence, Cloud Integration, and Web Application Development.
            Your company helps organizations modernize their data architecture, automate workflows, and build scalable
            digital platforms tailored to their business needs.

            Your task is to write a professional cold email to the client regarding the job mentioned above,
            demonstrating your company's ability to address their requirements effectively.
            Highlight relevant experience, expertise, and how your team can add value to their project.

            Also include the most relevant portfolio links from the following list to showcase your previous work:
            {links}

            Keep the tone polite, confident, and concise.
            Do NOT include any preamble or explanation.

            ### EMAIL (NO PREAMBLE):
            """
        )

        chain_email = prompt_email | self.llm
        res = chain_email.invoke({
            "job_data": str(job_data),
            "links": str(links)
        })
        return res.content

       


if __name__ == "__main__":
    print()