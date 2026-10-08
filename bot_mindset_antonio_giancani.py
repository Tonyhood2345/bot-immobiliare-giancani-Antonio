#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
======================================================================
  🎬 BOT VIDEO REELS & STORIE (1080x1920) — ANTONIO GIANCANI
  - Sorgente Frasi: Mindset.csv (Rigorosamente da Colonna F)
  - Video Background: Pixabay API (HD / Medium) con Ping-Pong Rewind Loop continuo
  - Voce Narrante: Italiano Neurale Edge-TTS (Lettura & Meditazione profonda)
  - Musica di Sottofondo: Tracce Royalty-Free bilanciate con Ducking (14%)
  - Grafica Premium:
      * Banner Profilo in ALTO con Avatar faccia.png e bordo oro (Video in primo piano)
      * Card Citazione Frosted Glass nel terzo inferiore
  - Palinsesto: Orari liberi da palinsesto live (08:30, 12:30, 16:30)
  - Consegna: Telegram (Chat ID 1723292483) con Approvazione Facebook
  - Regola Mandatoria: Chiusura copy sempre con '— Immobiliare Giancani'
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
import datetime
import subprocess
import requests
import urllib3
import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont
try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs):
        pass

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- 1. CONFIGURAZIONE & AMBIENTE ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY") or "57944902-1332365540ba08b082d67dcdf"
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN") or os.environ.get("AGENCY_TELEGRAM_TOKEN") or "8671578336:AAEHI-s-2g3dY9qnIIVc_hWzDdOuHm-MS6M"
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID") or os.environ.get("MINDSET_CHAT_ID") or "1723292483"

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY") or ""
FACEBOOK_PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID") or "234931856561526"
FACEBOOK_TOKEN = os.environ.get("FACEBOOK_TOKEN") or os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN") or ""

CSV_FILE = os.path.join(BASE_DIR, "Mindset.csv")
LOGO_PATH = os.path.join(BASE_DIR, "faccia.png")
MUSIC_DIR = os.path.join(BASE_DIR, "musica_sottofondo")
TEMP_DIR = os.path.join(BASE_DIR, "temp")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(MUSIC_DIR, exist_ok=True)

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

# Orari ottimali liberi (distanti da 07:00 Storie YouTube e 19:00-01:00 Diretta Streaming)
ORARI_LIBERI = ["08:30", "12:30", "16:30"]

SEARCH_QUERIES = [
    "focus",
    "discipline",
    "running dark",
    "gym workout",
    "sunrise horizon",
    "city timelapse night",
    "luxury office"
]


# --- 2. GESTIONE FONT WINDOWS & SISTEMA ---
def get_font(size, bold=True):
    """Carica un font TrueType pulito con fallback sicuro su Windows e Linux."""
    candidati = [
        os.path.join(BASE_DIR, "assets", "fonts", "Cinzel-Bold.ttf"),
        os.path.join(BASE_DIR, "assets", "fonts", "Lora-Bold.ttf"),
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf" if bold else "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
        "C:/Windows/Fonts/seguisb.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
    ]
    for p in candidati:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


# --- 3. ESTRAZIONE RIGOROSA DA COLONNA F (MINDSET.CSV) ---
def estrai_frase_colonna_f(csv_path=CSV_FILE, id_richiesto=None):
    """
    Legge Mindset.csv ed estrae tassativamente i testi dalla Colonna F (indice 5).
    Filtra righe vuote e seleziona la citazione.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"File CSV non trovato: {csv_path}")

    righe_valide = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        
        for idx, row in enumerate(reader, start=1):
            if not row or len(row) < 3:
                continue
            
            testo_colonna_f = ""
            if len(row) >= 6:
                testo_colonna_f = row[5].strip()
            elif len(row) >= 3:
                testo_colonna_f = f"{row[1].strip()} — {row[2].strip()}"
                
            if not testo_colonna_f:
                continue
                
            righe_valide.append({
                "id": str(row[0]) if len(row) > 0 else str(idx),
                "categoria": row[1].strip() if len(row) > 1 else "Mindset",
                "frase": row[2].strip() if len(row) > 2 else testo_colonna_f,
                "autore": row[3].strip() if len(row) > 3 else "Antonio Giancani",
                "stato": row[4].strip() if len(row) > 4 else "Disponibile",
                "colonna_f": testo_colonna_f
            })

    if not righe_valide:
        raise ValueError("Nessuna riga valida trovata in Mindset.csv.")

    if id_richiesto is not None:
        selezionate = [r for r in righe_valide if str(r["id"]) == str(id_richiesto)]
        if selezionate:
            return selezionate[0]

    scelta = random.choice(righe_valide)
    print(f"📖 [COLONNA F] Citazione selezionata (Riga #{scelta['id']} - {scelta['categoria']}):")
    print(f"   \"{scelta['colonna_f']}\"")
    return scelta


# --- 4. GENERAZIONE MEDITAZIONE & RIFLESSIONE (DIEGO IL SUGGERITORE DI UN'IDEA) ---
def genera_meditazione(categoria, frase, autore):
    """
    Genera un testo vocale interpretato da Diego come 'il suggeritore di un'idea':
    un consigliere intimo, carismatico e riflessivo che sussurra all'ascoltatore un'illuminazione o una prospettiva strategica.
    """
    frase_pulita = frase.strip('“”"\' ')
    cat_pulita = categoria.upper().strip()

    # 1. Tentativo con Gemini AI
    if GEMINI_API_KEY:
        try:
            url_gemini = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
            prompt = (
                f"Sei Diego, la voce narrante confidenziale e ispiratrice per Antonio Giancani nei video Shorts. "
                f"Il tuo ruolo è quello di essere 'il suggeritore di un'idea': non un motivatore aggressivo, "
                f"ma un mentore intimo e profondo che sussurra all'orecchio dell'ascoltatore un'illuminazione o una svolta di pensiero. "
                f"L'argomento è '{cat_pulita}'. La frase guida è: \"{frase_pulita}\" ({autore}). "
                f"Scrivi una riflessione di 24-28 parole che inizi suggerendo un'idea con tono calmo e magnetico "
                f"(ad esempio: 'Ti lascio un'idea...', 'Pensa a questo...', 'E se la vera svolta fosse...', 'Ascolta quest\\'idea...'). "
                f"Il testo deve suonare naturale, elegante e penetrante, come un segreto rivelato. Niente virgolette o emoji."
            )
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            res = requests.post(url_gemini, json=payload, timeout=8, verify=False)
            if res.status_code == 200:
                cand = res.json().get("candidates", [])
                if cand and cand[0].get("content", {}).get("parts"):
                    meditazione_ai = cand[0]["content"]["parts"][0]["text"].strip()
                    if len(meditazione_ai.split()) >= 10:
                        testo_finale = f"{frase_pulita}. {meditazione_ai}"
                        print(f"✨ Idea suggerita da Diego (Gemini AI): \"{meditazione_ai}\"")
                        return testo_finale
        except Exception as e:
            print(f"⚠️ Fallback Gemini: {e}")

    # 2. Fallback offline con stile 'Suggeritore di un'idea'
    meditazioni_archivio = {
        "DISCIPLINA": [
            "Ti lascio un'idea: la disciplina non è una punizione, ma il prezzo della tua libertà futura. Scegli oggi ciò che conta davvero per te.",
            "Pensa a questo: quando l'entusiasmo si spegne, la costanza silenziosa è l'unico vero ponte tra chi sogna e chi realizza.",
            "E se la vera differenza stesse nel fare quella piccola azione difficile, proprio quando non ne hai alcuna voglia? Riflettici."
        ],
        "MINDSET": [
            "Ascolta quest'idea: il mondo non cambia se continui a guardarlo nello stesso modo. Cambia prospettiva, e gli ostacoli diventeranno la tua scala.",
            "Ti lascio una riflessione: non sono gli eventi a definire la tua giornata, ma l'interpretazione che la tua mente sceglie di darne.",
            "Pensa a questo: la realtà che vivi è solo il riflesso delle convinzioni che hai accettato. E se oggi decidessi di puntare più in alto?"
        ],
        "FOCUS": [
            "Ti suggerisco un'idea: in un mondo pieno di rumore, la concentrazione su una sola cosa alla volta è la forma più pura di potere.",
            "Riflettici un istante: ogni volta che dici di sì a una distrazione, stai dicendo di no al tuo obiettivo più importante. Scegli con cura.",
            "E se il segreto fosse eliminare invece di aggiungere? Togli ciò che non serve e guarda quanta forza sprigiona la tua attenzione."
        ],
        "VENDITA": [
            "Ti lascio un'idea diversa sulla vendita: smetti di convincere e inizia ad ascoltare. Quando comprendi davvero, non devi più vendere nulla.",
            "Pensa a questo: le persone non comprano promesse, comprano la certezza e la fiducia che sai trasmettere guardandole negli occhi.",
            "Ascolta: la vendita più importante è quella che fai a te stesso ogni mattina, credendo fino in fondo nel valore che stai portando."
        ],
        "IMMOBILIARE": [
            "Ti suggerisco una prospettiva: una casa non è solo mattoni, è il palcoscenico dove costruisci i ricordi e la serenità della tua famiglia.",
            "Pensa a questo: mentre tutto intorno cambia velocemente, possedere qualcosa di solido sotto i piedi è la vera ancora del tuo futuro.",
            "E se ogni investimento immobiliare fosse prima di tutto un atto di protezione per il tuo domani? Guardalo da questa angolazione."
        ],
        "BUSINESS": [
            "Ti lascio un'idea strategica: le idee valgono poco finché non incontrano il coraggio dell'esecuzione rapida. Decidi e fai il primo passo.",
            "Pensa a questo: la grandezza di un'impresa non sta nell'assenza di problemi, ma nella lucidità con cui li trasformi in opportunità.",
            "Ascolta: l'eccellenza non è un atto isolato, è un'abitudine che coltivi nei dettagli invisibili ogni singolo giorno."
        ]
    }
    opzioni = meditazioni_archivio.get(cat_pulita, meditazioni_archivio["MINDSET"])
    meditazione_scelta = random.choice(opzioni)
    testo_finale = f"{frase_pulita}. {meditazione_scelta}"
    print(f"✨ Idea suggerita da Diego (Archivio): \"{meditazione_scelta}\"")
    return testo_finale


# --- 5. SINTESI VOCALE CON EDGE-TTS (DIEGO NEURAL: SUGGERITORE DI UN'IDEA) ---
async def sintetizza_audio_voce(testo_narrato, output_audio_path, voce="it-IT-DiegoNeural"):
    """Sintetizza la narrazione con voce neurale italiana Diego calibrata (-2% rate per ritmo intimo e riflessivo)."""
    import edge_tts
    print(f"🎙️ Generazione voce Diego narrante (suggeritore di un'idea, voce: {voce})...")
    communicate = edge_tts.Communicate(testo_narrato, voce, rate="-2%", pitch="+0Hz")
    await communicate.save(output_audio_path)
    if not os.path.exists(output_audio_path) or os.path.getsize(output_audio_path) < 1000:
        raise RuntimeError("Errore sintesi vocale: file audio non generato o non valido.")
    print(f"✅ Voce registrata: {output_audio_path} ({round(os.path.getsize(output_audio_path)/1024, 1)} KB)")


def ottieni_durata_file(media_path):
    """Calcola la durata esatta di qualsiasi file audio o video tramite FFmpeg."""
    cmd = [FFMPEG_EXE, "-i", media_path]
    p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    _, stderr = p.communicate()
    for line in stderr.splitlines():
        if "Duration:" in line:
            parts = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = parts.split(":")
            return float(h)*3600 + float(m)*60 + float(s)
    return 8.0


# --- 6. DOWNLOAD CLIP VIDEO VIA PIXABAY API ---
def cerca_e_scarica_clip_pixabay(query=None, video_id=None, temp_dir=TEMP_DIR):
    """
    Cerca e scarica una clip di alta qualità da Pixabay.
    Supporta:
    - video_id o URL diretto di Pixabay (es. 34091 oppure https://pixabay.com/videos/id-34091/)
    - query personalizzata (in italiano o inglese: mare, lusso, skyline, ufficio, tramonto, ecc.)
    - query casuale automatica tra temi di determinazione e mindset
    """
    import re
    if not PIXABAY_API_KEY:
        raise ValueError("PIXABAY_API_KEY mancante nel file .env.")

    url = "https://pixabay.com/api/videos/"

    # 1. Ricerca per ID o Link specifico
    if video_id:
        clean_id_match = re.search(r"(\d+)", str(video_id))
        clean_id = clean_id_match.group(1) if clean_id_match else str(video_id).strip()
        print(f"🎯 [PIXABAY API] Ricerca video specifico per ID: #{clean_id}...")
        params = {"key": PIXABAY_API_KEY, "id": clean_id}
        res = requests.get(url, params=params, verify=False, timeout=20)
        data = res.json()
        hits = data.get("hits", [])
        if hits:
            clip_scelta = hits[0]
            query_usata = f"Video #{clean_id} ({clip_scelta.get('tags', 'custom')})"
        else:
            print(f"⚠️ Video #{clean_id} non trovato su Pixabay. Procedo con ricerca per tema...")
            video_id = None

    # 2. Ricerca per parola chiave / tema
    if not video_id:
        query_scelta = query or random.choice(SEARCH_QUERIES)
        print(f"🔍 [PIXABAY API] Ricerca clip video per tema: '{query_scelta}'...")
        params = {
            "key": PIXABAY_API_KEY,
            "q": query_scelta,
            "video_type": "all",
            "per_page": 20
        }

        try:
            res = requests.get(url, params=params, verify=False, timeout=20)
            res.raise_for_status()
            data = res.json()
        except Exception:
            params["q"] = "focus"
            res = requests.get(url, params=params, verify=False, timeout=20)
            res.raise_for_status()
            data = res.json()

        hits = data.get("hits", [])
        if not hits:
            raise RuntimeError(f"Nessun video trovato su Pixabay per '{query_scelta}'.")

        random.shuffle(hits)
        clip_scelta = hits[0]
        query_usata = query_scelta

    # Estrazione URL del formato video (medium / large / small)
    videos = clip_scelta.get("videos", {})
    video_url = None
    for fmt in ["medium", "large", "small"]:
        if fmt in videos and videos[fmt].get("url"):
            video_url = videos[fmt]["url"]
            break

    if not video_url:
        raise RuntimeError("Nessun URL video valido nei risultati Pixabay.")

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_clip_path = os.path.join(temp_dir, f"raw_clip_{timestamp}.mp4")

    print(f"⬇️ Download clip Pixabay #{clip_scelta.get('id')} ({clip_scelta.get('duration')}s) - Tag: {clip_scelta.get('tags')}...")
    with requests.get(video_url, stream=True, verify=False, timeout=45) as r:
        r.raise_for_status()
        with open(temp_clip_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=65536):
                if chunk:
                    f.write(chunk)

    print(f"✅ Clip grezza salvata: {temp_clip_path} ({round(os.path.getsize(temp_clip_path)/(1024*1024), 2)} MB)")
    return temp_clip_path, query_usata


# --- 7. COMPOSIZIONE GRAFICA D'ELITE: SCRITTA IN ALTO & BANNER IN BASSO ---
def genera_overlay_grafico(categoria, frase, autore, output_png_path):
    """
    Crea un frame PNG trasparente a 1080x1920 con:
    - CARD CITAZIONE IN ALTO (Y: 90 - ~550):
        * Card Frosted Glass con bordo oro (#FFD700)
        * Categoria in oro, testo da Colonna F bianco con ombra, autore in oro
    - CENTRO DELLO SCHERMO COMPLETAMENTE LIBERO (Y: ~550 - 1650):
        * Oltre 1000px liberi per dare massimo risalto e primo piano all'azione scenica del video!
    - BANNER PROFILO IN BASSO (Y: 1660 - 1820):
        * Avatar reale faccia.png con maschera circolare antialias e bordo oro
        * Nome 'Antonio Giancani' e tagline 'MINDSET • STRATEGIA • CRESCITA'
    """
    W, H = 1080, 1920
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    font_name = get_font(36, bold=True)
    font_sub = get_font(21, bold=False)
    font_cat = get_font(32, bold=True)
    font_author = get_font(30, bold=True)

    card_left = 60
    card_right = W - 60

    # 1. CARD CITAZIONE IN ALTO
    frase_pulita = frase.strip().strip('"').strip('“').strip('”')
    if len(frase_pulita) > 120:
        font_size = 38
        line_w = 26
        line_h = 52
    elif len(frase_pulita) > 70:
        font_size = 44
        line_w = 24
        line_h = 58
    else:
        font_size = 50
        line_w = 22
        line_h = 66

    font_quote = get_font(font_size, bold=True)
    lines = textwrap.wrap(f"“{frase_pulita}”", width=line_w)

    h_quote = len(lines) * line_h + 160
    q_top = 90
    q_bottom = q_top + h_quote

    # Card frosted glass per la citazione in alto
    draw.rounded_rectangle(
        [(card_left, q_top), (card_right, q_bottom)],
        radius=34,
        fill=(10, 15, 24, 225),
        outline="#FFD700",
        width=3
    )

    # Categoria in Oro
    draw.text((W // 2, q_top + 40), f"◆ {categoria.upper()} ◆", font=font_cat, fill="#FFD700", anchor="mt")

    # Righe Frase
    curr_y = q_top + 115
    for l in lines:
        draw.text((W // 2 + 2, curr_y + 2), l, font=font_quote, fill=(0, 0, 0, 180), anchor="mt")
        draw.text((W // 2, curr_y), l, font=font_quote, fill="#FFFFFF", anchor="mt")
        curr_y += line_h

    # Autore Citazione
    curr_y += 15
    draw.text((W // 2, curr_y), f"— {autore} —", font=font_author, fill="#FFD700", anchor="mt")

    # 2. BANNER PROFILO IN BASSO
    banner_h = 160
    banner_y = H - banner_h - 100  # Y: 1660 a 1820 (zona protetta sopra bordo inferiore)

    draw.rounded_rectangle(
        [(card_left, banner_y), (card_right, banner_y + banner_h)],
        radius=30,
        fill=(10, 15, 24, 225),
        outline="#FFD700",
        width=2
    )

    # Avatar circolare faccia.png
    avatar_size = 116
    avatar_x = card_left + 22
    avatar_y = banner_y + (banner_h - avatar_size) // 2

    if os.path.exists(LOGO_PATH):
        try:
            face_img = Image.open(LOGO_PATH).convert("RGBA").resize((avatar_size, avatar_size), Image.Resampling.LANCZOS)
            mask = Image.new("L", (avatar_size, avatar_size), 0)
            dmask = ImageDraw.Draw(mask)
            dmask.ellipse((0, 0, avatar_size, avatar_size), fill=255)
            overlay.paste(face_img, (avatar_x, avatar_y), mask)
            # Anello dorato intorno all'avatar
            draw.ellipse((avatar_x - 2, avatar_y - 2, avatar_x + avatar_size + 2, avatar_y + avatar_size + 2), outline="#FFD700", width=3)
        except Exception as e:
            print(f"⚠️ Errore caricamento avatar faccia: {e}")

    # Testi nel Banner in Basso
    text_x = avatar_x + avatar_size + 24
    draw.text((text_x, banner_y + 40), "Antonio Giancani", font=font_name, fill="#FFFFFF")
    draw.text((text_x, banner_y + 90), "MINDSET • STRATEGIA • CRESCITA", font=font_sub, fill="#FFD700")

    overlay.save(output_png_path, "PNG")
    print(f"🎨 Overlay d'elite generato (Scritta in ALTO, Banner in BASSO): {output_png_path}")
    return output_png_path


# --- 8. SELEZIONE MUSICA DI SOTTOFONDO ROYALTY-FREE ---
def scegli_musica_sottofondo():
    """Seleziona una traccia royalty-free da musica_sottofondo con fallback sicuro."""
    tracce = [
        os.path.join(MUSIC_DIR, f)
        for f in os.listdir(MUSIC_DIR)
        if f.endswith((".mp3", ".wav")) and os.path.getsize(os.path.join(MUSIC_DIR, f)) > 5000
    ]
    if tracce:
        scelta = random.choice(tracce)
        print(f"🎶 Musica selezionata: {os.path.basename(scelta)}")
        return scelta
    return None


# --- 9. MONTAGGIO VIDEO CON LOOP IN REWIND (PING-PONG CONTINUO) ---
def monta_video_story_completo(raw_clip_path, overlay_png_path, audio_voce_path, output_video_path, bg_music_path=None):
    """
    Combina:
    - Clip video Pixabay con PING-PONG REWIND LOOP (se la clip è più corta della voce,
      va avanti e poi in reverse all'infinito, creando un loop fluido e continuo senza tagli)
    - Filtro di scurimento e contrasto
    - Overlay grafico PIL (Banner in alto + video in primo piano)
    - Traccia vocale Diego Neural
    - Traccia musicale di sottofondo ducked (volume 14%)
    """
    durata_clip = ottieni_durata_file(raw_clip_path)
    durata_voce = ottieni_durata_file(audio_voce_path)
    durata_totale = round(durata_voce + 1.2, 1)

    fade_out_st = max(0.5, durata_totale - 1.5)

    print(f"⏱️ Durata clip originale: {durata_clip}s | Durata narrazione vocale: {durata_totale}s")

    # Verifica se la clip è più breve del tempo totale richiesto
    serve_rewind_loop = (durata_clip < durata_totale)
    if serve_rewind_loop:
        print(f"🔄 [PING-PONG REWIND LOOP ATTIVATO] La clip dura {durata_clip}s (< {durata_totale}s).")
        print("   Applicazione loop continuo: avanti -> reverse -> avanti per un flusso visivo fluido e ininterrotto!")
        
        frames_clip = max(1, int(durata_clip * 30))
        cycle_frames = frames_clip * 2

        video_filter = (
            "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,"
            "eq=brightness=-0.14:contrast=1.06[v_scaled];"
            "[v_scaled]split[v_fwd][v_rev_in];"
            "[v_rev_in]reverse[v_rev];"
            "[v_fwd][v_rev]concat=n=2:v=1:a=0[v_cycle];"
            f"[v_cycle]loop=loop=-1:size={cycle_frames}:start=0[vbg];"
            "[vbg][1:v]overlay=0:0[vout]"
        )
    else:
        print("▶️ Clip sufficientemente lunga, riproduzione standard in avanti.")
        video_filter = (
            "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30,"
            "eq=brightness=-0.14:contrast=1.06[vbg];"
            "[vbg][1:v]overlay=0:0[vout]"
        )

    if bg_music_path and os.path.exists(bg_music_path):
        filter_complex = (
            f"[0:v]{video_filter};"
            "[2:a]volume=1.0[voice];"
            f"[3:a]volume=0.14,afade=t=in:ss=0:d=1.0,afade=t=out:st={fade_out_st:.2f}:d=1.5[music];"
            "[voice][music]amix=inputs=2:duration=first:dropout_transition=2[aout]"
        )
        cmd = [
            FFMPEG_EXE, "-y",
            "-ss", "0", "-i", raw_clip_path,
            "-i", overlay_png_path,
            "-i", audio_voce_path,
            "-i", bg_music_path,
            "-filter_complex", filter_complex,
            "-map", "[vout]", "-map", "[aout]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-t", str(durata_totale),
            output_video_path
        ]
    else:
        filter_complex = (
            f"[0:v]{video_filter};"
            "[2:a]volume=1.0[aout]"
        )
        cmd = [
            FFMPEG_EXE, "-y",
            "-ss", "0", "-i", raw_clip_path,
            "-i", overlay_png_path,
            "-i", audio_voce_path,
            "-filter_complex", filter_complex,
            "-map", "[vout]", "-map", "[aout]",
            "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k",
            "-t", str(durata_totale),
            output_video_path
        ]

    print(f"🎬 Avvio montaggio FFmpeg (1080x1920 @ 30fps, durata: {durata_totale}s)...")
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        err = res.stderr[-800:] if res.stderr else "Errore sconosciuto FFmpeg"
        raise RuntimeError(f"FFmpeg fallito:\n{err}")

    mb = round(os.path.getsize(output_video_path)/(1024*1024), 2)
    print(f"✅ Video definitivo renderizzato: {output_video_path} ({mb} MB)")
    return True


# --- 10. GESTIONE ORARI LIBERI DA PALINSESTO ---
def ottieni_prossimo_orario_libero():
    """
    Calcola la prossima finestra oraria ottimale priva di conflitti
    (distante da 07:00 storie YouTube e 19:00-01:00 diretta streaming serale).
    """
    now = datetime.datetime.now()
    orari_dt = []
    for h_str in ORARI_LIBERI:
        h, m = map(int, h_str.split(":"))
        dt = now.replace(hour=h, minute=m, second=0, microsecond=0)
        if dt > now:
            orari_dt.append(dt)

    if not orari_dt:
        h, m = map(int, ORARI_LIBERI[0].split(":"))
        prossimo = (now + datetime.timedelta(days=1)).replace(hour=h, minute=m, second=0, microsecond=0)
    else:
        prossimo = min(orari_dt)

    minuti_attesa = int((prossimo - now).total_seconds() // 60)
    return prossimo.strftime("%H:%M"), minuti_attesa


# --- 11. INVIO SU TELEGRAM CON APPROVAZIONE FACEBOOK ---
def invia_video_telegram(video_path, item, query_usata, orario_suggerito):
    """
    Invia il video a Telegram con didascalia completa e bottoni interattivi.
    Rispetta rigorosamente la chiusura '— Immobiliare Giancani'.
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Credenziali Telegram mancanti, invio saltato.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
    item_id = item.get("id", "0")

    caption = (
        f"🎬 *NUOVO VIDEO SHORTS / STORIES (1080x1920)*\n"
        f"⭐ *ANTONIO GIANCANI*\n\n"
        f"🏷️ *Categoria:* #{item.get('categoria', 'Mindset')}\n"
        f"📖 *Frase (Colonna F):*\n_{item.get('colonna_f', '')}_\n\n"
        f"🎙️ *Voce:* Diego Neurale (Lettura & Meditazione)\n"
        f"🎵 *Audio:* Musica di sottofondo Royalty-Free\n"
        f"🖼️ *Layout:* Scritta in ALTO, Banner in BASSO (Centro libero per il video)\n"
        f"🔄 *Effetto Video:* Loop in Rewind Continuo (Nessun salto visivo)\n"
        f"⏰ *Fascia Oraria Consigliata:* {orario_suggerito} (Libera da live)\n\n"
        f"🔒 *Stato Facebook:* Pronto e in attesa del tuo OK\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"— Immobiliare Giancani"
    )

    inline_keyboard = {
        "inline_keyboard": [
            [
                {"text": "✅ APPROVA PER PUBBLICAZIONE SU FACEBOOK", "callback_data": f"APPROVA_FB_{item_id}"}
            ],
            [
                {"text": "🔄 RIGENERA CON ALTRA CLIP", "callback_data": f"RIGENERA_{item_id}"},
                {"text": "❌ SCARTA", "callback_data": f"SCARTA_{item_id}"}
            ]
        ]
    }

    with open(video_path, "rb") as vf:
        files = {"video": vf}
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "caption": caption,
            "parse_mode": "Markdown",
            "reply_markup": json.dumps(inline_keyboard)
        }
        res = requests.post(url, data=data, files=files, timeout=120, verify=False)

    if res.status_code == 200:
        print("✅ Video consegnato con successo su Telegram!")
        return True
    else:
        print(f"❌ Errore invio Telegram ({res.status_code}): {res.text}")
        return False


def invia_notifica_telegram(messaggio_md):
    """Invia un messaggio di notifica su Telegram."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": f"{messaggio_md}\n\n━━━━━━━━━━━━━━━━━━━━\n— Immobiliare Giancani",
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=15, verify=False)
    except Exception:
        pass


# --- 12. PUBBLICAZIONE FACEBOOK GRAPH API ---
def pubblica_su_facebook(video_path, caption):
    """Pubblica automaticamente il video sulla Pagina Facebook."""
    print(f"🚀 [FACEBOOK] Pubblicazione automatica del video sulla Pagina ID: {FACEBOOK_PAGE_ID}...")
    if not FACEBOOK_PAGE_ID or not FACEBOOK_TOKEN:
        print("❌ Impossibile pubblicare su Facebook: token o Page ID mancante.")
        return False

    url = f"https://graph.facebook.com/v19.0/{FACEBOOK_PAGE_ID}/videos"
    try:
        with open(video_path, "rb") as vf:
            files = {"source": (os.path.basename(video_path), vf)}
            data = {"description": caption, "access_token": FACEBOOK_TOKEN}
            r = requests.post(url, files=files, data=data, timeout=180, verify=False)
            res = r.json()
            if r.status_code == 200 and "id" in res:
                video_id = res['id']
                print(f"🎉 Video pubblicato con successo su FACEBOOK! ID: {video_id}")
                msg_tg = (
                    f"🎉 *VIDEO PUBBLICATO CON SUCCESSO SU FACEBOOK!*\n\n"
                    f"📹 *Video ID:* `{video_id}`\n"
                    f"🌐 Il video Reels / Shorts è ora online sulla Pagina Facebook."
                )
                invia_notifica_telegram(msg_tg)
                return True
            else:
                print(f"❌ Errore pubblicazione Facebook: {res}")
                return False
    except Exception as e:
        print(f"❌ Eccezione Facebook: {e}")
        return False


# --- 13. PULIZIA FILE TEMPORANEI ---
def pulisci_cartella_temp(temp_dir=TEMP_DIR):
    """Rimuove tutti i file temporanei grezzi in ./temp/."""
    print("🧹 Pulizia file temporanei ./temp/...")
    if not os.path.exists(temp_dir):
        return
    for f in os.listdir(temp_dir):
        p = os.path.join(temp_dir, f)
        try:
            if os.path.isfile(p):
                os.remove(p)
        except Exception:
            pass


# --- 14. FLUSSO PRINCIPALE COMPLETO ---
async def genera_video_potenziato(id_richiesto=None, query_pexels=None, video_id=None, publish_fb=True):
    """Esegue l'intero ciclo di generazione potenziata con pubblicazione automatica su Facebook."""
    print("=" * 70)
    print("🎬 AVVIO BOT SHORTS / STORIES — ANTONIO GIANCANI (AUTOMATICO)")
    print("⭐ Scritta in Alto + Diego Suggeritore + Video in Primo Piano + Facebook Online")
    print("=" * 70)

    # 1. Estrazione da Colonna F
    item = estrai_frase_colonna_f(CSV_FILE, id_richiesto=id_richiesto)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    temp_clip_path = None

    try:
        # 2. Generazione testo e voce di Diego narrante (suggeritore di un'idea)
        testo_narrato = genera_meditazione(item["categoria"], item["frase"], item["autore"])
        temp_audio_path = os.path.join(TEMP_DIR, f"voice_{timestamp}.mp3")
        await sintetizza_audio_voce(testo_narrato, temp_audio_path, voce="it-IT-DiegoNeural")

        # 3. Download clip da Pixabay API (tramite tema oppure ID/Link specifico)
        temp_clip_path, query_usata = cerca_e_scarica_clip_pixabay(query=query_pexels, video_id=video_id, temp_dir=TEMP_DIR)

        # 4. Generazione Overlay Grafico con Scritta in ALTO e Banner Profilo in BASSO
        temp_overlay_path = os.path.join(TEMP_DIR, f"overlay_{timestamp}.png")
        genera_overlay_grafico(item["categoria"], item["frase"], item["autore"], temp_overlay_path)

        # 5. Selezione Musica Royalty-Free
        bg_music = scegli_musica_sottofondo()

        # 6. Montaggio Video Definitivo con Loop in Rewind se necessario
        output_filename = f"story_giancani_{timestamp}.mp4"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        monta_video_story_completo(temp_clip_path, temp_overlay_path, temp_audio_path, output_path, bg_music_path=bg_music)

        # 7. Calcolo prossimo orario libero
        prossimo_slot, minuti = ottieni_prossimo_orario_libero()
        print(f"⏰ Orario libero da palinsesto live: {prossimo_slot} (tra {minuti} min)")

        # 8. Invio immediato su Telegram per archivio e notifica
        invia_video_telegram(output_path, item, query_usata, prossimo_slot)

        # 9. Pubblicazione Automatica su Facebook
        if publish_fb:
            print("\n🚀 Avvio pubblicazione automatica su Facebook in corso...")
            copy_fb = (
                f"💎 {item.get('categoria', 'MINDSET').upper()} DEL GIORNO 💎\n\n"
                f"«{item['frase']}»\n"
                f"— {item['autore']} —\n\n"
                f"🎙️ {testo_narrato}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"👉 Riflessione a cura di:\n"
                f"⭐ ANTONIO GIANCANI ⭐\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"— Immobiliare Giancani"
            )
            pubblica_su_facebook(output_path, copy_fb)
        else:
            print("\n🔒 Pubblicazione Facebook disattivata via parametro.")

        return output_path

    finally:
        # 10. Pulizia cartella temp
        pulisci_cartella_temp(TEMP_DIR)
        print("=" * 70)
        print("🏁 PROCESSO COMPLETATO CON SUCCESSO — Immobiliare Giancani")
        print("=" * 70)


def loop_orari_liberi():
    """
    Esegue il bot ad anello sincronizzato sugli orari liberi:
    08:30, 12:30, 16:30 ogni giorno.
    """
    print("=" * 70)
    print("⏰ AVVIO SCHEDULER ORARI LIBERI: 08:30 | 12:30 | 16:30")
    print("=" * 70)
    while True:
        now = datetime.datetime.now()
        ora_corrente = now.strftime("%H:%M")
        
        if ora_corrente in ORARI_LIBERI and now.second < 30:
            print(f"\n🎯 [ORARIO LIBERO SCATTATO: {ora_corrente}] Generazione e pubblicazione automatica video...")
            asyncio.run(genera_video_potenziato(publish_fb=True))
            time.sleep(60)
        
        time.sleep(15)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Bot Video Shorts/Stories Antonio Giancani (Automatico su Facebook)")
    parser.add_argument("--id", type=str, default=None, help="ID citazione specifico da Mindset.csv")
    parser.add_argument("--query", "--tema", type=str, default=None, help="Tema o parola chiave del video su Pixabay (es. mare, lusso, skyline)")
    parser.add_argument("--video-id", "--url", type=str, default=None, help="ID o Link specifico del video da Pixabay")
    parser.add_argument("--no-publish-fb", "--solo-telegram", action="store_true", help="Invia solo su Telegram senza pubblicare su Facebook")
    parser.add_argument("--auto-publish", action="store_true", default=True, help="Pubblicazione automatica su Facebook (attiva di default)")
    parser.add_argument("--schedule", action="store_true", help="Attiva demone scheduler sugli orari liberi (08:30, 12:30, 16:30)")

    args = parser.parse_args()
    pubblica_fb = not args.no_publish_fb

    if args.schedule:
        loop_orari_liberi()
    else:
        asyncio.run(genera_video_potenziato(
            id_richiesto=args.id,
            query_pexels=args.query,
            video_id=args.video_id,
            publish_fb=pubblica_fb
        ))
