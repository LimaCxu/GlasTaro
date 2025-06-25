# -*- coding: utf-8 -*-
"""
辅助工具模块
"""

import uuid
import json
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List, Union
from decimal import Decimal, ROUND_HALF_UP
import re

def generate_uuid() -> str:
    """生成UUID
    
    Returns:
        str: UUID字符串
    """
    return str(uuid.uuid4())

def format_datetime(
    dt: datetime, 
    format_str: str = "%Y-%m-%d %H:%M:%S", 
    timezone_str: Optional[str] = None
) -> str:
    """格式化日期时间
    
    Args:
        dt: 日期时间对象
        format_str: 格式字符串
        timezone_str: 时区字符串
        
    Returns:
        str: 格式化后的日期时间字符串
    """
    if timezone_str:
        try:
            import pytz
            tz = pytz.timezone(timezone_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            dt = dt.astimezone(tz)
        except (ImportError, Exception):
            pass
    
    return dt.strftime(format_str)

def parse_datetime(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """解析日期时间字符串
    
    Args:
        date_str: 日期时间字符串
        format_str: 格式字符串
        
    Returns:
        Optional[datetime]: 解析后的日期时间对象
    """
    try:
        return datetime.strptime(date_str, format_str)
    except ValueError:
        return None

def get_current_timestamp() -> int:
    """获取当前时间戳
    
    Returns:
        int: 时间戳（秒）
    """
    return int(datetime.utcnow().timestamp())

def get_current_timestamp_ms() -> int:
    """获取当前时间戳（毫秒）
    
    Returns:
        int: 时间戳（毫秒）
    """
    return int(datetime.utcnow().timestamp() * 1000)

def timestamp_to_datetime(timestamp: Union[int, float]) -> datetime:
    """时间戳转日期时间
    
    Args:
        timestamp: 时间戳
        
    Returns:
        datetime: 日期时间对象
    """
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)

def get_date_range(days: int, from_date: Optional[datetime] = None) -> tuple[datetime, datetime]:
    """获取日期范围
    
    Args:
        days: 天数
        from_date: 起始日期，默认为当前日期
        
    Returns:
        tuple: (开始日期, 结束日期)
    """
    if from_date is None:
        from_date = datetime.utcnow()
    
    start_date = from_date - timedelta(days=days)
    return start_date, from_date

def get_start_of_day(dt: Optional[datetime] = None) -> datetime:
    """获取一天的开始时间
    
    Args:
        dt: 日期时间，默认为当前时间
        
    Returns:
        datetime: 一天的开始时间
    """
    if dt is None:
        dt = datetime.utcnow()
    
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)

def get_end_of_day(dt: Optional[datetime] = None) -> datetime:
    """获取一天的结束时间
    
    Args:
        dt: 日期时间，默认为当前时间
        
    Returns:
        datetime: 一天的结束时间
    """
    if dt is None:
        dt = datetime.utcnow()
    
    return dt.replace(hour=23, minute=59, second=59, microsecond=999999)

def format_currency(amount: Union[float, Decimal], currency: str = "USD") -> str:
    """格式化货币
    
    Args:
        amount: 金额
        currency: 货币代码
        
    Returns:
        str: 格式化后的货币字符串
    """
    if isinstance(amount, float):
        amount = Decimal(str(amount))
    
    # 保留两位小数
    amount = amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    currency_symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥",
        "CNY": "¥",
        "KRW": "₩",
        "RUB": "₽"
    }
    
    symbol = currency_symbols.get(currency, currency)
    
    if currency == "JPY":
        # 日元不显示小数
        return f"{symbol}{int(amount)}"
    else:
        return f"{symbol}{amount}"

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """截断文本
    
    Args:
        text: 原始文本
        max_length: 最大长度
        suffix: 后缀
        
    Returns:
        str: 截断后的文本
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def clean_text(text: str) -> str:
    """清理文本
    
    Args:
        text: 原始文本
        
    Returns:
        str: 清理后的文本
    """
    if not text:
        return ""
    
    # 移除多余的空白字符
    cleaned = re.sub(r'\s+', ' ', text.strip())
    
    # 移除控制字符
    cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', cleaned)
    
    return cleaned

def generate_hash(data: str, algorithm: str = "sha256") -> str:
    """生成哈希值
    
    Args:
        data: 原始数据
        algorithm: 哈希算法
        
    Returns:
        str: 哈希值
    """
    hash_obj = hashlib.new(algorithm)
    hash_obj.update(data.encode('utf-8'))
    return hash_obj.hexdigest()

def generate_short_id(length: int = 8) -> str:
    """生成短ID
    
    Args:
        length: ID长度
        
    Returns:
        str: 短ID
    """
    import secrets
    import string
    
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """安全的JSON解析
    
    Args:
        json_str: JSON字符串
        default: 默认值
        
    Returns:
        Any: 解析后的对象
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default

def safe_json_dumps(obj: Any, default: str = "{}") -> str:
    """安全的JSON序列化
    
    Args:
        obj: 要序列化的对象
        default: 默认值
        
    Returns:
        str: JSON字符串
    """
    try:
        return json.dumps(obj, ensure_ascii=False, default=str)
    except (TypeError, ValueError):
        return default

def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """合并字典
    
    Args:
        *dicts: 要合并的字典
        
    Returns:
        Dict[str, Any]: 合并后的字典
    """
    result = {}
    for d in dicts:
        if isinstance(d, dict):
            result.update(d)
    return result

def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """扁平化字典
    
    Args:
        d: 原始字典
        parent_key: 父键
        sep: 分隔符
        
    Returns:
        Dict[str, Any]: 扁平化后的字典
    """
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """分块列表
    
    Args:
        lst: 原始列表
        chunk_size: 块大小
        
    Returns:
        List[List[Any]]: 分块后的列表
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def remove_duplicates(lst: List[Any], key_func: Optional[callable] = None) -> List[Any]:
    """移除重复项
    
    Args:
        lst: 原始列表
        key_func: 键函数
        
    Returns:
        List[Any]: 去重后的列表
    """
    if key_func is None:
        return list(dict.fromkeys(lst))
    
    seen = set()
    result = []
    for item in lst:
        key = key_func(item)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result

def calculate_pagination(
    total_count: int, 
    page: int, 
    page_size: int
) -> Dict[str, Any]:
    """计算分页信息
    
    Args:
        total_count: 总数量
        page: 当前页
        page_size: 页面大小
        
    Returns:
        Dict[str, Any]: 分页信息
    """
    total_pages = (total_count + page_size - 1) // page_size
    offset = (page - 1) * page_size
    
    return {
        "total_count": total_count,
        "total_pages": total_pages,
        "current_page": page,
        "page_size": page_size,
        "offset": offset,
        "has_next": page < total_pages,
        "has_prev": page > 1,
        "next_page": page + 1 if page < total_pages else None,
        "prev_page": page - 1 if page > 1 else None
    }

def format_file_size(size_bytes: int) -> str:
    """格式化文件大小
    
    Args:
        size_bytes: 字节数
        
    Returns:
        str: 格式化后的文件大小
    """
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def generate_random_color() -> str:
    """生成随机颜色
    
    Returns:
        str: 十六进制颜色代码
    """
    import random
    return f"#{random.randint(0, 0xFFFFFF):06x}"

def is_valid_url(url: str) -> bool:
    """验证URL格式
    
    Args:
        url: URL字符串
        
    Returns:
        bool: 是否有效
    """
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'  # domain...
        r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # host...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(url_pattern.match(url))

def extract_numbers(text: str) -> List[float]:
    """从文本中提取数字
    
    Args:
        text: 文本
        
    Returns:
        List[float]: 数字列表
    """
    pattern = r'-?\d+(?:\.\d+)?'
    matches = re.findall(pattern, text)
    return [float(match) for match in matches]

def mask_sensitive_info(text: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """掩码敏感信息
    
    Args:
        text: 原始文本
        mask_char: 掩码字符
        visible_chars: 可见字符数
        
    Returns:
        str: 掩码后的文本
    """
    if len(text) <= visible_chars:
        return mask_char * len(text)
    
    visible_start = visible_chars // 2
    visible_end = visible_chars - visible_start
    
    return (
        text[:visible_start] + 
        mask_char * (len(text) - visible_chars) + 
        text[-visible_end:] if visible_end > 0 else ""
    )

def retry_on_exception(
    func: callable, 
    max_retries: int = 3, 
    delay: float = 1.0, 
    exceptions: tuple = (Exception,)
) -> Any:
    """异常重试装饰器
    
    Args:
        func: 要执行的函数
        max_retries: 最大重试次数
        delay: 重试延迟
        exceptions: 要捕获的异常类型
        
    Returns:
        Any: 函数执行结果
    """
    import time
    
    for attempt in range(max_retries + 1):
        try:
            return func()
        except exceptions as e:
            if attempt == max_retries:
                raise e
            time.sleep(delay * (2 ** attempt))  # 指数退避
    
    return None