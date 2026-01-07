import os
import requests

# Assicurati di avere il token aggiornato nei Secrets o incollalo qui tra virgolette per il test
# TOKEN = "INCOLLA_QUI_IL_TOKEN_PER_TESTARE_SUBITO" 
TOKEN = os.environ.get("FACEBOOK_TOKEN") 

def lista_pagine():
    print("🕵️‍♂️ Interrogo Facebook per vedere le tue Pagine...")
    
    if not TOKEN:
        print("❌ Errore: Manca il Token!")
        return

    url = f"https://graph.facebook.com/v19.0/me/accounts?access_token={TOKEN}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if "data" in data:
            pagine = data['data']
            if len(pagine) == 0:
                print("⚠️ RISULTATO: Nessuna Pagina trovata!")
                print("Motivo probabile: Stai usando un Profilo Personale.")
                print("Soluzione: Devi creare una 'Pagina' da Facebook (es. 'Antonio Giancani Real Estate').")
            else:
                print(f"✅ Trovate {len(pagine)} Pagine gestibili:")
                print("-" * 30)
                for p in pagine:
                    print(f"Nome: {p['name']}")
                    print(f"ID:   {p['id']}")
                    print(f"Token: {p['access_token'][:15]}...") # Ne mostro solo un pezzo
                    print("-" * 30)
                print("USA L'ID CHE VEDI QUI SOPRA NEL TUO MAIN.PY!")
        else:
            print("❌ Errore nella risposta:", data)
            
    except Exception as e:
        print(f"❌ Errore di connessione: {e}")

if __name__ == "__main__":
    lista_pagine()
