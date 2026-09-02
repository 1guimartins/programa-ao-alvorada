from datetime import datetime, timedelta
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="PCP Supermercados Alvorada",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Estilização
st.markdown(
    """
    <style>
    .stApp { background-color: #0f172a; }
    .header-alvorada {
        background: linear-gradient(90deg, #FF6600 0%, #009944 100%);
        color: white;
        text-align: center;
        padding: 12px;
        border-radius: 8px;
        font-weight: bold;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
        margin-bottom: 20px;
    }
    @media (max-width: 768px) {
        .stDataFrame { font-size: 12px; }
        h2 { font-size: 18px !important; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🛒 PCP - Supermercados Alvorada")

# --- CORREÇÃO DA LISTA DE SETORES ---
# Define os setores padrão sem puxar nomes antigos do cache
if "lista_setores" not in st.session_state or "Panqueca" in st.session_state["lista_setores"]:
    st.session_state["lista_setores"] = [
        "Panificação",
        "Pré-Pesagem",
        "Confeitaria / Bolos Secos",
    ]

hoje = datetime.now()
inicio_semana_atual = hoje - timedelta(days=hoje.weekday())

opcoes_semanas = []
for i in range(-4, 5):
    inicio_sem = inicio_semana_atual + timedelta(weeks=i)
    fim_sem = inicio_sem + timedelta(days=6)
    label = f"Semana {inicio_sem.strftime('%d/%m')} a {fim_sem.strftime('%d/%m/%Y')}"
    if i == 0:
        label += " (Atual)"
    opcoes_semanas.append(label)

dias_semana = [
    "Segunda-Feira",
    "Terça-Feira",
    "Quarta-Feira",
    "Quinta-Feira",
    "Sexta-Feira",
    "Sábado",
    "Domingo",
]

tipos_bolos = ["PLACA", "REDONDO", "COBERTURA", "CREMOSO", "INGLÊS", "CASEIRO"]

cores_bolos = {
    "PLACA": "background-color: #6c757d; color: white; font-weight: bold;",
    "INGLÊS": "background-color: #2b579a; color: white; font-weight: bold;",
    "CASEIRO": "background-color: #d97706; color: white; font-weight: bold;",
    "REDONDO": "background-color: #15803d; color: white; font-weight: bold;",
    "CREMOSO": "background-color: #ca8a04; color: black; font-weight: bold;",
    "COBERTURA": "background-color: #b91c1c; color: white; font-weight: bold;",
}


def colorir_linhas_bolo(row):
    tipo = row["Tipo de Bolo"]
    estilo = cores_bolos.get(tipo, "")
    return [estilo] * len(row)


def processar_texto_colado(texto):
    linhas = texto.strip().split("\n")
    dados = []
    for linha in linhas:
        partes = [p.strip() for p in linha.split("\t") if p.strip()]
        if len(partes) >= 3:
            dados.append(
                {"Qtd": partes[0], "Unidade": partes[1], "Produto": partes[2]}
            )
        elif len(partes) == 2:
            dados.append({"Qtd": partes[0], "Unidade": "", "Produto": partes[1]})
        elif len(partes) == 1:
            dados.append({"Qtd": "", "Unidade": "", "Produto": partes[0]})
    return pd.DataFrame(dados)


# --- BARRA LATERAL ---
st.sidebar.header("🗓️ Período / Semana")
semana_ativa = st.sidebar.selectbox(
    "Selecione uma semana:", opcoes_semanas, index=4
)

st.sidebar.markdown("---")
st.sidebar.header("📂 Seleção de Setor")
setor_ativo = st.sidebar.radio(
    "Escolha a Programação:", st.session_state["lista_setores"]
)

st.sidebar.markdown("---")
st.sidebar.header("➕ Criar Novo Setor")
novo_setor = st.sidebar.text_input(
    "Nome do novo setor:", placeholder="Ex: Salgados, Embalagem..."
)
if st.sidebar.button("Criar Setor"):
    if novo_setor.strip() and novo_setor not in st.session_state["lista_setores"]:
        st.session_state["lista_setores"].append(novo_setor.strip())
        st.sidebar.success(f"Setor '{novo_setor}' criado!")
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.header("⚙️ Gestão da Semana")

chave_pub = f"publicado_{semana_ativa}_{setor_ativo}"
if chave_pub not in st.session_state:
    st.session_state[chave_pub] = False

if st.session_state[chave_pub]:
    st.sidebar.success("✅ Esta semana está PUBLICADA!")
    if st.sidebar.button("🔓 Desproteger para Editar"):
        st.session_state[chave_pub] = False
        st.rerun()
else:
    if st.sidebar.button("🚀 Publicar Semana Inteira"):
        st.session_state[chave_pub] = True
        st.sidebar.success("Semana publicada aos líderes!")
        st.rerun()

if st.sidebar.button("🗑️ Excluir Programação desta Semana"):
    chaves_para_remover = [
        k for k in st.session_state.keys() if k.startswith(f"{semana_ativa}_{setor_ativo}")
    ]
    for k in chaves_para_remover:
        del st.session_state[k]
    st.sidebar.warning("Programação da semana apagada!")
    st.rerun()

# --- HEADER ALVORADA ---
st.markdown(
    f"<div class='header-alvorada'>"
    f"<h2>PROGRAMAÇÃO DE {setor_ativo.upper()}</h2>"
    f"<small>{semana_ativa.upper()}</small>"
    f"</div>",
    unsafe_allow_html=True,
)

# --- NAVEGAÇÃO DE DIAS ---
st.write("### 📅 Selecione o dia:")
abas = st.tabs([f"🗓️ {dia[:3]}" for dia in dias_semana])

for i, dia in enumerate(dias_semana):
    with abas[i]:
        if setor_ativo == "Confeitaria / Bolos Secos":
            st.markdown(f"### 📌 Confeitaria - {dia}")

            titulos_sub_abas = ["📋 Visão Geral"]
            for tipo in tipos_bolos:
                chave = f"{semana_ativa}_{setor_ativo}_{dia}_{tipo}"
                tem_dados = (
                    chave in st.session_state
                    and not st.session_state[chave].empty
                )
                indicador = "🟢" if tem_dados else "⚪"
                titulos_sub_abas.append(f"{indicador} {tipo}")

            sub_abas = st.tabs(titulos_sub_abas)

            # --- VISÃO GERAL ---
            with sub_abas[0]:
                lista_geral = []
                for tipo in tipos_bolos:
                    chave = f"{semana_ativa}_{setor_ativo}_{dia}_{tipo}"
                    if (
                        chave in st.session_state
                        and not st.session_state[chave].empty
                    ):
                        df_temp = st.session_state[chave].copy()
                        df_temp.insert(0, "Tipo de Bolo", tipo)
                        lista_geral.append(df_temp)

                if lista_geral:
                    df_consolidado = pd.concat(lista_geral, ignore_index=True)
                    st.success(f"**Resumo de Produção para {dia}:**")
                    df_estilizado = df_consolidado.style.apply(
                        colorir_linhas_bolo, axis=1
                    )
                    st.dataframe(
                        df_estilizado, use_container_width=True, hide_index=True
                    )
                else:
                    st.info(f"Nenhum bolo cadastrado para {dia} nesta semana.")

            # --- TIPOS INDIVIDUAIS ---
            for j, tipo in enumerate(tipos_bolos):
                with sub_abas[j + 1]:
                    chave_atual = f"{semana_ativa}_{setor_ativo}_{dia}_{tipo}"
                    if chave_atual not in st.session_state:
                        st.session_state[chave_atual] = pd.DataFrame(
                            columns=["Qtd", "Unidade", "Produto"]
                        )

                    col_tabela, col_colar = st.columns([2, 1])

                    with col_colar:
                        st.markdown(f"**📋 Colar itens ({tipo}):**")
                        texto_colado = st.text_area(
                            "Copie do Excel e cole:",
                            key=f"input_{chave_atual}",
                            height=120,
                            placeholder=f"Cole itens de {tipo}...",
                        )

                        if st.button(
                            f"💾 Salvar {tipo}", key=f"btn_{chave_atual}"
                        ):
                            if texto_colado.strip():
                                df_novo = processar_texto_colado(texto_colado)
                                st.session_state[chave_atual] = df_novo
                                st.success(f"{tipo} atualizado!")
                                st.rerun()

                    with col_tabela:
                        st.markdown(f"**Tipo de Bolo: {tipo}**")
                        df_editado = st.data_editor(
                            st.session_state[chave_atual],
                            num_rows="dynamic",
                            use_container_width=True,
                            key=f"editor_{chave_atual}",
                        )
                        st.session_state[chave_atual] = df_editado

        else:
            # Setores Padrão
            chave_atual = f"{semana_ativa}_{setor_ativo}_{dia}"
            if chave_atual not in st.session_state:
                st.session_state[chave_atual] = pd.DataFrame(
                    columns=["Qtd", "Unidade", "Produto"]
                )

            col_tabela, col_colar = st.columns([2, 1])

            with col_colar:
                st.markdown(f"**📋 Colar itens para {dia}:**")
                texto_colado = st.text_area(
                    "Copie do Excel e cole aqui:",
                    key=f"input_{chave_atual}",
                    height=120,
                    placeholder="Cole aqui (Ctrl+V)...",
                )

                if st.button(
                    f"💾 Importar para {dia}", key=f"btn_{chave_atual}"
                ):
                    if texto_colado.strip():
                        df_novo = processar_texto_colado(texto_colado)
                        st.session_state[chave_atual] = df_novo
                        st.success(f"Programação de {dia} atualizada!")
                        st.rerun()

            with col_tabela:
                st.markdown(f"### 📌 Programação: {dia}")
                df_editado = st.data_editor(
                    st.session_state[chave_atual],
                    num_rows="dynamic",
                    use_container_width=True,
                    key=f"editor_{chave_atual}",
                )
                st.session_state[chave_atual] = df_editado