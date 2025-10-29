import re
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time

def clean_text(text):
    """
    Cleans a text by removing HTML tags, URLs, special characters,
    and extra whitespace.
    """
    # Remove HTML tags
    text = re.sub(r'<[^>]*?>', '', text)
    
    # Remove URLs
    text = re.sub(r'https?://\S+', '', text)
    
    # Remove non-alphanumeric characters (except spaces)
    text = re.sub(r'[^a-zA-Z0-9 ]', '', text)
    
    # Replace multiple consecutive spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    
    # Trim leading and trailing spaces
    text = text.strip()
    
    return text


def scrape_job_page(url: str, timeout: int = 10) -> Optional[str]:
    """
    🆕 V3 FEATURE: Enhanced web scraping with better error handling.
    
    Args:
        url (str): Job posting URL
        timeout (int): Request timeout in seconds
        
    Returns:
        str: Scraped page content or None if failed
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()
        
        text = soup.get_text(separator=' ', strip=True)
        return clean_text(text)
        
    except requests.exceptions.RequestException as e:
        print(f"Error scraping {url}: {str(e)}")
        return None


def discover_jobs_from_keywords(keywords: List[str], location: str = "Remote", 
                                max_results: int = 10) -> List[Dict]:
    """
    🆕 V3 FEATURE: AI-Powered Job Discovery
    
    Discovers relevant job postings based on skill keywords using free job boards.
    Uses Indeed's RSS feeds and other free sources.
    
    Args:
        keywords (list): List of skills/technologies to search for
        location (str): Job location
        max_results (int): Maximum number of jobs to return
        
    Returns:
        list: [
            {
                "title": str,
                "company": str,
                "location": str,
                "description_snippet": str,
                "url": str,
                "match_score": float (0-1)
            }
        ]
    """
    jobs_found = []
    
    # Construct search query
    query = " ".join(keywords[:3])  # Use top 3 keywords
    
    # Method 1: Indeed RSS (Free, no API key needed)
    try:
        indeed_url = f"https://www.indeed.com/jobs?q={query.replace(' ', '+')}&l={location.replace(' ', '+')}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(indeed_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Parse Indeed job cards
        job_cards = soup.find_all('div', class_='job_seen_beacon', limit=max_results)
        
        for card in job_cards:
            try:
                title_elem = card.find('h2', class_='jobTitle')
                company_elem = card.find('span', class_='companyName')
                location_elem = card.find('div', class_='companyLocation')
                snippet_elem = card.find('div', class_='job-snippet')
                
                if title_elem and company_elem:
                    title = title_elem.get_text(strip=True)
                    company = company_elem.get_text(strip=True)
                    loc = location_elem.get_text(strip=True) if location_elem else location
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    
                    # Extract job URL
                    link_elem = title_elem.find('a')
                    job_url = f"https://www.indeed.com{link_elem['href']}" if link_elem and 'href' in link_elem.attrs else ""
                    
                    # Calculate match score based on keyword presence
                    match_score = calculate_match_score(title + " " + snippet, keywords)
                    
                    jobs_found.append({
                        "title": title,
                        "company": company,
                        "location": loc,
                        "description_snippet": snippet[:200],
                        "url": job_url,
                        "match_score": match_score,
                        "source": "Indeed"
                    })
                    
            except Exception as e:
                continue
        
        # Sort by match score
        jobs_found.sort(key=lambda x: x['match_score'], reverse=True)
        
    except Exception as e:
        print(f"Error discovering jobs: {str(e)}")
    
    return jobs_found[:max_results]


def calculate_match_score(text: str, keywords: List[str]) -> float:
    """
    Calculates how well a job posting matches given keywords.
    
    Args:
        text (str): Job posting text
        keywords (list): List of skills/keywords
        
    Returns:
        float: Match score between 0 and 1
    """
    text_lower = text.lower()
    matches = sum(1 for keyword in keywords if keyword.lower() in text_lower)
    return min(matches / len(keywords), 1.0) if keywords else 0.0


def extract_company_name_from_url(url: str) -> str:
    """
    Extracts company name from job posting URL.

    Args:
        url (str): Job posting URL

    Returns:
        str: Extracted company name or domain
    """
    try:
        # Try to extract from domain
        from urllib.parse import urlparse
        domain = urlparse(url).netloc

        # Remove common prefixes
        domain = domain.replace('www.', '').replace('careers.', '').replace('jobs.', '')

        # Get main domain name
        company = domain.split('.')[0]

        # Capitalize properly
        return company.title()

    except Exception:
        return "Company"


def extract_company_from_title(title: str, url: str) -> str:
    """
    Extracts company name from job title or URL with improved logic.

    Args:
        title (str): Job title text
        url (str): Job posting URL

    Returns:
        str: Extracted company name
    """
    # First try to extract from URL
    company_from_url = extract_company_name_from_url(url)
    if company_from_url and company_from_url != "Company":
        return company_from_url

    # Try to extract from title patterns like "Company - Job Title" or "Job Title at Company"
    title_lower = title.lower()

    # Common patterns
    patterns = [
        r'(.+?)\s*-\s*.+',  # "Company - Job Title"
        r'.+?\s+at\s+(.+)',  # "Job Title at Company"
        r'(.+?)\s+hiring',  # "Company hiring"
    ]

    for pattern in patterns:
        match = re.search(pattern, title_lower, re.IGNORECASE)
        if match:
            company = match.group(1).strip()
            # Clean up common words
            company = re.sub(r'\b(jobs?|careers?|hiring|recruiting)\b', '', company, flags=re.IGNORECASE).strip()
            if company and len(company) > 1:
                return company.title()

    # Fallback to URL extraction
    return company_from_url


def extract_location_from_snippet(snippet: str) -> str:
    """
    Extracts location information from job snippet.

    Args:
        snippet (str): Job description snippet

    Returns:
        str: Extracted location or empty string
    """
    # Common location patterns
    location_patterns = [
        r'in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # "in City" or "in City State"
        r'at\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # "at City"
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:jobs?|positions?|roles?)',  # "City jobs"
    ]

    for pattern in location_patterns:
        match = re.search(pattern, snippet, re.IGNORECASE)
        if match:
            location = match.group(1).strip()
            # Filter out non-location words
            if not any(word in location.lower() for word in ['developer', 'engineer', 'manager', 'senior', 'junior']):
                return location

    return ""


def validate_email_format(email: str) -> bool:
    """
    Validates email format.
    
    Args:
        email (str): Email string to validate
        
    Returns:
        bool: True if valid format
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def rate_limit_sleep(min_seconds: float = 1.0, max_seconds: float = 2.0):
    """
    Sleep for a random duration to respect rate limits.
    
    Args:
        min_seconds (float): Minimum sleep time
        max_seconds (float): Maximum sleep time
    """
    import random
    time.sleep(random.uniform(min_seconds, max_seconds))


def extract_skills_from_portfolio(portfolio_data: List[Dict]) -> List[str]:
    """
    🆕 V3 FEATURE: Extract unique skills from portfolio for job discovery.
    
    Args:
        portfolio_data (list): Portfolio entries with tech stacks
        
    Returns:
        list: Unique list of skills/technologies
    """
    skills = set()
    
    for entry in portfolio_data:
        if 'TechStack' in entry:
            # Split by common delimiters
            tech_items = re.split(r'[,;|]', entry['TechStack'])
            for tech in tech_items:
                tech = tech.strip()
                if tech and len(tech) > 1:  # Avoid single characters
                    skills.add(tech)
    
    return sorted(list(skills))


def search_jobs_google_custom(query: str, num_results: int = 10) -> List[Dict]:
    """
    🆕 V3 FEATURE: Alternative job search using DuckDuckGo (no API key needed).

    Args:
        query (str): Search query (e.g., "Python developer remote")
        num_results (int): Number of results to return

    Returns:
        list: Job postings found
    """
    jobs = []

    try:
        # DuckDuckGo HTML scraping (free, no API key)
        search_url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}+job"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Parse search results
        results = soup.find_all('div', class_='result', limit=num_results * 2)

        for result in results:
            try:
                title_elem = result.find('a', class_='result__a')
                snippet_elem = result.find('a', class_='result__snippet')

                if title_elem and 'href' in title_elem.attrs:
                    title = title_elem.get_text(strip=True)
                    url = title_elem['href']
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""

                    # Filter for job-related results
                    if any(keyword in title.lower() for keyword in ['job', 'career', 'hiring', 'position']):
                        # Extract company name from title or URL
                        company = extract_company_from_title(title, url)

                        # Extract location from snippet if available
                        location = extract_location_from_snippet(snippet)
                        if not location:
                            location = "Remote"  # Default fallback

                        # Calculate dynamic match score
                        match_score = calculate_match_score(title + " " + snippet, query.split())

                        jobs.append({
                            "title": title,
                            "company": company,
                            "location": location,
                            "description_snippet": snippet[:200],
                            "url": url,
                            "match_score": match_score,
                            "source": "DuckDuckGo"
                        })

                        if len(jobs) >= num_results:
                            break

            except Exception:
                continue

    except Exception as e:
        print(f"Error in DuckDuckGo search: {str(e)}")

    return jobs


def fetch_job_boards_aggregate(keywords: List[str], location: str = "Remote") -> List[Dict]:
    """
    🆕 V3 FEATURE: Aggregate jobs from multiple free sources.
    
    Combines results from Indeed, LinkedIn (public), and web search.
    
    Args:
        keywords (list): Skills to search for
        location (str): Desired location
        
    Returns:
        list: Aggregated job listings
    """
    all_jobs = []
    
    # Source 1: Indeed
    indeed_jobs = discover_jobs_from_keywords(keywords, location, max_results=5)
    all_jobs.extend(indeed_jobs)
    
    # Source 2: Web search for additional results
    query = f"{' '.join(keywords[:2])} developer {location} job"
    web_jobs = search_jobs_google_custom(query, num_results=5)
    all_jobs.extend(web_jobs)
    
    # Remove duplicates based on URL
    seen_urls = set()
    unique_jobs = []
    
    for job in all_jobs:
        if job['url'] and job['url'] not in seen_urls:
            seen_urls.add(job['url'])
            unique_jobs.append(job)
    
    # Sort by match score
    unique_jobs.sort(key=lambda x: x.get('match_score', 0), reverse=True)
    
    return unique_jobs


def format_email_for_download(email: str, metadata: Dict) -> str:
    """
    🆕 V3 FEATURE: Format email with metadata for download.
    
    Args:
        email (str): Email content
        metadata (dict): Job and analysis metadata
        
    Returns:
        str: Formatted email with header
    """
    header = f"""
==========================================
AI-Generated Cold Email
==========================================
Date Generated: {time.strftime('%Y-%m-%d %H:%M')}
Position: {metadata.get('role', 'N/A')}
Company: {metadata.get('company', 'N/A')}
Tone: {metadata.get('tone', 'N/A').upper()}
Success Score: {metadata.get('success_score', 'N/A')}/100
==========================================

"""
    return header + email


def batch_process_jobs(job_urls: List[str], max_concurrent: int = 3) -> List[Dict]:
    """
    🆕 V3 FEATURE: Process multiple job URLs efficiently.
    
    Args:
        job_urls (list): List of job posting URLs
        max_concurrent (int): Maximum concurrent requests
        
    Returns:
        list: Scraped job data
    """
    results = []
    
    for i, url in enumerate(job_urls):
        if i > 0 and i % max_concurrent == 0:
            rate_limit_sleep(2.0, 3.0)
        
        content = scrape_job_page(url)
        if content:
            results.append({
                "url": url,
                "content": content,
                "company": extract_company_name_from_url(url)
            })
    
    return results


# Testing function
if __name__ == "__main__":
    print("=== Testing V3 Utils ===\n")
    
    # Test 1: Job Discovery
    print("1. Testing Job Discovery:")
    keywords = ["Python", "Machine Learning", "Data Science"]
    jobs = discover_jobs_from_keywords(keywords, "Remote", max_results=3)
    print(f"Found {len(jobs)} jobs")
    if jobs:
        print(f"Top match: {jobs[0]['title']} at {jobs[0]['company']}")
    
    # Test 2: Skill Extraction
    print("\n2. Testing Skill Extraction:")
    sample_portfolio = [
        {"TechStack": "Python, TensorFlow, AWS"},
        {"TechStack": "React | Node.js | MongoDB"}
    ]
    skills = extract_skills_from_portfolio(sample_portfolio)
    print(f"Extracted skills: {skills}")
    
    # Test 3: Company Name Extraction
    print("\n3. Testing Company Name Extraction:")
    url = "https://careers.google.com/jobs/12345"
    company = extract_company_name_from_url(url)
    print(f"Extracted company: {company}")
    
    print("\n✅ All utils tests completed!")