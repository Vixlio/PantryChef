import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- CONFIGURATION ---
st.set_page_config(page_title="Iron Chef Vision", page_icon="📸")

st.title("📸 Iron Chef Vision")
st.write("Snap a photo of your fridge or pantry. I'll handle the rest.")

# --- SIDEBAR: API KEY SETUP ---
with st.sidebar:
    st.header("🔑 Setup")
    api_key = st.text_input("Enter your Gemini API Key:", type="password")
    st.markdown("[Get a free key here](https://aistudio.google.com/app/apikey)")
    st.divider()
    st.write("This app uses **Gemini 1.5 Flash** for computer vision.")

# --- THE "BRAIN" (Vision Logic) ---
def get_recipe_from_image(image_input):
    # 1. Configure the model
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')

    # 2. The Hidden Prompt (The Wrapper)
    prompt = """
    You are a creative chef. Look at this image of ingredients.
    1. Identify what ingredients are visible.
    2. Suggest a creative, delicious recipe using MAINLY these items.
    3. You can assume user has basic staples (salt, oil, flour, water).
    4. Format the output with clear bold headings for 'Ingredients Found' and 'Instructions'.
    """

    # 3. The API Call (Image + Text)
    with st.spinner("👨‍🍳 Analyzing your ingredients..."):
        response = model.generate_content([prompt, image_input])
    
    return response.text

# --- THE APP INTERFACE ---

# 1. The Image Uploader
uploaded_file = st.file_uploader("Upload a fridge photo", type=["jpg", "jpeg", "png"])

# 2. Display the Image (so user knows it worked)
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Your Ingredients", use_column_width=True)

    # 3. The "Cook" Button
    if st.button("👨‍🍳 Cook Something!"):
        if not api_key:
            st.error("Please enter your API Key in the sidebar first!")
        else:
            try:
                # Call the AI
                recipe = get_recipe_from_image(image)
                st.success("Recipe Generated!")
                st.markdown(recipe)
            except Exception as e:
                st.error(f"An error occurred: {e}")
