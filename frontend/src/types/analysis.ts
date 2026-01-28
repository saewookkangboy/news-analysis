/**
 * 분석 결과 타입 정의
 * 분석 유형별로 상세한 타입을 정의하여 타입 안정성을 보장합니다.
 */

// 기본 메타데이터
export interface AnalysisMetadata {
  analysis_type: 'keyword' | 'audience' | 'comprehensive';
  has_trend_data?: boolean;
  has_sentiment_data?: boolean;
  has_competition_data?: boolean;
  persona_count?: number;
  segment_count?: number;
  has_journey_data?: boolean;
  has_keyword_data?: boolean;
  has_audience_data?: boolean;
  has_alignment_data?: boolean;
  normalized?: boolean;
}

// 분석 개요
export interface AnalysisOverview {
  purpose_scope?: string;
  period_market_sources?: string;
  methodology?: {
    research_approach?: string;
    limitations_assumptions?: string;
    research_logic?: string;
  };
}

// 키워드 분석 관련 타입
export interface KeywordTrendAnalysis {
  interest_change_summary?: string;
  spike_causes?: Array<{
    rank: number;
    hypothesis: string;
    verification_points: string;
  }>;
  seasonality_event_news?: string;
}

export interface RelatedKeywordsClusters {
  synonyms_similar?: string[];
  problem_solution?: string[];
  comparison_alternative?: string[];
  purchase_conversion?: string[];
  brand_product?: string[];
  cluster_intent_mapping?: {
    informational?: string[];
    commercial?: string[];
    transactional?: string[];
    navigational?: string[];
  };
  recommended_content_formats?: {
    guide?: string;
    list?: string;
    case_study?: string;
    faq?: string;
    tool?: string;
    checklist?: string;
  };
}

export interface KeywordSentimentAnalysis {
  sentiment_distribution?: {
    positive?: string;
    negative?: string;
    neutral?: string;
  };
  positive_drivers?: {
    keywords?: string[];
    representative_sentences?: string[];
  };
  negative_drivers?: {
    keywords?: string[];
    representative_sentences?: string[];
  };
  risk_early_warning_keywords?: string[];
}

export interface KeywordCompetitionAnalysis {
  competitors?: string[];
  positioning_framework?: {
    price?: string;
    performance?: string;
    trust?: string;
    convenience?: string;
    support?: string;
  };
  differentiation_points?: string[];
}

// 오디언스 분석 관련 타입
export interface AudienceSegmentation {
  segmentation_criteria?: {
    needs_problems?: string;
    purchase_motivation?: string;
    usage_context?: string;
    budget_sensitivity?: string;
    channel_preference?: string;
  };
  segments?: Array<{
    segment_name: string;
    size_estimate: string;
    growth_potential: string;
    priority: string;
  }>;
}

export interface CustomerJourneyStage {
  key_questions?: string[];
  information_sources?: string[];
  conversion_barriers?: string[];
  persuasion_levers?: string[];
}

export interface CustomerJourney {
  awareness?: CustomerJourneyStage;
  consideration?: CustomerJourneyStage;
  conversion?: CustomerJourneyStage;
  retention?: CustomerJourneyStage;
}

export interface Persona {
  persona_name: string;
  one_line_summary: string;
  background: {
    occupation?: string;
    lifestyle?: string;
    digital_literacy?: string;
  };
  goals_success_criteria?: string;
  pain_points?: string[];
  trigger?: string;
  objection?: string;
  channels_content_habits?: string;
  preferred_message_tone?: string;
  conversion_proof_needed?: string;
  recommended_content_offer?: string;
  prohibited_messages?: string;
}

// 종합 분석 관련 타입
export interface KeywordAudienceAlignment {
  search_intent_match?: string;
  keyword_opportunity_for_audience?: string;
  audience_preferred_keywords?: string;
  content_gap_analysis?: string;
}

export interface CoreKeywordInsights {
  primary_search_intent?: string;
  key_opportunity_keywords?: string[];
  trending_keywords?: string[];
  search_volume_trend?: string;
}

export interface CoreAudienceInsights {
  target_demographics?: {
    age_range?: string;
    gender?: string;
    location?: string;
    income_level?: string;
    expected_occupations?: string[];
  };
  key_behavior_patterns?: {
    purchase_behavior?: string;
    media_consumption?: string;
    online_activity?: string;
  };
  core_values_and_needs?: {
    primary_values?: string[];
    main_pain_points?: string[];
    key_aspirations?: string[];
  };
}

export interface TrendsAndPatterns {
  converging_trends?: string[];
  period_analysis?: string;
  future_outlook?: string;
}

// 전략적 권장사항
export interface StrategicRecommendations {
  // 키워드 분석용
  channel_operations?: {
    priority_channels?: Array<{
      channel: string;
      keyword_clusters: string[];
      priority: string;
    }>;
  };
  content_strategy?: {
    tofu_mapping?: {
      keywords?: string[];
      content_types?: string[];
    };
    mofu_mapping?: {
      keywords?: string[];
      content_types?: string[];
    };
    bofu_mapping?: {
      keywords?: string[];
      content_types?: string[];
    };
    content_elements?: {
      title_hook?: string;
      structure_outline?: string;
      faq_aeo?: string;
      geo_local?: string;
    };
  };
  kpi_measurement?: {
    kpi_definitions?: string[];
    dashboard_items?: string[];
    measurement_cycle?: string;
  };
  
  // 오디언스 분석용
  channel_strategy?: {
    persona_channel_matrix?: Array<{
      persona_name: string;
      channels: Array<{
        channel: string;
        message: string;
        format: string;
        effectiveness: string;
      }>;
    }>;
  };
  kpi_framework?: {
    kpi_definitions?: string[];
    event_design?: string;
    reporting_cycle?: string;
  };
  
  // 종합 분석용
  immediate_actions?: string[];
  marketing_strategy?: {
    keyword_targeting?: string;
    messaging_framework?: string;
    channel_strategy?: string;
  };
  short_term_goals?: string[];
  long_term_vision?: string[];
  success_metrics?: {
    keyword_metrics?: string;
    audience_metrics?: string;
    integrated_kpis?: string;
  };
}

// 실행 로드맵
export interface ExecutionRoadmap {
  day_30?: {
    priorities?: string[];
    deliverables?: string[];
    roles_responsibilities?: string;
  };
  day_60?: {
    priorities?: string[];
    deliverables?: string[];
    roles_responsibilities?: string;
  };
  day_90?: {
    priorities?: string[];
    deliverables?: string[];
    roles_responsibilities?: string;
  };
  operational_direction?: {
    editorial_calendar?: string;
    ab_testing?: string;
    repurposing_strategy?: string;
  };
  marketing_governance?: {
    approval_process?: string;
    brand_safety?: string;
    risk_response_rules?: string;
  };
}

// 키워드 분석 결과
export interface KeywordAnalysisResult {
  target_keyword: string;
  target_type: 'keyword';
  executive_summary: string;
  analysis_overview: AnalysisOverview;
  key_findings: {
    findings?: Array<{
      finding: string;
      evidence: string;
      interpretation: string;
      implication: string;
    }>;
    primary_insights?: string[];
  };
  detailed_analysis: {
    trend_analysis: KeywordTrendAnalysis;
    related_keywords: RelatedKeywordsClusters;
    sentiment_analysis: KeywordSentimentAnalysis;
    competition_analysis: KeywordCompetitionAnalysis;
  };
  strategic_recommendations: StrategicRecommendations;
  execution_roadmap: ExecutionRoadmap;
  risk_response?: {
    negative_issue_scenarios?: string[];
    qa?: string[];
    brand_safety_checklist?: string[];
  };
  appendix?: {
    keyword_list_by_cluster?: {
      synonyms?: string[];
      problem_solution?: string[];
      comparison?: string[];
      purchase?: string[];
      brand?: string[];
    };
    references?: Array<{
      id: number;
      citation: string;
      url?: string;
    }>;
  };
  metadata: AnalysisMetadata;
}

// 오디언스 분석 결과
export interface AudienceAnalysisResult {
  target_keyword: string;
  target_type: 'audience';
  executive_summary: string;
  analysis_overview: AnalysisOverview;
  key_insights: Array<{
    insight: string;
    evidence: string;
    interpretation: string;
    implication: string;
  }>;
  detailed_analysis: {
    segmentation: AudienceSegmentation;
    customer_journey: CustomerJourney;
    personas: Persona[];
  };
  strategic_recommendations: StrategicRecommendations;
  execution_roadmap: ExecutionRoadmap;
  risk_governance?: {
    brand_safety?: {
      content_approval_process?: string;
      risk_response_rules?: string;
      escalation_system?: string;
    };
    faq_templates?: string[];
    operational_regulations?: string;
  };
  appendix?: {
    message_bank?: Array<{
      persona_name: string;
      hooks?: string[];
      headlines?: string[];
      ctas?: string[];
    }>;
    references?: Array<{
      id: number;
      citation: string;
      url?: string;
    }>;
  };
  metadata: AnalysisMetadata;
}

// 종합 분석 결과
export interface ComprehensiveAnalysisResult {
  target_keyword: string;
  target_type: 'comprehensive';
  executive_summary: string;
  key_findings: {
    integrated_insights: string[];
    quantitative_metrics: {
      market_size?: string;
      opportunity_score?: string;
      growth_potential?: string;
      competition_level?: string;
      success_probability?: string;
    };
  };
  detailed_analysis: {
    keyword_audience_alignment: KeywordAudienceAlignment;
    keyword_insights: CoreKeywordInsights;
    audience_insights: CoreAudienceInsights;
    trends_and_patterns: TrendsAndPatterns;
  };
  strategic_recommendations: StrategicRecommendations;
  metadata: AnalysisMetadata;
}

// 통합 분석 결과 타입 (유니온 타입)
export type NormalizedAnalysisResult = 
  | KeywordAnalysisResult 
  | AudienceAnalysisResult 
  | ComprehensiveAnalysisResult;

// 기존 호환성을 위한 타입 (하위 호환)
export interface TargetAnalysisResult {
  target_keyword: string;
  target_type: string;
  executive_summary?: string;
  analysis?: {
    overview?: any;
    insights?: any;
    recommendations?: any;
  };
  sentiment?: any;
  context?: any;
  tone?: any;
  recommendations?: any;
  progress_info?: {
    current_step?: string;
    progress?: number;
  };
  // 정규화된 필드들
  analysis_overview?: AnalysisOverview;
  key_findings?: any;
  key_insights?: any[];
  detailed_analysis?: any;
  strategic_recommendations?: StrategicRecommendations;
  execution_roadmap?: ExecutionRoadmap;
  metadata?: AnalysisMetadata;
}
