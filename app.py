import streamlit as st
import streamlit.components.v1 as components
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import re
import io
import base64
import time
import random
import math
import hashlib
import os
import tempfile
import segno
import unicodedata
from fpdf import FPDF


# -----------------------------------------------------------------------------
# 1. KONFIGURATION & SETUP
# -----------------------------------------------------------------------------
st.set_page_config(
page_title="Klassenkonto", 
    layout="wide", 
    page_icon="💶",
    initial_sidebar_state="collapsed"

)

# App URL für Infotexte / QR Codes
FALLBACK_URL = "https://klassenkonto-app-mbm47r42x2muagq3jhzaxg.streamlit.app" 
APP_URL = st.secrets.get("app_url", FALLBACK_URL)
if APP_URL.endswith("/"): APP_URL = APP_URL[:-1]



# -----------------------------------------------------------------------------
# UI THEME (Premium Login + Dark Mode Optimierung)
# -----------------------------------------------------------------------------

def inject_premium_ui_css():
    st.markdown(
        """
<style>
:root {
  --kk-radius: 20px;
  --kk-radius-sm: 12px;
  --kk-shadow: 0 24px 70px rgba(0,0,0,.14);
  --kk-shadow-soft: 0 14px 35px rgba(0,0,0,.12);
  --kk-border: rgba(49, 51, 63, 0.18);
  --kk-border-strong: rgba(49, 51, 63, 0.28);
  --kk-text: rgba(49, 51, 63, 0.92);
  --kk-muted: rgba(49, 51, 63, 0.62);
  --kk-bg: #f6f7fb;
  --kk-card: rgba(255,255,255,.84);
  --kk-accent: #2e7dff;
  --kk-accent2: #00c2a8;
  --kk-danger: #e05252;
  --kk-success: #1ea97a;
  --kk-warning: #f2b01e;
  --kk-input: rgba(255,255,255,.92);
  --kk-input-focus: rgba(46, 125, 255, .20);
}

@media (prefers-color-scheme: dark) {
  :root {
    --kk-border: rgba(255,255,255,0.14);
    --kk-border-strong: rgba(255,255,255,0.22);
    --kk-text: rgba(255,255,255,0.92);
    --kk-muted: rgba(255,255,255,0.62);
    --kk-bg: #0e1117;
    --kk-card: rgba(22, 27, 34, .82);
    --kk-accent: #7aa7ff;
    --kk-accent2: #42e7c6;
    --kk-danger: #ff6b6b;
    --kk-success: #39d98a;
    --kk-warning: #ffd166;
    --kk-input: rgba(16, 20, 26, .86);
    --kk-input-focus: rgba(122, 167, 255, .22);
  }
}

/* Background */
[data-testid="stAppViewContainer"] {
  background:
    radial-gradient(1200px 650px at 12% 0%, rgba(46,125,255,.16), transparent 60%),
    radial-gradient(900px 520px at 88% 10%, rgba(0,194,168,.14), transparent 55%),
    radial-gradient(800px 520px at 50% 95%, rgba(242,176,30,.10), transparent 55%),
    var(--kk-bg) !important;
}

.block-container { padding-top: 1.15rem !important; }

/* Premium card */
@keyframes kkSlideUp {
  from { opacity: 0; transform: translateY(14px) scale(.99); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}

.kk-center { display: flex; justify-content: center; }
.kk-card {
  width: min(580px, 94vw);
  background: var(--kk-card);
  border: 1px solid var(--kk-border);
  border-radius: var(--kk-radius);
  box-shadow: var(--kk-shadow);
  padding: 22px 22px 14px 22px;
  backdrop-filter: blur(10px);
  animation: kkSlideUp .42s ease-out;
  position: relative;
}
.kk-card::before {
  content: "";
  position: absolute;
  inset: 0 0 auto 0;
  height: 6px;
  border-radius: var(--kk-radius) var(--kk-radius) 12px 12px;
  background: linear-gradient(90deg, var(--kk-accent), var(--kk-accent2));
  opacity: .95;
}

.kk-logo-wrap { display:flex; justify-content:center; align-items:center; width:100%; margin-top:14px; margin-bottom:8px; }
.kk-logo {
  width: 72px;
  height: 72px;
  border-radius: 18px;
  border: 1px solid var(--kk-border);
  box-shadow: var(--kk-shadow-soft);
  object-fit: contain;
  background: rgba(255,255,255,.45);
}
@media (prefers-color-scheme: dark) {
  .kk-logo { background: rgba(255,255,255,.06); }
}

.kk-title { text-align:center; font-size:2.35rem; font-weight:800; letter-spacing:-0.02em; line-height:1.08; margin:0 0 12px 0; color: var(--kk-text); }
.kk-sub { text-align: center; color: var(--kk-muted); font-size: .98rem; margin-top: -6px; }

.kk-pill {
  display: inline-flex;
  gap: 8px;
  align-items: center;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid var(--kk-border);
  background: rgba(0,0,0,.03);
}
@media (prefers-color-scheme: dark) {
  .kk-pill { background: rgba(255,255,255,.04); }
}

/* Buttons */
.stButton > button {
  border-radius: 14px !important;
  padding: 0.58rem 0.95rem !important;
  border: 1px solid var(--kk-border-strong) !important;
}
.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, var(--kk-accent), var(--kk-accent2)) !important;
  border: 1px solid transparent !important;
  color: white !important;
}

/* Inputs */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] div[data-baseweb="select"] {
  border-radius: 14px !important;
  border: 1px solid var(--kk-border) !important;
  background: var(--kk-input) !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus,
[data-testid="stNumberInput"] input:focus {
  outline: none !important;
  box-shadow: 0 0 0 4px var(--kk-input-focus) !important;
  border-color: rgba(46,125,255,.55) !important;
}

/* Expander & DataFrame */
[data-testid="stExpander"],
[data-testid="stDataFrame"],
[data-testid="stAlert"] {
  border-radius: var(--kk-radius-sm) !important;
  border: 1px solid var(--kk-border) !important;
  overflow: hidden;
}

/* Sidebar background */
section[data-testid="stSidebar"] > div {
  background: rgba(255,255,255,.55);
}
@media (prefers-color-scheme: dark) {
  section[data-testid="stSidebar"] > div {
    background: rgba(22, 27, 34, .65);
  }
}
.kk-logo-img { width: 120px; height: auto; display:block; margin: 0 auto; }
.kk-brand { display:flex; flex-direction:column; align-items:center; width:100%; }
</style>
        """,
        unsafe_allow_html=True,
    )




def dedupe_click_guard(action_hash: str, window_s: int = 8) -> bool:
    """UI-Schutz gegen Doppelklick / mehrfaches Absenden."""
    try:
        now = time.time()
        k_h = 'last_action_hash'
        k_t = 'last_action_time'
        prev_h = str(st.session_state.get(k_h, '') or '')
        prev_t = float(st.session_state.get(k_t, 0) or 0)
        if prev_h == str(action_hash) and (now - prev_t) < window_s:
            return False
        st.session_state[k_h] = str(action_hash)
        st.session_state[k_t] = now
        return True
    except Exception:
        return True

def toast(kind: str, msg: str):
    """Streamlit toast helper (fällt auf st.info/error zurück, falls nicht verfügbar)."""
    try:
        st.toast(msg)
    except Exception:
        if kind == 'error':
            st.error(msg)
        elif kind == 'success':
            st.success(msg)
        elif kind == 'warning':
            st.warning(msg)
        else:
            st.info(msg)



# --- Schutz gegen Code-Raten (Familien-Login) ---
def fam_check_lockout(prefix: str = 'fam', max_tries: int = 5, base_lock_s: int = 60):
    """Return (locked: bool, remaining_seconds: int). Uses st.session_state."""
    now = time.time()
    lock_key = f'{prefix}_lock_until'
    cnt_key = f'{prefix}_fail_count'
    if cnt_key not in st.session_state: st.session_state[cnt_key] = 0
    if lock_key not in st.session_state: st.session_state[lock_key] = 0.0
    lock_until = float(st.session_state.get(lock_key, 0.0) or 0.0)
    if lock_until > now:
        return True, int(lock_until - now)
    return False, 0

def fam_register_fail(prefix: str = 'fam', max_tries: int = 5, base_lock_s: int = 60):
    """Increment fail counter; set lockout if threshold reached."""
    now = time.time()
    lock_key = f'{prefix}_lock_until'
    cnt_key = f'{prefix}_fail_count'
    cnt = int(st.session_state.get(cnt_key, 0) or 0) + 1
    st.session_state[cnt_key] = cnt
    # ab max_tries: Sperre, dann exponentiell verlängern (max 15 Minuten)
    if cnt >= max_tries:
        extra = max(0, cnt - max_tries)
        lock_s = min(900, base_lock_s * (2 ** extra))
        st.session_state[lock_key] = now + lock_s
        return lock_s
    return 0

def fam_reset_lockout(prefix: str = 'fam'):
    for k in [f'{prefix}_lock_until', f'{prefix}_fail_count']:
        if k in st.session_state: st.session_state[k] = 0
def check_secrets():
    missing = []
    if "connections" not in st.secrets: missing.append("[connections.gsheets]")
    if missing: st.error(f"Fehlende Secrets: {missing}"); st.stop()

check_secrets()
conn = st.connection("gsheets", type=GSheetsConnection)

# -----------------------------------------------------------------------------
# 2. HILFSFUNKTIONEN


def parse_amount(val, default=0.0):
    """Parse Betrag aus CSV/Text. Akzeptiert '10', '10,5', '10.50', '1.234,56'."""
    try:
        if val is None:
            return float(default)
        s = str(val).strip()
        if s == '' or s.lower() == 'nan':
            return float(default)
        s = s.replace('€', '').replace('EUR', '').strip()
        if s.count(',') == 1 and s.count('.') >= 1:
            s = s.replace('.', '').replace(',', '.')
        else:
            s = s.replace(',', '.')
        return float(s)
    except Exception:
        return float(default)
def normalize_text(text):
    text = str(text).strip()

    replacements = {
        "Ä": "AE",
        "Ö": "OE",
        "Ü": "UE",
        "ä": "ae",
        "ö": "oe",
        "ü": "ue",
        "ß": "ss"
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = unicodedata.normalize("NFKD", text)

    text = "".join(
        c for c in text
        if not unicodedata.combining(c)
    )

    return text


# -----------------------------------------------------------------------------
# Buchungen: robuste Normalisierung (Status/Empfänger-Spalten)
# -----------------------------------------------------------------------------

def sanitize_status_columns(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    if 'Ueberweisen_An' not in df.columns:
        df['Ueberweisen_An'] = ''
    if 'Status' not in df.columns:
        df['Status'] = ''

    ua = df['Ueberweisen_An'].astype(str).str.strip()
    stv = df['Status'].astype(str).str.strip()

    st_missing = stv.isin(['', 'nan', 'None'])
    ua_is_status = ua.isin(['Offen', 'Erledigt'])
    st_is_status = stv.isin(['Offen', 'Erledigt'])

    m1 = ua_is_status & st_missing
    if m1.any():
        df.loc[m1, 'Status'] = ua[m1]
        df.loc[m1, 'Ueberweisen_An'] = ''

    m2 = ua_is_status & (~st_is_status) & (~st_missing)
    if m2.any():
        tmp = df.loc[m2, 'Status'].copy()
        df.loc[m2, 'Status'] = df.loc[m2, 'Ueberweisen_An']
        df.loc[m2, 'Ueberweisen_An'] = tmp

    return df

# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# Datum: einheitliche Anzeige (yyy.mm.dd.)
DATE_DISPLAY_FMT = "%Y.%m.%d"

def format_date_display(val):
    """Datum robust für Anzeige formatieren: yyyy.mm.dd.(str/datetime/Timestamp)."""
    try:
        if val is None:
            return ""
        s = str(val).strip()
        if s == "" or s.lower() in {"nan", "none"}:
            return ""
        dt = pd.to_datetime(val, errors="coerce", dayfirst=True)
        if pd.isna(dt):
            return s
        return dt.strftime(DATE_DISPLAY_FMT)
    except Exception:
        return str(val) if val is not None else ""

def format_date_columns(df: pd.DataFrame, cols=None) -> pd.DataFrame:
    """Kopie des DF, in der Datumsspalten als dd.mm.yyyy formatiert sind (nur Anzeige)."""
    if df is None:
        return df
    df2 = df.copy()
    if cols is None:
        cols = [c for c in df2.columns if str(c).lower() in {"datum", "archiv_datum", "archiv_jahr"}]
    for c in cols:
        if c in df2.columns:
            df2[c] = df2[c].apply(format_date_display)
    return df2

def hash_password(password):
    return hashlib.sha256(str(password).encode()).hexdigest()


# -----------------------------------------------------------------------------
# Duplikat-Schutz: deterministische Buchungs-ID (Hash)
# -----------------------------------------------------------------------------

def compute_buchung_hash(entry: dict) -> str:
    """Erzeugt eine stabile Hash-ID für eine Buchung (ohne Zeitstempel)."""
    try:
        def _norm(s):
            return str(s or '').strip()
        datum = _norm(entry.get('Datum'))
        sid = _norm(entry.get('ID')).upper()
        amt = float(entry.get('Betrag', 0.0) or 0.0)
        amt = round(amt, 2)
        beschr = _norm(entry.get('Beschreibung'))[:200]
        erf = _norm(entry.get('Erfasst_Von'))
        payee = _norm(entry.get('Ueberweisen_An'))
        status = _norm(entry.get('Status'))
        raw = f"{datum}|{sid}|{amt:.2f}|{beschr}|{erf}|{payee}|{status}"
        return hashlib.sha256(raw.encode('utf-8')).hexdigest()
    except Exception:
        return hashlib.sha256(str(entry).encode('utf-8')).hexdigest()


def check_password_strength(password):
    if len(password) < 12: return False, f"Zu kurz ({len(password)}/12)."
    if not re.search(r"[a-z]", password): return False, "Kleinbuchstabe fehlt."
    if not re.search(r"[A-Z]", password): return False, "Großbuchstabe fehlt."
    if not re.search(r"\d", password): return False, "Zahl fehlt."
    return True, ""

def generate_random_code(length=16):
    chars = string.ascii_letters + string.digits
    chars = chars.replace('l', '').replace('I', '').replace('O', '').replace('0', '') 
    return ''.join(random.choice(chars) for _ in range(length))

def normalize_id(val: str) -> str:
    return str(val).replace(".0", "").strip().upper()


def make_id_name_options(df, id_col="ID", name_col="Name", sep=" - ", include_all=False, all_label="(alle)"):
    """Robuste Options-Liste wie 'ID - Name' ohne DataFrame.agg/apply.
    Entfernt NaN/None, trimmt, und gibt nur sinnvolle Einträge zurück.
    """
    try:
        if df is None or df.empty or id_col not in df.columns or name_col not in df.columns:
            return [all_label] if include_all else []
        tmp = df[[id_col, name_col]].copy()
        tmp[id_col] = tmp[id_col].fillna("").astype(str).replace(["nan", "None"], "").str.strip()
        tmp[name_col] = tmp[name_col].fillna("").astype(str).replace(["nan", "None"], "").str.strip()

        label = tmp[id_col]
        label = label.where(tmp[name_col].eq(""), tmp[id_col] + sep + tmp[name_col])
        label = label.where(tmp[id_col].ne(""), tmp[name_col])

        out = [x for x in label.tolist() if str(x).strip()]
        return ([all_label] + out) if include_all else out
    except Exception:
        return [all_label] if include_all else []

# Validierung: genau 10 Zeichen A-Z/0-9 (Bestands-IDs zulassen)
ID10_PATTERN = re.compile(r"^[A-Z0-9]{10}$")
# Generationsmuster: YYYY + 6 Zeichen
ID10_YEAR_PATTERN = re.compile(r"^\d{4}[A-Z0-9]{6}$")

def is_valid_student_id_10(id_str: str) -> bool:
    """True, wenn ID genau 10 Zeichen A-Z/0-9 hat."""
    return bool(ID10_PATTERN.match(normalize_id(id_str)))

def generate_student_id_10(existing_ids: set) -> str:
    """Generiert eine eindeutige 10-stellige ID: YYYY + 6 Zeichen (A-Z/0-9)."""
    year = datetime.now().strftime('%Y')
    chars = (string.ascii_uppercase + string.digits)
    for bad in ['O','I','0','1']:
        chars = chars.replace(bad, '')

    for _ in range(500):
        suffix = ''.join(random.choice(chars) for _ in range(6))
        cand = (year + suffix).upper()
        if cand not in existing_ids:
            return cand

    return year + ''.join(random.choice(chars) for _ in range(6))

def get_next_logical_id(df_stamm):
    """Backward compatible: liefert neue 10-stellige Schüler-ID (YYYY + 6 Zeichen)."""
    try:
        existing = set(df_stamm['ID'].astype(str).apply(normalize_id)) if 'ID' in df_stamm.columns else set()
        return generate_student_id_10(existing)
    except Exception:
        return datetime.now().strftime('%Y') + 'AAAAAA'


def generate_epc_qr(iban, bic, recipient, amount, text):
    try:
        amount_str = f"{abs(amount):.2f}"
        if amount == 0: amount_str = "0.00"
        qr_content = f"BCD\n002\n1\nSCT\n{bic}\n{recipient}\n{iban}\nEUR{amount_str}\n\n\n{text}"
        img = segno.make(qr_content, error='M')
        out = io.BytesIO()
        img.save(out, kind='png', scale=4)
        return out
    except Exception:
        return None

def parse_csv_elba(uploaded_file):
    parsed = []
    try:
        df = pd.read_csv(uploaded_file, sep=';', header=None, encoding='latin-1', dtype=str)
        for index, row in df.iterrows():
            try:
                raw_date = str(row[0]).strip() if pd.notna(row[0]) else ""
                raw_text = str(row[1]).strip() if pd.notna(row[1]) else ""
                raw_amount = str(row[3]).strip() if pd.notna(row[3]) else "0"
                amount_str = raw_amount.replace('.', '').replace(',', '.')
                amount_val = float(amount_str)
                
                id_matches = re.findall(r'\b(?:\d{4}[A-Z0-9]{6}|[A-Z]{3,5}\d{4,6}|[A-Z]{4}\d{6}|\d{5,10})\b', raw_text.upper())
                
                if id_matches and abs(amount_val) > 0.001:
                    try:
                        date_obj = datetime.strptime(raw_date, "%d.%m.%Y")
                        date_db = date_obj.strftime("%Y-%m-%d")
                    except:
                        date_db = datetime.today().strftime("%Y-%m-%d")
                    now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    anzahl_kinder = len(id_matches)
                    betrag_pro_kind = round(amount_val / anzahl_kinder, 2)
                    for found_id in id_matches:
                        parsed.append({
                            "ID": found_id.upper(),
                            "Betrag": betrag_pro_kind,
                            "Datum": date_db,
                            "Zeitstempel": now_ts,
                            "Beschreibung": raw_text[:200],
                            "Status": "Erledigt"
                        })
            except Exception: continue
    except Exception as e:
        st.error(f"Fehler beim Lesen der CSV: {e}")
        return pd.DataFrame()
    return pd.DataFrame(parsed)

class PDF(FPDF):
    def header(self):
        logo_path = 'logo.png'
        if os.path.exists(logo_path):
            try:
                self.image(logo_path, 10, 8, 15)
                self.set_font('Arial', 'B', 15)
                self.cell(20); self.cell(0, 10, 'Klassenkonto', 0, 1, 'L'); self.ln(10)
            except:
                self.set_font('Arial', 'B', 15); self.cell(0, 10, 'Klassenkonto', 0, 1, 'C'); self.ln(5)
    def footer(self):
        self.set_y(-15); self.set_font('Arial', 'I', 8); self.cell(0, 10, f'Seite {self.page_no()}', 0, 0, 'C')

def create_pdf_report(student_name, klasse, transactions, iban=None, bic=None, empf=None, id_val=None):
    pdf = PDF(); pdf.add_page(); pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Kontoauszug für: {student_name} ({klasse})", 0, 1)
    pdf.cell(0, 10, f"Erstellt am: {datetime.now().strftime(DATE_DISPLAY_FMT)}", 0, 1); pdf.ln(5)
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(30, 10, "Datum", 1); pdf.cell(90, 10, "Zweck", 1); pdf.cell(30, 10, "Betrag", 1, 0, 'R'); pdf.ln()
    pdf.set_font("Arial", size=10); total = 0
    for _, row in transactions.iterrows():
        try:
            desc = str(row['Beschreibung']).encode('latin-1', 'replace').decode('latin-1')
            dat = format_date_display(row['Datum']); amt = row['Betrag']; total += amt
            pdf.cell(30, 10, dat, 1); pdf.cell(90, 10, desc[:45], 1); pdf.cell(30, 10, f"{amt:.2f} EUR", 1, 0, 'R'); pdf.ln()
        except: pass
    pdf.ln(5); pdf.set_font("Arial", 'B', 12); pdf.cell(120, 10, "Aktueller Kontostand:", 0)
    col = (200, 0, 0) if total < 0 else (0, 150, 0); pdf.set_text_color(*col)
    pdf.cell(30, 10, f"{total:.2f} EUR", 0, 0, 'R'); pdf.set_text_color(0, 0, 0)
    
    if iban and bic and id_val and str(id_val).strip() != "":
        pdf.ln(15); pdf.set_font("Arial", 'B', 11)
        pdf.cell(0, 10, "Zahlschein / QR-Code zur Einzahlung:", 0, 1)
        pdf.set_font("Arial", '', 10)
        pdf.cell(0, 5, "Scannen Sie diesen Code für eine Überweisung (Betrag frei wählbar).", 0, 1)
        qr_text = f"{id_val} {student_name}"
        qr_buffer = generate_epc_qr(iban, bic, empf, 0.00, qr_text)
        if qr_buffer:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                tmp.write(qr_buffer.getvalue()); tmp_path = tmp.name
            try: 
                pdf.image(tmp_path, x=15, y=pdf.get_y()+5, w=40)
            finally: 
                try: os.remove(tmp_path)
                except: pass
    return pdf.output(dest='S').encode('latin-1')

# -----------------------------------------------------------------------------
# 3. DATENBANK LOGIK
# -----------------------------------------------------------------------------
@st.cache_data(ttl=120)
def load_stammdaten():
    """Lädt und bereinigt Stammdaten. (Schnell – wird für Login benötigt)"""
    cols_stamm = ["Rolle", "Name", "Klasse", "ID", "Email", "Zugangscode", "Passwort", "Muss_Passwort_Aendern"]
    for attempt in range(3):
        try:
            df_stamm = conn.read(worksheet="Stammdaten")
            df_stamm.columns = df_stamm.columns.str.strip()
            for c in cols_stamm:
                if c not in df_stamm.columns:
                    df_stamm[c] = ""
            df_stamm['ID'] = df_stamm['ID'].astype(str).str.replace(r"\.0$", "", regex=True).str.strip().str.upper()
            df_stamm['ID'] = df_stamm['ID'].replace("NAN", "")
            df_stamm['Klasse'] = df_stamm['Klasse'].astype(str).str.replace("nan", "")
            df_stamm = df_stamm[df_stamm['Name'].notna()]
            df_stamm['Email'] = df_stamm['Email'].astype(str).str.strip().str.lower()
            df_stamm['Passwort'] = df_stamm['Passwort'].astype(str).str.strip()
            df_stamm['Zugangscode'] = df_stamm['Zugangscode'].astype(str).replace(["nan", "None", ""], "").str.strip()
            df_stamm['Muss_Passwort_Aendern'] = df_stamm['Muss_Passwort_Aendern'].astype(str).str.strip().str.lower()

            def get_rank(rolle_raw):
                r = str(rolle_raw).strip().lower()
                if "admin" in r:
                    return 1
                if "lehrer" in r:
                    return 2
                if "schüler" in r or "schueler" in r:
                    return 3
                return 99

            df_stamm['_SortRank'] = df_stamm['Rolle'].apply(get_rank)

            def get_sort_class(row):
                return "" if row['_SortRank'] < 3 else str(row['Klasse'])

            df_stamm['_SortClass'] = df_stamm.apply(get_sort_class, axis=1)
            df_stamm = df_stamm.sort_values(by=['_SortRank', '_SortClass', 'Name']).drop(columns=['_SortRank', '_SortClass'])
            return df_stamm
        except Exception as e:
            if "429" in str(e) or "Quota" in str(e):
                time.sleep(2 + attempt)
                continue
            st.error(f"Datenbankfehler (Stammdaten): {e}")
            break
    return pd.DataFrame(columns=cols_stamm)


@st.cache_data(ttl=120)
def load_klassenblatt():
    """Lädt Klassen-Worksheet (schnell, für Familien-Ansicht / Nachrichten)."""
    cols_klasse = ["Klasse", "IBAN", "BIC", "Empfaenger", "Nachricht"]
    try:
        df_klassen = conn.read(worksheet="Klassen")
        df_klassen.columns = df_klassen.columns.str.strip()
    except Exception:
        df_klassen = pd.DataFrame(columns=cols_klasse)
    for c in cols_klasse:
        if c not in df_klassen.columns:
            df_klassen[c] = ""
    df_klassen['Klasse'] = df_klassen['Klasse'].astype(str).str.strip()
    return df_klassen


@st.cache_data(ttl=120)
def load_buchungen():
    """Lädt Buchungen – das ist der langsamste Teil und wird deshalb lazy geladen."""
    cols_buch = ["Datum", "Zeitstempel", "ID", "Name", "Beschreibung", "Betrag", "Erfasst_Von", "Ueberweisen_An", "Status"]
    for attempt in range(3):
        try:
            df_buch = conn.read(worksheet="Buchungen")
            df_buch.columns = df_buch.columns.str.strip()
            if 'Ueberweisen_An' not in df_buch.columns:
                df_buch['Ueberweisen_An'] = ''
            if df_buch.empty:
                df_buch = pd.DataFrame(columns=cols_buch)
            else:
                for col in cols_buch:
                    if col not in df_buch.columns:
                        if col == "Beschreibung" and "Text" in df_buch.columns:
                            df_buch["Beschreibung"] = df_buch["Text"]
                        elif col == "Betrag":
                            df_buch[col] = 0.0
                        else:
                            df_buch[col] = ""

            df_buch['ID'] = df_buch['ID'].astype(str).str.replace(r"\.0$", "", regex=True).str.strip().str.upper()
            df_buch['Betrag'] = df_buch['Betrag'].apply(parse_amount).fillna(0.0)
            df_buch['Beschreibung'] = df_buch['Beschreibung'].astype(str)
            if 'Ueberweisen_An' in df_buch.columns:
                df_buch['Ueberweisen_An'] = df_buch['Ueberweisen_An'].astype(str).replace(['nan', 'None'], '').fillna('')
            df_buch = sanitize_status_columns(df_buch)
            if 'Status' in df_buch.columns and 'Betrag' in df_buch.columns:
                _st = df_buch['Status'].astype(str).str.strip().replace(['nan','None'], '')
                _missing = _st.eq('')
                if _missing.any():
                    df_buch.loc[_missing & (df_buch['Betrag'] > 0), 'Status'] = 'Erledigt'
                    df_buch.loc[_missing & (df_buch['Betrag'] <= 0), 'Status'] = 'Offen'
            return df_buch
        except Exception as e:
            if "429" in str(e) or "Quota" in str(e):
                time.sleep(2 + attempt)
                continue
            st.error(f"Datenbankfehler (Buchungen): {e}")
            break
    return pd.DataFrame(columns=cols_buch)


def load_data(full: bool = True):
    """Kompatibilitäts-Wrapper.

    * full=False: nur Stammdaten + Klassenblatt (schneller Start / Login)
    * full=True : zusätzlich Buchungen (für eingeloggte Bereiche / Salden)
    """
    df_stamm = load_stammdaten()
    df_klassen = load_klassenblatt()
    df_buch = load_buchungen() if full else pd.DataFrame(columns=["Datum", "Zeitstempel", "ID", "Name", "Beschreibung", "Betrag", "Erfasst_Von", "Ueberweisen_An", "Status"])
    return df_stamm, df_buch, df_klassen



def update_password(email, new_password_plain):
    try:
        df_stamm = conn.read(worksheet="Stammdaten", ttl=0) 
        mask = df_stamm['Email'].astype(str).str.strip().str.lower() == email.lower()
        if mask.any():
            hashed_pw = hash_password(new_password_plain)
            df_stamm.loc[mask, 'Passwort'] = hashed_pw
            df_stamm.loc[mask, 'Muss_Passwort_Aendern'] = "nein"
            conn.update(worksheet="Stammdaten", data=df_stamm); st.cache_data.clear(); return True
        return False
    except Exception as e: st.error(f"Fehler: {e}"); return False

def admin_reset_user_password(target_email, new_plain_pw, force_change_next_login):
    try:
        df_fresh = conn.read(worksheet="Stammdaten", ttl=0)
        mask = df_fresh['Email'].astype(str).str.strip().str.lower() == target_email.lower()
        if mask.any():
            hashed_pw = hash_password(new_plain_pw)
            df_fresh.loc[mask, 'Passwort'] = hashed_pw
            df_fresh.loc[mask, 'Muss_Passwort_Aendern'] = "Ja" if force_change_next_login else "nein"
            conn.update(worksheet="Stammdaten", data=df_fresh)
            st.cache_data.clear()
            return True
        return False
    except Exception as e:
        st.error(f"DB Fehler: {e}")
        return False

def update_class_message(klasse, message):
    try:
        df_kl = conn.read(worksheet="Klassen", ttl=0)
        if 'Klasse' not in df_kl.columns: return False
        if klasse in df_kl['Klasse'].values: df_kl.loc[df_kl['Klasse'] == klasse, 'Nachricht'] = message
        else: new_row = pd.DataFrame([{"Klasse": klasse, "Nachricht": message}]); df_kl = pd.concat([df_kl, new_row], ignore_index=True)
        conn.update(worksheet="Klassen", data=df_kl); st.cache_data.clear(); return True
    except Exception as e: st.error(f"Fehler: {e}"); return False

def save_buchung_batch(neue_buchungen_df):
    """Speichert neue Buchungen (Append) + Duplikat-Schutz (BuchungsHash)."""
    try:
        if neue_buchungen_df is None or len(neue_buchungen_df) == 0:
            return True

        df_in = neue_buchungen_df.copy()
        if 'BuchungsHash' not in df_in.columns:
            df_in['BuchungsHash'] = ''
        try:
            df_in['BuchungsHash'] = df_in.apply(lambda r: compute_buchung_hash(r.to_dict()), axis=1)
        except Exception:
            df_in['BuchungsHash'] = [compute_buchung_hash(r) for r in df_in.to_dict(orient='records')]

        try:
            ws = conn.client.open_by_key(conn.spreadsheet).worksheet('Buchungen')
            header = ws.row_values(1)
            if not header:
                header = list(df_in.columns)
                ws.append_row(header, value_input_option='USER_ENTERED')

            if 'BuchungsHash' not in header:
                header = header + ['BuchungsHash']
                ws.update('A1', [header])

            try:
                col_idx = header.index('BuchungsHash') + 1
                existing = set(x.strip() for x in ws.col_values(col_idx)[1:] if str(x).strip())
            except Exception:
                existing = set()

            df2 = df_in[~df_in['BuchungsHash'].astype(str).isin(existing)].copy()
            if len(df2) == 0:
                return True

            for h in header:
                if h not in df2.columns:
                    df2[h] = ''
            df2 = df2[header]
            df2 = df2.where(pd.notna(df2), '')
            ws.append_rows(df2.astype(str).values.tolist(), value_input_option='USER_ENTERED')
            # st.cache_data.clear()
            return True
        except Exception:
            pass

        df_buch = conn.read(worksheet="Buchungen", ttl=0)
        if 'BuchungsHash' in df_buch.columns:
            existing = set(df_buch['BuchungsHash'].astype(str).str.strip().tolist())
            df_in = df_in[~df_in['BuchungsHash'].astype(str).isin(existing)].copy()
            if len(df_in) == 0:
                return True
        df_neu = pd.concat([df_buch, df_in], ignore_index=True)
        conn.update(worksheet="Buchungen", data=df_neu)
        st.cache_data.clear()
        return True

    except Exception as e:
        st.error(f"Speicherfehler: {e}")
        return False


def save_buchung_einzeln(
    datum,
    id_val,
    name,
    klasse,
    text,
    betrag,
    user,
    status="Erledigt",
    ueberweisen_an=""
):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        "Datum": datum.strftime("%Y-%m-%d"),
        "Zeitstempel": now,
        "ID": str(id_val).upper(),
        "Name": name,
        "Klasse": klasse,
        "Beschreibung": text,
        "Betrag": float(betrag),
        "Erfasst_Von": user,
        "Ueberweisen_An": ueberweisen_an,
        "Status": status
    }
    return save_buchung_batch(pd.DataFrame([entry]))

def update_buchungs_status(df_updated):
    try: conn.update(worksheet="Buchungen", data=df_updated); st.cache_data.clear(); return True
    except Exception as e: st.error(f"Update Fehler: {e}"); return False



def preview_schuljahreswechsel(df_stamm: pd.DataFrame, df_klassen: pd.DataFrame, action_map: dict | None = None, max_grade: int = 4):
    """Vorschau + Sicherheits-Check für den Schuljahreswechsel.

    Gültige Klassenformate:
      - 1a, 2b, 3c, 4d (Zahl 1-max_grade + ein Buchstabe)
      - PTSa, PTSb, PTSc (Abschlussklassen)
      - Historisch im Klassenblatt: *_alt (wird ignoriert)

    action_map (optional): dict {"1a": "Aufstieg"|"Archiv"|"Keine"}.
      - Wenn None: Standard: 1-3 Aufstieg, 4x + PTS Archiv.

    Rückgabe (dict):
      ok (bool)
      counts: schueler_total, schueler_promote, schueler_archiv
      invalid_students, invalid_staff_tokens, invalid_klassen
      archive_list: Liste (ID/Name/Klasse) für Archiv
    """
    pat_num = re.compile(rf'^[1-{max_grade}][A-Za-z]$')
    def _norm(x):
        return str(x).strip().replace(' ', '').replace('nan', '')

    def _class_key(x):
        return _norm(x).upper()

    action_map_norm = {_class_key(k): str(v) for k, v in (action_map or {}).items()}

    def _is_pts(c: str) -> bool:
        return _class_key(c).startswith('PTS')

    def _is_valid_class(c: str) -> bool:
        cc = _norm(c)
        if cc.lower().endswith('_alt'):
            return True
        return bool(pat_num.match(cc)) or _is_pts(cc)

    def _default_action(cls: str) -> str:
        cc = _norm(cls)
        if not cc:
            return 'Keine'
        if cc.lower().endswith('_alt'):
            return 'Keine'
        if _is_pts(cc):
            return 'Archiv'
        if pat_num.match(cc):
            g = int(cc[0])
            return 'Archiv' if g >= max_grade else 'Aufstieg'
        return 'Keine'

    def _action_for(cls: str) -> str:
        cc = _norm(cls)
        key = _class_key(cc)
        if key in action_map_norm:
            return str(action_map_norm.get(key) or 'Keine')
        return _default_action(cc)

    invalid_students = []
    invalid_staff_tokens = []
    invalid_klassen = []

    if df_stamm is None or df_stamm.empty:
        return {
            'ok': True,
            'counts': {'schueler_total': 0, 'schueler_promote': 0, 'schueler_archiv': 0},
            'invalid_students': [],
            'invalid_staff_tokens': [],
            'invalid_klassen': [],
            'archive_list': [],
        }

    ds = df_stamm.copy()
    ds.columns = ds.columns.astype(str).str.strip()
    for c in ['Rolle','Name','Klasse','ID','Email']:
        if c not in ds.columns:
            ds[c] = ''

    is_student = ds['Rolle'].astype(str).str.lower().str.contains('schüler')
    stud = ds[is_student].copy()
    stud['Klasse_norm'] = stud['Klasse'].astype(str).apply(_norm)

    archive_list = []
    promote_cnt = 0
    archiv_cnt = 0

    for _, r in stud.iterrows():
        cls = r.get('Klasse_norm','')
        nm = str(r.get('Name',''))
        sid = str(r.get('ID',''))
        # Schüler-Klasse muss gültig sein
        if not cls or not _is_valid_class(cls) or cls.lower().endswith('_alt'):
            invalid_students.append({'Name': nm, 'ID': sid, 'Klasse': str(r.get('Klasse',''))})
            continue
        act = _action_for(cls)
        if act == 'Archiv':
            archiv_cnt += 1
            archive_list.append({'ID': sid, 'Name': nm, 'Klasse': cls})
        elif act == 'Aufstieg':
            promote_cnt += 1

    # Lehrer/Admin Tokens prüfen
    is_staff = ds['Rolle'].astype(str).str.lower().str.contains('lehrer|admin')
    staff = ds[is_staff].copy()
    for _, r in staff.iterrows():
        raw = str(r.get('Klasse','') or '')
        if not raw or raw.lower() == 'nan':
            continue
        tokens = [t.strip() for t in re.split(r'[,;]+', raw) if t.strip()]
        for t in tokens:
            tn = _norm(t)
            if not tn:
                continue
            if not _is_valid_class(tn) or tn.lower().endswith('_alt'):
                invalid_staff_tokens.append({'Name': str(r.get('Name','')), 'Email': str(r.get('Email','')), 'Klasse_Token': t})

    # Klassen-Sheet prüfen (historische *_alt ignorieren)
    if df_klassen is not None and not df_klassen.empty:
        dk = df_klassen.copy()
        dk.columns = dk.columns.astype(str).str.strip()
        if 'Klasse' not in dk.columns:
            dk['Klasse'] = ''
        for k in dk['Klasse'].astype(str).tolist():
            kn = _norm(k)
            if not kn:
                continue
            if kn.lower().endswith('_alt'):
                continue
            if not _is_valid_class(kn):
                invalid_klassen.append({'Klasse': k})

    ok = (len(invalid_students) == 0 and len(invalid_staff_tokens) == 0 and len(invalid_klassen) == 0)

    return {
        'ok': ok,
        'counts': {
            'schueler_total': int(len(stud)),
            'schueler_promote': int(promote_cnt),
            'schueler_archiv': int(archiv_cnt),
        },
        'invalid_students': invalid_students,
        'invalid_staff_tokens': invalid_staff_tokens,
        'invalid_klassen': invalid_klassen,
        'archive_list': archive_list,
    }
def perform_jahreswechsel(df_buch, df_stamm, action_map: dict, max_grade: int = 4):
    """Schuljahreswechsel mit Klassen-Auswahl.

    action_map: dict {"1a": "Aufstieg"|"Archiv"|"Keine"}

    Regeln:
      - Archivieren (Schüler) ist nur erlaubt, wenn Kontostand (Summe Buchungen) == 0.00
      - Klassenblatt: IBAN/BIC/Nachricht bleiben erhalten
          * Aufstieg: Klasse wird hochgestuft
          * Archiv: Klasse wird zu <Klasse>_alt umbenannt (nicht gelöscht)

    Rückgabe: (success: bool, info: dict|str)
    """
    try:
        ph = st.empty()
        prog = None
        try:
            prog = ph.progress(0, text="Schuljahreswechsel: starte …")
        except Exception:
            prog = None

        def _p(v, t):
            try:
                if prog is not None:
                    prog.progress(v, text=t)
            except Exception:
                pass

        def _norm_class(s: str) -> str:
            return str(s).strip().replace(" ", "").replace("nan", "")

        pat_num = re.compile(rf'^[1-{max_grade}][A-Za-z]$')
        cls_rx = re.compile(r'^(?P<grade>[1-9][0-9]?)(?P<suf>[A-Za-z].*)$')
        def _class_key(s: str) -> str:
            return _norm_class(s).upper()

        action_map_norm = {_class_key(k): str(v) for k, v in (action_map or {}).items()}

        def _is_pts(c: str) -> bool:
            return _class_key(c).startswith('PTS')

        def _promote_label(c: str) -> str:
            cc = _norm_class(c)
            m = cls_rx.match(cc)
            if not m:
                return cc
            g = int(m.group('grade'))
            suf = m.group('suf')
            return f"{g+1}{suf}"

        def _action_for(cls: str) -> str:
            cc = _norm_class(cls)
            return str(action_map_norm.get(_class_key(cc), 'Keine') or 'Keine')

        def promote_teacher_field(val: str) -> str:
            raw = str(val or "").strip()
            if not raw or raw.lower() == 'nan':
                return ""
            parts = [p.strip() for p in re.split(r'[,;]+', raw) if p.strip()]
            out = []
            for p in parts:
                c = _norm_class(p)
                if not c:
                    continue
                act = _action_for(c)
                if act == 'Archiv':
                    continue
                if act == 'Aufstieg':
                    out.append(_promote_label(c))
                else:
                    out.append(c)
            # unique
            seen=set(); uniq=[]
            for x in out:
                k=x.lower()
                if k not in seen:
                    seen.add(k); uniq.append(x)
            return ",".join(uniq)

        _p(10, "Schuljahreswechsel: lade Stammdaten/Klassen/Archiv …")
        df_s = conn.read(worksheet="Stammdaten", ttl=0)
        df_s.columns = df_s.columns.str.strip()
        for c in ["Rolle","Name","Klasse","ID","Email","Zugangscode","Passwort","Muss_Passwort_Aendern"]:
            if c not in df_s.columns:
                df_s[c] = ""
        df_s["ID"] = df_s["ID"].astype(str).str.replace(r"\.0$", "", regex=True).str.strip().str.upper()
        df_s["Klasse"] = df_s["Klasse"].astype(str).replace("nan", "").apply(_norm_class)

        try:
            df_k = conn.read(worksheet="Klassen", ttl=0)
            df_k.columns = df_k.columns.str.strip()
        except Exception:
            df_k = pd.DataFrame(columns=["Klasse", "IBAN", "BIC", "Empfaenger", "Nachricht"])
        for c in ["Klasse", "IBAN", "BIC", "Empfaenger", "Nachricht"]:
            if c not in df_k.columns:
                df_k[c] = ""
        df_k["Klasse"] = df_k["Klasse"].astype(str).replace("nan", "").apply(_norm_class)

        # Sicherheits-Check (gültige Klassenformate)
        prev = preview_schuljahreswechsel(df_s, df_k, action_map=action_map, max_grade=max_grade)
        if not prev.get('ok', True):
            return False, {'msg': 'Ungültiges Klassenformat gefunden. Bitte korrigieren.', 'preview': prev}

        # --- Saldo-Check für Archiv-Klassen (muss 0 sein) ---
        _p(18, "Schuljahreswechsel: Saldo-Check für Archiv …")
        df_b = df_buch if df_buch is not None else pd.DataFrame(columns=['ID','Betrag'])
        if not df_b.empty:
            df_b2 = df_b.copy()
            if 'ID' in df_b2.columns:
                df_b2['ID'] = df_b2['ID'].astype(str).str.replace(r"\.0$","",regex=True).str.strip().str.upper()
            if 'Betrag' in df_b2.columns:
                df_b2['Betrag'] = pd.to_numeric(df_b2['Betrag'], errors='coerce').fillna(0.0)
            salden = df_b2.groupby('ID')['Betrag'].sum()
        else:
            salden = pd.Series(dtype=float)

        is_student = df_s["Rolle"].astype(str).str.lower().str.contains("schüler")
        stud = df_s[is_student].copy()
        stud['Klasse'] = stud['Klasse'].astype(str).apply(_norm_class)
        stud['ID'] = stud['ID'].astype(str).str.upper()
        stud['Saldo'] = stud['ID'].map(salden).fillna(0.0)

        archive_class_keys = {k for k, v in action_map_norm.items() if str(v) == 'Archiv'}
        stud['KlasseKey'] = stud['Klasse'].apply(_class_key)
        unsettled = stud[stud['KlasseKey'].isin(archive_class_keys) & (stud['Saldo'].abs() > 0.009)][['Name','ID','Klasse','Saldo']]
        if not unsettled.empty:
            return False, {
                'msg': 'Archivieren ist nicht erlaubt, solange Kontostände nicht 0 sind.',
                'unsettled': unsettled.to_dict(orient='records'),
            }

        archiv_log = prev.get('archive_list', [])
        df_a = load_archiv_sheet()
        dt = datetime.now().strftime("%Y-%m-%d")

        # 1) Archivieren: alle Schüler deren Klasse auf Archiv gesetzt ist
        _p(30, "Schuljahreswechsel: Abschlussklassen archivieren …")
        idx_to_archive = stud[stud['KlasseKey'].isin(archive_class_keys)].index.tolist()
        ids_to_archive = stud.loc[idx_to_archive, 'ID'].astype(str).tolist() if idx_to_archive else []

        if ids_to_archive:
            moved = df_s.loc[idx_to_archive].copy()
            moved["Archiv_Datum"] = dt
            moved["Archiv_Jahr"] = dt
            moved["Archiv_Grund"] = "Schuljahreswechsel (Archiv per Klassen-Auswahl)"
            if "Zugangscode" in moved.columns: moved["Zugangscode"] = ""
            if "Passwort" in moved.columns: moved["Passwort"] = hash_password(generate_random_code(24))
            if "Muss_Passwort_Aendern" in moved.columns: moved["Muss_Passwort_Aendern"] = "Ja"

            cols_arch = ["Rolle","Name","Klasse","ID","Email","Zugangscode","Passwort","Muss_Passwort_Aendern","Archiv_Datum","Archiv_Jahr","Archiv_Grund"]
            for c in cols_arch:
                if c not in moved.columns:
                    moved[c] = ""
            moved = moved[cols_arch]

            if not df_a.empty:
                df_a["ID"] = df_a["ID"].astype(str).str.replace(r"\.0$","",regex=True).str.strip().str.upper()
                df_a = df_a[~df_a["ID"].isin([x.upper() for x in ids_to_archive])]
            df_a2 = pd.concat([df_a, moved], ignore_index=True)
        else:
            df_a2 = df_a

        # 2) Stammdaten: Archivierte entfernen, Klassen nach action_map behandeln
        _p(45, "Schuljahreswechsel: Stammdaten aktualisieren …")
        df_s2 = df_s.drop(index=idx_to_archive).copy() if idx_to_archive else df_s.copy()

        # Schüler: Aufstieg, Archiv wurde entfernt
        idx_students2 = df_s2[df_s2["Rolle"].astype(str).str.lower().str.contains("schüler")].index
        for idx in idx_students2:
            c = _norm_class(df_s2.at[idx, 'Klasse'])
            act = _action_for(c)
            if act == 'Aufstieg' and (pat_num.match(c) is not None):
                df_s2.at[idx, 'Klasse'] = _promote_label(c)

        # Lehrer/Admin: Klassenliste aktualisieren
        idx_staff = df_s2[df_s2["Rolle"].astype(str).str.lower().str.contains("lehrer|admin")].index
        for idx in idx_staff:
            df_s2.at[idx, 'Klasse'] = promote_teacher_field(df_s2.at[idx, 'Klasse'])

        # 3) Klassenblatt: IBAN behalten, Klassen umbenennen
        _p(55, "Schuljahreswechsel: Klassen-Stammdaten aktualisieren …")
        new_rows = []
        for _, row in df_k.iterrows():
            oldc = _norm_class(row.get('Klasse',''))
            if not oldc:
                continue
            row2 = row.copy()
            if oldc.lower().endswith('_alt'):
                new_rows.append(row2)
                continue
            act = _action_for(oldc)
            if act == 'Archiv':
                row2['Klasse'] = f"{oldc}_alt"
            elif act == 'Aufstieg' and (cls_rx.match(oldc) is not None):
                row2['Klasse'] = _promote_label(oldc)
            else:
                row2['Klasse'] = oldc
            new_rows.append(row2)

        df_k2 = pd.DataFrame(new_rows) if new_rows else pd.DataFrame(columns=df_k.columns)
        if not df_k2.empty:
            df_k2['Klasse'] = df_k2['Klasse'].astype(str).apply(_norm_class)
            df_k2 = df_k2.drop_duplicates(subset=['Klasse'], keep='first')

        # 4) Neue Buchungen: nur Saldo-Überträge
        _p(70, "Schuljahreswechsel: Überträge erstellen …")
        if df_buch is None or df_buch.empty:
            salden_df = pd.DataFrame(columns=['ID','Betrag'])
        else:
            salden_df = df_buch.groupby('ID')['Betrag'].sum().reset_index()
            salden_df = salden_df[abs(salden_df['Betrag']) > 0.009]

        now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        today = datetime.today().strftime("%Y-%m-%d")
        name_map = dict(zip(df_s['ID'].astype(str).str.upper(), df_s['Name'].astype(str)))
        if df_a2 is not None and not df_a2.empty:
            name_map.update(dict(zip(df_a2['ID'].astype(str).str.upper(), df_a2['Name'].astype(str))))

        new_entries = []
        for _, row in salden_df.iterrows():
            sv = str(row['ID']).strip().upper()
            if sv and sv != 'NAN':
                new_entries.append({
                    'Datum': today,
                    'Zeitstempel': now_ts,
                    'ID': sv,
                    'Name': name_map.get(sv, 'Unbekannt'),
                    'Klasse': class_map.get(sv, ''),
                    'Beschreibung': 'Übertrag Vorjahr',
                    'Betrag': float(row['Betrag']),
                    'Erfasst_Von': 'System',
                    'Status': 'Erledigt',
                })
        df_new_buch = pd.DataFrame(new_entries) if new_entries else pd.DataFrame(columns=["Datum","Zeitstempel","ID","Name","Beschreibung","Betrag","Erfasst_Von","Status"])

        # 5) Schreiben
        _p(85, "Schuljahreswechsel: speichere Änderungen …")
        try:
            conn.client.open_by_key(conn.spreadsheet).worksheet('Buchungen').clear()
        except Exception:
            pass
        conn.update(worksheet='Buchungen', data=df_new_buch)
        conn.update(worksheet='Stammdaten', data=df_s2)
        conn.update(worksheet='Klassen', data=df_k2)
        save_archiv_sheet(df_a2)

        st.cache_data.clear()
        _p(100, "Schuljahreswechsel: fertig ✅")
        try:
            ph.empty()
        except Exception:
            pass

        return True, {
            'uebertraege': int(len(df_new_buch)),
            'archiviert': int(len(ids_to_archive)),
            'stamm_gesamt': int(len(df_s2)),
            'archiv_log': archiv_log,
        }

    except Exception as e:
        try:
            ph.empty()
        except Exception:
            pass
        return False, str(e)
def load_archiv_sheet():
    """Lädt Worksheet 'Archiv'. Falls nicht vorhanden -> leeres DataFrame."""
    cols = ["Rolle","Name","Klasse","ID","Email","Zugangscode","Passwort","Muss_Passwort_Aendern","Archiv_Datum","Archiv_Jahr","Archiv_Grund"]
    try:
        df_a = conn.read(worksheet="Archiv")
        df_a.columns = df_a.columns.str.strip()
        for c in cols:
            if c not in df_a.columns: df_a[c] = ""
        df_a["ID"] = df_a["ID"].astype(str).str.replace(r"\.0$","",regex=True).str.strip().str.upper()
        df_a["Email"] = df_a["Email"].astype(str).str.strip().str.lower()
        # Wunsch: In Spalte Archiv_Jahr steht das Datum der Archivierung
        df_a["Archiv_Datum"] = df_a["Archiv_Datum"].astype(str).replace("nan", "")
        df_a["Archiv_Jahr"] = df_a["Archiv_Jahr"].astype(str).replace("nan", "")
        df_a.loc[df_a["Archiv_Jahr"].str.strip() == "", "Archiv_Jahr"] = df_a["Archiv_Datum"]
        return df_a
    except Exception:
        return pd.DataFrame(columns=cols)

def save_archiv_sheet(df_archiv: pd.DataFrame):
    try:
        conn.update(worksheet="Archiv", data=df_archiv)
        st.cache_data.clear()
        return True, "Archiv gespeichert"
    except Exception as e:
        return False, str(e)

def archive_students(student_ids: list, reason: str = ""):
    """Verschiebt ausgewählte Schüler aus Stammdaten ins Archiv."""
    try:
        # Progressanzeige (damit beim Speichern keine Unsicherheit entsteht)
        prog_placeholder = st.empty()
        prog = None
        try:
            prog = prog_placeholder.progress(0, text="Archivieren: starte …")
        except Exception:
            prog = None
        def _p(val, txt):
            try:
                if prog is not None: prog.progress(val, text=txt)
            except Exception:
                pass
        _p(10, "Archivieren: lade Stammdaten …")
        ids = [str(x).strip().upper() for x in student_ids if str(x).strip()]
        if not ids: return False, "Keine Auswahl"
        df_s = conn.read(worksheet="Stammdaten", ttl=0)
        _p(25, "Archivieren: Schüler auswählen …")
        df_s.columns = df_s.columns.str.strip()
        if "ID" not in df_s.columns: return False, "Stammdaten ohne ID"
        df_s["ID"] = df_s["ID"].astype(str).str.replace(r"\.0$","",regex=True).str.strip().str.upper()
        mask = (df_s.get("Rolle", "") == "Schüler") & df_s["ID"].isin(ids)
        if not mask.any(): return False, "Keine passenden Schüler gefunden"
        moved = df_s.loc[mask].copy()
        _p(40, "Archivieren: Archiv laden …")
        dt = datetime.now().strftime("%Y-%m-%d")
        moved["Archiv_Datum"] = dt
        moved["Archiv_Jahr"] = dt  # Datum in Archiv_Jahr
        moved["Archiv_Grund"] = str(reason)[:200]
        # Zugang sperren: Code leeren + Passwort randomisieren
        if "Zugangscode" in moved.columns: moved["Zugangscode"] = ""
        if "Passwort" in moved.columns: moved["Passwort"] = hash_password(generate_random_code(24))
        if "Muss_Passwort_Aendern" in moved.columns: moved["Muss_Passwort_Aendern"] = "Ja"
        df_a = load_archiv_sheet()
        _p(60, "Archivieren: Daten vorbereiten …")
        cols_arch = ["Rolle","Name","Klasse","ID","Email","Zugangscode","Passwort","Muss_Passwort_Aendern","Archiv_Datum","Archiv_Jahr","Archiv_Grund"]
        for c in cols_arch:
            if c not in moved.columns: moved[c] = ""
        moved = moved[cols_arch]
        # im Archiv: gleicher ID-Eintrag? -> überschreiben (neueste Archivierung gewinnt)
        if not df_a.empty:
            df_a["ID"] = df_a["ID"].astype(str).str.replace(r"\.0$","",regex=True).str.strip().str.upper()
            df_a = df_a[~df_a["ID"].isin(moved["ID"].astype(str).tolist())]
        df_a2 = pd.concat([df_a, moved], ignore_index=True)
        # Stammdaten ohne die verschobenen Schüler speichern
        df_s2 = df_s.loc[~mask].copy()
        _p(80, "Archivieren: schreibe Stammdaten …")
        conn.update(worksheet="Stammdaten", data=df_s2)
        _p(90, "Archivieren: schreibe Archiv …")
        save_archiv_sheet(df_a2)
        st.cache_data.clear()
        _p(100, "Archivieren: fertig ✅")
        try:
            prog_placeholder.empty()
        except Exception:
            pass
        return True, f"{int(mask.sum())} Schüler archiviert"
    except Exception as e:
        try:
            if prog_placeholder: prog_placeholder.empty()
        except Exception:
            pass
        return False, str(e)

def delete_students_from_archiv(student_ids: list):
    """Löscht ausgewählte Schüler endgültig aus dem Archiv."""
    try:
        # Progressanzeige
        prog_placeholder = st.empty()
        prog = None
        try:
            prog = prog_placeholder.progress(0, text="Löschen: starte …")
        except Exception:
            prog = None
        def _p(val, txt):
            try:
                if prog is not None: prog.progress(val, text=txt)
            except Exception:
                pass
        _p(15, "Löschen: Archiv laden …")
        ids = [str(x).strip().upper() for x in student_ids if str(x).strip()]
        if not ids: return False, "Keine Auswahl"
        df_a = load_archiv_sheet()
        _p(40, "Löschen: Auswahl prüfen …")
        if df_a.empty: return False, "Archiv ist leer"
        df_a["ID"] = df_a["ID"].astype(str).str.replace(r"\.0$","",regex=True).str.strip().str.upper()
        mask = (df_a.get("Rolle", "") == "Schüler") & df_a["ID"].isin(ids)
        if not mask.any(): return False, "Keine passenden Schüler im Archiv"
        df_a2 = df_a.loc[~mask].copy()
        _p(80, "Löschen: schreibe Archiv …")
        save_archiv_sheet(df_a2)
        st.cache_data.clear()
        _p(100, "Löschen: fertig ✅")
        try:
            prog_placeholder.empty()
        except Exception:
            pass
        return True, f"{int(mask.sum())} Schüler aus Archiv gelöscht"
    except Exception as e:
        try:
            if prog_placeholder: prog_placeholder.empty()
        except Exception:
            pass
        return False, str(e)

def render_student_details_ui(df_stamm, df_buch, allowed_classes=None, key_suffix=""):
    all_classes_in_db = sorted([k for k in df_stamm[df_stamm['Rolle']=='Schüler']['Klasse'].unique() if k and str(k)!="nan"])
    if allowed_classes is not None:
        allowed_norm = [c.strip().lower() for c in allowed_classes]
        final_classes = [c for c in all_classes_in_db if c.strip().lower() in allowed_norm]
    else:
        final_classes = all_classes_in_db
        
    if not final_classes:
        st.warning("Keine Klassen zugewiesen.")
        return

    sel_klasse = st.selectbox("Klasse wählen:", final_classes, key=f"det_kl_{key_suffix}")
    
    if sel_klasse:
        studs = df_stamm[(df_stamm['Klasse']==sel_klasse) & (df_stamm['Rolle']=='Schüler')].sort_values('Name')
        if not studs.empty:
            sel_student_name = st.selectbox("Schüler wählen:", studs['Name'].tolist(), key=f"det_st_{key_suffix}")
            
            if sel_student_name:
                row_s = studs[studs['Name'] == sel_student_name].iloc[0]
                sv = row_s['ID']
                my_bookings = df_buch[df_buch['ID'] == sv].copy()
                
                st.markdown("---")
                c1, c2 = st.columns([1, 3])
                saldo = my_bookings['Betrag'].sum()
                
                with c1:
                    delta_col = "normal" if saldo >= 0 else "inverse"
                    st.metric("Aktueller Kontostand", f"{saldo:.2f} €", delta_color=delta_col)
                    st.caption(f"ID: {sv}")
                    if 'Zugangscode' in row_s and str(row_s['Zugangscode']) != "nan":
                         st.info(f"🔑 Code: **{row_s['Zugangscode']}**")
                
                with c2:
                    if not my_bookings.empty:
                        my_bookings['Datum'] = pd.to_datetime(my_bookings['Datum']).dt.strftime(DATE_DISPLAY_FMT)
                        my_bookings = my_bookings.sort_values('Zeitstempel', ascending=False)
                        def highlight_amount(val): return f'color: {"#d9534f" if val < 0 else "#28a745"}; font-weight: bold'
                        st.dataframe(my_bookings[['Datum', 'Beschreibung', 'Betrag', 'Erfasst_Von', 'Status']].style.map(highlight_amount, subset=['Betrag']).format({"Betrag": "{:.2f} €"}), use_container_width=True, hide_index=True)
                    else: st.info("Noch keine Buchungen vorhanden.")
        else: st.warning("Klasse ist leer.")

# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------
# 5. UI - HAUPTPROGRAMM
# -----------------------------------------------------------------------------

# Session-State früh initialisieren (verhindert „falschen Startbildschirm“ beim ersten Run)
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "force_pw_change" not in st.session_state:
    st.session_state.force_pw_change = False

# Cache-Container für Buchungen (lazy)
if 'df_buch_cached' not in st.session_state:
    st.session_state.df_buch_cached = None

# Premium UI CSS injizieren
inject_premium_ui_css()

# Für den Start / Login laden wir nur die schnellen Tabellen (Stammdaten + Klassen)
# Buchungen werden erst dann geladen, wenn sie wirklich gebraucht werden.
df_stamm, _df_buch_placeholder, df_klassen = load_data(full=False)

# Sidebar erst aufbauen, wenn jemand eingeloggt ist (keine „falsche“ Navigation beim Start)

if st.session_state.user_email and not st.session_state.force_pw_change:
    st.sidebar.header("Navigation")
else:
    # Sidebar bewusst minimal halten, damit kein „falscher Startbildschirm“ aufblitzt
    st.sidebar.empty()

user_role = "Gast"; user_name = "Unbekannt"; user_klasse = "" 

# Premium UI CSS injizieren
inject_premium_ui_css()

# User-Daten (falls eingeloggt) aus Stammdaten ermitteln
if st.session_state.user_email and 'Email' in df_stamm.columns:
    r = df_stamm[df_stamm['Email'] == st.session_state.user_email]
    if not r.empty:
        muss_aendern = str(r.iloc[0].get('Muss_Passwort_Aendern', '')).strip().lower()
        if muss_aendern in ["ja", "yes", "true", "1"]:
            st.session_state.force_pw_change = True
        user_role = r.iloc[0].get('Rolle', 'Gast')
        user_name = r.iloc[0].get('Name', 'Unbekannt')
        user_klasse = str(r.iloc[0].get('Klasse', '')).strip()
    else:
        st.session_state.user_email = None
        st.session_state.force_pw_change = False

# Sidebar-Status
if st.session_state.user_email and not st.session_state.force_pw_change:
    st.sidebar.success(f"👤 {user_name}")
    st.sidebar.caption(f"Rolle: {user_role}")
    if user_role == "Lehrer":
        if user_klasse:
            st.sidebar.caption(f"KV für: {user_klasse}")
        else:
            st.sidebar.warning("Keine KV-Klasse hinterlegt.")
    if st.sidebar.button("Daten neu laden"):
        st.cache_data.clear()
        st.session_state.df_buch_cached = None
        st.rerun()
    if st.sidebar.button("Abmelden", type="primary"):
        st.session_state.user_email = None
        st.session_state.force_pw_change = False
        st.rerun()
else:
    st.sidebar.info("Nicht eingeloggt")

st.sidebar.markdown("---")
st.sidebar.caption("MS Niederndorf v30.4")

# --- PREMIUM STARTSEITE (Zentriertes Login) ---

def _render_logo_center():
    logo_path = 'logo.png'
    if os.path.exists(logo_path):
        # Streamlit kann Bilder nicht direkt in HTML rendern, daher ein kleines st.image oberhalb.
        st.image(logo_path, width=90)


def _get_buchungen_lazy():
    """Lädt Buchungen nur bei Bedarf (Cache + Session)."""
    if st.session_state.df_buch_cached is None:
        st.session_state.df_buch_cached = load_buchungen()
    return st.session_state.df_buch_cached

def render_centered_login():
    # Remember-Email innerhalb der Session
    if 'remember_email' not in st.session_state:
        st.session_state.remember_email = True
    if 'remembered_email' not in st.session_state:
        st.session_state.remembered_email = ""

    _l, mid, _r = st.columns([1, 2, 1])
    with mid:
        st.markdown('<div class="kk-center"><div class="kk-card">', unsafe_allow_html=True)

        # Logo (zentriert)
        st.markdown('<div class="kk-logo-wrap">', unsafe_allow_html=True)
                # Brand (Logo + Headline) exakt zentriert
        if os.path.exists('logo.png'):
            try:
                with open('logo.png', 'rb') as _f:
                    _b64 = base64.b64encode(_f.read()).decode('utf-8')
                st.markdown(
                    f"""<div class='kk-brand'>
                          <div class='kk-logo-wrap'>
                            <img class='kk-logo-img' src='data:image/png;base64,{_b64}' />
                          </div>
                          <div class='kk-title'>Klassenkonto</div>
                        </div>
                        <div style='height:10px'></div>""",
                    unsafe_allow_html=True,
                )
            except Exception:
                st.image('logo.png', width=120)
                st.markdown("<div class='kk-title'>Klassenkonto</div><div style='height:10px'></div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='kk-title'>Klassenkonto</div><div style='height:10px'></div>", unsafe_allow_html=True)

        tab_fam, tab_staff = st.tabs(["👨‍👩‍👧 Familien-Login", "⚙️ Lehrer/Admin"])

        with tab_staff:
            st.markdown("<span class='kk-pill'>🔐 Lehrer/Admin Anmeldung</span>", unsafe_allow_html=True)

            # Premium UX: remember email + show password
            c1, c2 = st.columns([1.2, 1])
            with c1:
                remember = st.checkbox("E-Mail merken (Session)", value=bool(st.session_state.remember_email))
                st.session_state.remember_email = remember
            with c2:
                show_pw = st.checkbox("Passwort anzeigen", value=False)

            # Soft error UX container
            with st.form("login_form_center", clear_on_submit=False):
                email_input = st.text_input("E-Mail", value=st.session_state.remembered_email, placeholder="name@schule.at")
                pass_input = st.text_input("Passwort", type="default" if show_pw else "password")
                submit = st.form_submit_button("Anmelden", type="primary")

            if submit:
                email_clean = email_input.strip().lower()
                user_found = df_stamm[df_stamm['Email'] == email_clean] if 'Email' in df_stamm.columns else pd.DataFrame()
                if not user_found.empty:
                    stored_pass = str(user_found.iloc[0].get('Passwort', '')).strip()
                    input_hashed = hash_password(pass_input.strip())
                    valid = (stored_pass == input_hashed) or (stored_pass == pass_input.strip())
                    if valid:
                        st.session_state.user_email = email_clean
                        if st.session_state.remember_email:
                            st.session_state.remembered_email = email_clean
                        toast('success', 'Anmeldung erfolgreich')
                        time.sleep(0.35)
                        st.rerun()
                    else:
                        st.error("❌ Passwort stimmt nicht. Tipp: Groß-/Kleinschreibung prüfen.")
                else:
                    st.error("❌ Diese E-Mail ist nicht registriert.")



        with tab_fam:
            st.markdown("<span class='kk-pill'>🔑 Zugangscode (Eltern)</span>", unsafe_allow_html=True)
            try:
                url_code = st.query_params.get("code", "")
            except Exception:
                url_code = ""
            c = url_code if url_code else ""
            ic = st.text_input("Bitte Zugangscode eingeben:", value=c, type="password", placeholder="Zugangscode")

            if ic:
                # Fehlversuchs-Sperre (Brute-Force-Schutz)
                locked, rem = fam_check_lockout(prefix='fam', max_tries=5, base_lock_s=60)
                if locked:
                    st.warning(f"Zu viele Fehlversuche. Bitte {rem} Sekunden warten.")
                    st.stop()
                clean_code = ic.strip()
                if 'Zugangscode' in df_stamm.columns:
                    r = df_stamm[df_stamm['Zugangscode'] == clean_code]
                    if not r.empty:
                        d = r.iloc[0]
                        student_name = d.get('Name', '')
                        student_class = d.get('Klasse', '')
                        fam_reset_lockout(prefix='fam'); st.info(f"Schüler: **{student_name}** ({student_class})")

                        if not df_klassen.empty:
                            msg_row = df_klassen[df_klassen['Klasse'] == student_class]
                            if not msg_row.empty:
                                msg_text = str(msg_row.iloc[0].get('Nachricht', ''))
                                if msg_text and msg_text != "nan":
                                    st.warning(f"📢 Nachricht von der Schule:\n\n{msg_text}")

                        sv = str(d.get('ID', '')).replace(".0", "").strip().upper()
                        b = _get_buchungen_lazy()[_get_buchungen_lazy()['ID'] == sv].copy() if sv else pd.DataFrame()

                        sal = 0.0
                        if not b.empty:
                            sal = b['Betrag'].sum()

                        col_delta = "normal" if sal >= 0 else "inverse"
                        st.metric("Guthaben", f"{sal:.2f} €", delta_color=col_delta)

                        # QR-Code
                        if not df_klassen.empty:
                            kr = df_klassen[df_klassen['Klasse'] == student_class]
                            if not kr.empty:
                                iban = kr.iloc[0].get('IBAN', '')
                                st.write(f"IBAN: {iban}")
                                bic = kr.iloc[0].get('BIC', '') if 'BIC' in kr.columns else ""
                                empf = kr.iloc[0].get('Empfaenger', '') if 'Empfaenger' in kr.columns else ""

                                if not empf or str(empf) == "nan":
                                    empf = "MS Niederndorf"

                                if iban:
                                    amount_qr = abs(sal) if sal < 0 else 0.00

                                    if sal < 0:
                                        st.warning(f"Aktueller Fehlbetrag: {abs(sal):.2f} €")

                                    st.write("Scannen Sie diesen Code mit Ihrer Banking-App für eine einfache Überweisung.")

                                    qr_text = f"{sv} {student_name}"
                                    qr_buffer = generate_epc_qr(
                                        iban,
                                        bic,
                                        empf,
                                        amount_qr,
                                        qr_text
                                    )

                                    if qr_buffer:
                                        st.image(qr_buffer, width=200)

                        if not b.empty:

                            b = b.sort_values('Datum', ascending=False)
                            b['Datum'] = pd.to_datetime(b['Datum']).dt.strftime(DATE_DISPLAY_FMT)
                            def col(v):
                                return f'color: {"#ff6b6b" if v < 0 else "#39d98a"}; font-weight: bold'
                            st.dataframe(
                                b[['Datum', 'Betrag', 'Beschreibung']]
                                .style.map(col, subset=['Betrag'])
                                .format({"Betrag": "{:.2f} €"}),
                                column_config={
                                    "Datum": st.column_config.TextColumn(
                                        "Datum",
                                        width="small"
                                    ),
                                    "Betrag": st.column_config.TextColumn(
                                        "Betrag",
                                        width="small"
                                    ),
                                    "Beschreibung": st.column_config.TextColumn(
                                        "Beschreibung",
                                        width="large"
                                    ),
                                },
                                hide_index=True,
                                use_container_width=True,
                            )
                        else:
                            st.info("Keine Umsätze.")

                            # PDF
                            if not df_klassen.empty:
                                kr = df_klassen[df_klassen['Klasse'] == student_class]
                                if not kr.empty:
                                    iban = kr.iloc[0].get('IBAN', '')
                                    bic = kr.iloc[0].get('BIC', '') if 'BIC' in kr.columns else ""
                                    empf = kr.iloc[0].get('Empfaenger', '') if 'Empfaenger' in kr.columns else ""
                                    if not empf or str(empf) == "nan":
                                        empf = "MS Niederndorf"
                                    pdf_bytes = create_pdf_report(student_name, student_class, b, iban, bic, empf, sv)
                                else:
                                    pdf_bytes = create_pdf_report(student_name, student_class, b)
                            else:
                                pdf_bytes = create_pdf_report(student_name, student_class, b)

                            st.download_button(
                                "📄 Kontoauszug (PDF)",
                                data=pdf_bytes,
                                file_name=f"Kontoauszug_{student_name}.pdf",
                                mime='application/pdf',
                            )
                        
                    else:
                        fam_register_fail(prefix='fam', max_tries=5, base_lock_s=60); time.sleep(0.6); st.error("Code ungültig.")
                else:
                    st.error("Wartung: Datenbankfehler.")

        st.markdown('</div></div>', unsafe_allow_html=True)


def render_centered_password_change():
    _l, mid, _r = st.columns([1, 2, 1])
    with mid:
        st.markdown('<div class="kk-center"><div class="kk-card">', unsafe_allow_html=True)
        st.markdown('<div class="kk-title">### 🔒 Passwort ändern</div>', unsafe_allow_html=True)
        st.markdown('<div class="kk-sub">Aus Sicherheitsgründen müssen Sie Ihr Passwort ändern.</div>', unsafe_allow_html=True)
        st.info("Regeln: Min. 12 Zeichen, Groß- und Kleinbuchstaben, Zahlen.")
        with st.form("change_pw", clear_on_submit=False):
            p1 = st.text_input("Neues Passwort", type="password")
            p2 = st.text_input("Wiederholen", type="password")
            submit_pw = st.form_submit_button("Speichern", type="primary")
        if submit_pw:
            if p1 != p2:
                st.error("Passwörter ungleich")
            else:
                is_secure, msg = check_password_strength(p1)
                if not is_secure:
                    st.error(f"❌ {msg}")
                else:
                    if update_password(st.session_state.user_email, p1):
                        toast('success', '✅ Passwort geändert')
                        st.session_state.force_pw_change = False
                        time.sleep(0.6)
                        st.rerun()
        st.markdown('</div></div>', unsafe_allow_html=True)
# --- MENÜ ---
# Falls ein Passwortwechsel erzwungen wird, zentriert anzeigen und beenden.
if st.session_state.user_email and st.session_state.force_pw_change:
    render_centered_password_change()
    st.stop()

# Wenn niemand (Lehrer/Admin) eingeloggt ist, zeigen wir die Startseite (zentriert) und beenden.
if not st.session_state.user_email:
    render_centered_login()
    st.divider(); st.caption("MS Niederndorf v30.4 (Secure & Private)")
    st.stop()

options = []
if user_role == "Lehrer":
    options.append("Lehrer")
elif user_role == "Admin":
    options.extend(["Admin", "Lehrer"])
# -----------------------------------------------------------------------------
# Login-/Passwort-Flow: Auf der ersten Seite ausschließlich Login anzeigen
# (verhindert, dass kurz ein anderer Screen „aufblitzt“)
# -----------------------------------------------------------------------------
if st.session_state.force_pw_change:
    render_centered_password_change()
    st.stop()

if not st.session_state.user_email:
    render_centered_login()
    st.stop()

# Ab hier ist der User eingeloggt -> Buchungen für Salden/Übersichten bereitstellen
# (wird gecached; Start vor Login bleibt schnell)
df_buch = _get_buchungen_lazy()

menu = st.sidebar.radio("Navigation:", options)

# -----------------------------------------------------------------------------
# Login-Hinweis: offene Auszahlungen / Verbuchungsstatus
# -----------------------------------------------------------------------------
def render_open_payout_notice():
    try:
        if user_role not in ["Lehrer", "Admin"]:
            return
        if df_buch is None or df_buch.empty:
            st.info("ℹ️ Keine Buchungen vorhanden – es gibt aktuell keine offenen Auszahlungen.")
            return

        df_open = df_buch.copy()
        for col in ["Betrag", "Status", "Erfasst_Von", "Datum", "Name", "Beschreibung", "Ueberweisen_An"]:
            if col not in df_open.columns:
                df_open[col] = ""

        df_open["Betrag"] = pd.to_numeric(df_open["Betrag"], errors="coerce").fillna(0.0)
        df_open["Status"] = df_open["Status"].astype(str).str.strip()

        offene = df_open[(df_open["Betrag"] < 0) & (df_open["Status"] != "Erledigt")].copy()
        if user_role == "Lehrer":
            offene = offene[
                offene["Erfasst_Von"].astype(str).str.strip()
                == str(user_name).strip()
            ].copy()
            zieltext = "für dich"
        else:
            zieltext = "insgesamt"

        grp = offene.groupby(
            ['Datum', 'Beschreibung', 'Erfasst_Von', 'Ueberweisen_An'],
            dropna=False
        ).agg(
            Anzahl=('ID', 'count'),
            Gesamtbetrag=('Betrag', 'sum')
        ).reset_index()

        if offene.empty:
            st.success(f"✅ Hinweis: Es sind {zieltext} keine offenen Auszahlungen vorhanden. Die offenen Beträge scheinen verbucht/erledigt zu sein.")
            return

        offene_summe = abs(float(offene["Betrag"].sum()))
        st.warning(
            f"⚠️ Es sind {zieltext} noch "
            f"{len(grp)} offene Sammelbuchungen "
            f"mit insgesamt {offene_summe:.2f} €"
        )



    except Exception:
        # Hinweis darf die App nicht blockieren.
        pass

render_open_payout_notice()

# -----------------------------------------------------------------------------
# WIEDERVERWENDBARE BUCHUNGS-FUNKTION (CENT-GENAU, AUTO/MANUELL, LIVE-SALDO)
# -----------------------------------------------------------------------------
def render_booking_ui(is_teacher=False, preselected_class=None, multi_class=True):
    """Buchen-UI im Look der Screenshots.

    - Cent-genaue Verteilung bei "Gesamtsumme aufteilen"
    - Auto/Manuell Umschalter (Auto sperrt Betragsspalte; Auto->Manuell übernimmt Auto-Werte als Start)
    - Live-Saldo pro Schüler
    - ID nicht sichtbar (intern _id)

    Duplikate (deutlicher):
    - Vor dem Speichern prüfen wir die BuchungsHashes gegen bestehende Einträge.
    - Wenn alles Duplikate: klare Warnung, KEINE Luftballons.

    OFFEN:
    - Nach erfolgreichem Speichern wird df_buch_cached geleert, damit OFFEN sofort aktualisiert.
    """

    prefix = "t_" if is_teacher else "s_"

    def cent_split(total_eur: float, n: int):
        total_cent = int(round(float(total_eur) * 100))
        if n <= 0:
            return []
        base = total_cent // n
        rest = total_cent % n
        cents = [base] * n
        for i in range(rest):
            cents[i] += 1
        return [c / 100.0 for c in cents]

    def _pop_keys(keys):
        for k in keys:
            try:
                st.session_state.pop(k, None)
            except Exception:
                pass

    # 1) Klasse

    st.markdown("")

    all_classes = sorted([
        k for k in df_stamm[df_stamm['Rolle'] == 'Schüler']['Klasse'].unique()
        if k and str(k) != 'nan'
    ])

    if not all_classes:
        st.warning("Keine Klassen gefunden.")
        return None

    default_idx = (
        all_classes.index(preselected_class)
        if preselected_class in all_classes
        else 0
    )

    if multi_class:
        sel_klassen = st.multiselect(
            "Klassen auswählen",
             all_classes,
             default=[all_classes[default_idx]],
             key=f"{prefix}klasse_sel"
        )
    else:
        sel_klassen = st.selectbox(
            "Klasse auswählen",
            all_classes,
            index=default_idx,
            key=f"{prefix}klasse_sel_single"
        )

    st.markdown(" ")

    

    # 2) Typ/Datum/Zweck
    c1, c2, c3 = st.columns([1.2, 1.1, 2])

    with c1:
        typ = st.radio(
            "Typ",
            ["Ausgabe (-)", "Einzahlung (+)"],
            horizontal=True,
            key=f"{prefix}typ"
        )

    with c2:
        date_val = st.date_input(
            "Datum",
            key=f"{prefix}datum"
        )

    with c3:
        text_val = st.text_input(
            "Zweck / Beschreibung",
            key=f"{prefix}zweck"
        )

    # 3) Verteilung/Betrag/Auto
    c4, c5, c6 = st.columns([1.5, 1, 1])

    with c4:
        dist_mode = st.radio(
            "Verteilung",
            ["Fester Betrag pro Kopf", "Gesamtsumme aufteilen"],
            horizontal=True,
            key=f"{prefix}dist",
        )

    with c5:
        amount_label = "Betrag pro Schüler (€)" if dist_mode == "Fester Betrag pro Kopf" else "Gesamtsumme (€)"

        selected_key = "_".join(sorted(sel_klassen))
        sel_klasse = selected_key
        amount_key = f"{prefix}amt_txt_{selected_key}"

        if amount_key not in st.session_state:
            st.session_state[amount_key] = ""

        amount_raw = st.text_input(
            amount_label,
            placeholder="z.B. 12,50",
            key=amount_key,
            help="Du kannst einfach tippen – kein 0,00 zum Löschen. Komma oder Punkt möglich.",
        )

        amount = parse_amount(amount_raw, 0.0)

    with c6:
        auto_mode = st.toggle("Auto", value=True, key=f"{prefix}auto")

    payee_val = ""

    if typ == "Ausgabe (-)":

        empfaenger_liste = sorted(
            df_stamm[
                df_stamm["Rolle"].astype(str).str.strip().isin(["Admin", "Lehrer"])
            ]["Name"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        payee_val = st.selectbox(
            "💸 Überweisen an (Empfänger) *",
            options=["Bitte Empfänger wählen...", "Direktion"] + empfaenger_liste,
            key=f"{prefix}payee"
        )

        if payee_val == "Bitte Empfänger wählen...":
            payee_val = ""

        if not str(payee_val).strip():
            st.info("ℹ️ Pflichtfeld: Ohne Empfänger kann bei Ausgabe nicht gebucht werden.")

    st.divider()

    # 4) Schüler
    df_class = df_stamm[
        (df_stamm['Klasse'].isin(sel_klassen)) &
        (df_stamm['Rolle'] == 'Schüler')
    ][['ID', 'Name', 'Klasse']].copy().sort_values(['Klasse', 'Name'])

    if df_class.empty:
        st.warning("Keine Schüler.")
        return None

    df_class['ID'] = df_class['ID'].astype(str).str.strip().str.upper()
    all_ids = set(df_class['ID'].tolist())



        # 5) Live-Salden
    saldo_map = {}

    try:
        if df_buch is not None and not df_buch.empty:
            tmp = df_buch.copy()
            tmp['ID'] = tmp['ID'].astype(str).str.strip().str.upper()
            tmp['Betrag'] = pd.to_numeric(tmp['Betrag'], errors='coerce').fillna(0.0)
            saldo_map = tmp.groupby('ID')['Betrag'].sum().to_dict()
    except Exception:
        saldo_map = {}

    # 6) State
    selected_key = "_".join(sorted(sel_klassen))

    sel_klasse = selected_key

    key_sel = f"{prefix}exclude_{selected_key}"
    key_amt = f"{prefix}amt_map_{selected_key}"
    key_prev_auto = f"{prefix}prev_auto_{selected_key}"
    key_auto_sig = f"{prefix}auto_sig_{selected_key}"

    ed_key_l = f"{prefix}ed_{selected_key}_L"
    ed_key_r = f"{prefix}ed_{selected_key}_R"

    if key_sel not in st.session_state:
        st.session_state[key_sel] = set()

    if key_amt not in st.session_state or not isinstance(st.session_state.get(key_amt), dict):
        st.session_state[key_amt] = {}

    if key_prev_auto not in st.session_state:
        st.session_state[key_prev_auto] = True

    excluded = set(str(x).strip().upper() for x in st.session_state[key_sel])
    amt_map = st.session_state[key_amt]

    # 7) Buttons
    b1, b2, b3 = st.columns(3)
    with b1:
        if st.button("✅ Alle", key=f"{prefix}all_{sel_klasse}"):
            st.session_state[key_sel] = set()

            for sid in all_ids:
                sel_key = f"{prefix}man_sel_{sel_klasse}_{sid}"
                st.session_state[sel_key] = True

    with b2:
        if st.button("⬜ Keine", key=f"{prefix}none_{sel_klasse}"):
            st.session_state[key_sel] = set(all_ids)

            for sid in all_ids:
                sel_key = f"{prefix}man_sel_{sel_klasse}_{sid}"
                st.session_state[sel_key] = False

    with b3:
        if st.button("🔁 Invertieren", key=f"{prefix}inv_{sel_klasse}"):

            cur = set(str(x).strip().upper() for x in st.session_state[key_sel])
            st.session_state[key_sel] = set(all_ids) - cur

            for sid in all_ids:
                sel_key = f"{prefix}man_sel_{sel_klasse}_{sid}"
                st.session_state[sel_key] = not bool(
                    st.session_state.get(sel_key, True)
                )

    excluded = set(str(x).strip().upper() for x in st.session_state[key_sel])
    selected = sorted(list(all_ids - excluded))

    # 8) Auto-Verteilung
    if dist_mode == "Gesamtsumme aufteilen":
        split_vals = cent_split(amount, len(selected))
        dist_map = {sid: v for sid, v in zip(selected, split_vals)}
    else:
        per = round(float(amount), 2)
        dist_map = {sid: per for sid in selected}

    prev_auto = bool(st.session_state.get(key_prev_auto, True))
    if prev_auto and (not auto_mode):
        for sid in selected:
            amt_map[str(sid)] = float(dist_map.get(sid, 0.0))
        for sid in excluded:
            amt_map[str(sid)] = 0.0
        st.session_state[key_amt] = amt_map
    st.session_state[key_prev_auto] = auto_mode

    # 9) DF
    rows = []
    for _, r in df_class.iterrows():
        sid = str(r['ID']).strip().upper()
        is_sel = sid not in excluded
        val = float(dist_map.get(sid, 0.0)) if (auto_mode and is_sel) else float(amt_map.get(sid, 0.0)) if (not auto_mode and is_sel) else 0.0
        saldo = float(saldo_map.get(sid, 0.0))
        rows.append({'Klasse': r['Klasse'], 'Auswahl': bool(is_sel), 'Schüler': r['Name'], 'Betrag €': float(val), 'Saldo €': float(saldo), '_id': sid})

    df_view = pd.DataFrame(rows)

    # Reset editor when inputs changed
    auto_sig = (bool(auto_mode), str(dist_mode), round(float(amount or 0.0), 2), tuple(selected))
    if auto_mode and st.session_state.get(key_auto_sig) != auto_sig:
        st.session_state[key_auto_sig] = auto_sig
        _pop_keys([ed_key_l, ed_key_r])

    # 11) Editor / Manuelle Eingabe
    # Auto-Modus bleibt wie bisher im data_editor.
    # Manuell-Modus wird bewusst mit einzelnen Eingabefeldern gerendert, weil der data_editor
    # bei mehreren Betragseingaben nach Reruns einzelne Werte wieder auf 0,00 zurücksetzen kann.
    if not auto_mode:
        # Enter-Taste: in der manuellen Betragserfassung zum nächsten Eingabefeld springen.
        # Hinweis: Das Script läuft nur im Manuell-Modus dieser Buchungsmaske.
        components.html(
            """
            <script>
            (function () {
              const doc = window.parent.document;

              function visible(el) {
                if (!el) return false;
                const style = window.parent.getComputedStyle(el);
                const rect = el.getBoundingClientRect();
                return style.display !== 'none' && style.visibility !== 'hidden' && rect.width > 0 && rect.height > 0;
              }

              function inputs() {
                return Array.from(doc.querySelectorAll('input'))
                  .filter(el => visible(el))
                  .filter(el => !el.disabled && !el.readOnly)
                  .filter(el => ['text', 'number', 'search', ''].includes((el.getAttribute('type') || 'text').toLowerCase()))
                  .filter(el => (el.getAttribute('placeholder') || '') === '0,00');
              }

              function bindEnterFocus() {
                inputs().forEach(function (el) {
                  if (el.dataset.enterNextBound === '1') return;
                  el.dataset.enterNextBound = '1';
                  el.addEventListener('keydown', function (ev) {
                    if (ev.key !== 'Enter') return;
                    ev.preventDefault();
                    ev.stopPropagation();
                    const list = inputs();
                    const idx = list.indexOf(el);
                    if (idx >= 0 && idx < list.length - 1) {
                      list[idx + 1].focus();
                      try { list[idx + 1].select(); } catch (e) {}
                    }
                  });
                });
              }

              bindEnterFocus();
              setTimeout(bindEnterFocus, 300);
              setTimeout(bindEnterFocus, 900);
              const observer = new MutationObserver(bindEnterFocus);
              observer.observe(doc.body, { childList: true, subtree: true });
            })();
            </script>
            """,
            height=0,
        )

        st.caption("Manuelle Beträge: Werte werden je Schüler stabil gespeichert. Mit Enter springst du zum nächsten Betragsfeld.")
        manual_rows = []
        mid = len(df_view) // 2 + 1
        col_l, col_r = st.columns(2)

        def _render_manual_header():
            h_sel, h_name, h_amt, h_saldo = st.columns([0.5, 2.5, 1.2, 1.1])
            with h_sel:
                st.markdown("**✓**")
            with h_name:
                st.markdown("**Schüler**")
            with h_amt:
                st.markdown("**Betrag €**")
            with h_saldo:
                st.markdown("**Saldo**")

        def _render_manual_rows(df_part):
            out = []
            for _, row in df_part.iterrows():
                sid = str(row['_id']).strip().upper()
                name = f"[{row['Klasse']}] {row['Schüler']}"
                saldo = float(row.get('Saldo €', 0.0) or 0.0)

                sel_key = f"{prefix}man_sel_{sel_klasse}_{sid}"
                amt_key = f"{prefix}man_amt_{sel_klasse}_{sid}"
                valid_key = f"{prefix}man_amt_valid_{sel_klasse}_{sid}"

                if sel_key not in st.session_state:
                    st.session_state[sel_key] = bool(sid not in excluded)
                if amt_key not in st.session_state:
                    start_val = float(amt_map.get(sid, row.get('Betrag €', 0.0)) or 0.0)
                    st.session_state[amt_key] = "" if abs(start_val) < 0.0001 else f"{start_val:.2f}".replace('.', ',')
                if valid_key not in st.session_state:
                    st.session_state[valid_key] = float(amt_map.get(sid, row.get('Betrag €', 0.0)) or 0.0)

                c_sel, c_name, c_amt, c_saldo = st.columns([0.5, .5, 1.2, 1.1])
                with c_sel:
                    ausgew = st.checkbox("", key=sel_key, label_visibility="collapsed")
                with c_name:
                    st.write(name)
                with c_amt:
                    raw_amt = st.text_input(
                        "Betrag €",
                        key=amt_key,
                        label_visibility="collapsed",
                        placeholder="0,00",
                    )
                with c_saldo:
                    st.write(f"{saldo:.2f} €")

                raw_clean = str(raw_amt or "").strip()
                if raw_clean:
                    wert = float(parse_amount(raw_clean, st.session_state.get(valid_key, 0.0)))
                    st.session_state[valid_key] = wert
                else:
                    wert = 0.0
                    st.session_state[valid_key] = 0.0

                if not ausgew:
                    wert = 0.0

                out.append({
                    'Klasse': row['Klasse'],
                    'Auswahl': bool(ausgew),
                    'Schüler': name,
                    'Betrag €': float(wert),
                    'Saldo €': saldo,
                    '_id': sid
                })
            return out

        with col_l:
            _render_manual_header()
            manual_rows.extend(_render_manual_rows(df_view.iloc[:mid]))
        with col_r:
            _render_manual_header()
            manual_rows.extend(_render_manual_rows(df_view.iloc[mid:]))

        edited = pd.DataFrame(manual_rows)
        new_excl = set(edited.loc[edited['Auswahl'] == False, '_id'].astype(str).str.upper().tolist())
        st.session_state[key_sel] = new_excl

        for _, row in edited.iterrows():
            sid = str(row['_id']).strip().upper()
            if bool(row['Auswahl']):
                amt_map[sid] = float(row.get('Betrag €', 0.0) or 0.0)
            else:
                amt_map[sid] = 0.0
        st.session_state[key_amt] = amt_map

    else:
        cfg = {
            'Auswahl': st.column_config.CheckboxColumn('✓'),
            'Schüler': st.column_config.TextColumn('Schüler', disabled=True),
            'Betrag €': st.column_config.NumberColumn('Betrag €', min_value=0.0, step=0.01),
            'Saldo €': st.column_config.NumberColumn('Saldo €', disabled=True, format='%.2f €'),
            '_id': None,
        }
        disabled_cols = ['Schüler', 'Saldo €', 'Betrag €']

        mid = len(df_view) // 2 + 1
        col_l, col_r = st.columns(2)
        with col_l:
            ed1 = st.data_editor(df_view.iloc[:mid], column_config=cfg, hide_index=True, disabled=disabled_cols, key=ed_key_l, use_container_width=True, height=520)
        with col_r:
            ed2 = st.data_editor(df_view.iloc[mid:], column_config=cfg, hide_index=True, disabled=disabled_cols, key=ed_key_r, use_container_width=True, height=520)

        edited = pd.concat([ed1, ed2], ignore_index=True)

        # 12) Checkbox change -> auto recompute
        new_excl = set(edited.loc[edited['Auswahl'] == False, '_id'].astype(str).str.upper().tolist())
        if new_excl != excluded:
            st.session_state[key_sel] = new_excl
            new_selected = sorted(list(all_ids - new_excl))
            st.session_state[key_auto_sig] = (True, str(dist_mode), round(float(amount or 0.0), 2), tuple(new_selected))
            _pop_keys([ed_key_l, ed_key_r])
            st.rerun()

        st.session_state[key_sel] = new_excl

    # Total
    total = float(pd.to_numeric(edited.loc[edited['Auswahl'] == True, 'Betrag €'], errors='coerce').fillna(0.0).sum())
    st.markdown("### Gesamtbetrag")
    st.markdown(f"## {total:.2f} €")

    # 14) Buchen
    must_payee = (typ == "Ausgabe (-)")
    can_book = bool(str(text_val).strip()) and (total > 0.0) and ((not must_payee) or bool(str(payee_val).strip()))

    if st.button("✅ Buchen durchführen", type="primary", key=f"{prefix}btn_book_{sel_klasse}", disabled=(not can_book)):
        target_status = "Offen" if typ == "Ausgabe (-)" else "Erledigt"
        now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date_str = date_val.strftime("%Y-%m-%d")

        batch = []
        for _, row in edited.iterrows():
            if bool(row['Auswahl']):
                sid = str(row['_id']).strip().upper()
                name = str(row['Schüler'])
                val = float(row.get('Betrag €', 0.0) or 0.0)
                if typ == "Ausgabe (-)":
                    val *= -1
                if abs(val) > 0.0001:
                    batch.append({
                        'Datum': date_str,
                        'Zeitstempel': now_ts,
                        'ID': sid,
                        'Name': name,
                        'Klasse': row['Klasse'],
                        'Beschreibung': text_val,
                        'Betrag': float(val),
                        'Erfasst_Von': user_name,
                        'Ueberweisen_An': payee_val,
                        'Status': target_status,
                    })

        if batch:
            df_batch = pd.DataFrame(batch)
            # --- Duplikate VORHER prüfen ---
            existing = set()
            try:
                ws = conn.client.open_by_key(conn.spreadsheet).worksheet('Buchungen')
                header = ws.row_values(1)
                if 'BuchungsHash' in header:
                    col_idx = header.index('BuchungsHash') + 1
                    existing = set(x.strip() for x in ws.col_values(col_idx)[1:] if str(x).strip())
            except Exception:
                try:
                    df_old = conn.read(worksheet='Buchungen', ttl=0)
                    if 'BuchungsHash' in df_old.columns:
                        existing = set(df_old['BuchungsHash'].astype(str).str.strip().tolist())
                except Exception:
                    existing = set()

            # Hash berechnen für neue
            df_batch['BuchungsHash'] = df_batch.apply(lambda r: compute_buchung_hash(r.to_dict()), axis=1)
            is_new = ~df_batch['BuchungsHash'].astype(str).isin(existing)
            added = int(is_new.sum())
            dups = int((~is_new).sum())

            if added == 0 and dups > 0:
                st.warning("⛔ Doppelbuchung erkannt: Diese Buchung war bereits vorhanden und wurde NICHT gespeichert.")
                return sel_klasse

            if dups > 0:
                st.info(f"ℹ️ {dups} Duplikat(e) wurden erkannt und werden ignoriert.")

            df_to_save = df_batch[is_new].drop(columns=['BuchungsHash'], errors='ignore').copy()
            ok = save_buchung_batch(df_to_save)

            if ok:
                st.success(f"✅ Gespeichert ({added} neu)")
                if added > 0:
                    st.balloons()

                # Feinschliff: manuelle Betragsfelder nach erfolgreicher Buchung leeren.
                try:
                    if not auto_mode:
                        for _sid in df_class['ID'].astype(str).str.strip().str.upper().tolist():
                            st.session_state[f"{prefix}man_amt_{sel_klasse}_{_sid}"] = ""
                            st.session_state[f"{prefix}man_amt_valid_{sel_klasse}_{_sid}"] = 0.0
                        st.session_state[key_amt] = {}
                except Exception:
                    pass

                # Cache leeren -> OFFEN aktualisiert sofort
                try:
                    st.session_state.df_buch_cached = None
                except Exception:
                    pass
                time.sleep(0.6)
                st.rerun()
            else:
                st.error("Speichern fehlgeschlagen.")

    return sel_klasse
# -----------------------------------------------------------------------------
# LEHRER BEREICH
# -----------------------------------------------------------------------------
if menu == "Lehrer" and user_role in ["Lehrer", "Admin"]:
    st.header(f"🧾 Finanzen (Lehrer) - {user_name}")

    # Klassenvorstand-Heuristik:
    # - Lehrer mit eingetragener Klasse (user_klasse) => KV
    # - Admin sieht ebenfalls Klassenumsätze
    kv_classes = [c.strip() for c in str(user_klasse).split(",") if c and str(c).strip() and str(c).strip().lower() != "nan"]
    is_kv = (user_role == "Admin") or (len(kv_classes) > 0)

    tab_labels = ["✍️ Buchen", "🧾 Meine Umsätze"]
    if is_kv:
        tab_labels.append("🏫 Klassenumsätze")
    tab_labels.append("📊 Kontostände & Verlauf")

    tabs = st.tabs(tab_labels)
    tab_buchen = tabs[0]
    tab_meine = tabs[1]
    tab_klasse = tabs[2] if is_kv else None
    tab_ueberblick = tabs[3] if is_kv else tabs[2]

    def _show_umsatz_table(df_in: pd.DataFrame, key_prefix: str):
        if df_in is None or df_in.empty:
            st.info("Keine Umsätze vorhanden.")
            return
        df = df_in.copy()
        # Datum parsen für Zeitraumfilter
        if 'Datum' in df.columns:
            df['Datum_dt'] = pd.to_datetime(df['Datum'], errors='coerce', dayfirst=True)
        else:
            df['Datum_dt'] = pd.NaT

        # Zeitraumfilter
        if df['Datum_dt'].notna().any():
            min_d = df['Datum_dt'].min()
            max_d = df['Datum_dt'].max()
            try:
                dr = st.date_input("Zeitraum", value=(min_d.date(), max_d.date()), key=f"{key_prefix}_dr")
                if isinstance(dr, (tuple, list)) and len(dr) == 2:
                    d0, d1 = dr
                    df = df[(df['Datum_dt'].dt.date >= d0) & (df['Datum_dt'].dt.date <= d1)]
            except Exception:
                pass

        # Kennzahlen
        if 'Betrag' in df.columns:
            ein = float(df.loc[df['Betrag'] > 0, 'Betrag'].sum())
            aus = float(-df.loc[df['Betrag'] < 0, 'Betrag'].sum())
            net = float(df['Betrag'].sum())
        else:
            ein = aus = net = 0.0
        c1, c2, c3 = st.columns(3)
        c1.metric("Einnahmen", f"{ein:.2f} €")
        c2.metric("Ausgaben", f"{aus:.2f} €")
        c3.metric("Saldo", f"{net:.2f} €")

        # Sortierung
        if 'Zeitstempel' in df.columns:
            df = df.sort_values('Zeitstempel', ascending=False)
        elif 'Datum_dt' in df.columns:
            df = df.sort_values('Datum_dt', ascending=False)
        # Datum für Anzeige formatieren (ohne interne Logik zu verändern)
        df_disp = df.copy()
        if 'Datum' in df_disp.columns:
            if 'Datum_dt' in df_disp.columns:
                df_disp['Datum'] = df_disp['Datum_dt'].dt.strftime(DATE_DISPLAY_FMT)
                df_disp['Datum'] = df_disp['Datum'].fillna(df['Datum'].apply(format_date_display))
            else:
                df_disp['Datum'] = df_disp['Datum'].apply(format_date_display)

        

        show_cols = [c for c in ["Datum", "Zeitstempel", "ID", "Name", "Beschreibung", "Betrag", "Status", "Ueberweisen_An", "Erfasst_Von"] if c in df.columns]
        st.dataframe(df_disp[show_cols] if show_cols else df_disp, use_container_width=True, height=520)

        # Download
        try:
            csv = df_disp[show_cols].to_csv(index=False).encode('utf-8') if show_cols else df_disp.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ CSV herunterladen", csv, file_name=f"{key_prefix}.csv", mime="text/csv")
        except Exception:
            pass

    with tab_buchen:
        selected_class_for_view = render_booking_ui(is_teacher=True, preselected_class=None, multi_class=True)

    with tab_meine:
        st.subheader("Meine Umsätze")
        df_my = df_buch.copy() if df_buch is not None else pd.DataFrame()
        if not df_my.empty and 'Erfasst_Von' in df_my.columns:
            df_my = df_my[df_my['Erfasst_Von'].astype(str) == str(user_name)]
        _show_umsatz_table(df_my, key_prefix=f"meine_umsaetze_{user_name}")

    if is_kv and tab_klasse is not None:
        with tab_klasse:
            st.subheader("Klassenumsätze")
            # Klasse wählen (bei mehreren KV-Klassen)
            sel_kv = kv_classes[0] if len(kv_classes) == 1 else st.selectbox("Klasse", kv_classes, key="kv_sel_klasse")

            if sel_kv:
                curr_stud = df_stamm[(df_stamm['Klasse'] == sel_kv) & (df_stamm['Rolle'] == 'Schüler')].sort_values('Name')
                sv_list = curr_stud['ID'].astype(str).tolist() if not curr_stud.empty else []
                df_cls = df_buch[df_buch['ID'].isin(sv_list)].copy() if (df_buch is not None and sv_list) else pd.DataFrame()
                _show_umsatz_table(df_cls, key_prefix=f"klassen_umsaetze_{sel_kv}")
            else:
                st.info("Keine Klasse hinterlegt.")

    with tab_ueberblick:
        st.subheader("Kontostände")
        # Die Übersicht bezieht sich auf die zuletzt gewählte Klasse
        if user_role == "Admin":
            all_classes = sorted([
                k for k in df_stamm[df_stamm['Rolle'] == 'Schüler']['Klasse'].unique()
                if pd.notna(k)
            ])

            selected_class_for_view = st.selectbox(
                "Klasse",
                all_classes,
                key="konto_klasse"
            )

        elif is_kv:
            selected_class_for_view = kv_classes[0]

        else:
            selected_class_for_view = None
        

        sel_clean = str(selected_class_for_view).strip().lower()
        my_classes = [c.strip().lower() for c in str(user_klasse).split(",") if c and str(c).strip() and str(c).strip().lower() != "nan"]
        is_kv_for_selected = (user_role == "Admin") or (user_role == "Lehrer" and sel_clean in my_classes)
        
        if is_kv_for_selected:
            if selected_class_for_view:
                curr_stud = df_stamm[(df_stamm['Klasse'].isin(selected_class_for_view if isinstance(selected_class_for_view, list) else [selected_class_for_view])) & (df_stamm['Rolle'] == 'Schüler')].sort_values('Name')
                if not curr_stud.empty:
                    sv_list = curr_stud['ID'].astype(str).tolist()
                    # Salden je Schüler berechnen – ALLE Schüler der Klasse anzeigen (auch ohne Buchungen)

                    ums = df_buch[df_buch['ID'].isin(sv_list)]

                    saldo_df = ums.groupby('ID', as_index=False)['Betrag'].sum() if not ums.empty else pd.DataFrame(columns=['ID','Betrag'])

                    sald = (curr_stud[['ID','Name']]

                            .merge(saldo_df, on='ID', how='left')

                            .fillna({'Betrag': 0.0})

                            .sort_values('Name'))

                    def col(v):
                        return f'color: {"#ff6b6b" if v<0 else "#39d98a"}; font-weight: bold'

                    mid = math.ceil(len(sald)/2)
                    c1, c2 = st.columns(2)
                    with c1:
                        st.dataframe(sald.iloc[:mid][['Name','Betrag']].style.map(col, subset=['Betrag']).format({"Betrag":"{:.2f} €"}), hide_index=True, use_container_width=True)
                    with c2:
                        st.dataframe(sald.iloc[mid:][['Name','Betrag']].style.map(col, subset=['Betrag']).format({"Betrag":"{:.2f} €"}), hide_index=True, use_container_width=True)

                    st.markdown('---')
                    st.subheader("Detail-Ansicht (Verlauf)")
                    allowed_cls = my_classes if user_role == "Lehrer" else None
                    # Verlauf: nur die IDs der Klasse
                    df_view = ums.copy()
                    if not df_view.empty:
                        show_cols = [c for c in ["Datum","Zeitstempel","Name","Beschreibung","Betrag","Erfasst_Von","Status","Ueberweisen_An"] if c in df_view.columns]
                        df_view_disp = format_date_columns(df_view, cols=['Datum'])
                        st.dataframe(df_view_disp[show_cols] if show_cols else df_view_disp, use_container_width=True, height=520)
                else:
                    st.info("Keine Schüler in dieser Klasse.")
            else:
                st.info("Bitte zuerst unter 'Buchen' eine Klasse wählen.")
        else:
            st.info(f"🔒 Kontostände für {selected_class_for_view} nur für den Klassenvorstand sichtbar.")

elif menu == "Admin" and user_role == "Admin":
    st.header(f"🔐 Verwaltung ({user_name})")
    st.divider()
    admin_group = st.radio("Bereich:", ["💶 Finanzen", "🛠️ Verwaltung"], horizontal=True)
    if admin_group == "💶 Finanzen":
        s_menu = st.radio("Menü:", ["Manuell Buchen", "Bank-Import", "OFFEN", "🏫 Klassenübersicht", "Schüler-Akte", "Umsatzsuche"], horizontal=True)
    else:
        s_menu = st.radio("Menü:", ["Benutzer anlegen", "Passwort Reset", "Zugangs-Daten", "Schuljahreswechsel", "Administration"], horizontal=True)

    st.divider()
    
    if s_menu == "🏫 Klassenübersicht":
        st.subheader("🏫 Klassenübersicht")
        all_s = df_stamm[df_stamm['Rolle']=='Schüler'].copy()
        sald_all = df_buch.groupby('ID')['Betrag'].sum().reset_index()
        master = pd.merge(all_s, sald_all, on='ID', how='left'); master['Betrag'] = master['Betrag'].fillna(0.0)
        # ARCHIV hinzufügen (Schüler) – bleibt in Gesamt-Übersicht sichtbar
        df_arch = load_archiv_sheet()
        if not df_arch.empty:
            arch_s = df_arch[df_arch["Rolle"].astype(str) == "Schüler"].copy()
            if not arch_s.empty:
                # Saldo aus Buchungen berechnen
                if not df_buch.empty:
                    sald_arch = df_buch.groupby("ID")["Betrag"].sum().reset_index()
                    arch_s = arch_s.merge(sald_arch, on="ID", how="left")
                    arch_s["Betrag"] = arch_s["Betrag"].fillna(0.0)
                else:
                    arch_s["Betrag"] = 0.0
                arch_s["Archiviert"] = "Ja"
                # Datumsspalte sicherstellen
                if "Archiv_Datum" not in arch_s.columns: arch_s["Archiv_Datum"] = ""
                # gleiche Spalten wie master
                for c in master.columns:
                    if c not in arch_s.columns: arch_s[c] = ""
                master = pd.concat([master, arch_s[master.columns]], ignore_index=True)
              
        
        col_klasse, col_kpi = st.columns([2, 1])

        with col_klasse:
            klassen_liste = sorted(master["Klasse"].dropna().astype(str).unique())

            sel_klasse = st.selectbox(
                "🏫 Klasse auswählen",
                ["Alle Klassen"] + klassen_liste
            )

        if sel_klasse != "Alle Klassen":
            master = master[master["Klasse"] == sel_klasse]

        with col_kpi:
            st.metric(
                "💰 Klassenguthaben",
                f"{master['Betrag'].sum():.2f} €",
                f"{len(master)} Schüler"
            )

        # --- Robustheit: Archiv-Spalten können fehlen (z.B. leeres/fehlendes Archiv) ---
        for _c, _default in [("Archiv_Datum", ""), ("Archiviert", "Nein")]:
            if _c not in master.columns:
                master[_c] = _default
        # Ansicht-Spalten (fehlende werden leer gefüllt)
        _cols_show = ['Klasse','Name','Betrag','ID','Archiv_Datum','Archiviert']
        master_view = master.reindex(columns=_cols_show)

        master_view = master_view.sort_values(
            by=["Klasse", "Name"],
            ascending=[True, True]
        )

        master_view = format_date_columns(master_view, cols=['Archiv_Datum'])
        st.dataframe(master_view, column_config={"Betrag":st.column_config.NumberColumn("Saldo", format="%.2f €")}, hide_index=True, use_container_width=True, height=600)

    # --- BENUTZER ANLEGEN ---
    elif s_menu == "Benutzer anlegen":
        st.subheader("➕ Neue Benutzer anlegen")
        mode = st.radio("Modus:", ["Einzel-Eingabe (Maske)", "Massen-Import (CSV)"], horizontal=True, key="user_add_mode")

        if mode == "Einzel-Eingabe (Maske)":
            st.info("Hier können Sie einzelne Schüler oder Lehrer manuell hinzufügen.")
            with st.form("add_single_user"):
                c1, c2 = st.columns(2)
                rolle_neu = c1.selectbox("Rolle", ["Schüler", "Lehrer", "Admin"]) 
                klasse_neu = c2.text_input("Klasse (z.B. 1a, 4b)", help="Bei Lehrern leer lassen oder KV-Klasse eintragen")
                id_neu = ""
                if rolle_neu == "Schüler":
                    id_neu = st.text_input("Schüler-ID (10-stellig, optional)", placeholder="YYYYXXXXXX", help="Optional: eigene ID vergeben (10 Zeichen A-Z/0-9). Leer lassen = automatische Generierung (YYYY + 6 Zeichen).")
                    startbetrag = 0.0
                    if rolle_neu == "Schüler":
                        startbetrag = st.number_input("Startbetrag (optional)", min_value=0.0, step=1.0, value=0.0, help="Optionaler Startbetrag, der beim Anlegen als Einzahlung gebucht wird.")

                c3, c4 = st.columns(2)
                name_neu = c3.text_input("Nachname Vorname")
                email_neu = c4.text_input("E-Mail (Optional / für Lehrer wichtig)")
                pw_input = st.text_input("Initial-Passwort setzen", value="Start123!", help="Das Passwort, mit dem sich der User zum ersten Mal einloggen muss.")

                if st.form_submit_button("Benutzer speichern"):
                    if name_neu:
                        name_neu = normalize_text(name_neu)
                        try:
                            df_fresh = conn.read(worksheet="Stammdaten", ttl=0)
                            dup_name = False; dup_email = False
                            if name_neu.strip().lower() in df_fresh['Name'].astype(str).str.strip().str.lower().values: dup_name = True
                            if email_neu and email_neu.strip().lower() in df_fresh['Email'].astype(str).str.strip().str.lower().values: dup_email = True
                            
                            if dup_name: st.error(f"⚠️ Der Benutzer '{name_neu}' existiert bereits!")
                            elif dup_email: st.error(f"⚠️ Die E-Mail '{email_neu}' ist bereits vergeben!")
                            else:
                                next_id = ""
                                if rolle_neu == "Schüler":
                                    custom = normalize_id(id_neu) if "id_neu" in locals() else ""
                                    if custom:
                                        if not is_valid_student_id_10(custom):
                                            st.error("❌ Ungültige ID. Erwartet: genau 10 Zeichen (A-Z/0-9).")
                                            st.stop()
                                        if "ID" in df_fresh.columns and (df_fresh["ID"].astype(str).apply(normalize_id) == custom).any():
                                            st.error("❌ Diese ID ist bereits vergeben.")
                                            st.stop()
                                        next_id = custom
                                    else:
                                        next_id = get_next_logical_id(df_fresh)
                                else:
                                    next_id = ""
                                new_code = generate_random_code(16)
                                hashed_pw = hash_password(pw_input.strip())
                                new_entry = {"Rolle": rolle_neu, "Name": name_neu, "Klasse": klasse_neu if klasse_neu else "", "ID": next_id, "Email": email_neu.lower().strip(), "Zugangscode": new_code, "Passwort": hashed_pw, "Muss_Passwort_Aendern": "Ja"}
                                df_updated = pd.concat([df_fresh, pd.DataFrame([new_entry])], ignore_index=True)
                                conn.update(worksheet="Stammdaten", data=df_updated); st.cache_data.clear()
                                st.success(f"✅ {name_neu} erfolgreich angelegt!")
                                # Optional: Startbetrag als Einzahlung buchen
                                if rolle_neu == 'Schüler' and float(startbetrag or 0) > 0.009 and next_id:
                                    ok_b = save_buchung_einzeln(datetime.today(), next_id, name_neu, klasse_neu, 'Startbetrag (Anlage)', float(startbetrag), user_name, 'Erledigt')
                                    if ok_b:
                                        st.info(f"Startbetrag gebucht: {float(startbetrag):.2f} €")
                                if next_id: st.info(f"ID: {next_id}")
                        except Exception as e: st.error(f"Fehler beim Speichern: {e}")
                    else: st.error("Bitte einen Namen eingeben.")

        elif mode == "Massen-Import (CSV)":
            st.markdown("#### Schritt 1: Vorlage & Upload")
            st.info("Das System benötigt ein Semikolon (;) als Trennzeichen (Standard bei deutschem Excel).")
            pw_batch = st.text_input("Initial-Passwort für diesen Import festlegen", value="Start123!", key="pw_csv_batch")
            csv_template = """Rolle;Name;Klasse;Email;ID;Startbetrag
Schüler;Max Mustermann;1a;;;10
Schüler;Lisa Musterfrau;1a;;;0
Lehrer;Herr Beispiel;;lehrer@schule.at;;
Admin;Frau Sekretariat;;;;
"""
            st.download_button("📥 CSV-Vorlage herunterladen", data=csv_template.encode("utf-8-sig"), file_name="vorlage_neue_user.csv", mime="text/csv; charset=utf-8")
            up_file = st.file_uploader("CSV Datei auswählen", type=["csv"], key="csv_upload_users")
            
            if up_file:
                df_upload = pd.DataFrame(); read_success = False; error_msg = ""
                try:
                    up_file.seek(0)
                    df_upload = pd.read_csv(up_file, sep=";", encoding="utf-8-sig", dtype=str)
                    read_success = True
                except Exception:
                    try:
                        up_file.seek(0)
                        df_upload = pd.read_csv(up_file, sep=";", encoding="utf-8", dtype=str)
                        read_success = True
                    except Exception:
                        try:
                            up_file.seek(0)
                            df_upload = pd.read_csv(up_file, sep=";", encoding="cp1252", dtype=str)
                            read_success = True
                        except Exception as e2:
                            try:
                                up_file.seek(0)
                                df_upload = pd.read_csv(up_file, sep=";", encoding="latin-1", dtype=str)
                                read_success = True
                            except Exception as e3:
                                error_msg = f"Konnte Datei nicht lesen. Fehler: {e3}"
                if not read_success: st.error(f"❌ Datei ist beschädigt oder hat ein falsches Format.\nDetails: {error_msg}")
                else:
                    df_upload.columns = df_upload.columns.str.strip()
                    if len(df_upload.columns) < 2: st.error("❌ **Format-Fehler:** Es wurde nur 1 Spalte erkannt (Trennzeichen falsch?)."); st.dataframe(df_upload.head()) 
                    else:
                        req_cols = ["Rolle", "Name"]; missing = [c for c in req_cols if c not in df_upload.columns]
                        if missing: st.error(f"❌ **Fehlende Spalten:** {missing}"); st.info(f"Gefundene Spalten: {list(df_upload.columns)}")
                        else:
                            st.success("✅ **Datei-Format gültig!**"); st.write(f"Erkannte Datensätze: **{len(df_upload)}**"); st.dataframe(df_upload.head(3))
                            if st.button(f"🚀 Jetzt {len(df_upload)} Benutzer importieren", type="primary"):
                                with st.spinner("Import läuft..."):
                                    try:
                                        df_fresh = conn.read(worksheet="Stammdaten", ttl=0)
                                        existing_names = set(df_fresh['Name'].astype(str).str.strip().str.lower())
                                        existing_emails = set(df_fresh['Email'].astype(str).str.strip().str.lower())
                                        new_rows = []; new_bookings = []; skipped_count = 0
                                        hashed_batch_pw = hash_password(pw_batch.strip())
                                        existing_ids = set(df_fresh['ID'].astype(str).apply(normalize_id)) if 'ID' in df_fresh.columns else set()
                                        
                                        for idx, row in df_upload.iterrows():
                                            curr_name = str(row['Name']).strip()
                                            curr_name = normalize_text(curr_name)
                                            curr_email = str(row['Email']).strip().lower() if 'Email' in row and pd.notna(row['Email']) else ""
                                            # Optionaler Startbetrag aus CSV
                                            startbetrag_val = 0.0
                                            if 'Startbetrag' in df_upload.columns:
                                                startbetrag_val = parse_amount(row.get('Startbetrag', 0), 0.0)
                                            elif 'Betrag' in df_upload.columns:
                                                startbetrag_val = parse_amount(row.get('Betrag', 0), 0.0)
                                            if curr_name.lower() in existing_names or (curr_email and curr_email in existing_emails): skipped_count += 1; continue

                                            r_rolle = row['Rolle'] if pd.notna(row['Rolle']) else "Schüler"
                                            if str(r_rolle).strip() == "Schüler":
                                                provided = ""
                                                if "ID" in df_upload.columns and pd.notna(row.get("ID", "")) and str(row.get("ID", "")).strip() != "":
                                                    provided = normalize_id(row.get("ID", ""))
                                                if provided:
                                                    if not is_valid_student_id_10(provided):
                                                        raise ValueError(f"Ungültige ID im CSV für {curr_name}: {provided} (erwartet: 10 Zeichen A-Z/0-9)")
                                                    if provided in existing_ids:
                                                        raise ValueError(f"Doppelte ID im CSV/DB: {provided}")
                                                    this_id = provided
                                                else:
                                                    this_id = generate_student_id_10(existing_ids)
                                                existing_ids.add(this_id)
                                            else: this_id = ""
                                            
                                            new_rows.append({"Rolle": r_rolle, "Name": curr_name, "Klasse": row['Klasse'] if 'Klasse' in row and pd.notna(row['Klasse']) else "", "ID": this_id, "Email": curr_email, "Zugangscode": generate_random_code(16), "Passwort": hashed_batch_pw, "Muss_Passwort_Aendern": "Ja"})
                                            
                                            # Startbetrag als Einzahlung buchen (nur Schüler)
                                            
                                            if str(r_rolle).strip() == 'Schüler' and abs(float(startbetrag_val or 0)) > 0.009 and this_id:
                                            
                                                new_bookings.append({
                                            
                                                    'Datum': datetime.today().strftime('%Y-%m-%d'),
                                            
                                                    'Zeitstempel': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                            
                                                    'ID': str(this_id).upper(),

                                                    'Klasse': curr_klasse,
                                            
                                                    'Name': curr_name,
                                            
                                                    'Beschreibung': 'Startbetrag (Import)',
                                            
                                                    'Betrag': float(startbetrag_val),
                                            
                                                    'Erfasst_Von': user_name,
                                            
                                                    'Status': 'Erledigt',
                                            
                                                })
                                            existing_names.add(curr_name.lower())
                                            if curr_email: existing_emails.add(curr_email)
                                        
                                        if new_rows:
                                            df_final = pd.concat([df_fresh, pd.DataFrame(new_rows)], ignore_index=True)
                                            conn.update(worksheet="Stammdaten", data=df_final); st.cache_data.clear(); st.balloons()
                                            if new_bookings:
                                                save_buchung_batch(pd.DataFrame(new_bookings))

                                            msg = f"🎉 Import erfolgreich! {len(new_rows)} Benutzer hinzugefügt."
                                            if skipped_count > 0: msg += f" ( {skipped_count} Duplikate wurden übersprungen)."
                                            st.success(msg)
                                            st.balloons()
                                            try:
                                                st.session_state["csv_upload_users"] = None
                                                st.session_state["user_add_mode"] = "Massen-Import (CSV)"
                                            except Exception:
                                                pass
                                            time.sleep(1.2)
                                            st.rerun()
                                        else: st.warning(f"Keine neuen Benutzer importiert. {skipped_count} Duplikate gefunden.")
                                    except Exception as e: st.error(f"Schreibfehler in Datenbank: {e}")

    # --- PASSWORT RESET (NEU) ---
    elif s_menu == "Passwort Reset":
        st.subheader("🔑 Passwörter verwalten")
        st.info("Hier können Sie das Passwort für Lehrer oder andere Administratoren neu setzen.")
        
        # Nur Lehrer und Admins laden
        users_df = df_stamm[df_stamm['Rolle'].isin(['Lehrer', 'Admin'])].sort_values('Name')
        
        # Liste für Dropdown erstellen: "Name (Email)"
        user_list = []
        for index, row in users_df.iterrows():
            email_display = row['Email'] if str(row['Email']) != "nan" and row['Email'] else "Keine Email"
            user_list.append(f"{row['Name']} ({email_display})")
            
        selected_user_str = st.selectbox("Benutzer auswählen:", ["Bitte wählen..."] + user_list)
        
        if selected_user_str != "Bitte wählen...":
            # Email aus String extrahieren: "Name (email)" -> email
            # Wir suchen einfach die Zeile im DF basierend auf Name und Email
            sel_name = selected_user_str.split(" (")[0]
            sel_email_part = selected_user_str.split(" (")[1].replace(")", "")
            
            st.divider()
            st.markdown(f"**Gewählter Benutzer:** {sel_name}")
            
            with st.form("admin_pw_reset_form"):
                new_pw_admin = st.text_input("Neues Passwort vergeben:", type="password")
                force_reset = st.checkbox("Benutzer muss Passwort beim nächsten Login ändern?", value=True)
                
                if st.form_submit_button("Passwort speichern"):
                    if len(new_pw_admin) < 4:
                        st.error("Passwort zu kurz.")
                    else:
                        # Email finden für DB Update
                        if admin_reset_user_password(sel_email_part, new_pw_admin, force_reset):
                            st.success(f"Passwort für {sel_name} wurde geändert!")
                            st.balloons()
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error("Fehler: Benutzer nicht in Datenbank gefunden.")
    elif s_menu == "Schüler-Akte":
        st.subheader("📂 Detaillierte Schüler-Akte")
        render_student_details_ui(df_stamm, df_buch, allowed_classes=None, key_suffix="admin")

    elif s_menu == "OFFEN":
        st.subheader("Offene Auszahlungen an Lehrer")
        show_done = st.toggle("Erledigte anzeigen", value=False, key="offen_show_done", help="Wenn aktiviert, werden auch erledigte Auszahlungen (Status=Erledigt) angezeigt.")
        if show_done:
            off = df_buch[(df_buch['Betrag']<0)].copy()
        else:
            off = df_buch[(df_buch['Betrag']<0) & (df_buch['Status']!='Erledigt')].copy()
        if not off.empty:
            # Klasse zur Buchung ermitteln (über Schüler-ID aus dem Stammblatt)
            # Hinweis: df_buch speichert i.d.R. keine Klasse je Buchung, daher mappen wir über die ID.
            off['ID'] = off['ID'].astype(str).str.strip().str.upper()
            _id2klasse = df_stamm[df_stamm['Rolle'] == 'Schüler'][['ID', 'Klasse']].copy()
            _id2klasse['ID'] = _id2klasse['ID'].astype(str).str.strip().str.upper()
            id_to_class = _id2klasse.set_index('ID')['Klasse'].to_dict()
            off['Klasse'] = off['ID'].map(id_to_class).fillna('')

            grp = off.groupby(['Klasse','Datum','Beschreibung','Erfasst_Von','Ueberweisen_An'], as_index=False).agg({'Betrag':'sum','Name':'count'}).sort_values('Datum', ascending=False)

            # Datum robust parsen (für Sortierung)
            grp['_dt'] = pd.to_datetime(grp['Datum'], errors='coerce', dayfirst=True)
            grp['Dat'] = grp['_dt'].dt.strftime(DATE_DISPLAY_FMT)
            grp.insert(0, "Erledigt", False)

            # Sortierung (optional)
            sort_choice = st.selectbox(
                "Sortierung",
                ["Empfänger (Überweisen an)", "Lehrer (Erfasst von)", "Datum"],
                index=0,
                key="offen_sort"
            )
            if sort_choice == "Empfänger (Überweisen an)":
                grp = grp.sort_values(['Ueberweisen_An', 'Erfasst_Von', '_dt'], ascending=[True, True, False], na_position='last')
            elif sort_choice == "Lehrer (Erfasst von)":
                grp = grp.sort_values(['Erfasst_Von', 'Ueberweisen_An', '_dt'], ascending=[True, True, False], na_position='last')
            else:
                grp = grp.sort_values(['_dt', 'Ueberweisen_An', 'Erfasst_Von'], ascending=[False, True, True], na_position='last')

            # Summen
            total_payout = float((-grp['Betrag']).sum())
            per_emp = grp.groupby('Ueberweisen_An', dropna=False)['Betrag'].sum().reset_index(name='Summe')
            per_emp['Auszahlung'] = (-per_emp['Summe']).astype(float)
            per_emp = per_emp.sort_values('Auszahlung', ascending=False)
            k1, k2, k3 = st.columns(3)
            k1.metric("Positionen", f"{len(grp)}")
            k2.metric("Auszahlungsbetrag" if not show_done else "Auszahlungsbetrag (inkl. erledigt)", f"{total_payout:,.2f} €")
            k3.metric("Empfänger", f"{per_emp['Ueberweisen_An'].nunique(dropna=False)}")

            with st.expander("Summen pro Empfänger anzeigen"):
                st.dataframe(per_emp[['Ueberweisen_An','Auszahlung']].rename(columns={'Ueberweisen_An':'Empfänger'}), use_container_width=True, hide_index=True)

            # --- PDF Export (OFFEN) ---
            def _df_to_pdf_bytes_offen(df_main: pd.DataFrame, df_sum: pd.DataFrame, title: str, subtitle_lines=None) -> bytes:
                """PDF: Titel + Meta + Tabelle (Detail) + Tabelle (Summen) + Gesamt."""
                from io import BytesIO
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
                from reportlab.lib.styles import getSampleStyleSheet
                from reportlab.lib import colors
                from reportlab.lib.pagesizes import A4, landscape
                from datetime import datetime

                buf = BytesIO()
                doc = SimpleDocTemplate(buf, pagesize=landscape(A4), leftMargin=24, rightMargin=24, topMargin=24, bottomMargin=24)
                styles = getSampleStyleSheet()
                story = []

                story.append(Paragraph(title, styles['Title']))
                story.append(Paragraph(f"Erstellt am: {datetime.now().strftime('%d.%m.%Y %H:%M')}", styles['Normal']))
                if subtitle_lines:
                    for s in subtitle_lines:
                        story.append(Paragraph(str(s), styles['Normal']))
                story.append(Spacer(1, 12))

                # Detail-Tabelle
                if df_main is None or df_main.empty:
                    story.append(Paragraph("Keine Datensätze vorhanden.", styles['Normal']))
                    doc.build(story)
                    return buf.getvalue()

                df = df_main.copy().fillna('')
                max_rows = 250
                if len(df) > max_rows:
                    df = df.head(max_rows)
                    story.append(Paragraph(f"Hinweis: Detailausgabe ist auf die ersten {max_rows} Zeilen begrenzt.", styles['Italic']))
                    story.append(Spacer(1, 8))

                for c in df.columns:
                    df[c] = df[c].astype(str)

                data = [list(df.columns)] + df.values.tolist()
                t = Table(data, repeatRows=1)
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f0f0f0')),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0,0), (-1,0), 9),
                    ('FONTSIZE', (0,1), (-1,-1), 8),
                    ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#fafafa')]),
                ]))
                story.append(t)

                # Summen-Tabelle
                story.append(Spacer(1, 14))
                story.append(Paragraph("Summen pro Empfänger", styles['Heading2']))

                df2 = (df_sum.copy() if df_sum is not None else pd.DataFrame())
                if not df2.empty:
                    df2 = df2.fillna('')
                    # Spaltennamen hübsch
                    if 'Ueberweisen_An' in df2.columns:
                        df2 = df2.rename(columns={'Ueberweisen_An':'Empfänger'})
                    if 'Auszahlung' in df2.columns:
                        df2['Auszahlung'] = df2['Auszahlung'].apply(lambda x: f"{float(x):,.2f} €" if str(x) != '' else '')

                    data2 = [list(df2.columns)] + df2.astype(str).values.tolist()
                    t2 = Table(data2, repeatRows=1)
                    t2.setStyle(TableStyle([
                        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f0f0f0')),
                        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0,0), (-1,0), 9),
                        ('FONTSIZE', (0,1), (-1,-1), 8),
                        ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
                        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#fafafa')]),
                    ]))
                    story.append(t2)
                else:
                    story.append(Paragraph("Keine Summen verfügbar.", styles['Normal']))

                story.append(Spacer(1, 10))
                story.append(Paragraph(f"Gesamt-Auszahlungsbetrag: {total_payout:,.2f} €", styles['Heading2']))

                doc.build(story)
                return buf.getvalue()

            # Daten für PDF
            pdf_cols = ['Dat','Klasse','Erfasst_Von','Ueberweisen_An','Beschreibung','Betrag','Name']
            pdf_cols = [c for c in pdf_cols if c in grp.columns]
            pdf_main = grp[pdf_cols].copy()

            subtitle = [
                f"Anzeige: {'nur offen' if not show_done else 'inkl. erledigt'}",
                f"Sortierung: {sort_choice}",
            ]
            pdf_bytes = _df_to_pdf_bytes_offen(pdf_main, per_emp[['Ueberweisen_An','Auszahlung']].copy(), "OFFEN – Offene Auszahlungen", subtitle_lines=subtitle)
            st.download_button("⬇️ PDF Export (OFFEN)", data=pdf_bytes, file_name="offen_offene_auszahlungen.pdf", mime="application/pdf")

            # Aufräumen: interne Sortierspalte aus Anzeige entfernen
            if '_dt' in grp.columns:
                pass
            anzeige = grp.copy()

            anzeige = anzeige.rename(columns={
                "Dat": "Anzeige_Datum",
                "Erfasst_Von": "Erfasst von",
                "Ueberweisen_An": "Empfänger",
                "Name": "Schüler",
                "Betrag": "Gesamtbetrag"
            })
            
            ed = st.data_editor(
                anzeige[
                    [
                        'Erledigt',
                        'Anzeige_Datum',
                        'Klasse',
                        'Erfasst von',
                        'Empfänger',
                        'Beschreibung',
                        'Schüler',
                        'Gesamtbetrag'
                    ]
                ],
                column_config={
                    "Erledigt": st.column_config.CheckboxColumn("Überwiesen?"),
                    "Schüler": st.column_config.NumberColumn("Anzahl Schüler"),
                    "Gesamtbetrag": st.column_config.NumberColumn(
                        "Gesamtbetrag",
                        format="%.2f €"
                    )
                },
                hide_index=True,
                use_container_width=True
            )
            todo = ed[ed['Erledigt']==True]
            if len(todo)>0:
                if st.button("✅ Verbuchen"):
                    df_new = df_buch.copy()
                    for i,r in todo.iterrows():
                        
                        mask = (
                            (df_new['Klasse'] == r['Klasse']) &
                            (df_new['Beschreibung'] == r['Beschreibung']) &
                            (df_new['Status'] != 'Erledigt')
                        )
                        
                        
                        df_new.loc[mask, 'Status'] = 'Erledigt'
                        
                    update_buchungs_status(df_new); st.success("Erledigt!"); time.sleep(1); st.rerun()
            else: st.success("Alles erledigt.")


    elif s_menu in ["Umsatzsuche", "Auswertungen", "Umsatzsuche"]:
        df_rep = df_buch.copy()
        if df_rep.empty:
            st.info("Keine Buchungen vorhanden.")
        else:
            # --- Vorbereitung ---
            df_rep['Datum_dt'] = pd.to_datetime(df_rep['Datum'], errors='coerce', dayfirst=True)
            df_rep['Betrag'] = pd.to_numeric(df_rep['Betrag'], errors='coerce').fillna(0.0)
            df_rep['Art'] = df_rep['Betrag'].apply(lambda x: 'Einnahme' if x > 0 else ('Ausgabe' if x < 0 else '0'))
            if 'Ueberweisen_An' not in df_rep.columns:
                df_rep['Ueberweisen_An'] = ''

            # --- PDF Helper ---
            def _df_to_pdf_bytes(df_in: pd.DataFrame, title: str, subtitle_lines=None, landscape_mode=False) -> bytes:
                """Erstellt ein einfaches PDF (Titel + Meta + Tabelle) als Bytes."""
                from io import BytesIO
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
                from reportlab.lib.styles import getSampleStyleSheet
                from reportlab.lib import colors
                from reportlab.lib.pagesizes import A4, landscape
                from datetime import datetime

                buf = BytesIO()
                pagesize = landscape(A4) if landscape_mode else A4
                doc = SimpleDocTemplate(buf, pagesize=pagesize, leftMargin=24, rightMargin=24, topMargin=24, bottomMargin=24)
                styles = getSampleStyleSheet()
                story = []
                story.append(Paragraph(title, styles['Title']))
                story.append(Paragraph(f"Erstellt am: {datetime.now().strftime('%d.%m.%Y %H:%M')}", styles['Normal']))

                if subtitle_lines:
                    for s in subtitle_lines:
                        story.append(Paragraph(str(s), styles['Normal']))

                story.append(Spacer(1, 12))

                if df_in is None or df_in.empty:
                    story.append(Paragraph("Keine Daten für diese Auswahl.", styles['Normal']))
                    doc.build(story)
                    return buf.getvalue()

                df = df_in.copy().fillna('')
                max_rows = 250
                if len(df) > max_rows:
                    df = df.head(max_rows)
                    story.append(Paragraph(f"Hinweis: Ausgabe ist auf die ersten {max_rows} Zeilen begrenzt.", styles['Italic']))
                    story.append(Spacer(1, 8))

                for c in df.columns:
                    df[c] = df[c].astype(str)

                data = [list(df.columns)] + df.values.tolist()
                table = Table(data, repeatRows=1)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f0f0f0')),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0,0), (-1,0), 9),
                    ('FONTSIZE', (0,1), (-1,-1), 8),
                    ('GRID', (0,0), (-1,-1), 0.25, colors.grey),
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#fafafa')]),
                ]))
                story.append(table)
                doc.build(story)
                return buf.getvalue()

            def _filter_summary_lines() -> list:
                parts = []
                try:
                    parts.append(f"Zeitraum: {date_range[0]} – {date_range[1]}" if date_range else "Zeitraum: (nicht gesetzt)")
                except Exception:
                    parts.append("Zeitraum: (nicht gesetzt)")
                parts.append(f"Schüler: {sel_schueler}")
                parts.append(f"Klasse: {sel_klasse}")
                parts.append(f"Lehrer: {sel_lehrer}")
                parts.append("Status: (entfernt)")
                parts.append(f"Art: {', '.join(art) if art else '(alle)'}")
                if q and q.strip():
                    parts.append(f"Freitext: {q.strip()}")
                return parts

            st.caption("Filter auswählen – Details und Szenarien aktualisieren sich automatisch.")

            c1, c2, c3 = st.columns(3)
            with c1:
                min_d = df_rep['Datum_dt'].min(); max_d = df_rep['Datum_dt'].max()
                if pd.isna(min_d) or pd.isna(max_d):
                    date_range = None
                    st.warning("Datum konnte nicht geparst werden – bitte Daten prüfen.")
                else:
                    date_range = st.date_input("Zeitraum", value=(min_d.date(), max_d.date()))

            with c2:
                klassen = ["(alle)"]
                if not df_stamm.empty and 'Klasse' in df_stamm.columns:
                    klassen += sorted(df_stamm['Klasse'].dropna().astype(str).unique())
                sel_klasse = st.selectbox("Klasse", options=klassen, index=0, key="umsatz_sel_klasse")

            # Wenn die Klasse geändert wird, Schüler-Auswahl zurücksetzen
            if "umsatz_prev_klasse" not in st.session_state:
                st.session_state.umsatz_prev_klasse = sel_klasse
            elif st.session_state.umsatz_prev_klasse != sel_klasse:
                st.session_state.umsatz_prev_klasse = sel_klasse
                st.session_state.umsatz_sel_schueler = "(alle)"

            with c3:
                schueler_options = ["(alle)"]
                if not df_stamm.empty and {'ID','Name'}.issubset(df_stamm.columns):
                    df_s = df_stamm.copy()
                    if 'Rolle' in df_s.columns:
                        df_s = df_s[df_s['Rolle'].astype(str).str.lower().str.contains('schüler|schueler', na=False)]
                    if 'Klasse' in df_s.columns and sel_klasse != "(alle)":
                        df_s = df_s[df_s['Klasse'].astype(str) == str(sel_klasse)]
                    schueler_options += make_id_name_options(df_s)
                sel_schueler = st.selectbox("Schüler", options=schueler_options, index=0, key="umsatz_sel_schueler")

            c4, c5 = st.columns(2)
            with c4:
                lehrer = ["(alle)"] + sorted(df_rep.get('Erfasst_Von', pd.Series(dtype=str)).dropna().astype(str).unique())
                sel_lehrer = st.selectbox("Lehrer / Erfasst von", options=lehrer, index=0)
            sel_status = '(alle)'  # Status-Filter entfernt (Default)
            with c5:
                art = st.multiselect("Art", options=['Einnahme','Ausgabe'], default=['Einnahme','Ausgabe'])

            q = st.text_input("Freitextsuche (Beschreibung / Name / ID)", placeholder="z.B. Kopierpapier, 2A, MAX...")
            apply_filters_to_scenarios = True  # Schalter entfernt (immer aktiv)

            def _apply_filters(df_in: pd.DataFrame) -> pd.DataFrame:
                df_f = df_in.copy()
                if date_range and isinstance(date_range, (tuple, list)) and len(date_range) == 2:
                    d1, d2 = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
                    df_f = df_f[(df_f['Datum_dt'] >= d1) & (df_f['Datum_dt'] <= d2)]
                if sel_schueler != "(alle)":
                    sid = sel_schueler.split(' - ', 1)[0].strip().upper()
                    df_f = df_f[df_f['ID'].astype(str).str.upper().str.strip() == sid]
                if sel_klasse != "(alle)" and not df_stamm.empty and {'ID','Klasse'}.issubset(df_stamm.columns):
                    id2k = df_stamm[['ID','Klasse']].copy(); id2k['ID'] = id2k['ID'].astype(str).str.upper().str.strip()
                    df_f['ID_norm'] = df_f['ID'].astype(str).str.upper().str.strip()
                    df_f = df_f.merge(id2k.rename(columns={'ID':'ID_norm'}), on='ID_norm', how='left')
                    df_f = df_f[df_f['Klasse'].astype(str) == str(sel_klasse)]
                if sel_lehrer != "(alle)":
                    df_f = df_f[df_f.get('Erfasst_Von','').astype(str) == str(sel_lehrer)]
                if art:
                    df_f = df_f[df_f['Art'].isin(art)]
                if q and q.strip():
                    qq = q.strip().lower()
                    hay = (df_f.get('Beschreibung', pd.Series('', index=df_f.index)).astype(str).str.lower() + ' ' +
                           df_f.get('Name', pd.Series('', index=df_f.index)).astype(str).str.lower() + ' ' +
                           df_f.get('ID', pd.Series('', index=df_f.index)).astype(str).str.lower())
                    df_f = df_f[hay.str.contains(qq, na=False)]
                return df_f

            df_details = _apply_filters(df_rep)
            df_scen = _apply_filters(df_rep) if apply_filters_to_scenarios else df_rep.copy()

            details_container = st.container()
            with details_container:
                show_cols = ['Datum','ID','Name','Beschreibung','Betrag','Erfasst_Von','Ueberweisen_An','Status']
                show_cols = [c for c in show_cols if c in df_details.columns]
                df_show = df_details.sort_values('Datum_dt', ascending=False)[show_cols].copy()
                df_show = format_date_columns(df_show, cols=['Datum'])
                st.dataframe(df_show, use_container_width=True, hide_index=True)
                c_csv, c_pdf = st.columns(2)
                with c_csv:
                    st.download_button("⬇️ CSV Export (Details)", data=df_show.to_csv(index=False).encode('utf-8'), file_name="auswertung_details.csv", mime="text/csv")
                with c_pdf:
                    st.download_button("⬇️ PDF Export (Details)", data=_df_to_pdf_bytes(df_show, "Auswertung – Details", subtitle_lines=_filter_summary_lines(), landscape_mode=True), file_name="auswertung_details.pdf", mime="application/pdf")

            # Weitere Auswertungs-Ansichten entfernt (vereinfachte Umsatzsuche)
    elif s_menu == "Manuell Buchen":
        render_booking_ui(is_teacher=False, preselected_class=None)
    
    # --- BANK IMPORT ---
    elif s_menu == "Bank-Import":
        st.subheader("🏦 Bank Import (ELBA CSV)")
        st.info("Laden Sie hier die .csv Datei aus dem Online-Banking hoch.")
        uploaded_file = st.file_uploader("CSV Datei hier hineinziehen", type=["csv"], key="bank_csv_upload")
        if uploaded_file is not None:
            df_import = parse_csv_elba(uploaded_file)
            if not df_import.empty:
                existing_keys = set()
                for _, row in df_buch.iterrows():
                    try:
                        amt = round(float(row['Betrag']), 2); date_str = str(row['Datum']).strip()
                        sv_str = str(row['ID']).strip().upper(); desc_str = str(row['Beschreibung']).strip()
                        key = f"{sv_str}_{date_str}_{amt}_{desc_str}"; existing_keys.add(key)
                    except: continue
                new_unique_bookings = []; duplicates_count = 0; preview_list = []
                for _, row in df_import.iterrows():
                    amt = round(float(row['Betrag']), 2); date_str = str(row['Datum']).strip()
                    sv_str = str(row['ID']).strip().upper(); desc_str = str(row['Beschreibung']).strip()
                    check_key = f"{sv_str}_{date_str}_{amt}_{desc_str}"
                    student_match = df_stamm[df_stamm['ID'] == sv_str]
                    student_name = student_match.iloc[0]['Name'] if not student_match.empty else "⚠️ UNBEKANNT"
                    student_class = (
                        student_match.iloc[0]['Klasse']
                        if not student_match.empty
                        else ""
                    )
                    is_duplicate = check_key in existing_keys
                    if is_duplicate:
                        duplicates_count += 1; status_icon = "🔁 BEREITS GEBUCHT"
                    else:
                        new_unique_bookings.append({"Datum": format_date_display(row['Datum']),"Zeitstempel": row['Zeitstempel'],"ID": sv_str,"Name": student_name if student_name != "⚠️ UNBEKANNT" else "Unbekannt","Klasse": student_class,"Beschreibung": row['Beschreibung'],"Betrag": row['Betrag'],"Erfasst_Von": "Bank-Import","Status": "Erledigt"})
                        status_icon = "✅ NEU"
                    preview_list.append({"Status": status_icon,"Datum": format_date_display(row['Datum']),"Name": student_name,"Betrag": row['Betrag'],"Beschreibung": row['Beschreibung']})
                st.divider(); st.markdown(f"### 📊 Analyse-Ergebnis")
                c1, c2, c3 = st.columns(3)
                c1.metric("Zeilen in CSV", len(df_import))
                c2.metric("Davon Duplikate", duplicates_count, delta_color="off")
                c3.metric("Neue Buchungen", len(new_unique_bookings), delta_color="normal")
                st.caption("Vorschau der Analyse:")
                df_preview = pd.DataFrame(preview_list)
                def color_status(val): return f'color: {"#d9534f" if "BEREITS" in val else "#28a745"}; font-weight: bold'
                st.dataframe(df_preview.style.map(color_status, subset=['Status']), use_container_width=True, hide_index=True)
                st.divider()
                if len(new_unique_bookings) > 0:
                    col_btn, _ = st.columns([1, 3])
                    if col_btn.button(f"🚀 {len(new_unique_bookings)} neue Buchungen importieren", type="primary"):
                        if save_buchung_batch(pd.DataFrame(new_unique_bookings)):
                            st.balloons(); st.success(f"✅ Import erfolgreich! {duplicates_count} Duplikate ignoriert."); st.session_state.pop("bank_csv_upload", None); st.rerun()
                elif duplicates_count > 0 and len(new_unique_bookings) == 0:
                    st.success("✅ Alles auf dem neuesten Stand! Alle Zeilen in dieser CSV sind bereits gebucht.")
                else: st.warning("Keine gültigen Daten gefunden.")
            else: st.warning("In dieser Datei wurden keine gültigen IDs gefunden.")

    elif s_menu == "Zugangs-Daten":
        st.subheader("🔑 Zugangs-Daten Verwaltung")
        
        # 1. Auswahl der Klasse
        all_classes = sorted([k for k in df_stamm['Klasse'].unique() if k and str(k)!="nan"])
        sel_klasse = st.selectbox("Klasse wählen:", all_classes)
        
        if sel_klasse:
            # Daten filtern: Nur Schüler der gewählten Klasse
            mask = (df_stamm['Klasse'] == sel_klasse) & (df_stamm['Rolle'] == 'Schüler')
            df_view = df_stamm[mask][['Klasse', 'Name', 'ID', 'Zugangscode']].sort_values('Name')
            
            if not df_view.empty:
                # 2. Browser Ansicht (Name, Code, ID)
                st.markdown("### 👁️ Vorschau")
                st.dataframe(
                    df_view, 
                    use_container_width=True, 
                    hide_index=True,
                    column_config={
                        "Name": "Schüler Name",
                        "ID": "Schüler ID",
                        "Zugangscode": st.column_config.TextColumn("Zugangscode", help="Dieser Code ist für den Login")
                    }
                )
                
                st.markdown("### 📥 Downloads")
                
                # Daten für Export aufbereiten
                df_export = df_view.copy()
                # Den Link zur App inkl. Code Parameter bauen
                df_export['App_Link'] = df_export['Zugangscode'].apply(lambda c: f"{APP_URL}/?code={c}")
                # Klasseninformationen ergänzen
                kl_info = df_klassen[['Klasse', 'IBAN', 'Empfaenger']].copy()

                df_export = df_export.merge(
                    kl_info,
                    on='Klasse',
                    how='left'
                )

                df_export['Verwendungszweck'] = (
                    df_export['ID'].astype(str)
                    + " "
                    + df_export['Name'].astype(str)
                )
                
                col_d1, col_d2 = st.columns(2)
                
                # A) CSV Download (Text & Link)
                with col_d1:
                    csv_data = df_export.to_csv(index=False, sep=";").encode('utf-8-sig')
                    st.download_button(
                        label="📄 1. Liste als CSV laden (Excel)",
                        data=csv_data,
                        file_name=f"Zugangsdaten_{sel_klasse}.csv",
                        mime="text/csv",
                        help="Enthält Name, ID, Code und den Link als Text."
                    )
                
                # B) PDF Download (für die QR-Codes)
                with col_d2:
                    if st.button("🏁 2. QR-Codes als PDF laden"):
                        try:
                            # -----------------------------
                            # QR-PDF: 2-Spalten Layout + sauberer Seitenumbruch
                            # Verbesserungen:
                            # - Linkanzeige als Kurz-Link ohne Parameter (Domain/Path), QR enthält den vollen Link
                            # - Code fett hervorgehoben
                            # - Rahmen pro Block + Rahmen um QR für besseres Drucken/Ausschneiden
                            # -----------------------------
                            pdf_qr = FPDF(format="A4", unit="mm")
                            margin = 12
                            gutter = 6  # Abstand zwischen den Spalten

                            # Wir steuern den Seitenumbruch selbst (stabiler bei MultiCell + Bildern)
                            pdf_qr.set_auto_page_break(auto=False, margin=margin)
                            pdf_qr.set_margins(margin, margin, margin)
                            pdf_qr.add_page()

                            page_w = pdf_qr.w
                            page_h = pdf_qr.h
                            usable_w = page_w - 2 * margin
                            col_w = (usable_w - gutter) / 2.0
                            x_col_1 = margin
                            x_col_2 = margin + col_w + gutter

                            # QR-Größe automatisch: so groß wie möglich, aber Text darf nicht zu schmal werden
                            qr_max = 28
                            qr_min = 18
                            gap = 4
                            min_text_w = 58
                            qr_size = min(qr_max, max(qr_min, col_w - gap - min_text_w))
                            text_w = col_w - qr_size - gap

                            # Titel
                            pdf_qr.set_font("Arial", "B", 14)
                            pdf_qr.cell(0, 10, f"Zugangscodes Klasse {sel_klasse}", 0, 1, "C")
                            pdf_qr.ln(2)

                            def short_link_no_params(link: str, max_chars: int = 46) -> str:
                                # Kurz-Link für Anzeige: Scheme+Domain+Path (ohne Query/Fragment)
                                try:
                                    from urllib.parse import urlsplit, urlunsplit
                                    parts = urlsplit(str(link))
                                    base = urlunsplit((parts.scheme, parts.netloc, parts.path, '', ''))
                                except Exception:
                                    base = str(link)
                                    if '?' in base:
                                        base = base.split('?', 1)[0]
                                if len(base) <= max_chars:
                                    return base
                                keep_tail = 10
                                head = max_chars - (keep_tail + 1)
                                return base[:head] + "..." + base[-keep_tail:]

                            def wrap_text(pdf, text, max_width):
                                words = str(text).split()
                                lines, line = [], ""
                                for w in words:
                                    test = (line + " " + w).strip()
                                    if pdf.get_string_width(test) <= max_width:
                                        line = test
                                    else:
                                        if line:
                                            lines.append(line)
                                        line = w
                                if line:
                                    lines.append(line)
                                return lines if lines else [""]

                            def estimate_block_height(name, sid, code, link_disp):
                                h = 0
                                h += 7
                                h += 5
                                h += 5
                                pdf_qr.set_font("Arial", "", 8)
                                link_lines = wrap_text(pdf_qr, link_disp, text_w)[:2]
                                h += 4 * max(1, len(link_lines))
                                h += 6
                                return max(h, qr_size + 8)

                            y = pdf_qr.get_y()
                            col_index = 0
                            last_row_height = 0

                            try:
                                pdf_qr.set_line_width(0.2)
                            except Exception:
                                pass

                            for _, row in df_export.iterrows():
                                name = str(row["Name"])
                                sid = str(row["ID"])
                                code = str(row["Zugangscode"])
                                link_full = str(row["App_Link"])  # QR: voller Link
                                link_disp = short_link_no_params(link_full, max_chars=46)

                                needed_h = estimate_block_height(name, sid, code, link_disp)

                                if y + needed_h > (page_h - margin):
                                    pdf_qr.add_page()
                                    y = pdf_qr.get_y()
                                    col_index = 0
                                    last_row_height = 0

                                start_x = x_col_1 if col_index == 0 else x_col_2
                                start_y = y

                                # Rahmen um Block
                                pdf_qr.rect(start_x, start_y, col_w, needed_h)

                                pad = 2
                                tx = start_x + pad
                                ty = start_y + pad

                                # Text
                                pdf_qr.set_xy(tx, ty)
                                pdf_qr.set_font("Arial", "B", 12)
                                pdf_qr.multi_cell(text_w - pad, 7, name, border=0)

                                curr_y = pdf_qr.get_y()
                                pdf_qr.set_xy(tx, curr_y)
                                pdf_qr.set_font("Arial", "", 10)
                                pdf_qr.multi_cell(text_w - pad, 5, f"ID: {sid}", border=0)

                                curr_y = pdf_qr.get_y()
                                pdf_qr.set_xy(tx, curr_y)
                                pdf_qr.set_font("Arial", "B", 10)
                                pdf_qr.multi_cell(text_w - pad, 5, f"Code: {code}", border=0)

                                pdf_qr.set_font("Arial", "", 8)
                                pdf_qr.set_text_color(60, 60, 60)
                                link_lines = wrap_text(pdf_qr, link_disp, text_w - pad)[:2]
                                curr_y = pdf_qr.get_y()
                                pdf_qr.set_xy(tx, curr_y)
                                pdf_qr.multi_cell(text_w - pad, 4, "\n".join(link_lines), border=0)
                                pdf_qr.set_text_color(0, 0, 0)

                                # QR
                                scale = max(3, min(10, int(qr_size / 3.5)))
                                qr_obj = segno.make(link_full, error="L")
                                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                                    qr_obj.save(tmp_file, kind="png", scale=scale)
                                    tmp_path = tmp_file.name

                                try:
                                    qr_x = start_x + (col_w - qr_size - pad)
                                    qr_y = start_y + pad
                                    # Rahmen um QR
                                    pdf_qr.rect(qr_x, qr_y, qr_size, qr_size)
                                    pdf_qr.image(tmp_path, x=qr_x, y=qr_y, w=qr_size, h=qr_size)
                                finally:
                                    try:
                                        os.remove(tmp_path)
                                    except:
                                        pass

                                # echte Höhe prüfen (z.B. sehr langer Name)
                                text_end_y = pdf_qr.get_y()
                                real_end_y = max(text_end_y, start_y + pad + qr_size) + pad
                                real_h = max(needed_h, real_end_y - start_y)
                                if real_h > needed_h + 0.5:
                                    pdf_qr.rect(start_x, start_y, col_w, real_h)
                                    needed_h = real_h

                                # Untere Linie innerhalb der Box
                                pdf_qr.set_y(start_y + needed_h)
                                pdf_qr.line(start_x, pdf_qr.get_y(), start_x + col_w, pdf_qr.get_y())

                                if col_index == 0:
                                    col_index = 1
                                    last_row_height = needed_h
                                else:
                                    col_index = 0
                                    y = y + max(last_row_height, needed_h) + 2
                                    last_row_height = 0

                            pdf_bytes = pdf_qr.output(dest="S").encode("latin-1", "replace")
                            st.success("PDF generiert! Bitte unten klicken:")
                            st.download_button(
                                label="📥 PDF Herunterladen",
                                data=pdf_bytes,
                                file_name=f"QR_Codes_{sel_klasse}.pdf",
                                mime="application/pdf",
                            )
                        except Exception as e:
                            st.error(f"Fehler bei PDF Generierung: {e}")
            else:
                st.warning("Keine Schüler in dieser Klasse gefunden.")
    elif s_menu == "Schuljahreswechsel":
        st.subheader("⚠️ Schuljahreswechsel (Klassen-Auswahl)")
        st.error("ACHTUNG: Buchungen werden zurückgesetzt (nur Überträge bleiben), Klassen werden je Auswahl hochgestuft oder archiviert. Archivieren nur bei Saldo 0. IBANs im Klassenblatt bleiben erhalten.")
        
        # Persistentes Archiv-Log (bleibt sichtbar)
        if 'sjw_archiv_log_csv' not in st.session_state: st.session_state['sjw_archiv_log_csv'] = b''
        if 'sjw_archiv_log_name' not in st.session_state: st.session_state['sjw_archiv_log_name'] = ''
        if st.session_state.get('sjw_archiv_log_csv'):
            st.success('✅ Archiv-Log ist verfügbar (vom letzten Durchlauf).')
            st.download_button('📥 Archiv-Log herunterladen (CSV)', data=st.session_state['sjw_archiv_log_csv'], file_name=st.session_state.get('sjw_archiv_log_name','archiv_log.csv'), mime='text/csv')
            if st.button('🧹 Archiv-Log ausblenden', key='sjw_clear_log'):
                st.session_state['sjw_archiv_log_csv'] = b''
                st.session_state['sjw_archiv_log_name'] = ''
                st.rerun()
        st.markdown('---')
        
        # Klassenliste erzeugen (aktiv, ohne *_alt)
        classes_from_stamm = sorted(set(df_stamm[df_stamm['Rolle']=='Schüler']['Klasse'].astype(str).tolist())) if not df_stamm.empty else []
        classes_from_kl = sorted(set(df_klassen['Klasse'].astype(str).tolist())) if not df_klassen.empty and 'Klasse' in df_klassen.columns else []
        all_classes = sorted(set([c.strip() for c in (classes_from_stamm + classes_from_kl) if c and str(c).lower()!='nan']))
        all_classes = [c for c in all_classes if not c.lower().endswith('_alt')]
        
        def _default_action(cls: str) -> str:
            c = str(cls).strip().replace(' ', '')
            if not c: return 'Keine'
            u = c.upper()
            if u.startswith('PTS'): return 'Archiv'
            m = re.match(r'^([1-9])([A-Za-z])$', c)
            if m:
                g = int(m.group(1))
                return 'Archiv' if g >= 4 else 'Aufstieg'
            return 'Keine'
        
        # Editor-State
        state_key = 'sjw_actions_df'
        if state_key not in st.session_state or set(st.session_state[state_key]['Klasse'].tolist()) != set(all_classes):
            st.session_state[state_key] = pd.DataFrame({'Klasse': all_classes, 'Aktion': [_default_action(c) for c in all_classes]})
        
        st.markdown('##### Klassen-Aktionen')
        df_actions = st.data_editor(
            st.session_state[state_key],
            hide_index=True,
            use_container_width=True,
            column_config={
                'Aktion': st.column_config.SelectboxColumn('Aktion', options=['Aufstieg','Archiv','Keine'], required=True),
            },
            key='sjw_actions_editor'
        )
        st.session_state[state_key] = df_actions
        
        action_map = dict(zip(df_actions['Klasse'].astype(str), df_actions['Aktion'].astype(str)))

        def _sjw_class_key(s: str) -> str:
            return str(s).strip().replace(' ', '').replace('nan', '').upper()

        action_map_norm = {_sjw_class_key(k): str(v) for k, v in action_map.items()}
        
        # Vorschau basierend auf Auswahl
        prev = preview_schuljahreswechsel(df_stamm, df_klassen, action_map=action_map, max_grade=4)
        c = prev.get('counts', {})
        col1, col2, col3 = st.columns(3)
        col1.metric('Schüler gesamt', c.get('schueler_total', 0))
        col2.metric('Wird hochgestuft', c.get('schueler_promote', 0))
        col3.metric('Wird archiviert', c.get('schueler_archiv', 0))
        
        with st.expander('📄 Vorschau: Schüler, die archiviert würden', expanded=False):
            df_prev_arch = pd.DataFrame(prev.get('archive_list', []))
            if df_prev_arch.empty:
                st.info('Keine Schüler für Archivierung laut Auswahl.')
            else:
                st.dataframe(df_prev_arch, use_container_width=True, hide_index=True)
                csv_prev = df_prev_arch.to_csv(index=False, sep=';', encoding='utf-8-sig').encode('utf-8-sig')
                st.download_button('📥 Vorschau-CSV herunterladen', data=csv_prev, file_name='vorschau_archiv.csv', mime='text/csv')
        
        # Saldo-Check: Archiv nur wenn Saldo==0
        archive_class_keys = {k for k, v in action_map_norm.items() if v == 'Archiv'}
        if not df_buch.empty:
            salden = df_buch.groupby('ID')['Betrag'].sum()
        else:
            salden = pd.Series(dtype=float)
        stud = df_stamm[df_stamm['Rolle']=='Schüler'][['Name','ID','Klasse']].copy() if not df_stamm.empty else pd.DataFrame(columns=['Name','ID','Klasse'])
        if not stud.empty:
            stud['ID'] = stud['ID'].astype(str).str.replace(r'\.0$','',regex=True).str.strip().str.upper()
            stud['KlasseKey'] = stud['Klasse'].astype(str).apply(_sjw_class_key)
            stud['Saldo'] = stud['ID'].map(salden).fillna(0.0)
            unsettled = stud[stud['KlasseKey'].isin(archive_class_keys) & (stud['Saldo'].abs() > 0.009)][['Name','ID','Klasse','Saldo']]
        else:
            unsettled = pd.DataFrame(columns=['Name','ID','Klasse','Saldo'])
        
        if not unsettled.empty:
            st.error('❌ Archivieren ist gesperrt: Es gibt Schüler in Archiv-Klassen mit Kontostand ≠ 0.')
            st.dataframe(unsettled, use_container_width=True, hide_index=True)
            csv_un = unsettled.to_csv(index=False, sep=';', encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button('📥 Liste offener Kontostände (CSV)', data=csv_un, file_name='offene_kontostaende.csv', mime='text/csv')
        
        if not prev.get('ok', True):
            st.error('❌ Sicherheits-Check fehlgeschlagen: ungültige Klassenformate vorhanden.')
            with st.expander('Details: Ungültige Einträge', expanded=True):
                if prev.get('invalid_students'):
                    st.markdown('**Ungültige Schüler-Klassen:**')
                    st.dataframe(pd.DataFrame(prev.get('invalid_students')), use_container_width=True, hide_index=True)
                if prev.get('invalid_staff_tokens'):
                    st.markdown('**Ungültige Lehrer/Admin-Klassen (Tokens):**')
                    st.dataframe(pd.DataFrame(prev.get('invalid_staff_tokens')), use_container_width=True, hide_index=True)
                if prev.get('invalid_klassen'):
                    st.markdown('**Ungültige Einträge im Klassen-Sheet:**')
                    st.dataframe(pd.DataFrame(prev.get('invalid_klassen')), use_container_width=True, hide_index=True)
        
        confirm = st.text_input("Zum Bestätigen 'NEUSTART' eingeben:")
        run_disabled = (not prev.get('ok', True)) or (not unsettled.empty)
        if st.button('Durchführen', type='primary', disabled=run_disabled):
            if confirm == 'NEUSTART':
                with st.spinner('Schuljahreswechsel läuft… bitte warten'):
                    success, info = perform_jahreswechsel(df_buch, df_stamm, action_map, max_grade=4)
                if success:
                    st.success(f"Erfolgreich! {info.get('uebertraege',0)} Überträge. {info.get('archiviert',0)} Schüler archiviert.")
                    st.info(f"Stammdaten neu: {info.get('stamm_gesamt',0)} Einträge")
                    df_log = pd.DataFrame(info.get('archiv_log', []))
                    if not df_log.empty:
                        csv_bytes = df_log.to_csv(index=False, sep=';', encoding='utf-8-sig').encode('utf-8-sig')
                        st.session_state['sjw_archiv_log_csv'] = csv_bytes
                        st.session_state['sjw_archiv_log_name'] = f"archiv_log_{datetime.now().strftime('%Y-%m-%d')}.csv"
                        st.balloons()
                        st.info('Archiv-Log gespeichert – Download oben verfügbar.')
                else:
                    # Fehlerdetails (Saldo-Block oder Preview)
                    if isinstance(info, dict) and info.get('unsettled'):
                        st.error(info.get('msg','Fehler'))
                        st.dataframe(pd.DataFrame(info.get('unsettled')), use_container_width=True, hide_index=True)
                    elif isinstance(info, dict) and info.get('preview'):
                        st.error(info.get('msg','Fehler'))
                        st.dataframe(pd.DataFrame(info.get('preview',{}).get('invalid_students',[])), use_container_width=True, hide_index=True)
                    else:
                        st.error(f"Fehler: {info}")
            else:
                st.warning('Falsche Bestätigung.')


            
    # --- ADMIN (Wartung) ---
    elif s_menu == "Administration":
        st.subheader("🛠️ Administration & Wartung")
        if not df_buch.empty:
            log_df = df_buch.merge(df_stamm[['ID', 'Klasse']], on='ID', how='left')
            if 'Klasse_x' in log_df.columns and 'Klasse_y' in log_df.columns:
                log_df['Klasse'] = log_df['Klasse_x'].fillna(log_df['Klasse_y'])

            elif 'Klasse_y' in log_df.columns:
                log_df['Klasse'] = log_df['Klasse_y']
            log_df = log_df.sort_values('Zeitstempel', ascending=False)
        else: log_df = pd.DataFrame()

        col_storno, col_codes, col_db = st.columns([2, 1, 1])
        with col_storno:
            st.markdown("##### 🔍 1. Buchung suchen & stornieren")
            if not log_df.empty:
                filtered_df = log_df
                # Bank-Importe ausblenden
                filtered_df = filtered_df[
                    filtered_df['Erfasst_Von'] != 'Bank-Import'
                ]
                # Nur offene Positionen dürfen storniert werden
                filtered_df = filtered_df[
                    filtered_df['Status'].astype(str).str.strip() == 'Offen'
                ]

                # Storno-Buchungen ausblenden
                filtered_df = filtered_df[
                    ~filtered_df['Beschreibung'].astype(str).str.startswith("Storno:")
                ]
                

                gruppen = (
                    filtered_df.groupby(
                        ['Zeitstempel', 'Beschreibung', 'Erfasst_Von', 'Klasse'],
                        dropna=False
                    )
                    .agg(
                        Anzahl=('ID', 'count'),
                        Gesamtbetrag=('Betrag', 'sum')
                    )
                    .reset_index()
                    .sort_values(
                    ['Zeitstempel', 'Erfasst_Von'],
                    ascending=[False, True]
                    )
                )
                options = gruppen.apply(
                    lambda x:
                        f"{x['Zeitstempel']} | "
                        f"{x['Klasse']} | "
                        f"{x['Erfasst_Von']} | "
                        f"{x['Beschreibung']} | "
                        f"{x['Anzahl']} Buchungen | "
                        f"{x['Gesamtbetrag']:.2f} €",
                    axis=1
                ).tolist()
                sel_storno = st.selectbox("Buchung wählen:", ["Bitte wählen..."] + options)
                if sel_storno != "Bitte wählen...":
                    idx = options.index(sel_storno)
                    row_to_cancel = gruppen.iloc[idx]
                    st.warning(
                        f"Gesamte Buchung "
                        f"'{row_to_cancel['Beschreibung']}' "
                        f"mit {row_to_cancel['Anzahl']} Einträgen "
                        f"wirklich stornieren?"
                    )
                    if st.button("🚨 JA, stornieren", key="btn_storno"):
                        st.error("STORNO START")
                        gruppe = filtered_df[
                            (filtered_df['Zeitstempel'] == row_to_cancel['Zeitstempel']) &
                            (filtered_df['Beschreibung'] == row_to_cancel['Beschreibung']) &
                            (filtered_df['Erfasst_Von'] == row_to_cancel['Erfasst_Von']) &
                            (filtered_df['Klasse'] == row_to_cancel['Klasse'])
                        ]
                        st.error(f"GRUPPE: {len(gruppe)}")
                        st.error("VOR SCHLEIFE")


                        for _, buch in gruppe.iterrows():
                            st.error(
                                f"{buch['Name']} | {buch['Klasse']} | {buch['Beschreibung']}"
                            )
                        try:
                            save_buchung_einzeln(
                                datetime.today(),
                                buch['ID'],
                                buch['Name'],
                                buch['Klasse'],
                                f"Storno: {buch['Beschreibung']}",
                                float(buch['Betrag']) * -1,
                                user_name,
                                "Erledigt"
                            )
                            st.error("BUCHUNG GESPEICHERT")
                        except Exception as e:
                            st.error(f"STORNO FEHLER: {e}")


                        # mask = (
                        #     (df_buch['Zeitstempel'] == row_to_cancel['Zeitstempel']) &
                        #     (df_buch['Beschreibung'] == row_to_cancel['Beschreibung']) &
                        #     (df_buch['Erfasst_Von'] == row_to_cancel['Erfasst_Von']) &
                        #     (df_buch['Klasse'] == row_to_cancel['Klasse'])
                        # )

                        # st.error(f"MASK TREFFER: {mask.sum()}")

                        

                        # conn.update(
                        #     worksheet="Buchungen",
                        #     data=df_buch
                        # )

                        st.success(f"{len(gruppe)} Buchungen storniert!")
                        time.sleep(1)
                        st.rerun()

                        
            else: st.info("Keine Buchungen vorhanden.")

        with col_codes:
            st.markdown("##### 🔑 2. Zugangsdaten")
            st.caption("Erzeugt Codes für Schüler ohne Code.")
            if st.button("Codes generieren", key="btn_codes"):
                st.cache_data.clear() 
                try:
                    df_fresh = conn.read(worksheet="Stammdaten", ttl=0) 
                    c = 0
                    if 'Rolle' in df_fresh.columns:
                        for i, r in df_fresh.iterrows():
                            code_val = str(r['Zugangscode'])
                            if r['Rolle'] == 'Schüler' and (code_val in ["", "nan", "None", "<NA>"]):
                                df_fresh.at[i, 'Zugangscode'] = generate_random_code(16)
                                c += 1
                        if c > 0:
                            conn.update(worksheet="Stammdaten", data=df_fresh)
                            st.success(f"{c} Codes erzeugt & gespeichert!"); time.sleep(1); st.rerun()
                        else: st.info("Alle Schüler haben bereits Codes.")
                    else: st.error("Fehler: Spalte 'Rolle' fehlt in frischen Daten.")
                except Exception as e: st.error(f"Fehler beim Generieren: {e}")

        with col_db:
            st.markdown("##### 💾 3. Datenbank")
            st.caption("Sortiert Lehrer (Name) & Schüler (Klasse) neu.")
            if st.button("🔄 Sortierung speichern", key="btn_sort"):
                st.cache_data.clear()
                try: 
                    df_fresh = conn.read(worksheet="Stammdaten", ttl=0)
                    def get_rank_fresh(rolle_raw):
                        r = str(rolle_raw).strip().lower()
                        if "admin" in r: return 1
                        if "lehrer" in r: return 2
                        if "schüler" in r: return 3
                        return 99
                    df_fresh['_SortRank'] = df_fresh['Rolle'].apply(get_rank_fresh)
                    def get_sort_class_fresh(row): return "" if row['_SortRank'] < 3 else str(row['Klasse'])
                    df_fresh['_SortClass'] = df_fresh.apply(get_sort_class_fresh, axis=1)
                    df_sorted = df_fresh.sort_values(
    by=['_SortRank', '_SortClass', 'Name'],
    key=lambda s: s.astype(str).str.upper()
).drop(columns=['_SortRank', '_SortClass'])

                    conn.update(worksheet="Stammdaten", data=df_sorted)
                    st.success("Erfolgreich sortiert & gespeichert!"); st.balloons()
                except Exception as e: st.error(f"Fehler: {e}")


        st.markdown("---")
        st.markdown("##### 🗄️ Archiv (Schüler)")
        st.caption("Ablauf: 1) Klasse wählen → 2) Alle/Keine/Invertieren → 3) Abhaken (3 Spalten) → 4) Begründung → Archivieren.")
        st.markdown("##### 📂 Archiv-Ordner")
        df_arch = load_archiv_sheet()
        arch_s = df_arch[df_arch.get("Rolle", "").astype(str) == "Schüler"].copy() if not df_arch.empty else pd.DataFrame()
        if arch_s.empty:
            st.info("Archiv ist leer oder Worksheet 'Archiv' fehlt.")
        else:
            arch_s = arch_s.sort_values(["Archiv_Datum","Klasse","Name"], ascending=[False, True, True])
            show = arch_s[["Name","Klasse","ID","Archiv_Datum","Archiv_Grund"]].copy() if not arch_s.empty else pd.DataFrame()
            show.insert(0, "Auswahl", False)
            state_a = "arch_folder_state"
            if state_a not in st.session_state or len(st.session_state.get(state_a, [])) != len(show):
                st.session_state[state_a] = show
            b1, b2, b3, _sp = st.columns([1,1,1,2])
            with b1:
                if st.button("✅ Alle auswählen", key="arch_folder_all"):
                    tmp = st.session_state[state_a].copy(); tmp["Auswahl"] = True; st.session_state[state_a] = tmp; st.rerun()
            with b2:
                if st.button("⬜ Keine auswählen", key="arch_folder_none"):
                    tmp = st.session_state[state_a].copy(); tmp["Auswahl"] = False; st.session_state[state_a] = tmp; st.rerun()
            with b3:
                if st.button("🔁 Invertieren", key="arch_folder_inv"):
                    tmp = st.session_state[state_a].copy(); tmp["Auswahl"] = ~tmp["Auswahl"].astype(bool); st.session_state[state_a] = tmp; st.rerun()
            df_edit = st.data_editor(st.session_state[state_a], hide_index=True, use_container_width=True,
                column_config={"Auswahl": st.column_config.CheckboxColumn("Löschen?", default=False), "Name": st.column_config.TextColumn("Name", disabled=True), "Klasse": st.column_config.TextColumn("Klasse", disabled=True), "ID": st.column_config.TextColumn("ID", disabled=True), "Archiv_Datum": st.column_config.TextColumn("Archiv-Datum", disabled=True), "Archiv_Grund": st.column_config.TextColumn("Grund", disabled=True)},
                key="arch_folder_editor")
            st.session_state[state_a] = df_edit
            ids = df_edit[df_edit["Auswahl"] == True]["ID"].astype(str).tolist()
            st.caption(f"Ausgewählt zum Löschen: {len(ids)}")
            confirm = st.text_input("Zum Löschen bitte LÖSCHEN eingeben", value="", key="arch_del_confirm")
            if st.button("🗑️ Aus Archiv löschen", key="arch_del_btn"):
                if confirm.strip().upper() != "LÖSCHEN":
                    st.error("Bestätigung fehlt: bitte LÖSCHEN eingeben.")
                else:
                    with st.spinner("Löschen läuft… bitte warten"):
                        ok, msg = delete_students_from_archiv(ids)
                    (st.success if ok else st.error)(msg)
                    if ok:
                        st.balloons()
                        st.rerun()

        with st.expander("🗄️ Manuell archivieren (Sonderfälle)", expanded=False):
            # Feedback nach langer Aktion
            if st.session_state.get("arch_flash_msg"):
                st.success(st.session_state.get("arch_flash_msg"))
                if st.session_state.get("arch_flash_balloons", False):
                    st.balloons()
                st.session_state["arch_flash_msg"] = ""
                st.session_state["arch_flash_balloons"] = False
            df_students = df_stamm[df_stamm["Rolle"] == "Schüler"].copy() if not df_stamm.empty else pd.DataFrame()
            classes = sorted([c for c in df_students["Klasse"].astype(str).unique() if c and str(c) != "nan"]) if not df_students.empty else []
            sel_cls = st.selectbox("1) Klasse auswählen", [""] + classes, key="arch_cls_sel")
            if sel_cls:
                cand = df_students[df_students["Klasse"] == sel_cls].copy().sort_values("Name")
                cand["ID"] = cand["ID"].astype(str)
                state_key = f"arch_pick_state_{sel_cls}"
                if state_key not in st.session_state:
                    df_pick = cand[["Name","ID"]].copy()
                    df_pick.insert(0, "Auswahl", True)
                    st.session_state[state_key] = df_pick
                else:
                    # Sync: entfernte IDs raus, neue rein
                    base = st.session_state[state_key].copy()
                    base["ID"] = base["ID"].astype(str)
                    cur = cand[["Name","ID"]].copy()
                    cur.insert(0, "Auswahl", True)
                    base = base[base["ID"].isin(cur["ID"])].copy()
                    missing = cur[~cur["ID"].isin(base["ID"])].copy()
                    if not missing.empty: base = pd.concat([base, missing], ignore_index=True)
                    st.session_state[state_key] = base

                # 2) Alle/Keine/Invertieren
                b_all, b_none, b_inv, _sp = st.columns([1, 1, 1, 2])
                with b_all:
                    if st.button("✅ Alle auswählen", key=f"arch_all_{sel_cls}"):
                        tmp = st.session_state[state_key].copy(); tmp["Auswahl"] = True; st.session_state[state_key] = tmp; st.rerun()
                with b_none:
                    if st.button("⬜ Keine auswählen", key=f"arch_none_{sel_cls}"):
                        tmp = st.session_state[state_key].copy(); tmp["Auswahl"] = False; st.session_state[state_key] = tmp; st.rerun()
                with b_inv:
                    if st.button("🔁 Invertieren", key=f"arch_inv_{sel_cls}"):
                        tmp = st.session_state[state_key].copy(); tmp["Auswahl"] = ~tmp["Auswahl"].astype(bool); st.session_state[state_key] = tmp; st.rerun()

                # 3) Checkboxen in 3 Spalten
                df_show = st.session_state[state_key].copy().sort_values("Name")
                n = len(df_show)
                n1 = (n + 2) // 3
                n2 = (n + 1) // 3
                col_1, col_2, col_3 = st.columns(3)
                cfg = {"Auswahl": st.column_config.CheckboxColumn("Archivieren?", default=True), "Name": st.column_config.TextColumn("Schüler", disabled=True), "ID": st.column_config.TextColumn("ID", disabled=True)}
                with col_1:
                    ed_1 = st.data_editor(df_show.iloc[:n1].copy(), hide_index=True, use_container_width=True, column_config=cfg, key=f"arch_pick_1_{sel_cls}")
                with col_2:
                    ed_2 = st.data_editor(df_show.iloc[n1:n1+n2].copy(), hide_index=True, use_container_width=True, column_config=cfg, key=f"arch_pick_2_{sel_cls}")
                with col_3:
                    ed_3 = st.data_editor(df_show.iloc[n1+n2:].copy(), hide_index=True, use_container_width=True, column_config=cfg, key=f"arch_pick_3_{sel_cls}")
                df_merged = pd.concat([ed_1, ed_2, ed_3], ignore_index=True)
                base = st.session_state[state_key].copy()
                base["ID"] = base["ID"].astype(str)
                df_merged["ID"] = df_merged["ID"].astype(str)
                sel_map = df_merged.set_index("ID")["Auswahl"]
                base["Auswahl"] = base["ID"].map(sel_map).fillna(base["Auswahl"]).astype(bool)
                st.session_state[state_key] = base

                # 4) Begründung
                reason = st.text_input("4) Begründung", value="", key=f"arch_reason_{sel_cls}")
                ids = st.session_state[state_key][st.session_state[state_key]["Auswahl"] == True]["ID"].astype(str).tolist()
                st.caption(f"Ausgewählt: {len(ids)} Schüler")
                if st.button("📦 Archivieren", type="primary", key=f"arch_go_{sel_cls}"):
                    with st.spinner("Archivieren läuft… bitte warten"):
                        ok, msg = archive_students(ids, reason=reason)
                    (st.success if ok else st.error)(msg)
                    if ok:
                        st.session_state["arch_flash_msg"] = msg
                        st.session_state["arch_flash_balloons"] = True
                        st.rerun()
            else:
                st.info("Bitte eine Klasse auswählen.")

        st.markdown("---"); st.markdown("###### 📜 Buchungs-Logbuch")
        if not log_df.empty:
            display_df = filtered_df if 'filtered_df' in locals() else log_df
            st.dataframe(display_df[['Zeitstempel', 'Name', 'Klasse', 'Beschreibung', 'Betrag', 'Erfasst_Von']], use_container_width=True, hide_index=True)

# -----------------------------------------------------------------------------
# ERZIEHUNGSBERECHTIGTE BEREICH
# -----------------------------------------------------------------------------
if menu == "Familien-Login":
    st.header("👨‍👩‍👧 Familien-Login")
    try:
        query_params = st.query_params
        url_code = query_params.get("code", "")
    except: url_code = ""

    c = url_code if url_code else ""
    ic = st.text_input("Bitte Zugangscode eingeben:", value=c, type="password")
    
    if ic:
        # Fehlversuchs-Sperre (Brute-Force-Schutz)
        locked, rem = fam_check_lockout(prefix='fam', max_tries=5, base_lock_s=60)
        if locked:
            st.warning(f"Zu viele Fehlversuche. Bitte {rem} Sekunden warten.")
            st.stop()
        if 'Zugangscode' in df_stamm.columns:
            clean_code = ic.strip()
            r = df_stamm[df_stamm['Zugangscode']==clean_code]
            if not r.empty:
                d = r.iloc[0]; student_name = d['Name']; student_class = d['Klasse']
                fam_reset_lockout(prefix='fam'); st.info(f"Schüler: **{student_name}** ({student_class})")
                
                if not df_klassen.empty:
                    msg_row = df_klassen[df_klassen['Klasse'] == student_class]
                    if not msg_row.empty:
                        msg_text = str(msg_row.iloc[0]['Nachricht'])
                        if msg_text and msg_text != "nan": st.warning(f"📢 Nachricht von der Schule:\n\n{msg_text}")
                
                sv=str(d['ID']).replace(".0","").strip().upper()
                b = _get_buchungen_lazy()[_get_buchungen_lazy()['ID']==sv].copy()
                
                if not b.empty:
                    sal = b['Betrag'].sum(); col_delta = "normal" if sal>=0 else "inverse"
                    st.metric("Guthaben", f"{sal:.2f} €", delta_color=col_delta)
                    if not df_klassen.empty:
                        k = d['Klasse']; kr = df_klassen[df_klassen['Klasse'] == k]
                        if not kr.empty:
                            iban = kr.iloc[0]['IBAN']; bic = kr.iloc[0]['BIC'] if 'BIC' in kr.columns else ""
                            empf = kr.iloc[0]['Empfaenger'] if 'Empfaenger' in kr.columns and str(kr.iloc[0]['Empfaenger']) != "nan" else "MS Niederndorf"
                            if iban:
                                if sal < 0: st.warning(f"Aktueller Fehlbetrag: {abs(sal):.2f} €"); amount_qr = abs(sal)
                                else: amount_qr = 0.00
                                st.write("Scannen Sie diesen Code mit Ihrer Banking-App für eine einfache Überweisung.")
                                qr_text = f"{sv} {d['Name']}"
                                qr_buffer = generate_epc_qr(iban, bic, empf, amount_qr, qr_text)
                                if qr_buffer: st.image(qr_buffer, width=200)
                    
                    b = b.sort_values('Datum', ascending=False)
                    b['Datum'] = pd.to_datetime(b['Datum']).dt.strftime(DATE_DISPLAY_FMT)
                    def col(v): return f'color: {"#d9534f" if v<0 else "#28a745"}; font-weight: bold'
                    st.dataframe(b[['Datum','Beschreibung','Betrag']].style.map(col, subset=['Betrag']).format({"Betrag":"{:.2f} €"}), hide_index=True, use_container_width=True)
                    if not df_klassen.empty:
                        k = d['Klasse']; kr = df_klassen[df_klassen['Klasse'] == k]
                        if not kr.empty:
                            iban = kr.iloc[0]['IBAN']; bic = kr.iloc[0]['BIC'] if 'BIC' in kr.columns else ""; empf = kr.iloc[0]['Empfaenger'] if 'Empfaenger' in kr.columns and str(kr.iloc[0]['Empfaenger']) != "nan" else "MS Niederndorf"
                            pdf_bytes = create_pdf_report(d['Name'], d['Klasse'], b, iban, bic, empf, sv)
                        else: pdf_bytes = create_pdf_report(d['Name'], d['Klasse'], b)
                    else: pdf_bytes = create_pdf_report(d['Name'], d['Klasse'], b)
                    st.download_button("📄 Kontoauszug (PDF)", data=pdf_bytes, file_name=f"Kontoauszug_{d['Name']}.pdf", mime='application/pdf')
                else: st.info("Keine Umsätze.")
            else: fam_register_fail(prefix='fam', max_tries=5, base_lock_s=60); time.sleep(0.6); st.error("Code ungültig.")
        else: st.error("Wartung: Datenbankfehler.")

st.divider(); st.caption("MS Niederndorf v30.4 (Secure & Private)")





