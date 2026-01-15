import os
import json
import streamlit as st
from groq import Groq
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from deep_translator import GoogleTranslator  # لميزة الترجمة
import requests
from io import BytesIO
import random
from datetime import datetime
import base64
import markdown2  # لتحويل Markdown إلى HTML

# ================== SETTINGS ==================
GROQ_API_KEY = "your_groq_api_key_here"
client = Groq(api_key=GROQ_API_KEY)

# ================== AI EBOOK GENERATOR ==================
class GlobalEbookGenerator:
    def __init__(self):
        self.supported_languages = ['en', 'es', 'fr', 'de', 'pt', 'ru', 'ar', 'zh', 'ja']
        self.default_language = 'en'
    
    def generate_ebook(self, topic, niche, pages=50, language='en', 
                      include_quiz=True, include_images=True, style='professional'):
        """
        Generate a complete ebook in English with optional translations
        """
        
        # Step 1: Generate content in English
        english_content = self._generate_english_content(topic, niche, pages, include_quiz, style)
        
        # Step 2: Translate if needed (optional)
        if language != 'en':
            translated_content = self._translate_content(english_content, language)
        else:
            translated_content = english_content
        
        # Step 3: Create PDF
        pdf_file = self._create_professional_pdf(translated_content, include_quiz, include_images)
        
        # Step 4: Create marketing materials
        marketing_kit = self._create_marketing_kit(english_content, translated_content)
        
        return {
            "pdf_file": pdf_file,
            "marketing_kit": marketing_kit,
            "language": language,
            "word_count": self._count_words(english_content),
            "seo_optimized": True
        }
    
    def _generate_english_content(self, topic, niche, pages, include_quiz, style):
        """
        Generate high-quality English content using Groq
        """
        prompt = f"""
        You are a professional ebook writer and digital product creator. 
        Create a complete, ready-to-sell ebook about:
        
        TOPIC: {topic}
        NICHE: {niche}
        TARGET AUDIENCE: Global audience (primarily English-speaking)
        PAGES: {pages}
        STYLE: {style} (professional, conversational, academic, or persuasive)
        
        REQUIREMENTS:
        
        1. **BOOK TITLE**: 
           - Main title (catchy, SEO-friendly)
           - Subtitle (explains benefit)
        
        2. **BOOK DESCRIPTION**:
           - 150-200 words for back cover/Amazon description
           - Includes keywords: {topic}, {niche}
           - Highlights 3 main benefits
        
        3. **TABLE OF CONTENTS**:
           - 8-12 chapters logically organized
           - Each chapter title should be benefit-driven
        
        4. **INTRODUCTION**:
           - Hook the reader
           - State the problem
           - Promise the solution
           - Build credibility
        
        5. **CHAPTER CONTENT** (For each chapter):
           - Chapter title
           - 500-800 words of valuable content
           - Practical examples/case studies
           - Actionable tips/step-by-step guides
           - Subheadings for readability
        
        6. **CONCLUSION**:
           - Summarize key points
           - Call to action
           - Next steps for the reader
        
        7. **APPENDICES** (if applicable):
           - Checklists
           - Templates
           - Resource lists
           - Recommended tools
        
        {"8. **INTERACTIVE QUIZ**: " if include_quiz else ""}
           {"- 10 multiple-choice questions" if include_quiz else ""}
           {"- Questions test understanding of key concepts" if include_quiz else ""}
           {"- Answers with explanations" if include_quiz else ""}
        
        9. **MARKETING COPY**:
           - 5 email subject lines for promotion
           - 10 social media post ideas
           - 5 Amazon book categories
           - Suggested price range ($9.99 - $49.99)
        
        10. **SEO METADATA**:
            - Primary keyword: {topic}
            - Secondary keywords (5-7)
            - Meta description
        
        OUTPUT FORMAT: JSON with these exact keys:
        {{
            "title": "Main Title",
            "subtitle": "Subtitle",
            "description": "Full description",
            "introduction": "Introduction content",
            "chapters": [
                {{
                    "title": "Chapter 1 Title",
                    "content": "Chapter content...",
                    "key_points": ["Point 1", "Point 2"],
                    "action_items": ["Do this", "Try that"]
                }}
            ],
            "conclusion": "Conclusion content",
            "appendices": ["Checklist", "Resources"],
            {"quiz": [{{"question": "Q?", "options": ["A", "B", "C"], "answer": 0, "explanation": "..."}}] if include_quiz else ""}
            "marketing": {{
                "email_subjects": [],
                "social_media": [],
                "categories": [],
                "price_suggestions": {{"low": 9.99, "high": 49.99}}
            }},
            "seo": {{
                "primary_keyword": "",
                "secondary_keywords": [],
                "meta_description": ""
            }}
        }}
        
        IMPORTANT: Write in professional, engaging American English. 
        Focus on providing REAL VALUE that justifies the price.
        """
        
        try:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-70b-8192",
                temperature=0.8,
                max_tokens=10000
            )
            
            content = response.choices[0].message.content
            
            # Extract JSON
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start != -1:
                json_str = content[json_start:json_end]
                return json.loads(json_str)
                
        except Exception as e:
            print(f"API Error: {e}")
        
        # Fallback structure
        return self._create_fallback_structure(topic, niche)
    
    def _translate_content(self, content, target_lang):
        """
        Translate content to target language (optional feature)
        """
        if target_lang == 'en':
            return content
        
        try:
            translator = GoogleTranslator(source='en', target=target_lang)
            
            translated = content.copy()
            translated['title'] = translator.translate(content['title'])
            translated['description'] = translator.translate(content['description'])
            
            # Translate chapters
            for chapter in translated.get('chapters', []):
                chapter['title'] = translator.translate(chapter['title'])
                chapter['content'] = translator.translate(chapter['content'])
            
            return translated
        except:
            return content  # Return original if translation fails
    
    def _create_professional_pdf(self, content, include_quiz, include_images):
        """
        Create a professional PDF ebook
        """
        filename = f"ebook_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        doc = SimpleDocTemplate(filename, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles for professional ebook
        title_style = ParagraphStyle(
            'EbookTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=30,
            alignment=1
        )
        
        # Add title
        story.append(Paragraph(content.get('title', 'Professional Ebook'), title_style))
        story.append(Paragraph(content.get('subtitle', ''), styles['Heading2']))
        story.append(Spacer(1, 40))
        
        # Add description
        story.append(Paragraph("Book Description", styles['Heading3']))
        story.append(Paragraph(content.get('description', ''), styles['Normal']))
        story.append(Spacer(1, 30))
        
        # Add chapters
        story.append(Paragraph("Table of Contents", styles['Heading3']))
        
        toc_data = [['Chapter', 'Title']]
        for i, chapter in enumerate(content.get('chapters', []), 1):
            toc_data.append([f"Chapter {i}", chapter.get('title', '')])
        
        toc_table = Table(toc_data, colWidths=[1.5*inch, 4*inch])
        toc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(toc_table)
        story.append(Spacer(1, 30))
        
        # Add chapters content
        for i, chapter in enumerate(content.get('chapters', []), 1):
            story.append(Paragraph(f"Chapter {i}: {chapter.get('title', '')}", styles['Heading2']))
            story.append(Paragraph(chapter.get('content', ''), styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Add quiz if requested
        if include_quiz and 'quiz' in content:
            story.append(Paragraph("Knowledge Check Quiz", styles['Heading3']))
            for j, question in enumerate(content['quiz'], 1):
                story.append(Paragraph(f"Q{j}: {question.get('question', '')}", styles['Normal']))
                for opt_idx, option in enumerate(question.get('options', [])):
                    story.append(Paragraph(f"  {chr(65+opt_idx)}) {option}", styles['Normal']))
                story.append(Spacer(1, 10))
        
        doc.build(story)
        return filename
    
    def _create_marketing_kit(self, english_content, translated_content):
        """
        Create complete marketing package
        """
        return {
            "email_templates": self._generate_email_templates(english_content),
            "social_media_posts": self._generate_social_media_posts(english_content),
            "amazon_listing": self._generate_amazon_listing(english_content),
            "sales_page_copy": self._generate_sales_page(english_content),
            "graphics_prompts": self._generate_graphics_prompts(english_content)
        }
    
    def _generate_email_templates(self, content):
        """Generate email sequences for promotion"""
        emails = []
        
        prompts = [
            f"Write a launch announcement email for this ebook: {content['title']}",
            f"Write a follow-up email highlighting key benefits of: {content['title']}",
            f"Write a limited-time offer email for: {content['title']}"
        ]
        
        for prompt in prompts:
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-70b-8192",
                temperature=0.7,
                max_tokens=500
            )
            emails.append(response.choices[0].message.content)
        
        return emails
    
    def _generate_social_media_posts(self, content):
        """Generate social media posts"""
        platforms = ['Twitter', 'LinkedIn', 'Instagram', 'Facebook', 'TikTok']
        posts = {}
        
        for platform in platforms:
            prompt = f"Write 3 engaging {platform} posts to promote this ebook: {content['title']}"
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-70b-8192",
                temperature=0.8,
                max_tokens=300
            )
            posts[platform] = response.choices[0].message.content
        
        return posts
    
    def _generate_amazon_listing(self, content):
        """Generate Amazon KDP listing"""
        prompt = f"""
        Create a complete Amazon KDP listing for this ebook:
        
        Title: {content['title']}
        
        Include:
        1. Book description (for Amazon product page)
        2. 7 search keywords for Amazon
        3. 2 categories on Amazon
        4. Author bio (fictional but professional)
        """
        
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-70b-8192",
            temperature=0.7,
            max_tokens=800
        )
        
        return response.choices[0].message.content
    
    def _generate_sales_page(self, content):
        """Generate sales page copy"""
        prompt = f"""
        Write a high-converting sales page for this ebook: {content['title']}
        
        Include:
        - Attention-grabbing headline
        - Problem identification
        - Solution presentation
        - Benefits list (10+ benefits)
        - Features list
        - Testimonials (create 3 believable testimonials)
        - FAQ section
        - Strong call-to-action
        - Money-back guarantee text
        """
        
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-70b-8192",
            temperature=0.8,
            max_tokens=1500
        )
        
        return response.choices[0].message.content
    
    def _generate_graphics_prompts(self, content):
        """Generate prompts for ebook cover and graphics"""
        prompts = {
            "cover": f"Professional ebook cover for: {content['title']}. Style: modern, clean, professional. Colors: blue, white, gold.",
            "social_media_graphics": f"Social media graphics promoting: {content['title']}. Include key benefits and call-to-action.",
            "infographics": f"Create infographic ideas that visualize key concepts from: {content['title']}"
        }
        return prompts
    
    def _count_words(self, content):
        """Count total words in the ebook"""
        total = 0
        total += len(str(content.get('description', '')).split())
        total += len(str(content.get('introduction', '')).split())
        for chapter in content.get('chapters', []):
            total += len(str(chapter.get('content', '')).split())
        total += len(str(content.get('conclusion', '')).split())
        return total
    
    def _create_fallback_structure(self, topic, niche):
        """Create basic structure if API fails"""
        return {
            "title": f"The Complete Guide to {topic}",
            "subtitle": f"Master {topic} in the {niche} Industry",
            "description": f"A comprehensive guide to mastering {topic} in the {niche} field.",
            "introduction": f"Welcome to your journey in mastering {topic}.",
            "chapters": [
                {
                    "title": f"Introduction to {topic}",
                    "content": f"This chapter covers the basics of {topic}.",
                    "key_points": ["Point 1", "Point 2"],
                    "action_items": ["Action 1", "Action 2"]
                }
            ],
            "conclusion": "Thank you for reading this guide.",
            "marketing": {
                "email_subjects": [f"Learn {topic} Today", f"Master {topic} Guide"],
                "social_media": [f"Check out this guide on {topic}"],
                "price_suggestions": {"low": 9.99, "high": 29.99}
            }
        }

# ================== STREAMLIT UI ==================
def create_web_interface():
    """Create a modern web interface for the ebook generator"""
    
    st.set_page_config(
        page_title="AI Ebook Factory Pro",
        page_icon="📘",
        layout="wide"
    )
    
    st.title("📘 AI Ebook Factory Pro")
    st.subheader("Generate Professional, Ready-to-Sell Ebooks in Minutes")
    
    with st.sidebar:
        st.header("⚙️ Settings")
        
        topic = st.text_input("📝 Ebook Topic", 
                             placeholder="e.g., Digital Marketing Strategies")
        
        niche = st.text_input("🎯 Target Niche", 
                             placeholder="e.g., Small Business Owners")
        
        pages = st.slider("📄 Number of Pages", 30, 200, 50)
        
        language = st.selectbox(
            "🌍 Output Language",
            ['English', 'Spanish', 'French', 'German', 'Portuguese', 
             'Russian', 'Arabic', 'Chinese', 'Japanese'],
            index=0
        )
        
        include_quiz = st.checkbox("✅ Include Interactive Quiz", value=True)
        include_images = st.checkbox("🖼️ Include Image Placeholders", value=True)
        
        style = st.selectbox(
            "✍️ Writing Style",
            ['Professional', 'Conversational', 'Academic', 'Persuasive'],
            index=0
        )
        
        generate_btn = st.button("🚀 Generate Ebook", type="primary", use_container_width=True)
    
    if generate_btn and topic and niche:
        with st.spinner("🤖 AI is writing your bestseller..."):
            generator = GlobalEbookGenerator()
            
            # Map language to code
            lang_codes = {'English': 'en', 'Spanish': 'es', 'French': 'fr', 
                         'German': 'de', 'Portuguese': 'pt', 'Russian': 'ru',
                         'Arabic': 'ar', 'Chinese': 'zh', 'Japanese': 'ja'}
            
            result = generator.generate_ebook(
                topic=topic,
                niche=niche,
                pages=pages,
                language=lang_codes[language],
                include_quiz=include_quiz,
                include_images=include_images,
                style=style.lower()
            )
            
            # Display results
            st.success(f"✅ Ebook Generated Successfully!")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Word Count", f"{result['word_count']:,}")
            with col2:
                st.metric("Language", language)
            with col3:
                st.metric("SEO Optimized", "Yes" if result['seo_optimized'] else "No")
            
            # Download buttons
            with open(result['pdf_file'], "rb") as f:
                st.download_button(
                    label="📥 Download PDF Ebook",
                    data=f,
                    file_name=f"{topic.replace(' ', '_')}_ebook.pdf",
                    mime="application/pdf"
                )
            
            # Preview marketing materials
            with st.expander("📈 Marketing Kit Preview"):
                tab1, tab2, tab3, tab4 = st.tabs(["Email Templates", "Social Media", "Amazon Listing", "Sales Page"])
                
                with tab1:
                    for i, email in enumerate(result['marketing_kit']['email_templates'], 1):
                        st.subheader(f"Email Template #{i}")
                        st.text_area(f"Email {i}", email, height=200, key=f"email_{i}")
                
                with tab2:
                    for platform, posts in result['marketing_kit']['social_media_posts'].items():
                        st.subheader(platform)
                        st.write(posts)
                
                with tab3:
                    st.write(result['marketing_kit']['amazon_listing'])
                
                with tab4:
                    st.write(result['marketing_kit']['sales_page_copy'])
            
            # Monetization suggestions
            st.info("💰 **Monetization Tips:** Sell on Gumroad ($9.99-$49.99), use as lead magnet, or bundle with courses.")

# ================== MAIN ==================
if __name__ == "__main__":
    # To run as web app: streamlit run ebook_generator.py
    create_web_interface()
