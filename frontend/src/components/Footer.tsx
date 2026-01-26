import React from 'react';

const Footer: React.FC = () => {
  const relatedSites = [
    { name: 'TROE', url: 'https://troe.kr/' },
    { name: '잉크닷', url: 'https://inkdot.kr/' },
    { name: '프롬프트 메이커', url: 'https://prompt.allrounder.im/' },
  ];

  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-white border-t border-black flex-shrink-0">
      <div className="px-6 py-6">
        <div className="max-w-7xl mx-auto">
          {/* 연관 사이트 섹션 */}
          <div className="mb-4">
            <div className="flex flex-wrap items-center justify-center gap-4">
              <span className="text-sm text-black ibm-plex-sans-kr-medium" style={{ letterSpacing: '-0.42px' }}>
                연관 사이트:
              </span>
              {relatedSites.map((site, index) => (
                <React.Fragment key={site.url}>
                  <a
                    href={site.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-black hover:text-gray-600 transition-colors duration-200 ibm-plex-sans-kr-medium underline"
                    style={{ letterSpacing: '-0.42px' }}
                  >
                    {site.name}
                  </a>
                  {index < relatedSites.length - 1 && (
                    <span className="text-black">|</span>
                  )}
                </React.Fragment>
              ))}
            </div>
          </div>

          {/* 저작권 및 정보 섹션 */}
          <div className="text-center">
            <p className="text-xs text-black ibm-plex-sans-kr-regular" style={{ letterSpacing: '-0.36px' }}>
              © {currentYear} News Trend Analyzer. All rights reserved.
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
