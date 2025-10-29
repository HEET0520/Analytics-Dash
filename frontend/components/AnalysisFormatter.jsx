// frontend/components/AnalysisFormatter.jsx
"use client";
import React from 'react';

const AnalysisFormatter = ({ analysisText }) => {
  if (!analysisText) return null;

  const parseAnalysis = (text) => {
    const sections = [];
    const lines = text.split('\n').filter(line => line.trim());
    
    let currentSection = null;
    let currentSubsection = null;
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim();
      
      // Main section headers (### What are...)
      if (line.startsWith('### ')) {
        if (currentSection) sections.push(currentSection);
        currentSection = {
          title: line.replace('### ', ''),
          subsections: [],
          content: []
        };
        currentSubsection = null;
      }
      // Subsection headers (* **Title:**)
      else if (line.startsWith('*   **') && line.includes(':**')) {
        if (currentSection) {
          currentSubsection = {
            title: line.replace('*   **', '').replace(':**', ''),
            items: []
          };
          currentSection.subsections.push(currentSubsection);
        }
      }
      // List items (*   **Bold text:** or *   Regular text)
      else if (line.startsWith('*   ')) {
        const content = line.replace('*   ', '');
        if (currentSubsection) {
          currentSubsection.items.push(content);
        } else if (currentSection) {
          currentSection.content.push(content);
        }
      }
      // Regular content
      else if (line && currentSection) {
        if (currentSubsection) {
          currentSubsection.items.push(line);
        } else {
          currentSection.content.push(line);
        }
      }
    }
    
    if (currentSection) sections.push(currentSection);
    return sections;
  };

  const formatMetric = (text) => {
    // Highlight percentages, amounts, and key metrics
    return text
      .replace(/\*\*([^*]+)\*\*/g, '<strong class="text-slate-900 dark:text-slate-100 font-semibold">$1</strong>')
      .replace(/(\d+\.?\d*%)/g, '<span class="text-emerald-600 dark:text-emerald-400 font-semibold">$1</span>')
      .replace(/(₹[\d,]+ Crore?)/g, '<span class="text-blue-600 dark:text-blue-400 font-semibold">$1</span>')
      .replace(/(\d+ bps)/g, '<span class="text-purple-600 dark:text-purple-400 font-semibold">$1</span>')
      .replace(/(₹[\d,]+)/g, '<span class="text-blue-600 dark:text-blue-400 font-semibold">$1</span>');
  };

  const sections = parseAnalysis(analysisText);

  return (
    <div className="space-y-6">
      {sections.map((section, sectionIndex) => (
        <div key={sectionIndex} className="bg-white dark:bg-slate-800 rounded-lg p-6 border border-slate-200 dark:border-slate-700">
          <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100 mb-4 flex items-center gap-2">
            <div className="w-2 h-2 bg-gradient-to-r from-brandStart to-brandEnd rounded-full"></div>
            {section.title}
          </h3>
          
          {section.subsections.map((subsection, subIndex) => (
            <div key={subIndex} className="mb-6 last:mb-0">
              <h4 className="text-md font-medium text-slate-800 dark:text-slate-200 mb-3 flex items-center gap-2">
                <svg className="h-4 w-4 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
                {subsection.title}
              </h4>
              <div className="ml-6 space-y-2">
                {subsection.items.map((item, itemIndex) => (
                  <div key={itemIndex} className="flex items-start gap-3">
                    <div className="w-1.5 h-1.5 bg-slate-400 dark:bg-slate-500 rounded-full mt-2 flex-shrink-0"></div>
                    <div 
                      className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed"
                      dangerouslySetInnerHTML={{ __html: formatMetric(item) }}
                    />
                  </div>
                ))}
              </div>
            </div>
          ))}
          
          {section.content.length > 0 && (
            <div className="space-y-2">
              {section.content.map((content, contentIndex) => (
                <div key={contentIndex} className="text-sm text-slate-700 dark:text-slate-300 leading-relaxed">
                  <span dangerouslySetInnerHTML={{ __html: formatMetric(content) }} />
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default AnalysisFormatter;
