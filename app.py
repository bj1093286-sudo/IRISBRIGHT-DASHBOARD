import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date, time
import holidays
import math
import io

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
    "전체 현황":   ["전체 현황"],
    "VOC 분석":    ["VOC 인입 분석"],
    "사업자":      ["사업자 현황"],
    "전화":        ["전화 현황","전화 상담사"],
    "채팅":        ["채팅 현황","채팅 상담사"],
    "게시판":      ["게시판 현황","게시판 상담사"],
    "상담사":      ["상담사 종합"],
    "위험/병목":   ["SLA 위반 분석","이상치 탐지","연속 미응대"],
    "예측/계획":   ["요일×시간대 패턴","변동성 지수","인력 산정"],
    "상담사 품질": ["AHT 분산분석","학습곡선","멀티채널 효율"],
    "운영 비교":   ["비용 시뮬레이터","팀×채널 매트릭스"],
}
EXCLUDE_AGENTS = {"이은덕", "양현정", "이혜선", "한인경", "박성주", "엄소라"}

# SLA 임계값
SLA_PHONE_WAIT  = None   # 전화 SLA 미적용
SLA_CHAT_WAIT   = 120    # 채팅 2분
SLA_BOARD_IN    = 10800  # 게시판 근무내 3시간
SLA_BOARD_OFF   = 25200  # 게시판 근무외 7시간

# ══════════════════════════════════════════════
# 페이지 설정
# ══════════════════════════════════════════════
st.set_page_config(
    page_title="Contact Center OPS",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════
# 전체 글로벌 CSS (기존 + 신규)
# ══════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    background: #F0F2F5 !important;
    color: #0f172a;
}
.main .block-container {
    padding: 20px 28px !important;
    max-width: 100% !important;
    background: #F0F2F5 !important;
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%) !important;
    min-width: 240px !important;
    max-width: 240px !important;
    border-right: 1px solid rgba(255,255,255,0.05) !important;
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    transform: none !important;
    width: 240px !important;
    position: relative !important;
    left: 0 !important;
}
section[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }
section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
section[data-testid="stSidebar"] > div { display: block !important; visibility: visible !important; width: 240px !important; }
[data-testid="collapsedControl"] {
    display: flex !important; visibility: visible !important; opacity: 1 !important;
    pointer-events: all !important; position: fixed !important; left: 240px !important;
    top: 50% !important; z-index: 999999 !important; background: #1e293b !important;
    border-radius: 0 8px 8px 0 !important; padding: 8px 4px !important;
    border: 1px solid rgba(255,255,255,0.12) !important; border-left: none !important;
    box-shadow: 3px 0 12px rgba(0,0,0,0.25) !important; transition: background 150ms ease !important;
}
[data-testid="collapsedControl"] svg { fill: #e2e8f0 !important; color: #e2e8f0 !important; width: 16px !important; height: 16px !important; }
[data-testid="collapsedControl"]:hover { background: #6366f1 !important; }

section[data-testid="stSidebar"] .stButton > button {
    background: transparent !important; border: none !important; border-radius: 8px !important;
    color: #cbd5e1 !important; width: 100% !important; text-align: left !important;
    padding: 0 12px !important; height: 36px !important; font-size: 13px !important;
    font-weight: 500 !important; margin-bottom: 2px !important;
    transition: all 150ms cubic-bezier(0.4, 0, 0.2, 1) !important; letter-spacing: -0.01em !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(99,102,241,0.15) !important; color: #fff !important;
}
.sidebar-active button {
    background: rgba(99,102,241,0.2) !important; border-left: 2px solid #6366f1 !important;
    color: #fff !important; font-weight: 600 !important;
}
section[data-testid="stSidebar"] .stRadio label { font-size: 13px !important; font-weight: 500 !important; color: #cbd5e1 !important; }
section[data-testid="stSidebar"] .stDateInput input {
    background: rgba(255,255,255,0.06) !important; border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 6px !important; color: #e2e8f0 !important; font-size: 13px !important;
    height: 34px !important; transition: border-color 150ms ease !important;
}
section[data-testid="stSidebar"] .stDateInput input:focus {
    border-color: rgba(99,102,241,0.6) !important; box-shadow: 0 0 0 2px rgba(99,102,241,0.15) !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] { background: rgba(255,255,255,0.06) !important; border-radius: 6px !important; }
section[data-testid="stSidebar"] [data-baseweb="select"] * { color: #e2e8f0 !important; background: #1e293b !important; }

.dash-header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 20px; padding: 18px 24px; background: #ffffff;
    border-radius: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.03);
    border: 1px solid rgba(226,232,240,0.8);
}
.dash-header-left h1 { font-size: 18px; font-weight: 800; color: #0f172a; letter-spacing: -0.025em; margin-bottom: 3px; line-height: 1.3; }
.dash-header-left span { font-size: 12px; color: #64748b; font-weight: 500; }
.dash-badge { font-size: 11px; font-weight: 700; padding: 2px 10px; border-radius: 9999px; display: inline-flex; align-items: center; gap: 4px; }
.dash-badge.primary { color: #6366f1; background: rgba(99,102,241,0.1); border: 1px solid rgba(99,102,241,0.2); }
.dash-badge.neutral { color: #64748b; background: rgba(148,163,184,0.1); border: 1px solid rgba(148,163,184,0.2); }
.dash-badge.danger  { color: #dc2626; background: rgba(239,68,68,0.08);  border: 1px solid rgba(239,68,68,0.15); }
.dash-badge.success { color: #16a34a; background: rgba(34,197,94,0.08);  border: 1px solid rgba(34,197,94,0.15); }
.dash-badge.warning { color: #d97706; background: rgba(245,158,11,0.08); border: 1px solid rgba(245,158,11,0.15); }

.section-title {
    font-size: 13px; font-weight: 700; color: #0f172a; margin: 22px 0 10px;
    letter-spacing: -0.015em; display: flex; align-items: center; gap: 8px; line-height: 1.4;
}
.section-title::before {
    content: ''; display: inline-block; width: 3px; height: 15px;
    background: linear-gradient(180deg, #6366f1, #8b5cf6); border-radius: 9999px; flex-shrink: 0;
}

.card {
    background: #ffffff; border-radius: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.03);
    padding: 20px 24px; border: 1px solid rgba(226,232,240,0.8); margin-bottom: 4px;
    transition: box-shadow 150ms ease;
}
.card:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.07), 0 1px 3px rgba(0,0,0,0.04); }
.card-title { font-size: 13px; font-weight: 700; color: #0f172a; margin-bottom: 2px; letter-spacing: -0.015em; line-height: 1.4; }
.card-subtitle { font-size: 11px; font-weight: 500; color: #64748b; margin-bottom: 14px; line-height: 1.4; }

.kpi-card {
    background: #ffffff; border-radius: 12px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.03);
    padding: 18px 20px 16px; border: 1px solid rgba(226,232,240,0.8);
    height: 100%; position: relative; overflow: hidden;
    transition: box-shadow 150ms ease, transform 150ms ease;
}
.kpi-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.08); transform: translateY(-1px); }
.kpi-card::before {
    content: ''; position: absolute; top: 0; left: 0;
    width: 100%; height: 3px; background: linear-gradient(90deg, #6366f1, #8b5cf6);
    border-radius: 12px 12px 0 0;
}
.kpi-card.green::before  { background: linear-gradient(90deg, #22c55e, #16a34a); }
.kpi-card.orange::before { background: linear-gradient(90deg, #f59e0b, #d97706); }
.kpi-card.red::before    { background: linear-gradient(90deg, #ef4444, #dc2626); }
.kpi-card.blue::before   { background: linear-gradient(90deg, #3b82f6, #2563eb); }
.kpi-label { font-size: 11px; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 10px; margin-top: 4px; }
.kpi-value { font-size: 24px; font-weight: 700; color: #0f172a; letter-spacing: -0.025em; line-height: 1.1; margin-bottom: 10px; }
.kpi-unit  { font-size: 13px; color: #94a3b8; margin-left: 3px; font-weight: 500; }
.kpi-delta-row { display: flex; gap: 4px; flex-wrap: wrap; align-items: center; margin-top: 4px; }
.kpi-delta { display: inline-flex; align-items: center; gap: 3px; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 9999px; letter-spacing: 0.01em; }
.kpi-delta.up   { background: rgba(239,68,68,0.08);  color: #dc2626; border: 1px solid rgba(239,68,68,0.15); }
.kpi-delta.down { background: rgba(34,197,94,0.08);  color: #16a34a; border: 1px solid rgba(34,197,94,0.15); }
.kpi-delta.neu  { background: rgba(148,163,184,0.1); color: #64748b; border: 1px solid rgba(148,163,184,0.2); }
.kpi-delta.up.rev   { background: rgba(34,197,94,0.08)  !important; color: #16a34a !important; border: 1px solid rgba(34,197,94,0.15) !important; }
.kpi-delta.down.rev { background: rgba(239,68,68,0.08)  !important; color: #dc2626 !important; border: 1px solid rgba(239,68,68,0.15) !important; }

.donut-legend { display: flex; flex-direction: column; gap: 5px; margin-top: 10px; }
.donut-item { display: flex; align-items: center; justify-content: space-between; padding: 7px 10px; border-radius: 8px; background: #f8fafc; border: 1px solid rgba(226,232,240,0.6); transition: background 150ms ease, border-color 150ms ease; }
.donut-item:hover { background: #f1f5f9; border-color: rgba(99,102,241,0.15); }
.donut-left  { display: flex; align-items: center; gap: 8px; min-width: 0; flex: 1; }
.swatch      { width: 8px; height: 8px; border-radius: 3px; flex: 0 0 auto; }
.donut-label { font-size: 12px; font-weight: 500; color: #374151; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.donut-right { display: flex; align-items: center; gap: 8px; flex: 0 0 auto; }
.donut-val   { font-size: 12px; font-weight: 700; color: #0f172a; }
.donut-pct   { font-size: 11px; font-weight: 700; color: #fff; padding: 2px 8px; border-radius: 9999px; min-width: 42px; text-align: center; }

.stTabs [data-baseweb="tab-list"] { background: #f1f5f9 !important; border-radius: 8px !important; padding: 3px !important; border: 1px solid rgba(226,232,240,0.8) !important; gap: 2px !important; }
.stTabs [data-baseweb="tab"] { border-radius: 6px !important; font-weight: 500 !important; font-size: 13px !important; color: #64748b !important; padding: 6px 16px !important; transition: all 150ms cubic-bezier(0.4, 0, 0.2, 1) !important; height: 32px !important; }
.stTabs [aria-selected="true"] { background: #6366f1 !important; color: #fff !important; box-shadow: 0 1px 3px rgba(99,102,241,0.3) !important; font-weight: 600 !important; }

[data-baseweb="tag"] { background: rgba(99,102,241,0.1) !important; border: 1px solid rgba(99,102,241,0.2) !important; border-radius: 9999px !important; font-size: 11px !important; }

#MainMenu  { visibility: hidden !important; }
footer     { visibility: hidden !important; }
.stDeployButton          { display: none !important; }
div[data-testid="stToolbar"] { display: none !important; }

::-webkit-scrollbar       { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(148,163,184,0.4); border-radius: 9999px; }
::-webkit-scrollbar-thumb:hover { background: rgba(148,163,184,0.7); }

.sidebar-divider { border: none; border-top: 1px solid rgba(255,255,255,0.07); margin: 10px 0; }

.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 60px 24px; text-align: center; gap: 12px; background: #ffffff; border-radius: 12px; border: 1px solid rgba(226,232,240,0.8); box-shadow: 0 1px 3px rgba(0,0,0,0.05); }

/* ── 신규: Alert 카드 ── */
.alert-card {
    padding: 12px 16px; border-radius: 10px; margin-bottom: 8px;
    display: flex; align-items: flex-start; gap: 10px;
    font-size: 12px; font-weight: 500; line-height: 1.5;
}
.alert-card.danger  { background: rgba(239,68,68,0.07);  border: 1px solid rgba(239,68,68,0.18);  color: #b91c1c; }
.alert-card.warning { background: rgba(245,158,11,0.07); border: 1px solid rgba(245,158,11,0.18); color: #b45309; }
.alert-card.info    { background: rgba(59,130,246,0.07); border: 1px solid rgba(59,130,246,0.18); color: #1d4ed8; }
.alert-card.success { background: rgba(34,197,94,0.07);  border: 1px solid rgba(34,197,94,0.18);  color: #15803d; }
.alert-icon { font-size: 16px; flex-shrink: 0; margin-top: 1px; }

/* ── 신규: Insights Drawer ── */
.insights-drawer {
    background: #fff; border-radius: 12px; border: 1px solid rgba(226,232,240,0.8);
    box-shadow: 0 1px 3px rgba(0,0,0,0.05); padding: 16px 20px; margin-bottom: 16px;
}
.insights-drawer-title {
    font-size: 13px; font-weight: 700; color: #0f172a; margin-bottom: 10px;
    display: flex; align-items: center; gap: 6px; letter-spacing: -0.015em;
}

/* ── 신규: Flag 뱃지 ── */
.flag-badge {
    display: inline-flex; align-items: center; gap: 4px;
    font-size: 10px; font-weight: 700; padding: 2px 8px;
    border-radius: 9999px; border: 1px solid;
}
.flag-badge.red    { background: rgba(239,68,68,0.08);  color: #dc2626; border-color: rgba(239,68,68,0.2); }
.flag-badge.amber  { background: rgba(245,158,11,0.08); color: #b45309; border-color: rgba(245,158,11,0.2); }
.flag-badge.green  { background: rgba(34,197,94,0.08);  color: #15803d; border-color: rgba(34,197,94,0.2); }
.flag-badge.indigo { background: rgba(99,102,241,0.08); color: #4338ca; border-color: rgba(99,102,241,0.2); }

/* ── 신규: Matrix 셀 ── */
.matrix-header { font-size: 11px; font-weight: 700; color: #64748b; text-align: center; padding: 6px; background: #f8fafc; border-radius: 6px; margin-bottom: 2px; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# 한국 공휴일
# ══════════════════════════════════════════════
def get_kr_holidays():
    today = date.today()
    yr = today.year
    return holidays.KR(years=[yr-1, yr, yr+1], observed=True)

KR_HOLIDAYS = get_kr_holidays()

# ══════════════════════════════════════════════
# 유틸 (기존 유지)
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
    try:
        if prev is None or float(prev) == 0:
            return None
        return round((float(curr) - float(prev)) / float(prev) * 100, 1)
    except:
        return None

def calc_delta_pp(curr, prev):
    try:
        if prev is None:
            return None
        return round(float(curr) - float(prev), 1)
    except:
        return None

def get_prev_period(df, start, end):
    if df.empty or "일자" not in df.columns:
        return pd.DataFrame()
    period_days = (pd.Timestamp(end) - pd.Timestamp(start)).days + 1
    prev_end    = pd.Timestamp(start) - timedelta(days=1)
    prev_start  = prev_end - timedelta(days=period_days - 1)
    mask = (df["일자"] >= prev_start) & (df["일자"] <= prev_end)
    return df[mask].copy()

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
    df["주차"] = df[date_col] - pd.to_timedelta(df[date_col].dt.dayofweek, unit="D")
    df["주차"] = pd.to_datetime(df["주차"].dt.date)
    df["월"] = pd.to_datetime(df[date_col].dt.to_period("M").dt.start_time)
    return df

def get_chart_range(unit, end_date, month_range=3):
    ed = pd.Timestamp(end_date)
    if unit == "일별": return ed - timedelta(days=89), ed
    if unit == "주별": return ed - timedelta(weeks=12), ed
    return ed - timedelta(days=30*month_range), ed

def parse_duration_seconds(v):
    if v is None:
        return 0.0
    if isinstance(v, (int, float, np.integer, np.floating)):
        if np.isnan(v): return 0.0
        return float(v)
    s = str(v).strip()
    if s == "" or s.lower() in {"nan","none","null","-",""}:
        return 0.0
    try:
        return float(s)
    except:
        pass
    s = s.replace(",","").strip()
    if ":" not in s:
        return 0.0
    parts = s.split(":")
    parts = [p.strip() for p in parts if p.strip() != ""]
    if len(parts) == 3:
        try:
            h   = float(parts[0])
            m   = float(parts[1])
            sec = float(parts[2])
            return h * 3600.0 + m * 60.0 + sec
        except:
            return 0.0
    if len(parts) == 2:
        try:
            return float(parts[0]) * 60.0 + float(parts[1])
        except:
            return 0.0
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

def is_business_day(d: date) -> bool:
    if d.weekday() >= 5:
        return False
    if d in KR_HOLIDAYS:
        return False
    return True

def overlap_seconds(a_s: datetime, a_e: datetime, b_s: datetime, b_e: datetime) -> float:
    start = max(a_s, b_s)
    end   = min(a_e, b_e)
    if end <= start: return 0.0
    return (end - start).total_seconds()

def split_board_leadtime(start_dt, end_dt):
    if pd.isna(start_dt) or pd.isna(end_dt):
        return 0.0, 0.0, 0.0
    s = pd.Timestamp(start_dt).to_pydatetime()
    e = pd.Timestamp(end_dt).to_pydatetime()
    if e <= s:
        return 0.0, 0.0, 0.0
    in_sec  = 0.0
    off_sec = 0.0
    cur_day = s.date()
    end_day = e.date()
    while cur_day <= end_day:
        if not is_business_day(cur_day):
            cur_day += timedelta(days=1)
            continue
        day_start = datetime.combine(cur_day, time(0,  0, 0))
        day_end   = datetime.combine(cur_day, time(23,59,59)) + timedelta(seconds=1)
        seg_s = max(s, day_start)
        seg_e = min(e, day_end)
        if seg_e > seg_s:
            bh_s = datetime.combine(cur_day, time(WORK_START, 0, 0))
            bh_e = datetime.combine(cur_day, time(WORK_END,   0, 0))
            off_s1 = datetime.combine(cur_day, time(0,  0, 0))
            off_e1 = datetime.combine(cur_day, time(WORK_START, 0, 0))
            off_s2 = datetime.combine(cur_day, time(WORK_END, 0, 0))
            off_e2 = datetime.combine(cur_day, time(23,59,59)) + timedelta(seconds=1)
            in_sec  += overlap_seconds(seg_s, seg_e, bh_s,  bh_e)
            off_sec += overlap_seconds(seg_s, seg_e, off_s1, off_e1)
            off_sec += overlap_seconds(seg_s, seg_e, off_s2, off_e2)
        cur_day += timedelta(days=1)
    total = in_sec + off_sec
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
# UI 헬퍼 (기존 유지)
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
    st.markdown(
        f"<div class='section-title'>{txt}</div>",
        unsafe_allow_html=True
    )

def donut_legend_html(labels, values, colors):
    total = float(sum(v for v in values if v is not None))
    rows  = []
    for i, (lab, val) in enumerate(zip(labels, values)):
        v   = float(val) if val is not None else 0.0
        pct = (v / total * 100.0) if total > 0 else 0.0
        c   = colors[i % len(colors)]
        # 긴 레이블 툴팁 처리
        disp = lab if len(lab) <= 18 else lab[:16] + "…"
        rows.append(f"""
        <div class="donut-item">
          <div class="donut-left">
            <span class="swatch" style="background:{c}; box-shadow: 0 0 0 2px {c}22;"></span>
            <span class="donut-label" title="{lab}">{disp}</span>
          </div>
          <div class="donut-right">
            <span class="donut-val">{int(v):,}</span>
            <span class="donut-pct" style="background:{c}">{pct:.1f}%</span>
          </div>
        </div>""")
    return f"<div class='donut-legend'>{''.join(rows)}</div>"

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
        dh += ('<span style="font-size:10px;color:#94a3b8;margin:0 2px;'
               'font-weight:700;letter-spacing:0.02em;">YoY</span>')
        dh += badge(delta_yoy, reverse)

    return f"""<div class="kpi-card{ac}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}<span class="kpi-unit">{unit}</span></div>
        <div class="kpi-delta-row">{dh}</div>
    </div>"""

def base_layout(h=320, title="", legend_side=False):
    lg = (
        dict(orientation="v", yanchor="middle", y=0.5,
             xanchor="left", x=1.02,
             font=dict(size=11, family="Inter", color="#64748b"),
             bgcolor="rgba(0,0,0,0)", borderwidth=0)
        if legend_side else
        dict(orientation="h", yanchor="bottom", y=1.02,
             xanchor="right", x=1,
             font=dict(size=11, family="Inter", color="#64748b"),
             bgcolor="rgba(0,0,0,0)", borderwidth=0)
    )
    return dict(
        height=h,
        title=dict(
            text=title,
            font=dict(size=13, color="#0f172a", family="Inter", weight=700),
            x=0, pad=dict(l=0, b=8)
        ),
        margin=dict(l=8, r=12, t=44 if title else 12, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", size=11, color="#64748b"),
        legend=lg,
        xaxis=dict(
            showgrid=False, zeroline=False,
            tickfont=dict(size=10, color="#94a3b8"),
            automargin=True,
            linecolor="rgba(226,232,240,0.6)",
            tickcolor="rgba(226,232,240,0.6)"
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(226,232,240,0.5)",
            gridwidth=1,
            zeroline=False,
            tickfont=dict(size=10, color="#94a3b8"),
            automargin=True,
        ),
        hoverlabel=dict(
            bgcolor="#0f172a",
            bordercolor="#0f172a",
            font=dict(color="#f8fafc", size=12, family="Inter"),
        ),
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
            line=dict(color=c, width=2.5, shape="spline", smoothing=0.8),
            marker=dict(size=5, color="#ffffff",
                        line=dict(color=c, width=2)),
            fill="tozeroy", fillcolor=hex_rgba(c, 0.06),
            hovertemplate=f"<b>%{{x}}</b><br>{name}: %{{y:,}}<extra></extra>"
        ))
    fig.update_layout(**base_layout(h, title))
    return fig

def donut_chart(labels, values, colors=None, h=250, title=""):
    if not colors: colors = PALETTE
    total = sum(v for v in values if v) if values else 0
    fig   = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.72,
        marker=dict(
            colors=colors[:len(labels)],
            line=dict(color="#ffffff", width=3)
        ),
        textinfo="none",
        hovertemplate="<b>%{label}</b><br>%{value:,}건 (%{percent})<extra></extra>",
    ))
    lo = base_layout(h, title, legend_side=False)
    lo["showlegend"] = False
    lo["annotations"] = [dict(
        text=(f"<span style='font-size:10px;'>{total:,}</span>"),
        x=0.5, y=0.5, showarrow=False, align="center",
        font=dict(size=18, color="#0f172a", family="Inter")
    )]
    fig.update_layout(**lo)
    return fig

def heatmap_chart(df_pivot, h=320, title=""):
    fig = go.Figure(go.Heatmap(
        z=df_pivot.values,
        x=df_pivot.columns.astype(str),
        y=df_pivot.index.astype(str),
        colorscale=[
            [0,   "#f8fafc"],
            [0.3, "#e0e7ff"],
            [0.6, "#818cf8"],
            [1.0, "#3730a3"]
        ],
        showscale=True,
        colorbar=dict(
            thickness=10, len=0.8,
            tickfont=dict(size=10, color="#94a3b8"),
            outlinewidth=0,
        ),
        hovertemplate="시간대: <b>%{x}시</b><br>날짜: <b>%{y}</b><br>건수: <b>%{z}</b><extra></extra>",
    ))
    fig.update_layout(**base_layout(h, title))
    return fig

def line_chart_simple(df, x, y, color, h=290, y_suffix=""):
    fig = go.Figure(go.Scatter(
        x=df[x], y=df[y],
        mode="lines+markers",
        line=dict(color=color, width=2.5, shape="spline", smoothing=0.8),
        marker=dict(size=5, color="#ffffff", line=dict(color=color, width=2)),
        fill="tozeroy", fillcolor=hex_rgba(color, 0.06),
        hovertemplate=f"<b>%{{x}}</b><br>%{{y:,.1f}}{y_suffix}<extra></extra>"
    ))
    lo = base_layout(h, "")
    if y_suffix:
        lo["yaxis"]["ticksuffix"] = y_suffix
    fig.update_layout(**lo)
    return fig

# ══════════════════════════════════════════════
# CSV 다운로드 버튼 (신규)
# ══════════════════════════════════════════════
def download_csv_button(df: pd.DataFrame, filename: str, label: str = "📥 CSV 다운로드"):
    """DataFrame을 CSV로 다운로드하는 버튼을 렌더링"""
    if df.empty:
        return
    buf = io.BytesIO()
    df.to_csv(buf, index=False, encoding="utf-8-sig")
    buf.seek(0)
    st.download_button(
        label=label,
        data=buf.getvalue(),
        file_name=filename,
        mime="text/csv",
        key=f"dl_{filename}_{id(df)}"
    )

# ══════════════════════════════════════════════
# Insights Drawer (신규)
# ══════════════════════════════════════════════
def insights_drawer(key: str, title: str, content_fn):
    """
    세션 상태 기반 열림/닫힘 드로어 패턴.
    content_fn(): 드로어 내부에서 실행할 렌더링 함수(callable)
    """
    open_key = f"drawer_{key}"
    if open_key not in st.session_state:
        st.session_state[open_key] = False

    col_title, col_btn = st.columns([5, 1])
    with col_title:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:8px;padding:6px 0;">
          <span style="font-size:13px;font-weight:700;color:#0f172a;">{title}</span>
        </div>""", unsafe_allow_html=True)
    with col_btn:
        lbl = "접기 ▲" if st.session_state[open_key] else "열기 ▼"
        if st.button(lbl, key=f"btn_{key}"):
            st.session_state[open_key] = not st.session_state[open_key]

    if st.session_state[open_key]:
        st.markdown("<div class='insights-drawer'>", unsafe_allow_html=True)
        content_fn()
        st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# 데이터 로드 (기존 유지)
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
        for col in df.columns:
            if "(초)" in col:
                df[col] = df[col].apply(parse_duration_seconds).astype(float)
        time_cols = ["대기시간(초)", "통화시간(초)", "ACW시간(초)"]
        for col in time_cols:
            if col in df.columns:
                df[col] = df[col].apply(parse_duration_seconds).astype(float)
            else:
                df[col] = 0.0
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
# 일별 추이 집계 (기존 유지)
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
                line=dict(color=COLORS["warning"], width=2.5, shape="spline", smoothing=0.8),
                marker=dict(size=5, color="#ffffff", line=dict(color=COLORS["warning"], width=2)),
                fill="tozeroy", fillcolor=hex_rgba(COLORS["warning"], 0.06),
                text=tmp["label"],
                hovertemplate="<b>%{x}</b><br>AHT: %{text}<extra></extra>"
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
                line=dict(color=COLORS["info"], width=2.5, shape="spline", smoothing=0.8),
                marker=dict(size=5, color="#ffffff", line=dict(color=COLORS["info"], width=2)),
                fill="tozeroy", fillcolor=hex_rgba(COLORS["info"], 0.06),
                text=tmp["label"],
                hovertemplate="<b>%{x}</b><br>대기: %{text}<extra></extra>"
            ))
            fig.update_layout(**base_layout(290, ""))
            st.plotly_chart(fig, use_container_width=True)
            card_close()
        _, c_mid, _ = st.columns([1, 2, 1])
        with c_mid:
            card_open("일별 평균 리드타임", "Avg lead time (접수→종료)")
            tmp = df_daily.copy()
            tmp["label"] = tmp["평균리드타임"].apply(fmt_hms)
            fig = go.Figure(go.Scatter(
                x=tmp["일자"], y=tmp["평균리드타임"],
                mode="lines+markers",
                line=dict(color=COLORS["warning"], width=2.5, shape="spline", smoothing=0.8),
                marker=dict(size=5, color="#ffffff", line=dict(color=COLORS["warning"], width=2)),
                fill="tozeroy", fillcolor=hex_rgba(COLORS["warning"], 0.06),
                text=tmp["label"],
                hovertemplate="<b>%{x}</b><br>리드타임: %{text}<extra></extra>"
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
                line=dict(color=COLORS["success"], width=2.5, shape="spline", smoothing=0.8),
                marker=dict(size=5, color="#ffffff", line=dict(color=COLORS["success"], width=2)),
                fill="tozeroy", fillcolor=hex_rgba(COLORS["success"], 0.06),
                text=tmp["in_label"],
                hovertemplate="<b>%{x}</b><br>근무내: %{text}<extra></extra>"
            ))
            fig.add_trace(go.Scatter(
                x=tmp["일자"], y=tmp["평균근무외LT"],
                mode="lines+markers", name="근무외",
                line=dict(color=COLORS["danger"], width=2.5, shape="spline", smoothing=0.8),
                marker=dict(size=5, color="#ffffff", line=dict(color=COLORS["danger"], width=2)),
                text=tmp["off_label"],
                hovertemplate="<b>%{x}</b><br>근무외: %{text}<extra></extra>"
            ))
            fig.update_layout(**base_layout(290, ""))
            st.plotly_chart(fig, use_container_width=True)
            card_close()

# ══════════════════════════════════════════════
# 기존 페이지들 (유지)
# ══════════════════════════════════════════════
def page_overview(phone, chat, board, unit, month_range, start, end,
                  phone_all=None, chat_all=None, board_all=None):
    updated = datetime.now().strftime("%Y-%m-%d %H:%M")
    s_str = start.strftime("%Y.%m.%d") if hasattr(start,"strftime") else str(start)
    e_str = end.strftime("%Y.%m.%d")   if hasattr(end,  "strftime") else str(end)

    period_days = (pd.Timestamp(end) - pd.Timestamp(start)).days + 1
    prev_end    = pd.Timestamp(start) - timedelta(days=1)
    prev_start  = prev_end - timedelta(days=period_days - 1)
    ps_str = prev_start.strftime("%Y.%m.%d")
    pe_str = prev_end.strftime("%Y.%m.%d")

    st.markdown(f"""
    <div class="dash-header">
      <div class="dash-header-left">
        <h1>📊 Contact Center Dashboard</h1>
        <span>마지막 업데이트: {updated}</span>
      </div>
      <div style="display:flex;flex-direction:column;align-items:flex-end;gap:5px;">
        <span class="dash-badge primary">📅 {s_str} ~ {e_str}</span>
        <span class="dash-badge neutral">🔄 비교: {ps_str} ~ {pe_str}</span>
      </div>
    </div>""", unsafe_allow_html=True)

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

    section_title("채널별 인입 분포 & 추이")
    c_donut, c_trend = st.columns([1,2])
    with c_donut:
        card_open("채널 분포","Channel distribution")
        fig = donut_chart(["전화","채팅","게시판"],[t_ph,t_ch,t_bo],
                          [COLORS["phone"],COLORS["chat"],COLORS["board"]],h=230)
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
            unit=unit, y_label="건수", h=310)
        st.plotly_chart(fig, use_container_width=True)
        card_close()

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
    rr_ph_df = rr_trend(phone)
    rr_ch_df = rr_trend(chat)
    rr_bo_df = rr_trend(board)
    fig2  = go.Figure()
    for nm, rr_df, c in [
        ("전화 응대율",   rr_ph_df, COLORS["phone"]),
        ("채팅 응대율",   rr_ch_df, COLORS["chat"]),
        ("게시판 응답률", rr_bo_df, COLORS["board"]),
    ]:
        if rr_df is not None and not rr_df.empty and pc in rr_df.columns:
            fig2.add_trace(go.Scatter(
                x=rr_df[pc], y=rr_df["응대율"],
                mode="lines+markers", name=nm,
                line=dict(color=c, width=2.5, shape="spline", smoothing=0.8),
                marker=dict(size=5, color="#ffffff", line=dict(color=c, width=2)),
                fill="tozeroy", fillcolor=hex_rgba(c, 0.05),
                hovertemplate="<b>%{x}</b><br>%{y:.1f}%<extra></extra>"
            ))
    lo = base_layout(280, "")
    lo["yaxis"]["ticksuffix"] = "%"
    lo["yaxis"]["range"] = [0, 110]
    fig2.update_layout(**lo)
    st.plotly_chart(fig2, use_container_width=True)
    card_close()

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
        f"<span class='dash-badge primary' style='font-size:12px;padding:4px 12px;'>"
        f"총 {len(voc):,}건</span>",
        unsafe_allow_html=True
    )
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

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

    section_title("비중 분석")
    cA, cB = st.columns(2)
    with cA:
        if "사업자명" in voc.columns:
            op_df = voc.groupby("사업자명").size().reset_index(name="건수").sort_values("건수",ascending=False).head(12)
            card_open("사업자 분포", "상위 12")
            st.plotly_chart(donut_chart(op_df["사업자명"].tolist(), op_df["건수"].tolist(), h=220), use_container_width=True)
            st.markdown(donut_legend_html(op_df["사업자명"].tolist(), op_df["건수"].tolist(), PALETTE), unsafe_allow_html=True)
            card_close()
    with cB:
        if "브랜드" in voc.columns:
            br_df = voc.groupby("브랜드").size().reset_index(name="건수").sort_values("건수",ascending=False).head(12)
            card_open("브랜드 분포", "상위 12")
            st.plotly_chart(donut_chart(br_df["브랜드"].tolist(), br_df["건수"].tolist(), h=220), use_container_width=True)
            st.markdown(donut_legend_html(br_df["브랜드"].tolist(), br_df["건수"].tolist(), PALETTE), unsafe_allow_html=True)
            card_close()

    if "대분류" in voc.columns:
        card_open("대분류 × 채널", "채널별 문의 유형 구성")
        cat1_df = voc.groupby(["채널","대분류"]).size().reset_index(name="건수")
        fig = px.bar(cat1_df, x="대분류", y="건수", color="채널", barmode="group",
                     color_discrete_map={"전화":COLORS["phone"],"채팅":COLORS["chat"],"게시판":COLORS["board"]})
        lo = base_layout(300,"")
        fig.update_layout(**lo)
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(fig, use_container_width=True)
        card_close()

    c1, c2 = st.columns(2)
    with c1:
        if "중분류" in voc.columns:
            card_open("중분류 TOP 20")
            mid_df = voc.groupby("중분류").size().reset_index(name="건수").sort_values("건수",ascending=False).head(20)
            fig = px.bar(mid_df, x="건수", y="중분류", orientation="h",
                         color="건수",
                         color_continuous_scale=["#e0e7ff", "#6366f1", "#3730a3"])
            fig.update_layout(**base_layout(420,""))
            fig.update_traces(marker_line_width=0)
            fig.update_coloraxes(showscale=False)
            st.plotly_chart(fig, use_container_width=True)
            card_close()
    with c2:
        if "소분류" in voc.columns:
            card_open("소분류 TOP 20")
            sub_df = voc.groupby("소분류").size().reset_index(name="건수").sort_values("건수",ascending=False).head(20)
            fig = px.bar(sub_df, x="건수", y="소분류", orientation="h",
                         color="건수",
                         color_continuous_scale=["#dcfce7", "#22c55e", "#15803d"])
            fig.update_layout(**base_layout(420,""))
            fig.update_traces(marker_line_width=0)
            fig.update_coloraxes(showscale=False)
            st.plotly_chart(fig, use_container_width=True)
            card_close()

    # ── D1: 반복 문의 근사 ─────────────────────────────
    section_title("D1. 반복 문의 근사 (Repeat Contact)")
    page_voc_d1(voc, unit)

    # ── D2: 대분류 × 중분류 × 처리시간 히트맵 ──────────
    section_title("D2. VOC 유형 × 처리시간 히트맵")
    page_voc_d2(phone, chat, board)

    # ── D3: 신규 / 급증 VOC 유형 탐지 ──────────────────
    section_title("D3. 신규 & 급증 VOC 탐지")
    page_voc_d3(voc)


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

    card_open("사업자별 채널 인입", "채널별 인입 건수 비교")
    fig = px.bar(all_op, x="사업자명", y="인입", color="채널", barmode="stack",
                 color_discrete_map={"전화":COLORS["phone"],"채팅":COLORS["chat"],"게시판":COLORS["board"]})
    fig.update_layout(**base_layout(360,""))
    fig.update_traces(marker_line_width=0)
    st.plotly_chart(fig, use_container_width=True)
    card_close()

    card_open("사업자별 채널 응대율", "채널별 응대율 비교 (%)")
    fig2 = px.bar(all_op, x="사업자명", y="응대율", color="채널", barmode="group",
                  color_discrete_map={"전화":COLORS["phone"],"채팅":COLORS["chat"],"게시판":COLORS["board"]})
    lo = base_layout(320,"")
    lo["yaxis"]["ticksuffix"] = "%"
    lo["yaxis"]["range"] = [0, 110]
    fig2.update_layout(**lo)
    fig2.update_traces(marker_line_width=0)
    st.plotly_chart(fig2, use_container_width=True)
    card_close()

    card_open("사업자별 요약 테이블")
    try:
        pivot = all_op.pivot_table(index="사업자명", columns="채널",
                                   values=["인입","응대율"], aggfunc="first")
        st.dataframe(pivot, use_container_width=True)
        download_csv_button(all_op, "operator_summary.csv")
    except:
        st.dataframe(all_op, use_container_width=True)
    card_close()

def page_phone(phone, unit, month_range, start, end):
    if phone.empty:
        st.info("전화 데이터가 없습니다."); return

    resp = phone[phone["응대여부"]=="응대"]
    total = len(phone)
    rc    = len(resp)
    rr    = rc / total * 100 if total else 0

    def safe_mean(series):
        try:
            return pd.to_numeric(series, errors="coerce").mean() or 0.0
        except:
            return 0.0

    aw  = safe_mean(resp["대기시간(초)"])  if not resp.empty else 0
    att = safe_mean(resp["통화시간(초)"])  if not resp.empty else 0
    acw = safe_mean(resp["ACW시간(초)"])   if not resp.empty else 0
    aht = att + acw

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    with c1: st.markdown(kpi_card("전체 인입",  fmt_num(total), unit="건"),           unsafe_allow_html=True)
    with c2: st.markdown(kpi_card("응대건수",   fmt_num(rc),    unit="건", accent="green"),  unsafe_allow_html=True)
    with c3: st.markdown(kpi_card("응대율",     fmt_pct(rr),    accent="blue"),        unsafe_allow_html=True)
    with c4: st.markdown(kpi_card("평균 ATT",   fmt_hms(att),   accent="blue"),        unsafe_allow_html=True)
    with c5: st.markdown(kpi_card("평균 ACW",   fmt_hms(acw),   accent="orange"),      unsafe_allow_html=True)
    with c6: st.markdown(kpi_card("평균 AHT",   fmt_hms(aht),   accent="green"),       unsafe_allow_html=True)

    render_daily_trends_block("phone", daily_trend_phone(phone))

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
        card_open("응대 현황", "Responded vs Missed")
        fig = donut_chart(["응대","미응대"],[rc, total-rc],
                          [COLORS["success"],COLORS["danger"]], h=250)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(
            donut_legend_html(["응대","미응대"],[rc,total-rc],
                              [COLORS["success"],COLORS["danger"]]),
            unsafe_allow_html=True
        )
        card_close()

    section_title("시간대별 인입 / 응대 현황")
    min_unit = st.radio("시간 단위", [5, 10, 30, 60], index=3, horizontal=True,
                        format_func=lambda x: f"{x}분", key="phone_min_unit")

    df_time = phone.copy()
    df_time = df_time[df_time["인입시각"].notna()].copy()

    if min_unit == 60:
        df_time["시간대"] = df_time["인입시각"].dt.hour
        x_label = "시간대(시)"
    else:
        df_time["시간대"] = (
            df_time["인입시각"].dt.hour * 60 + df_time["인입시각"].dt.minute
        ) // min_unit * min_unit
        df_time["시간대"] = df_time["시간대"].apply(
            lambda x: f"{x//60:02d}:{x%60:02d}"
        )
        x_label = f"시간대({min_unit}분 단위)"

    hourly = df_time.groupby("시간대").agg(
        인입=("시간대", "count"),
        응대=("응대여부", lambda x: (x=="응대").sum()),
    ).reset_index()
    hourly["미응대"] = hourly["인입"] - hourly["응대"]
    hourly["응대율"] = (hourly["응대"] / hourly["인입"] * 100).round(1)

    card_open(f"시간대별 인입/응대 + 응대율 ({min_unit}분 단위)")
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=hourly["시간대"], y=hourly["응대"],
        name="응대", marker_color=COLORS["phone"],
        marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>응대: %{y:,}<extra></extra>"
    ))
    fig3.add_trace(go.Bar(
        x=hourly["시간대"], y=hourly["미응대"],
        name="미응대", marker_color=hex_rgba(COLORS["danger"], 0.6),
        marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>미응대: %{y:,}<extra></extra>"
    ))
    fig3.add_trace(go.Scatter(
        x=hourly["시간대"], y=hourly["응대율"], name="응대율(%)",
        yaxis="y2", mode="lines+markers",
        line=dict(color=COLORS["warning"], width=2.5, shape="spline", smoothing=0.8),
        marker=dict(size=5, color="#ffffff", line=dict(color=COLORS["warning"], width=2)),
        hovertemplate="<b>%{x}</b><br>응대율: %{y:.1f}%<extra></extra>"
    ))
    fig3.update_layout(
        **base_layout(330,""), barmode="stack",
        yaxis2=dict(
            overlaying="y", side="right", showgrid=False,
            ticksuffix="%", range=[0,110],
            tickfont=dict(size=10, color="#94a3b8"),
        )
    )
    st.plotly_chart(fig3, use_container_width=True)
    card_close()

    if not resp.empty:
        section_title("AHT 구성 분석 (ATT + ACW)")
        aht_df = resp.groupby(pc).agg(
            ATT=("통화시간(초)", "mean"),
            ACW=("ACW시간(초)", "mean"),
        ).reset_index()
        aht_df["AHT"] = aht_df["ATT"] + aht_df["ACW"]
        c1, c2 = st.columns([2, 1])
        with c1:
            card_open("기간별 평균 AHT 구성", "ATT(통화시간) + ACW(후처리) = AHT")
            fig4 = go.Figure()
            fig4.add_trace(go.Bar(
                x=aht_df[pc], y=aht_df["ATT"],
                name="ATT (통화시간)",
                marker_color=COLORS["primary"], marker_line_width=0,
                hovertemplate="<b>%{x}</b><br>ATT: %{y:.0f}초<extra></extra>"
            ))
            fig4.add_trace(go.Bar(
                x=aht_df[pc], y=aht_df["ACW"],
                name="ACW (후처리)",
                marker_color=COLORS["warning"], marker_line_width=0,
                hovertemplate="<b>%{x}</b><br>ACW: %{y:.0f}초<extra></extra>"
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

    if "대분류" in phone.columns:
        section_title("문의 유형 분석")
        cat_df = phone.groupby("대분류").size().reset_index(name="건수").sort_values("건수",ascending=False)
        c1, c2 = st.columns([1,2])
        with c1:
            card_open("대분류 분포")
            st.plotly_chart(donut_chart(cat_df["대분류"].tolist(), cat_df["건수"].tolist(), h=220), use_container_width=True)
            st.markdown(donut_legend_html(cat_df["대분류"].tolist(), cat_df["건수"].tolist(), PALETTE), unsafe_allow_html=True)
            card_close()
        with c2:
            card_open("대분류별 인입 건수")
            fig5 = px.bar(cat_df, x="건수", y="대분류", orientation="h",
                          color="건수",
                          color_continuous_scale=["#e0e7ff", "#6366f1", "#3730a3"])
            fig5.update_layout(**base_layout(300,""))
            fig5.update_traces(marker_line_width=0)
            fig5.update_coloraxes(showscale=False)
            st.plotly_chart(fig5, use_container_width=True)
            card_close()

    section_title("인입 히트맵 (날짜 × 시간대)")
    if "인입시간대" in phone.columns and "일자" in phone.columns:
        tmp = phone.copy()
        tmp["일자str"] = pd.to_datetime(tmp["일자"]).dt.strftime("%m-%d")
        pivot = tmp.pivot_table(index="일자str", columns="인입시간대",
                                values="응대여부", aggfunc="count", fill_value=0)
        card_open("날짜 × 시간대 인입 히트맵", "셀 밝기 = 인입 건수")
        st.plotly_chart(heatmap_chart(pivot, h=340), use_container_width=True)
        card_close()

def page_phone_agent(phone, unit, month_range):
    if phone.empty:
        st.info("전화 데이터가 없습니다.")
        return
    phone = phone[~phone["상담사명"].isin(EXCLUDE_AGENTS)].copy()
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

    card_open("상담사별 성과 테이블", "ATT=통화시간 / ACW=후처리시간 / AHT=ATT+ACW")
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
    download_csv_button(ag, "phone_agent_performance.csv")
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
            card_open("팀별 평균 AHT (ATT + ACW 구성)")
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=tm["팀명"], y=tm["평균ATT"],
                name="ATT", marker_color=COLORS["primary"], marker_line_width=0
            ))
            fig.add_trace(go.Bar(
                x=tm["팀명"], y=tm["평균ACW"],
                name="ACW", marker_color=COLORS["warning"], marker_line_width=0
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
            card_open("근속그룹별 평균 AHT (ATT + ACW 구성)")
            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                x=tg["근속그룹"], y=tg["평균ATT"],
                name="ATT", marker_color=COLORS["primary"], marker_line_width=0
            ))
            fig2.add_trace(go.Bar(
                x=tg["근속그룹"], y=tg["평균ACW"],
                name="ACW", marker_color=COLORS["warning"], marker_line_width=0
            ))
            fig2.update_layout(barmode="stack", **base_layout(300, ""))
            st.plotly_chart(fig2, use_container_width=True)
            card_close()

    section_title("상담사별 AHT 분포 (상위 20)")
    top20 = ag.head(20)
    card_open("상담사별 평균 AHT (ATT + ACW 스택)")
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=top20["상담사명"], y=top20["평균ATT"],
        name="ATT (통화시간)", marker_color=COLORS["primary"], marker_line_width=0
    ))
    fig3.add_trace(go.Bar(
        x=top20["상담사명"], y=top20["평균ACW"],
        name="ACW (후처리)", marker_color=COLORS["warning"], marker_line_width=0
    ))
    fig3.update_layout(barmode="stack", **base_layout(380, ""))
    st.plotly_chart(fig3, use_container_width=True)
    card_close()

def page_chat(chat, unit, month_range, start, end):
    if chat.empty:
        st.info("채팅 데이터가 없습니다."); return

    resp     = chat[chat["응대여부"]=="응대"]
    total    = len(chat)
    rc       = len(resp)
    rr       = rc / total * 100 if total else 0
    avg_wait = resp["응답시간(초)"].mean() if not resp.empty else 0
    avg_lt   = resp["리드타임(초)"].mean()  if not resp.empty else 0

    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: st.markdown(kpi_card("전체 인입",     fmt_num(total), unit="건"), unsafe_allow_html=True)
    with c2: st.markdown(kpi_card("응대건수",      fmt_num(rc),    unit="건", accent="green"), unsafe_allow_html=True)
    with c3: st.markdown(kpi_card("응대율",        fmt_pct(rr),    accent="blue"), unsafe_allow_html=True)
    with c4: st.markdown(kpi_card("평균 대기시간", fmt_hms(avg_wait), accent="orange"), unsafe_allow_html=True)
    with c5: st.markdown(kpi_card("평균 리드타임", fmt_hms(avg_lt),   accent="blue"), unsafe_allow_html=True)

    render_daily_trends_block("chat", daily_trend_chat(chat))

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
        card_open("응대 현황", "Responded vs Missed")
        fig = donut_chart(["응대","미응대"],[rc,total-rc],
                          [COLORS["success"],COLORS["danger"]], h=250)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(
            donut_legend_html(["응대","미응대"],[rc,total-rc],
                              [COLORS["success"],COLORS["danger"]]),
            unsafe_allow_html=True
        )
        card_close()

    section_title("시간대별 인입 / 응대 현황")
    hourly = chat.groupby("인입시간대").agg(
        인입=("인입시간대","count"),
        응대=("응대여부", lambda x: (x=="응대").sum()),
    ).reset_index()
    hourly["미응대"] = hourly["인입"] - hourly["응대"]
    hourly["응대율"] = (hourly["응대"] / hourly["인입"] * 100).round(1)

    card_open("시간대별 인입/응대 + 응대율")
    fig_h = go.Figure()
    fig_h.add_trace(go.Bar(
        x=hourly["인입시간대"], y=hourly["응대"],
        name="응대", marker_color=COLORS["chat"], marker_line_width=0
    ))
    fig_h.add_trace(go.Bar(
        x=hourly["인입시간대"], y=hourly["미응대"],
        name="미응대", marker_color=hex_rgba(COLORS["danger"], 0.6), marker_line_width=0
    ))
    fig_h.add_trace(go.Scatter(
        x=hourly["인입시간대"], y=hourly["응대율"], name="응대율(%)",
        yaxis="y2", mode="lines+markers",
        line=dict(color=COLORS["warning"], width=2.5, shape="spline", smoothing=0.8),
        marker=dict(size=5, color="#ffffff", line=dict(color=COLORS["warning"], width=2))
    ))
    fig_h.update_layout(
        **base_layout(330,""), barmode="stack",
        yaxis2=dict(
            overlaying="y", side="right", showgrid=False,
            ticksuffix="%", range=[0,110],
            tickfont=dict(size=10, color="#94a3b8")
        )
    )
    st.plotly_chart(fig_h, use_container_width=True)
    card_close()

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
                          color="평균대기",
                          color_continuous_scale=["#d1fae5","#22c55e","#15803d"])
            fig3.update_layout(**base_layout(300,""))
            fig3.update_traces(marker_line_width=0)
            fig3.update_coloraxes(showscale=False)
            st.plotly_chart(fig3, use_container_width=True)
            card_close()
        with c2:
            card_open("대분류별 평균 리드타임(초)")
            fig4 = px.bar(cat_df, x="대분류", y="평균리드타임",
                          color="평균리드타임",
                          color_continuous_scale=["#fef3c7","#f59e0b","#b45309"])
            fig4.update_layout(**base_layout(300,""))
            fig4.update_traces(marker_line_width=0)
            fig4.update_coloraxes(showscale=False)
            st.plotly_chart(fig4, use_container_width=True)
            card_close()

    if "플랫폼" in chat.columns:
        section_title("플랫폼별 분포")
        plat = chat.groupby("플랫폼").size().reset_index(name="건수").sort_values("건수",ascending=False).head(12)
        c1, c2 = st.columns([1,2])
        with c1:
            card_open("플랫폼 분포", "상위 12")
            st.plotly_chart(donut_chart(plat["플랫폼"].tolist(), plat["건수"].tolist(), h=220), use_container_width=True)
            st.markdown(donut_legend_html(plat["플랫폼"].tolist(), plat["건수"].tolist(), PALETTE), unsafe_allow_html=True)
            card_close()
        with c2:
            card_open("플랫폼별 건수")
            fig5 = px.bar(plat, x="플랫폼", y="건수",
                          color="건수",
                          color_continuous_scale=["#d1fae5","#22c55e","#15803d"])
            fig5.update_layout(**base_layout(260,""))
            fig5.update_traces(marker_line_width=0)
            fig5.update_coloraxes(showscale=False)
            st.plotly_chart(fig5, use_container_width=True)
            card_close()

def page_chat_agent(chat, unit, month_range):
    if chat.empty:
        st.info("채팅 데이터가 없습니다."); return
    resp = chat[chat["응대여부"]=="응대"]
    chat = chat[~chat["상담사명"].isin(EXCLUDE_AGENTS)].copy()
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

    card_open("상담사별 성과 테이블", "대기시간 = 접수 → 첫멘트 응답 소요시간")
    st.dataframe(
        ag[["상담사명","응대수","평균대기시간_표시","평균리드타임_표시"]].rename(columns={
            "평균대기시간_표시":"평균 대기시간",
            "평균리드타임_표시":"평균 리드타임",
        }),
        use_container_width=True, height=400
    )
    download_csv_button(ag, "chat_agent_performance.csv")
    card_close()

    c1, c2 = st.columns(2)
    with c1:
        if "팀명" in resp.columns:
            section_title("팀별 평균 대기시간")
            tm = resp.groupby("팀명").agg(
                응대수=("팀명","count"), 평균대기=("응답시간(초)","mean")
            ).round(1).reset_index()
            card_open("팀별 평균 대기시간(초)")
            fig = px.bar(tm, x="팀명", y="평균대기",
                         color="평균대기",
                         color_continuous_scale=["#d1fae5","#22c55e","#15803d"])
            fig.update_layout(**base_layout(290,""))
            fig.update_traces(marker_line_width=0)
            fig.update_coloraxes(showscale=False)
            st.plotly_chart(fig, use_container_width=True)
            card_close()
    with c2:
        if "근속그룹" in resp.columns:
            section_title("근속그룹별 평균 대기시간")
            tg = resp.groupby("근속그룹").agg(
                응대수=("근속그룹","count"), 평균대기=("응답시간(초)","mean")
            ).round(1).reset_index()
            card_open("근속그룹별 평균 대기시간(초)")
            fig2 = px.bar(tg, x="근속그룹", y="평균대기",
                          color="평균대기",
                          color_continuous_scale=["#e0e7ff","#6366f1","#3730a3"])
            fig2.update_layout(**base_layout(290,""))
            fig2.update_traces(marker_line_width=0)
            fig2.update_coloraxes(showscale=False)
            st.plotly_chart(fig2, use_container_width=True)
            card_close()

    section_title("상담사별 평균 대기시간 분포 (상위 20)")
    top20 = ag.head(20)
    card_open("상담사별 평균 대기시간(초)")
    fig3 = px.bar(
        top20, x="평균대기시간", y="상담사명", orientation="h",
        color="평균대기시간",
        color_continuous_scale=["#dcfce7","#22c55e","#15803d"]
    )
    fig3.update_layout(**base_layout(420,""))
    fig3.update_traces(marker_line_width=0)
    fig3.update_coloraxes(showscale=False)
    st.plotly_chart(fig3, use_container_width=True)
    card_close()

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

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    with c1: st.markdown(kpi_card("전체 티켓",      fmt_num(total),    unit="건"),              unsafe_allow_html=True)
    with c2: st.markdown(kpi_card("응답완료",        fmt_num(rc),       unit="건", accent="green"),  unsafe_allow_html=True)
    with c3: st.markdown(kpi_card("응답률",          fmt_pct(rr),       accent="blue"),          unsafe_allow_html=True)
    with c4: st.markdown(kpi_card("평균 근무내 LT",  fmt_hms(avg_in),   accent="green"),         unsafe_allow_html=True)
    with c5: st.markdown(kpi_card("평균 근무외 LT",  fmt_hms(avg_off),  accent="red"),           unsafe_allow_html=True)
    with c6: st.markdown(kpi_card("평균 전체 LT",    fmt_hms(avg_total),accent="orange"),        unsafe_allow_html=True)

    render_daily_trends_block("board", daily_trend_board(board))

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
        card_open("응답 현황", "Responded vs Pending")
        fig = donut_chart(["응답","미응답"],[rc,total-rc],
                          [COLORS["success"],COLORS["danger"]], h=250)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(
            donut_legend_html(["응답","미응답"],[rc,total-rc],
                              [COLORS["success"],COLORS["danger"]]),
            unsafe_allow_html=True
        )
        card_close()

    if not resp.empty:
        section_title("근무내/외 리드타임 기간별 추이")
        lt_grp = resp.groupby(pc).agg(
            근무내LT=("근무내리드타임(초)","mean"),
            근무외LT=("근무외리드타임(초)","mean"),
        ).reset_index()
        card_open("기간별 평균 리드타임", "근무내(영업시간) vs 근무외(영업시간 외)")
        fig_lt = go.Figure()
        fig_lt.add_trace(go.Bar(
            x=lt_grp[pc], y=lt_grp["근무내LT"],
            name="근무내", marker_color=COLORS["success"], marker_line_width=0,
            hovertemplate="<b>%{x}</b><br>근무내: %{y:.0f}초<extra></extra>"
        ))
        fig_lt.add_trace(go.Bar(
            x=lt_grp[pc], y=lt_grp["근무외LT"],
            name="근무외", marker_color=COLORS["danger"], marker_line_width=0,
            hovertemplate="<b>%{x}</b><br>근무외: %{y:.0f}초<extra></extra>"
        ))
        fig_lt.update_layout(barmode="stack", **base_layout(300,""))
        st.plotly_chart(fig_lt, use_container_width=True)
        card_close()

    section_title("시간대별 접수 / 응답 현황")
    hourly = board.groupby("인입시간대").agg(
        접수=("인입시간대","count"),
        응답=("응대여부", lambda x: (x=="응대").sum()),
    ).reset_index()
    hourly["미응답"] = hourly["접수"] - hourly["응답"]
    hourly["응답률"] = (hourly["응답"] / hourly["접수"] * 100).round(1)

    card_open("시간대별 접수/응답 + 응답률")
    fig_h = go.Figure()
    fig_h.add_trace(go.Bar(
        x=hourly["인입시간대"], y=hourly["응답"],
        name="응답", marker_color=COLORS["board"], marker_line_width=0,
        hovertemplate="<b>%{x}시</b><br>응답: %{y:,}<extra></extra>"
    ))
    fig_h.add_trace(go.Bar(
        x=hourly["인입시간대"], y=hourly["미응답"],
        name="미응답", marker_color=hex_rgba(COLORS["danger"], 0.6), marker_line_width=0,
        hovertemplate="<b>%{x}시</b><br>미응답: %{y:,}<extra></extra>"
    ))
    fig_h.add_trace(go.Scatter(
        x=hourly["인입시간대"], y=hourly["응답률"], name="응답률(%)",
        yaxis="y2", mode="lines+markers",
        line=dict(color=COLORS["warning"], width=2.5, shape="spline", smoothing=0.8),
        marker=dict(size=5, color="#ffffff", line=dict(color=COLORS["warning"], width=2)),
        hovertemplate="<b>%{x}시</b><br>응답률: %{y:.1f}%<extra></extra>"
    ))
    fig_h.update_layout(
        **base_layout(330,""), barmode="stack",
        yaxis2=dict(
            overlaying="y", side="right", showgrid=False,
            ticksuffix="%", range=[0,110],
            tickfont=dict(size=10, color="#94a3b8")
        )
    )
    st.plotly_chart(fig_h, use_container_width=True)
    card_close()

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
            st.plotly_chart(
                donut_chart(cat_df["대분류"].tolist(), cat_df["건수"].tolist(), h=220),
                use_container_width=True
            )
            st.markdown(
                donut_legend_html(cat_df["대분류"].tolist(), cat_df["건수"].tolist(), PALETTE),
                unsafe_allow_html=True
            )
            card_close()
        with c2:
            card_open("대분류별 건수 / 응답률")
            fig3 = go.Figure()
            fig3.add_trace(go.Bar(
                x=cat_df["대분류"], y=cat_df["건수"],
                name="건수", marker_color=COLORS["board"], marker_line_width=0,
                hovertemplate="<b>%{x}</b><br>건수: %{y:,}<extra></extra>"
            ))
            fig3.add_trace(go.Scatter(
                x=cat_df["대분류"], y=cat_df["응답률"], name="응답률(%)",
                yaxis="y2", mode="lines+markers",
                line=dict(color=COLORS["success"], width=2.5, shape="spline", smoothing=0.8),
                marker=dict(size=6, color="#ffffff", line=dict(color=COLORS["success"], width=2)),
                hovertemplate="<b>%{x}</b><br>응답률: %{y:.1f}%<extra></extra>"
            ))
            fig3.update_layout(
                **base_layout(300,""),
                yaxis2=dict(
                    overlaying="y", side="right", showgrid=False,
                    ticksuffix="%", range=[0,110],
                    tickfont=dict(size=10, color="#94a3b8")
                )
            )
            st.plotly_chart(fig3, use_container_width=True)
            card_close()

    if "플랫폼" in board.columns:
        section_title("플랫폼별 분포")
        plat = board.groupby("플랫폼").size().reset_index(name="건수").sort_values("건수",ascending=False).head(12)
        c1, c2 = st.columns([1,2])
        with c1:
            card_open("플랫폼 분포", "상위 12")
            st.plotly_chart(
                donut_chart(plat["플랫폼"].tolist(), plat["건수"].tolist(), h=220),
                use_container_width=True
            )
            st.markdown(
                donut_legend_html(plat["플랫폼"].tolist(), plat["건수"].tolist(), PALETTE),
                unsafe_allow_html=True
            )
            card_close()
        with c2:
            card_open("플랫폼별 건수")
            fig4 = px.bar(plat, x="플랫폼", y="건수",
                          color="건수",
                          color_continuous_scale=["#fef3c7","#f59e0b","#b45309"])
            fig4.update_layout(**base_layout(260,""))
            fig4.update_traces(marker_line_width=0)
            fig4.update_coloraxes(showscale=False)
            st.plotly_chart(fig4, use_container_width=True)
            card_close()

    # ── E1: 근무외 비율 추이 ────────────────────────────
    section_title("E1. 근무외 처리 비율 추이")
    page_board_e1(board, unit)

    # ── E2: 요일/시간대별 리드타임 패턴 ─────────────────
    section_title("E2. 접수 요일 × 시간대별 리드타임 패턴")
    page_board_e2(board)


def page_board_agent(board, unit, month_range):
    if board.empty:
        st.info("게시판 데이터가 없습니다."); return
    board = board[~board["상담사명"].isin(EXCLUDE_AGENTS)].copy()
    resp  = board[board["응대여부"]=="응대"]
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
            "평균전체LT_표시": "평균 전체 LT",
        }),
        use_container_width=True, height=400
    )
    download_csv_button(ag, "board_agent_performance.csv")
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
            fig.add_trace(go.Bar(
                x=tm["팀명"], y=tm["근무내LT"],
                name="근무내", marker_color=COLORS["success"], marker_line_width=0
            ))
            fig.add_trace(go.Bar(
                x=tm["팀명"], y=tm["근무외LT"],
                name="근무외", marker_color=COLORS["danger"], marker_line_width=0
            ))
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
            fig2.add_trace(go.Bar(
                x=tg["근속그룹"], y=tg["근무내LT"],
                name="근무내", marker_color=COLORS["success"], marker_line_width=0
            ))
            fig2.add_trace(go.Bar(
                x=tg["근속그룹"], y=tg["근무외LT"],
                name="근무외", marker_color=COLORS["danger"], marker_line_width=0
            ))
            fig2.update_layout(barmode="group", **base_layout(290,""))
            st.plotly_chart(fig2, use_container_width=True)
            card_close()

    section_title("상담사별 LT 분포 (상위 20)")
    top20 = ag.head(20)
    card_open("상담사별 근무내/외 LT 비교 (초)")
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=top20["평균근무내LT"], y=top20["상담사명"],
        orientation="h", name="근무내",
        marker_color=COLORS["success"], marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>근무내: %{x:.0f}초<extra></extra>"
    ))
    fig3.add_trace(go.Bar(
        x=top20["평균근무외LT"], y=top20["상담사명"],
        orientation="h", name="근무외",
        marker_color=COLORS["danger"], marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>근무외: %{x:.0f}초<extra></extra>"
    ))
    fig3.update_layout(barmode="stack", **base_layout(440,""))
    st.plotly_chart(fig3, use_container_width=True)
    card_close()


def page_agent_total(phone, chat, board):
    section_title("상담사 종합 성과")
    if not phone.empty: phone = phone[~phone["상담사명"].isin(EXCLUDE_AGENTS)].copy()
    if not chat.empty:  chat  = chat[~chat["상담사명"].isin(EXCLUDE_AGENTS)].copy()
    if not board.empty: board = board[~board["상담사명"].isin(EXCLUDE_AGENTS)].copy()

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
            "상담사명":          name,
            "전화 응대":         len(ph),
            "채팅 응대":         len(ch),
            "게시판 응답":       len(bo),
            "전화 ATT":          fmt_hms(ph["통화시간(초)"].mean())  if not ph.empty else "0:00:00",
            "전화 ACW":          fmt_hms(ph["ACW시간(초)"].mean())   if not ph.empty else "0:00:00",
            "전화 AHT":          fmt_hms(ph["통화시간(초)"].mean() + ph["ACW시간(초)"].mean()) if not ph.empty else "0:00:00",
            "채팅 대기":         fmt_hms(ch["응답시간(초)"].mean())  if (not ch.empty and "응답시간(초)" in ch.columns) else "0:00:00",
            "채팅 리드타임":     fmt_hms(ch["리드타임(초)"].mean())  if not ch.empty else "0:00:00",
            "게시판 근무내 LT":  fmt_hms(bo["근무내리드타임(초)"].mean()) if (not bo.empty and "근무내리드타임(초)" in bo.columns) else "0:00:00",
            "게시판 근무외 LT":  fmt_hms(bo["근무외리드타임(초)"].mean()) if (not bo.empty and "근무외리드타임(초)" in bo.columns) else "0:00:00",
        })

    df_ag = pd.DataFrame(rows).sort_values("전화 응대", ascending=False)

    card_open("상담사 종합 테이블", "전체 채널 성과 통합")
    st.dataframe(df_ag, use_container_width=True, height=500)
    download_csv_button(df_ag, "agent_total_performance.csv")
    card_close()

    section_title("상담사별 채널 응대 분포 (상위 15)")
    top15 = df_ag.head(15)
    card_open("Top 15 채널별 응대 건수")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="전화", x=top15["상담사명"], y=top15["전화 응대"],
        marker_color=COLORS["phone"], marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>전화: %{y:,}<extra></extra>"
    ))
    fig.add_trace(go.Bar(
        name="채팅", x=top15["상담사명"], y=top15["채팅 응대"],
        marker_color=COLORS["chat"], marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>채팅: %{y:,}<extra></extra>"
    ))
    fig.add_trace(go.Bar(
        name="게시판", x=top15["상담사명"], y=top15["게시판 응답"],
        marker_color=COLORS["board"], marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>게시판: %{y:,}<extra></extra>"
    ))
    fig.update_layout(barmode="stack", **base_layout(380,""))
    st.plotly_chart(fig, use_container_width=True)
    card_close()


# ══════════════════════════════════════════════
# ★ 신규 페이지 A1: SLA 위반 분석
# ══════════════════════════════════════════════
def page_sla_breach(phone, chat, board, unit):
    section_title("A1. SLA 위반 지표")

    # ── 1. 슬라이더 UI ──────────────────────────────
    with st.expander("⚙️ SLA 기준값 조정", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            phone_sla_on = st.checkbox("전화 SLA 적용", value=False, key="sla_ph_on")
            sla_phone_val = st.number_input("전화 대기시간 기준(초)", min_value=5,
                                            max_value=300, value=20, step=5,
                                            key="sla_ph_val", disabled=not phone_sla_on)
        with c2:
            sla_chat_val = st.slider("채팅 응답시간 기준(초)", min_value=30,
                                     max_value=300, value=120, step=10, key="sla_ch_val")
        with c3:
            sla_board_in_h = st.slider("근무내 기준(시간)", min_value=1,
                                       max_value=12, value=3, step=1, key="sla_bo_in")
        with c4:
            sla_board_off_h = st.slider("근무외 기준(시간)", min_value=1,
                                        max_value=24, value=7, step=1, key="sla_bo_off")

    # ── 2. 변수 확정 (반드시 슬라이더 직후, KPI 계산 전) ──
    _sla_phone     = sla_phone_val if phone_sla_on else None
    _sla_chat      = sla_chat_val
    _sla_board_in  = sla_board_in_h * 3600
    _sla_board_off = sla_board_off_h * 3600

    # ── 3. 데이터 필터 ───────────────────────────────
    ph_resp = phone[phone["응대여부"]=="응대"] if not phone.empty else pd.DataFrame()
    ch_resp = chat[chat["응대여부"]=="응대"]   if not chat.empty  else pd.DataFrame()
    bo_resp = board[board["응대여부"]=="응대"] if not board.empty else pd.DataFrame()

    # ── 4. KPI 계산 ──────────────────────────────────
    # 전화: 사용자 설정 SLA 기준
    ph_breach_n = int((ph_resp["대기시간(초)"] > _sla_phone).sum()) if (not ph_resp.empty and _sla_phone) else 0
    ph_breach_r = ph_breach_n / len(ph_resp) * 100 if len(ph_resp) > 0 else 0.0

    # 채팅: 응답시간 기준
    ch_breach_n = int((ch_resp["응답시간(초)"] > _sla_chat).sum()) if not ch_resp.empty else 0
    ch_breach_r = ch_breach_n / len(ch_resp) * 100 if len(ch_resp) > 0 else 0.0

    # 게시판: 근무내/근무외 기준
    if not bo_resp.empty:
        bo_breach_in_n  = int((bo_resp["근무내리드타임(초)"] > _sla_board_in).sum())
        bo_breach_off_n = int((bo_resp["근무외리드타임(초)"] > _sla_board_off).sum())
        bo_breach_n = bo_breach_in_n + bo_breach_off_n
        bo_breach_r = bo_breach_n / len(bo_resp) * 100
    else:
        bo_breach_n = 0
        bo_breach_r = 0.0

    # ── KPI 카드 ─────────────────────────────────
    c1,c2,c3,c4,c5,c6 = st.columns(6)
    with c1: st.markdown(kpi_card("전화 SLA위반",   fmt_num(ph_breach_n), unit="건", accent="red"),    unsafe_allow_html=True)
    with c2: st.markdown(kpi_card("전화 위반율",     fmt_pct(ph_breach_r), accent="red",   reverse=True), unsafe_allow_html=True)
    with c3: st.markdown(kpi_card("채팅 SLA위반",   fmt_num(ch_breach_n), unit="건", accent="orange"), unsafe_allow_html=True)
    with c4: st.markdown(kpi_card("채팅 위반율",     fmt_pct(ch_breach_r), accent="orange",reverse=True), unsafe_allow_html=True)
    with c5: st.markdown(kpi_card("게시판 SLA위반", fmt_num(bo_breach_n), unit="건", accent="orange"), unsafe_allow_html=True)
    with c6: st.markdown(kpi_card("게시판 위반율",   fmt_pct(bo_breach_r), accent="orange",reverse=True), unsafe_allow_html=True)

    st.markdown(f"""
    <div class="alert-card info">
      <span class="alert-icon">ℹ️</span>
      <span>SLA 기준: 전화 대기 &gt; <b>{SLA_PHONE_WAIT}초</b> &nbsp;|&nbsp;
      채팅 응답 &gt; <b>{SLA_CHAT_WAIT}초</b> &nbsp;|&nbsp;
      게시판 전체 LT &gt; <b>24시간</b></span>
    </div>""", unsafe_allow_html=True)

    # ── 일별 SLA 위반 추이 스파크라인 ─────────────
    section_title("SLA 위반 일별 추이")

    def daily_breach(df, time_col, threshold, label):
        if df.empty or time_col not in df.columns:
            return pd.DataFrame(columns=["일자", label])
        tmp = df.copy()
        tmp["일자"] = pd.to_datetime(tmp["일자"], errors="coerce").dt.date
        tmp["위반"] = tmp[time_col] > threshold
        out = tmp.groupby("일자")["위반"].sum().reset_index(name=label)
        out["일자"] = pd.to_datetime(out["일자"])
        return out

    ph_daily = daily_breach(ph_resp, "대기시간(초)", _sla_phone, "전화위반") if _sla_phone else pd.DataFrame()
    ch_daily = daily_breach(ch_resp, "응답시간(초)", _sla_chat,  "채팅위반")
    bo_daily = daily_breach(bo_resp, "리드타임(초)", _sla_board_in + _sla_board_off, "게시판위반")

    c1, c2, c3 = st.columns(3)
    with c1:
        card_open(f"전화 SLA 위반 추이 (>{SLA_PHONE_WAIT}초)")
        if not ph_daily.empty:
            fig = go.Figure(go.Scatter(
                x=ph_daily["일자"], y=ph_daily["전화위반"],
                mode="lines+markers",
                line=dict(color=COLORS["danger"], width=2.5, shape="spline", smoothing=0.8),
                marker=dict(size=5, color="#fff", line=dict(color=COLORS["danger"], width=2)),
                fill="tozeroy", fillcolor=hex_rgba(COLORS["danger"], 0.07),
                hovertemplate="<b>%{x}</b><br>위반: %{y}건<extra></extra>"
            ))
            fig.update_layout(**base_layout(220, ""))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("데이터 없음")
        card_close()
    with c2:
        card_open(f"채팅 SLA 위반 추이 (>{SLA_CHAT_WAIT}초)")
        if not ch_daily.empty:
            fig = go.Figure(go.Scatter(
                x=ch_daily["일자"], y=ch_daily["채팅위반"],
                mode="lines+markers",
                line=dict(color=COLORS["warning"], width=2.5, shape="spline", smoothing=0.8),
                marker=dict(size=5, color="#fff", line=dict(color=COLORS["warning"], width=2)),
                fill="tozeroy", fillcolor=hex_rgba(COLORS["warning"], 0.07),
                hovertemplate="<b>%{x}</b><br>위반: %{y}건<extra></extra>"
            ))
            fig.update_layout(**base_layout(220, ""))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("데이터 없음")
        card_close()
    with c3:
        card_open("게시판 SLA 위반 추이 (>24h)")
        if not bo_daily.empty:
            fig = go.Figure(go.Scatter(
                x=bo_daily["일자"], y=bo_daily["게시판위반"],
                mode="lines+markers",
                line=dict(color=COLORS["board"], width=2.5, shape="spline", smoothing=0.8),
                marker=dict(size=5, color="#fff", line=dict(color=COLORS["board"], width=2)),
                fill="tozeroy", fillcolor=hex_rgba(COLORS["board"], 0.07),
                hovertemplate="<b>%{x}</b><br>위반: %{y}건<extra></extra>"
            ))
            fig.update_layout(**base_layout(220, ""))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("데이터 없음")
        card_close()

    # ── Top 위반 드라이버 ─────────────────────────
    section_title("SLA 위반 주요 원인 드라이버")

    def breach_drivers(df, time_col, threshold, ch_label):
        if df.empty or time_col not in df.columns:
            return pd.DataFrame()
        tmp = df[df[time_col] > threshold].copy()
        if tmp.empty:
            return pd.DataFrame()
        rows = []
        for grp_col in ["브랜드","사업자명","대분류"]:
            if grp_col in tmp.columns:
                g = tmp.groupby(grp_col).size().reset_index(name="위반건수")
                g["구분"] = grp_col
                g.rename(columns={grp_col: "항목"}, inplace=True)
                rows.append(g)
        if not rows:
            return pd.DataFrame()
        out = pd.concat(rows).sort_values("위반건수", ascending=False)
        out["채널"] = ch_label
        return out

    tabs_driver = st.tabs(["📞 전화", "💬 채팅", "📝 게시판"])
    for tab, (df_r, tcol, thr, lbl) in zip(
        tabs_driver,
        [
            (ph_resp, "대기시간(초)", _sla_phone if _sla_phone else 99999, "전화"),
            (ch_resp, "응답시간(초)", _sla_chat,                           "채팅"),
            (bo_resp, "근무내리드타임(초)", _sla_board_in,                 "게시판"),
        ]
    ):
        with tab:
            drv = breach_drivers(df_r, tcol, thr, lbl)
            if drv.empty:
                st.info("위반 데이터 없음")
                continue
            for grp in ["브랜드","사업자명","대분류"]:
                sub = drv[drv["구분"]==grp].head(10)
                if sub.empty:
                    continue
                card_open(f"{grp}별 SLA 위반 TOP 10")
                fig = px.bar(
                    sub, x="위반건수", y="항목", orientation="h",
                    color="위반건수",
                    color_continuous_scale=["#fee2e2","#ef4444","#b91c1c"]
                )
                fig.update_layout(**base_layout(280,""))
                fig.update_traces(marker_line_width=0)
                fig.update_coloraxes(showscale=False)
                st.plotly_chart(fig, use_container_width=True)
                download_csv_button(sub, f"sla_driver_{lbl}_{grp}.csv")
                card_close()


# ══════════════════════════════════════════════
# ★ 신규 페이지 A2: 이상치 탐지
# ══════════════════════════════════════════════
def page_outlier(phone, chat, board):
    section_title("A2. 이상치 (Outlier) 탐지")

    std_mult = st.radio(
        "이상치 기준 (평균 + N×표준편차)",
        [2, 3], index=1, horizontal=True,
        format_func=lambda x: f"Mean + {x}σ",
        key="outlier_std"
    )

    def outlier_stats(series: pd.Series, label: str):
        s = series.dropna()
        if len(s) < 5:
            return None, None, None, None
        m  = s.mean()
        sd = s.std()
        cutoff = m + std_mult * sd
        n_out  = int((s > cutoff).sum())
        r_out  = n_out / len(s) * 100
        return m, sd, cutoff, n_out, r_out, s

    metrics = []
    if not phone.empty:
        ph_resp = phone[phone["응대여부"]=="응대"]
        if not ph_resp.empty:
            res = outlier_stats(ph_resp["AHT(초)"], "전화 AHT")
            if res[0] is not None:
                metrics.append(("전화 AHT", *res, COLORS["phone"]))
    if not chat.empty:
        ch_resp = chat[chat["응대여부"]=="응대"]
        if not ch_resp.empty:
            res = outlier_stats(ch_resp["응답시간(초)"], "채팅 대기")
            if res[0] is not None:
                metrics.append(("채팅 대기시간", *res, COLORS["chat"]))
    if not board.empty:
        bo_resp = board[board["응대여부"]=="응대"]
        if not bo_resp.empty:
            res = outlier_stats(bo_resp["리드타임(초)"], "게시판 LT")
            if res[0] is not None:
                metrics.append(("게시판 전체LT", *res, COLORS["board"]))

    if not metrics:
        st.info("충분한 응대 데이터가 없습니다.")
        return

    # ── KPI 카드 ─────────────────────────────────
    cols = st.columns(len(metrics))
    for col, (lbl, m, sd, cutoff, n_out, r_out, series, color) in zip(cols, metrics):
        with col:
            st.markdown(
                kpi_card(f"{lbl} 이상치", fmt_num(n_out),
                         unit="건", accent="red"),
                unsafe_allow_html=True
            )
            st.markdown(
                kpi_card(f"{lbl} 이상치율", fmt_pct(r_out),
                         accent="orange", reverse=True),
                unsafe_allow_html=True
            )

    # ── 분포 히스토그램 + 컷오프 라인 ─────────────
    section_title("분포 시각화 (히스토그램 + 이상치 경계)")
    for lbl, m, sd, cutoff, n_out, r_out, series, color in metrics:
        card_open(f"{lbl} 분포", f"이상치 기준: >{cutoff:.0f}초 (Mean+{std_mult}σ) | 이상치 {n_out}건 ({r_out:.1f}%)")
        fig = go.Figure()
        # 정상범위
        normal = series[series <= cutoff]
        outlier = series[series > cutoff]
        fig.add_trace(go.Histogram(
            x=normal, name="정상",
            marker_color=hex_rgba(color, 0.6),
            marker_line_color=color, marker_line_width=0.5,
            nbinsx=40,
            hovertemplate="구간: %{x}<br>건수: %{y}<extra></extra>"
        ))
        if not outlier.empty:
            fig.add_trace(go.Histogram(
                x=outlier, name="이상치",
                marker_color=hex_rgba(COLORS["danger"], 0.7),
                marker_line_color=COLORS["danger"], marker_line_width=0.5,
                nbinsx=20,
                hovertemplate="구간: %{x}<br>이상치: %{y}<extra></extra>"
            ))
        # 컷오프 라인
        fig.add_vline(
            x=cutoff,
            line=dict(color=COLORS["danger"], width=2, dash="dash"),
            annotation_text=f"컷오프 {cutoff:.0f}초",
            annotation_position="top right",
            annotation_font=dict(size=11, color=COLORS["danger"])
        )
        # 평균 라인
        fig.add_vline(
            x=m,
            line=dict(color=color, width=1.5, dash="dot"),
            annotation_text=f"평균 {m:.0f}초",
            annotation_position="top left",
            annotation_font=dict(size=11, color=color)
        )
        lo = base_layout(280, "")
        lo["barmode"] = "overlay"
        lo["xaxis"]["title"] = dict(text="처리시간(초)", font=dict(size=11))
        lo["yaxis"]["title"] = dict(text="건수", font=dict(size=11))
        fig.update_layout(**lo)
        st.plotly_chart(fig, use_container_width=True)
        card_close()

    # ── 박스플롯: 팀별 AHT 분산 ──────────────────
    if not phone.empty and "팀명" in phone.columns:
        section_title("전화 AHT 팀별 박스플롯 (분산 비교)")
        ph_resp = phone[phone["응대여부"]=="응대"].copy()
        ph_resp = ph_resp[~ph_resp["상담사명"].isin(EXCLUDE_AGENTS)]
        if not ph_resp.empty and "팀명" in ph_resp.columns:
            card_open("팀별 AHT 분포 (Box Plot)", "IQR 범위 + 이상치 포인트 표시")
            fig_box = px.box(
                ph_resp, x="팀명", y="AHT(초)",
                color="팀명",
                color_discrete_sequence=PALETTE,
                points="outliers",
                hover_data=["상담사명"] if "상담사명" in ph_resp.columns else None,
            )
            fig_box.update_traces(marker_size=4)
            fig_box.update_layout(**base_layout(340, ""))
            st.plotly_chart(fig_box, use_container_width=True)
            card_close()

    if not chat.empty and "팀명" in chat.columns:
        section_title("채팅 대기시간 팀별 박스플롯")
        ch_resp = chat[chat["응대여부"]=="응대"].copy()
        ch_resp = ch_resp[~ch_resp["상담사명"].isin(EXCLUDE_AGENTS)]
        if not ch_resp.empty:
            card_open("팀별 채팅 대기시간 분포 (Box Plot)", "이상치 포인트 표시")
            fig_box2 = px.box(
                ch_resp, x="팀명", y="응답시간(초)",
                color="팀명",
                color_discrete_sequence=PALETTE,
                points="outliers",
            )
            fig_box2.update_traces(marker_size=4)
            fig_box2.update_layout(**base_layout(320, ""))
            st.plotly_chart(fig_box2, use_container_width=True)
            card_close()


# ══════════════════════════════════════════════
# ★ 신규 페이지 A3: 연속 미응대 탐지
# ══════════════════════════════════════════════
def page_burst(phone, chat):
    section_title("A3. 연속 미응대 (Burst) 탐지")

    c1, c2, c3 = st.columns(3)
    with c1:
        n_threshold = st.number_input(
            "연속 미응대 임계값 (N건)", min_value=2, max_value=50, value=5, step=1,
            key="burst_n"
        )
    with c2:
        interval_min = st.selectbox(
            "그룹 인터벌", [5, 10, 15, 30, 60], index=1,
            format_func=lambda x: f"{x}분", key="burst_interval"
        )
    with c3:
        ch_sel = st.multiselect(
            "채널", ["전화","채팅"], default=["전화","채팅"],
            key="burst_ch"
        )

    frames = []
    if "전화" in ch_sel and not phone.empty and "인입시각" in phone.columns:
        tmp = phone[["인입시각","응대여부","사업자명","브랜드"]].copy()
        tmp = tmp[tmp["인입시각"].notna()]
        tmp["채널"] = "전화"
        tmp["시각"] = tmp["인입시각"]
        frames.append(tmp[["시각","응대여부","사업자명","브랜드","채널"]])
    if "채팅" in ch_sel and not chat.empty and "접수일시" in chat.columns:
        tmp = chat[["접수일시","응대여부","사업자명","브랜드"]].copy()
        tmp = tmp[tmp["접수일시"].notna()]
        tmp["채널"] = "채팅"
        tmp["시각"] = tmp["접수일시"]
        frames.append(tmp[["시각","응대여부","사업자명","브랜드","채널"]])

    if not frames:
        st.info("인입 시각 데이터가 없습니다.")
        return

    df_all = pd.concat(frames, ignore_index=True).sort_values("시각")
    df_all["버킷"] = df_all["시각"].dt.floor(f"{interval_min}min")
    df_all["미응대"] = (df_all["응대여부"] == "미응대").astype(int)

    # 버킷별 미응대 집계
    bucket_agg = df_all.groupby(["버킷","채널"]).agg(
        전체=("미응대","count"),
        미응대수=("미응대","sum"),
    ).reset_index()
    bucket_agg["미응대율"] = (bucket_agg["미응대수"] / bucket_agg["전체"] * 100).round(1)

    # 임계값 초과 버스트 구간
    burst_df = bucket_agg[bucket_agg["미응대수"] >= n_threshold].copy()
    burst_df["버킷_종료"] = burst_df["버킷"] + timedelta(minutes=interval_min)

    st.markdown(
        f"<span class='dash-badge {'danger' if len(burst_df) > 0 else 'success'}'>"
        f"{'⚠️' if len(burst_df) > 0 else '✅'} "
        f"버스트 구간 {len(burst_df)}개 발견 (기준: {interval_min}분 내 ≥{n_threshold}건 미응대)"
        f"</span>",
        unsafe_allow_html=True
    )
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── 타임라인 차트 ──────────────────────────────
    section_title("미응대 타임라인")
    card_open("시간 버킷별 미응대 건수 (버스트 구간 강조)")
    fig_tl = go.Figure()
    for ch, c in [("전화", COLORS["phone"]), ("채팅", COLORS["chat"])]:
        sub = bucket_agg[bucket_agg["채널"]==ch]
        if sub.empty:
            continue
        fig_tl.add_trace(go.Bar(
            x=sub["버킷"], y=sub["미응대수"],
            name=f"{ch} 미응대",
            marker_color=hex_rgba(c, 0.5),
            marker_line_color=c, marker_line_width=0.5,
            hovertemplate="<b>%{x}</b><br>미응대: %{y}건<extra></extra>"
        ))
    # 버스트 구간 음영
    for _, row in burst_df.iterrows():
        fig_tl.add_vrect(
            x0=row["버킷"], x1=row["버킷_종료"],
            fillcolor=hex_rgba(COLORS["danger"], 0.15),
            line=dict(color=COLORS["danger"], width=1, dash="dot"),
            annotation_text="🔴", annotation_position="top left",
        )
    lo = base_layout(320, "")
    lo["barmode"] = "stack"
    lo["xaxis"]["title"] = dict(text=f"시간 ({interval_min}분 버킷)", font=dict(size=11))
    fig_tl.update_layout(**lo)
    st.plotly_chart(fig_tl, use_container_width=True)
    card_close()

    # ── 버스트 테이블 ──────────────────────────────
    if not burst_df.empty:
        section_title("버스트 구간 목록")
        card_open(f"임계값 초과 구간 ({n_threshold}건 이상)")
        display_burst = burst_df[["버킷","버킷_종료","채널","미응대수","전체","미응대율"]].rename(columns={
            "버킷":    "시작",
            "버킷_종료":"종료",
            "미응대수": "미응대",
            "전체":    "전체인입",
            "미응대율": "미응대율(%)",
        }).sort_values("미응대", ascending=False)
        st.dataframe(display_burst, use_container_width=True, height=320)
        download_csv_button(display_burst, "burst_detection.csv")
        card_close()
    else:
        st.markdown("""
        <div class="alert-card success">
          <span class="alert-icon">✅</span>
          <span>설정된 기준 이상의 버스트 구간이 감지되지 않았습니다.</span>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# ★ 신규 페이지 B1: 요일×시간대 패턴 히트맵
# ══════════════════════════════════════════════
def page_weekday_heatmap(phone, chat):
    section_title("B1. 요일 × 시간대 인입 패턴")

    WEEKDAY_KR = {0:"월",1:"화",2:"수",3:"목",4:"금",5:"토",6:"일"}
    WEEKDAY_ORDER = ["월","화","수","목","금","토","일"]

    c1, c2 = st.columns(2)
    with c1:
        ch_sel = st.selectbox("채널", ["전화","채팅"], key="wh_ch")
    with c2:
        metric_sel = st.selectbox(
            "지표",
            ["인입건수","미응대율(%)","평균처리시간(초)"],
            key="wh_metric"
        )

    df_target = phone if ch_sel == "전화" else chat
    time_col  = "인입시각" if ch_sel == "전화" else "접수일시"
    metric_col = "AHT(초)" if ch_sel == "전화" else "응답시간(초)"

    if df_target.empty or time_col not in df_target.columns:
        st.info(f"{ch_sel} 시각 데이터가 없습니다.")
        return

    tmp = df_target.copy()
    tmp = tmp[tmp[time_col].notna()]
    tmp["요일"] = tmp[time_col].dt.dayofweek.map(WEEKDAY_KR)
    tmp["시간대"] = tmp[time_col].dt.hour

    if metric_sel == "인입건수":
        piv = tmp.pivot_table(index="요일", columns="시간대",
                              values=time_col, aggfunc="count", fill_value=0)
        z_label = "건수"
        color_scale = [[0,"#f8fafc"],[0.3,"#e0e7ff"],[0.6,"#818cf8"],[1.0,"#3730a3"]]
    elif metric_sel == "미응대율(%)":
        tmp["미응대"] = (tmp["응대여부"] == "미응대").astype(float)
        piv = tmp.pivot_table(index="요일", columns="시간대",
                              values="미응대", aggfunc="mean", fill_value=0)
        piv = (piv * 100).round(1)
        z_label = "미응대율(%)"
        color_scale = [[0,"#f0fdf4"],[0.3,"#fef3c7"],[0.7,"#fca5a5"],[1.0,"#b91c1c"]]
    else:
        resp_tmp = tmp[tmp["응대여부"]=="응대"]
        if resp_tmp.empty or metric_col not in resp_tmp.columns:
            st.info("처리시간 데이터 없음")
            return
        piv = resp_tmp.pivot_table(index="요일", columns="시간대",
                                   values=metric_col, aggfunc="mean", fill_value=0)
        z_label = "평균처리시간(초)"
        color_scale = [[0,"#fef3c7"],[0.5,"#f59e0b"],[1.0,"#92400e"]]

    # 요일 순서 정렬
    piv = piv.reindex([d for d in WEEKDAY_ORDER if d in piv.index])

    card_open(f"{ch_sel} 요일 × 시간대 히트맵", f"지표: {metric_sel}")
    fig = go.Figure(go.Heatmap(
        z=piv.values,
        x=piv.columns.astype(str),
        y=piv.index.astype(str),
        colorscale=color_scale,
        showscale=True,
        colorbar=dict(
            title=dict(text=z_label, font=dict(size=11)),
            thickness=10, len=0.8,
            tickfont=dict(size=10, color="#94a3b8"),
            outlinewidth=0
        ),
        hovertemplate=f"요일: <b>%{{y}}</b><br>시간대: <b>%{{x}}시</b><br>{z_label}: <b>%{{z}}</b><extra></extra>"
    ))
    lo = base_layout(340, "")
    lo["xaxis"]["title"] = dict(text="시간대 (시)", font=dict(size=11))
    lo["yaxis"]["title"] = dict(text="요일", font=dict(size=11))
    fig.update_layout(**lo)
    st.plotly_chart(fig, use_container_width=True)
    card_close()

    # 요일별 합계 바 차트
    section_title("요일별 인입 합계")
    c1, c2 = st.columns(2)
    with c1:
        card_open("요일별 인입 건수 (전화)")
        if not phone.empty and "인입시각" in phone.columns:
            ph_tmp = phone.copy()
            ph_tmp = ph_tmp[ph_tmp["인입시각"].notna()]
            ph_tmp["요일"] = ph_tmp["인입시각"].dt.dayofweek.map(WEEKDAY_KR)
            ph_dow = ph_tmp.groupby("요일").size().reindex(WEEKDAY_ORDER, fill_value=0).reset_index(name="건수")
            ph_dow.columns = ["요일","건수"]
            fig_dow = px.bar(ph_dow, x="요일", y="건수",
                             color="건수",
                             color_continuous_scale=["#e0e7ff","#6366f1","#3730a3"])
            fig_dow.update_layout(**base_layout(260,""))
            fig_dow.update_traces(marker_line_width=0)
            fig_dow.update_coloraxes(showscale=False)
            st.plotly_chart(fig_dow, use_container_width=True)
        else:
            st.info("데이터 없음")
        card_close()
    with c2:
        card_open("요일별 인입 건수 (채팅)")
        if not chat.empty and "접수일시" in chat.columns:
            ch_tmp = chat.copy()
            ch_tmp = ch_tmp[ch_tmp["접수일시"].notna()]
            ch_tmp["요일"] = ch_tmp["접수일시"].dt.dayofweek.map(WEEKDAY_KR)
            ch_dow = ch_tmp.groupby("요일").size().reindex(WEEKDAY_ORDER, fill_value=0).reset_index(name="건수")
            ch_dow.columns = ["요일","건수"]
            fig_dow2 = px.bar(ch_dow, x="요일", y="건수",
                              color="건수",
                              color_continuous_scale=["#d1fae5","#22c55e","#15803d"])
            fig_dow2.update_layout(**base_layout(260,""))
            fig_dow2.update_traces(marker_line_width=0)
            fig_dow2.update_coloraxes(showscale=False)
            st.plotly_chart(fig_dow2, use_container_width=True)
        else:
            st.info("데이터 없음")
        card_close()


# ══════════════════════════════════════════════
# ★ 신규 페이지 B2: 변동성 지수 (CV)
# ══════════════════════════════════════════════
def page_volatility(phone, chat, board, unit):
    section_title("B2. 인입 변동성 지수 (CV = σ/μ × 100)")

    st.markdown("""
    <div class="alert-card info">
      <span class="alert-icon">📊</span>
      <span><b>CV (변동계수)</b>: 평균 대비 표준편차 비율(%). CV가 높을수록 인입량 예측이 어렵고 인력 계획 리스크가 높습니다.</span>
    </div>""", unsafe_allow_html=True)

    pc = get_period_col(unit)

    def compute_cv(df, label):
        if df.empty or pc not in df.columns:
            return None
        grp = df.groupby(pc).size()
        if len(grp) < 3:
            return None
        m  = grp.mean()
        sd = grp.std()
        cv = sd / m * 100 if m > 0 else 0.0
        return {"채널": label, "평균": round(m,1), "표준편차": round(sd,1), "CV(%)": round(cv,1), "최대": int(grp.max()), "최소": int(grp.min())}

    rows = []
    for df, lbl in [(phone,"전화"),(chat,"채팅"),(board,"게시판")]:
        r = compute_cv(df, lbl)
        if r: rows.append(r)

    if not rows:
        st.info("충분한 기간 데이터가 없습니다.")
        return

    cv_df = pd.DataFrame(rows).sort_values("CV(%)", ascending=False)

    # ── KPI 카드 ─────────────────────────────────
    cols = st.columns(len(cv_df))
    for col, (_, row) in zip(cols, cv_df.iterrows()):
        with col:
            accent = "red" if row["CV(%)"] > 50 else ("orange" if row["CV(%)"] > 30 else "green")
            st.markdown(
                kpi_card(f"{row['채널']} CV", f"{row['CV(%)']:.1f}", unit="%", accent=accent),
                unsafe_allow_html=True
            )

    card_open("채널별 CV 비교 테이블")
    st.dataframe(cv_df, use_container_width=True)
    card_close()

    # ── 브랜드/사업자별 CV ─────────────────────────
    section_title("브랜드 / 사업자별 변동성 순위")
    tabs_cv = st.tabs(["전화","채팅","게시판"])
    for tab, df, lbl in zip(tabs_cv, [phone,chat,board], ["전화","채팅","게시판"]):
        with tab:
            if df.empty or pc not in df.columns:
                st.info("데이터 없음")
                continue
            for grp_col in ["브랜드","사업자명"]:
                if grp_col not in df.columns:
                    continue
                grp_cv = []
                for val, sub in df.groupby(grp_col):
                    g = sub.groupby(pc).size()
                    if len(g) < 3:
                        continue
                    m  = g.mean()
                    sd = g.std()
                    cv_val = sd / m * 100 if m > 0 else 0.0
                    grp_cv.append({grp_col: val, "평균": round(m,1), "CV(%)": round(cv_val,1)})
                if not grp_cv:
                    continue
                grp_cv_df = pd.DataFrame(grp_cv).sort_values("CV(%)", ascending=False).head(15)
                card_open(f"{lbl} {grp_col}별 CV 순위 (상위 15)", "CV가 높을수록 변동성 크고 예측 어려움")
                fig = px.bar(
                    grp_cv_df, x="CV(%)", y=grp_col, orientation="h",
                    color="CV(%)",
                    color_continuous_scale=["#d1fae5","#f59e0b","#ef4444"]
                )
                fig.update_layout(**base_layout(320,""))
                fig.update_traces(marker_line_width=0)
                fig.update_coloraxes(showscale=False)
                st.plotly_chart(fig, use_container_width=True)
                download_csv_button(grp_cv_df, f"cv_{lbl}_{grp_col}.csv")
                card_close()


# ══════════════════════════════════════════════
# ★ 신규 페이지 B3: 인력 산정 (Erlang-C 기반)
# ══════════════════════════════════════════════
def erlang_c_prob(agents: int, traffic_intensity: float) -> float:
    """
    Erlang-C: P(waiting) = C(N, A) 계산
    N = agents, A = traffic intensity (λ/μ = arrival_rate * aht)
    """
    if agents <= 0 or traffic_intensity <= 0:
        return 1.0
    if traffic_intensity >= agents:
        return 1.0  # 과부하
    try:
        # P0 계산 (Erlang-C)
        sum_term = sum((traffic_intensity ** k) / math.factorial(k) for k in range(agents))
        erlang_b_num = (traffic_intensity ** agents) / math.factorial(agents)
        erlang_b_den = erlang_b_num + (1 - traffic_intensity / agents) * sum_term
        if erlang_b_den <= 0:
            return 1.0
        prob_wait = erlang_b_num / erlang_b_den
        return min(prob_wait, 1.0)
    except (OverflowError, ZeroDivisionError):
        return 1.0


def service_level_erlang(agents: int, traffic_intensity: float,
                          aht: float, target_sec: float) -> float:
    """서비스 레벨 = 1 - P(wait) * exp(-(N-A)*t/AHT)"""
    if agents <= 0 or aht <= 0:
        return 0.0
    if traffic_intensity >= agents:
        return 0.0
    pw = erlang_c_prob(agents, traffic_intensity)
    exponent = -(agents - traffic_intensity) * target_sec / aht
    sl = 1.0 - pw * math.exp(exponent)
    return max(0.0, min(1.0, sl))


def required_agents_erlang(calls_per_interval: float, aht: float,
                            interval_sec: float, target_sl: float,
                            target_sec: float, max_agents: int = 200) -> int:
    """목표 SL 달성을 위한 최소 상담사 수 반환"""
    if calls_per_interval <= 0 or aht <= 0:
        return 0
    traffic = calls_per_interval * aht / interval_sec  # A (Erlang)
    min_agents = max(1, math.ceil(traffic))
    for n in range(min_agents, max_agents + 1):
        sl = service_level_erlang(n, traffic, aht, target_sec)
        if sl >= target_sl:
            return n
    return max_agents


def page_staffing(phone, chat):
    section_title("B3. 인력 산정 시뮬레이터 (Erlang-C 기반)")

    st.markdown("""
    <div class="alert-card warning">
      <span class="alert-icon">⚠️</span>
      <span><b>시뮬레이션 가정:</b> Erlang-C 모델 적용 (무한 대기열, Poisson 도착, 지수분포 처리시간).
      포기(Abandon) 미반영. 결과는 <b>추정치</b>이며 실제 운영 계획 수립 시 참고용으로만 사용하세요.</span>
    </div>""", unsafe_allow_html=True)

    tab_phone, tab_chat = st.tabs(["📞 전화 인력 산정", "💬 채팅 인력 산정"])

    # ── 전화 ──────────────────────────────────────
    with tab_phone:
        if phone.empty:
            st.info("전화 데이터가 없습니다.")
        else:
            ph_resp = phone[phone["응대여부"]=="응대"]
            avg_aht = float(ph_resp["AHT(초)"].mean()) if not ph_resp.empty else 300.0

            c1, c2, c3 = st.columns(3)
            with c1:
                target_sl_ph  = st.slider("목표 응대율(%)", 60, 100, 80, 5, key="sl_ph") / 100
                target_sec_ph = st.number_input("목표 대기시간 이내(초)", 10, 120, 20, 5, key="ts_ph")
            with c2:
                interval_ph  = st.selectbox("인터벌(분)", [15,30,60], index=1, key="iv_ph")
                shrinkage_ph = st.slider("수축률 Shrinkage(%)", 0, 40, 20, 5, key="sh_ph") / 100
            with c3:
                custom_aht_ph = st.number_input(
                    f"평균 AHT(초) [데이터 평균: {avg_aht:.0f}초]",
                    min_value=30, max_value=3600,
                    value=int(avg_aht) or 300,
                    step=30, key="aht_ph"
                )

            interval_sec_ph = interval_ph * 60
            # 인터벌당 평균 인입 계산
            if "인입시각" in phone.columns:
                tmp_ph = phone.copy()
                tmp_ph = tmp_ph[tmp_ph["인입시각"].notna()]
                tmp_ph["버킷"] = tmp_ph["인입시각"].dt.floor(f"{interval_ph}min")
                avg_calls_ph = tmp_ph.groupby("버킷").size().mean()
            else:
                avg_calls_ph = len(phone) / max(1, (phone["일자"].nunique() * (8 * 60 / interval_ph)))

            traffic_ph = avg_calls_ph * custom_aht_ph / interval_sec_ph
            req_agents_raw = required_agents_erlang(
                avg_calls_ph, custom_aht_ph, interval_sec_ph,
                target_sl_ph, target_sec_ph
            )
            req_agents_net = math.ceil(req_agents_raw / (1 - shrinkage_ph))
            sl_achieved = service_level_erlang(req_agents_raw, traffic_ph, custom_aht_ph, target_sec_ph)

            section_title("전화 인력 산정 결과")
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.markdown(kpi_card("인터벌당 평균 인입", f"{avg_calls_ph:.1f}", unit="건", accent="blue"), unsafe_allow_html=True)
            with c2: st.markdown(kpi_card("트래픽 강도(A)", f"{traffic_ph:.2f}", unit="Erl", accent="orange"), unsafe_allow_html=True)
            with c3: st.markdown(kpi_card("순수 필요 인원", fmt_num(req_agents_raw), unit="명", accent="green"), unsafe_allow_html=True)
            with c4: st.markdown(kpi_card(f"수축률({shrinkage_ph*100:.0f}%) 반영", fmt_num(req_agents_net), unit="명", accent="red"), unsafe_allow_html=True)

            st.markdown(f"""
            <div class="alert-card {'success' if sl_achieved >= target_sl_ph else 'danger'}">
              <span class="alert-icon">{'✅' if sl_achieved >= target_sl_ph else '❌'}</span>
              <span>목표 SL <b>{target_sl_ph*100:.0f}%</b> @ <b>{target_sec_ph}초</b> 이내 &nbsp;→&nbsp;
              달성 SL: <b>{sl_achieved*100:.1f}%</b> (순수 {req_agents_raw}명 기준)</span>
            </div>""", unsafe_allow_html=True)

            # 시간대별 필요 인원 테이블
            if "인입시각" in phone.columns:
                section_title("시간대별 필요 인원 추정")
                tmp_ph = phone.copy()
                tmp_ph = tmp_ph[tmp_ph["인입시각"].notna()]
                tmp_ph["시간대"] = tmp_ph["인입시각"].dt.hour
                hourly_calls = tmp_ph.groupby("시간대").size() / max(1, phone["일자"].nunique())
                rows_staff = []
                for hr, calls in hourly_calls.items():
                    calls_per_iv = calls * interval_ph / 60
                    n_raw = required_agents_erlang(
                        calls_per_iv, custom_aht_ph, interval_sec_ph,
                        target_sl_ph, target_sec_ph
                    )
                    n_net = math.ceil(n_raw / (1 - shrinkage_ph))
                    rows_staff.append({
                        "시간대": f"{hr:02d}:00",
                        f"평균인입({interval_ph}분)": round(calls_per_iv,1),
                        "순수 필요인원": n_raw,
                        "수축률 반영": n_net,
                    })
                staff_df = pd.DataFrame(rows_staff)
                card_open("시간대별 인력 산정 테이블")
                st.dataframe(staff_df, use_container_width=True, height=340)
                download_csv_button(staff_df, "staffing_phone_hourly.csv")
                card_close()

    # ── 채팅 ──────────────────────────────────────
    with tab_chat:
        if chat.empty:
            st.info("채팅 데이터가 없습니다.")
        else:
            ch_resp = chat[chat["응대여부"]=="응대"]
            avg_lt_chat = float(ch_resp["리드타임(초)"].mean()) if not ch_resp.empty else 600.0

            c1, c2, c3 = st.columns(3)
            with c1:
                target_sl_ch  = st.slider("목표 응대율(%)", 60, 100, 80, 5, key="sl_ch") / 100
                target_sec_ch = st.number_input("목표 대기시간 이내(초)", 10, 300, 60, 10, key="ts_ch")
            with c2:
                interval_ch  = st.selectbox("인터벌(분)", [15,30,60], index=1, key="iv_ch")
                concurrency  = st.slider("동시처리 수 (채팅 동시응대)", 1, 5, 2, 1, key="conc_ch")
                shrinkage_ch = st.slider("수축률 Shrinkage(%)", 0, 40, 20, 5, key="sh_ch") / 100
            with c3:
                custom_lt_ch = st.number_input(
                    f"평균 리드타임(초) [데이터 평균: {avg_lt_chat:.0f}초]",
                    min_value=30, max_value=7200,
                    value=int(avg_lt_chat) or 600,
                    step=30, key="lt_ch"
                )

            interval_sec_ch = interval_ch * 60
            if "접수일시" in chat.columns:
                tmp_ch = chat.copy()
                tmp_ch = tmp_ch[tmp_ch["접수일시"].notna()]
                tmp_ch["버킷"] = tmp_ch["접수일시"].dt.floor(f"{interval_ch}min")
                avg_calls_ch = tmp_ch.groupby("버킷").size().mean()
            else:
                avg_calls_ch = len(chat) / max(1, (chat["일자"].nunique() * (8 * 60 / interval_ch)))

            # 채팅은 동시처리를 고려: 실효 AHT = LT / concurrency
            eff_aht_ch = custom_lt_ch / concurrency
            traffic_ch = avg_calls_ch * eff_aht_ch / interval_sec_ch
            req_agents_ch_raw = required_agents_erlang(
                avg_calls_ch, eff_aht_ch, interval_sec_ch,
                target_sl_ch, target_sec_ch
            )
            req_agents_ch_net = math.ceil(req_agents_ch_raw / (1 - shrinkage_ch))

            section_title("채팅 인력 산정 결과")
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.markdown(kpi_card("인터벌당 평균 인입", f"{avg_calls_ch:.1f}", unit="건", accent="green"), unsafe_allow_html=True)
            with c2: st.markdown(kpi_card("트래픽 강도(A)", f"{traffic_ch:.2f}", unit="Erl", accent="orange"), unsafe_allow_html=True)
            with c3: st.markdown(kpi_card("순수 필요 인원", fmt_num(req_agents_ch_raw), unit="명", accent="green"), unsafe_allow_html=True)
            with c4: st.markdown(kpi_card(f"수축률 반영", fmt_num(req_agents_ch_net), unit="명", accent="red"), unsafe_allow_html=True)

            st.markdown(f"""
            <div class="alert-card info">
              <span class="alert-icon">💡</span>
              <span>동시처리 {concurrency}회 적용 → 실효 AHT = {eff_aht_ch:.0f}초.
              Erlang-C는 단일 대기열 가정이므로 채팅 동시처리 환경에서는 <b>실제 필요 인원이 더 낮을 수 있습니다.</b></span>
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# ★ 신규 페이지 C1: AHT 분산 분석 (Box Plot)
# ══════════════════════════════════════════════
def page_aht_dispersion(phone, chat):
    section_title("C1. 상담사 AHT / 대기시간 분산 분석")

    std_mult_flag = st.radio(
        "이상 상담사 플래그 기준", [2, 3], index=0, horizontal=True,
        format_func=lambda x: f"75백분위 초과 + 평균+{x}σ 이상",
        key="disp_std"
    )

    # ── 전화 AHT 박스플롯 ──────────────────────────
    if not phone.empty:
        ph_resp = phone[phone["응대여부"]=="응대"].copy()
        ph_resp = ph_resp[~ph_resp["상담사명"].isin(EXCLUDE_AGENTS)]

        if not ph_resp.empty and "AHT(초)" in ph_resp.columns:
            section_title("전화 AHT 분산 (팀별 / 근속그룹별)")
            c1, c2 = st.columns(2)
            with c1:
                if "팀명" in ph_resp.columns:
                    card_open("팀별 AHT 박스플롯")
                    fig = px.box(
                        ph_resp, x="팀명", y="AHT(초)", color="팀명",
                        color_discrete_sequence=PALETTE, points="outliers",
                        hover_data=["상담사명"] if "상담사명" in ph_resp.columns else None
                    )
                    fig.update_traces(marker_size=4)
                    fig.update_layout(**base_layout(320,""))
                    st.plotly_chart(fig, use_container_width=True)
                    card_close()
            with c2:
                if "근속그룹" in ph_resp.columns:
                    card_open("근속그룹별 AHT 박스플롯")
                    fig2 = px.box(
                        ph_resp, x="근속그룹", y="AHT(초)", color="근속그룹",
                        color_discrete_sequence=PALETTE, points="outliers",
                        hover_data=["상담사명"] if "상담사명" in ph_resp.columns else None
                    )
                    fig2.update_traces(marker_size=4)
                    fig2.update_layout(**base_layout(320,""))
                    st.plotly_chart(fig2, use_container_width=True)
                    card_close()

            # 상담사별 플래그
            section_title("⚑ 이상 상담사 플래그 (전화 AHT)")
            ag_ph = ph_resp.groupby("상담사명")["AHT(초)"].agg(["mean","std","count"]).reset_index()
            ag_ph.columns = ["상담사명","평균AHT","표준편차","건수"]
            global_mean = ph_resp["AHT(초)"].mean()
            global_std  = ph_resp["AHT(초)"].std()
            p75 = ph_resp["AHT(초)"].quantile(0.75)
            cutoff = global_mean + std_mult_flag * global_std
            flag_df = ag_ph[
                (ag_ph["평균AHT"] > p75) &
                (ag_ph["평균AHT"] > cutoff)
            ].sort_values("평균AHT", ascending=False)

            if not flag_df.empty:
                st.markdown(f"""
                <div class="alert-card danger">
                  <span class="alert-icon">🚩</span>
                  <span><b>{len(flag_df)}명</b>의 상담사가 75백분위({p75:.0f}초) 초과 + 평균+{std_mult_flag}σ({cutoff:.0f}초) 이상 AHT를 기록했습니다.</span>
                </div>""", unsafe_allow_html=True)
                card_open("이상 상담사 플래그 목록")
                flag_df["평균AHT_표시"] = flag_df["평균AHT"].apply(fmt_hms)
                flag_df["표준편차_표시"] = flag_df["표준편차"].apply(lambda x: fmt_hms(x) if not pd.isna(x) else "-")
                st.dataframe(
                    flag_df[["상담사명","건수","평균AHT_표시","표준편차_표시"]].rename(columns={
                        "평균AHT_표시":"평균 AHT","표준편차_표시":"표준편차"
                    }),
                    use_container_width=True, height=240
                )
                download_csv_button(flag_df, "aht_flag_agents.csv")
                card_close()
            else:
                st.markdown("""
                <div class="alert-card success">
                  <span class="alert-icon">✅</span>
                  <span>이상치 상담사가 감지되지 않았습니다.</span>
                </div>""", unsafe_allow_html=True)

    # ── 채팅 대기시간 박스플롯 ─────────────────────
    if not chat.empty:
        ch_resp = chat[chat["응대여부"]=="응대"].copy()
        ch_resp = ch_resp[~ch_resp["상담사명"].isin(EXCLUDE_AGENTS)]

        if not ch_resp.empty and "응답시간(초)" in ch_resp.columns:
            section_title("채팅 대기시간 분산")
            c1, c2 = st.columns(2)
            with c1:
                if "팀명" in ch_resp.columns:
                    card_open("팀별 채팅 대기시간 박스플롯")
                    fig3 = px.box(
                        ch_resp, x="팀명", y="응답시간(초)", color="팀명",
                        color_discrete_sequence=PALETTE, points="outliers"
                    )
                    fig3.update_traces(marker_size=4)
                    fig3.update_layout(**base_layout(300,""))
                    st.plotly_chart(fig3, use_container_width=True)
                    card_close()
            with c2:
                if "근속그룹" in ch_resp.columns:
                    card_open("근속그룹별 채팅 대기시간 박스플롯")
                    fig4 = px.box(
                        ch_resp, x="근속그룹", y="응답시간(초)", color="근속그룹",
                        color_discrete_sequence=PALETTE, points="outliers"
                    )
                    fig4.update_traces(marker_size=4)
                    fig4.update_layout(**base_layout(300,""))
                    st.plotly_chart(fig4, use_container_width=True)
                    card_close()


# ══════════════════════════════════════════════
# ★ 신규 페이지 C2: 학습곡선 (근속그룹별)
# ══════════════════════════════════════════════
def page_learning_curve(phone, chat, board):
    section_title("C2. 근속그룹별 학습 곡선")

    TENURE_ORDER = [l for _, l in TENURE_GROUPS]

    def tenure_stats(df, metric_col, vol_col=None):
        if df.empty or "근속그룹" not in df.columns:
            return pd.DataFrame()
        resp = df[df["응대여부"]=="응대"] if "응대여부" in df.columns else df
        if resp.empty:
            return pd.DataFrame()
        agg_dict = {"건수": (metric_col if vol_col is None else vol_col, "count")}
        if metric_col in resp.columns:
            agg_dict["평균지표"] = (metric_col, "mean")
        if "응대여부" in df.columns:
            total_df = df.groupby("근속그룹").size().rename("전체인입")
            resp_cnt = resp.groupby("근속그룹").size().rename("응대건수")
            out = pd.concat([total_df, resp_cnt], axis=1).fillna(0).reset_index()
            out["응대율"] = (out["응대건수"] / out["전체인입"] * 100).round(1)
            if metric_col in resp.columns:
                mean_df = resp.groupby("근속그룹")[metric_col].mean().rename("평균지표").reset_index()
                out = out.merge(mean_df, on="근속그룹", how="left")
        else:
            out = resp.groupby("근속그룹").agg(응대건수=(metric_col,"count")).reset_index()
        existing = [t for t in TENURE_ORDER if t in out["근속그룹"].values]
        out = out.set_index("근속그룹").reindex(existing).reset_index()
        return out

    tab_ph, tab_ch, tab_bo = st.tabs(["📞 전화 AHT","💬 채팅 대기","📝 게시판 LT"])

    with tab_ph:
        df_lc = tenure_stats(phone, "AHT(초)")
        if df_lc.empty:
            st.info("데이터 없음")
        else:
            c1, c2 = st.columns(2)
            with c1:
                card_open("근속그룹별 평균 AHT", "신규→기존 순서로 AHT 안정화 곡선")
                if "평균지표" in df_lc.columns:
                    fig = go.Figure(go.Scatter(
                        x=df_lc["근속그룹"], y=df_lc["평균지표"],
                        mode="lines+markers",
                        line=dict(color=COLORS["primary"], width=2.5, shape="spline", smoothing=0.6),
                        marker=dict(size=8, color=COLORS["primary"],
                                    line=dict(color="#fff", width=2)),
                        fill="tozeroy", fillcolor=hex_rgba(COLORS["primary"], 0.06),
                        text=df_lc["평균지표"].apply(fmt_hms),
                        hovertemplate="<b>%{x}</b><br>평균AHT: %{text}<extra></extra>"
                    ))
                    fig.update_layout(**base_layout(300,""))
                    st.plotly_chart(fig, use_container_width=True)
                card_close()
            with c2:
                card_open("근속그룹별 응대율", "숙련도에 따른 응대율 변화")
                if "응대율" in df_lc.columns:
                    fig2 = go.Figure(go.Bar(
                        x=df_lc["근속그룹"], y=df_lc["응대율"],
                        marker_color=COLORS["success"], marker_line_width=0,
                        text=df_lc["응대율"].apply(lambda x: f"{x:.1f}%"),
                        textposition="outside",
                        hovertemplate="<b>%{x}</b><br>응대율: %{y:.1f}%<extra></extra>"
                    ))
                    lo = base_layout(300,"")
                    lo["yaxis"]["ticksuffix"] = "%"
                    lo["yaxis"]["range"] = [0, 115]
                    fig2.update_layout(**lo)
                    st.plotly_chart(fig2, use_container_width=True)
                card_close()
            card_open("근속그룹별 학습곡선 데이터")
            disp_cols = [c for c in ["근속그룹","응대건수","전체인입","응대율","평균지표"] if c in df_lc.columns]
            st.dataframe(df_lc[disp_cols], use_container_width=True)
            card_close()

    with tab_ch:
        df_lc_ch = tenure_stats(chat, "응답시간(초)")
        if df_lc_ch.empty:
            st.info("데이터 없음")
        else:
            card_open("근속그룹별 평균 채팅 대기시간 (학습곡선)")
            if "평균지표" in df_lc_ch.columns:
                fig3 = go.Figure(go.Scatter(
                    x=df_lc_ch["근속그룹"], y=df_lc_ch["평균지표"],
                    mode="lines+markers",
                    line=dict(color=COLORS["chat"], width=2.5, shape="spline", smoothing=0.6),
                    marker=dict(size=8, color=COLORS["chat"], line=dict(color="#fff", width=2)),
                    fill="tozeroy", fillcolor=hex_rgba(COLORS["chat"], 0.06),
                    text=df_lc_ch["평균지표"].apply(fmt_hms),
                    hovertemplate="<b>%{x}</b><br>평균대기: %{text}<extra></extra>"
                ))
                fig3.update_layout(**base_layout(300,""))
                st.plotly_chart(fig3, use_container_width=True)
            card_close()

    with tab_bo:
        df_lc_bo = tenure_stats(board, "리드타임(초)")
        if df_lc_bo.empty:
            st.info("데이터 없음")
        else:
            card_open("근속그룹별 평균 게시판 LT (학습곡선)")
            if "평균지표" in df_lc_bo.columns:
                fig4 = go.Figure(go.Scatter(
                    x=df_lc_bo["근속그룹"], y=df_lc_bo["평균지표"],
                    mode="lines+markers",
                    line=dict(color=COLORS["board"], width=2.5, shape="spline", smoothing=0.6),
                    marker=dict(size=8, color=COLORS["board"], line=dict(color="#fff", width=2)),
                    fill="tozeroy", fillcolor=hex_rgba(COLORS["board"], 0.06),
                    text=df_lc_bo["평균지표"].apply(fmt_hms),
                    hovertemplate="<b>%{x}</b><br>평균LT: %{text}<extra></extra>"
                ))
                fig4.update_layout(**base_layout(300,""))
                st.plotly_chart(fig4, use_container_width=True)
            card_close()


# ══════════════════════════════════════════════
# ★ 신규 페이지 C3: 멀티채널 효율
# ══════════════════════════════════════════════
def page_multichannel(phone, chat, board):
    section_title("C3. 멀티채널 vs 단일채널 상담사 효율 비교")

    dfs = []
    if not phone.empty:
        ph_resp = phone[phone["응대여부"]=="응대"][["상담사명","AHT(초)","대기시간(초)"]].copy()
        ph_resp.columns = ["상담사명","전화_AHT","전화_대기"]
        dfs.append(("전화", ph_resp))
    if not chat.empty:
        ch_resp = chat[chat["응대여부"]=="응대"][["상담사명","응답시간(초)","리드타임(초)"]].copy()
        ch_resp.columns = ["상담사명","채팅_대기","채팅_LT"]
        dfs.append(("채팅", ch_resp))
    if not board.empty:
        bo_resp = board[board["응대여부"]=="응대"][["상담사명","리드타임(초)"]].copy()
        bo_resp.columns = ["상담사명","게시판_LT"]
        dfs.append(("게시판", bo_resp))

    if not dfs:
        st.info("데이터가 없습니다.")
        return

    # 채널별 응대 건수 집계
    ch_counts = []
    for ch_lbl, sub in dfs:
        cnt = sub.groupby("상담사명").size().rename(f"{ch_lbl}_cnt")
        ch_counts.append(cnt)
    count_df = pd.concat(ch_counts, axis=1).fillna(0)
    count_df["활성채널수"] = (count_df > 0).sum(axis=1)
    count_df["멀티채널"] = count_df["활성채널수"] >= 2

    # 멀티채널 vs 단일채널 분류
    multi_agents  = set(count_df[count_df["멀티채널"]].index)
    single_agents = set(count_df[~count_df["멀티채널"]].index)

    # KPI 요약
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(kpi_card("전체 상담사", fmt_num(len(count_df)), unit="명"), unsafe_allow_html=True)
    with c2: st.markdown(kpi_card("멀티채널 상담사", fmt_num(len(multi_agents)), unit="명", accent="green"), unsafe_allow_html=True)
    with c3: st.markdown(kpi_card("단일채널 상담사", fmt_num(len(single_agents)), unit="명", accent="blue"), unsafe_allow_html=True)

    # 성과 비교
    def compare_metric(df_sub, metric_col, agent_set, label):
        filtered = df_sub[df_sub["상담사명"].isin(agent_set)]
        if filtered.empty or metric_col not in filtered.columns:
            return None
        return filtered[metric_col].mean()

    section_title("멀티채널 vs 단일채널 성과 비교")

    rows_cmp = []
    if not phone.empty:
        ph_resp = phone[phone["응대여부"]=="응대"]
        m_aht = compare_metric(ph_resp, "AHT(초)", multi_agents,  "멀티")
        s_aht = compare_metric(ph_resp, "AHT(초)", single_agents, "단일")
        if m_aht is not None and s_aht is not None:
            rows_cmp.append({"지표":"전화 AHT(초)","멀티채널":round(m_aht,1),"단일채널":round(s_aht,1),"차이":round(m_aht-s_aht,1)})
        m_vol = len(ph_resp[ph_resp["상담사명"].isin(multi_agents)])  / max(1, len(multi_agents))
        s_vol = len(ph_resp[ph_resp["상담사명"].isin(single_agents)]) / max(1, len(single_agents))
        rows_cmp.append({"지표":"전화 인당 응대수","멀티채널":round(m_vol,1),"단일채널":round(s_vol,1),"차이":round(m_vol-s_vol,1)})

    if not chat.empty:
        ch_resp = chat[chat["응대여부"]=="응대"]
        m_wait = compare_metric(ch_resp, "응답시간(초)", multi_agents,  "멀티")
        s_wait = compare_metric(ch_resp, "응답시간(초)", single_agents, "단일")
        if m_wait is not None and s_wait is not None:
            rows_cmp.append({"지표":"채팅 대기시간(초)","멀티채널":round(m_wait,1),"단일채널":round(s_wait,1),"차이":round(m_wait-s_wait,1)})

    if not board.empty:
        bo_resp = board[board["응대여부"]=="응대"]
        m_lt = compare_metric(bo_resp, "리드타임(초)", multi_agents,  "멀티")
        s_lt = compare_metric(bo_resp, "리드타임(초)", single_agents, "단일")
        if m_lt is not None and s_lt is not None:
            rows_cmp.append({"지표":"게시판 LT(초)","멀티채널":round(m_lt,1),"단일채널":round(s_lt,1),"차이":round(m_lt-s_lt,1)})

    if rows_cmp:
        cmp_df = pd.DataFrame(rows_cmp)
        card_open("멀티채널 vs 단일채널 성과 델타 요약")
        st.dataframe(cmp_df, use_container_width=True)
        download_csv_button(cmp_df, "multichannel_comparison.csv")
        card_close()

        # 시각화: 그룹 바
        if len(cmp_df) > 0:
            card_open("성과 비교 차트")
            fig_cmp = go.Figure()
            fig_cmp.add_trace(go.Bar(
                x=cmp_df["지표"], y=cmp_df["멀티채널"],
                name="멀티채널", marker_color=COLORS["success"], marker_line_width=0,
                hovertemplate="<b>%{x}</b><br>멀티채널: %{y:,.1f}<extra></extra>"
            ))
            fig_cmp.add_trace(go.Bar(
                x=cmp_df["지표"], y=cmp_df["단일채널"],
                name="단일채널", marker_color=COLORS["info"], marker_line_width=0,
                hovertemplate="<b>%{x}</b><br>단일채널: %{y:,.1f}<extra></extra>"
            ))
            fig_cmp.update_layout(barmode="group", **base_layout(300,""))
            st.plotly_chart(fig_cmp, use_container_width=True)
            card_close()

    # 상담사별 채널 활동 현황
    section_title("상담사별 채널 커버리지 (상위 30)")
    count_display = count_df.reset_index()
    count_display.columns = [c if c != "index" else "상담사명" for c in count_display.columns]
    if "상담사명" not in count_display.columns:
        count_display = count_display.rename(columns={count_display.columns[0]: "상담사명"})
    count_display = count_display[~count_display["상담사명"].isin(EXCLUDE_AGENTS)]
    count_display["멀티채널"] = count_display["멀티채널"].map({True:"✅ 멀티", False:"단일"})
    card_open("상담사별 채널 활동 건수")
    st.dataframe(count_display.head(30), use_container_width=True, height=360)
    download_csv_button(count_display, "multichannel_agents.csv")
    card_close()


# ══════════════════════════════════════════════
# ★ D1: VOC 반복 문의 근사
# ══════════════════════════════════════════════
def page_voc_d1(voc_df, unit):
    """VOC 페이지 내 D1 섹션"""
    if voc_df.empty or "대분류" not in voc_df.columns:
        st.info("반복 문의 분석에 필요한 대분류 데이터가 없습니다.")
        return

    # 동일 사업자명 + 대분류 + 일자 기준 2건 이상 = 추정 반복
    if "사업자명" not in voc_df.columns:
        st.info("사업자명 컬럼이 없습니다.")
        return

    tmp = voc_df.copy()
    tmp["일자_단"] = pd.to_datetime(tmp["일자"], errors="coerce").dt.date
    grp = tmp.groupby(["사업자명","대분류","일자_단"]).size().reset_index(name="건수")
    repeat = grp[grp["건수"] >= 2].copy()
    repeat_total = repeat["건수"].sum()
    all_total    = len(tmp)
    repeat_rate  = repeat_total / all_total * 100 if all_total > 0 else 0.0

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(kpi_card("추정 반복 문의", fmt_num(repeat_total), unit="건", accent="orange"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card("반복 문의율", fmt_pct(repeat_rate), accent="red", reverse=True), unsafe_allow_html=True)

    st.markdown("""
    <div class="alert-card info">
      <span class="alert-icon">ℹ️</span>
      <span><b>정의:</b> 동일 사업자 + 동일 대분류 + 동일 날짜에 2건 이상 인입된 경우를 추정 반복 문의로 분류합니다.</span>
    </div>""", unsafe_allow_html=True)

    if repeat.empty:
        st.info("반복 문의가 감지되지 않았습니다.")
        return

    c1, c2 = st.columns(2)
    with c1:
        # 대분류별 반복 건수
        cat_rep = repeat.groupby("대분류")["건수"].sum().reset_index().sort_values("건수", ascending=False).head(10)
        card_open("반복 문의 TOP 대분류")
        fig = px.bar(cat_rep, x="건수", y="대분류", orientation="h",
                     color="건수",
                     color_continuous_scale=["#fef3c7","#f59e0b","#b45309"])
        fig.update_layout(**base_layout(280,""))
        fig.update_traces(marker_line_width=0)
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(fig, use_container_width=True)
        card_close()
    with c2:
        # 브랜드/사업자별 반복
        op_rep = repeat.groupby("사업자명")["건수"].sum().reset_index().sort_values("건수", ascending=False).head(10)
        card_open("반복 문의 TOP 사업자")
        fig2 = px.bar(op_rep, x="건수", y="사업자명", orientation="h",
                      color="건수",
                      color_continuous_scale=["#e0e7ff","#6366f1","#3730a3"])
        fig2.update_layout(**base_layout(280,""))
        fig2.update_traces(marker_line_width=0)
        fig2.update_coloraxes(showscale=False)
        st.plotly_chart(fig2, use_container_width=True)
        card_close()

    # 기간별 반복 추이
    pc = get_period_col(unit)
    if pc in tmp.columns:
        repeat_trend = tmp.merge(
            repeat[["사업자명","대분류","일자_단"]],
            on=["사업자명","대분류","일자_단"], how="inner"
        )
        trend_grp = repeat_trend.groupby(pc).size().reset_index(name="반복건수")
        card_open("반복 문의 기간별 추이")
        fig3 = go.Figure(go.Scatter(
            x=trend_grp[pc], y=trend_grp["반복건수"],
            mode="lines+markers",
            line=dict(color=COLORS["warning"], width=2.5, shape="spline", smoothing=0.8),
            marker=dict(size=5, color="#fff", line=dict(color=COLORS["warning"], width=2)),
            fill="tozeroy", fillcolor=hex_rgba(COLORS["warning"], 0.07),
            hovertemplate="<b>%{x}</b><br>반복 문의: %{y:,}건<extra></extra>"
        ))
        fig3.update_layout(**base_layout(260,""))
        st.plotly_chart(fig3, use_container_width=True)
        card_close()

    download_csv_button(repeat, "repeat_contact.csv")


# ══════════════════════════════════════════════
# ★ D2: 대분류×중분류 × 처리시간 히트맵
# ══════════════════════════════════════════════
def page_voc_d2(phone, chat, board):
    """VOC 페이지 내 D2 섹션"""
    c1, c2 = st.columns(2)
    with c1:
        ch_d2 = st.selectbox("채널 선택", ["전화(AHT)","채팅(대기시간)","게시판(LT)"], key="d2_ch")
    with c2:
        top_n = st.slider("표시 카테고리 수 (대분류 기준)", 3, 15, 8, key="d2_topn")

    if ch_d2 == "전화(AHT)":
        df_d2 = phone[phone["응대여부"]=="응대"].copy() if not phone.empty else pd.DataFrame()
        metric_col = "AHT(초)"
        metric_label = "평균 AHT(초)"
    elif ch_d2 == "채팅(대기시간)":
        df_d2 = chat[chat["응대여부"]=="응대"].copy() if not chat.empty else pd.DataFrame()
        metric_col = "응답시간(초)"
        metric_label = "평균 대기(초)"
    else:
        df_d2 = board[board["응대여부"]=="응대"].copy() if not board.empty else pd.DataFrame()
        metric_col = "리드타임(초)"
        metric_label = "평균 LT(초)"

    if df_d2.empty or "대분류" not in df_d2.columns or "중분류" not in df_d2.columns:
        st.info("대분류/중분류 데이터가 없습니다.")
        return
    if metric_col not in df_d2.columns:
        st.info(f"{metric_col} 컬럼이 없습니다.")
        return

    # 상위 N 대분류 추출
    top_cats = df_d2.groupby("대분류").size().nlargest(top_n).index.tolist()
    df_filtered = df_d2[df_d2["대분류"].isin(top_cats)]

    pivot = df_filtered.pivot_table(
        index="대분류", columns="중분류",
        values=metric_col, aggfunc="mean"
    ).round(0)

    if pivot.empty:
        st.info("히트맵 생성에 충분한 데이터가 없습니다.")
        return

    card_open(f"대분류 × 중분류 × {metric_label} 히트맵", f"채널: {ch_d2} | 상위 {top_n}개 대분류")
    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.astype(str).tolist(),
        y=pivot.index.astype(str).tolist(),
        colorscale=[
            [0,   "#f0fdf4"],
            [0.3, "#bbf7d0"],
            [0.6, "#f59e0b"],
            [1.0, "#dc2626"]
        ],
        showscale=True,
        colorbar=dict(
            title=dict(text=metric_label, font=dict(size=11)),
            thickness=10, len=0.8,
            tickfont=dict(size=10, color="#94a3b8"),
            outlinewidth=0
        ),
        hovertemplate=f"대분류: <b>%{{y}}</b><br>중분류: <b>%{{x}}</b><br>{metric_label}: <b>%{{z:.0f}}</b><extra></extra>",
        text=pivot.values.astype(str),
        texttemplate="%{z:.0f}",
        textfont=dict(size=9, color="#374151"),
    ))
    h = max(320, len(pivot.index) * 36 + 80)
    lo = base_layout(h, "")
    lo["xaxis"]["tickangle"] = -30
    lo["xaxis"]["automargin"] = True
    lo["yaxis"]["automargin"] = True
    fig.update_layout(**lo)
    st.plotly_chart(fig, use_container_width=True)
    card_close()


# ══════════════════════════════════════════════
# ★ D3: 신규/급증 VOC 탐지
# ══════════════════════════════════════════════
def page_voc_d3(voc_df):
    """VOC 페이지 내 D3 섹션"""
    if voc_df.empty or "소분류" not in voc_df.columns:
        st.info("소분류 데이터가 없습니다.")
        return

    growth_threshold = st.slider(
        "급증 기준 (전주 대비 증가율 %)", 30, 200, 50, 10,
        key="d3_growth"
    )

    tmp = voc_df.copy()
    tmp["일자"] = pd.to_datetime(tmp["일자"], errors="coerce")
    tmp["주차"] = tmp["일자"] - pd.to_timedelta(tmp["일자"].dt.dayofweek, unit="D")
    tmp["주차"] = pd.to_datetime(tmp["주차"].dt.date)

    weeks = sorted(tmp["주차"].dropna().unique())
    if len(weeks) < 2:
        st.info("주차 비교를 위해 최소 2주 이상의 데이터가 필요합니다.")
        return

    curr_week = weeks[-1]
    prev_week = weeks[-2]

    curr_df = tmp[tmp["주차"] == curr_week]
    prev_df = tmp[tmp["주차"] == prev_week]

    curr_cnt = curr_df.groupby("소분류").size().rename("이번주")
    prev_cnt = prev_df.groupby("소분류").size().rename("전주")

    cmp = pd.concat([curr_cnt, prev_cnt], axis=1).fillna(0)
    cmp["증가율(%)"] = np.where(
        cmp["전주"] > 0,
        ((cmp["이번주"] - cmp["전주"]) / cmp["전주"] * 100).round(1),
        np.nan
    )

    # 신규 출현 (전주 0, 이번주 > 0)
    new_voc = cmp[(cmp["전주"] == 0) & (cmp["이번주"] > 0)].copy()
    new_voc["유형"] = "🆕 신규"

    # 급증 (증가율 >= threshold)
    surge_voc = cmp[(cmp["전주"] > 0) & (cmp["증가율(%)"] >= growth_threshold)].copy()
    surge_voc["유형"] = f"🔺 급증(+{growth_threshold}%↑)"

    combined = pd.concat([new_voc, surge_voc]).reset_index()
    combined.columns = ["소분류","이번주","전주","증가율(%)","유형"]
    combined = combined.sort_values("이번주", ascending=False)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(kpi_card("신규 출현 소분류", fmt_num(len(new_voc)), unit="개", accent="blue"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card(f"급증 소분류(+{growth_threshold}%↑)", fmt_num(len(surge_voc)), unit="개", accent="red"), unsafe_allow_html=True)

    st.markdown(f"""
    <div class="alert-card info">
      <span class="alert-icon">📅</span>
      <span>비교 기준: <b>이번주</b> ({str(curr_week)[:10]}) vs <b>전주</b> ({str(prev_week)[:10]})</span>
    </div>""", unsafe_allow_html=True)

    if combined.empty:
        st.markdown("""
        <div class="alert-card success">
          <span class="alert-icon">✅</span>
          <span>신규 또는 급증 VOC 유형이 감지되지 않았습니다.</span>
        </div>""", unsafe_allow_html=True)
        return

    card_open("신규 & 급증 VOC 패널")
    st.dataframe(combined, use_container_width=True, height=320)
    download_csv_button(combined, "emerging_voc.csv")
    card_close()

    # 채널/브랜드 교차
    if "채널" in voc_df.columns:
        curr_full = tmp[tmp["주차"] == curr_week]
        new_cats  = set(new_voc.index.tolist()) | set(surge_voc.index.tolist())
        if new_cats:
            curr_new = curr_full[curr_full["소분류"].isin(new_cats)]
            if not curr_new.empty:
                card_open("신규/급증 VOC 채널 × 브랜드 분포")
                for grp_col in ["채널","브랜드","사업자명"]:
                    if grp_col in curr_new.columns:
                        g = curr_new.groupby(grp_col).size().reset_index(name="건수").sort_values("건수", ascending=False).head(10)
                        st.markdown(f"**{grp_col}별:**")
                        fig_g = px.bar(g, x=grp_col, y="건수",
                                       color="건수",
                                       color_continuous_scale=["#e0e7ff","#6366f1","#3730a3"])
                        fig_g.update_layout(**base_layout(200,""))
                        fig_g.update_traces(marker_line_width=0)
                        fig_g.update_coloraxes(showscale=False)
                        st.plotly_chart(fig_g, use_container_width=True)
                card_close()


# ══════════════════════════════════════════════
# ★ E1: 게시판 근무외 비율 추이
# ══════════════════════════════════════════════
def page_board_e1(board, unit):
    """Board 페이지 내 E1 섹션"""
    if board.empty:
        return
    resp = board[board["응대여부"]=="응대"]
    if resp.empty or "근무외리드타임(초)" not in resp.columns:
        st.info("근무외 리드타임 데이터가 없습니다.")
        return

    pc = get_period_col(unit)
    if pc not in resp.columns:
        return

    grp = resp.groupby(pc).agg(
        근무내합=("근무내리드타임(초)","sum"),
        근무외합=("근무외리드타임(초)","sum"),
    ).reset_index()
    grp["전체합"] = grp["근무내합"] + grp["근무외합"]
    grp["근무외비율(%)"] = np.where(
        grp["전체합"] > 0,
        (grp["근무외합"] / grp["전체합"] * 100).round(1),
        0.0
    )

    c1, c2 = st.columns(2)
    with c1:
        card_open("근무외 처리 비율 추이", f"기간 단위: {unit}")
        fig = go.Figure(go.Scatter(
            x=grp[pc], y=grp["근무외비율(%)"],
            mode="lines+markers",
            line=dict(color=COLORS["danger"], width=2.5, shape="spline", smoothing=0.8),
            marker=dict(size=5, color="#fff", line=dict(color=COLORS["danger"], width=2)),
            fill="tozeroy", fillcolor=hex_rgba(COLORS["danger"], 0.07),
            hovertemplate="<b>%{x}</b><br>근무외 비율: %{y:.1f}%<extra></extra>"
        ))
        lo = base_layout(280,"")
        lo["yaxis"]["ticksuffix"] = "%"
        lo["yaxis"]["range"] = [0, 105]
        fig.update_layout(**lo)
        st.plotly_chart(fig, use_container_width=True)
        card_close()

    with c2:
        # 요일별 근무외 비율
        WEEKDAY_KR = {0:"월",1:"화",2:"수",3:"목",4:"금",5:"토",6:"일"}
        WEEKDAY_ORDER = ["월","화","수","목","금","토","일"]
        if "접수일시" in resp.columns:
            tmp = resp.copy()
            tmp = tmp[tmp["접수일시"].notna()]
            tmp["요일"] = tmp["접수일시"].dt.dayofweek.map(WEEKDAY_KR)
            dow_grp = tmp.groupby("요일").agg(
                근무내합=("근무내리드타임(초)","sum"),
                근무외합=("근무외리드타임(초)","sum"),
            ).reset_index()
            dow_grp["근무외비율(%)"] = np.where(
                (dow_grp["근무내합"]+dow_grp["근무외합"]) > 0,
                dow_grp["근무외합"] / (dow_grp["근무내합"]+dow_grp["근무외합"]) * 100,
                0.0
            ).round(1)
            dow_grp = dow_grp.set_index("요일").reindex(
                [d for d in WEEKDAY_ORDER if d in dow_grp["요일"].values]
            ).reset_index()
            card_open("요일별 근무외 처리 비율", "주말/공휴일 의존도 파악")
            fig2 = px.bar(
                dow_grp, x="요일", y="근무외비율(%)",
                color="근무외비율(%)",
                color_continuous_scale=["#d1fae5","#f59e0b","#ef4444"]
            )
            lo2 = base_layout(280,"")
            lo2["yaxis"]["ticksuffix"] = "%"
            fig2.update_layout(**lo2)
            fig2.update_traces(marker_line_width=0)
            fig2.update_coloraxes(showscale=False)
            st.plotly_chart(fig2, use_container_width=True)
            card_close()


# ══════════════════════════════════════════════
# ★ E2: 게시판 접수 요일/시간대별 리드타임 패턴
# ══════════════════════════════════════════════
def page_board_e2(board):
    """Board 페이지 내 E2 섹션"""
    if board.empty or "접수일시" not in board.columns:
        return
    resp = board[board["응대여부"]=="응대"].copy()
    resp = resp[resp["접수일시"].notna()]
    if resp.empty:
        return

    WEEKDAY_KR = {0:"월",1:"화",2:"수",3:"목",4:"금",5:"토",6:"일"}
    WEEKDAY_ORDER = ["월","화","수","목","금","토","일"]
    resp["접수요일"] = resp["접수일시"].dt.dayofweek.map(WEEKDAY_KR)
    resp["접수시간대"] = resp["접수일시"].dt.hour
    resp["시간버킷"] = pd.cut(
        resp["접수시간대"],
        bins=[0,6,10,14,18,22,24],
        labels=["심야(0-6시)","오전초(6-10시)","오전(10-14시)","오후(14-18시)","저녁(18-22시)","밤(22-24시)"],
        right=False
    )

    c1, c2 = st.columns(2)
    with c1:
        card_open("접수 요일별 평균 전체 LT", "요일에 따른 처리 지연 패턴")
        dow_lt = resp.groupby("접수요일")["리드타임(초)"].mean().round(0).reset_index()
        dow_lt.columns = ["요일","평균LT(초)"]
        existing = [d for d in WEEKDAY_ORDER if d in dow_lt["요일"].values]
        dow_lt = dow_lt.set_index("요일").reindex(existing).reset_index()
        dow_lt["표시"] = dow_lt["평균LT(초)"].apply(fmt_hms)
        fig = px.bar(
            dow_lt, x="요일", y="평균LT(초)",
            color="평균LT(초)",
            color_continuous_scale=["#d1fae5","#f59e0b","#dc2626"],
            text="표시"
        )
        fig.update_traces(textposition="outside", marker_line_width=0)
        lo = base_layout(280,"")
        fig.update_layout(**lo)
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(fig, use_container_width=True)
        card_close()

    with c2:
        card_open("접수 시간 버킷별 평균 전체 LT", "어떤 시간대 접수가 가장 오래 걸리나")
        bkt_lt = resp.groupby("시간버킷", observed=True)["리드타임(초)"].mean().round(0).reset_index()
        bkt_lt.columns = ["시간버킷","평균LT(초)"]
        bkt_lt["표시"] = bkt_lt["평균LT(초)"].apply(fmt_hms)
        fig2 = px.bar(
            bkt_lt, x="시간버킷", y="평균LT(초)",
            color="평균LT(초)",
            color_continuous_scale=["#d1fae5","#f59e0b","#dc2626"],
            text="표시"
        )
        fig2.update_traces(textposition="outside", marker_line_width=0)
        lo2 = base_layout(280,"")
        fig2.update_layout(**lo2)
        fig2.update_coloraxes(showscale=False)
        st.plotly_chart(fig2, use_container_width=True)
        card_close()

    # 요일 × 시간버킷 히트맵
    pivot_e2 = resp.pivot_table(
        index="접수요일", columns="시간버킷",
        values="리드타임(초)", aggfunc="mean"
    ).round(0)
    pivot_e2 = pivot_e2.reindex([d for d in WEEKDAY_ORDER if d in pivot_e2.index])

    if not pivot_e2.empty:
        card_open("요일 × 시간버킷 × 평균 LT 히트맵", "어두울수록 처리 지연 심각")
        fig3 = go.Figure(go.Heatmap(
            z=pivot_e2.values,
            x=[str(c) for c in pivot_e2.columns],
            y=pivot_e2.index.astype(str).tolist(),
            colorscale=[
                [0,   "#f0fdf4"],
                [0.4, "#fef3c7"],
                [0.7, "#fca5a5"],
                [1.0, "#b91c1c"]
            ],
            showscale=True,
            colorbar=dict(
                title=dict(text="평균LT(초)", font=dict(size=11)),
                thickness=10, len=0.8,
                tickfont=dict(size=10, color="#94a3b8"),
                outlinewidth=0
            ),
            hovertemplate="요일: <b>%{y}</b><br>시간대: <b>%{x}</b><br>평균LT: <b>%{z:.0f}초</b><extra></extra>"
        ))
        fig3.update_layout(**base_layout(320,""))
        st.plotly_chart(fig3, use_container_width=True)
        card_close()


# ══════════════════════════════════════════════
# ★ 신규 페이지 F1: 비용 시뮬레이터
# ══════════════════════════════════════════════
def page_cost_simulator(phone, chat, board):
    section_title("F1. 채널 비용 시뮬레이터 (시간 기반 프록시)")

    st.markdown("""
    <div class="alert-card warning">
      <span class="alert-icon">⚠️</span>
      <span><b>가정:</b> 처리시간(초)을 비용 프록시로 사용합니다.
      전화=AHT, 채팅=리드타임, 게시판=전체LT. 실제 비용은 인건비 단가를 별도 입력하여 산출하세요.</span>
    </div>""", unsafe_allow_html=True)

    # ── 현재 채널별 총 처리시간 ──────────────────────
    ph_resp = phone[phone["응대여부"]=="응대"] if not phone.empty else pd.DataFrame()
    ch_resp = chat[chat["응대여부"]=="응대"]   if not chat.empty  else pd.DataFrame()
    bo_resp = board[board["응대여부"]=="응대"] if not board.empty else pd.DataFrame()

    total_ph_sec = float(ph_resp["AHT(초)"].sum())         if not ph_resp.empty else 0.0
    total_ch_sec = float(ch_resp["리드타임(초)"].sum())    if not ch_resp.empty else 0.0
    total_bo_sec = float(bo_resp["리드타임(초)"].sum())    if not bo_resp.empty else 0.0

    avg_ph_aht   = float(ph_resp["AHT(초)"].mean())        if not ph_resp.empty else 0.0
    avg_ch_lt    = float(ch_resp["리드타임(초)"].mean())   if not ch_resp.empty else 0.0

    n_ph = len(ph_resp)
    n_ch = len(ch_resp)
    n_bo = len(bo_resp)

    col1, col2, col3 = st.columns(3)
    with col1: st.markdown(kpi_card("전화 총 처리시간", fmt_hms(total_ph_sec), accent="blue"),   unsafe_allow_html=True)
    with col2: st.markdown(kpi_card("채팅 총 처리시간", fmt_hms(total_ch_sec), accent="green"),  unsafe_allow_html=True)
    with col3: st.markdown(kpi_card("게시판 총 처리시간", fmt_hms(total_bo_sec), accent="orange"), unsafe_allow_html=True)

    # ── 단가 입력 ──────────────────────────────────
    section_title("인건비 단가 설정")
    c1, c2 = st.columns(2)
    with c1:
        hourly_rate = st.number_input(
            "시간당 비용 (원/시간)",
            min_value=1000, max_value=100000,
            value=15000, step=1000,
            key="cost_rate"
        )
    with c2:
        chat_concurrency_cost = st.slider(
            "채팅 동시처리 수 (비용 할인률 적용)", 1, 5, 2, 1,
            key="cost_conc"
        )

    rate_per_sec = hourly_rate / 3600

    cost_ph = total_ph_sec * rate_per_sec
    cost_ch = (total_ch_sec / chat_concurrency_cost) * rate_per_sec
    cost_bo = total_bo_sec * rate_per_sec
    cost_total = cost_ph + cost_ch + cost_bo

    section_title("현재 채널별 비용 추정")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(kpi_card("전화 비용",   f"{cost_ph/10000:.1f}", unit="만원", accent="blue"),   unsafe_allow_html=True)
    with c2: st.markdown(kpi_card("채팅 비용",   f"{cost_ch/10000:.1f}", unit="만원", accent="green"),  unsafe_allow_html=True)
    with c3: st.markdown(kpi_card("게시판 비용", f"{cost_bo/10000:.1f}", unit="만원", accent="orange"),  unsafe_allow_html=True)
    with c4: st.markdown(kpi_card("전체 비용",   f"{cost_total/10000:.1f}", unit="만원"),               unsafe_allow_html=True)

    # ── What-If 시뮬레이터 ─────────────────────────
    section_title("📐 What-If 시뮬레이션: 전화 → 채팅 전환 효과")

    st.markdown("""
    <div class="alert-card info">
      <span class="alert-icon">💡</span>
      <span>전화 인입의 일부를 채팅으로 전환했을 때 절감 가능한 총 처리시간 및 비용을 추정합니다.</span>
    </div>""", unsafe_allow_html=True)

    shift_pct = st.slider(
        "전화 → 채팅 전환 비율 (%)", 0, 100, 20, 5,
        key="cost_shift"
    )

    shifted_calls = int(n_ph * shift_pct / 100)
    saved_ph_sec  = shifted_calls * avg_ph_aht
    added_ch_sec  = shifted_calls * avg_ch_lt / chat_concurrency_cost

    net_saving_sec  = saved_ph_sec - added_ch_sec
    net_saving_cost = net_saving_sec * rate_per_sec

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(kpi_card("전환 콜 수", fmt_num(shifted_calls), unit="건", accent="blue"), unsafe_allow_html=True)
    with c2: st.markdown(kpi_card("전화 절감 시간", fmt_hms(saved_ph_sec), accent="green"), unsafe_allow_html=True)
    with c3: st.markdown(kpi_card("채팅 추가 시간", fmt_hms(added_ch_sec), accent="orange"), unsafe_allow_html=True)
    with c4:
        accent_net = "green" if net_saving_sec > 0 else "red"
        st.markdown(kpi_card(
            "순 절감 비용",
            f"{net_saving_cost/10000:.1f}",
            unit="만원",
            accent=accent_net
        ), unsafe_allow_html=True)

    # 시각화: 전환 비율별 절감 효과 곡선
    shift_range = list(range(0, 101, 5))
    savings_curve = []
    for sp in shift_range:
        sc = int(n_ph * sp / 100)
        sav = sc * avg_ph_aht - sc * avg_ch_lt / chat_concurrency_cost
        savings_curve.append({"전환율(%)": sp, "순절감시간(초)": sav, "순절감비용(만원)": sav * rate_per_sec / 10000})
    sc_df = pd.DataFrame(savings_curve)

    card_open("전환 비율별 순 절감 비용 곡선")
    fig_sc = go.Figure()
    fig_sc.add_trace(go.Scatter(
        x=sc_df["전환율(%)"], y=sc_df["순절감비용(만원)"],
        mode="lines+markers",
        line=dict(color=COLORS["success"], width=2.5, shape="spline", smoothing=0.8),
        marker=dict(size=5, color="#fff", line=dict(color=COLORS["success"], width=2)),
        fill="tozeroy", fillcolor=hex_rgba(COLORS["success"], 0.06),
        hovertemplate="전환율: <b>%{x}%</b><br>순절감: <b>%{y:.1f}만원</b><extra></extra>"
    ))
    # 현재 선택 지점 강조
    fig_sc.add_vline(
        x=shift_pct,
        line=dict(color=COLORS["primary"], width=2, dash="dash"),
        annotation_text=f"현재 {shift_pct}%",
        annotation_font=dict(size=11, color=COLORS["primary"])
    )
    lo_sc = base_layout(280,"")
    lo_sc["xaxis"]["ticksuffix"] = "%"
    lo_sc["yaxis"]["title"] = dict(text="순 절감 비용(만원)", font=dict(size=11))
    fig_sc.update_layout(**lo_sc)
    st.plotly_chart(fig_sc, use_container_width=True)
    card_close()


# ══════════════════════════════════════════════
# ★ 신규 페이지 F2: 팀 × 채널 매트릭스
# ══════════════════════════════════════════════
def page_team_channel_matrix(phone, chat, board):
    section_title("F2. 팀 × 채널 커버리지 매트릭스")

    # 팀 목록 수집
    teams = set()
    for df in [phone, chat, board]:
        if not df.empty and "팀명" in df.columns:
            teams.update(df["팀명"].dropna().unique())
    teams = sorted(teams)

    if not teams:
        st.info("팀명 데이터가 없습니다.")
        return

    metric_opt = st.selectbox(
        "표시 지표",
        ["응대건수","응대율(%)","평균처리시간(초)"],
        key="matrix_metric"
    )

    def team_channel_agg(df, ch_label, time_col):
        if df.empty or "팀명" not in df.columns:
            return pd.DataFrame()
        tmp = df.copy()
        total = tmp.groupby("팀명").size().rename("전체")
        resp_cnt = tmp[tmp["응대여부"]=="응대"].groupby("팀명").size().rename("응대")
        out = pd.concat([total, resp_cnt], axis=1).fillna(0).reset_index()
        out["응대율(%)"] = (out["응대"] / out["전체"] * 100).round(1)
        if time_col and time_col in tmp.columns:
            mean_t = tmp[tmp["응대여부"]=="응대"].groupby("팀명")[time_col].mean().rename("평균처리시간(초)").round(1)
            out = out.merge(mean_t, on="팀명", how="left")
        else:
            out["평균처리시간(초)"] = 0.0
        out["채널"] = ch_label
        return out

    ch_data = []
    ch_data.append(team_channel_agg(phone, "전화", "AHT(초)"))
    ch_data.append(team_channel_agg(chat,  "채팅", "응답시간(초)"))
    ch_data.append(team_channel_agg(board, "게시판","리드타임(초)"))
    ch_all = pd.concat([d for d in ch_data if not d.empty], ignore_index=True)

    if ch_all.empty:
        st.info("매트릭스 생성에 필요한 데이터가 없습니다.")
        return

    # 피벗 테이블
    if metric_opt == "응대건수":
        val_col = "응대"
    elif metric_opt == "응대율(%)":
        val_col = "응대율(%)"
    else:
        val_col = "평균처리시간(초)"

    pivot_mat = ch_all.pivot_table(
        index="팀명", columns="채널",
        values=val_col, aggfunc="first"
    ).fillna(0)

    # 히트맵 렌더링
    card_open("팀 × 채널 매트릭스 히트맵", f"지표: {metric_opt}")

    if metric_opt == "응대건수":
        cs = [[0,"#f8fafc"],[0.4,"#bfdbfe"],[0.7,"#6366f1"],[1.0,"#1e1b4b"]]
    elif metric_opt == "응대율(%)":
        cs = [[0,"#fee2e2"],[0.5,"#fef3c7"],[1.0,"#d1fae5"]]
    else:
        cs = [[0,"#d1fae5"],[0.5,"#fef3c7"],[1.0,"#fee2e2"]]

    fig_mat = go.Figure(go.Heatmap(
        z=pivot_mat.values,
        x=pivot_mat.columns.tolist(),
        y=pivot_mat.index.tolist(),
        colorscale=cs,
        showscale=True,
        colorbar=dict(
            title=dict(text=metric_opt, font=dict(size=11)),
            thickness=10, len=0.8,
            tickfont=dict(size=10, color="#94a3b8"),
            outlinewidth=0
        ),
        text=pivot_mat.values.round(1).astype(str),
        texttemplate="%{z:.1f}",
        textfont=dict(size=11, color="#374151"),
        hovertemplate=f"팀: <b>%{{y}}</b><br>채널: <b>%{{x}}</b><br>{metric_opt}: <b>%{{z:.1f}}</b><extra></extra>"
    ))
    h = max(300, len(pivot_mat) * 38 + 80)
    lo_mat = base_layout(h, "")
    lo_mat["xaxis"]["side"] = "top"
    fig_mat.update_layout(**lo_mat)
    st.plotly_chart(fig_mat, use_container_width=True)
    card_close()

    # 정렬 가능한 상세 테이블
    section_title("팀 × 채널 상세 테이블")
    sort_col = st.selectbox("정렬 기준", ch_all.columns.tolist(), key="matrix_sort")
    card_open("상세 데이터 (정렬 가능)")
    st.dataframe(
        ch_all.sort_values(sort_col, ascending=False),
        use_container_width=True, height=400
    )
    download_csv_button(ch_all, "team_channel_matrix.csv")
    card_close()

    # 병목 팀 알림
    section_title("⚑ 병목 팀 감지")
    bottleneck = []
    for team in teams:
        t_data = ch_all[ch_all["팀명"] == team]
        for _, row in t_data.iterrows():
            if row["응대율(%)"] < 70:
                bottleneck.append(f"<span class='flag-badge red'>🔴 {team} ({row['채널']}): 응대율 {row['응대율(%)']:.1f}%</span>")
    if bottleneck:
        st.markdown(
            "<div style='display:flex;flex-wrap:wrap;gap:6px;margin-top:8px;'>" +
            "".join(bottleneck) + "</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown("""
        <div class="alert-card success">
          <span class="alert-icon">✅</span>
          <span>응대율 70% 미만 병목 팀이 감지되지 않았습니다.</span>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# 사이드바 렌더링 (기존 구조 유지 + 신규 메뉴 추가)
# ══════════════════════════════════════════════
def render_sidebar(phone_raw, chat_raw, board_raw):
    with st.sidebar:
        st.markdown("""
        <div style="
            padding: 20px 16px 16px;
            border-bottom: 1px solid rgba(255,255,255,0.07);
            margin-bottom: 14px;
        ">
            <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;">
                <div style="
                    width:28px;height:28px;
                    background:linear-gradient(135deg,#6366f1,#8b5cf6);
                    border-radius:8px;display:flex;align-items:center;
                    justify-content:center;font-size:14px;flex-shrink:0;
                ">📞</div>
                <div style="font-size:15px;font-weight:800;color:#fff;letter-spacing:-0.03em;">CC OPS</div>
            </div>
            <div style="
                font-size:10.5px;color:rgba(148,163,184,0.8);
                font-weight:500;padding-left:36px;letter-spacing:0.01em;
            ">Contact Center Analytics</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔄  데이터 새로고침", key="btn_refresh"):
            st.cache_data.clear()
            st.rerun()

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        st.markdown("""
        <div style="font-size:10px;font-weight:800;color:rgba(148,163,184,0.6);
        text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px;margin-top:4px;">기간 단위</div>
        """, unsafe_allow_html=True)
        unit = st.radio("기간 단위", ["일별","주별","월별"],
                        horizontal=True, label_visibility="collapsed")
        month_range = 3
        if unit == "월별":
            month_range = st.slider("추이 범위(개월)", 1, 6, 3)

        st.markdown("""
        <div style="margin-top:14px;font-size:10px;font-weight:800;
        color:rgba(148,163,184,0.6);text-transform:uppercase;
        letter-spacing:0.08em;margin-bottom:8px;">날짜 빠른 선택</div>
        """, unsafe_allow_html=True)

        today = date.today()
        c1, c2 = st.columns(2)
        with c1:
            if st.button("7일",    key="d7"):
                st.session_state["ds"] = today - timedelta(days=6)
                st.session_state["de"] = today
        with c2:
            if st.button("30일",   key="d30"):
                st.session_state["ds"] = today - timedelta(days=29)
                st.session_state["de"] = today
        c3, c4 = st.columns(2)
        with c3:
            if st.button("이번달", key="dmonth"):
                st.session_state["ds"] = today.replace(day=1)
                st.session_state["de"] = today
        with c4:
            if st.button("전체",   key="dall"):
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

        all_ops = sorted(set(
            list(phone_raw["사업자명"].dropna().unique() if "사업자명" in phone_raw.columns else []) +
            list(chat_raw["사업자명"].dropna().unique()  if "사업자명" in chat_raw.columns  else []) +
            list(board_raw["사업자명"].dropna().unique() if "사업자명" in board_raw.columns else [])
        ))
        st.markdown("""
        <div style="margin-top:14px;font-size:10px;font-weight:800;
        color:rgba(148,163,184,0.6);text-transform:uppercase;
        letter-spacing:0.08em;margin-bottom:5px;">사업자 필터</div>
        """, unsafe_allow_html=True)
        sel_ops = st.multiselect("사업자", all_ops, default=[],
                                 label_visibility="collapsed", key="sel_ops")

        all_brands = sorted(set(
            list(phone_raw["브랜드"].dropna().unique() if "브랜드" in phone_raw.columns else []) +
            list(chat_raw["브랜드"].dropna().unique()  if "브랜드" in chat_raw.columns  else []) +
            list(board_raw["브랜드"].dropna().unique() if "브랜드" in board_raw.columns else [])
        ))
        st.markdown("""
        <div style="margin-top:10px;font-size:10px;font-weight:800;
        color:rgba(148,163,184,0.6);text-transform:uppercase;
        letter-spacing:0.08em;margin-bottom:5px;">브랜드 필터</div>
        """, unsafe_allow_html=True)
        sel_brands = st.multiselect("브랜드", all_brands, default=[],
                                    label_visibility="collapsed", key="sel_brands")

        st.markdown("""
        <div style="margin-top:16px;padding-top:14px;
        border-top:1px solid rgba(255,255,255,0.07);"></div>
        """, unsafe_allow_html=True)

        menu = st.session_state.get("menu", "전체 현황")

        icon_map = {
            "전체 현황":       "🏠",
            "VOC 인입 분석":   "📋",
            "사업자 현황":     "🏢",
            "전화 현황":       "📞",
            "전화 상담사":     "👤",
            "채팅 현황":       "💬",
            "채팅 상담사":     "👤",
            "게시판 현황":     "📝",
            "게시판 상담사":   "👤",
            "상담사 종합":     "📊",
            # 신규
            "SLA 위반 분석":   "🚨",
            "이상치 탐지":     "🔍",
            "연속 미응대":     "⚡",
            "요일×시간대 패턴":"🗓️",
            "변동성 지수":     "📈",
            "인력 산정":       "👥",
            "AHT 분산분석":   "📉",
            "학습곡선":        "📚",
            "멀티채널 효율":   "🔄",
            "비용 시뮬레이터": "💰",
            "팀×채널 매트릭스":"🧩",
        }

        for group, items in MENU_GROUPS.items():
            st.markdown(f"""
            <div style="margin:12px 0 5px 4px;font-size:10px;font-weight:800;
            color:rgba(148,163,184,0.5);text-transform:uppercase;letter-spacing:0.08em;">
            {group}</div>
            """, unsafe_allow_html=True)
            for item in items:
                is_active = (menu == item)
                wrap_cls  = "sidebar-active" if is_active else ""
                icon      = icon_map.get(item, "•")
                label     = f"{icon}  {item}"
                st.markdown(f"<div class='{wrap_cls}'>", unsafe_allow_html=True)
                if st.button(label, key=f"m_{item}"):
                    st.session_state["menu"] = item
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='height:60px'></div>", unsafe_allow_html=True)

    return unit, month_range, date_start, date_end, sel_ops, sel_brands


# ══════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════
def main():
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

    if all(len(df) == 0 for df in [phone_f, chat_f, board_f]):
        st.markdown("""
        <div class="empty-state">
            <div style="width:56px;height:56px;background:rgba(99,102,241,0.08);
            border-radius:16px;display:flex;align-items:center;justify-content:center;
            font-size:28px;border:1px solid rgba(99,102,241,0.15);">📊</div>
            <div style="font-size:18px;font-weight:800;color:#0f172a;letter-spacing:-0.025em;">
                데이터 연결 필요
            </div>
            <div style="font-size:13px;color:#64748b;font-weight:400;line-height:1.6;max-width:320px;">
                Google Sheets에 데이터를 입력하거나<br>필터 조건을 확인해주세요.
            </div>
            <div style="font-size:11px;color:#94a3b8;background:#f8fafc;padding:6px 14px;
            border-radius:9999px;font-weight:600;border:1px solid rgba(226,232,240,0.8);">
            SHEET_ID 및 GID_MAP 설정을 확인하세요</div>
        </div>
        """, unsafe_allow_html=True)
        return

    menu = st.session_state.get("menu", "전체 현황")

    # ── 기존 라우팅 ──────────────────────────────
    if menu == "전체 현황":
        page_overview(
            phone_f, chat_f, board_f, unit, month_range, date_start, date_end,
            phone_all=phone_m, chat_all=chat_m, board_all=board_m
        )
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

    # ── 신규 라우팅 ──────────────────────────────
    elif menu == "SLA 위반 분석":
        page_sla_breach(phone_f, chat_f, board_f, unit)
    elif menu == "이상치 탐지":
        page_outlier(phone_f, chat_f, board_f)
    elif menu == "연속 미응대":
        page_burst(phone_f, chat_f)
    elif menu == "요일×시간대 패턴":
        page_weekday_heatmap(phone_f, chat_f)
    elif menu == "변동성 지수":
        page_volatility(phone_f, chat_f, board_f, unit)
    elif menu == "인력 산정":
        page_staffing(phone_f, chat_f)
    elif menu == "AHT 분산분석":
        page_aht_dispersion(phone_f, chat_f)
    elif menu == "학습곡선":
        page_learning_curve(phone_f, chat_f, board_f)
    elif menu == "멀티채널 효율":
        page_multichannel(phone_f, chat_f, board_f)
    elif menu == "비용 시뮬레이터":
        page_cost_simulator(phone_f, chat_f, board_f)
    elif menu == "팀×채널 매트릭스":
        page_team_channel_matrix(phone_f, chat_f, board_f)


if __name__ == "__main__":
    main()
