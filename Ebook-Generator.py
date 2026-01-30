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
            return self.models["llama3_70b"]  # Best for planning
        elif "creative" in genre or "fiction" in genre:
            return self.models["mixtral"]  # Best for creativity
        elif "technical" in genre or "academic" in genre:
            return self.models["llama3_70b"]  # Best for depth
        else:
            return self.models["gemma2"]  # Good all-rounder
    
    @st.cache_data(ttl=3600, show_spinner=False)
    def call_ai(_self, system_prompt, user_prompt, model_name, max_tokens=6000, temperature=0.75):
        try:
            response = requests.post(
                _self.groq_url,
                headers={
                    "Authorization": f"Bearer {_self.groq_api_key}",
                    "Content-Type": "application/json"
                },
                json={
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
                },
                timeout=120
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            else:
                return f"API Error: {response.status_code}"
        except Exception as e:
            return f"Network Error: {str(e)}"
    
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
        """Generate a compelling book chapter"""
        
        model = self.select_model_for_task("chapter", book_info['genre'], book_info['target_audience'])
        
        system_prompt = f"""You are a {style} writer creating bestselling content.
        
        Writing principles to follow:
        1. Start with a story or shocking statistic
        2. Use short paragraphs and sentences
        3. Include actionable steps readers can take NOW
        4. Add real-world examples and case studies
        5. End with a motivational call to action
        6. Use power words and emotional triggers
        
        Current bestselling trends:
        - Readers want transformation, not just information
        - Storytelling increases engagement by 300%
        - Actionable content gets shared 5x more
        - Controversial ideas generate buzz"""
        
        user_prompt = f"""Write a bestselling book chapter:
        
        BOOK: {book_info['title']} - {book_info['subtitle']}
        GENRE: {book_info['genre']}
        TARGET READER: {book_info['target_audience']}
        
        CHAPTER {chapter_info['number']}: {chapter_info['title']}
        CHAPTER HOOK: {chapter_info['hook']}
        KEY POINTS TO COVER: {', '.join(chapter_info['key_points'])}
        
        WORD COUNT: {word_count} words
        WRITING STYLE: {style}
        
        Chapter Structure Requirements:
        1. OPENING HOOK: Start with a compelling story, question, or statistic
        2. THE PROBLEM: Clearly define what's wrong or missing
        3. THE SOLUTION: Present your unique approach
        4. ACTION STEPS: Provide 3-5 actionable steps readers can implement
        5. CASE STUDY: Include a real or hypothetical success story
        6. COMMON MISTAKES: Warn about what to avoid
        7. TRANSFORMATION: Describe the ideal outcome
        8. CHAPTER SUMMARY: Key takeaways in bullet points
        9. ACTION EXERCISE: A practical exercise for immediate application
        
        Formatting:
        - Use Markdown formatting
        - Include ## Headers for sections
        - Use **bold** for key points
        - Add > blockquotes for important insights
        - Include numbered lists for steps
        - Add [EXERCISE] sections with practical tasks
        
        Make this chapter so valuable readers would pay for it alone."""
        
        result = self.call_ai(system_prompt, user_prompt, model, 8000, 0.8)
        
        # Fallback to OpenAI
        if result and result.startswith("Error"):
            result = self.call_openai(system_prompt, user_prompt, max_tokens=6000)
        
        return result
    
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
        
        result = self.call_ai(system_prompt, user_prompt, self.models["llama3_70b"], 3000, 0.8)
        
        if result and result.startswith("Error"):
            result = self.call_openai(system_prompt, user_prompt)
        
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
        
        result = self.call_ai(system_prompt, user_prompt, self.models["mixtral"], 2500, 0.85)
        
        if result and result.startswith("Error"):
            result = self.call_openai(system_prompt, user_prompt)
        
        return result
    
    def generate_marketing_package(self, book_info):
        """Generate complete marketing assets"""
        
        system_prompt = """You are a top-tier book marketing expert who knows how to make books sell.
        You understand Amazon algorithms, social media virality, and email marketing conversion.
        
        Your marketing assets consistently:
        - Increase book sales by 300%+
        - Generate 5-star reviews
        - Create buzz on social media
        - Build author authority
        - Drive speaking engagements"""
        
        user_prompt = f"""Create a complete marketing package for this book:
        
        BOOK: {book_info['title']}
        SUBTITLE: {book_info['subtitle']}
        GENRE: {book_info['genre']}
        TARGET AUDIENCE: {book_info['target_audience']}
        HOOK: {book_info.get('marketing_hook', 'Transform your life with this guide')}
        
        REQUIRED MARKETING ASSETS:
        
        1. BOOK DESCRIPTION (Amazon/Kindle):
           - 1500 characters max
           - SEO-optimized
           - Bullet points of benefits
           - Call to action
        
        2. AUTHOR BIO (Compelling & Credible):
           - 200 words
           - Establishes expertise
           - Builds trust
           - Personal touch
        
        3. SOCIAL MEDIA PACKAGE:
           - 10 Twitter/X posts (280 chars each)
           - 5 LinkedIn posts (professional)
           - 5 Instagram captions (engaging)
           - 3 TikTok hooks (15 seconds)
           - 10 relevant hashtags
        
        4. EMAIL SEQUENCE (5 emails):
           - Welcome/Pre-order announcement
           - Chapter preview
           - Launch day excitement
           - Social proof/reviews
           - Upsell/related products
        
        5. PRESS RELEASE:
           - Newsworthy angle
           - Quotes from "author"
           - Contact information
           - Key facts
        
        6. AD COPY (Facebook/Amazon Ads):
           - 3 different headlines
           - 2 primary descriptions
           - Target audience suggestions
           - Budget recommendations
        
        7. KEYWORDS & CATEGORIES:
           - 10 primary keywords
           - 5 Amazon categories
           - 3 BISAC codes
        
        Return as JSON with these sections."""
        
        result = self.call_ai(system_prompt, user_prompt, self.models["llama3_70b"], 8000, 0.7)
        
        # Fallback to OpenAI
        if result and result.startswith("Error"):
            result = self.call_openai(system_prompt, user_prompt, max_tokens=6000)
        
        if result and not result.startswith("Error"):
            try:
                if '```json' in result:
                    result = result.split('```json')[1].split('```')[0].strip()
                
                marketing = json.loads(result)
                
                # Add generated metadata
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
        """Generate book cover concepts and descriptions"""
        
        system_prompt = """You are a professional book cover designer who knows what sells.
        You understand color psychology, typography, and market trends."""
        
        user_prompt = f"""Create 3 professional book cover concepts for:
        
        TITLE: {book_info['title']}
        SUBTITLE: {book_info['subtitle']}
        GENRE: {book_info['genre']}
        
        For each concept, provide:
        1. Design Style (Minimalist, Bold, Elegant, etc.)
        2. Color Palette (Hex codes)
        3. Typography Suggestions
        4. Imagery/Graphics Ideas
        5. Emotional Appeal
        6. Target Reader Attraction
        7. Why This Design Sells
        
        Return as JSON array of 3 concepts."""
        
        result = self.call_ai(system_prompt, user_prompt, self.models["mixtral"], 4000, 0.8)
        
        if result and not result.startswith("Error"):
            try:
                concepts = json.loads(result.replace('```json', '').replace('```', '').strip())
                return concepts
            except:
                pass
        
        # Fallback cover concepts
        return [
            {
                "name": "Professional Minimalist",
                "colors": ["#2c3e50", "#3498db", "#ffffff"],
                "style": "Clean, modern, trustworthy",
                "best_for": "Business/Professional books"
            }
        ]

# ========== ENHANCED DATABASE ==========
class BookDatabasePro:
    def __init__(self):
        os.makedirs("ebook_data", exist_ok=True)
        self.conn = sqlite3.connect('ebook_data/ebooks_pro.db', check_same_thread=False)
        self.create_tables()
    
    def create_tables(self):
        # Books table with enhanced fields
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
        
        # Sales tracking (simulated)
        self.conn.execute('''CREATE TABLE IF NOT EXISTS sales_simulation (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER,
            month TEXT,
            units_sold INTEGER,
            revenue REAL,
            platform TEXT,
            FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
        )''')
        
        # User analytics
        self.conn.execute('''CREATE TABLE IF NOT EXISTS user_analytics (
            user_hash TEXT PRIMARY KEY,
            total_books INTEGER DEFAULT 0,
            total_words INTEGER DEFAULT 0,
            estimated_earnings REAL DEFAULT 0,
            favorite_genre TEXT,
            last_active TEXT,
            subscription_tier TEXT DEFAULT 'free'
        )''')
        
        # Export history
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
            # Check if required fields exist
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
            
            # Calculate estimated value
            word_count = book_data.get('word_count', 0)
            estimated_value = word_count * 0.05  # $0.05 per word (industry standard)
            
            # Prepare data for insertion
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
                datetime.now().isoformat(),  # Use ISO format string
                user_hash
            )
            
            # Execute insert
            cursor = self.conn.execute('''INSERT INTO books 
                (title, subtitle, topic, genre, content, word_count, chapters, 
                 style, target_audience, marketing_package, cover_concepts, 
                 estimated_value, created_at, user_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                book_tuple
            )
            
            book_id = cursor.lastrowid
            
            # Update user analytics
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
            # Get current stats
            cursor = self.conn.execute(
                '''SELECT total_books, total_words, estimated_earnings 
                   FROM user_analytics WHERE user_hash = ?''', 
                (user_hash,)
            )
            row = cursor.fetchone()
            
            if row:
                # Update existing record
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
                # Insert new record
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
            
            # Unpickle binary data
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
        
        # Get book details
        book = self.get_book_details(book_id)
        if not book:
            return []
        
        # Sales simulation logic
        base_price = 9.99
        platforms = ['Amazon', 'Gumroad', 'Website', 'Bundle']
        
        sales_data = []
        current_date = datetime.now()
        
        for month in range(months):
            month_date = current_date + timedelta(days=30*month)
            month_str = month_date.strftime('%Y-%m')
            
            # Simulate sales curve (hump-shaped)
            if month < 3:  # Launch phase
                units = random.randint(50, 200)
            elif month < 6:  # Growth phase
                units = random.randint(200, 500)
            else:  # Stable phase
                units = random.randint(50, 150)
            
            # Adjust by genre
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
            
            # Save to database
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

# ========== ADVANCED EXPORT MANAGER ==========
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
        
        :root {{
            --primary: #2c3e50;
            --secondary: #3498db;
            --accent: #e74c3c;
            --light: #ecf0f1;
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Inter', sans-serif;
            line-height: 1.8;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .book-container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            box-shadow: 0 25px 50px rgba(0,0,0,0.3);
            border-radius: 15px;
            overflow: hidden;
        }}
        
        .cover {{
            background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
            color: white;
            padding: 100px 40px;
            text-align: center;
            position: relative;
        }}
        
        .cover h1 {{
            font-family: 'Merriweather', serif;
            font-size: 3.5rem;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        
        .cover h2 {{
            font-size: 1.8rem;
            font-weight: 300;
            opacity: 0.9;
            margin-bottom: 40px;
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
            color: var(--primary);
            margin: 40px 0 20px;
        }}
        
        h1 {{ 
            font-size: 2.5rem;
            border-bottom: 3px solid var(--accent);
            padding-bottom: 15px;
        }}
        
        h2 {{ 
            font-size: 2rem;
            border-left: 4px solid var(--secondary);
            padding-left: 15px;
        }}
        
        p {{ 
            margin-bottom: 25px;
            font-size: 1.1rem;
        }}
        
        blockquote {{
            border-left: 4px solid var(--secondary);
            padding: 20px;
            margin: 30px 0;
            background: var(--light);
            font-style: italic;
        }}
        
        .exercise {{
            background: #e8f4fc;
            border: 2px dashed var(--secondary);
            padding: 20px;
            margin: 30px 0;
            border-radius: 10px;
        }}
        
        .exercise h4 {{
            color: var(--secondary);
            margin-top: 0;
        }}
        
        footer {{
            text-align: center;
            padding: 40px;
            background: var(--primary);
            color: white;
            margin-top: 60px;
        }}
        
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            
            .book-container {{
                box-shadow: none;
                border-radius: 0;
            }}
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
        # Convert headers
        text = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
        text = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
        
        # Convert bold and italic
        text = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>', text)
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        
        # Convert lists
        lines = text.split('\n')
        html_lines = []
        in_list = False
        
        for line in lines:
            if re.match(r'^\s*[-*+]\s+', line):
                if not in_list:
                    html_lines.append('<ul>')
                    in_list = True
                html_lines.append(f'<li>{line.strip()[2:]}</li>')
            elif re.match(r'^\s*\d+\.\s+', line):
                if not in_list:
                    html_lines.append('<ol>')
                    in_list = True
                html_lines.append(f'<li>{line.strip()[3:]}</li>')
            else:
                if in_list:
                    html_lines.append('</ul>' if '*' in line or '-' in line else '</ol>')
                    in_list = False
                
                if line.strip() and not line.startswith('<'):
                    html_lines.append(f'<p>{line}</p>')
                elif line.strip():
                    html_lines.append(line)
        
        if in_list:
            html_lines.append('</ul>')
        
        return '\n'.join(html_lines)
    
    @staticmethod
    def to_pdf(book_data, author):
        """Export to PDF using FPDF2"""
        try:
            pdf = FPDF()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.add_page()
            
            # Title
            pdf.set_font("Arial", "B", 24)
            pdf.cell(200, 10, book_data['title'], ln=True, align="C")
            
            # Subtitle
            pdf.set_font("Arial", "I", 16)
            pdf.cell(200, 10, book_data.get('subtitle', ''), ln=True, align="C")
            
            # Author
            pdf.set_font("Arial", "", 14)
            pdf.cell(200, 10, f"by {author}", ln=True, align="C")
            
            pdf.ln(20)
            
            # Content
            pdf.set_font("Arial", "", 12)
            content = book_data.get('full_content', '')
            
            # Simple markdown parsing
            lines = content.split('\n')
            for line in lines:
                if line.startswith('# '):
                    pdf.set_font("Arial", "B", 16)
                    pdf.cell(200, 10, line[2:], ln=True)
                    pdf.set_font("Arial", "", 12)
                elif line.startswith('## '):
                    pdf.set_font("Arial", "B", 14)
                    pdf.cell(200, 10, line[3:], ln=True)
                    pdf.set_font("Arial", "", 12)
                elif line.startswith('### '):
                    pdf.set_font("Arial", "B", 12)
                    pdf.cell(200, 10, line[4:], ln=True)
                    pdf.set_font("Arial", "", 12)
                elif line.strip():
                    pdf.multi_cell(0, 10, line)
                else:
                    pdf.ln(5)
            
            # Generate file
            filename = f"ebook_data/{book_data['title'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf.output(filename)
            return filename
        except Exception as e:
            st.error(f"PDF generation error: {str(e)}")
            return None
    
    @staticmethod
    def to_epub(book_data, author):
        """Export to EPUB format"""
        try:
            book = epub.EpubBook()
            
            # Set metadata
            book.set_title(book_data['title'])
            book.set_language('en')
            book.add_author(author)
            
            # Create chapters
            chapters = []
            content = book_data.get('full_content', '')
            
            # Split content into chapters
            chapter_parts = content.split('# CHAPTER')
            
            for i, part in enumerate(chapter_parts):
                if i == 0:  # Introduction
                    continue
                
                title_end = part.find('\n')
                chapter_title = part[:title_end].strip() if title_end != -1 else f"Chapter {i}"
                chapter_content = part[title_end:] if title_end != -1 else part
                
                # Create chapter
                chapter = epub.EpubHtml(
                    title=chapter_title,
                    file_name=f'chap_{i}.xhtml',
                    lang='en'
                )
                chapter.content = f'<h1>{chapter_title}</h1>{EnhancedExportManager.markdown_to_html(chapter_content)}'
                chapters.append(chapter)
                book.add_item(chapter)
            
            # Define Table of Contents
            book.toc = chapters
            
            # Add navigation files
            book.add_item(epub.EpubNcx())
            book.add_item(epub.EpubNav())
            
            # Define CSS style
            style = '''
            @namespace epub "http://www.idpf.org/2007/ops";
            body { font-family: "Times New Roman", Times, serif; }
            h1 { text-align: center; }
            h2 { text-align: left; }
            '''
            
            # Add CSS file
            nav_css = epub.EpubItem(
                uid="style_nav",
                file_name="style/nav.css",
                media_type="text/css",
                content=style
            )
            book.add_item(nav_css)
            
            # Generate file
            filename = f"ebook_data/{book_data['title'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.epub"
            epub.write_epub(filename, book, {})
            return filename
        except Exception as e:
            st.error(f"EPUB generation error: {str(e)}")
            return None
    
    @staticmethod
    def to_docx(book_data, author):
        """Export to DOCX using ReportLab (simplified)"""
        try:
            filename = f"ebook_data/{book_data['title'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            # Create PDF first (simplified approach)
            doc = SimpleDocTemplate(
                filename,
                pagesize=letter,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=18
            )
            
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            story.append(Paragraph(book_data['title'], styles['Title']))
            story.append(Paragraph(f"by {author}", styles['Normal']))
            story.append(Paragraph("<br/><br/>", styles['Normal']))
            
            # Content
            content = book_data.get('full_content', '')
            lines = content.split('\n')
            
            for line in lines:
                if line.startswith('# '):
                    story.append(Paragraph(line[2:], styles['Heading1']))
                elif line.startswith('## '):
                    story.append(Paragraph(line[3:], styles['Heading2']))
                elif line.startswith('### '):
                    story.append(Paragraph(line[4:], styles['Heading3']))
                elif line.strip():
                    story.append(Paragraph(line, styles['Normal']))
                else:
                    story.append(Paragraph("<br/>", styles['Normal']))
            
            doc.build(story)
            return filename
        except Exception as e:
            st.error(f"DOCX generation error: {str(e)}")
            return None
    
    @staticmethod
    def create_cover_image(book_data):
        """Generate a simple cover image using Pillow"""
        try:
            # Create a simple cover
            img = Image.new('RGB', (1200, 1800), color=(41, 128, 185))
            
            # Save to file
            filename = f"ebook_data/cover_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            img.save(filename)
            return filename
        except Exception as e:
            st.error(f"Cover image error: {str(e)}")
            return None

# ========== SOCIAL MEDIA MANAGER ==========
class SocialMediaManager:
    def __init__(self):
        self.twitter_client = None
        # Initialize social media clients if API keys are available
        
    def post_to_twitter(self, message, image_path=None):
        """Post to Twitter/X"""
        try:
            # This is a placeholder - implement with actual Twitter API
            st.info(f"Twitter post ready: {message[:50]}...")
            return True
        except Exception as e:
            st.error(f"Twitter error: {str(e)}")
            return False
    
    def post_to_linkedin(self, message, image_path=None):
        """Post to LinkedIn"""
        try:
            st.info(f"LinkedIn post ready: {message[:50]}...")
            return True
        except Exception as e:
            st.error(f"LinkedIn error: {str(e)}")
            return False

# ========== PAYMENT INTEGRATION ==========
class PaymentManager:
    def __init__(self):
        self.stripe_client = None
        # Initialize Stripe if key available
        stripe_key = os.getenv("STRIPE_API_KEY")
        if stripe_key:
            stripe.api_key = stripe_key
            self.stripe_client = stripe
    
    def create_checkout_session(self, amount, description):
        """Create Stripe checkout session"""
        if not self.stripe_client:
            st.warning("Stripe not configured")
            return None
        
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': description,
                        },
                        'unit_amount': int(amount * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url='https://yourdomain.com/success',
                cancel_url='https://yourdomain.com/cancel',
            )
            return session.url
        except Exception as e:
            st.error(f"Stripe error: {str(e)}")
            return None

# ========== MAIN APPLICATION ==========
def main():
    st.set_page_config(
        page_title="EbookMaster Ultra Pro",
        page_icon="👑",
        layout="wide"
    )
    
    # Custom CSS
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
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 10px;
        font-weight: 600;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .export-btn {
        background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('<h1 class="main-header">📚 EbookMaster Ultra Pro</h1>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">🚀 Create Bestselling Books with AI • Global English Market</p>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: right; padding: 10px; background: #f8f9fa; border-radius: 10px;">
            <div style="color: #27ae60; font-weight: bold; font-size: 1.2rem;">💰 Profit Calculator</div>
            <div style="font-size: 0.9rem;">Est. Earnings: $500-$5,000/book</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'user_hash' not in st.session_state:
        st.session_state.user_hash = hashlib.md5(str(time.time()).encode()).hexdigest()[:12]
    
    if 'current_book' not in st.session_state:
        st.session_state.current_book = None
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ SETTINGS")
        
        with st.expander("🔑 API CONFIGURATION", expanded=True):
            groq_key = st.text_input("Groq API Key", type="password",
                                   help="Get free API key from console.groq.com")
            
            # Additional API keys
            openai_key = st.text_input("OpenAI API Key (Optional)", type="password")
            stripe_key = st.text_input("Stripe API Key (Optional)", type="password")
            
            if groq_key:
                st.success("✅ Groq API Ready")
                if openai_key:
                    st.success("✅ OpenAI API Ready")
                if stripe_key:
                    st.success("✅ Stripe API Ready")
            
            # Test API
            if st.button("Test Connection", type="secondary"):
                with st.spinner("Testing..."):
                    ai = AIPowerhouse(groq_key)
                    test = ai.call_ai("Test", "Hello", ai.models["gemma2"], 10)
                    if test and not test.startswith("Error"):
                        st.success("✅ Connection Successful!")
                    else:
                        st.error("❌ Connection Failed")
        
        with st.expander("👤 AUTHOR PROFILE", expanded=True):
            author_name = st.text_input("Author Name", "John Smith")
            author_bio = st.text_area("Author Bio", 
                                    "Bestselling author and expert in personal development. "
                                    "Helped thousands achieve extraordinary results.")
            author_website = st.text_input("Website", "https://authorwebsite.com")
        
        with st.expander("📖 BOOK CONFIGURATION", expanded=True):
            # Genre selection
            ai_helper = AIPowerhouse("")
            genre = st.selectbox(
                "Book Genre",
                list(ai_helper.genres.values()),
                index=0,
                help="Choose the genre that best fits your book"
            )
            
            # Writing style
            style = st.selectbox(
                "Writing Style",
                list(ai_helper.writing_styles.keys()),
                format_func=lambda x: x.title(),
                index=0
            )
            
            # Target audience
            target_audience = st.selectbox(
                "Target Audience",
                [
                    "Beginners looking to learn",
                    "Professionals seeking advancement",
                    "Entrepreneurs building businesses",
                    "Students and learners",
                    "General readers seeking transformation"
                ],
                index=1
            )
        
        with st.expander("⚡ GENERATION SETTINGS", expanded=False):
            chapters = st.slider("Number of Chapters", 5, 20, 10)
            words_per_chapter = st.slider("Words per Chapter", 1500, 5000, 2500)
            
            quality_preset = st.select_slider(
                "Quality Preset",
                options=["Fast", "Balanced", "High", "Maximum"],
                value="High"
            )
            
            # Quality adjustments
            if quality_preset == "Fast":
                temperature = 0.8
                max_tokens = 4000
            elif quality_preset == "Balanced":
                temperature = 0.75
                max_tokens = 6000
            elif quality_preset == "High":
                temperature = 0.7
                max_tokens = 8000
            else:  # Maximum
                temperature = 0.65
                max_tokens = 10000
        
        with st.expander("💰 MONETIZATION", expanded=False):
            st.info("Estimated Book Value Calculator")
            
            col1, col2 = st.columns(2)
            with col1:
                price = st.number_input("Price ($)", 4.99, 29.99, 9.99, 0.99)
            
            with col2:
                copies = st.number_input("Est. Monthly Copies", 10, 10000, 100, 10)
            
            monthly_revenue = price * copies
            st.metric("Estimated Monthly Revenue", f"${monthly_revenue:,.2f}")
            
            if monthly_revenue > 1000:
                st.success(f"🔥 Potential: ${monthly_revenue*12:,.0f}/year")
        
        with st.expander("📤 EXPORT SETTINGS", expanded=False):
            export_formats = st.multiselect(
                "Export Formats",
                ["PDF", "HTML", "EPUB", "DOCX"],
                default=["PDF", "HTML"]
            )
            
            include_cover = st.checkbox("Include Cover Image", True)
            watermark = st.checkbox("Add Watermark", False)
        
        # User stats
        db = BookDatabasePro()
        stats = db.get_user_stats(st.session_state.user_hash)
        
        if stats:
            st.divider()
            st.subheader("📊 YOUR STATS")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Books Created", stats[0])
            with col2:
                st.metric("Total Words", f"{stats[1]:,}")
            
            if stats[2]:
                st.metric("Est. Value", f"${stats[2]:,.2f}")
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🚀 CREATE BOOK", 
        "📖 PREVIEW", 
        "📤 EXPORT", 
        "📊 ANALYTICS", 
        "💰 MONETIZE", 
        "🎯 STRATEGY"
    ])
    
    with tab1:
        st.header("🚀 CREATE YOUR BESTSELLER")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            topic = st.text_area(
                "BOOK TOPIC / NICHE",
                height=150,
                placeholder="Example: Transforming from night owl to morning master\n"
                          "Example: Building a 7-figure online business from scratch\n"
                          "Example: Mastering cryptocurrency investing for beginners",
                help="Be specific! The more detailed, the better the book."
            )
            
            # Topic enhancement suggestions
            if topic:
                with st.expander("💡 TOPIC ENHANCEMENT SUGGESTIONS"):
                    st.write("Make your topic more compelling:")
                    st.code(f"From: '{topic}'\n"
                          f"To: 'The {topic} Blueprint: How to [Achieve Result] in [Timeframe]'\n"
                          f"Or: '{topic} Unleashed: The Proven System for [Benefit]'", 
                          language=None)
        
        with col2:
            st.markdown("### 🎯 SUCCESS TIPS")
            st.info("""
            **High-Profit Niches:**
            - Personal Development
            - Business & Money
            - Health & Wellness
            - Relationships
            - Technology/AI
            
            **What Sells:**
            - Problem → Solution
            - Step-by-Step Systems
            - Case Studies & Examples
            - Actionable Exercises
            """)
        
        # Generate button
        if st.button("✨ GENERATE COMPLETE BOOK", type="primary", use_container_width=True):
            if not groq_key:
                st.error("Please enter your Groq API Key in the sidebar")
                st.stop()
            
            if not topic.strip():
                st.error("Please enter a book topic")
                st.stop()
            
            # Initialize AI and DB
            ai = AIPowerhouse(groq_key)
            db = BookDatabasePro()
            
            # Progress tracking
            progress_bar = st.progress(0)
            status = st.empty()
            
            # STEP 1: Generate Outline
            status.text("📋 Creating bestselling outline...")
            outline = ai.generate_outline(topic, chapters, genre, style, target_audience)
            progress_bar.progress(10)
            
            if not outline:
                st.error("Failed to create outline")
                st.stop()
            
            st.session_state.outline = outline
            
            # Display outline
            with st.expander("📋 BOOK OUTLINE", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Title:** {outline['title']}")
                    st.markdown(f"**Subtitle:** {outline.get('subtitle', '')}")
                    st.markdown(f"**Genre:** {outline.get('genre', '')}")
                    st.markdown(f"**Target:** {outline.get('target_audience', '')}")
                
                with col2:
                    st.markdown(f"**Chapters:** {len(outline.get('chapters', []))}")
                    st.markdown(f"**Pages:** ~{outline.get('estimated_pages', 0)}")
                    st.markdown(f"**Potential:** {outline.get('bestseller_potential', '')}")
                    if outline.get('marketing_hook'):
                        st.markdown(f"**Hook:** {outline['marketing_hook']}")
                
                st.divider()
                st.markdown("### Chapter Breakdown")
                for ch in outline.get('chapters', [])[:5]:  # Show first 5
                    st.markdown(f"**{ch['number']}. {ch['title']}**")
                    st.caption(f"{ch['hook']}")
            
            # STEP 2: Generate Introduction
            status.text("✍️ Writing captivating introduction...")
            introduction = ai.generate_introduction(outline, style)
            progress_bar.progress(20)
            st.session_state.introduction = introduction
            
            # STEP 3: Generate Chapters
            chapters_content = []
            total_chapters = len(outline.get('chapters', []))
            
            for i, chapter in enumerate(outline.get('chapters', [])):
                progress = 20 + ((i + 1) / total_chapters * 60)
                progress_bar.progress(int(progress))
                status.text(f"📝 Writing Chapter {i+1}/{total_chapters}: {chapter['title'][:50]}...")
                
                chapter_content = ai.generate_chapter(
                    outline, 
                    chapter, 
                    words_per_chapter, 
                    style
                )
                
                if chapter_content:
                    chapters_content.append(chapter_content)
                    
                    # Quick preview
                    if i < 3:  # Show progress for first 3 chapters
                        st.success(f"✓ Chapter {i+1}: {chapter['title'][:30]}...")
            
            st.session_state.chapters = chapters_content
            
            # STEP 4: Generate Conclusion
            status.text("🎯 Writing powerful conclusion...")
            conclusion = ai.generate_conclusion(outline, style)
            progress_bar.progress(90)
            st.session_state.conclusion = conclusion
            
            # STEP 5: Assemble Book
            status.text("📦 Assembling complete book...")
            full_content = f"# INTRODUCTION\n\n{introduction}\n\n"
            
            for i, (chapter, content) in enumerate(zip(outline.get('chapters', []), chapters_content)):
                full_content += f"# CHAPTER {chapter['number']}: {chapter['title']}\n\n{content}\n\n"
            
            full_content += f"# CONCLUSION\n\n{conclusion}"
            
            st.session_state.full_content = full_content
            
            # STEP 6: Generate Marketing Package
            status.text("📢 Creating marketing assets...")
            marketing = ai.generate_marketing_package(outline)
            st.session_state.marketing = marketing
            
            # STEP 7: Generate Cover Concepts
            status.text("🎨 Designing cover concepts...")
            covers = ai.generate_cover_concepts(outline)
            st.session_state.covers = covers
            
            # STEP 8: Save to Database
            status.text("💾 Saving book...")
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
            
            try:
                book_id = db.save_book(book_data, st.session_state.user_hash)
                if book_id:
                    st.session_state.current_book_id = book_id
                    
                    # Generate sales simulation
                    sales_data = db.generate_sales_simulation(book_id)
                    st.session_state.sales_data = sales_data
                    
                    progress_bar.progress(100)
                    status.text("✅ BOOK CREATED SUCCESSFULLY!")
                    
                    # Success metrics
                    st.balloons()
                    st.success(f"🎉 **{outline['title']}** created successfully!")
                    
                    # Quick stats
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Words", f"{len(full_content.split()):,}")
                    with col2:
                        st.metric("Chapters", len(chapters_content))
                    with col3:
                        est_value = len(full_content.split()) * 0.05
                        st.metric("Est. Value", f"${est_value:,.2f}")
                    with col4:
                        est_pages = len(full_content.split()) // 250
                        st.metric("Pages", f"~{est_pages}")
                else:
                    st.error("Failed to save book to database!")
            except Exception as e:
                st.error(f"Error during save: {str(e)}")
    
    with tab2:
        st.header("📖 BOOK PREVIEW")
        
        if 'full_content' not in st.session_state:
            st.warning("Create a book first to see preview")
        else:
            preview_col, stats_col = st.columns([3, 1])
            
            with preview_col:
                # Book cover simulation
                if 'covers' in st.session_state and st.session_state.covers:
                    cover_concept = st.session_state.covers[0]
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, {cover_concept.get('colors', ['#2c3e50', '#3498db'])[0]} 0%, {cover_concept.get('colors', ['#2c3e50', '#3498db'])[1]} 100%);
                                padding: 40px; border-radius: 10px; text-align: center; color: white; margin-bottom: 20px;">
                        <h1 style="font-size: 2.5rem; margin-bottom: 10px;">{st.session_state.outline['title']}</h1>
                        <h2 style="font-size: 1.5rem; opacity: 0.9;">{st.session_state.outline.get('subtitle', '')}</h2>
                        <p style="margin-top: 30px;">by {author_name}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Content preview
                st.subheader("Introduction")
                st.markdown(st.session_state.introduction[:1000] + "..." 
                          if len(st.session_state.introduction) > 1000 
                          else st.session_state.introduction)
                
                if st.checkbox("Show full preview (first 5000 words)"):
                    st.markdown(st.session_state.full_content[:5000] + "...")
            
            with stats_col:
                st.markdown("### 📊 Book Stats")
                
                if 'outline' in st.session_state:
                    outline = st.session_state.outline
                    
                    st.metric("Genre", outline.get('genre', ''))
                    st.metric("Target Audience", outline.get('target_audience', ''))
                    st.metric("Bestseller Potential", outline.get('bestseller_potential', ''))
                    
                    if 'marketing' in st.session_state:
                        st.divider()
                        st.markdown("### 🎯 Marketing Score")
                        
                        # Calculate marketing score
                        marketing = st.session_state.marketing
                        score = 85  # Default score
                        
                        if len(marketing.get('keywords', [])) >= 5:
                            score += 5
                        if marketing.get('book_description', ''):
                            score += 10
                        
                        st.metric("Score", f"{score}/100")
                        
                        if score >= 80:
                            st.success("Ready to publish!")
                        elif score >= 60:
                            st.warning("Needs improvement")
                        else:
                            st.error("Needs major work")
    
    with tab3:
        st.header("📤 EXPORT BOOK")
        
        if 'full_content' not in st.session_state:
            st.warning("Create a book first to export")
        else:
            st.info("Export your book in multiple formats:")
            
            book_data = {
                'title': st.session_state.outline['title'],
                'subtitle': st.session_state.outline.get('subtitle', ''),
                'full_content': st.session_state.full_content
            }
            
            export_manager = EnhancedExportManager()
            db = BookDatabasePro()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("📄 Export as PDF", use_container_width=True):
                    with st.spinner("Generating PDF..."):
                        filename = export_manager.to_pdf(book_data, author_name)
                        if filename:
                            with open(filename, "rb") as file:
                                st.download_button(
                                    label="📥 Download PDF",
                                    data=file,
                                    file_name=f"{book_data['title'].replace(' ', '_')}.pdf",
                                    mime="application/pdf"
                                )
                            if st.session_state.get('current_book_id'):
                                db.log_export(st.session_state.current_book_id, "PDF", filename)
            
            with col2:
                if st.button("🌐 Export as HTML", use_container_width=True):
                    with st.spinner("Generating HTML..."):
                        html_content = export_manager.to_html(book_data, author_name)
                        st.download_button(
                            label="📥 Download HTML",
                            data=html_content,
                            file_name=f"{book_data['title'].replace(' ', '_')}.html",
                            mime="text/html"
                        )
                        if st.session_state.get('current_book_id'):
                            db.log_export(st.session_state.current_book_id, "HTML", "exported.html")
            
            with col3:
                if st.button("📱 Export as EPUB", use_container_width=True):
                    with st.spinner("Generating EPUB..."):
                        filename = export_manager.to_epub(book_data, author_name)
                        if filename:
                            with open(filename, "rb") as file:
                                st.download_button(
                                    label="📥 Download EPUB",
                                    data=file,
                                    file_name=f"{book_data['title'].replace(' ', '_')}.epub",
                                    mime="application/epub+zip"
                                )
                            if st.session_state.get('current_book_id'):
                                db.log_export(st.session_state.current_book_id, "EPUB", filename)
            
            with col4:
                if st.button("📝 Export as DOCX", use_container_width=True):
                    with st.spinner("Generating DOCX..."):
                        filename = export_manager.to_docx(book_data, author_name)
                        if filename:
                            with open(filename, "rb") as file:
                                st.download_button(
                                    label="📥 Download DOCX",
                                    data=file,
                                    file_name=f"{book_data['title'].replace(' ', '_')}.docx",
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                                )
                            if st.session_state.get('current_book_id'):
                                db.log_export(st.session_state.current_book_id, "DOCX", filename)
            
            # Social Media Sharing
            st.divider()
            st.subheader("📱 Share on Social Media")
            
            if 'marketing' in st.session_state:
                marketing = st.session_state.marketing
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🐦 Share on Twitter/X", use_container_width=True):
                        if marketing.get('social_media', {}).get('twitter'):
                            tweet = marketing['social_media']['twitter'][0]
                            st.code(tweet)
                            st.info("Copy and paste this to Twitter")
                
                with col2:
                    if st.button("💼 Share on LinkedIn", use_container_width=True):
                        st.info("Coming soon - LinkedIn integration")
    
    with tab4:
        st.header("📊 SALES ANALYTICS")
        
        if 'sales_data' not in st.session_state:
            st.info("Generate a book first to see sales projections")
        else:
            sales_data = st.session_state.sales_data
            
            # Convert to DataFrame
            df = pd.DataFrame(sales_data)
            
            # Summary metrics
            total_revenue = df['revenue'].sum()
            total_units = df['units'].sum()
            avg_monthly = df['revenue'].mean()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Revenue (12m)", f"${total_revenue:,.2f}")
            with col2:
                st.metric("Total Units Sold", f"{total_units:,}")
            with col3:
                st.metric("Avg Monthly Revenue", f"${avg_monthly:,.2f}")
            
            # Charts
            fig = go.Figure()
            
            # Revenue chart
            fig.add_trace(go.Scatter(
                x=df['month'],
                y=df['revenue'],
                mode='lines+markers',
                name='Revenue',
                line=dict(color='#3498db', width=3)
            ))
            
            fig.update_layout(
                title="12-Month Revenue Projection",
                xaxis_title="Month",
                yaxis_title="Revenue ($)",
                template="plotly_white",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Platform breakdown
            platform_df = df.groupby('platform').agg({
                'revenue': 'sum',
                'units': 'sum'
            }).reset_index()
            
            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(df.tail(6), use_container_width=True)
            
            with col2:
                st.dataframe(platform_df, use_container_width=True)
            
            # Download report
            csv = df.to_csv(index=False)
            st.download_button(
                "📥 Download Sales Report",
                csv,
                "sales_projection.csv",
                "text/csv"
            )
    
    with tab5:
        st.header("💰 MONETIZATION STRATEGY")
        
        st.markdown("""
        ## 🚀 MULTIPLE INCOME STREAMS
        
        ### 1. **DIRECT BOOK SALES**
        - **Amazon KDP**: 70% royalty ($6.99 per $9.99 book)
        - **Gumroad**: 95%+ royalty, direct to customer
        - **Website**: 100% profit, build email list
        - **Bundle Sales**: Package multiple books
        
        ### 2. **PREMIUM FORMATS**
        - **Audiobook**: $15-25 per copy (ACX/Audible)
        - **Workbook Edition**: Add $10-20 value
        - **Premium Hardcover**: $29.99-49.99
        - **Online Course**: $197-997 (based on book content)
        
        ### 3. **LEVERAGE STRATEGIES**
        - **Speaking Gigs**: $1,000-10,000 per talk
        - **Consulting**: $200-500/hour as "authority"
        - **Affiliate Offers**: Recommend tools/services
        - **Licensing**: Sell translation rights
        
        ## 💰 REALISTIC EARNINGS PROJECTION
        
        | Income Stream | Monthly Units | Price | Monthly Revenue | Annual |
        |--------------|---------------|-------|-----------------|--------|
        | Ebook Sales | 100 | $9.99 | $999 | $11,988 |
        | Audiobook | 50 | $19.99 | $999 | $11,988 |
        | Online Course | 10 | $297 | $2,970 | $35,640 |
        | **TOTAL** | | | **$4,968** | **$59,616** |
        
        > *Based on 1 bestselling book with proper marketing*
        """)
        
        # Monetization calculator
        st.divider()
        st.subheader("📈 EARNINGS CALCULATOR")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            ebook_price = st.number_input("Ebook Price", 2.99, 29.99, 9.99)
            ebook_sales = st.number_input("Monthly Ebook Sales", 0, 10000, 100)
        
        with col2:
            audiobook_price = st.number_input("Audiobook Price", 9.99, 49.99, 19.99)
            audiobook_sales = st.number_input("Monthly Audiobook Sales", 0, 5000, 50)
        
        with col3:
            course_price = st.number_input("Course Price", 97.0, 1997.0, 297.0)
            course_sales = st.number_input("Monthly Course Sales", 0, 1000, 10)
        
        # Calculate
        ebook_revenue = ebook_price * ebook_sales
        audio_revenue = audiobook_price * audiobook_sales
        course_revenue = course_price * course_sales
        total_monthly = ebook_revenue + audio_revenue + course_revenue
        
        st.metric("Total Monthly Revenue", f"${total_monthly:,.2f}")
        st.metric("Projected Annual Revenue", f"${total_monthly * 12:,.2f}")
        
        if total_monthly > 10000:
            st.success("🎉 **6-Figure Potential!** With proper marketing and scaling.")
        elif total_monthly > 5000:
            st.info("💰 **Solid Side Income!** Great foundation for full-time.")
        elif total_monthly > 1000:
            st.warning("📈 **Good Start!** Focus on marketing to scale.")
    
    with tab6:
        st.header("🎯 PUBLISHING STRATEGY")
        
        # Step-by-step guide
        steps = [
            ("1. FINALIZE & EDIT", """
            **Immediate Actions:**
            - Read through entire book (1-2 hours)
            - Fix any obvious errors
            - Add personal stories/anecdotes
            - Insert calls to action
            - Create chapter summaries
            
            **Professional Help (Optional):**
            - Editor: $500-$2,000
            - Proofreader: $300-$800
            - Formatter: $200-$500
            """),
            
            ("2. COVER DESIGN", """
            **Essential Elements:**
            - Professional cover ($200-$500)
            - Compelling title visible as thumbnail
            - Genre-appropriate design
            - Author name clearly displayed
            - Subtitle explaining benefit
            
            **Tools & Services:**
            - 99designs: $299-$599
            - Fiverr Pro: $150-$400
            - Canva Pro: $12.99/month (DIY)
            - Adobe Express: Free option
            """),
            
            ("3. PUBLISHING PLATFORMS", """
            **Primary Platforms (DO ALL):**
            1. **Amazon KDP** (Kindle & Paperback)
               - 70% royalty, global reach
            2. **Google Play Books**
               - Easy upload, Android users
            3. **Apple Books**
               - iOS users, good royalties
            4. **Kobo Writing Life**
               - International markets
            
            **Secondary Platforms:**
            - Barnes & Noble Press
            - Smashwords/Draft2Digital
            - Your own website (Gumroad)
            """),
            
            ("4. LAUNCH STRATEGY", """
            **Pre-Launch (2 weeks before):**
            - Build email list (free chapter)
            - Get reviews from ARC team
            - Social media teasers
            - Create landing page
            
            **Launch Week:**
            - Price at $0.99 or free (3 days)
            - Email sequence to list
            - Social media blitz
            - Amazon ads ($10/day)
            - Goodreads giveaway
            
            **Post-Launch:**
            - Collect reviews
            - Run promotions
            - Create audiobook
            - Plan next book
            """),
            
            ("5. MARKETING SYSTEM", """
            **Daily/Weekly Actions:**
            
            **Content Marketing:**
            - Blog posts from book chapters
            - YouTube videos explaining concepts
            - Podcast interviews
            - Medium articles
            
            **Social Media:**
            - Twitter/X: 3x daily
            - LinkedIn: Daily professional posts
            - Instagram: Visual quotes
            - TikTok: Short educational videos
            
            **Advertising:**
            - Amazon Ads: $5-20/day
            - Facebook Ads: $5-10/day
            - BookBub Featured Deal: $50-$500
            - Goodreads ads
            """),
            
            ("6. SCALE & AUTOMATE", """
            **Build Systems:**
            
            **Email Funnel:**
            1. Lead magnet (free chapter)
            2. Welcome sequence (5 emails)
            3. Nurture sequence (book value)
            4. Sales sequence (upsells)
            
            **Upsell Path:**
            - Book ($9.99)
            - Workbook ($19.99)
            - Audiobook ($24.99)
            - Course ($297)
            - Coaching ($997+)
            
            **Automation Tools:**
            - ConvertKit for email ($29/month)
            - Canva for graphics ($12.99/month)
            - Hootsuite for social ($49/month)
            - Amazon Ads automation
            """)
        ]
        
        for step_title, step_content in steps:
            with st.expander(f"📌 {step_title}", expanded=False):
                st.markdown(step_content)
        
        # Quick checklist
        st.divider()
        st.subheader("✅ PUBLISHING CHECKLIST")
        
        checklist = [
            ("Book fully edited and proofread", False),
            ("Professional cover designed", False),
            ("ISBN obtained (optional)", False),
            ("Amazon KDP account setup", False),
            ("Book description optimized", False),
            ("Keywords researched (7)", False),
            ("Categories selected (2)", False),
            ("Preview checked on multiple devices", False),
            ("Launch email sequence ready", False),
            ("Social media graphics created", False),
            ("ARC reviewers lined up", False),
            ("Launch price strategy set", False)
        ]
        
        for item, checked in checklist:
            st.checkbox(item, checked)

# Run the app
if __name__ == "__main__":
    main()
