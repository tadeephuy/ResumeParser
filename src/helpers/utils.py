import base64
import streamlit as st
import fitz
import PIL
def init_state(key, value):
    if key not in st.session_state:
        st.session_state[key] = value

def display_pdf_pil(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read())
    pix_list = []
    for page in doc:
        pix = page.get_pixmap(dpi=300) # render page to an image
        pix_list.append(PIL.Image.frombytes("RGB", [pix.width, pix.height], pix.samples))
    st.image(pix_list)

def display_pdf_embed(uploaded_file):
    # cannot display on Streamlit Cloud
    # suitable for local development
    base64_pdf = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height=600px type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)
    st.session_state['uploaded'] = True