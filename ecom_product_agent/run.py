import sys
import uvicorn
from app.main import app
from app.services.vector_service import VectorService
from app.services.full_category_vector_service import FullCategoryVectorService
from app.utils.data_loader import load_own_pool_data, load_full_category_data
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        # 启动交互式CLI
        from cli import main as cli_main
        cli_main()
    else:
        # 初始化自有池索引（如果不存在则创建）
        logger.info("检查自有商品池索引...")
        vector_service = VectorService()
        if not vector_service.load_index():
            logger.info("自有商品池索引不存在，正在创建...")
            df_own = load_own_pool_data()
            texts = df_own['商品名称'].tolist()
            metadatas = df_own.to_dict('records')
            vector_service.create_index(texts, metadatas)
            logger.info("自有商品池索引创建完成。")

        # 初始化全类目表索引（如果不存在则创建）
        logger.info("检查全类目表索引...")
        full_cat_vector_service = FullCategoryVectorService()
        if not full_cat_vector_service.load_index():
            logger.info("全类目表索引不存在，正在创建...")
            df_full = load_full_category_data()
            texts = df_full['商品名称'].tolist()
            metadatas = df_full.to_dict('records')
            full_cat_vector_service.create_index(texts, metadatas)
            logger.info("全类目表索引创建完成。")

        # 启动API服务
        uvicorn.run(app, host="0.0.0.0", port=8000)