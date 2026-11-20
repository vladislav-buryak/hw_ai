import os
import pymupdf
import chromadb
from sentence_transformers import SentenceTransformer
import ollama

# Налаштування моделі Ollama (зміни на "llama3", якщо використовуєш її замість "qwen2.5")
OLLAMA_MODEL = "qwen2.5"
DOCS_FOLDER = "./base"
CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "local_knowledge_base"

print("Завантаження моделі ембеддингів...")
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

chromadb_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chromadb_client.get_or_create_collection(name=COLLECTION_NAME)


def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    try:
        with pymupdf.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text() + "\n"
    except Exception as e:
        print(f"[Error] Не вдалося прочитати PDF {pdf_path}: {e}")
    return text


def index_documents():
    if not os.path.exists(DOCS_FOLDER):
        os.makedirs(DOCS_FOLDER)
        print(f"Створено папку {DOCS_FOLDER}. Додайте туди файли та перезапустіть скрипт.")
        return

    added_count = 0
    for filename in os.listdir(DOCS_FOLDER):
        file_path = os.path.join(DOCS_FOLDER, filename)
        if not os.path.isfile(file_path):
            continue

        doc_id = f"file_{filename}"
        existing = collection.get(ids=[doc_id])
        if existing and existing["ids"]:
            continue

        file_content = ""
        if filename.endswith(".pdf"):
            file_content = extract_text_from_pdf(file_path)
        elif filename.endswith((".txt", ".md")):
            with open(file_path, "r", encoding="utf-8") as f:
                file_content = f.read()
        else:
            continue

        file_content = file_content.strip()
        if not file_content:
            print(f"[Skip] Файл {filename} порожній.")
            continue

        vector = embedding_model.encode([file_content]).tolist()
        collection.add(
            documents=[file_content],
            embeddings=vector,
            ids=[doc_id],
            metadatas=[{"source": filename}],
        )
        added_count += 1
        print(f"[+] Проіндексовано: {filename}")

    print(f"Всього документів у базі: {collection.count()} (нових: {added_count})\n")


def ask_rag(user_query: str):
    query_embedding = embedding_model.encode([user_query]).tolist()
    results = collection.query(query_embeddings=query_embedding, n_results=2)

    retrieved_chunks = results["documents"][0]
    sources = results["metadatas"][0]

    print("\n--- Знайдені джерела ---")
    for i, meta in enumerate(sources):
        print(f"[{i + 1}] {meta['source']}")

    context = "\n\n".join(retrieved_chunks)

    prompt = f"""Use ONLY the following contextual data from the files to answer the question.
If the context does not answer the question, say: "I don't have that information in my knowledge base."

Context:
{context}

User query:
{user_query}"""

    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a helpful corporate assistant that answers strictly based on the provided documents."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    print("\n" + "=" * 50)
    print("Відповідь моделі:")
    print("=" * 50)
    print(response["message"]["content"])
    print("=" * 50 + "\n")


if __name__ == "__main__":
    index_documents()

    if collection.count() == 0:
        print("База знань порожня. Спочатку запустіть create_docs.py!")
        exit()

    print("RAG-асистент готовий до роботи! (Введіть 'exit' для виходу)\n")
    while True:
        query = input("Ваш запит: ").strip()
        if not query:
            continue
        if query.lower() in ("exit", "quit", "q"):
            break
        ask_rag(query)