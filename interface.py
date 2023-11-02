from __future__ import annotations

import json
import time
from copy import deepcopy
from PyPDF2 import PdfReader
import streamlit as st

from src.parsing.process_cv import parsing_cv
from src.helpers.utils import init_state, display_pdf_pil
from src.helpers.callbacks import uploader_callback, downloader_callback
from src.parsing.post_process import (write_description, reset_description, 
                                  rewrite_resp, reset_resp, infer_more_skills, submit_form)

init_state('parsed_pdf', {})
init_state('uploaded', False)
init_state('processed', False)
init_state('output_json', None)

##################################### LAYOUT DEFINITION ################################################
st.set_page_config(page_title="Resume Parser", page_icon="📑")
st.title("📑 Resume Parser")

with st.sidebar:
    # resume upload
    uploaded_file = st.file_uploader("Upload Resume", on_change=uploader_callback)
    if uploaded_file is not None:       
        display_pdf_pil(uploaded_file=uploaded_file)

if st.session_state['processed']:
    status = st.status("Editing the resume ... ", expanded=True)
elif (uploaded_file is not None):
    status = st.status("Processing the resume ... ", expanded=True) 

if (uploaded_file is not None) and (not(st.session_state['processed'])):
    #status.write("📝 Extracting text...")
    pdf = PdfReader(uploaded_file)
    pdf = '\n'.join([pdf.pages[c].extract_text() for c in range(len(pdf.pages))])

    status.write("👩‍💻 Analyzing the resume...")
    t1 = time.perf_counter(), time.process_time()
    #parsed_cv = parsing_cv(uploaded_file.getvalue())
    parsed_cv = parsing_cv(pdf)
    t2 = time.perf_counter(), time.process_time()
    print({
            parsing_cv.__name__: [
                f"Real time: {t2[0] - t1[0]:.2f} seconds",
                f"CPU time: {t2[1] - t1[1]:.2f} seconds",
            ]
    })
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
            autofilled_work_exp[i]["work_company"] = st.text_input(
                "Company",
                work_exp[i].get("work_company", ""),
                key=f"work_company_{i}",
            )

            # timeline
            c1, c2 = st.columns(2)
            w_f = c1.text_input("From",
                                work_exp[i].get("work_timeline", [None,None])[0], 
                                key=f"work_timeline_from_{i}")
            w_t = c2.text_input("To", 
                                work_exp[i].get("work_timeline", [None,None])[-1], 
                                key=f"work_timeline_to_{i}")
            autofilled_work_exp[i]["work_timeline"] = [w_f, w_t]

            # title
            autofilled_work_exp[i]["work_title"] = st.text_input("Title", 
                                                            work_exp[i].get("work_title", ""), 
                                                            key=f"work_title_{i}")

            # description
            autofilled_work_exp[i]["work_description"] = st.text_area(
                "Description",
                work_exp[i].get("work_description", ""),
                height=150,
                key=f"work_description_{i}",
            )
            bc1, bc2 = st.columns(2, gap="large")
            bc1.button("✍️ Rewrite", on_click=write_description, args=(i,), key=f"rewrite_button_desc_{i}")
            bc2.button("🔄 Reset", on_click=reset_description, args=(i,), key=f"reset_button_desc_{i}")  

            # responsibilities
            resps_list = work_exp[i].get("work_responsibilities", [])
            height = min(50*len(resps_list) if len(resps_list) > 0 else 10, 300)

            resps_str = "\n".join([f"- {c}" for c in resps_list])
            autofilled_work_exp[i]["work_responsibilities"] = st.text_area("Responsibilities",
                                                                    resps_str,
                                                                    height=height,
                                                                    key=f"work_responsibilities_{i}")

            bc1, bc2 = st.columns(2, gap="large")
            bc1.button("✍️ Rewrite", on_click=rewrite_resp, args=(i,), key=f"rewrite_button_resp_{i}")
            bc2.button("🔄 Reset", on_click=reset_resp, args=(i,), key=f"reset_button_resp_{i}")            

            st.markdown("""---""")

    with st.expander(label="EDUCATION", expanded=True,):
        edus = st.session_state['parsed_pdf'].get('education', [])
        autofilled_edus = deepcopy(edus)
        if len(edus) > 0:
            for i, edu in enumerate(edus):
                # Degree
                autofilled_edus[i]["edu_degree"] = st.text_input("Degree",
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
                autofilled_edus[i]["edu_school"] = st.text_input(
                    "School",
                    edus[i].get("edu_school", ""),
                    key=f"edu_school_{i}",
                )

                # GPA
                autofilled_edus[i]["edu_gpa"] = st.text_input("GPA", 
                                                        edus[i].get("edu_gpa", ""), 
                                                        key=f"edu_gpa_{i}")

                # description
                autofilled_edus[i]["edu_description"] = st.text_area(
                    "Description",
                    edus[i].get("edu_description", ""),
                    height=50,
                    key=f"edu_description_{i}",
                )
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
                w_f = c1.text_input("From",
                                    projects[i].get("project_timeline", [None,None])[0], 
                                    key=f"project_timeline_from_{i}")
                w_t = c2.text_input("To", 
                                    projects[i].get("project_timeline", [None,None])[-1], 
                                    key=f"project_timeline_to_{i}")
                autofilled_projects[i]["project_timeline"] = [w_f, w_t]

                # description
                autofilled_projects[i]["project_description"] = st.text_area(
                    "Description",
                    projects[i].get("project_description", ""),
                    height=50,
                    key=f"project_description_{i}",
                )


    with st.expander(label="SKILLS", expanded=True,):
        certifications = st.session_state['parsed_pdf'].get('certifications', [])
        certifications = st.text_area("Certifications", "\n".join(certifications), key="certifications")

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
        download_data = json.dumps(st.session_state['output_json'])
        c2.download_button("🖨️ Export file", data=download_data, file_name='export_doc.json',
                           on_click=downloader_callback, key="export")
    status.update(label="Completed", state="complete", expanded=False)