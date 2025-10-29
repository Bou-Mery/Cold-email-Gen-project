import streamlit as st
from langchain_community.document_loaders import WebBaseLoader
from chains import Chain
from portfolio import Portfolio
from utils import (
    clean_text,
    scrape_job_page,
    discover_jobs_from_keywords,
    extract_company_name_from_url,
    format_email_for_download,
    fetch_job_boards_aggregate
)
import time
import os


def health_check():
    """Health check endpoint for Docker."""
    return {"status": "healthy", "timestamp": time.time()}

def create_streamlit_app(llm, portfolio, clean_text):
    # ========== PROFESSIONAL AI-POWERED UI STYLES ==========
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
        
        * {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        .main-hero {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #d946ef 100%);
            padding: 3rem 2rem;
            border-radius: 20px;
            margin-bottom: 2.5rem;
            box-shadow: 0 20px 60px rgba(99, 102, 241, 0.3);
            position: relative;
            overflow: hidden;
        }
        
        .main-hero::before {
            content: '';
            position: absolute;
            top: -50%;
            right: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            animation: pulse 15s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1) rotate(0deg); }
            50% { transform: scale(1.1) rotate(180deg); }
        }
        
        .hero-content {
            position: relative;
            z-index: 1;
        }
        
        .main-hero h1 {
            color: white;
            font-size: 3rem;
            font-weight: 800;
            margin: 0 0 0.5rem 0;
            text-shadow: 0 4px 20px rgba(0,0,0,0.2);
            letter-spacing: -0.02em;
        }
        
        .hero-subtitle {
            color: rgba(255, 255, 255, 0.95);
            font-size: 1.3rem;
            font-weight: 500;
            margin-bottom: 1rem;
        }
        
        .ai-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(10px);
            padding: 0.5rem 1.2rem;
            backdrop-filter: blur(10px);
            padding: 0.5rem 1.2rem;
            border-radius: 30px;
            font-size: 0.95rem;
            font-weight: 600;
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }
        
        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }
        
        .feature-card {
            background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
            border: 2px solid #e2e8f0;
            border-radius: 16px;
            padding: 1.5rem;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: default;
        }
        
        .feature-card:hover {
            border-color: #6366f1;
            transform: translateY(-4px);
            box-shadow: 0 12px 40px rgba(99, 102, 241, 0.15);
        }
        
        .feature-icon {
            font-size: 2.5rem;
            margin-bottom: 0.8rem;
            display: block;
        }
        
        .feature-title {
            font-size: 1.1rem;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 0.5rem;
        }
        
        .feature-desc {
            font-size: 0.9rem;
            color: #64748b;
            line-height: 1.6;
        }
        
        .section-header {
            display: flex;
            align-items: center;
            gap: 0.8rem;
            margin: 2.5rem 0 1.5rem 0;
            padding-bottom: 1rem;
            border-bottom: 2px solid #e2e8f0;
        }
        
        .section-header h2 {
            font-size: 1.8rem;
            font-weight: 700;
            color: #1e293b;
            margin: 0;
        }
        
        .section-icon {
            font-size: 2rem;
        }
        
        .job-card-modern {
            background: white;
            border: 2px solid #e2e8f0;
            border-radius: 16px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .job-card-modern::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            height: 100%;
            width: 4px;
            background: linear-gradient(180deg, #6366f1, #8b5cf6);
            transform: scaleY(0);
            transition: transform 0.3s ease;
        }
        
        .job-card-modern:hover {
            border-color: #6366f1;
            box-shadow: 0 8px 30px rgba(99, 102, 241, 0.15);
            transform: translateX(4px);
        }
        
        .job-card-modern:hover::before {
            transform: scaleY(1);
        }
        
        .match-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            padding: 0.4rem 0.9rem;
            border-radius: 20px;
            font-weight: 700;
            font-size: 0.85rem;
            color: white;
        }
        
        .metric-card {
            background: white;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            padding: 1.2rem;
            text-align: center;
            transition: all 0.3s ease;
        }
        
        .metric-card:hover {
            border-color: #6366f1;
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(99, 102, 241, 0.1);
        }
        
        .metric-value {
            font-size: 2.2rem;
            font-weight: 800;
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.3rem;
        }
        
        .metric-label {
            font-size: 0.85rem;
            color: #64748b;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        
        .strategy-card {
            background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
            border: 2px solid #e2e8f0;
            border-radius: 16px;
            padding: 1.8rem;
            margin: 1.5rem 0;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
        }
        
        .score-display {
            text-align: center;
            margin: 2rem 0;
        }
        
        .score-circle {
            width: 140px;
            height: 140px;
            margin: 0 auto 1rem;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 3rem;
            font-weight: 800;
            position: relative;
        }
        
        .score-excellent {
            background: linear-gradient(135deg, #10b981, #059669);
            color: white;
            box-shadow: 0 8px 30px rgba(16, 185, 129, 0.3);
        }
        
        .score-good {
            background: linear-gradient(135deg, #3b82f6, #2563eb);
            color: white;
            box-shadow: 0 8px 30px rgba(59, 130, 246, 0.3);
        }
        
        .score-fair {
            background: linear-gradient(135deg, #f59e0b, #d97706);
            color: white;
            box-shadow: 0 8px 30px rgba(245, 158, 11, 0.3);
        }
        
        .score-poor {
            background: linear-gradient(135deg, #ef4444, #dc2626);
            color: white;
            box-shadow: 0 8px 30px rgba(239, 68, 68, 0.3);
        }
        
        .tone-badge-modern {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.6rem 1.2rem;
            border-radius: 25px;
            font-weight: 700;
            font-size: 0.95rem;
            border: 2px solid;
        }
        
        .tone-formal { 
            background: linear-gradient(135deg, #dbeafe, #bfdbfe);
            border-color: #3b82f6;
            color: #1e40af;
        }
        
        .tone-technical { 
            background: linear-gradient(135deg, #e9d5ff, #d8b4fe);
            border-color: #8b5cf6;
            color: #6b21a8;
        }
        
        .tone-creative { 
            background: linear-gradient(135deg, #fed7aa, #fdba74);
            border-color: #f97316;
            color: #9a3412;
        }
        
        .tone-corporate { 
            background: linear-gradient(135deg, #d1fae5, #a7f3d0);
            border-color: #10b981;
            color: #065f46;
        }
        
        .tone-marketing { 
            background: linear-gradient(135deg, #fce7f3, #fbcfe8);
            border-color: #ec4899;
            color: #9f1239;
        }
        
        .insight-box {
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            border-left: 4px solid #f59e0b;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1.5rem 0;
        }
        
        .insight-box strong {
            color: #92400e;
            display: block;
            margin-bottom: 0.8rem;
            font-size: 1.1rem;
        }
        
        .insight-item {
            color: #78350f;
            margin: 0.5rem 0;
            padding-left: 1.2rem;
            position: relative;
        }
        
        .insight-item::before {
            content: '→';
            position: absolute;
            left: 0;
            font-weight: bold;
        }
        
        .timeline-container {
            background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 50%, #d946ef 100%);
            height: 6px;
            border-radius: 3px;
            margin: 2rem 0;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
        }
        
        .mode-selector {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
            margin: 2rem 0;
        }
        
        .mode-option {
            background: white;
            border: 3px solid #e2e8f0;
            border-radius: 16px;
            padding: 2rem;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .mode-option:hover {
            border-color: #6366f1;
            transform: scale(1.02);
            box-shadow: 0 12px 40px rgba(99, 102, 241, 0.15);
        }
        
        .mode-option.selected {
            border-color: #6366f1;
            background: linear-gradient(135deg, #eef2ff, #e0e7ff);
        }
        
        .cta-button {
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
            color: white;
            padding: 1rem 2rem;
            border-radius: 12px;
            font-weight: 700;
            font-size: 1.1rem;
            border: none;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 8px 25px rgba(99, 102, 241, 0.3);
        }
        
        .cta-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 35px rgba(99, 102, 241, 0.4);
        }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 1rem;
            margin: 2rem 0;
        }
        
        .footer-section {
            background: linear-gradient(100deg, #6366f1 0%, #8b5cf6 50%, #d946ef 100%);
            color: white;
            padding: 3rem 2rem;
            border-radius: 20px;
            margin-top: 4rem;
            text-align: center;
        }
        
        .footer-title {
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
        }
        
        .footer-features {
            display: flex;
            justify-content: center;
            gap: 2rem;
            flex-wrap: wrap;
            margin: 1.5rem 0;
            font-size: 0.9rem;
            color: #cbd5e1;
        }
        
        .footer-link {
            color: #818cf8;
            text-decoration: none;
            font-weight: 600;
            transition: color 0.3s ease;
        }
        
        .footer-link:hover {
            color: #a5b4fc;
        }
        
        .stButton>button {
            background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 0.75rem 2rem !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 25px rgba(99, 102, 241, 0.3) !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # ========== HERO SECTION ==========
    st.markdown("""
        <div class="main-hero">
            <div class="hero-content">
                <h1>🚀 AI Cold Email Generator</h1>
                <p class="hero-subtitle">Transform job postings into personalized, high-converting email campaigns</p>
                <span class="ai-badge">
                    <span>⚡</span>
                    <span>Powered by Advanced AI • V3.0</span>
                </span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # ========== KEY FEATURES SHOWCASE ==========
    with st.expander("✨ Platform Capabilities", expanded=False):
        st.markdown("""
        <div class="feature-grid">
            <div class="feature-card">
                <span class="feature-icon">🎯</span>
                <div class="feature-title">Intelligent Job Discovery</div>
                <div class="feature-desc">AI automatically finds and matches relevant opportunities based on your skills</div>
            </div>
            <div class="feature-card">
                <span class="feature-icon">🏢</span>
                <div class="feature-title">Company Intelligence</div>
                <div class="feature-desc">Deep research into company values, culture, and priorities for personalization</div>
            </div>
            <div class="feature-card">
                <span class="feature-icon">📧</span>
                <div class="feature-title">Multi-Strategy Emails</div>
                <div class="feature-desc">3 proven approaches: Value Proposition, Problem-Solution, Storytelling</div>
            </div>
            <div class="feature-card">
                <span class="feature-icon">📊</span>
                <div class="feature-title">Success Analytics</div>
                <div class="feature-desc">AI-powered effectiveness scoring with actionable improvement insights</div>
            </div>
            <div class="feature-card">
                <span class="feature-icon">🔄</span>
                <div class="feature-title">Automated Follow-ups</div>
                <div class="feature-desc">Complete 3-email sequences timed for maximum engagement</div>
            </div>
            <div class="feature-card">
                <span class="feature-icon">🎨</span>
                <div class="feature-title">Adaptive Tone</div>
                <div class="feature-desc">Smart detection and matching of communication style to company culture</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # ========== MODE SELECTION ==========
    st.markdown('<div class="section-header"><span class="section-icon">🎯</span><h2>Choose Your Workflow</h2></div>', unsafe_allow_html=True)
    
    mode = st.radio(
        "",
        ["🧠 Smart Discovery", "🔗 Direct URL Input"],
        horizontal=True,
        label_visibility="collapsed",
        help="Smart Discovery: AI finds jobs for you | Direct: Paste specific URL"
    )
    
    # ========================================
    # MODE 1: SMART DISCOVERY
    # ========================================
    if mode == "🧠 Smart Discovery":
        
        # Portfolio Analysis
        with st.expander("📊 Portfolio Overview", expanded=False):
            portfolio.load_portfolio()
            summary = portfolio.get_portfolio_summary()
            
            st.markdown('<div class="stats-grid">', unsafe_allow_html=True)
            
            cols = st.columns(4)
            metrics = [
                (summary['total_projects'], "Projects", "📁"),
                (summary['total_skills'], "Skills", "⚡"),
                (len(summary.get('languages', [])), "Languages", "💻"),
                (len(summary.get('frameworks', [])), "Frameworks", "🔧")
            ]
            
            for col, (value, label, icon) in zip(cols, metrics):
                with col:
                    st.markdown(f"""
                        <div class="metric-card">
                            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{icon}</div>
                            <div class="metric-value">{value}</div>
                            <div class="metric-label">{label}</div>
                        </div>
                    """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("**🔥 Core Competencies:**")
            st.write(", ".join(summary['top_skills'][:8]))
        
        # Job Discovery Interface
        st.markdown('<div class="section-header"><span class="section-icon">🔍</span><h2>AI Job Discovery</h2></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            default_skills = ", ".join(portfolio.get_top_skills(3))
            search_input = st.text_input(
                "Skills & Keywords",
                value=default_skills,
                placeholder="e.g., Python, Machine Learning, AWS"
            )
        
        with col2:
            location_input = st.text_input("Location", value="Remote")
        
        discover_button = st.button("🚀 Discover Opportunities", type="primary", use_container_width=True)
        
        if discover_button and search_input:
            with st.spinner("🔍 AI analyzing job market..."):
                keywords = [k.strip() for k in search_input.split(',') if k.strip()]
                jobs = fetch_job_boards_aggregate(keywords, location_input)
                
                if jobs:
                    st.success(f"✅ Discovered {len(jobs)} matching opportunities")
                    st.session_state['discovered_jobs'] = jobs
                else:
                    st.warning("No matches found. Try different keywords.")
        
        # Display discovered jobs
        if 'discovered_jobs' in st.session_state and st.session_state['discovered_jobs']:
            st.markdown('<div class="section-header"><span class="section-icon">📋</span><h2>Select Opportunities</h2></div>', unsafe_allow_html=True)
            
            selected_jobs = []
            
            for idx, job in enumerate(st.session_state['discovered_jobs']):
                score = job.get('match_score', 0)
                score_color = "#10b981" if score > 0.7 else "#f59e0b" if score > 0.4 else "#ef4444"

                col1, col2 = st.columns([0.5, 9.5])

                with col1:
                    is_selected = st.checkbox("", key=f"job_{idx}", label_visibility="collapsed")
                    if is_selected:
                        selected_jobs.append((idx, job))

                with col2:
                    job_url = job.get('url', '')
                    url_display = f'<a href="{job_url}" target="_blank" style="color: #6366f1; text-decoration: none; font-weight: 600;">🌐 View Position</a>' if job_url else '<span style="color: #ef4444;">URL unavailable</span>'

                    st.markdown(f"""
                    <div class="job-card-modern">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div style="flex: 1;">
                                <div style="color: #1e293b; font-size: 1.2rem; font-weight: 700; margin-bottom: 0.4rem;">{job['title']}</div>
                                <div style="color: #64748b; font-size: 0.95rem; margin-bottom: 0.5rem;">{job['location']}</div>
                                <div>{url_display}</div>
                            </div>
                            <div>
                                <span class="match-badge" style="background-color: {score_color};">
                                    {int(score * 100)}% Match
                                </span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Process selected jobs
            if selected_jobs:
                st.markdown("---")
                st.info(f"✅ {len(selected_jobs)} opportunity selected")
                
                if st.button("✨ Generate Email Campaigns", type="primary", use_container_width=True):
                    for idx, job in selected_jobs:
                        st.markdown('<div class="section-header"><span class="section-icon">📧</span><h2>Email Campaign</h2></div>', unsafe_allow_html=True)
                        st.markdown(f"**Company:** {job['company']}")

                        job_url = job.get('url', '')
                        if job_url:
                            st.markdown(f"**Position Link:** [{job_url}]({job_url})")

                        with st.spinner(f"🔄 Generating campaign for {job['title']}..."):
                            try:
                                # Scrape job details
                                if job.get('url'):
                                    job_content = scrape_job_page(job['url'])
                                    if job_content:
                                        job_data = llm.extract_jobs(job_content)
                                    else:
                                        job_data = {
                                            'role': job['title'],
                                            'experience': 'Not specified',
                                            'skills': [],
                                            'description': job.get('description_snippet', '')
                                        }
                                else:
                                    job_data = {
                                        'role': job['title'],
                                        'experience': 'Not specified',
                                        'skills': [],
                                        'description': job.get('description_snippet', '')
                                    }
                                
                                # Company Research
                                with st.spinner("🏢 Analyzing company..."):
                                    company_intel = llm.research_company(
                                        job['company'],
                                        job_data.get('description', '')
                                    )
                                
                          
                                
                                # Detect Tone
                                detected_tone = llm.detect_style(job_data.get('description', ''))
                                
                                tone_emoji = {
                                    'formal': '🎩',
                                    'technical': '💻',
                                    'creative': '🎨',
                                    'corporate': '🏢',
                                    'marketing': '📢'
                                }
                                
                                st.markdown(f"""
                                <div style="text-align: center; margin: 1.5rem 0;">
                                    <span class="tone-badge-modern tone-{detected_tone}">
                                        <span>{tone_emoji.get(detected_tone, '✨')}</span>
                                        <span>Communication Style: {detected_tone.upper()}</span>
                                    </span>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Portfolio Matching
                                skills = job_data.get('skills', [])
                                links = portfolio.query_links(str(skills))
                                
                                # Generate 3 Email Strategies
                                with st.spinner("✍️ Crafting email strategies..."):
                                    email_variations = llm.generate_email_variations(
                                        job_data, 
                                        links, 
                                        detected_tone,
                                        company_intel
                                    )
                                
                                # Display email strategies
                                tab1, tab2, tab3 = st.tabs(["💼 Value Focus", "🔧 Solution Approach", "📖 Story Method"])
                                
                                strategies = [
                                    ("value_proposition", tab1, "Value Proposition", "ROI-focused approach"),
                                    ("problem_solution", tab2, "Problem-Solution", "Pain point resolution"),
                                    ("storytelling", tab3, "Storytelling", "Narrative engagement")
                                ]
                                
                                best_email = None
                                best_score = 0
                                
                                for strategy_key, tab, title, description in strategies:
                                    with tab:
                                        email = email_variations[strategy_key]
                                        
                                        st.markdown(f"**{title}** • *{description}*")
                                        
                                        # Analyze effectiveness
                                        analysis = llm.analyze_email_effectiveness(email, job_data)
                                        score = analysis.get('success_score', 75)
                                        
                                        if score > best_score:
                                            best_score = score
                                            best_email = email
                                        
                                        # Score visualization
                                        score_class = "score-excellent" if score >= 80 else "score-good" if score >= 70 else "score-fair" if score >= 60 else "score-poor"
                                        
                                        st.markdown(f"""
                                        <div class="score-display">
                                            <div class="score-circle {score_class}">
                                                {score}
                                            </div>
                                            <div style="color: #64748b; font-weight: 600;">Success Prediction Score</div>
                                        </div>
                                        """, unsafe_allow_html=True)
                                        
                                        # Metrics
                                        with st.expander("📊 Detailed Breakdown"):
                                            metrics = analysis.get('key_metrics', {})
                                            
                                            mcol1, mcol2, mcol3, mcol4 = st.columns(4)
                                            
                                            metric_items = [
                                                (mcol1, "Relevance", metrics.get('relevance', 0)),
                                                (mcol2, "Clarity", metrics.get('clarity', 0)),
                                                (mcol3, "Personal", metrics.get('personalization', 0)),
                                                (mcol4, "CTA", metrics.get('call_to_action', 0))
                                            ]
                                            
                                            for col, label, value in metric_items:
                                                with col:
                                                    st.metric(label, f"{value}/25")
                                            
                                            st.markdown("**✅ Strengths:**")
                                            for strength in analysis.get('strengths', []):
                                                st.markdown(f"• {strength}")
                                            
                                            st.markdown("**💡 Optimization Tips:**")
                                            for improvement in analysis.get('improvements', []):
                                                st.markdown(f"• {improvement}")
                                        
                                        # Email content
                                        st.markdown("**📧 Generated Email:**")
                                        st.code(email, language='markdown')
                                        
                                        # Download
                                        metadata = {
                                            'role': job_data.get('role', 'N/A'),
                                            'company': job['company'],
                                            'tone': detected_tone,
                                            'success_score': score,
                                            'strategy': title
                                        }
                                        formatted_email = format_email_for_download(email, metadata)
                                        
                                        st.download_button(
                                            label=f"📥 Download {title}",
                                            data=formatted_email,
                                            file_name=f"{job['company']}_{strategy_key}.txt",
                                            mime="text/plain",
                                            key=f"download_{idx}_{strategy_key}"
                                        )
                                
                                # Follow-up Sequence
                                st.markdown('<div class="section-header"><span class="section-icon">🔄</span><h2>Follow-up Campaign</h2></div>', unsafe_allow_html=True)
                                st.caption("*Automated sequence based on best-performing strategy*")
                                
                                with st.spinner("Generating follow-up sequence..."):
                                    followups = llm.generate_follow_up_sequence(
                                        best_email,
                                        job_data,
                                        job['company']
                                    )
                                
                                st.markdown('<div class="timeline-container"></div>', unsafe_allow_html=True)
                                
                                fcol1, fcol2, fcol3 = st.columns(3)
                                
                                for col, followup in zip([fcol1, fcol2, fcol3], followups):
                                    with col:
                                        day = followup.get('day', 0)
                                        st.markdown(f"""
                                        <div class="strategy-card">
                                            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">📅</div>
                                            <div style="font-weight: 700; color: #1e293b; margin-bottom: 0.5rem;">Day {day}</div>
                                            <div style="color: #64748b; font-size: 0.9rem;">{followup.get('subject', 'N/A')[:50]}...</div>
                                        </div>
                                        """, unsafe_allow_html=True)
                                        
                                        with st.expander("View Email"):
                                            st.code(followup.get('email', 'N/A'), language='markdown')
                                            
                                            st.download_button(
                                                label="📥 Download",
                                                data=followup.get('email', ''),
                                                file_name=f"{job['company']}_followup_day{day}.txt",
                                                mime="text/plain",
                                                key=f"followup_{idx}_{day}"
                                            )
                                
                            except Exception as e:
                                st.error(f"❌ Error processing {job['company']}: {str(e)}")
    
    # ========================================
    # MODE 2: DIRECT URL INPUT
    # ========================================
    else:
        
        with st.expander("ℹ️ How It Works", expanded=False):
            st.markdown("""
            <div class="feature-grid">
                <div class="feature-card">
                    <span class="feature-icon">🔍</span>
                    <div class="feature-title">Find Job</div>
                    <div class="feature-desc">Locate position on any platform</div>
                </div>
                <div class="feature-card">
                    <span class="feature-icon">📋</span>
                    <div class="feature-title">Copy URL</div>
                    <div class="feature-desc">Get the posting link</div>
                </div>
                <div class="feature-card">
                    <span class="feature-icon">⚡</span>
                    <div class="feature-title">Generate</div>
                    <div class="feature-desc">AI creates campaigns</div>
                </div>
                <div class="feature-card">
                    <span class="feature-icon">📧</span>
                    <div class="feature-title">Deploy</div>
                    <div class="feature-desc">Send & track results</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            url_input = st.text_input(
                "Job Posting URL",
                value="https://www.indeed.com/q-Java-Developer-jobs.html?vjk=037c41907400c83f",
                placeholder="https://company.com/careers/position"
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            generation_mode = st.selectbox(
                "Output Type",
                ["Quick Email", "Full Campaign"],
                help="Quick: Single email | Full: Complete package"
            )
        
        with st.expander("⚙️ Advanced Settings", expanded=False):
            override_tone = st.selectbox(
                "Communication Style",
                ["Auto-detect", "Formal", "Technical", "Creative", "Corporate", "Marketing"]
            )
        
        submit_button = st.button("✨ Generate Campaign", type="primary", use_container_width=True)
        
        if submit_button:
            if not url_input or not url_input.startswith("http"):
                st.error("⚠️ Please provide a valid URL")
            else:
                with st.spinner("🔄 Processing job posting..."):
                    try:
                        loader = WebBaseLoader([url_input])
                        data = clean_text(loader.load().pop().page_content)
                        
                        portfolio.load_portfolio()
                        job_data = llm.extract_jobs(data)
                        
                        if not job_data:
                            st.error("⚠️ Unable to extract job information")
                        else:
                            company_name = extract_company_name_from_url(url_input)
                            
                            # Detect tone
                            if override_tone == "Auto-detect":
                                detected_tone = llm.detect_style(data)
                            else:
                                detected_tone = override_tone.lower()
                            
                            tone_emoji = {
                                'formal': '🎩', 'technical': '💻', 'creative': '🎨',
                                'corporate': '🏢', 'marketing': '📢'
                            }
                            
                            st.markdown(f"""
                            <div style="text-align: center; margin: 1.5rem 0;">
                                <span class="tone-badge-modern tone-{detected_tone}">
                                    <span>{tone_emoji.get(detected_tone, '✨')}</span>
                                    <span>Style: {detected_tone.upper()}</span>
                                </span>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            skills = job_data.get('skills', [])
                            links = portfolio.query_links(str(skills))
                            
                            # QUICK MODE
                            if generation_mode == "Quick Email":
                                with st.spinner("✍️ Crafting email..."):
                                    email = llm.generate_cold_email(job_data, links, tone=detected_tone)
                                
                                st.markdown('<div class="section-header"><span class="section-icon">✉️</span><h2>Your Email</h2></div>', unsafe_allow_html=True)
                                st.code(email, language='markdown')
                                
                                st.download_button(
                                    label="📥 Download Email",
                                    data=email,
                                    file_name=f"cold_email_{detected_tone}.txt",
                                    mime="text/plain"
                                )
                            
                            # FULL CAMPAIGN MODE
                            else:
                                with st.spinner("🏢 Analyzing company..."):
                                    company_intel = llm.research_company(company_name, data)
                                
                                st.markdown(f"""
                                <div class="insight-box">
                                    <strong>🏢 Company Profile</strong>
                                    <div class="insight-item"><strong>Values:</strong> {', '.join(company_intel.get('key_values', [])[:3])}</div>
                                    <div class="insight-item"><strong>Focus:</strong> {company_intel.get('recent_focus', 'N/A')[:120]}...</div>
                                    <div class="insight-item"><strong>Culture:</strong> {', '.join(company_intel.get('culture_traits', [])[:3])}</div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                with st.spinner("✍️ Creating strategies..."):
                                    email_variations = llm.generate_email_variations(
                                        job_data, links, detected_tone, company_intel
                                    )
                                
                                st.markdown('<div class="section-header"><span class="section-icon">📧</span><h2>Email Strategies</h2></div>', unsafe_allow_html=True)
                                
                                tab1, tab2, tab3 = st.tabs(["💼 Value", "🔧 Solution", "📖 Story"])
                                
                                strategies = [
                                    ("value_proposition", tab1, "Value Proposition"),
                                    ("problem_solution", tab2, "Problem-Solution"),
                                    ("storytelling", tab3, "Storytelling")
                                ]
                                
                                best_email = None
                                best_score = 0
                                
                                for strategy_key, tab, title in strategies:
                                    with tab:
                                        email = email_variations[strategy_key]
                                        analysis = llm.analyze_email_effectiveness(email, job_data)
                                        score = analysis.get('success_score', 75)
                                        
                                        if score > best_score:
                                            best_score = score
                                            best_email = email
                                        
                                        score_class = "score-excellent" if score >= 80 else "score-good" if score >= 70 else "score-fair"
                                        
                                        st.markdown(f"""
                                        <div class="score-display">
                                            <div class="score-circle {score_class}">
                                                {score}
                                            </div>
                                            <div style="color: #64748b; font-weight: 600;">Predicted Success Rate</div>
                                        </div>
                                        """, unsafe_allow_html=True)
                                        
                                        metrics = analysis.get('key_metrics', {})
                                        col1, col2, col3, col4 = st.columns(4)
                                        
                                        with col1:
                                            st.metric("Relevance", f"{metrics.get('relevance', 0)}/25")
                                        with col2:
                                            st.metric("Clarity", f"{metrics.get('clarity', 0)}/25")
                                        with col3:
                                            st.metric("Personal", f"{metrics.get('personalization', 0)}/25")
                                        with col4:
                                            st.metric("CTA", f"{metrics.get('call_to_action', 0)}/25")
                                        
                                        st.markdown("**📧 Email Content:**")
                                        st.code(email, language='markdown')
                                        
                                        st.download_button(
                                            label=f"📥 Download",
                                            data=email,
                                            file_name=f"{strategy_key}.txt",
                                            mime="text/plain",
                                            key=f"dl_{strategy_key}"
                                        )
                                
                                # Follow-ups
                                st.markdown('<div class="section-header"><span class="section-icon">🔄</span><h2>Follow-up Sequence</h2></div>', unsafe_allow_html=True)
                                
                                followups = llm.generate_follow_up_sequence(best_email, job_data, company_name)
                                
                                st.markdown('<div class="timeline-container"></div>', unsafe_allow_html=True)
                                
                                for followup in followups:
                                    with st.expander(f"📅 Day {followup.get('day', 0)}: {followup.get('subject', 'N/A')[:60]}"):
                                        st.code(followup.get('email', ''), language='markdown')
                                        st.download_button(
                                            label="📥 Download",
                                            data=followup.get('email', ''),
                                            file_name=f"followup_day{followup.get('day', 0)}.txt",
                                            mime="text/plain",
                                            key=f"fup_{followup.get('day', 0)}"
                                        )
                            
                    except Exception as e:
                        import traceback
                        st.error(f"❌ Processing Error: {str(e)}")
                        with st.expander("Technical Details"):
                            st.code(traceback.format_exc())
    
    st.markdown("""
      <div class="footer-section">
🚀 <b>AI Cold Email Generator V3</b> | Powered by LangChain, Groq & ChromaDB<br>
🔗 <a href="https://github.com/Bou-Mery" target="_blank">GitHub</a> | ✉️ <a href="mailto:meryemboukhrais2.com">Contact</a><br>
© 2025 BOUKHRAIS Meryem | MIT License<br>
<span class="tip">💡 Tip: Use “Smart Discovery” to find relevant jobs automatically!</span>
</div>
"""
    , unsafe_allow_html=True)



if __name__ == "__main__":
    try:
        if "GROQ_API_KEY" not in st.secrets:
            st.error("❌ GROQ_API_KEY manquante. Configurez-la dans Streamlit Secrets.")
            st.stop()
        
        chain = Chain(groq_api_key=st.secrets["GROQ_API_KEY"])
        portfolio = Portfolio()
        
        create_streamlit_app(chain, portfolio, clean_text)
        
    except Exception as e:
        st.error(f"❌ Erreur de démarrage: {str(e)}")
    portfolio = Portfolio()
    
    st.set_page_config(
        layout="wide",
        page_title="AI Cold Email Generator V3",
        page_icon="🚀",
        initial_sidebar_state="collapsed"
    )
    
    create_streamlit_app(chain, portfolio, clean_text)
