# main_app.py

import streamlit as st
import json
import os
from datetime import datetime
from config import FREE_MODELS, CHAT_PRESETS
from api_engine import get_chat_response_stream

# --- 📁 GESTIONE PERSISTENZA E EXPORT ---
HISTORY_FILE = "chat_history.json"

def save_chat(messages):
    """Salva la cronologia in un file JSON."""
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(messages, f, indent=4, ensure_ascii=False)
    except Exception as e:
        st.error(f"Errore nel salvataggio: {e}")

def load_chat():
    """Carica la cronologia dal file JSON se esiste."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def export_chat_markdown(messages, model_name):
    """Genera una stringa Markdown professionale dalla cronologia."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    md_output = f"# 🧠 MindMatrix Chat Session\n"
    md_output += f"**Modello:** {model_name}  \n"
    md_output += f"**Data Esportazione:** {timestamp}\n\n"
    md_output += "---\n\n"
    
    for msg in messages:
        role = msg["role"]
        if role == "system":
            md_output += f"### 🎭 Ruolo di Sistema\n> {msg['content']}\n\n---\n\n"
        elif role == "user":
            md_output += f"### 👤 Utente\n{msg['content']}\n\n"
        elif role == "assistant":
            md_output += f"### 🤖 Assistente\n{msg['content']}\n\n"
            if msg.get("reasoning_details"):
                md_output += f"#### 💭 Processo di Ragionamento\n```text\n{msg['reasoning_details']}\n```\n\n"
            md_output += "---\n\n"
    return md_output

# 1. CONFIGURAZIONE PAGINA
st.set_page_config(page_title="MindMatrix Chat", page_icon="🧠", layout="wide")

# --- 🎨 CUSTOM CSS PER IL RAGIONAMENTO ---
st.markdown("""
    <style>
    .reasoning-box {
        background-color: #161b22;
        border-left: 4px solid #58a6ff;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        font-family: 'Source Code Pro', monospace;
        font-size: 0.85em;
        color: #8b949e;
        line-height: 1.5;
        max-height: 350px;
        overflow-y: auto;
        white-space: pre-wrap;
    }
    .reasoning-title {
        color: #58a6ff;
        font-weight: bold;
        margin-bottom: 5px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🧠 MindMatrix: Multi-Model Streaming")

# Inizializzazione session_state (Caricamento automatico)
if "messages" not in st.session_state:
    st.session_state.messages = load_chat()

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
    
    # --- 🎛️ PARAMETRI AVANZATI ---
    with st.expander("🛠️ Parametri Avanzati"):
        temp = st.slider("Temperatura (Creatività)", 0.0, 2.0, 0.7, 0.1)
        max_t = st.slider("Max Tokens (Lunghezza)", 100, 8000, 2000, 100)
        mem_window = st.slider("Memoria Chat (Messaggi)", 1, 30, 10, 1)
    
    st.divider()
    if st.button("🗑️ Nuova Chat", use_container_width=True):
        st.session_state.messages = []
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        st.rerun()
    
    # --- 📤 ESPORTAZIONE (Corretto Posizionamento) ---
    if st.session_state.messages:
        chat_md = export_chat_markdown(st.session_state.messages, selected_model_name)
        st.download_button(
            label="📥 Esporta Chat (Markdown)",
            data=chat_md,
            file_name=f"MindMatrix_Export_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.md",
            mime="text/markdown",
            use_container_width=True
        )

# 3. SICUREZZA
if not api_key:
    st.warning("⚠️ Inserisci la tua API Key nella barra laterale per iniziare.")
    st.stop()

# 4. FUNZIONE HELPER PER IL RENDERING DEL RAGIONAMENTO
def display_reasoning(text, is_streaming=False):
    title = "💭 Sto ragionando..." if is_streaming else "🧠 Pensiero del Modello"
    st.markdown(f'<div class="reasoning-box"><div class="reasoning-title">{title}</div>{text}</div>', unsafe_allow_html=True)

# 5. RENDERING CRONOLOGIA
for msg in st.session_state.messages:
    if msg["role"] != "system": 
        with st.chat_message(msg["role"]):
            if msg.get("reasoning_details"):
                with st.expander("🔍 Visualizza Processo Logico"):
                    display_reasoning(msg["reasoning_details"])
            st.markdown(msg["content"])

# 6. LOGICA DI CHAT (STREAMING)
if prompt := st.chat_input("Scrivi qui il tuo messaggio..."):
    
    new_system_msg = {"role": "system", "content": system_input}
    if not st.session_state.messages:
        if system_input.strip():
            st.session_state.messages.append(new_system_msg)
    elif st.session_state.messages[0]["role"] == "system":
        st.session_state.messages[0] = new_system_msg

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        reasoning_placeholder = st.empty()
        content_placeholder = st.empty()
        
        full_content = ""
        full_reasoning = ""
        
        # --- ✂️ GESTIONE CONTESTO (MEMORY WINDOW) ---
        chat_history = [m for m in st.session_state.messages if m["role"] != "system"]
        pruned_history = chat_history[-mem_window:]
        system_msg = [m for m in st.session_state.messages if m["role"] == "system"]
        messages_to_send = system_msg + pruned_history
        
        # --- 🛡️ SANIFICAZIONE PAYLOAD API ---
        # OpenRouter non accetta campi extra come 'reasoning_details'. 
        # Inviamo solo role e content.
        api_messages = [{"role": m["role"], "content": m["content"]} for m in messages_to_send]
        # ------------------------------------
        
        try:
            with st.spinner(f"In ascolto da {selected_model_name}..."):
                stream_gen = get_chat_response_stream(
                    api_key, 
                    model_id, 
                    api_messages, # Inviato il payload pulito
                    temperature=temp,
                    max_tokens=max_t
                )
                
                for chunk in stream_gen:
                    if chunk["reasoning"]:
                        full_reasoning += str(chunk["reasoning"])
                        with reasoning_placeholder:
                            display_reasoning(full_reasoning, is_streaming=True)
                    
                    if chunk["content"]:
                        full_content += chunk["content"]
                        content_placeholder.markdown(full_content + "▌")
                
                content_placeholder.markdown(full_content)
                
                if full_reasoning:
                    with reasoning_placeholder:
                        with st.expander("🔍 Visualizza Processo Logico"):
                            display_reasoning(full_reasoning)

            # Aggiunta e salvataggio
            st.session_state.messages.append({
                "role": "assistant", 
                "content": full_content, 
                "reasoning_details": full_reasoning
            })
            save_chat(st.session_state.messages)
            st.rerun() # --- FORZA AGGIORNAMENTO UI PER EXPORT ---

        except Exception as e:
            st.error(f"❌ Errore: {str(e)}")
