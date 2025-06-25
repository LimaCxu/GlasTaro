# -*- coding: utf-8 -*-
"""
API v1版本路由
"""

from fastapi import APIRouter
from .auth import router as auth_router
from .users import router as users_router
from .divination import router as divination_router
from .orders import router as orders_router
from .payments import router as payments_router
from .admin import router as admin_router
from .callbacks import router as callbacks_router

# 创建v1 API路由
api_router = APIRouter()

# 包含各个模块的路由
api_router.include_router(auth_router, prefix="/auth", tags=["认证"])
api_router.include_router(users_router, prefix="/users", tags=["用户"])
api_router.include_router(divination_router, prefix="/divination", tags=["占卜"])
api_router.include_router(orders_router, prefix="/orders", tags=["订单"])
api_router.include_router(payments_router, prefix="/payments", tags=["支付"])
api_router.include_router(admin_router, prefix="/admin", tags=["管理"])
api_router.include_router(callbacks_router, prefix="/callbacks", tags=["回调"])

__all__ = ["api_router"]