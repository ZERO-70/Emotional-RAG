from transformers import pipeline

# load emotion classification model once
emotion_classifier = pipeline("text-classification", model="cardiffnlp/twitter-roberta-base-emotion")

def detect_emotion(text: str) -> str:
    """
    Returns the dominant emotion label for the given text.
    """
    result = emotion_classifier(text)[0]
    return result["label"]
