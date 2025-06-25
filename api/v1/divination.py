# -*- coding: utf-8 -*-
"""
占卜相关API路由
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

from core.dependencies import (
    get_divination_service,
    get_current_user,
    get_pagination_params,
    rate_limit_check
)
from models.user import User
from services.divination_service import DivinationService
from utils.exceptions import (
    DivinationLimitExceededError,
    ValidationError,
    ResourceNotFoundError
)
from utils.helpers import format_datetime

router = APIRouter()

# 请求模型
class CreateDivinationRequest(BaseModel):
    """创建占卜请求"""
    spread_id: int = Field(..., description="牌阵ID")
    question: Optional[str] = Field(None, max_length=500, description="问题")
    question_type: Optional[str] = Field(None, description="问题类型")
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据")

class GenerateInterpretationRequest(BaseModel):
    """生成解释请求"""
    session_id: str = Field(..., description="占卜会话ID")
    card_position: Optional[int] = Field(None, description="牌位置（单张牌解释）")
    interpretation_type: str = Field("overall", description="解释类型：single或overall")

# 响应模型
class TarotCardResponse(BaseModel):
    """塔罗牌响应"""
    id: int
    name: str
    name_en: str
    suit: Optional[str]
    number: Optional[int]
    arcana_type: str
    keywords: List[str]
    description: str
    upright_meaning: str
    reversed_meaning: str
    image_url: Optional[str]
    symbolism: Optional[str]
    element: Optional[str]
    planet: Optional[str]
    zodiac: Optional[str]

class SpreadTemplateResponse(BaseModel):
    """牌阵模板响应"""
    id: int
    name: str
    name_en: str
    description: str
    card_count: int
    positions: List[Dict[str, Any]]
    difficulty_level: str
    category: str
    image_url: Optional[str]
    instructions: Optional[str]
    is_active: bool

class DivinationSessionResponse(BaseModel):
    """占卜会话响应"""
    id: int
    session_id: str
    user_id: int
    spread_id: int
    spread_name: str
    question: Optional[str]
    question_type: Optional[str]
    cards: List[Dict[str, Any]]
    interpretation: Optional[str]
    status: str
    created_at: str
    completed_at: Optional[str]
    metadata: Optional[Dict[str, Any]]

class DailyTarotResponse(BaseModel):
    """每日塔罗响应"""
    id: int
    user_id: int
    card: TarotCardResponse
    is_reversed: bool
    interpretation: str
    date: str
    created_at: str

class DivinationStatsResponse(BaseModel):
    """占卜统计响应"""
    total_sessions: int
    completed_sessions: int
    monthly_sessions: int
    favorite_spread: Optional[str]
    most_drawn_card: Optional[str]
    accuracy_rating: Optional[float]
    streak_days: int
    last_divination: Optional[str]

@router.get("/cards", response_model=List[TarotCardResponse], summary="获取塔罗牌列表")
async def get_tarot_cards(
    suit: Optional[str] = Query(None, description="花色"),
    arcana_type: Optional[str] = Query(None, description="大小阿卡纳类型"),
    limit: int = Query(78, ge=1, le=78, description="数量限制"),
    divination_service: DivinationService = Depends(get_divination_service)
):
    """获取塔罗牌列表"""
    cards = await divination_service.get_all_tarot_cards(
        suit=suit,
        arcana_type=arcana_type,
        limit=limit
    )
    
    return [
        TarotCardResponse(
            id=card.id,
            name=card.name,
            name_en=card.name_en,
            suit=card.suit,
            number=card.number,
            arcana_type=card.arcana_type,
            keywords=card.keywords or [],
            description=card.description,
            upright_meaning=card.upright_meaning,
            reversed_meaning=card.reversed_meaning,
            image_url=card.image_url,
            symbolism=card.symbolism,
            element=card.element,
            planet=card.planet,
            zodiac=card.zodiac
        )
        for card in cards
    ]

@router.get("/cards/{card_id}", response_model=TarotCardResponse, summary="获取指定塔罗牌")
async def get_tarot_card(
    card_id: int,
    divination_service: DivinationService = Depends(get_divination_service)
):
    """获取指定塔罗牌详情"""
    card = await divination_service.get_tarot_card_by_id(card_id)
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="塔罗牌不存在"
        )
    
    return TarotCardResponse(
        id=card.id,
        name=card.name,
        name_en=card.name_en,
        suit=card.suit,
        number=card.number,
        arcana_type=card.arcana_type,
        keywords=card.keywords or [],
        description=card.description,
        upright_meaning=card.upright_meaning,
        reversed_meaning=card.reversed_meaning,
        image_url=card.image_url,
        symbolism=card.symbolism,
        element=card.element,
        planet=card.planet,
        zodiac=card.zodiac
    )

@router.get("/cards/random", response_model=TarotCardResponse, summary="获取随机塔罗牌")
async def get_random_tarot_card(
    exclude_ids: Optional[str] = Query(None, description="排除的牌ID，逗号分隔"),
    divination_service: DivinationService = Depends(get_divination_service)
):
    """获取随机塔罗牌"""
    exclude_list = []
    if exclude_ids:
        try:
            exclude_list = [int(x.strip()) for x in exclude_ids.split(",") if x.strip()]
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的排除ID格式"
            )
    
    card = await divination_service.get_random_tarot_cards(1, exclude_list)
    
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="没有可用的塔罗牌"
        )
    
    card = card[0]
    return TarotCardResponse(
        id=card.id,
        name=card.name,
        name_en=card.name_en,
        suit=card.suit,
        number=card.number,
        arcana_type=card.arcana_type,
        keywords=card.keywords or [],
        description=card.description,
        upright_meaning=card.upright_meaning,
        reversed_meaning=card.reversed_meaning,
        image_url=card.image_url,
        symbolism=card.symbolism,
        element=card.element,
        planet=card.planet,
        zodiac=card.zodiac
    )

@router.get("/spreads", response_model=List[SpreadTemplateResponse], summary="获取牌阵模板列表")
async def get_spread_templates(
    category: Optional[str] = Query(None, description="分类"),
    difficulty: Optional[str] = Query(None, description="难度级别"),
    divination_service: DivinationService = Depends(get_divination_service)
):
    """获取牌阵模板列表"""
    spreads = await divination_service.get_spread_templates(
        category=category,
        difficulty_level=difficulty
    )
    
    return [
        SpreadTemplateResponse(
            id=spread.id,
            name=spread.name,
            name_en=spread.name_en,
            description=spread.description,
            card_count=spread.card_count,
            positions=spread.positions or [],
            difficulty_level=spread.difficulty_level,
            category=spread.category,
            image_url=spread.image_url,
            instructions=spread.instructions,
            is_active=spread.is_active
        )
        for spread in spreads
    ]

@router.get("/spreads/{spread_id}", response_model=SpreadTemplateResponse, summary="获取指定牌阵模板")
async def get_spread_template(
    spread_id: int,
    divination_service: DivinationService = Depends(get_divination_service)
):
    """获取指定牌阵模板详情"""
    spread = await divination_service.get_spread_template_by_id(spread_id)
    
    if not spread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="牌阵模板不存在"
        )
    
    return SpreadTemplateResponse(
        id=spread.id,
        name=spread.name,
        name_en=spread.name_en,
        description=spread.description,
        card_count=spread.card_count,
        positions=spread.positions or [],
        difficulty_level=spread.difficulty_level,
        category=spread.category,
        image_url=spread.image_url,
        instructions=spread.instructions,
        is_active=spread.is_active
    )

@router.get("/daily", response_model=DailyTarotResponse, summary="获取每日塔罗")
async def get_daily_tarot(
    current_user: User = Depends(get_current_user),
    divination_service: DivinationService = Depends(get_divination_service)
):
    """获取用户的每日塔罗牌"""
    daily_tarot = await divination_service.get_daily_tarot(current_user.id)
    
    if not daily_tarot:
        # 创建今日塔罗
        daily_tarot = await divination_service.create_daily_tarot(current_user.id)
    
    return DailyTarotResponse(
        id=daily_tarot.id,
        user_id=daily_tarot.user_id,
        card=TarotCardResponse(
            id=daily_tarot.card.id,
            name=daily_tarot.card.name,
            name_en=daily_tarot.card.name_en,
            suit=daily_tarot.card.suit,
            number=daily_tarot.card.number,
            arcana_type=daily_tarot.card.arcana_type,
            keywords=daily_tarot.card.keywords or [],
            description=daily_tarot.card.description,
            upright_meaning=daily_tarot.card.upright_meaning,
            reversed_meaning=daily_tarot.card.reversed_meaning,
            image_url=daily_tarot.card.image_url,
            symbolism=daily_tarot.card.symbolism,
            element=daily_tarot.card.element,
            planet=daily_tarot.card.planet,
            zodiac=daily_tarot.card.zodiac
        ),
        is_reversed=daily_tarot.is_reversed,
        interpretation=daily_tarot.interpretation,
        date=daily_tarot.date.isoformat(),
        created_at=format_datetime(daily_tarot.created_at)
    )

@router.post("/sessions", response_model=DivinationSessionResponse, summary="创建占卜会话")
async def create_divination_session(
    request: CreateDivinationRequest,
    current_user: User = Depends(get_current_user),
    divination_service: DivinationService = Depends(get_divination_service),
    _: None = Depends(rate_limit_check)
):
    """创建新的占卜会话"""
    try:
        session = await divination_service.create_divination_session(
            user_id=current_user.id,
            spread_id=request.spread_id,
            question=request.question,
            question_type=request.question_type,
            metadata=request.metadata
        )
        
        return DivinationSessionResponse(
            id=session.id,
            session_id=session.session_id,
            user_id=session.user_id,
            spread_id=session.spread_id,
            spread_name=session.spread.name,
            question=session.question,
            question_type=session.question_type,
            cards=session.cards or [],
            interpretation=session.interpretation,
            status=session.status,
            created_at=format_datetime(session.created_at),
            completed_at=format_datetime(session.completed_at) if session.completed_at else None,
            metadata=session.metadata
        )
    
    except DivinationLimitExceededError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e)
        )
    except (ValidationError, ResourceNotFoundError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/sessions", response_model=List[DivinationSessionResponse], summary="获取占卜会话列表")
async def get_divination_sessions(
    status_filter: Optional[str] = Query(None, description="状态过滤"),
    limit: int = Query(20, ge=1, le=100, description="数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    current_user: User = Depends(get_current_user),
    divination_service: DivinationService = Depends(get_divination_service)
):
    """获取用户的占卜会话列表"""
    sessions = await divination_service.get_user_divination_sessions(
        user_id=current_user.id,
        status=status_filter,
        limit=limit,
        offset=offset
    )
    
    return [
        DivinationSessionResponse(
            id=session.id,
            session_id=session.session_id,
            user_id=session.user_id,
            spread_id=session.spread_id,
            spread_name=session.spread.name,
            question=session.question,
            question_type=session.question_type,
            cards=session.cards or [],
            interpretation=session.interpretation,
            status=session.status,
            created_at=format_datetime(session.created_at),
            completed_at=format_datetime(session.completed_at) if session.completed_at else None,
            metadata=session.metadata
        )
        for session in sessions
    ]

@router.get("/sessions/{session_id}", response_model=DivinationSessionResponse, summary="获取占卜会话详情")
async def get_divination_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    divination_service: DivinationService = Depends(get_divination_service)
):
    """获取指定占卜会话详情"""
    session = await divination_service.get_divination_session_by_session_id(session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="占卜会话不存在"
        )
    
    # 检查权限
    if session.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足"
        )
    
    return DivinationSessionResponse(
        id=session.id,
        session_id=session.session_id,
        user_id=session.user_id,
        spread_id=session.spread_id,
        spread_name=session.spread.name,
        question=session.question,
        question_type=session.question_type,
        cards=session.cards or [],
        interpretation=session.interpretation,
        status=session.status,
        created_at=format_datetime(session.created_at),
        completed_at=format_datetime(session.completed_at) if session.completed_at else None,
        metadata=session.metadata
    )

@router.post("/sessions/{session_id}/interpretation", summary="生成占卜解释")
async def generate_interpretation(
    session_id: str,
    request: GenerateInterpretationRequest,
    current_user: User = Depends(get_current_user),
    divination_service: DivinationService = Depends(get_divination_service)
):
    """为占卜会话生成解释"""
    try:
        # 验证会话归属
        session = await divination_service.get_divination_session_by_session_id(session_id)
        if not session or session.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="占卜会话不存在"
            )
        
        if request.interpretation_type == "single":
            if request.card_position is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="单张牌解释需要指定牌位置"
                )
            
            interpretation = await divination_service.generate_single_card_interpretation(
                session_id=session_id,
                card_position=request.card_position
            )
        else:
            interpretation = await divination_service.generate_overall_interpretation(
                session_id=session_id
            )
        
        return {
            "message": "解释生成成功",
            "interpretation": interpretation,
            "type": request.interpretation_type
        }
    
    except (ValidationError, ResourceNotFoundError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/stats", response_model=DivinationStatsResponse, summary="获取占卜统计")
async def get_divination_stats(
    current_user: User = Depends(get_current_user),
    divination_service: DivinationService = Depends(get_divination_service)
):
    """获取用户占卜统计信息"""
    stats = await divination_service.get_user_divination_stats(current_user.id)
    
    return DivinationStatsResponse(**stats)

@router.get("/history", summary="获取占卜历史")
async def get_divination_history(
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    spread_id: Optional[int] = Query(None, description="牌阵ID"),
    pagination: Dict[str, int] = Depends(get_pagination_params),
    current_user: User = Depends(get_current_user),
    divination_service: DivinationService = Depends(get_divination_service)
):
    """获取用户占卜历史"""
    try:
        from datetime import datetime
        
        start_dt = None
        end_dt = None
        
        if start_date:
            start_dt = datetime.fromisoformat(start_date)
        if end_date:
            end_dt = datetime.fromisoformat(end_date)
        
        sessions = await divination_service.get_user_divination_sessions(
            user_id=current_user.id,
            start_date=start_dt,
            end_date=end_dt,
            spread_id=spread_id,
            limit=pagination["size"],
            offset=pagination["offset"]
        )
        
        return {
            "sessions": [
                {
                    "id": session.id,
                    "session_id": session.session_id,
                    "spread_name": session.spread.name,
                    "question": session.question,
                    "status": session.status,
                    "created_at": format_datetime(session.created_at),
                    "completed_at": format_datetime(session.completed_at) if session.completed_at else None,
                    "card_count": len(session.cards) if session.cards else 0
                }
                for session in sessions
            ],
            "page": pagination["page"],
            "size": pagination["size"]
        }
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"日期格式错误: {str(e)}"
        )