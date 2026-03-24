from app.services.full_category_vector_service import FullCategoryVectorService
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class SimilaritySearcher:
    def __init__(self, full_category_vector_service: FullCategoryVectorService, own_product_pool_set: set):
        self.vector_service = full_category_vector_service
        self.own_pool_set = own_product_pool_set

    def search_similar_products(self, query_products: List[str], k: int = 5,
                                status_filter: str = None, exclude_own: bool = True) -> List[Dict[str, Any]]:
        """
        搜索与 query_products 相似的全类目商品
        """
        all_results = []
        seen_skus = set()

        for query in query_products:
            try:
                results = self.vector_service.search_similar(query, k=k)
                for res in results:
                    metadata = res["metadata"]
                    sku = metadata.get("sku")
                    # 去重
                    if sku in seen_skus:
                        continue
                    # 状态过滤
                    if status_filter and metadata.get("状态") != status_filter:
                        continue
                    # 排除自有池
                    if exclude_own and sku in self.own_pool_set:
                        continue
                    seen_skus.add(sku)
                    all_results.append({
                        "product_name": metadata.get("商品名称"),
                        "category": f"{metadata.get('一级类目')}/{metadata.get('二级类目')}/{metadata.get('三级类目')}",
                        "price": metadata.get("价格"),
                        "volume": metadata.get("成交量"),
                        "status": metadata.get("状态"),
                        "similarity_score": res["score"],
                        "matched_query": query
                    })
            except Exception as e:
                logger.error(f"搜索失败: {e}")
        # 按相似度排序
        all_results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return all_results