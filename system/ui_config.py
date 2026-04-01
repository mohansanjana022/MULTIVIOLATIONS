# import streamlit as st
# import base64

# def apply_global_style():

#     def get_base64(file):
#         with open(file, "rb") as f:
#             return base64.b64encode(f.read()).decode()

#     bg_img = get_base64("assets/bg.png")

#     st.markdown(f"""
#     <style>

#     /* REMOVE SCROLL + DEFAULT SPACE */
#     html, body, [data-testid="stAppViewContainer"] {{
#         height: 100%;
#         margin: 0;
#         padding: 0;
#     }}

#     .block-container {{
#         padding: 2rem 3rem !important;
#     }}

#     header, footer {{
#         display: none !important;
#     }}

#     /* 🔥 FULL APP BACKGROUND */
#     [data-testid="stAppViewContainer"] {{
#         background:
#             linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.85)),
#             url("data:image/png;base64,{bg_img}") !important;
#         background-size: cover !important;
#         background-position: center !important;
#         background-attachment: fixed;
#     }}
#     h1, h2, h3, h4, h5, h6, p, span, label {{
#         color: white !important;
#     }}

#     /* 🔥 GLASS CONTAINER */
#     .glass {{
#         background: rgba(255,255,255,0.08);
#         backdrop-filter: blur(18px);
#         -webkit-backdrop-filter: blur(18px);
#         border-radius: 16px;
#         padding: 25px;
#         border: 1px solid rgba(255,255,255,0.2);
#         box-shadow: 0 10px 40px rgba(0,0,0,0.6);
#         color: white;
#     }}

#     /* HEADINGS */
#     h1, h2, h3 {{
#         color: white !important;
#     }}

#     /* INPUTS */
#     input, textarea {{
#         background: rgba(255,255,255,0.9) !important;
#         border-radius: 10px !important;
#     }}

#     /* BUTTON */
#     .stButton > button {{
#         background: linear-gradient(90deg,#ff4b2b,#ff416c);
#         color: white;
#         border-radius: 10px;
#         border: none;
#         font-weight: 600;
#     }}

#     .stButton > button:hover {{
#         transform: scale(1.05);
#         box-shadow: 0 5px 20px rgba(255,65,108,0.5);
#     }}

#     </style>
#     """, unsafe_allow_html=True)

import streamlit as st
import base64

def apply_global_style():

    def get_base64(file):
        with open(file, "rb") as f:
            return base64.b64encode(f.read()).decode()

    bg_img = get_base64("assets/bg.png")

    st.markdown(f"""
    <style>

    html, body, [data-testid="stAppViewContainer"] {{
        height: 100%;
        margin: 0;
        padding: 0;
    }}

    header, footer {{
        display: none !important;
    }}

    /* 🔥 FULL BACKGROUND */
    [data-testid="stAppViewContainer"] {{
        background:
            linear-gradient(rgba(0,0,0,0.75), rgba(0,0,0,0.85)),
            url("data:image/png;base64,{bg_img}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}

    # /* 🔥 TEXT VISIBILITY FIX */
    # span, label {{
    #     color: #f9fafb !important;
    # }}

    /* 🔥 GLASS CARD */
    .glass {{
        background: rgba(255,255,255,0.08);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 18px;
        padding: 25px;
        border: 1px solid rgba(255,255,255,0.2);
        box-shadow: 0 10px 40px rgba(0,0,0,0.7);
        color: white;
        margin-bottom: 20px;
    }}

    /* 🔥 INPUTS */
    input, textarea {{
        background: rgba(255,255,255,0.95) !important;
        border-radius: 10px !important;
        color: black !important;
    }}

    /* 🔥 BUTTON */
    .stButton > button {{
        background: linear-gradient(90deg,#ff4b2b,#ff416c);
        color: white;
        border-radius: 10px;
        border: none;
        font-weight: 600;
    }}

    .stButton > button:hover {{
        transform: scale(1.05);
        box-shadow: 0 5px 20px rgba(255,65,108,0.5);
    }}

    </style>
    """, unsafe_allow_html=True)