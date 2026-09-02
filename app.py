import json
import os
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="PCP Supermercados Alvorada",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Estilização Adaptável + Fontes Maiores
st.markdown(
    """
    <style>
    .header-alvorada {
        background: linear-gradient(90deg, #FF6600 0%, #009944 100%);
        color: white !important;
        text-align: center;
        padding: 14px;
        border-radius: 8px;
        font-weight: bold;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.15);
        margin-bottom: 20px;
    }
    .badge-modo {
        text-align: center;
        padding: 10px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 16px !important;
        margin-bottom: 15px;
    }

    /* Aumenta a fonte geral da página */
    html, body, [class*="css"], .stMarkdown, p, span {
        font-size: 16px !important;
    }

    /* Melhora abas no celular */
    button[data-baseweb="tab"] {
        font-size: 15px !important;
        padding-left: 8px !important;
        padding-right: 8px !important;
    }

    @media (max-width: 768px) {
        h2 { font-size: 20px !important; }
        h3 { font-size: 18px !important; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- CONFIGURAÇÃO DE COLUNAS COM QUEBRA DE LINHA ATIVADA ---
config_colunas = {
    "Qtd": st.column_config.TextColumn("Qtd", width="small"),
    "Unidade": st.column_config.TextColumn("Unidade", width="small"),
    "Produto": st.column_config.TextColumn(
        "Produto", width="large"
    ),  # Largura expandida para caber nomes longos
}

# --- PERSISTÊNCIA DE DADOS ---
ARQUIVO_DADOS = "dados_pcp.json"


def carregar_banco():
    if os.path.exists(ARQUIVO_DADOS):
        with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"publicados": {}, "dados": {}, "setores": []}


def salvar_banco(db):
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)


db = carregar_banco()

st.title("🛒 PCP - Supermercados Alvorada")

# --- CONTROLE DE ACESSO ---
st.sidebar.header("🔐 Perfil de Acesso")
perfil = st.sidebar.radio(
    "Acessar como:", ["👁️ Líder (Apenas Visualizar)", "⚙️ Administrador"]
)

esolo_adm = False
if perfil == "⚙️ Administrador":
    senha = st.sidebar.text_input("Digite a senha de ADM:", type="password")
    if senha == "1234":
        esolo_adm = True
        st.sidebar.success("Acesso ADM Liberado!")
    else:
        if senha != "":
            st.sidebar.error("Senha incorreta!")

# Banners
if esolo_adm:
    st.markdown(
        "<div class='badge-modo' style='background-color: #d97706; color: #ffffff;'>⚙️ MODO ADMINISTRADOR - EDIÇÃO LIBERADA</div>",
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        "<div class='badge-modo' style='background-color: #009944; color: #ffffff;'>👁️ MODO LÍDER - VISUALIZAÇÃO DE DADOS PUBLICADOS</div>",
        unsafe_allow_html=True,
    )

# --- SETORES ---
setores_padrao = [
    "Panificação",
    "Pré-Pesagem",
    "Confeitaria / Bolos Secos",
    "Pratos Prontos",
    "Pão de Queijo / Salgados Fritos",
    "Salgados Assados",
    "Biscoitão",
    "Pizzas Congeladas",
    "Bolos Congelados",
    "Confeitaria / Sobremesas",
    "Levain",
    "Embalagem Congelada",
]

lista_setores = db.get("setores", [])
if not lista_setores:
    lista_setores = setores_padrao
    db["setores"] = lista_setores
    salvar_banco(db)

hoje = datetime.now()
inicio_semana_atual = hoje - timedelta(days=hoje.weekday())

opcoes_semanas = []
datas_semanas = {}

for i in range(-4, 5):
    inicio_sem = inicio_semana_atual + timedelta(weeks=i)
    fim_sem = inicio_sem + timedelta(days=6)
    label = f"Semana {inicio_sem.strftime('%d/%m')} a {fim_sem.strftime('%d/%m/%Y')}"
    if i == 0:
        label += " (Atual)"
    opcoes_semanas.append(label)
    datas_semanas[label] = inicio_sem

tipos_bolos = ["PLACA", "REDONDO", "COBERTURA", "CREMOSO", "INGLÊS", "CASEIRO"]

cores_bolos = {
    "PLACA": "background-color: #6c757d; color: #ffffff; font-weight: bold;",
    "INGLÊS": "background-color: #2b579a; color: #ffffff; font-weight: bold;",
    "CASEIRO": "background-color: #d97706; color: #ffffff; font-weight: bold;",
    "REDONDO": "background-color: #15803d; color: #ffffff; font-weight: bold;",
    "CREMOSO": "background-color: #ca8a04; color: #000000; font-weight: bold;",
    "COBERTURA": "background-color: #b91c1c; color: #ffffff; font-weight: bold;",
}


def colorir_linhas_bolo(row):
    tipo = row["Tipo de Bolo"]
    return [cores_bolos.get(tipo, "")] * len(row)


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
st.sidebar.markdown("---")
st.sidebar.header("🗓️ Período / Semana")
semana_ativa = st.sidebar.selectbox(
    "Selecione uma semana:", opcoes_semanas, index=4
)

data_inicio_selecionada = datas_semanas[semana_ativa]
dias_semana_com_data = []
nomes_dias = [
    "Segunda-Feira",
    "Terça-Feira",
    "Quarta-Feira",
    "Quinta-Feira",
    "Sexta-Feira",
    "Sábado",
    "Domingo",
]

for idx, nome_dia in enumerate(nomes_dias):
    data_dia = data_inicio_selecionada + timedelta(days=idx)
    dias_semana_com_data.append(
        {
            "nome": nome_dia,
            "data_curta": data_dia.strftime("%d/%m"),
            "data_completa": data_dia.strftime("%d/%m/%Y"),
            "label_aba": f"{nome_dia[:3]} ({data_dia.strftime('%d/%m')})",
        }
    )

st.sidebar.markdown("---")
st.sidebar.header("📂 Seleção de Setor")
setor_ativo = st.sidebar.radio("Escolha a Programação:", lista_setores)

chave_semana = f"{semana_ativa}_{setor_ativo}"
esta_publicado = db.get("publicados", {}).get(chave_semana, False)

# Recursos ADM
if esolo_adm:
    st.sidebar.markdown("---")
    st.sidebar.header("🚀 Publicação aos Líderes")

    if esta_publicado:
        st.sidebar.success("✅ ESTA PROGRAMAÇÃO ESTÁ PUBLICADA!")
        if st.sidebar.button("🔒 Desmarcar Publicação"):
            db["publicados"][chave_semana] = False
            salvar_banco(db)
            st.rerun()
    else:
        st.sidebar.warning("⚠️ Programação não publicada.")
        if st.sidebar.button("🚀 PUBLICAR PARA OS LÍDERES"):
            db["publicados"][chave_semana] = True
            salvar_banco(db)
            st.sidebar.success("Publicado com sucesso!")
            st.rerun()

    if st.sidebar.button("🚀 PUBLICAR TODOS OS SETORES DA SEMANA"):
        for s in lista_setores:
            db["publicados"][f"{semana_ativa}_{s}"] = True
        salvar_banco(db)
        st.sidebar.success("Todos os setores liberados!")
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.header("➕ Criar Novo Setor")
    novo_setor = st.sidebar.text_input(
        "Nome do setor:", placeholder="Ex: Salgados..."
    )
    if st.sidebar.button("Criar Setor"):
        if novo_setor.strip() and novo_setor not in lista_setores:
            lista_setores.append(novo_setor.strip())
            db["setores"] = lista_setores
            salvar_banco(db)
            st.sidebar.success(f"Setor '{novo_setor}' criado!")
            st.rerun()

# --- HEADER ALVORADA ---
st.markdown(
    f"<div class='header-alvorada'>"
    f"<h2>PROGRAMAÇÃO DE {setor_ativo.upper()}</h2>"
    f"<small>{semana_ativa.upper()}</small>"
    f"</div>",
    unsafe_allow_html=True,
)

# --- DIAS DA SEMANA COM DATA ---
st.write("### 📅 Selecione o dia:")
abas = st.tabs([item["label_aba"] for item in dias_semana_com_data])

for i, item_dia in enumerate(dias_semana_com_data):
    dia_nome = item_dia["nome"]
    dia_data_full = item_dia["data_completa"]

    with abas[i]:
        if not esolo_adm and not esta_publicado:
            st.info(
                "⏳ A programação desta semana ainda não foi publicada pelo Administrador."
            )
            continue

        if setor_ativo == "Confeitaria / Bolos Secos":
            st.markdown(f"### 📌 Confeitaria: {dia_nome} - {dia_data_full}")

            titulos_sub_abas = ["📋 Visão Geral"]
            for tipo in tipos_bolos:
                chave_item = f"{chave_semana}_{dia_nome}_{tipo}"
                tem_dados = (
                    chave_item in db["dados"] and len(db["dados"][chave_item]) > 0
                )
                indicador = "🟢" if tem_dados else "⚪"
                titulos_sub_abas.append(f"{indicador} {tipo}")

            sub_abas = st.tabs(titulos_sub_abas)

            # Visão Geral
            with sub_abas[0]:
                lista_geral = []
                for tipo in tipos_bolos:
                    chave_item = f"{chave_semana}_{dia_nome}_{tipo}"
                    dados_salvos = db["dados"].get(chave_item, [])
                    if dados_salvos:
                        df_temp = pd.DataFrame(dados_salvos)
                        df_temp.insert(0, "Tipo de Bolo", tipo)
                        lista_geral.append(df_temp)

                if lista_geral:
                    df_consolidado = pd.concat(lista_geral, ignore_index=True)
                    st.success(
                        f"**Resumo de Produção para {dia_nome} ({dia_data_full}):**"
                    )
                    df_estilizado = df_consolidado.style.apply(
                        colorir_linhas_bolo, axis=1
                    )
                    st.dataframe(
                        df_estilizado, use_container_width=True, hide_index=True
                    )
                else:
                    st.info(
                        f"Nenhum bolo cadastrado para {dia_nome} ({dia_data_full})."
                    )

            # Tipos de Bolos
            for j, tipo in enumerate(tipos_bolos):
                with sub_abas[j + 1]:
                    chave_item = f"{chave_semana}_{dia_nome}_{tipo}"
                    dados_existentes = db["dados"].get(chave_item, [])
                    df_atual = pd.DataFrame(dados_existentes)
                    if df_atual.empty:
                        df_atual = pd.DataFrame(
                            columns=["Qtd", "Unidade", "Produto"]
                        )

                    if esolo_adm:
                        col_tabela, col_colar = st.columns([2, 1])
                        with col_colar:
                            st.markdown(f"**📋 Colar itens ({tipo}):**")
                            texto_colado = st.text_area(
                                "Copie do Excel e cole:",
                                key=f"input_{chave_item}",
                                height=120,
                            )
                            if st.button(
                                f"💾 Salvar {tipo}", key=f"btn_{chave_item}"
                            ):
                                if texto_colado.strip():
                                    df_novo = processar_texto_colado(texto_colado)
                                    db["dados"][chave_item] = df_novo.to_dict(
                                        "records"
                                    )
                                    salvar_banco(db)
                                    st.success(f"{tipo} salvo!")
                                    st.rerun()

                        with col_tabela:
                            st.markdown(f"**Tipo de Bolo: {tipo}**")
                            df_editado = st.data_editor(
                                df_atual,
                                num_rows="dynamic",
                                use_container_width=True,
                                column_config=config_colunas,
                                key=f"editor_{chave_item}",
                            )
                            if st.button(
                                f"💾 Salvar Edição Manual ({tipo})",
                                key=f"save_manual_{chave_item}",
                            ):
                                db["dados"][chave_item] = df_editado.to_dict(
                                    "records"
                                )
                                salvar_banco(db)
                                st.success("Alterações salvas!")
                                st.rerun()
                    else:
                        st.markdown(f"**Tipo de Bolo: {tipo}**")
                        st.dataframe(
                            df_atual,
                            use_container_width=True,
                            hide_index=True,
                            column_config=config_colunas,
                        )

        else:
            # Setores Padrão
            chave_item = f"{chave_semana}_{dia_nome}"
            dados_existentes = db["dados"].get(chave_item, [])
            df_atual = pd.DataFrame(dados_existentes)
            if df_atual.empty:
                df_atual = pd.DataFrame(columns=["Qtd", "Unidade", "Produto"])

            if esolo_adm:
                col_tabela, col_colar = st.columns([2, 1])
                with col_colar:
                    st.markdown(f"**📋 Colar itens para {dia_nome}:**")
                    texto_colado = st.text_area(
                        "Copie do Excel e cole aqui:",
                        key=f"input_{chave_item}",
                        height=120,
                    )
                    if st.button(
                        f"💾 Importar para {dia_nome}", key=f"btn_{chave_item}"
                    ):
                        if texto_colado.strip():
                            df_novo = processar_texto_colado(texto_colado)
                            db["dados"][chave_item] = db["dados"].get(
                                chave_item, []
                            )
                            db["dados"][chave_item] = df_novo.to_dict("records")
                            salvar_banco(db)
                            st.success(f"Programação de {dia_nome} salva!")
                            st.rerun()

                with col_tabela:
                    st.markdown(f"### 📌 Programação: {dia_nome} - {dia_data_full}")
                    df_editado = st.data_editor(
                        df_atual,
                        num_rows="dynamic",
                        use_container_width=True,
                        column_config=config_colunas,
                        key=f"editor_{chave_item}",
                    )
                    if st.button(
                        f"💾 Salvar Alterações de {dia_nome}",
                        key=f"save_manual_{chave_item}",
                    ):
                        db["dados"][chave_item] = df_editado.to_dict("records")
                        salvar_banco(db)
                        st.success("Programação salva!")
                        st.rerun()
            else:
                st.markdown(f"### 📌 Programação: {dia_nome} - {dia_data_full}")
                st.dataframe(
                    df_atual,
                    use_container_width=True,
                    hide_index=True,
                    column_config=config_colunas,
                )