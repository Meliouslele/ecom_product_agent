from pydantic import BaseModel, Field
from typing import List, Optional

class ProductInfo(BaseModel):
    """原始商品信息模型"""
    category_l1: str = Field(..., alias="一级类目")
    category_l2: str = Field(..., alias="二级类目")
    category_l3: str = Field(..., alias="三级类目")
    product_name: str = Field(..., alias="商品名称")
    price: str = Field(..., alias="价格")
    volume: int = Field(..., alias="成交量")
    sku: str = Field(..., alias="sku")
    status: str = Field(..., alias="状态")

    class Config:
        validate_by_name = True  # 代替原来的 allow_population_by_field_name
        populate_by_name = True   # 允许通过字段名赋值（可选）

class ProcessedProduct(ProductInfo):
    """处理后的商品模型，包含提取的关键词"""
    keywords: List[str] = []

class SimilarityResult(BaseModel):
    """相似度匹配结果"""
    target_product: ProcessedProduct
    similar_product_from_pool: ProductInfo
    similarity_score: float