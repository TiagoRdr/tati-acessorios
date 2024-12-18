import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")
# Streamlit Community: https://tati-aceapprios.streamlit.app/


# Título do Dashboard com animação, texto na cor rgb(28, 100, 34) e fundo transparente
st.markdown(
    """
    <div style="text-align: center; padding: 40px; background-color: transparent;">
        <h1 style="color: #05241f; font-weight: bold; font-size: 70px; margin: 0; 
                   text-shadow: 3px 3px 5px rgba(0,0,0,0.3); animation: fadeIn 2s ease-in;">
            TATA ACESSÓRIOS
        </h1>
        <h3 style="color: #05241f; font-weight: bold; font-size: 30px; margin: 0;
                   text-shadow: 2px 2px 4px rgba(0,0,0,0.3); animation: fadeIn 3s ease-in;">
            DASHBOARD | VENDAS E PRODUTOS
        </h3>
    </div>
    <style>
        @keyframes fadeIn {
            0% {
                opacity: 0;
                transform: translateY(-20px);
            }
            100% {
                opacity: 1;
                transform: translateY(0);
            }
        }
    </style>
    """,
    unsafe_allow_html=True
)


def load_transform_data():
    df_vendas = pd.read_csv("tati-vendas.csv", sep=',')
    df_produtos = pd.read_csv("tati-produtos.csv", sep=',')
    df_fornecedores = pd.read_csv("tati-fornecedores.csv", sep=',')


    df_vendas['valor da venda'] = format_monetary_float(df_vendas, 'valor da venda')
    df_produtos['valor da peça'] = format_monetary_float(df_produtos, 'valor da peça')
    df_produtos['valor vender'] = format_monetary_float(df_produtos, 'valor vender')

    df_vendas['Dia'] = (df_vendas['Dia'] + "/2024")

    df_vendas_produtos_forn = df_vendas.merge(df_produtos, on='id da peça', how='left') \
    .merge(df_fornecedores, on='id do fornecedor', how='left')
    
    df_vendas_produtos_forn['Lucro da Venda'] = df_vendas_produtos_forn['valor da venda'] - df_vendas_produtos_forn['valor da peça']

    return df_vendas_produtos_forn


def format_monetary_float(df : pd.DataFrame, column : str):
    return df[column].str.replace(",", ".").str.replace("R$", "").astype(float)

def format_monetary(column : str):
    return f"{column:,.2f}".replace(".", ",")


#Barra lateral de filtros
def filter_sidebar(df_vendas):
    st.sidebar.image("logo.jpg", use_container_width=True)


    # Título dos filtros
    st.sidebar.markdown(
        """
        <hr style="border: 1px solid #ccc;">
        <h1 style="text-align: center; color: #05241f;">Filtros</h1>
        <p style="text-align: center; font-size: 14px; color: #05241f;">
            Ajuste os filtros abaixo para refinar os dados exibidos.
        </p>
        """,
        unsafe_allow_html=True
    )

    df_vendas["Dia"] = pd.to_datetime(df_vendas["Dia"], format="%d/%m/%Y")
    data_min, data_max = df_vendas["Dia"].min(), df_vendas["Dia"].max()

    # Filtro de data
    st.sidebar.subheader("Período de Vendas")
    data_inicial = st.sidebar.date_input("Data Inicial", value=data_min, min_value=data_min, max_value=data_max, key="data_inicial")
    data_final = st.sidebar.date_input("Data Final", value=data_max, min_value=data_min, max_value=data_max, key="data_final")

    st.sidebar.subheader("Produtos")
    options_produtos = st.sidebar.multiselect(
        "Selecione um ou mais produtos:",
        options=sorted(df_vendas['descrição da peça'].unique()),
        placeholder="Escolha os produtos"
    )

    # Aplicação dos filtros no DataFrame
    df_filtered = df_vendas[
        (df_vendas["Dia"] >= pd.to_datetime(data_inicial)) &
        (df_vendas["Dia"] <= pd.to_datetime(data_final))
    ]

    if options_produtos:
        df_filtered = df_filtered[df_filtered["descrição da peça"].isin(options_produtos)]

    # Retorno do DataFrame filtrado
    return df_filtered




def card_show(df_filtered):
    # Calculando os totais
    total_vendas_periodo = format_monetary(df_filtered["valor da venda"].sum())
    total_lucro_periodo = format_monetary(df_filtered["Lucro da Venda"].sum())
    ticket_medio = format_monetary(df_filtered["valor da venda"].mean())

    # Template para os Cards com animação
    card_template = """
    <div
    style="
        background-color: #05241f; 
        border-radius: 10px; 
        border: 1px solid white; 
        padding: 20px; 
        text-align: center; 
        width: 100%; 
        max-width: 470px; 
        margin-top: 20px; 
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); 
        animation: fadeIn 2s ease-in;">
        <h1 style="color: {color}; font-size: 2.8em; margin: 0; padding-bottom: 10px;">R$ {value}</h1>
        <p style="font-size: 1.5em; margin: 0; color: #E0E0E0;">{label}</p>
    </div>
    """

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(card_template.format(color="#FFFFFF", value=total_vendas_periodo, label="Total de Vendas"), unsafe_allow_html=True)
    with col2:
        st.markdown(card_template.format(color="#FFFFFF", value=total_lucro_periodo, label="Total de Lucro"), unsafe_allow_html=True)
    with col3:
        st.markdown(card_template.format(color="#FFFFFF", value=ticket_medio, label="Ticket Médio"), unsafe_allow_html=True)

    # Adicionando a animação CSS
    st.markdown(
        """
        <style>
        @keyframes fadeIn {
            0% {
                opacity: 0;
                transform: translateY(-30px);
            }
            100% {
                opacity: 1;
                transform: translateY(0);
            }
        }
        </style>
        """,
        unsafe_allow_html=True
    )


#Função do gráfico de Faturamento utilizando Plotly
def charts_revenue(df_filtered):
    # Título do gráfico
    st.subheader("1. Faturamento Diário de Dezembro/2024")

    df_filtered["Dia"] = pd.to_datetime(df_filtered["Dia"])
    df_filtered["dia"] = df_filtered["Dia"].dt.to_period("d").astype(str)
    resumo_mensal = df_filtered.groupby("dia")[["valor da venda", "Lucro da Venda"]].sum().reset_index()

    # Criando o gráfico para o total de vendas e linha para o lucro
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=resumo_mensal["dia"],
        y=resumo_mensal["valor da venda"],
        name="Total de Vendas",
        marker_color="DodgerBlue",  # Cor mais agradável
        text=resumo_mensal["valor da venda"].apply(lambda x: f"R$ {x:,.2f}"),  # Formato de texto mais amigável
        texttemplate='%{text}', 
        textposition="outside"
    ))

    fig.add_trace(go.Scatter(
        x=resumo_mensal["dia"],
        y=resumo_mensal["Lucro da Venda"],
        name="Lucro Total",
        mode="lines+markers",
        line=dict(color="green", width=2),
        marker=dict(size=8, color='green')
    ))

    fig.update_layout(
        xaxis_title="Dia",
        yaxis_title="Valor (R$)",
        barmode="group",
        template="plotly_white",
        legend_title="Indicadores",
        xaxis=dict(tickangle=-45),
        margin=dict(l=40, r=40, t=30, b=10),
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)



def charts_type_sales(df_filtered):
    col1, col2 = st.columns(2)

    with col1:
        # Gráfico de Faturamento por Tipo de Produto
        st.subheader("2.1 Faturamento Por Fornecedor")
        total_venda_por_tipo = df_filtered.groupby('nome do fornecedor')['valor da venda'].sum().reset_index()

        fig = go.Figure()
        # Use `hole` to create a donut-like pie chart
        fig = go.Figure(data=[go.Pie(labels=total_venda_por_tipo['nome do fornecedor'], values=total_venda_por_tipo['valor da venda'], hole=.4, marker=dict(colors=['#FF9933', '#CC0066']))])
        # Ajustando a altura do gráfico para diminuir o tamanho
        fig.update_layout(
            height=380,
            width=300# Ajuste o valor para o tamanho desejado
        )
        st.plotly_chart(fig, use_container_width=False)

    with col2:
        # Título do gráfico
        st.subheader("2.2. Faturamento Diário por Fornecedor - Dezembro/2024")

        # Conversão da coluna "Dia" para datetime e extração do dia como string
        df_filtered["Dia"] = pd.to_datetime(df_filtered["Dia"])
        df_filtered["dia"] = df_filtered["Dia"].dt.to_period("d").astype(str)

        # Agrupamento dos dados por dia e fornecedor
        faturamento_diario = df_filtered.groupby(["dia", "nome do fornecedor"])["valor da venda"].sum().reset_index()

        # Definindo as cores a serem alternadas entre as barras
        cores = ['#FF9933', '#CC0066']  # Duas cores definidas

        # Criando o gráfico de barras empilhadas
        fig = go.Figure()

        # Adicionando uma barra para cada fornecedor
        for idx, fornecedor in enumerate(faturamento_diario["nome do fornecedor"].unique()):
            dados_fornecedor = faturamento_diario[faturamento_diario["nome do fornecedor"] == fornecedor]
            fig.add_trace(go.Bar(
                x=dados_fornecedor["dia"],
                y=dados_fornecedor["valor da venda"],
                name=fornecedor,
                text=dados_fornecedor["valor da venda"].apply(lambda x: f"R$ {x:,.2f}"),
                texttemplate='%{text}',
                textposition="inside",
                marker=dict(color=cores[idx % len(cores)])  # Alterna as cores entre os fornecedores
            ))

        # Ajustando o layout do gráfico
        fig.update_layout(
            xaxis_title="Dia",
            yaxis_title="Valor Vendido (R$)",
            barmode="stack",  # Barras empilhadas para cada fornecedor
            template="plotly_white",
            legend_title="Fornecedores",
            xaxis=dict(tickangle=-45),
            margin=dict(l=40, r=40, t=30, b=10),
            height=500,
            width=900
        )

        st.plotly_chart(fig, use_container_width=False)


#Exibição dos dados brutos
def full_data(df_filtered):
    if st.checkbox('Mostrar Dados Brutos'):
        st.subheader('Dados Brutos')
        st.write(df_filtered)

def chat_produtos(df_filtered):
    # Título do gráfico
    st.subheader("3. Faturamento e Lucro por Produto - Dezembro/2024")

    # Agrupando por produto para somar vendas e lucro
    produtos_agrupados = df_filtered.groupby('descrição da peça').agg({
        'valor da venda': 'sum',
        'Lucro da Venda': 'sum'
    }).reset_index()

    # Ordenando por valor total de vendas
    produtos_agrupados = produtos_agrupados.sort_values(by="valor da venda", ascending=False)

    # Criando o gráfico de barras empilhadas
    fig = go.Figure()

    # Barra para o total de vendas
    fig.add_trace(go.Bar(
        x=produtos_agrupados["descrição da peça"],
        y=produtos_agrupados["valor da venda"],
        name="Total Vendido",
        marker_color="DodgerBlue",  # Cor azul para vendas
        text=produtos_agrupados["valor da venda"].apply(lambda x: f"R$ {x:,.2f}"),  # Formato amigável
        texttemplate='%{text}', 
        textposition="inside"
    ))

    # Barra para o lucro total
    fig.add_trace(go.Bar(
        x=produtos_agrupados["descrição da peça"],
        y=produtos_agrupados["Lucro da Venda"],
        name="Lucro Total",
        marker_color="green",  # Cor verde para lucro
        text=produtos_agrupados["Lucro da Venda"].apply(lambda x: f"R$ {x:,.2f}"),  # Formato amigável
        texttemplate='%{text}', 
        textposition="inside"
    ))

    # Ajustando layout
    fig.update_layout(
        xaxis_title="Produtos",
        yaxis_title="Valor (R$)",
        barmode="stack",  # Barras empilhadas
        template="plotly_white",
        legend_title="Indicadores",
        xaxis=dict(tickangle=-45),
        margin=dict(l=40, r=40, t=30, b=10),
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)


def grafico_pago_a_receber_com_tabela(df_filtered):
    # Título do gráfico
    st.subheader("Faturamento Pago x A Receber | Clientes com Pagamento Pendente")

    # Tratamento da coluna "Pago"
    df_filtered['Pago'] = df_filtered['Pago'].map({'Sim': 'Pago', 'Não': 'A Receber', 'Nao': 'A Receber'})

    # Agrupar os dados de acordo com a coluna 'Pago' (Sim ou Não)
    faturamento_pago = df_filtered.groupby('Pago')['valor da venda'].sum().reset_index()

    # Criando o gráfico de pizza
    fig = go.Figure(data=[go.Pie(
        labels=faturamento_pago['Pago'],
        values=faturamento_pago['valor da venda'],
        name="Status de Pagamento",
        marker=dict(colors=['#28A745', '#FF5733']),  # Cor para 'Pago' e 'A Receber'
        textinfo='label+percent',  # Mostrar porcentagem ao lado do rótulo
        pull=[0.1, 0],  # Dar um destaque visual ao valor 'Pago'
    )])

    # Ajustando o layout do gráfico
    fig.update_layout(
        template="plotly_white",
        legend_title="Status",
        height=400
    )

    # Exibindo o gráfico
    col1, col2 = st.columns([3, 2])  # Definindo duas colunas, a primeira com mais largura

    with col1:
        st.plotly_chart(fig, use_container_width=True)

    with col2:

        # Filtrando os clientes que ainda não pagaram
        df_nao_pago = df_filtered[df_filtered["Pago"] == "A Receber"][["id venda", "Dia", "Nome do cliente", "valor da venda"]]

        # Convertendo a data para o formato dd/mm/yyyy
        df_nao_pago["Dia"] = pd.to_datetime(df_nao_pago["Dia"]).dt.strftime('%d/%m/%Y')

        # Formatando o valor da venda com vírgula e 2 casas decimais
        df_nao_pago["valor da venda"] = df_nao_pago["valor da venda"].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

        # Renomeando as colunas para exibir de forma mais amigável
        df_nao_pago = df_nao_pago.rename(columns={"Dia": "Data da Venda", "Nome do cliente": "Cliente", "valor da venda": "Valor da Venda"})

        # Exibindo a tabela com clientes que não pagaram
        st.dataframe(df_nao_pago.drop(columns=["id venda"]), use_container_width=True)


if __name__ == '__main__':
    df_vendas = load_transform_data()
    df_vendas.to_csv("df_vendas.csv")
    df_filtered = filter_sidebar(df_vendas)
    card_show(df_filtered)
    charts_revenue(df_filtered)
    charts_type_sales(df_filtered)
    full_data(df_filtered)
    chat_produtos(df_filtered)
    grafico_pago_a_receber_com_tabela(df_filtered)
