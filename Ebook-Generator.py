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

# CSS
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
    
    .stat-card {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

class EbookMasterUltra:
    def __init__(self, groq_api_key):
        self.groq_api_key = groq_api_key
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.3-70b-versatile"
    
    def call_ai(self, system_prompt, user_prompt, max_tokens=4000, temperature=0.7):
        """استدعاء AI"""
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
            st.error(f"Error: {str(e)}")
            return None
    
    def generate_outline(self, topic, title, num_chapters, audience, tone):
        """توليد الهيكل"""
        
        prompt = f"""Create a book outline for:

Title: {title}
Topic: {topic}
Audience: {audience}
Tone: {tone}
Chapters: {num_chapters}

Return JSON:
{{
  "title": "{title}",
  "subtitle": "subtitle",
  "tagline": "tagline",
  "description": "description",
  "chapters": [
    {{
      "number": 1,
      "title": "Chapter Title",
      "summary": "summary",
      "sections": [
        {{
          "title": "Section",
          "key_points": ["point1", "point2"]
        }}
      ]
    }}
  ]
}}

Return ONLY JSON."""

        result = self.call_ai(
            "You are a bestselling book architect.",
            prompt,
            max_tokens=4000
        )
        
        if result:
            try:
                cleaned = result.strip().replace('```json', '').replace('```', '').strip()
                return json.loads(cleaned)
            except:
                return None
        return None
    
    def generate_chapter(self, outline, chapter_num, tone, word_count):
        """توليد فصل"""
        
        chapter = outline['chapters'][chapter_num - 1]
        
        prompt = f"""Write Chapter {chapter_num} of "{outline['title']}":

Title: {chapter['title']}
Summary: {chapter['summary']}

Requirements:
- {word_count} words
- Tone: {tone}
- Include examples
- Use Markdown (##, ###)
- Actionable content

Write complete chapter."""

        return self.call_ai(
            "You are a bestselling author.",
            prompt,
            max_tokens=5000
        )
    
    def generate_introduction(self, outline, tone):
        """توليد المقدمة"""
        
        prompt = f"""Write introduction for "{outline['title']}".

Requirements:
- Hook readers
- Explain value
- 800 words
- Tone: {tone}
- Markdown format

Make it compelling!"""

        return self.call_ai(
            "You are an expert at writing book introductions.",
            prompt,
            max_tokens=2500
        )
    
    def generate_conclusion(self, outline, tone):
        """توليد الخاتمة"""
        
        prompt = f"""Write conclusion for "{outline['title']}".

Requirements:
- Summarize key points
- Call to action
- 600 words
- Tone: {tone}
- Inspiring

Make them take action!"""

        return self.call_ai(
            "You are skilled at writing powerful conclusions.",
            prompt,
            max_tokens=2000
        )

def create_premium_html(outline, content, author):
    """إنشاء HTML"""
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{outline['title']}</title>
    <style>
        body {{
            font-family: Georgia, serif;
            line-height: 1.8;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px;
        }}
        .cover {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 100px 40px;
            text-align: center;
            border-radius: 15px;
        }}
        h1 {{ font-size: 3rem; }}
        h2 {{ color: #667eea; margin-top: 40px; }}
    </style>
</head>
<body>
    <div class="cover">
        <h1>{outline['title']}</h1>
        <h2>{outline['subtitle']}</h2>
        <p>by {author}</p>
    </div>
    
    <div style="margin-top: 60px;">
        {content}
    </div>
    
    <footer style="margin-top: 80px; text-align: center; color: #999;">
        <p>© {datetime.now().year} {author}</p>
    </footer>
</body>
</html>"""
    
    return html

def main():
    # Header
    st.markdown("""
        <div class="hero-section">
            <h1 style="font-size: 3.5rem; margin: 0;">👑 EbookMaster Ultra</h1>
            <p style="font-size: 1.3rem; margin-top: 15px;">AI-Powered Book Generator</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        groq_key = st.text_input("🤖 Groq API Key", type="password")
        
        st.divider()
        
        author = st.text_input("✍️ Author", "AI Author")
        audience = st.selectbox("👥 Audience", ["Beginners", "Everyone", "Professionals"])
        tone = st.selectbox("🎭 Tone", ["Professional", "Conversational", "Motivational"])
        
        st.divider()
        
        num_chapters = st.slider("📑 Chapters", 3, 15, 8)
        word_count = st.slider("📏 Words/Chapter", 1000, 3000, 1500)
    
    # Main
    tab1, tab2, tab3 = st.tabs(["📝 Create", "📖 Preview", "💾 Export"])
    
    with tab1:
        st.subheader("📚 Book Topic")
        
        topic = st.text_area(
            "What's your book about?",
            placeholder="E.g., Complete Guide to Digital Marketing",
            height=100
        )
        
        # Examples
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💼 Business", use_container_width=True):
                topic = "Complete Guide to Starting an Online Business"
        
        with col2:
            if st.button("🤖 AI/Tech", use_container_width=True):
                topic = "Artificial Intelligence for Beginners"
        
        with col3:
            if st.button("💪 Self-Help", use_container_width=True):
                topic = "Transform Your Life with Daily Habits"
        
        st.divider()
        
        # Generate
        if st.button("🚀 Generate Book", type="primary", use_container_width=True):
            if not groq_key or not topic:
                st.error("❌ Fill all fields!")
                return
            
            master = EbookMasterUltra(groq_key)
            
            progress = st.progress(0)
            status = st.empty()
            
            # Outline
            status.info("📋 Creating outline...")
            outline = master.generate_outline(topic, topic, num_chapters, audience, tone)
            progress.progress(20)
            
            if not outline:
                st.error("❌ Failed! Check API key.")
                return
            
            st.session_state.outline = outline
            st.success(f"✅ {outline['title']}")
            
            # Introduction
            status.info("✍️ Writing introduction...")
            intro = master.generate_introduction(outline, tone)
            progress.progress(25)
            st.session_state.introduction = intro
            
            # Chapters
            chapters = []
            for i in range(1, num_chapters + 1):
                prog = 25 + (i / num_chapters * 65)
                progress.progress(int(prog))
                status.info(f"✍️ Chapter {i}/{num_chapters}")
                
                chapter = master.generate_chapter(outline, i, tone, word_count)
                if chapter:
                    chapters.append(chapter)
                    st.success(f"✅ Chapter {i}")
            
            st.session_state.chapters = chapters
            
            # Conclusion
            status.info("🎯 Writing conclusion...")
            conclusion = master.generate_conclusion(outline, tone)
            progress.progress(100)
            st.session_state.conclusion = conclusion
            
            # Done!
            st.markdown("""
                <div class="success-banner">
                    🎉 Book Complete!
                </div>
            """, unsafe_allow_html=True)
            
            # Stats
            total_words = sum(len(c.split()) for c in chapters)
            total_words += len(intro.split()) + len(conclusion.split())
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📑 Chapters", num_chapters)
            with col2:
                st.metric("📝 Words", f"{total_words:,}")
            with col3:
                st.metric("📄 Pages", f"~{int(total_words/250)}")
    
    with tab2:
        if 'outline' in st.session_state:
            outline = st.session_state.outline
            
            st.markdown(f"""
                <div class="cover-preview">
                    <h1>{outline['title']}</h1>
                    <h2>{outline['subtitle']}</h2>
                    <p style="font-size: 1.2rem; margin-top: 30px;">by {author}</p>
                </div>
            """, unsafe_allow_html=True)
            
            if 'introduction' in st.session_state:
                st.markdown("## Introduction")
                st.markdown(st.session_state.introduction)
            
            if 'chapters' in st.session_state:
                for i, content in enumerate(st.session_state.chapters, 1):
                    with st.expander(f"Chapter {i}: {outline['chapters'][i-1]['title']}"):
                        st.markdown(content)
            
            if 'conclusion' in st.session_state:
                st.markdown("## Conclusion")
                st.markdown(st.session_state.conclusion)
        else:
            st.info("📝 Generate a book first!")
    
    with tab3:
        if 'outline' in st.session_state:
            # Compile
            full_content = ""
            
            if 'introduction' in st.session_state:
                full_content += f"# Introduction\n\n{st.session_state.introduction}\n\n"
            
            for ch in st.session_state.chapters:
                full_content += f"{ch}\n\n"
            
            if 'conclusion' in st.session_state:
                full_content += f"# Conclusion\n\n{st.session_state.conclusion}\n\n"
            
            # HTML
            html = create_premium_html(
                st.session_state.outline,
                full_content.replace('\n', '<br>'),
                author
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    "📄 Download HTML",
                    html,
                    f"{st.session_state.outline['title'].replace(' ', '_')}.html",
                    mime="text/html",
                    use_container_width=True
                )
            
            with col2:
                md = f"# {st.session_state.outline['title']}\n\n{full_content}"
                st.download_button(
                    "📝 Download Markdown",
                    md,
                    f"{st.session_state.outline['title'].replace(' ', '_')}.md",
                    use_container_width=True
                )
            
            st.info("""
            ### 📖 Create PDF:
            1. Download HTML
            2. Open in Chrome
            3. Ctrl+P → Save as PDF
            """)
        else:
            st.info("📝 Generate a book first!")

if __name__ == "__main__":
    main()
