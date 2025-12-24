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

# --- THE BRAIN (Now with Camera + Error Fixes) ---
# FIX: We add 'hash_funcs' to tell Streamlit how to handle the Image object
@st.cache_data(show_spinner=False, hash_funcs={Image.Image: lambda _: None})
def get_recipe(image_input):
    # Check if key is present
    if not api_key:
        return "🚨 Error: No API Key provided. Please check your Secrets."

    try:
        genai.configure(api_key=api_key)
        # Using 1.5-flash for better rate limits
        model = genai.GenerativeModel('gemini-1.5-flash') 
        
        prompt = """
        You are a creative chef. Look at this image of ingredients.
        1. Identify what ingredients are visible.
        2. Suggest a creative, delicious recipe using MAINLY these items.
        3. Assume user has basic staples (salt, oil, flour, water).
        """
        
        # Send the image to Google
        response = model.generate_content([prompt, image_input])
        return response.text
        
    except Exception as e:
        return f"Error: {e}"

# --- THE APP INTERFACE ---
st.title("📸 Iron Chef Vision")
st.write("Snap a photo of your fridge to get a recipe.")

# Tabs for Camera vs Upload
tab1, tab2 = st.tabs(["📸 Camera", "📂 Upload"])

image_to_process = None

with tab1:
    # This is the Selfie Camera
    camera_photo = st.camera_input("Take a picture")
    if camera_photo:
        image_to_process = Image.open(camera_photo)

with tab2:
    # This is the File Uploader
    uploaded_file = st.file_uploader("Choose a file", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image_to_process = Image.open(uploaded_file)

# --- THE COOKING ACTION ---
if image_to_process:
    # Display the image so you know it worked
    st.image(image_to_process, caption="Ingredients Detected", width=300)

    if st.button("👨‍🍳 Cook Something!"):
        with st.spinner("👨‍🍳 Chef is analyzing..."):
            # Call the AI (Now cached safely!)
            recipe = get_recipe(image_to_process)
            
            if "Error" in recipe:
                st.error(recipe)
            else:
                st.success("Recipe Generated!")
                st.markdown(recipe)
