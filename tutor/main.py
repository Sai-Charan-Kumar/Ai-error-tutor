#!/usr/bin/env python3
"""
AI Error Tutor - Streamlit GUI
A friendly Python error message rewriter using AI
 
"""

import streamlit as st
import config
from src.pipeline import AIErrorTutor
from codecarbon import EmissionsTracker  # Imported CodeCarbon

st.set_page_config(
    page_title="AI Error Tutor",
    page_icon="🌅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* 🌅 Deep Warm Obsidian/Plum Background */
    .stApp {
        background: linear-gradient(135deg, #180a15 0%, #0d0509 50%, #14050a 100%);
        color: #f3e8ee;
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }

    /* Hide the sidebar completely */
    [data-testid="collapsedControl"] {
        display: none;
    }

    /* 💎 Glassmorphism Cards */
    .explanation-card, .fix-card, .similar-card, .security-card {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-left-width: 4px;
        border-radius: 12px;
        padding: 20px 24px;
        margin: 16px 0;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .explanation-card:hover, .fix-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 40px 0 rgba(0, 0, 0, 0.6);
    }

    /* ⚡ Vibrant Warm Neon Accents */
    .explanation-card { border-left-color: #ff9d00; } /* Neon Sunset Orange */
    .fix-card         { border-left-color: #ccff00; } /* Neon Chartreuse/Yellow-Green */
    .similar-card     { border-left-color: #ff00aa; } /* Hot Pink */
    .security-card    { border-left-color: #ff2a2a; } /* Vibrant Crimson */

    /* Headings with warm text shadows */
    .explanation-card h3 { color: #ff9d00; font-size: 1.2em; margin-bottom: 10px; margin-top: 0; text-shadow: 0 0 10px rgba(255, 157, 0, 0.3); }
    .fix-card h4         { color: #ccff00; font-size: 1.2em; margin-bottom: 10px; margin-top: 0; text-shadow: 0 0 10px rgba(204, 255, 0, 0.3); }
    .security-card h4    { color: #ff2a2a; font-size: 1.2em; margin-bottom: 10px; margin-top: 0; text-shadow: 0 0 10px rgba(255, 42, 42, 0.3); }

    .explanation-card p, .fix-card p, .similar-card p {
        color: #e2d5dc;
        font-size: 15.5px;
        line-height: 1.6;
        margin-bottom: 0;
    }

    /* 🖥️ Code Container */
    .code-container {
        background: #0a0407; /* Super dark warm grey/black */
        border-radius: 10px;
        padding: 16px 0;
        font-family: 'Fira Code', 'Consolas', monospace;
        font-size: 14.5px;
        line-height: 1.6;
        overflow-x: auto;
        border: 1px solid #2a111b;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.8);
    }

    .code-line {
        padding: 2px 16px;
        display: block;
        white-space: pre;
    }

    .code-line-number {
        color: #6a4a58;
        user-select: none;
        display: inline-block;
        width: 40px;
        text-align: right;
        margin-right: 20px;
        border-right: 1px solid #3d212f;
        padding-right: 15px;
    }

    /* Highlighted Error Line */
    .code-line-error {
        background: linear-gradient(90deg, rgba(255, 42, 42, 0.15) 0%, rgba(255, 42, 42, 0) 100%);
        position: relative;
    }

    .code-line-error::before {
        content: "";
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
        background-color: #ff2a2a;
        box-shadow: 0 0 8px #ff2a2a;
    }

    .code-line-normal {
        color: #e5e7eb;
    }

    /* 🚀 Status Banners */
    .status-success {
        background: rgba(204, 255, 0, 0.08);
        border: 1px solid rgba(204, 255, 0, 0.2);
        border-left: 5px solid #ccff00;
        color: #f3e8ee;
        padding: 16px 20px;
        border-radius: 8px;
        font-size: 16px;
        font-weight: 600;
        margin: 15px 0;
        text-shadow: 0 0 5px rgba(204, 255, 0, 0.3);
    }

    .status-error {
        background: rgba(255, 42, 42, 0.08);
        border: 1px solid rgba(255, 42, 42, 0.2);
        border-left: 5px solid #ff2a2a;
        color: #f3e8ee;
        padding: 16px 20px;
        border-radius: 8px;
        font-size: 16px;
        font-weight: 600;
        margin: 15px 0;
        text-shadow: 0 0 5px rgba(255, 42, 42, 0.4);
    }

    /* Markdown elements */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px;
    }

    /* Customizing Streamlit Inputs & Buttons to match */
    .stTextArea textarea {
        background-color: #0a0407 !important;
        color: #ff9d00 !important;
        border: 1px solid #3d212f !important;
        border-radius: 8px !important;
        font-family: 'Fira Code', 'Consolas', monospace !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #ff9d00 !important;
        box-shadow: 0 0 10px rgba(255, 157, 0, 0.3) !important;
    }

    /* Primary Button Gradient - Hot Pink to Sunset Orange */
    button[kind="primary"] {
        background: linear-gradient(90deg, #ff00aa 0%, #ff9d00 100%) !important;
        border: none !important;
        color: white !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
    }
    
    button[kind="primary"]:hover {
        transform: scale(1.02) !important;
        box-shadow: 0 0 15px rgba(255, 157, 0, 0.5) !important;
    }

    /* Streamlit overrides */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

</style>
""", unsafe_allow_html=True)


@st.cache_resource
def load_tutor():
    """Load the AI Error Tutor (cached across reruns)."""
    try:
        return AIErrorTutor(model_path=config.MODEL_SAVE_PATH, use_ai=True)
    except Exception:
        return AIErrorTutor(use_ai=False)


tutor = load_tutor()

DEMO_CODES = {
    "NameError — Typo in function name": 'print("Testing NameError")\nprnt("Hello World")',
    "TypeError — Adding string and int": 'age = 25\nmessage = "Your age is: " + age\nprint(message)',
    "SyntaxError — Missing colon": 'def greet(name)\n    print(f"Hello, {name}!")\n\ngreet("World")',
    "IndexError — Out of range": 'fruits = ["apple", "banana", "cherry"]\nprint(fruits[10])',
    "ZeroDivisionError": 'result = 100 / 0\nprint(result)',
    "KeyError — Missing key": 'data = {"name": "Alice"}\nprint(data["age"])',
    "🚫 Security Test": 'import os\nos.system("ls")',
}


def render_code_with_highlight(code, error_line=None):
    """Render code with syntax-highlighted error lines."""
    lines = code.split('\n')
    html_lines = []

    for i, line in enumerate(lines, 1):
        escaped_line = (
            line.replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
        )

        if not escaped_line:
            escaped_line = " "

        line_num = f'<span class="code-line-number">{i}</span>'

        if i == error_line:
            css_class = "code-line code-line-error"
        else:
            css_class = "code-line code-line-normal"

        html_lines.append(f'<span class="{css_class}">{line_num}{escaped_line}</span>')

    html = f'<div class="code-container">{"".join(html_lines)}</div>'
    return html


# ─────────────────────────────────────────────
# Main Content Layout
# ─────────────────────────────────────────────

st.markdown("# 🌅 AI Error Tutor")

# Top Menu: About & Shortcuts Expander
with st.expander("ℹ️ About & Shortcuts", expanded=False):
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        st.markdown("**⌨️ Shortcuts:**")
        st.markdown("- **Ctrl + Enter** → Run Analysis\n- **Ctrl + A** → Select all code")
    with col_info2:
        st.markdown("**🛠️ Core Stack:**")
        st.markdown("- T5 Transformer (AI) | AST Parser | Security Validator")

st.markdown("---")

# Code Editor Section
col_editor, col_empty = st.columns([3, 1]) 

with col_editor:
    selected_demo = st.selectbox(
        "Load a demo snippet or write your own:",
        ["— Select a demo —"] + list(DEMO_CODES.keys()),
        label_visibility="visible"
    )

if selected_demo != "— Select a demo —" and selected_demo in DEMO_CODES:
    default_code = DEMO_CODES[selected_demo]
else:
    default_code = st.session_state.get('code', '# Type your Python code here...\n\n')

code = st.text_area(
    "Editor Input",
    value=default_code,
    height=250,
    key="code_input",
    label_visibility="collapsed",
    placeholder="# Type or paste your Python code here...\n\nprint('Hello World!')"
)

# Action Buttons
col_btn1, col_btn2, col_btn3 = st.columns([1.5, 1, 5])

with col_btn1:
    analyze_clicked = st.button("▶ Run Analysis", type="primary", use_container_width=True)

with col_btn2:
    clear_clicked = st.button("🗑 Clear", use_container_width=True)

if clear_clicked:
    st.session_state['code'] = ''
    st.rerun()


# ─────────────────────────────────────────────
# Analysis Results (Terminal View)
# ─────────────────────────────────────────────

if analyze_clicked and code.strip():

    st.markdown("---")
    st.markdown("### 💻 Output Terminal")

    with st.spinner("🤖 Interrogating the compiler..."):
        # Wrap AI execution in CodeCarbon context manager
        with EmissionsTracker(project_name="AI_Error_Tutor_Analysis", log_level="error") as tracker:
            result = tutor.analyze_code(code)

    # ─── Success Banner ───
    if result.success:
        st.markdown('<div class="status-success">✓ Build finished successfully. 0 errors found.</div>',
                    unsafe_allow_html=True)

        if result.security_warnings:
            warned = [w for w in result.security_warnings if w.level == 'WARNING']
            if warned:
                with st.expander("⚠️ Security Linter Notes", expanded=False):
                    for w in warned:
                        st.warning(f"**Line {w.line_number}:** {w.message}\n\n`{w.code_snippet}`")

    # ─── Security Blocked ───
    elif result.error_type == 'SecurityError':
        st.markdown('<div class="status-error">✖ Execution Blocked — Security Risk Detected</div>',
                    unsafe_allow_html=True)

        st.markdown(f"""
        <div class="explanation-card" style="border-left-color: #ff2a2a;">
            <h3 style="color: #ff2a2a; text-shadow: 0 0 10px rgba(255, 42, 42, 0.3);">🛡️ Security Alert</h3>
            <p>{result.friendly_explanation}</p>
        </div>
        """, unsafe_allow_html=True)

        if result.security_warnings:
            for w in result.security_warnings:
                if w.level == 'BLOCKED':
                    st.markdown(f"""
                    <div class="security-card">
                        <h4>Blocked Command (Line {w.line_number})</h4>
                        <p>{w.message}<br><code style="background:transparent; padding:0; color:#ff2a2a;">{w.code_snippet}</code></p>
                    </div>
                    """, unsafe_allow_html=True)

        blocked_lines = [w.line_number for w in result.security_warnings if w.level == 'BLOCKED'] if result.security_warnings else []
        if blocked_lines:
            st.markdown(render_code_with_highlight(code, blocked_lines[0]),
                        unsafe_allow_html=True)

    # ─── Standard Error Found ───
    else:
        st.markdown(
            f'<div class="status-error">✖ {result.error_type} at line {result.line_number}</div>',
            unsafe_allow_html=True)

        st.markdown(
            render_code_with_highlight(code, result.line_number),
            unsafe_allow_html=True
        )

        st.markdown(f"""
        <div class="explanation-card">
            <h3>💡 AI Diagnostics</h3>
            <p>{result.friendly_explanation}</p>
        </div>
        """, unsafe_allow_html=True)

        if result.suggested_fix:
            st.markdown(f"""
            <div class="fix-card">
                <h4>🔧 Suggested Fix</h4>
                <p>{result.suggested_fix}</p>
            </div>
            """, unsafe_allow_html=True)

        if result.similar_names:
            names_html = ', '.join(
                f'<code style="color:#ff00aa; background:rgba(255,0,170,0.1); padding:2px 8px; border-radius:4px; border: 1px solid rgba(255,0,170,0.3);">{n}</code>'
                for n in result.similar_names
            )
            st.markdown(f"""
            <div class="similar-card">
                <p><strong style="color:#ff00aa; text-shadow: 0 0 8px rgba(255,0,170,0.4);">❓ Did you mean:</strong> {names_html}</p>
            </div>
            """, unsafe_allow_html=True)

        with st.expander("View Raw Traceback", expanded=False):
            st.code(result.raw_error, language="python")

elif analyze_clicked:
    st.warning("⚠️ Please write some code in the editor before running analysis.")
