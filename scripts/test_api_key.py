from google import genai

client = genai.Client()

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Explain first RAG and then GraphRAG in a few words.",
)
print(response.text)
