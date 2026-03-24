from langchain_community.vectorstores import Chroma
from app.services.embeddings import DashScopeEmbeddings
from typing import List, Dict, Any
import os
from config.settings import FULL_CAT_VECTOR_STORE_PERSIST_DIR

class FullCategoryVectorService:
    def __init__(self):
        self.embeddings = DashScopeEmbeddings()
        self.persist_directory = FULL_CAT_VECTOR_STORE_PERSIST_DIR
        self.vectorstore = None

    def create_index(self, texts: List[str], metadatas: List[Dict[str, Any]]):
        self.vectorstore = Chroma.from_texts(
            texts=texts,
            embedding=self.embeddings,
            metadatas=metadatas,
            persist_directory=self.persist_directory
        )
        self.vectorstore.persist()

    def load_index(self) -> bool:
        if os.path.exists(self.persist_directory):
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            return True
        return False

    def search_similar(self, query: str, k: int = 5) -> List[Dict[str, Any]]:   
        if not self.vectorstore:
            raise ValueError("Full category vectorstore not initialized.")
        results = self.vectorstore.similarity_search_with_score(query, k=k)
        # 打印前几个距离值，调试用
        for i, (doc, distance) in enumerate(results[:3]):
            print(f"DEBUG: 第{i+1}个结果距离 = {distance}")
        formatted = []
        for doc, distance in results:
            similarity = 1 / (1 + distance)
            formatted.append({
                "metadata": doc.metadata,
                "score": similarity,
                "text": doc.page_content
            })
        return formatted