import os
from dotenv import load_dotenv

load_dotenv()

# 阿里云通义千问 API 配置
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "your-api-key-here")
LLM_MODEL_NAME = "qwen-turbo"          # 可选: qwen-turbo, qwen-plus, qwen-max
EMBEDDING_MODEL_NAME = "text-embedding-v3"  # 千问 Embedding 模型

# 向量数据库配置
VECTOR_STORE_PERSIST_DIR = "./data/processed/chroma_db"
FULL_CAT_VECTOR_STORE_PERSIST_DIR = "./data/processed/full_category_chroma_db"

# 相似度阈值
SIMILARITY_THRESHOLD = 0.7

# 数据文件路径
OWN_POOL_CSV = "data/raw/own_product_pool.csv"
FULL_CATEGORY_CSV = "data/raw/full_category_products.csv"