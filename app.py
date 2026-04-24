import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Nemotron CoT Chat", page_icon="🧠")
st.title("🧠 Nemotron Reasoning Chat")

# --- CONFIGURAZIONE CLIENT ---
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# Sidebar per inserire la chiave se non vuoi scriverla nel codice
with st.sidebar:
    st.session_state.api_key = st.text_input("OpenRouter API Key", type="password")

if not st.session_state.api_key:
    st.warning("Per favore, inserisci la tua API Key nella sidebar.")
    st.stop()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.session_state.api_key,
)

# --- INIZIALIZZAZIONE MESSAGGI ---
# Nota: salviamo esattamente la struttura richiesta dal template
if "messages" not in st.session_state:
    st.session_state.messages = []

# Visualizzazione Chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        # Se il messaggio ha dettagli di ragionamento, mostriamoli
        if "reasoning_details" in msg and msg["reasoning_details"]:
            with st.expander("Dettagli ragionamento precedente"):
                st.code(msg["reasoning_details"])

# --- LOGICA CHAT ---
if prompt := st.chat_input("Chiedimi qualcosa (es. Quante 'r' ci sono in strawberry?)"):
    
    # Aggiungiamo il messaggio dell'utente
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            # Chiamata API identica al template che hai postato
            response = client.chat.completions.create(
                model="nvidia/nemotron-3-super-120b-a12b:free",
                messages=st.session_state.messages,
                extra_body={"reasoning": {"enabled": True}} # Attiva il ragionamento
            )

            # Estraiamo il messaggio e il ragionamento come nel template
            obj_msg = response.choices[0].message
            content = obj_msg.content
            # Il campo segreto che permette la continuità:
            reasoning_details = getattr(obj_msg, "reasoning_details", None)

            st.markdown(content)
            
            if reasoning_details:
                with st.expander("Ragionamento corrente"):
                    st.write(reasoning_details)

            # Salviamo il messaggio nel formato richiesto per la prossima chiamata
            # Includendo reasoning_details, la prossima volta il modello continuerà da qui
            st.session_state.messages.append({
                "role": "assistant",
                "content": content,
                "reasoning_details": reasoning_details
            })