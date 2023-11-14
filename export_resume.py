import json
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_COLOR_INDEX
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT


def create_docx_file(data):

    # Create a new Word document
    doc = Document()

    # Create a table with two columns
    table0 = doc.add_table(rows=1, cols=2)

    # Define the table cells
    cell_00 = table0.cell(0, 0)
    cell_01 = table0.cell(0, 1)

    # Add logo
    image_path = "SMD_icon.PNG"
    cell_00.add_paragraph().add_run().add_picture(image_path)

    # Add name
    name = cell_01.add_paragraph(data['candidate_name'])
    name.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    name_runs = name.runs
    for run in name_runs:
        run.font.size = Pt(24)
        run.font.color.theme_color = WD_COLOR_INDEX.DARK_BLUE
        run.font.bold = True

    # Add title
    title = cell_01.add_paragraph(data['candidate_title'])
    title.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    title_runs = title.runs
    for run in title_runs:
        run.font.size = Pt(16)
        run.font.bold = True

    # Add summary
    cell_01.add_paragraph(data['summary'])

    # Add a horizontal line
    doc.add_paragraph('_' * 100).alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    doc.add_paragraph('www.smartdev.com | Hanoi City, Vietnam').alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    doc.add_paragraph('_' * 100).alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    # Iterate through all paragraphs and remove space after each one
    for paragraph in doc.paragraphs:
        paragraph.paragraph_format.space_after = 0 

    # Create a table with two columns
    table1 = doc.add_table(rows=1, cols=2)

    # Define the table cells
    cell_10 = table1.cell(0, 0)
    cell_11 = table1.cell(0, 1)

    # Add links
    if len(data['links']) > 1:
        contact = cell_10.add_paragraph('Contact')
        contact_runs = contact.runs
        for run in contact_runs:
            run.font.size = Pt(20)
            run.font.bold = True

        # Create the hyperlink
        for link in data['links']:
            cell_10.add_paragraph(link, style='List Bullet')

    # Add work experience
    exp = cell_11.add_paragraph('Work Experience')
    exp_runs = exp.runs
    for run in exp_runs:
        run.font.size = Pt(20)
        run.font.bold = True

    for exp in data['work_exp']:
        details = cell_11.add_paragraph(f"{exp['work_timeline'][0]} - {exp['work_timeline'][1]} | {exp['work_title']} - {exp['work_company']}")
        details_runs = details.runs
        for run in details_runs:
            run.font.bold = True

        cell_11.add_paragraph(exp['work_description'])

        # Add responsibilities
        res = cell_11.add_paragraph('Responsibilities: ')
        res_runs = res.runs
        for run in res_runs:
            run.font.bold = True

        for resp in exp['work_responsibilities']:
            cell_11.add_paragraph(resp, style='List Bullet')

    # Add projects
    if len(data['projects']) > 0:
        projects = cell_11.add_paragraph('Projects')
        projects_runs = projects.runs
        for run in projects_runs:
            run.font.size = Pt(20)
            run.font.bold = True

        for project in data['projects']:
            details = cell_11.add_paragraph(f" {exp['project_name']}")
            details_runs = details.runs
            for run in details_runs:
                run.font.bold = True

            cell_11.add_paragraph(exp['project_description'])


    # Add education
    ed = cell_10.add_paragraph('Education')
    edu_runs = ed.runs
    for run in edu_runs:
        run.font.size = Pt(20)
        run.font.bold = True

    for edu in data['education']:
        edu_details = cell_10.add_paragraph(f"{edu['edu_timeline'][0]} - {edu['edu_timeline'][1]} | {edu['edu_degree']} - {edu['edu_school']}")
        edu_details_runs = edu_details.runs
        for run in edu_details_runs:
            run.font.bold = True

    # Add certifcations
    if len(data['certifications']) > 0:
        certs = cell_10.add_paragraph('Certifications')
        certs_runs = certs.runs
        for run in certs_runs:
            run.font.size = Pt(20)
            run.font.bold = True

        for cert in data['certifications']:
            cell_10.add_paragraph(cert, style='List Bullet')

    # Add skills
    if len(data['skills']) > 0:
        skills = cell_10.add_paragraph('Skills')
        skills_runs = skills.runs
        for run in skills_runs:
            run.font.size = Pt(20)
            run.font.bold = True

        for skill in data['skills']:
            skill_name = skill['skill_name']
            yoe = skill['yoe']
            if yoe is not None:
                skill_text = f"{skill_name} - {yoe} years"
            else:
                skill_text = skill_name
            cell_10.add_paragraph(skill_text, style='List Bullet')

    return doc
