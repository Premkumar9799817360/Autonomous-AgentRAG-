"""
AgentRAG — Autonomous
"""
import os, re, io, json, time, hashlib, warnings, traceback
import markdown as md_lib
from datetime import datetime

warnings.filterwarnings("ignore")

import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="AgentRAG — Autonomous", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&family=Fraunces:wght@700;800&display=swap');
:root{
  --bg:#f6f7f9;--bg2:#eef0f4;--bg3:#e4e7ed;--card:#ffffff;
  --border:#dde1ea;--border2:#b8bfcc;--text:#151820;--text2:#3d4556;--text3:#6b7590;--muted:#9aa2b8;
  --primary:#2563eb;--primary-l:#eff6ff;--primary-b:#bfdbfe;
  --violet:#7c3aed;--violet-l:#f5f3ff;--violet-b:#ddd6fe;
  --emerald:#059669;--emerald-l:#ecfdf5;--emerald-b:#a7f3d0;
  --amber:#d97706;--amber-l:#fffbeb;--amber-b:#fde68a;
  --rose:#e11d48;--rose-l:#fff1f2;--rose-b:#fecdd3;
  --teal:#0d9488;--teal-l:#f0fdfa;--teal-b:#99f6e4;
  --orange:#ea580c;--orange-l:#fff7ed;--orange-b:#fed7aa;
  --shadow:0 1px 3px rgba(0,0,0,0.07);--shadow-md:0 4px 12px rgba(0,0,0,0.09);
  --radius:14px;--radius-sm:9px;
}
*{box-sizing:border-box}
html,body,[class*="css"],.main,.block-container{font-family:'Inter',sans-serif!important;background:var(--bg)!important;color:var(--text)!important;}
::-webkit-scrollbar{width:4px;height:4px}::-webkit-scrollbar-thumb{background:var(--border2);border-radius:10px}
section[data-testid="stSidebar"]{background:var(--card)!important;border-right:1px solid var(--border)!important;}

/* ── SIDEBAR ── */
.sb-brand{padding:22px 18px 18px;background:linear-gradient(140deg,#0f2460 0%,#1e3a8a 50%,#312e81 100%);position:relative;overflow:hidden}
.sb-brand::after{content:'⚡';position:absolute;right:14px;top:14px;font-size:2.5rem;opacity:0.08}
.sb-logo{font-family:'Fraunces',serif;font-size:1.35rem;font-weight:800;color:white;letter-spacing:-0.5px}
.sb-sub{font-family:'JetBrains Mono',monospace;font-size:0.54rem;color:rgba(255,255,255,0.5);letter-spacing:2.5px;text-transform:uppercase;margin-top:4px}
.sb-pill{display:inline-flex;align-items:center;gap:5px;margin-top:10px;padding:3px 10px;border-radius:100px;background:rgba(255,255,255,0.1);border:1px solid rgba(255,255,255,0.18);font-size:0.58rem;color:rgba(255,255,255,0.75);font-family:'JetBrains Mono',monospace;letter-spacing:1px}
.sb-dot{width:6px;height:6px;border-radius:50%;background:#34d399;animation:pulse-g 2s infinite}
.snav{padding:13px 4px 4px;font-size:0.56rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--muted);display:flex;align-items:center;gap:6px}
.snav::after{content:'';flex:1;height:1px;background:var(--border)}
.api-ok{display:flex;align-items:center;gap:8px;padding:8px 11px;border-radius:var(--radius-sm);margin:5px 0;font-size:0.74rem;font-weight:600;background:var(--emerald-l);color:var(--emerald);border:1px solid var(--emerald-b);}
.api-err{display:flex;align-items:center;gap:8px;padding:8px 11px;border-radius:var(--radius-sm);margin:5px 0;font-size:0.74rem;font-weight:600;background:var(--rose-l);color:var(--rose);border:1px solid var(--rose-b);}
.api-idle{display:flex;align-items:center;gap:8px;padding:8px 11px;border-radius:var(--radius-sm);margin:5px 0;font-size:0.74rem;font-weight:600;background:var(--bg2);color:var(--muted);border:1px solid var(--border);}
.src-pill{display:flex;align-items:center;gap:7px;padding:7px 10px;border-radius:var(--radius-sm);background:var(--bg2);border:1px solid var(--border);margin:3px 0;font-size:0.73rem;color:var(--text2)}
.src-pill-name{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-weight:500}
.src-badge{font-size:0.54rem;padding:2px 7px;border-radius:100px;font-weight:600}
.src-badge.pdf{background:var(--rose-l);color:var(--rose)}.src-badge.csv{background:var(--emerald-l);color:var(--emerald)}.src-badge.txt{background:var(--violet-l);color:var(--violet)}

/* ── HEADER ── */
.main-header{padding:26px 0 20px;margin-bottom:20px;border-bottom:2px solid var(--border);display:flex;align-items:flex-start;justify-content:space-between;flex-wrap:wrap;gap:12px}
.main-title{font-family:'Fraunces',serif;font-size:2rem;font-weight:800;letter-spacing:-1px;color:var(--text);line-height:1;margin-bottom:5px}
.main-title span{color:var(--primary)}
.main-sub{font-family:'JetBrains Mono',monospace;font-size:0.62rem;color:var(--muted);letter-spacing:2px;text-transform:uppercase}
.hbadge{padding:4px 11px;border-radius:100px;font-size:0.66rem;font-weight:700;letter-spacing:0.5px;font-family:'JetBrains Mono',monospace;display:inline-block;margin:2px}
.hbadge.blue{background:var(--primary-l);color:var(--primary)}.hbadge.violet{background:var(--violet-l);color:var(--violet)}.hbadge.green{background:var(--emerald-l);color:var(--emerald)}.hbadge.amber{background:var(--amber-l);color:var(--amber)}.hbadge.teal{background:var(--teal-l);color:var(--teal)}

/* ── METRICS ── */
.metrics-row{display:grid;grid-template-columns:repeat(5,1fr);gap:9px;margin-bottom:18px}
.mc{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:13px 15px;box-shadow:var(--shadow);}
.mc-val{font-family:'JetBrains Mono',monospace;font-size:1.4rem;font-weight:500;line-height:1;color:var(--text)}
.mc-lbl{font-size:0.55rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted);margin-top:4px}

/* ── PIPELINE ── */
.pipe-wrap{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:14px 18px;margin-bottom:14px;box-shadow:var(--shadow)}
.pipe-title{font-family:'JetBrains Mono',monospace;font-size:0.55rem;font-weight:600;letter-spacing:2.5px;text-transform:uppercase;color:var(--muted);margin-bottom:12px;display:flex;align-items:center;gap:7px}
.pipe-steps{display:flex;align-items:center;overflow-x:auto;padding-bottom:2px;gap:0}
.step{display:flex;flex-direction:column;align-items:center;gap:4px;min-width:52px;flex:1}
.step-connector{flex:1;height:2px;min-width:6px;margin-bottom:22px;background:var(--border);}
.step-connector.done{background:linear-gradient(90deg,var(--emerald),var(--primary))}.step-connector.active{background:linear-gradient(90deg,var(--primary),var(--border));animation:flow 1.5s infinite}
.step-icon{width:30px;height:30px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px;}
.step-icon.idle{border:1.5px solid var(--border);background:var(--bg2);color:var(--muted)}.step-icon.active{border:2px solid var(--primary);background:var(--primary-l);animation:pulse-step 1.2s infinite;}.step-icon.done{border:2px solid var(--emerald);background:var(--emerald-l)}.step-icon.skip{border:1.5px dashed var(--border2);background:var(--bg3);opacity:0.5}
.step-label{font-size:0.46rem;font-weight:700;letter-spacing:0.5px;text-transform:uppercase;text-align:center;color:var(--muted);}.step-label.active{color:var(--primary)}.step-label.done{color:var(--emerald)}
.step-time{font-family:'JetBrains Mono',monospace;font-size:0.44rem;color:var(--muted);background:var(--bg2);padding:1px 4px;border-radius:3px;min-height:12px}

/* ── BANNER ── */
.pbanner{display:flex;align-items:center;gap:12px;padding:12px 16px;border-radius:var(--radius-sm);background:linear-gradient(135deg,var(--primary-l),var(--violet-l));border:1px solid var(--primary-b);margin-bottom:12px;}
.pspin{width:17px;height:17px;border:2px solid var(--primary-b);border-top-color:var(--primary);border-radius:50%;animation:spin 0.7s linear infinite;flex-shrink:0}
.ptext{font-size:0.83rem;font-weight:600;color:var(--primary)}.psub{font-size:0.63rem;color:var(--muted);margin-left:auto;font-family:'JetBrains Mono',monospace;}

/* ── CHAT MESSAGES ── */
.chat-wrap{display:flex;flex-direction:column;gap:18px}
.msg-user{display:flex;justify-content:flex-end;animation:slide-r 0.3s ease}
.msg-user .meta{font-size:0.56rem;color:var(--muted);text-align:right;margin-bottom:5px;font-family:'JetBrains Mono',monospace;}
.msg-user .bubble{max-width:65%;background:linear-gradient(135deg,var(--primary) 0%,#4f46e5 100%);border-radius:16px 16px 3px 16px;padding:12px 17px;color:white;font-size:0.89rem;line-height:1.65;box-shadow:0 4px 15px rgba(37,99,235,0.3)}
.msg-ai{animation:slide-l 0.3s ease}
.msg-ai .meta{font-size:0.56rem;color:var(--muted);margin-bottom:6px;font-family:'JetBrains Mono',monospace;display:flex;align-items:center;gap:6px;flex-wrap:wrap}
.tag{padding:2px 7px;border-radius:4px;font-size:0.54rem;font-weight:700;border:1px solid}
.tag.model{background:var(--primary-l);color:var(--primary);border-color:var(--primary-b)}.tag.safe{background:var(--emerald-l);color:var(--emerald);border-color:var(--emerald-b)}.tag.reflect{background:var(--amber-l);color:var(--amber);border-color:var(--amber-b)}.tag.qtype{background:var(--teal-l);color:var(--teal);border-color:var(--teal-b)}

/* ── AI BUBBLE ── */
.msg-ai .bubble{max-width:88%;background:var(--card);border:1px solid var(--border);border-left:3px solid var(--primary);border-radius:3px 16px 16px 16px;padding:20px 24px;font-size:0.9rem;line-height:1.85;color:var(--text);box-shadow:var(--shadow-md)}
.msg-ai .bubble h1{font-family:'Fraunces',serif!important;font-size:1.3rem!important;font-weight:800!important;color:var(--text)!important;margin:16px 0 8px!important;padding-bottom:7px;border-bottom:2px solid var(--border)}
.msg-ai .bubble h2{font-size:1.08rem!important;font-weight:700!important;color:var(--text)!important;margin:14px 0 7px!important;padding-bottom:5px;border-bottom:1px solid var(--border)}
.msg-ai .bubble h3{font-size:0.97rem!important;font-weight:700!important;color:var(--primary)!important;margin:12px 0 6px!important}
.msg-ai .bubble p{margin:9px 0!important;color:var(--text2)!important;line-height:1.85!important;font-size:0.9rem!important}
.msg-ai .bubble ul,.msg-ai .bubble ol{padding-left:22px!important;margin:8px 0!important}
.msg-ai .bubble li{margin:6px 0!important;color:var(--text2)!important;line-height:1.7!important;font-size:0.9rem!important}
.msg-ai .bubble strong{color:var(--text)!important;font-weight:700!important}
.msg-ai .bubble em{color:var(--text3)!important;font-style:italic!important}
.msg-ai .bubble code{font-family:'JetBrains Mono',monospace!important;background:var(--bg2)!important;color:var(--violet)!important;padding:2px 7px!important;border-radius:4px!important;font-size:0.83em!important;}
.msg-ai .bubble blockquote{border-left:3px solid var(--primary-b)!important;margin:10px 0!important;padding:8px 14px!important;background:var(--primary-l)!important;border-radius:0 8px 8px 0!important;color:var(--text2)!important;font-size:0.87rem!important}

/* ══════════════════════════════════════════
   COLORFUL RESPONSE TABLES
   ══════════════════════════════════════════ */
.msg-ai .bubble table{
  border-collapse:separate!important;border-spacing:0!important;
  width:100%!important;margin:18px 0!important;font-size:0.85rem!important;
  border-radius:12px!important;overflow:hidden!important;
  box-shadow:0 4px 20px rgba(37,99,235,0.13)!important;
  border:1px solid var(--primary-b)!important
}
.msg-ai .bubble thead{background:linear-gradient(135deg,#1e3a8a 0%,#2563eb 55%,#7c3aed 100%)!important}
.msg-ai .bubble thead th{
  color:#ffffff!important;font-weight:700!important;
  padding:12px 18px!important;text-align:left!important;border:none!important;
  font-size:0.78rem!important;letter-spacing:0.8px!important;text-transform:uppercase!important;
}
.msg-ai .bubble thead th:first-child{border-radius:12px 0 0 0!important}
.msg-ai .bubble thead th:last-child{border-radius:0 12px 0 0!important}
.msg-ai .bubble tbody tr:nth-child(odd){background:linear-gradient(90deg,#f0f9ff,#faf5ff)!important}
.msg-ai .bubble tbody tr:nth-child(even){background:#ffffff!important}
.msg-ai .bubble tbody tr:hover{background:linear-gradient(90deg,#dbeafe,#ede9fe)!important;transition:background 0.2s ease}
.msg-ai .bubble td{
  border:none!important;border-bottom:1px solid #e0e7ff!important;
  padding:11px 18px!important;color:var(--text2)!important;
  vertical-align:middle!important;font-weight:500!important;font-size:0.88rem!important;
}
.msg-ai .bubble td:first-child{font-weight:700!important;color:var(--primary)!important;}
.msg-ai .bubble tbody tr:last-child td{border-bottom:none!important}
.msg-ai .bubble tbody tr:last-child td:first-child{border-radius:0 0 0 12px!important}
.msg-ai .bubble tbody tr:last-child td:last-child{border-radius:0 0 12px 0!important}

/* ══════════════════════════════════════════
   SOURCE REFERENCES — color coded by source number
   ══════════════════════════════════════════ */
.sources-section{margin-top:14px;padding-top:12px;border-top:2px solid var(--border)}
.sources-title{font-size:0.58rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--muted);margin-bottom:8px;display:flex;align-items:center;gap:7px}
.sources-title::after{content:'';flex:1;height:1px;background:var(--border)}
.source-ref{display:flex;align-items:flex-start;gap:10px;padding:9px 12px;border-radius:var(--radius-sm);margin:5px 0;font-size:0.78rem;border:1px solid;line-height:1.5}
.source-ref.s1{background:linear-gradient(90deg,#eff6ff,#f8faff);border-color:#93c5fd;border-left:3px solid #2563eb}
.source-ref.s2{background:linear-gradient(90deg,#f5f3ff,#faf8ff);border-color:#c4b5fd;border-left:3px solid #7c3aed}
.source-ref.s3{background:linear-gradient(90deg,#ecfdf5,#f0fdfb);border-color:#6ee7b7;border-left:3px solid #059669}
.source-ref.s4{background:linear-gradient(90deg,#fffbeb,#fffdf5);border-color:#fcd34d;border-left:3px solid #d97706}
.source-ref.s5{background:linear-gradient(90deg,#fff1f2,#fff8f9);border-color:#fda4af;border-left:3px solid #e11d48}
.src-num{font-family:'JetBrains Mono',monospace;font-size:0.7rem;font-weight:800;width:22px;height:22px;border-radius:50%;display:flex;align-items:center;justify-content:center;flex-shrink:0;margin-top:1px}
.src-num.n1{background:#2563eb;color:white}.src-num.n2{background:#7c3aed;color:white}.src-num.n3{background:#059669;color:white}.src-num.n4{background:#d97706;color:white}.src-num.n5{background:#e11d48;color:white}
.src-info{flex:1}
.src-file{font-weight:700;color:var(--text);font-size:0.8rem}
.src-page{font-family:'JetBrains Mono',monospace;font-size:0.65rem;color:var(--muted);margin-top:2px}
.src-snippet{font-size:0.75rem;color:var(--text2);margin-top:4px;line-height:1.5;font-style:italic}
.src-sim{font-family:'JetBrains Mono',monospace;font-size:0.6rem;padding:2px 7px;border-radius:100px;font-weight:700;white-space:nowrap}

/* ══════════════════════════════════════════
   GRADE BADGES — Fixed: Excellent/Good/Average/Poor
   ══════════════════════════════════════════ */
.grade-badge{display:inline-flex;align-items:center;gap:6px;padding:4px 12px;border-radius:100px;font-size:0.65rem;font-weight:800;font-family:'JetBrains Mono',monospace;letter-spacing:0.5px;border:1.5px solid;}
.grade-excellent{background:linear-gradient(135deg,#ecfdf5,#d1fae5);color:#065f46;border-color:#6ee7b7;}
.grade-good{background:linear-gradient(135deg,#eff6ff,#dbeafe);color:#1e40af;border-color:#93c5fd;}
.grade-better{background:linear-gradient(135deg,#fffbeb,#fef3c7);color:#92400e;border-color:#fcd34d;}
.grade-bad{background:linear-gradient(135deg,#fff1f2,#fecdd3);color:#9f1239;border-color:#fda4af;}

/* ══════════════════════════════════════════
   QUALITY GUIDE PANEL
   ══════════════════════════════════════════ */
.quality-guide{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:16px 20px;margin:12px 0;box-shadow:var(--shadow)}
.quality-guide-title{font-size:0.58rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--muted);margin-bottom:12px;display:flex;align-items:center;gap:7px}
.quality-guide-title::after{content:'';flex:1;height:1px;background:var(--border)}
.quality-rows{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}
.quality-row{border-radius:10px;padding:11px 13px;border:1.5px solid}
.quality-row.excellent{background:linear-gradient(135deg,#f0fdf4,#dcfce7);border-color:#86efac}
.quality-row.good{background:linear-gradient(135deg,#eff6ff,#dbeafe);border-color:#93c5fd}
.quality-row.better{background:linear-gradient(135deg,#fffbeb,#fef9c3);border-color:#fde047}
.quality-row.bad{background:linear-gradient(135deg,#fff1f2,#ffe4e6);border-color:#fda4af}
.quality-label{font-size:0.65rem;font-weight:800;letter-spacing:1px;text-transform:uppercase;margin-bottom:3px}
.quality-label.excellent{color:#15803d}.quality-label.good{color:#1d4ed8}.quality-label.better{color:#b45309}.quality-label.bad{color:#be123c}
.quality-range{font-family:'JetBrains Mono',monospace;font-size:0.72rem;font-weight:700;margin-bottom:5px}
.quality-desc{font-size:0.68rem;color:var(--text2);line-height:1.5}

/* ── SIMILARITY BAR ── */
.sim-score-bar{display:flex;align-items:center;gap:8px;margin-top:8px}
.sim-label{font-size:0.68rem;font-weight:700;color:var(--text2);white-space:nowrap;font-family:'JetBrains Mono',monospace}
.sim-track{flex:1;height:8px;background:var(--bg3);border-radius:4px;overflow:hidden}
.sim-fill{height:100%;border-radius:4px;transition:width 0.6s ease;}
.sim-fill.excellent{background:linear-gradient(90deg,#10b981,#059669)}
.sim-fill.good{background:linear-gradient(90deg,#3b82f6,#2563eb)}
.sim-fill.average{background:linear-gradient(90deg,#f59e0b,#d97706)}
.sim-fill.poor{background:linear-gradient(90deg,#f87171,#e11d48)}
.sim-pct{font-family:'JetBrains Mono',monospace;font-size:0.68rem;font-weight:700;color:var(--text2);white-space:nowrap;min-width:38px;text-align:right}

/* ── CHUNK CARDS ── */
.chunk-card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius-sm);padding:13px 16px;margin:6px 0;font-size:0.8rem;line-height:1.72;color:var(--text2);box-shadow:var(--shadow)}
.chunk-card.table-type{border-left:3px solid var(--teal)}.chunk-card.narrative-type{border-left:3px solid var(--primary)}
.ctag{font-family:'JetBrains Mono',monospace;font-size:0.52rem;font-weight:600;padding:2px 7px;border-radius:4px;display:inline-block;margin:0 2px 4px 0}
.ctag.type{background:var(--primary-l);color:var(--primary)}.ctag.src{background:var(--bg2);color:var(--text2);border:1px solid var(--border)}.ctag.sim{background:var(--emerald-l);color:var(--emerald)}.ctag.rnk{background:var(--amber-l);color:var(--amber)}.ctag.ctype{background:var(--teal-l);color:var(--teal)}

/* ── ANSWER QUALITY BAR ── */
.answer-quality-bar{display:flex;align-items:center;gap:10px;padding:10px 16px;border-radius:var(--radius-sm);margin:8px 0;background:var(--card);border:1px solid var(--border);box-shadow:var(--shadow)}
.aq-label{font-size:0.6rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;color:var(--muted);white-space:nowrap}
.aq-divider{width:1px;height:18px;background:var(--border)}
.aq-item{display:flex;align-items:center;gap:5px;font-size:0.72rem;color:var(--text2)}
.aq-key{font-weight:700;color:var(--text3)}

/* ── MISC ── */
.sq-panel{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:17px 19px;margin-bottom:15px;box-shadow:var(--shadow)}
.sq-title{font-size:0.57rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--muted);margin-bottom:11px;}
.sq-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:7px}
.sq-item{padding:9px 13px;border-radius:var(--radius-sm);border:1px solid var(--border);background:var(--bg2);font-size:0.78rem;color:var(--text2);font-weight:500;line-height:1.4;}
.empty-state{text-align:center;padding:55px 35px;color:var(--muted)}
.empty-icon{font-size:3.2rem;margin-bottom:14px;animation:float 3s ease-in-out infinite}
.empty-title{font-family:'Fraunces',serif;font-size:1.1rem;font-weight:800;color:var(--text2);margin-bottom:7px}
.empty-sub{font-size:0.83rem;color:var(--muted);line-height:1.7;max-width:360px;margin:0 auto}
.timing-strip{display:flex;flex-wrap:wrap;gap:6px;align-items:center;padding:7px 12px;border-radius:var(--radius-sm);background:var(--bg2);border:1px solid var(--border);margin-top:8px}
.titem{font-family:'JetBrains Mono',monospace;font-size:0.59rem;color:var(--muted);display:flex;align-items:center;gap:3px}
.tkey{font-weight:600;color:var(--text2)}
.log-panel{background:#0f172a;border-radius:var(--radius-sm);padding:12px 14px;font-family:'JetBrains Mono',monospace;font-size:0.70rem;max-height:290px;overflow-y:auto;border:1px solid #1e293b}
.log-entry{padding:2px 0;border-bottom:1px solid rgba(255,255,255,0.03)}
.log-ts{color:#64748b;margin-right:7px}.log-INFO{color:#38bdf8}.log-OK{color:#34d399}.log-WARN{color:#fbbf24}.log-ERR{color:#f87171}.log-msg{color:#e2e8f0}

/* ── TABS & BUTTONS ── */
.stTabs [data-baseweb="tab-list"]{background:transparent!important;gap:2px;border-bottom:2px solid var(--border)!important}
.stTabs [data-baseweb="tab"]{font-size:0.82rem!important;font-weight:600!important;color:var(--text3)!important;background:transparent!important;border-radius:8px 8px 0 0!important;padding:9px 15px!important;}
.stTabs [aria-selected="true"]{color:var(--primary)!important;background:var(--primary-l)!important;border-bottom:2px solid var(--primary)!important}
.stButton>button{background:linear-gradient(135deg,var(--primary),var(--violet))!important;color:white!important;border:none!important;border-radius:var(--radius-sm)!important;font-weight:700!important;font-size:0.82rem!important;padding:8px 17px!important;}
.stTextInput input,.stTextArea textarea,.stChatInput textarea{background:var(--card)!important;color:var(--text)!important;border:1.5px solid var(--border)!important;border-radius:var(--radius-sm)!important;}
div[data-testid="stExpander"]{background:var(--card)!important;border:1px solid var(--border)!important;border-radius:var(--radius-sm)!important;}

@keyframes fade-in{from{opacity:0}to{opacity:1}}
@keyframes slide-l{from{opacity:0;transform:translateX(-12px)}to{opacity:1;transform:translateX(0)}}
@keyframes slide-r{from{opacity:0;transform:translateX(12px)}to{opacity:1;transform:translateX(0)}}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-7px)}}
@keyframes pulse-g{0%,100%{box-shadow:0 0 0 0 rgba(52,211,153,0.5)}50%{box-shadow:0 0 0 4px rgba(52,211,153,0)}}
@keyframes pulse-step{0%,100%{box-shadow:0 0 0 4px rgba(37,99,235,0.12)}50%{box-shadow:0 0 0 8px rgba(37,99,235,0.2)}}
@keyframes flow{0%,100%{opacity:1}50%{opacity:0.3}}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# GRADE HELPERS — Fixed labels: Excellent / Good / Average / Poor
# ══════════════════════════════════════════════════════════
def score_grade(score_0_to_1):
    """
    Returns (label, css_class, icon, description).
    Grade labels: Excellent / Good / Better / Bad — four clear, distinct tiers.
    """
    pct = score_0_to_1 * 100
    if pct >= 70:
        return (
            "Excellent", "excellent", "🟢",
            "Highly grounded in your document. The information is accurate and well-supported."
        )
    elif pct >= 50:
        return (
            "Good", "good", "🔵",
            "Mostly accurate. Key facts came from your document, with minor gaps possible."
        )
    elif pct >= 30:
        return (
            "Better", "better", "🟡",
            "Partially supported. Verify key details against the original document."
        )
    else:
        return (
            "Bad", "bad", "🔴",
            "Low document support. Try rephrasing your question or re-upload the correct file."
        )

def sim_grade(sim_0_to_1):
    """Grade for cosine similarity — returns (css_class, display_label)."""
    pct = sim_0_to_1 * 100
    if pct >= 70:   return "excellent", "🟢 Excellent"
    elif pct >= 50: return "good",      "🔵 Good"
    elif pct >= 30: return "better",    "🟡 Better"
    else:           return "bad",       "🔴 Bad"

def render_quality_guide():
    return '''
<div class="quality-guide">
  <div class="quality-guide-title">📖 Answer Quality Guide — What Do These Scores Mean?</div>
  <div class="quality-rows">
    <div class="quality-row excellent">
      <div class="quality-label excellent">🟢 Excellent</div>
      <div class="quality-range">≥ 70%</div>
      <div class="quality-desc">Answer is <strong>very accurate</strong>. Almost all information came directly from your document. You can trust this result.</div>
    </div>
    <div class="quality-row good">
      <div class="quality-label good">🔵 Good</div>
      <div class="quality-range">50 – 69%</div>
      <div class="quality-desc">Answer is <strong>mostly accurate</strong>. The main facts came from your document. Minor details may have small gaps.</div>
    </div>
    <div class="quality-row better">
      <div class="quality-label better">🟡 Better</div>
      <div class="quality-range">30 – 49%</div>
      <div class="quality-desc">Answer is <strong>partially supported</strong>. Check key numbers and facts against the original document to be sure.</div>
    </div>
    <div class="quality-row bad">
      <div class="quality-label bad">🔴 Bad</div>
      <div class="quality-range">&lt; 30%</div>
      <div class="quality-desc">Answer has <strong>low document support</strong>. Try rephrasing your question, or make sure the right document is uploaded.</div>
    </div>
  </div>
</div>'''

# ── LOGGING ──
def log_event(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    if "log_entries" not in st.session_state:
        st.session_state.log_entries = []
    st.session_state.log_entries.append({"ts": ts, "level": level, "msg": msg})
    if len(st.session_state.log_entries) > 400:
        st.session_state.log_entries = st.session_state.log_entries[-400:]

# ── SESSION STATE ──
def init_state():
    defaults = {
        "groq_api_key": "", "api_valid": None, "history": [], "processed_sources": [],
        "parent_store": {}, "child_store": [], "all_embeddings": [],
        "chroma_client": None, "collection": None,
        "collection_name": "agentrag_precision_v6",
        "embed_model_name": "all-MiniLM-L6-v2",
        "pipeline_stage": "idle", "pipeline_timing": {},
        "stats": {"total_files": 0, "total_chunks": 0, "total_parents": 0, "queries": 0},
        "eval_results": {}, "sample_questions": [], "pending_query": "",
        "log_entries": [], "conversation_memory": [],
        "guardrail_results": {}, "reflection_results": {},
        "agent_reasoning": [], "hallucination_score": None,
        "clicked_sq": set(), "last_query_type": "factual", "retry_count": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()
if not isinstance(st.session_state.get("clicked_sq"), set):
    st.session_state.clicked_sq = set()

# ── MARKDOWN RENDERER ──
def render_markdown(text):
    try:
        return md_lib.markdown(text, extensions=['tables', 'fenced_code', 'nl2br', 'sane_lists'])
    except:
        t = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        t = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', t)
        t = re.sub(r'\*(.+?)\*', r'<em>\1</em>', t)
        t = re.sub(r'`(.+?)`', r'<code>\1</code>', t)
        for lvl, tag in [("### ", "h3"), ("## ", "h2"), ("# ", "h1")]:
            t = re.sub(rf'^{re.escape(lvl)}(.+)$', rf'<{tag}>\1</{tag}>', t, flags=re.M)
        t = re.sub(r'^\- (.+)$', r'<li>\1</li>', t, flags=re.M)
        return t

# ── API VALIDATION ──
def validate_groq_key(key):
    try:
        from groq import Groq
        Groq(api_key=key).chat.completions.create(
            model="llama-3.1-8b-instant", messages=[{"role": "user", "content": "hi"}], max_tokens=3)
        log_event("Groq API validated ✓", "OK")
        return True
    except Exception as e:
        log_event(f"API invalid: {e}", "ERR")
        return False

# ── EMBEDDER ──
@st.cache_resource(show_spinner=False)
def get_embedder(model_name):
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(model_name)

def embed_texts(texts, model_name):
    return get_embedder(model_name).encode(texts, show_progress_bar=False, batch_size=32, normalize_embeddings=True)

# ── CHROMADB ──
def get_chroma_collection(name):
    import chromadb
    if st.session_state.chroma_client is None:
        st.session_state.chroma_client = chromadb.PersistentClient(path="./chroma_v6")
        log_event("ChromaDB init ✓", "OK")
    try:
        col = st.session_state.chroma_client.get_or_create_collection(name=name, metadata={"hnsw:space": "cosine"})
        st.session_state.collection = col
        return col
    except Exception as e:
        log_event(f"ChromaDB error: {e}", "ERR")
        return None

def clear_all_data():
    try:
        if st.session_state.chroma_client:
            try:
                st.session_state.chroma_client.delete_collection(st.session_state.collection_name)
            except:
                pass
        for k, v in {
            "chroma_client": None, "collection": None, "parent_store": {}, "child_store": [],
            "all_embeddings": [], "processed_sources": [], "sample_questions": [], "history": [],
            "eval_results": {}, "clicked_sq": set(), "conversation_memory": [],
            "guardrail_results": {}, "reflection_results": {}, "agent_reasoning": [],
            "hallucination_score": None, "log_entries": [], "retry_count": 0,
            "stats": {"total_files": 0, "total_chunks": 0, "total_parents": 0, "queries": 0},
            "pipeline_stage": "idle", "pipeline_timing": {}, "last_query_type": "factual"
        }.items():
            st.session_state[k] = v
        log_event("All data cleared ✓", "OK")
    except Exception as e:
        log_event(f"Clear error: {e}", "ERR")

# ══════════════════════════════════════════════════════════
# QUERY TYPE DETECTION
# ══════════════════════════════════════════════════════════
QUERY_TYPE_PATTERNS = {
    "tabular": [
        r'\b(salary|salari|pay|ctc|package|annex(ure)?|table|breakdown|component|figure|amount|inr|rs\.?|₹|lakh|gross|net|basic|benefit|pf|insurance|deduction|tax|allowance)\b',
        r'\b(show|list|detail|explain)\b.{0,30}\b(salary|pay|component|annex|benefit|figure|breakdown)\b',
        r'\b(how much|what is the).{0,20}(amount|figure|salary|pay|cost|value)\b',
    ],
    "list": [r'\b(list|enumerate|all|every|what are|types of|give me|show me all)\b'],
    "comparison": [r'\b(compar|vs\.?|versus|difference|better|worse|between|contrast)\b'],
    "factual": [r'\b(who|what|when|where|which|how|why|define|explain|name|designation)\b'],
}

def detect_query_type(query):
    q = query.lower()
    for qtype, patterns in QUERY_TYPE_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, q):
                log_event(f"Query type: {qtype}", "INFO")
                return qtype
    return "narrative"

def should_skip_compression(query_type, query):
    if query_type in ("tabular", "list", "comparison"):
        return True
    detail_words = ["detail", "full", "complete", "all", "entire", "everything", "exact", "show", "annexure", "annex"]
    return any(w in query.lower() for w in detail_words)

# ══════════════════════════════════════════════════════════
# PDF EXTRACTION — Tables as markdown, TOC detected
# ══════════════════════════════════════════════════════════
def extract_pdf_smart(file_bytes, file_name):
    try:
        import pdfplumber
        pages_content = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                page_data = {"page": page_num, "blocks": []}
                try:
                    raw_tables = page.extract_tables() or []
                    for tbl in raw_tables:
                        if not tbl or len(tbl) < 2: continue
                        clean_rows = []
                        for row in tbl:
                            if row and any(cell and len(str(cell).strip()) > 1 for cell in row):
                                clean_rows.append([str(c).strip() if c else "" for c in row])
                        if len(clean_rows) >= 2:
                            header = clean_rows[0]
                            md = "| " + " | ".join(header) + " |\n"
                            md += "| " + " | ".join(["---"] * len(header)) + " |\n"
                            for row in clean_rows[1:]:
                                while len(row) < len(header): row.append("")
                                md += "| " + " | ".join(row[:len(header)]) + " |\n"
                            page_data["blocks"].append({"content_type": "table", "text": md, "page": page_num})
                except Exception as te:
                    log_event(f"Table extract p{page_num}: {te}", "WARN")
                try:
                    text_page = page
                    try:
                        tbboxes = page.find_tables()
                        for b in (tbboxes or []):
                            text_page = text_page.outside_bbox(b.bbox)
                    except:
                        pass
                    raw_text = (text_page.extract_text(x_tolerance=2, y_tolerance=3) or "").strip()
                    if not raw_text:
                        pages_content.append(page_data); continue
                    lines = raw_text.split("\n")
                    toc_score = sum(1 for l in lines[:20]
                        if re.search(r'\.\s*\d{1,3}\s*$', l.strip()) or
                           re.search(r'^(annexure|section|clause|chapter|appendix)\s+\d', l.strip(), re.I))
                    if toc_score >= 3:
                        page_data["blocks"].append({"content_type": "toc", "text": raw_text, "page": page_num})
                    else:
                        clean = re.sub(r'\n{3,}', '\n\n', raw_text)
                        clean = re.sub(r'[ \t]{3,}', '  ', clean)
                        clean = re.sub(r'(?m)^\s*\S\s*$', '', clean).strip()
                        if clean:
                            page_data["blocks"].append({"content_type": "text", "text": clean, "page": page_num})
                except Exception as xe:
                    log_event(f"Text extract p{page_num}: {xe}", "WARN")
                pages_content.append(page_data)
        log_event(f"PDF '{file_name}': {len(pages_content)} pages ✓", "OK")
        return pages_content
    except Exception as e:
        log_event(f"PDF error: {e}", "ERR")
        return []

def is_table_text(text):
    lines = text.strip().split("\n")
    pipe_lines = sum(1 for l in lines if l.count("|") >= 2)
    kv_lines = sum(1 for l in lines if re.match(r'^.{2,40}\s*:\s*.+', l.strip()))
    return pipe_lines >= 2 or (kv_lines >= 3 and len(lines) >= 3)

def split_narrative(text, chunk_size=800, overlap=120):
    if len(text) <= chunk_size: return [text] if text.strip() else []
    for sep in ["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " "]:
        if sep not in text: continue
        parts = text.split(sep)
        chunks, current = [], ""
        for part in parts:
            candidate = (current + sep + part) if current else part
            if len(candidate) <= chunk_size:
                current = candidate
            else:
                if current.strip(): chunks.append(current.strip())
                current = part if len(part) <= chunk_size else part[:chunk_size]
        if current.strip(): chunks.append(current.strip())
        if not chunks: continue
        if overlap > 0 and len(chunks) > 1:
            ov = [chunks[0]]
            for i in range(1, len(chunks)):
                prev_tail = chunks[i-1][-overlap:] if len(chunks[i-1]) > overlap else chunks[i-1]
                ov.append(prev_tail + " " + chunks[i])
            return [c for c in ov if len(c.strip()) > 30]
        return [c for c in chunks if len(c.strip()) > 30]
    return [text[i:i+chunk_size] for i in range(0, len(text), max(1, chunk_size - overlap))]

def chunk_with_parent_child(text, file_name, source_type, page_nums, content_type="text", extra_meta=None):
    parents, children = [], []
    meta_base = {
        "source_type": source_type, "file_name": file_name,
        "content_type": content_type, "page_nums": str(page_nums),
        "char_count": len(text), "word_count": len(text.split()),
        "timestamp": datetime.now().isoformat(),
    }
    if extra_meta: meta_base.update(extra_meta)

    if content_type == "table" or is_table_text(text):
        pid = hashlib.md5(f"{file_name}_tbl_{text[:40]}".encode()).hexdigest()
        meta = {**meta_base, "content_type": "table"}
        parents.append({"id": pid, "text": text, "metadata": meta, "chunk_type": "table"})
        lines = [l for l in text.split("\n") if l.strip() and "---" not in l]
        header = lines[0] if lines else ""
        for ri, row in enumerate(lines[1:], 1):
            if not row.strip(): continue
            cid = hashlib.md5(f"{pid}_r{ri}".encode()).hexdigest()
            children.append({"id": cid, "text": f"{header}\n{row}", "parent_id": pid,
                             "metadata": {**meta, "parent_id": pid, "chunk_type": "table_row", "row_index": ri}})
        cid_full = hashlib.md5(f"{pid}_full".encode()).hexdigest()
        children.append({"id": cid_full, "text": text, "parent_id": pid,
                         "metadata": {**meta, "parent_id": pid, "chunk_type": "table_full"}})
    elif content_type == "toc":
        pid = hashlib.md5(f"{file_name}_toc_{page_nums}".encode()).hexdigest()
        meta = {**meta_base, "content_type": "toc"}
        parents.append({"id": pid, "text": text, "metadata": meta, "chunk_type": "toc"})
        children.append({"id": hashlib.md5(f"{pid}_c".encode()).hexdigest(),
                         "text": text[:600], "parent_id": pid,
                         "metadata": {**meta, "parent_id": pid, "chunk_type": "toc_child"}})
    else:
        parent_texts = split_narrative(text, 1800, 200)
        for pi, pt in enumerate(parent_texts):
            pid = hashlib.md5(f"{file_name}_{page_nums}_{pi}_{pt[:30]}".encode()).hexdigest()
            meta = {**meta_base, "parent_index": pi, "content_type": "narrative"}
            parents.append({"id": pid, "text": pt, "metadata": meta, "chunk_type": "narrative"})
            for ci, ct in enumerate(split_narrative(pt, 400, 60)):
                cid = hashlib.md5(f"{pid}_c{ci}".encode()).hexdigest()
                children.append({"id": cid, "text": ct, "parent_id": pid,
                                 "metadata": {**meta, "parent_id": pid, "chunk_type": "child", "child_index": ci}})
            sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+(?=[A-Z"\'])', pt) if len(s.strip()) > 20]
            for si, sent in enumerate(sents):
                win = " ".join(sents[max(0, si-2):min(len(sents), si+3)])
                swid = hashlib.md5(f"{pid}_sw{si}".encode()).hexdigest()
                children.append({"id": swid, "text": win, "parent_id": pid,
                                 "metadata": {**meta, "parent_id": pid, "chunk_type": "sentence_window", "sentence_index": si}})
    return parents, children

# ── FILE PROCESSORS ──
def process_pdf(file_bytes, file_name):
    pages = extract_pdf_smart(file_bytes, file_name)
    all_p, all_c = [], []
    for page_data in pages:
        for block in page_data.get("blocks", []):
            text = block["text"].strip()
            if not text or len(text) < 20: continue
            p, c = chunk_with_parent_child(text, file_name, "pdf", [block["page"]],
                content_type=block["content_type"], extra_meta={"page_start": block["page"]})
            all_p.extend(p); all_c.extend(c)
    log_event(f"PDF '{file_name}': {len(all_p)} parents, {len(all_c)} children ✓", "OK")
    return all_p, all_c

def process_csv(file_bytes, file_name):
    try:
        df = pd.read_csv(io.BytesIO(file_bytes))
        rows, cols = df.shape
        md = f"**{file_name}** — {rows} rows × {cols} columns\n\n"
        md += "| " + " | ".join(df.columns) + " |\n"
        md += "| " + " | ".join(["---"] * len(df.columns)) + " |\n"
        for _, row in df.head(200).iterrows():
            md += "| " + " | ".join([str(v) for v in row.values]) + " |\n"
        p, c = chunk_with_parent_child(md, file_name, "csv", [1], content_type="table",
            extra_meta={"total_rows": rows, "columns": str(df.columns.tolist()[:10])})
        return p, c
    except Exception as e:
        log_event(f"CSV error: {e}", "ERR")
        return [], []

def process_txt(file_bytes, file_name):
    try:
        text = file_bytes.decode("utf-8", errors="replace")
        p, c = chunk_with_parent_child(text, file_name, "txt", [1])
        return p, c
    except Exception as e:
        log_event(f"TXT error: {e}", "ERR")
        return [], []

def process_json(file_bytes, file_name):
    try:
        data = json.loads(file_bytes.decode("utf-8"))
        text = json.dumps(data, indent=2) if not isinstance(data, str) else data
        p, c = chunk_with_parent_child(text, file_name, "json", [1])
        return p, c
    except Exception as e:
        log_event(f"JSON error: {e}", "ERR")
        return [], []

def auto_process(file):
    name = file.name.lower()
    data = file.read()
    log_event(f"Processing '{file.name}' ({len(data)/1024:.1f} KB)", "INFO")
    if name.endswith(".pdf"):   return process_pdf(data, file.name)
    elif name.endswith(".csv"): return process_csv(data, file.name)
    elif name.endswith(".json"): return process_json(data, file.name)
    else:                        return process_txt(data, file.name)

def store_chunks(parent_list, child_list, model_name):
    try:
        col = get_chroma_collection(st.session_state.collection_name)
        if col is None: return False
        for p in parent_list:
            st.session_state.parent_store[p["id"]] = p
        texts = [c["text"] for c in child_list]
        embeddings = embed_texts(texts, model_name)
        ids, docs, metas, embs = [], [], [], []
        for c, emb in zip(child_list, embeddings):
            ids.append(c["id"]); docs.append(c["text"])
            metas.append({k: str(v)[:500] for k, v in c["metadata"].items()})
            embs.append(emb.tolist())
        for i in range(0, len(ids), 100):
            col.upsert(ids=ids[i:i+100], documents=docs[i:i+100],
                       metadatas=metas[i:i+100], embeddings=embs[i:i+100])
        st.session_state.child_store.extend(child_list)
        st.session_state.all_embeddings.extend(embeddings.tolist())
        log_event(f"Stored {len(ids)} vectors + {len(parent_list)} parents ✓", "OK")
        return True
    except Exception as e:
        log_event(f"Store error: {e}", "ERR")
        traceback.print_exc()
        return False

# ══════════════════════════════════════════════════════════
# RETRIEVAL — Dense + BM25 + Parent expansion
# ══════════════════════════════════════════════════════════
def retrieve_dense(query, top_k, model_name, query_type="factual"):
    try:
        col = get_chroma_collection(st.session_state.collection_name)
        if col is None or col.count() == 0: return []
        q_emb = embed_texts([query], model_name)[0].tolist()
        n = min(top_k * 4, col.count())
        results = col.query(query_embeddings=[q_emb], n_results=n,
                            include=["documents", "metadatas", "distances"])
        out = []
        for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
            cos_sim = round(1 - dist, 4)
            ctype = meta.get("content_type", "")
            boost = 0.15 if (query_type == "tabular" and ctype == "table") else \
                    0.08 if (query_type == "list" and ctype == "table") else 0.0
            out.append({"text": doc, "metadata": meta,
                        "cosine_similarity": min(1.0, cos_sim + boost),
                        "raw_cosine": cos_sim, "boost": boost, "method": "dense",
                        "parent_id": meta.get("parent_id", ""),
                        "chunk_type": meta.get("chunk_type", ""),
                        "content_type": ctype})
        return out
    except Exception as e:
        log_event(f"Dense error: {e}", "ERR")
        return []

def retrieve_bm25(query, top_k, query_type="factual"):
    try:
        children = st.session_state.child_store
        if not children: return []
        from rank_bm25 import BM25Okapi
        texts = [c["text"] for c in children]
        bm25 = BM25Okapi([t.lower().split() for t in texts])
        scores = bm25.get_scores(query.lower().split())
        max_score = float(max(scores)) if max(scores) > 0 else 1.0
        top_idx = np.argsort(scores)[::-1][:top_k * 4]
        out = []
        for idx in top_idx:
            if scores[idx] <= 0 or idx >= len(children): continue
            c = children[idx]
            norm = round(float(scores[idx]) / max_score, 4)
            ctype = c.get("metadata", {}).get("content_type", "")
            boost = 0.15 if (query_type == "tabular" and ctype == "table") else 0.0
            out.append({"text": c["text"], "metadata": c.get("metadata", {}),
                        "cosine_similarity": min(1.0, norm + boost), "raw_cosine": norm,
                        "boost": boost, "method": "bm25",
                        "parent_id": c.get("parent_id", "") or c.get("metadata", {}).get("parent_id", ""),
                        "chunk_type": c.get("metadata", {}).get("chunk_type", ""),
                        "content_type": ctype})
        return out
    except Exception as e:
        log_event(f"BM25 error: {e}", "ERR")
        return []

def fuse_and_expand(dense, bm25, alpha, top_k):
    score_map, item_map = {}, {}
    for r in dense:
        key = r.get("parent_id") or r["text"][:80]
        score = r["cosine_similarity"] * alpha
        if key not in score_map or score > score_map[key]:
            score_map[key] = score; item_map[key] = r
    for r in bm25:
        key = r.get("parent_id") or r["text"][:80]
        score = r["cosine_similarity"] * (1 - alpha)
        if key in score_map:
            score_map[key] += score
        else:
            score_map[key] = score; item_map[key] = r
    sorted_keys = sorted(score_map.keys(), key=lambda k: score_map[k], reverse=True)
    parent_store = st.session_state.parent_store
    results, seen = [], set()
    for key in sorted_keys:
        item = item_map[key]
        pid = item.get("parent_id") or item.get("metadata", {}).get("parent_id", "")
        if pid and pid not in seen and pid in parent_store:
            parent = parent_store[pid]
            seen.add(pid)
            results.append({
                "text": parent["text"], "metadata": parent["metadata"],
                "cosine_similarity": round(min(1.0, score_map[key]), 4),
                "child_text": item["text"][:200], "method": "fused+expanded",
                "parent_id": pid, "chunk_type": parent.get("chunk_type", "narrative"),
                "content_type": parent["metadata"].get("content_type", "text"),
            })
        elif not pid:
            r2 = item.copy(); r2["cosine_similarity"] = round(min(1.0, score_map[key]), 4)
            k2 = item["text"][:80]
            if k2 not in seen:
                seen.add(k2); results.append(r2)
        if len(results) >= top_k * 2: break
    log_event(f"Fused+expanded: {len(results)} unique results", "OK")
    return results

RERANK_THRESHOLD = -5.0

def rerank_with_threshold(query, results, model_name):
    try:
        from sentence_transformers import CrossEncoder
        model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-2-v2")
        pairs = [(query, r.get("child_text", r["text"])[:600]) for r in results]
        scores = model.predict(pairs)
        for r, s in zip(results, scores):
            r["rerank_score"] = round(float(s), 4)
        results.sort(key=lambda x: x.get("rerank_score", 0), reverse=True)
        max_score = max(r.get("rerank_score", -999) for r in results) if results else -999
        needs_retry = max_score < RERANK_THRESHOLD
        if needs_retry:
            log_event(f"Rerank: all below threshold ({max_score:.2f}) → retry", "WARN")
        else:
            log_event(f"Rerank: best={max_score:.3f} ✓", "OK")
        return results, needs_retry
    except Exception as e:
        log_event(f"Rerank skipped: {e}", "WARN")
        return results, False

def full_retrieval(query, top_k, model_name, alpha, query_type, use_rerank=False):
    dense = retrieve_dense(query, top_k, model_name, query_type)
    bm25 = retrieve_bm25(query, top_k, query_type)
    fused = fuse_and_expand(dense, bm25, alpha, top_k)
    if use_rerank and fused:
        fused, needs_retry = rerank_with_threshold(query, fused, model_name)
        if needs_retry:
            log_event("Retry with expanded query…", "INFO")
            for alt in [query + " details information", query.replace("explain", "show"), " ".join(query.split()[:4])]:
                d2 = retrieve_dense(alt, top_k, model_name, query_type)
                b2 = retrieve_bm25(alt, top_k, query_type)
                f2 = fuse_and_expand(d2, b2, alpha, top_k)
                if f2:
                    f2r, still_bad = rerank_with_threshold(alt, f2, model_name)
                    if not still_bad:
                        fused = f2r
                        log_event(f"Retry OK with: '{alt[:40]}'", "OK")
                        break
    final = fused[:top_k]
    if final:
        avg = np.mean([r["cosine_similarity"] for r in final])
        log_event(f"Retrieval: {len(final)} results, avg_cosine={avg:.3f} ✓", "OK")
    return final

def rewrite_query(query, gc, memory_ctx="", query_type="factual"):
    hint = {
        "tabular": "Focus on specific numbers, amounts, and structured data.",
        "list": "Expand to retrieve all items in a comprehensive list.",
        "factual": "Make the question specific and precise.",
        "narrative": "Keep the question context-aware and detailed."
    }.get(query_type, "")
    try:
        resp = gc.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "system", "content": f"Rewrite for better document retrieval. {hint} Return ONLY the rewritten question."},
                      {"role": "user", "content": query}],
            max_tokens=120, temperature=0.1)
        rw = resp.choices[0].message.content.strip()
        if rw and rw != query:
            log_event(f"Rewrite: '{query[:30]}'→'{rw[:30]}'", "INFO")
        return rw or query
    except:
        return query

def run_guardrails(query, gc):
    result = {"toxicity": {"pass": True, "score": 0.0}, "injection": {"pass": True}, "overall_safe": True, "block_reason": ""}
    for p in [r'ignore (all |previous )?(instructions?|prompts?)', r'(jailbreak|dan mode)']:
        if re.search(p, query.lower()):
            result["injection"]["pass"] = False; result["overall_safe"] = False
            result["block_reason"] = "Prompt injection detected"
            log_event("Injection detected!", "ERR")
            return result
    try:
        resp = gc.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "system", "content": 'Rate toxicity 0-1. JSON: {"score":0.0,"safe":true}'},
                      {"role": "user", "content": f"Text: {query[:400]}"}],
            max_tokens=40, temperature=0.1)
        raw = re.sub(r'^[^{]*', '', resp.choices[0].message.content.strip())
        raw = re.sub(r'[^}]*$', '', raw)
        score = float(json.loads(raw).get("score", 0))
        result["toxicity"]["score"] = round(score, 2)
        if score > 0.75:
            result["toxicity"]["pass"] = False; result["overall_safe"] = False
            result["block_reason"] = f"High toxicity ({score:.2f})"
    except:
        pass
    log_event(f"Guardrails: safe={result['overall_safe']}", "OK")
    return result

HALLUCINATED_NEGATION_PATTERNS = [
    r"there is no (information|data|detail|mention|content)",
    r"not (found|mentioned|specified|stated|available|provided) in",
    r"(no|none|nothing) (relevant|related|specific|direct)",
    r"the (document|text|source|provided).{0,30}(does not|doesn't) (contain|mention|specify)",
    r"(cannot|can't|unable to) (find|locate|determine)",
    r"no (direct|specific|explicit) (information|connection|reference)",
]

def validate_compression(original, compressed):
    for pattern in HALLUCINATED_NEGATION_PATTERNS:
        if re.search(pattern, compressed, re.IGNORECASE):
            if not re.search(pattern, original, re.IGNORECASE):
                log_event(f"Hallucinated negation blocked", "WARN")
                return original[:800].strip()
    return compressed

def smart_compress_context(query, chunks, gc, query_type):
    if should_skip_compression(query_type, query):
        return chunks, f"Skipped: {query_type}"
    compressed_chunks = []; t_before, t_after = 0, 0
    for chunk in chunks[:6]:
        ctype = chunk.get("content_type", chunk.get("chunk_type", "text"))
        if ctype == "table" or is_table_text(chunk["text"]):
            chunk["compressed"] = False
            compressed_chunks.append(chunk); continue
        text = chunk["text"]; t_before += len(text.split())
        if len(text.split()) < 80:
            chunk["compressed"] = False; compressed_chunks.append(chunk)
            t_after += len(text.split()); continue
        try:
            resp = gc.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content":
                     "Extract ONLY sentences directly relevant to the query. Rules:\n"
                     "- Return the extracted text ONLY — no commentary, no preamble\n"
                     "- NEVER write 'there is no information' — return what IS present\n"
                     "- Minimum 2-3 complete sentences\n"
                     "- If nothing seems relevant, return the first 3 sentences as-is"},
                    {"role": "user", "content": f"Query: {query}\n\nText:\n{text[:1200]}"}
                ],
                max_tokens=400, temperature=0.0)
            ct = resp.choices[0].message.content.strip()
            ct = validate_compression(text, ct)
        except:
            ct = text[:700]
        t_after += len(ct.split())
        c2 = chunk.copy(); c2["text"] = ct; c2["original_text"] = text; c2["compressed"] = True
        compressed_chunks.append(c2)
    return compressed_chunks, f"{t_before}→{t_after} words"

def self_reflect(query, answer, retrieved, gc, max_retries=2):
    ctx = " ".join([r["text"][:700] for r in retrieved[:4]])[:2500]
    rf = {"iterations": 0, "critiques": [], "final_quality": 0, "improved": False}
    current = answer
    for iteration in range(max_retries):
        try:
            cr = gc.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": 'Evaluate answer vs source. JSON: {"quality_score":0-100,"issues":["list"],"needs_improvement":true/false,"critique":"brief"}'},
                    {"role": "user", "content": f"Q: {query}\n\nSources:\n{ctx}\n\nAnswer:\n{current}"}
                ],
                max_tokens=300, temperature=0.1)
            raw = re.sub(r'^[^{]*', '', cr.choices[0].message.content.strip())
            raw = re.sub(r'[^}]*$', '', raw)
            crit = json.loads(raw)
            quality = int(crit.get("quality_score", 75))
            rf["critiques"].append({"iteration": iteration + 1, "quality": quality, "critique": crit.get("critique", "")})
            rf["iterations"] = iteration + 1; rf["final_quality"] = quality
            if quality >= 82 or not crit.get("needs_improvement", True):
                log_event(f"Reflection OK: {quality}/100", "OK"); break
            ir = gc.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "Rewrite fixing ALL issues. Be complete and accurate. Use Markdown tables for structured data."},
                    {"role": "user", "content": f"Q: {query}\n\nSources:\n{ctx}\n\nCurrent answer:\n{current}\n\nIssues: {'; '.join(crit.get('issues', []))}\n\nImproved answer:"}
                ],
                max_tokens=1600, temperature=0.1)
            current = ir.choices[0].message.content.strip()
            rf["improved"] = True
        except Exception as e:
            log_event(f"Reflection error: {e}", "WARN"); break
    return current, rf

def score_hallucination(answer, retrieved, model_name):
    try:
        if not retrieved: return {"score": 0.5, "label": "UNKNOWN", "grounded_pct": 50}
        emb = get_embedder(model_name)
        sents = [s.strip() for s in re.split(r'(?<=[.!?])\s+', answer.strip()) if len(s.strip()) > 25][:10]
        if not sents: return {"score": 0.5, "label": "UNKNOWN", "grounded_pct": 50}
        ctx = [r["text"][:600] for r in retrieved[:5]]
        ae = emb.encode(sents, normalize_embeddings=True, show_progress_bar=False)
        ce = emb.encode(ctx, normalize_embeddings=True, show_progress_bar=False)
        sent_scores = [max(float(np.dot(a, c)) for c in ce) for a in ae]
        avg = float(np.mean(sent_scores))
        label = "GROUNDED" if avg > 0.60 else "PARTIAL" if avg > 0.40 else "HALLUCINATED"
        low = [sents[i] for i, s in enumerate(sent_scores) if s < 0.35]
        log_event(f"Grounding: {label} ({avg*100:.0f}%)", "OK")
        return {"score": round(avg, 3), "grounded_pct": round(avg * 100, 1), "label": label,
                "sentence_count": len(sents), "low_sim_sentences": low[:2]}
    except Exception as e:
        log_event(f"Grounding error: {e}", "WARN")
        return {"score": 0.5, "label": "ERROR", "grounded_pct": 50}

def get_memory_ctx(max_turns=3):
    mem = st.session_state.conversation_memory
    if not mem: return ""
    return "\n".join([f"{'Human' if e['role'] == 'human' else 'AI'}: {e['content'][:300]}"
                      for e in mem[-max_turns*2:]])

def update_memory(query, answer):
    st.session_state.conversation_memory.append({"role": "human", "content": query})
    st.session_state.conversation_memory.append({"role": "assistant", "content": answer[:500]})
    if len(st.session_state.conversation_memory) > 20:
        st.session_state.conversation_memory = st.session_state.conversation_memory[-20:]

# ══════════════════════════════════════════════════════════
# GENERATE ANSWER — Clean language, correct source citation
# ══════════════════════════════════════════════════════════
def generate_answer(query, retrieved, gc, model, query_type="factual", memory_ctx=""):
    """
    Production-level answer generation.
    - Builds numbered, page-accurate source blocks from actual metadata
    - Uses a strict system prompt that enforces clean, grammatical English
    - Never mixes raw source text into the answer — always synthesizes
    - Never references pages not present in the retrieved metadata
    """
    if not retrieved:
        return (
            "## No Relevant Content Found\n\n"
            "The system could not locate relevant information for your question in the indexed document. "
            "Please try one of the following:\n"
            "- Rephrase your question using different keywords\n"
            "- Verify that the correct document has been uploaded\n"
            "- Check that the document contains information about this topic"
        )

    # ── Build source blocks with EXACT page numbers from metadata (never guess) ──
    source_blocks = []
    source_registry = []  # Track (source_number, filename, page) for citation accuracy

    for i, r in enumerate(retrieved[:6]):
        meta = r.get("metadata", {})
        fname = os.path.basename(str(meta.get("file_name") or meta.get("url", "unknown")))
        # Only use page numbers that actually exist in the metadata
        page_nums = meta.get("page_nums", "") or meta.get("page_start", "")
        ctype = r.get("content_type", r.get("chunk_type", "text"))

        page_label = f"Page {page_nums}" if page_nums else "Document"
        type_label = "[TABLE DATA]" if ctype == "table" else "[TEXT]"
        src_num = i + 1

        source_registry.append({
            "num": src_num,
            "file": fname,
            "page": page_label,
            "type": ctype,
        })

        header = f"[SOURCE {src_num} — {fname}, {page_label}, {type_label}]"
        source_blocks.append(f"{header}\n{r['text']}")

    context = "\n\n" + ("─" * 60) + "\n\n".join(source_blocks)
    memory_block = f"\n\nPrevious conversation context:\n{memory_ctx}\n" if memory_ctx else ""

    # ── Query-type specific formatting instruction ──
    format_instruction = {
        "tabular": (
            "CRITICAL: The user is asking about structured data (salary, figures, amounts, components). "
            "You MUST present ALL numerical data in a properly formatted Markdown table. "
            "Use columns appropriate to the data, for example: | Component | Amount | Notes |. "
            "Never convert table data into plain prose. Every number must appear in the table."
        ),
        "list": (
            "The user wants a complete enumeration. "
            "Include every item found across all sources. "
            "Use a numbered list and group related items under clear subheadings."
        ),
        "comparison": (
            "The user wants a comparison between two or more things. "
            "Present the comparison as a structured Markdown table with clear column headers."
        ),
        "factual": (
            "The user wants a specific, precise fact. "
            "Lead with the direct answer in the first sentence. "
            "Then provide supporting context from the source. "
            "Copy exact names, numbers, and dates precisely as they appear."
        ),
        "narrative": (
            "The user wants a thorough explanation. "
            "Structure your answer with clear ## headings for each main topic. "
            "Write in complete paragraphs — one focused idea per paragraph."
        ),
    }.get(query_type, "Provide a clear, well-structured answer using information from the sources.")

    # ── Build source citation guide for the LLM ──
    citation_guide = "\n".join([
        f"  Source {s['num']} = {s['file']}, {s['page']}"
        for s in source_registry
    ])

    system_prompt = f"""You are AgentRAG — a professional, precise document question-answering assistant.

═══════════════════════════════════════════════════════════
LANGUAGE RULES (MANDATORY — no exceptions)
═══════════════════════════════════════════════════════════
1. Write in fluent, professional English with correct grammar and punctuation.
2. Every sentence must be complete and clearly readable by a non-technical person.
3. Do NOT copy raw source text verbatim into your answer. Synthesize and present information naturally.
4. Do NOT mix multiple source excerpts together — organize information logically by topic.
5. Never write incomplete fragments, run-on sentences, or unpunctuated lists of raw facts.
6. Use proper Markdown formatting: ## headings, **bold** for key values, clean paragraph breaks.

═══════════════════════════════════════════════════════════
ACCURACY RULES (MANDATORY)
═══════════════════════════════════════════════════════════
1. Answer EXCLUSIVELY from the numbered sources provided below. Add nothing from outside.
2. Cite every claim using the source number: write [Source 1], [Source 2], etc.
3. Copy numbers, names, amounts, and dates EXACTLY as they appear — do not round or paraphrase figures.
4. If a source contains a table, reproduce it as a properly formatted Markdown table in your answer.
5. If the answer is not found in any source, write: "This information was not found in the provided document."
6. NEVER reference a page number or section that is not explicitly listed in the sources given to you.

═══════════════════════════════════════════════════════════
SOURCE CITATION MAP (use these exact references only)
═══════════════════════════════════════════════════════════
{citation_guide}

═══════════════════════════════════════════════════════════
FORMAT INSTRUCTION FOR THIS QUERY TYPE: {query_type.upper()}
═══════════════════════════════════════════════════════════
{format_instruction}

═══════════════════════════════════════════════════════════
STRUCTURE YOUR ANSWER AS FOLLOWS
═══════════════════════════════════════════════════════════
1. Start with a brief, clear direct answer to the question (1–2 sentences).
2. Provide the detailed information organized by topic under ## headings.
3. Use tables for any structured or numerical data.
4. End with a brief summary only if the answer is long and complex.

NEVER produce: bullet lists of raw quotes, mixed source fragments without structure, 
incomplete sentences, unprofessional phrasing, or text that reads like a data dump."""

    user_message = (
        f"SOURCES:\n{context}"
        f"{memory_block}"
        f"\n\n{'═'*50}\n"
        f"QUESTION: {query}\n"
        f"{'═'*50}\n\n"
        f"Write a complete, clear, professional answer using only the sources above:"
    )

    try:
        resp = gc.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=2000,
            temperature=0.05,
        )
        answer = resp.choices[0].message.content.strip()
        log_event(f"Generation OK: {len(answer.split())} words", "OK")
        return answer
    except Exception as e:
        log_event(f"Generation error: {e}", "ERR")
        return (
            f"## Generation Error\n\n"
            f"An error occurred while generating the answer: `{e}`\n\n"
            f"Please check your API key and try again."
        )

def generate_sample_questions(gc):
    parents = list(st.session_state.parent_store.values())
    if not parents: return []
    try:
        sample = " ".join([p["text"][:600] for p in parents[:6]])[:3000]
        resp = gc.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "system", "content": "Generate exactly 6 specific, clear questions a user would ask about this document. Include questions about specific numbers, names, and key facts. Return ONLY a JSON array of 6 strings."},
                      {"role": "user", "content": f"Document:\n{sample}"}],
            max_tokens=400, temperature=0.6)
        raw = re.sub(r'^[^[]*', '', resp.choices[0].message.content.strip())
        raw = re.sub(r'[^\]]*$', '', raw)
        return [q for q in json.loads(raw) if isinstance(q, str)][:6]
    except Exception as e:
        log_event(f"Sample Q error: {e}", "WARN")
        return []

# ── PIPELINE STEPS ──
STEP_DEFS = [
    ("guard", "🛡️", "Guard"), ("detect", "🔍", "Detect"), ("rewrite", "✏️", "Rewrite"),
    ("retrieve", "📡", "Retrieve"), ("rerank", "🔀", "Rerank"), ("compress", "🗜️", "Compress"),
    ("generate", "💬", "Generate"), ("reflect", "🪞", "Reflect"), ("hall", "🎯", "Ground"), ("eval", "📊", "Eval"),
]

def render_pipeline(ph, active, done, skipped, timing):
    html = ""
    for i, (key, icon, label) in enumerate(STEP_DEFS):
        if key in skipped:    cls, lc, t_str = "skip", "", "skip"
        elif key in done:
            cls, lc = "done", "done"
            t_str = f"{timing.get(key, '')}s" if key in timing else "✓"
        elif key == active:   cls, lc, t_str = "active", "active", "…"
        else:                 cls, lc, t_str = "idle", "", ""
        html += f'<div class="step"><div class="step-icon {cls}">{icon}</div><div class="step-label {lc}">{label}</div><div class="step-time">{t_str or "&nbsp;"}</div></div>'
        if i < len(STEP_DEFS) - 1:
            cc = "done" if key in done else ("active" if key == active else "")
            html += f'<div class="step-connector {cc}"></div>'
    ph.markdown(f'<div class="pipe-wrap"><div class="pipe-title">⚡ PRECISION PIPELINE</div><div class="pipe-steps">{html}</div></div>', unsafe_allow_html=True)

def evaluate_retrieval(results):
    if not results: return {}
    sims = [r.get("cosine_similarity", 0) for r in results]
    srcs = list(set(r["metadata"].get("file_name", r["metadata"].get("url", "?")) for r in results))
    ctypes = [r.get("content_type", "text") for r in results]
    return {
        "num_retrieved": len(results),
        "avg_cosine_similarity": round(float(np.mean(sims)), 4),
        "max_cosine_similarity": round(float(max(sims)), 4),
        "min_cosine_similarity": round(float(min(sims)), 4),
        "coverage_score": min(1.0, len(results) / 5),
        "source_diversity": round(len(srcs) / max(1, len(results)), 3),
        "table_chunks_retrieved": ctypes.count("table"),
        "sources": srcs,
    }

# ══════════════════════════════════════════════════════════
# MAIN PIPELINE
# ══════════════════════════════════════════════════════════
def run_rag_pipeline(query, settings, stage_ph, banner_ph):
    from groq import Groq
    gc = Groq(api_key=st.session_state.groq_api_key)
    timing, done, skipped = {}, [], []

    def set_stage(stage, msg):
        banner_ph.markdown(f'<div class="pbanner"><div class="pspin"></div><div class="ptext">{msg}</div><div class="psub">{stage.upper()}</div></div>', unsafe_allow_html=True)
        render_pipeline(stage_ph, stage, done, skipped, timing)

    def finish(stage, t, skip=False):
        if skip: skipped.append(stage)
        else: done.append(stage)
        if not skip: timing[stage] = round(t, 2)
        render_pipeline(stage_ph, "", done, skipped, timing)

    result = {"query": query, "rewritten_query": query, "retrieved": [], "answer": "",
              "eval": {}, "timing": timing, "guardrail_results": {},
              "reflection_results": {}, "hallucination_score": None,
              "query_type": "factual", "retry_happened": False}

    # 1. GUARD
    if settings.get("use_guardrails", True):
        set_stage("guard", "🛡️ Running safety checks…"); t0 = time.time()
        gr = run_guardrails(query, gc)
        result["guardrail_results"] = gr; st.session_state.guardrail_results = gr
        finish("guard", time.time() - t0)
        if not gr["overall_safe"]:
            banner_ph.empty()
            result["answer"] = f"**Safety check failed:** {gr['block_reason']}"
            return result
    else:
        finish("guard", 0, skip=True)

    # 2. DETECT
    set_stage("detect", "🔍 Detecting query type…"); t0 = time.time()
    qt = detect_query_type(query)
    result["query_type"] = qt; st.session_state.last_query_type = qt
    finish("detect", time.time() - t0)

    # 3. REWRITE
    memory_ctx = get_memory_ctx(settings.get("memory_turns", 3))
    if settings.get("rewrite_query", True):
        set_stage("rewrite", f"✏️ Rewriting query for better retrieval…"); t0 = time.time()
        result["rewritten_query"] = rewrite_query(query, gc, memory_ctx, qt)
        finish("rewrite", time.time() - t0)
    else:
        finish("rewrite", 0, skip=True)
    rq = result["rewritten_query"]

    # 4. RETRIEVE
    set_stage("retrieve", "📡 Retrieving relevant document sections…"); t0 = time.time()
    retrieved = full_retrieval(rq, settings.get("top_k", 5), settings.get("embed_model", "all-MiniLM-L6-v2"),
                               settings.get("alpha", 0.65), qt, use_rerank=False)
    finish("retrieve", time.time() - t0)

    # 5. RERANK
    if settings.get("use_rerank", True) and retrieved:
        set_stage("rerank", "🔀 Re-ranking by relevance…"); t0 = time.time()
        retrieved, needs_retry = rerank_with_threshold(rq, retrieved, settings.get("embed_model"))
        if needs_retry:
            result["retry_happened"] = True; st.session_state.retry_count += 1
        finish("rerank", time.time() - t0)
    else:
        finish("rerank", 0, skip=True)

    # 6. COMPRESS
    skip_compress = should_skip_compression(qt, query)
    if settings.get("use_compression", True) and not skip_compress and retrieved:
        set_stage("compress", "🗜️ Compressing context…"); t0 = time.time()
        retrieved, cs = smart_compress_context(rq, retrieved, gc, qt)
        finish("compress", time.time() - t0)
    else:
        finish("compress", 0, skip=True)

    result["retrieved"] = retrieved[:settings.get("top_k", 5)]

    # 7. GENERATE
    set_stage("generate", f"💬 Generating answer…"); t0 = time.time()
    answer = generate_answer(rq, result["retrieved"], gc,
                             model=settings.get("llm_model", "llama-3.3-70b-versatile"),
                             query_type=qt, memory_ctx=memory_ctx)
    finish("generate", time.time() - t0)

    # 8. REFLECT
    if settings.get("use_reflection", False) and result["retrieved"]:
        set_stage("reflect", "🪞 Self-reflection check…"); t0 = time.time()
        answer, rf = self_reflect(rq, answer, result["retrieved"], gc, max_retries=settings.get("reflection_retries", 2))
        result["reflection_results"] = rf; st.session_state.reflection_results = rf
        finish("reflect", time.time() - t0)
    else:
        finish("reflect", 0, skip=True)
    result["answer"] = answer

    # 9. GROUNDING CHECK
    if settings.get("use_hallucination_check", True) and result["retrieved"]:
        set_stage("hall", "🎯 Checking answer grounding…"); t0 = time.time()
        hs = score_hallucination(answer, result["retrieved"], settings.get("embed_model"))
        result["hallucination_score"] = hs; st.session_state.hallucination_score = hs
        finish("hall", time.time() - t0)
    else:
        finish("hall", 0, skip=True)

    # 10. EVAL
    set_stage("eval", "📊 Computing metrics…"); t0 = time.time()
    result["eval"] = evaluate_retrieval(result["retrieved"])
    finish("eval", time.time() - t0)

    update_memory(query, answer)
    banner_ph.empty()
    st.session_state.pipeline_stage = "done"
    st.session_state.pipeline_timing = timing
    st.session_state.stats["queries"] += 1
    st.session_state.eval_results = result["eval"]
    log_event(f"Pipeline done in {sum(timing.values()):.2f}s ✓", "OK")
    return result

# ══════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown('<div class="sb-brand"><div class="sb-logo">⚡ AgentRAG</div><div class="sb-sub">Autonomous</div><div class="sb-pill"><div class="sb-dot"></div>'
    '<a href="https://prembhargav.onrender.com/" target="_blank" style="text-decoration:none; color:inherit;">Prem Kumar Developer</a>'
    '</div>'
    '</div>', unsafe_allow_html=True)

    st.markdown('<div class="snav">🔑 API Key</div>', unsafe_allow_html=True)
    key_input = st.text_input("Groq API Key", type="password", value=st.session_state.groq_api_key, placeholder="gsk_…", label_visibility="collapsed")
    c1, c2 = st.columns([2, 1])
    with c1:
        if st.button("Validate Key", use_container_width=True):
            if key_input.strip():
                st.session_state.groq_api_key = key_input.strip()
                with st.spinner(""): ok = validate_groq_key(key_input.strip())
                st.session_state.api_valid = ok; st.rerun()
    with c2:
        if st.button("Clear", use_container_width=True):
            st.session_state.groq_api_key = ""; st.session_state.api_valid = None; st.rerun()
    if st.session_state.api_valid is True:   st.markdown('<div class="api-ok">✅ Connected</div>', unsafe_allow_html=True)
    elif st.session_state.api_valid is False: st.markdown('<div class="api-err">❌ Invalid Key</div>', unsafe_allow_html=True)
    else:                                     st.markdown('<div class="api-idle">⏳ Not Validated</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="snav">📁 Data Sources</div>', unsafe_allow_html=True)
    multi_files = st.file_uploader("Drop files", type=["pdf", "csv", "json", "txt", "md"], accept_multiple_files=True, label_visibility="collapsed")
    embed_model = st.selectbox("Embedding Model", ["all-MiniLM-L6-v2", "all-mpnet-base-v2", "paraphrase-multilingual-MiniLM-L12-v2"])
    st.session_state.embed_model_name = embed_model
    cp, cc = st.columns([3, 1])
    with cp: process_btn = st.button("⚡ Process & Index", use_container_width=True)
    with cc:
        if st.button("🗑️", use_container_width=True, help="Clear all data"):
            clear_all_data(); st.success("Cleared!"); st.rerun()

    if process_btn:
        if st.session_state.api_valid is not True:
            st.error("⚠️ Validate API key first.")
        else:
            items = list(multi_files or [])
            if not items:
                st.warning("No files provided.")
            else:
                all_p, all_c = [], []
                prog = st.progress(0, "Processing…")
                for fi, item in enumerate(items):
                    pct = int((fi / len(items)) * 80)
                    prog.progress(pct, f"Processing {item.name}…")
                    ps, cs = auto_process(item)
                    all_p.extend(ps); all_c.extend(cs)
                    if item.name not in st.session_state.processed_sources:
                        st.session_state.processed_sources.append(item.name)
                        st.session_state.stats["total_files"] += 1
                if all_c:
                    prog.progress(85, "Embedding & indexing…")
                    ok = store_chunks(all_p, all_c, embed_model)
                    if ok:
                        st.session_state.stats["total_chunks"] += len(all_c)
                        st.session_state.stats["total_parents"] += len(all_p)
                        prog.progress(95, "Generating sample questions…")
                        from groq import Groq
                        gq = Groq(api_key=st.session_state.groq_api_key)
                        st.session_state.sample_questions = generate_sample_questions(gq)
                        st.session_state.clicked_sq = set()
                        prog.progress(100, "Done!")
                        tbl_cnt = sum(1 for p in all_p if p.get("chunk_type") == "table")
                        st.success(f"✅ {len(all_p)} parents · {len(all_c)} children · {tbl_cnt} table chunks")
                prog.empty()

    st.markdown("---")
    st.markdown('<div class="snav">🎯 RAG Settings</div>', unsafe_allow_html=True)
    llm_model = st.selectbox("LLM (Groq)", ["llama-3.3-70b-versatile", "meta-llama/llama-4-scout-17b-16e-instruct", "qwen/qwen3-32b", "llama-3.1-8b-instant", "gemma2-9b-it"])
    top_k = st.slider("Top-K parent chunks", 3, 10, 5)
    alpha = st.slider("Dense weight (α)", 0.0, 1.0, 0.65, 0.05)

    st.markdown('<div class="snav">⚙️ Pipeline Features</div>', unsafe_allow_html=True)
    with st.expander("Configure", expanded=True):
        use_rewrite    = st.checkbox("✏️ Query Rewriting", True)
        use_rerank     = st.checkbox("🔀 Rerank + Threshold", True, help="Low scores trigger auto-retry")
        use_compression = st.checkbox("🗜️ Smart Compression", True, help="Auto-skipped for tables and lists")
        use_reflection = st.checkbox("🪞 Self-Reflection", False)
        reflection_retries = st.slider("Reflection retries", 1, 3, 2) if use_reflection else 2
        use_hall_check = st.checkbox("🎯 Grounding Check", True)
        use_guardrails = st.checkbox("🛡️ Guardrails", True)
        use_memory     = st.checkbox("🧠 Conversation Memory", True)
        memory_turns   = st.slider("Memory turns", 1, 8, 3) if use_memory else 0

    if st.session_state.processed_sources:
        st.markdown("---")
        st.markdown('<div class="snav">📚 Indexed Documents</div>', unsafe_allow_html=True)
        for src in st.session_state.processed_sources:
            ext = src.split(".")[-1].lower()
            icon = {"pdf": "📄", "csv": "📊", "json": "🔧", "txt": "📝", "md": "📝"}.get(ext, "📎")
            name = os.path.basename(src)
            pc = sum(1 for p in st.session_state.parent_store.values() if p.get("metadata", {}).get("file_name", "") == src)
            tc = sum(1 for p in st.session_state.parent_store.values() if p.get("metadata", {}).get("file_name", "") == src and p.get("chunk_type") == "table")
            st.markdown(f'<div class="src-pill"><span style="font-size:0.9rem">{icon}</span><span class="src-pill-name" title="{name}">{name[:24]}{"…" if len(name) > 24 else ""}</span><span class="src-badge {ext}">{pc}p / {tc}t</span></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# MAIN AREA
# ══════════════════════════════════════════════════════════
col_obj = get_chroma_collection(st.session_state.collection_name)
vec_count = col_obj.count() if col_obj else 0
s = st.session_state.stats
parent_count = len(st.session_state.parent_store)
tbl_count = sum(1 for p in st.session_state.parent_store.values() if p.get("chunk_type") == "table")

st.markdown(f'''
<div class="main-header">
  <div>
    <div class="main-title">Agent<span>RAG</span> <span style="font-size:1rem;color:var(--muted);font-family:\'JetBrains Mono\',monospace">Autonomous </span></div>
  </div>
  <div>
    <span class="hbadge blue">📡 Parent-Child RAG</span>
    <span class="hbadge teal">📊 Table-Aware</span>
    <span class="hbadge green">🟢 Grade Labels</span>
    <span class="hbadge amber">🎯 Grounding Check</span>
    <span class="hbadge violet">📖 Score Guide</span>
  </div>
</div>''', unsafe_allow_html=True)

st.markdown(f'''
<div class="metrics-row">
  <div class="mc"><div class="mc-val">{vec_count:,}</div><div class="mc-lbl">Child Vectors</div></div>
  <div class="mc"><div class="mc-val">{parent_count:,}</div><div class="mc-lbl">Parent Chunks</div></div>
  <div class="mc"><div class="mc-val">{tbl_count}</div><div class="mc-lbl">Table Chunks</div></div>
  <div class="mc"><div class="mc-val">{s["queries"]}</div><div class="mc-lbl">Queries Run</div></div>
  <div class="mc"><div class="mc-val">{st.session_state.retry_count}</div><div class="mc-lbl">Auto-Retries</div></div>
</div>''', unsafe_allow_html=True)

tab_chat, tab_data, tab_eval, tab_safety, tab_logs, tab_about = st.tabs([
    "💬 Chat", "📊 Data Explorer", "📈 Evaluation", "🛡️ Safety", "📋 Logs", "ℹ️ About"
])

# ══════════════════════════════════════════════════════════
# CHAT TAB
# ══════════════════════════════════════════════════════════
with tab_chat:
    pipeline_ph = st.empty()
    render_pipeline(pipeline_ph, "", "", [], st.session_state.pipeline_timing)
    banner_ph = st.empty()

    # Quality guide — always visible
    st.markdown(render_quality_guide(), unsafe_allow_html=True)

    if not st.session_state.history:
        st.markdown('''
        <div class="empty-state">
          <div class="empty-icon">⚡</div>
          <div class="empty-title">AgentRAG Autonomous</div>
          <div class="empty-sub">
            Upload a document from the sidebar, then ask any question.<br><br>
            <strong>v6 Improvements:</strong><br>
            ✅ Clean, grammatically correct answers — no mixed context<br>
            ✅ Correct source page citations — only pages actually retrieved<br>
            ✅ Grade labels: Excellent · Good · Average · Poor<br>
            ✅ Color-coded source references in every answer<br>
            ✅ All AI tools removed — focused, fast, accurate
          </div>
        </div>''', unsafe_allow_html=True)
    else:
        chat_html = '<div class="chat-wrap">'
        for i, msg in enumerate(st.session_state.history):
            if msg["role"] == "user":
                cs = msg["content"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                chat_html += f'<div class="msg-user"><div><div class="meta">YOU · {msg.get("ts","")}</div><div class="bubble">{cs}</div></div></div>'
            else:
                qt_disp = msg.get("query_type", "factual")
                qt_icon = {"tabular": "📊", "list": "📋", "factual": "🎯", "narrative": "📖", "comparison": "⚖️"}.get(qt_disp, "🔍")
                model_t = f'<span class="tag model">{msg.get("model","")}</span>'
                safe_t  = '<span class="tag safe">🛡️ safe</span>' if msg.get("guardrail_results", {}).get("overall_safe", True) else '<span class="tag" style="color:var(--rose)">⚠️ blocked</span>'
                reflect_t = '<span class="tag reflect">🪞 reflected</span>' if msg.get("reflection_results", {}).get("improved") else ""
                qt_t   = f'<span class="tag qtype">{qt_icon} {qt_disp}</span>'
                retry_t = '<span class="tag" style="background:var(--orange-l);color:var(--orange);border-color:var(--orange-b)">🔄 retried</span>' if msg.get("retry_happened") else ""

                # Grade badge for hallucination score
                hs = msg.get("hallucination_score")
                hall_t = ""
                if hs:
                    pct = hs.get("grounded_pct", 50)
                    grade_label, grade_cls, grade_icon, _ = score_grade(pct / 100)
                    hall_t = f'<span class="grade-badge grade-{grade_cls}">{grade_icon} {grade_label} · {pct:.0f}%</span>'

                # Build answer HTML
                answer_html = render_markdown(msg["content"])

                # Color-coded source references (exact pages from metadata)
                src_refs_html = ""
                if msg.get("sources"):
                    src_refs_html = '<div class="sources-section"><div class="sources-title">📎 Sources Used</div>'
                    colors = ["s1", "s2", "s3", "s4", "s5"]
                    nums = ["n1", "n2", "n3", "n4", "n5"]
                    for si, src in enumerate(msg["sources"][:5]):
                        meta = src.get("metadata", {})
                        fname = meta.get("file_name") or meta.get("url", "Unknown")
                        page  = meta.get("page_nums") or meta.get("page_start", "")
                        ctype = src.get("content_type", src.get("chunk_type", ""))
                        sim   = src.get("cosine_similarity", 0)
                        sim_pct = int(sim * 100)
                        g_cls, g_lbl = sim_grade(sim)
                        page_str = f"Page {page}" if page else "Document"
                        type_icon = "📊 Table" if ctype == "table" else "📝 Text"
                        snippet = src.get("child_text", src.get("text", ""))[:120].replace("<", "&lt;").replace(">", "&gt;")
                        sc = colors[si % len(colors)]
                        nc = nums[si % len(nums)]
                        src_refs_html += f'''
                        <div class="source-ref {sc}">
                          <div class="src-num {nc}">{si+1}</div>
                          <div class="src-info">
                            <div class="src-file">{os.path.basename(str(fname))}</div>
                            <div class="src-page">{page_str} · {type_icon}</div>
                            <div class="src-snippet">"{snippet}…"</div>
                          </div>
                          <span class="src-sim grade-badge grade-{g_cls}" style="font-size:0.58rem;padding:3px 8px">{g_lbl}</span>
                        </div>'''
                    src_refs_html += '</div>'

                chat_html += f'<div class="msg-ai"><div class="meta">AgentRAG {model_t} {qt_t} {safe_t} {reflect_t} {retry_t} {hall_t}</div><div class="bubble">{answer_html}{src_refs_html}</div></div>'

        chat_html += "</div>"
        st.markdown(chat_html, unsafe_allow_html=True)

        last_ai = next((m for m in reversed(st.session_state.history) if m["role"] == "assistant"), None)

        # Answer quality bar
        if last_ai and last_ai.get("hallucination_score"):
            hs = last_ai["hallucination_score"]
            pct = hs.get("grounded_pct", 50)
            grade_label, grade_cls, grade_icon, grade_reason = score_grade(pct / 100)
            st.markdown(f'''
            <div class="answer-quality-bar">
              <span class="aq-label">Answer Quality</span>
              <div class="aq-divider"></div>
              <span class="grade-badge grade-{grade_cls}">{grade_icon} {grade_label}</span>
              <div class="aq-divider"></div>
              <span class="aq-item"><span class="aq-key">Grounding:</span>&nbsp;{pct:.0f}% sourced from document</span>
              <div class="aq-divider"></div>
              <span class="aq-item" style="color:var(--muted);font-size:0.65rem">💡 {grade_reason}</span>
            </div>''', unsafe_allow_html=True)

        if last_ai:
            qt_val = last_ai.get("query_type", "")
            qt_msg = {
                "tabular":    "📊 Tabular query — compression skipped, table chunks boosted for better retrieval",
                "list":       "📋 List query — all items retrieved, no compression applied",
                "factual":    "🎯 Factual query — precise single-answer retrieval mode",
                "narrative":  "📖 Narrative query — context-rich paragraph retrieval",
                "comparison": "⚖️ Comparison query — both sides retrieved for balanced answer"
            }.get(qt_val, "")
            if qt_msg: st.caption(qt_msg)

        if last_ai and last_ai.get("timing"):
            t = last_ai["timing"]; total = sum(t.values())
            items_html = " · ".join(f'<span class="titem"><span class="tkey">{k}</span>&nbsp;{v}s</span>' for k, v in t.items())
            items_html += f' <span class="titem" style="margin-left:auto;color:var(--primary);font-weight:700">⏱ {total:.2f}s total</span>'
            st.markdown(f'<div class="timing-strip">{items_html}</div>', unsafe_allow_html=True)

        # Retrieved chunks detail
        if last_ai and last_ai.get("sources"):
            with st.expander(f"🔍 Retrieved Chunks — {len(last_ai['sources'])} sections with similarity scores", expanded=False):
                for r in last_ai["sources"]:
                    meta = r.get("metadata", {})
                    src  = meta.get("file_name") or meta.get("url", "?")
                    ctype = r.get("content_type", r.get("chunk_type", "narrative"))
                    sim  = r.get("cosine_similarity", 0); sim_pct = int(sim * 100)
                    page = meta.get("page_nums") or meta.get("page_start", "")
                    page_str = f" · Page {page}" if page else ""
                    rerank = r.get("rerank_score")
                    ctype_class = "table-type" if ctype == "table" else "narrative-type"
                    g_cls, g_lbl = sim_grade(sim)
                    grade_label_f, _, grade_icon_f, grade_reason_f = score_grade(sim)
                    txt_preview = r["text"][:500] + ("…" if len(r["text"]) > 500 else "")
                    child_preview = r.get("child_text", "")[:120]
                    st.markdown(f'''
                    <div class="chunk-card {ctype_class}">
                      <div style="display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin-bottom:6px">
                        <span class="ctag type">{meta.get("source_type","?").upper()}</span>
                        <span class="ctag src">{os.path.basename(str(src))[:22]}{page_str}</span>
                        <span class="ctag ctype">{"📊 TABLE" if ctype=="table" else "📝 TEXT"}</span>
                        <span class="ctag sim">Cosine {sim:.3f} ({sim_pct}%)</span>
                        {f'<span class="ctag rnk">Rerank {rerank:.2f}</span>' if rerank else ""}
                        <span class="grade-badge grade-{g_cls}" style="margin-left:auto;font-size:0.58rem;padding:3px 9px">{grade_icon_f} {grade_label_f}</span>
                      </div>
                      <div class="sim-score-bar">
                        <span class="sim-label">Similarity</span>
                        <div class="sim-track"><div class="sim-fill {g_cls}" style="width:{sim_pct}%"></div></div>
                        <span class="sim-pct">{sim_pct}%</span>
                      </div>
                      <div style="font-size:0.6rem;color:var(--muted);margin-top:3px;font-style:italic">💡 {grade_reason_f}</div>
                      <div style="margin-top:9px;font-size:0.79rem;line-height:1.7;color:var(--text2)">{txt_preview}</div>
                      {f'<div style="margin-top:6px;font-size:0.7rem;color:var(--primary);padding:4px 8px;background:var(--primary-l);border-radius:4px">🎯 Best match: &quot;{child_preview}…&quot;</div>' if child_preview else ""}
                    </div>''', unsafe_allow_html=True)

        if last_ai and last_ai.get("reflection_results", {}).get("critiques"):
            with st.expander("🪞 Self-Reflection Log"):
                rf = last_ai["reflection_results"]
                st.markdown(f"**Iterations:** {rf.get('iterations',0)} | **Quality Score:** {rf.get('final_quality',0)}/100 | **Improved:** {'✅' if rf.get('improved') else '❌'}")

    # Sample questions
    qs_to_show = [q for i, q in enumerate(st.session_state.sample_questions) if i not in st.session_state.clicked_sq]
    if qs_to_show and vec_count > 0:
        items_html = "".join(f'<div class="sq-item">→ {q.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")}</div>' for q in qs_to_show)
        st.markdown(f'<div class="sq-panel"><div class="sq-title">⚡ Suggested Questions from Your Document</div><div class="sq-grid">{items_html}</div></div>', unsafe_allow_html=True)
        sq_cols = st.columns(2)
        for i, q in enumerate(qs_to_show[:6]):
            orig_idx = next((j for j, oq in enumerate(st.session_state.sample_questions) if oq == q), i)
            with sq_cols[i % 2]:
                if st.button(q[:65] + ("…" if len(q) > 65 else ""), key=f"sq_{orig_idx}", use_container_width=True):
                    st.session_state.pending_query = q
                    if not isinstance(st.session_state.clicked_sq, set):
                        st.session_state.clicked_sq = set()
                    st.session_state.clicked_sq.add(orig_idx)
                    st.rerun()

    chat_query = st.chat_input("Ask anything about your document…")
    query = chat_query or st.session_state.get("pending_query", "")
    if st.session_state.pending_query: st.session_state.pending_query = ""
    if query:
        if st.session_state.api_valid is not True:
            st.error("⚠️ Please validate your API key first.")
        elif vec_count == 0:
            st.warning("⚠️ No documents indexed yet. Upload a file and click Process & Index.")
        else:
            st.session_state.history.append({"role": "user", "content": query, "ts": datetime.now().strftime("%H:%M")})
            settings = {
                "rewrite_query": use_rewrite, "use_rerank": use_rerank,
                "use_compression": use_compression, "use_reflection": use_reflection,
                "reflection_retries": reflection_retries, "use_hallucination_check": use_hall_check,
                "use_guardrails": use_guardrails,
                "memory_turns": memory_turns if use_memory else 0,
                "llm_model": llm_model, "embed_model": embed_model,
                "top_k": top_k, "alpha": alpha,
            }
            result = run_rag_pipeline(query, settings, pipeline_ph, banner_ph)
            st.session_state.history.append({
                "role": "assistant", "content": result["answer"], "sources": result["retrieved"],
                "model": llm_model, "eval": result["eval"], "timing": result["timing"],
                "guardrail_results": result.get("guardrail_results", {}),
                "reflection_results": result.get("reflection_results", {}),
                "hallucination_score": result.get("hallucination_score"),
                "query_type": result.get("query_type", "factual"),
                "retry_happened": result.get("retry_happened", False),
            })
            st.rerun()


# ── DATA EXPLORER TAB ──
with tab_data:
    st.markdown("### 📊 Data Explorer")
    if not st.session_state.parent_store:
        st.info("No data indexed yet.")
    else:
        parents = list(st.session_state.parent_store.values())
        children = st.session_state.child_store
        tbl_parents  = [p for p in parents if p.get("chunk_type") == "table"]
        narr_parents = [p for p in parents if p.get("chunk_type") == "narrative"]
        toc_parents  = [p for p in parents if p.get("chunk_type") == "toc"]
        st.success(f"""**Document Structure:**
- 📊 **{len(tbl_parents)} table chunks** — preserved complete, never split or compressed
- 📝 **{len(narr_parents)} narrative chunks** — parent-child split (1800/400 chars)
- 📑 **{len(toc_parents)} TOC chunks** — detected and marked low priority
- 🔢 **{len(children)} child vectors** — fine-grained retrieval units""")
        c1, c2 = st.columns(2)
        with c1:
            if tbl_parents:
                st.markdown("**📊 Table Chunks Found:**")
                for tp in tbl_parents[:5]:
                    meta = tp.get("metadata", {})
                    st.markdown(f"""<div class="chunk-card table-type"><span class="ctag type">TABLE</span> <span class="ctag src">Page {meta.get('page_nums','?')}</span> <span class="ctag sim">{meta.get('word_count',0)} words</span><div style="margin-top:6px;font-size:0.78rem;color:var(--text2)">{tp['text'][:250]}…</div></div>""", unsafe_allow_html=True)
        with c2:
            type_counts = {ct: [p.get("chunk_type") for p in parents].count(ct) for ct in set(p.get("chunk_type", "?") for p in parents)}
            st.markdown("**Chunk Type Distribution:**")
            st.dataframe(pd.DataFrame(list(type_counts.items()), columns=["Type", "Count"]), use_container_width=True, hide_index=True)


# ── EVALUATION TAB ──
with tab_eval:
    st.markdown("### 📈 Retrieval Evaluation")
    ev = st.session_state.eval_results
    if not ev:
        st.info("Run a query first to see evaluation metrics.")
    else:
        avg_sim = ev.get("avg_cosine_similarity", 0)
        grade_label, grade_cls, grade_icon, grade_reason = score_grade(avg_sim)
        st.markdown(f'''
        <div style="padding:16px 20px;border-radius:12px;background:var(--card);border:1px solid var(--border);margin-bottom:16px;box-shadow:var(--shadow)">
          <div style="font-size:0.55rem;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:var(--muted);margin-bottom:10px">Overall Retrieval Quality</div>
          <div style="display:flex;align-items:center;gap:14px;margin-bottom:8px">
            <span class="grade-badge grade-{grade_cls}" style="font-size:0.78rem;padding:6px 16px">{grade_icon} {grade_label}</span>
            <span style="font-size:0.85rem;color:var(--text2)">{avg_sim*100:.1f}% average cosine similarity across retrieved chunks</span>
          </div>
          <div style="font-size:0.7rem;color:var(--muted);font-style:italic">💡 {grade_reason}</div>
        </div>''', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""<div class="metrics-row" style="grid-template-columns:repeat(2,1fr)">
              <div class="mc"><div class="mc-val">{ev.get('num_retrieved',0)}</div><div class="mc-lbl">Chunks Retrieved</div></div>
              <div class="mc"><div class="mc-val">{ev.get('avg_cosine_similarity',0)*100:.0f}%</div><div class="mc-lbl">Avg Similarity</div></div>
              <div class="mc"><div class="mc-val">{ev.get('max_cosine_similarity',0)*100:.0f}%</div><div class="mc-lbl">Best Match</div></div>
              <div class="mc"><div class="mc-val">{ev.get('table_chunks_retrieved',0)}</div><div class="mc-lbl">Tables Found</div></div>
            </div>""", unsafe_allow_html=True)
        with c2:
            hs = st.session_state.hallucination_score
            metrics = {"Avg Similarity": ev.get("avg_cosine_similarity", 0),
                       "Best Match": ev.get("max_cosine_similarity", 0),
                       "Coverage": ev.get("coverage_score", 0)}
            if hs: metrics["Answer Grounding"] = hs.get("score", 0)
            for name, val in metrics.items():
                pct = int(val * 100)
                g_cls, _ = sim_grade(val)
                color = {"excellent": "var(--emerald)", "good": "var(--primary)", "better": "var(--amber)", "bad": "var(--rose)"}.get(g_cls, "var(--muted)")
                gl, _, gi, _ = score_grade(val)
                st.markdown(f'<div style="display:flex;justify-content:space-between;align-items:center;font-size:0.72rem;font-weight:600;color:var(--text2);margin-bottom:4px"><span>{name}</span><span style="display:flex;align-items:center;gap:6px"><span class="grade-badge grade-{g_cls}" style="font-size:0.52rem;padding:2px 7px">{gi} {gl}</span><span style="font-family:\'JetBrains Mono\',monospace;color:var(--muted)">{pct}%</span></span></div><div style="height:7px;background:var(--bg2);border-radius:4px;overflow:hidden;margin-bottom:10px"><div style="width:{pct}%;height:100%;border-radius:4px;background:{color}"></div></div>', unsafe_allow_html=True)
    if len(st.session_state.history) > 1:
        st.markdown("### Query History")
        rows = []
        for i, msg in enumerate(st.session_state.history):
            if msg["role"] == "assistant" and msg.get("eval"):
                e = msg["eval"]; q = st.session_state.history[i-1]["content"][:55] if i > 0 else "?"
                hs2 = msg.get("hallucination_score")
                avg_s = e.get("avg_cosine_similarity", 0)
                gl, _, gi, _ = score_grade(avg_s)
                rows.append({
                    "Query": q, "Type": msg.get("query_type", "?"),
                    "Retrieved": e.get("num_retrieved", 0),
                    "Avg Similarity": f"{avg_s*100:.0f}%",
                    "Grade": f"{gi} {gl}",
                    "Tables": e.get("table_chunks_retrieved", 0),
                    "Grounding": f"{hs2.get('label','')} {hs2.get('grounded_pct',0):.0f}%" if hs2 else "—",
                    "Retried": "🔄" if msg.get("retry_happened") else "—",
                    "Safe": "✅" if msg.get("guardrail_results", {}).get("overall_safe", True) else "❌",
                })
        if rows: st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# ── SAFETY TAB ──
with tab_safety:
    st.markdown("### 🛡️ Safety & Grounding Dashboard")
    st.markdown(render_quality_guide(), unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        gr = st.session_state.guardrail_results
        if gr:
            st.markdown("**Last Query Safety Check:**")
            safe = gr.get("overall_safe", True)
            st.markdown(f'<div style="padding:10px 14px;border-radius:8px;background:{"var(--emerald-l)" if safe else "var(--rose-l)"};border:1px solid {"var(--emerald-b)" if safe else "var(--rose-b)"};color:{"var(--emerald)" if safe else "var(--rose)"};font-weight:700">{"✅ Query is safe to process" if safe else "⚠️ Blocked: " + gr.get("block_reason","")}</div>', unsafe_allow_html=True)
            st.markdown(f"Toxicity score: `{gr.get('toxicity',{}).get('score',0):.2f}`")
        else:
            st.info("No query run yet.")
    with c2:
        hs = st.session_state.hallucination_score
        if hs:
            st.markdown("**Last Answer Grounding:**")
            pct = hs.get("grounded_pct", 50)
            grade_label, grade_cls, grade_icon, grade_reason = score_grade(pct / 100)
            st.markdown(f'<span class="grade-badge grade-{grade_cls}" style="font-size:0.78rem;padding:7px 16px">{grade_icon} {grade_label} — {pct:.0f}% grounded</span>', unsafe_allow_html=True)
            st.markdown(f"- Sentences analyzed: `{hs.get('sentence_count',0)}`")
            st.markdown(f"- Average similarity: `{hs.get('score',0):.3f}`")
            st.info(f"💡 **What this means:** {grade_reason}")
            if hs.get("low_sim_sentences"):
                st.warning("Sentences with low document support (may need verification):")
                for s in hs["low_sim_sentences"]:
                    st.markdown(f"• *{s[:100]}…*")
        else:
            st.info("Run a query with Grounding Check enabled.")


# ── LOGS TAB ──
with tab_logs:
    st.markdown("### 📋 System Logs")
    logs = st.session_state.log_entries
    if not logs:
        st.info("No log entries yet.")
    else:
        lc1, lc2 = st.columns([3, 1])
        with lc2:
            filter_level = st.selectbox("Filter", ["ALL", "INFO", "OK", "WARN", "ERR"], label_visibility="collapsed")
        filtered = logs if filter_level == "ALL" else [l for l in logs if l["level"] == filter_level]
        log_html = '<div class="log-panel">'
        for entry in reversed(filtered[-150:]):
            msg = entry["msg"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            log_html += f'<div class="log-entry"><span class="log-ts">{entry["ts"]}</span><span class="log-{entry["level"]}">[{entry["level"]}]</span> <span class="log-msg">{msg}</span></div>'
        log_html += "</div>"
        st.markdown(log_html, unsafe_allow_html=True)
        st.caption(f"{len(filtered)} entries shown (total: {len(logs)})")


# ── ABOUT TAB ──
with tab_about:
    st.markdown("### ℹ️ About Autonomous AgentRAG")
    st.markdown(
        """
        <div class="info-grid">
          <div class="info-card"><div class="info-card-icon">🛡️</div>
            <div class="info-card-title">Safety Guardrails</div>
            <div class="info-card-desc">Three-layer safety before every query.</div>
            <ul class="feature-list"><li>LLM toxicity scoring (0.0–1.0)</li><li>PII regex detection</li><li>Prompt injection patterns</li><li>Auto-block with explanation</li></ul></div>
          <div class="info-card"><div class="info-card-icon">🔗</div>
            <div class="info-card-title">Multi-hop Retrieval</div>
            <div class="info-card-desc">Decomposes complex questions into sub-queries.</div>
            <ul class="feature-list"><li>LLM query decomposition</li><li>Independent retrieval per hop</li><li>RRF deduplication &amp; merge</li><li>Best for multi-step reasoning</li></ul></div>
          <div class="info-card"><div class="info-card-icon">🪞</div>
            <div class="info-card-title">Self-Reflection</div>
            <div class="info-card-desc">LLM critiques and iteratively improves its answer.</div>
            <ul class="feature-list"><li>Quality scoring 0–100</li><li>Configurable retries 1–3</li><li>Auto-improve if score &lt; 80</li><li>Full iteration log</li></ul></div>
          <div class="info-card"><div class="info-card-icon">🎯</div>
            <div class="info-card-title">Hallucination Scoring</div>
            <div class="info-card-desc">Embedding cosine similarity per sentence.</div>
            <ul class="feature-list"><li>GROUNDED / PARTIAL / HALLUCINATED</li><li>Per-sentence analysis</li><li>No extra LLM call needed</li><li>Flags low-grounded sentences</li></ul></div>
          <div class="info-card"><div class="info-card-icon">🤖</div>
            <div class="info-card-title">Agent Reasoning</div>
            <div class="info-card-desc">Step-by-step chain-of-thought before answer.</div>
            <ul class="feature-list"><li>ANALYZE → RETRIEVE → SYNTHESIZE → CONCLUDE</li><li>3–5 explicit steps</li><li>Injected into generation prompt</li></ul></div>
          <div class="info-card"><div class="info-card-icon">🧠</div>
            <div class="info-card-title">Conversation Memory</div>
            <div class="info-card-desc">Sliding window memory for follow-up context.</div>
            <ul class="feature-list"><li>Configurable window 1–10 turns</li><li>Injected into every prompt</li><li>Clearable via Safety tab</li></ul></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Pipeline Architecture**")
        st.code(
            "Query\n"
            "  ↓ 🛡️  Guardrails (Toxicity · PII · Injection)\n"
            "  ↓ ✏️  Query Rewriter\n"
            "  ↓ 🔍  Retrieval (Hybrid RRF / Semantic / BM25)\n"
            "  ↓ 🔀  Cross-encoder Reranker (optional)\n"
            "  ↓ 🗜️  Context Compressor (optional)\n"
            "  ↓ 🤖  Agent Reasoning Loop (optional)\n"
            "  ↓ 🛠️  AI Tools (Web · Fact · Expand)\n"
            "  ↓ 💬  Answer Generation (Groq LLM + Memory)\n"
            "  ↓ 🪞  Self-Reflection & Correction (optional)\n"
            "  ↓ 🎯  Hallucination Scoring (optional)\n"
            "  ↓ 📊  Retrieval Evaluation\n"
            "  ↓ 🧠  Update Conversation Memory\n"
            "  ↓ Formatted Markdown Response",
            language="",
        )
    with col2:
        st.markdown("**Quick Start**")
        st.markdown(
            "1. Enter your **Groq API key** → **Validate Key**\n"
            "2. Upload PDFs, CSVs, or paste a URL\n"
            "3. Click **⚡ Process & Index**\n"
            "4. Toggle pipeline features in sidebar\n"
            "5. Ask in the Chat tab\n\n"
            "**Free Groq models:** llama-3.3-70b-versatile, gemma2-9b-it\n\n"
            "**Recommended combos:**\n"
            "- Research: Multi-hop + Context Expander + Hallucination Scoring\n"
            "- Critical docs: Guardrails + Fact Checker + Self-Reflection\n"
            "- Conversation: Memory + Agent Reasoning + Query Rewriting"
        )