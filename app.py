import streamlit as st
import pandas as pd
import plotly.express as px
import re
import os
import time

# 1. Configuração da página (deve ser a primeira linha do Streamlit)
st.set_page_config(page_title="Burj Lavie Dash", layout="wide")

# Certifique-se de que não há espaços antes de 'col1'
col1, col2 = st.columns([1, 4])

with col1:
    # Ajuste de respiro com espaços padrão
    st.write(" ") 
    if os.path.exists("assets/logo.png"):
        st.image("assets/logo.png", width=120)
    else:
        st.subheader(" ")

st.divider()

# --- 2. CONSTANTES E LINKS ---
URL_CONTROLE = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRVExszkNXNNlYOBVkCnjwrcBFFDj7XX-H5oOkAmOfOIjCySfPINUOYDnuv1Y5o3A/pub?gid=1498853259&single=true&output=csv"
URL_VALOR_CONTRATO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRVExszkNXNNlYOBVkCnjwrcBFFDj7XX-H5oOkAmOfOIjCySfPINUOYDnuv1Y5o3A/pub?gid=1894460667&single=true&output=csv"
URL_MEDICAO_SERVICOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRVExszkNXNNlYOBVkCnjwrcBFFDj7XX-H5oOkAmOfOIjCySfPINUOYDnuv1Y5o3A/pub?gid=1458244410&single=true&output=csv"

VALOR_SERVICO_INSTALACAO = 140000.00
METRAGEM_CONTRATO_FIXA = 1572.48
IMG_LOGO = "assets/burj_lavie2.jpg"

# --- 3. ESTILIZAÇÃO CUSTOMIZADA ---
def apply_custom_styles():
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("https://okayimoveispb.com.br/wp-content/uploads/2024/10/WhatsApp-Image-2024-10-09-at-3.06.13-PM-1.jpeg");
            background-attachment: fixed; background-size: cover;
        }}
        [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {{
            background-color: rgba(255, 255, 255, 0.85);
            padding: 5px 10px; border-radius: 8px; color: #1E3A5F !important;
        }}
        .main-header {{ display: flex; align-items: center; margin-bottom: 20px; }}
        </style>
    """, unsafe_allow_html=True)

apply_custom_styles()

# --- 4. FUNÇÕES DE SUPORTE E DADOS ---
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

@st.cache_data(ttl=600) # Cache de 10 minutos
def fetch_data(url):
    try:
        # Adiciona timestamp para evitar cache do Google
        return pd.read_csv(f"{url}&cache={int(time.time())}", header=None, dtype=str)
    except:
        return pd.DataFrame()

# --- 5. CABEÇALHO E SIDEBAR ---
with st.sidebar:
    if os.path.exists(IMG_LOGO): st.image(IMG_LOGO, use_container_width=True)
    st.title("Menu de Navegação")
    st.divider()

col_l, col_t = st.columns([0.1, 0.9])
with col_l:
    if os.path.exists(IMG_LOGO): st.image(IMG_LOGO, width=80)
with col_t:
    st.title("BURJ LAVIE")

tab1, tab2, tab3, tab4 = st.tabs(["Instalação", "Financeiro", "Medição Atual", "Imprimir Medição"])

# --- TAB 1: INSTALAÇÃO E FINANCEIRO ---
with tab1:
    df_contrato = fetch_data(URL_VALOR_CONTRATO)
    v_total_contrato = limpar_num(df_contrato.iloc[2, 1]) if not df_contrato.empty else 1750000.0
    
    df_raw = fetch_data(URL_CONTROLE)
    if not df_raw.empty:
        setor = df_raw.iloc[2:]
        dados_i = []
        for _, row in setor.iterrows():
            ref = str(row[0]).strip()
            if ref and ref != 'nan':
                area_t = limpar_num(row[6])
                m2_inst = limpar_num(row[21])
                dados_i.append({'Referencia': ref, 'Area Total': area_t, 'M2 Instalado': m2_inst, 'Area Pendente': max(0.0, area_t - m2_inst)})
        
        df_i = pd.DataFrame(dados_i)
        if not df_i.empty:
            pago_m2 = df_i['M2 Instalado'].sum()
            progresso_pct = (pago_m2 / METRAGEM_CONTRATO_FIXA)
            v_medido_bruto = progresso_pct * VALOR_SERVICO_INSTALACAO
            valor_retencao = v_medido_bruto * 0.05
            
            st.subheader("💰 Resumo Financeiro")
            m1, m2, m3 = st.columns(3)
            m1.metric("🛠️ Total do Serviço", f"R$ {VALOR_SERVICO_INSTALACAO:,.2f}")
            m2.metric("Meta Total", f"{METRAGEM_CONTRATO_FIXA:,.2f} m²")
            m3.metric("✅ Instalado", f"{pago_m2:,.2f} m²", f"{progresso_pct*100:.1f}%")

            st.divider()
            c1, c2, c3 = st.columns(3)
            c1.metric("💵 Medição Líquida", f"R$ {v_medido_bruto - valor_retencao:,.2f}")
            c2.metric("🔒 Retenção (5%)", f"R$ {valor_retencao:,.2f}")
            c3.metric("💳 Saldo a Receber", f"R$ {max(0.0, VALOR_SERVICO_INSTALACAO - v_medido_bruto):,.2f}")
            
            st.metric("📄 Contrato Global (Compra)", f"R$ {v_total_contrato:,.2f}")

            st.markdown("### 📊 Análise de Progresso")
            ce, cd = st.columns([1, 1.5])
            with ce:
                st.plotly_chart(px.pie(names=['Instalado', 'Pendente'], values=[pago_m2, max(0.0, METRAGEM_CONTRATO_FIXA-pago_m2)], 
                                       hole=0.6,