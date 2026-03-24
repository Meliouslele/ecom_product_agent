import dashscope
from config.settings import DASHSCOPE_API_KEY, LLM_MODEL_NAME
import logging

logger = logging.getLogger(__name__)

# 设置 API Key
dashscope.api_key = DASHSCOPE_API_KEY

def get_llm_response(system_prompt: str, user_prompt: str, temperature: float = 0.7) -> str:
    """
    调用通义千问API获取回复
    """
    try:
        response = dashscope.Generation.call(
            model=LLM_MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            result_format='message'
        )
        if response.status_code == 200:
            return response.output.choices[0].message.content
        else:
            logger.error(f"API调用失败: {response.code} - {response.message}")
            raise Exception(f"API调用失败: {response.code} - {response.message}")
    except Exception as e:
        logger.exception("LLM服务异常")
        raise