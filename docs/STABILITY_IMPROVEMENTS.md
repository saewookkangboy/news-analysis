# 서비스 안정화 및 기능 고도화 개선 사항

**작성일**: 2026-01-28

## 1. 개선 요약

전체 데이터·코드 검토 후 다음 항목을 반영했습니다.

- **백엔드**: Dashboard 스텁 API 추가, 타입 호환성 정리
- **프론트엔드**: 누락 컴포넌트 추가, API 스펙 정합성, 에러 핸들링 강화
- **공통**: `target_type` 스펙 통일, ErrorBoundary 개선

---

## 2. 백엔드 변경

### 2.1 Dashboard API 스텁 (`/api/dashboard/*`)

- **파일**: `backend/api/dashboard_routes.py` (신규)
- **내용**: Dashboard UI 연동용 목 데이터 API
- **엔드포인트**:
  - `GET /api/dashboard/overview?category=`
  - `GET /api/dashboard/funnels?category=`
  - `GET /api/dashboard/kpi-trends?category=`
  - `GET /api/dashboard/recent-events?category=`
  - `GET /api/dashboard/scenario-performance?category=`
  - `GET /api/dashboard/category-metrics?category=`
- **카테고리**: `all` | `ecommerce` | `lead_generation` | `general_website`
- **참고**: 추후 실제 이벤트/분석 연동 시 이 스텁을 교체하면 됩니다.

### 2.2 라우터 등록

- `backend/main.py`에 `dashboard_router` 등록
- prefix: `/api/dashboard`, tags: `["dashboard"]`

### 2.3 Python 3.8 호환

- `dashboard_routes.py`에서 `dict[...]`, `list[...]` 대신 `typing.Dict`, `typing.List` 사용

---

## 3. 프론트엔드 변경

### 3.1 Dashboard 연동

- **`dashboardService.ts`**
  - `DashboardOverview`에  
    `total_sessions`, `total_conversions`, `average_conversion_rate`,  
    `total_revenue`, `average_order_value`, `total_leads`,  
    `lead_conversion_rate`, `total_page_views`, `unique_visitors` 추가
- **`Dashboard.tsx`**
  - overview 접근 시 `??`로 기본값 처리 (undefined 방지)
  - fetch 실패 시 overview fallback에  
    `total_sessions`, `total_conversions`, `average_conversion_rate` 포함

### 3.2 누락 컴포넌트 추가

다음 컴포넌트를 새로 추가하여 Dashboard 로딩 시 오류가 나지 않도록 했습니다.

| 컴포넌트 | 역할 |
|----------|------|
| `MetricCard` | 메트릭 표시 카드 |
| `LoadingSpinner` | 로딩 UI |
| `ErrorMessage` | 에러 메시지 + 재시도 버튼 |
| `FunnelChart` | 퍼널 시각화 |
| `KPITrendChart` | KPI 트렌드 |
| `ScenarioComparisonChart` | 시나리오 비교 |
| `RecentEventsTable` | 최근 이벤트 테이블 |
| `AdminPanel` | 관리자 패널 (스텁) |
| `CategorySelector` | 카테고리 선택 (스텁, 현재 미사용) |
| `CategoryMetrics` | 카테고리별 메트릭 |

### 3.3 분석 API 스펙 통일

- **`analysisService.ts`**
  - `AnalysisRequest.target_type`:  
    `'competitor'` 제거, `'keyword' | 'audience' | 'comprehensive'`로 통일
  - 백엔드 `target_type` 검증 값과 일치

### 3.4 ErrorBoundary 개선

- **`ErrorBoundary.tsx`**
  - 캐치한 에러 메시지 노출
  - **다시 시도**: state 초기화 후 자식 리렌더
  - **새로고침**: `window.location.reload()`

---

## 4. 안정성·동작 확인

- Dashboard 스텁 API `GET /api/dashboard/overview`, `GET /api/dashboard/funnels` 등 호출 검증
- `DashboardOverview` 확장 필드 및 fallback으로 인한 `undefined` 접근 방지
- `target_type` 값을 백엔드와 맞춰 분석 요청 시 400 방지
- ErrorBoundary로 런타임 에러 시 메시지 + 복구 액션 제공

---

## 5. 추천 후속 작업

- [ ] Dashboard 스텁을 실제 이벤트/분석 데이터 소스로 교체
- [ ] API 호출 재시도(retry) 및 타임아웃 정책 정리
- [ ] 프론트엔드 빌드 설정 추가 시 `Dashboard` 및 위 컴포넌트 동작 재검증
