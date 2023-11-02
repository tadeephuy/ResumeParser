import json
import os
import streamlit as st
from langchain.prompts.prompt import PromptTemplate

from ..helpers.utils import init_chain
from ..model.prompt_template import (WRITING_DESCRIPTION_PROMPTING,
                                     REWRITING_TASK_PROMPTING,
                                     ADDING_SKILLS_PROMPTING)

WRITE_DESCRIPTION_PROMPT = PromptTemplate(
    input_variables=["title", "company", "description", "resp"],
    template=WRITING_DESCRIPTION_PROMPTING
)
REWRITE_TASK_PROMPT = PromptTemplate(
    input_variables=["title", "company", "description", "resp"],
    template=REWRITING_TASK_PROMPTING
)
ADD_ON_SKILL_PROMPT = PromptTemplate(
    input_variables=["resume_json", "skills"],
    template=ADDING_SKILLS_PROMPTING
)

def get_experience_information(index):
    resp = st.session_state.get(f"work_responsibilities_{index}", "")
    title = st.session_state.get(f"work_title_{index}", "employee")
    company = st.session_state.get(f"work_company_{index}", "Company")
    description = st.session_state.get(f"work_description_{index}", "")
    
    return resp, title, company, description

def reset_description(work_exp, i):
    description = work_exp[i].get("work_description", "") 
    st.session_state[f"work_description_{i}"] = description
    st.toast('Description restored.', icon='🔄')

def reset_resp(work_exp, i):
    resps_list = work_exp[i].get("work_responsibilities", []) 
    resps_str = "\n".join([f"- {c}" for c in resps_list])
    st.session_state[f"work_responsibilities_{i}"] = resps_str
    st.toast('Responsibilities restored.', icon='🔄')

def init_chain_experience(task, chat_model):
    return (
        init_chain(chat_model, REWRITE_TASK_PROMPT)
        if task == "rewrite_resp"
        else init_chain(chat_model, WRITE_DESCRIPTION_PROMPT)
    )

def update_object(autofilled_obj, index, task, model_response):
    if task == "rewrite_resp":
        st.session_state[f"work_responsibilities_{index}"] = model_response
        autofilled_obj[index]["work_responsibilities"]  = st.session_state[f"work_responsibilities_{index}"]
    else:
        st.session_state[f"work_description_{index}"] = model_response
        autofilled_obj[index]["work_description"]  = st.session_state[f"work_description_{index}"]

def write_experience_information(index, task, chat_model, autofilled_obj):
    resp, title, company, description = get_experience_information(index)
    chain = init_chain_experience(task, chat_model)
    model_response = chain.run({
        "title": title,
        "company": company,
        "description": description,
        "resp": resp
    })
    
    update_object(autofilled_obj, index, task, model_response)

def submit_form():
    export_work_exp = []
    for i in range(len(autofilled_work_exp)):
        ewe = {
            "work_timeline": [st.session_state[f"work_timeline_from_{i}"], st.session_state[f"work_timeline_to_{i}"]],
            "work_company": st.session_state[f"work_company_{i}"],
            "work_title": st.session_state[f"work_title_{i}"],
            "work_description": st.session_state[f"work_description_{i}"],
            "work_responsibilities": [c[2:] for c in st.session_state[f"work_responsibilities_{i}"].split('\n')]
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
        }
        export_projects.append(ep)
    
    export_skills = []
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