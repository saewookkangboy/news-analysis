/**
 * 분석 결과 정규화 유틸리티
 * 백엔드에서 받은 분석 결과를 프론트엔드에서 사용하기 쉬운 형태로 변환합니다.
 */
import {
  TargetAnalysisResult,
  NormalizedAnalysisResult,
  KeywordAnalysisResult,
  AudienceAnalysisResult,
  ComprehensiveAnalysisResult,
} from '../types/analysis';

/**
 * 분석 결과를 정규화된 형태로 변환
 */
export function normalizeAnalysisResult(
  result: TargetAnalysisResult
): NormalizedAnalysisResult | TargetAnalysisResult {
  if (!result || !result.target_type) {
    return result;
  }

  const targetType = result.target_type;

  try {
    switch (targetType) {
      case 'keyword':
        return normalizeKeywordResult(result);
      case 'audience':
        return normalizeAudienceResult(result);
      case 'comprehensive':
        return normalizeComprehensiveResult(result);
      default:
        return result;
    }
  } catch (error) {
    console.error('분석 결과 정규화 실패:', error);
    return result;
  }
}

/**
 * 키워드 분석 결과 정규화
 */
function normalizeKeywordResult(
  result: TargetAnalysisResult
): KeywordAnalysisResult {
  return {
    target_keyword: result.target_keyword || '',
    target_type: 'keyword',
    executive_summary: result.executive_summary || '',
    analysis_overview: result.analysis_overview || {},
    key_findings: result.key_findings || {
      findings: [],
      primary_insights: [],
    },
    detailed_analysis: {
      trend_analysis: result.detailed_analysis?.trend_analysis || {},
      related_keywords: result.detailed_analysis?.related_keywords || {},
      sentiment_analysis: result.detailed_analysis?.sentiment_analysis || {},
      competition_analysis: result.detailed_analysis?.competition_analysis || {},
    },
    strategic_recommendations: result.strategic_recommendations || {},
    execution_roadmap: result.execution_roadmap || {},
    risk_response: (result as any).risk_response,
    appendix: (result as any).appendix,
    metadata: result.metadata || {
      analysis_type: 'keyword',
    },
  };
}

/**
 * 오디언스 분석 결과 정규화
 */
function normalizeAudienceResult(
  result: TargetAnalysisResult
): AudienceAnalysisResult {
  return {
    target_keyword: result.target_keyword || '',
    target_type: 'audience',
    executive_summary: result.executive_summary || '',
    analysis_overview: result.analysis_overview || {},
    key_insights: result.key_insights || [],
    detailed_analysis: {
      segmentation: result.detailed_analysis?.segmentation || {},
      customer_journey: result.detailed_analysis?.customer_journey || {},
      personas: result.detailed_analysis?.personas || [],
    },
    strategic_recommendations: result.strategic_recommendations || {},
    execution_roadmap: result.execution_roadmap || {},
    risk_governance: (result as any).risk_governance,
    appendix: (result as any).appendix,
    metadata: result.metadata || {
      analysis_type: 'audience',
    },
  };
}

/**
 * 종합 분석 결과 정규화
 */
function normalizeComprehensiveResult(
  result: TargetAnalysisResult
): ComprehensiveAnalysisResult {
  return {
    target_keyword: result.target_keyword || '',
    target_type: 'comprehensive',
    executive_summary: result.executive_summary || '',
    key_findings: result.key_findings || {
      integrated_insights: [],
      quantitative_metrics: {},
    },
    detailed_analysis: {
      keyword_audience_alignment: result.detailed_analysis?.keyword_audience_alignment || {},
      keyword_insights: result.detailed_analysis?.keyword_insights || {},
      audience_insights: result.detailed_analysis?.audience_insights || {},
      trends_and_patterns: result.detailed_analysis?.trends_and_patterns || {},
    },
    strategic_recommendations: result.strategic_recommendations || {},
    metadata: result.metadata || {
      analysis_type: 'comprehensive',
    },
  };
}

/**
 * 분석 유형별로 결과에서 핵심 정보 추출
 */
export function extractKeyInsights(result: NormalizedAnalysisResult): {
  summary: string;
  insights: string[];
  recommendations: string[];
} {
  const summary = result.executive_summary || '';
  let insights: string[] = [];
  let recommendations: string[] = [];

  if (result.target_type === 'keyword') {
    const keywordResult = result as KeywordAnalysisResult;
    insights = keywordResult.key_findings?.primary_insights || [];
    recommendations =
      keywordResult.strategic_recommendations?.immediate_actions || [];
  } else if (result.target_type === 'audience') {
    const audienceResult = result as AudienceAnalysisResult;
    insights = audienceResult.key_insights?.map((i) => i.insight) || [];
    recommendations =
      audienceResult.strategic_recommendations?.immediate_actions || [];
  } else if (result.target_type === 'comprehensive') {
    const comprehensiveResult = result as ComprehensiveAnalysisResult;
    insights = comprehensiveResult.key_findings?.integrated_insights || [];
    recommendations =
      comprehensiveResult.strategic_recommendations?.immediate_actions || [];
  }

  return { summary, insights, recommendations };
}

/**
 * 분석 결과에서 페르소나 정보 추출 (오디언스 분석용)
 */
export function extractPersonas(
  result: NormalizedAnalysisResult
): Array<{
  name: string;
  summary: string;
  painPoints: string[];
}> {
  if (result.target_type !== 'audience') {
    return [];
  }

  const audienceResult = result as AudienceAnalysisResult;
  return (audienceResult.detailed_analysis?.personas || []).map((persona) => ({
    name: persona.persona_name,
    summary: persona.one_line_summary,
    painPoints: persona.pain_points || [],
  }));
}

/**
 * 분석 결과에서 키워드 클러스터 추출 (키워드 분석용)
 */
export function extractKeywordClusters(
  result: NormalizedAnalysisResult
): {
  synonyms: string[];
  problemSolution: string[];
  comparison: string[];
  purchase: string[];
  brand: string[];
} {
  if (result.target_type !== 'keyword') {
    return {
      synonyms: [],
      problemSolution: [],
      comparison: [],
      purchase: [],
      brand: [],
    };
  }

  const keywordResult = result as KeywordAnalysisResult;
  const relatedKeywords = keywordResult.detailed_analysis?.related_keywords || {};

  return {
    synonyms: relatedKeywords.synonyms_similar || [],
    problemSolution: relatedKeywords.problem_solution || [],
    comparison: relatedKeywords.comparison_alternative || [],
    purchase: relatedKeywords.purchase_conversion || [],
    brand: relatedKeywords.brand_product || [],
  };
}
