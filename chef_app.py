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
    if "GEMINI_API_KEY" not in os.environ:
        api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")
    else:
        api_key = os.environ["GEMINI_API_KEY"]

# --- 3. CUSTOM CSS ---
st.markdown("""
    <style>
        /* 1. FORCE LOGO & IMAGES TO CENTER (MOBILE & DESKTOP) */
        /* This Flexbox rule creates a strong magnetic pull to the center */
        div[data-testid="stImage"] {
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
        }
        
        /* 2. CENTER ALL TEXT HEADERS */
        /* We do not specify color, so it adapts to Light/Dark mode automatically */
        h1, h3, p {
            text-align: center !important;
        }

        /* 3. REMOVE TOP PADDING */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 0rem;
        }
        
        /* 4. BUTTON STYLES */
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
            background-color: #e8eaed;
            border: 1px solid #dadce0;
            color: #202124;
        }
        
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 4. THE BRAIN ---
def get_recipe(images):
    if not api_key:
        return "🚨 Error: No API Key provided."
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash-lite') 
        
        prompt = """
        You are a smart kitchen AI. Analyze these images of a kitchen/pantry.
        1. List ALL ingredients you see across all photos.
        2. Create a modern, delicious recipe using these items.
        3. Format the output cleanly with bold headers.
        """
        
        content = [prompt] + images
        
        with st.spinner(f"Analyzing {len(images)} photos..."):
            response = model.generate_content(content)
            return response.text
            
    except Exception as e:
        return f"Error: {e}"

# --- 5. APP LAYOUT ---

# Initialize Session State
if 'ingredient_images' not in st.session_state:
    st.session_state.ingredient_images = []

# A. LOGO SECTION (No Columns - Pure CSS Centering)
if os.path.exists("logo.png"):
    # We use 300px which is safe for mobile screens
    st.image("logo.png", width=300) 
elif os.path.exists("Logo.png"):
    st.image("Logo.png", width=300)
elif os.path.exists("logo.PNG"):
    st.image("logo.PNG", width=300)
else:
    # Fallback text if no logo
    st.markdown("<h1 style='text-align: center;'>ChefLens</h1>", unsafe_allow_html=True)

# Subtitle (No hardcoded color - adapts to theme)
st.markdown("""
    <p style='text-align: center; margin-top: -10px; font-size: 16px; opacity: 0.8;'>
        Visual Intelligence for Your Kitchen
    </p>
""", unsafe_allow_html=True)

# Spacer
st.write("")
st.write("")

# B. INPUT AREA
# 1. Custom Centered Header
st.markdown("<h3 style='text-align: center; font-size: 20px;'>Snap a photo of your ingredients</h3>", unsafe_allow_html=True)

# 2. Camera Input
# We use columns ONLY here to control the width of the camera viewport
col1, col2, col3 = st.columns([1, 10, 1])
with col2:
    camera_photo = st.camera_input(label="Snap Photo", label_visibility="hidden")
    
    if camera_photo:
        img = Image.open(camera_photo)
        st.session_state.ingredient_images.append(img)
        # We don't rerun immediately so you can keep snapping

    # C. PHOTO GALLERY (The "Basket")
    if len(st.session_state.ingredient_images) > 0:
        st.write("---")
        # Dynamic text that adapts to theme
        st.markdown(f"<p style='text-align: center;'><b>{len(st.session_state.ingredient_images)} Photos Captured</b></p>", unsafe_allow_html=True)
        
        # Display thumbnails
        cols = st.columns(3)
        for idx, img in enumerate(st.session_state.ingredient_images):
            with cols[idx % 3]:
                st.image(img, use_container_width=True)
                
        # Clear Button
        if st.button("Clear Photos & Start Over"):
            st.session_state.ingredient_images = []
            st.rerun()

    # D. ACTION BUTTON
    st.write("") 
    if len(st.session_state.ingredient_images) > 0:
        if st.button("Generate Recipe", use_container_width=True):
            if 'recipe_result' in st.session_state:
                del st.session_state['recipe_result']
            
            result = get_recipe(st.session_state.ingredient_images)
            st.session_state.recipe_result = result
            st.rerun()

# --- 6. RESULTS DISPLAY ---
if 'recipe_result' in st.session_state and st.session_state.recipe_result:
    st.markdown("---")
    
    if "Error" in st.session_state.recipe_result:
        st.error(st.session_state.recipe_result)
    else:
        st.subheader("👨‍🍳 Result")
        st.markdown(st.session_state.recipe_result)
