"""
API 라우트 통합 테스트
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


class TestHealthCheck:
    """헬스 체크 엔드포인트 테스트"""
    
    def test_health_check(self):
        """헬스 체크 응답 확인"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"


class TestTargetAnalyze:
    """타겟 분석 엔드포인트 테스트"""
    
    def test_analyze_target_invalid_type(self):
        """잘못된 타겟 타입 검증"""
        response = client.post(
            "/api/target/analyze",
            json={
                "target_keyword": "test",
                "target_type": "invalid_type"
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "error" in data or "detail" in data
    
    def test_analyze_target_missing_keyword(self):
        """키워드 누락 검증"""
        response = client.post(
            "/api/target/analyze",
            json={
                "target_type": "keyword"
            }
        )
        assert response.status_code == 422  # Validation error
    
    def test_analyze_target_invalid_date_format(self):
        """잘못된 날짜 형식 검증"""
        response = client.post(
            "/api/target/analyze",
            json={
                "target_keyword": "test",
                "target_type": "keyword",
                "start_date": "2025-13-01"  # 잘못된 월
            }
        )
        assert response.status_code == 400
        data = response.json()
        assert "error" in data or "detail" in data
    
    def test_analyze_target_valid_request(self, no_api_keys):
        """유효한 요청 (API 키 없이 기본 분석 모드)"""
        response = client.post(
            "/api/target/analyze",
            json={
                "target_keyword": "테스트 키워드",
                "target_type": "keyword"
            }
        )
        # API 키가 없어도 기본 분석 모드로 응답
        assert response.status_code == 200
        data = response.json()
        assert "success" in data or "target_keyword" in data
    
    def test_analyze_target_audience_type(self, no_api_keys):
        """오디언스 타입 분석"""
        response = client.post(
            "/api/target/analyze",
            json={
                "target_keyword": "테스트",
                "target_type": "audience"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "target_type" in data or "success" in data
    
    def test_analyze_target_comprehensive_type(self, no_api_keys):
        """종합 분석 타입"""
        response = client.post(
            "/api/target/analyze",
            json={
                "target_keyword": "테스트",
                "target_type": "comprehensive"
            }
        )
        assert response.status_code == 200
    
    def test_analyze_target_with_dates(self, no_api_keys):
        """날짜 범위 포함 분석"""
        response = client.post(
            "/api/target/analyze",
            json={
                "target_keyword": "테스트",
                "target_type": "keyword",
                "start_date": "2025-01-01",
                "end_date": "2025-01-31"
            }
        )
        assert response.status_code == 200
    
    def test_analyze_target_with_context(self, no_api_keys):
        """추가 컨텍스트 포함 분석"""
        response = client.post(
            "/api/target/analyze",
            json={
                "target_keyword": "테스트",
                "target_type": "keyword",
                "additional_context": "추가 정보"
            }
        )
        assert response.status_code == 200


class TestDashboardRoutes:
    """대시보드 라우트 테스트"""
    
    def test_dashboard_overview(self):
        """대시보드 개요 조회"""
        response = client.get("/api/dashboard/overview?category=all")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert data["success"] is True
        assert "data" in data
    
    def test_dashboard_funnels(self):
        """퍼널 데이터 조회"""
        response = client.get("/api/dashboard/funnels?category=all")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "data" in data
        assert isinstance(data["data"], list)
    
    def test_dashboard_kpi_trends(self):
        """KPI 트렌드 조회"""
        response = client.get("/api/dashboard/kpi-trends?category=all")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "data" in data
    
    def test_dashboard_recent_events(self):
        """최근 이벤트 조회"""
        response = client.get("/api/dashboard/recent-events?category=all&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "data" in data
    
    def test_dashboard_category_metrics(self):
        """카테고리별 메트릭 조회"""
        response = client.get("/api/dashboard/category-metrics?category=ecommerce")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "data" in data


class TestCORS:
    """CORS 설정 테스트"""
    
    def test_cors_headers(self):
        """CORS 헤더 확인"""
        response = client.options("/api/target/analyze")
        # OPTIONS 요청은 200 또는 204를 반환해야 함
        assert response.status_code in [200, 204, 405]  # 405는 메서드 허용 안됨
