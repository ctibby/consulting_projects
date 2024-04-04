from transformers import pipeline
from sklearn.metrics.pairwise import cosine_similarity
import torch
import numpy as np

def topic_similarity(article_text, topics_file='relevant_topics.txt', max_length=512):
    # Load topics
    with open(topics_file, 'r') as file:
        topics = file.readlines()
    topics = [topic.strip() for topic in topics]
    
    # Initialize the feature extraction pipeline
    feature_extraction = pipeline('feature-extraction', model='distilbert-base-uncased', tokenizer='distilbert-base-uncased')

    # Truncate the article text if it's too long
    inputs = feature_extraction.tokenizer(article_text, return_tensors="pt", truncation=True, max_length=max_length)
    article_vector = np.mean(feature_extraction.model(**inputs)[0].detach().numpy(), axis=1).reshape(1, -1)
    
    for topic in topics:
        topic_inputs = feature_extraction.tokenizer(topic, return_tensors="pt", truncation=True, max_length=max_length)
        topic_vector = np.mean(feature_extraction.model(**topic_inputs)[0].detach().numpy(), axis=1).reshape(1, -1)
        
        similarity = np.dot(article_vector, topic_vector.T) / (np.linalg.norm(article_vector) * np.linalg.norm(topic_vector))
        
        # If similarity is above a certain threshold, consider the article relevant
        if similarity >= 0.8:  # Adjust threshold as needed
            return True
    
    return False


def topic_similarity_with_keyword_check(article_text, topics_file='relevant_topics.txt'):
    # Load topics
    with open(topics_file, 'r') as file:
        topics = file.readlines()
    topics = [topic.strip().lower() for topic in topics]

    # Check for direct keyword match
    article_text_lower = article_text.lower()
    for topic in topics:
        if topic in article_text_lower:
            return True

    # If no direct match, proceed with semantic similarity (or any other advanced method you intend to use)
    # Example semantic similarity check (place your existing method here)
    # This part is optional and can be adjusted based on your needs
    similarity_check_passed = topic_similarity(article_text)
    if similarity_check_passed:
        return True

    # If no matches found
    return False
