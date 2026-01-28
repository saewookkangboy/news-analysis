import React from 'react';

const Footer: React.FC = () => {
  const relatedSites = [
    { name: 'TROE', url: 'https://troe.kr/' },
    { name: '잉크닷', url: 'https://inkdot.kr/' },
    { name: '프롬프트 메이커', url: 'https://prompt.allrounder.im/' },
  ];

  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-white border-t border-gray-200 flex-shrink-0">
      <div className="px-4 sm:px-6 py-6">
        <div className="max-w-7xl mx-auto">
          {/* 연관 사이트 섹션 - Flat Design */}
          <div className="mb-4">
            <div className="flex flex-wrap items-center justify-center gap-4">
              <span className="flat-caption">
                연관 사이트:
              </span>
              {relatedSites.map((site, index) => (
                <React.Fragment key={site.url}>
                  <a
                    href={site.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flat-caption text-blue-600 hover:text-blue-700 transition-colors duration-200 underline"
                  >
                    {site.name}
                  </a>
                  {index < relatedSites.length - 1 && (
                    <span className="flat-caption text-gray-400">|</span>
                  )}
                </React.Fragment>
              ))}
            </div>
          </div>

          {/* 저작권 및 정보 섹션 - Flat Design */}
          <div className="text-center">
            <p className="flat-caption text-gray-600">
              © {currentYear} News Trend Analyzer. All rights reserved.
            </p>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
