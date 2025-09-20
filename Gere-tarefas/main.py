import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3

# --- Funções de Banco de Dados ---
# Conexão com o banco de dados
def conectar_bd():
    conn = sqlite3.connect("tarefas.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tarefas(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarefa TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn

# Carregar as tarefas do banco de dados
def carregar_tarefas():
    conn = conectar_bd()
    df = pd.read_sql("SELECT * FROM tarefas", conn)
    conn.close()
    return df

# Adicionar nova tarefa
def adicionar_tarefa():
    tarefa = st.session_state.get("entrada_tarefa", "").strip()
    if not tarefa:
        st.error("A tarefa não pode estar vazia!")
        return

    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tarefas (tarefa, status) VALUES (?, ?)", (tarefa, "Pendente"))
    conn.commit()
    conn.close()
    st.session_state["entrada_tarefa"] = ""

# Atualizar status das tarefas
def atualizar_status(tarefa_id, novo_status):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("UPDATE tarefas SET status = ? WHERE id = ?", (novo_status, tarefa_id))
    conn.commit()
    conn.close()

# Deletar tarefas
def deletar_tarefa(tarefa_id):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tarefas WHERE id = ?", (tarefa_id,))
    conn.commit()
    conn.close()


# --- Layout do Aplicativo ---
st.set_page_config(
    page_title="App de Tarefas",
    layout="wide",
)

st.title("Gerenciador de Tarefas")
st.text_input("Adicione uma nova tarefa:", key="entrada_tarefa", on_change=adicionar_tarefa)

# Carregar tarefas
lista_tarefas = carregar_tarefas()

# Container principal
with st.container():
    col_esq, col_dir = st.columns(2)

    with col_esq:
        if not lista_tarefas.empty:
            st.header("Lista de Tarefas")
            for index, row in lista_tarefas.iterrows():
                tarefa_concluida = row["status"] == "Concluída"
                
                col1, col2 = st.columns([1, 10])

                with col1:
                    checkbox_state = st.checkbox("", key=f"checkbox_{row['id']}", value=tarefa_concluida)
                
                with col2:
                    if checkbox_state:
                        st.markdown(f"~~{row['tarefa']}~~")
                    else:
                        st.markdown(f"{row['tarefa']}")
                
                # Atualiza o status quando o checkbox muda
                novo_status = "Concluída" if checkbox_state else "Pendente"
                if novo_status != row["status"]:
                    atualizar_status(row["id"], novo_status)
                
                # Botão de deletar
                if st.button("🗑️", key=f"delete_{row['id']}"):
                    deletar_tarefa(row['id'])
                    st.experimental_rerun() # Precisa de rerun para refletir a exclusão

    with col_dir:
        if not lista_tarefas.empty:
            dados_progresso = lista_tarefas['status'].value_counts().reset_index()
            dados_progresso.columns = ['Status', 'Quantidade']
            
            cores_personalizadas = {
                "Pendente": "#fbbf24",
                "Concluída": "#10b981"
            }
            
            fig = px.pie(
                dados_progresso,
                names="Status",
                values="Quantidade",
                title="📊 Progresso das Tarefas",
                color="Status",
                color_discrete_map=cores_personalizadas,
                hole=0.4,
            )

            fig.update_traces(
                textposition="inside",
                textinfo="percent+label",
                marker=dict(line=dict(color='#ffffff', width=2)),
                pull=[0.05 if s == "Pendente" else 0 for s in dados_progresso["Status"]],
            )

            fig.update_layout(
                title_font_size=22,
                font=dict(family="Segoe UI, sans-serif", size=16),
                paper_bgcolor="#f9fafb",
                plot_bgcolor="#f9fafb",
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=14)
                )
            )

            st.plotly_chart(fig, use_container_width=True)