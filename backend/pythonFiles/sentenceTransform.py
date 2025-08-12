from sentence_transformers import SentenceTransformer, util
import numpy as np
import json
import torch


model = SentenceTransformer('../my_model_dir')

with open("../data/output.json", "r") as file:
    data0 = json.load(file)


keys = list(data0.keys())



# Encode all documents
doc_embeddings = np.load("../data/doc_embeddings.npy")

# Query
query = input("What do you want to search: ")
query_embedding = model.encode(query, convert_to_tensor=True)
# Ensure query embedding is on CPU
query_embedding = query_embedding.cpu()

# Find similarity
cos_scores = util.pytorch_cos_sim(query_embedding, doc_embeddings)
top_k = 3
top_scores, top_indices = torch.topk(cos_scores, k=top_k)



cos_scores = cos_scores.flatten()

for data in top_indices[0]:
    key = keys[data]
    print("Similarity: " + str(float(cos_scores[data])))
    print(key)
    print(data0[key])
    print("-----------------------------------------------------------------")