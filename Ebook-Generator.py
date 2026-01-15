import os
import json
import streamlit as st
from groq import Groq
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from deep_translator import GoogleTranslator
from datetime import datetime

# ================== SETTINGS & AUTH ==================
# تأكد انك حطيتي الـ Key فـ Streamlit Secrets باسم GROQ_API_KEY
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    GROQ_API_KEY = "your_fallback_key_here" # حط الساروت هنا غير للتجربة المحلية

client = Groq(api_key=GROQ_API_KEY)

# ================== AI EBOOK GENERATOR ==================
class GlobalEbookGenerator:
    def __init__(self):
        self.supported_languages = ['en', 'es', 'fr', 'de', 'pt', 'ru', 'ar', 'zh', 'ja']
    
    def _extract_json(self, text):
        """تنظيف واستخراج الـ JSON من جواب الذكاء الاصطناعي"""
        try:
            # مسح الـ Markdown tags إذا وجدوا
            clean_text = text.replace("```json", "").replace("```", "").strip()
            start_idx = clean_text.find('{')
            end_idx = clean_text.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                return json.loads(clean_text[start_idx:end_idx])
        except Exception as e:
            st.error(f"Error decoding JSON: {e}")
        return None

    def generate_ebook(self, topic, niche, pages, language='en', include_quiz=True, style='professional'):
        # Step 1: Generate content
        english_content = self._generate_english_content(topic, niche, pages, include_quiz, style)
        
        if not english_content:
            return None

        # Step 2: Translate if needed
        if language != 'en':
            content = self._translate_content(english_content, language)
        else:
            content = english_content
        
        # Step 3: Create PDF
        pdf_filename = self._create_professional_pdf(content, include_quiz)
        
        # Step 4: Simple Marketing Kit (Based on generated content)
        marketing_kit = {
            "title": content.get('title', 'Your Ebook'),
            "email_subjects": content.get('marketing', {}).get('email_subjects', []),
            "social_media": content.get('marketing', {}).get('social_media', []),
            "description": content.get('description', '')
        }
        
        return {
            "pdf_file": pdf_filename,
            "marketing_kit": marketing_kit,
            "word_count": self._count_words(content)
        }

    def _generate_english_content(self, topic, niche, pages, include_quiz, style):
        prompt = f"""
        Create a high-quality ebook JSON structure about {topic} for the {niche} niche.
        Style: {style}. Pages target: {pages}.
        
        Return ONLY a JSON object with these keys:
        {{
            "title": "str",
            "subtitle": "str",
            "description": "str",
            "chapters": [{{ "title": "str", "content": "str" }}],
            "conclusion": "str",
            "marketing": {{ "email_subjects": [], "social_media": [] }},
            "quiz": [{{"question": "str", "options": [], "answer": 0}}]
        }}
        """
        try:
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-70b-8192",
                temperature=0.7,
                max_tokens=8000
            )
            return self._extract_json(chat_completion.choices[0].message.content)
        except Exception as e:
            st.error(f"Groq API Error: {e}")
            return None

    def _translate_content(self, content, target_lang):
        translator = GoogleTranslator(source='en', target=target_lang)
        try:
            content['title'] = translator.translate(content['title'])
            content['description'] = translator.translate(content['description'])
            for ch in content['chapters']:
                ch['title'] = translator.translate(ch['title'])
                ch['content'] = translator.translate(ch['content'])
            return content
        except:
            return content

    def _create_professional_pdf(self, content, include_quiz):
        filename = f"ebook_{datetime.now().strftime('%H%M%S')}.pdf"
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Title
        story.append(Paragraph(content.get('title', 'Ebook'), styles['Title']))
        story.append(Spacer(1, 12))
        
        # Description
        story.append(Paragraph("About this Book", styles['Heading2']))
        story.append(Paragraph(content.get('description', ''), styles['Normal']))
        story.append(Spacer(1, 24))

        # Chapters
        for i, chapter in enumerate(content.get('chapters', []), 1):
            story.append(Paragraph(f"Chapter {i}: {chapter.get('title', '')}", styles['Heading2']))
            story.append(Paragraph(chapter.get('content', ''), styles['Normal']))
            story.append(Spacer(1, 12))

        if include_quiz and 'quiz' in content:
            story.append(Paragraph("Quiz", styles['Heading2']))
            for q in content['quiz']:
                story.append(Paragraph(q['question'], styles['Normal']))
                story.append(Spacer(1, 6))

        doc.build(story)
        return filename

    def _count_words(self, content):
        text = str(content)
        return len(text.split())

# ================== STREAMLIT UI ==================
def main():
    st.set_page_config(page_title="AI Ebook Factory", page_icon="📘")
    st.title("📘 AI Ebook Factory Pro")

    with st.sidebar:
        topic = st.text_input("Topic")
        niche = st.text_input("Niche")
        pages = st.slider("Target length", 10, 100, 30)
        lang = st.selectbox("Language", ["English", "Spanish", "French", "Arabic"])
        generate_btn = st.button("Generate Ebook")

    if generate_btn and topic and niche:
        with st.spinner("Writing your ebook..."):
            gen = GlobalEbookGenerator()
            lang_map = {"English": "en", "Spanish": "es", "French": "fr", "Arabic": "ar"}
            
            result = gen.generate_ebook(topic, niche, pages, language=lang_map[lang])
            
            if result:
                st.success("Generated!")
                st.metric("Words Count", result['word_count'])
                
                with open(result['pdf_file'], "rb") as f:
                    st.download_button("Download PDF", f, file_name="ebook.pdf")
                
                with st.expander("Marketing Kit"):
                    st.write(result['marketing_kit'])
            else:
                st.error("Failed to generate. Check your API key or connection.")

if __name__ == "__main__":
    main()
