import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
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
# 페이지 설정 & CSS
# ══════════════════════════════════════════════
st.set_page_config(page_title="Contact Center OPS", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body,[class*="css"]{font-family:'Inter',-apple-system,sans-serif;background:#F5F6F8!important;color:#0f172a}
section[data-testid="stSidebar"]{background:#1e293b!important;border-right:none!important;width:220px!important}
section[data-testid="stSidebar"] *{color:#e2e8f0!important}
section[data-testid="stSidebar"] .stButton>button{
    background:#334155!important;border:none!important;border-radius:10px!important;
    color:#e2e8f0!important;width:100%!important;text-align:left!important;
    padding:10px 14px!important;font-size:13px!important;font-weight:500!important;margin-bottom:2px!important}
section[data-testid="stSidebar"] .stButton>button:hover{background:#6366f1!important;color:#fff!important}
.main .block-container{padding:24px 32px!important;max-width:100%!important;background:#F5F6F8!important}
.dash-header{display:flex;align-items:center;justify-content:space-between;
    margin-bottom:28px;padding:20px 28px;background:#fff;border-radius:20px;
    box-shadow:0 2px 12px rgba(0,0,0,0.06)}
.dash-header-left h1{font-size:22px;font-weight:800;color:#0f172a;letter-spacing:-.5px;margin-bottom:4px}
.dash-header-left span{font-size:12px;color:#94a3b8}
.kpi-card{background:#fff;border-radius:20px;box-shadow:0 2px 12px rgba(0,0,0,0.06);
    padding:22px 24px;height:100%;margin-bottom:4px}
.kpi-label{font-size:11px;font-weight:600;color:#64748b;text-transform:uppercase;
    letter-spacing:.5px;margin-bottom:10px}
.kpi-value{font-size:24px;font-weight:800;color:#0f172a;letter-spacing:-1px;line-height:1;margin-bottom:8px}
.kpi-unit{font-size:12px;color:#94a3b8;margin-left:4px;font-weight:400}
.kpi-delta-row{display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin-top:6px}
.kpi-delta{display:inline-flex;align-items:center;gap:3px;font-size:11px;
    font-weight:600;padding:3px 8px;border-radius:20px}
.kpi-delta.up{background:#fef2f2;color:#ef4444}
.kpi-delta.down{background:#f0fdf4;color:#22c55e}
.kpi-delta.neu{background:#f8fafc;color:#94a3b8}
.kpi-delta.up.rev{background:#f0fdf4!important;color:#22c55e!important}
.kpi-delta.down.rev{background:#fef2f2!important;color:#ef4444!important}
.section-title{font-size:15px;font-weight:700;color:#0f172a;margin:24px 0 12px;letter-spacing:-.3px}
#MainMenu,footer,header{visibility:hidden}
.stDeployButton{display:none}
div[data-testid="stToolbar"]{display:none}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# 유틸
# ══════════════════════════════════════════════
def hex_rgba(h, a=0.08):
    h=h.lstrip("#"); r,g,b=int(h[0:2],16),int(h[2:4],16),int(h[4:6],16)
    return f"rgba({r},{g},{b},{a})"

def fmt_hms(sec):
    """초 → H:MM:SS 포맷"""
    try: sec=int(float(sec))
    except: return "0:00:00"
    if sec<=0: return "0:00:00"
    h=sec//3600; m=(sec%3600)//60; s=sec%60
    return f"{h}:{m:02d}:{s:02d}"

def fmt_pct(val):
    try: return f"{float(val):.1f}%"
    except: return "0.0%"

def to_date(v):
    if v is None: return None
    if isinstance(v,date) and not isinstance(v,datetime): return v
    if isinstance(v,datetime): return v.date()
    try: return pd.Timestamp(v).date()
    except: return None

def get_tenure_group(hire_date, base_date):
    try:
        if pd.isna(hire_date): return "미입력"
    except: return "미입력"
    hire=to_date(hire_date); base=to_date(base_date)
    if not hire or not base: return "미입력"
    days=(base-hire).days
    for t,l in TENURE_GROUPS:
        if days<=t: return l
    return "기존5 (4년초과)"

def gsheet_url(gid):
    return f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"

def get_period_col(unit):
    return {"일별":"일자","주별":"주차","월별":"월"}[unit]

def assign_period_cols(df, date_col="일자"):
    if date_col not in df.columns: return df
    df=df.copy()
    df[date_col]=pd.to_datetime(df[date_col],errors="coerce")
    df["일자"]=df[date_col]
    df["주차"]=df[date_col].dt.to_period("W").dt.start_time
    df["월"]=df[date_col].dt.to_period("M").dt.start_time
    return df

def get_chart_range(unit, end_date, month_range=3):
    ed=pd.Timestamp(end_date)
    if unit=="일별": return ed-timedelta(days=89),ed
    if unit=="주별": return ed-timedelta(weeks=12),ed
    return ed-timedelta(days=30*month_range),ed

# ══════════════════════════════════════════════
# 데이터 로드
# ══════════════════════════════════════════════
@st.cache_data(ttl=300,show_spinner=False)
def load_agent():
    try:
        df=pd.read_csv(gsheet_url(GID_MAP["agent"]))
        df.columns=df.columns.str.strip()
        df["입사일"]=pd.to_datetime(df["입사일"],errors="coerce")
        return df
    except: return pd.DataFrame(columns=["상담사명","팀명","입사일"])

@st.cache_data(ttl=300,show_spinner=False)
def load_phone():
    try:
        df=pd.read_csv(gsheet_url(GID_MAP["phone"]))
        df.columns=df.columns.str.strip()
        df["일자"]=pd.to_datetime(df["일자"],errors="coerce")
        df["인입시각"]=pd.to_datetime(df["일자"].astype(str)+" "+df["인입시각"].astype(str),errors="coerce")
        for c in ["통화시간(초)","ACW시간(초)","대기시간(초)"]:
            df[c]=pd.to_numeric(df.get(c,0),errors="coerce").fillna(0)
        df["AHT(초)"]=df["통화시간(초)"]+df["ACW시간(초)"]
        df["응대여부"]=df["상담사명"].apply(lambda x:"미응대" if str(x).strip()=="미응대" else "응대")
        df["인입시간대"]=df["인입시각"].dt.hour
        return assign_period_cols(df,"일자")
    except: return pd.DataFrame(columns=["일자","사업자명","브랜드","상담사명","인입시각",
        "대기시간(초)","통화시간(초)","ACW시간(초)","대분류","중분류","소분류",
        "AHT(초)","응대여부","인입시간대","주차","월"])

@st.cache_data(ttl=300,show_spinner=False)
def load_chat():
    try:
        df=pd.read_csv(gsheet_url(GID_MAP["chat"]))
        df.columns=df.columns.str.strip()
        df["일자"]=pd.to_datetime(df["일자"],errors="coerce")
        df["접수일시"]=pd.to_datetime(df["접수일시"],errors="coerce")
        df["첫멘트발송일시"]=pd.to_datetime(df["첫멘트발송일시"],errors="coerce")
        df["종료일시"]=pd.to_datetime(df["종료일시"],errors="coerce")
        df["응답시간(초)"]=(df["첫멘트발송일시"]-df["접수일시"]).dt.total_seconds().clip(lower=0)
        df["리드타임(초)"]=(df["종료일시"]-df["접수일시"]).dt.total_seconds().clip(lower=0)
        포기=df["배분전포기여부"].astype(str).str.strip().str.upper() if "배분전포기여부" in df.columns else pd.Series(["N"]*len(df))
        df["응대여부"]=df.apply(
            lambda r:"미응대" if pd.isna(r["첫멘트발송일시"]) or 포기.iloc[r.name]=="Y" else "응대",axis=1)
        df["인입시간대"]=df["접수일시"].dt.hour
        return assign_period_cols(df,"일자")
    except: return pd.DataFrame(columns=["일자","사업자명","브랜드","플랫폼","상담사명",
        "접수일시","첫멘트발송일시","종료일시","배분전포기여부","대분류","중분류","소분류",
        "응답시간(초)","리드타임(초)","응대여부","인입시간대","주차","월"])

@st.cache_data(ttl=300,show_spinner=False)
def load_board():
    try:
        df=pd.read_csv(gsheet_url(GID_MAP["board"]))
        df.columns=df.columns.str.strip()
        df["일자"]=pd.to_datetime(df["일자"],errors="coerce")
        df["접수일시"]=pd.to_datetime(df["접수일시"],errors="coerce")
        df["응답일시"]=pd.to_datetime(df["응답일시"],errors="coerce")
        df["리드타임(초)"]=(df["응답일시"]-df["접수일시"]).dt.total_seconds().clip(lower=0)
        df["응대여부"]=df["응답일시"].apply(lambda x:"미응대" if pd.isna(x) else "응대")
        df["인입시간대"]=df["접수일시"].dt.hour
        return assign_period_cols(df,"일자")
    except: return pd.DataFrame(columns=["일자","사업자명","브랜드","플랫폼","상담사명",
        "접수일시","응답일시","대분류","중분류","소분류","리드타임(초)","응대여부","인입시간대","주차","월"])

def merge_agent(df, agent_df, base_d):
    if agent_df.empty or "상담사명" not in df.columns:
        df=df.copy(); df["팀명"]="미지정"; df["근속그룹"]="미입력"; return df
    merged=df.merge(agent_df[["상담사명","팀명","입사일"]],on="상담사명",how="left")
    merged["팀명"]=merged["팀명"].fillna("미지정")
    merged["근속그룹"]=merged["입사일"].apply(lambda x:get_tenure_group(x,base_d))
    return merged

def filter_df(df, start, end, brands=None, operators=None):
    if df.empty or "일자" not in df.columns: return df
    mask=(df["일자"]>=pd.Timestamp(start))&(df["일자"]<=pd.Timestamp(end))
    df=df[mask].copy()
    if brands and "브랜드" in df.columns: df=df[df["브랜드"].isin(brands)]
    if operators and "사업자명" in df.columns: df=df[df["사업자명"].isin(operators)]
    return df

# ══════════════════════════════════════════════
# KPI 카드
# ══════════════════════════════════════════════
def kpi_card(label, value, delta_curr=None, delta_yoy=None, reverse=False, unit=""):
    def badge(val,rev):
        if val is None: return ""
        sign="▲" if val>0 else("▼" if val<0 else "—")
        d="up" if val>0 else("down" if val<0 else "neu")
        rc=" rev" if rev else ""
        return f'<span class="kpi-delta {d}{rc}">{sign} {abs(val):.1f}%</span>'
    dh=""
    if delta_curr is not None: dh+=badge(delta_curr,reverse)
    if delta_yoy  is not None:
        dh+='<span style="font-size:10px;color:#94a3b8;margin:0 4px;">YoY</span>'
        dh+=badge(delta_yoy,reverse)
    return f"""<div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}<span class="kpi-unit">{unit}</span></div>
        <div class="kpi-delta-row">{dh}</div></div>"""

# ══════════════════════════════════════════════
# 차트 공통
# ══════════════════════════════════════════════
def base_layout(h=320, title="", legend_side=False):
    lg = dict(orientation="v",yanchor="middle",y=0.5,xanchor="left",x=1.02,font=dict(size=11)) \
         if legend_side else \
         dict(orientation="h",yanchor="bottom",y=1.02,xanchor="right",x=1,font=dict(size=11))
    return dict(
        height=h,
        title=dict(text=title,font=dict(size=13,color="#0f172a",family="Inter"),x=0),
        margin=dict(l=8,r=8,t=40 if title else 16,b=8),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter",size=11,color="#64748b"),
        legend=lg,
        xaxis=dict(showgrid=False,zeroline=False,tickfont=dict(size=10)),
        yaxis=dict(showgrid=True,gridcolor="#f1f5f9",zeroline=False,tickfont=dict(size=10)),
    )

def trend_chart(series_dict, unit, y_label="건수", h=320, month_range=3, title=""):
    pc=get_period_col(unit)
    fig=go.Figure()
    for i,(name,s) in enumerate(series_dict.items()):
        if s is None or s.empty or pc not in s.columns or y_label not in s.columns: continue
        c=PALETTE[i%len(PALETTE)]
        fig.add_trace(go.Scatter(x=s[pc],y=s[y_label],mode="lines+markers",name=name,
            line=dict(color=c,width=2.5),marker=dict(size=6,color=c),
            fill="tozeroy",fillcolor=hex_rgba(c,0.07)))
    fig.update_layout(**base_layout(h,title))
    return fig

def donut_chart(labels, values, colors=None, h=260, title=""):
    if not colors: colors=PALETTE
    total=sum(v for v in values if v) if values else 0
    fig=go.Figure(go.Pie(
        labels=labels,values=values,hole=0.62,
        marker=dict(colors=colors[:len(labels)],line=dict(color="#fff",width=3)),
        textinfo="none",
        hovertemplate="%{label}: %{value:,}건 (%{percent})<extra></extra>",
    ))
    lo=base_layout(h,title,legend_side=True)
    lo["annotations"]=[dict(text=f"<b>{total:,}</b>",x=0.5,y=0.5,showarrow=False,
        font=dict(size=18,color="#0f172a",family="Inter"))]
    fig.update_layout(**lo)
    return fig

def bar_h_chart(df, x, y, color=None, h=320, title=""):
    fig=px.bar(df,x=x,y=y,color=color,orientation="h",
        color_discrete_sequence=PALETTE)
    fig.update_traces(marker_line_width=0)
    fig.update_layout(**base_layout(h,title))
    return fig

def heatmap_chart(df_pivot, h=320, title=""):
    fig=go.Figure(go.Heatmap(
        z=df_pivot.values,x=df_pivot.columns.astype(str),y=df_pivot.index.astype(str),
        colorscale=[[0,"#f8fafc"],[0.5,"#818cf8"],[1,"#4338ca"]],showscale=True,
        hovertemplate="시간대: %{x}시<br>날짜: %{y}<br>건수: %{z}<extra></extra>",
    ))
    fig.update_layout(**base_layout(h,title))
    return fig

# ══════════════════════════════════════════════
# 전체 현황
# ══════════════════════════════════════════════
def page_overview(phone, chat, board, unit, month_range, start, end):
    updated=datetime.now().strftime("%Y-%m-%d %H:%M")
    s_str=start.strftime("%Y.%m.%d") if hasattr(start,"strftime") else str(start)
    e_str=end.strftime("%Y.%m.%d")   if hasattr(end,"strftime")   else str(end)
    st.markdown(f"""<div class="dash-header">
        <div class="dash-header-left"><h1>Contact Center Dashboard</h1><span>Updated {updated}</span></div>
        <div class="dash-header-right">
            <span style="font-size:12px;color:#64748b;background:#f1f5f9;padding:6px 14px;border-radius:20px;font-weight:600;">
                {s_str} ~ {e_str}</span></div></div>""",unsafe_allow_html=True)

    t_ph=len(phone);t_ch=len(chat);t_bo=len(board);t_all=t_ph+t_ch+t_bo
    r_ph=len(phone[phone["응대여부"]=="응대"]) if not phone.empty else 0
    r_ch=len(chat[chat["응대여부"]=="응대"])   if not chat.empty  else 0
    r_bo=len(board[board["응대여부"]=="응대"]) if not board.empty else 0

    c1,c2,c3,c4=st.columns(4)
    for col,lbl,val,u in [(c1,"전체 인입",f"{t_all:,}","건"),(c2,"전화 인입",f"{t_ph:,}","건"),
                           (c3,"채팅 인입",f"{t_ch:,}","건"),(c4,"게시판 인입",f"{t_bo:,}","건")]:
        with col: st.markdown(kpi_card(lbl,val,unit=u),unsafe_allow_html=True)

    st.markdown('<div class="section-title">채널별 응대율</div>',unsafe_allow_html=True)
    c1,c2,c3=st.columns(3)
    for col,lbl,val in [(c1,"전화 응대율",fmt_pct(r_ph/t_ph*100 if t_ph else 0)),
                         (c2,"채팅 응대율",fmt_pct(r_ch/t_ch*100 if t_ch else 0)),
                         (c3,"게시판 응대율",fmt_pct(r_bo/t_bo*100 if t_bo else 0))]:
        with col: st.markdown(kpi_card(lbl,val),unsafe_allow_html=True)

    st.markdown('<div class="section-title">채널별 인입 분포 & 추이</div>',unsafe_allow_html=True)
    cd,ct=st.columns([1,2])
    with cd:
        st.plotly_chart(donut_chart(["전화","채팅","게시판"],[t_ph,t_ch,t_bo],
            [COLORS["phone"],COLORS["chat"],COLORS["board"]],title="채널 분포"),use_container_width=True)
    with ct:
        pc=get_period_col(unit); cr_s,_=get_chart_range(unit,end,month_range)
        def agg(df):
            if df.empty or pc not in df.columns: return pd.DataFrame(columns=[pc,"건수"])
            return df[df[pc]>=pd.Timestamp(cr_s)].groupby(pc).size().reset_index(name="건수")
        st.plotly_chart(trend_chart({"전화":agg(phone),"채팅":agg(chat),"게시판":agg(board)},
            unit=unit,y_label="건수",title="채널별 인입 추이"),use_container_width=True)

# ══════════════════════════════════════════════
# VOC 인입 분석
# ══════════════════════════════════════════════
def page_voc(phone, chat, board, unit, month_range):
    st.markdown('<div class="section-title">VOC 인입 분석</div>',unsafe_allow_html=True)

    # 전체 합치기
    frames=[]
    for df,ch in [(phone,"전화"),(chat,"채팅"),(board,"게시판")]:
        if df.empty: continue
        tmp=df.copy(); tmp["채널"]=ch
        frames.append(tmp)
    if not frames: st.info("데이터가 없습니다."); return
    all_df=pd.concat(frames,ignore_index=True)

    pc=get_period_col(unit); cr_s,_=get_chart_range(unit,pd.Timestamp("today"),month_range)

    # ── 필터 UI (대분류/중분류/소분류)
    col_f1,col_f2,col_f3,col_f4=st.columns(4)
    with col_f1:
        ch_sel=st.multiselect("채널",["전화","채팅","게시판"],default=["전화","채팅","게시판"],key="voc_ch")
    cats1=sorted(all_df["대분류"].dropna().unique().tolist()) if "대분류" in all_df.columns else []
    with col_f2:
        cat1_sel=st.multiselect("대분류",cats1,default=[],key="voc_cat1")
    # 중분류 동적
    mid_pool=all_df[all_df["대분류"].isin(cat1_sel)]["중분류"].dropna().unique().tolist() if cat1_sel and "중분류" in all_df.columns else (all_df["중분류"].dropna().unique().tolist() if "중분류" in all_df.columns else [])
    with col_f3:
        cat2_sel=st.multiselect("중분류",sorted(mid_pool),default=[],key="voc_cat2")
    sub_pool=all_df[all_df["중분류"].isin(cat2_sel)]["소분류"].dropna().unique().tolist() if cat2_sel and "소분류" in all_df.columns else (all_df["소분류"].dropna().unique().tolist() if "소분류" in all_df.columns else [])
    with col_f4:
        cat3_sel=st.multiselect("소분류",sorted(sub_pool),default=[],key="voc_cat3")

    voc=all_df.copy()
    if ch_sel:   voc=voc[voc["채널"].isin(ch_sel)]
    if cat1_sel and "대분류" in voc.columns: voc=voc[voc["대분류"].isin(cat1_sel)]
    if cat2_sel and "중분류" in voc.columns: voc=voc[voc["중분류"].isin(cat2_sel)]
    if cat3_sel and "소분류" in voc.columns: voc=voc[voc["소분류"].isin(cat3_sel)]

    total_voc=len(voc)
    st.markdown(f'<div class="section-title">총 {total_voc:,}건</div>',unsafe_allow_html=True)

    # ── 추이 (기간별)
    st.markdown('<div class="section-title">인입 추이</div>',unsafe_allow_html=True)
    if pc in voc.columns:
        trend_data={}
        for ch in (ch_sel or ["전화","채팅","게시판"]):
            s=voc[(voc["채널"]==ch)&(voc[pc]>=pd.Timestamp(cr_s))].groupby(pc).size().reset_index(name="건수")
            if not s.empty: trend_data[ch]=s
        if trend_data:
            st.plotly_chart(trend_chart(trend_data,unit=unit,y_label="건수",h=300,title="VOC 인입 추이"),use_container_width=True)

    # ── 사업자별 비중
    st.markdown('<div class="section-title">사업자별 인입 비중</div>',unsafe_allow_html=True)
    if "사업자명" in voc.columns:
        op_df=voc.groupby("사업자명").size().reset_index(name="건수").sort_values("건수",ascending=False)
        c1,c2=st.columns([1,2])
        with c1:
            st.plotly_chart(donut_chart(op_df["사업자명"].tolist(),op_df["건수"].tolist(),
                title="사업자 분포",h=280),use_container_width=True)
        with c2:
            fig=px.bar(op_df,x="건수",y="사업자명",orientation="h",
                color_discrete_sequence=[COLORS["primary"]])
            fig.update_layout(**base_layout(280,"사업자별 건수"))
            st.plotly_chart(fig,use_container_width=True)

    # ── 브랜드별 비중
    st.markdown('<div class="section-title">브랜드별 인입 비중</div>',unsafe_allow_html=True)
    if "브랜드" in voc.columns:
        br_df=voc.groupby("브랜드").size().reset_index(name="건수").sort_values("건수",ascending=False)
        top_br=br_df.head(15)
        c1,c2=st.columns([1,2])
        with c1:
            st.plotly_chart(donut_chart(top_br["브랜드"].tolist(),top_br["건수"].tolist(),
                title="브랜드 분포 (상위15)",h=300),use_container_width=True)
        with c2:
            fig=px.bar(top_br,x="건수",y="브랜드",orientation="h",
                color_discrete_sequence=[COLORS["info"]])
            fig.update_layout(**base_layout(300,"브랜드별 건수"))
            st.plotly_chart(fig,use_container_width=True)

    # ── 대분류 비중
    st.markdown('<div class="section-title">대분류별 비중</div>',unsafe_allow_html=True)
    if "대분류" in voc.columns:
        cat1_df=voc.groupby(["채널","대분류"]).size().reset_index(name="건수").sort_values("건수",ascending=False)
        fig=px.bar(cat1_df,x="대분류",y="건수",color="채널",barmode="stack",
            color_discrete_map={"전화":COLORS["phone"],"채팅":COLORS["chat"],"게시판":COLORS["board"]})
        fig.update_layout(**base_layout(320,"대분류별 채널 인입"))
        st.plotly_chart(fig,use_container_width=True)

    # ── 중분류 TOP20
    if "중분류" in voc.columns:
        st.markdown('<div class="section-title">중분류 TOP 20</div>',unsafe_allow_html=True)
        mid_df=voc.groupby("중분류").size().reset_index(name="건수").sort_values("건수",ascending=False).head(20)
        fig=px.bar(mid_df,x="건수",y="중분류",orientation="h",
            color_discrete_sequence=[COLORS["warning"]])
        fig.update_layout(**base_layout(400,"중분류 TOP 20"))
        st.plotly_chart(fig,use_container_width=True)

    # ── 소분류 TOP20
    if "소분류" in voc.columns:
        st.markdown('<div class="section-title">소분류 TOP 20</div>',unsafe_allow_html=True)
        sub_df=voc.groupby("소분류").size().reset_index(name="건수").sort_values("건수",ascending=False).head(20)
        fig=px.bar(sub_df,x="건수",y="소분류",orientation="h",
            color_discrete_sequence=[COLORS["success"]])
        fig.update_layout(**base_layout(400,"소분류 TOP 20"))
        st.plotly_chart(fig,use_container_width=True)

# ══════════════════════════════════════════════
# 사업자 현황
# ══════════════════════════════════════════════
def page_operator(phone, chat, board, unit, month_range):
    st.markdown('<div class="section-title">사업자별 인입 현황</div>',unsafe_allow_html=True)
    def op_s(df,ch):
        if df.empty or "사업자명" not in df.columns: return pd.DataFrame()
        g=df.groupby("사업자명").agg(인입=("사업자명","count"),
            응대=("응대여부",lambda x:(x=="응대").sum())).reset_index()
        g["응대율"]=(g["응대"]/g["인입"]*100).round(1); g["채널"]=ch; return g
    all_op=pd.concat([op_s(phone,"전화"),op_s(chat,"채팅"),op_s(board,"게시판")])
    if all_op.empty: st.info("사업자명 데이터 없음."); return
    fig=px.bar(all_op,x="사업자명",y="인입",color="채널",barmode="stack",
        color_discrete_map={"전화":COLORS["phone"],"채팅":COLORS["chat"],"게시판":COLORS["board"]})
    fig.update_layout(**base_layout(360,"사업자별 채널 인입"))
    st.plotly_chart(fig,use_container_width=True)
    try:
        pivot=all_op.pivot_table(index="사업자명",columns="채널",values=["인입","응대율"],aggfunc="first")
        st.dataframe(pivot,use_container_width=True)
    except: st.dataframe(all_op,use_container_width=True)

# ══════════════════════════════════════════════
# 전화 현황
# ══════════════════════════════════════════════
def page_phone(phone, unit, month_range, start, end):
    if phone.empty: st.info("전화 데이터가 없습니다."); return
    resp=phone[phone["응대여부"]=="응대"]
    total=len(phone); rc=len(resp)
    rr=rc/total*100 if total else 0
    aw=resp["대기시간(초)"].mean() if not resp.empty else 0
    at=resp["통화시간(초)"].mean() if not resp.empty else 0
    aa=resp["ACW시간(초)"].mean()  if not resp.empty else 0
    ah=resp["AHT(초)"].mean()      if not resp.empty else 0

    # KPI 6개
    c1,c2,c3,c4,c5,c6=st.columns(6)
    for col,lbl,val,u in [
        (c1,"전체 인입",f"{total:,}","건"),
        (c2,"응대",f"{rc:,}","건"),
        (c3,"응대율",fmt_pct(rr),""),
        (c4,"평균 대기",fmt_hms(aw),""),
        (c5,"평균 통화",fmt_hms(at),""),
        (c6,"평균 AHT",fmt_hms(ah),""),
    ]:
        with col: st.markdown(kpi_card(lbl,val,unit=u),unsafe_allow_html=True)

    # ACW KPI 추가
    st.markdown('<div class="section-title">후처리(ACW) 평균</div>',unsafe_allow_html=True)
    st.markdown(kpi_card("평균 ACW",fmt_hms(aa)),unsafe_allow_html=True)

    # 추이
    pc=get_period_col(unit); cr_s,_=get_chart_range(unit,end,month_range)
    ph_in=phone[phone[pc]>=pd.Timestamp(cr_s)].groupby(pc).size().reset_index(name="건수")
    ph_re=resp[resp[pc]>=pd.Timestamp(cr_s)].groupby(pc).size().reset_index(name="건수") if not resp.empty else pd.DataFrame(columns=[pc,"건수"])

    st.markdown('<div class="section-title">인입 / 응대 추이</div>',unsafe_allow_html=True)
    c1,c2=st.columns([2,1])
    with c1: st.plotly_chart(trend_chart({"전화 인입":ph_in,"응대":ph_re},
        unit=unit,y_label="건수",title="인입 / 응대 추이"),use_container_width=True)
    with c2: st.plotly_chart(donut_chart(["응대","미응대"],[rc,total-rc],
        [COLORS["success"],COLORS["danger"]],title="응대 현황"),use_container_width=True)

    # 시간대별 인입/응대 (핵심 추가)
    st.markdown('<div class="section-title">시간대별 인입 / 응대 현황</div>',unsafe_allow_html=True)
    hourly=phone.groupby("인입시간대").agg(
        인입=("인입시간대","count"),
        응대=("응대여부",lambda x:(x=="응대").sum()),
    ).reset_index()
    hourly["미응대"]=hourly["인입"]-hourly["응대"]
    hourly["응대율"]=(hourly["응대"]/hourly["인입"]*100).round(1)
    fig3=go.Figure()
    fig3.add_trace(go.Bar(x=hourly["인입시간대"],y=hourly["응대"],name="응대",marker_color=COLORS["phone"]))
    fig3.add_trace(go.Bar(x=hourly["인입시간대"],y=hourly["미응대"],name="미응대",marker_color=hex_rgba(COLORS["danger"],0.7)))
    fig3.add_trace(go.Scatter(x=hourly["인입시간대"],y=hourly["응대율"],name="응대율(%)",
        yaxis="y2",mode="lines+markers",line=dict(color=COLORS["warning"],width=2),marker=dict(size=6)))
    fig3.update_layout(
        **base_layout(320,"시간대별 인입 / 응대"),
        barmode="stack",
        yaxis2=dict(overlaying="y",side="right",showgrid=False,ticksuffix="%",range=[0,110]),
    )
    st.plotly_chart(fig3,use_container_width=True)

    # AHT 구성 추이
    if not resp.empty:
        st.markdown('<div class="section-title">AHT 구성 분석 (통화 + ACW)</div>',unsafe_allow_html=True)
        aht_df=resp.groupby(pc).agg(통화시간=("통화시간(초)","mean"),ACW시간=("ACW시간(초)","mean")).reset_index()
        fig4=go.Figure()
        fig4.add_trace(go.Bar(x=aht_df[pc],y=aht_df["통화시간"],name="통화시간",marker_color=COLORS["primary"]))
        fig4.add_trace(go.Bar(x=aht_df[pc],y=aht_df["ACW시간"],name="ACW",marker_color=COLORS["warning"]))
        fig4.update_layout(barmode="stack",**base_layout(300,"기간별 평균 AHT 구성 (초)"))
        st.plotly_chart(fig4,use_container_width=True)

    # 대기시간 추이
    if not resp.empty:
        st.markdown('<div class="section-title">평균 대기시간 추이</div>',unsafe_allow_html=True)
        wait_df=resp.groupby(pc).agg(평균대기=("대기시간(초)","mean")).reset_index()
        wait_df["평균대기_hms"]=wait_df["평균대기"].apply(fmt_hms)
        fig_w=go.Figure(go.Scatter(x=wait_df[pc],y=wait_df["평균대기"],mode="lines+markers",
            line=dict(color=COLORS["info"],width=2.5),marker=dict(size=6),
            fill="tozeroy",fillcolor=hex_rgba(COLORS["info"],0.07),
            text=wait_df["평균대기_hms"],hovertemplate="%{x}<br>평균 대기: %{text}<extra></extra>"))
        fig_w.update_layout(**base_layout(260,"평균 대기시간 추이"))
        st.plotly_chart(fig_w,use_container_width=True)

    # 문의 유형
    if "대분류" in phone.columns:
        st.markdown('<div class="section-title">문의 유형 분석</div>',unsafe_allow_html=True)
        cat_df=phone.groupby("대분류").size().reset_index(name="건수").sort_values("건수",ascending=False)
        c1,c2=st.columns([1,2])
        with c1: st.plotly_chart(donut_chart(cat_df["대분류"].tolist(),cat_df["건수"].tolist(),
            title="대분류 분포"),use_container_width=True)
        with c2:
            fig5=px.bar(cat_df,x="건수",y="대분류",orientation="h",
                color_discrete_sequence=[COLORS["primary"]])
            fig5.update_layout(**base_layout(300,"대분류별 인입"))
            st.plotly_chart(fig5,use_container_width=True)

    # 히트맵
    st.markdown('<div class="section-title">인입 히트맵 (날짜 × 시간대)</div>',unsafe_allow_html=True)
    if "인입시간대" in phone.columns and "일자" in phone.columns:
        tmp=phone.copy(); tmp["일자str"]=tmp["일자"].dt.strftime("%m-%d")
        pivot=tmp.pivot_table(index="일자str",columns="인입시간대",
            values="응대여부",aggfunc="count",fill_value=0)
        st.plotly_chart(heatmap_chart(pivot,title="날짜 × 시간대 인입 히트맵"),use_container_width=True)

# ══════════════════════════════════════════════
# 전화 상담사
# ══════════════════════════════════════════════
def page_phone_agent(phone, unit, month_range):
    if phone.empty: st.info("전화 데이터가 없습니다."); return
    resp=phone[phone["응대여부"]=="응대"]
    if resp.empty: st.info("응대 데이터가 없습니다."); return

    st.markdown('<div class="section-title">상담사별 전화 성과</div>',unsafe_allow_html=True)
    ag=resp.groupby("상담사명").agg(
        응대수=("상담사명","count"),
        평균대기=("대기시간(초)","mean"),
        평균통화=("통화시간(초)","mean"),
        평균ACW=("ACW시간(초)","mean"),
        평균AHT=("AHT(초)","mean"),
    ).round(1).reset_index().sort_values("응대수",ascending=False)
    # 시간 포맷 컬럼 추가
    for c in ["평균대기","평균통화","평균ACW","평균AHT"]:
        ag[c+"_표시"]=ag[c].apply(fmt_hms)
    st.dataframe(ag[["상담사명","응대수","평균대기_표시","평균통화_표시","평균ACW_표시","평균AHT_표시"]]\
        .rename(columns={"평균대기_표시":"평균대기","평균통화_표시":"평균통화",
                          "평균ACW_표시":"평균ACW","평균AHT_표시":"평균AHT"}),
        use_container_width=True,height=400)

    if "팀명" in resp.columns:
        st.markdown('<div class="section-title">팀별 평균 AHT</div>',unsafe_allow_html=True)
        tm=resp.groupby("팀명").agg(응대수=("팀명","count"),평균AHT=("AHT(초)","mean")).round(1).reset_index()
        fig=px.bar(tm,x="팀명",y="평균AHT",color_discrete_sequence=[COLORS["primary"]])
        fig.update_layout(**base_layout(300,"팀별 평균 AHT (초)"))
        st.plotly_chart(fig,use_container_width=True)

    if "근속그룹" in resp.columns:
        st.markdown('<div class="section-title">근속그룹별 AHT</div>',unsafe_allow_html=True)
        tg=resp.groupby("근속그룹").agg(응대수=("근속그룹","count"),평균AHT=("AHT(초)","mean")).round(1).reset_index()
        fig2=px.bar(tg,x="근속그룹",y="평균AHT",color_discrete_sequence=[COLORS["info"]])
        fig2.update_layout(**base_layout(300,"근속그룹별 평균 AHT (초)"))
        st.plotly_chart(fig2,use_container_width=True)

# ══════════════════════════════════════════════
# 채팅 현황
# ══════════════════════════════════════════════
def page_chat(chat, unit, month_range, start, end):
    if chat.empty: st.info("채팅 데이터가 없습니다."); return
    resp=chat[chat["응대여부"]=="응대"]
    total=len(chat); rc=len(resp)
    rr=rc/total*100 if total else 0
    ar=resp["응답시간(초)"].mean() if not resp.empty else 0
    al=resp["리드타임(초)"].mean() if not resp.empty else 0

    c1,c2,c3,c4,c5=st.columns(5)
    for col,lbl,val,u in [
        (c1,"전체 인입",f"{total:,}","건"),(c2,"응대",f"{rc:,}","건"),
        (c3,"응대율",fmt_pct(rr),""),(c4,"평균 응답시간",fmt_hms(ar),""),
        (c5,"평균 리드타임",fmt_hms(al),""),
    ]:
        with col: st.markdown(kpi_card(lbl,val,unit=u),unsafe_allow_html=True)

    pc=get_period_col(unit); cr_s,_=get_chart_range(unit,end,month_range)
    ch_in=chat[chat[pc]>=pd.Timestamp(cr_s)].groupby(pc).size().reset_index(name="건수")
    ch_re=resp[resp[pc]>=pd.Timestamp(cr_s)].groupby(pc).size().reset_index(name="건수") if not resp.empty else pd.DataFrame(columns=[pc,"건수"])

    st.markdown('<div class="section-title">인입 / 응대 추이</div>',unsafe_allow_html=True)
    c1,c2=st.columns([2,1])
    with c1: st.plotly_chart(trend_chart({"채팅 인입":ch_in,"응대":ch_re},
        unit=unit,y_label="건수",title="채팅 인입 / 응대 추이"),use_container_width=True)
    with c2: st.plotly_chart(donut_chart(["응대","미응대"],[rc,total-rc],
        [COLORS["success"],COLORS["danger"]],title="응대 현황"),use_container_width=True)

    # 시간대별
    st.markdown('<div class="section-title">시간대별 인입 / 응대 현황</div>',unsafe_allow_html=True)
    hourly=chat.groupby("인입시간대").agg(
        인입=("인입시간대","count"),
        응대=("응대여부",lambda x:(x=="응대").sum()),
    ).reset_index()
    hourly["미응대"]=hourly["인입"]-hourly["응대"]
    hourly["응대율"]=(hourly["응대"]/hourly["인입"]*100).round(1)
    fig_h=go.Figure()
    fig_h.add_trace(go.Bar(x=hourly["인입시간대"],y=hourly["응대"],name="응대",marker_color=COLORS["chat"]))
    fig_h.add_trace(go.Bar(x=hourly["인입시간대"],y=hourly["미응대"],name="미응대",marker_color=hex_rgba(COLORS["danger"],0.7)))
    fig_h.add_trace(go.Scatter(x=hourly["인입시간대"],y=hourly["응대율"],name="응대율(%)",
        yaxis="y2",mode="lines+markers",line=dict(color=COLORS["warning"],width=2),marker=dict(size=6)))
    fig_h.update_layout(**base_layout(320,"시간대별 인입 / 응대"),barmode="stack",
        yaxis2=dict(overlaying="y",side="right",showgrid=False,ticksuffix="%",range=[0,110]))
    st.plotly_chart(fig_h,use_container_width=True)

    # 대분류별 리드타임
    if "대분류" in chat.columns and not resp.empty:
        st.markdown('<div class="section-title">대분류별 평균 리드타임</div>',unsafe_allow_html=True)
        cat_df=resp.groupby("대분류").agg(건수=("대분류","count"),
            평균리드타임=("리드타임(초)","mean")).round(1).reset_index().sort_values("건수",ascending=False)
        cat_df["평균리드타임_표시"]=cat_df["평균리드타임"].apply(fmt_hms)
        fig3=px.bar(cat_df,x="대분류",y="평균리드타임",
            color_discrete_sequence=[COLORS["chat"]],
            hover_data={"평균리드타임_표시":True,"평균리드타임":False})
        fig3.update_layout(**base_layout(300,"대분류별 평균 리드타임"))
        st.plotly_chart(fig3,use_container_width=True)

    if "플랫폼" in chat.columns:
        st.markdown('<div class="section-title">플랫폼별 분포</div>',unsafe_allow_html=True)
        plat=chat.groupby("플랫폼").size().reset_index(name="건수")
        st.plotly_chart(donut_chart(plat["플랫폼"].tolist(),plat["건수"].tolist(),
            title="플랫폼 분포"),use_container_width=True)

# ══════════════════════════════════════════════
# 채팅 상담사
# ══════════════════════════════════════════════
def page_chat_agent(chat, unit, month_range):
    if chat.empty: st.info("채팅 데이터가 없습니다."); return
    resp=chat[chat["응대여부"]=="응대"]
    if resp.empty: st.info("응대 데이터가 없습니다."); return
    st.markdown('<div class="section-title">상담사별 채팅 성과</div>',unsafe_allow_html=True)
    ag=resp.groupby("상담사명").agg(
        응대수=("상담사명","count"),
        평균응답시간=("응답시간(초)","mean"),
        평균리드타임=("리드타임(초)","mean"),
    ).round(1).reset_index().sort_values("응대수",ascending=False)
    for c in ["평균응답시간","평균리드타임"]:
        ag[c+"_표시"]=ag[c].apply(fmt_hms)
    st.dataframe(ag[["상담사명","응대수","평균응답시간_표시","평균리드타임_표시"]]\
        .rename(columns={"평균응답시간_표시":"평균응답시간","평균리드타임_표시":"평균리드타임"}),
        use_container_width=True,height=400)

    if "팀명" in resp.columns:
        st.markdown('<div class="section-title">팀별 평균 리드타임</div>',unsafe_allow_html=True)
        tm=resp.groupby("팀명").agg(응대수=("팀명","count"),평균리드타임=("리드타임(초)","mean")).round(1).reset_index()
        fig=px.bar(tm,x="팀명",y="평균리드타임",color_discrete_sequence=[COLORS["chat"]])
        fig.update_layout(**base_layout(300,"팀별 평균 리드타임 (초)"))
        st.plotly_chart(fig,use_container_width=True)

    if "근속그룹" in resp.columns:
        st.markdown('<div class="section-title">근속그룹별 리드타임</div>',unsafe_allow_html=True)
        tg=resp.groupby("근속그룹").agg(응대수=("근속그룹","count"),평균리드타임=("리드타임(초)","mean")).round(1).reset_index()
        fig2=px.bar(tg,x="근속그룹",y="평균리드타임",color_discrete_sequence=[COLORS["info"]])
        fig2.update_layout(**base_layout(300,"근속그룹별 평균 리드타임 (초)"))
        st.plotly_chart(fig2,use_container_width=True)

# ══════════════════════════════════════════════
# 게시판 현황
# ══════════════════════════════════════════════
def page_board(board, unit, month_range, start, end):
    if board.empty: st.info("게시판 데이터가 없습니다."); return
    resp=board[board["응대여부"]=="응대"]
    total=len(board); rc=len(resp)
    rr=rc/total*100 if total else 0
    al=resp["리드타임(초)"].mean() if not resp.empty else 0

    c1,c2,c3,c4=st.columns(4)
    for col,lbl,val,u in [
        (c1,"전체 티켓",f"{total:,}","건"),(c2,"응답완료",f"{rc:,}","건"),
        (c3,"응답률",fmt_pct(rr),""),(c4,"평균 리드타임",fmt_hms(al),""),
    ]:
        with col: st.markdown(kpi_card(lbl,val,unit=u),unsafe_allow_html=True)

    pc=get_period_col(unit); cr_s,_=get_chart_range(unit,end,month_range)
    bo_in=board[board[pc]>=pd.Timestamp(cr_s)].groupby(pc).size().reset_index(name="건수")
    bo_re=resp[resp[pc]>=pd.Timestamp(cr_s)].groupby(pc).size().reset_index(name="건수") if not resp.empty else pd.DataFrame(columns=[pc,"건수"])

    st.markdown('<div class="section-title">티켓 접수 / 응답 추이</div>',unsafe_allow_html=True)
    c1,c2=st.columns([2,1])
    with c1: st.plotly_chart(trend_chart({"접수":bo_in,"응답":bo_re},
        unit=unit,y_label="건수",title="게시판 접수 / 응답 추이"),use_container_width=True)
    with c2: st.plotly_chart(donut_chart(["응답","미응답"],[rc,total-rc],
        [COLORS["success"],COLORS["danger"]],title="응답 현황"),use_container_width=True)

    # 시간대별
    st.markdown('<div class="section-title">시간대별 접수 / 응답 현황</div>',unsafe_allow_html=True)
    hourly=board.groupby("인입시간대").agg(
        접수=("인입시간대","count"),
        응답=("응대여부",lambda x:(x=="응대").sum()),
    ).reset_index()
    hourly["미응답"]=hourly["접수"]-hourly["응답"]
    hourly["응답률"]=(hourly["응답"]/hourly["접수"]*100).round(1)
    fig_h=go.Figure()
    fig_h.add_trace(go.Bar(x=hourly["인입시간대"],y=hourly["응답"],name="응답",marker_color=COLORS["board"]))
    fig_h.add_trace(go.Bar(x=hourly["인입시간대"],y=hourly["미응답"],name="미응답",marker_color=hex_rgba(COLORS["danger"],0.7)))
    fig_h.add_trace(go.Scatter(x=hourly["인입시간대"],y=hourly["응답률"],name="응답률(%)",
        yaxis="y2",mode="lines+markers",line=dict(color=COLORS["warning"],width=2),marker=dict(size=6)))
    fig_h.update_layout(**base_layout(320,"시간대별 접수 / 응답"),barmode="stack",
        yaxis2=dict(overlaying="y",side="right",showgrid=False,ticksuffix="%",range=[0,110]))
    st.plotly_chart(fig_h,use_container_width=True)

    if "대분류" in board.columns:
        st.markdown('<div class="section-title">대분류별 티켓 분석</div>',unsafe_allow_html=True)
        cat_df=board.groupby("대분류").agg(건수=("대분류","count"),
            응답수=("응대여부",lambda x:(x=="응대").sum())).reset_index()
        cat_df["응답률"]=(cat_df["응답수"]/cat_df["건수"]*100).round(1)
        fig3=px.bar(cat_df,x="대분류",y="건수",color_discrete_sequence=[COLORS["board"]])
        fig3.update_layout(**base_layout(300,"대분류별 티켓 건수"))
        st.plotly_chart(fig3,use_container_width=True)

    if "플랫폼" in board.columns:
        st.markdown('<div class="section-title">플랫폼별 분포</div>',unsafe_allow_html=True)
        plat=board.groupby("플랫폼").size().reset_index(name="건수")
        st.plotly_chart(donut_chart(plat["플랫폼"].tolist(),plat["건수"].tolist(),
            title="플랫폼 분포"),use_container_width=True)

# ══════════════════════════════════════════════
# 게시판 상담사
# ══════════════════════════════════════════════
def page_board_agent(board, unit, month_range):
    if board.empty: st.info("게시판 데이터가 없습니다."); return
    resp=board[board["응대여부"]=="응대"]
    if resp.empty: st.info("응답 데이터가 없습니다."); return
    st.markdown('<div class="section-title">상담사별 게시판 성과</div>',unsafe_allow_html=True)
    ag=resp.groupby("상담사명").agg(
        응답수=("상담사명","count"),
        평균리드타임=("리드타임(초)","mean"),
    ).round(1).reset_index().sort_values("응답수",ascending=False)
    ag["평균리드타임_표시"]=ag["평균리드타임"].apply(fmt_hms)
    st.dataframe(ag[["상담사명","응답수","평균리드타임_표시"]].rename(columns={"평균리드타임_표시":"평균리드타임"}),
        use_container_width=True,height=400)

    if "팀명" in resp.columns:
        st.markdown('<div class="section-title">팀별 평균 리드타임</div>',unsafe_allow_html=True)
        tm=resp.groupby("팀명").agg(응답수=("팀명","count"),평균리드타임=("리드타임(초)","mean")).round(1).reset_index()
        fig=px.bar(tm,x="팀명",y="평균리드타임",color_discrete_sequence=[COLORS["board"]])
        fig.update_layout(**base_layout(300,"팀별 평균 리드타임 (초)"))
        st.plotly_chart(fig,use_container_width=True)

    if "근속그룹" in resp.columns:
        st.markdown('<div class="section-title">근속그룹별 리드타임</div>',unsafe_allow_html=True)
        tg=resp.groupby("근속그룹").agg(응답수=("근속그룹","count"),평균리드타임=("리드타임(초)","mean")).round(1).reset_index()
        fig2=px.bar(tg,x="근속그룹",y="평균리드타임",color_discrete_sequence=[COLORS["info"]])
        fig2.update_layout(**base_layout(300,"근속그룹별 평균 리드타임 (초)"))
        st.plotly_chart(fig2,use_container_width=True)

# ══════════════════════════════════════════════
# 상담사 종합
# ══════════════════════════════════════════════
def page_agent_total(phone, chat, board):
    st.markdown('<div class="section-title">상담사 종합 성과</div>',unsafe_allow_html=True)
    names=set()
    if not phone.empty: names.update(phone["상담사명"].unique())
    if not chat.empty:  names.update(chat["상담사명"].unique())
    if not board.empty: names.update(board["상담사명"].unique())
    names.discard("미응대")
    rows=[]
    for name in names:
        ph=phone[(phone["상담사명"]==name)&(phone["응대여부"]=="응대")] if not phone.empty else pd.DataFrame()
        ch=chat[(chat["상담사명"]==name)&(chat["응대여부"]=="응대")]    if not chat.empty  else pd.DataFrame()
        bo=board[(board["상담사명"]==name)&(board["응대여부"]=="응대")] if not board.empty else pd.DataFrame()
        rows.append({
            "상담사명":name,"전화응대":len(ph),"채팅응대":len(ch),"게시판응답":len(bo),
            "전화AHT":fmt_hms(ph["AHT(초)"].mean()) if not ph.empty else "0:00:00",
            "채팅리드타임":fmt_hms(ch["리드타임(초)"].mean()) if not ch.empty else "0:00:00",
            "게시판리드타임":fmt_hms(bo["리드타임(초)"].mean()) if not bo.empty else "0:00:00",
        })
    if not rows: st.info("데이터가 없습니다."); return
    df_ag=pd.DataFrame(rows).sort_values("전화응대",ascending=False)
    st.dataframe(df_ag,use_container_width=True,height=500)

    st.markdown('<div class="section-title">상담사별 채널 분포 (상위 10)</div>',unsafe_allow_html=True)
    top10=df_ag.head(10)
    fig=go.Figure()
    fig.add_trace(go.Bar(name="전화",x=top10["상담사명"],y=top10["전화응대"],marker_color=COLORS["phone"]))
    fig.add_trace(go.Bar(name="채팅",x=top10["상담사명"],y=top10["채팅응대"],marker_color=COLORS["chat"]))
    fig.add_trace(go.Bar(name="게시판",x=top10["상담사명"],y=top10["게시판응답"],marker_color=COLORS["board"]))
    fig.update_layout(barmode="stack",**base_layout(360,"상담사별 채널 분포"))
    st.plotly_chart(fig,use_container_width=True)

# ══════════════════════════════════════════════
# 사이드바
# ══════════════════════════════════════════════
def render_sidebar(phone_raw, chat_raw, board_raw):
    with st.sidebar:
        st.markdown("""
        <div style="padding:20px 16px 12px;border-bottom:1px solid #334155;margin-bottom:16px;">
            <div style="font-size:16px;font-weight:800;color:#f1f5f9;letter-spacing:-.5px;">CC OPS</div>
            <div style="font-size:11px;color:#64748b;margin-top:2px;">Contact Center Analytics</div>
        </div>""",unsafe_allow_html=True)

        if st.button("데이터 새로고침"):
            st.cache_data.clear(); st.rerun()

        st.markdown("<div style='height:8px'></div>",unsafe_allow_html=True)
        unit=st.radio("기간 단위",["일별","주별","월별"],horizontal=True)
        month_range=3
        if unit=="월별": month_range=st.slider("추이 범위(개월)",1,6,3)

        today=date.today()
        st.markdown('<div style="margin-top:10px;font-size:11px;color:#94a3b8;font-weight:600;">날짜 범위</div>',unsafe_allow_html=True)
        c1,c2=st.columns(2)
        with c1:
            if st.button("7일"):  st.session_state["ds"]=today-timedelta(days=6);  st.session_state["de"]=today
        with c2:
            if st.button("30일"): st.session_state["ds"]=today-timedelta(days=29); st.session_state["de"]=today
        c3,c4=st.columns(2)
        with c3:
            if st.button("이번달"): st.session_state["ds"]=today.replace(day=1); st.session_state["de"]=today
        with c4:
            if st.button("전체"):   st.session_state["ds"]=date(2024,1,1);        st.session_state["de"]=today

        date_start=st.date_input("시작일",value=st.session_state.get("ds",today-timedelta(days=29)))
        date_end  =st.date_input("종료일",value=st.session_state.get("de",today))

        all_ops=sorted(set(
            list(phone_raw["사업자명"].dropna().unique() if "사업자명" in phone_raw.columns else [])+
            list(chat_raw["사업자명"].dropna().unique()  if "사업자명" in chat_raw.columns  else [])+
            list(board_raw["사업자명"].dropna().unique() if "사업자명" in board_raw.columns else [])))
        st.markdown('<div style="margin-top:10px;font-size:11px;color:#94a3b8;font-weight:600;">사업자</div>',unsafe_allow_html=True)
        sel_ops=st.multiselect("사업자",all_ops,default=[],label_visibility="collapsed")

        all_brands=sorted(set(
            list(phone_raw["브랜드"].dropna().unique() if "브랜드" in phone_raw.columns else [])+
            list(chat_raw["브랜드"].dropna().unique()  if "브랜드" in chat_raw.columns  else [])+
            list(board_raw["브랜드"].dropna().unique() if "브랜드" in board_raw.columns else [])))
        st.markdown('<div style="margin-top:10px;font-size:11px;color:#94a3b8;font-weight:600;">브랜드</div>',unsafe_allow_html=True)
        sel_brands=st.multiselect("브랜드",all_brands,default=[],label_visibility="collapsed")

        st.markdown('<div style="height:12px;border-top:1px solid #334155;margin-top:14px;padding-top:14px;font-size:11px;color:#94a3b8;font-weight:600;">메뉴</div>',unsafe_allow_html=True)
        menu=st.session_state.get("menu","전체 현황")
        for group,items in MENU_GROUPS.items():
            for item in items:
                sel="▶ " if menu==item else "　"
                if st.button(f"{sel}{item}",key=f"m_{item}"):
                    st.session_state["menu"]=item; st.rerun()

    return unit,month_range,date_start,date_end,sel_ops,sel_brands

# ══════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════
def main():
    agent_raw=load_agent()
    phone_raw=load_phone()
    chat_raw =load_chat()
    board_raw=load_board()

    unit,month_range,date_start,date_end,sel_ops,sel_brands=render_sidebar(phone_raw,chat_raw,board_raw)

    base_d=date.today()
    phone_m=merge_agent(phone_raw,agent_raw,base_d)
    chat_m =merge_agent(chat_raw, agent_raw,base_d)
    board_m=merge_agent(board_raw,agent_raw,base_d)

    phone_f=filter_df(phone_m,date_start,date_end,sel_brands or None,sel_ops or None)
    chat_f =filter_df(chat_m, date_start,date_end,sel_brands or None,sel_ops or None)
    board_f=filter_df(board_m,date_start,date_end,sel_brands or None,sel_ops or None)

    if all(len(df)==0 for df in [phone_f,chat_f,board_f]):
        st.markdown("""
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
                    height:60vh;text-align:center;gap:12px;">
            <div style="font-size:40px;">📊</div>
            <div style="font-size:20px;font-weight:800;color:#0f172a;">데이터 연결 필요</div>
            <div style="font-size:13px;color:#64748b;">Google Sheets에 데이터를 입력하거나 필터 조건을 확인해주세요.</div>
            <div style="font-size:11px;color:#94a3b8;background:#f1f5f9;padding:8px 16px;border-radius:8px;">
                SHEET_ID 및 GID_MAP 설정을 확인하세요</div>
        </div>""",unsafe_allow_html=True)
        return

    menu=st.session_state.get("menu","전체 현황")
    if   menu=="전체 현황":     page_overview(phone_f,chat_f,board_f,unit,month_range,date_start,date_end)
    elif menu=="VOC 인입 분석": page_voc(phone_f,chat_f,board_f,unit,month_range)
    elif menu=="사업자 현황":   page_operator(phone_f,chat_f,board_f,unit,month_range)
    elif menu=="전화 현황":     page_phone(phone_f,unit,month_range,date_start,date_end)
    elif menu=="전화 상담사":   page_phone_agent(phone_f,unit,month_range)
    elif menu=="채팅 현황":     page_chat(chat_f,unit,month_range,date_start,date_end)
    elif menu=="채팅 상담사":   page_chat_agent(chat_f,unit,month_range)
    elif menu=="게시판 현황":   page_board(board_f,unit,month_range,date_start,date_end)
    elif menu=="게시판 상담사": page_board_agent(board_f,unit,month_range)
    elif menu=="상담사 종합":   page_agent_total(phone_f,chat_f,board_f)

if __name__=="__main__":
    main()
