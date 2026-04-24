# api_engine.py

# Questo file è il "Motore". Non sa nulla di grafica, bottoni o colori. Il suo unico scopo è prendere un messaggio, 
# impacchettarlo, spedirlo a OpenRouter, e restituire la risposta (testo e ragionamento JSON).

from openai import OpenAI

def get_chat_response(api_key, model, messages):
    """
    Funzione principale per comunicare con OpenRouter.
    Riceve la chiave, il modello scelto e la cronologia dei messaggi.
    """
    
    # 1. Configuriamo il "postino" che manderà il messaggio
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    
    # 2. Mettiamo tutto in un blocco Try/Except per gestire errori di rete
    try:
        # Chiamata all'API (con il ragionamento sempre attivato)
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            extra_body={"reasoning": {"enabled": True}}
        )
        
        # 3. Estraiamo il succo dal pacchetto gigante che ci torna indietro
        obj_msg = response.choices[0].message
        
        # Estraiamo i dati grezzi
        content = obj_msg.content
        reasoning = getattr(obj_msg, "reasoning_details", None)
        
        # --- IL NOSTRO NUOVO "SALVAGENTE" ---
        # A. Se il modello non manda una risposta formale, togliamo il brutto "None"
        if content is None:
            content = ""
            
        # B. Se la risposta è vuota, ma ha scritto tutto nel box del ragionamento...
        if content == "" and reasoning:
            # Se è una lista formattata (come succede a volte con Tencent/Nemotron)
            if isinstance(reasoning, list) and len(reasoning) > 0 and 'text' in reasoning[0]:
                content = reasoning[0]['text']
            # Se è solo una lunga stringa di testo
            elif isinstance(reasoning, str):
                content = reasoning
        # -----------------------------------
        
        # Prepariamo un "dizionario" pulito da restituire all'interfaccia grafica
        return {
            "content": content, # Il testo della risposta (ora sempre valido)
            "reasoning": reasoning # Il JSON del ragionamento (se c'è)
        }
        
    except Exception as e:
        # Se qualcosa esplode, blocchiamo tutto e generiamo un errore chiaro
        raise Exception(f"Errore di comunicazione con OpenRouter: {e}")