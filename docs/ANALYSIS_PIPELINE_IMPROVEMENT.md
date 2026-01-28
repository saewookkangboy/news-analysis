# 분석 유형별 데이터 파이프라인 개선

**작성일**: 2026-01-28  
**목적**: 분석 유형별로 다른 구조의 결과를 표준화하여 프론트엔드에서 일관되게 처리할 수 있도록 개선

## 개요

기존에는 `keyword`, `audience`, `comprehensive` 세 가지 분석 유형이 각각 다른 JSON 구조를 반환하여 프론트엔드에서 일관되게 처리하기 어려웠습니다. 이번 개선을 통해:

1. **백엔드 정규화 레이어**: 분석 유형별 결과를 표준화된 구조로 변환
2. **프론트엔드 타입 정의 강화**: 각 분석 유형별 상세 타입 정의
3. **데이터 변환 유틸리티**: 백엔드 결과를 프론트엔드에서 사용하기 쉬운 형태로 변환

## 구현 내용

### 1. 백엔드 정규화 레이어

**파일**: `backend/utils/result_normalizer.py`

#### 주요 기능

- `normalize_analysis_result()`: 분석 유형별로 결과를 표준화된 구조로 변환
- `ensure_result_structure()`: 필수 필드가 있는지 확인하고 기본값으로 채움

#### 정규화된 구조

**키워드 분석 (`keyword`)**:
```python
{
    "target_keyword": str,
    "target_type": "keyword",
    "executive_summary": str,
    "analysis_overview": {...},
    "key_findings": {
        "findings": [...],
        "primary_insights": [...]
    },
    "detailed_analysis": {
        "trend_analysis": {...},
        "related_keywords": {...},
        "sentiment_analysis": {...},
        "competition_analysis": {...}
    },
    "strategic_recommendations": {...},
    "execution_roadmap": {...},
    "metadata": {
        "analysis_type": "keyword",
        "has_trend_data": bool,
        "has_sentiment_data": bool,
        "has_competition_data": bool
    }
}
```

**오디언스 분석 (`audience`)**:
```python
{
    "target_keyword": str,
    "target_type": "audience",
    "executive_summary": str,
    "analysis_overview": {...},
    "key_insights": [...],
    "detailed_analysis": {
        "segmentation": {...},
        "customer_journey": {...},
        "personas": [...]
    },
    "strategic_recommendations": {...},
    "execution_roadmap": {...},
    "metadata": {
        "analysis_type": "audience",
        "persona_count": int,
        "segment_count": int,
        "has_journey_data": bool
    }
}
```

**종합 분석 (`comprehensive`)**:
```python
{
    "target_keyword": str,
    "target_type": "comprehensive",
    "executive_summary": str,
    "key_findings": {
        "integrated_insights": [...],
        "quantitative_metrics": {...}
    },
    "detailed_analysis": {
        "keyword_audience_alignment": {...},
        "keyword_insights": {...},
        "audience_insights": {...},
        "trends_and_patterns": {...}
    },
    "strategic_recommendations": {...},
    "metadata": {
        "analysis_type": "comprehensive",
        "has_keyword_data": bool,
        "has_audience_data": bool,
        "has_alignment_data": bool
    }
}
```

### 2. 백엔드 통합

**파일**: `backend/services/target_analyzer.py`

`analyze_target()` 함수에서 결과 반환 전에 정규화 레이어를 통과하도록 수정:

```python
# 결과 정규화 (분석 유형별 표준화된 구조로 변환)
normalized_result = normalize_analysis_result(result, target_type)
normalized_result = ensure_result_structure(normalized_result, target_type)
return normalized_result
```

### 3. 프론트엔드 타입 정의

**파일**: `frontend/src/types/analysis.ts`

#### 주요 타입

- `KeywordAnalysisResult`: 키워드 분석 결과 타입
- `AudienceAnalysisResult`: 오디언스 분석 결과 타입
- `ComprehensiveAnalysisResult`: 종합 분석 결과 타입
- `NormalizedAnalysisResult`: 통합 타입 (유니온 타입)

각 타입은 해당 분석 유형의 모든 필드를 명시적으로 정의하여 타입 안정성을 보장합니다.

### 4. 프론트엔드 데이터 변환 유틸리티

**파일**: `frontend/src/utils/analysisNormalizer.ts`

#### 주요 함수

- `normalizeAnalysisResult()`: 백엔드 결과를 정규화된 형태로 변환
- `extractKeyInsights()`: 분석 유형별로 핵심 인사이트 추출
- `extractPersonas()`: 오디언스 분석에서 페르소나 정보 추출
- `extractKeywordClusters()`: 키워드 분석에서 키워드 클러스터 추출

### 5. 프론트엔드 서비스 업데이트

**파일**: `frontend/src/services/analysisService.ts`

모든 분석 API 호출에서 결과를 자동으로 정규화하도록 수정:

```typescript
const response = await apiCall<TargetAnalysisResult>('/target/analyze', {...});

// 결과 정규화
if (response.success && response.data) {
  return {
    ...response,
    data: normalizeAnalysisResult(response.data) as NormalizedAnalysisResult,
  };
}
```

## 사용 예시

### 백엔드에서 정규화된 결과 반환

```python
# target_analyzer.py에서 자동으로 정규화됨
result = await analyze_target(
    target_keyword="마케팅",
    target_type="keyword"
)
# result는 이미 정규화된 구조
```

### 프론트엔드에서 타입 안전하게 사용

```typescript
import { AnalysisService } from '../services/analysisService';
import type { NormalizedAnalysisResult } from '../types/analysis';

const response = await AnalysisService.analyzeTarget({
  target_keyword: '마케팅',
  target_type: 'keyword'
});

if (response.success && response.data) {
  const result = response.data; // NormalizedAnalysisResult 타입
  
  // 타입 안전하게 접근
  if (result.target_type === 'keyword') {
    const trendAnalysis = result.detailed_analysis.trend_analysis;
    const relatedKeywords = result.detailed_analysis.related_keywords;
  }
}
```

### 유틸리티 함수 사용

```typescript
import { extractKeyInsights, extractPersonas } from '../utils/analysisNormalizer';

const { summary, insights, recommendations } = extractKeyInsights(result);
const personas = extractPersonas(result); // 오디언스 분석인 경우만
```

## 장점

1. **타입 안정성**: TypeScript 타입 정의로 컴파일 타임에 오류 발견
2. **일관성**: 모든 분석 유형이 표준화된 구조로 반환
3. **유지보수성**: 분석 유형별 구조가 명확히 정의되어 수정이 용이
4. **확장성**: 새로운 분석 유형 추가 시 정규화 레이어에만 추가하면 됨
5. **하위 호환성**: 기존 코드와의 호환성 유지

## 향후 개선 사항

1. **분석 결과 표시 컴포넌트 개선**: 분석 유형별로 적절한 UI 렌더링
2. **캐싱 전략**: 정규화된 결과를 캐시하여 성능 향상
3. **에러 핸들링 강화**: 정규화 실패 시 상세한 에러 정보 제공
4. **유효성 검증**: 정규화된 결과의 유효성 검증 로직 추가

## 관련 파일

- `backend/utils/result_normalizer.py`: 백엔드 정규화 레이어
- `backend/services/target_analyzer.py`: 분석 서비스 (정규화 통합)
- `frontend/src/types/analysis.ts`: 프론트엔드 타입 정의
- `frontend/src/utils/analysisNormalizer.ts`: 프론트엔드 변환 유틸리티
- `frontend/src/services/analysisService.ts`: API 서비스 (정규화 통합)

## 변경 이력

- 2026-01-28: 초기 구현 완료
  - 백엔드 정규화 레이어 추가
  - 프론트엔드 타입 정의 강화
  - 데이터 변환 유틸리티 추가
  - API 서비스에 정규화 통합
