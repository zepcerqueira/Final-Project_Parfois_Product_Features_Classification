import tensorflow as tf
import os
import cv2
import imghdr
import numpy as np
from matplotlib import pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Dense, Flatten, Dropout
from tensorflow.keras.metrics import Precision, Recall, BinaryAccuracy
from tensorflow.keras.models import load_model
from sklearn.metrics import confusion_matrix
import seaborn as sns
import pandas as pd
from mtcnn.mtcnn import MTCNN

def update_predictions(row):
    img_file_name = row["image_file_name"]
    img_path = os.path.join(images_to_check_folder, img_file_name)
    img_to_check = cv2.imread(img_path)

    if img_to_check is not None:
        resize = tf.image.resize(np.expand_dims(img_to_check, 0), (256, 256))[0]
        prediction = parfois_model_1.predict(np.expand_dims(resize / 255, 0))

        if prediction > 0.5:
            return 1
        else:
            return 0
    else:
        print(f"{img_file_name}: Unable to read the image")
        return None 
    

def model_predictions_2(row):
    img_file_name = row["image_file_name"]
    img_path = os.path.join(file_path, images_to_check_folder, img_file_name)
    img_to_check = cv2.imread(img_path)
    
    if img_to_check is not None:
        detected_faces = parfois_model_2.detect_faces(img_to_check)
        
        for face in detected_faces:
            if "keypoints" in face and "left_eye" in face["keypoints"] and "right_eye" in face["keypoints"] and "mouth_left" in face["keypoints"] and "mouth_right" in face["keypoints"]:
                return 1 
            if "keypoints" in face and "left_eye" in face["keypoints"] and "mouth_left" in face["keypoints"]:
                return 1  
            if "keypoints" in face and "right_eye" in face["keypoints"] and "mouth_right" in face["keypoints"]:
                return 1  
            if "keypoints" in face and "right_eye" in face["keypoints"]:
                return 1  
            if "keypoints" in face and "left_eye" in face["keypoints"]:
                return 1  
        return 0
    else:
        print(f"{img_file_name}: Unable to read the image")
        return -1
    
def filter_models_predictions(predictions_df):
    filtered_df = (
        predictions_df.sort_values("parfois_app_output", 
                       key=lambda x: x.map({"Recognition": 0, "No_Recognition": 1, "Product": 2}))
          .groupby("image_file_name")
          .first()
          .reset_index()
    )

    return filtered_df

if __name__ == "__main__":
    current_directory = os.getcwd()
    parent_directory = os.path.dirname(current_directory)
    model_folder = os.path.join(parent_directory, "model")
    model_path = os.path.join(model_folder, "parfois_product_feature_classification.h5")

    parfois_model_1 = load_model(model_path)
    parfois_model_2 = MTCNN(min_face_size=30, steps_threshold=[0.7, 0.8, 0.8])

    file_path = os.path.join(parent_directory, "studio_folder_check")
    file_path_2 = os.path.join(file_path, "product_ref_call")

    product_ref_path = os.path.join(file_path_2, "product_ref.xlsx")

    if not os.path.exists(product_ref_path):
        print("File Error: The file does not exist.", product_ref_path)
        exit()

    try:
        product_ref_df = pd.read_excel(product_ref_path)
    except Exception as e:
        print("Error reading the Excel file:", e)
        exit()

    downloaded_images_path = "studio_folder"
    images_to_check_folder = os.path.join(file_path, downloaded_images_path)
    images_to_check = set(os.listdir(images_to_check_folder))
    images_to_check = pd.DataFrame(images_to_check)
    images_to_check.rename(columns={0: "image_file_name"}, inplace=True)
    images_to_check["model_1_images_predictions"] = np.nan

    print("Model 01 for Product vs No_Recognition is running.")
    
    images_to_check["model_1_images_predictions"] = images_to_check.apply(update_predictions, axis=1)
    
    print("Model 02 for No_Recognition vs Recognition is running.")
    
    images_to_check["model_2_images_predictions"] = images_to_check.apply(model_predictions_2, axis=1)
    
    print("Model 01 and 02 run is completed.")

    images_to_check.loc[(images_to_check["model_1_images_predictions"] == 0) & (images_to_check["model_2_images_predictions"] == 0), "parfois_app_output"] = "Product"
    images_to_check.loc[(images_to_check["model_1_images_predictions"] == 1) & (images_to_check["model_2_images_predictions"] == 0), "parfois_app_output"] = "No_Recognition"
    images_to_check.loc[(images_to_check["model_1_images_predictions"] == 1) & (images_to_check["model_2_images_predictions"] == 1), "parfois_app_output"] = "Recognition"
    images_to_check.loc[(images_to_check["model_1_images_predictions"] == 0) & (images_to_check["model_2_images_predictions"] == 1), "parfois_app_output"] = "Recognition"

    images_to_check["image_file_name"] = images_to_check["image_file_name"].apply(lambda x: "_".join(x.split("_")[:2]))

    results_df = filter_models_predictions(images_to_check)

    results_df.sort_values(by="image_file_name").reset_index(drop=True)

    results_df.to_excel("studio_folder_check_updated.xlsx", index=False)

    print("Upgraded folder is done.")
