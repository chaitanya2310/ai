# styles/style.py - injects styles/style.css into the Streamlit page
import json
import os

import streamlit as st
import streamlit.components.v1 as components

CSS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "style.css")
STYLE_ID = "student-assistant-style"


def load_css():
    """Read style.css. Returns the CSS text, or None if the file is missing."""
    try:
        with open(CSS_PATH, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


def inject_css():
    """Apply styles/style.css. Call once near the top of ui.py."""
    css = load_css()
    if css is None:
        st.warning(f"Style file not found: {CSS_PATH}")
        return

    # Main method: a tiny script writes the CSS into the page's <head>.
    script = f"""
    <script>
      const doc = window.parent.document;
      let tag = doc.getElementById("{STYLE_ID}");
      if (!tag) {{
        tag = doc.createElement("style");
        tag.id = "{STYLE_ID}";
        doc.head.appendChild(tag);
      }}
      tag.textContent = {json.dumps(css)};
    </script>
    """
    if hasattr(st, "iframe"):                  # Streamlit >= 1.4x
        st.iframe(script, height=1)
    else:                                      # older Streamlit versions
        components.html(script, height=0)

    # Fallback in case the script can't reach the page.
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)