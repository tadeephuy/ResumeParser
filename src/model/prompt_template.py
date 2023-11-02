PARSING_CV_PROMPTING = """
resume information:
<begin>
{resume}
<end>

example output:
<begin>
{example}
<end>

template data:
<begin>
{template}
<end>

You are a Senior Recruiter (SR) reading the resume.
Parse the resume into the output dictionary following the example and template.
Note: the field "responsibilities" should be copied exactly from the resume.
Note: if the description is not provided, write a summary for the field description.

Answer format:

<output parsing result>
"""

WRITING_DESCRIPTION_PROMPTING = """
You are a career consultant.
You are improving the work experience section in your customer's resume.
Please rewrite a summary description of the work experience from responsibilities, job title and company name.
Rewrite it to make it more professional, highlighting important details, refering to the job title, description and the company.
Write in 1 concise paragraph, do not use subject, strictly no more than 50 words.

title: {title}
company: {company}
description: {description}
responsibilities:
{resp}

Answer format:
<rewritten responsibilities: within 50 words>
"""

REWRITING_TASK_PROMPTING = """
You are a career consultant.
You are improving the work experience section in your customer's resume.
The customer wrote the tasks too short.
If the number of responsibilities is less than 3, come up with at least 2 new responsibilities, refering to the description.
Rewrite it to make it more professional, refering to the job title, description and the company.
Only rewrite the responsibilities, write in bullet points.
The number of the final responsibilities must be at least 4.

title: {title}
company: {company}
description: {description}
responsibilities:
{resp}

Answer format:
<rewritten responsibilities>
"""

ADDING_SKILLS_PROMPTING = """
You are a career consultant.
You are improving the skills section in your customer's resume.
You read the skill list. You read the resume and try to look for more skills and their years of experience to add to the list.
The skill should be related to the domain. Only list the extra skills.

resume:
<begin>
{resume_json}
<end>

skill_list: {skills}

Answer format:
extra_skills:
[
      {"skill_name": "<extra skill 1: str>", "yoe": <years of experience: int>},
      {"skill_name": "<extra skill 2: str>", "yoe": <years of experience: int>},
]
"""