#!/usr/bin/env python3
"""
AI Error Tutor - Streamlit GUI
A friendly Python error message rewriter using AI
"""

import streamlit as st
import config
from src.pipeline import AIErrorTutor
from codecarbon import EmissionsTracker

st.set_page_config(
    page_title="AI Error Tutor",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

DARK = st.session_state.dark_mode

# Colour tokens - Flat/Minimalist style (No gradients)
if DARK:
    BG_APP          = "#0a0a0a"
    BG_CODE         = "#111111"
    BORDER_CODE     = "#262626"
    TEXT_PRIMARY    = "#f5f5f5"
    TEXT_SECONDARY  = "#a3a3a3"
    TEXT_MUTED      = "#737373"
    SURFACE         = "#141414"
    SURFACE_HOVER   = "#1f1f1f"
    BORDER_UI       = "#262626"
    BORDER_STRONG   = "#404040"
    LINE_NUM_COL    = "#525252"
    INPUT_BG        = "#111111"
    INPUT_BORDER    = "#262626"
    INPUT_COLOR     = "#38bdf8"
    ACCENT_ORANGE   = "#f97316"
    ACCENT_GREEN    = "#22c55e"
    ACCENT_PINK     = "#ec4899"
    ACCENT_RED      = "#ef4444"
    BTN_BG          = "#f5f5f5"
    BTN_TXT         = "#0a0a0a"
    BTN_HOVER       = "#d4d4d4"
    PILL_BG         = "#171717"
    PILL_BORD       = "#262626"
    PILL_COLOR      = "#a3a3a3"
else:
    BG_APP          = "#fdfdfd"
    BG_CODE         = "#f5f5f5"
    BORDER_CODE     = "#e5e5e5"
    TEXT_PRIMARY    = "#171717"
    TEXT_SECONDARY  = "#525252"
    TEXT_MUTED      = "#a3a3a3"
    SURFACE         = "#ffffff"
    SURFACE_HOVER   = "#f9f9f9"
    BORDER_UI       = "#e5e5e5"
    BORDER_STRONG   = "#d4d4d4"
    LINE_NUM_COL    = "#a3a3a3"
    INPUT_BG        = "#ffffff"
    INPUT_BORDER    = "#d4d4d4"
    INPUT_COLOR     = "#0284c7"
    ACCENT_ORANGE   = "#ea580c"
    ACCENT_GREEN    = "#16a34a"
    ACCENT_PINK     = "#db2777"
    ACCENT_RED      = "#dc2626"
    BTN_BG          = "#171717"
    BTN_TXT         = "#ffffff"
    BTN_HOVER       = "#404040"
    PILL_BG         = "#f5f5f5"
    PILL_BORD       = "#e5e5e5"
    PILL_COLOR      = "#525252"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Reset & base layout */
    .stApp {{
        background-color: {BG_APP};
        color: {TEXT_PRIMARY};
        font-family: 'Inter', sans-serif;
    }}
    .css-1d391kg {{ background-color: {SURFACE}; border-right: 1px solid {BORDER_UI}; }} /* Sidebar */
    .stSidebar {{ background-color: {SURFACE}; border-right: 1px solid {BORDER_UI}; }}
    [data-testid="stSidebarNav"] {{ display: none; }}
    footer {{ visibility: hidden; }}

    /* Typography */
    h1, h2, h3, h4 {{
        color: {TEXT_PRIMARY} !important;
        font-weight: 600 !important;
        letter-spacing: -0.5px;
    }}
    p, li, span {{ color: {TEXT_SECONDARY}; }}

    /* Controls */
    button[kind="secondary"] {{
        background-color: {SURFACE} !important;
        border: 1px solid {BORDER_STRONG} !important;
        color: {TEXT_PRIMARY} !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        transition: background-color 0.2s, border-color 0.2s !important;
    }}
    button[kind="secondary"]:hover {{
        background-color: {SURFACE_HOVER} !important;
        border-color: {TEXT_MUTED} !important;
    }}

    button[kind="primary"] {{
        background-color: {BTN_BG} !important;
        border: 1px solid {BTN_BG} !important;
        color: {BTN_TXT} !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        transition: background-color 0.2s !important;
    }}
    button[kind="primary"]:hover {{
        background-color: {BTN_HOVER} !important;
        border: 1px solid {BTN_HOVER} !important;
        color: {BTN_TXT} !important;
    }}

    /* Inputs */
    .stTextArea textarea {{
        background-color: {INPUT_BG} !important;
        color: {INPUT_COLOR} !important;
        border: 1px solid {INPUT_BORDER} !important;
        border-radius: 8px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 14px !important;
        line-height: 1.6 !important;
        caret-color: {ACCENT_ORANGE};
    }}
    .stTextArea textarea:focus {{
        border-color: {TEXT_PRIMARY} !important;
        box-shadow: none !important;
        outline: none !important;
    }}
    .stSelectbox > div > div {{
        background: {INPUT_BG} !important;
        border: 1px solid {INPUT_BORDER} !important;
        border-radius: 6px !important;
        color: {TEXT_PRIMARY} !important;
    }}

    /* Cards */
    .result-card {{
        background-color: {SURFACE};
        border: 1px solid {BORDER_UI};
        border-left-width: 4px;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 16px;
    }}
    .card-explain {{ border-left-color: {ACCENT_ORANGE}; }}
    .card-fix     {{ border-left-color: {ACCENT_GREEN}; }}
    .card-similar {{ border-left-color: {ACCENT_PINK}; }}
    .card-security{{ border-left-color: {ACCENT_RED}; }}

    .card-title {{
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .card-title.orange {{ color: {ACCENT_ORANGE}; }}
    .card-title.green  {{ color: {ACCENT_GREEN}; }}
    .card-title.pink   {{ color: {ACCENT_PINK}; }}
    .card-title.red    {{ color: {ACCENT_RED}; }}
    .card-body {{ font-size: 14px; line-height: 1.6; color: {TEXT_PRIMARY}; }}

    /* Status banners */
    .status-banner {{
        padding: 14px 18px;
        border-radius: 6px;
        font-size: 14px;
        font-weight: 600;
        margin-bottom: 16px;
        border: 1px solid {BORDER_UI};
    }}

    /* Code Block */
    .code-viewer {{
        background-color: {BG_CODE};
        border: 1px solid {BORDER_CODE};
        border-radius: 8px;
        overflow-x: auto;
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        line-height: 1.6;
        padding: 12px 0;
        margin-bottom: 16px;
    }}
    .code-line {{ display: block; padding: 2px 20px; white-space: pre; }}
    .code-line-error {{ background-color: rgba(239, 68, 68, 0.15); border-left: 3px solid {ACCENT_RED}; }}
    .line-num {{
        color: {LINE_NUM_COL};
        display: inline-block;
        min-width: 32px;
        text-align: right;
        margin-right: 16px;
        border-right: 1px solid {BORDER_CODE};
        padding-right: 12px;
        user-select: none;
    }}
    .line-code {{ color: {TEXT_PRIMARY}; }}
    .code-line-error .line-code {{ color: {ACCENT_RED}; }}

    .pill {{
        display: inline-block; padding: 2px 8px; border-radius: 4px;
        font-family: 'JetBrains Mono', monospace; font-size: 12px;
        background-color: {PILL_BG}; color: {TEXT_PRIMARY}; border: 1px solid {PILL_BORD};
        margin: 0 4px;
    }}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

@st.cache_resource
def load_tutor():
    try:
        return AIErrorTutor(model_path=config.MODEL_SAVE_PATH, use_ai=True)
    except Exception:
        return AIErrorTutor(use_ai=False)


def render_code_viewer(code: str, error_line=None) -> str:
    lines = code.split("\n")
    html_lines = []
    for i, line in enumerate(lines, 1):
        esc = (
            line
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        ) or " "
        is_err = (i == error_line)
        css = "code-line code-line-error" if is_err else "code-line"
        html_lines.append(
            f'<span class="{css}">'
            f'<span class="line-num">{i}</span>'
            f'<span class="line-code">{esc}</span>'
            f'</span>'
        )
    return f'<div class="code-viewer">{"".join(html_lines)}</div>'


tutor = load_tutor()

DEMO_CODES = {
    "NameError — typo in function name":   'print("Testing NameError")\nprnt("Hello World")',
    "TypeError — adding string and int":   'age = 25\nmessage = "Your age is: " + age\nprint(message)',
    "SyntaxError — missing colon":         'def greet(name)\n    print(f"Hello, {name}!")\n\ngreet("World")',
    "IndexError — out of range":           'fruits = ["apple", "banana", "cherry"]\nprint(fruits[10])',
    "ZeroDivisionError":                   'result = 100 / 0\nprint(result)',
    "KeyError — missing key":              'data = {"name": "Alice"}\nprint(data["age"])',
    "🚫 Security test":                    'import os\nos.system("ls")',
}

# ─────────────────────────────────────────────
# Layout: Sidebar
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 🤖 AI Error Tutor")
    
    _label = "☀️ Switch to Light" if st.session_state.dark_mode else "🌙 Switch to Dark"
    if st.button(_label, key="theme_toggle", use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<p style="font-size:12px;font-weight:600;color:'+TEXT_MUTED+';">LOAD DEMO</p>', unsafe_allow_html=True)
    selected_demo = st.selectbox(
        "demo",
        ["— Select a snippet —"] + list(DEMO_CODES.keys()),
        label_visibility="collapsed"
    )

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<p style="font-size:12px;font-weight:600;color:'+TEXT_MUTED+';">SYSTEM INFO</p>', unsafe_allow_html=True)
    st.markdown("- **Engine**: T5 Transformer\n- **Parser**: AST Parsing\n- **Security**: Validator Active\n- **Tracked**: CodeCarbon")


default_code = (
    DEMO_CODES[selected_demo]
    if selected_demo != "— Select a snippet —" and selected_demo in DEMO_CODES
    else st.session_state.get("code", "# Type or paste your Python code here...\n\n")
)

# ─────────────────────────────────────────────
# Layout: Main Body (Two Columns)
# ─────────────────────────────────────────────

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### 📝 Editor")
    code = st.text_area(
        "editor",
        value=default_code,
        height=350,
        key="code_input",
        label_visibility="collapsed"
    )

    btn_row = st.columns([1, 1])
    with btn_row[0]:
        analyze_clicked = st.button("▶ Run Analysis", type="primary", use_container_width=True)
    with btn_row[1]:
        clear_clicked = st.button("🗑 Clear Editor", use_container_width=True)

    if clear_clicked:
        st.session_state["code"] = ""
        st.rerun()

with col2:
    st.markdown("### 🖥️ Diagnostics Terminal")
    
    if not analyze_clicked and not code.strip():
        st.markdown(f'<div style="border: 1px dashed {BORDER_STRONG}; padding: 30px; text-align: center; border-radius: 8px; color: {TEXT_MUTED}; margin-top: 10px;">Waiting for code execution...</div>', unsafe_allow_html=True)

    if analyze_clicked and code.strip():
        
        with st.spinner("Analyzing code..."):
            with EmissionsTracker(project_name="AI_Error_Tutor_Analysis", log_level="error"):
                result = tutor.analyze_code(code)

        # Success
        if result.success:
            st.markdown(
                f'<div class="status-banner" style="color:{ACCENT_GREEN}; border-left: 4px solid {ACCENT_GREEN};">✓ Build successful — No errors detected.</div>',
                unsafe_allow_html=True,
            )
            if result.security_warnings:
                warned = [w for w in result.security_warnings if w.level == "WARNING"]
                if warned:
                    for w in warned:
                        st.markdown(f'<div class="status-banner" style="color:{ACCENT_ORANGE}; border-left: 4px solid {ACCENT_ORANGE};">⚠️ Line {w.line_number}: {w.message}</div>', unsafe_allow_html=True)

        # Security BLocked
        elif result.error_type == "SecurityError":
            st.markdown(
                f'<div class="status-banner" style="color:{ACCENT_RED}; border-left: 4px solid {ACCENT_RED};">✖ Execution Aborted: Security Risk Detected</div>',
                unsafe_allow_html=True,
            )
            st.markdown(f"""
            <div class="result-card card-security">
                <div class="card-title red">Security Policy Violation</div>
                <div class="card-body">{result.friendly_explanation}</div>
            </div>
            """, unsafe_allow_html=True)

            blocked_lines = []
            if result.security_warnings:
                for w in result.security_warnings:
                    if w.level == "BLOCKED":
                        blocked_lines.append(w.line_number)
            
            if blocked_lines:
                st.markdown(render_code_viewer(code, blocked_lines[0]), unsafe_allow_html=True)

        # Standard Errors
        else:
            st.markdown(
                f'<div class="status-banner" style="color:{ACCENT_RED}; border-left: 4px solid {ACCENT_RED};">✖ {result.error_type} at line {result.line_number}</div>',
                unsafe_allow_html=True,
            )

            st.markdown(render_code_viewer(code, result.line_number), unsafe_allow_html=True)

            st.markdown(f"""
            <div class="result-card card-explain">
                <div class="card-title orange">Diagnostic Summary</div>
                <div class="card-body">{result.friendly_explanation}</div>
            </div>
            """, unsafe_allow_html=True)

            if result.suggested_fix:
                st.markdown(f"""
                <div class="result-card card-fix">
                    <div class="card-title green">Proposed Resolution</div>
                    <div class="card-body">{result.suggested_fix}</div>
                </div>
                """, unsafe_allow_html=True)

            if result.similar_names:
                pills_html = "".join(f'<span class="pill">{n}</span>' for n in result.similar_names)
                st.markdown(f"""
                <div class="result-card card-similar">
                    <div class="card-title pink">Typo Suggestions</div>
                    <div class="card-body">{pills_html}</div>
                </div>
                """, unsafe_allow_html=True)

            with st.expander("Show raw stack trace", expanded=False):
                st.code(result.raw_error, language="python")
    
    elif analyze_clicked:
        st.markdown(f'<div class="status-banner" style="color:{ACCENT_ORANGE}; border-left: 4px solid {ACCENT_ORANGE};">⚠️ No code provided for analysis.</div>', unsafe_allow_html=True)
