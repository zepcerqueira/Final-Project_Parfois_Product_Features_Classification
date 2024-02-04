import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import urllib.parse
import os
from urllib.parse import urlparse
import requests

def standardise_file_names(filename):
    match = re.match(r'^([^_]+_[^_]+)', filename)
    if match:
        return match.group(1)
    else:
        return filename

def main():
    current_directory = os.getcwd()
    web_image_collector = os.path.join(current_directory, "web_image_collector")
    web_image_collector_2 = os.path.join(web_image_collector, "product_ref")
    product_ref_path = os.path.join(web_image_collector_2, "product_ref.xlsx")

    if not os.path.exists(product_ref_path):
        print("File Error: The file does not exist.", product_ref_path)
        exit()
    try:
        product_ref_df = pd.read_excel(product_ref_path)
    except Exception as e:
        print("Error reading the Excel file:", e)
        exit()

    page_url_01_list = []

    for index, row in product_ref_df.iterrows():
        product_ref = row["prod_ref"]
        page_url_01 = f"https://www.parfois.com/pt/pt/search/?q={product_ref}&lang=pt_PT"
        page_url_01_list.append(page_url_01)

    save_dir = os.path.join(web_image_collector, "downloaded_images")
    os.makedirs(save_dir, exist_ok=True)

    for page_url_01 in page_url_01_list:
        response_page_url_01 = requests.get(page_url_01)
        soup_page_numbers = BeautifulSoup(response_page_url_01.content, 'html.parser')

        parfois_components = soup_page_numbers.find_all("div", class_="full-width clearfix")
        for component in parfois_components:
            parfois_components2 = component.find_all("div", class_="pdp-main")  # ok

            for component in parfois_components2:
                parfois_components3 = component.find_all("div", class_="product-col-1")  # ok

                for component in parfois_components3:
                    parfois_components4 = component.find_all("div", class_="product-thumbnails")  # ok

                    for component in parfois_components4:
                        parfois_components5 = component.find_all("div", class_="vertical-carousel")  # ok

                        for component in parfois_components5:
                            img_tags = component.find_all("li", class_="thumb")  # ok

                            for li_tag in img_tags:
                                img_tag = li_tag.find("img", class_="productthumbnail seleccionada")
                                if img_tag:
                                    img_url = img_tag["data-hi-res"]
                                    img_name = os.path.basename(urlparse(img_url).path)
                                    img_path = os.path.join(save_dir, img_name)

                                    response = requests.get(img_url)
                                    with open(img_path, "wb") as img_file:
                                        img_file.write(response.content)

    existing_images = set(os.listdir(save_dir))
    image_downloaded_ref = pd.DataFrame(existing_images)
    image_downloaded_ref.rename(columns={0: "image_file_name"}, inplace=True)

    image_downloaded_ref["image_file_name"] = image_downloaded_ref["image_file_name"].apply(standardise_file_names)
    image_downloaded_ref = image_downloaded_ref.drop_duplicates(subset="image_file_name").reset_index(drop=True)

    product_ref_df["image_download_check"] = product_ref_df["prod_ref"].isin(image_downloaded_ref["image_file_name"]).astype(int)

if __name__ == "__main__":
    main()
