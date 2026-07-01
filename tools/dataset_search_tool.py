import os
import json
from google.adk.tools import ToolContext
from google import genai

# Cache the index in memory across tool calls
_SCHEME_INDEX = None

def load_index():
    global _SCHEME_INDEX
    if _SCHEME_INDEX is not None:
        return _SCHEME_INDEX
        
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    index_path = os.path.join(project_root, "data", "scheme_index.json")
    
    if not os.path.exists(index_path):
        return []
        
    try:
        with open(index_path, "r", encoding="utf-8") as f:
            _SCHEME_INDEX = json.load(f)
    except Exception as e:
        print(f"Error loading scheme index: {e}")
        return []
        
    return _SCHEME_INDEX

def cosine_similarity(v1, v2):
    dot_product = sum(x * y for x, y in zip(v1, v2))
    norm_v1 = sum(x * x for x in v1) ** 0.5
    norm_v2 = sum(x * x for x in v2) ** 0.5
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
    return dot_product / (norm_v1 * norm_v2)

def normalize_state(state_name: str) -> str:
    if not state_name:
        return ""
    return state_name.lower().replace(" ", "-").replace("_", "-").strip()

def dataset_search(query: str, tool_context: ToolContext) -> str:
    """
    Query the local database of Indian government schemes for details and guidelines.
    
    Args:
        query: The search terms or questions to look up in the local schemes database.
        tool_context: Injected context to retrieve the user's profile state.
        
    Returns:
        A list of top relevant scheme details, eligibility guidelines, and benefit descriptions.
    """
    # 1. Load the precompiled scheme index
    index = load_index()
    if not index:
        return "Error: Local scheme database index is not built. Please run index_data.py first."
        
    # 2. Extract the user's state from the session profile state
    state_filter = None
    user_profile = tool_context.state.get("user_profile", {})
    if isinstance(user_profile, dict):
        state_filter = user_profile.get("state")
        
    if state_filter:
        state_filter = normalize_state(state_filter)
        
    # 3. Filter documents (only include central schemes or matching state schemes)
    filtered_docs = []
    for doc in index:
        doc_state = normalize_state(doc.get("state", ""))
        if doc_state == "central" or (state_filter and doc_state == state_filter):
            filtered_docs.append(doc)
            
    # Fallback to central schemes if filtering yielded nothing
    if not filtered_docs:
        filtered_docs = [doc for doc in index if normalize_state(doc.get("state")) == "central"]
        
    if not filtered_docs:
        return "No schemes found in the database matching your criteria."
        
    # 4. Generate embedding for the search query
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "Error: GEMINI_API_KEY environment variable is not set."
        
    client = genai.Client(api_key=api_key)
    try:
        response = client.models.embed_content(
            model="gemini-embedding-2",
            contents=query
        )
        query_vector = response.embeddings[0].values
    except Exception as e:
        return f"Error calling Gemini Embedding API: {e}"
        
    # 5. Compute cosine similarities
    scored_docs = []
    for doc in filtered_docs:
        doc_emb = doc.get("embedding")
        if not doc_emb:
            continue
        sim = cosine_similarity(query_vector, doc_emb)
        scored_docs.append((sim, doc))
        
    # 6. Sort by similarity score descending and return top 5
    scored_docs.sort(key=lambda x: x[0], reverse=True)
    top_results = scored_docs[:5]
    
    output_parts = []
    for sim, doc in top_results:
        state_name = doc['state'].capitalize()
        link_str = f"Official Website: {doc['link']}" if doc['link'] else "Official Website: Not Available"
        output_parts.append(
            f"Scheme Name: {doc['title']}\n"
            f"State/Scope: {state_name}\n"
            f"Similarity Score: {sim:.4f}\n"
            f"Details: {doc['content'].strip()}\n"
            f"{link_str}\n"
            f"{'-'*40}"
        )
        
    return "\n\n".join(output_parts)
