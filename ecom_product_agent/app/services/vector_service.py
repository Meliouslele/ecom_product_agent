from langchain_community.vectorstores import Chroma
from app.services.embeddings import DashScopeEmbeddings
from typing import List, Dict, Any
import os
from config.settings import VECTOR_STORE_PERSIST_DIR

class VectorService:
    def __init__(self):
        self.embeddings = DashScopeEmbeddings()  # 使用千问 Embedding
        self.persist_directory = VECTOR_STORE_PERSIST_DIR
        self.vectorstore = None

    def create_index(self, texts: List[str], metadatas: List[Dict[str, Any]]):
        """从自有商品池创建向量索引"""
        self.vectorstore = Chroma.from_texts(
            texts=texts,
            embedding=self.embeddings,
            metadatas=metadatas,
            persist_directory=self.persist_directory
        )
        self.vectorstore.persist()

    def load_index(self) -> bool:
        """加载已存在的索引"""
        if os.path.exists(self.persist_directory):
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            return True
        return False

    def search_similar(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        if not self.vectorstore:
            raise ValueError("Vectorstore not initialized.")
        results = self.vectorstore.similarity_search_with_score(query, k=k)
        formatted_results = []
        for doc, distance in results:  # 注意：这里是距离，不是相似度
            # 将距离转换为相似度，范围 (0,1]，距离为0时相似度为1
            similarity = 1 / (1 + distance)
            formatted_results.append({
                "metadata": doc.metadata,
                "score": similarity,
                "text": doc.page_content
            })
        return formatted_results