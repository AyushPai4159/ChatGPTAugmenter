from sentence_transformers import SentenceTransformer
import json





model = SentenceTransformer('paraphrase-MiniLM-L6-v2')  # or your fine-tuned model




# Encode all documents



# Save entire model to local directory
model.save('../my_model_dir')