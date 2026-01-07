import os
import requests
import pandas as pd
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import textwrap
import random
from io import BytesIO
from PIL import Image, ImageOps, ImageDraw, ImageFont

# --- CONFIGURAZIONE ---
# Token Pagina diretto
FACEBOOK_TOKEN = os.environ.get("FACEBOOK_TOKEN")
TELEGRAM_TOKEN = os.environ.get("AGENCY_TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("MINDSET_CHAT_ID")

# ID PAGINA AZIENDALE
PAGE_ID = "108297671444008"

CSV_FILE = "Mindset.csv"
LOGO_PATH = "faccia.png"
FONT_NAME = "arial.ttf" 

# --- 1. GESTIONE DATI ---
def get_random_quote():
    try:
        df = pd.read_csv(CSV_FILE)
        if df.empty: return None
        return df.sample(1).iloc[0]
    except Exception as e:
        print(f"⚠️ Errore lettura CSV: {e}")
        return None

# --- 2. GENERATORE PROMPT ---
def get_image_prompt(categoria):
    cat = str(categoria).lower().strip()
    base_style = "cinematic lighting, photorealistic, 8k, luxury, success atmosphere, golden hour, high contrast"
    
    prompts_mindset = [
        f"man in suit standing on top of skyscraper looking at city sunrise, {base_style}",
        f"close up of a lion face, intense look, dark background with golden rim light, {base_style}",
        f"mountain climber reaching the peak, sun rays, epic view, {base_style}"
    ]
    prompts_business = [
        f"luxury modern villa exterior with pool, sunset, architectural masterpiece, {base_style}",
        f"modern glass skyscraper looking up, blue sky, reflection, {base_style}",
        f"close up of handshake, business meeting, blur office background, {base_style}",
        f"modern interior design office, luxury apartment, city view window, {base_style}"
    ]
    prompts_focus = [
        f"highway at night with light trails, speed, city skyline, {base_style}",
        f"chess board close up, king piece, strategy, dramatic light, {base_style}",
        f"gym workout weights, focus, sweat, determination, dark moody lighting, {base_style}"
    ]

    if "motiva" in cat or "mindset" in cat: return random.choice(prompts_mindset)
    elif "disciplina" in cat or "focus" in cat: return random.choice(prompts_focus)
    else: return random.choice(prompts_business)

# --- 3. AI & IMMAGINI ---
def get_ai_image(prompt_text):
    print(f"🎨 Generazione immagine: {prompt_text}")
    try:
        clean_prompt = prompt_text.replace(" ", "%20")
        url = f"https://image.pollinations.ai/prompt/{clean_prompt}?width=1080&height=1080&nologo=true"
        response = requests.get(url, timeout=20)
        if response.status_code == 200:
            return Image.open(BytesIO(response.content)).convert("RGBA")
    except Exception as e:
        print(f"⚠️ Errore AI: {e}")
    return Image.new('RGBA', (1080, 1080), (20, 20, 20))

# --- 4. FUNZIONE FONT ---
def load_font(size):
    fonts_to_try = [FONT_NAME, "DejaVuSans-Bold.ttf", "arial.ttf"]
    for font_path in fonts_to_try:
        try:
            return ImageFont.truetype(font_path, size)
        except: continue
    return ImageFont.load_default()

# --- 5. CREAZIONE GRAFICA PRINCIPALE ---
def create_quote_image(row):
    prompt = get_image_prompt(row['Categoria'])
    base_img = get_ai_image(prompt).resize((1080, 1080))
    
    overlay = Image.new('RGBA', base_img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    W, H = base_img.size
    
    font_txt = load_font(100)  
    font_author = load_font(60)   

    text = f"“{row['Frase']}”"
    lines = textwrap.wrap(text, width=16) 
    
    line_height = 110
    text_block_height = len(lines) * line_height
    author_height = 80
    total_content_height = text_block_height + author_height
    
    start_y = ((H - total_content_height) / 2) - 100 # Spostato un po' meno in alto
    
    padding = 50
    box_left = 40
    box_top = start_y - padding
    box_right = W - 40
    box_bottom = start_y + total_content_height + padding
    
    draw.rectangle([(box_left, box_top), (box_right, box_bottom)], fill=(0, 0, 0, 150), outline=None)
    
    final_img = Image.alpha_composite(base_img, overlay)
    draw_final = ImageDraw.Draw(final_img)
    
    current_y = start_y
    for line in lines:
        bbox = draw_final.textbbox((0, 0), line, font=font_txt)
        w = bbox[2] - bbox[0]
        draw_final.text(((W - w)/2, current_y), line, font=font_txt, fill="white")
        current_y += line_height
        
    author = f"- {str(row['Autore'])} -"
    bbox_auth = draw_final.textbbox((0, 0), author, font=font_author)
    w_auth = bbox_auth[2] - bbox_auth[0]
    draw_final.text(((W - w_auth)/2, current_y + 25), author, font=font_author, fill="#FFD700")

    return final_img

# --- 6. AGGIUNTA BRANDING (FACCIA + NOME A SINISTRA) ---
def add_branding(img):
    # 1. Preparazione variabili per il logo
    logo_w = 0
    logo_h = 0
    logo_x = 0
    logo_y = 0
    # USIAMO IL MARGINE SINISTRO ORA
    margin_left = 40
    margin_bottom = 40

    # 2. Caricamento e posizionamento della Faccia (Logo)
    if os.path.exists(LOGO_PATH):
        try:
            face = Image.open(LOGO_PATH).convert("RGBA")
            # Dimensione: 20% della larghezza dell'immagine
            logo_w = int(img.width * 0.20)
            logo_h = int(logo_w * (face.height / face.width))
            face = face.resize((logo_w, logo_h))
            
            # POSIZIONE: Angolo in basso a SINISTRA
            logo_x = margin_left
            logo_y = img.height - logo_h - margin_bottom
            
            img.paste(face, (logo_x, logo_y), face)
        except Exception as e:
            print(f"⚠️ Errore caricamento logo: {e}")

    # 3. Aggiunta del Nome "Antonio Giancani"
    draw = ImageDraw.Draw(img)
    font_name = load_font(55) # Font per la firma
    text = "Antonio Giancani"
    
    # Calcola dimensione del testo
    bbox = draw.textbbox((0, 0), text, font=font_name)
    text_h = bbox[3] - bbox[1]
    
    # Posizione del testo
    if logo_w > 0:
        # Se c'è il logo, testo a DESTRA del logo, centrato verticalmente
        text_x = logo_x + logo_w + 25 # 25px di spazio tra logo e testo
        text_y = logo_y + (logo_h - text_h) / 2
    else:
        # Se non c'è il logo, solo testo in basso a sinistra
        text_x = margin_left
        text_y = img.height - text_h - margin_bottom

    # Scritta in color Oro
    draw.text((text_x, text_y), text, font=font_name, fill="#FFD700")
    
    return img

# --- 7. TESTO POST ---
def genera_coaching(row):
    cat = str(row['Categoria']).lower()
    intro = random.choice(["🚀 𝗠𝗶𝗻𝗱𝘀𝗲𝘁 𝗜𝗺𝗺𝗼𝗯𝗶𝗹𝗶𝗮𝗿𝗲:", "💡 𝗖𝗼𝗻𝘀𝗶𝗴𝗹𝗶𝗼 𝗱𝗲𝗹 𝗴𝗶𝗼𝗿𝗻𝗼:", "🏠 𝗩𝗶𝘀𝗶𝗼𝗻𝗲 𝗲 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗼:"])
    msg = "Il tuo unico limite è la visione che hai di te stesso. Alza l'asticella."
    if "motiva" in cat: msg = "Non aspettare il momento giusto, crealo. Vince chi ha fame."
    elif "vendita" in cat: msg = "La vendita non è convincere, è aiutare il cliente a decidere."
    elif "disciplina" in cat: msg = "La costanza batte l'intensità."
    return f"{intro}\n{msg}"

# --- 8. SOCIAL ---
def send_telegram(img_bytes, caption):
    if not TELEGRAM_TOKEN: return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
        files = {'photo': ('img.png', img_bytes, 'image/png')}
        data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': caption}
        requests.post(url, files=files, data=data)
        print("✅ Telegram OK")
    except Exception as e: print(f"❌ Telegram Error: {e}")

def post_facebook(img_bytes, message):
    if not FACEBOOK_TOKEN: 
        print("❌ Token Facebook mancante nei Secrets")
        return
    
    # URL diretto per pubblicare sulla Pagina usando il Token Pagina
    url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/photos?access_token={FACEBOOK_TOKEN}"
    files = {'file': ('img.png', img_bytes, 'image/png')}
    data = {'message': message, 'published': 'true'}
    
    try:
        response = requests.post(url, files=files, data=data)
        if response.status_code == 200:
            print(f"✅ Facebook OK! Post ID: {response.json().get('id')}")
        else:
            print(f"❌ Facebook ERRORE: {response.status_code}")
            print(f"DETTAGLI: {response.text}")
    except Exception as e: 
        print(f"❌ Errore connessione Facebook: {e}")

# --- MAIN ---
if __name__ == "__main__":
    print("🚀 Avvio Bot Mindset...")
    row = get_random_quote()
    if row is not None:
        print(f"💼 Mindset: {row['Categoria']}")
        # Crea immagine base + Aggiungi Branding (Faccia e Nome a SINISTRA)
        img = add_branding(create_quote_image(row))
        
        buf = BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        
        coaching_text = genera_coaching(row)
        caption = (
            f"💎 {str(row['Categoria']).upper()} 💎\n\n"
            f"“{row['Frase']}”\n\n"
            f"────────────────\n{coaching_text}\n────────────────\n\n"
            f"👤 Antonio Giancani\n🏠 Agente Immobiliare\n\n#immobiliare #mindset #successo"
        )
        
        send_telegram(buf, caption)
        buf.seek(0)
        post_facebook(buf, caption)
    else:
        print("⚠️ Nessuna frase trovata nel CSV")
