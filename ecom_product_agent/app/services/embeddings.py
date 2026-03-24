from langchain_core.embeddings import Embeddings
import dashscope
from typing import List
import logging
from config.settings import DASHSCOPE_API_KEY, EMBEDDING_MODEL_NAME

logger = logging.getLogger(__name__)

# 设置 API Key
dashscope.api_key = DASHSCOPE_API_KEY

class DashScopeEmbeddings(Embeddings):
    """使用阿里云通义千问 Embedding API 的 LangChain Embeddings 包装类"""

    def __init__(self, model: str = EMBEDDING_MODEL_NAME):
        self.model = model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """为文档列表生成 embeddings"""
        embeddings = []
        for text in texts:
            try:
                resp = dashscope.TextEmbedding.call(
                    model=self.model,
                    input=text,
                    text_type="document"  # 文档类型
                )
                if resp.status_code == 200:
                    # 返回的 embedding 是一个列表的列表，每个元素对应一个输入文本
                    embeddings.append(resp.output['embeddings'][0]['embedding'])
                else:
                    logger.error(f"Embedding API 调用失败: {resp.code} - {resp.message}")
                    raise Exception(f"Embedding API 调用失败: {resp.code} - {resp.message}")
            except Exception as e:
                logger.exception("生成 embedding 失败")
                raise
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        try:
            resp = dashscope.TextEmbedding.call(
                model=self.model,
                input=text,
                text_type="query"
            )
            if resp.status_code == 200:
                vec = resp.output['embeddings'][0]['embedding']
                print(f"DEBUG: 向量长度={len(vec)}, 前5个值={vec[:5]}")  # 临时调试
                return vec
            else:
                logger.error(f"Embedding API 调用失败: {resp.code} - {resp.message}")
                raise Exception(f"Embedding API 调用失败: {resp.code} - {resp.message}")
        except Exception as e:
            logger.exception("生成 embedding 失败")
            raise