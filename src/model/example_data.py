DATA_TEMPLATE = """
Field	Subfield	Description	Key name	Format
Name	N/A	Name of the candidate	candidate_name	string
Current Title	N/A	Current job title of the candidate	candidate_title	string
Summary	N/A	A summary of the resume (generated)	summary	string
Links	N/A	External internet links if available	links	list of string
Languages			languages	list of dict
	language	name of the language	lang	string
	level	level of proficiency	lang_lvl	string
Work Experience			work_exp	list of dict
	Timeline	From - To	work_timeline	tuple of int
	Company	Company name	work_company	string
	Title	Job title at the company	work_title	string
  Responsibilities	Responsibilities, achievements done, written in bullet points, copy from the resume work_responsibilities	list of string
  Description Short summary of tasks, achievements, technology used, in maximum 30 words work_description	string
Education			education	list of dict
	Timeline	From - To	edu_timeline	tuple of int
	School	School name	edu_school	string
	Degree	Degree type, name, topic	edu_degree	string
	GPA	GPA of the degree	edu_gpa	tuple of float
	Descriptions	Other information	edu_description	string
Projects			projects	list of dict
	Timeline	From - To	project_timeline	tuple of int
	Project name	Project name	project_name	string
	Descriptions	Description of the project	project_description	string
Certifications  N/A list of achieved certifications certifications  list of string
Skills			skills or technologies used list of dict
	Skill name	Name of the skill	skill_name	string
	YOE	Year of experience, can be inferred	yoe	float
"""

OUTPUT_TEMPLATE = """
{
  "candidate_name": "John Doe",
  "candidate_title": "Software Engineer",
  "summary": "Experienced software engineer with a passion for creating efficient and scalable solutions.",
  "links": [
    "https://linkedin.com/in/johndoe"
  ],
  "languages": [
    {"lang": "Vietnamese", "lang_lvl": "native"},
    {"lang": "English", "lang_lvl": "fluent"},
  ]
  "work_exp": [
    {
      "work_timeline": [2018, 2023],
      "work_company": "TechCorp",
      "work_title": "Senior Software Engineer",
      "work_responsibilities": [
        "Designed and implemented new features",
        "Optimized existing codebase for performance improvements",
        "Mentored junior developers"
      ],
      "work_description": "Led a team of developers in designing and implementing critical features for the flagship product.",
    },
    {
      "work_timeline": [2015, 2018],
      "work_company": "CodeCrafters",
      "work_title": "Software Engineer",
      "work_responsibilities": [
        "Developed and maintained backend services",
        "Collaborated with UX/UI designers for front-end development"
      ],
      "work_description": "Collaborated with cross-functional teams to deliver high-quality software solutions.",
    }
  ],
  "education": [
    {
      "edu_timeline": [2011, 2015],
      "edu_school": "University of Tech",
      "edu_degree": "Bachelor of Science in Computer Science",
      "edu_gpa": 3.8,
      "edu_description": "Graduated with honors"
    }
  ],
  "projects": [
    {
      "project_timeline": [2020, 2021],
      "project_name": "Mobile Expense Tracker App",
      "project_description": "Designed and developed a mobile app for tracking personal expenses."
    }
  ],
  "certifications": [
    "IELTS 9.0",
    "2023: PMI Agile Certified Practicioner"
  ]
  "skills": [
    {"skill_name": "JavaScript", "yoe": 5},
    {"skill_name": "React", "yoe": 3}
  ]
}
"""
