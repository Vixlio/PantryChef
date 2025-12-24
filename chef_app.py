import streamlit as st
import google.generativeai as genai
from PIL import Image
import os

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="ChefLens", page_icon="🍳", layout="centered")

# --- 2. AUTHENTICATION ---
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

# --- 3. CUSTOM CSS (Tight & Modern) ---
st.markdown("""
    <style>
        /* REMOVE DEFAULT TOP PADDING */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
        }
        
        /* Google-style Button */
        div.stButton > button {
            display: block;
            margin: 0 auto;
            background-color: #f8f9fa; 
            color: #3c4043;
            border: 1px solid #f8f9fa;
            border-radius: 4px;
            padding: 10px 24px;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.3s;
        }
        div.stButton > button:hover {
            background-color: #f8f9fa;
            border: 1px solid #dadce0;
            box-shadow: 0 1px 1px rgba(0,0,0,.1);
            color: #202124;
        }
        
        /* Clean up layout */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 4. THE BRAIN ---
def get_recipe(image_input):
    if not api_key:
        return "🚨 Error: No API Key provided."
    
    try:
        genai.configure(api_key=api_key)
        # Using the "Lite" model (10 requests/min limit)
        model = genai.GenerativeModel('gemini-2.5-flash-lite') 
        
        prompt = """
        You are a smart kitchen AI. Analyze this image.
        1. List the ingredients you see.
        2. Create a modern, delicious recipe.
        3. Format the output cleanly with bold headers.
        """
        
        with st.spinner("Analyzing pixels..."):
            response = model.generate_content([prompt, image_input])
            return response.text
            
    except Exception as e:
        return f"Error: {e}"

# --- 5. APP LAYOUT ---

# A. SMART LOGO LOADER (Everything in one column now)
left_co, cent_co, last_co = st.columns([1, 4, 1])

with cent_co:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=350)
    elif os.path.exists("Logo.png"):
        st.image("Logo.png", width=350)
    elif os.path.exists("logo.PNG"):
        st.image("logo.PNG", width=350)
    else:
        st.markdown("<h1 style='text-align: center; color: #333;'>ChefLens</h1>", unsafe_allow_html=True)
        st.error("⚠️ Tip: Upload 'logo.png' to GitHub!")

    # B. SUBTITLE (Updated Text & Centered)
    st.markdown("""
        <p style='text-align: center; color:
