from transformers import AutoTokenizer, AutoModel
import torch
text_model_name = "roberta-base"
tokenizer = AutoTokenizer.from_pretrained(text_model_name)
text_model = AutoModel.from_pretrained(text_model_name)

def extract_text_features(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)

    # Get the outputs from the model
    with torch.no_grad():
        outputs = text_model(**inputs)

    # Extract the last hidden state
    features = outputs.last_hidden_state

    # Use the [CLS] token representation (assuming it's the first token)
    cls_features = features[:, 0, :].numpy().flatten()
    return cls_features