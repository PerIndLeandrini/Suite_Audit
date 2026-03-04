from __future__ import annotations

import csv
import io
from datetime import date, datetime
from pathlib import Path
from typing import Dict, List, Tuple

import streamlit as st
import pandas as pd
import time
import hmac

# PDF
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle

# -----------------------------
# Icona stato audit
# -----------------------------
def esito_icon(esito: str) -> str:
    e = (esito or "").lower()

    if "conforme" in e and "non" not in e:
        return "✅"
    elif "migliorabile" in e:
        return "⚠️"
    elif "non conforme" in e:
        return "❌"
    elif "critica" in e:
        return "⛔"
    else:
        return "•"

# -----------------------
# CONFIG
# -----------------------
st.set_page_config(
    page_title="Mini Audit 4Step",
    page_icon="🧩",
    layout="wide",
)


# -----------------------------
# Confronto password sicuro
# -----------------------------
def _check_pw(plain: str, stored: str) -> bool:
    return hmac.compare_digest(plain or "", stored or "")


# -----------------------------
# Lettura utenti da secrets
# -----------------------------
def get_users_from_secrets():
    try:
        users = st.secrets["auth"]["users"]
        passwords = st.secrets["auth"]["passwords"]

        # costruisce dict {username: password}
        return dict(zip(users, passwords))
    except Exception:
        return {}


# -----------------------------
# LOGIN PAGE
# -----------------------------
def login_gate(logo_path="logo.png"):

    if st.session_state.get("auth_ok"):
        return

    users = get_users_from_secrets()

    col1, col2, col3 = st.columns([1,2,1])

    with col2:

        try:
            st.image(logo_path, width=240)
        except:
            pass

        st.markdown("## 🔐 Accesso Mini Audit 4Step")
        st.caption("Inserisci le credenziali per continuare.")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        colA, colB = st.columns(2)

        with colA:
            login = st.button("✅ Entra", use_container_width=True)

        with colB:
            clear = st.button("🧹 Pulisci", use_container_width=True)

        if clear:
            st.rerun()

        if login:
            stored_pw = users.get(username)

            if stored_pw and _check_pw(password, stored_pw):
                st.session_state["auth_ok"] = True
                st.session_state["auth_user"] = username
                st.success("Accesso eseguito.")
                time.sleep(0.4)
                st.rerun()
            else:
                st.error("Credenziali non valide")

    st.stop()


# -----------------------------
# ATTIVA LOGIN
# -----------------------------
login_gate("logo.png")
# Palette “nostra” (navy / azzurro / bianco + grigi soft)
NAVY = "#0B1F3A"
NAVY_2 = "#0A1730"
AZURE = "#2F80ED"
LIGHT = "#F5F8FF"
SOFT = "#EEF3FF"
TEXT = "#101828"
BORDER = "rgba(16,24,40,0.10)"

# -----------------------
# CSS (fix invisibilità testi)
# - Sidebar scura
# - Testi sidebar bianchi SOLO per markdown/label
# - INPUT/SELECT in sidebar SEMPRE leggibili (sfondo bianco + testo scuro)
# -----------------------
st.markdown(
    f"""
<style>
:root {{
  --navy: {NAVY};
  --navy2: {NAVY_2};
  --azure: {AZURE};
  --light: {LIGHT};
  --soft: {SOFT};
  --text: {TEXT};
  --border: {BORDER};
}}

.stApp {{
  background: linear-gradient(180deg, var(--light) 0%, #ffffff 60%);
  color: var(--text);
}}

section[data-testid="stSidebar"] {{
  background: linear-gradient(180deg, var(--navy) 0%, var(--navy2) 100%);
}}

/* SOLO testi in sidebar (markdown/label) bianchi */
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stCaption,
section[data-testid="stSidebar"] .stSubheader {{
  color: #ffffff !important;
}}

/* INPUTS sidebar: forza leggibilità */
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea {{
  background: #ffffff !important;
  color: #111827 !important;
  border: 1px solid rgba(255,255,255,0.25) !important;
}}

section[data-testid="stSidebar"] [data-baseweb="select"] > div {{
  background: #ffffff !important;
  color: #111827 !important;
  border: 1px solid rgba(255,255,255,0.25) !important;
}}
section[data-testid="stSidebar"] [data-baseweb="select"] span {{
  color: #111827 !important;
}}

/* Cards */
.audit-card {{
  background: #ffffff;
  border: 1px solid rgba(16,24,40,0.08);
  border-radius: 18px;
  padding: 14px 16px;
  box-shadow: 0 6px 18px rgba(16,24,40,0.06);
}}
/* Sidebar score card: sempre leggibile */
section[data-testid="stSidebar"] .audit-card {{
  background: #ffffff !important;
  border: 1px solid rgba(255,255,255,0.35) !important;
}}

section[data-testid="stSidebar"] .audit-card,
section[data-testid="stSidebar"] .audit-card * {{
  color: #111827 !important;
  opacity: 1 !important;
}}
section[data-testid="stSidebar"] .audit-card .muted {{
  opacity: 1 !important;
  color: #374151 !important;
}}
.badge {{
  display: inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  font-weight: 800;
  font-size: 0.85rem;
  border: 1px solid rgba(16,24,40,0.12);
  background: var(--soft);
}}

.kpi {{
  font-size: 1.8rem;
  font-weight: 900;
  margin: 0;
}}

.muted {{
  opacity: .85;
}}

hr {{
  border: none;
  border-top: 1px solid var(--border);
  margin: 10px 0 14px 0;
}}

/* Migliora header expander */
details summary {{
  font-weight: 800 !important;
}}
/* safety net: testi main sempre leggibili */
.stApp, .stApp * {{
  color: #101828;
}}
section[data-testid="stSidebar"] * {{
  color: inherit;
}}

</style>
""",
    unsafe_allow_html=True,
)

# -----------------------
# SCORING
# -----------------------
SCORES = {
    "✅ Conforme": 2,
    "⚠️ Migliorabile": 1,
    "❌ Non conforme": 0,
    "⛔ Critica": -2,
}
SCORE_LABELS = list(SCORES.keys())

# -----------------------
# CHECKLIST (Michelin base + 4Step add-on)
# -----------------------
CHECKLIST: Dict[str, List[Tuple[str, str]]] = {
    "🧹 A — Housekeeping & Organizzazione": [
        ("I percorsi pedonali sono chiaramente definiti e liberi da ostacoli?", "Are walkways clearly defined and free of obstructions?"),
        ("I pavimenti sono puliti e privi di rifiuti?", "Are floors clean and clear of rubbish?"),
        ("Le aree di stoccaggio sono chiaramente identificate?", "Are storage areas clearly defined?"),
        ("Gli utensili manuali sono riposti nelle aree designate?", "Are hand tools in a designated area?"),
        ("Cavi elettrici ordinati e fissati?", "Is electrical cabling tied back/secured?"),
        ("Contenitori rifiuti mantenuti correttamente?", "Are waste bins maintained?"),
        ("Rifiuti separati correttamente?", "Is waste being separated properly?"),
        ("Attrezzature pulite e idonee all’uso?", "Is equipment clean and fit for function?"),
        ("Effetti personali lontani dalle aree produttive?", "Is personal property secured away from production areas?"),
        ("Bacheche informative ordinate e aggiornate?", "Are notice boards tidy and information up to date?"),
        ("Oli stoccati correttamente su bacino di contenimento?", "Is oil being stored properly on a bund?"),
        ("Assenza di perdite (olio/acqua) dai macchinari?", "Are any machines leaking oil or water?"),
        # 4Step add-on
        ("Segnaletica e marcature corsie/percorsi coerenti e visibili?", "Signage and markings (walkways/forklift lanes) visible and consistent?"),
        ("Ordine postazione operatore (5S light) mantenuto?", "Workstation order (light 5S) maintained?"),
        ("Illuminazione adeguata e senza punti critici evidenti?", "Lighting adequate with no obvious critical areas?"),
    ],
    "🦺 B — Health & Safety Operativa": [
        ("Apparecchiature elettriche portatili verificate (se applicabile)?", "Portable electrical appliances tested (if applicable)?"),
        ("Spine, cavi e interruttori in buono stato?", "Plugs, cables and switches in good repair?"),
        ("Assenza di sostanze chimiche non identificate?", "No unidentified chemicals present?"),
        ("Sostanze chimiche stoccate correttamente?", "Chemicals stored properly?"),
        ("Kit antiversamento disponibili e integri?", "Spill kits available and intact?"),
        ("DPI disponibili e correttamente utilizzati?", "PPE available and being worn?"),
        ("Istruzioni/Procedure operative visibili e comprensibili?", "Safe systems of work visible and understandable?"),
        ("Scaffalature/rack privi di danni evidenti?", "Racking free from damage?"),
        ("Assenza di lame/utensili taglienti lasciati esposti?", "No exposed blades/sharp tools left out?"),
        ("Vie di esodo/uscite di emergenza libere?", "Emergency exits and escape routes clear?"),
        ("Attrezzature di sollevamento censite/identificate e riposte correttamente?", "Lifting equipment accounted for, tagged and stored properly?"),
        ("Protezioni macchine integre e adeguate?", "Machine guards adequate and intact?"),
        ("Uso aria compressa sicuro (ugelli idonei / prassi corretta), se presente?", "Compressed air use safe (safe nozzles / correct practice), if present?"),
        # 4Step add-on
        ("Comportamenti sicuri osservati durante la visita?", "Safe behaviors observed during the walk-through?"),
        ("Nessuna condizione di rischio immediato evidente (es. improvvisazioni, bypass)?", "No obvious immediate-risk conditions (e.g., bypass, improvisations)?"),
    ],
    "📋 C — Controlli Documentali Reparto": [
        ("Controlli protezioni macchine presenti e aggiornati?", "Machinery guard checks available and up to date?"),
        ("Registro mole abrasive (se applicabile) aggiornato?", "Abrasive wheel logs (if applicable) up to date?"),
        ("Controlli carrelli elevatori (se applicabile) registrati?", "Forklift checks (if applicable) recorded?"),
        ("Controlli aspirazioni/LEV (se applicabile) disponibili?", "LEV checks (if applicable) available?"),
        ("Ispezioni/controlli supervisore registrati?", "Supervisor inspections recorded?"),
        # 4Step add-on
        ("Azioni correttive aperte visibili e gestite (se presenti)?", "Open corrective actions visible and managed (if any)?"),
        ("Evidenze formazione/abilitazioni disponibili per l’area (se rilevante)?", "Training/authorizations evidence available for the area (if relevant)?"),
    ],
}

# -----------------------
# CSV STORAGE
# -----------------------
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

RECORDS_CSV = DATA_DIR / "audit_records.csv"
FINDINGS_CSV = DATA_DIR / "audit_findings.csv"
ACTIONS_CSV = DATA_DIR / "audit_actions.csv"


def _ensure_csv(path: Path, headers: List[str]) -> None:
    if not path.exists():
        with path.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(headers)


def new_audit_id(header: dict) -> str:
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    base = (header.get("codice") or "MA-4STEP").strip()
    return f"{base}_{ts}"


def compute_score(audit: dict) -> tuple[int, int, float]:
    """
    Calcola punti e percentuale:
    - se esiste 'score' numerico per item -> usa quello
    - altrimenti mappa dall'esito (Conforme/Migliorabile/Non conforme/Critica)
    """
    results = audit.get("results", {}) or {}

    # max = 2 punti per item
    pts_max = 2 * len(results)

    ESITO_TO_SCORE = {
        "✅ Conforme": 2,
        "Conforme": 2,

        "⚠️ Migliorabile": 1,
        "Migliorabile": 1,

        "❌ Non conforme": 0,
        "Non conforme": 0,

        "⛔ Critica": 0,
        "Critica": 0,
    }

    pts = 0
    for item in results.values():
        # 1) prova score diretto (CSV viewer spesso lo ha)
        s = item.get("score", None)
        if s is not None and str(s).strip() != "":
            try:
                pts += int(float(s))
                continue
            except:
                pass

        # 2) fallback: mappa da esito
        esito = (item.get("esito") or "").strip()
        pts += ESITO_TO_SCORE.get(esito, 0)

    pct = round((pts / pts_max) * 100, 1) if pts_max else 0.0
    return pts, pts_max, pct


def status_from_pct(pct: float) -> Tuple[str, str]:
    if pct >= 90:
        return ("🟢 Controllato", "Excellent control")
    if pct >= 75:
        return ("🟡 Attenzione", "Attention")
    if pct >= 60:
        return ("🟠 Criticità", "Critical areas")
    return ("🔴 Urgente", "Urgent action")


def save_audit_to_csv(audit: dict) -> str:
    audit_id = new_audit_id(audit["header"])
    pts, pts_max, pct = compute_score(audit)
    it_status, en_status = status_from_pct(pct)
    ts = datetime.now().isoformat(timespec="seconds")

    # Records (1 riga per audit)
    records_headers = [
        "audit_id", "timestamp",
        "codice", "cliente", "reparto", "area", "auditor", "data",
        "tipo", "riferimenti",
        "points", "points_max", "score_pct", "status_it", "status_en",
        "obs_good", "obs_risky", "obs_notes",
    ]
    _ensure_csv(RECORDS_CSV, records_headers)

    h = audit["header"]
    o = audit["observations"]
    record_row = [
        audit_id, ts,
        h.get("codice", ""), h.get("cliente", ""), h.get("reparto", ""), h.get("area", ""),
        h.get("auditor", ""), h.get("data", ""),
        h.get("tipo", ""), h.get("riferimenti", ""),
        pts, pts_max, round(pct, 1), it_status, en_status,
        o.get("good", ""), o.get("risky", ""), o.get("notes", ""),
    ]
    with RECORDS_CSV.open("a", newline="", encoding="utf-8") as f:
        csv.writer(f, delimiter=";").writerow(record_row)

    # Findings (1 riga per item)
    findings_headers = ["audit_id", "section", "item_no", "esito", "score", "ita", "eng", "note"]
    _ensure_csv(FINDINGS_CSV, findings_headers)

    counters: Dict[str, int] = {}
    for r in audit["results"].values():
        section = r["section"]
        counters[section] = counters.get(section, 0) + 1
        item_no = counters[section]

        with FINDINGS_CSV.open("a", newline="", encoding="utf-8") as f:
            csv.writer(f, delimiter=";").writerow([
                audit_id, section, item_no,
                r["esito"], SCORES.get(r["esito"], 0),
                r["ita"], r["eng"], r["note"]
            ])

    # Actions (1 riga per azione)
    actions_headers = ["audit_id", "azione", "owner", "due", "status"]
    _ensure_csv(ACTIONS_CSV, actions_headers)

    for a in audit.get("actions", []):
        with ACTIONS_CSV.open("a", newline="", encoding="utf-8") as f:
            csv.writer(f, delimiter=";").writerow([
                audit_id, a.get("azione", ""), a.get("owner", ""), a.get("due", ""), a.get("status", "")
            ])

    return audit_id


# -----------------------
# PDF EXPORT
# -----------------------
def build_pdf(audit: dict, logo_path: str = "logo.png") -> bytes:
    buff = io.BytesIO()

    # Margini un filo più “larghi” rispetto ai contenuti
    doc = SimpleDocTemplate(
        buff,
        pagesize=A4,
        leftMargin=14 * mm,
        rightMargin=14 * mm,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
        title="Mini Audit 4Step",
    )

    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=15, leading=18, textColor=colors.HexColor(NAVY))
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=11, leading=14, textColor=colors.HexColor(NAVY))

    # Stili per wrapping in tabella
    cell = ParagraphStyle(
        "cell",
        parent=styles["BodyText"],
        fontSize=8.4,
        leading=10.0,
        textColor=colors.HexColor("#111827"),
        wordWrap="CJK",  # aiuta il wrap anche con stringhe “dure”
    )
    cell_small = ParagraphStyle(
        "cell_small",
        parent=cell,
        fontSize=8.0,
        leading=9.6,
    )

    body = ParagraphStyle("body", parent=styles["BodyText"], fontSize=9.2, leading=11.5, alignment=TA_LEFT)

    story = []

    # Logo
    try:
        img = RLImage(logo_path, width=38 * mm, height=16 * mm)
        story.append(img)
    except Exception:
        pass

    story.append(Spacer(1, 6))
    story.append(Paragraph("Mini Audit HSE — 4Step (ITA / ENG)", h1))
    story.append(Spacer(1, 6))

    pts, pts_max, pct = compute_score(audit)
    it_status, en_status = status_from_pct(pct)

    header = audit["header"]
    header_rows = [
        ["Codice / Code", header.get("codice", "")],
        ["Cliente / Client", header.get("cliente", "")],
        ["Reparto / Department", header.get("reparto", "")],
        ["Area / Area", header.get("area", "")],
        ["Auditor / Inspector", header.get("auditor", "")],
        ["Data / Date", header.get("data", "")],
        ["Tipo / Type", header.get("tipo", "")],
        ["Riferimenti / References", header.get("riferimenti", "")],
        ["Score", f"{pts}/{pts_max}  —  {pct:.1f}%  —  {it_status} / {en_status}"],
    ]
    t = Table(header_rows, colWidths=[42 * mm, 140 * mm])
    t.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CBD5E1")),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor(LIGHT)),
            ]
        )
    )
    story.append(t)
    story.append(Spacer(1, 10))

    # Sezioni
    for section in CHECKLIST.keys():
        story.append(Paragraph(section, h2))
        story.append(Spacer(1, 4))

        # Header tabella
        rows = [
            ["#", "Esito", "ITA", "ENG", "Note"]
        ]

        idx = 0
        for r in audit["results"].values():
            if r["section"] != section:
                continue
            idx += 1

            ita_p = Paragraph(r["ita"], cell)
            eng_p = Paragraph(r["eng"], cell)
            note_txt = r["note"] or ""
            note_p = Paragraph(note_txt.replace("\n", "<br/>"), cell_small)

            rows.append([
                str(idx),
                r["esito"],
                ita_p,
                eng_p,
                note_p,
            ])

        # Colonne: stringhe lunghe su ITA/ENG -> diamo più spazio lì
        # (Se vuoi note più grandi, aumentiamo l’ultima colonna)
        col_widths = [7 * mm, 18 * mm, 70 * mm, 70 * mm, 25 * mm]

        tt = Table(rows, colWidths=col_widths, repeatRows=1)
        tt.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(NAVY)),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CBD5E1")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 9),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ]
            )
        )

        story.append(tt)
        story.append(Spacer(1, 10))

    # Observations
    obs = audit["observations"]
    story.append(Paragraph("🧠 Osservazioni / Observations", h2))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<b>Buone pratiche / Good practices</b><br/>{(obs.get('good') or '—')}", body))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<b>Comportamenti a rischio / Risky behaviors</b><br/>{(obs.get('risky') or '—')}", body))
    story.append(Spacer(1, 4))
    story.append(Paragraph(f"<b>Note / Notes</b><br/>{(obs.get('notes') or '—')}", body))
    story.append(Spacer(1, 10))

    # Actions
    story.append(Paragraph("🔧 Azioni e Follow-up / Actions & Follow-up", h2))
    story.append(Spacer(1, 4))

    if audit["actions"]:
        arows = [["Azione / Action", "Responsabile / Owner", "Scadenza / Due", "Stato / Status"]]
        for a in audit["actions"]:
            arows.append([
                Paragraph(a.get("azione", "") or "", cell),
                Paragraph(a.get("owner", "") or "", cell_small),
                Paragraph(a.get("due", "") or "", cell_small),
                Paragraph(a.get("status", "") or "", cell_small),
            ])

        at = Table(arows, colWidths=[95 * mm, 40 * mm, 23 * mm, 22 * mm], repeatRows=1)
        at.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(NAVY)),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CBD5E1")),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ]
            )
        )
        story.append(at)
    else:
        story.append(Paragraph("Nessuna azione registrata. / No actions recorded.", body))

    doc.build(story)
    pdf_bytes = buff.getvalue()
    buff.close()
    return pdf_bytes

# -----------------------
# SESSION STATE INIT
# -----------------------
def ss_init():
    if "audit" not in st.session_state:
        st.session_state.audit = {
            "header": {
                "codice": "MA-4STEP-01",
                "cliente": "",
                "reparto": "",
                "area": "Tutte le aree",
                "auditor": "",
                "data": date.today().isoformat(),
                "tipo": "Periodica",
                "riferimenti": "ISO 45001 / SGI interno",
            },
            "results": {},
            "actions": [],
            "observations": {"good": "", "risky": "", "notes": ""},
        }

        for section, items in CHECKLIST.items():
            for i, (ita, eng) in enumerate(items, start=1):
                key = f"{section}__{i}"
                st.session_state.audit["results"][key] = {
                    "section": section,
                    "ita": ita,
                    "eng": eng,
                    "esito": "✅ Conforme",
                    "note": "",
                }


ss_init()


def _find_record(records_list: list[dict], audit_id: str) -> dict | None:
    for r in records_list:
        if r.get("audit_id") == audit_id:
            return r
    return None

def build_audit_from_csv(audit_id: str, records_csv, findings_csv, actions_csv) -> dict:
    """Ricostruisce il dict 'audit' (header + results + observations + actions) a partire dai CSV."""
    records_list = read_csv_dicts(records_csv) if records_csv.exists() else []
    rec = _find_record(records_list, audit_id) or {}

    findings_list = [d for d in read_csv_dicts(findings_csv) if d.get("audit_id") == audit_id] if findings_csv.exists() else []
    actions_list  = [a for a in read_csv_dicts(actions_csv)  if a.get("audit_id") == audit_id] if actions_csv.exists() else []

    # Header (campi che già salvi in audit_records.csv)
    header = {
        "codice": rec.get("codice", ""),
        "cliente": rec.get("cliente", ""),
        "reparto": rec.get("reparto", ""),
        "area": rec.get("area", ""),
        "auditor": rec.get("auditor", ""),
        "data": rec.get("data", ""),
        "tipo": rec.get("tipo", ""),
        "riferimenti": rec.get("riferimenti", ""),
    }

    # Observations (se sono nel record)
    observations = {
        "good":  rec.get("obs_good", ""),
        "risky": rec.get("obs_risky", ""),
        "notes": rec.get("obs_notes", ""),
    }

    # Results: dict indicizzato, come usa la tua build_pdf (section + esito + score + ita/eng/note)
    # chiave stabile: "SECTION|item_no"
    results = {}
    for f in findings_list:
        key = f"{f.get('section','')}|{f.get('item_no','')}"
        try:
            score = int(f.get("score", 0))
        except:
            score = 0
        results[key] = {
            "section": f.get("section", ""),
            "item_no": f.get("item_no", ""),
            "esito": f.get("esito", ""),
            "score": score,
            "ita": f.get("ita", ""),
            "eng": f.get("eng", ""),
            "note": f.get("note", ""),
        }

    audit = {
        "audit_id": audit_id,
        "header": header,
        "observations": observations,
        "results": results,
        "actions": actions_list,
    }
    return audit
# -----------------------
# NAV
# -----------------------
with st.sidebar:
    # Logo
    try:
        st.image("logo.png", use_container_width=True)
    except Exception:
        st.markdown("**logo.png non trovato**")

    st.markdown("### 🧩 Mini Audit 4Step")
    st.caption("Bilingue ITA/ENG • Scoring live • Export PDF • Storico CSV")

    page = st.radio("Navigazione", ["🧩 Nuovo Audit", "📊 Storico & Analytics"], index=0)

    st.markdown("---")
    # Header fields
    h = st.session_state.audit["header"]
    h["codice"] = st.text_input("Codice Audit", h["codice"])
    h["cliente"] = st.text_input("Cliente", h["cliente"])
    h["reparto"] = st.text_input("Reparto / Department", h["reparto"])
    h["area"] = st.text_input("Area", h["area"])
    h["auditor"] = st.text_input("Auditor / Inspector", h["auditor"])
    h["data"] = str(st.date_input("Data", date.fromisoformat(h["data"])))
    h["tipo"] = st.selectbox("Tipo verifica", ["Periodica", "Cliente", "Interna", "Follow-up"],
                             index=["Periodica", "Cliente", "Interna", "Follow-up"].index(h["tipo"]))
    h["riferimenti"] = st.text_input("Riferimenti", h["riferimenti"])

    st.markdown("---")
    pts, pts_max, pct = compute_score(st.session_state.audit)
    it_status, _ = status_from_pct(pct)

    st.markdown(
        f"<div class='audit-card'><div class='badge'>📊 SCORE</div>"
        f"<p class='kpi'>{pct:.1f}%</p><p class='muted'>{pts}/{pts_max} • {it_status}</p></div>",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    # Actions buttons
    colA, colB = st.columns(2)
    with colA:
        if st.button("🧾 PDF", use_container_width=True):
            st.session_state["_last_pdf"] = build_pdf(st.session_state.audit, logo_path="logo.png")
    with colB:
        if st.button("💾 Salva", use_container_width=True):
            audit_id = save_audit_to_csv(st.session_state.audit)
            st.success(f"Salvato ✅ ID: {audit_id}")

    if "_last_pdf" in st.session_state:
        st.download_button(
            "⬇️ Scarica PDF",
            data=st.session_state["_last_pdf"],
            file_name=f"{st.session_state.audit['header'].get('codice','mini_audit')}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    st.markdown("---")
    with st.expander("⚙️ Reset"):
        if st.button("Reset audit (tutto Conforme)", use_container_width=True):
            for r in st.session_state.audit["results"].values():
                r["esito"] = "✅ Conforme"
                r["note"] = ""
            st.session_state.audit["actions"] = []
            st.session_state.audit["observations"] = {"good": "", "risky": "", "notes": ""}
            st.rerun()


# -----------------------
# PAGE: STORICO
# -----------------------
def read_csv_dicts(path: Path) -> List[dict]:
    with path.open("r", encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter=";"))


if page == "📊 Storico & Analytics":
    st.markdown("## 📊 Storico audit")

    if not RECORDS_CSV.exists():
        st.info("Ancora nessun audit salvato. Premi **💾 Salva** dopo aver compilato un audit.")
        st.stop()

    rows = read_csv_dicts(RECORDS_CSV)

    # filtri
    clienti = sorted({r["cliente"] for r in rows if r.get("cliente")})
    reparti = sorted({r["reparto"] for r in rows if r.get("reparto")})
    auditor = sorted({r["auditor"] for r in rows if r.get("auditor")})

    c1, c2, c3 = st.columns(3)
    with c1:
        f_cliente = st.selectbox("Cliente", ["(tutti)"] + clienti)
    with c2:
        f_reparto = st.selectbox("Reparto", ["(tutti)"] + reparti)
    with c3:
        f_auditor = st.selectbox("Auditor", ["(tutti)"] + auditor)

    filtered = [
        r for r in rows
        if (f_cliente == "(tutti)" or r.get("cliente") == f_cliente)
        and (f_reparto == "(tutti)" or r.get("reparto") == f_reparto)
        and (f_auditor == "(tutti)" or r.get("auditor") == f_auditor)
    ]

    st.caption(f"Audit trovati: **{len(filtered)}**")

    # tabella storico
    table = []
    for r in reversed(filtered):
        table.append({
            "timestamp": r.get("timestamp", ""),
            "codice": r.get("codice", ""),
            "cliente": r.get("cliente", ""),
            "reparto": r.get("reparto", ""),
            "auditor": r.get("auditor", ""),
            "score_%": r.get("score_pct", ""),
            "stato": r.get("status_it", ""),
            "audit_id": r.get("audit_id", ""),
        })

    st.dataframe(table, use_container_width=True, height=180)

    # download CSV grezzi
    dc1, dc2, dc3 = st.columns(3)
    with dc1:
        st.download_button("⬇️ Download audit_records.csv", data=RECORDS_CSV.read_bytes(),
                           file_name="audit_records.csv", mime="text/csv", use_container_width=True)
    with dc2:
        if FINDINGS_CSV.exists():
            st.download_button("⬇️ Download audit_findings.csv", data=FINDINGS_CSV.read_bytes(),
                               file_name="audit_findings.csv", mime="text/csv", use_container_width=True)
    with dc3:
        if ACTIONS_CSV.exists():
            st.download_button("⬇️ Download audit_actions.csv", data=ACTIONS_CSV.read_bytes(),
                               file_name="audit_actions.csv", mime="text/csv", use_container_width=True)
        

    st.markdown("---")

    # Expander SEMPRE visibile
    with st.expander("🔎 Vuoi analizzare il dettaglio di un audit?", expanded=True):
        audit_ids = [r.get("audit_id", "") for r in reversed(filtered)]
        audit_ids = [x for x in audit_ids if x]

        if not audit_ids:
            st.info("Nessun audit disponibile con i filtri selezionati.")
            sel_id = None
        else:
            sel_id = st.selectbox("Seleziona audit", audit_ids, key="viewer_audit_id")
            st.caption("Suggerimento: seleziona l’audit e scorri i dettagli qui sotto.")

    # DETTAGLIO FUORI dall'expander (full width)
    if sel_id:
        st.markdown(f"### 📌 Dettaglio audit: `{sel_id}`")

        if FINDINGS_CSV.exists():
        
            # -----------------------------
            # Lettura dati
            # -----------------------------
            det_list = [
                d for d in read_csv_dicts(FINDINGS_CSV)
                if d.get("audit_id") == sel_id
            ]

            if det_list:
                det_df = pd.DataFrame(det_list)

                # -----------------------------
                # Ordinamento
                # -----------------------------
                if "item_no" in det_df.columns:
                    det_df["item_no"] = det_df["item_no"].astype(int)

                det_df = det_df.sort_values(["section", "item_no"], ascending=[True, True])

                # -----------------------------
                # ICONA ESITO (NUOVO)
                # -----------------------------
                det_df["icon"] = det_df["esito"].apply(esito_icon)

                # -----------------------------
                # Ordine colonne (safe)
                # -----------------------------
                cols = [
                    "icon",
                    "esito",
                    "score",
                    "section",
                    "item_no",
                    "ita",
                    "eng",
                    "note",
                ]

                cols = [c for c in cols if c in det_df.columns]
                det_df = det_df[cols]

                # -----------------------------
                # (1) HEIGHT DINAMICA
                # -----------------------------
                rows = len(det_df)
                height = min(1400, max(420, 38 * (rows + 1)))

                # -----------------------------
                # UI
                # -----------------------------
                st.markdown("#### Checklist (findings)")

                st.data_editor(
                    det_df,
                    use_container_width=True,
                    height=height,
                    disabled=True,
                    hide_index=True
                )

            else:
                st.info("Nessun finding disponibile per questo audit.")

            if sel_id:
                # ... (la tua tabella det_df)
            
                col_pdf1, col_pdf2 = st.columns([1, 3])
                with col_pdf1:
                    if st.button("🧾 Esporta PDF dettaglio", use_container_width=True):
                        audit_obj = build_audit_from_csv(sel_id, RECORDS_CSV, FINDINGS_CSV, ACTIONS_CSV)
            
                        pdf_bytes = build_pdf(audit_obj, logo_path="logo.png")  # riusa la tua build_pdf
                        st.download_button(
                            "⬇️ Scarica PDF",
                            data=pdf_bytes,
                            file_name=f"{sel_id}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )

        if ACTIONS_CSV.exists():
            act_list = [a for a in read_csv_dicts(ACTIONS_CSV) if a.get("audit_id") == sel_id]
            act_df = pd.DataFrame(act_list)

            st.markdown("#### Azioni (actions)")
            st.data_editor(
                act_df,
                use_container_width=True,
                height=320,
                disabled=True,
                hide_index=True
            )


    st.stop()

def compute_score_from_results(audit: dict) -> tuple[int, int, float]:
    """
    Ritorna: points, points_max, pct
    Calcola SEMPRE dai risultati della checklist (audit['results']).
    """
    results = audit.get("results", {}) or {}

    # ogni item vale 2 punti (come in app) -> max = 2 * numero item
    n_items = len(results)
    points_max = 2 * n_items if n_items else 0

    points = 0
    for _, item in results.items():
        try:
            points += int(item.get("score", 0))
        except Exception:
            points += 0

    pct = round((points / points_max) * 100, 1) if points_max else 0.0
    return points, points_max, pct

def esito_icon(esito: str) -> str:
    e = (esito or "").lower()
    if "conforme" in e:
        return "✅"
    if "migliorabile" in e:
        return "⚠️"
    if "non conforme" in e:
        return "❌"
    if "critica" in e:
        return "⛔"
    return "•"
# -----------------------
# PAGE: NUOVO AUDIT
# -----------------------
st.markdown("## 🧩 Mini Audit HSE — 4Step (ITA / ENG)")
st.caption("Checklist Michelin preserved + upgrade 4Step: scoring, osservazioni, azioni, storico CSV. Export PDF con logo.")

# KPI row
pts, pts_max, pct = compute_score(st.session_state.audit)
it_status, en_status = status_from_pct(pct)

c1, c2, c3 = st.columns([1.15, 1.05, 2.2])
with c1:
    st.markdown(
        "<div class='audit-card'><div class='badge'>📌 STATO</div>"
        f"<p class='kpi'>{it_status}</p><p class='muted'>{en_status}</p></div>",
        unsafe_allow_html=True,
    )
with c2:
    st.markdown(
        "<div class='audit-card'><div class='badge'>📈 SCORE</div>"
        f"<p class='kpi'>{pct:.1f}%</p><p class='muted'>{pts}/{pts_max}</p></div>",
        unsafe_allow_html=True,
    )
with c3:
    st.markdown(
        "<div class='audit-card'><div class='badge'>🧠 REGOLA</div>"
        "<p class='muted'>✅=2 • ⚠️=1 • ❌=0 • ⛔=-2  |  Sotto 60% = 🔴 Urgente</p></div>",
        unsafe_allow_html=True,
    )

st.markdown("<hr/>", unsafe_allow_html=True)

# Sections
for section, items in CHECKLIST.items():
    with st.expander(section, expanded=True):
        for i, (ita, eng) in enumerate(items, start=1):
            key = f"{section}__{i}"
            r = st.session_state.audit["results"][key]

            a, b, c = st.columns([1.2, 2.6, 1.2])
            with a:
                r["esito"] = st.selectbox(
                    "Esito / Outcome",
                    SCORE_LABELS,
                    index=SCORE_LABELS.index(r["esito"]),
                    key=f"{key}__esito",
                )
            with b:
                st.markdown(f"**ITA:** {ita}<br/>**ENG:** {eng}", unsafe_allow_html=True)
            with c:
                r["note"] = st.text_input("Note", r["note"], key=f"{key}__note")

# Observations
st.markdown("### 🧠 Osservazioni (qualitative)")
o1, o2 = st.columns(2)
with o1:
    st.session_state.audit["observations"]["good"] = st.text_area(
        "Buone pratiche osservate / Good practices",
        st.session_state.audit["observations"]["good"],
        height=120,
    )
with o2:
    st.session_state.audit["observations"]["risky"] = st.text_area(
        "Comportamenti a rischio / Risky behaviors",
        st.session_state.audit["observations"]["risky"],
        height=120,
    )

st.session_state.audit["observations"]["notes"] = st.text_area(
    "Note generali / General notes",
    st.session_state.audit["observations"]["notes"],
    height=90,
)

st.markdown("<hr/>", unsafe_allow_html=True)

# Actions
st.markdown("### 🔧 Azioni e Follow-up")
st.caption("Aggiungi azioni correttive o miglioramenti. Finiscono anche nel PDF e nello storico CSV.")

if st.button("➕ Aggiungi azione"):
    st.session_state.audit["actions"].append({"azione": "", "owner": "", "due": "", "status": "Aperta"})

if st.session_state.audit["actions"]:
    for idx, a in enumerate(st.session_state.audit["actions"]):
        st.markdown(f"**Azione {idx + 1}**")
        x1, x2, x3, x4, x5 = st.columns([2.2, 1.2, 1.1, 1.0, 0.5])
        with x1:
            a["azione"] = st.text_input("Azione / Action", a["azione"], key=f"act_{idx}_azione")
        with x2:
            a["owner"] = st.text_input("Responsabile / Owner", a["owner"], key=f"act_{idx}_owner")
        with x3:
            a["due"] = st.text_input("Scadenza / Due (YYYY-MM-DD)", a["due"], key=f"act_{idx}_due")
        with x4:
            a["status"] = st.selectbox("Stato / Status", ["Aperta", "In corso", "Chiusa"],
                                       index=["Aperta", "In corso", "Chiusa"].index(a["status"]),
                                       key=f"act_{idx}_status")
        with x5:
            if st.button("🗑️", key=f"act_{idx}_del"):
                st.session_state.audit["actions"].pop(idx)
                st.rerun()

st.markdown("<hr/>", unsafe_allow_html=True)
st.info("Suggerimento operativo: compila, poi premi **💾 Salva** (storico CSV) e/o **🧾 PDF** dalla sidebar.")
