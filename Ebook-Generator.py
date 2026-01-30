import streamlit as st
import requests
import json
from datetime import datetime, timedelta
import re
import sqlite3
import pickle
import time
import hashlib
from functools import lru_cache
import os
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt
from fpdf import FPDF
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import ebooklib
from ebooklib import epub
from PIL import Image
from bs4 import BeautifulSoup
import lxml
from dotenv import load_dotenv
import openai
import boto3
import stripe
import tweepy
import io
import base64

# تحميل متغيرات البيئة
load_dotenv()

st.set_page_config(
    page_title="📚 EbookMaster Ultra Pro",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== DATABASE ENHANCEMENT ==========
try:
    import pysqlite3
    import sys
    sys.modules['sqlite3'] = pysqlite3
except ImportError:
    pass

import atexit

def cleanup_database():
    """Cleanup database connections on exit"""
    pass

atexit.register(cleanup_database)

# ========== ENHANCED AI MODELS ==========
class AIPowerhouse:
    def __init__(self, groq_api_key):
        self.groq_api_key = groq_api_key
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        
        # Premium AI Models for Maximum Quality
        self.models = {
            "llama3_70b": "llama-3.3-70b-versatile",
            "llama3_8b": "llama-3.1-8b-instant",
            "mixtral": "mixtral-8x7b-32768",
            "gemma2": "gemma2-9b-it"
        }
        
        # Style configurations
        self.writing_styles = {
            "bestseller": "Write like a New York Times bestselling author",
            "professional": "Write like an industry expert with 20+ years experience",
            "conversational": "Write like a friend giving advice over coffee",
            "academic": "Write with academic rigor and citations",
            "persuasive": "Write to convince and convert readers",
            "storytelling": "Write with compelling narrative and characters"
        }
        
        # Book genres for better targeting
        self.genres = {
            "self_help": "Self-Help & Personal Development",
            "business": "Business & Entrepreneurship",
            "health": "Health & Wellness",
            "finance": "Finance & Investing",
            "technology": "Technology & AI",
            "fiction": "Fiction & Storytelling",
            "education": "Educational & How-To"
        }
        
        # Initialize OpenAI if key available
        self.openai_client = None
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            self.openai_client = openai.OpenAI(api_key=openai_key)
    
    def select_model_for_task(self, task, genre, target_audience):
        """Intelligently select the best AI model for each task"""
        if "outline" in task or "structure" in task:
            return self.models["llama3_70b"]
        elif "creative" in genre or "fiction" in genre:
            return self.models["mixtral"]
        elif "technical" in genre or "academic" in genre:
            return self.models["llama3_70b"]
        else:
            return self.models["gemma2"]
    
    def call_ai(self, system_prompt, user_prompt, model_name, max_tokens=6000, temperature=0.75, retries=3):
        """استدعاء AI مع retry logic محسّن"""
        
        for attempt in range(retries):
            try:
                # تأكد من صحة البيانات
                if not self.groq_api_key or not self.groq_api_key.strip():
                    return "Error: API key is missing"
                
                # تنظيف النصوص
                system_prompt = str(system_prompt).strip()
                user_prompt = str(user_prompt).strip()
                
                if not system_prompt or not user_prompt:
                    return "Error: Prompts cannot be empty"
                
                # إعداد الـ payload
                payload = {
                    "model": model_name,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "top_p": 0.9,
                    "frequency_penalty": 0.1,
                    "presence_penalty": 0.1
                }
                
                # الاتصال بالـ API
                response = requests.post(
                    self.groq_url,
                    headers={
                        "Authorization": f"Bearer {self.groq_api_key}",
                        "Content-Type": "application/json"
                    },
                    json=payload,
                    timeout=120
                )
                
                # معالجة النتيجة
                if response.status_code == 200:
                    result = response.json()
                    if 'choices' in result and len(result['choices']) > 0:
                        content = result['choices'][0]['message']['content']
                        return content
                    else:
                        return f"Error: Invalid response format"
                
                elif response.status_code == 400:
                    error_detail = response.json() if response.text else {}
                    error_msg = error_detail.get('error', {}).get('message', 'Bad Request')
                    
                    # إذا كان الخطأ متعلق بالـ tokens، قلل العدد
                    if 'token' in error_msg.lower() or 'length' in error_msg.lower():
                        if max_tokens > 2000:
                            max_tokens = max_tokens // 2
                            continue
                    
                    return f"API Error 400: {error_msg}"
                
                elif response.status_code == 429:
                    # Rate limit - انتظر وحاول مرة أخرى
                    wait_time = (attempt + 1) * 2
                    time.sleep(wait_time)
                    continue
                
                elif response.status_code == 401:
                    return "Error: Invalid API Key"
                
                else:
                    return f"API Error {response.status_code}: {response.text[:200]}"
                    
            except requests.exceptions.Timeout:
                if attempt < retries - 1:
                    time.sleep(2)
                    continue
                return "Error: Request timeout. Please try again."
            
            except requests.exceptions.ConnectionError:
                if attempt < retries - 1:
                    time.sleep(2)
                    continue
                return "Error: Connection failed. Check your internet."
            
            except Exception as e:
                return f"Error: {str(e)[:200]}"
        
        return "Error: Maximum retries exceeded"
    
    def call_openai(self, system_prompt, user_prompt, model="gpt-4", max_tokens=4000):
        """Use OpenAI as fallback if available"""
        if not self.openai_client:
            return None
        
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"OpenAI Error: {str(e)}"
    
    def generate_outline(self, topic, chapters, genre, style, target_audience):
        """Generate a professional book outline"""
        
        model = self.select_model_for_task("outline", genre, target_audience)
        
        system_prompt = f"""You are a professional book architect with 20+ years in publishing.
Create compelling, market-ready book outlines that sell.

Current market trends to consider:
- Bestselling books have emotional hooks
- Readers want actionable steps
- Storytelling beats dry facts
- Problem → Solution → Transformation structure works best"""
        
        user_prompt = f"""Create a bestselling book outline:

BOOK TOPIC: {topic}
GENRE: {genre}
TARGET AUDIENCE: {target_audience}
WRITING STYLE: {style}
CHAPTERS: {chapters}

Requirements for success:
1. Create a CATCHY TITLE that makes people want to click
2. Add a compelling SUBTITLE that explains the benefit
3. Each chapter must have:
   - A provocative title
   - A 1-sentence hook
   - 3-5 key points covered
   - A transformation promise

Return ONLY valid JSON with this structure:
{{
    "title": "Catchy Main Title",
    "subtitle": "Compelling Subtitle That Shows Benefit",
    "genre": "{genre}",
    "target_audience": "{target_audience}",
    "marketing_hook": "One sentence that sells this book",
    "chapters": [
        {{
            "number": 1,
            "title": "Chapter Title That Creates Curiosity",
            "hook": "Why this chapter matters",
            "key_points": ["Point 1", "Point 2", "Point 3"],
            "transformation": "What reader gains"
        }}
    ],
    "estimated_pages": 250,
    "bestseller_potential": "High/Medium/Low"
}}"""
        
        result = self.call_ai(system_prompt, user_prompt, model, 4000, 0.7)
        
        # Fallback to OpenAI if Groq fails
        if result and result.startswith("Error"):
            result = self.call_openai(system_prompt, user_prompt)
        
        if result and not result.startswith("Error"):
            try:
                # Clean JSON extraction
                if '```json' in result:
                    result = result.split('```json')[1].split('```')[0].strip()
                elif '```' in result:
                    parts = result.split('```')
                    result = parts[1].strip() if len(parts) > 2 else result
                
                outline = json.loads(result)
                outline['generated_at'] = datetime.now().isoformat()
                outline['ai_model'] = model
                
                return outline
            except json.JSONDecodeError as e:
                st.warning(f"JSON parsing error: {str(e)}")
                # Create fallback outline
                return self.create_fallback_outline(topic, chapters, genre)
        
        return self.create_fallback_outline(topic, chapters, genre)
    
    def create_fallback_outline(self, topic, chapters, genre):
        """Create a professional fallback outline"""
        
        chapter_templates = {
            "self_help": [
                "The Awakening: Recognizing the Need for Change",
                "Breaking Free: Overcoming Limiting Beliefs",
                "The New Blueprint: Designing Your Ideal Life",
                "Daily Rituals: Building Unshakeable Habits",
                "Mindset Mastery: Thinking Like a Champion",
                "Relationships 2.0: Building Meaningful Connections",
                "Financial Freedom: Creating Abundance",
                "Health Revolution: Energizing Your Body",
                "Purpose Discovery: Finding Your Why",
                "Legacy Building: Making Your Mark"
            ],
            "business": [
                "Vision to Reality: The Entrepreneur's Mindset",
                "Market Domination: Finding Your Niche",
                "Product Perfection: Creating What Sells",
                "Marketing Machine: Attracting Customers Automatically",
                "Sales Funnels: Converting Leads to Clients",
                "Team Building: Scaling with the Right People",
                "Systems & Automation: Working Less, Earning More",
                "Funding Strategies: Getting Capital to Grow",
                "Digital Transformation: Leveraging Technology",
                "Exit Strategy: Building to Sell or Scale"
            ],
            "finance": [
                "Wealth Mindset: Thinking Like the Rich",
                "Debt Destruction: Breaking Free Forever",
                "Income Streams: Multiple Sources of Cash Flow",
                "Investing 101: Making Money Work for You",
                "Real Estate Riches: Property Investment Strategies",
                "Stock Market Mastery: Beating the Averages",
                "Cryptocurrency: The Future of Money",
                "Tax Optimization: Keeping More of What You Earn",
                "Retirement Planning: Financial Freedom Timeline",
                "Legacy & Giving: Wealth with Purpose"
            ]
        }
        
        # Get appropriate chapters for genre
        template = chapter_templates.get(genre, chapter_templates["self_help"])
        actual_chapters = min(chapters, len(template))
        
        return {
            "title": f"The Complete Guide to {topic}",
            "subtitle": f"How to Master {topic} and Transform Your Life",
            "genre": genre,
            "target_audience": "Ambitious professionals seeking transformation",
            "marketing_hook": f"Discover the secrets to mastering {topic} that they don't teach in school",
            "chapters": [
                {
                    "number": i + 1,
                    "title": template[i],
                    "hook": f"Learn the essential principles of {topic} that 95% of people miss",
                    "key_points": [
                        "The fundamental mistake most people make",
                        "3 proven strategies that work",
                        "How to implement immediately"
                    ],
                    "transformation": f"Master {topic} and achieve remarkable results"
                }
                for i in range(actual_chapters)
            ],
            "estimated_pages": chapters * 25,
            "bestseller_potential": "High",
            "is_fallback": True,
            "generated_at": datetime.now().isoformat()
        }
    
    def generate_chapter(self, book_info, chapter_info, word_count, style):
        """Generate a compelling book chapter - محسّن"""
        
        try:
            # التحقق من البيانات
            if not isinstance(book_info, dict) or not isinstance(chapter_info, dict):
                return self.generate_fallback_chapter(chapter_info, word_count)
            
            model = self.select_model_for_task("chapter", book_info.get('genre', ''), book_info.get('target_audience', ''))
            
            # تبسيط الـ prompts لتجنب أخطاء الـ tokens
            system_prompt = f"""You are a professional {style} writer creating bestselling content.

Write engaging, actionable chapters that transform readers.

Key principles:
1. Start with a hook (story/statistic)
2. Short paragraphs and sentences
3. Include actionable steps
4. Add real examples
5. End with motivation"""
            
            # تقليل طول الـ user prompt
            user_prompt = f"""Write Chapter {chapter_info.get('number', 1)}: {chapter_info.get('title', 'Untitled')}

BOOK: {book_info.get('title', 'Untitled Book')}
GENRE: {book_info.get('genre', 'General')}
TARGET: {book_info.get('target_audience', 'General readers')}

WORD COUNT: {word_count} words
STYLE: {style}

Structure:
1. HOOK: Start with engaging story/question
2. MAIN CONTENT: Explain key concepts
3. ACTION STEPS: 3-5 practical steps
4. EXAMPLE: Real-world case study
5. SUMMARY: Key takeaways
6. EXERCISE: Practical task

Use Markdown:
- ## for sections
- **bold** for emphasis
- Lists for steps

Write now:"""
            
            # استدعاء API مع max_tokens معقول
            result = self.call_ai(system_prompt, user_prompt, model, max_tokens=min(word_count * 2, 6000), temperature=0.75)
            
            # إذا فشل، استخدم fallback
            if result and result.startswith("Error"):
                st.warning(f"AI generation failed: {result}. Using fallback content.")
                return self.generate_fallback_chapter(chapter_info, word_count)
            
            return result if result else self.generate_fallback_chapter(chapter_info, word_count)
            
        except Exception as e:
            st.error(f"Chapter generation error: {str(e)}")
            return self.generate_fallback_chapter(chapter_info, word_count)
    
    def generate_fallback_chapter(self, chapter_info, word_count=2000):
        """Generate a professional fallback chapter"""
        
        chapter_num = chapter_info.get('number', 1)
        chapter_title = chapter_info.get('title', 'Chapter Title')
        
        content = f"""## Chapter {chapter_num}: {chapter_title}

### Introduction

Welcome to this transformative chapter. In the pages ahead, we'll explore the essential principles that will help you master the concepts presented in this book.

### The Core Concept

Every great achievement begins with understanding the fundamentals. In this chapter, we dive deep into the strategies that successful people use to achieve remarkable results.

**Key Insight:** The difference between success and failure often comes down to consistent application of proven principles.

### The Problem

Many people struggle because they:
- Lack a clear strategy
- Don't take consistent action
- Give up too quickly
- Don't learn from mistakes

### The Solution

Here's a proven framework for success:

1. **Clarify Your Goal**
   - Be specific about what you want
   - Write it down
   - Set a deadline
   - Visualize success daily

2. **Create Your Action Plan**
   - Break down big goals into small steps
   - Schedule time for each action
   - Track your progress
   - Adjust as needed

3. **Take Consistent Action**
   - Start before you're ready
   - Do something every day
   - Build momentum gradually
   - Celebrate small wins

4. **Learn and Adapt**
   - Track what works and what doesn't
   - Study successful people
   - Get feedback from mentors
   - Continuously improve

5. **Overcome Obstacles**
   - Expect challenges
   - Develop resilience
   - Find creative solutions
   - Never give up

### Real-World Example

Consider the story of Sarah, a marketing professional who wanted to start her own business. She:
- Set a clear goal (launch in 6 months)
- Created a detailed action plan
- Worked on her business 2 hours daily
- Learned from setbacks
- Achieved her goal ahead of schedule

**Result:** Sarah now runs a 6-figure business doing what she loves.

### Common Mistakes to Avoid

1. **Analysis Paralysis:** Don't overthink - take action
2. **Lack of Consistency:** Success requires daily effort
3. **No Accountability:** Find someone to keep you on track
4. **Ignoring Feedback:** Learn from both success and failure

### The Transformation

By implementing these strategies, you will:
- Achieve your goals faster
- Build unshakeable confidence
- Create lasting success
- Inspire others around you

### Chapter Summary

**Key Takeaways:**
- Success is predictable when you follow proven principles
- Consistency beats intensity every time
- Action creates clarity
- Small daily improvements compound into massive results
- The right strategy accelerates your progress

### Action Exercise

**Your Next Steps:**

1. **Identify Your Goal:** What's the one goal that would make the biggest impact on your life?

2. **Create Your Plan:** Break it down into weekly and daily actions.

3. **Take Action Today:** Do one thing right now that moves you forward.

4. **Track Your Progress:** Create a simple tracking system.

5. **Review Weekly:** Every Sunday, review what worked and adjust.

**Implementation Timeline:**
- Week 1: Planning and preparation
- Week 2-3: Initial action and momentum building
- Week 4+: Optimization and scaling

> "The secret of getting ahead is getting started." - Mark Twain

### Moving Forward

In the next chapter, we'll build on these foundations and explore advanced strategies for accelerating your success. You'll discover how to leverage your strengths, overcome limiting beliefs, and create unstoppable momentum.

Remember: You have everything you need to succeed. The only thing standing between you and your goals is consistent action.

Now, let's take what you've learned and put it into practice!

---

*End of Chapter {chapter_num}*
"""
        
        return content
    
    def generate_introduction(self, book_info, style):
        """Generate a captivating introduction"""
        
        system_prompt = """You write introductions that hook readers from the first sentence.
Your introductions make people feel understood, create curiosity, and promise transformation.

Techniques you use:
- Start with a personal story or shocking fact
- Create an "Aha!" moment in the first paragraph
- Make big promises (and deliver on them)
- Establish credibility quickly
- Create a sense of urgency to keep reading"""
        
        user_prompt = f"""Write a magnetic book introduction:

BOOK: {book_info['title']}
SUBTITLE: {book_info['subtitle']}
GENRE: {book_info['genre']}

Introduction Requirements:
1. First Sentence: Must be irresistible and create instant curiosity
2. The Hook: Why this book matters NOW
3. The Problem: What pain points it solves
4. The Promise: What transformation readers will get
5. Credibility: Why you're the right person to teach this
6. What's Inside: Brief overview of chapters
7. How to Use: Best way to read this book
8. First Action: Something readers can do immediately

Target Audience: {book_info['target_audience']}
Writing Style: {style}

Make readers feel: "This book was written specifically for me!"

Length: 800-1000 words"""
        
        result = self.call_ai(system_prompt, user_prompt, self.models["llama3_70b"], 2500, 0.8)
        
        if result and result.startswith("Error"):
            # Fallback introduction
            return f"""# Introduction to {book_info['title']}

Imagine a world where you've already achieved everything you've ever wanted. What would that look like? What would you be doing? Who would you be spending time with? The truth is, the life you've been dreaming about is closer than you think. But there's one thing standing between you and that life: knowledge.

**Why This Book Matters Now**

We're living in unprecedented times. The world is changing faster than ever before, and the old rules no longer apply. What worked for previous generations simply won't cut it anymore. You need new strategies, new thinking, and new approaches to succeed in today's world.

**The Problem You're Facing**

If you're like most people, you're probably dealing with one or more of these challenges:
- Feeling stuck and unsure how to move forward
- Knowing what you want but not knowing how to get there
- Working hard but not seeing the results you deserve
- Overwhelmed by all the conflicting advice out there

**The Promise**

In this book, you'll discover the exact strategies and systems that successful people use to achieve extraordinary results. You'll learn how to overcome obstacles, build unshakeable confidence, and create the life you truly want.

**What's Inside**

This book is divided into {len(book_info.get('chapters', []))} powerful chapters, each designed to build on the previous one. By the time you finish, you'll have a complete roadmap for success.

**How to Use This Book**

Read it from cover to cover first, then go back and implement the strategies one chapter at a time. Take notes, do the exercises, and most importantly - take action.

**Your First Action**

Right now, before you read another word, take out a piece of paper and write down your #1 goal. What's the one thing that, if you achieved it, would make everything else easier or unnecessary? Write it down. We'll build on this throughout the book.

Let's begin your transformation!"""
        
        return result
    
    def generate_conclusion(self, book_info, style):
        """Generate an inspiring conclusion with call to action"""
        
        system_prompt = """You write conclusions that leave readers inspired, motivated, and ready to take action.
Your conclusions summarize key points while creating momentum for implementation.

Structure you follow:
1. Recap the journey
2. Reinforce the transformation
3. Address lingering doubts
4. Provide a clear next step
5. End with an inspiring vision"""
        
        user_prompt = f"""Write a powerful book conclusion:

BOOK: {book_info['title']}
KEY MESSAGE: {book_info['subtitle']}

Conclusion Requirements:
1. The Journey Recap: Where we started and how far we've come
2. Core Principles: The 3-5 most important takeaways
3. Transformation Summary: What readers should now be able to do
4. Overcoming Resistance: How to handle setbacks
5. Next Steps: Clear action plan for the next 30 days
6. Long-term Vision: Where this leads in 1 year, 5 years
7. Final Inspiration: A motivational closing message
8. Call to Action: What to do right now

Writing Style: {style}

Make readers feel: "I can do this! Let's get started NOW!"

Length: 600-800 words"""
        
        result = self.call_ai(system_prompt, user_prompt, self.models["mixtral"], 2000, 0.85)
        
        if result and result.startswith("Error"):
            # Fallback conclusion
            return f"""# Conclusion: Your Journey Begins Now

## The Journey We've Taken Together

Congratulations! You've made it to the end of {book_info['title']}, but this is really just the beginning. Throughout this book, we've covered the essential strategies and principles you need to achieve extraordinary results.

## The Core Principles

Let's recap the most important lessons:

1. **Success is a System, Not a Secret**: You now have a proven framework that you can follow step by step.

2. **Action Creates Clarity**: You don't need to have all the answers before you start. Take action, learn, and adjust.

3. **Consistency Beats Intensity**: Small daily actions compound into massive results over time.

4. **Mindset Matters**: Your thoughts create your reality. Choose empowering beliefs.

5. **Progress, Not Perfection**: Focus on getting better every day, not being perfect.

## Your Transformation

By implementing what you've learned in this book, you now have the ability to:
- Set and achieve meaningful goals
- Overcome obstacles that used to stop you
- Build unshakeable confidence
- Create lasting success in any area of life

## Handling Setbacks

Remember: setbacks are not failures, they're feedback. When challenges arise (and they will), use these strategies:
- Revisit the relevant chapter in this book
- Adjust your approach based on what you've learned
- Stay focused on your long-term vision
- Keep taking action, even if it's just small steps

## Your 30-Day Action Plan

Here's what to do in the next month:

**Week 1:** Review your notes and create your master action plan
**Week 2:** Start implementing the strategies from Chapter 1-3
**Week 3:** Build on your momentum with chapters 4-6
**Week 4:** Integrate all strategies and measure your progress

## The Long-Term Vision

Imagine where you'll be in one year if you implement just 10% of what you've learned. Now imagine 5 years from now. The compound effect of consistent action is staggering.

## Final Inspiration

You have everything you need to succeed. The knowledge, the strategies, the roadmap - it's all here. The only thing standing between you and your dreams is action.

Don't let another day go by living below your potential. You were meant for greatness. You were meant to inspire others. You were meant to make a difference.

## Take Action NOW

Close this book and do ONE thing from your action plan. Right now. Not tomorrow, not next week - NOW.

Your future self will thank you.

**Now go make it happen!**

---

*"The future belongs to those who believe in the beauty of their dreams." - Eleanor Roosevelt*
"""
        
        return result
    
    def generate_marketing_package(self, book_info):
        """Generate complete marketing assets"""
        
        system_prompt = """You are a top-tier book marketing expert who knows how to make books sell.
You understand Amazon algorithms, social media virality, and email marketing conversion."""
        
        user_prompt = f"""Create marketing for: {book_info['title']}

Return as JSON with these sections:
- book_description
- author_bio
- social_media (twitter, hashtags)
- keywords
- categories"""
        
        result = self.call_ai(system_prompt, user_prompt, self.models["llama3_70b"], 4000, 0.7)
        
        if result and not result.startswith("Error"):
            try:
                if '```json' in result:
                    result = result.split('```json')[1].split('```')[0].strip()
                
                marketing = json.loads(result)
                marketing['generated_at'] = datetime.now().isoformat()
                marketing['estimated_value'] = "$5,000-$15,000 (agency pricing)"
                
                return marketing
            except:
                pass
        
        # Fallback marketing package
        return self.create_fallback_marketing(book_info)
    
    def create_fallback_marketing(self, book_info):
        """Create basic marketing package"""
        
        return {
            "book_description": f"{book_info['title']} is your complete guide to mastering {book_info.get('topic', 'your field')}. Packed with actionable strategies, real-world examples, and step-by-step instructions, this book will transform your approach and deliver remarkable results.",
            "author_bio": "A leading expert with years of experience helping people achieve extraordinary results. Passionate about sharing proven strategies that actually work.",
            "social_media": {
                "twitter": [
                    f"Just finished {book_info['title']}! Mind blown by the insights!",
                    f"3 game-changing ideas from {book_info['title']} that transformed my approach"
                ],
                "hashtags": ["#book", "#bestseller", "#selfhelp", "#success"]
            },
            "keywords": [book_info.get('topic', ''), "guide", "mastery", "how-to"],
            "categories": ["Self-Help", "Business", "Personal Development"],
            "generated_at": datetime.now().isoformat()
        }
    
    def generate_cover_concepts(self, book_info):
        """Generate book cover concepts"""
        
        return [
            {
                "name": "Professional Minimalist",
                "colors": ["#2c3e50", "#3498db", "#ffffff"],
                "style": "Clean, modern, trustworthy",
                "best_for": "Business/Professional books"
            }
        ]

# ========== DATABASE ==========
class BookDatabasePro:
    def __init__(self):
        os.makedirs("ebook_data", exist_ok=True)
        self.conn = sqlite3.connect('ebook_data/ebooks_pro.db', check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        self.conn.execute('''CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            subtitle TEXT,
            topic TEXT,
            genre TEXT,
            content BLOB,
            word_count INTEGER,
            chapters INTEGER,
            style TEXT,
            target_audience TEXT,
            marketing_package BLOB,
            cover_concepts BLOB,
            estimated_value REAL,
            created_at TEXT,
            user_hash TEXT,
            is_published BOOLEAN DEFAULT 0,
            sales_estimate REAL DEFAULT 0
        )''')
        
        self.conn.execute('''CREATE TABLE IF NOT EXISTS sales_simulation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER,
            month TEXT,
            units_sold INTEGER,
            revenue REAL,
            platform TEXT,
            FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
        )''')
        
        self.conn.execute('''CREATE TABLE IF NOT EXISTS user_analytics (
            user_hash TEXT PRIMARY KEY,
            total_books INTEGER DEFAULT 0,
            total_words INTEGER DEFAULT 0,
            estimated_earnings REAL DEFAULT 0,
            favorite_genre TEXT,
            last_active TEXT,
            subscription_tier TEXT DEFAULT 'free'
        )''')
        
        self.conn.execute('''CREATE TABLE IF NOT EXISTS export_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER,
            export_format TEXT,
            exported_at TEXT,
            file_path TEXT,
            FOREIGN KEY (book_id) REFERENCES books(id)
        )''')
        
        self.conn.commit()
    
    def save_book(self, book_data, user_hash):
        """Save complete book with all metadata"""
        try:
            if 'outline' not in book_data:
                st.error("Book outline is missing!")
                return None
            
            content_blob = pickle.dumps({
                'outline': book_data.get('outline'),
                'introduction': book_data.get('introduction'),
                'chapters': book_data.get('chapters'),
                'conclusion': book_data.get('conclusion'),
                'full_content': book_data.get('full_content')
            })
            
            marketing_blob = pickle.dumps(book_data.get('marketing_package', {}))
            covers_blob = pickle.dumps(book_data.get('cover_concepts', []))
            
            word_count = book_data.get('word_count', 0)
            estimated_value = word_count * 0.05
            
            book_tuple = (
                book_data['outline']['title'],
                book_data['outline'].get('subtitle', ''),
                book_data.get('topic', ''),
                book_data['outline'].get('genre', 'self_help'),
                content_blob,
                word_count,
                len(book_data.get('chapters', [])),
                book_data.get('style', 'professional'),
                book_data['outline'].get('target_audience', ''),
                marketing_blob,
                covers_blob,
                estimated_value,
                datetime.now().isoformat(),
                user_hash
            )
            
            cursor = self.conn.execute('''INSERT INTO books 
                (title, subtitle, topic, genre, content, word_count, chapters, 
                 style, target_audience, marketing_package, cover_concepts, 
                 estimated_value, created_at, user_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                book_tuple
            )
            
            book_id = cursor.lastrowid
            
            self.update_user_analytics(user_hash, word_count, estimated_value)
            
            self.conn.commit()
            return book_id
            
        except sqlite3.Error as e:
            st.error(f"Database error: {str(e)}")
            self.conn.rollback()
            return None
        except Exception as e:
            st.error(f"Error saving book: {str(e)}")
            return None
    
    def update_user_analytics(self, user_hash, word_count, estimated_value):
        """Update user analytics after saving a book"""
        try:
            cursor = self.conn.execute(
                '''SELECT total_books, total_words, estimated_earnings 
                   FROM user_analytics WHERE user_hash = ?''', 
                (user_hash,)
            )
            row = cursor.fetchone()
            
            if row:
                total_books = row[0] + 1
                total_words = row[1] + word_count
                total_earnings = row[2] + estimated_value
                
                self.conn.execute('''UPDATE user_analytics 
                    SET total_books = ?, 
                        total_words = ?, 
                        estimated_earnings = ?,
                        last_active = ?
                    WHERE user_hash = ?''',
                    (total_books, total_words, total_earnings, 
                     datetime.now().isoformat(), user_hash)
                )
            else:
                self.conn.execute('''INSERT INTO user_analytics 
                    (user_hash, total_books, total_words, estimated_earnings, last_active)
                    VALUES (?, ?, ?, ?, ?)''',
                    (user_hash, 1, word_count, estimated_value, datetime.now().isoformat())
                )
        except Exception as e:
            print(f"Error updating analytics: {e}")
    
    def get_user_stats(self, user_hash):
        cursor = self.conn.execute('''SELECT 
            total_books, 
            total_words, 
            estimated_earnings,
            last_active
            FROM user_analytics WHERE user_hash = ?''', (user_hash,))
        return cursor.fetchone()
    
    def get_all_books(self, user_hash, limit=50):
        cursor = self.conn.execute('''SELECT 
            id, title, subtitle, genre, word_count, created_at, estimated_value
            FROM books WHERE user_hash = ? 
            ORDER BY created_at DESC LIMIT ?''', (user_hash, limit))
        return cursor.fetchall()
    
    def get_book_details(self, book_id):
        cursor = self.conn.execute('''SELECT * FROM books WHERE id = ?''', (book_id,))
        row = cursor.fetchone()
        
        if row:
            columns = [description[0] for description in cursor.description]
            book_dict = dict(zip(columns, row))
            
            if book_dict.get('content'):
                book_dict['content'] = pickle.loads(book_dict['content'])
            if book_dict.get('marketing_package'):
                book_dict['marketing_package'] = pickle.loads(book_dict['marketing_package'])
            if book_dict.get('cover_concepts'):
                book_dict['cover_concepts'] = pickle.loads(book_dict['cover_concepts'])
            
            return book_dict
        return None
    
    def generate_sales_simulation(self, book_id, months=12):
        """Generate realistic sales simulation"""
        
        import random
        
        book = self.get_book_details(book_id)
        if not book:
            return []
        
        base_price = 9.99
        platforms = ['Amazon', 'Gumroad', 'Website', 'Bundle']
        
        sales_data = []
        current_date = datetime.now()
        
        for month in range(months):
            month_date = current_date + timedelta(days=30*month)
            month_str = month_date.strftime('%Y-%m')
            
            if month < 3:
                units = random.randint(50, 200)
            elif month < 6:
                units = random.randint(200, 500)
            else:
                units = random.randint(50, 150)
            
            genre_multiplier = {
                'self_help': 1.2,
                'business': 1.5,
                'finance': 1.3,
                'health': 1.1,
                'fiction': 0.8
            }.get(book.get('genre', 'self_help'), 1.0)
            
            units = int(units * genre_multiplier)
            revenue = units * base_price
            
            platform = random.choice(platforms)
            
            sales_data.append({
                'month': month_str,
                'units': units,
                'revenue': revenue,
                'platform': platform
            })
            
            self.conn.execute('''INSERT INTO sales_simulation 
                (book_id, month, units_sold, revenue, platform)
                VALUES (?, ?, ?, ?, ?)''',
                (book_id, month_str, units, revenue, platform))
        
        self.conn.commit()
        return sales_data
    
    def log_export(self, book_id, export_format, file_path):
        """Log export activity"""
        self.conn.execute('''INSERT INTO export_history 
            (book_id, export_format, exported_at, file_path)
            VALUES (?, ?, ?, ?)''',
            (book_id, export_format, datetime.now().isoformat(), file_path)
        )
        self.conn.commit()

# ========== EXPORT MANAGER ==========
class EnhancedExportManager:
    @staticmethod
    def to_html(book_data, author):
        """Export to professional HTML format"""
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{book_data['title']}</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=Merriweather:wght@400;700&display=swap');
        
        body {{
            font-family: 'Inter', sans-serif;
            line-height: 1.8;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}
        
        .book-container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 25px 50px rgba(0,0,0,0.1);
            border-radius: 15px;
            overflow: hidden;
        }}
        
        .cover {{
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            color: white;
            padding: 100px 40px;
            text-align: center;
        }}
        
        .cover h1 {{
            font-family: 'Merriweather', serif;
            font-size: 3.5rem;
            margin-bottom: 20px;
        }}
        
        .cover h2 {{
            font-size: 1.8rem;
            font-weight: 300;
            opacity: 0.9;
        }}
        
        .author {{
            font-size: 1.4rem;
            margin-top: 40px;
            font-style: italic;
        }}
        
        .content {{
            padding: 60px 40px;
        }}
        
        h1, h2, h3 {{
            color: #2c3e50;
            margin: 40px 0 20px;
        }}
        
        p {{ 
            margin-bottom: 25px;
            font-size: 1.1rem;
        }}
        
        footer {{
            text-align: center;
            padding: 40px;
            background: #2c3e50;
            color: white;
        }}
    </style>
</head>
<body>
    <div class="book-container">
        <div class="cover">
            <h1>{book_data['title']}</h1>
            <h2>{book_data.get('subtitle', '')}</h2>
            <div class="author">by {author}</div>
        </div>
        
        <div class="content">
            {EnhancedExportManager.markdown_to_html(book_data.get('full_content', ''))}
        </div>
        
        <footer>
            <p>© {datetime.now().year} {author}</p>
            <p style="opacity: 0.8; margin-top: 10px;">Created with EbookMaster Ultra Pro</p>
        </footer>
    </div>
</body>
</html>"""
        
        return html
    
    @staticmethod
    def markdown_to_html(text):
        """Convert markdown to HTML"""
        text = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
        text = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
        
        text = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>', text)
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        
        lines = text.split('\n')
        html_lines = []
        
        for line in lines:
            if line.strip() and not line.startswith('<'):
                html_lines.append(f'<p>{line}</p>')
            elif line.strip():
                html_lines.append(line)
        
        return '\n'.join(html_lines)
    
    @staticmethod
    def to_pdf(book_data, author):
        """Export to PDF"""
        try:
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            
            pdf.set_font("Arial", "B", 24)
            pdf.cell(200, 10, book_data['title'].encode('latin-1', 'replace').decode('latin-1'), ln=True, align="C")
            
            pdf.set_font("Arial", "I", 16)
            pdf.cell(200, 10, book_data.get('subtitle', '').encode('latin-1', 'replace').decode('latin-1'), ln=True, align="C")
            
            pdf.set_font("Arial", "", 14)
            pdf.cell(200, 10, f"by {author}".encode('latin-1', 'replace').decode('latin-1'), ln=True, align="C")
            
            pdf.ln(20)
            
            pdf.set_font("Arial", "", 12)
            content = book_data.get('full_content', '')
            
            lines = content.split('\n')
            for line in lines:
                try:
                    if line.startswith('# '):
                        pdf.set_font("Arial", "B", 16)
                        pdf.cell(200, 10, line[2:].encode('latin-1', 'replace').decode('latin-1'), ln=True)
                        pdf.set_font("Arial", "", 12)
                    elif line.startswith('## '):
                        pdf.set_font("Arial", "B", 14)
                        pdf.cell(200, 10, line[3:].encode('latin-1', 'replace').decode('latin-1'), ln=True)
                        pdf.set_font("Arial", "", 12)
                    elif line.strip():
                        pdf.multi_cell(0, 10, line.encode('latin-1', 'replace').decode('latin-1'))
                    else:
                        pdf.ln(5)
                except:
                    continue
            
            filename = f"ebook_data/{book_data['title'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf.output(filename)
            return filename
        except Exception as e:
            st.error(f"PDF generation error: {str(e)}")
            return None

# ========== MAIN APPLICATION ==========
def main():
    st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        color: #666;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('<h1 class="main-header">📚 EbookMaster Ultra Pro</h1>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">🚀 Create Bestselling Books with AI</p>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: right; padding: 10px; background: #f8f9fa; border-radius: 10px;">
            <div style="color: #27ae60; font-weight: bold;">💰 Est. $500-$5,000/book</div>
        </div>
        """, unsafe_allow_html=True)
    
    if 'user_hash' not in st.session_state:
        st.session_state.user_hash = hashlib.md5(str(time.time()).encode()).hexdigest()[:12]
    
    with st.sidebar:
        st.header("⚙️ SETTINGS")
        
        with st.expander("🔑 API KEY", expanded=True):
            groq_key = st.text_input("Groq API Key", type="password")
            if groq_key:
                st.success("✅ Ready")
        
        with st.expander("👤 AUTHOR", expanded=True):
            author_name = st.text_input("Author Name", "John Smith")
        
        with st.expander("📖 BOOK CONFIG", expanded=True):
            ai_helper = AIPowerhouse("")
            genre = st.selectbox("Genre", list(ai_helper.genres.values()))
            style = st.selectbox("Style", list(ai_helper.writing_styles.keys()))
            target_audience = st.selectbox("Target", [
                "Beginners",
                "Professionals",
                "Entrepreneurs",
                "General readers"
            ])
        
        with st.expander("⚡ GENERATION", expanded=False):
            chapters = st.slider("Chapters", 5, 20, 10)
            words_per_chapter = st.slider("Words/Chapter", 1500, 5000, 2500)
    
    tab1, tab2, tab3 = st.tabs(["🚀 CREATE", "📖 PREVIEW", "📤 EXPORT"])
    
    with tab1:
        st.header("🚀 CREATE YOUR BOOK")
        
        topic = st.text_area(
            "BOOK TOPIC",
            height=150,
            placeholder="Example: How to build a successful online business from scratch"
        )
        
        if st.button("✨ GENERATE BOOK", type="primary", use_container_width=True):
            if not groq_key:
                st.error("Please enter Groq API Key")
                st.stop()
            
            if not topic.strip():
                st.error("Please enter a topic")
                st.stop()
            
            ai = AIPowerhouse(groq_key)
            db = BookDatabasePro()
            
            progress_bar = st.progress(0)
            status = st.empty()
            
            # Generate Outline
            status.text("📋 Creating outline...")
            outline = ai.generate_outline(topic, chapters, genre, style, target_audience)
            progress_bar.progress(10)
            st.session_state.outline = outline
            
            # Generate Introduction
            status.text("✍️ Writing introduction...")
            introduction = ai.generate_introduction(outline, style)
            progress_bar.progress(20)
            st.session_state.introduction = introduction
            
            # Generate Chapters
            chapters_content = []
            total_chapters = len(outline.get('chapters', []))
            
            for i, chapter in enumerate(outline.get('chapters', [])):
                progress = 20 + ((i + 1) / total_chapters * 60)
                progress_bar.progress(int(progress))
                status.text(f"📝 Chapter {i+1}/{total_chapters}...")
                
                try:
                    chapter_content = ai.generate_chapter(outline, chapter, words_per_chapter, style)
                    
                    if chapter_content and not chapter_content.startswith("Error"):
                        chapters_content.append(chapter_content)
                        st.success(f"✓ Chapter {i+1}")
                    else:
                        fallback = ai.generate_fallback_chapter(chapter, words_per_chapter)
                        chapters_content.append(fallback)
                        st.warning(f"⚠ Chapter {i+1} (fallback)")
                
                except Exception as e:
                    fallback = ai.generate_fallback_chapter(chapter, words_per_chapter)
                    chapters_content.append(fallback)
            
            st.session_state.chapters = chapters_content
            
            # Generate Conclusion
            status.text("🎯 Writing conclusion...")
            conclusion = ai.generate_conclusion(outline, style)
            progress_bar.progress(90)
            st.session_state.conclusion = conclusion
            
            # Assemble Book
            full_content = f"# INTRODUCTION\n\n{introduction}\n\n"
            for i, (chapter, content) in enumerate(zip(outline.get('chapters', []), chapters_content)):
                full_content += f"# CHAPTER {chapter['number']}: {chapter['title']}\n\n{content}\n\n"
            full_content += f"# CONCLUSION\n\n{conclusion}"
            
            st.session_state.full_content = full_content
            
            # Generate Marketing
            marketing = ai.generate_marketing_package(outline)
            st.session_state.marketing = marketing
            
            # Generate Covers
            covers = ai.generate_cover_concepts(outline)
            st.session_state.covers = covers
            
            # Save
            book_data = {
                'outline': outline,
                'introduction': introduction,
                'chapters': chapters_content,
                'conclusion': conclusion,
                'full_content': full_content,
                'marketing_package': marketing,
                'cover_concepts': covers,
                'topic': topic,
                'style': style,
                'word_count': len(full_content.split())
            }
            
            book_id = db.save_book(book_data, st.session_state.user_hash)
            if book_id:
                st.session_state.current_book_id = book_id
                sales_data = db.generate_sales_simulation(book_id)
                st.session_state.sales_data = sales_data
                
                progress_bar.progress(100)
                status.text("✅ COMPLETE!")
                st.balloons()
                st.success(f"🎉 {outline['title']} created!")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Words", f"{len(full_content.split()):,}")
                with col2:
                    st.metric("Chapters", len(chapters_content))
                with col3:
                    st.metric("Pages", f"~{len(full_content.split()) // 250}")
    
    with tab2:
        st.header("📖 PREVIEW")
        
        if 'full_content' not in st.session_state:
            st.warning("Create a book first")
        else:
            st.subheader(st.session_state.outline['title'])
            st.caption(st.session_state.outline.get('subtitle', ''))
            st.divider()
            
            preview_length = st.slider("Preview words", 500, 5000, 1000)
            st.markdown(st.session_state.full_content[:preview_length] + "...")
    
    with tab3:
        st.header("📤 EXPORT")
        
        if 'full_content' not in st.session_state:
            st.warning("Create a book first")
        else:
            book_data = {
                'title': st.session_state.outline['title'],
                'subtitle': st.session_state.outline.get('subtitle', ''),
                'full_content': st.session_state.full_content
            }
            
            export_manager = EnhancedExportManager()
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📄 PDF", use_container_width=True):
                    with st.spinner("Generating..."):
                        filename = export_manager.to_pdf(book_data, author_name)
                        if filename:
                            with open(filename, "rb") as file:
                                st.download_button(
                                    "📥 Download PDF",
                                    file,
                                    file_name=f"{book_data['title'].replace(' ', '_')}.pdf",
                                    mime="application/pdf"
                                )
            
            with col2:
                if st.button("🌐 HTML", use_container_width=True):
                    html = export_manager.to_html(book_data, author_name)
                    st.download_button(
                        "📥 Download HTML",
                        html,
                        file_name=f"{book_data['title'].replace(' ', '_')}.html",
                        mime="text/html"
                    )

if __name__ == "__main__":
    main()
