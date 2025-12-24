import streamlit as st
import google.generativeai as genai
from PIL import Image
import os
import base64

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

# --- 3. HELPER FUNCTIONS ---
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# --- 4. CUSTOM CSS ---
st.markdown("""
    <style>
        /* 1. TYPOGRAPHY CLEANUP */
        h1, h3 { text-align: center !important; }
        p { 
            text-align: center !important; 
            line-height: 1.6 !important; 
        }
        .block-container { padding-top: 1rem; padding-bottom: 0rem; }
        
        /* 2. BUTTON STYLING */
        div.stButton > button {
            border-radius: 50px;
            padding: 14px 32px;
            font-size: 18px;
            font-weight: 600;
            border: none;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }
        div.stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 8px rgba(0,0,0,0.15);
        }

        /* 3. PURPLE PRIMARY BUTTONS */
        button[kind="primary"] {
            background-color: #8A2BE2 !important;
            border: 1px solid #8A2BE2 !important;
            color: white !important;
        }
         button[kind="primary"]:hover {
            background-color: #6A1B9A !important;
            border: 1px solid #6A1B9A !important;
        }

        /* 4. HIDE DEFAULT ELEMENTS */
        #MainMenu {visibility: hidden;} 
        footer {visibility: hidden;} 
        header {visibility: hidden;}
        
        div[data-baseweb="select"] > div {
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

# --- 5. THE BRAIN ---
def get_recipe(images, style):
    if not api_key:
        return "🚨 Error: No API Key provided."
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash-lite') 
        
        # BASE PROMPT
        base_prompt = """
        You are a smart kitchen AI. Analyze these images of a kitchen/pantry.
        1. List ALL ingredients you see across all photos.
        2. Create a recipe based on the user's chosen style.
        """
        
        # STYLE MODIFIERS
        if style == "🥗 Healthy & Clean":
            style_instruction = "STYLE: HEALTHY. Focus on nutrition, low calorie, and fresh ingredients."
        elif style == "👧 For the Kids":
            style_instruction = "STYLE: KID FRIENDLY. Make it fun, colorful, and hide veggies if needed."
        elif style == "🍔 Let Myself Go":
            style_instruction = "STYLE: INDULGENT. Maximum flavor, cheese, butter. Comfort food."
        else: 
            style_instruction = "STYLE: Modern & Delicious. Standard chef quality."
            
        final_prompt = base_prompt + style_instruction + "\n3. Format the output cleanly with bold headers."
        content = [final_prompt] + images
        
        with st.spinner(f"Cooking up something {style}..."):
            response = model.generate_content(content)
            return response.text
            
    except Exception as e:
        return f"Error: {e}"

# --- 6. APP LAYOUT ---

# Initialize Session State
if 'ingredient_images' not in st.session_state:
    st.session_state.ingredient_images = []
if 'camera_open' not in st.session_state:
    st.session_state.camera_open = False
if 'camera_key' not in st.session_state:
    st.session_state.camera_key = 0

# A. LOGO SECTION
logo_path = None
if os.path.exists("logo.png"): logo_path = "logo.png"
elif os.path.exists("Logo.png"): logo_path = "Logo.png"
elif os.path.exists("logo.PNG"): logo_path = "logo.PNG"

if logo_path:
    img_base64 = get_base64_image(logo_path)
    st.markdown(
        f'<img src="data:image/png;base64,{img_base64}" style="display: block; margin-left: auto; margin-right: auto; width: 600px; max-width: 90vw;">',
        unsafe_allow_html=True,
    )
else:
    st.markdown("<h1 style='text-align: center;'>ChefLens</h1>", unsafe_allow_html=True)

st.markdown("""
    <p style='text-align: center; margin-top: -20px; font-size: 16px; opacity: 0.8;'>
        Visual Intelligence for Your Kitchen
    </p>
""", unsafe_allow_html=True)

st.write("")
st.write("")

# B. INPUT AREA
camera_placeholder = st.empty()

# --- STATE 1: START SCREEN ---
if not st.session_state.camera_open:
    # Disclaimer Text
    st.markdown("""
        <p style='text-align: center; color: #666; font-size: 18px; max-width: 85%; margin: 0 auto; line-height: 1.6;'>
            Snap a photo of your fridge, pantry, or leftovers.<br>
            We'll cook up a custom recipe in seconds.
        </p>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("Open Kitchen Camera", type="primary", use_container_width=True):
        st.session_state.camera_open = True
        st.rerun()

# --- STATE 2: CAMERA OPEN ---
else:
    st.markdown("<h3 style='text-align: center; font-size: 20px;'>Add Ingredients to Basket</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 10, 1])
    with col2:
        camera_photo = st.camera_input(
            label="Snap Photo", 
            label_visibility="hidden", 
            key=f"camera_{st.session_state.camera_key}"
        )
        
        # --- REVIEW LOGIC ---
        if camera_photo:
            st.write("")
            c1, c2 = st.columns(2)
            with c1:
                # Add Button
                if st.button("✅ Add to Basket", type="primary", use_container_width=True):
                    img = Image.open(camera_photo)
                    st.session_state.ingredient_images.append(img)
                    st.session_state.camera_key += 1
                    st.rerun()
            with c2:
                # Redo Button
                if st.button("🔄 Redo Photo", use_container_width=True):
                    st.session_state.camera_key += 1
                    st.rerun()

# C. REVIEW BASKET
if len(st.session_state.ingredient_images) > 0:
    st.write("")
    
    # Check if 'container' is supported (it usually is)
    with st.container(border=True):
        st.markdown(f"<p style='text-align: center; margin-bottom: 10px;'><b>🛒 Your Basket ({len(st.session_state.ingredient_images)} items)</b></p>", unsafe_allow_html=True)
        
        cols = st.columns(2)
        for idx, img in enumerate(st.session_state.ingredient_images):
            with cols[idx % 2]:
                st.image(img, use_container_width=True)
        
        st.write("")
        
        # EDIT CONTROLS
        c1, c2 = st.columns(2)
        with c1:
            if st.button("↩️ Undo Last", use_container_width=True):
                if st.session_state.ingredient_images:
                    st.session_state.ingredient_images.pop()
                    st.session_state.camera_key += 1
                    st.rerun()
        with c2:
            if st.button("🗑️ Clear All", use_container_width=True):
                st.session_state.ingredient_images = []
                st.session_state.camera_key += 1
                st.rerun()

    st.write("")
    
    # --- VIBE SELECTOR ---
    st.markdown("<h3 style='text-align: center; font-size: 20px; margin-bottom: 5px;'>What's the vibe today?</h3>", unsafe_allow_html=True)
    
    cooking_style = st.selectbox(
        "Vibe",
        ["🥗 Healthy & Clean", "👨‍🍳 Standard / Modern", "👧 For the Kids", "🍔 Let Myself Go"],
        index=1,
        label_visibility="collapsed"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("Generate Recipe", type="primary", use_container_width=True):
        if 'recipe_result' in st.session_state:
            del st.session_state['recipe_result']
        
        result = get_recipe(st.session_state.ingredient_images, cooking_style)
        st.session_state.recipe_result = result
        st.rerun()

# --- 7. RESULTS DISPLAY ---
if 'recipe_result' in st.session_state and st.session_state.recipe_result:
    st.markdown("---")
    if "Error" in st.session_state.recipe_result:
        st.error(st.session_state.recipe_result)
    else:
        st.subheader("👨‍🍳 Result")
        st.markdown(st.session_state.recipe_result)
