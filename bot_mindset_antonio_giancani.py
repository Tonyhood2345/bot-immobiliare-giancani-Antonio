#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
======================================================================
  🎬 BOT VIDEO REELS & STORIE CON VOCE ED EFFETTI DINAMICI
  Autore: Antonio Giancani
  - Estrazione: Rigorosamente da Colonna F (Mindset.csv)
  - Voce Narrante: Italiano Neurale (Edge-TTS / gTTS)
  - Grafica: 1080x1920 (9:16 Verticale Reels/Stories)
  - Badge Logo: faccia.png (Avatar circolare con bordo oro)
  - Animazione: FFmpeg Ken Burns Effect (Zoom & Pan cinematografico)
  - Personal Branding: Esclusivo su Antonio Giancani (senza menzione agenzia)
  - Invio & Approvazione: Telegram con bottoni interattivi + Facebook Video Graph API
======================================================================
"""

import os
import sys
import csv
import json
import time
import random
import asyncio
import textwrap
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import urllib.parse
import imageio_ffmpeg
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- CONFIGURAZIONE ---
PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID") or "234931856561526"
FACEBOOK_TOKEN = os.environ.get("FACEBOOK_TOKEN") or ""
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN") or "8671578336:AAEHI-s-2g3dY9qnIIVc_hWzDdOuHm-MS6M"
TELEGRAM_CHAT_ID = os.environ.get("MINDSET_CHAT_ID") or "1723292483"

CSV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Mindset.csv")
LOGO_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "faccia.png")
MUSIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "musica_sottofondo")
FONT_NAME = "arial.ttf"

# Voce predefinita: Diego Neural
DEFAULT_VOICE = "it-IT-DiegoNeural"

# Percorso FFmpeg
FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

# Cartella temporanea di montaggio video
WORK_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "video_reels_output")
os.makedirs(WORK_DIR, exist_ok=True)
os.makedirs(MUSIC_DIR, exist_ok=True)


# --- 1. ESTRAZIONE RIGOROSA DA COLONNA F ---
def get_random_quote(id_richiesto=None):
    try:
        if not os.path.exists(CSV_FILE):
            print(f"⚠️ File {CSV_FILE} non trovato!")
            return None
            
        rows = []
        with open(CSV_FILE, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for idx, r in enumerate(reader, start=1):
                if not r or len(r) < 2:
                    continue
                if len(r) >= 6:
                    rows.append({
                        "ID": str(r[0]),
                        "Categoria": str(r[1]).strip(),
                        "Frase": str(r[2]).strip(),
                        "Autore": str(r[3]).strip(),
                        "Stato": str(r[4]).strip(),
                        "Colonna_F": str(r[5]).strip() # TESTO PRELEVATO DALLA COLONNA F
                    })
                elif len(r) >= 3:
                    # Formato standard 3 colonne: Categoria, Frase, Autore
                    rows.append({
                        "ID": str(idx),
                        "Categoria": str(r[0]).strip(),
                        "Frase": str(r[1]).strip(),
                        "Autore": str(r[2]).strip(),
                        "Stato": "Disponibile",
                        "Colonna_F": f"{str(r[1]).strip()} — {str(r[2]).strip()}" # Equivalente Colonna F
                    })
                    
        if not rows:
            print("⚠️ Nessuna riga valida trovata nel CSV!")
            return None
            
        if id_richiesto is not None:
            trovati = [r for r in rows if str(r["ID"]) == str(id_richiesto)]
            if trovati:
                return trovati[0]
                
        selected = random.choice(rows)
        print(f"📖 [COLONNA F] Citazione estratta (Riga {selected['ID']}): \"{selected['Colonna_F']}\"")
        return selected
    except Exception as e:
        print(f"⚠️ Errore lettura CSV: {e}")
        return None


# --- 2. GENERAZIONE MICRO-STORIA NARRATA (STORYTELLING SINCRONIZZATO) ---
def genera_micro_storia(categoria, frase, autore):
    """
    Genera una micro-storia o parabola di circa 28-35 parole (10-14 secondi di narrazione a voce)
    che racconta una situazione concreta mentre sullo schermo appare la citazione.
    """
    cat_pulita = str(categoria).upper().strip()
    frase_pulita = str(frase).strip('“”"\' ')
    autore_pulito = str(autore).strip()
    
    # 1. Tentativo con Groq API (Ultra-veloce e gratuito)
    groq_key = os.environ.get("GROQ_API_KEY")
    if groq_key:
        try:
            headers = {"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"}
            payload = {
                "model": "qwen/qwen3.8-27b",
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "Sei la voce narrante di Antonio Giancani per un Reels Instagram/Facebook. "
                            "Sullo schermo l'utente legge una citazione. Tu devi raccontare a voce una micro-storia "
                            "o parabola concreta di massimo 30-35 parole (circa 11-13 secondi di audio) "
                            "che illustri il significato pratico di quel pensiero. "
                            "Sii diretto, profondo ed emotivo. Non ripetere la citazione parola per parola tra virgolette, "
                            "racconta direttamente la storia in un perfetto italiano fluido."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"Citazione: \"{frase_pulita}\". Autore: {autore_pulito}. Categoria: {cat_pulita}."
                    }
                ],
                "max_tokens": 100,
                "temperature": 0.7
            }
            r = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers, verify=False, timeout=8)
            if r.status_code == 200:
                testo = r.json()["choices"][0]["message"]["content"].strip().strip('"')
                if len(testo.split()) >= 15:
                    print("  ✨ Micro-storia creata con AI Groq!", flush=True)
                    return testo
        except Exception as e:
            print(f"  ⚠️ Groq fallback: {e}")

    # 2. Tentativo con Google Gemini API
    gemini_key = os.environ.get("GOOGLE_API_KEY")
    if gemini_key:
        try:
            url_gemini = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
            prompt_g = (
                f"Scrivi una brevissima micro-storia in italiano di massimo 30 parole che dia vita a questo principio: "
                f"\"{frase_pulita}\" ({autore_pulito}). Non ripetere la citazione, racconta solo la micro-storia per un video Reels."
            )
            payload_g = {"contents": [{"parts": [{"text": prompt_g}]}]}
            r_g = requests.post(url_gemini, json=payload_g, timeout=8, verify=False)
            if r_g.status_code == 200:
                cand = r_g.json().get("candidates", [])[0]["content"]["parts"][0]["text"].strip().strip('"')
                if len(cand.split()) >= 15:
                    print("  ✨ Micro-storia creata con Gemini AI!", flush=True)
                    return cand
        except Exception:
            pass

    # 3. Fallback Narrativo Locale Intelligente (100% offline)
    storie_locali = {
        "IMMOBILIARE": [
            "Mentre molti spendono in beni che perdono valore domani, chi sceglie il mattone costruisce una fortezza silenziosa che protegge la famiglia e fa crescere il patrimonio negli anni.",
            "Nel 1980 un uomo scelse una casa invece di spese effimere. Quarant'anni dopo, quel solo immobile ha finanziato gli studi dei figli e garantito serenità a tutta la sua famiglia.",
            "La vera sicurezza non è accumulare cifre su uno schermo, ma possedere qualcosa di concreto sotto i tuoi piedi, capace di superare ogni tempesta economica."
        ],
        "MINDSET": [
            "Due persone guardano la stessa collina: una vede una salita faticosa, l'altra vede il panorama che conquisterà dall'alto. La realtà non cambia, cambia solo la tua mente.",
            "Quando decidi che nulla può fermarti, gli ostacoli smettono di essere muri e diventano semplicemente i gradini su cui salire per raggiungere la tua vera visione.",
            "La mente è come una terra fertile: se non semini intenzionalmente pensieri di grandezza e fiducia, le erbacce del dubbio cresceranno da sole."
        ],
        "VENDITA": [
            "Un consulente cercava di vendere a tutti i costi e riceveva solo rifiuti. Quando ha iniziato ad ascoltare davvero i bisogni del cliente, non ha più dovuto vendere nulla: hanno comprato loro.",
            "Non si tratta di convincere nessuno con le parole, ma di mostrare con i fatti che hai a cuore il futuro e il benessere di chi hai davanti.",
            "La fiducia non si compra con le promesse: si guadagna con la trasparenza e con la capacità di mantenere sempre la parola data."
        ],
        "DISCIPLINA": [
            "Ogni mattina lo scultore colpisce il marmo. Per mesi sembra non cambiare nulla, finché un giorno l'opera d'arte emerge. La grandezza è solo costanza invisibile.",
            "Nei giorni in cui manca l'entusiasmo, è la disciplina a prendere il timone. Chi vince non è chi ha sempre voglia, ma chi non si ferma mai.",
            "Non cercare scorciatoie miracolose. La vera magia accade quando ripeti i piccoli gesti giusti ogni singolo giorno, senza cedere alle distrazioni."
        ],
        "FOCUS": [
            "I raggi del sole scaldano la terra, ma solo quando una lente li concentra in un unico punto scocca la scintilla. Il tuo successo dipende da quanto sai essere focalizzato.",
            "Elimina il rumore di fondo. Chi cerca di fare tutto contemporaneamente finisce per non concludere nulla. Scegli la tua priorità e dedicale tutta la tua forza.",
            "Dire di no a cento cose secondarie è l'unico modo per dire un sì straordinario al tuo obiettivo più grande."
        ],
        "BUSINESS": [
            "Due imprenditori avevano la stessa idea: uno ha aspettato il momento perfetto, l'altro ha iniziato subito e ha corretto la rotta strada facendo. Oggi il secondo guida il mercato.",
            "Nel mondo degli affari la velocità di esecuzione batte la perfezione teorica. Decidi con lucidità, agisci con determinazione e crea valore concreto.",
            "La reputazione richiede vent'anni per essere costruita e cinque minuti per essere rovinata. Fai sempre ciò che è giusto, anche quando nessuno ti guarda."
        ]
    }
    opzioni = storie_locali.get(cat_pulita, storie_locali["MINDSET"])
    return random.choice(opzioni)


# --- 3. SINTESI VOCALE NEURALE ITALIANA CON FALLBACK ---
async def genera_audio_scena(testo, output_path, voce="it-IT-DiegoNeural"):
    success = False
    try:
        import edge_tts
        communicate = edge_tts.Communicate(testo, voce, rate="+2%", pitch="+0Hz")
        await asyncio.wait_for(communicate.save(output_path), timeout=8)
        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            success = True
    except Exception:
        pass
        
    if not success:
        from gtts import gTTS
        tts = gTTS(text=testo, lang='it', slow=False)
        tts.save(output_path)
    print(f"  🎙️ Traccia vocale registrata: {output_path} ({round(os.path.getsize(output_path)/1024, 1)} KB)", flush=True)


# --- 3. GENERAZIONE SFONDO AI DINAMICO 9:16 (720x1280) ---
def get_ai_background(categoria, output_path, seed=42):
    cat = str(categoria).lower().strip()
    base_style = "cinematic lighting, photorealistic 8k, luxury, success atmosphere, golden hour, high contrast, elegant vertical 9:16 composition"
    
    prompts_mindset = [
        f"visionary leader in tailored navy suit on top of modern skyscraper looking at sunrise, {base_style}",
        f"majestic lion close up, intense gaze, dark background with golden light, {base_style}",
        f"mountain climber on the highest sunlit peak, inspiring sun rays, {base_style}"
    ]
    prompts_business = [
        f"ultra luxury modern villa exterior with crystal swimming pool at sunset, masterpiece, {base_style}",
        f"modern architectural glass skyscraper reaching into blue sky, {base_style}",
        f"prestigious executive meeting in luxury panoramic lounge, {base_style}"
    ]
    prompts_focus = [
        f"golden highway at night with light trails, speed, futuristic skyline, {base_style}",
        f"chess board close up with golden king piece in spotlight, strategy, {base_style}",
        f"athlete pulling bowstring with laser focus, dramatic lighting, {base_style}"
    ]
    prompts_immobiliare = [
        f"prestigious Mediterranean luxury estate entrance with fountain and palm trees, sunset, {base_style}",
        f"modern luxury villa with private garden, panoramic sea view, warm sunlight, {base_style}"
    ]

    if "motiva" in cat or "mindset" in cat: 
        prompt_text = random.choice(prompts_mindset)
    elif "disciplina" in cat or "focus" in cat: 
        prompt_text = random.choice(prompts_focus)
    elif "immob" in cat:
        prompt_text = random.choice(prompts_immobiliare)
    else: 
        prompt_text = random.choice(prompts_business)

    print(f"  🎨 Generazione sfondo AI tematico...", flush=True)
    
    # Tentativo Pollinations
    try:
        clean_prompt = urllib.parse.quote(prompt_text)
        url_ai = f"https://image.pollinations.ai/prompt/{clean_prompt}?width=720&height=1280&nologo=true&seed={seed}"
        res_ai = requests.get(url_ai, timeout=30, verify=False)
        if res_ai.status_code == 200 and len(res_ai.content) > 10000:
            with open(output_path, "wb") as f:
                f.write(res_ai.content)
            print(f"  ✅ Sfondo AI scaricato con successo!", flush=True)
            return True
    except Exception as e:
        print(f"  ⚠️ Timeout AI: {e}. Uso fallback HD...")

    # Fallback Picsum
    try:
        url_stock = f"https://picsum.photos/seed/{seed}/720/1280?grayscale&blur=2"
        res_stock = requests.get(url_stock, timeout=15, verify=False)
        if res_stock.status_code == 200:
            with open(output_path, "wb") as f:
                f.write(res_stock.content)
            print(f"  ✅ Sfondo stock sicuro scaricato!", flush=True)
            return True
    except Exception:
        pass

    # Sfondo scuro di emergenza
    img_dark = Image.new('RGB', (720, 1280), (18, 22, 30))
    img_dark.save(output_path)
    return True


# --- 4. CARICAMENTO FONT ---
def load_font(size):
    fonts = [FONT_NAME, "C:\\Windows\\Fonts\\arialbd.ttf", "C:\\Windows\\Fonts\\arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
    for f in fonts:
        try:
            return ImageFont.truetype(f, size)
        except: 
            continue
    return ImageFont.load_default()


# --- 5. COMPOSIZIONE GRAFICA VERTICALE CON BADGE & TIPOGRAFIA ORO ---
def componi_frame_grafico(bg_path, testo_principale, autore, output_frame_path, categoria="MINDSET"):
    """
    Sovrappone lo sfondo AI con:
    - Overlay scuro di contrasto
    - Box in vetro scuro semitrasparente con bordo dorato
    - Testo citazione e autore in oro
    - Badge circolare con foto reale faccia.png
    - Firma 'Antonio Giancani - CONSULENZA & STRATEGIA'
    """
    base = Image.open(bg_path).convert("RGBA").resize((720, 1280))
    
    # Overlay scuro generale
    overlay_dark = Image.new('RGBA', base.size, (0, 0, 0, 110))
    base = Image.alpha_composite(base, overlay_dark)
    
    overlay_ui = Image.new('RGBA', base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay_ui)
    W, H = base.size
    
    # Header Superiore
    font_cat = load_font(28)
    draw.text((W//2, 80), f"◆ {categoria.upper()} ◆", font=font_cat, fill="#FFD700", anchor="mt")
    
    # Testo Citazione (Layout Più Stretto ed Elegante)
    testo_pulito = str(testo_principale).strip()
    if len(testo_pulito) > 110:
        font_size = 33
        line_height = 44
        wrap_w = 21
    elif len(testo_pulito) > 60:
        font_size = 39
        line_height = 50
        wrap_w = 18
    else:
        font_size = 45
        line_height = 58
        wrap_w = 15
        
    font_quote = load_font(font_size)
    font_author = load_font(28)
    
    lines = textwrap.wrap(f"“{testo_pulito}”", width=wrap_w)
    total_text_h = len(lines) * line_height + 55
    
    start_y = ((H - total_text_h) // 2) - 40
    padding = 32
    
    # Box centrale con bordo oro - Più Stretto Lateralmente (Margini 70px)
    box_margin_x = 70
    box_rect = [(box_margin_x, start_y - padding), (W - box_margin_x, start_y + total_text_h + padding)]
    draw.rounded_rectangle(box_rect, radius=18, fill=(12, 16, 24, 210), outline="#FFD700", width=2)
    
    # Scrittura testo
    curr_y = start_y
    for l in lines:
        draw.text((W//2, curr_y), l, font=font_quote, fill="white", anchor="mt")
        curr_y += line_height
        
    # Scrittura autore
    draw.text((W//2, curr_y + 12), f"— {autore} —", font=font_author, fill="#FFD700", anchor="mt")
    
    # Inserimento Badge Faccia in basso
    logo_size = 90
    if os.path.exists(LOGO_PATH):
        try:
            face = Image.open(LOGO_PATH).convert("RGBA").resize((logo_size, logo_size), Image.Resampling.LANCZOS)
            face_x = 45
            face_y = H - logo_size - 60
            base.paste(face, (face_x, face_y), face)
        except Exception as e:
            print(f"⚠️ Errore caricamento faccia: {e}")
            face_x = 45
            face_y = H - logo_size - 60
    else:
        face_x = 45
        face_y = H - logo_size - 60

    # Testo Branding Personale
    font_name = load_font(34)
    font_sub = load_font(20)
    text_x = face_x + logo_size + 18
    
    draw.text((text_x, face_y + 12), "Antonio Giancani", font=font_name, fill="#FFD700")
    draw.text((text_x, face_y + 50), "CONSULENZA & STRATEGIA", font=font_sub, fill="#E0E0E0")
    
    final_img = Image.alpha_composite(base, overlay_ui).convert("RGB")
    final_img.save(output_frame_path)
    return True


# --- 6. GESTIONE MUSICA DI SOTTOFONDO (CC0 NO COPYRIGHT SEMPRE DIVERSA) ---
def scegli_musica_sottofondo(categoria="MINDSET"):
    """Seleziona casualmente una traccia musicale CC0 Public Domain sempre diversa."""
    if not os.path.exists(MUSIC_DIR):
        os.makedirs(MUSIC_DIR, exist_ok=True)
        
    tracce = [os.path.join(MUSIC_DIR, f) for f in os.listdir(MUSIC_DIR) if f.endswith('.mp3') and os.path.getsize(os.path.join(MUSIC_DIR, f)) > 1000]
    
    # Se non sono presenti tracce locali, scarica fallback CC0 istantaneo
    if not tracce:
        print("  🎵 Download traccia musicale CC0 no-copyright di supporto...", flush=True)
        fallback_urls = [
            ("ambient_calma.mp3", "https://raw.githubusercontent.com/HazelvdW/MUSIFEAST-17/main/stimuli/Ambient_HIGH_11.mp3"),
            ("pianoforte_classico.mp3", "https://raw.githubusercontent.com/HazelvdW/MUSIFEAST-17/main/stimuli/Classical_HIGH_01.mp3"),
            ("cinematic_ispirazione.mp3", "https://raw.githubusercontent.com/HazelvdW/MUSIFEAST-17/main/stimuli/Film_HIGH_15.mp3"),
            ("jazz_business.mp3", "https://raw.githubusercontent.com/HazelvdW/MUSIFEAST-17/main/stimuli/Jazz_HIGH_08.mp3")
        ]
        for name, url in fallback_urls:
            try:
                dest = os.path.join(MUSIC_DIR, name)
                r = requests.get(url, timeout=15, verify=False)
                if r.status_code == 200 and len(r.content) > 1000:
                    with open(dest, 'wb') as f:
                        f.write(r.content)
                    tracce.append(dest)
            except Exception:
                pass

    if tracce:
        scelta = random.choice(tracce)
        print(f"  🎶 Sottofondo musicale selezionato (Royalty Free): {os.path.basename(scelta)}", flush=True)
        return scelta
    return None


# --- 7. CALCOLO DURATA AUDIO ---
def ottieni_durata_audio(audio_path):
    import subprocess
    cmd = [FFMPEG_EXE, "-i", audio_path]
    p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    _, stderr = p.communicate()
    for line in stderr.decode('utf-8', errors='ignore').split("\n"):
        if "Duration:" in line:
            parts = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = parts.split(":")
            return float(h)*3600 + float(m)*60 + float(s)
    return 5.0


# --- 8. MONTAGGIO VIDEO CON EFFETTO KEN BURNS E MIX AUDIO SOTTOFONDO ---
def crea_video_animato(frame_img_path, audio_path, output_video_path, bg_music_path=None):
    """
    Anima l'immagine con Slow Zoom in formato Reels 9:16 e mixa la voce neurale
    con un sottofondo musicale elegante a volume bilanciato (14%) con dissolvenza.
    """
    import subprocess
    durata = ottieni_durata_audio(audio_path) + 0.8
    frames_totali = int(durata * 25)
    
    # Filtro Zoom Pan fluido 720x1280 (9:16)
    zoom_filter = f"zoompan=z='min(zoom+0.0008,1.15)':d={frames_totali}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=720x1280:fps=25"
    
    if bg_music_path and os.path.exists(bg_music_path):
        fade_out_st = max(0.5, durata - 1.2)
        filter_complex = (
            f"[1:a]volume=1.0[voice];"
            f"[2:a]volume=0.14,afade=t=in:ss=0:d=0.8,afade=t=out:st={fade_out_st:.2f}:d=1.2[music];"
            f"[voice][music]amix=inputs=2:duration=first:dropout_transition=2[aout];"
            f"[0:v]{zoom_filter}[vout]"
        )
        cmd = [
            FFMPEG_EXE, "-y",
            "-loop", "1", "-i", frame_img_path,
            "-i", audio_path,
            "-i", bg_music_path,
            "-filter_complex", filter_complex,
            "-map", "[vout]", "-map", "[aout]",
            "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-t", str(durata),
            output_video_path
        ]
    else:
        cmd = [
            FFMPEG_EXE, "-y",
            "-loop", "1", "-i", frame_img_path,
            "-i", audio_path,
            "-vf", zoom_filter,
            "-c:v", "libx264", "-tune", "stillimage", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-shortest",
            "-t", str(durata),
            output_video_path
        ]
        
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    return True


# --- 9. COPYWRITING FACEBOOK AD ALTO INGAGGIO (EMOJI, SPUNTI, HASHTAG) ---
def genera_copy_post(row, storia=None):
    categoria = str(row['Categoria']).upper()
    frase = row['Frase']
    autore = row['Autore']
    
    intro_map = {
        "MINDSET": (
            "🧠 *IL POTERE DELLA MENTE E DELLA VISIONE*",
            "La differenza tra chi ottiene risultati straordinari e chi si ferma sta nel modo di interpretare le sfide ogni singolo giorno.",
            "Coltiva abitudini vincenti, allena la tua concentrazione e non permettere al rumore esterno di deviare i tuoi obiettivi."
        ),
        "VENDITA": (
            "💼 *L'ARTE DELLA NEGOZIAZIONE E DEL VALORE*",
            "Vendere non significa convincere, ma comprendere a fondo le reali esigenze delle persone e offrire la soluzione perfetta con integrità.",
            "Costruisci relazioni autentiche: la fiducia è la moneta più preziosa nel mercato di oggi."
        ),
        "IMMOBILIARE": (
            "🏛️ *STRATEGIA E VISIONE NEGLI INVESTIMENTI*",
            "Il valore di una scelta immobiliare non si misura nell'immediato, ma nella capacità di anticipare i trend e creare sicurezza nel tempo.",
            "Competenza, posizionamento e decisione: questi sono i tre pilastri per chi vuole costruire basi solide."
        ),
        "DISCIPLINA": (
            "⏳ *LA FORZA DELLA COSTANZA QUOTIDIANA*",
            "La motivazione ti fa partire, ma è solo la disciplina ferrea che ti porta al traguardo.",
            "Ogni piccolo sforzo ripetuto con perseveranza costruisce il ponte verso i tuoi sogni più grandi."
        ),
        "FOCUS": (
            "🎯 *ELIMINA IL SUPERFLUO, MASSIMIZZA L'IMPATTO*",
            "In un mondo pieno di distrazioni, la capacità di mantenere l'attenzione sull'essenziale è un autentico superpotere.",
            "Scegli dove indirizzare la tua energia: i risultati seguiranno la direzione del tuo focus."
        ),
        "BUSINESS": (
            "📈 *ECCELLENZA, VELOCITÀ ED ESECUZIONE*",
            "Le idee senza azione rimangono illusioni. Nel business vince chi sa decidere con rapidità ed eseguire con precisione millimetrica.",
            "Punta sempre all'eccellenza e fai parlare la solidità dei tuoi risultati."
        )
    }
    
    titolo_box, punto1, punto2 = intro_map.get(categoria, (
        "✨ *ISPIRAZIONE & STRATEGIA DEL GIORNO*",
        "Ogni traguardo comincia con la decisione coraggiosa di fare il primo passo e perseverare.",
        "Metti energia, dedizione e professionalità in tutto ciò che fai."
    ))
    
    sezione_storia = f"\n🎙️ *LA STORIA NEL VIDEO:*\n_{storia}_\n" if storia else ""
    
    caption = f"""💎 {categoria} DEL GIORNO 💎

«{frase}»
— {autore} —
{sezione_storia}
────────────────────────
{titolo_box}
────────────────────────
🔹 {punto1}
🔹 {punto2}

💡 *REGOLE CHIAVE:*
1️⃣ Azione costante e zero scuse
2️⃣ Focus sui risultati che contano davvero
3️⃣ Crescita e perfezionamento continuo

📲 *Guarda il Reels, lascia un mi piace e salva il post* per ritrovarlo ogni volta che hai bisogno della giusta carica!
💬 Scrivi nei commenti la tua riflessione su questa frase.

━━━━━━━━━━━━━━━━━━━━
👉 Riflessione e strategia a cura di:
⭐ ANTONIO GIANCANI ⭐
━━━━━━━━━━━━━━━━━━━━

#Mindset #CrescitaPersonale #Successo #Business #Focus #Disciplina #Leadership #MotivazioneDelGiorno #Strategia #Ispirazione #AntonioGiancani"""
    return caption


# --- 9. INVIO VIDEO CON TASTIERA DI APPROVAZIONE TELEGRAM ---
def invia_video_telegram(video_path, caption_text, item_id):
    print("📲 Invio VIDEO ANIMATO con tastiera di approvazione su Telegram...", flush=True)
    inline_keyboard = {
        "inline_keyboard": [
            [
                {"text": "✅ APPROVA E PUBBLICA VIDEO SU FACEBOOK", "callback_data": f"PUBBLICA_FB_VID_{item_id}"},
            ],
            [
                {"text": "🔄 RIGENERA CON ALTRA CITAZIONE", "callback_data": "RIGENERA_RANDOM"},
                {"text": "❌ SCARTA", "callback_data": "SCARTA"}
            ]
        ]
    }
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendVideo"
    
    # Limite Telegram per didascalie video: massimo 1024 caratteri
    if len(caption_text) > 750:
        testo_troncato = caption_text[:750].rsplit("\n", 1)[0]
        caption_telegram = (
            f"🎬 *NUOVO REELS (Colonna F)*\n\n"
            f"{testo_troncato}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👉 Strategia a cura di:\n"
            f"⭐ *ANTONIO GIANCANI* ⭐\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👆 *Clicca in basso per approvare e pubblicare!*"
        )
    else:
        caption_telegram = (
            f"🎬 *NUOVO REELS (Colonna F)*\n\n"
            f"{caption_text}\n\n"
            f"👆 *Clicca in basso per approvare e pubblicare!*"
        )

    with open(video_path, "rb") as vf:
        files = {"video": vf}
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "caption": caption_telegram,
            "parse_mode": "Markdown",
            "reply_markup": json.dumps(inline_keyboard)
        }
        res = requests.post(url, data=data, files=files, timeout=60, verify=False)
        
    if res.status_code == 200:
        print("✅ Video Reels inviato con successo su Telegram!", flush=True)
        return True
    else:
        print(f"❌ Errore invio Telegram ({res.status_code}): {res.text}", flush=True)
        return False


# --- 10. PUBBLICAZIONE VIDEO SU FACEBOOK GRAPH API CON DIAGNOSI AUTOMATICA ---
def ottieni_page_token_effettivo(token_base, page_id_target):
    """Verifica se il token è di pagina o utente; se utente, estrae il token specifico della pagina."""
    if not token_base:
        return None
    try:
        url_me = f"https://graph.facebook.com/v19.0/me?access_token={token_base}&fields=id,name,category"
        r_me = requests.get(url_me, timeout=15, verify=False)
        d_me = r_me.json()
        
        if "category" in d_me and (str(d_me.get("id")) == str(page_id_target) or not page_id_target):
            return token_base # È già un Page Access Token
            
        # È un User Token: cerchiamo nelle pagine gestite
        url_acc = f"https://graph.facebook.com/v19.0/me/accounts?access_token={token_base}&fields=id,name,access_token"
        r_acc = requests.get(url_acc, timeout=15, verify=False)
        d_acc = r_acc.json().get("data", [])
        for p in d_acc:
            if str(p.get("id")) == str(page_id_target) or not page_id_target:
                print(f"  🎯 Page Access Token rilevato per la Pagina: {p.get('name')} (ID: {p.get('id')})", flush=True)
                return p.get("access_token")
        if d_acc:
            return d_acc[0].get("access_token")
    except Exception as e:
        print(f"  ⚠️ Verifica token preliminare: {e}", flush=True)
    return token_base


def pubblica_video_facebook(video_path, caption):
    id_sicuro = str(PAGE_ID)[:5] if PAGE_ID else "NESSUN_ID"
    token_attivo = FACEBOOK_TOKEN
    print(f"🚀 Avvio Pubblicazione Video su Facebook (Page ID: {id_sicuro}... Token Configurato: {bool(token_attivo)})", flush=True)
    
    if not PAGE_ID or not token_attivo:
        msg_err = "⚠️ *Pubblicazione Facebook Saltata:* `FACEBOOK_PAGE_ID` o `FACEBOOK_TOKEN` non impostati nei Secrets di GitHub."
        print(msg_err, flush=True)
        invia_notifica_errore_fb(msg_err)
        return False

    # Estrazione o verifica Page Token
    token_da_usare = ottieni_page_token_effettivo(token_attivo, PAGE_ID)
    
    try:
        url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/videos"
        with open(video_path, "rb") as vf:
            files = {'source': ('video_reels_mindset.mp4', vf)}
            data = {'description': caption, 'access_token': token_da_usare}
            r = requests.post(url, files=files, data=data, timeout=180, verify=False)
            res_json = r.json()
            
            if r.status_code == 200 and "id" in res_json:
                vid_id = res_json.get("id")
                print(f"✅ Video Reels pubblicato con successo su Facebook! (Video ID: {vid_id})", flush=True)
                # Notifica Telegram di successo
                invia_notifica_successo_fb(vid_id)
                return True
            else:
                err = res_json.get("error", {})
                err_code = err.get("code", r.status_code)
                err_sub = err.get("error_subcode", "")
                err_msg = err.get("message", r.text)
                
                # Diagnosi specifica del motivo del fallimento
                if err_code == 190:
                    diagnosi = "🔴 *TOKEN SCADUTO O NON VALIDO* (Code 190)\nIl token di accesso Facebook è scaduto oppure è stato revocato."
                elif err_code == 200:
                    diagnosi = "🟠 *PERMESSI INSUFFICIENTI* (Code 200)\nIl token non ha i permessi `pages_manage_posts` o `publish_video` sulla Pagina."
                elif err_code == 100:
                    diagnosi = "🟡 *PARAMETRO O ID NON VALIDO* (Code 100)\nL'ID Pagina fornito non corrisponde o il formato video non è stato accettato."
                else:
                    diagnosi = f"⚠️ *ERRORE GRAPH API* (Code {err_code}, Sub: {err_sub})"
                    
                msg_completo = (
                    f"❌ *MANCATA PUBBLICAZIONE AUTOMATICA SU FACEBOOK*\n\n"
                    f"{diagnosi}\n\n"
                    f"📝 *Dettaglio Meta:* _{err_msg}_\n\n"
                    f"🆔 *Page ID Target:* `{PAGE_ID}`\n\n"
                    f"💡 *Come Correggere:*\n"
                    f"1. Apri *Meta Graph API Explorer*\n"
                    f"2. Seleziona la Pagina *Immobiliare Giancani* in 'User or Page'\n"
                    f"3. Spunta i permessi: `pages_manage_posts`, `pages_read_engagement`, `publish_video`\n"
                    f"4. Clicca *Generate Access Token* e aggiorna il Secret `FACEBOOK_TOKEN` su GitHub."
                )
                print(f"❌ Errore API Video Facebook: {err_msg}", flush=True)
                invia_notifica_errore_fb(msg_completo)
                return False
    except Exception as e:
        msg_exc = f"❌ *Eccezione durante la connessione a Facebook Graph API:*\n`{str(e)}`"
        print(msg_exc, flush=True)
        invia_notifica_errore_fb(msg_exc)
        return False


def invia_notifica_telegram(messaggio_md):
    """Invia tempestivamente su Telegram un avviso di sistema."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": f"{messaggio_md}\n\n━━━━━━━━━━━━━━━━━━━━\n⭐ *Antonio Giancani* ⭐",
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=15, verify=False)
    except Exception:
        pass


def invia_notifica_errore_fb(messaggio_md):
    invia_notifica_telegram(messaggio_md)


def invia_notifica_successo_fb(video_id):
    msg = f"🎉 *VIDEO PUBBLICATO CON SUCCESSO SU FACEBOOK!*\n\n📹 *Video ID:* `{video_id}`\n🌐 Il video Reels è ora online sulla Pagina Facebook."
    invia_notifica_telegram(msg)


# --- 11. PUBBLICAZIONE REELS SU INSTAGRAM GRAPH API ---
def ottieni_instagram_account_id(token, page_id):
    """Rileva l'ID dell'account Instagram Business o Creator collegato alla Pagina Facebook."""
    ig_env = os.environ.get("INSTAGRAM_ACCOUNT_ID")
    if ig_env:
        return ig_env.strip()
    try:
        url = f"https://graph.facebook.com/v19.0/{page_id}?fields=instagram_business_account&access_token={token}"
        r = requests.get(url, timeout=15, verify=False)
        data = r.json()
        if "instagram_business_account" in data and data["instagram_business_account"].get("id"):
            ig_id = data["instagram_business_account"]["id"]
            print(f"  📸 Account Instagram Business collegato rilevato: ID {ig_id}", flush=True)
            return ig_id
    except Exception as e:
        print(f"  ⚠️ Rilevamento Instagram account: {e}", flush=True)
    return None


def pubblica_reels_instagram(video_path, caption):
    """Pubblica automaticamente il video come Reels su Instagram tramite la Graph API di Meta (Resumable Upload)."""
    print("\n🚀 Avvio Pubblicazione Automatica Reels su Instagram...", flush=True)
    
    token_attivo = FACEBOOK_TOKEN
    if not PAGE_ID or not token_attivo:
        print("ℹ️ Pubblicazione Instagram saltata: Token o Page ID non configurati.", flush=True)
        return False
        
    token_da_usare = ottieni_page_token_effettivo(token_attivo, PAGE_ID)
    ig_id = ottieni_instagram_account_id(token_da_usare, PAGE_ID)
    
    if not ig_id:
        msg_no_ig = (
            "ℹ️ *PUBBLICAZIONE INSTAGRAM IN ATTESA DI COLLEGAMENTO*\n\n"
            "Il video è stato pubblicato su Facebook. Per pubblicare automaticamente anche su *Instagram*:\n"
            "1. Accedi a *Meta Business Suite* (o impostazioni della Pagina Facebook).\n"
            "2. Vai su *Impostazioni -> Account collegati -> Instagram*.\n"
            "3. Connetti il tuo profilo Instagram (Business o Creator).\n\n"
            "Non appena collegato, il bot pubblicherà in contemporanea su entrambi i canali!"
        )
        print(f"ℹ️ Nessun account Instagram Business collegato alla Pagina Facebook {PAGE_ID}.", flush=True)
        invia_notifica_telegram(msg_no_ig)
        return False

    try:
        # 1. Inizializzazione container multimediale Resumable per Reels
        url_container = f"https://graph.facebook.com/v19.0/{ig_id}/media"
        file_size = os.path.getsize(video_path)
        
        payload_container = {
            "media_type": "REELS",
            "caption": caption,
            "upload_type": "resumable",
            "access_token": token_da_usare
        }
        res_cont = requests.post(url_container, data=payload_container, timeout=30, verify=False).json()
        
        if "id" not in res_cont or "uri" not in res_cont:
            err_msg = res_cont.get("error", {}).get("message", str(res_cont))
            print(f"❌ Errore creazione container Instagram Reels: {err_msg}", flush=True)
            invia_notifica_telegram(f"⚠️ *Errore Inizializzazione Instagram Reels:*\n_{err_msg}_")
            return False
            
        container_id = res_cont["id"]
        upload_uri = res_cont["uri"]
        print(f"  📦 Container Instagram creato con successo (ID: {container_id})", flush=True)
        
        # 2. Caricamento binario del video
        headers_upload = {
            "Authorization": f"OAuth {token_da_usare}",
            "offset": "0",
            "file_size": str(file_size)
        }
        with open(video_path, "rb") as vf:
            r_upload = requests.post(upload_uri, headers=headers_upload, data=vf, timeout=180, verify=False)
            
        if r_upload.status_code not in [200, 201]:
            print(f"❌ Errore upload dati video su Instagram: {r_upload.text}", flush=True)
            return False
            
        print("  ⬆️ Video trasferito sui server di Instagram. Elaborazione in corso...", flush=True)
        
        # 3. Attesa elaborazione container da parte di Meta
        import time
        pronto = False
        for tentativo in range(15): # max 75 secondi
            time.sleep(5)
            url_status = f"https://graph.facebook.com/v19.0/{container_id}?fields=status_code&access_token={token_da_usare}"
            st_res = requests.get(url_status, timeout=15, verify=False).json()
            stato = st_res.get("status_code")
            if stato == "FINISHED":
                pronto = True
                break
            elif stato == "ERROR":
                print(f"❌ Errore elaborazione interna Instagram: {st_res}", flush=True)
                return False
                
        if not pronto:
            print("⚠️ Timeout elaborazione video su Instagram.", flush=True)
            return False
            
        # 4. Pubblicazione definitiva del Reels su Instagram
        url_publish = f"https://graph.facebook.com/v19.0/{ig_id}/media_publish"
        pub_res = requests.post(url_publish, data={"creation_id": container_id, "access_token": token_da_usare}, timeout=30, verify=False).json()
        
        if "id" in pub_res:
            ig_media_id = pub_res["id"]
            print(f"✅ Video Reels pubblicato con successo su INSTAGRAM! (Media ID: {ig_media_id})", flush=True)
            invia_notifica_telegram(f"🎉 *REELS PUBBLICATO CON SUCCESSO SU INSTAGRAM!*\n\n📸 *Instagram Media ID:* `{ig_media_id}`\n🌐 Il Reels è ora online sul tuo profilo Instagram.")
            return True
        else:
            print(f"❌ Errore pubblicazione Instagram: {pub_res}", flush=True)
            return False
            
    except Exception as e:
        print(f"❌ Eccezione durante pubblicazione Instagram: {e}", flush=True)
        return False


def pubblica_automaticamente_tutto(video_path, caption):
    """Pubblica automaticamente ogni video generato sia su Facebook che su Instagram."""
    print("\n" + "="*60, flush=True)
    print("🚀 AVVIO PUBBLICAZIONE AUTOMATICA (FACEBOOK & INSTAGRAM)", flush=True)
    print("="*60, flush=True)
    
    # 1. Pubblicazione su Pagina Facebook
    fb_ok = pubblica_video_facebook(video_path, caption)
    
    # 2. Pubblicazione su Instagram Reels
    ig_ok = pubblica_reels_instagram(video_path, caption)
    
    return fb_ok or ig_ok


# --- FLUSSO PRINCIPALE ---
async def main():
    print("="*60, flush=True)
    print("🎬 AVVIO BOT VIDEO REELS (PUBBLICAZIONE AUTOMATICA FB & IG)", flush=True)
    print("⭐ Personal Branding: Antonio Giancani", flush=True)
    print("="*60, flush=True)
    
    import argparse
    parser = argparse.ArgumentParser(description="Bot Video Reels da Colonna F con Pubblicazione Automatica FB & IG")
    parser.add_argument("--id", type=str, default=None, help="ID citazione specifico")
    parser.add_argument("--voice", type=str, default="it-IT-DiegoNeural", help="Voce neurale italiana (es. it-IT-DiegoNeural)")
    parser.add_argument("--auto-publish", action="store_true", default=True, help="Pubblicazione automatica attiva (default: True)")
    parser.add_argument("--manual-only", action="store_true", help="Disattiva la pubblicazione automatica e richiede approvazione")
    args = parser.parse_args()
    
    pubblica_in_automatico = not args.manual_only
    voce_selezionata = args.voice
    
    # 1. Estrazione rigorosa da Colonna F
    row = get_random_quote(args.id)
    if not row:
        print("❌ Nessuna riga disponibile nel CSV.")
        return
        
    item_id = row["ID"]
    categoria = row["Categoria"]
    frase = row["Frase"]
    autore = row["Autore"]
    testo_colonna_f = row["Colonna_F"]
    
    print(f"\n--- 🎞️ Elaborazione Reels #{item_id} [{categoria}] ---", flush=True)
    
    # File di output
    bg_file = os.path.join(WORK_DIR, f"bg_{item_id}.jpg")
    frame_file = os.path.join(WORK_DIR, f"frame_{item_id}.png")
    audio_file = os.path.join(WORK_DIR, f"audio_{item_id}.mp3")
    video_file = os.path.join(WORK_DIR, f"reels_mindset_{item_id}.mp4")
    
    # 2. Generazione Sfondo AI tematico
    get_ai_background(categoria, bg_file, seed=int(item_id)*13 + 7)
    
    # 3. Composizione Grafica con Badge e Tipografia Oro
    print("  🖼️ Composizione grafica con badge personalizzato...", flush=True)
    componi_frame_grafico(bg_file, frase, autore, frame_file, categoria=categoria)
    
    # 4. Generazione Micro-Storia Narrata Sincronizzata (Diego racconta una storia mentre sullo schermo si legge la frase)
    storia_vocale = genera_micro_storia(categoria, frase, autore)
    print(f"  🎙️ Narrazione Storytelling ({voce_selezionata}): \"{storia_vocale}\"", flush=True)
    await genera_audio_scena(storia_vocale, audio_file, voce=voce_selezionata)
    
    # 5. Selezione Musica di Sottofondo (CC0 No-Copyright) & Montaggio Video Animato
    musica_bg = scegli_musica_sottofondo(categoria)
    print("  🎥 Rendering video animato in formato Reels 9:16 con mix musicale...", flush=True)
    crea_video_animato(frame_file, audio_file, video_file, bg_music_path=musica_bg)
    print(f"  ✅ Video Reels generato: {video_file} ({round(os.path.getsize(video_file)/1024/1024, 2)} MB)", flush=True)
    
    # 6. Generazione Copy Facebook con Personal Branding Antonio Giancani
    caption_fb = genera_copy_post(row, storia=storia_vocale)
    
    # 7. Invio su Telegram con Bottoni Interattivi
    invia_video_telegram(video_file, caption_fb, item_id)
    
    # 8. Pubblicazione Automatica su Facebook & Instagram ogni volta che viene generato
    if pubblica_in_automatico:
        pubblica_automaticamente_tutto(video_file, caption_fb)
        
    print("\n" + "="*60, flush=True)
    print(f"⭐ VIDEO REELS #{item_id} INVIATO CON SUCCESSO — ANTONIO GIANCANI ⭐", flush=True)
    print("="*60, flush=True)


if __name__ == "__main__":
    asyncio.run(main())
