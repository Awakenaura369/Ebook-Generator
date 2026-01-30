import streamlit as st
import requests
import json
from datetime import datetime
import re
import random

st.set_page_config(
    page_title="EbookMaster Ultra",
    page_icon="👑",
    layout="wide"
)

# CSS الخرافي
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Lora:wght@400;600&display=swap');
    
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 60px 40px;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 40px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
    }
    
    .cover-preview {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 80px 40px;
        border-radius: 15px;
        text-align: center;
        margin: 20px 0;
        box-shadow: 0 15px 50px rgba(0,0,0,0.3);
        font-family: 'Playfair Display', serif;
    }
    
    .chapter-card {
        background: white;
        border-left: 5px solid #667eea;
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: transform 0.3s;
    }
    
    .chapter-card:hover {
        transform: translateX(10px);
    }
    
    .stat-card {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .feature-box {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 12px;
        border: 2px solid #e0e0e0;
        margin: 10px 0;
    }
    
    .success-banner {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        margin: 20px 0;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    .quote-box {
        background: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 20px;
        margin: 20px 0;
        font-style: italic;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

class EbookMasterUltra:
    def __init__(self, groq_api_key):
        self.groq_api_key = groq_api_key
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.3-70b-versatile"
        
        # قاعدة بيانات النيشات
        self.niches = {
            '💼 Business': ['entrepreneurship', 'marketing', 'sales', 'leadership', 'finance'],
            '🎓 Education': ['learning', 'teaching', 'study skills', 'online courses', 'education'],
            '💪 Self-Help': ['motivation', 'productivity', 'habits', 'mindfulness', 'success'],
            '🤖 Technology': ['AI', 'programming', 'blockchain', 'cybersecurity', 'tech trends'],
            '❤️ Health': ['fitness', 'nutrition', 'mental health', 'wellness', 'medical'],
            '💰 Finance': ['investing', 'crypto', 'passive income', 'budgeting', 'wealth'],
            '🎨 Creative': ['writing', 'design', 'art', 'photography', 'music'],
            '🏠 Lifestyle': ['minimalism', 'travel', 'relationships', 'parenting', 'home'],
        }
    
    def call_ai(self, system_prompt, user_prompt, max_tokens=4000, temperature=0.7):
        """استدعاء AI مع معالجة الأخطاء"""
        try:
            response = requests.post(
                self.groq_url,
                headers={
                    "Authorization": f"Bearer {self.groq_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "max_tokens": max_tokens,
                    "temperature": temperature
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            return None
        except Exception as e:
            st.error(f"AI Error: {str(e)}")
            return None
    
    def analyze_topic(self, topic):
        """تحليل الموضوع واقتراحات"""
        
        prompt = f"""Analyze this book topic: "{topic}"

Provide analysis in JSON format:

{{
  "niche": "Primary category",
  "sub_niche": "Specific sub-category",
  "target_readers": ["Reader type 1", "Reader type 2", "Reader type 3"],
  "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
  "market_demand": "High/Medium/Low",
  "competition": "High/Medium/Low",
  "suggested_improvements": "Brief suggestion to make topic better",
  "estimated_pages": 150
}}

Return ONLY valid JSON."""

        result = self.call_ai(
            "You are a book market analyst expert.",
            prompt,
            max_tokens=800,
            temperature=0.6
        )
        
        if result:
            try:
                cleaned = result.strip()
                if cleaned.startswith('```json'):
                    cleaned = cleaned[7:]
                if cleaned.startswith('```'):
                    cleaned = cleaned[3:]
                if cleaned.endswith('```'):
                    cleaned = cleaned[:-3]
                return json.loads(cleaned.strip())
            except:
                return None
        return None
    
    def generate_book_titles(self, topic, num=5):
        """توليد عناوين جذابة"""
        
        prompt = f"""Generate {num} compelling book titles for: "{topic}"

Requirements:
- Attention-grabbing and professional
- Include power words
- Clear value proposition
- SEO-friendly
- Between 5-10 words

Return as JSON array:
{{"titles": ["Title 1", "Title 2", ...]}}

Return ONLY valid JSON."""

        result = self.call_ai(
            "You are a bestselling book title creator.",
            prompt,
            max_tokens=500
        )
        
        if result:
            try:
                cleaned = result.strip().replace('```json', '').replace('```', '').strip()
                data = json.loads(cleaned)
                return data.get('titles', [])
            except:
                return []
        return []
    
    def generate_advanced_outline(self, topic, title, num_chapters, audience, tone):
        """توليد هيكل متقدم مع تفاصيل"""
        
        prompt = f"""Create an advanced book outline for:

Title: {title}
Topic: {topic}
Audience: {audience}
Tone: {tone}
Chapters: {num_chapters}

Generate in JSON format:

{{
  "title": "{title}",
  "subtitle": "Compelling subtitle",
  "tagline": "One-line hook",
  "description": "3-4 sentence description",
  "target_readers": ["Type 1", "Type 2"],
  "key_benefits": ["Benefit 1", "Benefit 2", "Benefit 3"],
  "chapters": [
    {{
      "number": 1,
      "title": "Chapter Title",
      "summary": "Brief chapter summary (2 sentences)",
      "learning_objectives": ["Objective 1", "Objective 2"],
      "sections": [
        {{
          "title": "Section Title",
          "key_points": ["Point 1", "Point 2", "Point 3"],
          "examples": ["Example topic 1", "Example topic 2"]
        }}
      ],
      "actionable_takeaway": "One key action item"
    }}
  ],
  "bonus_content": ["Bonus 1", "Bonus 2"]
}}

Make it comprehensive and valuable. Each chapter needs 3-5 sections.

Return ONLY valid JSON."""

        result = self.call_ai(
            "You are a master book architect who creates bestselling book structures.",
            prompt,
            max_tokens=5000,
            temperature=0.8
        )
        
        if result:
            try:
                cleaned = result.strip()
                if cleaned.startswith('```json'):
                    cleaned = cleaned[7:]
                if cleaned.startswith('```'):
                    cleaned = cleaned[3:]
                if cleaned.endswith('```'):
                    cleaned = cleaned[:-3]
                return json.loads(cleaned.strip())
            except Exception as e:
                st.error(f"Parse error: {e}")
                return None
        return None
    
    def generate_chapter_with_examples(self, outline, chapter_num, tone, word_count):
        """توليد فصل مع أمثلة وقصص"""
        
        chapter = outline['chapters'][chapter_num - 1]
        book_title = outline['title']
        
        prompt = f"""Write Chapter {chapter_num} of "{book_title}":

Chapter: {chapter['title']}
Summary: {chapter['summary']}

Sections to cover:
{chr(10).join(f"- {s['title']}: {', '.join(s['key_points'])}" for s in chapter['sections'])}

Learning Objectives:
{chr(10).join(f"- {obj}" for obj in chapter['learning_objectives'])}

Requirements:
- Tone: {tone}
- Length: {word_count} words
- Include:
  * Real-world examples
  * Case studies or stories
  * Practical exercises
  * Quotes (create inspiring ones)
  * Actionable tips
  * Common mistakes to avoid
- Format: Markdown with ##, ###
- Make it engaging and valuable
- End with: Key Takeaways section

Write complete, ready-to-publish content."""

        return self.call_ai(
            "You are a bestselling author known for engaging, practical books that transform readers' lives.",
            prompt,
            max_tokens=5000,
            temperature=0.7
        )
    
    def generate_introduction_advanced(self, outline, tone):
        """مقدمة متقدمة مع hook قوي"""
        
        prompt = f"""Write a compelling introduction for "{outline['title']}".

Subtitle: {outline['subtitle']}
Tagline: {outline['tagline']}

Structure:
1. **The Hook** (2-3 paragraphs):
   - Start with a powerful story, statistic, or question
   - Make it impossible to stop reading

2. **The Problem** (2 paragraphs):
   - What problem does this book solve?
   - Why is it urgent?

3. **The Promise** (2-3 paragraphs):
   - What will readers achieve?
   - Key benefits: {', '.join(outline['key_benefits'])}

4. **The Journey** (2 paragraphs):
   - Brief overview of what's inside
   - What makes this book different

5. **The Author's Story** (2 paragraphs):
   - Why you wrote this (make it personal)
   - Your credentials/experience

6. **How to Read This Book** (1 paragraph):
   - Best way to get value

Length: 800-1000 words
Tone: {tone}
Format: Markdown

Make it IMPOSSIBLE to put down!"""

        return self.call_ai(
            "You are a master at writing book introductions that hook readers from the first sentence.",
            prompt,
            max_tokens=3000,
            temperature=0.8
        )
    
    def generate_conclusion_with_cta(self, outline, tone):
        """خاتمة مع call-to-action قوي"""
        
        prompt = f"""Write a powerful conclusion for "{outline['title']}".

Structure:
1. **The Transformation** (2 paragraphs):
   - What has the reader learned?
   - How are they different now?

2. **Key Takeaways** (bullet points):
   - 5-7 main lessons from the book

3. **The Challenge** (2 paragraphs):
   - Inspire immediate action
   - What's the first step?

4. **The Vision** (2 paragraphs):
   - Paint a picture of their future success
   - Make them excited

5. **The Call to Action**:
   - Specific next steps
   - How to continue the journey

6. **Final Words** (1 paragraph):
   - Memorable closing statement
   - Leave them inspired

Length: 600-800 words
Tone: {tone}, inspiring, actionable
Format: Markdown

Make them want to START IMMEDIATELY!"""

        return self.call_ai(
            "You are skilled at writing conclusions that inspire massive action.",
            prompt,
            max_tokens=2500,
            temperature=0.8
        )
    
    def generate_bonus_chapter(self, outline, bonus_topic):
        """فصل إضافي بونص"""
        
        prompt = f"""Write a BONUS chapter for "{outline['title']}":

Topic: {bonus_topic}

This is exclusive bonus content that adds extra value!

Requirements:
- Length: 1000-1200 words
- Highly practical
- Include:
  * Checklists
  * Templates
  * Resources
  * Advanced tips
- Format: Markdown
- Make it feel like a special gift

Write complete bonus chapter."""

        return self.call_ai(
            "You are an expert at creating high-value bonus content.",
            prompt,
            max_tokens=3500
        )
    
    def generate_seo_keywords(self, topic):
        """توليد كلمات مفتاحية SEO"""
        
        prompt = f"""Generate SEO keywords for a book about: "{topic}"

Provide:
{{
  "primary_keywords": ["keyword1", "keyword2", "keyword3"],
  "long_tail_keywords": ["long tail 1", "long tail 2", "long tail 3"],
  "trending_keywords": ["trending1", "trending2"],
  "amazon_keywords": ["amz keyword1", "amz keyword2", "amz keyword3"]
}}

Return ONLY valid JSON."""

        result = self.call_ai(
            "You are an SEO expert specializing in book marketing.",
            prompt,
            max_tokens=500
        )
        
        if result:
            try:
                cleaned = result.strip().replace('```json', '').replace('```', '').strip()
                return json.loads(cleaned)
            except:
                return None
        return None

def create_premium_html(outline, content, author, cover_style="gradient1"):
    """HTML premium مع تصميم خرافي"""
    
    cover_gradients = {
        "gradient1": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "gradient2": "linear-gradient(135deg, #f093fb 0%, #f5576c 100%)",
        "gradient3": "linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)",
        "gradient4": "linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)",
        "gradient5": "linear-gradient(135deg, #fa709a 0%, #fee140 100%)",
    }
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{outline['title']}</title>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Lora:wght@400;600;700&family=Inter:wght@400;600&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Lora', serif;
            line-height: 1.9;
            color: #2c3e50;
            font-size: 18px;
            background: #fff;
        }}
        
        .page {{
            max-width: 800px;
            margin: 0 auto;
            padding: 60px 40px;
            min-height: 100vh;
        }}
        
        /* Cover Page */
        .cover {{
            background: {cover_gradients.get(cover_style, cover_gradients['gradient1'])};
            color: white;
            padding: 120px 60px;
            text-align: center;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            page-break-after: always;
            position: relative;
            overflow: hidden;
        }}
        
        .cover::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg"><rect width="100" height="100" fill="rgba(255,255,255,0.05)"/></svg>');
            opacity: 0.1;
        }}
        
        .cover-content {{
            position: relative;
            z-index: 1;
        }}
        
        .cover h1 {{
            font-family: 'Playfair Display', serif;
            font-size: 4.5rem;
            font-weight: 900;
            margin-bottom: 30px;
            line-height: 1.2;
            text-shadow: 2px 4px 8px rgba(0,0,0,0.3);
            letter-spacing: -2px;
        }}
        
        .cover h2 {{
            font-family: 'Inter', sans-serif;
            font-size: 1.8rem;
            font-weight: 400;
            margin-bottom: 60px;
            opacity: 0.95;
            letter-spacing: 1px;
        }}
        
        .cover .tagline {{
            font-size: 1.3rem;
            font-style: italic;
            margin-bottom: 80px;
            opacity: 0.9;
        }}
        
        .cover .author {{
            font-size: 2rem;
            margin-top: 60px;
            font-weight: 600;
            letter-spacing: 2px;
        }}
        
        .cover .year {{
            margin-top: 40px;
            font-size: 1.2rem;
            opacity: 0.8;
        }}
        
        /* Copyright Page */
        .copyright {{
            page-break-after: always;
            padding: 100px 60px;
            font-size: 0.95rem;
            line-height: 2;
        }}
        
        /* Table of Contents */
        .toc {{
            page-break-after: always;
            padding: 60px 40px;
        }}
        
        .toc h2 {{
            font-family: 'Playfair Display', serif;
            font-size: 3rem;
            color: #667eea;
            margin-bottom: 50px;
            border-bottom: 4px solid #667eea;
            padding-bottom: 20px;
        }}
        
        .toc ul {{
            list-style: none;
        }}
        
        .toc li {{
            padding: 18px 0;
            border-bottom: 1px solid #ecf0f1;
            font-size: 1.1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .toc li:hover {{
            background: #f8f9fa;
            padding-left: 15px;
            transition: all 0.3s;
        }}
        
        .toc .chapter-num {{
            color: #667eea;
            font-weight: 600;
            margin-right: 15px;
        }}
        
        /* Content */
        .content {{
            padding: 40px 60px;
        }}
        
        h1 {{
            font-family: 'Playfair Display', serif;
            font-size: 3rem;
            color: #2c3e50;
            margin: 80px 0 40px 0;
            page-break-before: always;
            border-bottom: 4px solid #667eea;
            padding-bottom: 20px;
        }}
        
        h2 {{
            font-family: 'Playfair Display', serif;
            font-size: 2.2rem;
            color: #34495e;
            margin: 60px 0 30px 0;
            page-break-after: avoid;
        }}
        
        h3 {{
            font-family: 'Inter', sans-serif;
            font-size: 1.6rem;
            color: #555;
            margin: 40px 0 20px 0;
        }}
        
        p {{
            margin-bottom: 25px;
            text-align: justify;
            text-indent: 30px;
        }}
        
        p:first-of-type {{
            text-indent: 0;
        }}
        
        p:first-of-type::first-letter {{
            font-size: 4rem;
            font-weight: bold;
            float: left;
            line-height: 0.9;
            margin: 10px 10px 0 0;
            color: #667eea;
            font-family: 'Playfair Display', serif;
        }}
        
        ul, ol {{
            margin: 30px 0 30px 40px;
            line-height: 2;
        }}
        
        li {{
            margin-bottom: 15px;
        }}
        
        blockquote {{
            border-left: 5px solid #667eea;
            background: #f8f9fa;
            padding: 30px 40px;
            margin: 40px 0;
            font-style: italic;
            font-size: 1.2rem;
            color: #555;
            border-radius: 5px;
        }}
        
        .key-takeaways {{
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            padding: 40px;
            border-radius: 15px;
            margin: 50px 0;
            border-left: 5px solid #2196f3;
        }}
        
        .key-takeaways h3 {{
            color: #1976d2;
            margin-top: 0;
        }}
        
        .bonus-box {{
            background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
            padding: 40px;
            border-radius: 15px;
            margin: 50px 0;
            border: 3px dashed #ff9800;
        }}
        
        .exercise-box {{
            background: #f1f8e9;
            padding: 30px;
            border-radius: 10px;
            margin: 30px 0;
            border-left: 5px solid #8bc34a;
        }}
        
        code {{
            background: #f4f4f4;
            padding: 3px 8px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
        }}
        
        .footer {{
            margin-top: 100px;
            padding-top: 40px;
            border-top: 2px solid #ecf0f1;
            text-align: center;
            color: #95a5a6;
            font-size: 0.9rem;
        }}
        
        @media print {{
            body {{
                font-size: 12pt;
            }}
            .cover, .toc, h1 {{
                page-break-after: always;
            }}
            h2, h3 {{
                page-break-after: avoid;
            }}
        }}
    </style>
</head>
<body>
    <!-- Cover -->
    <div class="cover">
        <div class="cover-content">
            <h1>{outline['title']}</h1>
            <h2>{outline['subtitle']}</h2>
            <p class="tagline">"{outline.get('tagline', '')}"</p>
            <p class="author">by {author}</p>
            <p class="year">{datetime.now().year}</p>
        </div>
    </div>
    
    <!-- Copyright -->
    <div class="copyright">
        <h2>Copyright © {datetime.now().year} by {author}</h2>
        <p style="margin-top: 40px;">
            All rights reserved. No part of this publication may be reproduced, 
            distributed, or transmitted in any form or by any means, including 
            photocopying, recording, or other electronic or mechanical methods, 
            without the prior written permission of the publisher.
        </p>
        <p style="margin-top: 30px;">
            <strong>Published by:</strong> {author}<br>
            <strong>First Edition:</strong> {datetime.now().strftime('%B %Y')}<br>
            <strong>Generated with:</strong> EbookMaster Ultra
        </p>
    </div>
    
    <!-- TOC -->
    <div class="toc">
        <h2>📚 Table of Contents</h2>
        <ul>
            <li><span class="chapter-num">•</span> <span>Introduction</span></li>
            {''.join(f'<li><span class="chapter-num">Chapter {i+1}</span> <span>{chapter["title"]}</span></li>' for i, chapter in enumerate(outline['chapters']))}
            <li><span class="chapter-num">•</span> <span>Conclusion</span></li>
            {f'<li><span class="chapter-num">🎁</span> <span>Bonus Content</span></li>' if outline.get('bonus_content') else ''}
        </ul>
    </div>
    
    <!-- Content -->
    <div class="content">
        {content}
    </div>
    
    <div class="footer">
        <p><strong>{outline['title']}</strong></p>
        <p>by {author}</p>
        <p style="margin-top: 20px;">Generated with EbookMaster Ultra | {datetime.now().strftime('%B %Y')}</p>
        <p>© {datetime.now().year} All Rights Reserved</p>
    </div>
</body>
</html>"""
    
    return html

def main():
    # Hero Section
    st.markdown("""
        <div class="hero-section">
            <h1 style="font-size: 4rem; margin-bottom: 20px; text-shadow: 2px 2px 8px rgba(0,0,0,0.3);">
                👑 EbookMaster Ultra
            </h1>
            <p style="font-size: 1.5rem; margin-bottom: 15px;">
                The Most Advanced AI Book Generator on Earth
            </p>
            <p style="font-size: 1.1rem; opacity: 0.9;">
                Generate Professional, Bestseller-Quality Books in Minutes
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Features Showcase
    with st.expander("🚀 Ultimate Features (Better Than ANY Tool!)", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="feature-box">
                <h3>🤖 AI-Powered</h3>
                <ul>
                    <li>Llama 3.3 70B</li>
                    <li>Advanced Prompts</li>
                    <li>Context-Aware</li>
                    <li>Natural Writing</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="feature-box">
                <h3>📚 Complete Books</h3>
                <ul>
                    <li>Smart Outline</li>
                    <li>Introduction</li>
                    <li>15+ Chapters</li>
                    <li>Conclusion</li>
                    <li>Bonus Content</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            **💾 Export Options:**
            - Premium HTML
            - PDF Ready
            - Markdown
            - Plain Text
            """)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        groq_key = st.text_input(
            "🤖 Groq API Key",
            type="password"
        )
        
        st.divider()
        
        author = st.text_input("✍️ Author", "AI Author")
        audience = st.selectbox("👥 Audience", ["Beginners", "Everyone", "Professionals"])
        tone = st.selectbox("🎭 Tone", ["Professional", "Conversational", "Motivational"])
        
        st.divider()
        
        num_chapters = st.slider("📑 Chapters", 3, 15, 8)
        word_count = st.slider("📏 Words/Chapter", 1000, 3000, 1500, 100)
        include_bonus = st.checkbox("🎁 Bonus Chapter", True)
        
        st.divider()
        
        cover_style = st.selectbox(
            "🎨 Cover",
            ["gradient1", "gradient2", "gradient3", "gradient4", "gradient5"]
        )
    
    # Main Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Create", "📖 Preview", "💾 Export", "🎯 SEO"])
    
    with tab1:
        st.subheader("📚 What's Your Book About?")
        
        topic = st.text_area(
            "Book Topic",
            placeholder="E.g., The Ultimate Guide to Digital Marketing in 2026",
            height=100,
            label_visibility="collapsed"
        )
        
        # Quick Examples
        col1, col2, col3, col4 = st.columns(4)
        
        examples = {
            "💼 Business": "Complete Guide to Starting a Successful Online Business",
            "🤖 AI/Tech": "Artificial Intelligence: Practical Guide for Beginners",
            "💪 Self-Help": "Transform Your Life: The Power of Daily Habits",
            "💰 Finance": "Financial Freedom: Invest Smart and Build Wealth"
        }
        
        for i, (col, (label, example)) in enumerate(zip([col1, col2, col3, col4], examples.items())):
            with col:
                if st.button(label, use_container_width=True, key=f"ex_{i}"):
                    st.session_state.topic_input = example
                    st.rerun()
        
        if 'topic_input' in st.session_state:
            topic = st.session_state.topic_input
        
        st.divider()
        
        # Generate Button
        col1, col2 = st.columns([4, 1])
        
        with col1:
            generate_btn = st.button(
                "🚀 Generate Complete Book",
                type="primary",
                use_container_width=True,
                disabled=not groq_key or not topic or not author
            )
        
        with col2:
            if 'book_data' in st.session_state:
                if st.button("🔄 New", use_container_width=True):
                    for key in ['book_data', 'outline', 'chapters', 'topic_input']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()
        
        # Generation Process
        if generate_btn:
            master = EbookMasterUltra(groq_key)
            
            progress = st.progress(0)
            status = st.empty()
            
            # Step 1: Analyze
            status.info("🧠 Analyzing topic...")
            analysis = master.analyze_topic(topic)
            progress.progress(5)
            
            if analysis:
                st.success(f"✅ Niche: {analysis.get('niche', 'General')}")
            
            # Step 2: Generate Titles
            status.info("📝 Creating titles...")
            titles = master.generate_book_titles(topic, 5)
            progress.progress(10)
            
            if titles:
                selected_title = st.selectbox("Choose Best Title:", titles, key="title_select")
            else:
                selected_title = topic
            
            # Step 3: Outline
            status.info("📋 Building outline...")
            outline = master.generate_advanced_outline(
                topic, selected_title, num_chapters, audience, tone
            )
            progress.progress(20)
            
            if outline:
                st.session_state.outline = outline
                st.success(f"✅ Outline: {outline['title']}")
                
                with st.expander("👀 View Outline"):
                    st.markdown(f"**{outline['title']}**")
                    st.caption(outline['subtitle'])
                    for i, ch in enumerate(outline['chapters'], 1):
                        st.markdown(f"{i}. {ch['title']}")
                
                # Step 4: Introduction
                status.info("✍️ Writing introduction...")
                intro = master.generate_introduction_advanced(outline, tone)
                progress.progress(25)
                
                if intro:
                    st.session_state.introduction = intro
                    st.success("✅ Introduction done!")
                
                # Step 5: Chapters
                chapters_content = []
                
                for i in range(1, num_chapters + 1):
                    prog = 25 + (i / num_chapters * 60)
                    progress.progress(int(prog))
                    status.info(f"✍️ Chapter {i}/{num_chapters}: {outline['chapters'][i-1]['title']}")
                    
                    chapter = master.generate_chapter_with_examples(
                        outline, i, tone, word_count
                    )
                    
                    if chapter:
                        chapters_content.append(chapter)
                        st.success(f"✅ Chapter {i}")
                
                st.session_state.chapters = chapters_content
                
                # Step 6: Conclusion
                status.info("🎯 Writing conclusion...")
                progress.progress(90)
                
                conclusion = master.generate_conclusion_with_cta(outline, tone)
                if conclusion:
                    st.session_state.conclusion = conclusion
                    st.success("✅ Conclusion!")
                
                # Step 7: Bonus
                if include_bonus and outline.get('bonus_content'):
                    status.info("🎁 Creating bonus...")
                    progress.progress(95)
                    
                    bonus = master.generate_bonus_chapter(
                        outline, 
                        outline['bonus_content'][0]
                    )
                    if bonus:
                        st.session_state.bonus = bonus
                
                progress.progress(100)
                
                # Save data
                st.session_state.book_data = {
                    'outline': outline,
                    'author': author,
                    'cover_style': cover_style
                }
                
                # Success!
                st.markdown("""
                    <div class="success-banner">
                        🎉 Book Complete! Ready to Preview & Download!
                    </div>
                """, unsafe_allow_html=True)
                
                # Stats
                total_words = sum(len(c.split()) for c in chapters_content)
                if intro:
                    total_words += len(intro.split())
                if conclusion:
                    total_words += len(conclusion.split())
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📑 Chapters", num_chapters)
                with col2:
                    st.metric("📝 Words", f"{total_words:,}")
                with col3:
                    st.metric("📄 Pages", f"~{int(total_words/250)}")
                with col4:
                    st.metric("⏱️ Read Time", f"{int(total_words/200)}min")
            
            else:
                st.error("❌ Failed! Check API key.")
    
    with tab2:
        if 'outline' in st.session_state:
            outline = st.session_state.outline
            
            # Cover Preview
            st.markdown(f"""
                <div class="cover-preview">
                    <h1>{outline['title']}</h1>
                    <h2>{outline['subtitle']}</h2>
                    <p style="font-style: italic; margin: 20px 0;">"{outline.get('tagline', '')}"</p>
                    <p style="font-size: 1.3rem; margin-top: 40px;">by {author}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Content Preview
            if 'introduction' in st.session_state:
                st.markdown("## 📖 Introduction")
                st.markdown(st.session_state.introduction)
            
            if 'chapters' in st.session_state:
                for i, content in enumerate(st.session_state.chapters, 1):
                    with st.expander(f"📑 Chapter {i}: {outline['chapters'][i-1]['title']}"):
                        st.markdown(content)
            
            if 'conclusion' in st.session_state:
                st.markdown("## 🎯 Conclusion")
                st.markdown(st.session_state.conclusion)
            
            if 'bonus' in st.session_state:
                st.markdown("## 🎁 Bonus Chapter")
                st.markdown(st.session_state.bonus)
        
        else:
            st.info("📝 Generate a book first!")
    
    with tab3:
        if 'book_data' in st.session_state:
            st.subheader("💾 Download Your Book")
            
            # Compile content
            full_content = ""
            
            if 'introduction' in st.session_state:
                full_content += f"# Introduction\n\n{st.session_state.introduction}\n\n"
            
            for i, ch in enumerate(st.session_state.chapters, 1):
                full_content += f"{ch}\n\n"
            
            if 'conclusion' in st.session_state:
                full_content += f"# Conclusion\n\n{st.session_state.conclusion}\n\n"
            
            if 'bonus' in st.session_state:
                full_content += f"# 🎁 Bonus Chapter\n\n{st.session_state.bonus}\n\n"
            
            # HTML
            html = create_premium_html(
                st.session_state.outline,
                full_content.replace('\n', '<br>'),
                author,
                cover_style
            )
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.download_button(
                    "📄 Premium HTML",
                    html,
                    f"{st.session_state.outline['title'].replace(' ', '_')}.html",
                    mime="text/html",
                    use_container_width=True
                )
            
            with col2:
                md = f"# {st.session_state.outline['title']}\n\n{full_content}"
                st.download_button(
                    "📝 Markdown",
                    md,
                    f"{st.session_state.outline['title'].replace(' ', '_')}.md",
                    use_container_width=True
                )
            
            with col3:
                txt = f"{st.session_state.outline['title']}\n{'='*50}\n\n{full_content}"
                st.download_button(
                    "📋 Plain Text",
                    txt,
                    f"{st.session_state.outline['title'].replace(' ', '_')}.txt",
                    use_container_width=True
                )
            
            st.divider()
            
            st.info("""
            ### 📖 How to Create PDF:
            1. Download HTML file
            2. Open in Chrome/Edge
            3. Press Ctrl+P (Print)
            4. Select "Save as PDF"
            5. Done! ✅
            
            ### 📚 Create EPUB:
            - Use [Calibre](https://calibre-ebook.com) (Free)
            - Import HTML → Convert to EPUB
            """)
        
        else:
            st.info("📝 Generate a book first!")
    
    with tab4:
        if 'book_data' in st.session_state:
            st.subheader("🎯 SEO & Marketing")
            
            master = EbookMasterUltra(groq_key)
            
            if st.button("🔍 Generate SEO Keywords"):
                with st.spinner("Analyzing..."):
                    keywords = master.generate_seo_keywords(topic)
                
                if keywords:
                    st.success("✅ Keywords Generated!")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### 🎯 Primary Keywords")
                        for kw in keywords.get('primary_keywords', []):
                            st.code(kw)
                        
                        st.markdown("### 📈 Trending")
                        for kw in keywords.get('trending_keywords', []):
                            st.code(kw)
                    
                    with col2:
                        st.markdown("### 🔍 Long-Tail")
                        for kw in keywords.get('long_tail_keywords', []):
                            st.code(kw)
                        
                        st.markdown("### 🛒 Amazon Keywords")
                        for kw in keywords.get('amazon_keywords', []):
                            st.code(kw)
        else:
            st.info("📝 Generate a book first!")
    
    # Footer
    st.divider()
    st.markdown("""
        <div style='text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white;'>
            <h3>👑 EbookMaster Ultra</h3>
            <p>The Most Powerful AI Book Generator</p>
            <p style='font-size: 0.9rem; opacity: 0.8;'>Generate Professional Books • Powered by Llama 3.3 70B</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
            <div class="feature-box">
                <h3>🎨 Premium Design</h3>
                <ul>
                    <li>5 Cover Styles</li>
                    <li>Professional Layout</li>
                    <li>Print-Ready PDF</li>
                    <li>EPUB Ready</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **📊 Advanced Features:**
            - Topic Analysis
            - SEO Keywords
            - Market Research
            - Title Generator
            - Competition Analysis
            """)
        
        with col2:
            st.markdown("""
            **✨ Content Quality:**
            - Real Examples
            - Case Studies
            - Actionable Tips
            - Exercises
            - Key Takeaways
            """)
        
        with col3:
            st.markdown
