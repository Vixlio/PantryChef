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

# --- THE BRAIN (Now with Memory!) ---
@st.cache_data(show_spinner=False)
def get_recipe(image_input):
    # Check if key is present
    if not api_key:
        return "🚨 Error: No API Key provided."

    try:
        genai.configure(api_key=api_key)
        # Use the stable 1.5 Flash model (High limits, fast speed)
        model = genai.GenerativeModel('gemini-1.5-flash') 
        
        prompt = """
        You are a creative chef. Look at this image of ingredients.
        1. Identify what ingredients are visible.
        2. Suggest a creative, delicious recipe using MAINLY these items.
        3. Assume user has basic staples (salt, oil, flour, water).
        """
        
        response = model.generate_content([prompt, image_input])
        return response.text
        
    except Exception as e:
        return f"Error: {e}"

# --- THE APP INTERFACE ---
st.title("📸 Iron Chef Vision")
st.write("Snap a photo of your fridge or upload one.")

# Tab Selection: Camera vs Upload
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

# --- THE COOKING LOGIC ---
if image_to_process:
    # Show the image so user knows what's happening
    st.image(image_to_process, caption="Ingredients Detected", width=300)

    if st.button("👨‍🍳 Cook Something!"):
        with st.spinner("👨‍🍳 Chef is analyzing..."):
            recipe = get_recipe(image_to_process)
            
            if "Error" in recipe:
                st.error(recipe)
            else:
                st.success("Recipe Generated!")
                st.markdown(recipe)
