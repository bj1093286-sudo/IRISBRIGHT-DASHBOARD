import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import holidays

# ─────────────────────────────────────────────
# SHEET 설정
# ─────────────────────────────────────────────
SHEET_ID = "1dcAiu3SeFb4OU4xZaen8qfjqKf64GJtasXCK6t-OEvw"
GID_MAP = {
    "agent": "0",
    "phone": "754152852",
    "chat":  "1359982286",
    "board": "677677090",
}

WORK_START = 10
WORK_END   = 18

COLORS = {
    "primary": "#6366f1",
    "success": "#22c55e",
    "danger":  "#ef4444",
    "warning": "#f59e0b",
    "info":    "#3b82f6",
    "neutral": "#94a3b8",
    "phone":   "#6366f1",
    "chat":    "#22c55e",
    "board":   "#f59e0b",
}

TENURE_GROUPS = [
    (14,   "신입1 (2주이내)"),
    (30,   "신입2 (1개월이내)"),
    (60,   "신입3 (2개월이내)"),
    (90,   "신입4 (3개월이내)"),
    (180,  "신입5 (6개월이내)"),
    (365,  "신입6 (1년이내)"),
    (548,  "기존1 (1.5년이내)"),
    (730,  "기존2 (2년이내)"),
    (1095, "기존3 (3년이내)"),
    (1460, "기존4 (4년이내)"),
    (9999, "기존5 (4년초과)"),
]

MENU_GROUPS = {
    "전체 현황": ["전체 현황"],
    "사업자":    ["사업자 현황"],
    "전화":      ["전화 현황", "전화 상담사"],
    "채팅":      ["채팅 현황", "채팅 상담사"],
    "게시판":    ["게시판 현황", "게시판 상담사"],
    "상담사":    ["상담사 종합"],
}

# ─────────────────────────────────────────────
# 페이지 설정
# ─────────────────────────────────────────────
st.set_page_config(page_title="Contact Center OPS", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: #F5F6F8 !important;
    color: #0f172a;
}
section[data-testid="stSidebar"] {
    background: #1e293b !important;
    border-right: none !important;
    width: 220px !important;
}
section[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
section[data-testid="stSidebar"] .stButton > button {
    background: #334155 !important;
    border: none !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    width: 100% !important;
    text-align: left !important;
    padding: 10px 14px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    margin-bottom: 2px !important;
    transition: background 0.15s !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: #6366f1 !important;
    color: #fff !important;
}
.main .block-container {
    padding: 24px 32px !important;
    max-width: 100% !important;
    background: #F5F6F8 !important;
}
.dash-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 28px;
    padding: 20px 28px;
    background: #fff;
    border-radius: 20px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.dash-header-left h1 {
    font-size: 22px;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.5px;
    margin-bottom: 4px;
}
.dash-header-left span { font-size: 12px; color: #94a3b8; font-weight: 400; }
.card {
    background: #fff;
    border-radius: 20px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    padding: 24px;
    margin-bottom: 20px;
}
.card-title { font-size: 14px; font-weight: 700; color: #0f172a; margin-bottom: 16px; }
.kpi-card {
    background: #fff;
    border-radius: 20px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    padding: 22px 24px;
    height: 100%;
}
.kpi-label {
    font-size: 11px;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 10px;
}
.kpi-value {
    font-size: 26px;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -1px;
    line-height: 1;
    margin-bottom: 8px;
}
.kpi-unit { font-size: 13px; color: #94a3b8; margin-left: 4px; font-weight: 400; }
.kpi-delta-row { display: flex; gap: 6px; flex-wrap: wrap; align-items: center; margin-top: 6px; }
.kpi-delta {
    display: inline-flex;
    align-items: center;
    gap: 3px;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 8px;
    border-radius: 20px;
}
.kpi-delta.up   { background: #fef2f2; color: #ef4444; }
.kpi-delta.down { background: #f0fdf4; color: #22c55e; }
.kpi-delta.neu  { background: #f8fafc; color: #94a3b8; }
.kpi-delta.up.rev   { background: #f0fdf4 !important; color: #22c55e !important; }
.kpi-delta.down.rev { background: #fef2f2 !important; color: #ef4444 !important; }
.section-title {
    font-size: 15px;
    font-weight: 700;
    color: #0f172a;
    margin: 24px 0 12px;
    letter-spacing: -0.3px;
}
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
div[data-testid="stToolbar"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 유틸
# ─────────────────────────────────────────────
def hex_rgba(hex_color: str, alpha: float = 0.08) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

def fmt_sec(sec):
    try:
        sec = int(float(sec))
    except:
        return "0s"
    if sec <= 0:
        return "0s"
    if sec < 60:
        return f"{sec}s"
    elif sec < 3600:
        return f"{sec//60}m {sec%60:02d}s"
    else:
        return f"{sec//3600}h {(sec%3600)//60:02d}m"

def fmt_pct(val):
    try:
        return f"{float(val):.1f}%"
    except:
        return "0.0%"

def get_tenure_group(hire_date, base_date):
    try:
        if pd.isna(hire_date):
            return "미입력"
    except:
        return "미입력"
    # 둘 다 date 객체로 통일
    if isinstance(hire_date, pd.Timestamp):
        hire = hire_date.date()
    elif isinstance(hire_date, datetime):
        hire = hire_date.date()
    elif isinstance(hire_date, date):
        hire = hire_date
    else:
        try:
            hire = pd.Timestamp(hire_date).date()
        except:
            return "미입력"

    if isinstance(base_date, pd.Timestamp):
        base = base_date.date()
    elif isinstance(base_date, datetime):
        base = base_date.date()
    elif isinstance(base_date, date):
        base = base_date
    else:
        try:
            base = pd.Timestamp(base_date).date()
        except:
            return "미입력"

    days = (base - hire).days
    for threshold, label in TENURE_GROUPS:
        if days <= threshold:
            return label
    return "기존5 (4년초과)"

def is_holiday_kr(d):
    try:
        kr = holidays.KR(years=d.year)
        return d in kr
    except:
        return False

def is_workday(d):
    return d.weekday() < 5 and not is_holiday_kr(d)

def gsheet_url(gid: str) -> str:
    return f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"

# ─────────────────────────────────────────────
# 기간 유틸
# ─────────────────────────────────────────────
def get_period_col(unit):
    return {"일별": "일자", "주별": "주차", "월별": "월"}[unit]

def assign_period_cols(df, date_col="일자"):
    if date_col not in df.columns:
        return df
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df["일자"] = df[date_col]
    df["주차"] = df[date_col].dt.to_period("W").dt.start_time
    df["월"]   = df[date_col].dt.to_period("M").dt.start_time
    return df

def get_chart_range(unit, end_date, month_range=3):
    if isinstance(end_date, date) and not isinstance(end_date, datetime):
        end_date = datetime.combine(end_date, datetime.min.time())
    if unit == "일별":
        return end_date - timedelta(days=89), end_date
    elif unit == "주별":
        return end_date - timedelta(weeks=12), end_date
    else:
        return end_date - timedelta(days=30 * month_range), end_date

# ─────────────────────────────────────────────
# 데이터 로드
# ─────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def load_agent():
    try:
        df = pd.read_csv(gsheet_url(GID_MAP["agent"]))
        df.columns = df.columns.str.strip()
        df["입사일"] = pd.to_datetime(df["입사일"], errors="coerce")
        return df
    except:
        return pd.DataFrame(columns=["상담사명", "팀명", "입사일"])

@st.cache_data(ttl=300, show_spinner=False)
def load_phone():
    try:
        df = pd.read_csv(gsheet_url(GID_MAP["phone"]))
        df.columns = df.columns.str.strip()
        df["일자"] = pd.to_datetime(df["일자"], errors="coerce")
        df["인입시각"] = pd.to_datetime(
            df["일자"].astype(str) + " " + df["인입시각"].astype(str), errors="coerce"
        )
        for col in ["통화시간(초)", "ACW시간(초)", "대기시간(초)"]:
            df[col] = pd.to_numeric(df.get(col, 0), errors="coerce").fillna(0)
        df["AHT(초)"]    = df["통화시간(초)"] + df["ACW시간(초)"]
        df["응대여부"]   = df["상담사명"].apply(lambda x: "미응대" if str(x).strip() == "미응대" else "응대")
        df["인입시간대"] = df["인입시각"].dt.hour
        df = assign_period_cols(df, "일자")
        return df
    except Exception as e:
        return pd.DataFrame(columns=["일자","사업자명","브랜드","상담사명","인입시각",
                                      "대기시간(초)","통화시간(초)","ACW시간(초)",
                                      "대분류","중분류","소분류","AHT(초)","응대여부","인입시간대","주차","월"])

@st.cache_data(ttl=300, show_spinner=False)
def load_chat():
    try:
        df = pd.read_csv(gsheet_url(GID_MAP["chat"]))
        df.columns = df.columns.str.strip()
        df["일자"]          = pd.to_datetime(df["일자"], errors="coerce")
        df["접수일시"]      = pd.to_datetime(df["접수일시"], errors="coerce")
        df["첫멘트발송일시"] = pd.to_datetime(df["첫멘트발송일시"], errors="coerce")
        df["종료일시"]      = pd.to_datetime(df["종료일시"], errors="coerce")
        df["응답시간(초)"]  = (df["첫멘트발송일시"] - df["접수일시"]).dt.total_seconds().clip(lower=0)
        df["리드타임(초)"]  = (df["종료일시"] - df["접수일시"]).dt.total_seconds().clip(lower=0)
        포기 = df["배분전포기여부"].astype(str).str.strip().str.upper() if "배분전포기여부" in df.columns else pd.Series(["N"]*len(df))
        df["응대여부"] = df.apply(
            lambda r: "미응대" if pd.isna(r["첫멘트발송일시"]) or 포기.iloc[r.name] == "Y" else "응대", axis=1
        )
        df["인입시간대"] = df["접수일시"].dt.hour
        df = assign_period_cols(df, "일자")
        return df
    except:
        return pd.DataFrame(columns=["일자","사업자명","브랜드","플랫폼","상담사명",
                                      "접수일시","첫멘트발송일시","종료일시","배분전포기여부",
                                      "대분류","중분류","소분류","응답시간(초)","리드타임(초)",
                                      "응대여부","인입시간대","주차","월"])

@st.cache_data(ttl=300, show_spinner=False)
def load_board():
    try:
        df = pd.read_csv(gsheet_url(GID_MAP["board"]))
        df.columns = df.columns.str.strip()
        df["일자"]     = pd.to_datetime(df["일자"], errors="coerce")
        df["접수일시"] = pd.to_datetime(df["접수일시"], errors="coerce")
        df["응답일시"] = pd.to_datetime(df["응답일시"], errors="coerce")
        df["리드타임(초)"] = (df["응답일시"] - df["접수일시"]).dt.total_seconds().clip(lower=0)
        df["응대여부"]     = df["응답일시"].apply(lambda x: "미응대" if pd.isna(x) else "응대")
        df["인입시간대"]   = df["접수일시"].dt.hour
        df = assign_period_cols(df, "일자")
        return df
    except:
        return pd.DataFrame(columns=["일자","사업자명","브랜드","플랫폼","상담사명",
                                      "접수일시","응답일시","대분류","중분류","소분류",
                                      "리드타임(초)","응대여부","인입시간대","주차","월"])

def merge_agent(df, agent_df, base_date):
    if agent_df.empty or "상담사명" not in df.columns:
        df = df.copy()
        df["팀명"]   = "미지정"
        df["근속그룹"] = "미입력"
        return df
    merged = df.merge(agent_df[["상담사명", "팀명", "입사일"]], on="상담사명", how="left")
    merged["팀명"] = merged["팀명"].fillna("미지정")
    # base_date를 date 객체로 통일
    if isinstance(base_date, datetime):
        base_d = base_date.date()
    elif isinstance(base_date, pd.Timestamp):
        base_d = base_date.date()
    else:
        base_d = base_date
    merged["근속그룹"] = merged["입사일"].apply(lambda x: get_tenure_group(x, base_d))
    return merged

# ─────────────────────────────────────────────
# 필터
# ─────────────────────────────────────────────
def filter_df(df, start, end, brands=None, operators=None):
    if df.empty:
        return df
    if "일자" not in df.columns:
        return df
    mask = (df["일자"] >= pd.Timestamp(start)) & (df["일자"] <= pd.Timestamp(end))
    df = df[mask].copy()
    if brands and "브랜드" in df.columns:
        df = df[df["브랜드"].isin(brands)]
    if operators and "사업자명" in df.columns:
        df = df[df["사업자명"].isin(operators)]
    return df

# ─────────────────────────────────────────────
# KPI 카드
# ─────────────────────────────────────────────
def kpi_card(label, value, delta_curr=None, delta_yoy=None, reverse=False, unit=""):
    def badge(val, rev):
        if val is None:
            return ""
        sign = "▲" if val > 0 else ("▼" if val < 0 else "—")
        direction = "up" if val > 0 else ("down" if val < 0 else "neu")
        rev_cls = " rev" if rev else ""
        return f'<span class="kpi-delta {direction}{rev_cls}">{sign} {abs(val):.1f}%</span>'

    delta_html = ""
    if delta_curr is not None:
        delta_html += badge(delta_curr, reverse)
    if delta_yoy is not None:
        delta_html += '<span style="font-size:10px;color:#94a3b8;margin:0 4px;">YoY</span>'
        delta_html += badge(delta_yoy, reverse)

    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}<span class="kpi-unit">{unit}</span></div>
        <div class="kpi-delta-row">{delta_html}</div>
    </div>
    """

def calc_delta(curr, prev):
    try:
        if prev is None or float(prev) == 0:
            return None
        return round((float(curr) - float(prev)) / float(prev) * 100, 1)
    except:
        return None

# ─────────────────────────────────────────────
# 차트
# ─────────────────────────────────────────────
def base_layout(h=320, title=""):
    return dict(
        height=h,
        title=dict(text=title, font=dict(size=13, color="#0f172a", family="Inter"), x=0),
        margin=dict(l=8, r=8, t=40 if title else 16, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", size=11, color="#64748b"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(size=11)),
        xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=10)),
        yaxis=dict(showgrid=True, gridcolor="#f1f5f9", zeroline=False, tickfont=dict(size=10)),
    )

def trend_chart(series_dict, unit, y_label="건수", h=320, month_range=3, title=""):
    pc = get_period_col(unit)
    fig = go.Figure()
    palette = [COLORS["primary"], COLORS["success"], COLORS["warning"], COLORS["info"], COLORS["danger"]]
    for i, (name, s) in enumerate(series_dict.items()):
        if s is None or s.empty or pc not in s.columns or y_label not in s.columns:
            continue
        color = palette[i % len(palette)]
        fig.add_trace(go.Scatter(
            x=s[pc], y=s[y_label],
            mode="lines+markers",
            name=name,
            line=dict(color=color, width=2.5),
            marker=dict(size=6, color=color),
            fill="tozeroy",
            fillcolor=hex_rgba(color, 0.07),
        ))
    fig.update_layout(**base_layout(h, title))
    return fig

def donut_chart(labels, values, colors=None, h=260, title=""):
    palette = [COLORS["primary"], COLORS["success"], COLORS["warning"], COLORS["info"], COLORS["danger"]]
    if colors is None:
        colors = palette
    total = sum(v for v in values if v) if values else 0
    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.62,
        marker=dict(colors=colors[:len(labels)], line=dict(color="#fff", width=3)),
        textinfo="none",
        hovertemplate="%{label}: %{value:,}건 (%{percent})<extra></extra>",
    ))
    fig.update_layout(
        **base_layout(h, title),
        annotations=[dict(
            text=f"<b>{total:,}</b>",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=18, color="#0f172a", family="Inter"),
        )],
        legend=dict(orientation="v", yanchor="middle", y=0.5,
                    xanchor="left", x=1.02, font=dict(size=11)),
    )
    return fig

def heatmap_chart(df_pivot, h=320, title=""):
    fig = go.Figure(go.Heatmap(
        z=df_pivot.values,
        x=df_pivot.columns.astype(str),
        y=df_pivot.index.astype(str),
        colorscale=[[0, "#f8fafc"], [0.5, "#818cf8"], [1, "#4338ca"]],
        showscale=True,
        hovertemplate="시간대: %{x}시<br>날짜: %{y}<br>건수: %{z}<extra></extra>",
    ))
    fig.update_layout(**base_layout(h, title))
    return fig

# ─────────────────────────────────────────────
# 전체 현황
# ─────────────────────────────────────────────
def page_overview(phone, chat, board, unit, month_range, start, end):
    updated = datetime.now().strftime("%Y-%m-%d %H:%M")
    st.markdown(f"""
    <div class="dash-header">
        <div class="dash-header-left">
            <h1>Contact Center Dashboard</h1>
            <span>Updated {updated}</span>
        </div>
        <div class="dash-header-right">
            <span style="font-size:12px;color:#64748b;background:#f1f5f9;
                         padding:6px 14px;border-radius:20px;font-weight:600;">
                {start.strftime("%Y.%m.%d") if hasattr(start,"strftime") else start} ~
                {end.strftime("%Y.%m.%d") if hasattr(end,"strftime") else end}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    t_ph = len(phone)
    t_ch = len(chat)
    t_bo = len(board)
    t_all = t_ph + t_ch + t_bo

    r_ph = len(phone[phone["응대여부"]=="응대"]) if not phone.empty else 0
    r_ch = len(chat[chat["응대여부"]=="응대"])   if not chat.empty  else 0
    r_bo = len(board[board["응대여부"]=="응대"]) if not board.empty else 0

    rr_ph = r_ph/t_ph*100 if t_ph else 0
    rr_ch = r_ch/t_ch*100 if t_ch else 0
    rr_bo = r_bo/t_bo*100 if t_bo else 0

    c1,c2,c3,c4 = st.columns(4)
    for col, label, val, u in [
        (c1,"전체 인입",f"{t_all:,}","건"),
        (c2,"전화 인입",f"{t_ph:,}","건"),
        (c3,"채팅 인입",f"{t_ch:,}","건"),
        (c4,"게시판 인입",f"{t_bo:,}","건"),
    ]:
        with col:
            st.markdown(kpi_card(label, val, unit=u), unsafe_allow_html=True)

    st.markdown('<div class="section-title">채널별 응대율</div>', unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    for col, label, val in [
        (c1,"전화 응대율",fmt_pct(rr_ph)),
        (c2,"채팅 응대율",fmt_pct(rr_ch)),
        (c3,"게시판 응대율",fmt_pct(rr_bo)),
    ]:
        with col:
            st.markdown(kpi_card(label, val), unsafe_allow_html=True)

    st.markdown('<div class="section-title">채널별 인입 분포 & 추이</div>', unsafe_allow_html=True)
    col_d, col_t = st.columns([1, 2])

    with col_d:
        fig = donut_chart(
            ["전화","채팅","게시판"],
            [t_ph, t_ch, t_bo],
            [COLORS["phone"], COLORS["chat"], COLORS["board"]],
            title="채널 분포"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_t:
        pc = get_period_col(unit)
        cr_s, cr_e = get_chart_range(unit, end, month_range)

        def agg(df):
            if df.empty or pc not in df.columns:
                return pd.DataFrame(columns=[pc,"건수"])
            return df[df[pc] >= pd.Timestamp(cr_s)].groupby(pc).size().reset_index(name="건수")

        fig2 = trend_chart(
            {"전화": agg(phone), "채팅": agg(chat), "게시판": agg(board)},
            unit=unit, y_label="건수", title="채널별 인입 추이"
        )
        st.plotly_chart(fig2, use_container_width=True)

# ─────────────────────────────────────────────
# 사업자 현황
# ─────────────────────────────────────────────
def page_operator(phone, chat, board, unit, month_range):
    st.markdown('<div class="section-title">사업자별 인입 현황</div>', unsafe_allow_html=True)

    def op_summary(df, ch):
        if df.empty or "사업자명" not in df.columns:
            return pd.DataFrame()
        g = df.groupby("사업자명").agg(
            인입=("사업자명","count"),
            응대=("응대여부", lambda x: (x=="응대").sum()),
        ).reset_index()
        g["응대율"] = (g["응대"]/g["인입"]*100).round(1)
        g["채널"] = ch
        return g

    all_op = pd.concat([
        op_summary(phone,"전화"),
        op_summary(chat,"채팅"),
        op_summary(board,"게시판"),
    ])

    if all_op.empty:
        st.info("사업자명 데이터가 없습니다.")
        return

    fig = px.bar(all_op, x="사업자명", y="인입", color="채널", barmode="stack",
                 color_discrete_map={"전화":COLORS["phone"],"채팅":COLORS["chat"],"게시판":COLORS["board"]})
    fig.update_layout(**base_layout(360,"사업자별 채널 인입"))
    st.plotly_chart(fig, use_container_width=True)

    try:
        pivot = all_op.pivot_table(index="사업자명", columns="채널",
                                   values=["인입","응대율"], aggfunc="first")
        st.dataframe(pivot, use_container_width=True)
    except:
        st.dataframe(all_op, use_container_width=True)

# ─────────────────────────────────────────────
# 전화 현황
# ─────────────────────────────────────────────
def page_phone(phone, unit, month_range, start, end):
    if phone.empty:
        st.info("전화 데이터가 없습니다.")
        return

    resp = phone[phone["응대여부"]=="응대"]
    total    = len(phone)
    resp_cnt = len(resp)
    rr       = resp_cnt/total*100 if total else 0
    avg_wait = resp["대기시간(초)"].mean() if not resp.empty else 0
    avg_talk = resp["통화시간(초)"].mean() if not resp.empty else 0
    avg_acw  = resp["ACW시간(초)"].mean()  if not resp.empty else 0
    avg_aht  = resp["AHT(초)"].mean()      if not resp.empty else 0

    cols = st.columns(6)
    for col, label, val, u in [
        (cols[0],"전체 인입",f"{total:,}","건"),
        (cols[1],"응대",f"{resp_cnt:,}","건"),
        (cols[2],"응대율",fmt_pct(rr),""),
        (cols[3],"평균 대기시간",fmt_sec(avg_wait),""),
        (cols[4],"평균 통화시간",fmt_sec(avg_talk),""),
        (cols[5],"평균 AHT",fmt_sec(avg_aht),""),
    ]:
        with col:
            st.markdown(kpi_card(label, val, unit=u), unsafe_allow_html=True)

    st.markdown('<div class="section-title">인입 / 응대 추이</div>', unsafe_allow_html=True)
    pc = get_period_col(unit)
    cr_s, _ = get_chart_range(unit, end, month_range)

    ph_in = phone[phone[pc]>=pd.Timestamp(cr_s)].groupby(pc).size().reset_index(name="건수")
    ph_re = resp[resp[pc]>=pd.Timestamp(cr_s)].groupby(pc).size().reset_index(name="건수")

    col_t, col_d = st.columns([2,1])
    with col_t:
        fig = trend_chart({"전화 인입":ph_in,"응대":ph_re},
                          unit=unit, y_label="건수", title="인입 / 응대 추이")
        st.plotly_chart(fig, use_container_width=True)
    with col_d:
        fig2 = donut_chart(["응대","미응대"],[resp_cnt, total-resp_cnt],
                           [COLORS["success"],COLORS["danger"]], title="응대 현황")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown('<div class="section-title">시간대별 인입 현황</div>', unsafe_allow_html=True)
    hourly = phone.groupby("인입시간대").agg(
        인입=("인입시간대","count"),
        응대=("응대여부", lambda x: (x=="응대").sum()),
    ).reset_index()
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(x=hourly["인입시간대"], y=hourly["인입"],
                          name="인입", marker_color=hex_rgba(COLORS["phone"],0.5)))
    fig3.add_trace(go.Bar(x=hourly["인입시간대"], y=hourly["응대"],
                          name="응대", marker_color=COLORS["phone"]))
    fig3.update_layout(**base_layout(300,"시간대별 인입 / 응대"))
    st.plotly_chart(fig3, use_container_width=True)

    if not resp.empty:
        st.markdown('<div class="section-title">AHT 구성 분석</div>', unsafe_allow_html=True)
        aht_df = resp.groupby(pc).agg(
            통화시간=("통화시간(초)","mean"),
            ACW시간=("ACW시간(초)","mean"),
        ).reset_index()
        fig4 = go.Figure()
        fig4.add_trace(go.Bar(x=aht_df[pc], y=aht_df["통화시간"],
                              name="통화시간", marker_color=COLORS["primary"]))
        fig4.add_trace(go.Bar(x=aht_df[pc], y=aht_df["ACW시간"],
                              name="ACW", marker_color=COLORS["warning"]))
        fig4.update_layout(barmode="stack", **base_layout(300,"기간별 평균 AHT 구성"))
        st.plotly_chart(fig4, use_container_width=True)

    if "대분류" in phone.columns:
        st.markdown('<div class="section-title">문의 유형 분석</div>', unsafe_allow_html=True)
        cat_df = phone.groupby("대분류").size().reset_index(name="건수").sort_values("건수",ascending=False)
        fig5 = px.bar(cat_df, x="대분류", y="건수",
                      color_discrete_sequence=[COLORS["primary"]])
        fig5.update_layout(**base_layout(300,"대분류별 인입"))
        st.plotly_chart(fig5, use_container_width=True)

    st.markdown('<div class="section-title">인입 히트맵 (날짜 × 시간대)</div>', unsafe_allow_html=True)
    if "인입시간대" in phone.columns and "일자" in phone.columns:
        tmp = phone.copy()
        tmp["일자str"] = tmp["일자"].dt.strftime("%m-%d")
        pivot = tmp.pivot_table(index="일자str", columns="인입시간대",
                                values="응대여부", aggfunc="count", fill_value=0)
        fig6 = heatmap_chart(pivot, title="날짜 × 시간대 인입 히트맵")
        st.plotly_chart(fig6, use_container_width=True)

# ─────────────────────────────────────────────
# 전화 상담사
# ─────────────────────────────────────────────
def page_phone_agent(phone, unit, month_range):
    if phone.empty:
        st.info("전화 데이터가 없습니다.")
        return
    resp = phone[phone["응대여부"]=="응대"]
    if resp.empty:
        st.info("응대 데이터가 없습니다.")
        return

    st.markdown('<div class="section-title">상담사별 전화 성과</div>', unsafe_allow_html=True)
    ag = resp.groupby("상담사명").agg(
        응대수=("상담사명","count"),
        평균대기=("대기시간(초)","mean"),
        평균통화=("통화시간(초)","mean"),
        평균ACW=("ACW시간(초)","mean"),
        평균AHT=("AHT(초)","mean"),
    ).round(1).reset_index().sort_values("응대수",ascending=False)
    st.dataframe(ag, use_container_width=True, height=400)

    if "팀명" in resp.columns:
        st.markdown('<div class="section-title">팀별 평균 AHT</div>', unsafe_allow_html=True)
        tm = resp.groupby("팀명").agg(응대수=("팀명","count"), 평균AHT=("AHT(초)","mean")).round(1).reset_index()
        fig = px.bar(tm, x="팀명", y="평균AHT", color_discrete_sequence=[COLORS["primary"]])
        fig.update_layout(**base_layout(300,"팀별 평균 AHT (초)"))
        st.plotly_chart(fig, use_container_width=True)

    if "근속그룹" in resp.columns:
        st.markdown('<div class="section-title">근속그룹별 AHT</div>', unsafe_allow_html=True)
        tg = resp.groupby("근속그룹").agg(응대수=("근속그룹","count"), 평균AHT=("AHT(초)","mean")).round(1).reset_index()
        fig2 = px.bar(tg, x="근속그룹", y="평균AHT", color_discrete_sequence=[COLORS["info"]])
        fig2.update_layout(**base_layout(300,"근속그룹별 평균 AHT (초)"))
        st.plotly_chart(fig2, use_container_width=True)

# ─────────────────────────────────────────────
# 채팅 현황
# ─────────────────────────────────────────────
def page_chat(chat, unit, month_range, start, end):
    if chat.empty:
        st.info("채팅 데이터가 없습니다.")
        return

    resp = chat[chat["응대여부"]=="응대"]
    total    = len(chat)
    resp_cnt = len(resp)
    rr       = resp_cnt/total*100 if total else 0
    avg_resp = resp["응답시간(초)"].mean() if not resp.empty else 0
    avg_lead = resp["리드타임(초)"].mean() if not resp.empty else 0

    cols = st.columns(5)
    for col, label, val, u in [
        (cols[0],"전체 인입",f"{total:,}","건"),
        (cols[1],"응대",f"{resp_cnt:,}","건"),
        (cols[2],"응대율",fmt_pct(rr),""),
        (cols[3],"평균 응답시간",fmt_sec(avg_resp),""),
        (cols[4],"평균 리드타임",fmt_sec(avg_lead),""),
    ]:
        with col:
            st.markdown(kpi_card(label, val, unit=u), unsafe_allow_html=True)

    pc = get_period_col(unit)
    cr_s, _ = get_chart_range(unit, end, month_range)
    ch_in = chat[chat[pc]>=pd.Timestamp(cr_s)].groupby(pc).size().reset_index(name="건수")
    ch_re = resp[resp[pc]>=pd.Timestamp(cr_s)].groupby(pc).size().reset_index(name="건수")

    st.markdown('<div class="section-title">인입 / 응대 추이</div>', unsafe_allow_html=True)
    col_t, col_d = st.columns([2,1])
    with col_t:
        fig = trend_chart({"채팅 인입":ch_in,"응대":ch_re},
                          unit=unit, y_label="건수", title="채팅 인입 / 응대 추이")
        st.plotly_chart(fig, use_container_width=True)
    with col_d:
        fig2 = donut_chart(["응대","미응대"],[resp_cnt, total-resp_cnt],
                           [COLORS["success"],COLORS["danger"]], title="응대 현황")
        st.plotly_chart(fig2, use_container_width=True)

    if "대분류" in chat.columns and not resp.empty:
        st.markdown('<div class="section-title">대분류별 평균 리드타임</div>', unsafe_allow_html=True)
        cat_df = resp.groupby("대분류").agg(
            건수=("대분류","count"),
            평균리드타임=("리드타임(초)","mean"),
        ).round(1).reset_index().sort_values("건수",ascending=False)
        fig3 = px.bar(cat_df, x="대분류", y="평균리드타임",
                      color_discrete_sequence=[COLORS["chat"]])
        fig3.update_layout(**base_layout(300,"대분류별 평균 리드타임 (초)"))
        st.plotly_chart(fig3, use_container_width=True)

    st.markdown('<div class="section-title">시간대별 인입 현황</div>', unsafe_allow_html=True)
    hourly = chat.groupby("인입시간대").agg(
        인입=("인입시간대","count"),
        응대=("응대여부", lambda x: (x=="응대").sum()),
    ).reset_index()
    fig4 = go.Figure()
    fig4.add_trace(go.Bar(x=hourly["인입시간대"], y=hourly["인입"],
                          name="인입", marker_color=hex_rgba(COLORS["chat"],0.5)))
    fig4.add_trace(go.Bar(x=hourly["인입시간대"], y=hourly["응대"],
                          name="응대", marker_color=COLORS["chat"]))
    fig4.update_layout(**base_layout(300,"시간대별 인입 / 응대"))
    st.plotly_chart(fig4, use_container_width=True)

    if "플랫폼" in chat.columns:
        st.markdown('<div class="section-title">플랫폼별 분포</div>', unsafe_allow_html=True)
        plat = chat.groupby("플랫폼").size().reset_index(name="건수")
        fig5 = donut_chart(plat["플랫폼"].tolist(), plat["건수"].tolist(), title="플랫폼 분포")
        st.plotly_chart(fig5, use_container_width=True)

# ─────────────────────────────────────────────
# 채팅 상담사
# ─────────────────────────────────────────────
def page_chat_agent(chat, unit, month_range):
    if chat.empty:
        st.info("채팅 데이터가 없습니다.")
        return
    resp = chat[chat["응대여부"]=="응대"]
    if resp.empty:
        st.info("응대 데이터가 없습니다.")
        return

    st.markdown('<div class="section-title">상담사별 채팅 성과</div>', unsafe_allow_html=True)
    ag = resp.groupby("상담사명").agg(
        응대수=("상담사명","count"),
        평균응답시간=("응답시간(초)","mean"),
        평균리드타임=("리드타임(초)","mean"),
    ).round(1).reset_index().sort_values("응대수",ascending=False)
    st.dataframe(ag, use_container_width=True, height=400)

    if "팀명" in resp.columns:
        st.markdown('<div class="section-title">팀별 평균 리드타임</div>', unsafe_allow_html=True)
        tm = resp.groupby("팀명").agg(응대수=("팀명","count"), 평균리드타임=("리드타임(초)","mean")).round(1).reset_index()
        fig = px.bar(tm, x="팀명", y="평균리드타임", color_discrete_sequence=[COLORS["chat"]])
        fig.update_layout(**base_layout(300,"팀별 평균 리드타임 (초)"))
        st.plotly_chart(fig, use_container_width=True)

    if "근속그룹" in resp.columns:
        st.markdown('<div class="section-title">근속그룹별 리드타임</div>', unsafe_allow_html=True)
        tg = resp.groupby("근속그룹").agg(응대수=("근속그룹","count"), 평균리드타임=("리드타임(초)","mean")).round(1).reset_index()
        fig2 = px.bar(tg, x="근속그룹", y="평균리드타임", color_discrete_sequence=[COLORS["info"]])
        fig2.update_layout(**base_layout(300,"근속그룹별 평균 리드타임 (초)"))
        st.plotly_chart(fig2, use_container_width=True)

# ─────────────────────────────────────────────
# 게시판 현황
# ─────────────────────────────────────────────
def page_board(board, unit, month_range, start, end):
    if board.empty:
        st.info("게시판 데이터가 없습니다.")
        return

    resp = board[board["응대여부"]=="응대"]
    total    = len(board)
    resp_cnt = len(resp)
    rr       = resp_cnt/total*100 if total else 0
    avg_lead = resp["리드타임(초)"].mean() if not resp.empty else 0

    cols = st.columns(4)
    for col, label, val, u in [
        (cols[0],"전체 티켓",f"{total:,}","건"),
        (cols[1],"응답완료",f"{resp_cnt:,}","건"),
        (cols[2],"응답률",fmt_pct(rr),""),
        (cols[3],"평균 리드타임",fmt_sec(avg_lead),""),
    ]:
        with col:
            st.markdown(kpi_card(label, val, unit=u), unsafe_allow_html=True)

    pc = get_period_col(unit)
    cr_s, _ = get_chart_range(unit, end, month_range)
    bo_in = board[board[pc]>=pd.Timestamp(cr_s)].groupby(pc).size().reset_index(name="건수")
    bo_re = resp[resp[pc]>=pd.Timestamp(cr_s)].groupby(pc).size().reset_index(name="건수")

    st.markdown('<div class="section-title">티켓 접수 / 응답 추이</div>', unsafe_allow_html=True)
    col_t, col_d = st.columns([2,1])
    with col_t:
        fig = trend_chart({"접수":bo_in,"응답":bo_re},
                          unit=unit, y_label="건수", title="게시판 접수 / 응답 추이")
        st.plotly_chart(fig, use_container_width=True)
    with col_d:
        fig2 = donut_chart(["응답","미응답"],[resp_cnt, total-resp_cnt],
                           [COLORS["success"],COLORS["danger"]], title="응답 현황")
        st.plotly_chart(fig2, use_container_width=True)

    if "대분류" in board.columns:
        st.markdown('<div class="section-title">대분류별 티켓 분석</div>', unsafe_allow_html=True)
        cat_df = board.groupby("대분류").agg(
            건수=("대분류","count"),
            응답수=("응대여부", lambda x: (x=="응대").sum()),
        ).reset_index()
        cat_df["응답률"] = (cat_df["응답수"]/cat_df["건수"]*100).round(1)
        fig3 = px.bar(cat_df, x="대분류", y="건수", color_discrete_sequence=[COLORS["board"]])
        fig3.update_layout(**base_layout(300,"대분류별 티켓 건수"))
        st.plotly_chart(fig3, use_container_width=True)

    if "플랫폼" in board.columns:
        st.markdown('<div class="section-title">플랫폼별 분포</div>', unsafe_allow_html=True)
        plat = board.groupby("플랫폼").size().reset_index(name="건수")
        fig4 = donut_chart(plat["플랫폼"].tolist(), plat["건수"].tolist(), title="플랫폼 분포")
        st.plotly_chart(fig4, use_container_width=True)

    st.markdown('<div class="section-title">시간대별 접수 현황</div>', unsafe_allow_html=True)
    hourly = board.groupby("인입시간대").agg(
        접수=("인입시간대","count"),
        응답=("응대여부", lambda x: (x=="응대").sum()),
    ).reset_index()
    fig5 = go.Figure()
    fig5.add_trace(go.Bar(x=hourly["인입시간대"], y=hourly["접수"],
                          name="접수", marker_color=hex_rgba(COLORS["board"],0.5)))
    fig5.add_trace(go.Bar(x=hourly["인입시간대"], y=hourly["응답"],
                          name="응답", marker_color=COLORS["board"]))
    fig5.update_layout(**base_layout(300,"시간대별 접수 / 응답"))
    st.plotly_chart(fig5, use_container_width=True)

# ─────────────────────────────────────────────
# 게시판 상담사
# ─────────────────────────────────────────────
def page_board_agent(board, unit, month_range):
    if board.empty:
        st.info("게시판 데이터가 없습니다.")
        return
    resp = board[board["응대여부"]=="응대"]
    if resp.empty:
        st.info("응답 데이터가 없습니다.")
        return

    st.markdown('<div class="section-title">상담사별 게시판 성과</div>', unsafe_allow_html=True)
    ag = resp.groupby("상담사명").agg(
        응답수=("상담사명","count"),
        평균리드타임=("리드타임(초)","mean"),
    ).round(1).reset_index().sort_values("응답수",ascending=False)
    st.dataframe(ag, use_container_width=True, height=400)

    if "팀명" in resp.columns:
        st.markdown('<div class="section-title">팀별 평균 리드타임</div>', unsafe_allow_html=True)
        tm = resp.groupby("팀명").agg(응답수=("팀명","count"), 평균리드타임=("리드타임(초)","mean")).round(1).reset_index()
        fig = px.bar(tm, x="팀명", y="평균리드타임", color_discrete_sequence=[COLORS["board"]])
        fig.update_layout(**base_layout(300,"팀별 평균 리드타임 (초)"))
        st.plotly_chart(fig, use_container_width=True)

    if "근속그룹" in resp.columns:
        st.markdown('<div class="section-title">근속그룹별 리드타임</div>', unsafe_allow_html=True)
        tg = resp.groupby("근속그룹").agg(응답수=("근속그룹","count"), 평균리드타임=("리드타임(초)","mean")).round(1).reset_index()
        fig2 = px.bar(tg, x="근속그룹", y="평균리드타임", color_discrete_sequence=[COLORS["info"]])
        fig2.update_layout(**base_layout(300,"근속그룹별 평균 리드타임 (초)"))
        st.plotly_chart(fig2, use_container_width=True)

# ─────────────────────────────────────────────
# 상담사 종합
# ─────────────────────────────────────────────
def page_agent_total(phone, chat, board):
    st.markdown('<div class="section-title">상담사 종합 성과</div>', unsafe_allow_html=True)

    names = set()
    if not phone.empty: names.update(phone["상담사명"].unique())
    if not chat.empty:  names.update(chat["상담사명"].unique())
    if not board.empty: names.update(board["상담사명"].unique())
    names.discard("미응대")

    rows = []
    for name in names:
        ph = phone[(phone["상담사명"]==name)&(phone["응대여부"]=="응대")] if not phone.empty else pd.DataFrame()
        ch = chat[(chat["상담사명"]==name)&(chat["응대여부"]=="응대")]    if not chat.empty  else pd.DataFrame()
        bo = board[(board["상담사명"]==name)&(board["응대여부"]=="응대")] if not board.empty else pd.DataFrame()
        rows.append({
            "상담사명":       name,
            "전화응대":       len(ph),
            "채팅응대":       len(ch),
            "게시판응답":     len(bo),
            "전화AHT평균":    round(ph["AHT(초)"].mean(),1) if not ph.empty else 0,
            "채팅리드타임평균": round(ch["리드타임(초)"].mean(),1) if not ch.empty else 0,
            "게시판리드타임평균": round(bo["리드타임(초)"].mean(),1) if not bo.empty else 0,
        })

    if not rows:
        st.info("데이터가 없습니다.")
        return

    df_ag = pd.DataFrame(rows).sort_values("전화응대", ascending=False)
    st.dataframe(df_ag, use_container_width=True, height=500)

    st.markdown('<div class="section-title">상담사별 채널 분포 (상위 10)</div>', unsafe_allow_html=True)
    top10 = df_ag.head(10)
    fig = go.Figure()
    fig.add_trace(go.Bar(name="전화",   x=top10["상담사명"], y=top10["전화응대"],   marker_color=COLORS["phone"]))
    fig.add_trace(go.Bar(name="채팅",   x=top10["상담사명"], y=top10["채팅응대"],   marker_color=COLORS["chat"]))
    fig.add_trace(go.Bar(name="게시판", x=top10["상담사명"], y=top10["게시판응답"], marker_color=COLORS["board"]))
    fig.update_layout(barmode="stack", **base_layout(360,"상담사별 채널 분포"))
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# 사이드바
# ─────────────────────────────────────────────
def render_sidebar(phone_raw, chat_raw, board_raw):
    with st.sidebar:
        st.markdown("""
        <div style="padding:20px 16px 12px;border-bottom:1px solid #334155;margin-bottom:16px;">
            <div style="font-size:16px;font-weight:800;color:#f1f5f9;letter-spacing:-0.5px;">CC OPS</div>
            <div style="font-size:11px;color:#64748b;margin-top:2px;">Contact Center Analytics</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔄 데이터 새로고침"):
            st.cache_data.clear()
            st.rerun()

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        unit = st.radio("기간 단위", ["일별","주별","월별"], horizontal=True)
        month_range = 3
        if unit == "월별":
            month_range = st.slider("추이 범위(개월)", 1, 6, 3)

        today = date.today()
        st.markdown('<div style="margin-top:10px;font-size:11px;color:#94a3b8;font-weight:600;">날짜 범위</div>', unsafe_allow_html=True)
        c1,c2 = st.columns(2)
        with c1:
            if st.button("7일"):
                st.session_state["ds"] = today - timedelta(days=6)
                st.session_state["de"] = today
        with c2:
            if st.button("30일"):
                st.session_state["ds"] = today - timedelta(days=29)
                st.session_state["de"] = today
        c3,c4 = st.columns(2)
        with c3:
            if st.button("이번달"):
                st.session_state["ds"] = today.replace(day=1)
                st.session_state["de"] = today
        with c4:
            if st.button("전체"):
                st.session_state["ds"] = date(2024,1,1)
                st.session_state["de"] = today

        date_start = st.date_input("시작일", value=st.session_state.get("ds", today-timedelta(days=29)))
        date_end   = st.date_input("종료일", value=st.session_state.get("de", today))

        # 사업자 필터
        all_ops = sorted(set(
            list(phone_raw["사업자명"].dropna().unique() if "사업자명" in phone_raw.columns else []) +
            list(chat_raw["사업자명"].dropna().unique()  if "사업자명" in chat_raw.columns  else []) +
            list(board_raw["사업자명"].dropna().unique() if "사업자명" in board_raw.columns else [])
        ))
        st.markdown('<div style="margin-top:10px;font-size:11px;color:#94a3b8;font-weight:600;">사업자</div>', unsafe_allow_html=True)
        sel_ops = st.multiselect("사업자", all_ops, default=[], label_visibility="collapsed")

        # 브랜드 필터
        all_brands = sorted(set(
            list(phone_raw["브랜드"].dropna().unique() if "브랜드" in phone_raw.columns else []) +
            list(chat_raw["브랜드"].dropna().unique()  if "브랜드" in chat_raw.columns  else []) +
            list(board_raw["브랜드"].dropna().unique() if "브랜드" in board_raw.columns else [])
        ))
        st.markdown('<div style="margin-top:10px;font-size:11px;color:#94a3b8;font-weight:600;">브랜드</div>', unsafe_allow_html=True)
        sel_brands = st.multiselect("브랜드", all_brands, default=[], label_visibility="collapsed")

        # 메뉴
        st.markdown('<div style="height:12px;border-top:1px solid #334155;margin-top:14px;padding-top:14px;font-size:11px;color:#94a3b8;font-weight:600;">메뉴</div>', unsafe_allow_html=True)
        menu = st.session_state.get("menu","전체 현황")
        for group, items in MENU_GROUPS.items():
            for item in items:
                sel = "▶ " if menu == item else "　"
                if st.button(f"{sel}{item}", key=f"m_{item}"):
                    st.session_state["menu"] = item
                    st.rerun()

    return unit, month_range, date_start, date_end, sel_ops, sel_brands

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    agent_raw = load_agent()
    phone_raw = load_phone()
    chat_raw  = load_chat()
    board_raw = load_board()

    unit, month_range, date_start, date_end, sel_ops, sel_brands = render_sidebar(phone_raw, chat_raw, board_raw)

    base_d = date.today()  # date 객체로 고정
    phone_m = merge_agent(phone_raw, agent_raw, base_d)
    chat_m  = merge_agent(chat_raw,  agent_raw, base_d)
    board_m = merge_agent(board_raw, agent_raw, base_d)

    phone_f = filter_df(phone_m, date_start, date_end, sel_brands or None, sel_ops or None)
    chat_f  = filter_df(chat_m,  date_start, date_end, sel_brands or None, sel_ops or None)
    board_f = filter_df(board_m, date_start, date_end, sel_brands or None, sel_ops or None)

    if all(len(df)==0 for df in [phone_f, chat_f, board_f]):
        st.markdown("""
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                    height:60vh;text-align:center;gap:12px;">
            <div style="font-size:40px;">📊</div>
            <div style="font-size:20px;font-weight:800;color:#0f172a;">데이터 연결 필요</div>
            <div style="font-size:13px;color:#64748b;">Google Sheets에 데이터를 입력하거나 필터 조건을 확인해주세요.</div>
            <div style="font-size:11px;color:#94a3b8;background:#f1f5f9;padding:8px 16px;border-radius:8px;">
                SHEET_ID 및 GID_MAP 설정을 확인하세요
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    menu = st.session_state.get("menu","전체 현황")

    if   menu == "전체 현황":     page_overview(phone_f, chat_f, board_f, unit, month_range, date_start, date_end)
    elif menu == "사업자 현황":   page_operator(phone_f, chat_f, board_f, unit, month_range)
    elif menu == "전화 현황":     page_phone(phone_f, unit, month_range, date_start, date_end)
    elif menu == "전화 상담사":   page_phone_agent(phone_f, unit, month_range)
    elif menu == "채팅 현황":     page_chat(chat_f, unit, month_range, date_start, date_end)
    elif menu == "채팅 상담사":   page_chat_agent(chat_f, unit, month_range)
    elif menu == "게시판 현황":   page_board(board_f, unit, month_range, date_start, date_end)
    elif menu == "게시판 상담사": page_board_agent(board_f, unit, month_range)
    elif menu == "상담사 종합":   page_agent_total(phone_f, chat_f, board_f)

if __name__ == "__main__":
    main()
