import streamlit as st
import requests
import json
from datetime import datetime
import re
import sqlite3
import pickle
import time
import hashlib
from functools import lru_cache
import os
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="📚 EbookMaster Ultra Pro",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== ENHANCED AI MODELS ==========
class AIPowerhouse:
    def __init__(self, groq_api_key):
        self.groq_api_key = groq_api_key
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        
        self.models = {
            "llama3_70b": "llama-3.3-70b-versatile",
            "llama3_8b": "llama-3.1-8b-instant",
            "mixtral": "mixtral-8x7b-32768",
            "gemma2": "gemma2-9b-it"
        }
        
        self.writing_styles = {
            "bestseller": "Write like a New York Times bestselling author",
            "professional": "Write like an industry expert with 20+ years experience",
            "conversational": "Write like a friend giving advice over coffee",
            "academic": "Write with academic rigor and citations",
            "persuasive": "Write to convince and convert readers",
            "storytelling": "Write with compelling narrative and characters"
        }
        
        self.genres = {
            "self_help": "Self-Help & Personal Development",
            "business": "Business & Entrepreneurship",
            "health": "Health & Wellness",
            "finance": "Finance & Investing",
            "technology": "Technology & AI",
            "fiction": "Fiction & Storytelling",
            "education": "Educational & How-To"
        }
    
    def select_model_for_task(self, task, genre, target_audience):
        if "outline" in task or "structure" in task:
            return self.models["llama3_70b"]
        elif "creative" in genre or "fiction" in genre:
            return self.models["mixtral"]
        elif "technical" in genre or "academic" in genre:
            return self.models["llama3_70b"]
        else:
            return self.models["gemma2"]
    
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

    def generate_outline(self, topic, chapters, genre, style, target_audience):
        model = self.select_model_for_task("outline", genre, target_audience)
        system_prompt = "You are a professional book architect. Create compelling, market-ready book outlines. Return ONLY valid JSON."
        user_prompt = f"Create a bestselling book outline for: {topic}. Genre: {genre}. Style: {style}. Chapters: {chapters}. Return JSON structure."
        
        result = self.call_ai(system_prompt, user_prompt, model, 4000, 0.7)
        if result and not result.startswith("Error"):
            try:
                if '```json' in result: result = result.split('```json')[1].split('```')[0].strip()
                elif '```' in result: result = result.split('```')[1].strip()
                outline = json.loads(result)
                outline['generated_at'] = datetime.now().isoformat()
                outline['ai_model'] = model
                return outline
            except: pass
        return self.create_fallback_outline(topic, chapters, genre)

    def create_fallback_outline(self, topic, chapters, genre):
        # ... (نفس الـ fallback اللي عندك)
        return {"title": f"The Complete Guide to {topic}", "chapters": [{"number": i+1, "title": f"Chapter {i+1}", "hook": "...", "key_points": []} for i in range(chapters)]}

    def generate_introduction(self, book_info, style):
        return self.call_ai("You write magnetic introductions.", f"Write intro for {book_info['title']}", self.models["llama3_70b"], 3000, 0.8)

    def generate_chapter(self, book_info, chapter_info, word_count, style):
        model = self.select_model_for_task("chapter", book_info.get('genre', 'self_help'), book_info.get('target_audience', 'general'))
        # تحسين الـ prompt لضمان جودة عالية في كل فصل على حدة
        system_prompt = f"You are a {style} ghostwriter. Write detailed chapters with Markdown."
        user_prompt = f"Write Chapter {chapter_info['number']}: {chapter_info['title']} for '{book_info['title']}'."
        return self.call_ai(system_prompt, user_prompt, model, 8000, 0.8)

    def generate_conclusion(self, book_info, style):
        return self.call_ai("You write inspiring conclusions.", f"Write conclusion for {book_info['title']}", self.models["mixtral"], 2500, 0.85)

    def generate_marketing_package(self, book_info):
        result = self.call_ai("You are a book marketing expert.", f"Create marketing JSON for {book_info['title']}", self.models["llama3_70b"], 8000, 0.7)
        try:
            if '```json' in result: result = result.split('```json')[1].split('```')[0].strip()
            return json.loads(result)
        except: return {"book_description": "Marketing asset ready."}

    def generate_cover_concepts(self, book_info):
        return [{"name": "Professional", "colors": ["#000", "#fff"]}]

# ========== ENHANCED DATABASE & EXPORT (نفس الكلاسات ديالك) ==========
class BookDatabasePro:
    def __init__(self):
        os.makedirs("ebook_data", exist_ok=True)
        self.conn = sqlite3.connect('ebook_data/ebooks_pro.db')
        self.create_tables()
    def create_tables(self):
        self.conn.execute('CREATE TABLE IF NOT EXISTS books (id INTEGER PRIMARY KEY, title TEXT, subtitle TEXT, topic TEXT, genre TEXT, content BLOB, word_count INTEGER, chapters INTEGER, style TEXT, target_audience TEXT, marketing_package BLOB, cover_concepts BLOB, estimated_value REAL, created_at TIMESTAMP, user_hash TEXT)')
        self.conn.execute('CREATE TABLE IF NOT EXISTS user_analytics (user_hash TEXT PRIMARY KEY, total_books INTEGER, total_words INTEGER, estimated_earnings REAL, last_active TIMESTAMP)')
        self.conn.commit()
    def save_book(self, book_data, user_hash):
        content_blob = pickle.dumps(book_data)
        marketing_blob = pickle.dumps(book_data.get('marketing_package', {}))
        covers_blob = pickle.dumps(book_data.get('cover_concepts', []))
        self.conn.execute('INSERT INTO books (title, topic, content, word_count, created_at, user_hash) VALUES (?, ?, ?, ?, ?, ?)', 
                         (book_data['outline']['title'], book_data.get('topic'), content_blob, book_data.get('word_count'), datetime.now(), user_hash))
        self.conn.commit()
        return self.conn.lastrowid
    def get_user_stats(self, user_hash):
        return self.conn.execute('SELECT total_books, total_words, estimated_earnings FROM user_analytics WHERE user_hash=?', (user_hash,)).fetchone()
    def generate_sales_simulation(self, book_id):
        return [{"month": "Jan", "revenue": 500, "units": 50, "platform": "Amazon"}]

# ========== APP MAIN ==========
def main():
    # ... (نفس إعدادات الواجهة والـ CSS)
    st.markdown('<h1 class="main-header">📚 EbookMaster Ultra Pro</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        groq_key = st.text_input("Groq API Key", type="password")
        author_name = st.text_input("Author Name", "John Smith")
        genre = st.selectbox("Genre", ["Business", "Self-Help", "Technology"])
        style = st.selectbox("Style", ["professional", "bestseller"])
        chapters_count = st.slider("Chapters", 5, 20, 10)
        words_per_chapter = st.slider("Words", 1000, 5000, 2500)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🚀 CREATE BOOK", "📖 PREVIEW", "📊 ANALYTICS", "💰 MONETIZE", "🎯 STRATEGY"])

    with tab1:
        topic = st.text_area("BOOK TOPIC / NICHE")
        if st.button("✨ GENERATE COMPLETE BOOK", type="primary", use_container_width=True):
            if not groq_key: st.error("API Key Required"); st.stop()
            
            ai = AIPowerhouse(groq_key)
            db = BookDatabasePro()
            progress_bar = st.progress(0)
            status = st.empty()

            # 1. Outline
            status.text("📋 Creating Outline...")
            outline = ai.generate_outline(topic, chapters_count, genre, style, "General")
            st.session_state.outline = outline
            progress_bar.progress(10)

            # 2. Intro
            status.text("✍️ Writing Introduction...")
            introduction = ai.generate_introduction(outline, style)
            st.session_state.introduction = introduction
            progress_bar.progress(20)

            # 3. Chapters (Loop Fix for Error 400)
            chapters_content = []
            for i, ch in enumerate(outline['chapters']):
                status.text(f"📝 Chapter {i+1}/{len(outline['chapters'])}: {ch['title']}")
                content = ai.generate_chapter(outline, ch, words_per_chapter, style)
                chapters_content.append(content)
                progress_bar.progress(20 + int((i+1)/len(outline['chapters']) * 60))
            
            st.session_state.chapters = chapters_content

            # 4. Conclusion & Assembly
            status.text("🎯 Finishing...")
            conclusion = ai.generate_conclusion(outline, style)
            full_content = f"# {outline['title']}\n\n{introduction}\n\n"
            for c_info, c_body in zip(outline['chapters'], chapters_content):
                full_content += f"## {c_info['title']}\n\n{c_body}\n\n"
            full_content += f"# CONCLUSION\n\n{conclusion}"
            
            st.session_state.full_content = full_content
            
            # Save & Success
            db.save_book({'outline': outline, 'full_content': full_content, 'word_count': len(full_content.split())}, "user_123")
            st.session_state.sales_data = db.generate_sales_simulation(1)
            progress_bar.progress(100)
            st.balloons()
            st.success("✅ Complete!")

    with tab3:
        if 'sales_data' in st.session_state:
            df = pd.DataFrame(st.session_state.sales_data)
            fig = go.Figure(go.Scatter(x=df['month'], y=df['revenue'], mode='lines+markers'))
            st.plotly_chart(fig)

if __name__ == "__main__":
    main()
