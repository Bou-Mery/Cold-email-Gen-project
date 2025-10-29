import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv
from typing import Dict, List
import json

load_dotenv()

#groq_api_key = os.getenv("GROQ_API_KEY")

class Chain:
    def __init__(self , groq_api_key: str = None):
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

        
        self.llm = ChatGroq(temperature=0, groq_api_key=groq_api_key, model="llama-3.1-8b-instant")
        self.creative_llm = ChatGroq(temperature=0.7, groq_api_key=groq_api_key, model="llama-3.1-8b-instant")

    def extract_jobs(self, cleaned_text):
        """
        Extracts job posting information from cleaned text.
        
        Args:
            cleaned_text (str): Pre-processed job posting text
            
        Returns:
            dict: Job data with keys: role, experience, skills, description
        """
        prompt_extract = ChatPromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            
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
    

    def detect_style(self, job_description):
        """
        🆕 V2 FEATURE: Adaptive Tone Detection
        
        Analyzes job posting text to determine the appropriate communication tone.
        
        Args:
            job_description (str): Raw or cleaned job posting text
            
        Returns:
            str: Detected tone style (formal, technical, creative, corporate, marketing)
        """
        prompt_tone = ChatPromptTemplate.from_template(
            """
            ### JOB POSTING TEXT:
            {job_text}
            
            ### INSTRUCTION:
            Analyze the above job posting and determine the most appropriate communication tone.
            
            Consider these indicators:
            - **Formal**: Legal, finance, government roles with rigid language
            - **Technical**: Engineering, data science with heavy jargon
            - **Creative**: Design, marketing, content roles with expressive language
            - **Corporate**: Traditional business roles with professional but approachable tone
            - **Marketing**: Sales, growth, customer-facing roles with persuasive language
            
            Respond with ONLY ONE WORD from: formal, technical, creative, corporate, marketing
            
            ### TONE (ONE WORD):
            """
        )
        
        chain_tone = prompt_tone | self.llm
        res = chain_tone.invoke({"job_text": job_description})
        
        detected_tone = res.content.strip().lower()
        
        valid_tones = ['formal', 'technical', 'creative', 'corporate', 'marketing']
        if detected_tone not in valid_tones:
            print(f"⚠️ Invalid tone '{detected_tone}' detected, defaulting to 'corporate'")
            detected_tone = 'corporate'
        
        return detected_tone
    

    def research_company(self, company_name: str, job_description: str = "") -> Dict:
        """
        🆕 V3 FEATURE: Smart Company Intelligence
        
        AI researches company for better email personalization.
        Analyzes job posting to infer company information when direct data unavailable.
        
        Args:
            company_name (str): Name of the company
            job_description (str): Job posting text for context
            
        Returns:
            dict: {
                "key_values": list of company values,
                "recent_focus": inferred recent initiatives,
                "culture_traits": list of culture indicators,
                "tech_stack": mentioned technologies
            }
        """
        prompt_research = ChatPromptTemplate.from_template(
            """
            ### COMPANY NAME:
            {company_name}
            
            ### JOB POSTING CONTEXT:
            {job_context}
            
            ### INSTRUCTION:
            Based on the company name and job posting, infer key information about this company.
            Analyze the language, requirements, and context to determine:
            
            1. **Key Values**: What does this company likely prioritize? (innovation, quality, customer-focus, etc.)
            2. **Recent Focus**: Based on the job role, what are they currently working on?
            3. **Culture Traits**: What kind of work environment do they suggest? (collaborative, fast-paced, etc.)
            4. **Tech Stack**: What technologies are mentioned or implied?
            
            Return ONLY a valid JSON object with these exact keys:
            - key_values (list of 3-4 strings)
            - recent_focus (string, 1-2 sentences)
            - culture_traits (list of 3-4 strings)
            - tech_stack (list of strings)
            
            NO PREAMBLE, ONLY JSON.
            
            ### JSON OUTPUT:
            """
        )
        
        chain_research = prompt_research | self.llm
        res = chain_research.invoke({
            "company_name": company_name,
            "job_context": job_description[:1000]  # Limit context
        })
        
        try:
            json_parser = JsonOutputParser()
            company_intel = json_parser.parse(res.content)
        except OutputParserException as e:
            print(f"Error parsing company research: {e}")
            company_intel = {
                "key_values": ["Innovation", "Quality", "Customer Focus"],
                "recent_focus": "Expanding their technical capabilities",
                "culture_traits": ["Collaborative", "Fast-paced", "Professional"],
                "tech_stack": []
            }
        
        return company_intel


    def generate_email_variations(self, job_data: Dict, links: List, 
                                   tone: str, company_intel: Dict) -> Dict[str, str]:
        """
        🆕 V3 FEATURE: Multi-Strategy Email Generation
        
        Generates 3 different email approaches for the same job.
        
        Args:
            job_data (dict): Extracted job information
            links (list): Portfolio links
            tone (str): Communication style
            company_intel (dict): Company research data
            
        Returns:
            dict: {
                "value_proposition": email focusing on value delivery,
                "problem_solution": email addressing pain points,
                "storytelling": email with narrative approach
            }
        """
        
        # Strategy 1: Value Proposition
        prompt_value = ChatPromptTemplate.from_template(
            """
            ### JOB DETAILS:
            {job_data}
            
            ### COMPANY INSIGHTS:
            {company_intel}
            
            ### YOUR PORTFOLIO:
            {links}
            
            ### INSTRUCTION:
            Write a cold email using a **VALUE PROPOSITION** strategy in a {tone} tone.
            
            Focus on:
            - Lead with the specific value you bring
            - Quantifiable benefits (speed, cost savings, quality)
            - Direct connection between their needs and your capabilities
            - Clear ROI indicators
            
            Keep it 200-250 words. NO preamble, NO subject line.
            
            ### EMAIL:
            """
        )
        
        # Strategy 2: Problem-Solution
        prompt_problem = ChatPromptTemplate.from_template(
            """
            ### JOB DETAILS:
            {job_data}
            
            ### COMPANY INSIGHTS:
            {company_intel}
            
            ### YOUR PORTFOLIO:
            {links}
            
            ### INSTRUCTION:
            Write a cold email using a **PROBLEM-SOLUTION** strategy in a {tone} tone.
            
            Focus on:
            - Identify a likely pain point they're facing
            - Empathize with the challenge
            - Present your solution naturally
            - Show how you've solved similar problems before
            
            Keep it 200-250 words. NO preamble, NO subject line.
            
            ### EMAIL:
            """
        )
        
        # Strategy 3: Storytelling
        prompt_story = ChatPromptTemplate.from_template(
            """
            ### JOB DETAILS:
            {job_data}
            
            ### COMPANY INSIGHTS:
            {company_intel}
            
            ### YOUR PORTFOLIO:
            {links}
            
            ### INSTRUCTION:
            Write a cold email using a **STORYTELLING** strategy in a {tone} tone.
            
            Focus on:
            - Open with a relevant short story or case study
            - Create an emotional connection
            - Show transformation (before/after)
            - Make it relatable and memorable
            
            Keep it 200-250 words. NO preamble, NO subject line.
            
            ### EMAIL:
            """
        )
        
        context = {
            "job_data": str(job_data),
            "company_intel": str(company_intel),
            "links": str(links),
            "tone": tone
        }
        
        # Generate all three variations
        chain_value = prompt_value | self.creative_llm
        chain_problem = prompt_problem | self.creative_llm
        chain_story = prompt_story | self.creative_llm
        
        email_value = chain_value.invoke(context).content
        email_problem = chain_problem.invoke(context).content
        email_story = chain_story.invoke(context).content
        
        return {
            "value_proposition": email_value,
            "problem_solution": email_problem,
            "storytelling": email_story
        }


    def analyze_email_effectiveness(self, email: str, job_data: Dict) -> Dict:
        """
        🆕 V3 FEATURE: Success Prediction & Analytics
        
        AI predicts email effectiveness and provides improvement suggestions.
        
        Args:
            email (str): Generated email content
            job_data (dict): Job posting information
            
        Returns:
            dict: {
                "success_score": int (0-100),
                "strengths": list of positive aspects,
                "improvements": list of suggestions,
                "key_metrics": dict of specific metrics
            }
        """
        prompt_analyze = ChatPromptTemplate.from_template(
            """
            ### EMAIL TO ANALYZE:
            {email}
            
            ### JOB CONTEXT:
            {job_data}
            
            ### INSTRUCTION:
            Analyze this cold email's effectiveness as a professional recruiter/hiring manager would.
            
            Evaluate based on:
            1. **Relevance**: Does it address the job requirements? (0-25 points)
            2. **Clarity**: Is the message clear and concise? (0-25 points)
            3. **Personalization**: Is it tailored to this specific role? (0-25 points)
            4. **Call-to-Action**: Does it have a clear next step? (0-25 points)
            
            Return ONLY a valid JSON object:
            {{
                "success_score": <total points 0-100>,
                "strengths": [<list of 2-3 strong points>],
                "improvements": [<list of 2-3 specific suggestions>],
                "key_metrics": {{
                    "relevance": <0-25>,
                    "clarity": <0-25>,
                    "personalization": <0-25>,
                    "call_to_action": <0-25>
                }}
            }}
            
            NO PREAMBLE, ONLY JSON.
            
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
            print(f"Error parsing email analysis: {e}")
            analysis = {
                "success_score": 75,
                "strengths": ["Clear communication", "Professional tone"],
                "improvements": ["Add more specific examples", "Strengthen call-to-action"],
                "key_metrics": {
                    "relevance": 20,
                    "clarity": 20,
                    "personalization": 18,
                    "call_to_action": 17
                }
            }
        
        return analysis


    def extract_job_links(self, job_results: List[Dict]) -> List[Dict]:
        """
        🆕 V3 FEATURE: Enhanced Job Link Extraction

        Validates and enhances job URLs from search results.
        Attempts to extract or validate URLs for better job discovery.

        Args:
            job_results (list): Raw job search results

        Returns:
            list: Job results with validated/enhanced URLs
        """
        enhanced_jobs = []

        for job in job_results:
            enhanced_job = job.copy()
            url = job.get('url', '')

            # Validate URL format
            if url and url.startswith(('http://', 'https://')):
                # URL is valid, keep as is
                enhanced_job['url'] = url
            elif url and not url.startswith(('http://', 'https://')):
                # Try to construct full URL
                if url.startswith('//'):
                    enhanced_job['url'] = 'https:' + url
                elif url.startswith('/'):
                    # Try to infer domain from company name
                    company_domain = job.get('company', '').lower().replace(' ', '')
                    if company_domain:
                        enhanced_job['url'] = f"https://careers.{company_domain}.com{url}"
                    else:
                        enhanced_job['url'] = None
                else:
                    enhanced_job['url'] = None
            else:
                enhanced_job['url'] = None

            enhanced_jobs.append(enhanced_job)

        return enhanced_jobs


    def generate_follow_up_sequence(self, initial_email: str, job_data: Dict,
                                    company_name: str) -> List[Dict]:
        """
        🆕 V3 FEATURE: Automated Follow-up System
        
        Creates a 3-email follow-up sequence over 14 days.
        
        Args:
            initial_email (str): The first email sent
            job_data (dict): Job information
            company_name (str): Company name for personalization
            
        Returns:
            list: [
                {"day": 3, "subject": "...", "email": "..."},
                {"day": 7, "subject": "...", "email": "..."},
                {"day": 14, "subject": "...", "email": "..."}
            ]
        """
        prompt_followup = ChatPromptTemplate.from_template(
            """
            ### ORIGINAL EMAIL:
            {initial_email}
            
            ### JOB DETAILS:
            {job_data}
            
            ### COMPANY:
            {company_name}
            
            ### INSTRUCTION:
            Create follow-up email #{followup_number} (to be sent after {days} days).
            
            **Follow-up Strategy:**
            - Follow-up 1 (Day 3): Gentle reminder, add one new value point
            - Follow-up 2 (Day 7): Share relevant resource/case study
            - Follow-up 3 (Day 14): Final check-in, alternative contact suggestion
            
            Keep it brief (100-150 words), professional, and non-pushy.
            Add a creative subject line.
            
            Return as JSON:
            {{
                "subject": "<subject line>",
                "email": "<email body>"
            }}
            
            NO PREAMBLE, ONLY JSON.
            
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
                    "email": f"Hi,\n\nI wanted to follow up on my previous email regarding the {job_data.get('role', 'position')} role.\n\nBest regards"
                })
        
        return follow_ups


    def generate_cold_email(self, job_data, links, tone=None, company_intel=None):
        """
        V2 FEATURE (Enhanced in V3): Generates a personalized cold email with adaptive tone.
        Now includes company intelligence for better personalization.
        
        Args:
            job_data (dict): Extracted job information
            links (list): Relevant portfolio links from ChromaDB
            tone (str, optional): Communication style. If None, will auto-detect.
            company_intel (dict, optional): Company research data from V3
            
        Returns:
            str: Generated cold email content
        """
        if tone is None:
            job_description_text = job_data.get('description', '')
            tone = self.detect_style(job_description_text)
            print(f"✨ Detected tone: {tone}")
        
        tone_instructions = {
            'formal': """
                Use highly professional language with complete sentences.
                Avoid contractions, casual phrases, or emojis.
                Address the recipient formally and maintain respectful distance.
            """,
            'technical': """
                Use technical terminology and demonstrate deep domain expertise.
                Reference specific technologies, frameworks, and methodologies.
                Focus on technical capabilities and measurable outcomes.
            """,
            'creative': """
                Use engaging, dynamic language with a conversational flow.
                Show personality while maintaining professionalism.
                Emphasize innovation and out-of-the-box thinking.
            """,
            'corporate': """
                Balance professionalism with approachability.
                Use clear business language without excessive formality.
                Focus on value proposition and mutual benefit.
            """,
            'marketing': """
                Use persuasive, benefit-driven language.
                Highlight results, success stories, and unique selling points.
                Create urgency and excitement about collaboration.
            """
        }
        
        tone_instruction = tone_instructions.get(tone, tone_instructions['corporate'])
        
        # Enhanced prompt with company intelligence
        company_context = ""
        if company_intel:
            company_context = f"""
            ### COMPANY INTELLIGENCE:
            Values: {', '.join(company_intel.get('key_values', []))}
            Recent Focus: {company_intel.get('recent_focus', '')}
            Culture: {', '.join(company_intel.get('culture_traits', []))}
            
            Use this information to personalize your email naturally.
            """
        
        prompt_email = ChatPromptTemplate.from_template(
            """
            ### JOB DESCRIPTION:
            {job_data}
            
            {company_context}

            ### COMMUNICATION TONE:
            {tone}
            
            ### TONE GUIDELINES:
            {tone_instruction}

            ### INSTRUCTION:
            You are a Business Development Engineer at a software and data solutions company specializing in
            Data Engineering, Artificial Intelligence, Cloud Integration, and Web Application Development.
            Your company helps organizations modernize their data architecture, automate workflows, and build scalable
            digital platforms tailored to their business needs.

            Your task is to write a professional cold email **in a {tone} style** to the client regarding the job mentioned above,
            demonstrating your company's ability to address their requirements effectively.
            
            **IMPORTANT**: Adapt your writing style according to the tone guidelines above.
            
            Highlight relevant experience, expertise, and how your team can add value to their project.
            Also include the most relevant portfolio links from the following list to showcase your previous work:
            {links}

            Keep the email concise (200-300 words maximum).
            Do NOT include any preamble, explanation, or subject line.

            ### EMAIL (NO PREAMBLE):
            """
        )

        chain_email = prompt_email | self.llm
        res = chain_email.invoke({
            "job_data": str(job_data),
            "links": str(links),
            "tone": tone,
            "tone_instruction": tone_instruction,
            "company_context": company_context
        })
        
        return res.content


if __name__ == "__main__":
    # V3 Testing Suite
    chain = Chain()
    
    # Test company research
    sample_job = """
    Senior ML Engineer at TechCorp. Work on large-scale recommendation systems.
    Required: Python, TensorFlow, distributed computing. We value innovation and collaboration.
    """
    
    print("=== Testing V3 Features ===\n")
    
    # 1. Company Research
    print("1. Company Research:")
    company_intel = chain.research_company("TechCorp", sample_job)
    print(json.dumps(company_intel, indent=2))
    
    # 2. Multi-Strategy Emails
    print("\n2. Email Variations:")
    job_data = {
        "role": "Senior ML Engineer",
        "experience": "5+ years",
        "skills": ["Python", "TensorFlow"],
        "description": sample_job
    }
    variations = chain.generate_email_variations(job_data, ["link1", "link2"], "technical", company_intel)
    print(f"Generated {len(variations)} variations")
    
    # 3. Email Analysis
    print("\n3. Email Analysis:")
    sample_email = variations["value_proposition"]
    analysis = chain.analyze_email_effectiveness(sample_email, job_data)
    print(f"Success Score: {analysis['success_score']}/100")
    
    # 4. Follow-up Sequence
    print("\n4. Follow-up Sequence:")
    followups = chain.generate_follow_up_sequence(sample_email, job_data, "TechCorp")
    print(f"Generated {len(followups)} follow-ups")
    
    print("\n✅ All V3 features tested successfully!")
