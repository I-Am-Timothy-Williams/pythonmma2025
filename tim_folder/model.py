from sentence_transformers import SentenceTransformer, util


model = SentenceTransformer('paraphrase-mpnet-base-v2')

job_descriptions = [
    "Software Engineer position with experience in Python and machine learning",
    "Data Scientist role involving analysis of large datasets using SQL and Python",
    "Product Manager position focusing on product development and market research"
]


embeddings = model.encode(job_descriptions, convert_to_tensor=True)

# Calculate cosine similarity between each pair of job descriptions
similarity_scores = util.pytorch_cos_sim(embeddings, embeddings)

# Print similarity scores
for i in range(len(job_descriptions)):
    for j in range(i+1, len(job_descriptions)):
        print(f"Similarity between job description {i+1} and job description {j+1}: {similarity_scores[i][j].item()}")


