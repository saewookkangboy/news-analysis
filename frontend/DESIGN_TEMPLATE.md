# 최종 디자인 템플릿 가이드

## 디자인 컨셉
**블랙/화이트 미니멀 테마** - 깔끔하고 전문적인 단색 디자인

## 레이아웃 구조

### 전체 구조
```
┌─────────────────────────────────────┐
│         네비게이션 바                │
├──────────┬──────────────────────────┤
│          │                          │
│  분석    │      분석 결과            │
│  설정    │                          │
│  패널    │                          │
│          │                          │
└──────────┴──────────────────────────┘
```

### 반응형 브레이크포인트
- **모바일** (< 1024px): 세로 레이아웃 (flex-col)
- **데스크톱** (≥ 1024px): 좌우 분할 레이아웃 (flex-row)

## 색상 팔레트

### 기본 색상
- **배경**: `#ffffff` (화이트)
- **텍스트**: `#000000` (블랙)
- **테두리**: `#000000` (블랙)
- **Hover**: `#333333` (다크 그레이)

### 사용 금지 색상
- 모든 컬러 (그린, 레드, 블루, 옐로우 등) 제거
- 블랙/화이트/그레이만 사용

## 컴포넌트 스타일 가이드

### 1. 네비게이션 바
- 배경: 화이트
- 테두리: 블랙 (하단)
- 활성 메뉴: 블랙 배경, 화이트 텍스트
- 비활성 메뉴: 화이트 배경, 블랙 텍스트
- Hover: 블랙 배경, 화이트 텍스트

### 2. 분석 설정 패널 (좌측)
- 너비: 320px (lg), 384px (xl)
- 배경: 화이트
- 테두리: 블랙 (우측)
- 선택된 카테고리: 블랙 배경, 화이트 텍스트
- 비선택 카테고리: 화이트 배경, 블랙 텍스트, 블랙 테두리

### 3. 분석 결과 패널 (우측)
- 배경: 화이트
- 패딩: 24px (lg), 32px (xl)
- 최대 너비: 1280px (max-w-7xl)

### 4. 카드
- 배경: 화이트
- 테두리: 블랙 (1px)
- 패딩: 20px (p-5) 또는 24px (p-6)
- 모서리: 둥근 모서리 (rounded-lg)

### 5. 버튼
- Primary: 블랙 배경, 화이트 텍스트
- Secondary: 화이트 배경, 블랙 텍스트, 블랙 테두리
- Hover: 반전 효과 또는 다크 그레이

### 6. 테이블
- 헤더: 화이트 배경, 블랙 텍스트
- 셀: 화이트 배경, 블랙 텍스트
- 테두리: 블랙 (하단)

### 7. 스크롤바
- 트랙: 화이트
- 썸: 블랙
- Hover: 다크 그레이 (#333333)

## 타이포그래피

### 폰트
- 기본: 'Inter', 시스템 폰트
- 코드: 'Courier New', monospace

### 크기
- 헤딩 1: `text-2xl` (24px)
- 헤딩 2: `text-lg` (18px)
- 헤딩 3: `text-base` (16px)
- 본문: `text-sm` (14px)
- 작은 텍스트: `text-xs` (12px)

### 굵기
- Bold: `font-bold` (700)
- Semibold: `font-semibold` (600)
- Medium: `font-medium` (500)
- Regular: 기본 (400)

## 간격 시스템

### 패딩/마진
- xs: 4px (1)
- sm: 8px (2)
- md: 16px (4)
- lg: 24px (6)
- xl: 32px (8)

### 그리드 간격
- 기본: 24px (gap-6)
- 작은 간격: 8px (gap-2)
- 큰 간격: 32px (gap-8)

## 애니메이션

### 전환 효과
- 기본: `transition-colors duration-200`
- 전체: `transition-all duration-200`

### 애니메이션
- Fade In: 0.3s ease-in-out
- Slide Up: 0.3s ease-out

## 반응형 디자인

### 브레이크포인트
- sm: 640px
- md: 768px
- lg: 1024px
- xl: 1280px

### 주요 반응형 클래스
- `flex-col lg:flex-row`: 모바일 세로, 데스크톱 가로
- `w-full lg:w-80`: 모바일 전체, 데스크톱 고정 너비
- `grid-cols-1 md:grid-cols-2 lg:grid-cols-4`: 반응형 그리드

## 사용 예시

### 카드 컴포넌트
```tsx
<div className="bg-white rounded-lg border border-black p-6">
  <h3 className="text-lg font-semibold text-black mb-4">제목</h3>
  <p className="text-sm text-black">내용</p>
</div>
```

### 버튼 컴포넌트
```tsx
<button className="bg-black text-white border border-black px-4 py-2 rounded-lg hover:bg-gray-900 transition-colors duration-200">
  버튼
</button>
```

### 선택된 상태
```tsx
<button className={`border transition-all duration-200 ${
  isSelected
    ? 'border-black bg-black text-white'
    : 'border-black bg-white text-black hover:bg-black hover:text-white'
}`}>
  옵션
</button>
```

## 파일 구조

```
frontend/src/
├── index.css          # 전역 스타일 및 디자인 시스템
├── App.css            # App 컴포넌트 스타일
├── App.tsx            # 메인 앱 컴포넌트
└── components/
    ├── Dashboard.tsx          # 대시보드 (좌우 분할 레이아웃)
    ├── AnalysisSettings.tsx   # 분석 설정 패널 (좌측)
    └── Navigation.tsx          # 네비게이션 바
```

## 체크리스트

- [x] 블랙/화이트 색상 팔레트 적용
- [x] 좌우 분할 레이아웃 구현
- [x] 반응형 디자인 적용
- [x] 모든 컴포넌트 스타일 통일
- [x] 미니멀한 디자인 유지
- [x] 애니메이션 및 전환 효과 적용
- [x] 스크롤바 커스터마이징
- [x] 일관된 타이포그래피
