import os
import requests
import pandas as pd
import textwrap
import random
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import urllib.parse

# --- CONFIGURAZIONE ---
PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID", "234931856561526")
FACEBOOK_TOKEN = os.environ.get("FACEBOOK_TOKEN")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("MINDSET_CHAT_ID")

CSV_FILE = "Mindset.csv"
LOGO_PATH = "faccia.png"
FONT_NAME = "arial.ttf"

# --- 1. GESTIONE DATI ---
def get_random_quote():
    try:
        if not os.path.exists(CSV_FILE):
            print(f"⚠️ File {CSV_FILE} non trovato!")
            return None
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

# --- 3. AI & IMMAGINI (Con Sistema Anti-Blocco) ---
def get_ai_image(prompt_text):
    print(f"🎨 Generazione immagine AI...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'
    }
    
    # Tentativo 1: Pollinations AI
    try:
        clean_prompt = urllib.parse.quote(prompt_text)
        random_seed = random.randint(1, 99999)
        url_ai = f"https://image.pollinations.ai/prompt/{clean_prompt}?width=1080&height=1080&nologo=true&seed={random_seed}"
        
        res_ai = requests.get(url_ai, headers=headers, timeout=20)
        if res_ai.status_code == 200:
            try:
                img = Image.open(BytesIO(res_ai.content)).convert("RGBA")
                print("✅ Sfondo AI scaricato con successo!")
                return img
            except Exception as e_img:
                print(f"⚠️ Il server AI ha inviato un errore: {e_img}")
        else:
            print(f"⚠️ Server AI bloccato (Codice: {res_ai.status_code}). Passo al Piano B...")
    except Exception as e:
        print(f"⚠️ Errore connessione AI: {e}. Passo al Piano B...")

    # Tentativo 2: Picsum (Sicuro al 100%)
    try:
        print("🔄 Scaricamento immagine stock sicura (Picsum)...")
        seed = random.randint(1, 99999)
        url_stock = f"https://picsum.photos/seed/{seed}/1080/1080?grayscale&blur=2"
        res_stock = requests.get(url_stock, timeout=15)
        if res_stock.status_code == 200:
            img_stock = Image.open(BytesIO(res_stock.content)).convert("RGBA")
            print("✅ Sfondo stock sicuro scaricato!")
            return img_stock
    except Exception as e:
        print(f"⚠️ Errore su Picsum: {e}")

    # Tentativo 3: Sfondo elegante
    print("⚠️ Uso sfondo grigio scuro di emergenza.")
    return Image.new('RGBA', (1080, 1080), (25, 25, 25))

# --- 4. FUNZIONE FONT ---
def load_font(size):
    fonts_to_try = [FONT_NAME, "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "arial.ttf"]
    for font_path in fonts_to_try:
        try:
            return ImageFont.truetype(font_path, size)
        except: continue
    return ImageFont.load_default()

# --- 5. CREAZIONE GRAFICA PRINCIPALE ---
def create_quote_image(row):
    prompt = get_image_prompt(row['Categoria'])
    base_img = get_ai_image(prompt).resize((1080, 1080))
    
    overlay = Image.new('RGBA', base_img.size, (0, 0, 0, 100))
    base_img = Image.alpha_composite(base_img, overlay)
    
    overlay_txt = Image.new('RGBA', base_img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay_txt)
    W, H = base_img.size
    
    font_txt = load_font(85)  
    font_author = load_font(50)   

    text = f"“{row['Frase']}”"
    lines = textwrap.wrap(text, width=20) 
    
    line_height = 95
    text_block_height = len(lines) * line_height
    author_height = 80
    total_content_height = text_block_height + author_height
    
    start_y = ((H - total_content_height) / 2) - 80 
    
    # Box testo
    padding = 50
    draw.rectangle([(40, start_y - padding), (W - 40, start_y + total_content_height + padding)], fill=(0, 0, 0, 170))
    
    # Scrittura Testo
    current_y = start_y
    for line in lines:
        draw.text((W//2, current_y), line, font=font_txt, fill="white", anchor="mt")
        current_y += line_height
        
    # Autore
    author = f"- {str(row['Autore'])} -"
    draw.text((W//2, current_y + 25), author, font=font_author, fill="#FFD700", anchor="mt")

    return Image.alpha_composite(base_img, overlay_txt)

# --- 6. AGGIUNTA BRANDING ---
def add_branding(img):
    margin_left = 40
    margin_bottom = 40
    logo_w, logo_h, logo_x, logo_y = 0, 0, 0, 0

    if os.path.exists(LOGO_PATH):
        try:
            face = Image.open(LOGO_PATH).convert("RGBA")
            logo_w = int(img.width * 0.20)
            logo_h = int(logo_w * (face.height / float(face.width)))
            face = face.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
            
            logo_x = margin_left
            logo_y = img.height - logo_h - margin_bottom
            img.paste(face, (logo_x, logo_y), face)
        except Exception as e:
            print(f"⚠️ Errore caricamento logo faccia: {e}")

    draw = ImageDraw.Draw(img)
    font_name = load_font(50)
    text = "Antonio Giancani"
    
    # Calcolo posizione del testo "Antonio Giancani"
    if logo_w > 0:
        text_x = logo_x + logo_w + 25
        text_y = logo_y + (logo_h // 2) - 25
    else:
        text_x = margin_left
        text_y = img.height - 80 - margin_bottom

    draw.text((text_x, text_y), text, font=font_name, fill="#FFD700")
    return img

# --- 7. CREAZIONE FORMATO STORIA ---
def create_story_image(square_img):
    print("📱 Creazione formato Storia...")
    story_w, story_h = 1080, 1920
    bg_color = (15, 15, 15)
    story_img = Image.new('RGBA', (story_w, story_h), bg_color)
    
    y_pos = (story_h - square_img.height) // 2
    story_img.paste(square_img, (0, y_pos))
    
    draw = ImageDraw.Draw(story_img)
    font_story = load_font(60)
    text_top = "NUOVO POST ⤵"
    
    draw.text((story_w//2, y_pos - 150), text_top, font=font_story, fill="#FFD700", anchor="mt")
    return story_img

# --- 8. TESTO POST ---
def genera_coaching(row):
    cat = str(row['Categoria']).lower()
    intro = random.choice(["🚀 𝗠𝗶𝗻𝗱𝘀𝗲𝘁 𝗜𝗺𝗺𝗼𝗯𝗶𝗹𝗶𝗮𝗿𝗲:", "💡 𝗖𝗼𝗻𝘀𝗶𝗴𝗹𝗶𝗼 𝗱𝗲𝗹 𝗴𝗶𝗼𝗿𝗻𝗼:", "🏠 𝗩𝗶𝘀𝗶𝗼𝗻𝗲 𝗲 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗼:"])
    
    if "motiva" in cat: msg = "Non aspettare il momento giusto, crealo. Vince chi ha fame."
    elif "vendita" in cat: msg = "La vendita non è convincere, è aiutare il cliente a decidere."
    elif "disciplina" in cat: msg = "La costanza batte l'intensità."
    else: msg = "Il tuo unico limite è la visione che hai di te stesso. Alza l'asticella."
    
    return f"{intro}\n{msg}"

# --- 9. SOCIAL ---
def send_telegram(img_bytes, caption):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID: 
        print("⚠️ Telegram saltato (mancano i segreti).")
        return
    print("✈️ Invio Telegram...")
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
        files = {'photo': ('post.png', img_bytes)}
        data = {'chat_id': TELEGRAM_CHAT_ID, 'caption': caption}
        r = requests.post(url, files=files, data=data)
        if r.status_code == 200: print("✅ Telegram OK")
        else: print(f"❌ Telegram Fail: {r.text}")
    except Exception as e: print(f"❌ Telegram Error: {e}")

def post_facebook(img_bytes, caption):
    id_sicuro = str(PAGE_ID)[:5] if PAGE_ID else "NESSUN_ID"
    print(f"🚀 Debug FB: ID={id_sicuro}... Token={bool(FACEBOOK_TOKEN)}")
    
    if not PAGE_ID or not FACEBOOK_TOKEN:
        print("❌ Facebook saltato: PAGE_ID o TOKEN mancante nei Secrets!")
        return
        
    try:
        url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/photos"
        payload = {'message': caption, 'access_token': FACEBOOK_TOKEN, 'published': 'true'}
        files = {'source': ('post.png', img_bytes)}
        r = requests.post(url, data=payload, files=files)
        if r.status_code == 200: print("✅ Facebook OK")
        else: print(f"❌ Errore API Facebook: {r.text}")
    except Exception as e: print(f"❌ Facebook Fail: {e}")

# --- MAIN ---
if __name__ == "__main__":
    print("🚀 Avvio Bot Mindset v2.1...")
    row = get_random_quote()
    
    if row is not None:
        print(f"💼 Categoria: {row['Categoria']}")
        
        # 1. Crea Immagine Square (Feed)
        img_square = add_branding(create_quote_image(row))
        buf_feed = BytesIO()
        img_square.save(buf_feed, format='PNG')
        img_bytes = buf_feed.getvalue()
        
        # 2. Crea Immagine Story (Opzionale, al momento salvata ma non inviata in API)
        img_story = create_story_image(img_square)
        buf_story = BytesIO()
        img_story.save(buf_story, format='PNG')
        
        # Testi
        coaching_text = genera_coaching(row)
        caption = (
            f"💎 {str(row['Categoria']).upper()} 💎\n\n"
            f"“{row['Frase']}”\n\n"
            f"────────────────\n{coaching_text}\n────────────────\n\n"
            f"👤 Antonio Giancani\n🏠 Agente Immobiliare\n\n#immobiliare #mindset #successo"
        )

        
        # 3. INVIO
        send_telegram(img_bytes, caption)
        post_facebook(img_bytes, caption)
        
    else:
        print("⚠️ Nessuna frase trovata nel CSV.")
