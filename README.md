# 🧠 MindMatrix: Multi-Model Reasoning Chat

**MindMatrix** è un'interfaccia di chat avanzata basata su Streamlit che sfrutta le API di OpenRouter per offrire un'esperienza multi-modello (Nemotron, Llama, Qwen) con un focus particolare sui dettagli di **ragionamento (reasoning)** dell'IA.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-FF4B4B.svg)
![OpenRouter](https://img.shields.io/badge/OpenRouter-API-orange.svg)

## 🚀 Caratteristiche Principali

- **Streaming in Tempo Reale**: Visualizzazione immediata della risposta mentre viene generata.
- **Reasoning Box**: Visualizzazione dedicata e stilizzata del processo logico del modello (per modelli che lo supportano come Nemotron).
- **Multi-Model Support**: Switch rapido tra i migliori modelli gratuiti disponibili su OpenRouter.
- **Parametri Avanzati**: Controllo granulare su Temperatura, Max Tokens e Finestra di Memoria.
- **Persistenza Automatica**: Salvataggio locale della cronologia in formato JSON per non perdere mai le conversazioni.
- **Esportazione Professionale**: Download della chat in formato Markdown (.md) includendo i dettagli del ragionamento.
- **Token Monitor**: Monitoraggio euristico del consumo di token per sessione.

## 🛠️ Installazione

1. **Clona il repository**:
   ```bash
   git clone https://github.com/tuo-username/NemotronChat.git
   cd NemotronChat
   ```

2. **Crea un ambiente virtuale**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Su Windows: venv\Scripts\activate
   ```

3. **Installa le dipendenze**:
   ```bash
   pip install -r requirements.txt
   ```

## 📖 Utilizzo

1. Avvia l'applicazione:
   ```bash
   streamlit run main_app.py
   ```
2. Inserisci la tua **OpenRouter API Key** nella sidebar.
3. Scegli un modello e inizia a chattare!

## 📂 Struttura del Progetto

- `main_app.py`: L'interfaccia grafica e la logica dell'applicazione.
- `api_engine.py`: Il motore di comunicazione con le API di OpenRouter.
- `config.py`: Configurazioni dei modelli e preset dei ruoli.
- `doc/`: Archivio dei report tecnici e della roadmap di sviluppo.
- `chat_history.json`: (Generato) File di persistenza locale.

## 🛡️ Sicurezza

MindMatrix non memorizza la tua API Key in modo permanente. Viene gestita esclusivamente durante la sessione attiva tramite l'interfaccia protetta di Streamlit.

---
*Sviluppato con passione da un Senior AI Engineer & Python Developer.*
