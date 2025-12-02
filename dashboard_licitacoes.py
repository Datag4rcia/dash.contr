import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Dashboard Licitações e Contratos",
    page_icon="📊",
    layout="wide"
)

# Título principal
st.title("📊 Dashboard de Licitações e Contratos")
st.markdown("---")

# Sidebar para upload de dados
with st.sidebar:
    st.header("⚙️ Configurações")
    uploaded_file = st.file_uploader("Carregue seu arquivo CSV", type=['csv'])
    
    st.markdown("---")
    st.markdown("### 📋 Variáveis esperadas:")
    st.markdown("""
    - licitacao_valor
    - licitacao_id
    - situacao_nome
    - secretaria_nome
    - ano
    - contrato_ano
    - contrato_valor
    - contrato_id
    - licitacao_data_ano
    - licitacao_data_mes
    - licitacao_data_dia
    - licitacao_data_weekday
    - contrato_data_ano
    - contrato_data_mes
    - contrato_data_dia
    - contrato_data_weekday
    - licitacao_categoria
    - contrato_categoria
    """)

# Função para carregar dados
@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    return df

# Verifica se há arquivo carregado
if uploaded_file is not None:
    df = load_data(uploaded_file)
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_licitacoes = df['licitacao_id'].nunique() if 'licitacao_id' in df.columns else 0
        st.metric("Total de Licitações", f"{total_licitacoes:,}")
    
    with col2:
        total_contratos = df['contrato_id'].nunique() if 'contrato_id' in df.columns else 0
        st.metric("Total de Contratos", f"{total_contratos:,}")
    
    with col3:
        if 'licitacao_valor' in df.columns:
            valor_total_lic = df['licitacao_valor'].sum()
            st.metric("Valor Total Licitações", f"R$ {valor_total_lic:,.2f}")
        else:
            st.metric("Valor Total Licitações", "N/A")
    
    with col4:
        if 'contrato_valor' in df.columns:
            valor_total_cont = df['contrato_valor'].sum()
            st.metric("Valor Total Contratos", f"R$ {valor_total_cont:,.2f}")
        else:
            st.metric("Valor Total Contratos", "N/A")
    
    st.markdown("---")
    
    # Filtros
    st.sidebar.markdown("---")
    st.sidebar.header("🔍 Filtros")
    
    # Filtro por ano
    if 'ano' in df.columns:
        anos = sorted(df['ano'].dropna().unique())
        ano_selecionado = st.sidebar.multiselect("Ano", anos, default=anos)
        df = df[df['ano'].isin(ano_selecionado)]
    
    # Filtro por secretaria
    if 'secretaria_nome' in df.columns:
        secretarias = sorted(df['secretaria_nome'].dropna().unique())
        secretaria_selecionada = st.sidebar.multiselect("Secretaria", secretarias, default=secretarias)
        df = df[df['secretaria_nome'].isin(secretaria_selecionada)]
    
    # Filtro por situação
    if 'situacao_nome' in df.columns:
        situacoes = sorted(df['situacao_nome'].dropna().unique())
        situacao_selecionada = st.sidebar.multiselect("Situação", situacoes, default=situacoes)
        df = df[df['situacao_nome'].isin(situacao_selecionada)]
    
    # Tabs para organizar visualizações
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Visão Geral", "🏢 Por Secretaria", "📅 Temporal", "📊 Detalhes"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de situações
            if 'situacao_nome' in df.columns:
                st.subheader("Distribuição por Situação")
                situacao_count = df['situacao_nome'].value_counts()
                fig = px.pie(values=situacao_count.values, names=situacao_count.index,
                           title="Licitações por Situação")
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Gráfico de categorias
            if 'licitacao_categoria' in df.columns:
                st.subheader("Categorias de Licitação")
                cat_count = df['licitacao_categoria'].value_counts().head(10)
                fig = px.bar(x=cat_count.values, y=cat_count.index, orientation='h',
                           title="Top 10 Categorias", labels={'x': 'Quantidade', 'y': 'Categoria'})
                st.plotly_chart(fig, use_container_width=True)
        
        # Gráfico de valores por ano
        if 'ano' in df.columns and 'licitacao_valor' in df.columns:
            st.subheader("Evolução de Valores por Ano")
            valores_ano = df.groupby('ano')['licitacao_valor'].sum().reset_index()
            fig = px.line(valores_ano, x='ano', y='licitacao_valor',
                         title="Valor Total de Licitações por Ano",
                         labels={'licitacao_valor': 'Valor (R$)', 'ano': 'Ano'})
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        if 'secretaria_nome' in df.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Licitações por Secretaria")
                sec_count = df['secretaria_nome'].value_counts().head(15)
                fig = px.bar(x=sec_count.values, y=sec_count.index, orientation='h',
                           labels={'x': 'Quantidade', 'y': 'Secretaria'})
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                if 'licitacao_valor' in df.columns:
                    st.subheader("Valores por Secretaria")
                    sec_valor = df.groupby('secretaria_nome')['licitacao_valor'].sum().sort_values(ascending=False).head(15)
                    fig = px.bar(x=sec_valor.values, y=sec_valor.index, orientation='h',
                               labels={'x': 'Valor (R$)', 'y': 'Secretaria'})
                    st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            # Análise por mês
            if 'licitacao_data_mes' in df.columns:
                st.subheader("Licitações por Mês")
                mes_count = df['licitacao_data_mes'].value_counts().sort_index()
                meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                        'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
                fig = px.bar(x=[meses[i-1] for i in mes_count.index], y=mes_count.values,
                           labels={'x': 'Mês', 'y': 'Quantidade'})
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Análise por dia da semana
            if 'licitacao_data_weekday' in df.columns:
                st.subheader("Licitações por Dia da Semana")
                weekday_count = df['licitacao_data_weekday'].value_counts().sort_index()
                dias = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
                fig = px.bar(x=[dias[i] for i in weekday_count.index], y=weekday_count.values,
                           labels={'x': 'Dia da Semana', 'y': 'Quantidade'})
                st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.subheader("📋 Tabela de Dados")
        
        # Selecionar colunas para exibir
        colunas_disponiveis = df.columns.tolist()
        colunas_selecionadas = st.multiselect(
            "Selecione as colunas para exibir:",
            colunas_disponiveis,
            default=colunas_disponiveis[:10]
        )
        
        if colunas_selecionadas:
            st.dataframe(df[colunas_selecionadas], use_container_width=True, height=400)
            
            # Botão para download
            csv = df[colunas_selecionadas].to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download CSV filtrado",
                data=csv,
                file_name=f'licitacoes_filtrado_{datetime.now().strftime("%Y%m%d")}.csv',
                mime='text/csv',
            )
        
        # Estatísticas descritivas
        if st.checkbox("Mostrar estatísticas descritivas"):
            st.subheader("Estatísticas Descritivas")
            st.dataframe(df.describe(), use_container_width=True)

else:
    st.info("👆 Por favor, carregue um arquivo CSV usando o menu lateral para começar a visualizar os dados.")
    
    # Instruções de uso
    st.markdown("""
    ### 🚀 Como usar este dashboard:
    
    1. **Carregue seus dados**: Use o menu lateral para fazer upload de um arquivo CSV
    2. **Explore as métricas**: Visualize os indicadores principais no topo da página
    3. **Aplique filtros**: Use os filtros laterais para segmentar os dados
    4. **Navegue pelas abas**: Explore diferentes visualizações e análises
    5. **Exporte dados**: Baixe os dados filtrados na aba "Detalhes"
    
    ### 📝 Formato do arquivo CSV:
    
    Seu arquivo deve conter as seguintes colunas (ou algumas delas):
    - Informações de licitação (valor, id, categoria, datas)
    - Informações de contrato (valor, id, categoria, datas)
    - Classificações (situação, secretaria, ano)
    """)

st.markdown("---")
st.markdown("*Dashboard desenvolvido com Streamlit + Plotly*")
