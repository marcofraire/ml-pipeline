import numpy as np
import requests
from io import BytesIO
from PIL import Image
from bs4 import BeautifulSoup
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing import image

def _preprocess_image(image_link):
   response = requests.get(image_link)
   img = Image.open(BytesIO(response.content))
   img = img.resize((224, 224))
   img_array = image.img_to_array(img)
   img_array = np.expand_dims(img_array, axis=0)
   img_array = preprocess_input(img_array)
   return img_array

def image_binary_classifier(model_path, image_link, threshold = 0.5):
      model = load_model(model_path)
      img_array = _preprocess_image(image_link)

      prediction = model.predict(img_array)

      is_positive = (prediction > threshold)[0][0]
      return is_positive, prediction[0][0]