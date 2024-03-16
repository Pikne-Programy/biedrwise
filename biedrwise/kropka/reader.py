import re
import cv2
import pytesseract
import numpy as np
from skimage.filters import threshold_local
from pytesseract import Output
from pdf2image import convert_from_path

def is_number(line) -> bool:
    return line.replace(",", "").isdigit()


def read(file) -> dict:
    # file = "paragon.jpg"
    file = convert_from_path(file, 500)
    image = cv2.imread(file, cv2.IMREAD_GRAYSCALE)
    extracted_text = pytesseract.image_to_string(image, lang="pol", config="--psm 6")
    # print(extracted_text)
    idx = extracted_text.find("Wartość")
    idx_end = extracted_text.find("Sprzedaż")
    new_text = extracted_text[idx+8:idx_end]
    # print(new_text)
    lines = new_text.split("\n")
    # print(lines)
    res = {}
    for idx, line in enumerate(lines):
        if "Rabat" in line or is_number(line) or not len(line):
            continue

        if (
            idx < len(lines) - 1
            and "Rabat" in lines[idx + 1]
            and is_number(lines[idx + 2])
        ):
            product_name = line.split(" ")[0]
            price = lines[idx + 2].replace(",", ".")
            if product_name in res:
                res[product_name] += float(price)
            else:
                res[product_name] = float(price)
        else:
            product_name = line.split(" ")[0]
            price = line.split(" ")[-1].replace(",", ".")
            if product_name in res:
                res[product_name] += float(price)
            else:
                res[product_name] = float(price)
    # print(res)            
    return res
