# 한글 폰트 가이드

## 적용된 폰트

### 1. IBM Plex Sans KR
- **용도**: 기본 한글 폰트 (우선 적용)
- **가중치**: 100, 200, 300, 400, 500, 600, 700
- **특징**: 모던하고 깔끔한 한글 폰트

### 2. Noto Sans KR
- **용도**: 대체 한글 폰트
- **가중치**: 100-900 (가변 폰트)
- **특징**: Google의 한글 폰트, 광범위한 가중치 지원

### 3. IBM Plex Sans
- **용도**: 영문/숫자 폰트
- **특징**: IBM Plex Sans KR과 조화

### 4. Nanum Gothic
- **용도**: 추가 한글 폰트 옵션
- **특징**: 가독성 좋은 한글 폰트

## 기본 폰트 스택

```css
font-family: 'IBM Plex Sans KR', 'Noto Sans KR', 'Inter', 
             -apple-system, BlinkMacSystemFont, 'Segoe UI', 
             'Roboto', sans-serif;
```

## 사용 방법

### CSS 클래스 사용

#### IBM Plex Sans KR
```html
<div class="ibm-plex-sans-kr-regular">일반 텍스트</div>
<div class="ibm-plex-sans-kr-medium">중간 굵기</div>
<div class="ibm-plex-sans-kr-semibold">세미볼드</div>
<div class="ibm-plex-sans-kr-bold">볼드</div>
```

#### Noto Sans KR
```html
<div class="noto-sans-kr-regular">일반 텍스트</div>
<div class="noto-sans-kr-medium">중간 굵기</div>
<div class="noto-sans-kr-bold">볼드</div>
```

### 인라인 스타일 사용

```tsx
<div style={{ fontFamily: "'IBM Plex Sans KR', sans-serif", fontWeight: 500 }}>
  한글 텍스트
</div>
```

### Tailwind CSS 사용

```tsx
<div className="font-sans">
  {/* 기본 폰트 스택 자동 적용 */}
</div>
```

## 폰트 가중치 매핑

| 클래스 | Font Weight | 용도 |
|--------|-------------|------|
| thin | 100 | 매우 얇은 텍스트 |
| extralight | 200 | 매우 가벼운 텍스트 |
| light | 300 | 가벼운 텍스트 |
| regular | 400 | 일반 텍스트 (기본) |
| medium | 500 | 중간 굵기 |
| semibold | 600 | 세미볼드 |
| bold | 700 | 볼드 |
| extrabold | 800 | 매우 굵은 텍스트 (Noto만) |
| black | 900 | 가장 굵은 텍스트 (Noto만) |

## 성능 최적화

### Preconnect 링크
HTML `<head>`에 다음 링크가 포함되어 있습니다:

```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
```

이 링크들은 폰트 로딩 속도를 향상시킵니다.

### 폰트 로딩 전략
- `display=swap`: 폰트가 로드되는 동안 시스템 폰트 표시
- CSS `@import` 사용: 자동으로 최적화된 로딩

## 컴포넌트별 권장 폰트

### 네비게이션
- **IBM Plex Sans KR Medium** (500)
- 깔끔하고 읽기 쉬운 메뉴

### 헤딩
- **IBM Plex Sans KR Semibold** (600) 또는 **Bold** (700)
- 강조가 필요한 제목

### 본문
- **IBM Plex Sans KR Regular** (400)
- 일반적인 텍스트 콘텐츠

### 버튼
- **IBM Plex Sans KR Medium** (500)
- 적절한 가시성

### 작은 텍스트
- **IBM Plex Sans KR Regular** (400) 또는 **Light** (300)
- 캡션, 설명 텍스트

## 예시 코드

### React 컴포넌트
```tsx
import React from 'react';

const KoreanText: React.FC = () => {
  return (
    <div className="ibm-plex-sans-kr-regular">
      <h1 className="ibm-plex-sans-kr-bold text-2xl">
        제목 텍스트
      </h1>
      <p className="ibm-plex-sans-kr-regular text-sm">
        본문 텍스트입니다. 한글이 깔끔하게 표시됩니다.
      </p>
      <button className="ibm-plex-sans-kr-medium">
        버튼 텍스트
      </button>
    </div>
  );
};
```

## 폰트 파일 위치

폰트는 Google Fonts에서 CDN으로 제공되며, 자동으로 최적화된 버전이 로드됩니다.

## 참고사항

- 모든 한글 텍스트는 자동으로 IBM Plex Sans KR 또는 Noto Sans KR이 적용됩니다.
- 영문/숫자는 IBM Plex Sans가 우선 적용됩니다.
- 폰트가 로드되지 않으면 시스템 폰트로 대체됩니다.
