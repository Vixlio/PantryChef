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
        /* 1. FORCE ALL IMAGES TO CENTER */
        div[data-testid="stImage"] {
            display: flex;
            justify-content: center;
        }
        
        /* 2. REMOVE TOP PADDING */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 0rem;
        }
        
        /* 3. CENTER TEXT */
        .stMarkdown p, .stMarkdown h3 {
            text-align: center !important;
            color: #666;
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

# A. LOGO SECTION
# We remove the columns here and just rely on the CSS 'justify-content: center' 
# which forces the image to the middle of the main container.
if os.path.exists("logo.png"):
    st.image("logo.png", width=400) # Adjusted width for balance
elif os.path.exists("Logo.png"):
    st.image("Logo.png", width=400)
elif os.path.exists("logo.PNG"):
    st.image("logo.PNG", width=400)
else:
    st.markdown("<h1 style='text-align: center; color: #333;'>ChefLens</h1>", unsafe_allow_html=True)

# Subtitle
st.markdown("""
    <p style='text-align: center; color: #666; margin-top: -15px; font-size: 16px;'>
        Visual Intelligence for Your Kitchen, Powered by Google Gemini
    </p>
""", unsafe_allow_html=True)

# Spacer
st.write("")
st.write("")

# B. INPUT AREA
# 1. Custom Centered Header (Replacing the default camera label)
st.markdown("<h3 style='text-align: center; color: #333; font-size: 20px;'>Snap a photo of your ingredients</h3>", unsafe_allow_html=True)

# 2. Camera Input (Label hidden because we made our own above)
# We use a trick to center the camera widget by putting it in a centered column
col1, col2, col3 = st.columns([1, 8, 1])
with col2:
    camera_photo = st.camera_input(label="Snap Photo", label_visibility="hidden")
    
    if camera_photo:
        img = Image.open(camera_photo)
        st.session_state.ingredient_images.append(img)
        # We don't rerun immediately so they can keep snapping quickly

    # C. PHOTO GALLERY (The "Basket")
    if len(st.session_state.ingredient_images) > 0:
        st.write("---")
        st.markdown(f"<p style='text-align: center;'><b>{len(st.session_state.ingredient_images)} Photos Captured</b></p>", unsafe_allow_html=True)
        
        # Display thumbnails in rows of 3
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
        # Use a full width button in the center column
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
