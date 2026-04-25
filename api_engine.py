# api_engine.py

from openai import OpenAI

def get_chat_response(api_key, model, messages):
    """
    Funzione sincrona standard (Legacy/Fallback).
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
        
        if getattr(response, 'choices', None) is None or len(response.choices) == 0:
            raise Exception("Il server ha restituito un pacchetto vuoto.")

        obj_msg = response.choices[0].message
        content = obj_msg.content or ""
        reasoning = getattr(obj_msg, "reasoning_details", None)
        
        # Salvagente per ragionamento senza contenuto
        if content == "" and reasoning:
            if isinstance(reasoning, list) and len(reasoning) > 0:
                content = reasoning[0].get('text', '') if isinstance(reasoning[0], dict) else ""
            elif isinstance(reasoning, str):
                content = reasoning
        
        return {"content": content, "reasoning": reasoning}
    except Exception as e:
        raise Exception(f"{e}")

def get_chat_response_stream(api_key, model, messages):
    """
    Funzione GENERATRICE per lo streaming.
    Yielda chunk di contenuto e accumula il ragionamento.
    """
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
            extra_body={"reasoning": {"enabled": True}}
        )
        
        for chunk in response:
            if not chunk.choices:
                continue
            
            delta = chunk.choices[0].delta
            
            # 1. Estrazione Ragionamento (se presente nel chunk)
            # Nota: OpenRouter spesso mette il reasoning in campi custom del delta
            reasoning_chunk = getattr(delta, "reasoning", None) or getattr(delta, "reasoning_details", None)
            
            # 2. Estrazione Contenuto
            content_chunk = delta.content or ""
            
            yield {
                "content": content_chunk,
                "reasoning": reasoning_chunk
            }
            
    except Exception as e:
        raise Exception(f"Errore Streaming: {e}")