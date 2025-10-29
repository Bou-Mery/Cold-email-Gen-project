import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv
from typing import Dict, List
import json

load_dotenv()

class Chain:
    def __init__(self, groq_api_key: str = None):
        # Method 1: Direct parameter
        if groq_api_key and groq_api_key.strip():
            self.groq_api_key = groq_api_key.strip()
            print("✅ API Key from direct parameter")
        
        # Method 2: Streamlit Secrets (DEPLOYMENT)
        elif hasattr(st, 'secrets') and "GROQ_API_KEY" in st.secrets and st.secrets["GROQ_API_KEY"].strip():
            self.groq_api_key = st.secrets["GROQ_API_KEY"].strip()
            print("✅ API Key from Streamlit Secrets (deployment)")
        
        # Method 3: Environment variable (LOCAL)
        elif os.getenv("GROQ_API_KEY") and os.getenv("GROQ_API_KEY").strip():
            self.groq_api_key = os.getenv("GROQ_API_KEY").strip()
            print("✅ API Key from .env (local)")
        
        # No method found
        else:
            raise ValueError(
                "❌ Groq API Key not found.\n\n"
                "LOCALLY: Create a .env file with GROQ_API_KEY=your_key\n"
                "IN DEPLOYMENT: Add GROQ_API_KEY to Streamlit Secrets"
            )
        
        # Validation
        if not self.groq_api_key:
            raise ValueError("Groq API Key is empty")
        
        print(f"🔑 Key loaded ({len(self.groq_api_key)} characters)")
        
        self.llm = ChatGroq(temperature=0, groq_api_key=self.groq_api_key, model="llama-3.1-8b-instant")
        self.creative_llm = ChatGroq(temperature=0.7, groq_api_key=self.groq_api_key, model="llama-3.1-8b-instant")

    def extract_jobs(self, cleaned_text):
        """Extract job posting information from cleaned text."""
        prompt_extract = ChatPromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            
            ### Instructions:
            The above text comes from a company's careers page.
            Your task is to extract ONE job posting and return it as a single flat JSON object with keys:
            role, experience, skills, description
            
            Return only valid JSON, no comments.
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

    def detect_style(self, job_description):
        """Detect appropriate communication tone from job posting."""
        prompt_tone = ChatPromptTemplate.from_template(
            """
            ### JOB POSTING TEXT:
            {job_text}
            
            ### INSTRUCTION:
            Analyze the job posting and determine the communication tone.
            Respond with ONE WORD from: formal, technical, creative, corporate, marketing
            
            ### TONE (ONE WORD):
            """
        )
        
        chain_tone = prompt_tone | self.llm
        res = chain_tone.invoke({"job_text": job_description})
        
        detected_tone = res.content.strip().lower()
        
        valid_tones = ['formal', 'technical', 'creative', 'corporate', 'marketing']
        if detected_tone not in valid_tones:
            print(f"⚠️ Invalid tone '{detected_tone}', defaulting to 'corporate'")
            detected_tone = 'corporate'
        
        return detected_tone

    def research_company(self, company_name: str, job_description: str = "") -> Dict:
        """Research company for better email personalization."""
        prompt_research = ChatPromptTemplate.from_template(
            """
            ### COMPANY NAME:
            {company_name}
            
            ### JOB POSTING CONTEXT:
            {job_context}
            
            ### INSTRUCTION:
            Based on the company and job posting, infer:
            1. Key Values (3-4 items)
            2. Recent Focus (1-2 sentences)
            3. Culture Traits (3-4 items)
            4. Tech Stack (list)
            
            Return ONLY valid JSON with keys:
            key_values, recent_focus, culture_traits, tech_stack
            
            ### JSON OUTPUT:
            """
        )
        
        chain_research = prompt_research | self.llm
        res = chain_research.invoke({
            "company_name": company_name,
            "job_context": job_description[:1000]
        })
        
        try:
            json_parser = JsonOutputParser()
            company_intel = json_parser.parse(res.content)
        except OutputParserException as e:
            print(f"Error parsing company research: {e}")
            company_intel = {
                "key_values": ["Innovation", "Quality", "Customer Focus"],
                "recent_focus": "Expanding technical capabilities",
                "culture_traits": ["Collaborative", "Fast-paced", "Professional"],
                "tech_stack": []
            }
        
        return company_intel

    def generate_email_variations(self, job_data: Dict, links: List, tone: str, company_intel: Dict) -> Dict[str, str]:
        """Generate 3 different email strategies."""
        
        prompt_value = ChatPromptTemplate.from_template(
            """
            ### JOB DETAILS:
            {job_data}
            
            ### COMPANY INSIGHTS:
            {company_intel}
            
            ### PORTFOLIO:
            {links}
            
            ### INSTRUCTION:
            Write a VALUE PROPOSITION email in {tone} tone.
            Focus on: quantifiable benefits, ROI, direct value.
            200-250 words. No preamble, no subject line.
            
            ### EMAIL:
            """
        )
        
        prompt_problem = ChatPromptTemplate.from_template(
            """
            ### JOB DETAILS:
            {job_data}
            
            ### COMPANY INSIGHTS:
            {company_intel}
            
            ### PORTFOLIO:
            {links}
            
            ### INSTRUCTION:
            Write a PROBLEM-SOLUTION email in {tone} tone.
            Focus on: identifying pain points, empathy, solution.
            200-250 words. No preamble, no subject line.
            
            ### EMAIL:
            """
        )
        
        prompt_story = ChatPromptTemplate.from_template(
            """
            ### JOB DETAILS:
            {job_data}
            
            ### COMPANY INSIGHTS:
            {company_intel}
            
            ### PORTFOLIO:
            {links}
            
            ### INSTRUCTION:
            Write a STORYTELLING email in {tone} tone.
            Focus on: case study, emotional connection, transformation.
            200-250 words. No preamble, no subject line.
            
            ### EMAIL:
            """
        )
        
        context = {
            "job_data": str(job_data),
            "company_intel": str(company_intel),
            "links": str(links),
            "tone": tone
        }
        
        chain_value = prompt_value | self.creative_llm
        chain_problem = prompt_problem | self.creative_llm
        chain_story = prompt_story | self.creative_llm
        
        return {
            "value_proposition": chain_value.invoke(context).content,
            "problem_solution": chain_problem.invoke(context).content,
            "storytelling": chain_story.invoke(context).content
        }

    def analyze_email_effectiveness(self, email: str, job_data: Dict) -> Dict:
        """Predict email effectiveness and provide suggestions."""
        prompt_analyze = ChatPromptTemplate.from_template(
            """
            ### EMAIL TO ANALYZE:
            {email}
            
            ### JOB CONTEXT:
            {job_data}
            
            ### INSTRUCTION:
            Analyze effectiveness based on:
            1. Relevance (0-25)
            2. Clarity (0-25)
            3. Personalization (0-25)
            4. Call-to-Action (0-25)
            
            Return JSON:
            {{
                "success_score": <total 0-100>,
                "strengths": [<2-3 points>],
                "improvements": [<2-3 suggestions>],
                "key_metrics": {{"relevance": <0-25>, "clarity": <0-25>, "personalization": <0-25>, "call_to_action": <0-25>}}
            }}
            
            ### JSON OUTPUT:
            """
        )
        
        chain_analyze = prompt_analyze | self.llm
        res = chain_analyze.invoke({
            "email": email,
            "job_data": str(job_data)
        })
        
        try:
            json_parser = JsonOutputParser()
            analysis = json_parser.parse(res.content)
        except OutputParserException as e:
            print(f"Error parsing analysis: {e}")
            analysis = {
                "success_score": 75,
                "strengths": ["Clear communication", "Professional tone"],
                "improvements": ["Add examples", "Strengthen CTA"],
                "key_metrics": {"relevance": 20, "clarity": 20, "personalization": 18, "call_to_action": 17}
            }
        
        return analysis

    def generate_follow_up_sequence(self, initial_email: str, job_data: Dict, company_name: str) -> List[Dict]:
        """Create 3-email follow-up sequence."""
        prompt_followup = ChatPromptTemplate.from_template(
            """
            ### ORIGINAL EMAIL:
            {initial_email}
            
            ### JOB DETAILS:
            {job_data}
            
            ### COMPANY:
            {company_name}
            
            ### INSTRUCTION:
            Create follow-up #{followup_number} (day {days}).
            100-150 words, professional, non-pushy.
            
            Return JSON: {{"subject": "...", "email": "..."}}
            
            ### JSON OUTPUT:
            """
        )
        
        follow_ups = []
        schedule = [(3, 1), (7, 2), (14, 3)]
        
        for days, number in schedule:
            chain_followup = prompt_followup | self.creative_llm
            res = chain_followup.invoke({
                "initial_email": initial_email,
                "job_data": str(job_data),
                "company_name": company_name,
                "followup_number": number,
                "days": days
            })
            
            try:
                json_parser = JsonOutputParser()
                followup_data = json_parser.parse(res.content)
                followup_data["day"] = days
                follow_ups.append(followup_data)
            except OutputParserException as e:
                print(f"Error parsing follow-up {number}: {e}")
                follow_ups.append({
                    "day": days,
                    "subject": f"Following up on {job_data.get('role', 'opportunity')}",
                    "email": f"Hi,\n\nFollowing up on my previous email.\n\nBest regards"
                })
        
        return follow_ups

    def generate_cold_email(self, job_data, links, tone=None, company_intel=None):
        """Generate personalized cold email with adaptive tone."""
        if tone is None:
            tone = self.detect_style(job_data.get('description', ''))
        
        tone_instructions = {
            'formal': "Use highly professional language, no contractions.",
            'technical': "Use technical terminology and demonstrate expertise.",
            'creative': "Use engaging, dynamic language with personality.",
            'corporate': "Balance professionalism with approachability.",
            'marketing': "Use persuasive, benefit-driven language."
        }
        
        company_context = ""
        if company_intel:
            company_context = f"""
            ### COMPANY INTELLIGENCE:
            Values: {', '.join(company_intel.get('key_values', []))}
            Focus: {company_intel.get('recent_focus', '')}
            Culture: {', '.join(company_intel.get('culture_traits', []))}
            """
        
        prompt_email = ChatPromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_data}
            
            {company_context}
            
            ### TONE: {tone}
            ### GUIDELINES: {tone_instruction}
            
            ### INSTRUCTION:
            Write a cold email as a Business Development Engineer at a software company.
            Highlight relevant expertise and portfolio links: {links}
            
            {tone} style, 200-300 words, no preamble or subject.
            
            ### EMAIL:
            """
        )
        
        chain_email = prompt_email | self.llm
        res = chain_email.invoke({
            "job_data": str(job_data),
            "links": str(links),
            "tone": tone,
            "tone_instruction": tone_instructions.get(tone, tone_instructions['corporate']),
            "company_context": company_context
        })
        
        return res.content


if __name__ == "__main__":
    print("Testing Chain initialization...")
    try:
        chain = Chain()
        print("✅ Chain initialized successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")
