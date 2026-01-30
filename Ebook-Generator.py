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

# إعدادات الصفحة الأصلية
st.set_page_config(
    page_title="📚 EbookMaster Ultra Pro",
    page_icon="👑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== ENHANCED AI MODELS (الكلاس الأصلي القوي) ==========
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
                    "top_p": 0.9
                },
                timeout=120
            )
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            return f"Error: {response.status_code}"
        except Exception as e:
            return f"Error: {str(e)}"

    def generate_outline(self, topic, chapters, genre, style, target_audience):
        system_prompt = "You are a professional book architect. Return ONLY valid JSON."
        user_prompt = f"Create a detailed book outline for '{topic}'. Total {chapters} chapters. Style: {style}. Return JSON with 'title', 'subtitle', and a list named 'chapters' containing 'number', 'title', 'hook', and 'key_points'."
        
        result = self.call_ai(system_prompt, user_prompt, self.models["llama3_70b"], 4000, 0.7)
        try:
            # تنظيف الـ JSON من أي نصوص زائدة
            clean_json = re.search(r'\{.*\}', result, re.DOTALL).group()
            return json.loads(clean_json)
        except:
            return self.create_fallback_outline(topic, chapters, genre)

    def create_fallback_outline(self, topic, chapters, genre):
        return {
            "title": f"The Mastery of {topic}",
            "subtitle": "A Comprehensive Guide",
            "chapters": [{"number": i+1, "title": f"The Foundations of {topic} Part {i+1}", "hook": "Essential insights.", "key_points": ["Point A", "Point B"]} for i in range(chapters)]
        }

    def generate_chapter(self, book_info, chapter_info, word_count, style):
        system_prompt = f"You are a professional {style} writer. Write in English."
        user_prompt = f"Write a full chapter for '{book_info['title']}'. Chapter {chapter_info['number']}: {chapter_info['title']}. Hook: {chapter_info['hook']}. Points: {', '.join(chapter_info['key_points'])}. Length: {word_count} words."
        return self.call_ai(system_prompt, user_prompt, self.models["llama3_70b"], 8000, 0.75)

# ========== DATABASE (نفس الكود الأصلي) ==========
class BookDatabasePro:
    def __init__(self):
        os.makedirs("ebook_data", exist_ok=True)
        self.conn = sqlite3.connect('ebook_data/ebooks_pro.db', check_same_thread=False)
        self.create_tables()
    def create_tables(self):
        self.conn.execute('CREATE TABLE IF NOT EXISTS books (id INTEGER PRIMARY KEY, title TEXT, content BLOB, user_hash TEXT, created_at TIMESTAMP)')
        self.conn.commit()
    def save_book(self, title, content, user_hash):
        self.conn.execute('INSERT INTO books (title, content, user_hash, created_at) VALUES (?, ?, ?, ?)', (title, pickle.dumps(content), user_hash, datetime.now()))
        self.conn.commit()

# ========== MAIN APP ==========
def main():
    # الـ CSS الجميل الخاص بك
    st.markdown("""<style>.main-header { font-size: 3rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }</style>""", unsafe_allow_html=True)
    st.markdown('<h1 class="main-header">📚 EbookMaster Ultra Pro</h1>', unsafe_allow_html=True)

    with st.sidebar:
        st.header("⚙️ SETTINGS")
        groq_key = st.text_input("Groq API Key", type="password")
        author_name = st.text_input("Author Name", "John Smith")
        genre = st.selectbox("Genre", ["Business", "Self-Help", "Tech"])
        style = st.selectbox("Writing Style", ["bestseller", "professional", "conversational"])
        num_chapters = st.slider("Chapters", 5, 15, 8)
        words_per_ch = st.slider("Words/Chapter", 1000, 4000, 2000)

    tab1, tab2, tab3 = st.tabs(["🚀 CREATE BOOK", "📖 PREVIEW", "📊 ANALYTICS"])

    with tab1:
        topic = st.text_area("BOOK TOPIC", placeholder="e.g. TikTok for Business")
        if st.button("✨ GENERATE COMPLETE BOOK", type="primary", use_container_width=True):
            if not groq_key: st.error("Please add API Key"); st.stop()
            
            ai = AIPowerhouse(groq_key)
            db = BookDatabasePro()
            
            # --- PROGRESS ---
            progress_bar = st.progress(0)
            status = st.empty()

            # 1. Outline
            status.info("📋 Planning Book Structure...")
            outline = ai.generate_outline(topic, num_chapters, genre, style, "Global Audience")
            st.session_state.outline = outline
            progress_bar.progress(15)

            # التأكد من عدم حدوث KeyError
            if 'chapters' not in outline:
                st.error("Outline format error. Retrying with fallback...")
                outline = ai.create_fallback_outline(topic, num_chapters, genre)

            # 2. Chapters Generation (إصلاح الـ Loop)
            chapters_content = []
            for i, ch in enumerate(outline['chapters']):
                status.warning(f"✍️ Writing Chapter {i+1}/{len(outline['chapters'])}: {ch['title']}...")
                content = ai.generate_chapter(outline, ch, words_per_ch, style)
                chapters_content.append(f"## {ch['title']}\n\n{content}")
                
                # تحديث البروجرس
                progress = 15 + int(((i + 1) / len(outline['chapters'])) * 75)
                progress_bar.progress(progress)

            # 3. Finalizing
            full_book = f"# {outline['title']}\n\nBy {author_name}\n\n" + "\n\n".join(chapters_content)
            st.session_state.full_content = full_book
            db.save_book(outline['title'], full_book, "user_001")
            
            progress_bar.progress(100)
            status.success("✅ Ebook Generated Successfully!")
            st.balloons()

    with tab2:
        if 'full_content' in st.session_state:
            st.markdown(st.session_state.full_content)
            st.download_button("📥 Download TXT", st.session_state.full_content, "my_ebook.txt")
        else:
            st.info("Your book preview will appear here.")

if __name__ == "__main__":
    main()
