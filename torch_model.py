import torch
from torchvision import transforms
from PIL import Image
import requests
from io import BytesIO
from scipy.spatial import distance
import numpy as np
import torch
from torchvision import models

# Load the pre-trained Vision Transformer model
model = models.vit_b_16(pretrained=True)
model.eval()  # Set to evaluation mode

# Modify the model to remove the classification head and adjust the final layer
# Assume the last block output is what we need
model = torch.nn.Sequential(
    model,
    torch.nn.Flatten()  # Flatten the output to create a single feature vector
)

def preprocess_image(img_link):
    # Define the transformation pipeline for the images
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])


    response = requests.get(img_link)
    img = Image.open(BytesIO(response.content))
    # Apply the transformation pipeline
    img_tensor = transform(img)
    return img_tensor.unsqueeze(0)

def extract_features(img_link):
    # Preprocess the image
    img_tensor = preprocess_image(img_link)
    
    # Disable gradient computation for inference
    with torch.no_grad():
        features = model(img_tensor)
    return features.squeeze().numpy()


def find_closest_image(new_features, features_list, mapping):
    distances = [distance.euclidean(new_features, features) for features in features_list]
    closest_index = np.argmin(distances)  # Get the index of the smallest distance
    return mapping[closest_index]