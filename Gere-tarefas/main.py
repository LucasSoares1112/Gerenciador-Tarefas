import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

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
    st.rerun()

# Atualizar status das tarefas
def atualizar_status(tarefa_id, novo_status):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("UPDATE tarefas SET status = ? WHERE id = ?", (novo_status, tarefa_id))
    conn.commit()
    conn.close()
    st.rerun()

# Deletar tarefas
def deletar_tarefa(tarefa_id):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tarefas WHERE id = ?", (tarefa_id,))
    conn.commit()
    conn.close()
    st.rerun()


# --- Layout do Aplicativo ---
st.set_page_config(
    page_title="App de Tarefas",
    layout="wide",
)

st.title("Gerenciador de Tarefas")
st.text_input("Adicione uma nova tarefa:", key="entrada_tarefa")
st.button("Adicionar", on_click=adicionar_tarefa)

# Carregar tarefas
lista_tarefas = carregar_tarefas()

# Container principal
with st.container():
    col_esq, col_dir = st.columns(2)

    with col_esq:
        if not lista_tarefas.empty:
            for index, row in lista_tarefas.iterrows():
                c1, c2, c3 = st.columns([5, 2, 1])
                with c1:
                    # NOVA ESTILIZAÇÃO SIMPLIFICADA
                    st.markdown(f"""
                        <div style="background: #f8fafc; padding: 1rem; border-left: 4px solid #3b82f6; border-radius: 8px;">
                            {row["tarefa"]}
                        </div>
                    """, unsafe_allow_html=True)
                
                opcoes_status = ["Pendente", "Concluída"]
                status_atual = row["status"]

                with c2:
                    novo_status = st.selectbox(
                        "Status",
                        opcoes_status,
                        index=opcoes_status.index(status_atual),
                        key=f"status_{row['id']}"
                    )
                
                if novo_status != status_atual:
                    atualizar_status(row["id"], novo_status)

                with c3:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🗑️", key=f"delete_{row['id']}"):
                        deletar_tarefa(row['id'])
    
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