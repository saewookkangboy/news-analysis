"""
에러 핸들링 유틸리티 모듈
API 에러 처리 표준화
"""
import logging
from typing import Optional, Dict, Any
from fastapi import HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class APIError(Exception):
    """API 에러 기본 클래스"""
    def __init__(self, message: str, status_code: int = 500, error_code: Optional[str] = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)


class ValidationError(APIError):
    """입력 검증 에러"""
    def __init__(self, message: str, field: Optional[str] = None):
        error_code = f"VALIDATION_ERROR_{field.upper()}" if field else "VALIDATION_ERROR"
        super().__init__(message, status_code=400, error_code=error_code)
        self.field = field


class NotFoundError(APIError):
    """리소스를 찾을 수 없음"""
    def __init__(self, message: str = "요청한 리소스를 찾을 수 없습니다."):
        super().__init__(message, status_code=404, error_code="NOT_FOUND")


class UnauthorizedError(APIError):
    """인증 에러"""
    def __init__(self, message: str = "인증이 필요합니다."):
        super().__init__(message, status_code=401, error_code="UNAUTHORIZED")


class ForbiddenError(APIError):
    """권한 에러"""
    def __init__(self, message: str = "접근 권한이 없습니다."):
        super().__init__(message, status_code=403, error_code="FORBIDDEN")


class ServiceUnavailableError(APIError):
    """서비스 사용 불가 에러 (AI API 실패 등)"""
    def __init__(self, message: str = "서비스를 사용할 수 없습니다."):
        super().__init__(message, status_code=503, error_code="SERVICE_UNAVAILABLE")


def handle_api_error(error: Exception, context: Optional[str] = None) -> HTTPException:
    """
    API 에러를 처리하고 HTTPException으로 변환
    
    Args:
        error: 발생한 예외
        context: 에러 발생 컨텍스트 (예: "타겟 분석")
        
    Returns:
        HTTPException
    """
    context_str = f"{context}: " if context else ""
    
    # 커스텀 API 에러인 경우
    if isinstance(error, APIError):
        logger.error(f"{context_str}{error.message} (코드: {error.error_code})")
        return HTTPException(
            status_code=error.status_code,
            detail={
                "error": error.message,
                "error_code": error.error_code,
                "context": context
            }
        )
    
    # ValueError (일반적으로 검증 에러)
    if isinstance(error, ValueError):
        logger.error(f"{context_str}검증 에러: {error}")
        return HTTPException(
            status_code=400,
            detail={
                "error": str(error),
                "error_code": "VALIDATION_ERROR",
                "context": context
            }
        )
    
    # 기타 예외
    logger.error(f"{context_str}예외 발생: {type(error).__name__}: {error}", exc_info=True)
    return HTTPException(
        status_code=500,
        detail={
            "error": "내부 서버 오류가 발생했습니다.",
            "error_code": "INTERNAL_SERVER_ERROR",
            "context": context
        }
    )


def create_error_response(
    error: Exception,
    context: Optional[str] = None,
    include_details: bool = False
) -> JSONResponse:
    """
    에러 응답 생성
    
    Args:
        error: 발생한 예외
        context: 에러 발생 컨텍스트
        include_details: 상세 정보 포함 여부 (프로덕션에서는 False)
        
    Returns:
        JSONResponse
    """
    if isinstance(error, APIError):
        status_code = error.status_code
        error_detail = {
            "error": error.message,
            "error_code": error.error_code,
        }
        if context:
            error_detail["context"] = context
        if include_details:
            error_detail["details"] = str(error)
    elif isinstance(error, ValueError):
        status_code = 400
        error_detail = {
            "error": str(error),
            "error_code": "VALIDATION_ERROR",
        }
        if context:
            error_detail["context"] = context
    else:
        status_code = 500
        error_detail = {
            "error": "내부 서버 오류가 발생했습니다.",
            "error_code": "INTERNAL_SERVER_ERROR",
        }
        if context:
            error_detail["context"] = context
        if include_details:
            error_detail["details"] = str(error)
    
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            **error_detail
        }
    )


def validate_target_type(target_type: str) -> None:
    """
    타겟 타입 검증
    
    Args:
        target_type: 검증할 타겟 타입
        
    Raises:
        ValidationError: 유효하지 않은 타겟 타입인 경우
    """
    valid_types = ["keyword", "audience", "comprehensive"]
    if target_type not in valid_types:
        raise ValidationError(
            f"target_type은 {', '.join(valid_types)} 중 하나여야 합니다.",
            field="target_type"
        )


def validate_date_format(date_str: Optional[str], field_name: str = "date") -> None:
    """
    날짜 형식 및 유효성 검증 (YYYY-MM-DD)
    
    Args:
        date_str: 검증할 날짜 문자열
        field_name: 필드 이름
        
    Raises:
        ValidationError: 유효하지 않은 날짜 형식 또는 유효하지 않은 날짜인 경우
    """
    if date_str is None:
        return
    
    import re
    from datetime import datetime
    
    # 형식 검증 (YYYY-MM-DD)
    date_pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(date_pattern, date_str):
        raise ValidationError(
            f"{field_name}는 YYYY-MM-DD 형식이어야 합니다. (예: 2026-01-28)",
            field=field_name
        )
    
    # 유효한 날짜인지 검증
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValidationError(
            f"{field_name}는 유효한 날짜여야 합니다. (예: 2026-01-28, 잘못된 예: 2025-13-01)",
            field=field_name
        )
