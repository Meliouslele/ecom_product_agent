from app.services.vector_service import VectorService
from app.models.schemas import ProcessedProduct
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

class SimilarityMatcher:
    def __init__(self, vector_service: VectorService, similarity_threshold: float = 0.7):
        self.vector_service = vector_service
        self.similarity_threshold = similarity_threshold

    def find_similar_products(
        self,
        target_products: List[ProcessedProduct]
    ) -> List[Tuple[ProcessedProduct, dict, float]]:
        """
        为目标商品列表寻找相似的自有商品
        返回: [(目标商品, 相似的自有商品元数据, 相似度分数)]
        """
        results = []
        for product in target_products:
            if not product.keywords:
                continue
            query_text = " ".join(product.keywords)
            try:
                similar_items = self.vector_service.search_similar(query_text, k=1)
                if similar_items:
                    best_match = similar_items[0]
                    score = best_match["score"]  # 已经是相似度（1-distance）
                    if score >= self.similarity_threshold:
                        results.append((product, best_match["metadata"], score))
            except Exception as e:
                logger.error(f"相似度匹配失败: {e}")
        return results