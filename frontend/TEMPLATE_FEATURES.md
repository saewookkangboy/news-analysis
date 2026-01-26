# Marketing Website Template 반영 사항

## 참고 템플릿
[basehub-ai/marketing-website-template](https://github.com/basehub-ai/marketing-website-template)

## 적용된 주요 기능

### 1. 타이포그래피 시스템
- ✅ 음수 letter-spacing 적용
- ✅ 최적화된 line-height
- ✅ tracking-tight 클래스 지원
- ✅ 폰트 크기별 letter-spacing 최적화

### 2. 고급 애니메이션
- ✅ enterFromRight/Left 애니메이션
- ✅ scaleIn/Out (3D 효과 포함)
- ✅ cubic-bezier 이징 함수
- ✅ fadeIn/Out 애니메이션

### 3. 인터랙션 효과
- ✅ Hover 시 transform: translateY 적용
- ✅ 선택된 항목 scale-105 효과
- ✅ 부드러운 전환 효과

### 4. 네비게이션 개선
- ✅ Sticky 네비게이션
- ✅ Backdrop blur 효과
- ✅ 개선된 간격 및 크기
- ✅ 스케일 애니메이션

### 5. 컴포넌트 스타일
- ✅ 카드 hover 효과
- ✅ 버튼 hover 효과
- ✅ 폼 입력 focus 효과
- ✅ 그림자 효과 (선택적)

## 차이점

### 유지된 요소
- 블랙/화이트 미니멀 테마 유지
- 좌우 분할 레이아웃 구조 유지
- 기존 컴포넌트 구조 유지

### 개선된 요소
- 타이포그래피 시스템
- 애니메이션 품질
- 인터랙션 효과
- 시각적 피드백

## 사용 예시

### 타이포그래피
```tsx
<h1 style={{ letterSpacing: '-1.04px' }}>제목</h1>
<p style={{ letterSpacing: '-0.42px' }}>본문</p>
```

### 애니메이션
```tsx
<div className="animate-fade-in">페이드 인</div>
<div className="enter-from-right">오른쪽에서 진입</div>
<div className="scale-in">스케일 인</div>
```

### 인터랙션
```tsx
<button className="hover:translate-y-[-1px] transition-all">
  버튼
</button>
```

## 성능 최적화
- CSS 애니메이션 사용 (GPU 가속)
- transform 속성 활용 (reflow 최소화)
- 적절한 duration 설정 (200-300ms)
