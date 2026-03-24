from app.services.llm_service import get_llm_response
import json
import re
import logging

logger = logging.getLogger(__name__)

class KeywordExtractor:
    def __init__(self):
        pass

    def extract(self, product_name: str) -> list:
        """使用通义千问API提取商品名称的关键词"""
        system_prompt = """你是一个专业的电商商品名称分析专家。
你的任务是从给定的商品名称中，提取出最核心的、代表商品类目和功能的关键词。
请以JSON列表的格式输出，只输出列表，不要有其他任何解释。
例如：
商品名称：黎派（LPA）书架简约时尚 落地收纳多功能大容量储物架 置物书架柜子 1500*400*1600mm
输出：["书架", "柜子", "书架柜子"]
商品名称：宝鸟女士秋冬毛呢工装大衣
输出：["大衣", "工装大衣"]
商品名称：得力7540橡皮擦(超市装)(黄)(2块/包) 12包 黄色绘画4B200A美术橡皮擦
输出：["橡皮擦", "美术橡皮擦"]"""
        user_prompt = product_name
        try:
            response = get_llm_response(system_prompt, user_prompt, temperature=0.1)
            # 清理可能的markdown代码块
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()
            keywords = json.loads(response)
            if isinstance(keywords, list):
                return keywords
            else:
                return []
        except Exception as e:
            logger.error(f"提取关键词失败: {e}, 原始响应: {response}")
            # 降级：简单分词（取前两个非数字词）
            words = re.findall(r'[\u4e00-\u9fa5]+', product_name)
            return words[:2] if words else []