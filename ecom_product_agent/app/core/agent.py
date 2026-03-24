from app.core.keyword_extractor import KeywordExtractor
from app.core.similarity_matcher import SimilarityMatcher
from app.models.schemas import ProductInfo, ProcessedProduct
from typing import List

class ProductAnalysisAgent:
    def __init__(self, vector_service, similarity_threshold=0.7):
        self.keyword_extractor = KeywordExtractor()
        self.similarity_matcher = SimilarityMatcher(vector_service, similarity_threshold)

    def run(self, full_category_products: List[ProductInfo]) -> List[dict]:
        """
        执行完整的分析流程
        """
        # 步骤1: 筛选出入池商品
        in_pool_products = [p for p in full_category_products if p.status == "入池"]

        # 步骤2: 提取关键词
        processed_products = []
        for product in in_pool_products:
            keywords = self.keyword_extractor.extract(product.product_name)
            processed = ProcessedProduct(**product.dict(by_alias=True), keywords=keywords)
            processed_products.append(processed)

        # 步骤3: 相似度匹配
        matches = self.similarity_matcher.find_similar_products(processed_products)

        # 步骤4: 格式化最终输出
        final_results = []
        for target_product, similar_meta, score in matches:
            final_results.append({
                "target_product_name": target_product.product_name,
                "target_product_keywords": target_product.keywords,
                "target_product_category": f"{target_product.category_l1}/{target_product.category_l2}/{target_product.category_l3}",
                "similar_product_in_our_pool": similar_meta.get("商品名称", similar_meta.get("product_name")),
                "similarity_score": round(score, 4),
                "status": target_product.status
            })

        return final_results