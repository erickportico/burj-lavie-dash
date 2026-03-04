import streamlit as st
import pandas as pd
import plotly.express as px
import re
import os
import time

# ==============================================================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
st.set_page_config(page_title="Burj Lavie Dash", layout="wide")

# Cabeçalho Superior (Logo e Espaçamento)
col1, col2 = st.columns([1, 4])
with col1:
    st.write(" ") 
    if os.path.exists("assets/logo.png"):
        st.image("assets/logo.png", width=120)
    else:
        st.subheader(" ")

st.divider()

# ==============================================================================
# 2. CONSTANTES E LINKS (GOOGLE SHEETS)
# ==============================================================================
URL_CONTROLE = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRVExszkNXNNlYOBVkCnjwrcBFFDj7XX-H5oOkAmOfOIjCySfPINUOYDnuv1Y5o3A/pub?gid=1498853259&single=true&output=csv"
URL_VALOR_CONTRATO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRVExszkNXNNlYOBVkCnjwrcBFFDj7XX-H5oOkAmOfOIjCySfPINUOYDnuv1Y5o3A/pub?gid=1894460667&single=true&output=csv"
URL_MEDICAO_SERVICOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRVExszkNXNNlYOBVkCnjwrcBFFDj7XX-H5oOkAmOfOIjCySfPINUOYDnuv1Y5o3A/pub?gid=1458244410&single=true&output=csv"

VALOR_SERVICO_INSTALACAO = 140000.00
METRAGEM_CONTRATO_FIXA = 1572.48
IMG_LOGO = "assets/burj_lavie2.jpg"

# ==============================================================================
# 3. ESTILIZAÇÃO CUSTOMIZADA (CSS)
# ==============================================================================
def apply_custom_styles():
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("https://okayimoveispb.com.br/wp-content/uploads/2024/10/WhatsApp-Image-2024-10-09-at-3.06.13-PM-1.jpeg");
            background-attachment: fixed; 
            background-size: cover;
        }}
        [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {{
            background-color: rgba(255, 255, 255, 0.85);
            padding: 5px 10px; 
            border-radius: 8px; 
            color: #1E3A5F !important;
        }}
        .main-header {{ display: flex; align-items: center; margin-bottom: 20px; }}
        
        /* Estilização do Card de Resumo Financeiro */
        .resumo-card {{
            background-color: rgba(248, 249, 250, 0.7);
            padding: 30px; 
            border-radius: 15px; 
            border-right: 8px solid #2ECC71;
            text-align: right; 
            width: 100%;
            box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        }}
        </style>
    """, unsafe_allow_html=True)

apply_custom_styles()

# ==============================================================================
# 4. FUNÇÕES DE SUPORTE E TRATAMENTO DE DADOS
# ==============================================================================
def limpar_num(val):
    if pd.isna(val) or val == "": return 0.0
    try:
        val_limpo = re.sub(r'[^\d,.-]', '', str(val).strip())
        if ',' in val_limpo and '.' in val_limpo:
            val_limpo = val_limpo.replace('.', '').replace(',', '.')
        elif ',' in val_limpo:
            val_limpo = val_limpo.replace(',', '.')
        return float(val_limpo)
    except: return 0.0

@st.cache_data(ttl=600)
def fetch_data(url):
    try:
        # Adiciona timestamp para forçar atualização no Google
        return pd.read_csv(f"{url}&cache={int(time.time())}", header=None, dtype=str)
    except:
        return pd.DataFrame()

# ==============================================================================
# 5. SIDEBAR E TÍTULO PRINCIPAL
# ==============================================================================
with st.sidebar:
    if os.path.exists(IMG_LOGO): 
        st.image(IMG_LOGO, use_container_width=True)
    st.title("Menu de Navegação")
    st.divider()

# Banner do Título
col_l, col_t = st.columns([0.1, 0.9])
with col_l:
    if os.path.exists(IMG_LOGO): st.image(IMG_LOGO, width=80)
with col_t:
    st.title("BURJ LAVIE")

# Definição das Abas
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Instalação", 
    "📦 Recebimento", 
    "📝 Medição Atual", 
    "🖨️ Imprimir Medição"
])

# ==============================================================================
# TAB 1: INSTALAÇÃO E FINANCEIRO
# ==============================================================================
with tab1:
    df_contrato = fetch_data(URL_VALOR_CONTRATO)
    v_total_contrato = limpar_num(df_contrato.iloc[2, 1]) if not df_contrato.empty else 1750000.0
    
    df_raw = fetch_data(URL_CONTROLE)
    if not df_raw.empty:
        setor = df_raw.iloc[2:]
        dados_i = []
        for _, row in