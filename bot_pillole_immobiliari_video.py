#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
======================================================================
  🏛️ BOT VIDEO PILLOLE IMMOBILIARI & LEGALI (1080x1920) — IMMOBILIARE GIANCANI
  - Sorgente Testi: database_pillole_immobiliari_legali.csv (Rigorosamente Colonna F)
  - Alternanza Automatica: 4 Post Video Reel : 1 Post Immagine Curata
  - Video Footage: Pixabay / Pexels API (Iper-contestuale: Rogito, Catasto, Mutui, Ville)
  - Voce Neurale Studio Broadcast: it-IT-IsabellaNeural con filtro calore e nitidezza
  - Musica di Sottofondo: Royalty-Free bilanciata con Ducking (14%)
  - Consegna: Telegram (Chat ID 1723292483) con copy personalizzato
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
from PIL import Image, ImageDraw, ImageFont, ImageFilter
try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs):
        pass

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- 1. CONFIGURAZIONE & PERCORSI ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY") or "57944902-1332365540ba08b082d67dcdf"
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY") or ""
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN") or os.environ.get("AGENCY_TELEGRAM_TOKEN") or "8671578336:AAEHI-s-2g3dY9qnIIVc_hWzDdOuHm-MS6M"
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID") or os.environ.get("MINDSET_CHAT_ID") or "1723292483"
FACEBOOK_PAGE_ID = os.environ.get("FACEBOOK_PAGE_ID_GIANCANI") or os.environ.get("FACEBOOK_PAGE_ID") or "234931856561526"
FACEBOOK_TOKEN = os.environ.get("FACEBOOK_TOKEN") or os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN") or ""

CSV_FILE = os.path.join(BASE_DIR, "database_pillole_immobiliari_legali.csv")
ROTATION_FILE = os.path.join(BASE_DIR, "stato_rotazione_pillole.json")
CURATED_ASSETS_DIR = os.path.join(BASE_DIR, "assets", "pillole_scene_curated")
LOGO_PATH = os.path.join(BASE_DIR, "assets", "logo_giancani_trasparente.png")
if not os.path.exists(LOGO_PATH):
    LOGO_PATH = os.path.join(BASE_DIR, "faccia.png")

MUSIC_DIR = os.path.join(BASE_DIR, "musica_sottofondo")
TEMP_DIR = os.path.join(BASE_DIR, "temp")
OUTPUT_DIR = os.path.join(BASE_DIR, "video_storie_output")

os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(MUSIC_DIR, exist_ok=True)

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()

# --- 2. MAPPATURA IPER-CONTESTUALE DELLE 10 PILLOLE (GEMINI.md REGOLA 1) ---
MAPPATURA_CONTESTUALE = {
    "1": {
        "queries_pixabay": ["signing document pen", "contract", "notary signing contract", "lawyer contract desk"],
        "queries_pexels": ["signing contract pen", "notary deed signing", "real estate closing documents"],
        "icona": "🖋️",
        "tema_visivo": "Firma Rogito Notarile e Registri"
    },
    "2": {
        "queries_pixabay": ["architect blueprint", "architectural floorplan", "blueprint", "drafting table"],
        "queries_pexels": ["architect blueprint plan", "architect drawing blueprint", "floor plan house"],
        "icona": "📐",
        "tema_visivo": "Planimetria Catastale e Progetto Tecnico"
    },
    "3": {
        "queries_pixabay": ["calculator money finance", "financial calculation desk", "bank loan", "finance paperwork"],
        "queries_pexels": ["mortgage calculation finance", "tax documents calculator", "finance consultation"],
        "icona": "💰",
        "tema_visivo": "Consulenza Mutuo e Agevolazioni Fiscali"
    },
    "4": {
        "queries_pixabay": ["business agreement handshake", "real estate handshake", "signing contract handshake"],
        "queries_pexels": ["business handshake deal", "real estate contract handshake", "handshake agreement"],
        "icona": "🤝",
        "tema_visivo": "Caparra Confirmatoria e Accordo Formale"
    },
    "5": {
        "queries_pixabay": ["modern luxury house", "contemporary home", "luxury house exterior", "architecture villa"],
        "queries_pexels": ["modern eco architecture home", "luxury modern villa exterior", "energy efficient architecture"],
        "icona": "⚡",
        "tema_visivo": "Attestato Energetico ed Edificio di Pregio"
    },
    "6": {
        "queries_pixabay": ["notary lawyer meeting", "legal consultation office", "business meeting desk", "lawyer"],
        "queries_pexels": ["notary legal consultation", "lawyer discussion office", "property legal deed"],
        "icona": "📜",
        "tema_visivo": "Tutela Legale e Atto Notarile di Donazione"
    },
    "7": {
        "queries_pixabay": ["official stamp document", "contract signing desk", "formal business agreement", "contract"],
        "queries_pexels": ["official deed signing", "contract agreement registration", "signing papers desk"],
        "icona": "📑",
        "tema_visivo": "Trascrizione Preliminare nei Registri"
    },
    "8": {
        "queries_pixabay": ["luxury classic house", "prestigious residence", "historic mansion villa", "luxury house"],
        "queries_pexels": ["prestigious estate house", "historic luxury estate", "real estate classic property"],
        "icona": "🏛️",
        "tema_visivo": "Continuità delle Trascrizioni e Proprietà"
    },
    "9": {
        "queries_pixabay": ["bank advisor meeting", "signing bank documents", "mortgage loan desk", "contract"],
        "queries_pexels": ["bank advisor mortgage meeting", "signing bank loan papers", "financial advisor loan"],
        "icona": "🏦",
        "tema_visivo": "Clausola Sospensiva e Approvazione Mutuo"
    },
    "10": {
        "queries_pixabay": ["modern condominium apartment", "apartment building exterior", "residential complex drone"],
        "queries_pexels": ["modern apartment building drone", "residential architecture complex", "condominium exterior"],
        "icona": "🏢",
        "tema_visivo": "Complesso Condominiale e Liberatoria Spese"
    },
    "11": {
        "queries_pixabay": ["house inspection survey", "architect inspecting building", "engineer building structure"],
        "queries_pexels": ["property inspection engineer", "architect inspecting house", "building survey inspection"],
        "icona": "🔍",
        "tema_visivo": "Perizia Tecnica e Verifica Vizi Occulti"
    },
    "12": {
        "queries_pixabay": ["modern living room luxury", "contemporary architecture villa", "luxury apartment interior"],
        "queries_pexels": ["modern luxury living room interior", "contemporary luxury villa", "bright architectural interior"],
        "icona": "🏠",
        "tema_visivo": "Certificato di Agibilità e Spazi a Norma"
    },
    "13": {
        "queries_pixabay": ["countryside estate villa", "vineyard luxury estate", "italian countryside villa", "olive grove"],
        "queries_pexels": ["countryside villa landscape", "italian estate vineyard", "prestigious country property"],
        "icona": "🌾",
        "tema_visivo": "Terreni Agricoli e Prelazione Confinanti"
    },
    "14": {
        "queries_pixabay": ["handing keys real estate", "signing rental lease agreement", "meeting keys handshake"],
        "queries_pexels": ["handing over keys house", "real estate rental contract", "signing lease deal"],
        "icona": "🔑",
        "tema_visivo": "Immobile a Reddito e Subentro Contrattuale"
    },
    "15": {
        "queries_pixabay": ["tax calculation money finance", "luxury house paperwork", "notary signing desk", "calculator"],
        "queries_pexels": ["financial tax calculation papers", "real estate tax paperwork", "finance consultation desk"],
        "icona": "📊",
        "tema_visivo": "Regola del Prezzo-Valore e Risparmio Fiscale"
    }
}


# --- 3. GESTIONE FONT ELEGANTE CON FALLBACK ROBUSTO ---
def get_font(size, bold=True):
    """Carica font TrueType prestigioso (Cinzel, Lora, Arial, Calibri)."""
    candidati = [
        os.path.join(BASE_DIR, "assets", "fonts", "Cinzel-Bold.ttf") if bold else os.path.join(BASE_DIR, "assets", "fonts", "Lora-Bold.ttf"),
        os.path.join(BASE_DIR, "assets", "fonts", "PlayfairDisplay-Bold.ttf"),
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibrib.ttf" if bold else "C:/Windows/Fonts/calibri.ttf",
        "C:/Windows/Fonts/seguisb.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf" if bold else "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ]
    for p in candidati:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


# --- 4. GESTIONE STATO DI ROTAZIONE 4 VIDEO : 1 IMMAGINE ---
def carica_o_inizializza_stato():
    """Legge lo stato della rotazione dal file JSON o lo inizializza se mancante."""
    if os.path.exists(ROTATION_FILE):
        try:
            with open(ROTATION_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data
        except Exception:
            pass
    return {
        "ultimo_id": 0,
        "conteggio_ciclo": 0,
        "totale_generati": 0,
        "totale_video": 0,
        "totale_immagini": 0,
        "storico": []
    }


def aggiorna_stato_rotazione(id_usato, formato_usato, titolo_pillola):
    """Aggiorna il ciclo 1..5 e memorizza l'ID utilizzato."""
    stato = carica_o_inizializza_stato()
    conteggio = (stato.get("conteggio_ciclo", 0) % 5) + 1
    stato["ultimo_id"] = int(id_usato)
    stato["conteggio_ciclo"] = conteggio
    stato["totale_generati"] = stato.get("totale_generati", 0) + 1
    if formato_usato == "video":
        stato["totale_video"] = stato.get("totale_video", 0) + 1
    else:
        stato["totale_immagini"] = stato.get("totale_immagini", 0) + 1

    stato["ultimo_titolo"] = titolo_pillola
    stato["ultima_data"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(ROTATION_FILE, "w", encoding="utf-8") as f:
        json.dump(stato, f, indent=2, ensure_ascii=False)
    return conteggio


# --- 5. ESTRAZIONE DATI RIGOROSA DA COLONNA F ---
def estrai_pillola_colonna_f(csv_path=CSV_FILE, id_richiesto=None, forza_formato=None):
    """
    Legge database_pillole_immobiliari_legali.csv ed estrae tassativamente
    il testo da Colonna F (indice 5).
    Determina il formato (video o immagine) secondo la rotazione 4:1.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Database pillole non trovato: {csv_path}")

    righe_valide = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        for idx, row in enumerate(reader, start=1):
            if not row or len(row) < 4:
                continue

            testo_colonna_f = ""
            if len(row) >= 6:
                testo_colonna_f = row[5].strip()
            elif len(row) >= 3:
                testo_colonna_f = f"{row[1].strip()}: {row[2].strip()}"

            if not testo_colonna_f:
                continue

            righe_valide.append({
                "id": str(row[0]).strip() if len(row) > 0 else str(idx),
                "categoria": row[1].strip() if len(row) > 1 else "Diritto Immobiliare",
                "titolo": row[2].strip() if len(row) > 2 else "Consulenza Immobiliare",
                "normativa": row[3].strip() if len(row) > 3 else "Codice Civile",
                "orario": row[4].strip() if len(row) > 4 else "06:00",
                "colonna_f": testo_colonna_f
            })

    if not righe_valide:
        raise ValueError("Nessuna riga valida trovata in database_pillole_immobiliari_legali.csv.")

    stato = carica_o_inizializza_stato()
    ultimo_id = stato.get("ultimo_id", 0)
    conteggio_ciclo = stato.get("conteggio_ciclo", 0)

    # Scelta ID: se specificato usiamo quello, altrimenti sequenziale continuo
    if id_richiesto is not None:
        selezionate = [r for r in righe_valide if str(r["id"]) == str(id_richiesto)]
        scelta = selezionate[0] if selezionate else righe_valide[0]
    else:
        # Trova la prossima riga ciclica
        prossimo_idx = (ultimo_id % len(righe_valide))
        scelta = righe_valide[prossimo_idx]

    # Determinazione formato 4:1
    prossimo_step_ciclo = (conteggio_ciclo % 5) + 1
    if forza_formato:
        formato = forza_formato.lower()
    else:
        # Step 1, 2, 3, 4 -> VIDEO; Step 5 -> IMMAGINE
        formato = "immagine" if prossimo_step_ciclo == 5 else "video"

    scelta["step_ciclo"] = prossimo_step_ciclo
    scelta["formato"] = formato

    print(f"🏛️ [COLONNA F] Pillola #{scelta['id']} selezionata: '{scelta['titolo']}'")
    print(f"📜 Normativa: {scelta['normativa']} | Categoria: {scelta['categoria']}")
    print(f"🔄 Cadenza Rotazione 4:1: Step {prossimo_step_ciclo}/5 ➔ Formato: {formato.upper()}")
    print(f"📝 Testo recitato (Colonna F): \"{scelta['colonna_f']}\"")
    return scelta


# --- 6. SINTESI VOCALE CON FILTRO STUDIO BROADCAST ---
async def sintetizza_audio_studio(testo, output_path, voce="it-IT-IsabellaNeural", rate="-3%"):
    """
    Sintetizza la voce con Edge-TTS e applica una catena di filtri audio FFmpeg
    per ricreare il calore, la presenza e l'autorevolezza di uno studio broadcast:
    - Highpass 80Hz (taglio rimbombi)
    - Lowpass 12kHz (morbidezza alte frequenze)
    - Bass boost +3.5dB a 150Hz (calore e corpo microfonico)
    - Treble boost +2.0dB a 3.5kHz (nitidezza vocale e consonanti cristalline)
    - Compand dinamico (voce radiofonica sempre presente e uniforme)
    """
    import edge_tts
    temp_raw_audio = output_path.replace(".mp3", "_raw.mp3")

    print(f"🎙️ Sintesi vocale ({voce}, ritmo: {rate}) in corso...")
    com = edge_tts.Communicate(testo, voice=voce, rate=rate)
    await com.save(temp_raw_audio)

    print("🎛️ Applicazione filtro 'Studio Broadcast' (Equalizzazione Calore + Compand)...")
    audio_filter = (
        "highpass=f=80,"
        "lowpass=f=12000,"
        "bass=g=3.5:f=150,"
        "treble=g=2.0:f=3500,"
        "compand=attacks=0.02:decays=0.2:points=-60/-60|-24/-12|0/-3:gain=2.0"
    )

    cmd = [
        FFMPEG_EXE, "-y",
        "-i", temp_raw_audio,
        "-af", audio_filter,
        "-ac", "2",
        "-b:a", "192k",
        output_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    try:
        os.remove(temp_raw_audio)
    except Exception:
        pass

    return output_path


# --- 7. DOPPIO MOTORE VIDEO: PIXABAY & PEXELS (IPER-CONTESTUALE) ---
def cerca_e_scarica_clip_pixabay(queries, temp_dir=TEMP_DIR):
    """Cerca e scarica una clip video HD da Pixabay tra una lista di query contestuali."""
    if not PIXABAY_API_KEY:
        return None

    random.shuffle(queries)
    for q in queries:
        try:
            url = f"https://pixabay.com/api/videos/?key={PIXABAY_API_KEY}&q={requests.utils.quote(q)}&video_type=film&per_page=10"
            r = requests.get(url, timeout=12, verify=False)
            if r.status_code != 200:
                continue
            data = r.json()
            hits = data.get("hits", [])
            if not hits:
                continue

            # Filtra video validi con durata tra 5 e 40 secondi
            valid_hits = [h for h in hits if 5 <= h.get("duration", 0) <= 40]
            if not valid_hits:
                valid_hits = hits

            hit = random.choice(valid_hits)
            videos = hit.get("videos", {})

            # Cerca il file con la migliore risoluzione verticale/orizzontale
            video_url = None
            for quality in ["large", "medium", "small", "tiny"]:
                if quality in videos and videos[quality].get("url"):
                    video_url = videos[quality]["url"]
                    break

            if not video_url:
                continue

            dest_path = os.path.join(temp_dir, f"pixabay_{hit['id']}.mp4")
            print(f"⬇️ Download clip Pixabay #{hit['id']} ({hit.get('duration')}s) per query '{q}'...")
            rv = requests.get(video_url, stream=True, timeout=25, verify=False)
            with open(dest_path, "wb") as vf:
                for chunk in rv.iter_content(chunk_size=128 * 1024):
                    if chunk:
                        vf.write(chunk)

            if os.path.exists(dest_path) and os.path.getsize(dest_path) > 100000:
                return dest_path
        except Exception as e:
            continue
    return None


def cerca_e_scarica_clip_pexels(queries, temp_dir=TEMP_DIR):
    """Cerca e scarica una clip video HD da Pexels come motore secondario."""
    if not PEXELS_API_KEY:
        return None

    random.shuffle(queries)
    for q in queries:
        try:
            url = f"https://api.pexels.com/videos/search?query={requests.utils.quote(q)}&per_page=8&orientation=portrait"
            headers = {"Authorization": PEXELS_API_KEY}
            r = requests.get(url, headers=headers, timeout=12, verify=False)
            if r.status_code != 200:
                # Prova senza orientation=portrait
                url = f"https://api.pexels.com/videos/search?query={requests.utils.quote(q)}&per_page=8"
                r = requests.get(url, headers=headers, timeout=12, verify=False)
                if r.status_code != 200:
                    continue

            data = r.json()
            videos = data.get("videos", [])
            if not videos:
                continue

            hit = random.choice(videos)
            video_files = hit.get("video_files", [])
            # Cerca file HD
            video_url = None
            for vf in sorted(video_files, key=lambda x: x.get("width", 0), reverse=True):
                if vf.get("link"):
                    video_url = vf["link"]
                    break

            if not video_url:
                continue

            dest_path = os.path.join(temp_dir, f"pexels_{hit['id']}.mp4")
            print(f"⬇️ Download clip Pexels #{hit['id']} ({hit.get('duration')}s) per query '{q}'...")
            rv = requests.get(video_url, stream=True, timeout=25, verify=False)
            with open(dest_path, "wb") as vf:
                for chunk in rv.iter_content(chunk_size=128 * 1024):
                    if chunk:
                        vf.write(chunk)

            if os.path.exists(dest_path) and os.path.getsize(dest_path) > 100000:
                return dest_path
        except Exception:
            continue
    return None


CATEGORIA_DYNAMIC_QUERIES = {
    "diritto": {
        "queries_pixabay": ["signing document pen", "contract notary", "lawyer contract desk", "legal consultation"],
        "queries_pexels": ["signing contract pen", "notary deed signing", "legal deed paperwork"],
        "icona": "⚖️",
        "tema_visivo": "Diritto Immobiliare e Tutela Notarile"
    },
    "urbanistica": {
        "queries_pixabay": ["architect blueprint", "architectural floorplan", "blueprint", "drafting table"],
        "queries_pexels": ["architect blueprint plan", "architect drawing blueprint", "floor plan house"],
        "icona": "📐",
        "tema_visivo": "Urbanistica, Catasto e Planimetrie"
    },
    "fiscale": {
        "queries_pixabay": ["calculator money finance", "tax calculation desk", "financial advisor loan", "finance paperwork"],
        "queries_pexels": ["tax calculation finance", "finance consultation desk", "mortgage calculation"],
        "icona": "💰",
        "tema_visivo": "Fisco, Tasse e Agevolazioni"
    },
    "contratti": {
        "queries_pixabay": ["signing contract handshake", "business agreement handshake", "real estate contract deal"],
        "queries_pexels": ["business handshake deal", "real estate contract handshake", "handshake agreement"],
        "icona": "🤝",
        "tema_visivo": "Contrattualistica e Accordi Blindati"
    },
    "successioni": {
        "queries_pixabay": ["historic luxury mansion", "prestigious estate house", "family heritage property", "notary papers"],
        "queries_pexels": ["historic luxury estate", "real estate classic property", "heritage mansion"],
        "icona": "🏛️",
        "tema_visivo": "Successioni Ereditarie e Continuità Storica"
    },
    "condominio": {
        "queries_pixabay": ["modern apartment building drone", "condominium exterior", "residential complex drone"],
        "queries_pexels": ["modern apartment building drone", "residential architecture complex", "condominium exterior"],
        "icona": "🏢",
        "tema_visivo": "Condominio e Parti Comuni"
    },
    "mutui": {
        "queries_pixabay": ["bank advisor meeting", "signing bank documents", "mortgage loan desk"],
        "queries_pexels": ["bank advisor mortgage meeting", "signing bank loan papers", "financial advisor loan"],
        "icona": "🏦",
        "tema_visivo": "Finanziamenti, Banche e Mutui"
    },
    "locazioni": {
        "queries_pixabay": ["handing keys real estate", "signing rental lease agreement", "meeting keys handshake"],
        "queries_pexels": ["handing over keys house", "real estate rental contract", "signing lease deal"],
        "icona": "🔑",
        "tema_visivo": "Locazioni e Contratti di Affitto"
    },
    "garanzie": {
        "queries_pixabay": ["house inspection survey", "architect inspecting building", "engineer building structure"],
        "queries_pexels": ["property inspection engineer", "architect inspecting house", "building survey inspection"],
        "icona": "🔍",
        "tema_visivo": "Verifica Tecnica, Perizie e Garanzie"
    },
    "energia": {
        "queries_pixabay": ["modern luxury house", "contemporary home", "solar energy modern house", "villa exterior"],
        "queries_pexels": ["modern eco architecture home", "luxury modern villa exterior", "energy efficient architecture"],
        "icona": "⚡",
        "tema_visivo": "Efficienza Energetica e Classe A"
    },
    "agrario": {
        "queries_pixabay": ["countryside estate villa", "vineyard luxury estate", "italian countryside villa", "olive grove"],
        "queries_pexels": ["countryside villa landscape", "italian estate vineyard", "prestigious country property"],
        "icona": "🌾",
        "tema_visivo": "Diritto Agrario e Proprietà Rurali"
    }
}


def ottieni_clip_video_contestuale(item, temp_dir=TEMP_DIR):
    """
    Ottiene la clip video perfetta per la pillola:
    Supporta dinamicamente fino a 365+ pillole collegando categoria e argomento.
    tenta Pixabay prima, poi Pexels come fallback.
    """
    item_id = str(item.get("id", "1"))
    if item_id in MAPPATURA_CONTESTUALE:
        info = MAPPATURA_CONTESTUALE[item_id]
    else:
        # Risoluzione dinamica basata su Categoria o Argomento per espansione 365+
        cat_lower = str(item.get("categoria", "")).lower()
        arg_lower = str(item.get("argomento", "")).lower()
        matched_info = None
        for k, v in CATEGORIA_DYNAMIC_QUERIES.items():
            if k in cat_lower or k in arg_lower:
                matched_info = v
                break
        if not matched_info:
            matched_info = {
                "queries_pixabay": ["modern luxury villa", "contemporary home interior", "signing contract desk"],
                "queries_pexels": ["modern luxury house exterior", "real estate contract closing", "architectural luxury home"],
                "icona": "🏡",
                "tema_visivo": f"{item.get('categoria', 'Immobiliare')} • {item.get('argomento', 'Consulenza')}"
            }
        info = matched_info

    queries_pix = info["queries_pixabay"]
    queries_pex = info["queries_pexels"]

    clip_path = cerca_e_scarica_clip_pixabay(queries_pix, temp_dir=temp_dir)
    if not clip_path:
        print("⚠️ Pixabay non ha fornito clip, passaggio al motore secondario Pexels...")
        clip_path = cerca_e_scarica_clip_pexels(queries_pex, temp_dir=temp_dir)

    if not clip_path:
        # Fallback sicuro su query generale architettura/contratto
        clip_path = cerca_e_scarica_clip_pixabay(["signing contract", "luxury house", "architect blueprint"], temp_dir=temp_dir)

    if not clip_path:
        raise RuntimeError("Impossibile reperire clip video contestuale dalle API.")

    return clip_path, info["tema_visivo"]


# --- 8. GENERAZIONE IMMAGINE CURATA PER IL 5° POST DEL CICLO ---
def ottieni_immagine_curata(item, temp_dir=TEMP_DIR):
    """
    Per il post #5 del ciclo (formato IMMAGINE), preleva la scena curata dedicata
    in assets/pillole_scene_curated/ oppure compone una card infografica master.
    """
    scena_path = os.path.join(CURATED_ASSETS_DIR, f"pillole_{item['id']}_scena_1.jpg")
    if os.path.exists(scena_path):
        print(f"🖼️ [5° POST - IMMAGINE] Utilizzo asset curato ufficiale: {os.path.basename(scena_path)}")
        return scena_path

    # Fallback su master
    fallback_path = os.path.join(BASE_DIR, "assets", "pillola_master_fallback.jpg")
    if os.path.exists(fallback_path):
        return fallback_path

    raise FileNotFoundError("Asset immagine curata non trovato per la pillola.")


# --- 9. GENERAZIONE OVERLAY GRAFICO PRESTIGIOSO (1080x1920) ---
def genera_overlay_grafico(categoria, titolo, normativa, testo_colonna_f, id_pillola, output_path):
    """
    Costruisce l'overlay PNG trasparente ad altissima risoluzione:
    - In Alto: Header Corporate con Logo, Categoria, Titolo Pillola e Norma in Oro
    - Al Centro: Oltre 1.000 pixel totalmente liberi per la clip in movimento
    - In Basso: Card Frosted Glass con il testo legale esatto estratto dalla Colonna F
    - Footer: Marchio Immobiliare Giancani con payoff di tutela e garanzia
    """
    W, H = 1080, 1920
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. HEADER SUPERIORE (Y: 90 - 490)
    top_y1, top_y2 = 90, 490
    card_top = Image.new("RGBA", (W - 100, top_y2 - top_y1), (11, 15, 25, 225))
    top_draw = ImageDraw.Draw(card_top)
    top_draw.rounded_rectangle([0, 0, W - 100, top_y2 - top_y1], radius=32, outline=(212, 175, 55, 230), width=4)
    img.paste(card_top, (50, top_y1), card_top)

    # Scritta Brand e Badge Rubrica
    font_badge = get_font(26, bold=True)
    badge_text = "IMMOBILIARE GIANCANI • TUTELA LEGALE & COMPRAVENDITE"
    bbox_b = draw.textbbox((0, 0), badge_text, font=font_badge)
    bw = bbox_b[2] - bbox_b[0]
    draw.text(((W - bw) / 2, 125), badge_text, font=font_badge, fill=(212, 175, 55, 255))

    # Pillola #ID e Categoria
    font_cat = get_font(32, bold=True)
    cat_text = f"PILLOLA #{id_pillola} • {categoria.upper()}"
    bbox_c = draw.textbbox((0, 0), cat_text, font=font_cat)
    cw = bbox_c[2] - bbox_c[0]
    draw.text(((W - cw) / 2, 175), cat_text, font=font_cat, fill=(240, 240, 240, 255))

    # Linea dorata divisoria
    draw.line([(120, 230), (W - 120, 230)], fill=(212, 175, 55, 180), width=2)

    # Titolo Argomento
    font_title = get_font(52, bold=True)
    righe_titolo = textwrap.wrap(titolo, width=24)
    y_titolo = 255
    for r in righe_titolo:
        bbox_t = draw.textbbox((0, 0), r, font=font_title)
        tw = bbox_t[2] - bbox_t[0]
        # Ombra titolo
        draw.text(((W - tw) / 2 + 2, y_titolo + 2), r, font=font_title, fill=(0, 0, 0, 220))
        draw.text(((W - tw) / 2, y_titolo), r, font=font_title, fill=(255, 255, 255, 255))
        y_titolo += 62

    # Riferimento normativo in basso alla card superiore
    font_norm = get_font(30, bold=True)
    norm_text = f"Riferimento di Legge: {normativa}"
    bbox_n = draw.textbbox((0, 0), norm_text, font=font_norm)
    nw = bbox_n[2] - bbox_n[0]
    draw.text(((W - nw) / 2, top_y2 - 50), norm_text, font=font_norm, fill=(212, 175, 55, 240))

    # 2. CARD TESTO COLONNA F NEL TERZO INFERIORE (Y: 1440 - 1760)
    bot_y1, bot_y2 = 1440, 1760
    card_bot = Image.new("RGBA", (W - 100, bot_y2 - bot_y1), (11, 15, 25, 230))
    bot_draw = ImageDraw.Draw(card_bot)
    bot_draw.rounded_rectangle([0, 0, W - 100, bot_y2 - bot_y1], radius=32, outline=(212, 175, 55, 210), width=3)
    img.paste(card_bot, (50, bot_y1), card_bot)

    # Testo della Colonna F ben formattato
    font_testo = get_font(33, bold=False)
    # Formattazione e wrapping
    righe_f = textwrap.wrap(testo_colonna_f, width=42)
    max_righe = 5
    if len(righe_f) > max_righe:
        righe_f = righe_f[:max_righe]
        righe_f[-1] = righe_f[-1].rstrip("., ") + "..."

    y_testo = bot_y1 + 40
    for r in righe_f:
        bbox_r = draw.textbbox((0, 0), r, font=font_testo)
        rw = bbox_r[2] - bbox_r[0]
        # Ombra testo
        draw.text(((W - rw) / 2 + 1, y_testo + 1), r, font=font_testo, fill=(0, 0, 0, 200))
        draw.text(((W - rw) / 2, y_testo), r, font=font_testo, fill=(245, 245, 245, 255))
        y_testo += 48

    # 3. FOOTER BRANDING (Y: 1780 - 1880)
    footer_text = "— Immobiliare Giancani —"
    font_foot = get_font(34, bold=True)
    bbox_f = draw.textbbox((0, 0), footer_text, font=font_foot)
    fw = bbox_f[2] - bbox_f[0]
    draw.text(((W - fw) / 2 + 2, 1795 + 2), footer_text, font=font_foot, fill=(0, 0, 0, 240))
    draw.text(((W - fw) / 2, 1795), footer_text, font=font_foot, fill=(212, 175, 55, 255))

    font_subfoot = get_font(23, bold=False)
    subfoot_text = "Consulenza Notarile, Conformità Catastale & Compravendita Protetta"
    bbox_sf = draw.textbbox((0, 0), subfoot_text, font=font_subfoot)
    sfw = bbox_sf[2] - bbox_sf[0]
    draw.text(((W - sfw) / 2, 1845), subfoot_text, font=font_subfoot, fill=(200, 200, 200, 220))

    img.save(output_path, "PNG")
    print(f"🎨 Overlay grafico generato: {output_path}")
    return output_path


# --- 10. SCELTA MUSICA DI SOTTOFONDO ---
def scegli_musica_sottofondo(music_dir=MUSIC_DIR):
    """Seleziona una traccia musicale royalty-free elegante."""
    if not os.path.exists(music_dir):
        return None
    brani = [f for f in os.listdir(music_dir) if f.lower().endswith(".mp3")]
    if not brani:
        return None
    # Preferisci tracce istituzionali / jazz / pianoforte
    preferiti = [b for b in brani if any(k in b.lower() for k in ["calma", "pianoforte", "jazz", "armonia", "ispirazione"])]
    scelto = random.choice(preferiti) if preferiti else random.choice(brani)
    return os.path.join(music_dir, scelto)


# --- 11. MONTAGGIO VIDEO DEFINITIVO (REELS 9:16) ---
def ottieni_durata_media(file_path):
    """Restituisce la durata in secondi di un file multimediale tramite FFprobe/FFmpeg."""
    cmd = [
        FFMPEG_EXE, "-i", file_path
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    for line in res.stderr.splitlines():
        if "Duration:" in line:
            try:
                parts = line.split("Duration:")[1].split(",")[0].strip()
                h, m, s = parts.split(":")
                return float(h) * 3600 + float(m) * 60 + float(s)
            except Exception:
                pass
    return 15.0


def monta_video_pillola(clip_input, overlay_png, audio_voce, output_mp4, bg_music_path=None, is_image=False):
    """
    Assembla il video definitivo 1080x1920 a 30fps:
    - Se is_image=True crea un video animato slow-zoom dalla foto curata
    - Se is_image=False adatta la clip video stock con loop rewind ping-pong
    - Sovrappone l'overlay grafico
    - Missa la voce equalizzata e la musica ducked al 14%
    """
    durata_voce = ottieni_durata_media(audio_voce)
    durata_totale = durata_voce + 1.2
    print(f"🎬 Durata voce studio: {durata_voce:.2f}s | Durata finale video: {durata_totale:.2f}s")

    cmd = [FFMPEG_EXE, "-y"]

    if is_image:
        # Genera video a partire dall'immagine statica con lieve slow-zoom Ken Burns
        v_filter = (
            f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
            f"zoompan=z='min(zoom+0.0005,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={int(durata_totale*30)}:s=1080x1920:fps=30,"
            f"eq=brightness=-0.08:contrast=1.06[vbase];"
            f"[vbase][1:v]overlay=0:0[vout]"
        )
        cmd.extend(["-loop", "1", "-t", str(durata_totale), "-i", clip_input])
    else:
        # Clip video: calcolo durata e ping-pong rewind loop
        durata_clip = ottieni_durata_media(clip_input)
        print(f"🎞️ Durata clip originale: {durata_clip:.2f}s")

        if durata_clip < durata_totale:
            print("🔄 Durata clip < voce: Attivazione Rewind Loop continuo (avanti -> reverse -> avanti)...")
            frames_clip = max(1, int(durata_clip * 30))
            cycle_frames = frames_clip * 2
            v_filter = (
                f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,"
                f"eq=brightness=-0.08:contrast=1.06[v_scaled];"
                f"[v_scaled]split[v_fwd][v_rev_in];"
                f"[v_rev_in]reverse[v_rev];"
                f"[v_fwd][v_rev]concat=n=2:v=1:a=0[v_cycle];"
                f"[v_cycle]loop=loop=-1:size={cycle_frames}:start=0[vbg];"
                f"[vbg]trim=duration={durata_totale}[vbase];"
                f"[vbase][1:v]overlay=0:0[vout]"
            )
        else:
            v_filter = (
                f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30,"
                f"trim=duration={durata_totale},eq=brightness=-0.08:contrast=1.06[vbase];"
                f"[vbase][1:v]overlay=0:0[vout]"
            )
        cmd.extend(["-i", clip_input])

    cmd.extend(["-i", overlay_png, "-i", audio_voce])

    # Gestione Audio con Ducking
    if bg_music_path and os.path.exists(bg_music_path):
        print(f"🎵 Sottofondo musicale con ducking: {os.path.basename(bg_music_path)}")
        cmd.extend(["-stream_loop", "-1", "-i", bg_music_path])
        filter_complex = (
            f"{v_filter};"
            f"[3:a]volume=0.14,afade=t=in:ss=0:d=0.8,afade=t=out:st={durata_totale-1.2}:d=1.2[amusic];"
            f"[2:a]volume=1.0[avoice];"
            f"[avoice][amusic]amix=inputs=2:duration=first:dropout_transition=2[aout]"
        )
    else:
        filter_complex = f"{v_filter};[2:a]volume=1.0[aout]"

    cmd.extend([
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", "[aout]",
        "-t", str(durata_totale),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "22",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        output_mp4
    ])

    print("🚀 Rendering definitivo con FFmpeg in corso...")
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        err = res.stderr[-800:] if res.stderr else "Errore sconosciuto FFmpeg"
        raise RuntimeError(f"FFmpeg fallito:\n{err}")

    size_mb = os.path.getsize(output_mp4) / (1024 * 1024)
    print(f"✅ Video renderizzato con successo: {output_mp4} ({size_mb:.2f} MB)")
    return output_mp4


# --- 12. INVIO SU TELEGRAM CON NOTIFICA PERSONALIZZATA ---
def invia_su_telegram(video_path, item, tema_visivo, formato_usato, messaggio_speciale="Ecco la nuova voce in questo post, ti piace?"):
    """Invia il video generato direttamente al canale/chat Telegram."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("⚠️ Notifica Telegram non inviata: credenziali assenti.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendVideo"
    caption = (
        f"{messaggio_speciale}\n\n"
        f"🏛️ *PILLOLA IMMOBILIARE #{item['id']}*: {item['titolo']}\n"
        f"📜 *Riferimento di Legge:* {item['normativa']}\n"
        f"🏷️ *Categoria:* {item['categoria']}\n\n"
        f"📋 *Consulenza da Colonna F:*\n"
        f"«{item['colonna_f']}»\n\n"
        f"🎙️ *Voce:* Isabella Neural (Filtro Broadcast Studio)\n"
        f"🎬 *Formato:* {formato_usato.upper()} (Cadenza 4:1 - Step {item['step_ciclo']}/5)\n"
        f"🎥 *Scena Contestuale:* {tema_visivo}\n\n"
        f"— Immobiliare Giancani"
    )

    try:
        with open(video_path, "rb") as vf:
            data = {
                "chat_id": TELEGRAM_CHAT_ID,
                "caption": caption,
                "parse_mode": "Markdown"
            }
            files = {"video": (os.path.basename(video_path), vf, "video/mp4")}
            r = requests.post(url, data=data, files=files, timeout=120, verify=False)
            res = r.json()
            if res.get("ok"):
                print("📲 Video e notifica consegnati con successo su Telegram!")
                return True
            else:
                print(f"❌ Errore Telegram ({r.status_code}): {res}")
                return False
    except Exception as e:
        print(f"❌ Eccezione Telegram: {e}")
        return False


# --- 13. PUBBLICAZIONE SU FACEBOOK (OPZIONALE) ---
def pubblica_su_facebook(video_path, caption):
    """Carica il Reel sulla Pagina Facebook aziendale Immobiliare Giancani."""
    if not FACEBOOK_TOKEN or not FACEBOOK_PAGE_ID:
        print("🔒 Pubblicazione Facebook non attiva: token o Page ID mancante.")
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
                return True
            else:
                print(f"❌ Errore pubblicazione Facebook: {res}")
                return False
    except Exception as e:
        print(f"❌ Eccezione Facebook: {e}")
        return False


# --- 14. PULIZIA FILE TEMPORANEI ---
def pulisci_temp(temp_dir=TEMP_DIR):
    """Rimuove file grezzi temporanei."""
    if not os.path.exists(temp_dir):
        return
    for f in os.listdir(temp_dir):
        try:
            p = os.path.join(temp_dir, f)
            if os.path.isfile(p):
                os.remove(p)
        except Exception:
            pass


# --- 15. FLUSSO PRINCIPALE COMPLETO ---
async def esegui_pipeline_pillole(id_richiesto=None, forza_formato=None, voce="it-IT-IsabellaNeural", pubblica_fb=False, messaggio_speciale="Ecco la nuova voce in questo post, ti piace?"):
    """Esegue la generazione completa della Pillola Immobiliare."""
    print("=" * 75)
    print("🏛️ BOT VIDEO PILLOLE IMMOBILIARI & LEGALI — IMMOBILIARE GIANCANI")
    print("⭐ Alternanza 4:1 | Stock Video Contestuale | Voce Studio Broadcast")
    print("=" * 75)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # 1. Estrazione dati rigorosamente da Colonna F
    item = estrai_pillola_colonna_f(CSV_FILE, id_richiesto=id_richiesto, forza_formato=forza_formato)
    formato = item["formato"]

    temp_clip_path = None
    try:
        # 2. Testo recitato da Isabella (introduzione istituzionale + Colonna F)
        testo_recitato = (
            f"Consulenza Immobiliare Giancani. {item['titolo']}. "
            f"{item['colonna_f']} "
            f"Affidati alla sicurezza di Immobiliare Giancani."
        )

        audio_studio_path = os.path.join(TEMP_DIR, f"audio_studio_{timestamp}.mp3")
        await sintetizza_audio_studio(testo_recitato, audio_studio_path, voce=voce, rate="-3%")

        # 3. Reperimento Visual (Video o Immagine in base al ciclo 4:1)
        is_image_mode = (formato == "immagine")
        if is_image_mode:
            visual_path = ottieni_immagine_curata(item, temp_dir=TEMP_DIR)
            tema_visivo = "Scheda Infografica e Scena Curata Master"
        else:
            visual_path, tema_visivo = ottieni_clip_video_contestuale(item, temp_dir=TEMP_DIR)
            temp_clip_path = visual_path

        # 4. Generazione Overlay Grafico
        overlay_path = os.path.join(TEMP_DIR, f"overlay_{timestamp}.png")
        genera_overlay_grafico(
            categoria=item["categoria"],
            titolo=item["titolo"],
            normativa=item["normativa"],
            testo_colonna_f=item["colonna_f"],
            id_pillola=item["id"],
            output_path=overlay_path
        )

        # 5. Sottofondo Musicale
        bg_music = scegli_musica_sottofondo()

        # 6. Montaggio Video 1080x1920
        out_filename = f"pillola_giancani_{item['id']}_{timestamp}.mp4"
        output_video_path = os.path.join(OUTPUT_DIR, out_filename)
        monta_video_pillola(
            clip_input=visual_path,
            overlay_png=overlay_path,
            audio_voce=audio_studio_path,
            output_mp4=output_video_path,
            bg_music_path=bg_music,
            is_image=is_image_mode
        )

        # 7. Invio su Telegram con domanda sulla nuova voce
        invia_su_telegram(
            video_path=output_video_path,
            item=item,
            tema_visivo=tema_visivo,
            formato_usato=formato,
            messaggio_speciale=messaggio_speciale
        )

        # 8. Aggiorna stato di rotazione 4:1
        nuovo_step = aggiorna_stato_rotazione(item["id"], formato, item["titolo"])
        print(f"📊 Rotazione aggiornata con successo! Prossimo step del ciclo: {((nuovo_step % 5) + 1)}/5")

        # 9. Pubblicazione su Facebook se richiesta
        if pubblica_fb:
            copy_fb = (
                f"🏛️ CONSULENZA IMMOBILIARE & LEGALE 🏛️\n\n"
                f"📌 {item['titolo'].upper()} ({item['normativa']})\n\n"
                f"{item['colonna_f']}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"👉 Per una compravendita sicura, trasparente e garantita:\n"
                f"⭐ IMMOBILIARE GIANCANI ⭐\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"— Immobiliare Giancani"
            )
            pubblica_su_facebook(output_video_path, copy_fb)

        return output_video_path

    finally:
        pulisci_temp(TEMP_DIR)
        print("=" * 75)
        print("🏁 PROCESSO COMPLETATO CON SUCCESSO — Immobiliare Giancani")
        print("=" * 75)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Bot Video Pillole Immobiliari & Legali (Alternanza 4:1)")
    parser.add_argument("--id", type=str, default=None, help="ID specifico della pillola da 1 a 10")
    parser.add_argument("--formato", type=str, default=None, choices=["video", "immagine"], help="Forza formato: 'video' o 'immagine'")
    parser.add_argument("--voce", type=str, default="it-IT-IsabellaNeural", help="Voce Edge-TTS")
    parser.add_argument("--pubblica-fb", action="store_true", help="Pubblica automaticamente su Facebook")
    parser.add_argument("--messaggio", type=str, default="Ecco la nuova voce in questo post, ti piace?", help="Messaggio di accompagnamento per Telegram")

    args = parser.parse_args()

    asyncio.run(esegui_pipeline_pillole(
        id_richiesto=args.id,
        forza_formato=args.formato,
        voce=args.voce,
        pubblica_fb=args.pubblica_fb,
        messaggio_speciale=args.messaggio
    ))
