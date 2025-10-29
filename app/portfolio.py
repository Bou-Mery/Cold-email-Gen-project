import pandas as pd
import chromadb 
import uuid
import os
from typing import List, Dict
import re
import streamlit as st

class Portfolio:
    def __init__(self, file_path="app/rsrc/links_portfolio.csv"):
        self.file_path = file_path
        
        try:
            # Try to load the CSV file
            self.data = pd.read_csv(self.file_path)
            st.sidebar.success(f"✅ Portfolio CSV loaded: {len(self.data)} projects")
        except Exception as e:
            st.error(f"❌ Error loading portfolio CSV from {self.file_path}: {str(e)}")
            # Create empty dataframe as fallback
            self.data = pd.DataFrame(columns=['TechStack', 'Portfolio_Link'])
            st.warning("⚠️ Using empty portfolio - some features will be limited")
        
        try:
            # Ensure the vector_db directory exists
            db_path = "vector_db"
            os.makedirs(db_path, exist_ok=True)
            
            # Initialize the ChromaDB client with the path
            self.client = chromadb.PersistentClient(path=db_path)
            self.collection = self.client.get_or_create_collection(name="portfolio_collection")
            st.sidebar.success("✅ ChromaDB initialized")
            
        except Exception as e:
            st.error(f"❌ Error initializing ChromaDB: {str(e)}")
            self.client = None
            self.collection = None
        
        # 🆕 V3: Cache for extracted skills
        self._skills_cache = None
        
    
    def load_portfolio(self):
        """
        V2 FEATURE: Load portfolio into ChromaDB vector store.
        """
        if not self.collection.count():
            for _, row in self.data.iterrows():
                self.collection.add(
                    documents=[row['TechStack']],
                    metadatas=[{"link": row['Portfolio_Link']}],
                    ids=[str(uuid.uuid4())]
                )

    
    def query_links(self, skills):
        """
        V2 FEATURE: Query relevant portfolio links based on skills.
        
        Args:
            skills (str): Skills string to match against
            
        Returns:
            list: Matching portfolio metadata
        """
        return self.collection.query(
            query_texts=[skills],
            n_results=2
        ).get('metadatas', [])
    
    
    def extract_all_skills(self) -> List[str]:
        """
        🆕 V3 FEATURE: Extract all unique skills from portfolio.
        
        Returns:
            list: Sorted list of unique skills/technologies
        """
        if self._skills_cache is not None:
            return self._skills_cache
        
        skills_set = set()
        
        for _, row in self.data.iterrows():
            tech_stack = str(row['TechStack'])
            
            # Split by common delimiters: comma, semicolon, pipe, slash
            skills = re.split(r'[,;|/]', tech_stack)
            
            for skill in skills:
                # Clean and normalize
                skill = skill.strip()
                
                # Remove parentheses content
                skill = re.sub(r'\([^)]*\)', '', skill).strip()
                
                # Skip empty or very short strings
                if len(skill) > 1 and not skill.isdigit():
                    skills_set.add(skill)
        
        # Sort alphabetically
        self._skills_cache = sorted(list(skills_set))
        return self._skills_cache
    
    
    def get_skill_categories(self) -> Dict[str, List[str]]:
        """
        🆕 V3 FEATURE: Categorize skills by domain.
        
        Returns:
            dict: {
                "languages": [...],
                "frameworks": [...],
                "databases": [...],
                "cloud": [...],
                "tools": [...]
            }
        """
        all_skills = self.extract_all_skills()
        
        categories = {
            "languages": [],
            "frameworks": [],
            "databases": [],
            "cloud": [],
            "tools": [],
            "other": []
        }
        
        # Define keyword mappings
        language_keywords = ['python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust', 'ruby', 'php', 'swift', 'kotlin', 'scala', 'r']
        framework_keywords = ['react', 'angular', 'vue', 'django', 'flask', 'spring', 'express', 'fastapi', 'tensorflow', 'pytorch', 'keras', 'scikit']
        database_keywords = ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'cassandra', 'dynamodb', 'firestore', 'elasticsearch']
        cloud_keywords = ['aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'terraform', 'jenkins']
        tool_keywords = ['git', 'jira', 'confluence', 'tableau', 'power bi', 'jupyter', 'vscode', 'postman']
        
        for skill in all_skills:
            skill_lower = skill.lower()
            categorized = False
            
            # Check each category
            if any(keyword in skill_lower for keyword in language_keywords):
                categories["languages"].append(skill)
                categorized = True
            elif any(keyword in skill_lower for keyword in framework_keywords):
                categories["frameworks"].append(skill)
                categorized = True
            elif any(keyword in skill_lower for keyword in database_keywords):
                categories["databases"].append(skill)
                categorized = True
            elif any(keyword in skill_lower for keyword in cloud_keywords):
                categories["cloud"].append(skill)
                categorized = True
            elif any(keyword in skill_lower for keyword in tool_keywords):
                categories["tools"].append(skill)
                categorized = True
            
            if not categorized:
                categories["other"].append(skill)
        
        return categories
    
    
    def get_top_skills(self, top_n: int = 10) -> List[str]:
        """
        🆕 V3 FEATURE: Get most frequently mentioned skills.
        
        Args:
            top_n (int): Number of top skills to return
            
        Returns:
            list: Top N skills by frequency
        """
        skill_counts = {}
        
        for _, row in self.data.iterrows():
            tech_stack = str(row['TechStack']).lower()
            
            for skill in self.extract_all_skills():
                if skill.lower() in tech_stack:
                    skill_counts[skill] = skill_counts.get(skill, 0) + 1
        
        # Sort by frequency
        sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)
        return [skill for skill, _ in sorted_skills[:top_n]]
    
    
    def find_projects_by_skill(self, skill: str) -> List[Dict]:
        """
        🆕 V3 FEATURE: Find portfolio projects that use a specific skill.
        
        Args:
            skill (str): Skill to search for
            
        Returns:
            list: [{"tech_stack": str, "link": str}]
        """
        matching_projects = []
        skill_lower = skill.lower()
        
        for _, row in self.data.iterrows():
            tech_stack = str(row['TechStack'])
            
            if skill_lower in tech_stack.lower():
                matching_projects.append({
                    "tech_stack": tech_stack,
                    "link": row['Portfolio_Link']
                })
        
        return matching_projects
    
    
    def suggest_skills_for_job(self, job_skills: List[str]) -> Dict:
        """
        🆕 V3 FEATURE: Analyze match between job requirements and portfolio.
        
        Args:
            job_skills (list): Required skills from job posting
            
        Returns:
            dict: {
                "matching_skills": [...],
                "missing_skills": [...],
                "match_percentage": float,
                "relevant_projects": [...]
            }
        """
        portfolio_skills = [s.lower() for s in self.extract_all_skills()]
        job_skills_lower = [s.lower() for s in job_skills]
        
        # Find matches
        matching = [s for s in job_skills if s.lower() in portfolio_skills]
        missing = [s for s in job_skills if s.lower() not in portfolio_skills]
        
        # Calculate match percentage
        match_pct = (len(matching) / len(job_skills) * 100) if job_skills else 0
        
        # Find relevant projects
        relevant_projects = []
        for skill in matching[:3]:  # Top 3 matching skills
            projects = self.find_projects_by_skill(skill)
            relevant_projects.extend(projects[:2])  # Max 2 projects per skill
        
        # Remove duplicates
        unique_projects = []
        seen_links = set()
        for proj in relevant_projects:
            if proj['link'] not in seen_links:
                seen_links.add(proj['link'])
                unique_projects.append(proj)
        
        return {
            "matching_skills": matching,
            "missing_skills": missing,
            "match_percentage": round(match_pct, 1),
            "relevant_projects": unique_projects[:4]  # Max 4 projects
        }
    
    
    def get_portfolio_summary(self) -> Dict:
        """
        🆕 V3 FEATURE: Get comprehensive portfolio statistics.
        
        Returns:
            dict: Portfolio analytics and summary
        """
        all_skills = self.extract_all_skills()
        categories = self.get_skill_categories()
        top_skills = self.get_top_skills(5)
        
        return {
            "total_projects": len(self.data),
            "total_skills": len(all_skills),
            "top_skills": top_skills,
            "skill_categories": {
                cat: len(skills) for cat, skills in categories.items() if skills
            },
            "languages": categories["languages"][:5],
            "frameworks": categories["frameworks"][:5],
            "databases": categories["databases"][:3],
            "cloud_platforms": categories["cloud"][:3]
        }
    
    
    def export_skills_list(self, output_file: str = "portfolio_skills.txt"):
        """
        🆕 V3 FEATURE: Export all skills to a text file.
        
        Args:
            output_file (str): Output file path
        """
        skills = self.extract_all_skills()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=== PORTFOLIO SKILLS ===\n\n")
            
            categories = self.get_skill_categories()
            
            for category, skill_list in categories.items():
                if skill_list:
                    f.write(f"\n{category.upper()}:\n")
                    for skill in sorted(skill_list):
                        f.write(f"  - {skill}\n")
        
        print(f"✅ Skills exported to {output_file}")


# Testing
if __name__ == "__main__":
    print("=== Testing V3 Portfolio Features ===\n")
    
    portfolio = Portfolio()
    portfolio.load_portfolio()
    
    # Test 1: Extract all skills
    print("1. All Skills:")
    skills = portfolio.extract_all_skills()
    print(f"   Total skills: {len(skills)}")
    print(f"   Sample: {skills[:5]}")
    
    # Test 2: Skill categories
    print("\n2. Skill Categories:")
    categories = portfolio.get_skill_categories()
    for cat, skills in categories.items():
        if skills:
            print(f"   {cat}: {len(skills)} skills")
    
    # Test 3: Top skills
    print("\n3. Top 5 Skills:")
    top = portfolio.get_top_skills(5)
    for i, skill in enumerate(top, 1):
        print(f"   {i}. {skill}")
    
    # Test 4: Job matching
    print("\n4. Job Match Analysis:")
    job_skills = ["Python", "TensorFlow", "AWS", "Docker", "Nonexistent"]
    match = portfolio.suggest_skills_for_job(job_skills)
    print(f"   Match: {match['match_percentage']}%")
    print(f"   Matching: {match['matching_skills']}")
    print(f"   Missing: {match['missing_skills']}")
    
    # Test 5: Portfolio summary
    print("\n5. Portfolio Summary:")
    summary = portfolio.get_portfolio_summary()
    print(f"   Projects: {summary['total_projects']}")
    print(f"   Skills: {summary['total_skills']}")
    print(f"   Top: {', '.join(summary['top_skills'][:3])}")
    
    print("\n✅ All portfolio tests completed!")
