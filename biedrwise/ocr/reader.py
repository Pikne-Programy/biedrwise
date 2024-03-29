import cv2
import pytesseract
from pdf2image import convert_from_path
from sys import stderr
from pathlib import Path


def is_number(line) -> bool:
    return line.replace(",", "").isdigit()


def pdf_to_img(filename):
    img = convert_from_path(filename, 500)
    path = f"{filename}.png"
    img[0].save(path, "PNG")
    return path


def ocr_read(filenane: str, pdf: bool) -> dict:
    if pdf:
        filenane = pdf_to_img(filenane)
    image = cv2.imread(filenane, cv2.IMREAD_GRAYSCALE)
    extracted_text = pytesseract.image_to_string(image, lang="pol", config="--psm 6")
    idx = extracted_text.find("Wartość")
    idx_end = extracted_text.find("Sprzedaż")
    new_text = extracted_text[idx + 8 : idx_end]
    lines = new_text.split("\n")
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
            if is_number(product_name[0]):
                continue
            cnt = line.split(" ")[-4]
            price = lines[idx + 2].replace(",", ".")
            price = price.replace("-", ".")
            print(product_name, price, cnt)
            if product_name in res:
                new_price = res[product_name][0] + float(price)
                new_cnt = res[product_name][1] + float(cnt)
                res[product_name] = (new_price, new_cnt)
            else:
                res[product_name] = (float(price), float(cnt))
        else:
            product_name = line.split(" ")[0]
            if is_number(product_name[0]):
                continue
            price = line.split(" ")[-1].replace(",", ".")
            price = price.replace("-", ".")
            cnt = line.split(" ")[-4]
            print(product_name, price, cnt)
            if product_name in res:
                new_price = res[product_name][0] + float(price)
                new_cnt = res[product_name][1] + float(cnt)
                res[product_name] = (new_price, new_cnt)
            else:
                res[product_name] = (float(price), float(cnt))
    return res
