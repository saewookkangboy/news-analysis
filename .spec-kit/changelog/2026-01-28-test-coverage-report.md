# 테스트 커버리지 리포트

**작성일**: 2026-01-28  
**테스트 실행**: pytest with pytest-cov

---

## 📊 전체 커버리지

- **전체 커버리지**: 26%
- **총 라인 수**: 2,481
- **커버된 라인**: 642
- **미커버 라인**: 1,839

---

## 📈 파일별 커버리지

### 높은 커버리지 (70% 이상) ✅
- `backend/utils/security.py`: **98%** ⭐
- `backend/config.py`: **84%**
- `backend/api/dashboard_routes.py`: **77%**
- `backend/services/progress_tracker.py`: **74%**

### 중간 커버리지 (40-70%)
- `backend/utils/error_handler.py`: **61%**
- `backend/main.py`: **56%**
- `backend/api/metrics.py`: **43%**
- `backend/api/monitoring.py`: **45%**

### 낮은 커버리지 (40% 미만) ⚠️
- `backend/api/routes.py`: **35%**
- `backend/middleware/cache_middleware.py`: **32%**
- `backend/utils/monitoring.py`: **22%**
- `backend/services/keyword_recommender.py`: **19%**
- `backend/services/sentiment_analyzer.py`: **17%**
- `backend/utils/result_normalizer.py`: **14%**
- `backend/utils/gemini_utils.py`: **12%**
- `backend/services/target_analyzer.py`: **8%** ⚠️
- `backend/utils/token_optimizer.py`: **8%**
- `backend/utils/json_repair.py`: **0%** ⚠️

---

## 🎯 우선순위별 개선 계획

### High Priority (즉시 개선)
1. **target_analyzer.py (8%)**
   - 핵심 비즈니스 로직
   - AI API 호출 테스트 추가 필요
   - Mock을 사용한 단위 테스트 작성

2. **routes.py (35%)**
   - API 엔드포인트 통합 테스트 확장
   - 성공 케이스 및 에러 케이스 추가

3. **json_repair.py (0%)**
   - 유틸리티 함수 테스트 추가
   - JSON 파싱 엣지 케이스 테스트

### Medium Priority (단기 개선)
4. **sentiment_analyzer.py (17%)**
   - 감정 분석 로직 테스트
   - 다양한 입력 케이스 테스트

5. **token_optimizer.py (8%)**
   - 토큰 최적화 로직 테스트
   - 경계값 테스트

6. **gemini_utils.py (12%)**
   - Gemini API 유틸리티 테스트
   - Fallback 로직 테스트

### Low Priority (중기 개선)
7. **cache_middleware.py (32%)**
   - 캐시 동작 테스트
   - TTL 테스트

8. **monitoring.py (22%)**
   - 메트릭 수집 테스트
   - 성능 측정 테스트

---

## 📝 커버리지 목표

### 단기 목표 (1주)
- 전체 커버리지: **40%**
- 핵심 모듈 (security, error_handler, routes): **70% 이상**

### 중기 목표 (1개월)
- 전체 커버리지: **60%**
- 모든 유틸리티 모듈: **80% 이상**
- 서비스 모듈: **50% 이상**

### 장기 목표 (3개월)
- 전체 커버리지: **80%**
- 모든 모듈: **70% 이상**
- 핵심 비즈니스 로직: **90% 이상**

---

## 🔧 개선 방안

### 1. Mock 기반 테스트 추가
```python
# target_analyzer.py 테스트 예시
@patch('backend.services.target_analyzer.get_api_key_safely')
@patch('backend.services.target_analyzer._analyze_with_openai')
async def test_analyze_target_with_openai(mock_openai, mock_key):
    mock_key.return_value = "sk-test123..."
    mock_openai.return_value = {"result": "test"}
    # 테스트 로직
```

### 2. 통합 테스트 확장
- 실제 API 호출 시뮬레이션
- 다양한 입력 케이스 테스트
- 에러 시나리오 테스트

### 3. 유틸리티 함수 테스트
- 순수 함수 테스트 (의존성 없음)
- 경계값 테스트
- 엣지 케이스 테스트

---

## 📋 다음 작업

### 즉시 작업
- [ ] `target_analyzer.py` Mock 테스트 작성
- [ ] `json_repair.py` 유틸리티 테스트 작성
- [ ] `routes.py` 통합 테스트 확장

### 단기 작업
- [ ] `sentiment_analyzer.py` 테스트 추가
- [ ] `token_optimizer.py` 테스트 추가
- [ ] `gemini_utils.py` 테스트 추가

### 중기 작업
- [ ] 커버리지 목표 달성 (40% → 60%)
- [ ] CI/CD에 커버리지 체크 추가
- [ ] 커버리지 리포트 자동 생성

---

## 📊 커버리지 리포트

HTML 리포트가 생성되었습니다:
- **위치**: `htmlcov/index.html`
- **열기**: 브라우저에서 `htmlcov/index.html` 파일 열기

---

**리포트 생성일**: 2026-01-28  
**다음 리뷰**: 커버리지 40% 달성 후
