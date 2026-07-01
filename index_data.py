import os
import glob
import json
import time
from google import genai

def parse_scheme_file(file_path, data_dir):
    # Determine the state/scope from the parent folder name
    rel_path = os.path.relpath(file_path, data_dir)
    state = os.path.dirname(rel_path).lower().strip()
    
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = [line.strip() for line in f.readlines()]
        
    non_empty = [line for line in lines if line]
    if not non_empty:
        return None
        
    title = non_empty[0]
    
    link = ""
    content_lines = []
    for line in non_empty[1:]:
        if "Official Website:" in line:
            parts = line.split("Official Website:", 1)
            link = parts[1].strip()
        elif line.startswith("http://") or line.startswith("https://"):
            link = line.strip()
        else:
            content_lines.append(line)
            
    content = "\n".join(content_lines)
    
    # Construct search passage
    passage = f"Title: {title}\nState: {state.capitalize()}\nContent: {content}"
    
    return {
        "state": state,
        "title": title,
        "content": content,
        "link": link,
        "passage": passage
    }

from google.genai import types

def embed_with_retry(client, passages, max_retries=5):
    delay = 2
    content_objects = [
        types.Content(parts=[types.Part.from_text(text=p)])
        for p in passages
    ]
    for i in range(max_retries):
        try:
            response = client.models.embed_content(
                model="gemini-embedding-2",
                contents=content_objects
            )
            return [emb.values for emb in response.embeddings]
        except Exception as e:
            if i == max_retries - 1:
                raise e
            print(f"Error embedding batch (retry {i+1}/{max_retries} in {delay}s): {e}")
            time.sleep(delay)
            delay *= 2

def build_index():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "data")
    output_path = os.path.join(data_dir, "scheme_index.json")
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is not set!")
        return

    client = genai.Client(api_key=api_key)
    
    # 1. Parse all documents
    print("Scanning and parsing scheme files...")
    txt_files = glob.glob(os.path.join(data_dir, "**/*.txt"), recursive=True)
    
    docs = []
    for file_path in txt_files:
        # Skip macOS AppleDouble metadata files
        if os.path.basename(file_path).startswith("._"):
            continue
        doc = parse_scheme_file(file_path, data_dir)
        if doc:
            docs.append(doc)
            
    total_docs = len(docs)
    print(f"Parsed {total_docs} valid documents.")
    
    # 2. Embed passages in batches of 100
    batch_size = 100
    all_embeddings = []
    
    print("Generating embeddings using gemini-embedding-2...")
    for idx in range(0, total_docs, batch_size):
        batch = docs[idx : idx + batch_size]
        passages = [doc["passage"] for doc in batch]
        
        print(f"Embedding batch {idx // batch_size + 1} ({idx} to {min(idx + batch_size, total_docs)})...")
        try:
            vectors = embed_with_retry(client, passages)
            all_embeddings.extend(vectors)
        except Exception as e:
            print(f"Failed to generate embeddings: {e}")
            return
            
    # Combine docs with their corresponding embeddings
    for doc, emb in zip(docs, all_embeddings):
        doc["embedding"] = emb
        
    # 3. Save index as JSON
    print(f"Saving search index to {output_path}...")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)
        
    print("Index build completed successfully!")

if __name__ == "__main__":
    build_index()
