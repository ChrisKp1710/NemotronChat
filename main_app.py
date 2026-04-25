# main_app.py

import streamlit as st
from config import FREE_MODELS, CHAT_PRESETS
from api_engine import get_chat_response_stream

# 1. CONFIGURAZIONE PAGINA
st.set_page_config(page_title="MindMatrix Chat", page_icon="🧠", layout="wide")
st.title("🧠 MindMatrix: Multi-Model Streaming")

# Inizializzazione session_state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "current_model" not in st.session_state:
    st.session_state.current_model = list(FREE_MODELS.keys())[0]

# 2. SIDEBAR
with st.sidebar:
    st.title("⚙️ Setup Chat")
    api_key = st.text_input("OpenRouter API Key", type="password")
    st.divider()
    
    selected_model_name = st.selectbox("🤖 Scegli il Modello Free", list(FREE_MODELS.keys()))
    model_id = FREE_MODELS[selected_model_name] 
    
    if selected_model_name != st.session_state.current_model:
        st.session_state.current_model = selected_model_name
        st.toast(f"✅ Modello aggiornato: {selected_model_name}", icon="🔄")
    
    preset_name = st.selectbox("🎭 Scegli un Ruolo", list(CHAT_PRESETS.keys()))
    system_input = st.text_area("Istruzioni di Sistema (Modificabili)", value=CHAT_PRESETS[preset_name], height=150)
    
    st.divider()
    if st.button("🗑️ Nuova Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 3. SICUREZZA
if not api_key:
    st.warning("⚠️ Inserisci la tua API Key nella barra laterale per iniziare.")
    st.stop()

# 4. RENDERING CRONOLOGIA
for msg in st.session_state.messages:
    if msg["role"] != "system": 
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("reasoning_details"):
                with st.expander("💭 Dettagli Ragionamento"):
                    # Se è una lista/dizionario lo mostriamo come JSON, altrimenti testo
                    if isinstance(msg["reasoning_details"], (list, dict)):
                        st.json(msg["reasoning_details"])
                    else:
                        st.write(msg["reasoning_details"])

# 5. LOGICA DI CHAT (STREAMING)
if prompt := st.chat_input("Scrivi qui il tuo messaggio..."):
    
    # Gestione dinamica del System Prompt: lo aggiorniamo/inseriamo sempre come primo messaggio
    new_system_msg = {"role": "system", "content": system_input}
    if not st.session_state.messages:
        if system_input.strip():
            st.session_state.messages.append(new_system_msg)
    elif st.session_state.messages[0]["role"] == "system":
        st.session_state.messages[0] = new_system_msg # Aggiorna il ruolo esistente

    # Aggiunta messaggio utente
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Risposta Assistente in Streaming
    with st.chat_message("assistant"):
        # Contenitori per l'output progressivo
        reasoning_placeholder = st.empty()
        content_placeholder = st.empty()
        
        full_content = ""
        full_reasoning = ""
        
        try:
            # Avvio streaming
            with st.spinner(f"In ascolto da {selected_model_name}..."):
                stream_gen = get_chat_response_stream(api_key, model_id, st.session_state.messages)
                
                for chunk in stream_gen:
                    # Gestione Ragionamento
                    if chunk["reasoning"]:
                        # Se è il primo pezzo di ragionamento, inizializziamo l'expander visivo
                        full_reasoning += str(chunk["reasoning"])
                        with reasoning_placeholder.expander("💭 Sto ragionando...", expanded=True):
                            st.write(full_reasoning)
                    
                    # Gestione Contenuto
                    if chunk["content"]:
                        full_content += chunk["content"]
                        content_placeholder.markdown(full_content + "▌")
                
                # Pulizia finale del cursore
                content_placeholder.markdown(full_content)
                
                # Se il ragionamento è finito, chiudiamo l'expander (opzionale: lo lasciamo visibile)
                if full_reasoning:
                    with reasoning_placeholder.expander("💭 Ragionamento Completato"):
                        st.write(full_reasoning)

            # Salvataggio finale in memoria
            st.session_state.messages.append({
                "role": "assistant", 
                "content": full_content, 
                "reasoning_details": full_reasoning
            })

        except Exception as e:
            error_msg = str(e)
            if "429" in error_msg:
                st.error("🚦 Traffico Intenso! Prova a cambiare modello.")
            else:
                st.error(f"❌ Errore: {error_msg}")