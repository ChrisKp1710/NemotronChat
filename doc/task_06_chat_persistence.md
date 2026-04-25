# Report Tecnico: Persistenza Locale & Auto-Save

**Data:** 25 Aprile 2026
**Stato:** Completato
**Task ID:** 06

## 1. Obiettivo
Garantire che la sessione di chat non vada persa in caso di refresh della pagina o chiusura del browser, implementando un sistema di salvataggio locale automatico.

## 2. Implementazione Tecnica
- **Formato Dati**: Utilizzato il formato JSON per la semplicità di interscambio con le liste di messaggi di OpenAI/OpenRouter.
- **Funzioni Core**:
    - `save_chat()`: Scrive il `session_state.messages` su `chat_history.json`.
    - `load_chat()`: Tenta di leggere il file all'avvio dell'applicazione.
- **Integrazione Streamlit**:
    - Inizializzazione della sessione tramite `load_chat()` invece di una lista vuota.
    - Chiamata a `save_chat()` inserita immediatamente dopo la ricezione del messaggio completo dall'assistente.

## 3. Gestione del Ciclo di Vita
- **Reset**: Il tasto "Nuova Chat" è stato aggiornato per invocare `os.remove(HISTORY_FILE)`, garantendo che al prossimo riavvio l'utente parta da una sessione realmente pulita.
- **Sicurezza**: Aggiunta gestione delle eccezioni (`try/except`) durante il caricamento del file per prevenire crash in caso di file JSON corrotti.

## 4. Stato Finale
L'applicazione è ora "stateless" dal punto di vista dell'utente ma "stateful" dal punto di vista del sistema. La continuità della conversazione è garantita.

---
*Senior AI & Python Engineer*
