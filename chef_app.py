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

# --- 3. CUSTOM CSS ---
st.markdown("""
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
        }
        .stMarkdown p {
            text-align: center;
            color: #666;
        }
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
        
        # We create a list containing the prompt + ALL images
        content = [prompt] + images
        
        with st.spinner(f"Analyzing {len(images)} photos..."):
            response = model.generate_content(content)
            return response.text
            
    except Exception as e:
        return f"Error: {e}"

# --- 5. APP LAYOUT ---

# Initialize Session State for the "Basket" of images
if 'ingredient_images' not in st.session_state:
    st.session_state.ingredient_images = []

# A. HEADER
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

    st.markdown("""
        <p style='text-align: center; color: #666; margin-top: -25px; font-size: 16px;'>
            Visual Intelligence for Your Kitchen
        </p>
    """, unsafe_allow_html=True)

# B. INPUT AREA
col1, col2, col3 = st.columns([1, 6, 1])

with col2:
    # 1. FILE UPLOADER (Accepts Multiple)
    uploaded_files = st.file_uploader("Upload photos (Fridge, Pantry, Freezer)", 
                                    type=["jpg", "png", "jpeg"], 
                                    accept_multiple_files=True)
    
    # Logic: If user uploads files, we add them to our list
    current_images = []
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            image = Image.open(uploaded_file)
            current_images.append(image)

    # 2. CAMERA (Optional Addition)
    # Note: Streamlit Camera clears itself on refresh, so mixing cam + upload 
    # is tricky. For now, we show the camera below the upload.
    camera_photo = st.camera_input("Or snap a photo")
    if camera_photo:
        cam_image = Image.open(camera_photo)
        current_images.append(cam_image)

    # C. PREVIEW GALLERY
    # Show small thumbnails of what we are about to cook
    if current_images:
        st.write("---")
        st.caption(f"Analyzing {len(current_images)} photos:")
        # Display images in a row
        cols = st.columns(len(current_images))
        for idx, img in enumerate(current_images):
            with cols[idx]:
                st.image(img, use_container_width=True)

    # D. ACTION BUTTON
    st.write("") 
    if current_images:
        if st.button("Generate Recipe"):
            if 'recipe_result' in st.session_state:
                del st.session_state['recipe_result']
            
            # Pass the WHOLE LIST of images to the AI
            result = get_recipe(current_images)
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
