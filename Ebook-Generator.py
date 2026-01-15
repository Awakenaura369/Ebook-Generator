import os
import json
import streamlit as st
from groq import Groq
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from deep_translator import GoogleTranslator
from datetime import datetime

# ================== 1. حماية الـ API KEY ==================
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    api_key = st.sidebar.text_input("Enter Groq API Key", type="password")

client = Groq(api_key=api_key) if api_key else None

# ================== 2. GENERATOR CLASS ==================
class GlobalEbookGenerator:
    def __init__(self):
        self.current_model = "llama-3.3-70b-versatile" 

    def _extract_json(self, text):
        try:
            clean_text = text.replace("```json", "").replace("```", "").strip()
            start_idx = clean_text.find('{')
            end_idx = clean_text.rfind('}') + 1
            if start_idx != -1:
                return json.loads(clean_text[start_idx:end_idx])
        except:
            pass
        return None

    def generate_ebook(self, topic, niche, pages, language='en'):
        if not client:
            st.warning("Please provide a valid Groq API Key.")
            return None

        prompt = f"""
        Generate a professional Ebook JSON for: {topic} in the {niche} niche.
        STRUCTURE:
        {{
            "title": "Title",
            "subtitle": "Subtitle",
            "description": "Sales description",
            "chapters": [ {{"title": "Ch1", "content": "Content..."}} ],
            "marketing": {{
                "email_templates": [],
                "social_media": "",
                "hotmart_sales_page": "High converting HTML/Text description for Hotmart"
            }}
        }}
        """
        
        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.current_model,
                temperature=0.7,
                max_tokens=4000 
            )
            content = self._extract_json(response.choices[0].message.content)
            
            if not content: return None

            if language != 'en':
                translator = GoogleTranslator(source='en', target=language)
                content['title'] = translator.translate(content['title'])
                content['description'] = translator.translate(content['description'])
                if "hotmart_sales_page" in content['marketing']:
                    content['marketing']['hotmart_sales_page'] = translator.translate(content['marketing']['hotmart_sales_page'])
                for ch in content['chapters']:
                    ch['title'] = translator.translate(ch['title'])
                    ch['content'] = translator.translate(ch['content'])

            pdf_file = self._create_pdf(content)
            return {"pdf": pdf_file, "data": content}
        except Exception as e:
            st.error(f"Error: {e}")
            return None

    def _create_pdf(self, content):
        filename = f"ebook_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        title_style = ParagraphStyle('TStyle', fontSize=26, textColor=colors.HexColor('#2C3E50'), alignment=1, spaceAfter=20)
        header_style = ParagraphStyle('HStyle', fontSize=18, textColor=colors.HexColor('#3498DB'), spaceBefore=15, spaceAfter=10)
        story.append(Paragraph(content['title'], title_style))
        story.append(Paragraph(content.get('subtitle', ''), styles['Heading2']))
        story.append(Spacer(1, 30))
        for i, ch in enumerate(content['chapters'], 1):
            story.append(Paragraph(f"Chapter {i}: {ch['title']}", header_style))
            story.append(Paragraph(ch['content'], styles['Normal']))
            story.append(Spacer(1, 15))
        doc.build(story)
        return filename

# ================== 3. STREAMLIT UI ==================
def main():
    st.set_page_config(page_title="Ebook Factory Pro", layout="wide")
    st.title("📘 AI Ebook Factory Pro")
    
    with st.sidebar:
        st.header("Settings")
        topic = st.text_input("Topic")
        niche = st.text_input("Niche")
        lang = st.selectbox("Language", ["English", "Arabic", "French"])
        pages = st.slider("Length", 5, 50, 10)
        btn = st.button("🚀 Generate Bestseller", type="primary")

    if btn and topic:
        with st.spinner("🤖 Writing your book..."):
            gen = GlobalEbookGenerator()
            lang_code = {"English":"en", "Arabic":"ar", "French":"fr"}[lang]
            result = gen.generate_ebook(topic, niche, pages, lang_code)
            
            if result:
                st.success("✅ Done!")
                with open(result['pdf'], "rb") as f:
                    st.download_button("📥 Download PDF", f, file_name=f"{topic}.pdf")
                
                st.divider()
                t1, t2, t3 = st.tabs(["📊 Book Preview", "📈 Marketing Kit", "💰 Hotmart Sales Page"])
                with t1:
                    st.header(result['data']['title'])
                    st.write(result['data']['description'])
                with t2:
                    st.json(result['data']['marketing'])
                with t3:
                    st.subheader("Copy this to Hotmart Description:")
                    st.code(result['data']['marketing'].get('hotmart_sales_page', 'Generating...'), language='html')

if __name__ == "__main__":
    main()
