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
    # If no secret, ask in sidebar
    if "GEMINI_API_KEY" not in os.environ:
        api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")
    else:
        api_key = os.environ["GEMINI_API_KEY"]

# --- 3. CUSTOM CSS ---
st.markdown("""
    <style>
        /* 1. FORCE IMAGE CENTERING */
        /* This forces all images in columns to align center */
        div[data-testid="column"] {
            display: flex;
            align-items: center; 
            justify-content: center;
        }

        /* 2. REMOVE TOP PADDING */
        .block-container {
            padding-top: 1rem;
            padding-bottom: 0rem;
        }
        
        /* 3. CENTER TEXT */
        .stMarkdown p {
            text-align: center;
            color: #666;
        }
        
        /* 4. BUTTON STYLE */
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

# A. LOGO SECTION (Fixed Centering)
# We use [1, 2, 1] which creates a narrower middle lane, forcing the logo to center.
left_co, cent_co, last_co = st.columns([1, 2, 1])

with cent_co:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=350)
    elif os.path.exists("Logo.png"):
        st.image("Logo.png", width=350)
    elif os.path.exists("logo.PNG"):
        st.image("logo.PNG", width=350)
    else:
        st.markdown("<h1 style='text-align: center; color: #333;'>ChefLens</h1>", unsafe_allow_html=True)

    # Subtitle inside the same centered column
    st.markdown("""
        <p style='text-align: center; color: #666; margin-top: -15px; font-size: 16px;'>
            Visual Intelligence for Your Kitchen, Powered by Google
        </p>
    """, unsafe_allow_html=True)

# B. INPUT AREA
# We keep this wider ([1,6,1]) so the drag-and-drop zone is nice and big
col1, col2, col3 = st.columns([1, 6, 1])

with col2:
    # Initialize session state for basket
    if 'ingredient_images' not in st.session_state:
        st.session_state.ingredient_images = []

    uploaded_files = st.file_uploader("Upload photos (Fridge, Pantry, Freezer)", 
                                    type=["jpg", "png", "jpeg"], 
                                    accept_multiple_files=True)
    
    current_images = []
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            image = Image.open(uploaded_file)
            current_images.append(image)

    # Camera input
    camera_photo = st.camera_input("Or snap a photo")
    if camera_photo:
        cam_image = Image.open(camera_photo)
        current_images.append(cam_image)

    # C. PREVIEW GALLERY
    if current_images:
        st.write("---")
        st.caption(f"Analyzing {len(current_images)} photos:")
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
