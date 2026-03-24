from fastapi import APIRouter, HTTPException
from app.core.agent import ProductAnalysisAgent
from app.services.vector_service import VectorService
from app.utils.data_loader import load_full_category_data, load_own_pool_data
from app.models.schemas import ProductInfo
import pandas as pd
import logging

router = APIRouter(prefix="/api/v1/products", tags=["Product Analysis"])
logger = logging.getLogger(__name__)

# 初始化向量服务（全局单例）
vector_service = VectorService()
if not vector_service.load_index():
    logger.info("自有商品池索引不存在，正在创建...")
    df_own = load_own_pool_data()
    texts = df_own['商品名称'].tolist()
    metadatas = df_own.to_dict('records')
    vector_service.create_index(texts, metadatas)
    logger.info("自有商品池索引创建完成。")

agent = ProductAnalysisAgent(vector_service)

@router.post("/analyze")
def analyze_products():
    """
    分析全类目商品表，返回与自有商品池相似但尚未入库的商品
    """
    try:
        df = load_full_category_data()
        products = [ProductInfo(**row.to_dict()) for _, row in df.iterrows()]
        results = agent.run(products)
        return {
            "status": "success",
            "total_analyzed": len(products),
            "recommendations": results
        }
    except Exception as e:
        logger.exception("分析失败")
        raise HTTPException(status_code=500, detail=str(e))