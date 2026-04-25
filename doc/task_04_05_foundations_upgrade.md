# Report Tecnico: Fondamenta Avanzate - Parametri & Contesto

**Data:** 25 Aprile 2026
**Stato:** Completato
**Task ID:** 04 & 05

## 1. Obiettivo
Rendere il motore di chat configurabile e tecnicamente robusto, permettendo il controllo della generazione (Temperature/Tokens) e la gestione automatica della memoria (Context Pruning).

## 2. Implementazione Parametri Generativi (Task 04)
- **Engine Update (`api_engine.py`)**: Esteso il metodo `get_chat_response_stream` per supportare i parametri `temperature` e `max_tokens`.
- **Interfaccia (`main_app.py`)**: Inserito un expander "Parametri Avanzati" nella sidebar contenente:
    - Slider **Temperatura**: Per regolare il bilanciamento tra determinismo e creatività.
    - Slider **Max Tokens**: Per definire la lunghezza massima della risposta singola.

## 3. Gestione del Contesto & Memory Window (Task 05)
- **Problema**: L'invio dell'intera cronologia causava errori di "Context Length Exceeded" in sessioni lunghe.
- **Soluzione (Pruning)**: Introdotta la variabile `mem_window`. Il sistema seleziona solo gli ultimi *N* messaggi dalla cronologia.
- **System Prompt Protection**: Implementata logica di filtraggio che garantisce la persistenza del messaggio di sistema (ruolo scelto dall'utente) all'inizio di ogni payload inviato all'API, indipendentemente dalla finestra di memoria scelta.

## 4. Stato Finale
Il software è ora in grado di gestire conversazioni teoricamente infinite senza crash tecnici, permettendo all'utente di ottimizzare il consumo di token e la qualità della risposta in base al compito (es. codifica vs scrittura creativa).

---
*Senior AI & Python Engineer*
