import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# --- Funções de Banco de Dados ---
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

def carregar_tarefas():
    conn = conectar_bd()
    df = pd.read_sql("SELECT * FROM tarefas", conn)
    conn.close()
    return df

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

def atualizar_status(tarefa_id, novo_status):
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("UPDATE tarefas SET status = ? WHERE id = ?", (novo_status, tarefa_id))
    conn.commit()
    conn.close()
    st.rerun()

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

# Campo de entrada de tarefa com botão Add separado
col_input, col_btn = st.columns([8, 1])
with col_input:
    st.text_input("Adicione uma nova tarefa:", key="entrada_tarefa", label_visibility="collapsed")
with col_btn:
    st.markdown("<br>", unsafe_allow_html=True)
    st.button("Adicionar", on_click=adicionar_tarefa, use_container_width=True)


# Carregar tarefas
lista_tarefas = carregar_tarefas()

# Container principal para as colunas de tarefas e gráfico
with st.container():
    col_esq, col_dir = st.columns(2)

    with col_esq:
        if not lista_tarefas.empty:
            for index, row in lista_tarefas.iterrows():
                tarefa_concluida = row["status"] == "Concluída"

                # Layout de três colunas para cada tarefa: checkbox, texto e lixeira
                col_chk, col_txt, col_lix = st.columns([0.8, 5, 1])
                
                with col_chk:
                    # Alinha o checkbox
                    st.markdown("<br>", unsafe_allow_html=True)
                    checkbox_state = st.checkbox("", key=f"checkbox_{row['id']}", value=tarefa_concluida, label_visibility="collapsed")
                
                with col_txt:
                    # Restaura a estilização de caixa para a tarefa
                    tarefa_texto = f"~~{row['tarefa']}~~" if checkbox_state else row['tarefa']
                    st.markdown(f"""
                        <div style = "padding: 1rem; margin: 0.5rem 0; background: #f8fafc; border-radius: 8px;
                        border-left: 4px solid #3b82f6; box-shadow: 2px 2px 6px rgba(0,0,0,0.05); color: black;">
                            {tarefa_texto}
                        </div>
                    """, unsafe_allow_html=True)

                with col_lix:
                    # Alinha o botão de lixeira
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🗑️", key=f"delete_{row['id']}", help="Excluir Tarefa"):
                        deletar_tarefa(row['id'])
                
                # A lógica de atualização do status permanece, mas sem o selectbox
                novo_status = "Concluída" if checkbox_state else "Pendente"
                if novo_status != row["status"]:
                    atualizar_status(row["id"], novo_status)
    
    with col_dir:
        if not lista_tarefas.empty:
            dados_progresso = lista_tarefas['status'].value_counts().reset_index()
            dados_progresso.columns = ['Status', 'Quantidade']
            
            cores_personalizadas = {
                "Pendente": "#fbbf24", # Amarelo
                "Concluída": "#10b981" # Verde
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
                title_font_color="white",
                font=dict(family="Segoe UI, sans-serif", size=16, color="white"),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.2,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=14, color="white")
                )
            )

            st.plotly_chart(fig, use_container_width=True)