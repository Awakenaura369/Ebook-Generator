import streamlit as st
from groq import Groq
import io

# --- CONFIGURATION & SESSION STATE ---
if "generated_ebook" not in st.session_state:
    st.session_state["generated_ebook"] = ""
if "is_generating" not in st.session_state:
    st.session_state["is_generating"] = False

st.set_page_config(page_title="EbookMaster Ultra Pro", layout="wide", initial_sidebar_state="expanded")

# --- CUSTOM CSS (Maintaining the look) ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    .stTextArea>div>div>textarea { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: SETTINGS & CONFIG ---
with st.sidebar:
    st.header("⚙️ System Settings")
    api_key = st.text_input("Groq API Key:", type="password", placeholder="gsk_...")
    
    st.subheader("Model Configuration")
    model_choice = st.selectbox("AI Model", ["llama3-70b-8192", "llama3-8b-8192"], index=0)
    
    temperature = st.slider("Creativity (Temperature)", 0.0, 1.0, 0.7)
    max_tokens_val = st.number_input("Max Tokens per Chapter", 512, 8192, 4000)
    
    st.divider()
    st.info("Engine: **Groq**\nStatus: Ready")

# --- MAIN INTERFACE ---
st.title("📘 EbookMaster Ultra Pro")
st.caption("Professional Ebook Generation Engine | Powered by Groq")

tab1, tab2, tab3 = st.tabs(["🏗️ Builder", "📝 Editor & Preview", "⚙️ Raw Data"])

with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Book Details")
        ebook_title = st.text_input("Ebook Title", placeholder="e.g., TikTok Unlocked")
        author_name = st.text_input("Author / Brand", placeholder="e.g., Affiliate Growth Lab")
        target_audience = st.text_input("Target Audience", placeholder="e.g., Small Business Owners")

    with col2:
        st.subheader("Outline & Structure")
        outline = st.text_area("Enter Chapters (One per line):", 
                              height=225, 
                              placeholder="Introduction\nChapter 1: The Basics\nChapter 2: Scaling...")

    if st.button("🚀 Start Full Generation"):
        if not api_key:
            st.error("Missing API Key! Please check settings.")
        elif not ebook_title or not outline:
            st.warning("Please fill in the title and chapters.")
        else:
            client = Groq(api_key=api_key)
            chapters = [line.strip() for line in outline.split('\n') if line.strip()]
            
            # Master Container
            full_content = f"# {ebook_title}\n\n**By {author_name}**\n\n"
            full_content += f"**Target Audience:** {target_audience}\n\n---\n\n"
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # --- THE FIX: CHAPTER-BY-CHAPTER GENERATION ---
            # This prevents API Error 400 by avoiding huge payloads
            try:
                for i, chapter in enumerate(chapters):
                    status_text.info(f"Generating {i+1}/{len(chapters)}: {chapter}...")
                    
                    # Individual request for each chapter
                    completion = client.chat.completions.create(
                        model=model_choice,
                        messages=[
                            {"role": "system", "content": "You are an expert ebook writer. Write in English. Be detailed and professional."},
                            {"role": "user", "content": f"Write a complete, detailed chapter for the ebook '{ebook_title}'.\nChapter Title: {chapter}\nTarget Audience: {target_audience}\nEnsure deep insights and clear formatting."}
                        ],
                        temperature=temperature,
                        max_tokens=max_tokens_val
                    )
                    
                    chapter_text = completion.choices[0].message.content
                    full_content += f"## {chapter}\n\n{chapter_text}\n\n---\n\n"
                    
                    # Update progress
                    progress_bar.progress((i + 1) / len(chapters))
                
                full_content += f"\n\n© 2026 {author_name}. Created with EbookMaster Ultra Pro."
                st.session_state["generated_ebook"] = full_content
                status_text.success("✅ Ebook generated successfully!")
                
            except Exception as e:
                st.error(f"Critical Error: {str(e)}")

with tab2:
    st.subheader("Ebook Preview")
    if st.session_state["generated_ebook"]:
        # Editable Preview
        edited_content = st.text_area("Final Polish:", st.session_state["generated_ebook"], height=600)
        st.session_state["generated_ebook"] = edited_content
        
        c1, c2 = st.columns(2)
        with c1:
            st.download_button("📥 Download as TXT", data=edited_content, file_name=f"{ebook_title}.txt")
    else:
        st.info("Wait for generation to complete...")

with tab3:
    st.subheader("System Debug & Raw Stats")
    if st.session_state["generated_ebook"]:
        st.write(f"**Word Count:** {len(st.session_state['generated_ebook'].split())}")
        st.write(f"**Character Count:** {len(st.session_state['generated_ebook'])}")
    else:
        st.write("No data generated yet.")
