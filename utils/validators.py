# -*- coding: utf-8 -*-
"""
数据验证器模块
"""

import re
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
from email_validator import validate_email as _validate_email, EmailNotValidError

def validate_email(email: str) -> bool:
    """验证邮箱地址
    
    Args:
        email: 邮箱地址
        
    Returns:
        bool: 是否有效
    """
    try:
        _validate_email(email)
        return True
    except EmailNotValidError:
        return False

def validate_phone(phone: str, country_code: str = "CN") -> bool:
    """验证手机号码
    
    Args:
        phone: 手机号码
        country_code: 国家代码
        
    Returns:
        bool: 是否有效
    """
    # 移除所有非数字字符
    clean_phone = re.sub(r'\D', '', phone)
    
    if country_code == "CN":
        # 中国手机号验证
        pattern = r'^1[3-9]\d{9}$'
        return bool(re.match(pattern, clean_phone))
    elif country_code == "US":
        # 美国手机号验证
        pattern = r'^[2-9]\d{2}[2-9]\d{2}\d{4}$'
        return bool(re.match(pattern, clean_phone))
    else:
        # 通用验证：7-15位数字
        return 7 <= len(clean_phone) <= 15

def validate_username(username: str) -> Dict[str, Any]:
    """验证用户名
    
    Args:
        username: 用户名
        
    Returns:
        Dict[str, Any]: 验证结果
    """
    result = {
        "is_valid": True,
        "errors": []
    }
    
    if not username:
        result["is_valid"] = False
        result["errors"].append("用户名不能为空")
        return result
    
    # 长度检查
    if len(username) < 3:
        result["is_valid"] = False
        result["errors"].append("用户名长度至少3位")
    elif len(username) > 50:
        result["is_valid"] = False
        result["errors"].append("用户名长度不能超过50位")
    
    # 字符检查
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        result["is_valid"] = False
        result["errors"].append("用户名只能包含字母、数字、下划线和连字符")
    
    # 不能以数字开头
    if username[0].isdigit():
        result["is_valid"] = False
        result["errors"].append("用户名不能以数字开头")
    
    return result

def validate_user_input(text: str, max_length: int = 1000, allow_empty: bool = False) -> Dict[str, Any]:
    """验证用户输入
    
    Args:
        text: 输入文本
        max_length: 最大长度
        allow_empty: 是否允许空值
        
    Returns:
        Dict[str, Any]: 验证结果
    """
    result = {
        "is_valid": True,
        "errors": [],
        "cleaned_text": text
    }
    
    if not text and not allow_empty:
        result["is_valid"] = False
        result["errors"].append("输入不能为空")
        return result
    
    if not text:
        return result
    
    # 长度检查
    if len(text) > max_length:
        result["is_valid"] = False
        result["errors"].append(f"输入长度不能超过{max_length}字符")
    
    # 检查危险字符
    dangerous_patterns = [
        r'<script[^>]*>.*?</script>',  # Script标签
        r'javascript:',  # JavaScript协议
        r'on\w+\s*=',  # 事件处理器
        r'<iframe[^>]*>.*?</iframe>',  # iframe标签
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            result["is_valid"] = False
            result["errors"].append("输入包含不安全内容")
            break
    
    # 清理文本
    cleaned = text.strip()
    # 移除多余的空白字符
    cleaned = re.sub(r'\s+', ' ', cleaned)
    result["cleaned_text"] = cleaned
    
    return result

def validate_uuid(uuid_string: str) -> bool:
    """验证UUID格式
    
    Args:
        uuid_string: UUID字符串
        
    Returns:
        bool: 是否有效
    """
    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        return False

def validate_date_range(start_date: datetime, end_date: datetime) -> Dict[str, Any]:
    """验证日期范围
    
    Args:
        start_date: 开始日期
        end_date: 结束日期
        
    Returns:
        Dict[str, Any]: 验证结果
    """
    result = {
        "is_valid": True,
        "errors": []
    }
    
    if start_date >= end_date:
        result["is_valid"] = False
        result["errors"].append("开始日期必须早于结束日期")
    
    # 检查日期是否在合理范围内
    now = datetime.utcnow()
    if start_date > now:
        result["is_valid"] = False
        result["errors"].append("开始日期不能是未来时间")
    
    # 检查时间跨度是否过大（例如不超过1年）
    max_days = 365
    if (end_date - start_date).days > max_days:
        result["is_valid"] = False
        result["errors"].append(f"日期范围不能超过{max_days}天")
    
    return result

def validate_pagination(page: int, page_size: int, max_page_size: int = 100) -> Dict[str, Any]:
    """验证分页参数
    
    Args:
        page: 页码
        page_size: 页面大小
        max_page_size: 最大页面大小
        
    Returns:
        Dict[str, Any]: 验证结果
    """
    result = {
        "is_valid": True,
        "errors": []
    }
    
    if page < 1:
        result["is_valid"] = False
        result["errors"].append("页码必须大于0")
    
    if page_size < 1:
        result["is_valid"] = False
        result["errors"].append("页面大小必须大于0")
    elif page_size > max_page_size:
        result["is_valid"] = False
        result["errors"].append(f"页面大小不能超过{max_page_size}")
    
    return result

def validate_rating(rating: int) -> bool:
    """验证评分
    
    Args:
        rating: 评分
        
    Returns:
        bool: 是否有效
    """
    return 1 <= rating <= 5

def validate_language_code(language_code: str) -> bool:
    """验证语言代码
    
    Args:
        language_code: 语言代码
        
    Returns:
        bool: 是否有效
    """
    # 支持的语言代码
    supported_languages = {
        "zh", "zh-CN", "zh-TW",  # 中文
        "en", "en-US", "en-GB",  # 英文
        "ru", "ru-RU",          # 俄文
        "ja", "ja-JP",          # 日文
        "ko", "ko-KR",          # 韩文
        "es", "es-ES",          # 西班牙文
        "fr", "fr-FR",          # 法文
        "de", "de-DE",          # 德文
    }
    
    return language_code in supported_languages

def validate_timezone(timezone_str: str) -> bool:
    """验证时区
    
    Args:
        timezone_str: 时区字符串
        
    Returns:
        bool: 是否有效
    """
    try:
        import pytz
        pytz.timezone(timezone_str)
        return True
    except pytz.exceptions.UnknownTimeZoneError:
        return False
    except ImportError:
        # 如果没有安装pytz，使用简单验证
        common_timezones = {
            "UTC", "GMT",
            "Asia/Shanghai", "Asia/Tokyo", "Asia/Seoul",
            "America/New_York", "America/Los_Angeles",
            "Europe/London", "Europe/Paris", "Europe/Berlin",
            "Australia/Sydney", "Australia/Melbourne"
        }
        return timezone_str in common_timezones

def validate_currency_code(currency_code: str) -> bool:
    """验证货币代码
    
    Args:
        currency_code: 货币代码
        
    Returns:
        bool: 是否有效
    """
    # 支持的货币代码
    supported_currencies = {
        "USD", "EUR", "GBP", "JPY", "CNY",
        "KRW", "RUB", "CAD", "AUD", "CHF",
        "HKD", "SGD", "TWD"
    }
    
    return currency_code.upper() in supported_currencies

def validate_amount(amount: float, min_amount: float = 0.01, max_amount: float = 10000.0) -> Dict[str, Any]:
    """验证金额
    
    Args:
        amount: 金额
        min_amount: 最小金额
        max_amount: 最大金额
        
    Returns:
        Dict[str, Any]: 验证结果
    """
    result = {
        "is_valid": True,
        "errors": []
    }
    
    if amount < min_amount:
        result["is_valid"] = False
        result["errors"].append(f"金额不能小于{min_amount}")
    
    if amount > max_amount:
        result["is_valid"] = False
        result["errors"].append(f"金额不能大于{max_amount}")
    
    # 检查小数位数（最多2位）
    if round(amount, 2) != amount:
        result["is_valid"] = False
        result["errors"].append("金额最多保留2位小数")
    
    return result

def validate_divination_type(divination_type: str) -> bool:
    """验证占卜类型
    
    Args:
        divination_type: 占卜类型
        
    Returns:
        bool: 是否有效
    """
    valid_types = {
        "daily_card",      # 每日一卡
        "love",           # 爱情占卜
        "career",         # 事业占卜
        "fortune",        # 财运占卜
        "health",         # 健康占卜
        "general",        # 综合占卜
        "three_card",     # 三卡占卜
        "celtic_cross",   # 凯尔特十字
        "custom"          # 自定义
    }
    
    return divination_type in valid_types

def sanitize_filename(filename: str) -> str:
    """清理文件名
    
    Args:
        filename: 原始文件名
        
    Returns:
        str: 清理后的文件名
    """
    # 移除危险字符
    dangerous_chars = r'[<>:"/\\|?*]'
    cleaned = re.sub(dangerous_chars, '_', filename)
    
    # 移除控制字符
    cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', cleaned)
    
    # 限制长度
    max_length = 255
    if len(cleaned) > max_length:
        name, ext = os.path.splitext(cleaned)
        cleaned = name[:max_length - len(ext)] + ext
    
    return cleaned.strip()

def validate_json_structure(data: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
    """验证JSON结构
    
    Args:
        data: JSON数据
        required_fields: 必需字段列表
        
    Returns:
        Dict[str, Any]: 验证结果
    """
    result = {
        "is_valid": True,
        "errors": [],
        "missing_fields": []
    }
    
    for field in required_fields:
        if field not in data:
            result["is_valid"] = False
            result["missing_fields"].append(field)
            result["errors"].append(f"缺少必需字段: {field}")
    
    return result