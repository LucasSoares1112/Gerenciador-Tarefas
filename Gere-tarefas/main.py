import streamlit as st
import pandas as pd

# Inicializa a lista de tarefas na sessão
if "tarefas" not in st.session_state:
    st.session_state.tarefas = []

# Adicionar nova tarefa à lista da sessão
def adicionar_tarefa_simples():
    tarefa = st.session_state.get("entrada_tarefa", "").strip()
    if not tarefa:
        return
    
    novo_id = len(st.session_state.tarefas) + 1
    nova_tarefa = {"id": novo_id, "tarefa": tarefa}
    st.session_state.tarefas.append(nova_tarefa)

    st.session_state["entrada_tarefa"] = ""

# ---
# Configuração da página e interface
st.title("Gerenciador de Tarefas Simples")
st.text_input("Adicione uma nova tarefa:", key="entrada_tarefa")
st.button("Adicionar", on_click=adicionar_tarefa_simples)

# Mostra as tarefas em uma lista simples
st.header("Minhas Tarefas:")
if st.session_state.tarefas:
    for tarefa in st.session_state.tarefas:
        st.write(f"- {tarefa['tarefa']}")