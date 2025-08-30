from sentence_transformers import SentenceTransformer
import json
import numpy as np

with open("../data/output.json", "r") as file:
    data = json.load(file)


keys = list(data.keys())



model = SentenceTransformer('../my_model_dir')

doc_embeddings = model.encode(keys, convert_to_tensor=True).cpu()
np.save("../data/doc_embeddings.npy", doc_embeddings)