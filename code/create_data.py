import os
import pandas as pd
import numpy as np
import glob
from PIL import Image
from sklearn.model_selection import train_test_split


def create_dataset(path_csv):
    """ Clean data by dropping unnecessary entries and filtering
        the categories"""

    # create dataframe, include only lines without errors
    data = pd.read_csv(path_csv, delimiter=",", on_bad_lines="skip")

    # Drop features not needed for analysis
    data = data.drop(["year", "usage", "productDisplayName",
                      "masterCategory", "subCategory"], axis=1)

    # Rename the id column to image_id
    data = data.rename(columns={"id": "image_id"})

    # List of article categories
    article_categories = ["Shirts", "Jeans", "Track Pants",
                          "Tshirts", "Casual Shoes", "Tops",
                          "Sandals", "Sweatshirts", "Formal Shoes",
                          "Waistcoat", "Sports Shoes", "Shorts",
                          "Heels", "Innerwear Vests", "Rain Jacket",
                          "Dresses", "Skirts", "Blazers",
                          "Shrug", "Trousers", "Jackets", "Sports Sandals",
                          "Sweaters", "Tracksuits",
                          "Leggings", "Jumpsuit", "Robe",
                          "Salwar and Dupatta", "Kurtas", "Sarees"]
    # List of colors
    # For future color prediction purposes. At the moment, we are only using
    # article categories (clothing types) in our modell
    # For color prediction, we are using the color entries of the csv data at the moment"""
    color_names = ["Navy Blue", "Blue", "Silver",
                   "Black", "Grey", "Green",
                   "Purple", "White", "Beige",
                   "Brown", "Bronze", "Teal",
                   "Copper", "Pink", "Off White",
                   "Maroon", "Red", "Khaki",
                   "Orange", "Coffee Brown",
                   "Yellow", "Charcoal", "Gold",
                   "Steel", "Tan", "Multi", "Magenta",
                   "Lavender", "Sea Green", "Cream",
                   "Peach", "Olive", "Skin", "Burgundy",
                   "Grey Melange", "Rust", "Rose",
                   "Lime Green", "Mauve", "Turquoise Blue",
                   "Metallic", "Mustard", "Taupe",
                   "Nude", "Mushroom Brown", "Fluorescent Green"]

    # Filter the data to only include entries where
    # articleType is in article_categories
    data = data.loc[data["articleType"].isin(article_categories)]

    # Delete rows that are not in color_names
    data = data.loc[data["baseColour"].isin(color_names)]

    # Drop any rows with missing values
    data = data.dropna()
    return data


def train_test(path_image, label_data, label_name):
    """ Convert images and one hot encoded labels to numpy arrays
        to create train and test datasets and normalize the values"""

    images_np = np.array(images)
    one_hot_labels = None

    if label_name == "article":
        # Read in the article labels and perform one-hot encoding
        df = pd.DataFrame({"label": label_data})
        one_hot_labels = pd.get_dummies(df["label"])
    elif label_name == "color":
        # Read in the color labels and perform one-hot encoding
        df = pd.DataFrame({"label": label_data})
        one_hot_labels = pd.get_dummies(df["label"])

    # Convert the one hot encoded labels to numpy arrays
    labels_np = one_hot_labels.to_numpy()

    # train-test-split
    X_train, X_test, y_train, y_test = train_test_split(images_np,
                                                        labels_np,
                                                        test_size=0.2,
                                                        random_state=0,
                                                        shuffle=True)
    # normalization of RGB values
    X_train, X_test = X_train / 255.0, X_test / 255.0
    return X_train, X_test, y_train, y_test


images = []
lable_list = []


def convert_image_to_array_endlist(path_image, data, label_name):
    """ This function takes the arguments "path_image" and data.
        Within the function, it uses the glob library to get
        all the jpg images in the given path, enumerates through them,
        extracts the image id from the filename, uses that id to find
        the corresponding entry in a dataframe, opens the image using
        the Image module and converts it to a numpy array. If the image
        shape is (384,256,3) then it appends the image and the corresponding
        article type to the "images" and "lable_article" lists respectively.
        It returns the "images" and "lable_article" lists."""

    for i, filename in enumerate(glob.glob(f"{path_image}*.jpg")):

        # Extract the image id from the filename
        image_id = int(filename.split("\\")[-1].split(".")[0])

        # Use the image id to find the corresponding entry dataframe
        df_entry_with_maching_image_id = data[data["image_id"] == image_id]

        # If the entry is empty, continue to the next iteration
        if df_entry_with_maching_image_id.empty:
            continue
        # Open the image using the Image module and convert it to a numpy array
        image = Image.open(filename)
        image = np.array(image)

        # If the image size is correct, than add the lable to label_list
        if image.shape == (384, 256, 3):
            if label_name == "article":
                article_entry = df_entry_with_maching_image_id.iloc[0, 2]
                lable_list.append(article_entry)
            # For future purposes, if one will actually use a ML model to predict colors
            elif label_name == "color":
                colors_entry = df_entry_with_maching_image_id.iloc[0, 3]
                lable_list.append(colors_entry)
            images.append(image)
    return images, lable_list


# runs all of the functions above
if __name__ == "__main__":
    root = os.getcwd()
    path_csv = os.path.join(root, "styles.csv")
    # path_csv = "/Users/lizak/OneDrive/Desktop/myntradataset"
    path_image = "/Users/lizak/OneDrive/Desktop/myntradataset/images/"
    data = create_dataset(path_csv)
    images, lable_article = convert_image_to_array_endlist(path_image,
                                                           data, "article")
    images, lable_color = convert_image_to_array_endlist(path_image,
                                                         data, "color")
    X_train_article, X_test_article, y_train_article, y_test_article = train_test(images, lable_article, "article")
    X_train_color, X_test_color, y_train_color, y_test_color = train_test(images, lable_color, "color")
