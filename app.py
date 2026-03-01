import streamlit as st
import pandas as pd
import plotly.express as px
import re
import os
import time

import streamlit as st
from PIL import Image

# 1. Configuração da página (deve ser a primeira linha do Streamlit)
st.set_page_config(page_title="Burj Lavie Dash", layout="wide")

# --- COLE EXATAMENTE ASSIM ---

# Certifique-se de que não há espaços antes de 'col1'
col1, col2 = st.columns([1, 4])

with col1:
    # O comando abaixo deve ter exatamente 4 espaços de recuo
    st.write(" ") # Pequeno ajuste de respiro
    if os.path.exists("assets/logo.png"):
        st.image("assets/logo.png", width=120)
    else:
        st.subheader("🏗️")

st.divider()

# --- 2. CONSTANTES E LINKS ---
URL_CONTROLE = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRf-GmTIzVVaAz-x5uZR8kEE7CkO6MZLa5ChRmcsWdrX2mcr_NkK2jTZSSCJLTJgubWl9kSY16UupzA/pub?gid=1866404057&single=true&output=csv"
URL_VALOR_CONTRATO = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRf-GmTIzVVaAz-x5uZR8kEE7CkO6MZLa5ChRmcsWdrX2mcr_NkK2jTZSSCJLTJgubWl9kSY16UupzA/pub?gid=1669157044&single=true&output=csv"
URL_MEDICAO_SERVICOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRf-GmTIzVVaAz-x5uZR8kEE7CkO6MZLa5ChRmcsWdrX2mcr_NkK2jTZSSCJLTJgubWl9kSY16UupzA/pub?gid=1938534493&single=true&output=csv"

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

tab1, tab2, tab3 = st.tabs(["📊 Instalação & Financeiro", "📅 Recebimento", "📏 Medição Atual"])

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
                                       hole=0.6, title="Progresso Total (%)", color_discrete_map={'Instalado': '#2ECC71', 'Pendente': '#E74C3C'}), use_container_width=True)
            with cd:
                df_p = df_i.melt(id_vars='Referencia', value_vars=['M2 Instalado', 'Area Pendente'], var_name='Status', value_name='Metragem')
                st.plotly_chart(px.bar(df_p, x='Referencia', y='Metragem', color='Status', title="Progresso por Lote", barmode='stack',
                                       color_discrete_map={'M2 Instalado': '#2ECC71', 'Area Pendente': '#E74C3C'}), use_container_width=True)
                
                
# --- TAB 2: RECEBIMENTO ---
with tab2:
    df_raw_r = fetch_data(URL_CONTROLE)
    if not df_raw_r.empty:
        recebidos = []
        pares = [(7, 8), (9, 10), (11, 12), (13, 14), (15, 16)]
        for i in range(2, len(df_raw_r)):
            for col_d, col_q in pares:
                d_str = str(df_raw_r.iloc[i, col_d]).strip().lower()
                if d_str not in ["nan", "", "none", "0"]:
                    try:
                        dt = pd.to_datetime(d_str, dayfirst=True) if "/" in d_str else pd.to_datetime(float(d_str), unit='D', origin='1899-12-30')
                        recebidos.append({'Data': dt, 'Modulos': limpar_num(df_raw_r.iloc[i, col_q])})
                    except: continue
        
        if recebidos:
            df_r = pd.DataFrame(recebidos).groupby('Data')['Modulos'].sum().reset_index().sort_values('Data')
            df_r['Data_F'] = df_r['Data'].dt.strftime('%d/%m/%Y')
            st.subheader("📋 Gestão de Recebimento")
            ca, cb = st.columns(2)
            ca.metric("📦 Total Recebido", f"{int(df_r['Modulos'].sum())} un")
            cb.metric("🎯 Média p/ Entrega", f"{df_r['Modulos'].mean():.1f} un")
            st.plotly_chart(px.bar(df_r, x='Data_F', y='Modulos', text='Modulos', title="Histórico de Entregas", color_discrete_sequence=['#1E3A5F']))
            st.dataframe(df_r[['Data_F', 'Modulos']].rename(columns={'Data_F':'Data', 'Modulos':'Qtd'}), use_container_width=True, hide_index=True)

# --- TAB 3: MEDIÇÃO ATUAL ---
with tab3:
    st.subheader("📝 Relatório de Medição")
    df_m = fetch_data(URL_MEDICAO_SERVICOS)
    if not df_m.empty:
        flat_data = [str(x).strip() for x in df_m.values.flatten() if str(x) != 'nan']
        def find_v(label):
            for i, txt in enumerate(flat_data):
                if label in txt and i+1 < len(flat_data): return limpar_num(flat_data[i+1])
            return 0.0
        
        m2_real = find_v("M² Realizado Atual")
        v_bruto = (m2_real / METRAGEM_CONTRATO_FIXA) * VALOR_SERVICO_INSTALACAO
        
        k1, k2, k3 = st.columns(3)
        k1.metric("📏 M² Realizado", f"{m2_real:,.2f} m²")
        k2.metric("💰 Valor Bruto", f"R$ {v_bruto:,.2f}")
        k3.metric("💵 Líquido (-5%)", f"R$ {v_bruto * 0.95:,.2f}")
        
st.markdown(f"""
    <div style="
        background-color: rgba(248, 249, 250, 0.7); /* Cor cinza claro com 70% de opacidade */
        padding: 30px; 
        border-radius: 15px; 
        border-right: 8px solid #2ECC71;
        text-align: right; 
        width: 100%;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    ">
        <p style="font-size: 20px; margin-bottom: 0px; color: #666; font-family: sans-serif;">
            Total Contrato: <b>{METRAGEM_CONTRATO_FIXA:,.2f} m²</b>
        </p>
        <p style="font-size: 20px; margin-top: 5px; color: #666; font-family: sans-serif;">
            Executado: <b>{m2_real:,.2f} m²</b>
        </p>
        <hr style="border: 0; border-top: 1px solid #ddd; margin: 15px 0 15px auto; width: 40%;">
        <p style="margin-bottom: 0px; font-size: 18px; color: #2ECC71; font-weight: bold; font-family: sans-serif; letter-spacing: 1px;">
            LÍQUIDO A RECEBER
        </p>
        <p style="color: #2ECC71; font-size: 40px; font-weight: 900; line-height: 1; margin-top: 5px; font-family: sans-serif;">
            R$ {v_bruto * 0.95:,.2f}
        </p>
    </div>
""", unsafe_allow_html=True)
