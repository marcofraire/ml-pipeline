

import torch
from blob import download_model_from_blob
import torch.nn as nn
import torch.nn.functional as F

def load_model(model, model_path):
    model.load_state_dict(torch.load(model_path))
    model.eval()  
    print('Model loaded and set to evaluation mode')
    return model



# Define the model class (should match the training time definition)
class ClassificationModel(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(ClassificationModel, self).__init__()
        self.fc1 = nn.Linear(input_dim, 512)
        self.fc2 = nn.Linear(512, 256)
        self.fc3 = nn.Linear(256, output_dim)
    
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x

def get_model(connecton_string):
    input_dim = 1768  # Number of features
    output_dim = 3    # Number of classes

    # Initialize the model
    model = ClassificationModel(input_dim, output_dim)
    model.eval()
    # Azure Blob Storage configuration
    container_name = 'ml-models'
    blob_name = 'is_book_ml_21-05-2024.pth'
    download_file_path = 'is_book_ml_21-05-2024.pth'

    # Download the model from Azure Blob Storage
    download_model_from_blob(connecton_string, container_name, blob_name, download_file_path)

    # Load the model
    model = load_model(model, download_file_path)
    return model


