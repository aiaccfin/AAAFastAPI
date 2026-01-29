# 可以定义标准的 metadata 结构
class PaymentMetadata(SQLModel):
    # 系统信息
    created_by: str
    created_at: str
    processed_by: Optional[str] = None
    processing_time_ms: Optional[int] = None
    
    # 审计信息  
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    
    # 工作流
    approval_required: bool = False
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[str] = None
    
    # 集成
    payment_gateway: Optional[str] = None
    gateway_transaction_id: Optional[str] = None
    gateway_response: Optional[Dict[str, Any]] = None
    
    # 自定义字段
    custom_fields: Dict[str, Any] = {}
    
    # AI 分析
    openai_analysis: Optional[Dict[str, Any]] = None

# 使用时自动构建
def create_payment_metadata(user: User, request: Request) -> Dict:
    return PaymentMetadata(
        created_by=user.id,
        created_at=datetime.utcnow().isoformat(),
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    ).dict()