import json

import streamlit as st


def uploader_callback():
    st.toast("Resume uploaded.", icon="📑")

    st.session_state['parsed_pdf'] = {}
    st.session_state['processed'] = False
    st.session_state['output_json'] = None

def downloader_callback():
    if st.session_state['output_json'] is None:
        st.toast(":red[Submit the form first!]", icon="⚠️")
        return
    st.toast("New resume downloaded!", icon="🎯")
    with open('./output/export_resume_doc.json', 'w', encoding='utf-8') as f:
        json.dump(st.session_state['output_json'], f, ensure_ascii=False, indent=4)