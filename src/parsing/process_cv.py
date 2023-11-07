import time
from langchain.prompts.prompt import PromptTemplate
from streamlit.logger import get_logger

from ..helpers.utils import init_chain
from ..helpers.sort_algo import extract_text_cv
from ..model.example_data import DATA_TEMPLATE, OUTPUT_TEMPLATE
from ..model.prompt_template import PARSING_CV_PROMPTING

LOGGER = get_logger(__name__)

PROMPT = PromptTemplate(
    input_variables=["resume", "example", "template"], template=PARSING_CV_PROMPTING
)


def parsing_cv (file_content, model, status_obj):
    t1 = time.perf_counter(), time.process_time()
    chain = init_chain(model, PROMPT)
    t2 = time.perf_counter(), time.process_time()
    LOGGER.info(f"Init Chain: Real time: {t2[0] - t1[0]:.2f} seconds, CPU time: {t2[1] - t1[1]:.2f} seconds")
    
    
    status_obj.write("📝 Extracting text...")
    t1 = time.perf_counter(), time.process_time()
    pages = extract_text_cv(file_content)
    t2 = time.perf_counter(), time.process_time()
    LOGGER.info(f"Extract Text: Real time: {t2[0] - t1[0]:.2f} seconds, CPU time: {t2[1] - t1[1]:.2f} seconds")
    
    
    status_obj.write("👩‍💻 Analyzing the resume...")
    t1 = time.perf_counter(), time.process_time()
    response = chain.run(
        {"resume": pages, "example": OUTPUT_TEMPLATE, "template": DATA_TEMPLATE}
    )
    t2 = time.perf_counter(), time.process_time()
    LOGGER.info(f"Run Chain: Real time: {t2[0] - t1[0]:.2f} seconds, CPU time: {t2[1] - t1[1]:.2f} seconds")
    
    return response
