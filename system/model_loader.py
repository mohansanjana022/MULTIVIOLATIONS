import torch
from transformers import DistilBertModel

def load_model():

    model = DistilBertModel.from_pretrained("distilbert-base-uncased")

    model.load_state_dict(
        torch.load("models/distilbert_multilabel_traffic.pth",
        map_location=torch.device("cpu"))
    )

    model.eval()

    return model

# import os
# import torch
# import requests
# from transformers import DistilBertModel
# import streamlit as st

# MODEL_URL = "https://huggingface.co/sanjanaM123/traffic-risk-model/resolve/main/distilbert_multilabel_traffic.pth"
# MODEL_PATH = "model.pth"

# @st.cache_resource
# def load_model():
#     # Step 1: Download model only if not exists
#     if not os.path.exists(MODEL_PATH):
#         with st.spinner("Downloading model... ⏳"):
#             response = requests.get(MODEL_URL, timeout=60)
#             with open(MODEL_PATH, "wb") as f:
#                 f.write(response.content)

#     # Step 2: Load base model
#     model = DistilBertModel.from_pretrained("distilbert-base-uncased")

#     # Step 3: Load trained weights
#     model.load_state_dict(
#         torch.load(MODEL_PATH, map_location=torch.device("cpu"))
#     )

#     # Step 4: Set evaluation mode
#     model.eval()

#     return model