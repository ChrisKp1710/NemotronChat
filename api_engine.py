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
        
        # Prepariamo un "dizionario" pulito da restituire all'interfaccia grafica
        return {
            "content": obj_msg.content, # Il testo della risposta
            "reasoning": getattr(obj_msg, "reasoning_details", None) # Il JSON del ragionamento (se c'è)
        }
        
    except Exception as e:
        # Se qualcosa esplode, blocchiamo tutto e generiamo un errore chiaro
        raise Exception(f"Errore di comunicazione con OpenRouter: {e}")