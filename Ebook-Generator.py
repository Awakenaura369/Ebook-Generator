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

class EbookMasterUltra:
    def __init__(self, groq_api_key):
        self.groq_api_key = groq_api_key
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.3-70b-versatile"
    
    def call_ai(self, system_prompt, user_prompt, max_tokens=4000):
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
                    "temperature": 0.7
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content']
            return None
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return None
    
    def generate_outline(self, topic, num_chapters):
        prompt = f"""Create a book outline for: "{topic}"
Chapters: {num_chapters}

Return JSON:
{{
  "title": "Book Title",
  "subtitle": "Subtitle",
  "chapters": [
    {{"number": 1, "title": "Chapter Title"}}
  ]
}}

Return ONLY JSON."""

        result = self.call_ai("You are a book architect.", prompt, 3000)
        
        if result:
            try:
                cleaned = result.strip().replace('```json', '').replace('```', '').strip()
                return json.loads(cleaned)
            except:
                return None
        return None
    
    def generate_chapter(self, title, chapter_title, word_count):
        prompt = f"""Write chapter for "{title}":
Chapter: {chapter_title}
Length: {word_count} words
Format: Markdown
Include examples and actionable tips."""

        return self.call_ai("You are a bestselling author.", prompt, 5000)
    
    def generate_intro(self, title):
        prompt = f"""Write introduction for "{title}".
800 words, engaging, markdown format."""
        return self.call_ai("You are an expert writer.", prompt, 2500)
    
    def generate_conclusion(self, title):
        prompt = f"""Write conclusion for "{title}".
600 words, inspiring, call-to-action."""
        return self.call_ai("You are an expert writer.", prompt, 2000)

def markdown_to_html(text):
    """Convert Markdown to clean HTML"""
    # Headers
    text = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    
    # Bold & Italic
    text = re.sub(r'\*\*\*(.*?)\*\*\*', r'<strong><em>\1</em></strong>', text)
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    
    # Paragraphs
    lines = text.split('\n')
    html_lines = []
    for line in lines:
        if line.strip() and not line.startswith('<'):
            html_lines.append(f'<p>{line}</p>')
        else:
            html_lines.append(line)
    
    return '\n'.join(html_lines)

def create_html(outline, content, author):
    """Create clean HTML"""
    content_html = markdown_to_html(content)
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{outline['title']}</title>
    <style>
        body {{
            font-family: Georgia, serif;
            line-height: 1.9;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px;
            color: #2c3e50;
        }}
        .cover {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 100px 40px;
            text-align: center;
            border-radius: 15px;
            margin-bottom: 60px;
        }}
        .cover h1 {{
            font-size: 3rem;
            margin-bottom: 20px;
        }}
        h1 {{ 
            color: #667eea; 
            font-size: 2.5rem;
            margin-top: 60px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 15px;
        }}
        h2 {{ 
            color: #34495e; 
            font-size: 2rem;
            margin-top: 40px; 
        }}
        h3 {{ 
            color: #555; 
            font-size: 1.5rem;
            margin-top: 30px; 
        }}
        p {{ 
            margin-bottom: 20px;
            text-align: justify;
        }}
        strong {{ font-weight: 700; }}
        em {{ font-style: italic; }}
    </style>
</head>
<body>
    <div class="cover">
        <h1>{outline['title']}</h1>
        <h2>{outline['subtitle']}</h2>
        <p style="font-size: 1.5rem; margin-top: 40px;">by {author}</p>
    </div>
    
    <div class="content">
        {content_html}
    </div>
    
    <footer style="margin-top: 100px; text-align: center; color: #999;">
        <p>© {datetime.now().year} {author}</p>
    </footer>
</body>
</html>"""
    
    return html

def main():
    st.title("👑 EbookMaster Ultra")
    st.caption("AI-Powered Book Generator")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        groq_key = st.text_input("🤖 Groq API Key", type="password")
        author = st.text_input("✍️ Author", "AI Author")
        num_chapters = st.slider("📑 Chapters", 3, 15, 8)
        word_count = st.slider("📏 Words/Chapter", 1000, 3000, 1500)
    
    # Main
    topic = st.text_area(
        "📚 Book Topic",
        placeholder="E.g., Complete Guide to Digital Marketing",
        height=100
    )
    
    if st.button("🚀 Generate Book", type="primary"):
        if not groq_key or not topic:
            st.error("❌ Fill all fields!")
            return
        
        master = EbookMasterUltra(groq_key)
        
        progress = st.progress(0)
        
        # Outline
        st.info("📋 Creating outline...")
        outline = master.generate_outline(topic, num_chapters)
        progress.progress(20)
        
        if not outline:
            st.error("❌ Failed!")
            return
        
        st.session_state.outline = outline
        st.success(f"✅ {outline['title']}")
        
        # Introduction
        st.info("✍️ Writing introduction...")
        intro = master.generate_intro(outline['title'])
        progress.progress(25)
        st.session_state.introduction = intro
        
        # Chapters
        chapters = []
        for i in range(num_chapters):
            prog = 25 + ((i+1) / num_chapters * 65)
            progress.progress(int(prog))
            st.info(f"✍️ Chapter {i+1}/{num_chapters}")
            
            chapter = master.generate_chapter(
                outline['title'],
                outline['chapters'][i]['title'],
                word_count
            )
            if chapter:
                chapters.append(chapter)
        
        st.session_state.chapters = chapters
        
        # Conclusion
        st.info("🎯 Writing conclusion...")
        conclusion = master.generate_conclusion(outline['title'])
        progress.progress(100)
        st.session_state.conclusion = conclusion
        
        st.success("🎉 Book Complete!")
        
        # Stats
        total = sum(len(c.split()) for c in chapters) + len(intro.split()) + len(conclusion.split())
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📑 Chapters", num_chapters)
        with col2:
            st.metric("📝 Words", f"{total:,}")
        with col3:
            st.metric("📄 Pages", f"~{int(total/250)}")
    
    # Preview & Export
    if 'outline' in st.session_state:
        st.divider()
        
        tab1, tab2 = st.tabs(["📖 Preview", "💾 Export"])
        
        with tab1:
            st.subheader(st.session_state.outline['title'])
            if 'introduction' in st.session_state:
                st.markdown("## Introduction")
                st.markdown(st.session_state.introduction)
            
            if 'chapters' in st.session_state:
                for i, ch in enumerate(st.session_state.chapters, 1):
                    with st.expander(f"Chapter {i}"):
                        st.markdown(ch)
            
            if 'conclusion' in st.session_state:
                st.markdown("## Conclusion")
                st.markdown(st.session_state.conclusion)
        
        with tab2:
            full = f"# Introduction\n\n{st.session_state.introduction}\n\n"
            for ch in st.session_state.chapters:
                full += f"{ch}\n\n"
            full += f"# Conclusion\n\n{st.session_state.conclusion}"
            
            html = create_html(st.session_state.outline, full, author)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    "📄 Download HTML",
                    html,
                    f"{st.session_state.outline['title'].replace(' ', '_')}.html",
                    mime="text/html"
                )
            
            with col2:
                st.download_button(
                    "📝 Download Markdown",
                    full,
                    f"{st.session_state.outline['title'].replace(' ', '_')}.md"
                )
            
            st.info("💡 Open HTML in Chrome → Ctrl+P → Save as PDF")

if __name__ == "__main__":
    main()
