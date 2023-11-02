from langchain.chains import LLMChain
from langchain.prompts.prompt import PromptTemplate
from langchain.chat_models import ChatOpenAI
from ..model.example_data import DATA_TEMPLATE, OUTPUT_TEMPLATE
from ..model.prompt_template import PARSING_CV_PROMPTING

import streamlit as st

PROMPT = PromptTemplate(
    input_variables=["resume", "example", "template"],
    template=PARSING_CV_PROMPTING
)
CHAT = ChatOpenAI(
    model="gpt-3.5-turbo-16k",
    temperature=0.0,
    openai_api_key=st.secrets["openai_api_key"],
)
CHAIN = LLMChain(llm=CHAT, prompt=PROMPT)


def parsing_cv(file_content: str):
    return CHAIN.run(
        {"resume": file_content, "example": OUTPUT_TEMPLATE, "template": DATA_TEMPLATE}
    )
