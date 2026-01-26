# 서비스 고도화 제안서
## 정성적 분석 및 다각도 인사이트 강화

---

## 📋 개요

현재 뉴스 트렌드 분석 서비스를 정성적 분석 관점에서 고도화하고, AI API를 활용하여 보다 넓은 시각의 정보를 제공할 수 있도록 개선하는 제안서입니다.

### 핵심 목표
1. **정성적 분석 강화**: 감정, 맥락, 톤, 사회적 영향 등 정성적 요소 분석
2. **다양한 데이터 추천**: 관련 키워드, 유사 주제, 경쟁 키워드, 보완 키워드 등 자동 추천
3. **다각도 인사이트**: 시장 동향, 사회적 영향, 미래 전망, 비교 분석 등 종합적 관점 제공

---

## 🎯 주요 개선 사항

### 1. 정성적 분석 기능 추가

#### 1.1 감정 분석 (Sentiment Analysis)
- **긍정/부정/중립 감정 분석**
  - 키워드에 대한 대중의 감정 톤 분석
  - 시간대별 감정 변화 추적
  - 감정 강도 점수화 (0-100)

- **구현 방법**:
  ```python
  {
    "sentiment": {
      "overall": "긍정적",
      "score": 72,  # 0-100
      "distribution": {
        "positive": 65,
        "neutral": 25,
        "negative": 10
      },
      "trend": "향상 중",  # 개선/악화/유지
      "key_emotional_drivers": [
        "혁신성에 대한 기대",
        "기술 발전에 대한 관심"
      ]
    }
  }
  ```

#### 1.2 맥락 분석 (Context Analysis)
- **사회적 맥락 이해**
  - 현재 사회적 이슈와의 연관성
  - 문화적/정치적 맥락
  - 시기적 특성 반영

- **구현 방법**:
  ```python
  {
    "context": {
      "social_relevance": "높음",
      "current_issues": [
        "디지털 전환 가속화",
        "AI 규제 논의"
      ],
      "cultural_context": "기술 혁신에 대한 사회적 관심 증가",
      "temporal_factors": "2026년 초반 기술 트렌드"
    }
  }
  ```

#### 1.3 톤 분석 (Tone Analysis)
- **언론/미디어 톤 분석**
  - 전문적/일반적 톤
  - 긍정적/비판적 톤
  - 객관적/주관적 톤

#### 1.4 스토리텔링 분석 (Narrative Analysis)
- **주요 내러티브 파악**
  - 키워드와 관련된 주요 스토리라인
  - 언론/소셜미디어에서 다뤄지는 각도
  - 논쟁 포인트 및 다양한 관점

---

### 2. 다양한 데이터 추천 시스템

#### 2.1 관련 키워드 추천
- **자동 관련 키워드 생성**
  - 시맨틱 유사 키워드
  - 동시 출현 키워드
  - 계층적 관련 키워드 (상위/하위 개념)

- **구현 방법**:
  ```python
  {
    "related_keywords": {
      "semantic_similar": [
        {"keyword": "머신러닝", "relevance": 0.92},
        {"keyword": "딥러닝", "relevance": 0.88}
      ],
      "co_occurring": [
        {"keyword": "빅데이터", "frequency": 0.75},
        {"keyword": "클라우드", "frequency": 0.68}
      ],
      "hierarchical": {
        "broader": ["AI 기술", "디지털 혁신"],
        "narrower": ["자연어처리", "컴퓨터 비전"]
      }
    }
  }
  ```

#### 2.2 유사 주제 추천
- **주제 확장 분석**
  - 유사한 관심사나 주제
  - 보완적 주제
  - 대안 주제

#### 2.3 경쟁/대안 키워드 추천
- **경쟁 키워드 식별**
  - 동일 목적의 대체 키워드
  - 경쟁 강도 분석
  - 선택 가이드 제공

#### 2.4 트렌드 연관 키워드
- **트렌드 연결 분석**
  - 상승 중인 관련 키워드
  - 하락 중인 관련 키워드
  - 신흥 키워드

---

### 3. 다각도 인사이트 강화

#### 3.1 시장 동향 분석
- **시장 관점 분석**
  - 시장 규모 및 성장률
  - 주요 플레이어 동향
  - 시장 세분화 분석

#### 3.2 사회적 영향 분석
- **사회적 파급 효과**
  - 일상생활에 미치는 영향
  - 산업 전반에 미치는 영향
  - 미래 사회 변화 예측

#### 3.3 미래 전망 분석
- **예측적 인사이트**
  - 단기 전망 (3-6개월)
  - 중기 전망 (1-2년)
  - 장기 전망 (3-5년)
  - 불확실성 요인 분석

#### 3.4 비교 분석 기능
- **다중 키워드 비교**
  - 여러 키워드 동시 분석
  - 비교 대시보드
  - 차별화 포인트 분석

#### 3.5 위험/기회 분석
- **리스크 및 기회 포인트**
  - 잠재적 위험 요소
  - 기회 요소
  - 대응 전략 제안

---

### 4. AI 프롬프트 고도화

#### 4.1 다단계 분석 프롬프트
- **1단계: 기본 분석**
  - 키워드 이해 및 정의
  - 기본 정보 수집

- **2단계: 정성적 분석**
  - 감정, 맥락, 톤 분석
  - 내러티브 파악

- **3단계: 확장 분석**
  - 관련 키워드 생성
  - 다각도 인사이트 도출

- **4단계: 종합 및 추천**
  - 모든 분석 결과 통합
  - 실행 가능한 추천 제공

#### 4.2 컨텍스트 강화 프롬프트
- **시대적 맥락 반영**
  - 현재 날짜/시기 정보 포함
  - 최근 이슈 반영
  - 지역적 맥락 (한국 시장 중심)

- **도메인 지식 활용**
  - 산업별 전문 지식
  - 시장 동향 이해
  - 경쟁 환경 분석

---

## 🛠 구현 계획

### Phase 1: 정성적 분석 기능 추가 (우선순위: 높음)

#### 1.1 감정 분석 모듈
```python
# backend/services/sentiment_analyzer.py
async def analyze_sentiment(
    target_keyword: str,
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    감정 분석 수행
    - AI API를 활용한 감정 톤 분석
    - 감정 점수화 및 분포 분석
    """
```

#### 1.2 맥락 분석 모듈
```python
# backend/services/context_analyzer.py
async def analyze_context(
    target_keyword: str,
    additional_context: Optional[str] = None
) -> Dict[str, Any]:
    """
    맥락 분석 수행
    - 사회적/문화적 맥락 이해
    - 시기적 특성 반영
    """
```

#### 1.3 프롬프트 업데이트
- `target_analyzer.py`의 `_build_analysis_prompt` 함수 확장
- 정성적 분석 요청 추가

### Phase 2: 데이터 추천 시스템 (우선순위: 높음)

#### 2.1 관련 키워드 추천 모듈
```python
# backend/services/keyword_recommender.py
async def recommend_related_keywords(
    target_keyword: str,
    max_results: int = 10
) -> Dict[str, Any]:
    """
    관련 키워드 추천
    - AI API를 활용한 시맨틱 유사 키워드 생성
    - 계층적 관계 분석
    """
```

#### 2.2 추천 API 엔드포인트 추가
```python
# backend/api/routes.py
@router.post("/recommend/keywords")
async def recommend_keywords(
    target_keyword: str = Body(...),
    recommendation_type: str = Body("all")
):
    """관련 키워드 추천"""
```

### Phase 3: 다각도 인사이트 강화 (우선순위: 중간)

#### 3.1 종합 분석 모듈
```python
# backend/services/comprehensive_analyzer.py
async def comprehensive_analysis(
    target_keyword: str,
    analysis_depth: str = "standard"  # basic, standard, deep
) -> Dict[str, Any]:
    """
    종합 분석 수행
    - 정량적 + 정성적 분석 통합
    - 다각도 인사이트 제공
    """
```

#### 3.2 비교 분석 기능
```python
# backend/services/comparison_analyzer.py
async def compare_keywords(
    keywords: List[str],
    comparison_aspects: List[str] = None
) -> Dict[str, Any]:
    """
    다중 키워드 비교 분석
    """
```

### Phase 4: UI/UX 개선 (우선순위: 중간)

#### 4.1 분석 결과 시각화
- 감정 분포 차트
- 관련 키워드 네트워크 그래프
- 트렌드 타임라인

#### 4.2 인터랙티브 대시보드
- 탭 기반 결과 표시
  - 기본 분석
  - 정성적 분석
  - 추천 키워드
  - 비교 분석

---

## 📊 새로운 API 엔드포인트

### 1. 정성적 분석
```http
POST /api/analysis/sentiment
Content-Type: application/json

{
  "target_keyword": "인공지능",
  "additional_context": "최신 기술 트렌드"
}
```

**응답 예시:**
```json
{
  "success": true,
  "data": {
    "sentiment": {
      "overall": "긍정적",
      "score": 72,
      "distribution": {...},
      "trend": "향상 중"
    },
    "context": {
      "social_relevance": "높음",
      "current_issues": [...]
    },
    "tone": {
      "professional": 0.85,
      "positive": 0.72,
      "objective": 0.68
    }
  }
}
```

### 2. 키워드 추천
```http
POST /api/recommend/keywords
Content-Type: application/json

{
  "target_keyword": "인공지능",
  "recommendation_type": "all",  # all, semantic, co_occurring, hierarchical
  "max_results": 10
}
```

**응답 예시:**
```json
{
  "success": true,
  "data": {
    "related_keywords": {
      "semantic_similar": [...],
      "co_occurring": [...],
      "hierarchical": {...}
    },
    "trending_related": [...],
    "alternative_keywords": [...]
  }
}
```

### 3. 종합 분석
```http
POST /api/analysis/comprehensive
Content-Type: application/json

{
  "target_keyword": "인공지능",
  "analysis_depth": "deep",  # basic, standard, deep
  "include_recommendations": true
}
```

### 4. 비교 분석
```http
POST /api/analysis/compare
Content-Type: application/json

{
  "keywords": ["인공지능", "머신러닝", "딥러닝"],
  "comparison_aspects": ["sentiment", "trend", "market"]
}
```

---

## 🔄 기존 분석 기능 확장

### 기존 `/api/target/analyze` 엔드포인트 개선

#### 옵션 추가
```python
@router.post("/target/analyze")
async def analyze_target_endpoint(
    target_keyword: str = Body(...),
    target_type: str = Body("keyword"),
    additional_context: Optional[str] = Body(None),
    use_gemini: bool = Body(False),
    include_sentiment: bool = Body(True),  # 새로 추가
    include_recommendations: bool = Body(True),  # 새로 추가
    analysis_depth: str = Body("standard")  # 새로 추가: basic, standard, deep
):
```

#### 응답 구조 확장
```json
{
  "success": true,
  "data": {
    "analysis": {
      // 기존 분석 결과
    },
    "sentiment": {
      // 정성적 분석 결과 (옵션)
    },
    "recommendations": {
      // 추천 키워드 (옵션)
    },
    "insights": {
      // 다각도 인사이트 (옵션)
    }
  }
}
```

---

## 🎨 프롬프트 개선 전략

### 1. 체인 오브 사고 (Chain of Thought) 프롬프트
```
1단계: 키워드 이해 및 정의
2단계: 정량적 분석 (검색량, 경쟁도 등)
3단계: 정성적 분석 (감정, 맥락, 톤)
4단계: 관련 키워드 생성
5단계: 다각도 인사이트 도출
6단계: 종합 및 추천
```

### 2. Few-shot Learning 프롬프트
- 예시를 포함하여 일관된 형식의 응답 유도
- JSON 스키마 명시

### 3. 컨텍스트 강화
- 현재 날짜/시기 정보
- 한국 시장 특성
- 최근 이슈 반영

---

## 📈 예상 효과

### 사용자 경험 개선
1. **더 풍부한 인사이트**: 정량적 + 정성적 분석으로 종합적 이해 가능
2. **자동화된 추천**: 수동 검색 없이 관련 키워드 자동 발견
3. **다각도 분석**: 한 번의 요청으로 다양한 관점의 분석 제공

### 비즈니스 가치
1. **의사결정 지원**: 더 나은 데이터 기반 의사결정
2. **시간 절약**: 여러 도구를 사용할 필요 없이 통합 분석
3. **전략 수립**: 미래 전망 및 위험/기회 분석으로 전략 수립 지원

---

## 🚀 구현 우선순위

### Phase 1 (1-2주)
- [ ] 감정 분석 모듈 구현
- [ ] 맥락 분석 모듈 구현
- [ ] 기존 분석에 정성적 분석 통합
- [ ] 프롬프트 개선

### Phase 2 (2-3주)
- [ ] 관련 키워드 추천 모듈 구현
- [ ] 추천 API 엔드포인트 추가
- [ ] UI에 추천 결과 표시

### Phase 3 (3-4주)
- [ ] 종합 분석 모듈 구현
- [ ] 비교 분석 기능 추가
- [ ] 미래 전망 분석 추가

### Phase 4 (4-5주)
- [ ] UI/UX 개선
- [ ] 시각화 추가
- [ ] 성능 최적화

---

## 💡 추가 고려 사항

### 1. AI API 비용 최적화
- 프롬프트 최적화로 토큰 수 감소
- 캐싱 전략 강화
- 배치 처리 고려

### 2. 응답 시간 개선
- 비동기 처리 최적화
- 부분 결과 스트리밍 (선택사항)
- 병렬 분석 수행

### 3. 확장성
- 모듈화된 구조로 기능 추가 용이
- 플러그인 방식의 분석 모듈
- 설정 기반 기능 활성화/비활성화

---

## 📝 결론

이 제안서는 현재 서비스를 정성적 분석과 다양한 데이터 추천 기능을 갖춘 종합적인 분석 플랫폼으로 고도화하는 로드맵을 제시합니다. AI API를 적극 활용하여 사용자에게 보다 넓은 시각의 정보와 실행 가능한 인사이트를 제공할 수 있도록 합니다.

단계적 구현을 통해 점진적으로 기능을 추가하고, 사용자 피드백을 반영하여 지속적으로 개선해 나갈 수 있습니다.
