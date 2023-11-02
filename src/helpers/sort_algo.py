from __future__ import annotations
from collections import deque
from typing import List, Dict
from functools import lru_cache

import io

import pdfplumber as plumber


LINE_HEIGHT_DIFF = (5, 30)
LEFT_X_DIFF = 5
LEFT_Y_DIFF = 20


def sort_horizontal(
    ocr_result: List[Dict[str, str | float | int | bool]]
) -> Dict[str, str | float | int]:
    """
    Sorting the OCR Result dictionary based on horizontal coordinates using the top-bottom values

    Args:
        ocr_result (List[Dict[str, str  |  float  |  int  |  bool]]): the ocr result using pdfplumber as backbone to parse

    Returns:
        Dict[str, str | float | int]: a dictionary contains all the text and coordinates after grouping them based on top-bottom values
    """
    result = {}

    for data in ocr_result:
        x0, x1, top, bottom = data["x0"], data["x1"], data["top"], data["bottom"]
        text = data["text"]

        top_left = [x0, bottom]  # x0, y1
        top_right = [x1, bottom]  # x1, y1
        bottom_left = [x0, top]  # x0, y0
        bottom_right = [x1, top]  # x1, y0

        if (top, bottom) in result:
            result[(top, bottom)]["text"] += f" {text}"
            result[(top, bottom)]["top_right"] = top_right
        else:
            result[(top, bottom)] = {
                "text": text,
                "top_left": top_left,
                "top_right": top_right,
                "bottom_left": bottom_left,
            }

        result[(top, bottom)]["bottom_right"] = bottom_right
    return result


def sort_vertical(input_dicts: Dict[str, str | float | int]) -> List[str]:
    """
    Sorts the input dictionary values vertically based on their position on the page.

    Args:
        input_dicts (Dict[str, Union[str, float, int]]): A dictionary containing the text and position of each element.

    Returns:
        List[str]: A list of strings containing the sorted text elements.
    """
    result = []
    remain = deque(input_dicts.values())
    remove_indices = set()

    while remain:
        current_value = remain.popleft()
        current_text = current_value["text"]
        current_top_left = current_value["top_left"]
        current_bottom_left = current_value["bottom_left"]

        for i, value in enumerate(remain):
            line_height_diff = [
                abs(current_bottom_left[0] - value["top_left"][0]),
                abs(current_bottom_left[1] - value["top_left"][1]),
            ]
            diff_top_left_x, diff_top_left_y = abs(
                current_top_left[0] - value["top_left"][0]
            ), abs(current_top_left[1] - value["top_left"][1])
            diff_bottom_left_x, diff_bottom_left_y = abs(
                current_bottom_left[0] - value["bottom_left"][0]
            ), abs(current_bottom_left[1] - value["bottom_left"][1])

            if (
                (line_height_diff[0] <= 5 and line_height_diff[1] <= 30)
                and (diff_top_left_x <= 5 and diff_top_left_y <= 20)
                and (diff_bottom_left_x <= 5 and diff_bottom_left_y <= 20)
            ):
                current_text += f" \n {value['text']}"
                current_top_left = value["top_left"]
                current_bottom_left = value["bottom_left"]
                remove_indices.add(i)

        remain = deque(val for i, val in enumerate(remain) if i not in remove_indices)
        remove_indices.clear()
        result.append(current_text)

    return result

@lru_cache
def read_pdf(file_content: bytes) -> List[Dict[str, str | float | int | bool]]:
    """
    Reads a PDF file and extracts text from it using OCR.

    Args:
        file_content (bytes): The content of the PDF file.

    Returns:
        List[Dict[str, str | float | int | bool]]: A list of dictionaries, where each dictionary represents a page in the PDF file and contains the extracted text.
    """

    ocr_result = []

    with plumber.open(io.BytesIO(file_content)) as pdf:
        for page in pdf.pages:
            output = page.dedupe_chars().extract_words(x_tolerance=2, y_tolerance=2)
            ocr_result.append(output)

    return ocr_result

def ocr_cv(file_content: bytes) -> List[str]:
    """
    Parses a CV file and extracts text from it using OCR.

    Args:
        file_content (bytes): The content of the CV file.

    Returns:
        List[str]: A list of strings containing the extracted text.
    """

    ocr_result = read_pdf(file_content)
    
    result = []
    for page in ocr_result:
        sorted_horizontal = sort_horizontal(page)
        sorted_vertical = sort_vertical(sorted_horizontal)
        result.extend(sorted_vertical)


    return "\n".join(result)