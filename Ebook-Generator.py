import streamlit as st
import requests
import json
from datetime import datetime
import re

st.set_page_config(
    page_title="EbookMaster Ultra v2",
    page_icon="👑",
    layout="wide"
)

# CSS (يبقى كما هو لأنه ممتاز)
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
        system_prompt = "You are a world-class book architect and strategist."
        prompt = f"""Create a deep, non-generic book outline for:
Title: {title}
Topic: {topic}
Audience: {audience}
Tone: {tone}
Chapters: {num_chapters}

Requirements:
1. Each chapter summary must focus on a UNIQUE phase (No overlap).
2. Ensure a logical progression from theory to advanced execution.

Return ONLY JSON:
{{
  "title": "{title}",
  "subtitle": "A Specific & High-Value Subtitle",
  "tagline": "One sentence magnetic hook",
  "description": "Short compelling blurb",
  "chapters": [
    {{
      "number": 1,
      "title": "Clear Actionable Title",
      "summary": "Deep technical summary of what will be taught",
      "sections": [
        {{ "title": "Section Name", "key_points": ["Specific point 1", "Specific point 2"] }}
      ]
    }}
  ]
}}"""
        result = self.call_ai(system_prompt, prompt, max_tokens=4000)
        if result:
            try:
                cleaned = result.strip().replace('```json', '').replace('```', '').strip()
                return json.loads(cleaned)
            except: return None
        return None
    
    def generate_chapter(self, outline, chapter_num, tone, word_count, previous_titles):
        chapter = outline['chapters'][chapter_num - 1]
        
        # تحسين الـ System Prompt لمنع التكرار
        system_prompt = f"""You are a bestselling technical author. 
        CRITICAL RULES: 
        1. NO REPETITION: Do not repeat concepts or intros from previous chapters: {previous_titles}.
        2. NO FLUFF: Skip the "In this chapter" or "In today's world" intros. Dive straight into the facts.
        3. FORMAT: Use H2 (##) and H3 (###). Use bold for emphasis. 
        4. VALUE: Every chapter MUST have 1 'Step-by-Step' guide and 1 'Pro-Tip' box."""

        prompt = f"""Write Chapter {chapter_num} of "{outline['title']}":
Chapter Title: {chapter['title']}
Context/Summary: {chapter['summary']}
Target Word Count: {word_count}
Tone: {tone}

Requirements:
- Start directly with the first sub-heading.
- Provide deep, actionable technical details.
- Include 3 real-world examples.
- End with a brief 'Chapter Summary' checklist."""

        return self.call_ai(system_prompt, prompt, max_tokens=5000)

    def generate_introduction(self, outline, tone):
        system_prompt = "You are an expert in persuasion and psychological hooks."
        prompt = f"""Write a compelling 800-word introduction for "{outline['title']}".
        Focus on the 'Why' and the 'Pain Points' of the reader. 
        Explain exactly what they will achieve by the end. 
        Tone: {tone}. Use Markdown."""
        return self.call_ai(system_prompt, prompt, max_tokens=2500)

    def generate_conclusion(self, outline, tone):
        system_prompt = "You are a motivational coach and strategist."
        prompt = f"""Write a powerful 600-word conclusion for "{outline['title']}".
        Summarize the transformation. Provide a clear 'Next Step' call to action.
        Tone: {tone}. Inspiring and final."""
        return self.call_ai(system_prompt, prompt, max_tokens=2000)

def create_premium_html(outline, content, author):
    # (دالة الـ HTML تبقى كما هي)
    html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><title>{outline['title']}</title>
    <style>body{{font-family: 'Segoe UI', serif; line-height: 1.8; max-width: 850px; margin: 0 auto; padding: 50px; color: #2d3436;}}
    .cover{{background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 120px 40px; text-align: center; border-radius: 20px; margin-bottom: 50px;}}
    h1{{font-size: 3.5rem; margin-bottom: 10px;}} h2{{font-weight: 300; opacity: 0.9;}}
    h2.ch-title{{color: #6c5ce7; border-bottom: 2px solid #eee; padding-bottom: 10px; margin-top: 50px;}}
    .pro-tip{{background: #f1f2f6; border-left: 5px solid #6c5ce7; padding: 20px; margin: 20px 0; font-style: italic;}}
    </style></head><body>
    <div class="cover"><h1>{outline['title']}</h1><h2>{outline['subtitle']}</h2><p>By {author}</p></div>
    <div>{content}</div>
    <footer style="margin-top: 100px; border-top: 1px solid #eee; padding-top: 20px; text-align: center;">© {datetime.now().year} {author}</footer>
    </body></html>"""
    return html

def main():
    st.markdown("""<div class="hero-section"><h1>👑 EbookMaster Ultra v2</h1><p>Professional Content, Zero Fluff</p></div>""", unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("⚙️ Settings")
        groq_key = st.text_input("🤖 Groq API Key", type="password")
        author = st.text_input("✍️ Author", "Expert Author")
        audience = st.selectbox("👥 Audience", ["Beginners", "Everyone", "Professionals", "Advanced Users"])
        tone = st.selectbox("🎭 Tone", ["Professional", "Conversational", "Aggressive/Bold", "Academic"])
        num_chapters = st.slider("📑 Chapters", 3, 15, 6)
        word_count = st.slider("📏 Words/Chapter", 800, 3000, 1200)

    tab1, tab2, tab3 = st.tabs(["📝 Create", "📖 Preview", "💾 Export"])
    
    with tab1:
        topic = st.text_area("What is your book about?", height=100)
        
        if st.button("🚀 Generate High-Value Book", type="primary", use_container_width=True):
            if not groq_key or not topic:
                st.error("❌ Fill all fields!")
                return
            
            master = EbookMasterUltra(groq_key)
            status = st.empty()
            progress = st.progress(0)
            
            # Outline
            status.info("📋 Architecting the outline (Sequential Logic)...")
            outline = master.generate_outline(topic, topic, num_chapters, audience, tone)
            
            if not outline:
                st.error("❌ Error generating outline. Check Key.")
                return
            
            st.session_state.outline = outline
            progress.progress(10)
            
            # Intro
            status.info("✍️ Crafting the Introduction...")
            intro = master.generate_introduction(outline, tone)
            st.session_state.introduction = intro
            progress.progress(20)
            
            # Sequential Chapter Generation
            chapters = []
            previous_titles = []
            for i in range(1, num_chapters + 1):
                status.info(f"✍️ Writing Chapter {i}: {outline['chapters'][i-1]['title']}...")
                
                # نمرر عناوين الفصول السابقة لمنع التكرار
                content = master.generate_chapter(outline, i, tone, word_count, previous_titles)
                if content:
                    chapters.append(content)
                    previous_titles.append(outline['chapters'][i-1]['title'])
                    st.success(f"✅ Finished Chapter {i}")
                
                prog_val = 20 + int((i / num_chapters) * 70)
                progress.progress(prog_val)
            
            st.session_state.chapters = chapters
            
            # Conclusion
            status.info("🎯 Finalizing with Conclusion...")
            conclusion = master.generate_conclusion(outline, tone)
            st.session_state.conclusion = conclusion
            progress.progress(100)
            status.empty()
            
            st.markdown('<div class="success-banner">🎉 Your Premium Ebook is Ready!</div>', unsafe_allow_html=True)

    # (باقي كود الـ Preview و Export يبقى كما هو في نسختك الأصلية)
    with tab2:
        if 'outline' in st.session_state:
            outline = st.session_state.outline
            st.markdown(f'<div class="cover-preview"><h1>{outline["title"]}</h1><p>By {author}</p></div>', unsafe_allow_html=True)
            if 'introduction' in st.session_state:
                with st.expander("Show Introduction"): st.markdown(st.session_state.introduction)
            for i, ch in enumerate(st.session_state.get('chapters', []), 1):
                with st.expander(f"Chapter {i}: {outline['chapters'][i-1]['title']}"): st.markdown(ch)
            if 'conclusion' in st.session_state:
                with st.expander("Show Conclusion"): st.markdown(st.session_state.conclusion)
        else: st.info("Start by generating a book in the 'Create' tab.")

    with tab3:
        if 'outline' in st.session_state:
            full_md = f"# {st.session_state.outline['title']}\n\n"
            full_md += f"## Introduction\n\n{st.session_state.introduction}\n\n"
            for ch in st.session_state.chapters: full_md += f"{ch}\n\n"
            full_md += f"## Conclusion\n\n{st.session_state.conclusion}"
            
            html = create_premium_html(st.session_state.outline, full_md.replace('\n', '<br>'), author)
            
            st.download_button("📄 Download HTML", html, "ebook.html", "text/html", use_container_width=True)
            st.download_button("📝 Download Markdown", full_md, "ebook.md", use_container_width=True)
        else: st.info("Generate content first.")

if __name__ == "__main__":
    main()
