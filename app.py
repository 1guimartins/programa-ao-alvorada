import json
import os
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="PCP Supermercados Alvorada",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- ESTILIZAÇÃO CSS ADAPTÁVEL E OTIMIZADA ---
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
    html, body, [class*="css"], .stMarkdown, p, span {
        font-size: 16px !important;
    }
    div[data-testid="stDataFrame"] div[role="gridcell"] {
        white-space: normal !important;
        word-wrap: break-word !important;
        font-size: 15px !important;
        line-height: 1.4 !important;
    }
    div[data-testid="stDataFrame"] div[role="columnheader"] {
        font-size: 16px !important;
        font-weight: bold !important;
    }
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

# --- CONFIGURAÇÃO DE COLUNAS DA TABELA PADRÃO ---
config_colunas = {
    "Status": st.column_config.SelectboxColumn(
        "Status",
        options=["⏳ Pendente", "🔄 Em Produção", "✅ Concluído"],
        default="⏳ Pendente",
        width="medium",
    ),
    "Qtd": st.column_config.TextColumn("Qtd", width="small"),
    "Unidade": st.column_config.TextColumn("Unidade", width="small"),
    "Produto": st.column_config.TextColumn("Produto", width="large"),
}

# --- PERSISTÊNCIA DE DADOS (CRIAÇÃO AUTOMÁTICA DO JSON) ---
ARQUIVO_DADOS = "dados_pcp.json"


def carregar_banco():
    if os.path.exists(ARQUIVO_DADOS):
        with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"publicados": {}, "dados": {}, "setores": [], "metas_semanais": {}}


def salvar_banco(db):
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)


db = carregar_banco()

st.title("🛒 PCP - Supermercados Alvorada")

# --- CONTROLE DE ACESSO ---
st.sidebar.header("🔐 Perfil de Acesso")
perfil = st.sidebar.radio(
    "Acessar como:", ["👁️ Líder (Visualização / Status)", "⚙️ Administrador"]
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

# Banners de perfil
if esolo_adm:
    st.markdown(
        "<div class='badge-modo' style='background-color: #d97706; color: #ffffff;'>⚙️ MODO ADMINISTRADOR - EDIÇÃO E CONFIGURAÇÕES LIBERADAS</div>",
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        "<div class='badge-modo' style='background-color: #009944; color: #ffffff;'>👁️ MODO LÍDER - VISUALIZAÇÃO E MARCAÇÃO DE STATUS DE PRODUÇÃO</div>",
        unsafe_allow_html=True,
    )

# --- SETORES ---
setores_padrao = [
    "Separação",
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

tipos_separacao = [
    "PÃES-ROSCAS",
    "PANETTONES",
    "PLACA",
    "CASEIRO-INGLES",
    "CREMOSO-COM COBERTURA",
    "REDONDO-BROWNIE",
    "BISCOITOS",
]


def colorir_linhas_bolo(row):
    tipo = row.get("Tipo de Bolo", "")
    return [cores_bolos.get(tipo, "")] * len(row)


def processar_texto_colado(texto):
    linhas = texto.strip().split("\n")
    dados = []
    for linha in linhas:
        partes = [p.strip() for p in linha.split("\t") if p.strip()]
        if len(partes) >= 3:
            dados.append(
                {
                    "Status": "⏳ Pendente",
                    "Qtd": partes[0],
                    "Unidade": partes[1],
                    "Produto": partes[2],
                }
            )
        elif len(partes) == 2:
            dados.append(
                {
                    "Status": "⏳ Pendente",
                    "Qtd": partes[0],
                    "Unidade": "",
                    "Produto": partes[1],
                }
            )
        elif len(partes) == 1:
            dados.append(
                {
                    "Status": "⏳ Pendente",
                    "Qtd": "",
                    "Unidade": "",
                    "Produto": partes[0],
                }
            )
    return pd.DataFrame(dados)


def processar_texto_meta_planilha(texto):
    linhas = texto.strip().split("\n")
    dados = []
    for linha in linhas:
        partes = [p.strip() for p in linha.split("\t") if p.strip()]
        if len(partes) >= 3:
            desc = partes[0]
            item_code = partes[1]
            try:
                total_val = float(
                    partes[2].replace(".", "").replace(",", ".")
                )
            except ValueError:
                total_val = 0.0
            dados.append(
                {
                    "Item": item_code,
                    "Descrição": desc,
                    "Meta_Semanal": total_val,
                }
            )
        elif len(partes) == 2:
            desc = partes[0]
            try:
                total_val = float(
                    partes[1].replace(".", "").replace(",", ".")
                )
            except ValueError:
                total_val = 0.0
            dados.append(
                {"Item": "-", "Descrição": desc, "Meta_Semanal": total_val}
            )
    return pd.DataFrame(dados)


def calcular_total_itens(df):
    if df.empty or "Qtd" not in df.columns:
        return 0, 0
    total_itens = len(df)
    soma_qtd = 0.0
    for v in df["Qtd"]:
        try:
            soma_qtd += float(
                str(v)
                .replace(",", ".")
                .replace("kg", "")
                .replace("un", "")
                .strip()
            )
        except ValueError:
            pass
    return total_itens, soma_qtd


# --- FUNÇÃO DE GERAR IMPRESSÃO FORMATADA EM A4 ---
def exibir_botao_impressao_a4(titulo, df):
    if df.empty:
        return

    data_hora = datetime.now().strftime("%d/%m/%Y às %H:%M")

    linhas_html = ""
    for idx, row in df.iterrows():
        status = row.get("Status", "⏳ Pendente")
        qtd = row.get(
            "Qtd",
            row.get(
                "Pedido Total",
                row.get("Meta Semanal", row.get("Saldo Restante", "")),
            ),
        )
        uni = row.get("Unidade", "")
        prod = row.get("Produto", row.get("Descrição", ""))
        tipo = row.get("Tipo de Bolo", row.get("Item", ""))
        col_tipo = f"<td>{tipo}</td>" if tipo else ""

        linhas_html += f"""
        <tr>
            <td style='text-align: center;'>{idx + 1}</td>
            <td style='text-align: center;'>{status}</td>
            {col_tipo}
            <td style='text-align: center; font-weight: bold;'>{qtd} {uni}</td>
            <td style='font-weight: 500;'>{prod}</td>
            <td style='width: 30px; text-align: center;'>[ &nbsp; ]</td>
        </tr>
        """

    cabecalho_tipo = (
        "<th>Código / Tipo</th>"
        if "Tipo de Bolo" in df.columns or "Item" in df.columns
        else ""
    )

    html_a4 = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {{ size: A4 portrait; margin: 15mm; }}
            body {{ font-family: Arial, sans-serif; color: #000; margin: 0; padding: 0; background-color: #fff; }}
            .header {{ text-align: center; border-bottom: 2px solid #009944; padding-bottom: 10px; margin-bottom: 15px; }}
            .header h1 {{ margin: 0; font-size: 20px; color: #FF6600; text-transform: uppercase; }}
            .header h2 {{ margin: 5px 0 0 0; font-size: 16px; color: #009944; }}
            .info-bar {{ display: flex; justify-content: space-between; margin-bottom: 15px; font-size: 12px; border-bottom: 1px solid #ddd; padding-bottom: 5px; }}
            table {{ width: 100%; border-collapse: collapse; font-size: 13px; margin-top: 10px; }}
            th, td {{ border: 1px solid #333; padding: 6px 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; font-weight: bold; font-size: 12px; text-transform: uppercase; }}
            .footer {{ margin-top: 30px; display: flex; justify-content: space-between; font-size: 11px; }}
            .assinatura {{ border-top: 1px solid #000; width: 40%; text-align: center; padding-top: 5px; margin-top: 30px; }}
            .btn-imprimir {{
                background-color: #009944; color: white; border: none; padding: 10px 18px;
                font-size: 15px; font-weight: bold; border-radius: 5px; cursor: pointer;
                margin-bottom: 10px; display: inline-flex; align-items: center; gap: 8px;
            }}
            .btn-imprimir:hover {{ background-color: #007a36; }}
            @media print {{
                .btn-imprimir {{ display: none; }}
            }}
        </style>
    </head>
    <body>
        <button class="btn-imprimir" onclick="window.print()">🖨️ IMPRIMIR / SALVAR PDF A4</button>
        <div class="header">
            <h1>SUPERMERCADOS ALVORADA - PCP</h1>
            <h2>{titulo}</h2>
        </div>
        <div class="info-bar">
            <span><strong>Emissão:</strong> {data_hora}</span>
            <span><strong>Total de itens:</strong> {len(df)}</span>
        </div>
        <table>
            <thead>
                <tr>
                    <th style="width: 30px; text-align: center;">#</th>
                    <th style="width: 110px; text-align: center;">Status</th>
                    {cabecalho_tipo}
                    <th style="width: 90px; text-align: center;">Qtd / Total</th>
                    <th>Descrição do Produto</th>
                    <th style="width: 40px; text-align: center;">OK</th>
                </tr>
            </thead>
            <tbody>
                {linhas_html}
            </tbody>
        </table>
        <div style="margin-top: 40px; display: flex; justify-content: space-between;">
            <div class="assinatura">Visto PCP / Liderança</div>
            <div class="assinatura">Visto Produção / Operacional</div>
        </div>
    </body>
    </html>
    """

    with st.expander(
        "🖨️ Abrir Folha de Impressão A4 / Salvar PDF", expanded=False
    ):
        components.html(html_a4, height=450, scrolling=True)


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

# Recursos ADM e Backup
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

    st.sidebar.markdown("---")
    st.sidebar.header("💾 Backup e Segurança")
    json_str = json.dumps(db, ensure_ascii=False, indent=4)
    st.sidebar.download_button(
        label="📥 Baixar Backup do Banco",
        data=json_str,
        file_name=f"backup_pcp_{datetime.now().strftime('%d_%m_%Y')}.json",
        mime="application/json",
    )

    arquivo_backup = st.sidebar.file_uploader(
        "Restaurar Banco de Dados:", type=["json"]
    )
    if arquivo_backup is not None:
        if st.sidebar.button("⚠️ Confirmar Restauração"):
            dados_restaurados = json.load(arquivo_backup)
            salvar_banco(dados_restaurados)
            st.sidebar.success("Banco de Dados restaurado!")
            st.rerun()

# --- HEADER ALVORADA ---
st.markdown(
    f"<div class='header-alvorada'>"
    f"<h2>PROGRAMAÇÃO DE {setor_ativo.upper()}</h2>"
    f"<small>{semana_ativa.upper()}</small>"
    f"</div>",
    unsafe_allow_html=True,
)

# --- BUSCA RÁPIDA DE PRODUTOS ---
termo_busca = st.text_input(
    "🔍 Busca Rápida de Produto:",
    placeholder="Digite o nome do produto para procurar nesta semana...",
)
if termo_busca.strip():
    st.markdown(f"**Resultados da busca por:** *'{termo_busca}'*")
    encontrados = []
    for chave, itens in db.get("dados", {}).items():
        if chave.startswith(chave_semana):
            partes_chave = chave.split("_")
            dia_info = partes_chave[-1]
            if isinstance(itens, list):
                for it in itens:
                    if termo_busca.lower() in str(it.get("Produto", "")).lower():
                        encontrados.append(
                            {
                                "Dia/Categoria": dia_info,
                                "Status": it.get("Status", "⏳ Pendente"),
                                "Qtd": it.get("Qtd", ""),
                                "Unidade": it.get("Unidade", ""),
                                "Produto": it.get("Produto", ""),
                            }
                        )
    if encontrados:
        st.dataframe(
            pd.DataFrame(encontrados),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Nenhum produto encontrado com esse nome.")
    st.markdown("---")


# =========================================================
# LÓGICA ESPECIAL PARA O SETOR DE SEPARAÇÃO (COM CUMULATIVO POR DIA)
# =========================================================
if setor_ativo == "Separação" or "Meta" in setor_ativo:
    st.markdown("### 📦 Separação - Controle por Categoria e Saldo Cumulativo")

    abas_dias = st.tabs([item["label_aba"] for item in dias_semana_com_data])

    for idx_dia, item_dia in enumerate(dias_semana_com_data):
        dia_nome = item_dia["nome"]
        dia_data_full = item_dia["data_completa"]

        with abas_dias[idx_dia]:
            if not esolo_adm and not esta_publicado:
                st.info(
                    "⏳ A programação desta semana ainda não foi publicada pelo Administrador."
                )
                continue

            st.markdown(f"#### 📅 Programação de {dia_nome} ({dia_data_full})")

            sub_abas_cat = st.tabs(tipos_separacao)

            for idx_cat, cat_nome in enumerate(tipos_separacao):
                with sub_abas_cat[idx_cat]:
                    chave_base_cat = f"{chave_semana}_{cat_nome}"

                    if esolo_adm:
                        with st.expander(
                            f"⚙️ Importar Pedido Total de {cat_nome} (ADM)",
                            expanded=False,
                        ):
                            texto_colado = st.text_area(
                                f"Cole do Excel (Descrição | Item | Total):",
                                key=f"txt_{chave_base_cat}",
                                height=100,
                            )
                            if st.button(
                                f"💾 Cadastrar Total em {cat_nome}",
                                key=f"btn_save_meta_{chave_base_cat}",
                            ):
                                if texto_colado.strip():
                                    df_parsed = processar_texto_meta_planilha(
                                        texto_colado
                                    )
                                    if "metas_semanais" not in db:
                                        db["metas_semanais"] = {}
                                    db["metas_semanais"][chave_base_cat] = (
                                        df_parsed.to_dict("records")
                                    )
                                    salvar_banco(db)
                                    st.success(f"Meta de {cat_nome} salva!")
                                    st.rerun()

                    meta_cat = db.get("metas_semanais", {}).get(
                        chave_base_cat, []
                    )

                    if not meta_cat:
                        st.info(
                            f"Nenhum pedido inicial cadastrado para a categoria '{cat_nome}'."
                        )
                    else:
                        df_meta_cat = pd.DataFrame(meta_cat)
                        lista_painel = []

                        for _, row in df_meta_cat.iterrows():
                            cod_item = str(row["Item"])
                            desc_item = row["Descrição"]
                            pedido_total_semana = float(row["Meta_Semanal"])

                            separado_dias_anteriores = 0.0
                            for d_prev_idx in range(idx_dia):
                                dia_prev_nome = nomes_dias[d_prev_idx]
                                ch_prev = f"{chave_base_cat}_{dia_prev_nome}"
                                lançado_prev = (
                                    db.get("dados", {})
                                    .get(ch_prev, {})
                                    .get(cod_item, 0.0)
                                )
                                separado_dias_anteriores += float(lançado_prev)

                            meta_disponivel_hoje = max(
                                0.0,
                                pedido_total_semana - separado_dias_anteriores,
                            )

                            chave_hoje = f"{chave_base_cat}_{dia_nome}"
                            separado_hoje = float(
                                db.get("dados", {})
                                .get(chave_hoje, {})
                                .get(cod_item, 0.0)
                            )

                            saldo_para_amanha = max(
                                0.0, meta_disponivel_hoje - separado_hoje
                            )

                            status = (
                                "✅ Concluído"
                                if saldo_para_amanha == 0
                                else (
                                    "🔄 Em Progresso"
                                    if separado_hoje > 0
                                    else "⏳ Pendente"
                                )
                            )

                            lista_painel.append(
                                {
                                    "Status": status,
                                    "Item": cod_item,
                                    "Descrição": desc_item,
                                    "Pedido Total": pedido_total_semana,
                                    "Meta do Dia (Saldo Anterior)": meta_disponivel_hoje,
                                    f"Separado em {dia_nome}": separado_hoje,
                                    "Saldo p/ Próximo Dia": saldo_para_amanha,
                                }
                            )

                        df_painel_cat = pd.DataFrame(lista_painel)
                        col_edit_hoje = f"Separado em {dia_nome}"

                        df_editado_cat = st.data_editor(
                            df_painel_cat,
                            disabled=[
                                "Status",
                                "Item",
                                "Descrição",
                                "Pedido Total",
                                "Meta do Dia (Saldo Anterior)",
                                "Saldo p/ Próximo Dia",
                            ],
                            use_container_width=True,
                            hide_index=True,
                            key=f"editor_{chave_base_cat}_{dia_nome}",
                        )

                        if st.button(
                            f"💾 Salvar Separação - {cat_nome} ({dia_nome})",
                            key=f"btn_save_sep_{chave_base_cat}_{dia_nome}",
                        ):
                            if "dados" not in db:
                                db["dados"] = {}

                            chave_hoje = f"{chave_base_cat}_{dia_nome}"
                            novos_valores = {}
                            for _, r in df_editado_cat.iterrows():
                                novos_valores[str(r["Item"])] = float(
                                    r[col_edit_hoje]
                                )

                            db["dados"][chave_hoje] = novos_valores
                            salvar_banco(db)
                            st.success(
                                f"Separação de {cat_nome} atualizada! Saldo transferido para o próximo dia."
                            )
                            st.rerun()

                        exibir_botao_impressao_a4(
                            f"SEPARAÇÃO: {cat_nome} - {dia_nome} ({dia_data_full})",
                            df_painel_cat,
                        )

# =========================================================
# LÓGICA PADRÃO PARA OS DEMAIS SETORES
# =========================================================
else:
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
                        if isinstance(dados_salvos, list) and dados_salvos:
                            df_temp = pd.DataFrame(dados_salvos)
                            df_temp.insert(0, "Tipo de Bolo", tipo)
                            lista_geral.append(df_temp)

                    if lista_geral:
                        df_consolidado = pd.concat(lista_geral, ignore_index=True)
                        t_itens, t_soma = calcular_total_itens(df_consolidado)
                        st.success(
                            f"📊 **Totais de Confeitaria:** {t_itens} tipos cadastrados | Soma de quantidades: **{t_soma:.2f}**"
                        )

                        df_estilizado = df_consolidado.style.apply(
                            colorir_linhas_bolo, axis=1
                        )
                        st.dataframe(
                            df_estilizado, use_container_width=True, hide_index=True
                        )

                        exibir_botao_impressao_a4(
                            f"CONFEITARIA - {dia_nome} ({dia_data_full})",
                            df_consolidado,
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
                        df_atual = (
                            pd.DataFrame(dados_existentes)
                            if isinstance(dados_existentes, list)
                            else pd.DataFrame()
                        )
                        if df_atual.empty:
                            df_atual = pd.DataFrame(
                                columns=["Status", "Qtd", "Unidade", "Produto"]
                            )
                        elif "Status" not in df_atual.columns:
                            df_atual.insert(0, "Status", "⏳ Pendente")

                        t_itens, t_soma = calcular_total_itens(df_atual)
                        st.info(
                            f"📌 **{tipo}:** {t_itens} itens | Total estimado: **{t_soma:.2f}**"
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
                                    f"💾 Salvar Edição ({tipo})",
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
                            df_editado = st.data_editor(
                                df_atual,
                                num_rows="fixed",
                                use_container_width=True,
                                column_config=config_colunas,
                                key=f"editor_lider_{chave_item}",
                            )
                            if st.button(
                                f"💾 Atualizar Status ({tipo})",
                                key=f"save_lider_{chave_item}",
                            ):
                                db["dados"][chave_item] = df_editado.to_dict(
                                    "records"
                                )
                                salvar_banco(db)
                                st.success("Status atualizado!")
                                st.rerun()

            else:
                # Setores Padrão
                chave_item = f"{chave_semana}_{dia_nome}"
                dados_existentes = db["dados"].get(chave_item, [])
                df_atual = (
                    pd.DataFrame(dados_existentes)
                    if isinstance(dados_existentes, list)
                    else pd.DataFrame()
                )
                if df_atual.empty:
                    df_atual = pd.DataFrame(
                        columns=["Status", "Qtd", "Unidade", "Produto"]
                    )
                elif "Status" not in df_atual.columns:
                    df_atual.insert(0, "Status", "⏳ Pendente")

                t_itens, t_soma = calcular_total_itens(df_atual)
                st.info(
                    f"📊 **Totais do Dia:** {t_itens} itens cadastrados | Soma de quantidades: **{t_soma:.2f}**"
                )

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
                    df_editado = st.data_editor(
                        df_atual,
                        num_rows="fixed",
                        use_container_width=True,
                        column_config=config_colunas,
                        key=f"editor_lider_{chave_item}",
                    )
                    if st.button(
                        f"💾 Atualizar Status de {dia_nome}",
                        key=f"save_lider_{chave_item}",
                    ):
                        db["dados"][chave_item] = df_editado.to_dict("records")
                        salvar_banco(db)
                        st.success("Status atualizados!")
                        st.rerun()

                exibir_botao_impressao_a4(
                    f"{setor_ativo.upper()} - {dia_nome} ({dia_data_full})", df_atual
                )