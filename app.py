import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import os

# Configuração da Página
st.set_page_config(page_title="SisJornada CBMPA", page_icon="🚒", layout="wide")

# LISTAS DE CONFIGURAÇÃO
LISTA_UBMS = [
    "QCG", "ABM", "CFAE", "CIOP", "COP", "CSMV/MO", "GBS", "GRAESP", "GMAF",
    "1º GBM", "2º GBM", "3º GBM", "4º GBM", "5º GBM", "6º GBM", "7º GBM", "8º GBM", 
    "9º GBM", "10º GBM", "11º GBM", "12º GBM", "13º GBM", "14º GBM", "15º GBM",
    "16º GBM", "17º GBM", "18º GBM", "19º GBM", "20º GBM", "21º GBM", "22º GBM", 
    "23º GBM", "24º GBM", "25º GBM", "26º GBM", "27º GBM", "28º GBM", "29º GBM",
    "30º GBM", "31º GBM", "32º GBM", "33º GBM"
]

LISTA_POSTOS = [
    "CEL QOBM", "TEN CEL QOBM", "MAJ QOBM", "CAP QOBM", "1º TEN QOBM", "2º TEN QOBM", "ASP OF BM",
    "SUB TEN BM", "1º SGT BM", "2º SGT BM", "3º SGT BM", "CB BM", "SD BM"
]

# CLASSE DO PDF
class PDFRelatorio(FPDF):
    def header(self):
        # Tenta carregar o brasão se ele existir no repositório
        if os.path.exists("brasao.png"):
            self.image('brasao.png', 10, 8, 20)
        self.set_font('Arial', 'B', 12)
        self.cell(0, 5, 'CORPO DE BOMBEIROS MILITAR DO PARÁ', 0, 1, 'C')
        self.cell(0, 5, 'COORDENADORIA ESTADUAL DE DEFESA CIVIL', 0, 1, 'C')
        self.cell(0, 5, 'COMANDO OPERACIONAL', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}/{{nb}}', 0, 0, 'C')

# CARREGAR DADOS
@st.cache_data
def carregar_dados():
    try:
        df = pd.read_csv("dados.csv", dtype=str)
        # Cria nome de guerra automático (Primeiro + Último nome)
        def get_nome_guerra(nome):
            partes = nome.split()
            return f"{partes[0]} {partes[-1]}" if len(partes) > 1 else nome
            
        df['NOME_GUERRA_AUTO'] = df['NOME_COMPLETO'].apply(get_nome_guerra)
        df['BUSCA'] = df['NOME_COMPLETO'] + " (MF: " + df['MF'] + ")"
        return df
    except:
        return pd.DataFrame()

df_militares = carregar_dados()

# INTERFACE
st.title("🚒 SisJornada - CBMPA")
st.info("Preencha os dados da prevenção e selecione o efetivo.")

# 1. DADOS DO COMANDANTE
st.subheader("1. Responsável (Comandante da Prevenção)")
if not df_militares.empty:
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        cmt_nome = st.selectbox("Nome:", options=df_militares['BUSCA'].unique(), index=None)
    with col2:
        cmt_posto = st.selectbox("Posto:", options=LISTA_POSTOS, index=5) # Padrão 2º TEN
    with col3:
        cmt_ubm = st.selectbox("UBM:", options=LISTA_UBMS, index=0) # Padrão QCG

    dados_cmt = {}
    if cmt_nome:
        nome_real = df_militares[df_militares['BUSCA'] == cmt_nome]['NOME_COMPLETO'].values[0]
        dados_cmt = {"NOME": nome_real, "POSTO": cmt_posto, "UBM": cmt_ubm}

    st.markdown("---")
    
    # 2. DADOS DO SERVIÇO
    st.subheader("2. Dados do Serviço")
    c1, c2, c3, c4 = st.columns(4)
    ns_num = c1.text_input("Nota de Serviço", "084/2025")
    bg_num = c2.text_input("Boletim Geral", "187/2024")
    data_evento = c3.date_input("Data", datetime.today())
    local_evento = c4.text_input("Local", "Capela São José")
    
    c5, c6 = st.columns(2)
    hora_inicio = c5.time_input("Início Previsto", value=datetime.strptime("07:30", "%H:%M").time())
    hora_fim = c6.time_input("Término Previsto", value=datetime.strptime("17:00", "%H:%M").time())

    st.markdown("---")

    # 3. SELEÇÃO DA GUARNIÇÃO
    st.subheader("3. Montar Guarnição")
    guarnicao_nomes = st.multiselect(
        "Busque os militares (Nome ou MF):",
        options=df_militares['BUSCA'].unique()
    )

    if guarnicao_nomes:
        # Prepara dados para edição
        df_selecionado = df_militares[df_militares['BUSCA'].isin(guarnicao_nomes)].copy()
        
        # Cria colunas padrão para o usuário editar
        df_editor = df_selecionado[['NOME_COMPLETO', 'NOME_GUERRA_AUTO', 'MF']].copy()
        df_editor['POSTO_GRAD'] = "SD BM" # Valor inicial
        df_editor['UBM_ATUAL'] = "QCG"    # Valor inicial
        
        # Reorganiza
        df_editor = df_editor[['POSTO_GRAD', 'NOME_COMPLETO', 'NOME_GUERRA_AUTO', 'UBM_ATUAL', 'MF']]
        
        st.warning("👇 **ATENÇÃO:** Na tabela abaixo, clique nas colunas 'POSTO_GRAD' e 'UBM_ATUAL' para corrigir a graduação e unidade de cada militar.")
        
        # TABELA INTERATIVA
        df_final = st.data_editor(
            df_editor,
            column_config={
                "POSTO_GRAD": st.column_config.SelectboxColumn("Posto/Grad", width="medium", options=LISTA_POSTOS, required=True),
                "UBM_ATUAL": st.column_config.SelectboxColumn("UBM", width="medium", options=LISTA_UBMS, required=True),
                "NOME_COMPLETO": st.column_config.TextColumn("Nome Completo", disabled=True),
                "NOME_GUERRA_AUTO": st.column_config.TextColumn("Nome de Guerra"),
                "MF": st.column_config.TextColumn("Matrícula", disabled=True)
            },
            hide_index=True,
            use_container_width=True
        )

        # 4. GERAR PDF
        if st.button("🖨️ Gerar Relatório PDF", type="primary"):
            pdf = PDFRelatorio()
            pdf.alias_nb_pages()
            pdf.add_page()
            
            # Layout do PDF
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'RELATÓRIO DE PREVENÇÃO – JORNADA EXTRAORDINÁRIA', 0, 1, 'C')
            pdf.ln(5)
            
            # Bloco 1
            pdf.set_font('Arial', 'B', 10)
            pdf.set_fill_color(230, 230, 230)
            pdf.cell(0, 6, '1. DADOS INICIAIS', 1, 1, 'L', 1)
            
            pdf.set_font('Arial', '', 9)
            pdf.cell(40, 6, 'CMT DA PREVENÇÃO:', 1)
            pdf.cell(0, 6, f"{dados_cmt.get('POSTO', '')} {dados_cmt.get('NOME', '')}", 1, 1)
            pdf.cell(20, 6, 'UBM:', 1)
            pdf.cell(30, 6, f"{dados_cmt.get('UBM', '')}", 1)
            pdf.cell(35, 6, 'TOTAL EFETIVO:', 1)
            pdf.cell(20, 6, f"{len(df_final)} Militares", 1)
            pdf.cell(30, 6, 'DATA:', 1)
            pdf.cell(0, 6, f"{data_evento.strftime('%d/%m/%Y')}", 1, 1)
            pdf.cell(40, 6, 'LOCAL:', 1)
            pdf.cell(0, 6, f"{local_evento}", 1, 1)
            pdf.cell(40, 6, 'HORÁRIO:', 1)
            pdf.cell(0, 6, f"Das {hora_inicio.strftime('%Hh%M')} às {hora_fim.strftime('%Hh%M')}", 1, 1)
            pdf.cell(40, 6, 'REFERÊNCIA:', 1)
            pdf.cell(0, 6, f"NS Nº {ns_num} - BG Nº {bg_num}", 1, 1)
            pdf.ln(5)

            # Bloco 2
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 6, '2. EFETIVO EMPREGADO', 1, 1, 'L', 1)
            
            pdf.set_font('Arial', 'B', 8)
            # Cabeçalhos
            pdf.cell(10, 6, 'ORD', 1, 0, 'C')
            pdf.cell(25, 6, 'POSTO/GRAD', 1, 0, 'C')
            pdf.cell(85, 6, 'NOME COMPLETO', 1, 0, 'C')
            pdf.cell(30, 6, 'UBM', 1, 0, 'C')
            pdf.cell(25, 6, 'MATRÍCULA', 1, 1, 'C')
            
            pdf.set_font('Arial', '', 8)
            # Linhas da Tabela
            for i, row in enumerate(df_final.itertuples()):
                pdf.cell(10, 6, str(i+1), 1, 0, 'C')
                pdf.cell(25, 6, str(row.POSTO_GRAD), 1, 0, 'C')
                pdf.cell(85, 6, str(row.NOME_COMPLETO)[:45], 1, 0, 'L')
                pdf.cell(30, 6, str(row.UBM_ATUAL), 1, 0, 'C')
                pdf.cell(25, 6, str(row.MF), 1, 1, 'C')
            
            pdf.ln(10)
            
            # Assinatura
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 5, f'Belém-PA, {datetime.today().strftime("%d de %B de %Y")}', 0, 1, 'C')
            pdf.ln(15)
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 5, '__________________________________________________', 0, 1, 'C')
            pdf.cell(0, 5, f"{dados_cmt.get('NOME', '')}", 0, 1, 'C')
            pdf.cell(0, 5, f"{dados_cmt.get('POSTO', '')} - Comandante da Prevenção", 0, 1, 'C')

            # Saída
            pdf_output = pdf.output(dest='S').encode('latin-1')
            st.success("✅ Relatório gerado!")
            st.download_button("📥 Baixar PDF (Assinar no Gov.br)", pdf_output, "Relatorio.pdf", "application/pdf")
else:
    st.warning("Aguardando dados...")
