import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date, time
import holidays

# ══════════════════════════════════════════════
# 설정
# ══════════════════════════════════════════════
SHEET_ID = "1dcAiu3SeFb4OU4xZaen8qfjqKf64GJtasXCK6t-OEvw"
GID_MAP  = {"agent":"0","phone":"754152852","chat":"1359982286","board":"677677090"}
WORK_START, WORK_END = 10, 18

COLORS = {
    "primary":"#6366f1","success":"#22c55e","danger":"#ef4444",
    "warning":"#f59e0b","info":"#3b82f6","neutral":"#94a3b8",
    "phone":"#6366f1","chat":"#22c55e","board":"#f59e0b",
}
PALETTE = ["#6366f1","#22c55e","#f59e0b","#3b82f6","#ef4444",
           "#8b5cf6","#06b6d4","#f97316","#ec4899","#14b8a6"]

TENURE_GROUPS = [
    (14,"신입1 (2주이내)"),(30,"신입2 (1개월이내)"),(60,"신입3 (2개월이내)"),
    (90,"신입4 (3개월이내)"),(180,"신입5 (6개월이내)"),(365,"신입6 (1년이내)"),
    (548,"기존1 (1.5년이내)"),(730,"기존2 (2년이내)"),(1095,"기존3 (3년이내)"),
    (1460,"기존4 (4년이내)"),(9999,"기존5 (4년초과)"),
]

MENU_GROUPS = {
    "전체 현황":["전체 현황"],
    "VOC 분석":["VOC 인입 분석"],
    "사업자":["사업자 현황"],
    "전화":["전화 현황","전화 상담사"],
    "채팅":["채팅 현황","채팅 상담사"],
    "게시판":["게시판 현황","게시판 상담사"],
    "상담사":["상담사 종합"],
}

# ══════════════════════════════════════════════
# 페이지 설정
# ══════════════════════════════════════════════
st.set_page_config(
    page_title="Contact Center OPS",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ← 여기에 바로 붙여넣기
st.markdown("""
<style>
section[data-testid="stSidebar"] {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    transform: none !important;
    width: 230px !important;
    min-width: 230px !important;
    position: relative !important;
    left: 0 !important;
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
}
section[data-testid="stSidebar"] > div {
    display: block !important;
    visibility: visible !important;
    width: 230px !important;
}
[data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    pointer-events: all !important;
    position: fixed !important;
    left: 230px !important;
    top: 50% !important;
    z-index: 999999 !important;
    background: #1e293b !important;
    border-radius: 0 8px 8px 0 !important;
    padding: 8px 4px !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-left: none !important;
    box-shadow: 3px 0 10px rgba(0,0,0,0.2) !important;
}
[data-testid="collapsedControl"] svg {
    fill: #e2e8f0 !important;
    color: #e2e8f0 !important;
    width: 16px !important;
    height: 16px !important;
}
[data-testid="collapsedControl"]:hover {
    background: #6366f1 !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── 기본 리셋 ── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, sans-serif !important;
    background: #F0F2F5 !important;
    color: #0f172a;
}

/* ── 메인 컨테이너 ── */
.main .block-container {
    padding: 20px 26px !important;
    max-width: 100% !important;
    background: #F0F2F5 !important;
}

/* ── 사이드바 본체 ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
    min-width: 230px !important;
    max-width: 230px !important;
}
section[data-testid="stSidebar"] > div:first-child {
    padding-top: 0 !important;
}
section[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}

/* ── 사이드바 토글(화살표) 버튼 - 절대 숨기지 않음 ── */
button[data-testid="collapsedControl"],
[data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    pointer-events: auto !important;
    z-index: 9999 !important;
    background: #1e293b !important;
    border-right: 1px solid rgba(255,255,255,0.1) !important;
    color: #e2e8f0 !important;
    width: 1.5rem !important;
    min-width: 1.5rem !important;
}
[data-testid="collapsedControl"] svg {
    fill: #e2e8f0 !important;
    color: #e2e8f0 !important;
}

/* ── 사이드바 버튼 ── */
section[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
    color: #cbd5e1 !important;
    width: 100% !important;
    text-align: left !important;
    padding: 9px 12px !important;
    font-size: 12.5px !important;
    font-weight: 600 !important;
    margin-bottom: 4px !important;
    transition: all .15s ease !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(99,102,241,0.20) !important;
    border-color: rgba(99,102,241,0.40) !important;
    color: #fff !important;
    transform: translateX(2px) !important;
}

/* ── 활성 메뉴 ── */
.sidebar-active button {
    background: rgba(99,102,241,0.28) !important;
    border-color: rgba(99,102,241,0.55) !important;
    color: #fff !important;
    box-shadow: 0 3px 12px rgba(99,102,241,0.25) !important;
}

/* ── 사이드바 라디오/슬라이더 ── */
section[data-testid="stSidebar"] .stRadio label {
    font-size: 12px !important;
    font-weight: 600 !important;
    color: #cbd5e1 !important;
}
section[data-testid="stSidebar"] .stDateInput input {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 8px !important;
    color: #e2e8f0 !important;
    font-size: 12px !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] {
    background: rgba(255,255,255,0.07) !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] * {
    color: #e2e8f0 !important;
    background: #1e293b !important;
}

/* ── 대시보드 헤더 ── */
.dash-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
    padding: 16px 22px;
    background: #fff;
    border-radius: 16px;
    box-shadow: 0 1px 8px rgba(15,23,42,0.07);
    border: 1px solid rgba(226,232,240,0.8);
}
.dash-header-left h1 {
    font-size: 19px;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -.5px;
    margin-bottom: 3px;
}
.dash-header-left span {
    font-size: 11.5px;
    color: #94a3b8;
    font-weight: 600;
}
.dash-badge {
    font-size: 11.5px;
    color: #6366f1;
    background: rgba(99,102,241,0.08);
    padding: 6px 14px;
    border-radius: 999px;
    font-weight: 800;
    border: 1px solid rgba(99,102,241,0.15);
}

/* ── 섹션 타이틀 ── */
.section-title {
    font-size: 14px;
    font-weight: 800;
    color: #0f172a;
    margin: 20px 0 10px;
    letter-spacing: -.3px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-title::before {
    content: '';
    display: inline-block;
    width: 3px;
    height: 16px;
    background: #6366f1;
    border-radius: 2px;
}

/* ── 카드 ── */
.card {
    background: #fff;
    border-radius: 16px;
    box-shadow: 0 1px 8px rgba(15,23,42,0.06);
    padding: 18px 20px;
    border: 1px solid rgba(226,232,240,0.7);
    margin-bottom: 4px;
}
.card-title {
    font-size: 12.5px;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 3px;
    letter-spacing: -.2px;
}
.card-subtitle {
    font-size: 10.5px;
    font-weight: 600;
    color: #94a3b8;
    margin-bottom: 12px;
}

/* ── KPI 카드 ── */
.kpi-card {
    background: #fff;
    border-radius: 16px;
    box-shadow: 0 1px 8px rgba(15,23,42,0.06);
    padding: 18px 20px;
    border: 1px solid rgba(226,232,240,0.7);
    height: 100%;
    position: relative;
    overflow: hidden;
}
.kpi-card::after {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 3px; height: 100%;
    background: linear-gradient(180deg, #6366f1, #8b5cf6);
    border-radius: 0 2px 2px 0;
}
.kpi-card.green::after  { background: linear-gradient(180deg,#22c55e,#16a34a); }
.kpi-card.orange::after { background: linear-gradient(180deg,#f59e0b,#d97706); }
.kpi-card.red::after    { background: linear-gradient(180deg,#ef4444,#dc2626); }
.kpi-card.blue::after   { background: linear-gradient(180deg,#3b82f6,#2563eb); }
.kpi-label {
    font-size: 10.5px;
    font-weight: 800;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: .6px;
    margin-bottom: 8px;
}
.kpi-value {
    font-size: 22px;
    font-weight: 900;
    color: #0f172a;
    letter-spacing: -1px;
    line-height: 1.1;
    margin-bottom: 8px;
}
.kpi-unit {
    font-size: 12px;
    color: #94a3b8;
    margin-left: 3px;
    font-weight: 700;
}
.kpi-delta-row {
    display: flex;
    gap: 5px;
    flex-wrap: wrap;
    align-items: center;
    margin-top: 6px;
}
.kpi-delta {
    display: inline-flex;
    align-items: center;
    gap: 2px;
    font-size: 10.5px;
    font-weight: 800;
    padding: 3px 9px;
    border-radius: 999px;
}
.kpi-delta.up   { background: #fef2f2; color: #ef4444; }
.kpi-delta.down { background: #f0fdf4; color: #22c55e; }
.kpi-delta.neu  { background: #f8fafc; color: #94a3b8; }
.kpi-delta.up.rev   { background: #f0fdf4 !important; color: #22c55e !important; }
.kpi-delta.down.rev { background: #fef2f2 !important; color: #ef4444 !important; }

/* ── 도넛 레전드 ── */
.donut-legend { display: flex; flex-direction: column; gap: 7px; margin-top: 8px; }
.donut-item {
    display: flex; align-items: center; justify-content: space-between;
    padding: 6px 10px; border-radius: 10px;
    background: #f8fafc; transition: background .12s;
}
.donut-item:hover { background: #f1f5f9; }
.donut-left  { display: flex; align-items: center; gap: 8px; min-width: 0; flex: 1; }
.swatch      { width: 9px; height: 9px; border-radius: 3px; flex: 0 0 auto; }
.donut-label { font-size: 12px; font-weight: 700; color: #334155; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.donut-right { display: flex; align-items: center; gap: 10px; flex: 0 0 auto; }
.donut-val   { font-size: 12px; font-weight: 800; color: #0f172a; }
.donut-pct   { font-size: 11px; font-weight: 700; color: #fff; padding: 2px 7px; border-radius: 999px; min-width: 40px; text-align: center; }

/* ── 탭 ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(99,102,241,0.06) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    border: 1px solid rgba(99,102,241,0.12) !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 9px !important;
    font-weight: 700 !important;
    font-size: 12px !important;
    color: #64748b !important;
    padding: 7px 16px !important;
}
.stTabs [aria-selected="true"] {
    background: #6366f1 !important;
    color: #fff !important;
    box-shadow: 0 3px 10px rgba(99,102,241,0.3) !important;
}

/* ── Multiselect 태그 ── */
[data-baseweb="tag"] {
    background: rgba(99,102,241,0.12) !important;
    border: 1px solid rgba(99,102,241,0.25) !important;
    border-radius: 6px !important;
}

/* ── Streamlit 기본 크롬 숨김 ── */
#MainMenu  { visibility: hidden !important; }
footer     { visibility: hidden !important; }
.stDeployButton          { display: none !important; }
div[data-testid="stToolbar"] { display: none !important; }

/* ── 스크롤바 ── */
::-webkit-scrollbar       { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #f1f5f9; }
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# 한국 공휴일
# ══════════════════════════════════════════════
KR_HOLIDAYS = holidays.KR()

# ══════════════════════════════════════════════
# 유틸
# ══════════════════════════════════════════════
def hex_rgba(h, a=0.08):
    h = h.lstrip("#")
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return f"rgba({r},{g},{b},{a})"

def fmt_hms(sec):
    try:
        sec = int(round(float(sec)))
    except:
        return "0:00:00"
    if sec <= 0:
        return "0:00:00"
    h = sec // 3600
    m = (sec % 3600) // 60
    s = sec % 60
    return f"{h}:{m:02d}:{s:02d}"

def fmt_pct(val):
    try:
        return f"{float(val):.1f}%"
    except:
        return "0.0%"

def fmt_num(val):
    try:
        return f"{int(val):,}"
    except:
        return "0"

def calc_delta(curr, prev):
    """증감률(%) 계산 - 인입건수 등에 사용"""
    try:
        if prev is None or float(prev) == 0:
            return None
        return round((float(curr) - float(prev)) / float(prev) * 100, 1)
    except:
        return None

def calc_delta_pp(curr, prev):
    """퍼센트포인트(%p) 차이 계산 - 응대율/응답률에 사용"""
    try:
        if prev is None:
            return None
        return round(float(curr) - float(prev), 1)
    except:
        return None

def get_prev_period(df, start, end):
    """이전 동일 기간 데이터 반환"""
    if df.empty or "일자" not in df.columns:
        return pd.DataFrame()
    period_days = (pd.Timestamp(end) - pd.Timestamp(start)).days + 1
    prev_end    = pd.Timestamp(start) - timedelta(days=1)
    prev_start  = prev_end - timedelta(days=period_days - 1)
    mask = (df["일자"] >= prev_start) & (df["일자"] <= prev_end)
    return df[mask].copy()
# ✅ 여기까지 ↑↑↑

def to_date(v):
    if v is None: return None

def to_date(v):
    if v is None: return None
    if isinstance(v, date) and not isinstance(v, datetime): return v
    if isinstance(v, datetime): return v.date()
    try: return pd.Timestamp(v).date()
    except: return None

def get_tenure_group(hire_date, base_date):
    try:
        if pd.isna(hire_date): return "미입력"
    except:
        return "미입력"
    hire = to_date(hire_date)
    base = to_date(base_date)
    if not hire or not base: return "미입력"
    days = (base - hire).days
    for t, l in TENURE_GROUPS:
        if days <= t: return l
    return "기존5 (4년초과)"

def gsheet_url(gid):
    return f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"

def get_period_col(unit):
    return {"일별":"일자","주별":"주차","월별":"월"}[unit]

def assign_period_cols(df, date_col="일자"):
    if date_col not in df.columns: return df
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df["일자"] = df[date_col]
    df["주차"] = df[date_col].dt.to_period("W").dt.start_time
    df["월"]   = df[date_col].dt.to_period("M").dt.start_time
    return df

def get_chart_range(unit, end_date, month_range=3):
    ed = pd.Timestamp(end_date)
    if unit == "일별": return ed - timedelta(days=89), ed
    if unit == "주별": return ed - timedelta(weeks=12), ed
    return ed - timedelta(days=30*month_range), ed

# ══════════════════════════════════════════════
# Robust duration parser
# ══════════════════════════════════════════════
def parse_duration_seconds(v):
    """
    H:MM:SS 문자열 또는 숫자(초) 모두 초(float)로 변환
    """
    if v is None:
        return 0.0
    if isinstance(v, (int, float, np.integer, np.floating)):
        if np.isnan(v): return 0.0
        return float(v)
    s = str(v).strip()
    if s == "" or s.lower() in {"nan","none","null","-",""}:
        return 0.0
    # 순수 숫자
    try:
        return float(s)
    except:
        pass
    s = s.replace(",","").strip()
    if ":" not in s:
        return 0.0
    parts = s.split(":")
    parts = [p.strip() for p in parts if p.strip() != ""]

    # ✅ H:MM:SS (예: 0:04:57 → 297초)
    if len(parts) == 3:
        try:
            h   = float(parts[0])
            m   = float(parts[1])
            sec = float(parts[2])
            return h * 3600.0 + m * 60.0 + sec
        except:
            return 0.0

    # ✅ MM:SS (예: 04:57 → 297초)
    if len(parts) == 2:
        try:
            return float(parts[0]) * 60.0 + float(parts[1])
        except:
            return 0.0

    # ✅ 단일값
    if len(parts) == 1:
        try:
            return float(parts[0])
        except:
            return 0.0

    return 0.0

def ensure_seconds_col(df, col):
    if col not in df.columns:
        df[col] = 0.0
        return df
    df[col] = df[col].apply(parse_duration_seconds).astype(float)
    return df
# ══════════════════════════════════════════════
# 게시판 근무내/근무외 리드타임 분리
# ══════════════════════════════════════════════
def is_business_day(d: date) -> bool:
    if d.weekday() >= 5:
        return False
    return d not in KR_HOLIDAYS

def overlap_seconds(a_s: datetime, a_e: datetime, b_s: datetime, b_e: datetime) -> float:
    start = max(a_s, b_s)
    end   = min(a_e, b_e)
    if end <= start: return 0.0
    return (end - start).total_seconds()

def split_board_leadtime(start_dt, end_dt):
    """Returns (in_hours_sec, off_hours_sec, total_sec)"""
    if pd.isna(start_dt) or pd.isna(end_dt):
        return 0.0, 0.0, 0.0
    s = pd.Timestamp(start_dt).to_pydatetime()
    e = pd.Timestamp(end_dt).to_pydatetime()
    if e <= s:
        return 0.0, 0.0, 0.0
    total   = (e - s).total_seconds()
    in_sec  = 0.0
    cur_day = s.date()
    end_day = e.date()
    while cur_day <= end_day:
        day_start = datetime.combine(cur_day, time(0, 0, 0))
        day_end   = datetime.combine(cur_day, time(23, 59, 59)) + timedelta(seconds=1)
        seg_s = max(s, day_start)
        seg_e = min(e, day_end)
        if seg_e > seg_s and is_business_day(cur_day):
            bh_s = datetime.combine(cur_day, time(WORK_START, 0, 0))
            bh_e = datetime.combine(cur_day, time(WORK_END,   0, 0))
            in_sec += overlap_seconds(seg_s, seg_e, bh_s, bh_e)
        cur_day += timedelta(days=1)
    off_sec = max(total - in_sec, 0.0)
    return float(in_sec), float(off_sec), float(total)

def add_board_split_cols(df):
    if df.empty: return df
    df = df.copy()
    if "접수일시" not in df.columns or "응답일시" not in df.columns:
        for c in ["근무내리드타임(초)","근무외리드타임(초)","리드타임(초)"]:
            if c not in df.columns: df[c] = 0.0
        return df
    in_list, off_list, tot_list = [], [], []
    for sdt, edt in zip(df["접수일시"], df["응답일시"]):
        i, o, t = split_board_leadtime(sdt, edt)
        in_list.append(i); off_list.append(o); tot_list.append(t)
    df["근무내리드타임(초)"] = np.array(in_list,  dtype=float)
    df["근무외리드타임(초)"] = np.array(off_list, dtype=float)
    if "리드타임(초)" not in df.columns:
        df["리드타임(초)"] = np.array(tot_list, dtype=float)
    else:
        df["리드타임(초)"] = df["리드타임(초)"].apply(parse_duration_seconds).astype(float)
        df.loc[df["리드타임(초)"] <= 0, "리드타임(초)"] = np.array(tot_list, dtype=float)
    return df

# ══════════════════════════════════════════════
# UI 헬퍼
# ══════════════════════════════════════════════
def card_open(title=None, subtitle=None):
    inner = ""
    if title:
        inner += f"<div class='card-title'>{title}</div>"
    if subtitle:
        inner += f"<div class='card-subtitle'>{subtitle}</div>"
    st.markdown(f"<div class='card'>{inner}", unsafe_allow_html=True)

def card_close():
    st.markdown("</div>", unsafe_allow_html=True)

def section_title(txt):
    st.markdown(f"<div class='section-title'>{txt}</div>", unsafe_allow_html=True)

def donut_legend_html(labels, values, colors):
    total = float(sum(v for v in values if v is not None))
    rows  = []
    for i, (lab, val) in enumerate(zip(labels, values)):
        v   = float(val) if val is not None else 0.0
        pct = (v / total * 100.0) if total > 0 else 0.0
        c   = colors[i % len(colors)]
        pct_bg = c  # use swatch color for percent badge
        rows.append(f"""
        <div class="donut-item">
          <div class="donut-left">
            <span class="swatch" style="background:{c}"></span>
            <span class="donut-label">{lab}</span>
          </div>
          <div class="donut-right">
            <span class="donut-val">{int(v):,}</span>
            <span class="donut-pct" style="background:{pct_bg}">{pct:.1f}%</span>
          </div>
        </div>""")
    return f"<div class='donut-legend'>{''.join(rows)}</div>"

# ══════════════════════════════════════════════
# KPI 카드
# ══════════════════════════════════════════════
def kpi_card(label, value, delta_curr=None, delta_yoy=None,
             reverse=False, unit="", accent="default", delta_unit="%"):
    accent_map = {
        "green":   " green",
        "orange":  " orange",
        "red":     " red",
        "blue":    " blue",
        "default": ""
    }
    ac = accent_map.get(accent, "")

    def badge(val, rev):
        if val is None: return ""
        sign = "▲" if val > 0 else ("▼" if val < 0 else "—")
        d    = "up" if val > 0 else ("down" if val < 0 else "neu")
        rc   = " rev" if rev else ""
        return (f'<span class="kpi-delta {d}{rc}">'
                f'{sign} {abs(val):.1f}{delta_unit}</span>')

    dh = ""
    if delta_curr is not None: dh += badge(delta_curr, reverse)
    if delta_yoy  is not None:
        dh += '<span style="font-size:10px;color:#94a3b8;margin:0 3px;font-weight:800;">YoY</span>'
        dh += badge(delta_yoy, reverse)

    return f"""<div class="kpi-card{ac}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}<span class="kpi-unit">{unit}</span></div>
        <div class="kpi-delta-row">{dh}</div>
    </div>"""

# ══════════════════════════════════════════════
# 차트 공통
# ══════════════════════════════════════════════
def base_layout(h=320, title="", legend_side=False):
    lg = (
        dict(orientation="v", yanchor="middle", y=0.5,
             xanchor="left", x=1.02, font=dict(size=11))
        if legend_side else
        dict(orientation="h", yanchor="bottom", y=1.02,
             xanchor="right", x=1, font=dict(size=11))
    )
    return dict(
        height=h,
        title=dict(text=title, font=dict(size=13, color="#0f172a", family="Inter"), x=0),
        margin=dict(l=10, r=10, t=44 if title else 14, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", size=11, color="#64748b"),
        legend=lg,
        xaxis=dict(showgrid=False, zeroline=False,
                   tickfont=dict(size=10), automargin=True),
        yaxis=dict(showgrid=True, gridcolor="#eef2f7", zeroline=False,
                   tickfont=dict(size=10), automargin=True),
    )

def trend_chart(series_dict, unit, y_label="건수", h=320, title=""):
    pc  = get_period_col(unit)
    fig = go.Figure()
    for i, (name, s) in enumerate(series_dict.items()):
        if s is None or s.empty or pc not in s.columns or y_label not in s.columns:
            continue
        c = PALETTE[i % len(PALETTE)]
        fig.add_trace(go.Scatter(
            x=s[pc], y=s[y_label],
            mode="lines+markers", name=name,
            line=dict(color=c, width=2.5),
            marker=dict(size=6, color=c, line=dict(color="#fff",width=1.5)),
            fill="tozeroy", fillcolor=hex_rgba(c, 0.07),
            hovertemplate="%{x}<br>%{y:,}<extra></extra>"
        ))
    fig.update_layout(**base_layout(h, title))
    return fig

def donut_chart(labels, values, colors=None, h=250, title=""):
    if not colors: colors = PALETTE
    total = sum(v for v in values if v) if values else 0
    fig   = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.70,
        marker=dict(colors=colors[:len(labels)],
                    line=dict(color="#fff", width=3)),
        textinfo="none",
        hovertemplate="%{label}: %{value:,}건 (%{percent})<extra></extra>",
    ))
    lo = base_layout(h, title, legend_side=False)
    lo["showlegend"] = False
    lo["annotations"] = [dict(
        text=f"<span style='font-size:10px;color:#94a3b8;font-weight:800'>TOTAL</span><br>"
             f"<b style='font-size:18px;color:#0f172a'>{total:,}</b>",
        x=0.5, y=0.5, showarrow=False, align="center",
        font=dict(size=14, color="#0f172a", family="Inter")
    )]
    fig.update_layout(**lo)
    return fig

def heatmap_chart(df_pivot, h=320, title=""):
    fig = go.Figure(go.Heatmap(
        z=df_pivot.values,
        x=df_pivot.columns.astype(str),
        y=df_pivot.index.astype(str),
        colorscale=[[0,"#f8fafc"],[0.4,"#a5b4fc"],[1,"#3730a3"]],
        showscale=True,
        hovertemplate="시간대: %{x}시<br>날짜: %{y}<br>건수: %{z}<extra></extra>",
    ))
    fig.update_layout(**base_layout(h, title))
    return fig

def line_chart_simple(df, x, y, color, h=290, y_suffix=""):
    fig = go.Figure(go.Scatter(
        x=df[x], y=df[y],
        mode="lines+markers",
        line=dict(color=color, width=2.6),
        marker=dict(size=6, color=color, line=dict(color="#fff",width=1.5)),
        fill="tozeroy", fillcolor=hex_rgba(color, 0.07),
        hovertemplate=f"%{{x}}<br>%{{y:,.1f}}{y_suffix}<extra></extra>"
    ))
    lo = base_layout(h, "")
    if y_suffix:
        lo["yaxis"]["ticksuffix"] = y_suffix
    fig.update_layout(**lo)
    return fig

# ══════════════════════════════════════════════
# 데이터 로드
# ══════════════════════════════════════════════
@st.cache_data(ttl=300, show_spinner=False)
def load_agent():
    try:
        df = pd.read_csv(gsheet_url(GID_MAP["agent"]))
        df.columns = df.columns.str.strip()
        df["입사일"] = pd.to_datetime(df["입사일"], errors="coerce")
        return df
    except:
        return pd.DataFrame(columns=["상담사명","팀명","입사일"])

@st.cache_data(ttl=300, show_spinner=False)
def load_phone():
    try:
        df = pd.read_csv(gsheet_url(GID_MAP["phone"]))
        df.columns = df.columns.str.strip()

        df["일자"] = pd.to_datetime(df["일자"], errors="coerce")
        df["인입시각"] = pd.to_datetime(
            df["일자"].astype(str) + " " + df["인입시각"].astype(str),
            errors="coerce"
        )

        # ✅ 모든 시간 컬럼 강제 파싱 (H:MM:SS → 초)
        for col in df.columns:
            if "(초)" in col:
                df[col] = df[col].apply(parse_duration_seconds).astype(float)

        # ✅ 혹시 컬럼명이 다를 경우 대비 - 있는 컬럼만 파싱
        time_cols = ["대기시간(초)", "통화시간(초)", "ACW시간(초)"]
        for col in time_cols:
            if col in df.columns:
                df[col] = df[col].apply(parse_duration_seconds).astype(float)
            else:
                df[col] = 0.0

        # ✅ AHT = ATT + ACW
        df["AHT(초)"] = df["통화시간(초)"] + df["ACW시간(초)"]

        df["응대여부"] = df["상담사명"].apply(
            lambda x: "미응대" if str(x).strip() == "미응대" else "응대"
        )
        df["인입시간대"] = df["인입시각"].dt.hour
        return assign_period_cols(df, "일자")

    except Exception as e:
        st.error(f"전화 데이터 로드 오류: {e}")
        return pd.DataFrame(columns=[
            "일자","사업자명","브랜드","상담사명","인입시각",
            "대기시간(초)","통화시간(초)","ACW시간(초)","대분류","중분류","소분류",
            "AHT(초)","응대여부","인입시간대","주차","월"
        ])

@st.cache_data(ttl=300, show_spinner=False)
def load_chat():
    try:
        df = pd.read_csv(gsheet_url(GID_MAP["chat"]))
        df.columns = df.columns.str.strip()
        df["일자"]          = pd.to_datetime(df["일자"],          errors="coerce")
        df["접수일시"]      = pd.to_datetime(df["접수일시"],      errors="coerce")
        df["첫멘트발송일시"] = pd.to_datetime(df["첫멘트발송일시"], errors="coerce")
        df["종료일시"]      = pd.to_datetime(df["종료일시"],      errors="coerce")
        # 응답시간 = 접수 → 첫멘트 (핵심 대기시간)
        df["응답시간(초)"]  = (
            (df["첫멘트발송일시"] - df["접수일시"]).dt.total_seconds().clip(lower=0)
        )
        df["리드타임(초)"]  = (
            (df["종료일시"] - df["접수일시"]).dt.total_seconds().clip(lower=0)
        )
        포기 = (
            df["배분전포기여부"].astype(str).str.strip().str.upper()
            if "배분전포기여부" in df.columns
            else pd.Series(["N"] * len(df))
        )
        df["응대여부"] = df.apply(
            lambda r: "미응대"
            if pd.isna(r["첫멘트발송일시"]) or 포기.iloc[r.name] == "Y"
            else "응대",
            axis=1
        )
        df["인입시간대"] = df["접수일시"].dt.hour
        return assign_period_cols(df, "일자")
    except:
        return pd.DataFrame(columns=[
            "일자","사업자명","브랜드","플랫폼","상담사명",
            "접수일시","첫멘트발송일시","종료일시","배분전포기여부",
            "대분류","중분류","소분류",
            "응답시간(초)","리드타임(초)","응대여부","인입시간대","주차","월"
        ])

@st.cache_data(ttl=300, show_spinner=False)
def load_board():
    try:
        df = pd.read_csv(gsheet_url(GID_MAP["board"]))
        df.columns = df.columns.str.strip()
        df["일자"]     = pd.to_datetime(df["일자"],     errors="coerce")
        df["접수일시"] = pd.to_datetime(df["접수일시"], errors="coerce")
        df["응답일시"] = pd.to_datetime(df["응답일시"], errors="coerce")
        df["리드타임(초)"] = (
            (df["응답일시"] - df["접수일시"]).dt.total_seconds().clip(lower=0)
        )
        df["응대여부"]   = df["응답일시"].apply(lambda x: "미응대" if pd.isna(x) else "응대")
        df["인입시간대"] = df["접수일시"].dt.hour
        # ★ 근무내/근무외 분리
        df = add_board_split_cols(df)
        return assign_period_cols(df, "일자")
    except:
        return pd.DataFrame(columns=[
            "일자","사업자명","브랜드","플랫폼","상담사명",
            "접수일시","응답일시","대분류","중분류","소분류",
            "리드타임(초)","근무내리드타임(초)","근무외리드타임(초)",
            "응대여부","인입시간대","주차","월"
        ])

def merge_agent(df, agent_df, base_d):
    if agent_df.empty or "상담사명" not in df.columns:
        df = df.copy()
        df["팀명"] = "미지정"
        df["근속그룹"] = "미입력"
        return df
    merged = df.merge(
        agent_df[["상담사명","팀명","입사일"]],
        on="상담사명", how="left"
    )
    merged["팀명"]    = merged["팀명"].fillna("미지정")
    merged["근속그룹"] = merged["입사일"].apply(lambda x: get_tenure_group(x, base_d))
    return merged

def filter_df(df, start, end, brands=None, operators=None):
    if df.empty or "일자" not in df.columns: return df
    mask = (
        (df["일자"] >= pd.Timestamp(start)) &
        (df["일자"] <= pd.Timestamp(end))
    )
    df = df[mask].copy()
    if brands    and "브랜드"   in df.columns: df = df[df["브랜드"].isin(brands)]
    if operators and "사업자명" in df.columns: df = df[df["사업자명"].isin(operators)]
    return df

# ══════════════════════════════════════════════
# 일별 추이 집계
# ══════════════════════════════════════════════
def daily_trend_phone(phone_df):
    if phone_df.empty:
        return pd.DataFrame(columns=["일자","인입","응대","응대율","평균AHT","평균ATT","평균ACW","평균대기"])
    df   = phone_df.copy()
    df["일자"] = pd.to_datetime(df["일자"], errors="coerce").dt.date
    resp = df[df["응대여부"] == "응대"].copy()

    g_all  = df.groupby("일자").size().rename("인입")
    g_resp = resp.groupby("일자").size().rename("응대") if not resp.empty else pd.Series(dtype=int, name="응대")
    g_aht  = resp.groupby("일자")["AHT(초)"].mean().rename("평균AHT")           if not resp.empty else pd.Series(dtype=float, name="평균AHT")
    g_att  = resp.groupby("일자")["통화시간(초)"].mean().rename("평균ATT")       if not resp.empty else pd.Series(dtype=float, name="평균ATT")
    g_acw  = resp.groupby("일자")["ACW시간(초)"].mean().rename("평균ACW")        if not resp.empty else pd.Series(dtype=float, name="평균ACW")
    g_wait = resp.groupby("일자")["대기시간(초)"].mean().rename("평균대기")      if not resp.empty else pd.Series(dtype=float, name="평균대기")

    out = pd.concat([g_all, g_resp, g_aht, g_att, g_acw, g_wait], axis=1).fillna(0.0).reset_index()
    out["응대율"] = np.where(out["인입"] > 0, out["응대"] / out["인입"] * 100.0, 0.0)
    out["일자"]   = pd.to_datetime(out["일자"])
    return out.sort_values("일자")

def daily_trend_chat(chat_df):
    if chat_df.empty:
        return pd.DataFrame(columns=["일자","인입","응대","응대율","평균대기","평균리드타임"])
    df   = chat_df.copy()
    df["일자"] = pd.to_datetime(df["일자"], errors="coerce").dt.date
    resp = df[df["응대여부"] == "응대"].copy()

    g_all  = df.groupby("일자").size().rename("인입")
    g_resp = resp.groupby("일자").size().rename("응대")             if not resp.empty else pd.Series(dtype=int,   name="응대")
    g_wait = resp.groupby("일자")["응답시간(초)"].mean().rename("평균대기")       if not resp.empty else pd.Series(dtype=float, name="평균대기")
    g_lt   = resp.groupby("일자")["리드타임(초)"].mean().rename("평균리드타임")   if not resp.empty else pd.Series(dtype=float, name="평균리드타임")

    out = pd.concat([g_all, g_resp, g_wait, g_lt], axis=1).fillna(0.0).reset_index()
    out["응대율"] = np.where(out["인입"] > 0, out["응대"] / out["인입"] * 100.0, 0.0)
    out["일자"]   = pd.to_datetime(out["일자"])
    return out.sort_values("일자")

def daily_trend_board(board_df):
    if board_df.empty:
        return pd.DataFrame(columns=["일자","접수","응답","응답률","평균근무내LT","평균근무외LT","평균전체LT"])
    df   = board_df.copy()
    df["일자"] = pd.to_datetime(df["일자"], errors="coerce").dt.date
    resp = df[df["응대여부"] == "응대"].copy()

    g_all  = df.groupby("일자").size().rename("접수")
    g_resp = resp.groupby("일자").size().rename("응답")                                  if not resp.empty else pd.Series(dtype=int,   name="응답")
    g_in   = resp.groupby("일자")["근무내리드타임(초)"].mean().rename("평균근무내LT")   if not resp.empty else pd.Series(dtype=float, name="평균근무내LT")
    g_off  = resp.groupby("일자")["근무외리드타임(초)"].mean().rename("평균근무외LT")   if not resp.empty else pd.Series(dtype=float, name="평균근무외LT")
    g_tot  = resp.groupby("일자")["리드타임(초)"].mean().rename("평균전체LT")            if not resp.empty else pd.Series(dtype=float, name="평균전체LT")

    out = pd.concat([g_all, g_resp, g_in, g_off, g_tot], axis=1).fillna(0.0).reset_index()
    out["응답률"] = np.where(out["접수"] > 0, out["응답"] / out["접수"] * 100.0, 0.0)
    out["일자"]   = pd.to_datetime(out["일자"])
    return out.sort_values("일자")

# ══════════════════════════════════════════════
# 일별 추이 렌더 블록
# ══════════════════════════════════════════════
def render_daily_trends_block(kind, df_daily):
    if df_daily.empty:
        st.info("선택한 기간에 대한 일별 추이 데이터가 없습니다.")
        return

    section_title("일별 추이 (선택 기간)")

    if kind == "phone":
        c1, c2, c3 = st.columns(3)
        with c1:
            card_open("일별 인입", "Inbound calls")
            fig = line_chart_simple(df_daily, "일자", "인입", COLORS["phone"])
            st.plotly_chart(fig, use_container_width=True)
            card_close()
        with c2:
            card_open("일별 응대율", "Answer rate %")
            fig = line_chart_simple(df_daily, "일자", "응대율", COLORS["success"], y_suffix="%")
            st.plotly_chart(fig, use_container_width=True)
            card_close()
        with c3:
            card_open("일별 평균 AHT", "Avg handle time")
            tmp = df_daily.copy()
            tmp["label"] = tmp["평균AHT"].apply(fmt_hms)
            fig = go.Figure(go.Scatter(
                x=tmp["일자"], y=tmp["평균AHT"],
                mode="lines+markers",
                line=dict(color=COLORS["warning"], width=2.6),
                marker=dict(size=6, color=COLORS["warning"], line=dict(color="#fff",width=1.5)),
                fill="tozeroy", fillcolor=hex_rgba(COLORS["warning"], 0.07),
                text=tmp["label"],
                hovertemplate="%{x}<br>AHT: %{text}<extra></extra>"
            ))
            fig.update_layout(**base_layout(290, ""))
            st.plotly_chart(fig, use_container_width=True)
            card_close()

    elif kind == "chat":
        c1, c2, c3 = st.columns(3)
        with c1:
            card_open("일별 인입", "Inbound chats")
            st.plotly_chart(
                line_chart_simple(df_daily, "일자", "인입", COLORS["chat"]),
                use_container_width=True
            )
            card_close()
        with c2:
            card_open("일별 응대율", "Answer rate %")
            st.plotly_chart(
                line_chart_simple(df_daily, "일자", "응대율", COLORS["success"], y_suffix="%"),
                use_container_width=True
            )
            card_close()
        with c3:
            card_open("일별 평균 대기시간", "Avg wait (접수→첫멘트)")
            tmp = df_daily.copy()
            tmp["label"] = tmp["평균대기"].apply(fmt_hms)
            fig = go.Figure(go.Scatter(
                x=tmp["일자"], y=tmp["평균대기"],
                mode="lines+markers",
                line=dict(color=COLORS["info"], width=2.6),
                marker=dict(size=6, color=COLORS["info"], line=dict(color="#fff",width=1.5)),
                fill="tozeroy", fillcolor=hex_rgba(COLORS["info"], 0.07),
                text=tmp["label"],
                hovertemplate="%{x}<br>대기: %{text}<extra></extra>"
            ))
            fig.update_layout(**base_layout(290, ""))
            st.plotly_chart(fig, use_container_width=True)
            card_close()

        # 리드타임 추가 행
        _, c_mid, _ = st.columns([1, 2, 1])
        with c_mid:
            card_open("일별 평균 리드타임", "Avg lead time (접수→종료)")
            tmp = df_daily.copy()
            tmp["label"] = tmp["평균리드타임"].apply(fmt_hms)
            fig = go.Figure(go.Scatter(
                x=tmp["일자"], y=tmp["평균리드타임"],
                mode="lines+markers",
                line=dict(color=COLORS["warning"], width=2.6),
                marker=dict(size=6, color=COLORS["warning"], line=dict(color="#fff",width=1.5)),
                fill="tozeroy", fillcolor=hex_rgba(COLORS["warning"], 0.07),
                text=tmp["label"],
                hovertemplate="%{x}<br>리드타임: %{text}<extra></extra>"
            ))
            fig.update_layout(**base_layout(300, ""))
            st.plotly_chart(fig, use_container_width=True)
            card_close()

    elif kind == "board":
        c1, c2, c3 = st.columns(3)
        with c1:
            card_open("일별 접수", "Inbound tickets")
            st.plotly_chart(
                line_chart_simple(df_daily, "일자", "접수", COLORS["board"]),
                use_container_width=True
            )
            card_close()
        with c2:
            card_open("일별 응답률", "Answer rate %")
            st.plotly_chart(
                line_chart_simple(df_daily, "일자", "응답률", COLORS["success"], y_suffix="%"),
                use_container_width=True
            )
            card_close()
        with c3:
            card_open("근무내/외 리드타임 추이", "In-hours vs Off-hours")
            tmp = df_daily.copy()
            tmp["in_label"]  = tmp["평균근무내LT"].apply(fmt_hms)
            tmp["off_label"] = tmp["평균근무외LT"].apply(fmt_hms)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=tmp["일자"], y=tmp["평균근무내LT"],
                mode="lines+markers", name="근무내",
                line=dict(color=COLORS["success"], width=2.6),
                marker=dict(size=6, color=COLORS["success"], line=dict(color="#fff",width=1.5)),
                text=tmp["in_label"],
                hovertemplate="%{x}<br>근무내: %{text}<extra></extra>"
            ))
            fig.add_trace(go.Scatter(
                x=tmp["일자"], y=tmp["평균근무외LT"],
                mode="lines+markers", name="근무외",
                line=dict(color=COLORS["danger"], width=2.6),
                marker=dict(size=6, color=COLORS["danger"], line=dict(color="#fff",width=1.5)),
                text=tmp["off_label"],
                hovertemplate="%{x}<br>근무외: %{text}<extra></extra>"
            ))
            fig.update_layout(**base_layout(290, ""))
            st.plotly_chart(fig, use_container_width=True)
            card_close()

# ══════════════════════════════════════════════
# 전체 현황
# ══════════════════════════════════════════════
def page_overview(phone, chat, board, unit, month_range, start, end,
                  phone_all=None, chat_all=None, board_all=None):
    updated = datetime.now().strftime("%Y-%m-%d %H:%M")
    s_str = start.strftime("%Y.%m.%d") if hasattr(start,"strftime") else str(start)
    e_str = end.strftime("%Y.%m.%d")   if hasattr(end,  "strftime") else str(end)

    st.markdown(f"""
    <div class="dash-header">
      <div class="dash-header-left">
        <h1>📊 Contact Center Dashboard</h1>
        <span>Updated {updated}</span>
      </div>
      <div><span class="dash-badge">{s_str} ~ {e_str}</span></div>
    </div>""", unsafe_allow_html=True)

    # ── 현재 기간 집계
    t_ph  = len(phone)
    t_ch  = len(chat)
    t_bo  = len(board)
    t_all = t_ph + t_ch + t_bo

    r_ph = len(phone[phone["응대여부"]=="응대"]) if not phone.empty else 0
    r_ch = len(chat[chat["응대여부"]=="응대"])   if not chat.empty  else 0
    r_bo = len(board[board["응대여부"]=="응대"]) if not board.empty else 0
    rr_ph = r_ph / t_ph * 100 if t_ph else 0
    rr_ch = r_ch / t_ch * 100 if t_ch else 0
    rr_bo = r_bo / t_bo * 100 if t_bo else 0

    # ── 이전 동일 기간 집계
    ph_prev = get_prev_period(phone_all, start, end) if phone_all is not None else pd.DataFrame()
    ch_prev = get_prev_period(chat_all,  start, end) if chat_all  is not None else pd.DataFrame()
    bo_prev = get_prev_period(board_all, start, end) if board_all is not None else pd.DataFrame()

    t_ph_prev  = len(ph_prev)
    t_ch_prev  = len(ch_prev)
    t_bo_prev  = len(bo_prev)
    t_all_prev = t_ph_prev + t_ch_prev + t_bo_prev

    rph_prev  = len(ph_prev[ph_prev["응대여부"]=="응대"]) if not ph_prev.empty else 0
    rch_prev  = len(ch_prev[ch_prev["응대여부"]=="응대"]) if not ch_prev.empty else 0
    rbo_prev  = len(bo_prev[bo_prev["응대여부"]=="응대"]) if not bo_prev.empty else 0
    rrph_prev = rph_prev / t_ph_prev * 100 if t_ph_prev else 0
    rrch_prev = rch_prev / t_ch_prev * 100 if t_ch_prev else 0
    rrbo_prev = rbo_prev / t_bo_prev * 100 if t_bo_prev else 0

    # ── KPI row (인입건수 - % 증감)
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.markdown(kpi_card("전체 인입",   fmt_num(t_all),
                         delta_curr=calc_delta(t_all, t_all_prev),
                         unit="건"), unsafe_allow_html=True)
    with c2: st.markdown(kpi_card("전화 인입",   fmt_num(t_ph),
                         delta_curr=calc_delta(t_ph, t_ph_prev),
                         unit="건", accent="blue"), unsafe_allow_html=True)
    with c3: st.markdown(kpi_card("채팅 인입",   fmt_num(t_ch),
                         delta_curr=calc_delta(t_ch, t_ch_prev),
                         unit="건", accent="green"), unsafe_allow_html=True)
    with c4: st.markdown(kpi_card("게시판 인입", fmt_num(t_bo),
                         delta_curr=calc_delta(t_bo, t_bo_prev),
                         unit="건", accent="orange"), unsafe_allow_html=True)

    # ── 응대율 (응대율 - %p 차이)
    section_title("채널별 응대율")
    c1,c2,c3 = st.columns(3)
    with c1: st.markdown(kpi_card("전화 응대율",   fmt_pct(rr_ph),
                         delta_curr=calc_delta_pp(rr_ph, rrph_prev),
                         accent="blue",   delta_unit="%p"), unsafe_allow_html=True)
    with c2: st.markdown(kpi_card("채팅 응대율",   fmt_pct(rr_ch),
                         delta_curr=calc_delta_pp(rr_ch, rrch_prev),
                         accent="green",  delta_unit="%p"), unsafe_allow_html=True)
    with c3: st.markdown(kpi_card("게시판 응답률", fmt_pct(rr_bo),
                         delta_curr=calc_delta_pp(rr_bo, rrbo_prev),
                         accent="orange", delta_unit="%p"), unsafe_allow_html=True)

    # ── 채널 분포 & 추이 (기존 유지)
    section_title("채널별 인입 분포 & 추이")
    c_donut, c_trend = st.columns([1,2])
    with c_donut:
        card_open("채널 분포","Channel distribution")
        fig = donut_chart(["전화","채팅","게시판"],[t_ph,t_ch,t_bo],
                          [COLORS["phone"],COLORS["chat"],COLORS["board"]],h=240)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(donut_legend_html(
            ["전화","채팅","게시판"],[t_ph,t_ch,t_bo],
            [COLORS["phone"],COLORS["chat"],COLORS["board"]]),
            unsafe_allow_html=True)
        card_close()
    with c_trend:
        card_open("채널별 인입 추이", f"기간 단위: {unit}")
        pc = get_period_col(unit)
        cr_s,_ = get_chart_range(unit, end, month_range)
        def agg(df):
            if df.empty or pc not in df.columns:
                return pd.DataFrame(columns=[pc,"건수"])
            return (df[df[pc] >= pd.Timestamp(cr_s)]
                    .groupby(pc).size().reset_index(name="건수"))
        fig = trend_chart(
            {"전화":agg(phone),"채팅":agg(chat),"게시판":agg(board)},
            unit=unit, y_label="건수", h=320)
        st.plotly_chart(fig, use_container_width=True)
        card_close()

    # ── 응대율 추이
    section_title("응대율 추이 비교")
    pc = get_period_col(unit)
    cr_s,_ = get_chart_range(unit, end, month_range)

    def rr_trend(df):
        if df.empty or pc not in df.columns:
            return pd.DataFrame(columns=[pc,"응대율"])
        return (df[df[pc] >= pd.Timestamp(cr_s)]
                .groupby(pc)
                .apply(lambda x: pd.Series({
                    "응대율": (x["응대여부"]=="응대").sum() / len(x) * 100.0
                }))
                .reset_index())

    card_open("채널별 응대율 추이", f"기간 단위: {unit}")
    fig2 = go.Figure()
    for nm, rr_df, c in [
        ("전화 응대율",   rr_trend(phone), COLORS["phone"]),
        ("채팅 응대율",   rr_trend(chat),  COLORS["chat"]),
        ("게시판 응답률", rr_trend(board), COLORS["board"]),
    ]:
        if not rr_df.empty and pc in rr_df.columns:
            fig2.add_trace(go.Scatter(
                x=rr_df[pc], y=rr_df["응대율"],
                mode="lines+markers", name=nm,
                line=dict(color=c, width=2.5),
                marker=dict(size=6, color=c),
                hovertemplate="%{x}<br>%{y:.1f}%<extra></extra>"
            ))
    lo = base_layout(280,"")
    lo["yaxis"]["ticksuffix"] = "%"
    lo["yaxis"]["range"] = [0,110]
    fig2.update_layout(**lo)
    st.plotly_chart(fig2, use_container_width=True)
    card_close()

    # 응대율 비교 추이
    section_title("응대율 추이 비교")
    pc = get_period_col(unit)
    cr_s, _ = get_chart_range(unit, end, month_range)

    def rr_trend(df):
        if df.empty or pc not in df.columns:
            return pd.DataFrame(columns=[pc,"응대율"])
        g = df[df[pc] >= pd.Timestamp(cr_s)].groupby(pc).apply(
            lambda x: pd.Series({
                "응대율": (x["응대여부"]=="응대").sum() / len(x) * 100.0
            })
        ).reset_index()
        return g

    card_open("채널별 응대율 추이", "기간 단위: " + unit)
    rr_ph = rr_trend(phone)
    rr_ch = rr_trend(chat)
    rr_bo = rr_trend(board)
    fig2  = go.Figure()
    for nm, rr_df, c in [
        ("전화 응대율",  rr_ph, COLORS["phone"]),
        ("채팅 응대율",  rr_ch, COLORS["chat"]),
        ("게시판 응답률",rr_bo, COLORS["board"]),
    ]:
        if rr_df is not None and not rr_df.empty and pc in rr_df.columns:
            fig2.add_trace(go.Scatter(
                x=rr_df[pc], y=rr_df["응대율"],
                mode="lines+markers", name=nm,
                line=dict(color=c, width=2.5),
                marker=dict(size=6, color=c, line=dict(color="#fff",width=1.5)),
                hovertemplate="%{x}<br>%{y:.1f}%<extra></extra>"
            ))
    lo = base_layout(280, "")
    lo["yaxis"]["ticksuffix"] = "%"
    lo["yaxis"]["range"] = [0, 110]
    fig2.update_layout(**lo)
    st.plotly_chart(fig2, use_container_width=True)
    card_close()

# ══════════════════════════════════════════════
# VOC 인입 분석
# ══════════════════════════════════════════════
def page_voc(phone, chat, board, unit, month_range, start, end):
    section_title("VOC 인입 분석")
    frames = []
    for df, ch in [(phone,"전화"),(chat,"채팅"),(board,"게시판")]:
        if df.empty: continue
        tmp = df.copy(); tmp["채널"] = ch
        frames.append(tmp)
    if not frames:
        st.info("데이터가 없습니다."); return
    all_df = pd.concat(frames, ignore_index=True)

    # 필터 UI
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    with col_f1:
        ch_sel = st.multiselect("채널", ["전화","채팅","게시판"],
                                default=["전화","채팅","게시판"], key="voc_ch")
    cats1 = sorted(all_df["대분류"].dropna().unique()) if "대분류" in all_df.columns else []
    with col_f2:
        cat1_sel = st.multiselect("대분류", cats1, default=[], key="voc_cat1")
    mid_pool = (
        all_df[all_df["대분류"].isin(cat1_sel)]["중분류"].dropna().unique()
        if cat1_sel and "중분류" in all_df.columns
        else (all_df["중분류"].dropna().unique() if "중분류" in all_df.columns else [])
    )
    with col_f3:
        cat2_sel = st.multiselect("중분류", sorted(mid_pool), default=[], key="voc_cat2")
    sub_pool = (
        all_df[all_df["중분류"].isin(cat2_sel)]["소분류"].dropna().unique()
        if cat2_sel and "소분류" in all_df.columns
        else (all_df["소분류"].dropna().unique() if "소분류" in all_df.columns else [])
    )
    with col_f4:
        cat3_sel = st.multiselect("소분류", sorted(sub_pool), default=[], key="voc_cat3")

    voc = all_df.copy()
    if ch_sel:    voc = voc[voc["채널"].isin(ch_sel)]
    if cat1_sel and "대분류" in voc.columns: voc = voc[voc["대분류"].isin(cat1_sel)]
    if cat2_sel and "중분류" in voc.columns: voc = voc[voc["중분류"].isin(cat2_sel)]
    if cat3_sel and "소분류" in voc.columns: voc = voc[voc["소분류"].isin(cat3_sel)]

    st.markdown(
        f"<div style='font-size:13px;font-weight:800;color:#6366f1;margin:8px 0 14px;'>"
        f"총 {len(voc):,}건</div>",
        unsafe_allow_html=True
    )

    # 추이 탭 (일/주/월)
    section_title("VOC 인입 추이")
    tab_d, tab_w, tab_m = st.tabs(["📅 일별", "📆 주별", "🗓️ 월별"])

    def voc_trend_fig(vdf, unit_):
        pc = get_period_col(unit_)
        if vdf.empty or pc not in vdf.columns: return None
        g = vdf.groupby([pc,"채널"]).size().reset_index(name="건수")
        pivot = {}
        for ch in (ch_sel or ["전화","채팅","게시판"]):
            s = g[g["채널"]==ch][[pc,"건수"]].sort_values(pc)
            if not s.empty: pivot[ch] = s
        return trend_chart(pivot, unit=unit_, y_label="건수", h=300) if pivot else None

    with tab_d:
        card_open("일별 VOC 인입")
        fig = voc_trend_fig(voc, "일별")
        if fig: st.plotly_chart(fig, use_container_width=True)
        else: st.info("데이터 없음")
        card_close()
    with tab_w:
        card_open("주별 VOC 인입")
        fig = voc_trend_fig(voc, "주별")
        if fig: st.plotly_chart(fig, use_container_width=True)
        else: st.info("데이터 없음")
        card_close()
    with tab_m:
        card_open("월별 VOC 인입")
        fig = voc_trend_fig(voc, "월별")
        if fig: st.plotly_chart(fig, use_container_width=True)
        else: st.info("데이터 없음")
        card_close()

    # 비중 분석
    section_title("비중 분석")
    cA, cB = st.columns(2)

    with cA:
        if "사업자명" in voc.columns:
            op_df  = voc.groupby("사업자명").size().reset_index(name="건수").sort_values("건수",ascending=False).head(12)
            card_open("사업자 분포", "상위 12")
            st.plotly_chart(donut_chart(op_df["사업자명"].tolist(), op_df["건수"].tolist(), h=230), use_container_width=True)
            st.markdown(donut_legend_html(op_df["사업자명"].tolist(), op_df["건수"].tolist(), PALETTE), unsafe_allow_html=True)
            card_close()
    with cB:
        if "브랜드" in voc.columns:
            br_df = voc.groupby("브랜드").size().reset_index(name="건수").sort_values("건수",ascending=False).head(12)
            card_open("브랜드 분포", "상위 12")
            st.plotly_chart(donut_chart(br_df["브랜드"].tolist(), br_df["건수"].tolist(), h=230), use_container_width=True)
            st.markdown(donut_legend_html(br_df["브랜드"].tolist(), br_df["건수"].tolist(), PALETTE), unsafe_allow_html=True)
            card_close()

    if "대분류" in voc.columns:
        card_open("대분류 × 채널", "Stacked bar")
        cat1_df = voc.groupby(["채널","대분류"]).size().reset_index(name="건수")
        fig = px.bar(cat1_df, x="대분류", y="건수", color="채널", barmode="stack",
                     color_discrete_map={"전화":COLORS["phone"],"채팅":COLORS["chat"],"게시판":COLORS["board"]})
        fig.update_layout(**base_layout(300,""))
        st.plotly_chart(fig, use_container_width=True)
        card_close()

    c1, c2 = st.columns(2)
    with c1:
        if "중분류" in voc.columns:
            card_open("중분류 TOP 20")
            mid_df = voc.groupby("중분류").size().reset_index(name="건수").sort_values("건수",ascending=False).head(20)
            fig = px.bar(mid_df, x="건수", y="중분류", orientation="h",
                         color_discrete_sequence=[COLORS["warning"]])
            fig.update_layout(**base_layout(400,""))
            st.plotly_chart(fig, use_container_width=True)
            card_close()
    with c2:
        if "소분류" in voc.columns:
            card_open("소분류 TOP 20")
            sub_df = voc.groupby("소분류").size().reset_index(name="건수").sort_values("건수",ascending=False).head(20)
            fig = px.bar(sub_df, x="건수", y="소분류", orientation="h",
                         color_discrete_sequence=[COLORS["success"]])
            fig.update_layout(**base_layout(400,""))
            st.plotly_chart(fig, use_container_width=True)
            card_close()

# ══════════════════════════════════════════════
# 사업자 현황
# ══════════════════════════════════════════════
def page_operator(phone, chat, board, unit, month_range):
    section_title("사업자별 인입 현황")

    def op_s(df, ch):
        if df.empty or "사업자명" not in df.columns: return pd.DataFrame()
        g = df.groupby("사업자명").agg(
            인입=("사업자명","count"),
            응대=("응대여부", lambda x: (x=="응대").sum())
        ).reset_index()
        g["응대율"] = (g["응대"] / g["인입"] * 100).round(1)
        g["채널"]   = ch
        return g

    all_op = pd.concat([op_s(phone,"전화"), op_s(chat,"채팅"), op_s(board,"게시판")])
    if all_op.empty:
        st.info("사업자명 데이터 없음."); return

    card_open("사업자별 채널 인입", "Stacked bar")
    fig = px.bar(all_op, x="사업자명", y="인입", color="채널", barmode="stack",
                 color_discrete_map={"전화":COLORS["phone"],"채팅":COLORS["chat"],"게시판":COLORS["board"]})
    fig.update_layout(**base_layout(360,""))
    st.plotly_chart(fig, use_container_width=True)
    card_close()

    card_open("사업자별 채널 응대율", "응대율 비교")
    fig2 = px.bar(all_op, x="사업자명", y="응대율", color="채널", barmode="group",
                  color_discrete_map={"전화":COLORS["phone"],"채팅":COLORS["chat"],"게시판":COLORS["board"]})
    lo = base_layout(320,"")
    lo["yaxis"]["ticksuffix"] = "%"
    fig2.update_layout(**lo)
    st.plotly_chart(fig2, use_container_width=True)
    card_close()

    card_open("사업자별 요약 테이블")
    try:
        pivot = all_op.pivot_table(index="사업자명", columns="채널",
                                   values=["인입","응대율"], aggfunc="first")
        st.dataframe(pivot, use_container_width=True)
    except:
        st.dataframe(all_op, use_container_width=True)
    card_close()

# ══════════════════════════════════════════════
# 전화 현황
# ══════════════════════════════════════════════
def page_phone(phone, unit, month_range, start, end):
    if phone.empty:
        st.info("전화 데이터가 없습니다."); return

    resp = phone[phone["응대여부"]=="응대"]
    total = len(phone)
    rc    = len(resp)
    rr    = rc / total * 100 if total else 0

    # ✅ 숫자형 강제 변환 후 mean() (이중 안전장치)
    def safe_mean(series):
        try:
            return pd.to_numeric(series, errors="coerce").mean() or 0.0
        except:
            return 0.0

    aw  = safe_mean(resp["대기시간(초)"])  if not resp.empty else 0
    att = safe_mean(resp["통화시간(초)"])  if not resp.empty else 0
    acw = safe_mean(resp["ACW시간(초)"])   if not resp.empty else 0
    aht = att + acw                                  # AHT = ATT+ACW (직접 계산)

    # KPI
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    with c1: st.markdown(kpi_card("전체 인입",  fmt_num(total), unit="건"),           unsafe_allow_html=True)
    with c2: st.markdown(kpi_card("응대건수",   fmt_num(rc),    unit="건", accent="green"),  unsafe_allow_html=True)
    with c3: st.markdown(kpi_card("응대율",     fmt_pct(rr),    accent="blue"),        unsafe_allow_html=True)
    with c4: st.markdown(kpi_card("평균 ATT",   fmt_hms(att),   accent="blue"),        unsafe_allow_html=True)
    with c5: st.markdown(kpi_card("평균 ACW",   fmt_hms(acw),   accent="orange"),      unsafe_allow_html=True)
    with c6: st.markdown(kpi_card("평균 AHT",   fmt_hms(aht),   accent="green"),       unsafe_allow_html=True)

    # ★ 일별 추이 (KPI 바로 아래)
    render_daily_trends_block("phone", daily_trend_phone(phone))

    # 기간별 추이
    section_title("기간 단위 추이")
    pc = get_period_col(unit)
    cr_s, _ = get_chart_range(unit, end, month_range)
    ph_in = phone[phone[pc] >= pd.Timestamp(cr_s)].groupby(pc).size().reset_index(name="건수")
    ph_re = (resp[resp[pc] >= pd.Timestamp(cr_s)].groupby(pc).size().reset_index(name="건수")
             if not resp.empty else pd.DataFrame(columns=[pc,"건수"]))

    c1, c2 = st.columns([2,1])
    with c1:
        card_open("인입 / 응대 추이", f"기간 단위: {unit}")
        st.plotly_chart(
            trend_chart({"전화 인입":ph_in,"응대":ph_re}, unit=unit, y_label="건수", h=300),
            use_container_width=True
        )
        card_close()
    with c2:
        card_open("응대 현황", "Donut")
        fig = donut_chart(["응대","미응대"],[rc, total-rc],
                          [COLORS["success"],COLORS["danger"]], h=260)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(
            donut_legend_html(["응대","미응대"],[rc,total-rc],
                              [COLORS["success"],COLORS["danger"]]),
            unsafe_allow_html=True
        )
        card_close()

    # 시간대별
    section_title("시간대별 인입 / 응대 현황")
    hourly = phone.groupby("인입시간대").agg(
        인입=("인입시간대","count"),
        응대=("응대여부", lambda x: (x=="응대").sum()),
    ).reset_index()
    hourly["미응대"] = hourly["인입"] - hourly["응대"]
    hourly["응대율"] = (hourly["응대"] / hourly["인입"] * 100).round(1)

    card_open("시간대별 인입/응대 + 응대율")
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(x=hourly["인입시간대"], y=hourly["응대"],   name="응대",   marker_color=COLORS["phone"]))
    fig3.add_trace(go.Bar(x=hourly["인입시간대"], y=hourly["미응대"], name="미응대", marker_color=hex_rgba(COLORS["danger"],0.7)))
    fig3.add_trace(go.Scatter(
        x=hourly["인입시간대"], y=hourly["응대율"], name="응대율(%)",
        yaxis="y2", mode="lines+markers",
        line=dict(color=COLORS["warning"],width=2), marker=dict(size=6)
    ))
    fig3.update_layout(
        **base_layout(320,""), barmode="stack",
        yaxis2=dict(overlaying="y", side="right", showgrid=False,
                    ticksuffix="%", range=[0,110])
    )
    st.plotly_chart(fig3, use_container_width=True)
    card_close()

    # AHT 구성
    if not resp.empty:
        section_title("AHT 구성 분석 (ATT + ACW)")
        aht_df = resp.groupby(pc).agg(
            ATT=("통화시간(초)", "mean"),
            ACW=("ACW시간(초)", "mean"),
        ).reset_index()
        aht_df["AHT"] = aht_df["ATT"] + aht_df["ACW"]
        c1, c2 = st.columns([2, 1])
        with c1:
            card_open("기간별 평균 AHT 구성", "ATT(통화) + ACW = AHT")
            fig4 = go.Figure()
            fig4.add_trace(go.Bar(
                x=aht_df[pc], y=aht_df["ATT"],
                name="ATT (통화시간)",
                marker_color=COLORS["primary"],
                hovertemplate="%{x}<br>ATT: %{y:.0f}초<extra></extra>"
            ))
            fig4.add_trace(go.Bar(
                x=aht_df[pc], y=aht_df["ACW"],
                name="ACW (후처리)",
                marker_color=COLORS["warning"],
                hovertemplate="%{x}<br>ACW: %{y:.0f}초<extra></extra>"
            ))
            fig4.update_layout(barmode="stack", **base_layout(290, ""))
            st.plotly_chart(fig4, use_container_width=True)
            card_close()
        with c2:
            card_open("평균 요약")
            att_avg = resp["통화시간(초)"].mean()
            acw_avg = resp["ACW시간(초)"].mean()
            aht_avg = att_avg + acw_avg
            st.markdown(kpi_card("평균 ATT", fmt_hms(att_avg), accent="blue"),   unsafe_allow_html=True)
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            st.markdown(kpi_card("평균 ACW", fmt_hms(acw_avg), accent="orange"), unsafe_allow_html=True)
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            st.markdown(kpi_card("평균 AHT", fmt_hms(aht_avg), accent="green"),  unsafe_allow_html=True)
            card_close()

    # 문의 유형
    if "대분류" in phone.columns:
        section_title("문의 유형 분석")
        cat_df = phone.groupby("대분류").size().reset_index(name="건수").sort_values("건수",ascending=False)
        c1, c2 = st.columns([1,2])
        with c1:
            card_open("대분류 분포")
            st.plotly_chart(donut_chart(cat_df["대분류"].tolist(), cat_df["건수"].tolist(), h=230), use_container_width=True)
            st.markdown(donut_legend_html(cat_df["대분류"].tolist(), cat_df["건수"].tolist(), PALETTE), unsafe_allow_html=True)
            card_close()
        with c2:
            card_open("대분류별 인입 건수")
            fig5 = px.bar(cat_df, x="건수", y="대분류", orientation="h",
                          color_discrete_sequence=[COLORS["primary"]])
            fig5.update_layout(**base_layout(300,""))
            st.plotly_chart(fig5, use_container_width=True)
            card_close()

    # 히트맵
    section_title("인입 히트맵 (날짜 × 시간대)")
    if "인입시간대" in phone.columns and "일자" in phone.columns:
        tmp = phone.copy()
        tmp["일자str"] = pd.to_datetime(tmp["일자"]).dt.strftime("%m-%d")
        pivot = tmp.pivot_table(index="일자str", columns="인입시간대",
                                values="응대여부", aggfunc="count", fill_value=0)
        card_open("날짜 × 시간대 인입 히트맵")
        st.plotly_chart(heatmap_chart(pivot, h=340), use_container_width=True)
        card_close()

# ══════════════════════════════════════════════
# 전화 상담사
# ══════════════════════════════════════════════
def page_phone_agent(phone, unit, month_range):
    if phone.empty:
        st.info("전화 데이터가 없습니다.")
        return
    resp = phone[phone["응대여부"]=="응대"]
    if resp.empty:
        st.info("응대 데이터가 없습니다.")
        return

    section_title("상담사별 전화 성과")

    ag = resp.groupby("상담사명").agg(
        응대수=("상담사명", "count"),
        평균대기=("대기시간(초)", "mean"),
        평균ATT=("통화시간(초)", "mean"),
        평균ACW=("ACW시간(초)", "mean"),
    ).reset_index().sort_values("응대수", ascending=False)

    ag["평균AHT"] = ag["평균ATT"] + ag["평균ACW"]

    for c in ["평균대기", "평균ATT", "평균ACW", "평균AHT"]:
        ag[c+"_표시"] = ag[c].apply(fmt_hms)

    card_open("상담사별 성과 테이블", "ATT=통화시간(G열) / ACW=후처리(H열) / AHT=ATT+ACW")
    st.dataframe(
        ag[["상담사명","응대수",
            "평균대기_표시","평균ATT_표시","평균ACW_표시","평균AHT_표시"]].rename(columns={
            "평균대기_표시": "평균 대기",
            "평균ATT_표시":  "평균 ATT",
            "평균ACW_표시":  "평균 ACW",
            "평균AHT_표시":  "평균 AHT",
        }),
        use_container_width=True,
        height=400
    )
    card_close()

    c1, c2 = st.columns(2)
    with c1:
        if "팀명" in resp.columns:
            section_title("팀별 평균 AHT")
            tm = resp.groupby("팀명").agg(
                응대수=("팀명", "count"),
                평균ATT=("통화시간(초)", "mean"),
                평균ACW=("ACW시간(초)", "mean"),
            ).reset_index()
            tm["평균AHT"] = tm["평균ATT"] + tm["평균ACW"]
            card_open("팀별 평균 AHT (초)")
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=tm["팀명"], y=tm["평균ATT"],
                name="ATT", marker_color=COLORS["primary"]
            ))
            fig.add_trace(go.Bar(
                x=tm["팀명"], y=tm["평균ACW"],
                name="ACW", marker_color=COLORS["warning"]
            ))
            fig.update_layout(barmode="stack", **base_layout(300, ""))
            st.plotly_chart(fig, use_container_width=True)
            card_close()

    with c2:
        if "근속그룹" in resp.columns:
            section_title("근속그룹별 AHT")
            tg = resp.groupby("근속그룹").agg(
                응대수=("근속그룹", "count"),
                평균ATT=("통화시간(초)", "mean"),
                평균ACW=("ACW시간(초)", "mean"),
            ).reset_index()
            tg["평균AHT"] = tg["평균ATT"] + tg["평균ACW"]
            card_open("근속그룹별 평균 AHT (초)")
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                x=tg["근속그룹"], y=tg["평균ATT"],
                name="ATT", marker_color=COLORS["primary"]
            ))
            fig2.add_trace(go.Bar(
                x=tg["근속그룹"], y=tg["평균ACW"],
                name="ACW", marker_color=COLORS["warning"]
            ))
            fig2.update_layout(barmode="stack", **base_layout(300, ""))
            st.plotly_chart(fig2, use_container_width=True)
            card_close()

    section_title("상담사별 AHT 분포 (상위 20)")
    top20 = ag.head(20)
    card_open("상담사별 평균 AHT (ATT+ACW 스택)")
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=top20["상담사명"], y=top20["평균ATT"],
        name="ATT (통화시간)", marker_color=COLORS["primary"]
    ))
    fig3.add_trace(go.Bar(
        x=top20["상담사명"], y=top20["평균ACW"],
        name="ACW (후처리)", marker_color=COLORS["warning"]
    ))
    fig3.update_layout(barmode="stack", **base_layout(380, ""))
    st.plotly_chart(fig3, use_container_width=True)
    card_close()

# ══════════════════════════════════════════════
# 채팅 현황
# ══════════════════════════════════════════════
def page_chat(chat, unit, month_range, start, end):
    if chat.empty:
        st.info("채팅 데이터가 없습니다."); return

    resp     = chat[chat["응대여부"]=="응대"]
    total    = len(chat)
    rc       = len(resp)
    rr       = rc / total * 100 if total else 0
    avg_wait = resp["응답시간(초)"].mean() if not resp.empty else 0
    avg_lt   = resp["리드타임(초)"].mean()  if not resp.empty else 0

    # KPI
    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: st.markdown(kpi_card("전체 인입",     fmt_num(total), unit="건"), unsafe_allow_html=True)
    with c2: st.markdown(kpi_card("응대건수",      fmt_num(rc),    unit="건", accent="green"), unsafe_allow_html=True)
    with c3: st.markdown(kpi_card("응대율",        fmt_pct(rr),    accent="blue"), unsafe_allow_html=True)
    with c4: st.markdown(kpi_card("평균 대기시간", fmt_hms(avg_wait), accent="orange"), unsafe_allow_html=True)
    with c5: st.markdown(kpi_card("평균 리드타임", fmt_hms(avg_lt),   accent="blue"), unsafe_allow_html=True)

    # ★ 일별 추이
    render_daily_trends_block("chat", daily_trend_chat(chat))

    # 기간별 추이
    section_title("기간 단위 추이")
    pc = get_period_col(unit)
    cr_s, _ = get_chart_range(unit, end, month_range)
    ch_in = chat[chat[pc] >= pd.Timestamp(cr_s)].groupby(pc).size().reset_index(name="건수")
    ch_re = (resp[resp[pc] >= pd.Timestamp(cr_s)].groupby(pc).size().reset_index(name="건수")
             if not resp.empty else pd.DataFrame(columns=[pc,"건수"]))

    c1, c2 = st.columns([2,1])
    with c1:
        card_open("인입 / 응대 추이", f"기간 단위: {unit}")
        st.plotly_chart(
            trend_chart({"채팅 인입":ch_in,"응대":ch_re}, unit=unit, y_label="건수", h=300),
            use_container_width=True
        )
        card_close()
    with c2:
        card_open("응대 현황")
        fig = donut_chart(["응대","미응대"],[rc,total-rc],
                          [COLORS["success"],COLORS["danger"]], h=260)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(
            donut_legend_html(["응대","미응대"],[rc,total-rc],
                              [COLORS["success"],COLORS["danger"]]),
            unsafe_allow_html=True
        )
        card_close()

    # 시간대별
    section_title("시간대별 인입 / 응대 현황")
    hourly = chat.groupby("인입시간대").agg(
        인입=("인입시간대","count"),
        응대=("응대여부", lambda x: (x=="응대").sum()),
    ).reset_index()
    hourly["미응대"] = hourly["인입"] - hourly["응대"]
    hourly["응대율"] = (hourly["응대"] / hourly["인입"] * 100).round(1)

    card_open("시간대별 인입/응대 + 응대율")
    fig_h = go.Figure()
    fig_h.add_trace(go.Bar(x=hourly["인입시간대"], y=hourly["응대"],   name="응대",   marker_color=COLORS["chat"]))
    fig_h.add_trace(go.Bar(x=hourly["인입시간대"], y=hourly["미응대"], name="미응대", marker_color=hex_rgba(COLORS["danger"],0.7)))
    fig_h.add_trace(go.Scatter(
        x=hourly["인입시간대"], y=hourly["응대율"], name="응대율(%)",
        yaxis="y2", mode="lines+markers",
        line=dict(color=COLORS["warning"],width=2), marker=dict(size=6)
    ))
    fig_h.update_layout(
        **base_layout(320,""), barmode="stack",
        yaxis2=dict(overlaying="y", side="right", showgrid=False,
                    ticksuffix="%", range=[0,110])
    )
    st.plotly_chart(fig_h, use_container_width=True)
    card_close()

    # 대분류별 리드타임
    if "대분류" in chat.columns and not resp.empty:
        section_title("대분류별 평균 대기시간/리드타임")
        cat_df = resp.groupby("대분류").agg(
            건수=("대분류","count"),
            평균대기=("응답시간(초)","mean"),
            평균리드타임=("리드타임(초)","mean"),
        ).round(1).reset_index().sort_values("건수",ascending=False)

        c1, c2 = st.columns(2)
        with c1:
            card_open("대분류별 평균 대기시간(초)")
            fig3 = px.bar(cat_df, x="대분류", y="평균대기",
                          color_discrete_sequence=[COLORS["chat"]])
            fig3.update_layout(**base_layout(300,""))
            st.plotly_chart(fig3, use_container_width=True)
            card_close()
        with c2:
            card_open("대분류별 평균 리드타임(초)")
            fig4 = px.bar(cat_df, x="대분류", y="평균리드타임",
                          color_discrete_sequence=[COLORS["warning"]])
            fig4.update_layout(**base_layout(300,""))
            st.plotly_chart(fig4, use_container_width=True)
            card_close()

    if "플랫폼" in chat.columns:
        section_title("플랫폼별 분포")
        plat = chat.groupby("플랫폼").size().reset_index(name="건수").sort_values("건수",ascending=False).head(12)
        c1, c2 = st.columns([1,2])
        with c1:
            card_open("플랫폼 분포", "상위 12")
            st.plotly_chart(donut_chart(plat["플랫폼"].tolist(), plat["건수"].tolist(), h=230), use_container_width=True)
            st.markdown(donut_legend_html(plat["플랫폼"].tolist(), plat["건수"].tolist(), PALETTE), unsafe_allow_html=True)
            card_close()
        with c2:
            card_open("플랫폼별 건수")
            fig5 = px.bar(plat, x="플랫폼", y="건수", color_discrete_sequence=[COLORS["chat"]])
            fig5.update_layout(**base_layout(260,""))
            st.plotly_chart(fig5, use_container_width=True)
            card_close()

# ══════════════════════════════════════════════
# 채팅 상담사
# ══════════════════════════════════════════════
def page_chat_agent(chat, unit, month_range):
    if chat.empty:
        st.info("채팅 데이터가 없습니다."); return
    resp = chat[chat["응대여부"]=="응대"]
    if resp.empty:
        st.info("응대 데이터가 없습니다."); return

    section_title("상담사별 채팅 성과")
    ag = resp.groupby("상담사명").agg(
        응대수=("상담사명","count"),
        평균대기시간=("응답시간(초)","mean"),
        평균리드타임=("리드타임(초)","mean"),
    ).reset_index().sort_values("응대수", ascending=False)

    for c in ["평균대기시간","평균리드타임"]:
        ag[c+"_표시"] = ag[c].apply(fmt_hms)

    card_open("상담사별 성과 테이블", "대기시간 = 접수→첫멘트 응답 소요시간")
    st.dataframe(
        ag[["상담사명","응대수","평균대기시간_표시","평균리드타임_표시"]].rename(columns={
            "평균대기시간_표시":"평균 대기시간",
            "평균리드타임_표시":"평균 리드타임",
        }),
        use_container_width=True, height=400
    )
    card_close()

    c1, c2 = st.columns(2)
    with c1:
        if "팀명" in resp.columns:
            section_title("팀별 평균 대기시간")
            tm = resp.groupby("팀명").agg(
                응대수=("팀명","count"), 평균대기=("응답시간(초)","mean")
            ).round(1).reset_index()
            card_open("팀별 평균 대기시간(초)")
            fig = px.bar(tm, x="팀명", y="평균대기", color_discrete_sequence=[COLORS["chat"]])
            fig.update_layout(**base_layout(290,""))
            st.plotly_chart(fig, use_container_width=True)
            card_close()
    with c2:
        if "근속그룹" in resp.columns:
            section_title("근속그룹별 평균 대기시간")
            tg = resp.groupby("근속그룹").agg(
                응대수=("근속그룹","count"), 평균대기=("응답시간(초)","mean")
            ).round(1).reset_index()
            card_open("근속그룹별 평균 대기시간(초)")
            fig2 = px.bar(tg, x="근속그룹", y="평균대기", color_discrete_sequence=[COLORS["info"]])
            fig2.update_layout(**base_layout(290,""))
            st.plotly_chart(fig2, use_container_width=True)
            card_close()

    # 상담사별 대기시간 분포 (top 20)
    section_title("상담사별 평균 대기시간 분포 (상위 20)")
    top20 = ag.head(20)
    card_open("상담사별 평균 대기시간(초)")
    fig3 = px.bar(
        top20, x="평균대기시간", y="상담사명", orientation="h",
        color="평균대기시간",
        color_continuous_scale=["#dcfce7","#22c55e","#15803d"]
    )
    fig3.update_layout(**base_layout(420,""))
    st.plotly_chart(fig3, use_container_width=True)
    card_close()

# ══════════════════════════════════════════════
# 게시판 현황
# ══════════════════════════════════════════════
def page_board(board, unit, month_range, start, end):
    if board.empty:
        st.info("게시판 데이터가 없습니다."); return

    resp      = board[board["응대여부"]=="응대"]
    total     = len(board)
    rc        = len(resp)
    rr        = rc / total * 100 if total else 0
    avg_in    = resp["근무내리드타임(초)"].mean() if (not resp.empty and "근무내리드타임(초)" in resp.columns) else 0
    avg_off   = resp["근무외리드타임(초)"].mean() if (not resp.empty and "근무외리드타임(초)" in resp.columns) else 0
    avg_total = resp["리드타임(초)"].mean()        if (not resp.empty and "리드타임(초)" in resp.columns) else 0

    # KPI
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    with c1: st.markdown(kpi_card("전체 티켓",     fmt_num(total), unit="건"), unsafe_allow_html=True)
    with c2: st.markdown(kpi_card("응답완료",      fmt_num(rc),    unit="건", accent="green"), unsafe_allow_html=True)
    with c3: st.markdown(kpi_card("응답률",        fmt_pct(rr),    accent="blue"), unsafe_allow_html=True)
    with c4: st.markdown(kpi_card("평균 근무내 LT", fmt_hms(avg_in),    accent="green"), unsafe_allow_html=True)
    with c5: st.markdown(kpi_card("평균 근무외 LT", fmt_hms(avg_off),   accent="red"),   unsafe_allow_html=True)
    with c6: st.markdown(kpi_card("평균 전체 LT",   fmt_hms(avg_total), accent="orange"), unsafe_allow_html=True)

    # ★ 일별 추이
    render_daily_trends_block("board", daily_trend_board(board))

    # 기간별 추이
    section_title("기간 단위 추이")
    pc = get_period_col(unit)
    cr_s, _ = get_chart_range(unit, end, month_range)
    bo_in = board[board[pc] >= pd.Timestamp(cr_s)].groupby(pc).size().reset_index(name="건수")
    bo_re = (resp[resp[pc] >= pd.Timestamp(cr_s)].groupby(pc).size().reset_index(name="건수")
             if not resp.empty else pd.DataFrame(columns=[pc,"건수"]))

    c1, c2 = st.columns([2,1])
    with c1:
        card_open("티켓 접수 / 응답 추이", f"기간 단위: {unit}")
        st.plotly_chart(
            trend_chart({"접수":bo_in,"응답":bo_re}, unit=unit, y_label="건수", h=300),
            use_container_width=True
        )
        card_close()
    with c2:
        card_open("응답 현황")
        fig = donut_chart(["응답","미응답"],[rc,total-rc],
                          [COLORS["success"],COLORS["danger"]], h=260)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(
            donut_legend_html(["응답","미응답"],[rc,total-rc],
                              [COLORS["success"],COLORS["danger"]]),
            unsafe_allow_html=True
        )
        card_close()

    # 근무내/외 LT 추이 (기간별)
    if not resp.empty:
        section_title("근무내/외 리드타임 기간별 추이")
        lt_grp = resp.groupby(pc).agg(
            근무내LT=("근무내리드타임(초)","mean"),
            근무외LT=("근무외리드타임(초)","mean"),
        ).reset_index()
        card_open("기간별 평균 리드타임 분리", "근무내 vs 근무외")
        fig_lt = go.Figure()
        fig_lt.add_trace(go.Bar(x=lt_grp[pc], y=lt_grp["근무내LT"], name="근무내",
                                marker_color=COLORS["success"]))
        fig_lt.add_trace(go.Bar(x=lt_grp[pc], y=lt_grp["근무외LT"], name="근무외",
                                marker_color=COLORS["danger"]))
        fig_lt.update_layout(barmode="stack", **base_layout(300,""))
        st.plotly_chart(fig_lt, use_container_width=True)
        card_close()

    # 시간대별
    section_title("시간대별 접수 / 응답 현황")
    hourly = board.groupby("인입시간대").agg(
        접수=("인입시간대","count"),
        응답=("응대여부", lambda x: (x=="응대").sum()),
    ).reset_index()
    hourly["미응답"] = hourly["접수"] - hourly["응답"]
    hourly["응답률"] = (hourly["응답"] / hourly["접수"] * 100).round(1)

    card_open("시간대별 접수/응답 + 응답률")
    fig_h = go.Figure()
    fig_h.add_trace(go.Bar(x=hourly["인입시간대"], y=hourly["응답"],   name="응답",   marker_color=COLORS["board"]))
    fig_h.add_trace(go.Bar(x=hourly["인입시간대"], y=hourly["미응답"], name="미응답", marker_color=hex_rgba(COLORS["danger"],0.7)))
    fig_h.add_trace(go.Scatter(
        x=hourly["인입시간대"], y=hourly["응답률"], name="응답률(%)",
        yaxis="y2", mode="lines+markers",
        line=dict(color=COLORS["warning"],width=2), marker=dict(size=6)
    ))
    fig_h.update_layout(
        **base_layout(320,""), barmode="stack",
        yaxis2=dict(overlaying="y", side="right", showgrid=False,
                    ticksuffix="%", range=[0,110])
    )
    st.plotly_chart(fig_h, use_container_width=True)
    card_close()

    # 대분류별
    if "대분류" in board.columns:
        section_title("대분류별 티켓 분석")
        cat_df = board.groupby("대분류").agg(
            건수=("대분류","count"),
            응답수=("응대여부", lambda x: (x=="응대").sum())
        ).reset_index()
        cat_df["응답률"] = (cat_df["응답수"] / cat_df["건수"] * 100).round(1)

        c1, c2 = st.columns([1,2])
        with c1:
            card_open("대분류 분포")
            st.plotly_chart(donut_chart(cat_df["대분류"].tolist(), cat_df["건수"].tolist(), h=230), use_container_width=True)
            st.markdown(donut_legend_html(cat_df["대분류"].tolist(), cat_df["건수"].tolist(), PALETTE), unsafe_allow_html=True)
            card_close()
        with c2:
            card_open("대분류별 건수 / 응답률")
            fig3 = go.Figure()
            fig3.add_trace(go.Bar(x=cat_df["대분류"], y=cat_df["건수"],
                                  name="건수", marker_color=COLORS["board"]))
            fig3.add_trace(go.Scatter(
                x=cat_df["대분류"], y=cat_df["응답률"], name="응답률(%)",
                yaxis="y2", mode="lines+markers",
                line=dict(color=COLORS["success"],width=2), marker=dict(size=7)
            ))
            fig3.update_layout(
                **base_layout(300,""),
                yaxis2=dict(overlaying="y", side="right", showgrid=False,
                            ticksuffix="%", range=[0,110])
            )
            st.plotly_chart(fig3, use_container_width=True)
            card_close()

    if "플랫폼" in board.columns:
        section_title("플랫폼별 분포")
        plat = board.groupby("플랫폼").size().reset_index(name="건수").sort_values("건수",ascending=False).head(12)
        c1, c2 = st.columns([1,2])
        with c1:
            card_open("플랫폼 분포", "상위 12")
            st.plotly_chart(donut_chart(plat["플랫폼"].tolist(), plat["건수"].tolist(), h=230), use_container_width=True)
            st.markdown(donut_legend_html(plat["플랫폼"].tolist(), plat["건수"].tolist(), PALETTE), unsafe_allow_html=True)
            card_close()
        with c2:
            card_open("플랫폼별 건수")
            fig4 = px.bar(plat, x="플랫폼", y="건수", color_discrete_sequence=[COLORS["board"]])
            fig4.update_layout(**base_layout(260,""))
            st.plotly_chart(fig4, use_container_width=True)
            card_close()

# ══════════════════════════════════════════════
# 게시판 상담사
# ══════════════════════════════════════════════
def page_board_agent(board, unit, month_range):
    if board.empty:
        st.info("게시판 데이터가 없습니다."); return
    resp = board[board["응대여부"]=="응대"]
    if resp.empty:
        st.info("응답 데이터가 없습니다."); return

    section_title("상담사별 게시판 성과")
    ag = resp.groupby("상담사명").agg(
        응답수=("상담사명","count"),
        평균근무내LT=("근무내리드타임(초)","mean"),
        평균근무외LT=("근무외리드타임(초)","mean"),
        평균전체LT=("리드타임(초)","mean"),
    ).reset_index().sort_values("응답수", ascending=False)

    for c in ["평균근무내LT","평균근무외LT","평균전체LT"]:
        ag[c+"_표시"] = ag[c].apply(fmt_hms)

    card_open("상담사별 성과 테이블", "근무내/근무외 리드타임 분리")
    st.dataframe(
        ag[["상담사명","응답수","평균근무내LT_표시","평균근무외LT_표시","평균전체LT_표시"]].rename(columns={
            "평균근무내LT_표시":"평균 근무내 LT",
            "평균근무외LT_표시":"평균 근무외 LT",
            "평균전체LT_표시":"평균 전체 LT",
        }),
        use_container_width=True, height=400
    )
    card_close()

    c1, c2 = st.columns(2)
    with c1:
        if "팀명" in resp.columns:
            section_title("팀별 평균 근무내/외 LT")
            tm = resp.groupby("팀명").agg(
                응답수=("팀명","count"),
                근무내LT=("근무내리드타임(초)","mean"),
                근무외LT=("근무외리드타임(초)","mean"),
            ).round(1).reset_index()
            card_open("팀별 평균 LT 분리 (초)")
            fig = go.Figure()
            fig.add_trace(go.Bar(x=tm["팀명"], y=tm["근무내LT"], name="근무내",
                                 marker_color=COLORS["success"]))
            fig.add_trace(go.Bar(x=tm["팀명"], y=tm["근무외LT"], name="근무외",
                                 marker_color=COLORS["danger"]))
            fig.update_layout(barmode="group", **base_layout(290,""))
            st.plotly_chart(fig, use_container_width=True)
            card_close()
    with c2:
        if "근속그룹" in resp.columns:
            section_title("근속그룹별 평균 LT")
            tg = resp.groupby("근속그룹").agg(
                응답수=("근속그룹","count"),
                근무내LT=("근무내리드타임(초)","mean"),
                근무외LT=("근무외리드타임(초)","mean"),
            ).round(1).reset_index()
            card_open("근속그룹별 평균 LT 분리 (초)")
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(x=tg["근속그룹"], y=tg["근무내LT"], name="근무내",
                                  marker_color=COLORS["success"]))
            fig2.add_trace(go.Bar(x=tg["근속그룹"], y=tg["근무외LT"], name="근무외",
                                  marker_color=COLORS["danger"]))
            fig2.update_layout(barmode="group", **base_layout(290,""))
            st.plotly_chart(fig2, use_container_width=True)
            card_close()

    # 상담사별 LT 분포 (top 20)
    section_title("상담사별 LT 분포 (상위 20)")
    top20 = ag.head(20)
    card_open("상담사별 근무내/외 LT (초)")
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=top20["평균근무내LT"], y=top20["상담사명"],
        orientation="h", name="근무내", marker_color=COLORS["success"]
    ))
    fig3.add_trace(go.Bar(
        x=top20["평균근무외LT"], y=top20["상담사명"],
        orientation="h", name="근무외", marker_color=COLORS["danger"]
    ))
    fig3.update_layout(barmode="stack", **base_layout(440,""))
    st.plotly_chart(fig3, use_container_width=True)
    card_close()

# ══════════════════════════════════════════════
# 상담사 종합
# ══════════════════════════════════════════════
def page_agent_total(phone, chat, board):
    section_title("상담사 종합 성과")

    names = set()
    if not phone.empty: names.update(phone["상담사명"].dropna().unique())
    if not chat.empty:  names.update(chat["상담사명"].dropna().unique())
    if not board.empty: names.update(board["상담사명"].dropna().unique())
    names.discard("미응대")

    if not names:
        st.info("데이터가 없습니다."); return

    rows = []
    for name in names:
        ph = (phone[(phone["상담사명"]==name) & (phone["응대여부"]=="응대")]
              if not phone.empty else pd.DataFrame())
        ch = (chat[(chat["상담사명"]==name)   & (chat["응대여부"]=="응대")]
              if not chat.empty  else pd.DataFrame())
        bo = (board[(board["상담사명"]==name) & (board["응대여부"]=="응대")]
              if not board.empty else pd.DataFrame())
        rows.append({
            "상담사명":     name,
            "전화 응대":    len(ph),
            "채팅 응대":    len(ch),
            "게시판 응답":  len(bo),
            "전화 ATT": fmt_hms(ph["통화시간(초)"].mean()) if not ph.empty else "0:00:00",
	    "전화 ACW": fmt_hms(ph["ACW시간(초)"].mean())  if not ph.empty else "0:00:00",
	    "전화 AHT": fmt_hms(ph["통화시간(초)"].mean() + ph["ACW시간(초)"].mean()) if not ph.empty else "0:00:00",
            "채팅 대기":    fmt_hms(ch["응답시간(초)"].mean())       if (not ch.empty and "응답시간(초)" in ch.columns) else "0:00:00",
            "채팅 리드타임":fmt_hms(ch["리드타임(초)"].mean())       if not ch.empty else "0:00:00",
            "게시판 근무내 LT": fmt_hms(bo["근무내리드타임(초)"].mean()) if (not bo.empty and "근무내리드타임(초)" in bo.columns) else "0:00:00",
            "게시판 근무외 LT": fmt_hms(bo["근무외리드타임(초)"].mean()) if (not bo.empty and "근무외리드타임(초)" in bo.columns) else "0:00:00",
        })

    df_ag = pd.DataFrame(rows).sort_values("전화 응대", ascending=False)

    card_open("상담사 종합 테이블", "전체 채널 성과 통합")
    st.dataframe(df_ag, use_container_width=True, height=500)
    card_close()

    section_title("상담사별 채널 응대 분포 (상위 15)")
    top15 = df_ag.head(15)
    card_open("Top 15 채널 분포")
    fig = go.Figure()
    fig.add_trace(go.Bar(name="전화", x=top15["상담사명"], y=top15["전화 응대"], marker_color=COLORS["phone"]))
    fig.add_trace(go.Bar(name="채팅", x=top15["상담사명"], y=top15["채팅 응대"], marker_color=COLORS["chat"]))
    fig.add_trace(go.Bar(name="게시판", x=top15["상담사명"], y=top15["게시판 응답"], marker_color=COLORS["board"]))
    fig.update_layout(barmode="stack", **base_layout(360,""))
    st.plotly_chart(fig, use_container_width=True)
    card_close()

# ══════════════════════════════════════════════
# 사이드바
# ══════════════════════════════════════════════
def render_sidebar(phone_raw, chat_raw, board_raw):
    with st.sidebar:
        # 로고/헤더
        st.markdown("""
        <div style="padding:20px 16px 14px;border-bottom:1px solid rgba(255,255,255,0.07);margin-bottom:12px;">
            <div style="font-size:17px;font-weight:900;color:#fff;letter-spacing:-.6px;">
                📞 CC OPS
            </div>
            <div style="font-size:10.5px;color:rgba(148,163,184,0.9);margin-top:3px;font-weight:700;">
                Contact Center Analytics
            </div>
        </div>""", unsafe_allow_html=True)

        if st.button("🔄  데이터 새로고침", key="btn_refresh"):
            st.cache_data.clear()
            st.rerun()

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        # 기간 단위
        st.markdown(
            "<div style='font-size:10.5px;color:rgba(148,163,184,0.9);"
            "font-weight:800;margin-bottom:4px;'>기간 단위</div>",
            unsafe_allow_html=True
        )
        unit = st.radio(
            "기간 단위", ["일별","주별","월별"],
            horizontal=True, label_visibility="collapsed"
        )
        month_range = 3
        if unit == "월별":
            month_range = st.slider("추이 범위(개월)", 1, 6, 3)

        # 날짜 범위 빠른 선택
        today = date.today()
        st.markdown(
            "<div style='margin-top:12px;font-size:10.5px;color:rgba(148,163,184,0.9);"
            "font-weight:800;margin-bottom:6px;'>날짜 범위 빠른 선택</div>",
            unsafe_allow_html=True
        )
        c1, c2 = st.columns(2)
        with c1:
            if st.button("7일", key="d7"):
                st.session_state["ds"] = today - timedelta(days=6)
                st.session_state["de"] = today
        with c2:
            if st.button("30일", key="d30"):
                st.session_state["ds"] = today - timedelta(days=29)
                st.session_state["de"] = today
        c3, c4 = st.columns(2)
        with c3:
            if st.button("이번달", key="dmonth"):
                st.session_state["ds"] = today.replace(day=1)
                st.session_state["de"] = today
        with c4:
            if st.button("전체", key="dall"):
                st.session_state["ds"] = date(2024, 1, 1)
                st.session_state["de"] = today

        date_start = st.date_input(
            "시작일",
            value=st.session_state.get("ds", today - timedelta(days=29)),
            key="date_start"
        )
        date_end = st.date_input(
            "종료일",
            value=st.session_state.get("de", today),
            key="date_end"
        )

        # 사업자 필터
        all_ops = sorted(set(
            list(phone_raw["사업자명"].dropna().unique() if "사업자명" in phone_raw.columns else []) +
            list(chat_raw["사업자명"].dropna().unique()  if "사업자명" in chat_raw.columns  else []) +
            list(board_raw["사업자명"].dropna().unique() if "사업자명" in board_raw.columns else [])
        ))
        st.markdown(
            "<div style='margin-top:10px;font-size:10.5px;color:rgba(148,163,184,0.9);"
            "font-weight:800;margin-bottom:4px;'>사업자 필터</div>",
            unsafe_allow_html=True
        )
        sel_ops = st.multiselect(
            "사업자", all_ops, default=[],
            label_visibility="collapsed", key="sel_ops"
        )

        # 브랜드 필터
        all_brands = sorted(set(
            list(phone_raw["브랜드"].dropna().unique() if "브랜드" in phone_raw.columns else []) +
            list(chat_raw["브랜드"].dropna().unique()  if "브랜드" in chat_raw.columns  else []) +
            list(board_raw["브랜드"].dropna().unique() if "브랜드" in board_raw.columns else [])
        ))
        st.markdown(
            "<div style='margin-top:10px;font-size:10.5px;color:rgba(148,163,184,0.9);"
            "font-weight:800;margin-bottom:4px;'>브랜드 필터</div>",
            unsafe_allow_html=True
        )
        sel_brands = st.multiselect(
            "브랜드", all_brands, default=[],
            label_visibility="collapsed", key="sel_brands"
        )

        # 메뉴 네비게이션
        st.markdown("""
        <div style="margin-top:16px;padding-top:14px;
                    border-top:1px solid rgba(255,255,255,0.07);
                    font-size:10.5px;color:rgba(148,163,184,0.9);
                    font-weight:800;margin-bottom:8px;">
            메뉴 네비게이션
        </div>""", unsafe_allow_html=True)

        menu = st.session_state.get("menu", "전체 현황")

        for group, items in MENU_GROUPS.items():
            st.markdown(
                f"<div style='margin:10px 0 5px;font-size:10px;"
                f"color:rgba(148,163,184,0.55);font-weight:900;"
                f"text-transform:uppercase;letter-spacing:.5px;'>{group}</div>",
                unsafe_allow_html=True
            )
            for item in items:
                is_active = (menu == item)
                wrap_cls  = "sidebar-active" if is_active else ""
                icon_map  = {
                    "전체 현황":     "🏠",
                    "VOC 인입 분석": "📋",
                    "사업자 현황":   "🏢",
                    "전화 현황":     "📞",
                    "전화 상담사":   "👤",
                    "채팅 현황":     "💬",
                    "채팅 상담사":   "👤",
                    "게시판 현황":   "📝",
                    "게시판 상담사": "👤",
                    "상담사 종합":   "📊",
                }
                icon  = icon_map.get(item, "•")
                label = f"{icon} {item}"
                st.markdown(f"<div class='{wrap_cls}'>", unsafe_allow_html=True)
                if st.button(label, key=f"m_{item}"):
                    st.session_state["menu"] = item
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        # 사이드바 하단 여백 (토글 버튼 가림 방지)
        st.markdown("<div style='height:60px'></div>", unsafe_allow_html=True)

    return unit, month_range, date_start, date_end, sel_ops, sel_brands

# ══════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════
def main():
    # 로딩 스피너
    with st.spinner("데이터를 불러오는 중..."):
        agent_raw = load_agent()
        phone_raw = load_phone()
        chat_raw  = load_chat()
        board_raw = load_board()

    unit, month_range, date_start, date_end, sel_ops, sel_brands = \
        render_sidebar(phone_raw, chat_raw, board_raw)

    base_d  = date.today()
    phone_m = merge_agent(phone_raw, agent_raw, base_d)
    chat_m  = merge_agent(chat_raw,  agent_raw, base_d)
    board_m = merge_agent(board_raw, agent_raw, base_d)

    phone_f = filter_df(phone_m, date_start, date_end, sel_brands or None, sel_ops or None)
    chat_f  = filter_df(chat_m,  date_start, date_end, sel_brands or None, sel_ops or None)
    board_f = filter_df(board_m, date_start, date_end, sel_brands or None, sel_ops or None)

    # 데이터 없을 때 안내
    if all(len(df) == 0 for df in [phone_f, chat_f, board_f]):
        st.markdown("""
        <div style="display:flex;flex-direction:column;align-items:center;
                    justify-content:center;height:60vh;text-align:center;gap:14px;">
            <div style="font-size:48px;">📊</div>
            <div style="font-size:22px;font-weight:900;color:#0f172a;">
                데이터 연결 필요
            </div>
            <div style="font-size:13px;color:#64748b;font-weight:700;">
                Google Sheets에 데이터를 입력하거나 필터 조건을 확인해주세요.
            </div>
            <div style="font-size:11.5px;color:#94a3b8;background:#f1f5f9;
                        padding:8px 18px;border-radius:12px;font-weight:800;
                        border:1px solid #e2e8f0;">
                SHEET_ID 및 GID_MAP 설정을 확인하세요
            </div>
        </div>""", unsafe_allow_html=True)
        return

    # 페이지 라우팅
    menu = st.session_state.get("menu", "전체 현황")

    if   menu == "전체 현황":
        page_overview(phone_f, chat_f, board_f, unit, month_range, date_start, date_end,
              phone_all=phone_m,   # 필터 전 전체 데이터 (이전기간 계산용)
              chat_all=chat_m,
              board_all=board_m)
    elif menu == "VOC 인입 분석":
        page_voc(phone_f, chat_f, board_f, unit, month_range, date_start, date_end)
    elif menu == "사업자 현황":
        page_operator(phone_f, chat_f, board_f, unit, month_range)
    elif menu == "전화 현황":
        page_phone(phone_f, unit, month_range, date_start, date_end)
    elif menu == "전화 상담사":
        page_phone_agent(phone_f, unit, month_range)
    elif menu == "채팅 현황":
        page_chat(chat_f, unit, month_range, date_start, date_end)
    elif menu == "채팅 상담사":
        page_chat_agent(chat_f, unit, month_range)
    elif menu == "게시판 현황":
        page_board(board_f, unit, month_range, date_start, date_end)
    elif menu == "게시판 상담사":
        page_board_agent(board_f, unit, month_range)
    elif menu == "상담사 종합":
        page_agent_total(phone_f, chat_f, board_f)


if __name__ == "__main__":
    main()
