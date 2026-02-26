# ═══════════════════════════════════════════════════════════════════
#  Contact Center Operational Dashboard  ·  Enterprise Edition v1.1
#  Multi-Channel (Phone / Chat / Board) Analytics
#  + 기간 단위별 증감분석 / 추이 차트
# ═══════════════════════════════════════════════════════════════════
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import holidays as holidays_lib

# ─────────────────────────────────────────────
# Google Sheets IDs
# ─────────────────────────────────────────────
SHEET_ID = st.secrets["SHEET_ID"]
GID_MAP  = {
    "agent": "0",
    "phone": "754152852",
    "chat":  "1359982286",
    "board": "677677090",
}

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Contact Center OPS",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
* { font-family:'Inter',sans-serif !important; }
.stApp { background:#F5F6F8; }
[data-testid="stSidebar"] {
    background:linear-gradient(180deg,#1a1a2e 0%,#16213e 55%,#0f3460 100%) !important;
}
[data-testid="stSidebar"] > div:first-child { padding:16px 14px 20px !important; }
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] .stMarkdown p { color:#dde3ee !important; font-size:12px !important; }
.sb-group {
    font-size:10px !important; font-weight:700 !important;
    letter-spacing:1.2px !important; text-transform:uppercase !important;
    color:#7a9cc6 !important; padding:10px 2px 4px !important; display:block !important;
}
[data-testid="stSidebar"] .stButton > button {
    width:100% !important; background:rgba(255,255,255,0.05) !important;
    color:#ccd6f0 !important; border:1px solid rgba(255,255,255,0.08) !important;
    border-radius:8px !important; padding:8px 12px !important; margin:2px 0 !important;
    text-align:left !important; font-size:12px !important; font-weight:500 !important;
    transition:all 0.18s ease !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background:rgba(52,152,219,0.30) !important;
    border-color:rgba(52,152,219,0.5) !important; color:#fff !important;
}
[data-testid="stSidebar"] hr { border-color:rgba(255,255,255,0.10) !important; margin:8px 0 !important; }
.kpi-card {
    background:#fff; border-radius:16px; padding:20px 24px;
    box-shadow:0 2px 12px rgba(0,0,0,.06);
    border-top:3px solid #3b82f6; margin-bottom:12px;
}
.kpi-label { font-size:11px; color:#94a3b8; font-weight:600;
             letter-spacing:0.6px; text-transform:uppercase; margin-bottom:6px; }
.kpi-value { font-size:28px; font-weight:800; color:#0f172a; line-height:1.1; }
.kpi-sub   { font-size:11px; color:#94a3b8; margin-top:4px; }
.kpi-delta-up   { font-size:12px; font-weight:600; color:#ef4444; margin-top:4px; }
.kpi-delta-down { font-size:12px; font-weight:600; color:#22c55e; margin-top:4px; }
.kpi-delta-neu  { font-size:12px; font-weight:600; color:#94a3b8; margin-top:4px; }
.section-title {
    font-size:14px; font-weight:700; color:#0f172a;
    margin:24px 0 12px; padding-bottom:8px;
    border-bottom:2px solid #e2e8f0;
}
.page-title { font-size:24px; font-weight:800; color:#0f172a; margin-bottom:2px; }
.page-sub   { font-size:13px; color:#64748b; margin-bottom:20px; }
.period-badge {
    display:inline-block; background:#eff6ff; color:#3b82f6;
    border-radius:6px; padding:2px 10px; font-size:11px;
    font-weight:600; margin-left:8px;
}
#MainMenu{display:none;} footer{display:none;}
::-webkit-scrollbar{width:5px;height:5px;}
::-webkit-scrollbar-track{background:#F5F6F8;}
::-webkit-scrollbar-thumb{background:#cbd5e1;border-radius:3px;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────
WORK_START = 10
WORK_END   = 18
COLORS = [
    "#3b82f6","#22c55e","#f97316","#ef4444","#8b5cf6",
    "#06b6d4","#eab308","#10b981","#f43f5e","#6366f1",
    "#84cc16","#0ea5e9","#a855f7","#14b8a6","#f59e0b",
]
TENURE_GROUPS = [
    (14,   "신입1"),(30,  "신입2"),(60,   "신입3"),
    (90,   "신입4"),(180, "신입5"),(365,  "신입6"),
    (548,  "기존1"),(730, "기존2"),(1095, "기존3"),
    (1460, "기존4"),(9999,"기존5"),
]
MENU_GROUPS = {
    "Overview": ["전체 현황"],
    "Phone":    ["전화 현황","전화 상담사"],
    "Chat":     ["채팅 현황","채팅 상담사"],
    "Board":    ["게시판 현황","게시판 상담사"],
    "Agent":    ["상담사 종합"],
}

# ─────────────────────────────────────────────
# PERIOD UTILITIES
# ─────────────────────────────────────────────
def get_period_col(unit):
    return {"일별":"일자_d","주별":"주차","월별":"월"}.get(unit,"일자_d")

def assign_period_cols(df):
    df = df.copy()
    df["일자_d"] = df["일자"].dt.strftime("%Y-%m-%d")
    df["주차"]   = df["일자"].dt.to_period("W").apply(
        lambda p: p.start_time.strftime("%Y-%m-%d"))
    df["월"]     = df["일자"].dt.to_period("M").apply(
        lambda p: p.strftime("%Y-%m"))
    return df

def get_prev_period(unit, current_label):
    try:
        if unit == "일별":
            d = datetime.strptime(str(current_label), "%Y-%m-%d")
            return (d - timedelta(days=1)).strftime("%Y-%m-%d")
        elif unit == "주별":
            d = datetime.strptime(str(current_label), "%Y-%m-%d")
            return (d - timedelta(weeks=1)).strftime("%Y-%m-%d")
        elif unit == "월별":
            d = datetime.strptime(str(current_label) + "-01", "%Y-%m-%d")
            prev = d - timedelta(days=1)
            return prev.strftime("%Y-%m")
    except:
        return None

def get_yoy_period(unit, current_label):
    try:
        if unit == "일별":
            d = datetime.strptime(str(current_label), "%Y-%m-%d")
            return (d - timedelta(weeks=52)).strftime("%Y-%m-%d")
        elif unit == "주별":
            d = datetime.strptime(str(current_label), "%Y-%m-%d")
            return (d - timedelta(weeks=52)).strftime("%Y-%m-%d")
        elif unit == "월별":
            d = datetime.strptime(str(current_label) + "-01", "%Y-%m-%d")
            return d.replace(year=d.year-1).strftime("%Y-%m")
    except:
        return None

def get_chart_range(unit, month_range=3):
    today = datetime.today()
    if unit == "일별":
        return today - timedelta(days=89)
    elif unit == "주별":
        return today - timedelta(weeks=12)
    elif unit == "월별":
        result = today.replace(day=1)
        for _ in range(month_range - 1):
            result = (result - timedelta(days=1)).replace(day=1)
        return result
    return today - timedelta(days=89)

def calc_delta(curr, prev):
    if prev is None or prev == 0 or pd.isnull(prev):
        return None
    return round((curr - prev) / abs(prev) * 100, 1)

# ─────────────────────────────────────────────
# TENURE / HOLIDAY / LEADTIME
# ─────────────────────────────────────────────
def get_tenure_group(hire_date, base_date):
    if pd.isnull(hire_date):
        return "미입력"
    days = (base_date - pd.Timestamp(hire_date)).days
    for limit, label in TENURE_GROUPS:
        if days <= limit:
            return label
    return "기존5"

def get_kr_holidays(years):
    kr = holidays_lib.KR(years=years)
    return set(kr.keys())

def fast_split_leadtime(start_dt, end_dt, holiday_set):
    if pd.isnull(start_dt) or pd.isnull(end_dt):
        return 0.0, 0.0
    total_min = (end_dt - start_dt).total_seconds() / 60
    if total_min <= 0:
        return 0.0, 0.0
    work_min = 0.0
    cur = start_dt.replace(second=0, microsecond=0)
    while cur < end_dt:
        day = cur.date()
        is_off = (cur.weekday() >= 5) or (day in holiday_set)
        next_day = datetime.combine(day + timedelta(days=1), datetime.min.time())
        if is_off:
            cur = min(next_day, end_dt)
            continue
        ws = cur.replace(hour=WORK_START, minute=0, second=0)
        we = cur.replace(hour=WORK_END,   minute=0, second=0)
        if cur < ws:
            cur = min(ws, end_dt)
            continue
        if cur < we:
            seg_end   = min(we, end_dt)
            work_min += (seg_end - cur).total_seconds() / 60
            cur = seg_end
            continue
        cur = min(next_day, end_dt)
    nonwork_min = total_min - work_min
    return round(max(work_min, 0), 1), round(max(nonwork_min, 0), 1)

# ─────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────
def gsheet_url(gid):
    return (f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
            f"/export?format=csv&gid={gid}")

@st.cache_data(ttl=300, show_spinner="에이전트 마스터 로딩...")
def load_agent():
    try:
        df = pd.read_csv(gsheet_url(GID_MAP["agent"]))
        df.columns = df.columns.str.strip()
        df["입사일"] = pd.to_datetime(df["입사일"], errors="coerce")
        return df
    except:
        return pd.DataFrame(columns=["상담사명","팀명","입사일"])

@st.cache_data(ttl=300, show_spinner="전화 데이터 로딩...")
def load_phone():
    try:
        df = pd.read_csv(gsheet_url(GID_MAP["phone"]))
        df.columns = df.columns.str.strip()
        df["일자"]        = pd.to_datetime(df["일자"], errors="coerce")
        df["대기시간(초)"] = pd.to_numeric(df["대기시간(초)"], errors="coerce").fillna(0)
        df["통화시간(초)"] = pd.to_numeric(df["통화시간(초)"], errors="coerce").fillna(0)
        df["ACW시간(초)"]  = pd.to_numeric(df["ACW시간(초)"],  errors="coerce").fillna(0)
        df["AHT(초)"]      = df["통화시간(초)"] + df["ACW시간(초)"]
        df["미응대"]       = df["상담사명"].str.strip() == "미응대"
        for c in ["대분류","중분류","소분류","브랜드"]:
            if c in df.columns: df[c] = df[c].fillna("").astype(str)
        return assign_period_cols(df)
    except:
        return pd.DataFrame(columns=[
            "일자","브랜드","상담사명","미응대","인입시각",
            "대기시간(초)","통화시간(초)","ACW시간(초)","AHT(초)",
            "대분류","중분류","소분류","일자_d","주차","월"])

@st.cache_data(ttl=300, show_spinner="채팅 데이터 로딩...")
def load_chat():
    try:
        df = pd.read_csv(gsheet_url(GID_MAP["chat"]))
        df.columns = df.columns.str.strip()
        df["일자"]           = pd.to_datetime(df["일자"], errors="coerce")
        df["접수일시"]       = pd.to_datetime(df["접수일시"], errors="coerce")
        df["첫멘트발송일시"] = pd.to_datetime(df["첫멘트발송일시"], errors="coerce")
        df["종료일시"]       = pd.to_datetime(df["종료일시"], errors="coerce")
        df["배분전포기여부"] = df["배분전포기여부"].fillna("N").astype(str).str.upper()
        df["미응대"]         = (df["첫멘트발송일시"].isnull() |
                                (df["배분전포기여부"] == "Y"))
        df["응답시간(초)"]   = ((df["첫멘트발송일시"] - df["접수일시"])
                                .dt.total_seconds().clip(lower=0).fillna(0))
        df["리드타임(초)"]   = ((df["종료일시"] - df["접수일시"])
                                .dt.total_seconds().clip(lower=0).fillna(0))
        for c in ["대분류","중분류","소분류","브랜드","플랫폼"]:
            if c in df.columns: df[c] = df[c].fillna("").astype(str)
        return assign_period_cols(df)
    except:
        return pd.DataFrame(columns=[
            "일자","브랜드","플랫폼","상담사명","미응대",
            "접수일시","첫멘트발송일시","종료일시",
            "배분전포기여부","응답시간(초)","리드타임(초)",
            "대분류","중분류","소분류","일자_d","주차","월"])

@st.cache_data(ttl=300, show_spinner="게시판 데이터 로딩...")
def load_board():
    try:
        df = pd.read_csv(gsheet_url(GID_MAP["board"]))
        df.columns = df.columns.str.strip()
        df["일자"]     = pd.to_datetime(df["일자"], errors="coerce")
        df["접수일시"] = pd.to_datetime(df["접수일시"], errors="coerce")
        df["응답일시"] = pd.to_datetime(df["응답일시"], errors="coerce")
        df["미응대"]   = df["응답일시"].isnull()
        years = set()
        for d in pd.concat([df["접수일시"].dropna(),
                            df["응답일시"].dropna()]):
            years.add(d.year)
        hset = get_kr_holidays(list(years)) if years else set()
        wl, nwl = [], []
        for _, row in df.iterrows():
            if pd.isnull(row["응답일시"]):
                wl.append(None); nwl.append(None)
            else:
                w, nw = fast_split_leadtime(
                    row["접수일시"], row["응답일시"], hset)
                wl.append(w); nwl.append(nw)
        df["근무내리드타임(분)"]  = wl
        df["근무외리드타임(분)"] = nwl
        df["전체리드타임(분)"]   = ((df["응답일시"] - df["접수일시"])
                                    .dt.total_seconds() / 60).clip(lower=0)
        for c in ["대분류","중분류","소분류","브랜드","플랫폼"]:
            if c in df.columns: df[c] = df[c].fillna("").astype(str)
        return assign_period_cols(df)
    except:
        return pd.DataFrame(columns=[
            "일자","브랜드","플랫폼","상담사명","미응대",
            "접수일시","응답일시",
            "근무내리드타임(분)","근무외리드타임(분)","전체리드타임(분)",
            "대분류","중분류","소분류","일자_d","주차","월"])

def merge_agent(df, agent_df, base_date):
    m = df.merge(agent_df, on="상담사명", how="left")
    m["팀명"]     = m["팀명"].fillna("미입력")
    m["입사일"]   = pd.to_datetime(m["입사일"], errors="coerce")
    m["근속그룹"] = m["입사일"].apply(
        lambda x: get_tenure_group(x, base_date))
    return m

# ─────────────────────────────────────────────
# UTILITIES
# ─────────────────────────────────────────────
def filter_df(df, dr, brands):
    if len(df) == 0:
        return df
    m = ((df["일자"] >= pd.Timestamp(dr[0])) &
         (df["일자"] <= pd.Timestamp(dr[1])))
    if brands:
        m &= df["브랜드"].isin(brands)
    return df[m].copy()

def sec(title):
    st.markdown(
        f'<div class="section-title">{title}</div>',
        unsafe_allow_html=True)

def kpi(label, value, sub="", delta=None,
        delta_label="전기대비", reverse=False, color="#3b82f6"):
    dh = ""
    if delta is not None:
        if delta > 0:
            cls = "kpi-delta-down" if reverse else "kpi-delta-up"
            dh  = f'<div class="{cls}">▲ {abs(delta):.1f}% ({delta_label})</div>'
        elif delta < 0:
            cls = "kpi-delta-up" if reverse else "kpi-delta-down"
            dh  = f'<div class="{cls}">▼ {abs(delta):.1f}% ({delta_label})</div>'
        else:
            dh  = '<div class="kpi-delta-neu">- 변동없음</div>'
    sh = f'<div class="kpi-sub">{sub}</div>' if sub else ""
    st.markdown(f"""
    <div class="kpi-card" style="border-top-color:{color}">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>{sh}{dh}
    </div>""", unsafe_allow_html=True)

def fmt_sec(s):
    if pd.isnull(s) or s == 0: return "0s"
    s = int(s); m, sec = divmod(s, 60)
    return f"{m}m {sec}s" if m else f"{sec}s"

def fmt_min(m):
    if pd.isnull(m) or m == 0: return "0m"
    m = float(m); h, mn = divmod(int(m), 60)
    return f"{h}h {mn}m" if h else f"{mn}m"

def chart_cfg(fig, h=320):
    fig.update_layout(
        height=h, margin=dict(t=10,b=40,l=0,r=10),
        legend=dict(orientation="h",yanchor="bottom",y=1.02,
                    xanchor="right",x=1,font=dict(size=11)),
        font=dict(size=11,family="Inter"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(showgrid=False,showline=True,
                     linecolor="#e2e8f0",tickfont=dict(size=10))
    fig.update_yaxes(showgrid=True,gridcolor="#f1f5f9",
                     tickfont=dict(size=10))
    return fig

def make_color_map(keys):
    return {k: COLORS[i%len(COLORS)] for i,k in enumerate(sorted(keys))}

def compact_table(data, height=280):
    st.dataframe(data, use_container_width=True, height=height)

def response_rate(df):
    if len(df) == 0: return 0.0
    return round((~df["미응대"]).sum() / len(df) * 100, 1)

def get_period_kpi(df, unit, val_col=None, agg="count",
                   responded_only=False):
    tdf = df[~df["미응대"]].copy() if responded_only else df.copy()
    if len(tdf) == 0:
        return 0, None, None, "-"
    pc = get_period_col(unit)
    if pc not in tdf.columns:
        return 0, None, None, "-"
    if val_col and agg != "count":
        series = tdf.groupby(pc)[val_col].agg(agg)
    else:
        series = tdf.groupby(pc).size()
    if series.empty:
        return 0, None, None, "-"
    series    = series.sort_index()
    cur_label = series.index[-1]
    cur_val   = series.iloc[-1]
    prev_val  = series.get(get_prev_period(unit, cur_label), None)
    yoy_val   = series.get(get_yoy_period(unit, cur_label), None)
    return cur_val, prev_val, yoy_val, cur_label

def delta_row(cur, prev, yoy, unit, reverse=False):
    unit_map = {"일별":"전일","주별":"전주","월별":"전월"}
    prev_lbl = unit_map.get(unit,"전기")
    def badge(val, lbl, rev):
        if val is None or pd.isnull(val): return ""
        if val > 0:
            cls = "kpi-delta-down" if rev else "kpi-delta-up"
            return f'<span class="{cls}">▲{abs(val):.1f}% ({lbl})</span>'
        elif val < 0:
            cls = "kpi-delta-up" if rev else "kpi-delta-down"
            return f'<span class="{cls}">▼{abs(val):.1f}% ({lbl})</span>'
        return f'<span class="kpi-delta-neu">- ({lbl})</span>'
    p_delta = calc_delta(cur, prev)
    y_delta = calc_delta(cur, yoy)
    parts   = [badge(p_delta, prev_lbl, reverse),
               badge(y_delta, "전년동기", reverse)]
    return " &nbsp; ".join(p for p in parts if p)

def trend_chart(df_dict, unit, val_col=None, agg="count",
                responded_only=False, y_label="건수",
                h=320, month_range=3):
    cutoff = get_chart_range(unit, month_range)
    pc     = get_period_col(unit)
    fig    = go.Figure()
    cmap   = make_color_map(list(df_dict.keys()))
    for name, df in df_dict.items():
        if len(df) == 0: continue
        tdf = df[~df["미응대"]].copy() if responded_only else df.copy()
        tdf = tdf[tdf["일자"] >= pd.Timestamp(cutoff)]
        if len(tdf) == 0: continue
        if pc not in tdf.columns: continue
        if val_col and agg != "count":
            s = tdf.groupby(pc)[val_col].agg(agg).round(1)
        else:
            s = tdf.groupby(pc).size()
        s = s.sort_index().reset_index()
        s.columns = [pc, y_label]
        color = cmap.get(name, "#888")
        fig.add_trace(go.Scatter(
            x=s[pc], y=s[y_label],
            mode="lines+markers", name=name,
            line=dict(color=color, width=2.5),
            marker=dict(size=7),
            fill="tozeroy",
            fillcolor=color + "18",
        ))
    if not fig.data:
        st.info("표시할 데이터가 없습니다.")
        return
    fig.update_layout(
        height=h, hovermode="x unified",
        margin=dict(t=10,b=40,l=0,r=10),
        legend=dict(orientation="h",yanchor="bottom",y=1.02,
                    xanchor="right",x=1,font=dict(size=11)),
        yaxis_title=y_label,
        font=dict(size=11,family="Inter"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(showgrid=False,showline=True,
                     linecolor="#e2e8f0",tickangle=-30,tickfont=dict(size=10))
    fig.update_yaxes(showgrid=True,gridcolor="#f1f5f9",tickfont=dict(size=10))
    st.plotly_chart(fig, use_container_width=True)

def bar_trend_chart(df_dict, unit, y_label="건수", h=300, month_range=3):
    cutoff = get_chart_range(unit, month_range)
    pc     = get_period_col(unit)
    rows   = []
    for name, df in df_dict.items():
        if len(df) == 0: continue
        tdf = df[df["일자"] >= pd.Timestamp(cutoff)]
        if pc not in tdf.columns: continue
        s = tdf.groupby(pc).size().sort_index().reset_index()
        s.columns = [pc, y_label]
        s["채널"] = name
        rows.append(s)
    if not rows:
        st.info("표시할 데이터가 없습니다.")
        return
    mlt  = pd.concat(rows)
    cmap = make_color_map(list(df_dict.keys()))
    fig  = px.bar(mlt, x=pc, y=y_label, color="채널",
                  barmode="stack", color_discrete_map=cmap)
    chart_cfg(fig, h=h)
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# PAGE — 전체 현황
# ─────────────────────────────────────────────
def page_overview(phone, chat, board, unit, month_range):
    st.markdown('<div class="page-title">전체 현황</div>',
                unsafe_allow_html=True)
    st.markdown(
        f'<div class="page-sub">전체 채널 통합 운영 현황'
        f'<span class="period-badge">{unit}</span></div>',
        unsafe_allow_html=True)

    ph_cur,ph_prev,ph_yoy,_ = get_period_kpi(phone, unit)
    ch_cur,ch_prev,ch_yoy,_ = get_period_kpi(chat,  unit)
    bo_cur,bo_prev,bo_yoy,_ = get_period_kpi(board, unit)
    prev_lbl = {"일별":"전일","주별":"전주","월별":"전월"}.get(unit,"전기")

    c1,c2,c3,c4 = st.columns(4)
    with c1:
        kpi("전체 인입",
            f"{len(phone)+len(chat)+len(board):,}건",
            sub=f"전화 {len(phone):,} / 채팅 {len(chat):,} / 게시판 {len(board):,}")
    with c2:
        kpi("전화 인입",f"{int(ph_cur):,}건",
            delta=calc_delta(ph_cur,ph_prev),
            delta_label=prev_lbl, color="#3b82f6")
    with c3:
        kpi("채팅 인입",f"{int(ch_cur):,}건",
            delta=calc_delta(ch_cur,ch_prev),
            delta_label=prev_lbl, color="#22c55e")
    with c4:
        kpi("게시판 인입",f"{int(bo_cur):,}건",
            delta=calc_delta(bo_cur,bo_prev),
            delta_label=prev_lbl, color="#f97316")

    yoy_parts = []
    for label,cur,yoy in [("전화",ph_cur,ph_yoy),
                           ("채팅",ch_cur,ch_yoy),
                           ("게시판",bo_cur,bo_yoy)]:
        b = delta_row(cur,None,yoy,unit)
        if b: yoy_parts.append(f"{label} {b}")
    if yoy_parts:
        st.markdown(
            f"<div style='font-size:12px;margin-bottom:12px'>"
            f"{'&nbsp;&nbsp;|&nbsp;&nbsp;'.join(yoy_parts)}</div>",
            unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    sec(f"채널별 인입 추이 ({unit})")
    trend_chart({"전화":phone,"채팅":chat,"게시판":board},
                unit=unit, y_label="건수", h=340, month_range=month_range)

    sec(f"채널별 누적 인입 ({unit})")
    bar_trend_chart({"전화":phone,"채팅":chat,"게시판":board},
                    unit=unit, y_label="건수", h=280, month_range=month_range)

    sec(f"채널별 응답률 추이 ({unit})")
    cutoff = get_chart_range(unit, month_range)
    pc     = get_period_col(unit)
    rr_rows = []
    for name, df in [("전화",phone),("채팅",chat),("게시판",board)]:
        if len(df) == 0: continue
        tdf = df[df["일자"] >= pd.Timestamp(cutoff)]
        if pc not in tdf.columns: continue
        grp = (tdf.groupby(pc)
               .apply(lambda g: round((~g["미응대"]).sum()/len(g)*100,1)
                      if len(g)>0 else 0)
               .reset_index())
        grp.columns = [pc,"응답률(%)"]
        grp["채널"] = name
        rr_rows.append(grp)
    if rr_rows:
        rr_df = pd.concat(rr_rows)
        cmap  = {"전화":"#3b82f6","채팅":"#22c55e","게시판":"#f97316"}
        fig_rr = go.Figure()
        for ch in ["전화","채팅","게시판"]:
            d = rr_df[rr_df["채널"]==ch]
            if len(d)==0: continue
            fig_rr.add_trace(go.Scatter(
                x=d[pc],y=d["응답률(%)"],
                mode="lines+markers",name=ch,
                line=dict(color=cmap[ch],width=2.5),
                marker=dict(size=7),
            ))
        fig_rr.update_layout(
            height=300, hovermode="x unified",
            yaxis=dict(title="응답률(%)",range=[0,105]),
            margin=dict(t=10,b=40,l=0,r=10),
            legend=dict(orientation="h",y=1.02,x=1,
                        xanchor="right",font=dict(size=11)),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(size=11),
        )
        fig_rr.update_xaxes(showgrid=False,showline=True,
                             linecolor="#e2e8f0",tickangle=-30)
        fig_rr.update_yaxes(showgrid=True,gridcolor="#f1f5f9")
        st.plotly_chart(fig_rr, use_container_width=True)

# ─────────────────────────────────────────────
# PAGE — 전화 현황
# ─────────────────────────────────────────────
def page_phone(phone, unit, month_range):
    st.markdown('<div class="page-title">전화 현황</div>',
                unsafe_allow_html=True)
    st.markdown(
        f'<div class="page-sub">전화 채널 운영 지표'
        f'<span class="period-badge">{unit}</span></div>',
        unsafe_allow_html=True)

    if len(phone) == 0:
        st.info("전화 데이터가 없습니다.")
        return

    responded = phone[~phone["미응대"]]
    prev_lbl  = {"일별":"전일","주별":"전주","월별":"전월"}.get(unit,"전기")
    cur,prev,yoy,_ = get_period_kpi(phone, unit)

    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: kpi("전체 인입",  f"{len(phone):,}건")
    with c2: kpi("응답",       f"{len(responded):,}건",        color="#22c55e")
    with c3: kpi("미응대",     f"{phone['미응대'].sum():,}건",  color="#ef4444")
    with c4: kpi("응답률",     f"{response_rate(phone)}%",      color="#3b82f6")
    with c5: kpi("평균 AHT",
                 fmt_sec(responded["AHT(초)"].mean() if len(responded)>0 else 0),
                 sub=(f"통화 {fmt_sec(responded['통화시간(초)'].mean())} / "
                      f"ACW {fmt_sec(responded['ACW시간(초)'].mean())}")
                 if len(responded)>0 else "",
                 color="#8b5cf6")

    bh = delta_row(cur,prev,yoy,unit)
    if bh:
        st.markdown(
            f"<div style='font-size:12px;margin-bottom:16px'>"
            f"인입 &nbsp; {bh}</div>",
            unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    t1,t2,t3,t4 = st.tabs(["추이 분석","시간대 분석","대분류 분석","상세 테이블"])

    with t1:
        sec(f"인입 추이 ({unit})")
        trend_chart({"전화 인입":phone,"응답":responded},
                    unit=unit,y_label="건수",h=320,month_range=month_range)
        sec(f"평균 AHT 추이 ({unit})")
        trend_chart({"평균 AHT(초)":responded},
                    unit=unit,val_col="AHT(초)",agg="mean",
                    y_label="AHT(초)",h=280,month_range=month_range)
        sec(f"평균 대기시간 추이 ({unit})")
        trend_chart({"평균 대기(초)":responded},
                    unit=unit,val_col="대기시간(초)",agg="mean",
                    y_label="대기시간(초)",h=260,month_range=month_range)

    with t2:
        sec("시간대별 인입량")
        if "인입시각" in phone.columns:
            phone2 = phone.copy()
            phone2["시간대"] = pd.to_datetime(
                phone2["인입시각"],format="%H:%M:%S",errors="coerce").dt.hour
            hour_d = (phone2.groupby(["시간대","미응대"])
                      .size().reset_index(name="건수"))
            hour_d["구분"] = hour_d["미응대"].map({True:"미응대",False:"응답"})
            fig = px.bar(hour_d,x="시간대",y="건수",color="구분",
                         barmode="stack",
                         color_discrete_map={"응답":"#3b82f6","미응대":"#ef4444"})
            chart_cfg(fig,h=300)
            st.plotly_chart(fig, use_container_width=True)

            if len(responded) > 0:
                sec("시간대별 평균 대기 / AHT")
                aht_h = (responded.copy()
                         .assign(시간대=pd.to_datetime(
                             responded["인입시각"],
                             format="%H:%M:%S",errors="coerce").dt.hour)
                         .groupby("시간대")[["대기시간(초)","AHT(초)"]]
                         .mean().round(1).reset_index())
                fig2 = go.Figure()
                fig2.add_trace(go.Bar(
                    x=aht_h["시간대"],y=aht_h["대기시간(초)"],
                    name="평균 대기(초)",marker_color="#3b82f6",opacity=0.8))
                fig2.add_trace(go.Scatter(
                    x=aht_h["시간대"],y=aht_h["AHT(초)"],
                    name="평균 AHT(초)",mode="lines+markers",
                    line=dict(color="#f97316",width=2.5),
                    marker=dict(size=8),yaxis="y2"))
                fig2.update_layout(
                    height=300,
                    yaxis=dict(title="대기시간(초)"),
                    yaxis2=dict(title="AHT(초)",overlaying="y",side="right"),
                    margin=dict(t=10,b=40,l=0,r=60),
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    legend=dict(orientation="h",y=1.02,x=1,
                                xanchor="right",font=dict(size=11)),
                    font=dict(size=11),
                )
                st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("인입시각 컬럼이 없습니다.")

    with t3:
        sec("대분류별 인입 비중")
        cat_d = (phone[phone["대분류"]!=""]
                 .groupby("대분류").size()
                 .reset_index(name="건수")
                 .sort_values("건수",ascending=False))
        if len(cat_d) > 0:
            col1,col2 = st.columns([1,1])
            with col1:
                fig3 = px.pie(cat_d,names="대분류",values="건수",hole=0.6,
                              color_discrete_sequence=COLORS)
                fig3.update_traces(textposition="inside",
                                   textinfo="percent+label",textfont_size=11)
                fig3.update_layout(height=300,margin=dict(t=0,b=0,l=0,r=0),
                                   plot_bgcolor="rgba(0,0,0,0)",
                                   paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig3, use_container_width=True)
            with col2:
                if len(responded) > 0:
                    sec("대분류별 평균 AHT")
                    aht_cat = (responded[responded["대분류"]!=""]
                               .groupby("대분류")["AHT(초)"]
                               .mean().round(1).reset_index()
                               .sort_values("AHT(초)",ascending=True))
                    fig4 = px.bar(aht_cat,y="대분류",x="AHT(초)",
                                  orientation="h",color="대분류",
                                  color_discrete_sequence=COLORS,text="AHT(초)")
                    fig4.update_traces(textposition="outside",textfont_size=10)
                    fig4.update_layout(height=300,showlegend=False,
                                       margin=dict(t=10,b=10,l=0,r=60),
                                       plot_bgcolor="rgba(0,0,0,0)",
                                       paper_bgcolor="rgba(0,0,0,0)",
                                       font=dict(size=11))
                    st.plotly_chart(fig4, use_container_width=True)

            sec("대분류별 추이")
            cutoff = get_chart_range(unit, month_range)
            pc     = get_period_col(unit)
            cats   = (phone[phone["대분류"]!=""]["대분류"]
                      .value_counts().head(6).index.tolist())
            fig5   = go.Figure()
            cmap2  = make_color_map(cats)
            for cat in cats:
                sub = phone[(phone["대분류"]==cat) &
                            (phone["일자"]>=pd.Timestamp(cutoff))]
                if pc not in sub.columns: continue
                s = sub.groupby(pc).size().sort_index().reset_index()
                s.columns = [pc,"건수"]
                fig5.add_trace(go.Scatter(
                    x=s[pc],y=s["건수"],mode="lines+markers",name=cat,
                    line=dict(color=cmap2.get(cat,"#888"),width=2),
                    marker=dict(size=6),
                ))
            chart_cfg(fig5,h=300)
            fig5.update_layout(hovermode="x unified")
            st.plotly_chart(fig5, use_container_width=True)

    with t4:
        sec("전화 로그 상세")
        show_cols = [c for c in
                     ["일자","브랜드","상담사명","미응대","인입시각",
                      "대기시간(초)","통화시간(초)","ACW시간(초)","AHT(초)",
                      "대분류","중분류","소분류"]
                     if c in phone.columns]
        compact_table(phone[show_cols], height=400)

# ─────────────────────────────────────────────
# PAGE — 전화 상담사
# ─────────────────────────────────────────────
def page_phone_agent(phone, unit, month_range):
    st.markdown('<div class="page-title">전화 상담사 분석</div>',
                unsafe_allow_html=True)
    st.markdown(
        f'<div class="page-sub">상담사별 전화 처리 성과'
        f'<span class="period-badge">{unit}</span></div>',
        unsafe_allow_html=True)

    if len(phone) == 0:
        st.info("전화 데이터가 없습니다.")
        return

    responded = phone[~phone["미응대"]]
    t1,t2,t3 = st.tabs(["상담사별 성과","팀별 현황","근속그룹별"])

    with t1:
        if len(responded) == 0:
            st.info("응답 데이터가 없습니다.")
        else:
            sec("상담사별 핵심 지표")
            ag = (responded.groupby("상담사명")
                  .agg(처리건수=("AHT(초)","count"),
                       평균대기=("대기시간(초)","mean"),
                       평균통화=("통화시간(초)","mean"),
                       평균ACW=("ACW시간(초)","mean"),
                       평균AHT=("AHT(초)","mean"))
                  .round(1).reset_index()
                  .sort_values("처리건수",ascending=False))
            ag["미응대수"] = (phone[phone["미응대"]]
                             .groupby("상담사명").size()
                             .reindex(ag["상담사명"]).fillna(0).values)
            ag["응답률(%)"] = (
                ag["처리건수"]/(ag["처리건수"]+ag["미응대수"])*100
            ).round(1)

            cmap = make_color_map(ag["상담사명"].unique())
            fig = px.bar(ag.head(20),x="상담사명",y="처리건수",
                         color="상담사명",color_discrete_map=cmap,text="처리건수")
            fig.update_traces(textposition="outside",textfont_size=10)
            chart_cfg(fig,h=300)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

            sec(f"상담사별 AHT 추이 ({unit}) — Top5")
            cutoff = get_chart_range(unit, month_range)
            pc     = get_period_col(unit)
            top5   = ag.head(5)["상담사명"].tolist()
            fig2   = go.Figure()
            cmap2  = make_color_map(top5)
            for ag_name in top5:
                sub = responded[(responded["상담사명"]==ag_name) &
                                (responded["일자"]>=pd.Timestamp(cutoff))]
                if pc not in sub.columns or len(sub)==0: continue
                s = sub.groupby(pc)["AHT(초)"].mean().round(1).reset_index()
                fig2.add_trace(go.Scatter(
                    x=s[pc],y=s["AHT(초)"],mode="lines+markers",name=ag_name,
                    line=dict(color=cmap2.get(ag_name,"#888"),width=2),
                    marker=dict(size=6)))
            chart_cfg(fig2,h=300)
            fig2.update_layout(hovermode="x unified")
            st.plotly_chart(fig2, use_container_width=True)

            with st.expander("상담사별 수치 테이블",expanded=False):
                compact_table(ag, height=340)

    with t2:
        if "팀명" in phone.columns and len(responded)>0:
            sec("팀별 처리 현황")
            team_r = (responded.groupby("팀명")
                      .agg(처리건수=("AHT(초)","count"),
                           평균AHT=("AHT(초)","mean"),
                           평균대기=("대기시간(초)","mean"))
                      .round(1).reset_index()
                      .sort_values("처리건수",ascending=False))
            fig3 = px.bar(team_r,x="팀명",y="처리건수",
                          color="팀명",color_discrete_sequence=COLORS,
                          text="처리건수")
            fig3.update_traces(textposition="outside",textfont_size=10)
            chart_cfg(fig3,h=280)
            fig3.update_layout(showlegend=False)
            st.plotly_chart(fig3, use_container_width=True)

            sec(f"팀별 AHT 추이 ({unit})")
            trend_dict = {tm: responded[responded["팀명"]==tm]
                          for tm in team_r["팀명"].tolist()}
            trend_chart(trend_dict,unit=unit,val_col="AHT(초)",agg="mean",
                        y_label="평균AHT(초)",h=280,month_range=month_range)
            compact_table(team_r, height=240)
        else:
            st.info("팀명 정보가 없습니다.")

    with t3:
        if "근속그룹" in phone.columns and len(responded)>0:
            sec("근속그룹별 평균 AHT")
            tg = (responded.groupby("근속그룹")
                  .agg(처리건수=("AHT(초)","count"),
                       평균AHT=("AHT(초)","mean"),
                       평균통화=("통화시간(초)","mean"),
                       평균ACW=("ACW시간(초)","mean"))
                  .round(1).reset_index())
            order = [g for _,g in TENURE_GROUPS]
            tg["순서"] = tg["근속그룹"].apply(
                lambda x: order.index(x) if x in order else 99)
            tg = tg.sort_values("순서")
            fig4 = px.bar(tg,x="근속그룹",y="평균AHT",
                          color="근속그룹",color_discrete_sequence=COLORS,
                          text="처리건수",labels={"평균AHT":"평균 AHT(초)"})
            fig4.update_traces(textposition="outside",textfont_size=10)
            chart_cfg(fig4,h=300)
            fig4.update_layout(showlegend=False)
            st.plotly_chart(fig4, use_container_width=True)
            compact_table(tg.drop(columns=["순서"]), height=260)
        else:
            st.info("근속그룹 정보가 없습니다.")

# ─────────────────────────────────────────────
# PAGE — 채팅 현황
# ─────────────────────────────────────────────
def page_chat(chat, unit, month_range):
    st.markdown('<div class="page-title">채팅 현황</div>',
                unsafe_allow_html=True)
    st.markdown(
        f'<div class="page-sub">채팅 채널 운영 지표'
        f'<span class="period-badge">{unit}</span></div>',
        unsafe_allow_html=True)

    if len(chat) == 0:
        st.info("채팅 데이터가 없습니다.")
        return

    responded = chat[~chat["미응대"]]
    prev_lbl  = {"일별":"전일","주별":"전주","월별":"전월"}.get(unit,"전기")
    cur,prev,yoy,_ = get_period_kpi(chat, unit)
    lt_cur,lt_prev,lt_yoy,_ = get_period_kpi(
        responded,unit,val_col="리드타임(초)",agg="mean")

    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: kpi("전체 인입",  f"{len(chat):,}건")
    with c2: kpi("응답",       f"{len(responded):,}건",       color="#22c55e")
    with c3: kpi("미응대",     f"{chat['미응대'].sum():,}건",  color="#ef4444")
    with c4: kpi("응답률",     f"{response_rate(chat)}%",      color="#3b82f6")
    with c5: kpi("평균 리드타임",
                 fmt_sec(responded["리드타임(초)"].mean() if len(responded)>0 else 0),
                 sub=f"평균 응답 {fmt_sec(responded['응답시간(초)'].mean())}"
                 if len(responded)>0 else "",
                 delta=calc_delta(lt_cur,lt_prev),
                 delta_label=prev_lbl, reverse=True, color="#8b5cf6")

    bh = delta_row(cur,prev,yoy,unit)
    if bh:
        st.markdown(
            f"<div style='font-size:12px;margin-bottom:16px'>"
            f"인입 &nbsp; {bh}</div>",
            unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    t1,t2,t3,t4 = st.tabs(["추이 분석","시간대 분석","대분류별 리드타임","상세 테이블"])

    with t1:
        sec(f"인입 추이 ({unit})")
        trend_chart({"채팅 인입":chat,"응답":responded},
                    unit=unit,y_label="건수",h=320,month_range=month_range)
        sec(f"평균 리드타임 추이 ({unit})")
        trend_chart({"평균 리드타임(초)":responded},
                    unit=unit,val_col="리드타임(초)",agg="mean",
                    y_label="리드타임(초)",h=280,month_range=month_range)
        sec(f"평균 응답시간 추이 ({unit})")
        trend_chart({"평균 응답시간(초)":responded},
                    unit=unit,val_col="응답시간(초)",agg="mean",
                    y_label="응답시간(초)",h=260,month_range=month_range)

    with t2:
        sec("시간대별 인입량")
        chat2 = chat.copy()
        chat2["시간대"] = chat2["접수일시"].dt.hour
        hour_d = (chat2.groupby(["시간대","미응대"])
                  .size().reset_index(name="건수"))
        hour_d["구분"] = hour_d["미응대"].map({True:"미응대",False:"응답"})
        fig = px.bar(hour_d,x="시간대",y="건수",color="구분",
                     barmode="stack",
                     color_discrete_map={"응답":"#22c55e","미응대":"#ef4444"})
        chart_cfg(fig,h=300)
        st.plotly_chart(fig, use_container_width=True)

    with t3:
        CHAT_G1 = ["주문/결제","상품"]
        CHAT_G2 = ["배송","취소","교환","반품","기타"]
        sec("대분류별 평균 리드타임")
        if len(responded) > 0:
            lt_cat = (responded[responded["대분류"]!=""]
                      .groupby("대분류")["리드타임(초)"]
                      .agg(["mean","count"]).round(1).reset_index()
                      .rename(columns={"mean":"평균리드타임(초)","count":"건수"}))
            lt_cat["그룹"] = lt_cat["대분류"].apply(
                lambda x: "그룹1 (주문/결제·상품)" if x in CHAT_G1
                else "그룹2 (배송·취소·교환·반품·기타)")
            lt_cat = lt_cat.sort_values("평균리드타임(초)",ascending=True)
            fig3 = px.bar(lt_cat,y="대분류",x="평균리드타임(초)",orientation="h",
                          color="그룹",
                          color_discrete_map={
                              "그룹1 (주문/결제·상품)":"#3b82f6",
                              "그룹2 (배송·취소·교환·반품·기타)":"#f97316"},
                          text="건수")
            fig3.update_traces(textposition="outside",textfont_size=10)
            fig3.update_layout(
                height=max(300,len(lt_cat)*30+60),
                margin=dict(t=10,b=10,l=0,r=60),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",font=dict(size=11))
            st.plotly_chart(fig3, use_container_width=True)

            sec(f"그룹별 리드타임 추이 ({unit})")
            responded2 = responded.copy()
            responded2["그룹"] = responded2["대분류"].apply(
                lambda x: "그룹1" if x in CHAT_G1 else "그룹2")
            trend_chart(
                {"그룹1":responded2[responded2["그룹"]=="그룹1"],
                 "그룹2":responded2[responded2["그룹"]=="그룹2"]},
                unit=unit,val_col="리드타임(초)",agg="mean",
                y_label="평균리드타임(초)",h=280,month_range=month_range)

    with t4:
        sec("채팅 로그 상세")
        show_cols = [c for c in
                     ["일자","브랜드","플랫폼","상담사명","미응대",
                      "접수일시","첫멘트발송일시","종료일시",
                      "배분전포기여부","응답시간(초)","리드타임(초)",
                      "대분류","중분류","소분류"]
                     if c in chat.columns]
        compact_table(chat[show_cols], height=400)

# ─────────────────────────────────────────────
# PAGE — 채팅 상담사
# ─────────────────────────────────────────────
def page_chat_agent(chat, unit, month_range):
    st.markdown('<div class="page-title">채팅 상담사 분석</div>',
                unsafe_allow_html=True)
    st.markdown(
        f'<div class="page-sub">상담사별 채팅 처리 성과'
        f'<span class="period-badge">{unit}</span></div>',
        unsafe_allow_html=True)

    if len(chat) == 0:
        st.info("채팅 데이터가 없습니다.")
        return

    responded = chat[~chat["미응대"]]
    t1,t2,t3 = st.tabs(["상담사별 성과","팀별 현황","근속그룹별"])

    with t1:
        if len(responded) == 0:
            st.info("응답 데이터가 없습니다.")
        else:
            sec("상담사별 핵심 지표")
            ag = (responded.groupby("상담사명")
                  .agg(처리건수=("리드타임(초)","count"),
                       평균응답=("응답시간(초)","mean"),
                       평균리드타임=("리드타임(초)","mean"))
                  .round(1).reset_index()
                  .sort_values("처리건수",ascending=False))
            cmap = make_color_map(ag["상담사명"].unique())
            fig = px.bar(ag.head(20),x="상담사명",y="처리건수",
                         color="상담사명",color_discrete_map=cmap,text="처리건수")
            fig.update_traces(textposition="outside",textfont_size=10)
            chart_cfg(fig,h=300)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

            sec(f"상담사별 리드타임 추이 ({unit}) — Top5")
            cutoff = get_chart_range(unit, month_range)
            pc     = get_period_col(unit)
            top5   = ag.head(5)["상담사명"].tolist()
            fig2   = go.Figure()
            cmap2  = make_color_map(top5)
            for ag_name in top5:
                sub = responded[(responded["상담사명"]==ag_name) &
                                (responded["일자"]>=pd.Timestamp(cutoff))]
                if pc not in sub.columns or len(sub)==0: continue
                s = sub.groupby(pc)["리드타임(초)"].mean().round(1).reset_index()
                fig2.add_trace(go.Scatter(
                    x=s[pc],y=s["리드타임(초)"],mode="lines+markers",name=ag_name,
                    line=dict(color=cmap2.get(ag_name,"#888"),width=2),
                    marker=dict(size=6)))
            chart_cfg(fig2,h=300)
            fig2.update_layout(hovermode="x unified")
            st.plotly_chart(fig2, use_container_width=True)

            with st.expander("상담사별 수치 테이블",expanded=False):
                compact_table(ag, height=320)

    with t2:
        if "팀명" in chat.columns and len(responded)>0:
            sec("팀별 처리 현황")
            team_r = (responded.groupby("팀명")
                      .agg(처리건수=("리드타임(초)","count"),
                           평균리드타임=("리드타임(초)","mean"),
                           평균응답=("응답시간(초)","mean"))
                      .round(1).reset_index()
                      .sort_values("처리건수",ascending=False))
            fig3 = px.bar(team_r,x="팀명",y="처리건수",
                          color="팀명",color_discrete_sequence=COLORS,text="처리건수")
            fig3.update_traces(textposition="outside",textfont_size=10)
            chart_cfg(fig3,h=280)
            fig3.update_layout(showlegend=False)
            st.plotly_chart(fig3, use_container_width=True)
            compact_table(team_r, height=240)
        else:
            st.info("팀명 정보가 없습니다.")

    with t3:
        if "근속그룹" in chat.columns and len(responded)>0:
            sec("근속그룹별 평균 리드타임")
            tg = (responded.groupby("근속그룹")
                  .agg(처리건수=("리드타임(초)","count"),
                       평균리드타임=("리드타임(초)","mean"),
                       평균응답=("응답시간(초)","mean"))
                  .round(1).reset_index())
            order = [g for _,g in TENURE_GROUPS]
            tg["순서"] = tg["근속그룹"].apply(
                lambda x: order.index(x) if x in order else 99)
            tg = tg.sort_values("순서")
            fig4 = px.bar(tg,x="근속그룹",y="평균리드타임",
                          color="근속그룹",color_discrete_sequence=COLORS,
                          text="처리건수",labels={"평균리드타임":"평균 리드타임(초)"})
            fig4.update_traces(textposition="outside",textfont_size=10)
            chart_cfg(fig4,h=300)
            fig4.update_layout(showlegend=False)
            st.plotly_chart(fig4, use_container_width=True)
            compact_table(tg.drop(columns=["순서"]), height=260)
        else:
            st.info("근속그룹 정보가 없습니다.")

# ─────────────────────────────────────────────
# PAGE — 게시판 현황
# ─────────────────────────────────────────────
def page_board(board, unit, month_range):
    st.markdown('<div class="page-title">게시판 현황</div>',
                unsafe_allow_html=True)
    st.markdown(
        f'<div class="page-sub">게시판/티켓 채널 — 근무내/외 리드타임 분리'
        f'<span class="period-badge">{unit}</span></div>',
        unsafe_allow_html=True)

    if len(board) == 0:
        st.info("게시판 데이터가 없습니다.")
        return

    responded = board[~board["미응대"]]
    prev_lbl  = {"일별":"전일","주별":"전주","월별":"전월"}.get(unit,"전기")
    cur,prev,yoy,_ = get_period_kpi(board, unit)
    wl_cur,wl_prev,wl_yoy,_ = get_period_kpi(
        responded,unit,val_col="근무내리드타임(분)",agg="mean")

    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: kpi("전체 티켓",  f"{len(board):,}건")
    with c2: kpi("응답 완료",  f"{len(responded):,}건",       color="#22c55e")
    with c3: kpi("미응대",     f"{board['미응대'].sum():,}건", color="#ef4444")
    with c4: kpi("응답률",     f"{response_rate(board)}%",     color="#3b82f6")
    with c5: kpi("근무내 리드타임",
                 fmt_min(responded["근무내리드타임(분)"].mean()
                         if len(responded)>0 else 0),
                 sub=f"근무외 {fmt_min(responded['근무외리드타임(분)'].mean())}"
                 if len(responded)>0 else "",
                 delta=calc_delta(wl_cur,wl_prev),
                 delta_label=prev_lbl, reverse=True, color="#8b5cf6")

    bh = delta_row(cur,prev,yoy,unit)
    if bh:
        st.markdown(
            f"<div style='font-size:12px;margin-bottom:16px'>"
            f"티켓 &nbsp; {bh}</div>",
            unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    t1,t2,t3,t4 = st.tabs(["추이 분석","리드타임 분석","플랫폼 분석","상세 테이블"])

    with t1:
        sec(f"티켓 인입 추이 ({unit})")
        trend_chart({"전체":board,"응답":responded},
                    unit=unit,y_label="건수",h=320,month_range=month_range)
        sec(f"근무내 리드타임 추이 ({unit})")
        trend_chart({"근무내(분)":responded},
                    unit=unit,val_col="근무내리드타임(분)",agg="mean",
                    y_label="근무내리드타임(분)",h=280,month_range=month_range)
        sec(f"근무외 리드타임 추이 ({unit})")
        trend_chart({"근무외(분)":responded},
                    unit=unit,val_col="근무외리드타임(분)",agg="mean",
                    y_label="근무외리드타임(분)",h=260,month_range=month_range)

    with t2:
        if len(responded) > 0:
            col1,col2 = st.columns(2)
            with col1:
                fig = px.histogram(responded,x="근무내리드타임(분)",nbins=30,
                                   color_discrete_sequence=["#3b82f6"])
                fig.update_layout(height=280,margin=dict(t=30,b=40,l=0,r=10),
                                   title="근무내 분포",
                                   plot_bgcolor="rgba(0,0,0,0)",
                                   paper_bgcolor="rgba(0,0,0,0)",font=dict(size=11))
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                fig2 = px.histogram(responded,x="근무외리드타임(분)",nbins=30,
                                    color_discrete_sequence=["#f97316"])
                fig2.update_layout(height=280,margin=dict(t=30,b=40,l=0,r=10),
                                    title="근무외 분포",
                                    plot_bgcolor="rgba(0,0,0,0)",
                                    paper_bgcolor="rgba(0,0,0,0)",font=dict(size=11))
                st.plotly_chart(fig2, use_container_width=True)

            sec("대분류별 근무내 / 근무외 리드타임")
            cat_lt = (responded[responded["대분류"]!=""]
                      .groupby("대분류")
                      .agg(건수=("근무내리드타임(분)","count"),
                           근무내평균=("근무내리드타임(분)","mean"),
                           근무외평균=("근무외리드타임(분)","mean"))
                      .round(1).reset_index()
                      .sort_values("건수",ascending=False))
            fig3 = px.bar(cat_lt,x="대분류",y=["근무내평균","근무외평균"],
                          barmode="group",
                          color_discrete_map={
                              "근무내평균":"#3b82f6","근무외평균":"#f97316"},
                          labels={"value":"평균 리드타임(분)","variable":"구분"})
            chart_cfg(fig3,h=300)
            st.plotly_chart(fig3, use_container_width=True)

    with t3:
        sec("플랫폼별 인입 현황")
        plat_d = (board[board["플랫폼"]!=""]
                  .groupby("플랫폼").size()
                  .reset_index(name="건수")
                  .sort_values("건수",ascending=False))
        if len(plat_d) > 0:
            col1,col2 = st.columns([1,1])
            with col1:
                fig4 = px.pie(plat_d,names="플랫폼",values="건수",hole=0.6,
                              color_discrete_sequence=COLORS)
                fig4.update_traces(textposition="inside",
                                   textinfo="percent+label",textfont_size=11)
                fig4.update_layout(height=300,margin=dict(t=0,b=0,l=0,r=0),
                                   plot_bgcolor="rgba(0,0,0,0)",
                                   paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig4, use_container_width=True)
            with col2:
                if len(responded) > 0:
                    sec("플랫폼별 근무내 리드타임")
                    plt_lt = (responded[responded["플랫폼"]!=""]
                              .groupby("플랫폼")["근무내리드타임(분)"]
                              .mean().round(1).reset_index()
                              .sort_values("근무내리드타임(분)",ascending=True))
                    fig5 = px.bar(plt_lt,y="플랫폼",x="근무내리드타임(분)",
                                  orientation="h",color="플랫폼",
                                  color_discrete_sequence=COLORS,
                                  text="근무내리드타임(분)")
                    fig5.update_traces(textposition="outside",textfont_size=10)
                    fig5.update_layout(height=300,showlegend=False,
                                       margin=dict(t=10,b=10,l=0,r=60),
                                       plot_bgcolor="rgba(0,0,0,0)",
                                       paper_bgcolor="rgba(0,0,0,0)",
                                       font=dict(size=11))
                    st.plotly_chart(fig5, use_container_width=True)

    with t4:
        sec("게시판 로그 상세")
        show_cols = [c for c in
                     ["일자","브랜드","플랫폼","상담사명","미응대",
                      "접수일시","응답일시",
                      "근무내리드타임(분)","근무외리드타임(분)","전체리드타임(분)",
                      "대분류","중분류","소분류"]
                     if c in board.columns]
        compact_table(board[show_cols], height=400)

# ─────────────────────────────────────────────
# PAGE — 게시판 상담사
# ─────────────────────────────────────────────
def page_board_agent(board, unit, month_range):
    st.markdown('<div class="page-title">게시판 상담사 분석</div>',
                unsafe_allow_html=True)
    st.markdown(
        f'<div class="page-sub">상담사별 게시판 처리 성과'
        f'<span class="period-badge">{unit}</span></div>',
        unsafe_allow_html=True)

    if len(board) == 0:
        st.info("게시판 데이터가 없습니다.")
        return

    responded = board[~board["미응대"]]
    t1,t2,t3 = st.tabs(["상담사별 성과","팀별 현황","근속그룹별"])

    with t1:
        if len(responded) == 0:
            st.info("응답 데이터가 없습니다.")
        else:
            sec("상담사별 처리 현황")
            ag = (responded.groupby("상담사명")
                  .agg(처리건수=("근무내리드타임(분)","count"),
                       근무내평균=("근무내리드타임(분)","mean"),
                       근무외평균=("근무외리드타임(분)","mean"),
                       전체평균=("전체리드타임(분)","mean"))
                  .round(1).reset_index()
                  .sort_values("처리건수",ascending=False))
            cmap = make_color_map(ag["상담사명"].unique())
            fig = px.bar(ag.head(20),x="상담사명",y="처리건수",
                         color="상담사명",color_discrete_map=cmap,text="처리건수")
            fig.update_traces(textposition="outside",textfont_size=10)
            chart_cfg(fig,h=300)
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

            sec(f"상담사별 근무내 리드타임 추이 ({unit}) — Top5")
            cutoff = get_chart_range(unit, month_range)
            pc     = get_period_col(unit)
            top5   = ag.head(5)["상담사명"].tolist()
            fig2   = go.Figure()
            cmap2  = make_color_map(top5)
            for ag_name in top5:
                sub = responded[(responded["상담사명"]==ag_name) &
                                (responded["일자"]>=pd.Timestamp(cutoff))]
                if pc not in sub.columns or len(sub)==0: continue
                s = sub.groupby(pc)["근무내리드타임(분)"].mean().round(1).reset_index()
                fig2.add_trace(go.Scatter(
                    x=s[pc],y=s["근무내리드타임(분)"],
                    mode="lines+markers",name=ag_name,
                    line=dict(color=cmap2.get(ag_name,"#888"),width=2),
                    marker=dict(size=6)))
            chart_cfg(fig2,h=300)
            fig2.update_layout(hovermode="x unified")
            st.plotly_chart(fig2, use_container_width=True)

            with st.expander("상담사별 수치 테이블",expanded=False):
                compact_table(ag, height=320)

    with t2:
        if "팀명" in board.columns and len(responded)>0:
            sec("팀별 처리 현황")
            team_r = (responded.groupby("팀명")
                      .agg(처리건수=("근무내리드타임(분)","count"),
                           근무내평균=("근무내리드타임(분)","mean"),
                           근무외평균=("근무외리드타임(분)","mean"))
                      .round(1).reset_index()
                      .sort_values("처리건수",ascending=False))
            fig3 = px.bar(team_r,x="팀명",y="처리건수",
                          color="팀명",color_discrete_sequence=COLORS,text="처리건수")
            fig3.update_traces(textposition="outside",textfont_size=10)
            chart_cfg(fig3,h=280)
            fig3.update_layout(showlegend=False)
            st.plotly_chart(fig3, use_container_width=True)
            compact_table(team_r, height=240)
        else:
            st.info("팀명 정보가 없습니다.")

    with t3:
        if "근속그룹" in board.columns and len(responded)>0:
            sec("근속그룹별 평균 리드타임")
            tg = (responded.groupby("근속그룹")
                  .agg(처리건수=("근무내리드타임(분)","count"),
                       근무내평균=("근무내리드타임(분)","mean"),
                       근무외평균=("근무외리드타임(분)","mean"))
                  .round(1).reset_index())
            order = [g for _,g in TENURE_GROUPS]
            tg["순서"] = tg["근속그룹"].apply(
                lambda x: order.index(x) if x in order else 99)
            tg = tg.sort_values("순서")
            fig4 = px.bar(tg,x="근속그룹",y=["근무내평균","근무외평균"],
                          barmode="group",
                          color_discrete_map={
                              "근무내평균":"#3b82f6","근무외평균":"#f97316"},
                          text_auto=True,
                          labels={"value":"평균(분)","variable":"구분"})
            chart_cfg(fig4,h=300)
            st.plotly_chart(fig4, use_container_width=True)
            compact_table(tg.drop(columns=["순서"]), height=260)
        else:
            st.info("근속그룹 정보가 없습니다.")

# ─────────────────────────────────────────────
# PAGE — 상담사 종합
# ─────────────────────────────────────────────
def page_agent_total(phone, chat, board, unit, month_range):
    st.markdown('<div class="page-title">상담사 종합 분석</div>',
                unsafe_allow_html=True)
    st.markdown(
        f'<div class="page-sub">전채널 통합 상담사 성과 요약'
        f'<span class="period-badge">{unit}</span></div>',
        unsafe_allow_html=True)

    t1,t2 = st.tabs(["채널별 처리 현황","근속그룹 종합"])

    with t1:
        sec("상담사별 채널 처리건수")
        ph_ag = (phone[~phone["미응대"]].groupby("상담사명")
                 .size().reset_index(name="전화")
                 if len(phone)>0 else pd.DataFrame(columns=["상담사명","전화"]))
        ch_ag = (chat[~chat["미응대"]].groupby("상담사명")
                 .size().reset_index(name="채팅")
                 if len(chat)>0 else pd.DataFrame(columns=["상담사명","채팅"]))
        bo_ag = (board[~board["미응대"]].groupby("상담사명")
                 .size().reset_index(name="게시판")
                 if len(board)>0 else pd.DataFrame(columns=["상담사명","게시판"]))
        merged = (ph_ag.merge(ch_ag,on="상담사명",how="outer")
                       .merge(bo_ag,on="상담사명",how="outer")
                       .fillna(0))
        merged[["전화","채팅","게시판"]] = (
            merged[["전화","채팅","게시판"]].astype(int))
        merged["합계"] = merged["전화"]+merged["채팅"]+merged["게시판"]
        merged = merged.sort_values("합계",ascending=False)

        if len(merged) > 0:
            mlt = merged.head(20).melt(
                id_vars="상담사명",value_vars=["전화","채팅","게시판"],
                var_name="채널",value_name="건수")
            fig = px.bar(mlt,x="상담사명",y="건수",color="채널",
                         barmode="stack",
                         color_discrete_map={
                             "전화":"#3b82f6","채팅":"#22c55e","게시판":"#f97316"})
            chart_cfg(fig,h=360)
            st.plotly_chart(fig, use_container_width=True)

            sec(f"전화 처리건수 추이 ({unit}) — Top5 상담사")
            top5   = merged.head(5)["상담사명"].tolist()
            cutoff = get_chart_range(unit, month_range)
            pc     = get_period_col(unit)
            fig2   = go.Figure()
            cmap   = make_color_map(top5)
            for ag_name in top5:
                if len(phone)==0: break
                sub = phone[(~phone["미응대"]) &
                            (phone["상담사명"]==ag_name) &
                            (phone["일자"]>=pd.Timestamp(cutoff))]
                if pc not in sub.columns or len(sub)==0: continue
                s = sub.groupby(pc).size().reset_index(name="건수")
                fig2.add_trace(go.Scatter(
                    x=s[pc],y=s["건수"],mode="lines+markers",name=ag_name,
                    line=dict(color=cmap.get(ag_name,"#888"),width=2),
                    marker=dict(size=6)))
            chart_cfg(fig2,h=300)
            fig2.update_layout(hovermode="x unified")
            st.plotly_chart(fig2, use_container_width=True)

            with st.expander("상담사별 채널 처리 테이블",expanded=False):
                compact_table(merged, height=360)

    with t2:
        if all("근속그룹" in df.columns for df in [phone,chat,board]):
            sec("근속그룹별 채널 처리 현황")
            ph_tg = (phone[~phone["미응대"]].groupby("근속그룹")
                     .size().reset_index(name="전화")
                     if len(phone)>0 else pd.DataFrame(columns=["근속그룹","전화"]))
            ch_tg = (chat[~chat["미응대"]].groupby("근속그룹")
                     .size().reset_index(name="채팅")
                     if len(chat)>0 else pd.DataFrame(columns=["근속그룹","채팅"]))
            bo_tg = (board[~board["미응대"]].groupby("근속그룹")
                     .size().reset_index(name="게시판")
                     if len(board)>0 else pd.DataFrame(columns=["근속그룹","게시판"]))
            tg_all = (ph_tg.merge(ch_tg,on="근속그룹",how="outer")
                           .merge(bo_tg,on="근속그룹",how="outer")
                           .fillna(0))
            tg_all[["전화","채팅","게시판"]] = (
                tg_all[["전화","채팅","게시판"]].astype(int))
            order = [g for _,g in TENURE_GROUPS]
            tg_all["순서"] = tg_all["근속그룹"].apply(
                lambda x: order.index(x) if x in order else 99)
            tg_all = tg_all.sort_values("순서")

            mlt2 = tg_all.melt(
                id_vars="근속그룹",value_vars=["전화","채팅","게시판"],
                var_name="채널",value_name="건수")
            fig3 = px.bar(mlt2,x="근속그룹",y="건수",color="채널",barmode="group",
                          color_discrete_map={
                              "전화":"#3b82f6","채팅":"#22c55e","게시판":"#f97316"})
            chart_cfg(fig3,h=320)
            st.plotly_chart(fig3, use_container_width=True)
            compact_table(tg_all.drop(columns=["순서"]), height=260)
        else:
            st.info("근속그룹 정보가 없습니다.")

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
def render_sidebar(phone, chat, board):
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:6px 0 14px">
            <div style="font-size:16px;font-weight:800;color:#fff;
                        letter-spacing:0.5px">Contact Center OPS</div>
            <div style="font-size:10px;color:#7a9cc6;margin-top:2px">
                운영 분석 대시보드</div>
        </div>""", unsafe_allow_html=True)
        st.markdown("---")

        st.markdown('<span class="sb-group">데이터</span>',
                    unsafe_allow_html=True)
        if st.button("데이터 새로고침", key="refresh"):
            st.cache_data.clear(); st.rerun()
        st.markdown("---")

        st.markdown('<span class="sb-group">기간 단위</span>',
                    unsafe_allow_html=True)
        unit = st.radio("", ["일별","주별","월별"],
                        horizontal=True, key="unit",
                        label_visibility="collapsed")
        month_range = 3
        if unit == "월별":
            month_range = st.slider("추이 표시 개월 수", 1, 6, 3, key="mrange")

        st.markdown("---")

        all_dates = pd.concat([
            phone["일자"] if len(phone)>0 else pd.Series(dtype="datetime64[ns]"),
            chat["일자"]  if len(chat)>0  else pd.Series(dtype="datetime64[ns]"),
            board["일자"] if len(board)>0 else pd.Series(dtype="datetime64[ns]"),
        ]).dropna()

        if len(all_dates) == 0:
            min_d = datetime.today().date()
            max_d = datetime.today().date()
        else:
            min_d = all_dates.min().date()
            max_d = all_dates.max().date()

        st.markdown('<span class="sb-group">날짜 필터</span>',
                    unsafe_allow_html=True)
        qc1,qc2,qc3 = st.columns(3)
        with qc1:
            if st.button("7일", key="q7"):
                st.session_state["_ps"] = max_d - timedelta(days=6)
                st.session_state["_pe"] = max_d
                st.session_state["_dv"] = st.session_state.get("_dv",0)+1
        with qc2:
            if st.button("30일", key="q30"):
                st.session_state["_ps"] = max_d - timedelta(days=29)
                st.session_state["_pe"] = max_d
                st.session_state["_dv"] = st.session_state.get("_dv",0)+1
        with qc3:
            if st.button("전체", key="qall"):
                st.session_state["_ps"] = min_d
                st.session_state["_pe"] = max_d
                st.session_state["_dv"] = st.session_state.get("_dv",0)+1

        ver = st.session_state.get("_dv", 0)
        ps  = st.session_state.get("_ps", min_d)
        pe  = st.session_state.get("_pe", max_d)
        ps  = max(min_d, min(max_d, ps))
        pe  = max(min_d, min(max_d, pe))
        if ps > pe: ps = pe

        d_start = st.date_input("시작일", value=ps,
                                min_value=min_d, max_value=max_d,
                                key=f"ds_{ver}")
        d_end   = st.date_input("종료일", value=pe,
                                min_value=min_d, max_value=max_d,
                                key=f"de_{ver}")
        st.markdown("---")

        st.markdown('<span class="sb-group">브랜드 필터</span>',
                    unsafe_allow_html=True)
        all_brands = sorted(set(
            (phone["브랜드"].dropna().unique().tolist() if len(phone)>0 else []) +
            (chat["브랜드"].dropna().unique().tolist()  if len(chat)>0  else []) +
            (board["브랜드"].dropna().unique().tolist() if len(board)>0 else [])
        ))
        sel_brands = st.multiselect("브랜드", all_brands, default=[],
                                    key="sb", placeholder="미선택 = 전체")
        st.markdown("---")

        if "menu" not in st.session_state:
            st.session_state.menu = "전체 현황"

        for group, items in MENU_GROUPS.items():
            st.markdown(f'<span class="sb-group">{group}</span>',
                        unsafe_allow_html=True)
            for name in items:
                if st.button(name, key=f"m_{name}"):
                    st.session_state.menu = name
                    st.rerun()

        st.markdown("---")
        st.markdown("""
        <div style="text-align:center">
            <span style="font-size:9px;color:#4a6fa5">
                Contact Center OPS v1.1
            </span>
        </div>""", unsafe_allow_html=True)

    return d_start, d_end, sel_brands, unit, month_range

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    agent_df = load_agent()
    phone_df = load_phone()
    chat_df  = load_chat()
    board_df = load_board()

    if all(len(df)==0 for df in [phone_df, chat_df, board_df]):
        st.markdown("""
        <div style="text-align:center;padding:80px 40px;background:#fff;
                    border-radius:20px;margin:40px auto;max-width:500px;
                    box-shadow:0 2px 12px rgba(0,0,0,.06)">
            <div style="font-size:20px;font-weight:800;color:#0f172a;margin-bottom:8px">
                데이터 연결 필요
            </div>
            <div style="font-size:13px;color:#64748b;margin-bottom:4px">
                Google Sheets GID 설정을 확인해주세요
            </div>
            <div style="font-size:12px;color:#94a3b8">
                SHEET_ID와 GID_MAP이 올바르게 설정되면 자동으로 로드됩니다
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    base_date = datetime.today()
    phone_df  = merge_agent(phone_df, agent_df, base_date)
    chat_df   = merge_agent(chat_df,  agent_df, base_date)
    board_df  = merge_agent(board_df, agent_df, base_date)

    d_start, d_end, sel_brands, unit, month_range = render_sidebar(
        phone_df, chat_df, board_df)

    phone_f = filter_df(phone_df, (d_start, d_end), sel_brands)
    chat_f  = filter_df(chat_df,  (d_start, d_end), sel_brands)
    board_f = filter_df(board_df, (d_start, d_end), sel_brands)

    menu = st.session_state.get("menu", "전체 현황")

    if   menu == "전체 현황":     page_overview(phone_f,chat_f,board_f,unit,month_range)
    elif menu == "전화 현황":     page_phone(phone_f,unit,month_range)
    elif menu == "전화 상담사":   page_phone_agent(phone_f,unit,month_range)
    elif menu == "채팅 현황":     page_chat(chat_f,unit,month_range)
    elif menu == "채팅 상담사":   page_chat_agent(chat_f,unit,month_range)
    elif menu == "게시판 현황":   page_board(board_f,unit,month_range)
    elif menu == "게시판 상담사": page_board_agent(board_f,unit,month_range)
    elif menu == "상담사 종합":   page_agent_total(phone_f,chat_f,board_f,unit,month_range)

if __name__ == "__main__":
    main()
