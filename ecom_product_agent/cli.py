import sys
import re
from app.services.vector_service import VectorService
from app.services.full_category_vector_service import FullCategoryVectorService
from app.core.similarity_searcher import SimilaritySearcher
from app.utils.data_loader import load_own_pool_data, load_full_category_data
from app.services.llm_service import get_llm_response
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_own_pool_set():
    df = load_own_pool_data()
    if 'sku' in df.columns:
        return set(df['sku'].astype(str).tolist())
    else:
        return set(df['商品名称'].tolist())

def extract_product_name_from_query(query: str) -> str:
    patterns = [
        r"有哪些与(.+?)相似的商品[？?]?",
        r"查找与(.+?)相似的?商品",
        r"推荐(.+?)的相似商品",
        r"输出与(.+?)相似的商品名称",
        r"与(.+?)相似的商品有哪些",
        r"(.+?)的相似商品",
        r"类似(.+?)的商品",
        r"有与(.+?)相似的[吗？?]",
        r"有没有与(.+?)相似的[商品]?[吗？?]",
        r"(.+?)的相似品",
    ]
    for pattern in patterns:
        match = re.search(pattern, query)
        if match:
            product_name = match.group(1).strip()
            product_name = re.sub(r'[，,、。？?()（）]', '', product_name)
            return product_name
    return None

def main():
    print("正在加载数据，请稍候...")
    full_cat_vector_service = FullCategoryVectorService()
    if not full_cat_vector_service.load_index():
        print("全类目表索引未找到，正在构建...")
        df_full = load_full_category_data()
        texts = df_full['商品名称'].tolist()
        metadatas = df_full.to_dict('records')
        full_cat_vector_service.create_index(texts, metadatas)
        print("全类目表索引构建完成。")

    own_pool_set = load_own_pool_set()
    searcher = SimilaritySearcher(full_cat_vector_service, own_pool_set)

    print("\n欢迎使用商品分析助手！")
    print("你可以问我以下问题：")
    print("1. 有哪些与【商品名】相似的商品？")
    print("2. 有哪些全类目商品表中为入池，与我司商品池（商品列表）相似度高但不在我司商品池表的（即潜在商品）？")
    print("输入 'exit' 或 'quit' 退出程序。\n")

    while True:
        user_input = input("Q: ").strip()
        if user_input.lower() in ['exit', 'quit']:
            print("再见！")
            break
        if not user_input:
            continue

        product_name = extract_product_name_from_query(user_input)
        if product_name:
            print(f"正在查找与「{product_name}」相似的商品...")
            results = searcher.search_similar_products([product_name], k=5, status_filter=None, exclude_own=False)
            if not results:
                print("未找到相似商品。")
            else:
                # 只显示相似度大于 0.5 的商品
                filtered = [item for item in results if item['similarity_score'] > 0.5]
                if not filtered:
                    print("未找到相似度大于 0.5 的商品。")
                else:
                    for i, item in enumerate(filtered, 1):
                        print(f"({i}) {item['product_name']} (相似度: {item['similarity_score']:.2f})")
                        print(f"    类目: {item['category']} | 价格: {item['price']} | 成交量: {item['volume']}")
            continue

        pattern2 = re.compile(r"与我司商品池[（(](.+?)[）)]")
        match2 = pattern2.search(user_input)
        if match2:
            product_list_str = match2.group(1).strip()
            products = re.split(r'[、,，\s]+', product_list_str)
            products = [p.strip() for p in products if p.strip()]
            if not products:
                print("未识别到商品列表，请提供至少一个商品名称。")
                continue
            print(f"正在查找与{products}相似、状态为「入池」且不在自有池的商品...")
            results = searcher.search_similar_products(products, k=3, status_filter="入池", exclude_own=True)
            if not results:
                print("未找到符合条件的潜在商品。")
            else:
                filtered = [item for item in results if item['similarity_score'] > 0.5]
                if not filtered:
                    print("未找到相似度大于 0.5 的潜在商品。")
                else:
                    for i, item in enumerate(filtered, 1):
                        print(f"({i}) {item['product_name']} (相似度: {item['similarity_score']:.2f})")
                        print(f"    类目: {item['category']} | 价格: {item['price']} | 成交量: {item['volume']}")
            continue

        # 未匹配任何已知意图，尝试用LLM引导
        print("正在理解你的问题，请稍候...")
        system_prompt = """你是一个电商商品分析助手，专门帮助用户查找相似商品或推荐潜在入池商品。
你的回答应当简洁、友好，并引导用户使用以下两种规范提问格式：
1. 查找相似商品：有哪些与【商品名】相似的商品？
2. 查找潜在入池商品：有哪些全类目商品表中为入池，与我司商品池（商品列表）相似度高但不在我司商品池表的？
如果用户的问题与商品分析无关，可以礼貌地表示无法回答，并引导用户提出正确的问题。"""
        user_prompt = f"用户输入：{user_input}\n请给出简短回复（不超过50字）。"
        try:
            reply = get_llm_response(system_prompt, user_prompt, temperature=0.5)
            print(f"助手: {reply}")
        except Exception as e:
            logger.error(f"LLM调用失败: {e}")
            print("抱歉，我无法理解你的问题。请参考以下示例：")
            print("  Q: 有哪些与尺子相似的商品？")
            print("  Q: 有哪些全类目商品表中为入池，与我司商品池（尺子、书架）相似度高但不在我司商品池表的？")

if __name__ == "__main__":
    main()