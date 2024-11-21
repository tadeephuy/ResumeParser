import streamlit as st
import io
import os
import base64
import json
from functools import partial
from copy import deepcopy
from PyPDF2 import PdfReader
import fitz
import shutil
from prompt import (prompt_to_parse_cv, prompt_to_rewrite_task, prompt_to_add_skills, prompt_to_write_description,
                    post_parse_cv, post_rewrite_task, post_add_skills, post_write_description)
from export_resume import create_docx_file, post_process
from langchain.schema import (
    AIMessage, HumanMessage, SystemMessage
)
from langchain.chat_models import ChatOpenAI
from word_document import WordDocProcessor

# initialize chat model
chat = ChatOpenAI(model="gpt-4o", temperature=0.0, 
                  openai_api_key=st.secrets['openai_api_key'])

def write_description(i):
    st.toast("Summarizing description ...", icon='✍️')
    
    resp = st.session_state.get(f"work_responsibilities_{i}", "")
    title = st.session_state.get(f"work_title_{i}", "employee")
    company = st.session_state.get(f"work_company_{i}", "Conpany")
    description = st.session_state.get(f"work_description_{i}", "")
    
    prompt = prompt_to_write_description(
        resp=resp, title=title, company=company, description=description
    )
    new_output = chat([
        SystemMessage(content="You are a career consultant."),
        HumanMessage(content=prompt)
    ])
    new_output = post_write_description(new_output.content)
    st.session_state[f"work_description_{i}"] = new_output
    autofilled_work_exp[i]["work_description"]  = st.session_state[f"work_description_{i}"]

def rewrite_resp(i):
    st.toast("Rewriting responsibilities ...", icon='✍️')
    
    resp = st.session_state.get(f"work_responsibilities_{i}", "")
    title = st.session_state.get(f"work_title_{i}", "employee")
    company = st.session_state.get(f"work_company_{i}", "Conpany")
    description = st.session_state.get(f"work_description_{i}", "")

    prompt = prompt_to_rewrite_task(
        resp=resp, title=title, company=company, description=description
    )
    new_output = chat([
        SystemMessage(content="You are a career consultant."),
        HumanMessage(content=prompt)
    ])
    new_output = post_rewrite_task(new_output.content)
    st.session_state[f"work_responsibilities_{i}"] = new_output
    autofilled_work_exp[i]["work_responsibilities"]  = st.session_state[f"work_responsibilities_{i}"]

def infer_more_skills():
    st.toast("Searching for more skills...", icon="🔎")
    export_skills = []
    for i in range(len(autofilled_skills)):
        es = {
            "skill_name": st.session_state[f"skill_name_{i}"],
            "yoe": st.session_state[f"yoe_{i}"],
        }
        export_skills.append(es)
    skills = '\n'.join(f"{c['skill_name']} - {c['yoe']}" for c in export_skills)
    
    prompt = prompt_to_add_skills(skills=skills, resume_json=str(st.session_state['parsed_pdf']))
    new_skills = chat([
        SystemMessage(content="You are a career consultant."),
        HumanMessage(content=prompt)
    ])
    new_skills = post_add_skills(new_skills.content)
    new_skills = eval(new_skills)
    st.session_state['new_skills'] = new_skills


def extract_text_from_pdf(uploaded_file):
    with st.status("Processing the resume ... ", expanded=True) as status:
        status.write("📑 Extracting text ...")
        pdf = PdfReader(uploaded_file)
        pdf = '\n'.join([pdf.pages[c].extract_text() for c in range(len(pdf.pages))])
        
        status.write("👩‍💻 Analyzing the resume ...")
        parsed_cv = chat([
            SystemMessage(content="You are a senior recruiter."),
            HumanMessage(content=prompt_to_parse_cv(resume=pdf))
        ])
        parsed_cv = post_parse_cv(parsed_cv.content)
        status.write("✍️ Filling the forms ...")
        parsed_cv = json.loads(parsed_cv)
        # with open('./sample.json', 'rb') as f:
        #     parsed_cv = json.load(f)
        st.session_state['parsed_pdf'] = parsed_cv
        st.session_state['processed'] = True

        status.update(label="Completed", state="complete", expanded=False)


def display_pdf(uploaded_file):

    os.makedirs('./tmp_output', exist_ok=True)
    doc = fitz.open(stream=uploaded_file.read())
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=300)  # render page to an image
        pix.save(f"./tmp_output/page_{i}.png")
    st.image([f"./tmp_output/page_{i}.png" for i in range(len(doc))])

    # wait until can display pdf on steamlit cloud
    # base64_pdf = base64.b64encode(uploaded_file.getvalue()).decode('utf-8')
    # pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height=600px type="application/pdf"></iframe>'
    # st.markdown(pdf_display, unsafe_allow_html=True)
    st.session_state['uploaded'] = True

def reset_description(i):
    description = work_exp[i].get("work_description", "") 
    st.session_state[f"work_description_{i}"] = description
    st.toast('Description restored.', icon='🔄')

def reset_resp(i):
    resps_list = work_exp[i].get("work_responsibilities", []) 
    resps_str = "\n".join([f"- {c}" for c in resps_list])
    st.session_state[f"work_responsibilities_{i}"] = resps_str
    st.toast('Responsibilities restored.', icon='🔄')

def submit_form():
    export_work_exp = []
    for i in range(len(autofilled_work_exp)):
        ewe = {
            "work_timeline": [st.session_state[f"work_timeline_from_{i}"], st.session_state[f"work_timeline_to_{i}"]],
            "work_company": st.session_state[f"work_company_{i}"],
            "work_title": st.session_state[f"work_title_{i}"],
            "work_description": st.session_state[f"work_description_{i}"],
            "work_responsibilities": [c[2:] for c in st.session_state[f"work_responsibilities_{i}"].split('\n')],
            "work_technologies": st.session_state[f"work_technologies_{i}"]
        }
        export_work_exp.append(ewe)
    
    export_education = []
    for i in range(len(autofilled_edus)):
        ee = {
            "edu_timeline": [st.session_state[f"edu_timeline_from_{i}"], st.session_state[f"edu_timeline_to_{i}"]],
            "edu_school": st.session_state[f"edu_school_{i}"],
            "edu_degree": st.session_state[f"edu_degree_{i}"],
            "edu_gpa": st.session_state[f"edu_gpa_{i}"],
            "edu_description": st.session_state[f"edu_description_{i}"],
        }
        export_education.append(ee)
    
    export_projects = []
    for i in range(len(autofilled_projects)):
        ep = {
            "project_timeline": [st.session_state[f"project_timeline_from_{i}"], st.session_state[f"project_timeline_to_{i}"]],
            "project_name": st.session_state[f"project_name_{i}"],
            "project_description": st.session_state[f"project_description_{i}"],
            "project_responsibilities": [c[2:] for c in st.session_state[f"project_responsibilities_{i}"].split('\n')],
            "project_technologies": st.session_state[f"project_technologies_{i}"]
        }
        export_projects.append(ep)
    
    export_skills = []
    for i in range(len(autofilled_skills)):
        es = {
            "skill_name": st.session_state[f"skill_name_{i}"],
            "yoe": st.session_state[f"yoe_{i}"],
        }
        export_skills.append(es)
    for i in range(len(autofilled_skills)):
        es = {
            "skill_name": st.session_state[f"skill_name_{i}"],
            "yoe": st.session_state[f"yoe_{i}"],
        }
        export_skills.append(es)
    
    export_languages = []
    for i in range(len(autofilled_languages)):
        el = {
            "lang": st.session_state[f"lang_{i}"],
            "lang_lvl": st.session_state[f"lang_lvl_{i}"],
        }
        export_languages.append(el)    

    export = {
        "candidate_name": st.session_state.candidate_name,
        "candidate_title": st.session_state.candidate_title,
        "summary": st.session_state.summary,
        "links": st.session_state.links.split('\n'),
        "languages": export_languages,
        "work_exp": export_work_exp,
        "education": export_education,
        "projects": export_projects,
        "certifications": st.session_state.certifications.split('\n'),
        "skills": export_skills
    }
    st.session_state['output_json'] = export
    os.makedirs('output', exist_ok=True)
    with open('./output/export_resume.json', 'w', encoding='utf-8') as f:
        json.dump(export, f, ensure_ascii=False, indent=4)
    st.toast("Form submitted!", icon="🎯")

def downloader_callback():
    if st.session_state['output_json'] is None:
        st.toast(":red[Submit the form first!]", icon="⚠️")
        return
    st.toast("New resume downloaded!", icon="🎯")
    with open('./output/export_resume_doc.json', 'w', encoding='utf-8') as f:
        json.dump(st.session_state['output_json'], f, ensure_ascii=False, indent=4)

def uploader_callback():
    st.toast("Resume uploaded.", icon="📑")
    shutil.rmtree("./tmp_output", True )

    st.session_state['parsed_pdf'] = dict()
    st.session_state['processed'] = False
    st.session_state['output_json'] = None

##################################### INITIALIZE STATES ################################################
def init_state(key, value):
    if key not in st.session_state:
        st.session_state[key] = value

init_state('parsed_pdf', dict())
init_state('uploaded', False)
init_state('processed', False)
init_state('output_json', None)
##################################### LAYOUT DEFINITION ################################################
st.set_page_config(page_title="Resume Parser", page_icon="📑")
st.title("📑 Resume Parser",)

# Inject custom CSS to set the width of the sidebar
st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            width: 100% !important; # Set the width to your desired value
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# st.button("Restart", on_click="restart")
with st.sidebar:
    # resume upload
    uploaded_file = st.file_uploader("Upload Resume", on_change=uploader_callback)
    if uploaded_file is not None and uploaded_file.name.endswith('.pdf'):       
        display_pdf(uploaded_file=uploaded_file)

if st.session_state['processed']:
    status = st.status("Editing the resume ... ", expanded=True)
elif (uploaded_file is not None):
    status = st.status("Processing the resume ... ", expanded=True) 

if (uploaded_file is not None) and (not(st.session_state['processed'])):
    # extract_text_from_pdf(uploaded_file=uploaded_file)
    status.write("📝 Extracting text...")
    if uploaded_file.name.endswith('.docx') or uploaded_file.name.endswith('.doc'):
        document = WordDocProcessor(uploaded_file.getvalue()).load_doc()
    else:
        document = PdfReader(uploaded_file)
        document = '\n'.join([document.pages[c].extract_text() for c in range(len(document.pages))])
    status.write("👩‍💻 Analyzing the resume...")
    parsed_cv = chat([
        SystemMessage(content="You are a senior recruiter."),
        HumanMessage(content=prompt_to_parse_cv(resume=document))
    ])
    parsed_cv = post_parse_cv(parsed_cv.content)
    parsed_cv = json.loads(parsed_cv)
    st.session_state['parsed_pdf'] = parsed_cv
    st.session_state['processed'] = True

if st.session_state['processed']:
    status.write("✍️ Filling the forms ...")
    with st.expander(label="INFORMATION", expanded=True,): 
        st.markdown("""---""")

        candidate_name = st.text_input('Name', value=st.session_state['parsed_pdf'].get('candidate_name', ""), key="candidate_name")
        candidate_title = st.text_input('Title', value=st.session_state['parsed_pdf'].get('candidate_title', ""), key="candidate_title")
        summary = st.text_area("Summary", value=st.session_state['parsed_pdf'].get('summary', ""), key="summary")
        links = st.text_area("Links", "\n".join(st.session_state['parsed_pdf'].get('links', [])), key="links")
        
        languages = st.session_state['parsed_pdf'].get('languages', [])
        autofilled_languages = deepcopy(languages)
        c1, c2 = st.columns([3,2])
        for i,lg in enumerate(languages):
            visibility = "visible" if i == 0 else "hidden"
            lang = c1.text_input("Language", languages[i].get("lang", ""), 
                                        label_visibility=visibility, 
                                        key=f"lang_{i}")
            lang_lvl = c2.text_input("Level", languages[i].get("lang_lvl", ""), 
                                        label_visibility=visibility, 
                                        key=f"lang_lvl_{i}")
            autofilled_languages[i] = {"lang": lang, "lang_lvl": lang_lvl}

    with st.expander(label="EXPERIENCE", expanded=True,):
        work_exp = st.session_state['parsed_pdf'].get('work_exp', [])
        autofilled_work_exp = deepcopy(work_exp)
        for i, we in enumerate(work_exp):
            # company
            autofilled_work_exp[i]["work_company"] = st.text_input(f"Company", 
                                                            work_exp[i].get("work_company", ""), 
                                                            key=f"work_company_{i}")

            # timeline
            c1, c2 = st.columns(2)
            timeline = work_exp[i].get("work_timeline", [None,None])
            if timeline is None: timeline = [None, None]
            w_f = c1.text_input("From", timeline[0], 
                                key=f"work_timeline_from_{i}")
            w_t = c2.text_input("To", timeline[-1], 
                                key=f"work_timeline_to_{i}")
            autofilled_work_exp[i]["work_timeline"] = [w_f, w_t]

            # title
            autofilled_work_exp[i]["work_title"] = st.text_input(f"Title", 
                                                            work_exp[i].get("work_title", ""), 
                                                            key=f"work_title_{i}")

            # description
            autofilled_work_exp[i]["work_description"] = st.text_area(f"Description",
                                                                work_exp[i].get("work_description", ""),
                                                                height=150,
                                                                key=f"work_description_{i}",)
            bc1, bc2 = st.columns(2, gap="large")
            bc1.button("✍️ Rewrite", on_click=write_description, args=(i,), key=f"rewrite_button_desc_{i}")
            bc2.button("🔄 Reset", on_click=reset_description, args=(i,), key=f"reset_button_desc_{i}")  

            # responsibilities
            resps_list = work_exp[i].get("work_responsibilities", [])
            height = min(100*len(resps_list) if len(resps_list) > 0 else 100, 300)
            
            resps_str = "\n".join([f"- {c}" for c in resps_list])
            autofilled_work_exp[i]["work_responsibilities"] = st.text_area(f"Responsibilities",
                                                                    resps_str,
                                                                    height=height,
                                                                    key=f"work_responsibilities_{i}")

            bc1, bc2 = st.columns(2, gap="large")
            bc1.button("✍️ Rewrite", on_click=rewrite_resp, args=(i,), key=f"rewrite_button_resp_{i}")
            bc2.button("🔄 Reset", on_click=reset_resp, args=(i,), key=f"reset_button_resp_{i}")            
            
            
            # technologies
            autofilled_work_exp[i]["technologies"] = st.text_area(f"Technologies",
                                                                work_exp[i].get("technologies", ""),
                                                                key=f"work_technologies_{i}")

            st.markdown("""---""")

    with st.expander(label="EDUCATION", expanded=True,):
        edus = st.session_state['parsed_pdf'].get('education', [])
        autofilled_edus = deepcopy(edus)
        if len(edus) > 0:
            for i, edu in enumerate(edus):
                # Degree
                autofilled_edus[i]["edu_degree"] = st.text_input(f"Degree",
                                                            edus[i].get("edu_degree", ""),
                                                            key=f"edu_degree_{i}")

                # timeline
                c1, c2 = st.columns(2)
                w_f = c1.text_input("From",
                                    edus[i].get("edu_timeline", [None,None])[0], 
                                    key=f"edu_timeline_from_{i}")
                w_t = c2.text_input("To", 
                                    edus[i].get("edu_timeline", [None,None])[-1], 
                                    key=f"edu_timeline_to_{i}")
                autofilled_edus[i]["edu_timeline"] = [w_f, w_t]
                
                # school
                autofilled_edus[i]["edu_school"] = st.text_input(f"School", 
                                                            edus[i].get("edu_school", ""), 
                                                            key=f"edu_school_{i}")

                # GPA
                autofilled_edus[i]["edu_gpa"] = st.text_input(f"GPA", 
                                                        edus[i].get("edu_gpa", ""), 
                                                        key=f"edu_gpa_{i}")
                
                # description
                autofilled_edus[i]["edu_description"] = st.text_area(f"Description",
                                                                edus[i].get("edu_description", ""),
                                                                height=100,
                                                                key=f"edu_description_{i}",)
                st.markdown("""---""")

    with st.expander(label="PROJECTS", expanded=True,):
        projects = st.session_state['parsed_pdf'].get('projects', [])
        autofilled_projects = deepcopy(projects)
        if len(projects) > 0:
            for i, prj in enumerate(projects):
                # name
                autofilled_projects[i]["project_name"] = st.text_input("Project name",
                                                                projects[i].get("project_name", ""),
                                                                key=f"project_name_{i}",)

                # timeline
                c1, c2 = st.columns(2)
                timeline = projects[i].get("project_timeline", [None,None])
                if timeline is None: timeline = [None,None]
                w_f = c1.text_input("From", timeline[0], 
                                    key=f"project_timeline_from_{i}")
                w_t = c2.text_input("To", timeline[-1], 
                                    key=f"project_timeline_to_{i}")
                autofilled_projects[i]["project_timeline"] = [w_f, w_t]
                
                # description
                autofilled_projects[i]["project_description"] = st.text_area(f"Description",
                                                                projects[i].get("project_description", ""),
                                                                height=100,
                                                                key=f"project_description_{i}",)

                # responsibilities
                resps_list = projects[i].get("project_responsibilities", [])
                height = min(100*len(resps_list) if len(resps_list) > 0 else 100, 300)
                
                resps_str = "\n".join([f"- {c}" for c in resps_list])
                autofilled_projects[i]["project_responsibilities"] = st.text_area(f"Responsibilities",
                                                                        resps_str,
                                                                        height=height,
                                                                        key=f"project_responsibilities_{i}")
                
                # technologies
                autofilled_projects[i]["project_technologies"] = st.text_area(f"Technologies",
                                                                    projects[i].get("project_technologies", ""),
                                                                    key=f"project_technologies_{i}")

    with st.expander(label="SKILLS", expanded=True,):
        certifications = st.session_state['parsed_pdf'].get('certifications', [])
        height = min(100*len(certifications) if len(certifications) > 0 else 100, 300)
        certifications = st.text_area("Certifications", "\n".join(certifications),
                                      height=height,
                                      key="certifications")

        skills = st.session_state['parsed_pdf'].get("skills", [])
        autofilled_skills = deepcopy(skills)
        c1, c2 = st.columns([4,1])
        for i,skill in enumerate(skills):
            visibility = "visible" if i == 0 else "hidden"
            skill_name = c1.text_input("Skill name", skills[i].get("skill_name", ""), 
                                        label_visibility=visibility, 
                                        key=f"skill_name_{i}")
            yoe = c2.text_input("YOE", skills[i].get("yoe", ""), 
                                        label_visibility=visibility, 
                                        key=f"yoe_{i}")
            autofilled_skills[i] = {"skill_name": skill_name, "yoe": yoe}

        # new skills
        offset = len(autofilled_skills)
        if 'new_skills' not in st.session_state:
            st.session_state['new_skills'] = []
        if len(st.session_state['new_skills']) == 0:
            st.button("Look for more skills", on_click=infer_more_skills)
        new_skills = st.session_state['new_skills']
        for i,skill in enumerate(new_skills):
            visibility = "visible" if i == 0 else "hidden"
            skill_name = c1.text_input("Skill name", new_skills[i].get("skill_name", ""), 
                                        label_visibility=visibility, 
                                        key=f"skill_name_{i+offset}")
            yoe = c2.text_input("YOE", new_skills[i].get("yoe", ""), 
                                        label_visibility=visibility, 
                                        key=f"yoe_{i+offset}")
            autofilled_skills.append({"skill_name": skill_name, "yoe": yoe})

    c1, c2 = st.columns(2, gap='large')
    c1.button("Submit", on_click=submit_form, key="submit")
    if st.session_state['output_json'] is not None:
        # download_data = json.dumps(st.session_state['output_json'])
        processed_data = post_process(st.session_state['output_json'])
        download_data = create_docx_file(processed_data)
        bio = io.BytesIO()
        download_data.save(bio)
        c2.download_button("🖨️ Export file", 
                           data=bio.getvalue(), 
                           file_name='export_resume.docx', 
                           mime="docx",
                           on_click=downloader_callback, key="export")
    status.update(label="Completed", state="complete", expanded=False)
