import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- CONFIGURATION ---
st.set_page_config(page_title="Iron Chef Vision", page_icon="📸")

# --- AUTHENTICATION ---
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Enter Gemini API Key", type="password")

# --- THE BRAIN ---
def get_recipe(image_input):
    if not api_key:
        return "🚨 Error: No API Key provided."
    
    try:
        genai.configure(api_key=api_key)
        
        # USE THE HIGH-LIMIT MODEL FROM YOUR SCREENSHOT
        model = genai.GenerativeModel('gemini-2.5-flash-lite') 
        
        prompt = """
        You are a creative chef. Look at this image of ingredients.
        1. Identify what ingredients are visible.
        2. Suggest a creative, delicious recipe using MAINLY these items.
        3. Assume user has basic staples (salt, oil, flour, water).
        """
        
        with st.spinner("👨‍🍳 Chef is analyzing..."):
            response = model.generate_content([prompt, image_input])
            return response.text
            
    except Exception as e:
        return f"Error: {e}"

# --- APP INTERFACE ---
st.title("📸 Iron Chef Vision")
st.write("Snap a photo of your fridge to get a recipe.")

# Session State (The Backpack)
if 'recipe_result' not in st.session_state:
    st.session_state.recipe_result = None

# Tabs
tab1, tab2 = st.tabs(["📸 Camera", "📂 Upload"])
image_to_process = None

with tab1:
    camera_photo = st.camera_input("Take a picture")
    if camera_photo:
        image_to_process = Image.open(camera_photo)

with tab2:
    uploaded_file = st.file_uploader("Choose a file", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image_to_process = Image.open(uploaded_file)

# --- THE COOKING ACTION ---
if image_to_process:
    st.image(image_to_process, caption="Ingredients Detected", width=300)

    if st.button("👨‍🍳 Cook Something!"):
        # Clear previous result first
        st.session_state.recipe_result = None 
        
        result = get_recipe(image_to_process)
        st.session_state.recipe_result = result
        st.rerun() # Force a refresh to show the new result

    # Display Result
    if st.session_state.recipe_result:
        if "Error" in st.session_state.recipe_result:
            st.error(st.session_state.recipe_result)
        else:
            st.success("Recipe Ready!")
            st.markdown(st.session_state.recipe_result)
