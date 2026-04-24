# api_engine.py

from openai import OpenAI

def get_chat_response(api_key, model, messages):
    """
    Funzione principale per comunicare con OpenRouter.
    """
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            extra_body={"reasoning": {"enabled": True}}
        )
        
        # --- 🛡️ NUOVO SCUDO ANTI-CRASH ---
        # Se OpenRouter ha un momento di down e non manda le 'choices'
        if getattr(response, 'choices', None) is None or len(response.choices) == 0:
            raise Exception("Il server ha restituito un pacchetto vuoto (Nessuna risposta generata).")
        # ---------------------------------

        obj_msg = response.choices[0].message
        
        # Estraiamo i dati grezzi
        content = obj_msg.content
        reasoning = getattr(obj_msg, "reasoning_details", None)
        
        if content is None:
            content = ""
            
        # --- 🛟 SALVAGENTE SUPER-BLINDATO ---
        if content == "" and reasoning:
            if isinstance(reasoning, list) and len(reasoning) > 0:
                primo_elemento = reasoning[0]
                # Controlliamo che sia davvero un dizionario prima di esplorarlo
                if isinstance(primo_elemento, dict) and 'text' in primo_elemento:
                    content = primo_elemento['text']
            elif isinstance(reasoning, str):
                content = reasoning
                
        # Se anche dopo il salvagente è vuoto, evitiamo errori grafici
        if content == "":
            # NOTA: Qui ho corretto le virgolette per non far crashare Python!
            content = "⚠️ Il modello ha 'ragionato', ma non ha scritto nessuna risposta finale."
        # ------------------------------------
        
        return {
            "content": content, 
            "reasoning": reasoning 
        }
        
    except Exception as e:
        # Passiamo l'errore al file dell'interfaccia grafica in modo pulito
        raise Exception(f"{e}")