import pandas as pd
from config.settings import OWN_POOL_CSV, FULL_CATEGORY_CSV
import logging

logger = logging.getLogger(__name__)

def load_csv_with_encoding(file_path, encodings=None):
    """
    尝试用多种编码读取CSV文件，返回DataFrame
    """
    if encodings is None:
        encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'gb18030']
    for enc in encodings:
        try:
            df = pd.read_csv(file_path, encoding=enc)
            logger.info(f"成功用 {enc} 编码读取文件 {file_path}")
            return df
        except UnicodeDecodeError:
            continue
        except Exception as e:
            logger.error(f"读取文件 {file_path} 时出错（编码 {enc}）: {e}")
    raise Exception(f"无法使用任何已知编码读取文件 {file_path}")

def load_own_pool_data(file_path=None):
    if file_path is None:
        file_path = OWN_POOL_CSV
    return load_csv_with_encoding(file_path)

def load_full_category_data(file_path=None):
    if file_path is None:
        file_path = FULL_CATEGORY_CSV
    return load_csv_with_encoding(file_path)