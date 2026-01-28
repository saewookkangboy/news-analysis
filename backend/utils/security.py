"""
보안 유틸리티 모듈
API 키 검증 및 보안 관련 기능
"""
import os
import logging
from typing import Optional, Tuple, Dict, Any
from backend.config import settings

logger = logging.getLogger(__name__)


def validate_api_key(api_key: Optional[str], key_name: str = "API_KEY") -> bool:
    """
    API 키 유효성 검증 (강화된 검증 로직)
    
    Args:
        api_key: 검증할 API 키
        key_name: API 키 이름 (로깅용)
        
    Returns:
        유효한 API 키인지 여부
    """
    if not api_key:
        return False
    
    # 빈 문자열 및 공백만 있는 경우 체크
    api_key_stripped = api_key.strip()
    if not api_key_stripped:
        logger.warning(f"{key_name}: 빈 문자열 또는 공백만 포함")
        return False
    
    # API 키 타입별 검증
    if key_name == "OPENAI_API_KEY":
        if not api_key_stripped.startswith("sk-"):
            logger.warning(f"{key_name}: OpenAI API 키 형식이 올바르지 않음 (sk-로 시작해야 함)")
            return False
        if len(api_key_stripped) < 20:  # OpenAI 키는 보통 20자 이상
            logger.warning(f"{key_name}: 길이가 너무 짧음 (최소 20자 필요)")
            return False
    elif key_name == "GEMINI_API_KEY":
        if len(api_key_stripped) < 20:  # Gemini 키는 보통 20자 이상
            logger.warning(f"{key_name}: 길이가 너무 짧음 (최소 20자 필요)")
            return False
    else:
        # 기타 API 키는 최소 20자 체크
        if len(api_key_stripped) < 20:
            logger.warning(f"{key_name}: 길이가 너무 짧음 (최소 20자 필요)")
            return False
    
    return True


def get_api_key_safely(key_name: str, from_settings: bool = True) -> Optional[str]:
    """
    안전하게 API 키를 가져옵니다 (로깅 없이)
    
    Args:
        key_name: 환경 변수 이름 (예: 'OPENAI_API_KEY')
        from_settings: Settings에서도 확인할지 여부
        
    Returns:
        API 키 또는 None
    """
    # 환경 변수에서 먼저 확인
    api_key = os.getenv(key_name)
    
    # Settings에서 확인 (환경 변수가 없을 경우)
    if not api_key and from_settings:
        api_key = getattr(settings, key_name, None)
    
    # 유효성 검증
    if api_key and validate_api_key(api_key, key_name):
        return api_key.strip()
    
    return None


def check_api_keys_status() -> Dict[str, Any]:
    """
    API 키 상태를 안전하게 확인합니다 (키 값은 노출하지 않음)
    
    Returns:
        API 키 상태 정보 딕셔너리
    """
    openai_key = get_api_key_safely('OPENAI_API_KEY')
    gemini_key = get_api_key_safely('GEMINI_API_KEY')
    
    has_openai = bool(openai_key)
    has_gemini = bool(gemini_key)
    
    status = {
        "openai_configured": has_openai,
        "gemini_configured": has_gemini,
        "message": ""
    }
    
    if not has_openai and not has_gemini:
        status["message"] = "❌ OpenAI API 키와 Gemini API 키가 모두 설정되지 않았습니다."
    elif not has_openai:
        status["message"] = "⚠️ OpenAI API 키가 설정되지 않았습니다."
    elif not has_gemini:
        status["message"] = "ℹ️ Gemini API 키가 설정되지 않았습니다."
    else:
        status["message"] = "✅ 모든 API 키가 설정되었습니다."
    
    return status


def log_api_key_status_safely(key_name: str, is_configured: bool) -> None:
    """
    API 키 상태를 안전하게 로깅합니다 (키 값은 노출하지 않음)
    
    Args:
        key_name: API 키 이름
        is_configured: 설정 여부
    """
    status = "✅ 설정됨" if is_configured else "❌ 미설정"
    logger.info(f"{key_name}: {status}")


def mask_api_key(api_key: Optional[str], show_length: bool = False) -> str:
    """
    API 키를 마스킹하여 안전하게 표시합니다
    
    Args:
        api_key: 마스킹할 API 키
        show_length: 길이를 표시할지 여부
        
    Returns:
        마스킹된 API 키 문자열
    """
    if not api_key:
        return "None"
    
    api_key_stripped = api_key.strip()
    if len(api_key_stripped) <= 8:
        return "***"
    
    # 앞 4자리와 뒤 4자리만 표시
    masked = f"{api_key_stripped[:4]}...{api_key_stripped[-4:]}"
    
    if show_length:
        masked += f" (길이: {len(api_key_stripped)} 문자)"
    
    return masked
