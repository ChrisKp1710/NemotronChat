import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="Nemotron CoT Chat", page_icon="🧠")
st.title("🧠 Nemotron Reasoning Chat")

# --- CONFIGURAZIONE CLIENT E SIDEBAR ---
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

with st.sidebar:
    st.header("⚙️ Impostazioni")
    st.session_state.api_key = st.text_input("OpenRouter API Key", type="password")
    
    st.divider() # Linea di separazione
    
    # 🌟 MIGLIORIA 1: Pulsante per resettare la chat
    if st.button("🗑️ Nuova Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun() # Ricarica la pagina istantaneamente

if not st.session_state.api_key:
    st.warning("⚠️ Per favore, inserisci la tua API Key nella sidebar per iniziare.")
    st.stop()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.session_state.api_key,
)

# --- INIZIALIZZAZIONE MESSAGGI ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- VISUALIZZAZIONE CHAT ESISTENTE ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        # 🌟 MIGLIORIA 2: Coerenza visiva (usiamo st.markdown per il testo)
        if "reasoning_details" in msg and msg["reasoning_details"]:
            with st.expander("💭 Dettagli ragionamento"):
                st.markdown(msg["reasoning_details"])

# --- LOGICA CHAT (NUOVI MESSAGGI) ---
if prompt := st.chat_input("Chiedimi qualcosa (es. Quante 'r' ci sono in strawberry?)"):
    
    # Aggiungiamo e mostriamo il messaggio dell'utente
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            
            # 🌟 MIGLIORIA 3: Blocco Try/Except per evitare crash
            try:
                response = client.chat.completions.create(
                    model="nvidia/nemotron-3-super-120b-a12b:free",
                    messages=st.session_state.messages,
                    extra_body={"reasoning": {"enabled": True}}
                )

                # Estraiamo il messaggio e il ragionamento
                obj_msg = response.choices[0].message
                content = obj_msg.content
                reasoning_details = getattr(obj_msg, "reasoning_details", None)

                # Mostriamo la risposta finale
                st.markdown(content)
                
                # Mostriamo il ragionamento con lo stesso stile dello storico
                if reasoning_details:
                    with st.expander("💭 Dettagli ragionamento"):
                        st.markdown(reasoning_details)

                # Salviamo nello storico
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": content,
                    "reasoning_details": reasoning_details
                })
                
            except Exception as e:
                # Se qualcosa va storto, mostriamo un errore elegante
                st.error(f"❌ Ops! Errore di comunicazione con l'API: {e}")