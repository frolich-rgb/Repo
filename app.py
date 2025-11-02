import streamlit as st
from ultralytics import YOLO
from PIL import Image
import numpy as np
import cv2
import urllib.parse

# ------------------------------------------------------------
# ⚙️ Configuração inicial da página
# ------------------------------------------------------------
st.set_page_config(page_title="Detector de Roupas e Cores", page_icon="👕", layout="wide")
st.title("👕 Detector de Roupas e Cores — Estilo Google Lens")
st.write("Envie uma imagem e o sistema tentará identificar **a roupa e a cor predominante**.")

# ------------------------------------------------------------
# 🚀 Cache do modelo (evita recarregar a cada execução)
# ------------------------------------------------------------
@st.cache_resource
def load_model():
    return YOLO("yolov8n.pt")

model = load_model()

# ------------------------------------------------------------
# 🎨 Funções auxiliares
# ------------------------------------------------------------
def get_color_name(rgb):
    """Recebe um valor RGB e retorna o nome da cor em português"""
    r, g, b = rgb
    colors = {
        "vermelho": (255, 0, 0),
        "verde": (0, 255, 0),
        "azul": (0, 0, 255),
        "amarelo": (255, 255, 0),
        "preto": (0, 0, 0),
        "branco": (255, 255, 255),
        "cinza": (128, 128, 128),
        "laranja": (255, 165, 0),
        "rosa": (255, 192, 203),
        "roxo": (128, 0, 128),
        "marrom": (139, 69, 19),
    }
    closest = min(colors.keys(), key=lambda c: np.linalg.norm(np.array(colors[c]) - np.array([r, g, b])))
    return closest

def get_predominant_color(image_region):
    """Calcula a cor predominante média da região"""
    np_img = np.array(image_region)
    np_img = cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR)
    avg_color = np_img.mean(axis=(0, 1))
    b, g, r = avg_color
    return get_color_name((r, g, b))

# ------------------------------------------------------------
# 📸 Upload da imagem
# ------------------------------------------------------------
uploaded_file = st.file_uploader("📸 Envie uma imagem", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    try:
        image = Image.open(uploaded_file)
        st.image(np.array(image), caption="🖼️ Imagem enviada", use_column_width=True)
    except Exception as e:
        st.error(f"Erro ao abrir a imagem: {e}")
    else:
        st.info("Analisando imagem... aguarde alguns segundos ⏳")

        # ------------------------------------------------------------
        # 🔍 Detecção com YOLOv8
        # ------------------------------------------------------------
        results = model(image)
        annotated_image = results[0].plot()

        st.image(annotated_image, caption="🔎 Detecção de objetos", use_column_width=True)

        roupas_detectadas = []_
