import time
from PyPDF2 import PdfReader
from langchain.prompts.prompt import PromptTemplate
from streamlit.logger import get_logger

from ..helpers.utils import init_chain
from ..helpers.sort_algo import extract_text_cv
from ..model.example_data import DATA_TEMPLATE, OUTPUT_TEMPLATE
from ..model.prompt_template import PARSING_CV_PROMPTING

LOGGER = get_logger(__name__)

PROMPT = PromptTemplate(
    input_variables=["resume", "example", "template"],
    template=PARSING_CV_PROMPTING
)


def extract_text_pdf(file, status_obj):
    status_obj.write("📝 Extracting text...")
    pdf_loader = PdfReader(file)
    page_text = [pdf_loader.pages[c].extract_text() for c in range(len(pdf_loader.pages))]
    #with concurrent.futures.ThreadPoolExecutor() as executor:
    #    page_text_futures = [executor.submit(lambda page: page.extract_text(), pdf_loader.pages[c]) for c in range(len(pdf_loader.pages))]
    #    page_text = [future.result() for future in concurrent.futures.as_completed(page_text_futures)]
    return page_text

async def chain_arun_async(chain, doc):
    response = await chain.arun({
        "resume": doc,
        "example": OUTPUT_TEMPLATE,
        "template": DATA_TEMPLATE
    })
    
    return response

async def parsing_cv_async(file_content, model, status_obj):
    chain = init_chain(model, PROMPT)
    
    t1 = time.perf_counter(), time.process_time()
    pages = extract_text_pdf(file_content, status_obj)
    t2 = time.perf_counter(), time.process_time()
    LOGGER.info(f"{extract_text_cv.__name__}: Real time: {t2[0] - t1[0]:.2f} seconds, CPU time: {t2[1] - t1[1]:.2f} seconds")
    status_obj.write("👩‍💻 Analyzing the resume...")
    
    t1 = time.perf_counter(), time.process_time()
    tasks = [chain_arun_async(chain, document) for document in pages]
    response = [await task for task in tasks]
    t2 = time.perf_counter(), time.process_time()
    LOGGER.info(f"Chain Extract: Real time: {t2[0] - t1[0]:.2f} seconds, CPU time: {t2[1] - t1[1]:.2f} seconds")
    return response
