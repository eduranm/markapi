from huggingface_hub import login
from huggingface_hub import hf_hub_download


HF_TOKEN = 'INTRODUCE_TOKEN'

login(token=HF_TOKEN)

LLAMA_MODEL_DIR = "llama3/llama-3.2"
MODEL_LLAMA = "llama-3.2-3b-instruct-q4_k_m.gguf"
repo_id = 'hugging-quants/Llama-3.2-3B-Instruct-Q4_K_M-GGUF'
filename = MODEL_LLAMA
local_dir = LLAMA_MODEL_DIR

downloaded_file = hf_hub_download(repo_id=repo_id, filename=filename, local_dir=local_dir)