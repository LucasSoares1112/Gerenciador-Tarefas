import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

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

#Atualizar status das tarefas
def atualizar_status(tarefa_id, status):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("UPDATE tarefas SET status = ? WHERE id = ?", (status, tarefa_id))
    conn.commit()
    conn.close()
    st.rerun()


#deletar tarefas
def deletar_tarefa(tarefa_id):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tarefas WHERE id = ?", (tarefa_id,)) # A vírgula é importante!
    conn.commit()
    conn.close()
    st.rerun()




# Configuração da página
st.set_page_config(
    page_title="App de Tarefas",
    layout="wide",
)

st.title("Gerenciador de Tarefas")
st.text_input("Adicione uma nova tarefa:", key="entrada_tarefa" )
st.button("Adicionar", on_click= adicionar_tarefa)

#Carrefar tarefas
lista_tarefas = carregar_tarefas()

#  Container principal
with st.container():
    col_esq, col_dir = st.columns(2)

    with col_esq:
        if not lista_tarefas.empty:
            for index, row in lista_tarefas.iterrows():
                c1, c2, c3 = st.columns([5, 2, 1])
                with c1:
                    st.markdown(f"""
                        <div style = "padding: 1rem; margin: 1rem 0; background: #f8fafc; border-radius: 8px;
                        border-left: 4px solid #3b82f6; box-shadow: 2px 2px 6px rgba(0,0,0,0.05) ">
                            {row["tarefa"]}
                        <\div>        
                    """, unsafe_allow_html=True)
                opcoes_status = ["Pendente", "Concluida"]
                status_atual = row["status"]

                novo_status = c2.selectbox(
                    "Status",
                    opcoes_status,
                    index=opcoes_status.index(status_atual),
                    key=f"status_{row["id"]}"
                )

                if novo_status != status_atual:
                    atualizar_status(row["id", novo_status])

                if c3.button("🗑️", key=f"delete_{row["id"]}"):
                    deletar_tarefas(row["id"]) 


    with col_dir:
        if not lista_tarefas.empty:
            dados_progresso = lista_tarefas['status'].value_counts().reset_index()
            dados_progresso.columns = ['Status', 'Quantidade']

            cores_personalizadas = {
                "Pendente": "#fbbf24",
                "Concluída": "#10b981"
            }
            cores = [cores_personalizadas.get(status, "#60a5fa") for status in dados_progresso] 