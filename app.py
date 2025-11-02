import streamlit as st
from ultralytics import YOLO
from PIL import Image
import numpy as np
import cv2
import urllib.parse

# Carrega o modelo YOLOv8 (pode trocar depois por YOLOv8-clothes.pt)
model = YOLO("yolov8n.pt")

st.set_page_config(page_title="Detector de Roupas e Cores", page_icon="👕", layout="wide")
st.title("👕 Detector de Roupas e Cores — Estilo Google Lens")
st.write("Envie uma imagem e o sistema tentará identificar **a roupa e a cor predominante**.")

# --- Funções auxiliares ---

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

# --- Interface Streamlit ---

uploaded_file = st.file_uploader("📸 Envie uma imagem", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    try:
        image = Image.open(uploaded_file)
        st.image(np.array(image), caption="🖼️ Imagem enviada", use_container_width=True)
    except Exception as e:
        st.error(f"Erro ao abrir a imagem: {e}")


    st.info("Analisando imagem... aguarde alguns segundos ⏳")
    results = model(image)

    annotated_image = results[0].plot()
    st.image(annotated_image, caption="🔎 Detecção de objetos", use_container_width=True)

    roupas_detectadas = []

    for box in results[0].boxes:
        cls = int(box.cls[0])
        obj_name = results[0].names[cls]

        # Considera pessoa como roupa (por enquanto)
        if obj_name == "person":
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            region = image.crop((x1, y1, x2, y2))
            color_name = get_predominant_color(region)
            roupas_detectadas.append(f"camisa {color_name}")

    if roupas_detectadas:
        st.subheader("👕 Roupas identificadas:")
        for desc in roupas_detectadas:
            st.success(desc)
            # URL de pesquisa da SHEIN Brasil
            shein_link = f"https://br.shein.com/pdsearch/{urllib.parse.quote(desc)}/"
            st.markdown(f"[🛍️ Ver {desc} na Shein Brasil]({shein_link})")
    else:
        st.warning("Nenhuma roupa reconhecida.")
