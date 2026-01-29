import streamlit as st
import requests
import json
from datetime import datetime
import re

st.set_page_config(
    page_title="EbookMaster Ultra",
    page_icon="👑",
    layout="wide"
)

# CSS (البنية والتصميم بقاو هما هما)
st.markdown("""
<style>
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
    }
</style>
""", unsafe_allow_html=True)

class EbookMasterUltra:
    def __init__(self, groq_api_key):
        self.groq_api_key = groq_api_key
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.3-70b-versatile"
    
    def call_ai(self, system_prompt, user_prompt, max_tokens=4000, temperature=0.6):
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
                timeout=90
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            return None
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return None
    
    def generate_outline(self, topic, title, num_chapters, audience, tone):
        # منع التكرار من البداية في الهيكل
        system_prompt = "You are a professional book architect."
        prompt = f"""Create a deep book outline for:
Title: {title}
Topic: {topic}
Audience: {audience}
Tone: {tone}
Chapters: {num_chapters}

Return JSON with "title", "subtitle", "tagline", "description", and "chapters" (each with "title", "summary").
Ensure each chapter covers a unique stage of the process with ZERO overlap."""

        result = self.call_ai(system_prompt, prompt, max_tokens=4000)
        if result:
            try:
                cleaned = result.strip().replace('```json', '').replace('```', '').strip()
                return json.loads(cleaned)
            except: return None
        return None
    
    def generate_chapter(self, outline, chapter_num, tone, word_count, previous_chapters_titles):
        chapter = outline['chapters'][chapter_num - 1]
        
        # هنا تم تعديل المنطق لمنع الرموز الكثيرة والتكرار
        system_prompt = f"""You are a professional author. 
        RULES:
        1. NO EXCESSIVE SYMBOLS: Use bolding (**) only for key terms, not entire sentences.
        2. NO REPETITION: Do not repeat introductions or concepts already discussed in: {previous_chapters_titles}.
        3. CLEAN FORMAT: Use ## for chapter titles and ### for sub-sections. No other special symbols.
        4. START IMMEDIATELY: No "In this chapter" fluff. Dive into the content.
        5. Provide real examples and a clean 'Pro-Tip' box at the end."""

        prompt = f"""Write Chapter {chapter_num}: {chapter['title']}
        Summary to cover: {chapter['summary']}
        Target: {word_count} words.
        Tone: {tone}."""

        return self.call_ai(system_prompt, prompt, max_tokens=5000)
    
    def generate_introduction(self, outline, tone):
        system_prompt = "You are an expert at writing compelling book introductions."
        prompt = f"""Write a professional introduction for "{outline['title']}".
        Focus on the problem and the solution.
        Avoid too many bold symbols. Keep it clean and readable.
        Tone: {tone}."""
        return self.call_ai(system_prompt, prompt, max_tokens=2500)
    
    def generate_conclusion(self, outline, tone):
        system_prompt = "You are skilled at writing powerful book conclusions."
        prompt = f"""Write a conclusion for "{outline['title']}".
        Summarize the transformation and provide a clear call to action.
        Tone: {tone}. Clean formatting only."""
        return self.call_ai(system_prompt, prompt, max_tokens=2000)

def create_premium_html(outline, content, author):
    # نفس دالة HTML مع تحسين بسيط في الخطوط للقراءة
    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 40px; color: #333; }}
        .cover {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 80px 40px; text-align: center; border-radius: 15px; }}
        h1 {{ font-size: 2.5rem; }}
        h2 {{ color: #764ba2; margin-top: 30px; border-bottom: 1px solid #eee; padding-bottom: 10px; }}
        h3 {{ color: #444; }}
        .pro-tip {{ background: #f9f9f9; border-left: 5px solid #764ba2; padding: 15px; margin: 20px 0; }}
    </style></head><body>
    <div class="cover"><h1>{outline['title']}</h1><p>By {author}</p></div>
    <div style="margin-top: 50px;">{content}</div>
    <footer style="margin-top: 50px; text-align: center; font-size: 0.8rem;">© {datetime.now().year} {author}</footer>
    </body></html>"""
    return html

def main():
    st.markdown("""<div class="hero-section"><h1>👑 EbookMaster Ultra</h1><p>High-Quality, Professional Ebooks</p></div>""", unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("⚙️ Settings")
        groq_key = st.text_input("🤖 Groq API Key", type="password")
        author = st.text_input("✍️ Author", "Moh del")
        audience = st.selectbox("👥 Audience", ["Beginners", "Everyone", "Professionals"])
        tone = st.selectbox("🎭 Tone", ["Professional", "Conversational", "Motivational"])
        num_chapters = st.slider("📑 Chapters", 3, 15, 6)
        word_count = st.slider("📏 Words/Chapter", 800, 3000, 1200)

    tab1, tab2, tab3 = st.tabs(["📝 Create", "📖 Preview", "💾 Export"])
    
    with tab1:
        topic = st.text_area("What's your book about?", height=100)
        if st.button("🚀 Generate Book", type="primary", use_container_width=True):
            if not groq_key or not topic:
                st.error("❌ Fill all fields!")
                return
            
            master = EbookMasterUltra(groq_key)
            progress = st.progress(0)
            status = st.empty()
            
            # Outline
            status.info("📋 Planning the structure...")
            outline = master.generate_outline(topic, topic, num_chapters, audience, tone)
            st.session_state.outline = outline
            progress.progress(10)
            
            # Introduction
            status.info("✍️ Writing introduction...")
            intro = master.generate_introduction(outline, tone)
            st.session_state.introduction = intro
            progress.progress(20)
            
            # Chapters
            chapters = []
            prev_titles = []
            for i in range(1, num_chapters + 1):
                status.info(f"✍️ Writing Chapter {i}/{num_chapters}...")
                chapter_content = master.generate_chapter(outline, i, tone, word_count, prev_titles)
                if chapter_content:
                    chapters.append(chapter_content)
                    prev_titles.append(outline['chapters'][i-1]['title'])
                progress.progress(20 + int((i/num_chapters)*70))
            
            st.session_state.chapters = chapters
            
            # Conclusion
            status.info("🎯 Finalizing...")
            st.session_state.conclusion = master.generate_conclusion(outline, tone)
            progress.progress(100)
            status.empty()
            st.markdown('<div class="success-banner">🎉 Book Complete!</div>', unsafe_allow_html=True)

    with tab2:
        if 'outline' in st.session_state:
            st.markdown(f"## {st.session_state.outline['title']}")
            if 'introduction' in st.session_state:
                with st.expander("Introduction"): st.markdown(st.session_state.introduction)
            for i, ch in enumerate(st.session_state.chapters, 1):
                with st.expander(f"Chapter {i}: {st.session_state.outline['chapters'][i-1]['title']}"):
                    st.markdown(ch)
            if 'conclusion' in st.session_state:
                with st.expander("Conclusion"): st.markdown(st.session_state.conclusion)
        else: st.info("Generate a book first.")

    with tab3:
        if 'outline' in st.session_state:
            full_content = f"# {st.session_state.outline['title']}\n\n## Introduction\n{st.session_state.introduction}\n\n"
            for ch in st.session_state.chapters: full_content += f"{ch}\n\n"
            full_content += f"## Conclusion\n{st.session_state.conclusion}"
            
            html = create_premium_html(st.session_state.outline, full_content.replace('\n', '<br>'), author)
            st.download_button("📄 Download HTML", html, "ebook.html", "text/html", use_container_width=True)
            st.download_button("📝 Download Markdown", full_content, "ebook.md", use_container_width=True)
        else: st.info("Generate a book first.")

if __name__ == "__main__":
    main()
