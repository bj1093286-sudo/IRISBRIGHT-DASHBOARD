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

# ─────────────────────────────────────────────
# 상수
# ─────────────────────────────────────────────
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
    "전체 현황":     ["전체 현황"],
    "사업자":        ["사업자 현황"],
    "전화":          ["전화 현황", "전화 상담사"],
    "채팅":          ["채팅 현황", "채팅 상담사"],
    "게시판":        ["게시판 현황", "게시판 상담사"],
    "상담사":        ["상담사 종합"],
}

# ─────────────────────────────────────────────
# 페이지 설정
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Contact Center OPS",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CSS — SaaS 디자인
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: #F5F6F8 !important;
    color: #0f172a;
}

/* 사이드바 */
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

/* 메인 배경 */
.main .block-container {
    padding: 24px 32px !important;
    max-width: 100% !important;
    background: #F5F6F8 !important;
}

/* 헤더 */
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
.dash-header-left span {
    font-size: 12px;
    color: #94a3b8;
    font-weight: 400;
}
.dash-header-right {
    display: flex;
    align-items: center;
    gap: 10px;
}

/* 카드 */
.card {
    background: #fff;
    border-radius: 20px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    padding: 24px;
    margin-bottom: 20px;
}
.card-title {
    font-size: 14px;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 16px;
    letter-spacing: -0.2px;
}

/* KPI 카드 */
.kpi-grid {
    display: grid;
    gap: 16px;
}
.kpi-card {
    background: #fff;
    border-radius: 20px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    padding: 22px 24px;
}
.kpi-label {
    font-size: 12px;
    font-weight: 600;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 10px;
}
.kpi-value {
    font-size: 28px;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -1px;
    line-height: 1;
    margin-bottom: 8px;
}
.kpi-delta-row {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    align-items: center;
}
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
.kpi-delta.up.rev   { background: #f0fdf4; color: #22c55e; }
.kpi-delta.down.rev { background: #fef2f2; color: #ef4444; }

/* 섹션 타이틀 */
.section-title {
    font-size: 16px;
    font-weight: 700;
    color: #0f172a;
    margin: 28px 0 14px;
    letter-spacing: -0.3px;
}

/* Streamlit 기본 요소 정리 */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }
div[data-testid="stToolbar"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 유틸 함수
# ─────────────────────────────────────────────
def hex_rgba(hex_color: str, alpha: float = 0.08) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

def get_tenure_group(hire_date, base_date):
    if pd.isna(hire_date):
        return "미입력"
    days = (base_date - hire_date).days
    for threshold, label in TENURE_GROUPS:
        if days <= threshold:
            return label
    return "기존5 (4년초과)"

def is_holiday(d):
    kr = holidays.KR(years=d.year)
    return d in kr

def is_workday(d):
    return d.weekday() < 5 and not is_holiday(d)

def split_leadtime(접수, 응답):
    if pd.isna(접수) or pd.isna(응답):
        return 0, 0
    total_minutes = (응답 - 접수).total_seconds() / 60
    work_min = 0
    cur = 접수
    while cur < 응답:
        nxt = min(cur + timedelta(minutes=1), 응답)
        if is_workday(cur.date()) and WORK_START <= cur.hour < WORK_END:
            work_min += (nxt - cur).total_seconds() / 60
        cur = nxt
    return round(work_min, 1), round(total_minutes - work_min, 1)

def gsheet_url(gid: str) -> str:
    return (
        f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
        f"/export?format=csv&gid={gid}"
    )

# ─────────────────────────────────────────────
# 기간 유틸
# ─────────────────────────────────────────────
def get_period_col(unit):
    return {"일별": "일자", "주별": "주차", "월별": "월"}[unit]

def assign_period_cols(df, date_col="일자"):
    if date_col not in df.columns:
        return df
    df = df.copy()
    df["일자"] = pd.to_datetime(df[date_col], errors="coerce")
    df["주차"] = df["일자"].dt.to_period("W").dt.start_time
    df["월"]   = df["일자"].dt.to_period("M").dt.start_time
    return df

def get_prev_period(unit, start, end):
    delta = end - start + timedelta(days=1)
    return start - delta, end - delta

def get_chart_range(unit, end_date, month_range=3):
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
        df["인입시각"] = pd.to_datetime(df["일자"].astype(str) + " " + df["인입시각"].astype(str), errors="coerce")
        df["통화시간(초)"] = pd.to_numeric(df.get("통화시간(초)", 0), errors="coerce").fillna(0)
        df["ACW시간(초)"]  = pd.to_numeric(df.get("ACW시간(초)", 0), errors="coerce").fillna(0)
        df["대기시간(초)"] = pd.to_numeric(df.get("대기시간(초)", 0), errors="coerce").fillna(0)
        df["AHT(초)"]      = df["통화시간(초)"] + df["ACW시간(초)"]
        df["응대여부"]     = df["상담사명"].apply(lambda x: "미응대" if str(x).strip() == "미응대" else "응대")
        df["인입시간대"]   = df["인입시각"].dt.hour
        df = assign_period_cols(df, "일자")
        return df
    except Exception as e:
        return pd.DataFrame(columns=["일자","사업자명","브랜드","상담사명","인입시각","대기시간(초)","통화시간(초)","ACW시간(초)","대분류","중분류","소분류","AHT(초)","응대여부","인입시간대","주차","월"])

@st.cache_data(ttl=300, show_spinner=False)
def load_chat():
    try:
        df = pd.read_csv(gsheet_url(GID_MAP["chat"]))
        df.columns = df.columns.str.strip()
        df["일자"] = pd.to_datetime(df["일자"], errors="coerce")
        df["접수일시"] = pd.to_datetime(df["접수일시"], errors="coerce")
        df["첫멘트발송일시"] = pd.to_datetime(df["첫멘트발송일시"], errors="coerce")
        df["종료일시"] = pd.to_datetime(df["종료일시"], errors="coerce")
        df["응답시간(초)"] = (df["첫멘트발송일시"] - df["접수일시"]).dt.total_seconds().clip(lower=0)
        df["리드타임(초)"] = (df["종료일시"] - df["접수일시"]).dt.total_seconds().clip(lower=0)
        포기여부 = df.get("배분전포기여부", pd.Series(["N"] * len(df)))
        df["응대여부"] = df.apply(
            lambda r: "미응대" if pd.isna(r["첫멘트발송일시"]) or str(포기여부.iloc[r.name]).strip().upper() == "Y"
            else "응대", axis=1
        )
        df["인입시간대"] = df["접수일시"].dt.hour
        df = assign_period_cols(df, "일자")
        return df
    except:
        return pd.DataFrame(columns=["일자","사업자명","브랜드","플랫폼","상담사명","접수일시","첫멘트발송일시","종료일시","배분전포기여부","대분류","중분류","소분류","응답시간(초)","리드타임(초)","응대여부","인입시간대","주차","월"])

@st.cache_data(ttl=300, show_spinner=False)
def load_board():
    try:
        df = pd.read_csv(gsheet_url(GID_MAP["board"]))
        df.columns = df.columns.str.strip()
        df["일자"] = pd.to_datetime(df["일자"], errors="coerce")
        df["접수일시"] = pd.to_datetime(df["접수일시"], errors="coerce")
        df["응답일시"] = pd.to_datetime(df["응답일시"], errors="coerce")
        df["리드타임(초)"] = (df["응답일시"] - df["접수일시"]).dt.total_seconds().clip(lower=0)
        df["응대여부"] = df["응답일시"].apply(lambda x: "미응대" if pd.isna(x) else "응대")
        df["인입시간대"] = df["접수일시"].dt.hour
        df = assign_period_cols(df, "일자")
        return df
    except:
        return pd.DataFrame(columns=["일자","사업자명","브랜드","플랫폼","상담사명","접수일시","응답일시","대분류","중분류","소분류","리드타임(초)","응대여부","인입시간대","주차","월"])

def merge_agent(df, agent_df, base_date):
    if agent_df.empty or "상담사명" not in df.columns:
        df["팀명"] = "미지정"
        df["근속그룹"] = "미입력"
        return df
    merged = df.merge(agent_df[["상담사명", "팀명", "입사일"]], on="상담사명", how="left")
    merged["팀명"] = merged["팀명"].fillna("미지정")
    merged["근속그룹"] = merged["입사일"].apply(
        lambda x: get_tenure_group(x, base_date)
    )
    return merged

# ─────────────────────────────────────────────
# 필터
# ─────────────────────────────────────────────
def filter_df(df, start, end, brands=None, operators=None):
    if df.empty:
        return df
    date_col = "일자"
    if date_col not in df.columns:
        return df
    mask = (df[date_col] >= pd.Timestamp(start)) & (df[date_col] <= pd.Timestamp(end))
    df = df[mask].copy()
    if brands and "브랜드" in df.columns:
        df = df[df["브랜드"].isin(brands)]
    if operators and "사업자명" in df.columns:
        df = df[df["사업자명"].isin(operators)]
    return df

# ─────────────────────────────────────────────
# KPI 렌더
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
        delta_html += f'<span style="font-size:10px;color:#94a3b8;margin-left:4px;">YoY</span>' + badge(delta_yoy, reverse)

    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}<span style="font-size:14px;color:#94a3b8;margin-left:4px;">{unit}</span></div>
        <div class="kpi-delta-row">{delta_html}</div>
    </div>
    """

def calc_delta(curr, prev):
    if prev is None or prev == 0:
        return None
    return round((curr - prev) / prev * 100, 1)

# ─────────────────────────────────────────────
# 차트 공통 설정
# ─────────────────────────────────────────────
def base_layout(h=320, title=""):
    return dict(
        height=h,
        title=dict(text=title, font=dict(size=13, color="#0f172a", family="Inter"), x=0),
        margin=dict(l=8, r=8, t=36 if title else 12, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", size=11, color="#64748b"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    font=dict(size=11)),
        xaxis=dict(showgrid=False, zeroline=False, tickfont=dict(size=10)),
        yaxis=dict(showgrid=True, gridcolor="#f1f5f9", zeroline=False, tickfont=dict(size=10)),
    )

def trend_chart(series_dict, unit, y_label="건수", h=320, month_range=3, title=""):
    """series_dict = {"라벨": df_with_period_and_y_label_col}"""
    pc = get_period_col(unit)
    fig = go.Figure()
    palette = [COLORS["primary"], COLORS["success"], COLORS["warning"], COLORS["info"], COLORS["danger"]]
    for i, (name, s) in enumerate(series_dict.items()):
        if s.empty or pc not in s.columns or y_label not in s.columns:
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
    layout = base_layout(h, title)
    fig.update_layout(**layout)
    return fig

def donut_chart(labels, values, colors=None, h=260, title=""):
    if colors is None:
        colors = [COLORS["primary"], COLORS["success"], COLORS["warning"], COLORS["info"], COLORS["danger"]]
    total = sum(values) if values else 0
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
        legend=dict(
            orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02,
            font=dict(size=11),
        ),
    )
    return fig

def bar_chart(df, x, y, color=None, h=300, title="", orientation="v"):
    fig = px.bar(df, x=x, y=y, color=color, barmode="group",
                 color_discrete_sequence=[COLORS["primary"], COLORS["success"], COLORS["warning"]],
                 orientation=orientation)
    fig.update_traces(marker_line_width=0)
    fig.update_layout(**base_layout(h, title))
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
# 공통 섹션 렌더 헬퍼
# ─────────────────────────────────────────────
def render_card(title, content_fn):
    st.markdown(f'<div class="card"><div class="card-title">{title}</div>', unsafe_allow_html=True)
    content_fn()
    st.markdown('</div>', unsafe_allow_html=True)

def fmt_sec(sec):
    sec = int(sec)
    if sec < 60:
        return f"{sec}s"
    elif sec < 3600:
        return f"{sec//60}m {sec%60:02d}s"
    else:
        return f"{sec//3600}h {(sec%3600)//60:02d}m"

def fmt_pct(val):
    return f"{val:.1f}%"

# ─────────────────────────────────────────────
# 전체 현황 페이지
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
            <span style="font-size:12px;color:#64748b;background:#f1f5f9;padding:6px 14px;border-radius:20px;font-weight:600;">
                {start.strftime("%Y.%m.%d")} ~ {end.strftime("%Y.%m.%d")}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    total_phone  = len(phone)
    total_chat   = len(chat)
    total_board  = len(board)
    total_all    = total_phone + total_chat + total_board

    resp_phone = len(phone[phone["응대여부"] == "응대"]) if not phone.empty else 0
    resp_chat  = len(chat[chat["응대여부"] == "응대"]) if not chat.empty else 0
    resp_board = len(board[board["응대여부"] == "응대"]) if not board.empty else 0

    rr_phone = resp_phone / total_phone * 100 if total_phone else 0
    rr_chat  = resp_chat  / total_chat  * 100 if total_chat  else 0
    rr_board = resp_board / total_board * 100 if total_board else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi_card("전체 인입", f"{total_all:,}", unit="건"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card("전화 인입", f"{total_phone:,}", unit="건"), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card("채팅 인입", f"{total_chat:,}", unit="건"), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_card("게시판 인입", f"{total_board:,}", unit="건"), unsafe_allow_html=True)

    st.markdown('<div class="section-title">채널별 응대율</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(kpi_card("전화 응대율", fmt_pct(rr_phone)), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card("채팅 응대율", fmt_pct(rr_chat)), unsafe_allow_html=True)
    with c3:
        st.markdown(kpi_card("게시판 응대율", fmt_pct(rr_board)), unsafe_allow_html=True)

    # 채널 분포 도넛
    st.markdown('<div class="section-title">채널별 인입 분포</div>', unsafe_allow_html=True)
    col_d, col_t = st.columns([1, 2])
    with col_d:
        fig = donut_chart(
            ["전화", "채팅", "게시판"],
            [total_phone, total_chat, total_board],
            [COLORS["phone"], COLORS["chat"], COLORS["board"]],
            title="채널 분포"
        )
        st.plotly_chart(fig, use_container_width=True)

    # 추이 차트
    with col_t:
        pc = get_period_col(unit)
        cr_s, cr_e = get_chart_range(unit, end, month_range)

        def agg_series(df, col="일자"):
            if df.empty or pc not in df.columns:
                return pd.DataFrame(columns=[pc, "건수"])
            s = df[df[pc] >= pd.Timestamp(cr_s)].groupby(pc).size().reset_index(name="건수")
            return s

        ph_s = agg_series(phone)
        ch_s = agg_series(chat)
        bo_s = agg_series(board)

        fig2 = trend_chart({"전화": ph_s, "채팅": ch_s, "게시판": bo_s},
                           unit=unit, y_label="건수", title="채널별 인입 추이")
        st.plotly_chart(fig2, use_container_width=True)

# ─────────────────────────────────────────────
# 사업자 현황 페이지
# ─────────────────────────────────────────────
def page_operator(phone, chat, board, unit, month_range):
    st.markdown('<div class="section-title">사업자별 인입 현황</div>', unsafe_allow_html=True)

    def op_summary(df, ch_name):
        if df.empty or "사업자명" not in df.columns:
            return pd.DataFrame()
        g = df.groupby("사업자명").agg(
            인입=("사업자명", "count"),
            응대=("응대여부", lambda x: (x == "응대").sum()),
        ).reset_index()
        g["응대율"] = (g["응대"] / g["인입"] * 100).round(1)
        g["채널"] = ch_name
        return g

    ph_op = op_summary(phone, "전화")
    ch_op = op_summary(chat, "채팅")
    bo_op = op_summary(board, "게시판")
    all_op = pd.concat([ph_op, ch_op, bo_op])

    if all_op.empty:
        st.info("사업자명 데이터가 없습니다.")
        return

    fig = px.bar(all_op, x="사업자명", y="인입", color="채널", barmode="stack",
                 color_discrete_map={"전화": COLORS["phone"], "채팅": COLORS["chat"], "게시판": COLORS["board"]})
    fig.update_layout(**base_layout(360, "사업자별 채널 인입"))
    st.plotly_chart(fig, use_container_width=True)

    # 사업자별 응대율 테이블
    pivot = all_op.pivot_table(index="사업자명", columns="채널", values=["인입", "응대율"], aggfunc="first")
    st.dataframe(pivot, use_container_width=True)

# ─────────────────────────────────────────────
# 전화 현황 페이지
# ─────────────────────────────────────────────
def page_phone(phone, unit, month_range, start, end):
    if phone.empty:
        st.info("전화 데이터가 없습니다.")
        return

    responded = phone[phone["응대여부"] == "응대"]
    total     = len(phone)
    resp_cnt  = len(responded)
    rr        = resp_cnt / total * 100 if total else 0
    avg_wait  = responded["대기시간(초)"].mean() if not responded.empty else 0
    avg_talk  = responded["통화시간(초)"].mean() if not responded.empty else 0
    avg_acw   = responded["ACW시간(초)"].mean()  if not responded.empty else 0
    avg_aht   = responded["AHT(초)"].mean()      if not responded.empty else 0

    # KPI 행
    cols = st.columns(6)
    kpis = [
        ("전체 인입", f"{total:,}", "건"),
        ("응대", f"{resp_cnt:,}", "건"),
        ("응대율", fmt_pct(rr), ""),
        ("평균 대기시간", fmt_sec(avg_wait), ""),
        ("평균 통화시간", fmt_sec(avg_talk), ""),
        ("평균 AHT", fmt_sec(avg_aht), ""),
    ]
    for col, (label, val, u) in zip(cols, kpis):
        with col:
            st.markdown(kpi_card(label, val, unit=u), unsafe_allow_html=True)

    # 추이 + 도넛
    st.markdown('<div class="section-title">인입/응대 추이</div>', unsafe_allow_html=True)
    pc = get_period_col(unit)
    cr_s, cr_e = get_chart_range(unit, end, month_range)

    ph_in = phone[phone[pc] >= pd.Timestamp(cr_s)].groupby(pc).size().reset_index(name="건수")
    ph_re = responded[responded[pc] >= pd.Timestamp(cr_s)].groupby(pc).size().reset_index(name="건수")

    col_t, col_d = st.columns([2, 1])
    with col_t:
        fig = trend_chart({"전화 인입": ph_in, "응대": ph_re},
                          unit=unit, y_label="건수", h=320, month_range=month_range,
                          title="인입 / 응대 추이")
        st.plotly_chart(fig, use_container_width=True)
    with col_d:
        fig2 = donut_chart(["응대", "미응대"], [resp_cnt, total - resp_cnt],
                           [COLORS["success"], COLORS["danger"]], title="응대 현황")
        st.plotly_chart(fig2, use_container_width=True)

    # 시간대별 인입
    st.markdown('<div class="section-title">시간대별 인입 현황</div>', unsafe_allow_html=True)
    hourly = phone.groupby("인입시간대").agg(
        인입=("인입시간대", "count"),
        응대=("응대여부", lambda x: (x == "응대").sum()),
    ).reset_index()
    hourly["응대율"] = (hourly["응대"] / hourly["인입"] * 100).round(1)

    fig3 = go.Figure()
    fig3.add_trace(go.Bar(x=hourly["인입시간대"], y=hourly["인입"],
                          name="인입", marker_color=hex_rgba(COLORS["primary"], 0.7)))
    fig3.add_trace(go.Bar(x=hourly["인입시간대"], y=hourly["응대"],
                          name="응대", marker_color=COLORS["primary"]))
    fig3.update_layout(**base_layout(300, "시간대별 인입 / 응대"))
    st.plotly_chart(fig3, use_container_width=True)

    # AHT 구성
    st.markdown('<div class="section-title">AHT 구성 분석</div>', unsafe_allow_html=True)
    if not responded.empty:
        aht_df = responded.groupby(pc).agg(
            통화시간=("통화시간(초)", "mean"),
            ACW시간=("ACW시간(초)", "mean"),
        ).reset_index()
        fig4 = go.Figure()
        fig4.add_trace(go.Bar(x=aht_df[pc], y=aht_df["통화시간"],
                              name="통화시간", marker_color=COLORS["primary"]))
        fig4.add_trace(go.Bar(x=aht_df[pc], y=aht_df["ACW시간"],
                              name="ACW", marker_color=COLORS["warning"]))
        fig4.update_layout(barmode="stack", **base_layout(300, "기간별 평균 AHT 구성"))
        st.plotly_chart(fig4, use_container_width=True)

    # 대분류별 인입
    st.markdown('<div class="section-title">문의 유형 분석</div>', unsafe_allow_html=True)
    if "대분류" in phone.columns:
        cat_df = phone.groupby("대분류").size().reset_index(name="건수").sort_values("건수", ascending=False)
        fig5 = px.bar(cat_df, x="대분류", y="건수",
                      color_discrete_sequence=[COLORS["primary"]])
        fig5.update_layout(**base_layout(300, "대분류별 인입"))
        st.plotly_chart(fig5, use_container_width=True)

    # 히트맵
    st.markdown('<div class="section-title">인입 히트맵 (날짜 × 시간대)</div>', unsafe_allow_html=True)
    if "인입시간대" in phone.columns and "일자" in phone.columns:
        phone_copy = phone.copy()
        phone_copy["일자str"] = phone_copy["일자"].dt.strftime("%m-%d")
        pivot = phone_copy.pivot_table(index="일자str", columns="인입시간대",
                                       values="응대여부", aggfunc="count", fill_value=0)
        fig6 = heatmap_chart(pivot, title="날짜 × 시간대 인입 히트맵")
        st.plotly_chart(fig6, use_container_width=True)

# ─────────────────────────────────────────────
# 전화 상담사 페이지
# ─────────────────────────────────────────────
def page_phone_agent(phone, unit, month_range):
    if phone.empty:
        st.info("전화 데이터가 없습니다.")
        return

    st.markdown('<div class="section-title">상담사별 전화 성과</div>', unsafe_allow_html=True)
    responded = phone[phone["응대여부"] == "응대"]
    if responded.empty:
        st.info("응대 데이터가 없습니다.")
        return

    agent_df = responded.groupby("상담사명").agg(
        응대수=("상담사명", "count"),
        평균대기=("대기시간(초)", "mean"),
        평균통화=("통화시간(초)", "mean"),
        평균ACW=("ACW시간(초)", "mean"),
        평균AHT=("AHT(초)", "mean"),
    ).round(1).reset_index().sort_values("응대수", ascending=False)

    st.dataframe(agent_df, use_container_width=True, height=400)

    # 팀별 평균
    if "팀명" in responded.columns:
        st.markdown('<div class="section-title">팀별 평균 AHT</div>', unsafe_allow_html=True)
        team_df = responded.groupby("팀명").agg(
            응대수=("팀명", "count"),
            평균AHT=("AHT(초)", "mean"),
        ).round(1).reset_index()
        fig = px.bar(team_df, x="팀명", y="평균AHT",
                     color_discrete_sequence=[COLORS["primary"]])
        fig.update_layout(**base_layout(300, "팀별 평균 AHT (초)"))
        st.plotly_chart(fig, use_container_width=True)

    # 근속그룹별
    if "근속그룹" in responded.columns:
        st.markdown('<div class="section-title">근속그룹별 AHT</div>', unsafe_allow_html=True)
        tg_df = responded.groupby("근속그룹").agg(
            응대수=("근속그룹", "count"),
            평균AHT=("AHT(초)", "mean"),
        ).round(1).reset_index()
        fig2 = px.bar(tg_df, x="근속그룹", y="평균AHT",
                      color_discrete_sequence=[COLORS["info"]])
        fig2.update_layout(**base_layout(300, "근속그룹별 평균 AHT (초)"))
        st.plotly_chart(fig2, use_container_width=True)

# ─────────────────────────────────────────────
# 채팅 현황 페이지
# ─────────────────────────────────────────────
def page_chat(chat, unit, month_range, start, end):
    if chat.empty:
        st.info("채팅 데이터가 없습니다.")
        return

    responded = chat[chat["응대여부"] == "응대"]
    total    = len(chat)
    resp_cnt = len(responded)
    rr       = resp_cnt / total * 100 if total else 0
    avg_resp = responded["응답시간(초)"].mean() if not responded.empty else 0
    avg_lead = responded["리드타임(초)"].mean() if not responded.empty else 0

    cols = st.columns(5)
    kpis = [
        ("전체 인입", f"{total:,}", "건"),
        ("응대", f"{resp_cnt:,}", "건"),
        ("응대율", fmt_pct(rr), ""),
        ("평균 응답시간", fmt_sec(avg_resp), ""),
        ("평균 리드타임", fmt_sec(avg_lead), ""),
    ]
    for col, (label, val, u) in zip(cols, kpis):
        with col:
            st.markdown(kpi_card(label, val, unit=u), unsafe_allow_html=True)

    # 추이
    pc = get_period_col(unit)
    cr_s, _ = get_chart_range(unit, end, month_range)
    ch_in = chat[chat[pc] >= pd.Timestamp(cr_s)].groupby(pc).size().reset_index(name="건수")
    ch_re = responded[responded[pc] >= pd.Timestamp(cr_s)].groupby(pc).size().reset_index(name="건수")

    st.markdown('<div class="section-title">인입/응대 추이</div>', unsafe_allow_html=True)
    col_t, col_d = st.columns([2, 1])
    with col_t:
        fig = trend_chart({"채팅 인입": ch_in, "응대": ch_re},
                          unit=unit, y_label="건수", title="채팅 인입 / 응대 추이")
        st.plotly_chart(fig, use_container_width=True)
    with col_d:
        fig2 = donut_chart(["응대", "미응대"], [resp_cnt, total - resp_cnt],
                           [COLORS["success"], COLORS["danger"]], title="응대 현황")
        st.plotly_chart(fig2, use_container_width=True)

    # 대분류별 리드타임
    if "대분류" in chat.columns and not responded.empty:
        st.markdown('<div class="section-title">대분류별 평균 리드타임</div>', unsafe_allow_html=True)
        cat_df = responded.groupby("대분류").agg(
            건수=("대분류", "count"),
            평균리드타임=("리드타임(초)", "mean"),
        ).round(1).reset_index().sort_values("건수", ascending=False)
        fig3 = px.bar(cat_df, x="대분류", y="평균리드타임",
                      color_discrete_sequence=[COLORS["chat"]])
        fig3.update_layout(**base_layout(300, "대분류별 평균 리드타임 (초)"))
        st.plotly_chart(fig3, use_container_width=True)

    # 시간대별
    st.markdown('<div class="section-title">시간대별 인입 현황</div>', unsafe_allow_html=True)
    hourly = chat.groupby("인입시간대").agg(
        인입=("인입시간대", "count"),
        응대=("응대여부", lambda x: (x == "응대").sum()),
    ).reset_index()
    fig4 = go.Figure()
    fig4.add_trace(go.Bar(x=hourly["인입시간대"], y=hourly["인입"],
                          name="인입", marker_color=hex_rgba(COLORS["chat"], 0.7)))
    fig4.add_trace(go.Bar(x=hourly["인입시간대"], y=hourly["응대"],
                          name="응대", marker_color=COLORS["chat"]))
    fig4.update_layout(**base_layout(300, "시간대별 인입 / 응대"))
    st.plotly_chart(fig4, use_container_width=True)

    # 플랫폼 분포
    if "플랫폼" in chat.columns:
        st.markdown('<div class="section-title">플랫폼별 인입 분포</div>', unsafe_allow_html=True)
        plat = chat.groupby("플랫폼").size().reset_index(name="건수")
        fig5 = donut_chart(plat["플랫폼"].tolist(), plat["건수"].tolist(), title="플랫폼 분포")
        st.plotly_chart(fig5, use_container_width=True)

# ─────────────────────────────────────────────
# 채팅 상담사 페이지
# ─────────────────────────────────────────────
def page_chat_agent(chat, unit, month_range):
    if chat.empty:
        st.info("채팅 데이터가 없습니다.")
        return

    responded = chat[chat["응대여부"] == "응대"]
    if responded.empty:
        st.info("응대 데이터가 없습니다.")
        return

    st.markdown('<div class="section-title">상담사별 채팅 성과</div>', unsafe_allow_html=True)
    agent_df = responded.groupby("상담사명").agg(
        응대수=("상담사명", "count"),
        평균응답시간=("응답시간(초)", "mean"),
        평균리드타임=("리드타임(초)", "mean"),
    ).round(1).reset_index().sort_values("응대수", ascending=False)
    st.dataframe(agent_df, use_container_width=True, height=400)

    if "팀명" in responded.columns:
        st.markdown('<div class="section-title">팀별 평균 리드타임</div>', unsafe_allow_html=True)
        team_df = responded.groupby("팀명").agg(
            응대수=("팀명", "count"),
            평균리드타임=("리드타임(초)", "mean"),
        ).round(1).reset_index()
        fig = px.bar(team_df, x="팀명", y="평균리드타임",
                     color_discrete_sequence=[COLORS["chat"]])
        fig.update_layout(**base_layout(300, "팀별 평균 리드타임 (초)"))
        st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# 게시판 현황 페이지
# ─────────────────────────────────────────────
def page_board(board, unit, month_range, start, end):
    if board.empty:
        st.info("게시판 데이터가 없습니다.")
        return

    responded = board[board["응대여부"] == "응대"]
    total    = len(board)
    resp_cnt = len(responded)
    rr       = resp_cnt / total * 100 if total else 0
    avg_lead = responded["리드타임(초)"].mean() if not responded.empty else 0

    cols = st.columns(4)
    kpis = [
        ("전체 티켓", f"{total:,}", "건"),
        ("응답완료", f"{resp_cnt:,}", "건"),
        ("응답률", fmt_pct(rr), ""),
        ("평균 리드타임", fmt_sec(avg_lead), ""),
    ]
    for col, (label, val, u) in zip(cols, kpis):
        with col:
            st.markdown(kpi_card(label, val, unit=u), unsafe_allow_html=True)

    # 추이
    pc = get_period_col(unit)
    cr_s, _ = get_chart_range(unit, end, month_range)
    bo_in = board[board[pc] >= pd.Timestamp(cr_s)].groupby(pc).size().reset_index(name="건수")
    bo_re = responded[responded[pc] >= pd.Timestamp(cr_s)].groupby(pc).size().reset_index(name="건수")

    st.markdown('<div class="section-title">티켓 접수 / 응답 추이</div>', unsafe_allow_html=True)
    col_t, col_d = st.columns([2, 1])
    with col_t:
        fig = trend_chart({"접수": bo_in, "응답": bo_re},
                          unit=unit, y_label="건수", title="게시판 접수 / 응답 추이")
        st.plotly_chart(fig, use_container_width=True)
    with col_d:
        fig2 = donut_chart(["응답", "미응답"], [resp_cnt, total - resp_cnt],
                           [COLORS["success"], COLORS["danger"]], title="응답 현황")
        st.plotly_chart(fig2, use_container_width=True)

    # 대분류별
    if "대분류" in board.columns:
        st.markdown('<div class="section-title">대분류별 티켓 분석</div>', unsafe_allow_html=True)
        cat_df = board.groupby("대분류").agg(
            건수=("대분류", "count"),
            응답수=("응대여부", lambda x: (x == "응대").sum()),
        ).reset_index()
        cat_df["응답률"] = (cat_df["응답수"] / cat_df["건수"] * 100).round(1)
        fig3 = px.bar(cat_df, x="대분류", y="건수",
                      color_discrete_sequence=[COLORS["board"]])
        fig3.update_layout(**base_layout(300, "대분류별 티켓 건수"))
        st.plotly_chart(fig3, use_container_width=True)

    # 플랫폼 분포
    if "플랫폼" in board.columns:
        st.markdown('<div class="section-title">플랫폼별 분포</div>', unsafe_allow_html=True)
        plat = board.groupby("플랫폼").size().reset_index(name="건수")
        fig4 = donut_chart(plat["플랫폼"].tolist(), plat["건수"].tolist(), title="플랫폼 분포")
        st.plotly_chart(fig4, use_container_width=True)

    # 시간대별
    st.markdown('<div class="section-title">시간대별 접수 현황</div>', unsafe_allow_html=True)
    hourly = board.groupby("인입시간대").agg(
        접수=("인입시간대", "count"),
        응답=("응대여부", lambda x: (x == "응대").sum()),
    ).reset_index()
    fig5 = go.Figure()
    fig5.add_trace(go.Bar(x=hourly["인입시간대"], y=hourly["접수"],
                          name="접수", marker_color=hex_rgba(COLORS["board"], 0.7)))
    fig5.add_trace(go.Bar(x=hourly["인입시간대"], y=hourly["응답"],
                          name="응답", marker_color=COLORS["board"]))
    fig5.update_layout(**base_layout(300, "시간대별 접수 / 응답"))
    st.plotly_chart(fig5, use_container_width=True)

# ─────────────────────────────────────────────
# 게시판 상담사 페이지
# ─────────────────────────────────────────────
def page_board_agent(board, unit, month_range):
    if board.empty:
        st.info("게시판 데이터가 없습니다.")
        return

    responded = board[board["응대여부"] == "응대"]
    if responded.empty:
        st.info("응답 데이터가 없습니다.")
        return

    st.markdown('<div class="section-title">상담사별 게시판 성과</div>', unsafe_allow_html=True)
    agent_df = responded.groupby("상담사명").agg(
        응답수=("상담사명", "count"),
        평균리드타임=("리드타임(초)", "mean"),
    ).round(1).reset_index().sort_values("응답수", ascending=False)
    st.dataframe(agent_df, use_container_width=True, height=400)

    if "팀명" in responded.columns:
        st.markdown('<div class="section-title">팀별 평균 리드타임</div>', unsafe_allow_html=True)
        team_df = responded.groupby("팀명").agg(
            응답수=("팀명", "count"),
            평균리드타임=("리드타임(초)", "mean"),
        ).round(1).reset_index()
        fig = px.bar(team_df, x="팀명", y="평균리드타임",
                     color_discrete_sequence=[COLORS["board"]])
        fig.update_layout(**base_layout(300, "팀별 평균 리드타임 (초)"))
        st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# 상담사 종합 페이지
# ─────────────────────────────────────────────
def page_agent_total(phone, chat, board):
    st.markdown('<div class="section-title">상담사 종합 성과</div>', unsafe_allow_html=True)

    rows = []
    for name in set(
        list(phone["상담사명"].unique() if not phone.empty else []) +
        list(chat["상담사명"].unique()  if not chat.empty  else []) +
        list(board["상담사명"].unique() if not board.empty else [])
    ):
        if name == "미응대":
            continue
        ph = phone[(phone["상담사명"] == name) & (phone["응대여부"] == "응대")] if not phone.empty else pd.DataFrame()
        ch = chat[(chat["상담사명"]   == name) & (chat["응대여부"]  == "응대")] if not chat.empty  else pd.DataFrame()
        bo = board[(board["상담사명"] == name) & (board["응대여부"] == "응대")] if not board.empty else pd.DataFrame()
        rows.append({
            "상담사명":  name,
            "전화응대":  len(ph),
            "채팅응대":  len(ch),
            "게시판응답": len(bo),
            "전화AHT평균": round(ph["AHT(초)"].mean(), 1) if not ph.empty else 0,
            "채팅리드타임평균": round(ch["리드타임(초)"].mean(), 1) if not ch.empty else 0,
            "게시판리드타임평균": round(bo["리드타임(초)"].mean(), 1) if not bo.empty else 0,
        })

    if not rows:
        st.info("데이터가 없습니다.")
        return

    df_agent = pd.DataFrame(rows).sort_values("전화응대", ascending=False)
    st.dataframe(df_agent, use_container_width=True, height=500)

    # 채널 분포 상위 10명
    st.markdown('<div class="section-title">상담사별 채널 분포 (상위 10)</div>', unsafe_allow_html=True)
    top10 = df_agent.head(10)
    fig = go.Figure()
    fig.add_trace(go.Bar(name="전화", x=top10["상담사명"], y=top10["전화응대"],
                         marker_color=COLORS["phone"]))
    fig.add_trace(go.Bar(name="채팅", x=top10["상담사명"], y=top10["채팅응대"],
                         marker_color=COLORS["chat"]))
    fig.add_trace(go.Bar(name="게시판", x=top10["상담사명"], y=top10["게시판응답"],
                         marker_color=COLORS["board"]))
    fig.update_layout(barmode="stack", **base_layout(360, "상담사별 채널 분포"))
    st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────
# 사이드바
# ─────────────────────────────────────────────
def render_sidebar(phone_raw, chat_raw, board_raw):
    with st.sidebar:
        st.markdown("""
        <div style="padding:20px 16px 12px;border-bottom:1px solid #334155;margin-bottom:16px;">
            <div style="font-size:16px;font-weight:800;color:#f1f5f9;letter-spacing:-0.5px;">
                CC OPS
            </div>
            <div style="font-size:11px;color:#64748b;margin-top:2px;">Contact Center Analytics</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("데이터 새로고침"):
            st.cache_data.clear()
            st.rerun()

        st.markdown('<div style="height:12px;"></div>', unsafe_allow_html=True)

        # 기간 단위
        unit = st.radio("기간 단위", ["일별", "주별", "월별"], horizontal=True)

        # 월별 추이 범위
        month_range = 3
        if unit == "월별":
            month_range = st.slider("추이 범위 (개월)", 1, 6, 3)

        # 날짜 범위
        today = date.today()
        st.markdown('<div style="margin-top:12px;font-size:11px;color:#94a3b8;font-weight:600;">날짜 범위</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("7일"):
                st.session_state["date_start"] = today - timedelta(days=6)
                st.session_state["date_end"]   = today
        with col2:
            if st.button("30일"):
                st.session_state["date_start"] = today - timedelta(days=29)
                st.session_state["date_end"]   = today
        col3, col4 = st.columns(2)
        with col3:
            if st.button("이번달"):
                st.session_state["date_start"] = today.replace(day=1)
                st.session_state["date_end"]   = today
        with col4:
            if st.button("전체"):
                st.session_state["date_start"] = date(2024, 1, 1)
                st.session_state["date_end"]   = today

        date_start = st.date_input("시작일", value=st.session_state.get("date_start", today - timedelta(days=29)))
        date_end   = st.date_input("종료일", value=st.session_state.get("date_end", today))

        # 사업자 필터
        all_ops = sorted(set(
            list(phone_raw["사업자명"].dropna().unique() if "사업자명" in phone_raw.columns else []) +
            list(chat_raw["사업자명"].dropna().unique()  if "사업자명" in chat_raw.columns  else []) +
            list(board_raw["사업자명"].dropna().unique() if "사업자명" in board_raw.columns else [])
        ))
        st.markdown('<div style="margin-top:12px;font-size:11px;color:#94a3b8;font-weight:600;">사업자</div>', unsafe_allow_html=True)
        sel_ops = st.multiselect("사업자 선택", all_ops, default=[], label_visibility="collapsed")

        # 브랜드 필터
        all_brands = sorted(set(
            list(phone_raw["브랜드"].dropna().unique() if "브랜드" in phone_raw.columns else []) +
            list(chat_raw["브랜드"].dropna().unique()  if "브랜드" in chat_raw.columns  else []) +
            list(board_raw["브랜드"].dropna().unique() if "브랜드" in board_raw.columns else [])
        ))
        st.markdown('<div style="margin-top:12px;font-size:11px;color:#94a3b8;font-weight:600;">브랜드</div>', unsafe_allow_html=True)
        sel_brands = st.multiselect("브랜드 선택", all_brands, default=[], label_visibility="collapsed")

        # 메뉴
        st.markdown('<div style="height:16px;border-top:1px solid #334155;margin-top:16px;padding-top:16px;font-size:11px;color:#94a3b8;font-weight:600;">메뉴</div>', unsafe_allow_html=True)
        menu = st.session_state.get("menu", "전체 현황")
        for group, items in MENU_GROUPS.items():
            for item in items:
                selected = "✦ " if menu == item else ""
                if st.button(f"{selected}{item}", key=f"menu_{item}"):
                    st.session_state["menu"] = item
                    st.rerun()

    return unit, month_range, date_start, date_end, sel_ops, sel_brands

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    # 데이터 로드
    agent_raw = load_agent()
    phone_raw = load_phone()
    chat_raw  = load_chat()
    board_raw = load_board()

    # 사이드바
    unit, month_range, date_start, date_end, sel_ops, sel_brands = render_sidebar(phone_raw, chat_raw, board_raw)

    # 에이전트 병합
    base_date = datetime.now().date()
    phone_m = merge_agent(phone_raw, agent_raw, base_date)
    chat_m  = merge_agent(chat_raw,  agent_raw, base_date)
    board_m = merge_agent(board_raw, agent_raw, base_date)

    # 필터 적용
    phone_f = filter_df(phone_m, date_start, date_end, sel_brands or None, sel_ops or None)
    chat_f  = filter_df(chat_m,  date_start, date_end, sel_brands or None, sel_ops or None)
    board_f = filter_df(board_m, date_start, date_end, sel_brands or None, sel_ops or None)

    # 데이터 없을 때
    if all(len(df) == 0 for df in [phone_f, chat_f, board_f]):
        st.markdown("""
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                    height:60vh;text-align:center;gap:12px;">
            <div style="font-size:48px;">📊</div>
            <div style="font-size:20px;font-weight:800;color:#0f172a;">데이터 연결 필요</div>
            <div style="font-size:13px;color:#64748b;">Google Sheets에 데이터를 입력하거나 필터 조건을 확인해주세요.</div>
            <div style="font-size:11px;color:#94a3b8;background:#f1f5f9;padding:8px 16px;border-radius:8px;">
                SHEET_ID 및 GID_MAP 설정을 확인하세요
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # 메뉴 라우팅
    menu = st.session_state.get("menu", "전체 현황")

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
