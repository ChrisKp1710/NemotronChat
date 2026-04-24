# main_app.py

# Questo è il file "Vetrina". È quello che avvierai nel terminale.
# Si occupa solo di disegnare la grafica con Streamlit e usare gli altri due file per far funzionare tutto.

import streamlit as st
# Importiamo la nostra banca dati e il nostro motore dagli altri file creati!
from config import FREE_MODELS, CHAT_PRESETS
from api_engine import get_chat_response

# 1. CONFIGURAZIONE PAGINA
st.set_page_config(page_title="Multi-Model CoT Chat", page_icon="🧠", layout="wide")

# Inizializziamo subito la lista dei messaggi se non esiste
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- NOVITÀ: Memoria per il cambio modello ---
if "current_model" not in st.session_state:
    st.session_state.current_model = list(FREE_MODELS.keys())[0]

# 2. COSTRUZIONE DELLA BARRA LATERALE (SIDEBAR)
with st.sidebar:
    st.title("⚙️ Setup Chat")
    
    # Inserimento Password
    api_key = st.text_input("OpenRouter API Key", type="password")
    st.divider()
    
    # Menu a tendina per scegliere il modello (legge dal file config.py)
    selected_model_name = st.selectbox("🤖 Scegli il Modello Free", list(FREE_MODELS.keys()))
    # Prende il codice esatto del modello scelto
    model_id = FREE_MODELS[selected_model_name] 
    
    # --- NOVITÀ: Toast di conferma quando cambi modello ---
    if selected_model_name != st.session_state.current_model:
        st.session_state.current_model = selected_model_name
        st.toast(f"✅ Modello aggiornato a: {selected_model_name}", icon="🔄")
    
    # Menu a tendina per il ruolo dell'IA (legge dal file config.py)
    preset_name = st.selectbox("🎭 Scegli un Ruolo", list(CHAT_PRESETS.keys()))
    # Casella di testo che si autocompila in base alla scelta sopra
    system_input = st.text_area("Istruzioni di Sistema (Modificabili)", value=CHAT_PRESETS[preset_name], height=150)
    
    st.divider()
    
    # Tasto per resettare la memoria della chat
    if st.button("🗑️ Nuova Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# 3. BLOCCO DI SICUREZZA
# Se manca la chiave, mostriamo un avviso e fermiamo l'esecuzione della pagina
if not api_key:
    st.warning("⚠️ Inserisci la tua API Key nella barra laterale per iniziare.")
    st.stop()

# 4. DISEGNO DELLA CHAT STORICA
# Scorriamo tutti i messaggi salvati e li stampiamo a schermo
for msg in st.session_state.messages:
    # Non stampiamo a schermo le istruzioni "segrete" di sistema
    if msg["role"] != "system": 
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"]) # Stampa il testo normale
            
            # Se c'è un ragionamento, usa st.json per farlo bello colorato!
            if "reasoning_details" in msg and msg["reasoning_details"]:
                with st.expander("💭 Dettagli Ragionamento JSON"):
                    st.json(msg["reasoning_details"])

# 5. INPUT DELL'UTENTE E RISPOSTA
if prompt := st.chat_input("Scrivi qui il tuo messaggio..."):
    
    # Se è il primissimo messaggio, aggiungiamo di nascosto il System Prompt scelto
    if len(st.session_state.messages) == 0 and system_input.strip() != "":
        st.session_state.messages.append({"role": "system", "content": system_input})

    # Aggiungiamo il messaggio dell'utente alla lista e lo disegniamo
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Disegniamo la bolla di risposta dell'assistente
    with st.chat_message("assistant"):
        with st.spinner(f"Sto elaborando con {selected_model_name}..."):
            try:
                # CHIAMIAMO IL NOSTRO MOTORE ESTERNO (api_engine.py)
                result = get_chat_response(api_key, model_id, st.session_state.messages)
                
                # Stampiamo la risposta
                st.markdown(result["content"])
                
                # Stampiamo il JSON a colori
                if result["reasoning"]:
                    with st.expander("💭 Dettagli Ragionamento JSON"):
                        st.json(result["reasoning"])
                
                # Salviamo il tutto nella cronologia per la prossima domanda
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": result["content"], 
                    "reasoning_details": result["reasoning"]
                })
                
            except Exception as e:
                # Se c'è un errore, lo convertiamo in testo per analizzarlo
                error_msg = str(e)
                
                # --- NOVITÀ: Gestione elegante del Traffico Intenso (Errore 429) ---
                if "429" in error_msg or "rate-limited" in error_msg:
                    st.error("🚦 **Traffico Intenso sul Server!**")
                    st.warning(f"Il modello **{selected_model_name}** al momento è sovraccarico (Troppi utenti stanno usando la versione Free).\n\n👉 **Soluzione:** Scegli un altro modello dal menu a sinistra per continuare a chattare!")
                else:
                    # Per tutti gli altri tipi di errori, mostriamo il messaggio originale
                    st.error(f"❌ Ops! Errore di comunicazione: {error_msg}")