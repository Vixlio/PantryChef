import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- CONFIGURATION ---
st.set_page_config(page_title="ChefLens", page_icon="🍳", layout="centered")

# --- AUTHENTICATION ---
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

# --- CUSTOM CSS ---
st.markdown("""
    <style>
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
            padding: 10px 10px;
            font-size: 14px;
            font-weight: 500;
        }
        div.stButton > button:hover {
            background-color: #f8f9fa;
            border: 1px solid #dadce0;
            box-shadow: 0 1px 1px rgba(0,0,0,.1);
            color: #202124;
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- THE BRAIN ---
def get_recipe(image_input):
    if not api_key:
        return "🚨 Error: No API Key provided."
    
    try:
        genai.configure(api_key=api_key)
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

# --- APP LAYOUT ---

# 1. THE LOGO (Real Image Version)
# We use columns to center the image. 
# [1, 2, 1] means: (Empty Space) - (Logo) - (Empty Space)
left_co, cent_co, last_co = st.columns([1, 2, 1])

with cent_co:
    # TRY to load the logo. If it fails, show text instead.
    try:
        # Make sure your file on GitHub is named EXACTLY "logo.png" (case sensitive!)
        st.image("logo.png", width=350) 
    except:
        st.error("Logo not found. Upload 'logo.png' to GitHub!")

st.markdown("Visual Intelligence for Your Kitchen")

# 2. The Input Area
col1, col2, col3 = st.columns([1, 6, 1])

with col2:
    tab_cam, tab_up = st.tabs(["📸 Camera", "📂 Upload"])
    image_to_process = None
    
    with tab_cam:
        camera_photo = st.camera_input("Snap a photo")
        if camera_photo:
            image_to_process = Image.open(camera_photo)
            
    with tab_up:
        uploaded_file = st.file_uploader("Choose a file", type=["jpg", "png"])
        if uploaded_file:
            image_to_process = Image.open(uploaded_file)

    st.write("")
    if image_to_process:
        if st.button("Generate Recipe"):
            if 'recipe_result' in st.session_state:
                del st.session_state['recipe_result']
            
            result = get_recipe(image_to_process)
            st.session_state.recipe_result = result
            st.rerun()

# --- RESULTS ---
if 'recipe_result' in st.session_state and st.session_state.recipe_result:
    st.markdown("---")
    if "Error" in st.session_state.recipe_result:
        st.error(st.session_state.recipe_result)
    else:
        st.subheader("👨‍🍳 Result")
        st.markdown(st.session_state.recipe_result)
