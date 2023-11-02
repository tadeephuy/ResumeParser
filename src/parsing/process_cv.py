from functools import lru_cache
from PyPDF2 import PdfReader
from langchain.prompts.prompt import PromptTemplate

from ..helpers.utils import init_chain
from ..model.example_data import DATA_TEMPLATE, OUTPUT_TEMPLATE
from ..model.prompt_template import PARSING_CV_PROMPTING

PROMPT = PromptTemplate(
    input_variables=["resume", "example", "template"],
    template=PARSING_CV_PROMPTING
)


def ocr_pdf(file, status_obj):
    status_obj.write("📝 Extracting text...")
    pdf_loader = PdfReader(file)
    return '\n'.join([pdf_loader.pages[c].extract_text() for c in range(len(pdf_loader.pages))])


def parsing_cv(file_content, model, status_obj):
    chain = init_chain(model, PROMPT)
    document = ocr_pdf(file_content, status_obj)
    status_obj.write("👩‍💻 Analyzing the resume...")
    return chain.run({
        "resume": document,
        "example": OUTPUT_TEMPLATE,
        "template": DATA_TEMPLATE
    })
