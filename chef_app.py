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
        /* FORCE IMAGE CENTERING */
        div[data-testid="column"] {
            display: flex;
            align-items: center; 
            justify-content: center;
        }

        /* REMOVE TOP PADDING */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
        }
        
        /* CENTER TEXT */
        .stMarkdown p {
            text-align: center;
            color: #666;
        }
        
        /* BUTTON STYLES */
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

# A. LOGO SECTION (SUPER SIZE)
# We use [1, 10, 1] to give the middle column MAXIMUM width
left_co, cent_co, last_co = st.columns([1, 10, 1])

with cent_co:
    if os.path.exists("logo.png"):
        # Width increased to 500px (or as wide as the phone screen allows)
        st.image("logo.png", width=500)
    elif os.path.exists("Logo.png"):
        st.image("Logo.png", width=500)
    elif os.path.exists("logo.PNG"):
        st.image("logo.PNG", width=500)
    else:
        st.markdown("<h1 style='text-align: center; color: #333;'>ChefLens</h1>", unsafe_allow_html=True)

    # Subtitle with AGGRESSIVE negative margin (-35px)
    st.markdown("""
        <p style='text-align: center; color: #666; margin-top: -35px; font-size: 16px;'>
            Visual Intelligence for Your Kitchen, Powered by Google Gemini
        </p>
    """, unsafe_allow_html=True)

# B. INPUT AREA
col1, col2, col3 = st.columns([1, 6, 1])

with col2:
    # 1. CAMERA INPUT
    camera_photo = st.camera_input("Snap a photo of your ingredients")
    
    if camera_photo:
        img = Image.open(camera_photo)
        # Avoid adding duplicates if the user hasn't snapped a new one
        # (Simple logic: if the last image in the list is the same, skip)
        st.session_state.ingredient_images.append(img)

    # 2. PHOTO GALLERY (The "Basket")
    if len(st.session_state.ingredient_images) > 0:
        st.write("---")
        st.markdown(f"<p style='text-align: center;'><b>{len(st.session_state.ingredient_images)} Photos Captured</b></p>", unsafe_allow_html=True)
        
        cols = st.columns(3)
        for idx, img in enumerate(st.session_state.ingredient_images):
            with cols[idx % 3]:
                st.image(img, use_container_width=True)
                
        if st.button("Clear Photos & Start Over"):
            st.session_state.ingredient_images = []
            st.rerun()

    # C. ACTION BUTTON
    st.write("") 
    if len(st.session_state.ingredient_images) > 0:
        if st.button("Generate Recipe"):
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
