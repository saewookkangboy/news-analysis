"""
분석 결과 정규화 유틸리티
분석 유형별로 다른 구조의 결과를 표준화된 형태로 변환합니다.
"""
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


def normalize_analysis_result(
    raw_result: Dict[str, Any],
    target_type: str
) -> Dict[str, Any]:
    """
    분석 결과를 표준화된 구조로 정규화합니다.
    
    Args:
        raw_result: AI 모델에서 반환된 원본 결과
        target_type: 분석 유형 ('keyword', 'audience', 'comprehensive')
        
    Returns:
        표준화된 분석 결과 딕셔너리
    """
    try:
        if target_type == "keyword":
            return _normalize_keyword_result(raw_result)
        elif target_type == "audience":
            return _normalize_audience_result(raw_result)
        elif target_type == "comprehensive":
            return _normalize_comprehensive_result(raw_result)
        else:
            logger.warning(f"알 수 없는 분석 유형: {target_type}, 원본 결과 반환")
            return _normalize_generic_result(raw_result)
    except Exception as e:
        logger.error(f"결과 정규화 중 오류: {e}", exc_info=True)
        # 정규화 실패 시 원본 결과를 기본 구조로 감싸서 반환
        return _normalize_generic_result(raw_result)


def _normalize_keyword_result(raw_result: Dict[str, Any]) -> Dict[str, Any]:
    """키워드 분석 결과 정규화"""
    normalized = {
        "target_keyword": raw_result.get("target_keyword", ""),
        "target_type": "keyword",
        "executive_summary": raw_result.get("executive_summary", ""),
        "analysis_overview": raw_result.get("analysis_overview", {}),
        "key_findings": _extract_key_findings(raw_result, "keyword"),
        "detailed_analysis": {
            "trend_analysis": raw_result.get("detailed_analysis", {}).get("trend_analysis", {}),
            "related_keywords": raw_result.get("detailed_analysis", {}).get("related_keywords_clusters", {}),
            "sentiment_analysis": raw_result.get("detailed_analysis", {}).get("sentiment_analysis", {}),
            "competition_analysis": raw_result.get("detailed_analysis", {}).get("competition_alternative_keywords", {}),
        },
        "strategic_recommendations": {
            "channel_operations": raw_result.get("strategic_implications", {}).get("channel_operations", {}),
            "content_strategy": raw_result.get("strategic_implications", {}).get("content_strategy", {}),
            "kpi_measurement": raw_result.get("strategic_implications", {}).get("kpi_measurement", {}),
        },
        "execution_roadmap": raw_result.get("execution_roadmap", {}),
        "risk_response": raw_result.get("risk_response", {}),
        "appendix": raw_result.get("appendix", {}),
        "metadata": {
            "analysis_type": "keyword",
            "has_trend_data": bool(raw_result.get("detailed_analysis", {}).get("trend_analysis")),
            "has_sentiment_data": bool(raw_result.get("detailed_analysis", {}).get("sentiment_analysis")),
            "has_competition_data": bool(raw_result.get("detailed_analysis", {}).get("competition_alternative_keywords")),
        }
    }
    
    # 하위 호환성을 위한 기존 필드 유지
    if "key_findings" in raw_result:
        existing_findings = normalized.get("key_findings", {})
        if isinstance(existing_findings, dict):
            normalized["key_findings"] = _merge_findings(
                existing_findings,
                raw_result.get("key_findings", {})
            )
    
    return normalized


def _normalize_audience_result(raw_result: Dict[str, Any]) -> Dict[str, Any]:
    """오디언스 분석 결과 정규화"""
    detailed_audience = raw_result.get("detailed_audience_analysis", {})
    
    normalized = {
        "target_keyword": raw_result.get("target_keyword", ""),
        "target_type": "audience",
        "executive_summary": raw_result.get("executive_summary", ""),
        "analysis_overview": raw_result.get("analysis_overview", {}),
        "key_insights": raw_result.get("key_insights", []),
        "detailed_analysis": {
            "segmentation": detailed_audience.get("segmentation", {}),
            "customer_journey": detailed_audience.get("customer_journey_decision", {}),
            "personas": detailed_audience.get("personas", []),
        },
        "strategic_recommendations": {
            "channel_strategy": raw_result.get("strategic_recommendations", {}).get("persona_based_channel_strategy", {}),
            "content_strategy": raw_result.get("strategic_recommendations", {}).get("content_strategy", {}),
            "kpi_framework": raw_result.get("strategic_recommendations", {}).get("kpi_measurement_framework", {}),
        },
        "execution_roadmap": raw_result.get("execution_roadmap", {}),
        "risk_governance": raw_result.get("risk_governance", {}),
        "appendix": raw_result.get("appendix", {}),
        "metadata": {
            "analysis_type": "audience",
            "persona_count": len(detailed_audience.get("personas", [])),
            "segment_count": len(detailed_audience.get("segmentation", {}).get("segments", [])),
            "has_journey_data": bool(detailed_audience.get("customer_journey_decision")),
        }
    }
    
    return normalized


def _normalize_comprehensive_result(raw_result: Dict[str, Any]) -> Dict[str, Any]:
    """종합 분석 결과 정규화"""
    integrated = raw_result.get("integrated_analysis", {})
    
    normalized = {
        "target_keyword": raw_result.get("target_keyword", ""),
        "target_type": "comprehensive",
        "executive_summary": raw_result.get("executive_summary", ""),
        "key_findings": {
            "integrated_insights": raw_result.get("key_findings", {}).get("integrated_insights", []),
            "quantitative_metrics": raw_result.get("key_findings", {}).get("quantitative_metrics", {}),
        },
        "detailed_analysis": {
            "keyword_audience_alignment": integrated.get("keyword_audience_alignment", {}),
            "keyword_insights": integrated.get("core_keyword_insights", {}),
            "audience_insights": integrated.get("core_audience_insights", {}),
            "trends_and_patterns": integrated.get("trends_and_patterns", {}),
        },
        "strategic_recommendations": {
            "immediate_actions": raw_result.get("forward_looking_recommendations", {}).get("immediate_actions", []),
            "content_strategy": raw_result.get("forward_looking_recommendations", {}).get("content_strategy", {}),
            "marketing_strategy": raw_result.get("forward_looking_recommendations", {}).get("marketing_strategy", {}),
            "short_term_goals": raw_result.get("forward_looking_recommendations", {}).get("short_term_goals", []),
            "long_term_vision": raw_result.get("forward_looking_recommendations", {}).get("long_term_vision", []),
            "success_metrics": raw_result.get("forward_looking_recommendations", {}).get("success_metrics", {}),
        },
        "metadata": {
            "analysis_type": "comprehensive",
            "has_keyword_data": bool(integrated.get("core_keyword_insights")),
            "has_audience_data": bool(integrated.get("core_audience_insights")),
            "has_alignment_data": bool(integrated.get("keyword_audience_alignment")),
        }
    }
    
    return normalized


def _normalize_generic_result(raw_result: Dict[str, Any]) -> Dict[str, Any]:
    """일반적인 결과 정규화 (알 수 없는 유형)"""
    return {
        "target_keyword": raw_result.get("target_keyword", ""),
        "target_type": raw_result.get("target_type", "unknown"),
        "executive_summary": raw_result.get("executive_summary", ""),
        "key_findings": raw_result.get("key_findings", {}),
        "detailed_analysis": raw_result.get("detailed_analysis", {}),
        "strategic_recommendations": raw_result.get("strategic_recommendations", {}),
        "raw_data": raw_result,  # 원본 데이터 보존
        "metadata": {
            "analysis_type": "generic",
            "normalized": False,
        }
    }


def _extract_key_findings(raw_result: Dict[str, Any], analysis_type: str) -> Dict[str, Any]:
    """핵심 발견사항 추출"""
    if analysis_type == "keyword":
        key_findings = raw_result.get("key_findings", [])
        if isinstance(key_findings, list):
            return {
                "findings": key_findings,
                "primary_insights": [f.get("finding", "") for f in key_findings if isinstance(f, dict)],
            }
        elif isinstance(key_findings, dict):
            return key_findings
    elif analysis_type == "audience":
        key_insights = raw_result.get("key_insights", [])
        return {
            "insights": key_insights,
            "summary": raw_result.get("executive_summary", ""),
        }
    
    return raw_result.get("key_findings", {})


def _merge_findings(normalized: Dict[str, Any], original: Dict[str, Any]) -> Dict[str, Any]:
    """발견사항 병합"""
    merged = normalized.copy()
    
    if isinstance(original, dict):
        for key, value in original.items():
            if key not in merged or not merged[key]:
                merged[key] = value
            elif isinstance(merged[key], list) and isinstance(value, list):
                merged[key] = list(set(merged[key] + value))
            elif isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = {**merged[key], **value}
    
    return merged


def ensure_result_structure(result: Dict[str, Any], target_type: str) -> Dict[str, Any]:
    """
    결과에 필수 필드가 있는지 확인하고 없으면 기본값으로 채웁니다.
    
    Args:
        result: 분석 결과
        target_type: 분석 유형
        
    Returns:
        필수 필드가 보장된 결과
    """
    # 기본 필수 필드
    if "target_keyword" not in result:
        result["target_keyword"] = ""
    if "target_type" not in result:
        result["target_type"] = target_type
    if "executive_summary" not in result:
        result["executive_summary"] = "분석 결과 요약이 제공되지 않았습니다."
    
    # 분석 유형별 필수 필드 확인
    if target_type == "keyword":
        if "detailed_analysis" not in result:
            result["detailed_analysis"] = {}
        if "trend_analysis" not in result.get("detailed_analysis", {}):
            result["detailed_analysis"]["trend_analysis"] = {}
    
    elif target_type == "audience":
        if "detailed_analysis" not in result:
            result["detailed_analysis"] = {}
        if "personas" not in result.get("detailed_analysis", {}):
            result["detailed_analysis"]["personas"] = []
    
    elif target_type == "comprehensive":
        if "key_findings" not in result:
            result["key_findings"] = {}
        if "integrated_insights" not in result.get("key_findings", {}):
            result["key_findings"]["integrated_insights"] = []
    
    return result
