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
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except:
    GROQ_API_KEY = "your_groq_api_key_here"

client = Groq(api_key=GROQ_API_KEY)

# ================== AI EBOOK GENERATOR ==================
class GlobalEbookGenerator:
    def __init__(self):
        self.supported_languages = ['en', 'es', 'fr', 'de', 'pt', 'ru', 'ar', 'zh', 'ja']

    def _extract_json(self, text):
        """ذكاء اصطناعي لاستخراج الـ JSON وحل مشكلة ValueError"""
        try:
            clean_text = text.replace("```json", "").replace("```", "").strip()
            start_idx = clean_text.find('{')
            end_idx = clean_text.rfind('}') + 1
            if start_idx != -1:
                return json.loads(clean_text[start_idx:end_idx])
        except:
            pass
        return None

    def generate_ebook(self, topic, niche, pages, language='en', include_quiz=True, style='professional'):
        # 1. Content Generation Prompt
        prompt = f"""
        You are a world-class ebook creator. Create a comprehensive JSON for an ebook about: {topic} in the {niche} niche.
        Target Length: {pages} pages. Style: {style}.
        
        OUTPUT ONLY VALID JSON:
        {{
            "title": "Main Title",
            "subtitle": "Compelling Subtitle",
            "description": "Full sales description",
            "chapters": [
                {{"title": "Chapter 1", "content": "Detailed content for chapter 1 (at least 300 words)..."}},
                {{"title": "Chapter 2", "content": "Detailed content for chapter 2..."}}
            ],
            "conclusion": "Summary and CTA",
            "marketing": {{
                "email_templates": ["Email 1", "Email 2"],
                "social_media": {{"Twitter": "Post", "LinkedIn": "Post"}},
                "amazon_listing": "KDP description",
                "sales_page": "High converting sales copy"
            }},
            "quiz": [{{"question": "Q1", "options": ["A", "B"], "answer": 0}}]
        }}
        """
        
        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-70b-8192",
                temperature=0.7,
                max_tokens=8000
            )
            content = self._extract_json(response.choices[0].message.content)
            
            if not content: return None

            # 2. Translation (If needed)
            if language != 'en':
                content = self._translate_all(content, language)

            # 3. PDF Creation
            pdf_file = self._create_pdf(content, include_quiz)
            
            return {"pdf": pdf_file, "data": content}
        except Exception as e:
            st.error(f"Error: {e}")
            return None

    def _translate_all(self, content, lang):
        translator = GoogleTranslator(source='auto', target=lang)
        content['title'] = translator.translate(content['title'])
        content['description'] = translator.translate(content['description'])
        for ch in content['chapters']:
            ch['title'] = translator.translate(ch['title'])
            ch['content'] = translator.translate(ch['content'])
        return content

    def _create_pdf(self, content, include_quiz):
        filename = f"ebook_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Custom Styles
        title_style = ParagraphStyle('TitleStyle', fontSize=26, textColor=colors.HexColor('#2C3E50'), alignment=1, spaceAfter=20)
        header_style = ParagraphStyle('HeaderStyle', fontSize=18, textColor=colors.HexColor('#3498DB'), spaceBefore=15, spaceAfter=10)

        # Title Page
        story.append(Paragraph(content['title'], title_style))
        story.append(Paragraph(content.get('subtitle', ''), styles['Heading2']))
        story.append(Spacer(1, 30))

        # Table of Contents Table
        story.append(Paragraph("Table of Contents", header_style))
        toc_data = [[f"Ch {i+1}", ch['title']] for i, ch in enumerate(content['chapters'])]
        t = Table(toc_data, colWidths=[1*inch, 4*inch])
        t.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.whitesmoke), ('GRID', (0,0), (-1,-1), 0.5, colors.grey)]))
        story.append(t)
        story.append(Spacer(1, 30))

        # Chapters
        for i, ch in enumerate(content['chapters'], 1):
            story.append(Paragraph(f"Chapter {i}: {ch['title']}", header_style))
            story.append(Paragraph(ch['content'], styles['Normal']))
            story.append(Spacer(1, 15))

        if include_quiz and 'quiz' in content:
            story.append(Paragraph("Knowledge Check", header_style))
            for q in content['quiz']:
                story.append(Paragraph(f"Q: {q['question']}", styles['Normal']))
                story.append(Spacer(1, 10))

        doc.build(story)
        return filename

# ================== STREAMLIT UI ==================
def main():
    st.set_page_config(page_title="Ebook Factory Pro", layout="wide")
    st.title("📘 AI Ebook Factory Pro")
    
    with st.sidebar:
        st.header("Settings")
        topic = st.text_input("Topic")
        niche = st.text_input("Niche")
        lang = st.selectbox("Language", ["English", "Spanish", "French", "Arabic"])
        pages = st.slider("Length", 5, 50, 10)
        btn = st.button("🚀 Generate Bestseller", type="primary")

    if btn and topic:
        with st.spinner("Writing content..."):
            gen = GlobalEbookGenerator()
            lang_code = {"English":"en", "Spanish":"es", "French":"fr", "Arabic":"ar"}[lang]
            result = gen.generate_ebook(topic, niche, pages, lang_code)
            
            if result:
                st.success("Done!")
                with open(result['pdf'], "rb") as f:
                    st.download_button("📥 Download PDF", f, file_name=f"{topic}.pdf")
                
                # Marketing Kit Tabs
                st.divider()
                st.subheader("📈 Marketing Kit")
                t1, t2, t3, t4 = st.tabs(["Emails", "Social Media", "Amazon KDP", "Sales Page"])
                
                m = result['data']['marketing']
                with t1: st.write(m.get('email_templates'))
                with t2: st.write(m.get('social_media'))
                with t3: st.write(m.get('amazon_listing'))
                with t4: st.write(m.get('sales_page'))

if __name__ == "__main__":
    main()
