import tiktoken

def count_tokens(text):
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(text)
    return len(tokens)

def chunk_text(text, max_tokens=8000):
    enc = tiktoken.get_encoding("cl100k_base")
    tokens = enc.encode(text)
    
    chunks = []
    while len(tokens) > max_tokens:
        chunk = tokens[:max_tokens]
        tokens = tokens[max_tokens:]
        chunks.append(enc.decode(chunk))
    
    if tokens:
        chunks.append(enc.decode(tokens))
    
    return chunks
