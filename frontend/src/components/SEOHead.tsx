import { useEffect } from 'react';

interface SEOHeadProps {
  title?: string;
  description?: string;
  keywords?: string;
  ogImage?: string;
  canonicalUrl?: string;
}

/**
 * SEO 최적화를 위한 동적 메타 태그 관리 컴포넌트
 * React 앱에서 페이지별 SEO 메타 태그를 동적으로 설정합니다.
 */
export default function SEOHead({
  title = '뉴스 트렌드 분석 서비스 | AI 기반 키워드, 오디언스, 경쟁자 분석',
  description = 'AI 기반 키워드 분석, 오디언스 분석, 경쟁자 분석을 제공하는 뉴스 트렌드 분석 플랫폼. OpenAI GPT-4o-mini와 Google Gemini 2.0 Flash를 활용한 전문적인 마케팅 인사이트를 제공합니다.',
  keywords = '뉴스 트렌드 분석, 키워드 분석, 오디언스 분석, 경쟁자 분석, AI 분석, 마케팅 인사이트, 트렌드 분석, 키워드 리서치, SEO 분석, 마케팅 분석 도구',
  ogImage = 'https://news-trend-analyzer.vercel.app/og-image.png',
  canonicalUrl = 'https://news-trend-analyzer.vercel.app/',
}: SEOHeadProps) {
  useEffect(() => {
    // 기본 메타 태그 업데이트
    document.title = title;
    
    // Description 메타 태그
    let metaDescription = document.querySelector('meta[name="description"]');
    if (!metaDescription) {
      metaDescription = document.createElement('meta');
      metaDescription.setAttribute('name', 'description');
      document.head.appendChild(metaDescription);
    }
    metaDescription.setAttribute('content', description);
    
    // Keywords 메타 태그
    let metaKeywords = document.querySelector('meta[name="keywords"]');
    if (!metaKeywords) {
      metaKeywords = document.createElement('meta');
      metaKeywords.setAttribute('name', 'keywords');
      document.head.appendChild(metaKeywords);
    }
    metaKeywords.setAttribute('content', keywords);
    
    // Open Graph 메타 태그
    const ogTags = {
      'og:title': title,
      'og:description': description,
      'og:image': ogImage,
      'og:url': canonicalUrl,
      'og:type': 'website',
      'og:locale': 'ko_KR',
      'og:site_name': '뉴스 트렌드 분석 서비스',
    };
    
    Object.entries(ogTags).forEach(([property, content]) => {
      let meta = document.querySelector(`meta[property="${property}"]`);
      if (!meta) {
        meta = document.createElement('meta');
        meta.setAttribute('property', property);
        document.head.appendChild(meta);
      }
      meta.setAttribute('content', content);
    });
    
    // Twitter Card 메타 태그
    const twitterTags = {
      'twitter:card': 'summary_large_image',
      'twitter:title': title,
      'twitter:description': description,
      'twitter:image': ogImage,
    };
    
    Object.entries(twitterTags).forEach(([name, content]) => {
      let meta = document.querySelector(`meta[name="${name}"]`);
      if (!meta) {
        meta = document.createElement('meta');
        meta.setAttribute('name', name);
        document.head.appendChild(meta);
      }
      meta.setAttribute('content', content);
    });
    
    // Canonical URL
    let canonical = document.querySelector('link[rel="canonical"]');
    if (!canonical) {
      canonical = document.createElement('link');
      canonical.setAttribute('rel', 'canonical');
      document.head.appendChild(canonical);
    }
    canonical.setAttribute('href', canonicalUrl);
    
    // 구조화된 데이터 (JSON-LD)
    let jsonLd = document.querySelector('script[type="application/ld+json"]');
    if (!jsonLd) {
      jsonLd = document.createElement('script');
      jsonLd.setAttribute('type', 'application/ld+json');
      document.head.appendChild(jsonLd);
    }
    
    const structuredData = {
      '@context': 'https://schema.org',
      '@type': 'WebApplication',
      name: '뉴스 트렌드 분석 서비스',
      alternateName: 'News Trend Analyzer',
      url: canonicalUrl,
      description: description,
      applicationCategory: 'BusinessApplication',
      operatingSystem: 'Web',
      offers: {
        '@type': 'Offer',
        price: '0',
        priceCurrency: 'KRW',
      },
      featureList: [
        '키워드 분석',
        '오디언스 분석',
        '경쟁자 분석',
        'AI 기반 인사이트',
        '트렌드 분석',
      ],
      provider: {
        '@type': 'Organization',
        name: 'News Trend Analyzer',
      },
    };
    
    jsonLd.textContent = JSON.stringify(structuredData);
  }, [title, description, keywords, ogImage, canonicalUrl]);
  
  return null; // 이 컴포넌트는 렌더링하지 않음
}
