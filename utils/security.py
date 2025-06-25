# -*- coding: utf-8 -*-
"""
安全工具模块
"""

import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from passlib.hash import bcrypt

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT配置
JWT_SECRET_KEY = secrets.token_urlsafe(32)  # 在生产环境中应该从环境变量读取
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7

def hash_password(password: str) -> str:
    """哈希密码
    
    Args:
        password: 明文密码
        
    Returns:
        str: 哈希后的密码
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码
    
    Args:
        plain_password: 明文密码
        hashed_password: 哈希密码
        
    Returns:
        bool: 密码是否匹配
    """
    return pwd_context.verify(plain_password, hashed_password)

def generate_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
    token_type: str = "access"
) -> str:
    """生成JWT令牌
    
    Args:
        data: 要编码的数据
        expires_delta: 过期时间增量
        token_type: 令牌类型 (access/refresh)
        
    Returns:
        str: JWT令牌
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        if token_type == "refresh":
            expire = datetime.utcnow() + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        else:
            expire = datetime.utcnow() + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": token_type
    })
    
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """验证JWT令牌
    
    Args:
        token: JWT令牌
        token_type: 期望的令牌类型
        
    Returns:
        Optional[Dict[str, Any]]: 解码后的数据，验证失败返回None
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # 检查令牌类型
        if payload.get("type") != token_type:
            return None
            
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None

def generate_api_key(length: int = 32) -> str:
    """生成API密钥
    
    Args:
        length: 密钥长度
        
    Returns:
        str: API密钥
    """
    return secrets.token_urlsafe(length)

def generate_secure_random_string(length: int = 16) -> str:
    """生成安全随机字符串
    
    Args:
        length: 字符串长度
        
    Returns:
        str: 随机字符串
    """
    return secrets.token_hex(length)

def hash_api_key(api_key: str) -> str:
    """哈希API密钥
    
    Args:
        api_key: API密钥
        
    Returns:
        str: 哈希后的API密钥
    """
    return hashlib.sha256(api_key.encode()).hexdigest()

def verify_api_key(api_key: str, hashed_key: str) -> bool:
    """验证API密钥
    
    Args:
        api_key: 原始API密钥
        hashed_key: 哈希后的API密钥
        
    Returns:
        bool: 是否匹配
    """
    return hash_api_key(api_key) == hashed_key

def generate_otp(length: int = 6) -> str:
    """生成一次性密码
    
    Args:
        length: OTP长度
        
    Returns:
        str: OTP
    """
    return ''.join([str(secrets.randbelow(10)) for _ in range(length)])

def generate_session_id() -> str:
    """生成会话ID
    
    Returns:
        str: 会话ID
    """
    return secrets.token_urlsafe(32)

def mask_sensitive_data(data: str, mask_char: str = "*", visible_chars: int = 4) -> str:
    """掩码敏感数据
    
    Args:
        data: 原始数据
        mask_char: 掩码字符
        visible_chars: 可见字符数
        
    Returns:
        str: 掩码后的数据
    """
    if len(data) <= visible_chars:
        return mask_char * len(data)
    
    visible_start = visible_chars // 2
    visible_end = visible_chars - visible_start
    
    masked_length = len(data) - visible_chars
    
    return (
        data[:visible_start] + 
        mask_char * masked_length + 
        data[-visible_end:] if visible_end > 0 else ""
    )

def validate_password_strength(password: str) -> Dict[str, Any]:
    """验证密码强度
    
    Args:
        password: 密码
        
    Returns:
        Dict[str, Any]: 验证结果
    """
    result = {
        "is_valid": True,
        "score": 0,
        "issues": []
    }
    
    # 长度检查
    if len(password) < 8:
        result["issues"].append("密码长度至少8位")
        result["is_valid"] = False
    else:
        result["score"] += 1
    
    # 包含大写字母
    if not any(c.isupper() for c in password):
        result["issues"].append("密码应包含大写字母")
    else:
        result["score"] += 1
    
    # 包含小写字母
    if not any(c.islower() for c in password):
        result["issues"].append("密码应包含小写字母")
    else:
        result["score"] += 1
    
    # 包含数字
    if not any(c.isdigit() for c in password):
        result["issues"].append("密码应包含数字")
    else:
        result["score"] += 1
    
    # 包含特殊字符
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        result["issues"].append("密码应包含特殊字符")
    else:
        result["score"] += 1
    
    # 设置强度等级
    if result["score"] >= 4:
        result["strength"] = "strong"
    elif result["score"] >= 3:
        result["strength"] = "medium"
    else:
        result["strength"] = "weak"
        result["is_valid"] = False
    
    return result

def sanitize_input(input_str: str) -> str:
    """清理输入字符串
    
    Args:
        input_str: 输入字符串
        
    Returns:
        str: 清理后的字符串
    """
    if not input_str:
        return ""
    
    # 移除潜在的危险字符
    dangerous_chars = ['<', '>', '"', "'", '&', '\x00']
    cleaned = input_str
    
    for char in dangerous_chars:
        cleaned = cleaned.replace(char, "")
    
    # 限制长度
    max_length = 1000
    if len(cleaned) > max_length:
        cleaned = cleaned[:max_length]
    
    return cleaned.strip()

def generate_csrf_token() -> str:
    """生成CSRF令牌
    
    Returns:
        str: CSRF令牌
    """
    return secrets.token_urlsafe(32)

def constant_time_compare(a: str, b: str) -> bool:
    """常量时间字符串比较（防止时序攻击）
    
    Args:
        a: 字符串A
        b: 字符串B
        
    Returns:
        bool: 是否相等
    """
    if len(a) != len(b):
        return False
    
    result = 0
    for x, y in zip(a, b):
        result |= ord(x) ^ ord(y)
    
    return result == 0