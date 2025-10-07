'use client';

import { useState } from 'react';
import axios from 'axios';

// API endpoint for the backend
const API_URL = 'http://localhost:8000/analyze';

// Sample text for demo
const SAMPLE_TEXT = `Content marketing has become essential for modern digital strategies. Quality content helps improve search engine rankings and attracts organic traffic to your website. SEO best practices include thorough keyword research, on-page optimization, and creating engaging content that provides real value to readers. Regular content updates and proper formatting with headings and paragraphs improve readability and user experience. Link building and social media promotion also contribute to better online visibility and brand awareness.`;

// Interface for API response
interface SerpPreview {
  meta_title: string;
  meta_description: string;
  url_slug: string;
  ctr_score: number;
  title_length: number;
  description_length: number;
  title_issues: string[];
  description_issues: string[];
}

interface AnalysisResult {
  readability: number;
  top_keywords: [string, number][];
  keyword_density: Record<string, number>;
  plagiarism_score: number;
  final_score: number;
  suggestions: string[];  // AI-powered improvement suggestions
  serp_preview: SerpPreview;  // Google SERP preview and CTR prediction
}

// ResultCard component - displays individual metric
interface ResultCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  color?: string;
  icon?: string;
}

function ResultCard({ title, value, subtitle, color = 'blue', icon }: ResultCardProps) {
  const colorClasses = {
    blue: 'bg-blue-50 border-blue-200 text-blue-900',
    green: 'bg-green-50 border-green-200 text-green-900',
    orange: 'bg-orange-50 border-orange-200 text-orange-900',
    purple: 'bg-purple-50 border-purple-200 text-purple-900',
  };

  return (
    <div className={`rounded-lg border-2 p-6 ${colorClasses[color as keyof typeof colorClasses] || colorClasses.blue}`}>
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-sm font-semibold uppercase tracking-wide opacity-75">{title}</h3>
        {icon && <span className="text-2xl">{icon}</span>}
      </div>
      <div className="text-3xl font-bold mb-1">{value}</div>
      {subtitle && <p className="text-sm opacity-75">{subtitle}</p>}
    </div>
  );
}

// Main page component
export default function Home() {
  const [text, setText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);

  // Copy SERP snippet to clipboard
  const copySerpSnippet = () => {
    if (!result?.serp_preview) return;
    
    const snippet = `${result.serp_preview.meta_title}\n${result.serp_preview.meta_description}\nwww.example.com/${result.serp_preview.url_slug}`;
    
    navigator.clipboard.writeText(snippet).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  // Highlight keywords in text
  const highlightKeywords = (text: string, keywords: [string, number][]) => {
    if (!keywords || keywords.length === 0) return text;
    
    let highlightedText = text;
    const topKeywords = keywords.slice(0, 3).map(([word]) => word);
    
    topKeywords.forEach((keyword) => {
      const regex = new RegExp(`\\b(${keyword})\\b`, 'gi');
      highlightedText = highlightedText.replace(regex, '<mark class="bg-yellow-200 px-1 rounded">$1</mark>');
    });
    
    return highlightedText;
  };

  // Handle analysis
  const handleAnalyze = async () => {
    if (!text.trim()) {
      setError('Please enter some text to analyze');
      return;
    }

    if (text.length < 10) {
      setError('Text must be at least 10 characters long');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      console.log('Sending request to:', API_URL);
      console.log('Text length:', text.length);

      const response = await axios.post(API_URL, { text });
      
      console.log('Response received:', response.data);
      setResult(response.data);
    } catch (err: any) {
      console.error('Error during analysis:', err);
      
      if (err.code === 'ERR_NETWORK') {
        setError('Unable to connect to the backend. Make sure the API server is running on http://localhost:8000');
      } else if (err.response) {
        setError(err.response.data?.detail || 'An error occurred during analysis');
      } else {
        setError('An unexpected error occurred');
      }
    } finally {
      setLoading(false);
    }
  };

  // Load sample text
  const handleLoadSample = () => {
    setText(SAMPLE_TEXT);
    setError('');
    setResult(null);
  };

  // Get score color based on value
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-blue-600';
    if (score >= 40) return 'text-orange-600';
    return 'text-red-600';
  };

  // Get readability interpretation
  const getReadabilityText = (score: number) => {
    if (score >= 90) return 'Very Easy';
    if (score >= 80) return 'Easy';
    if (score >= 70) return 'Fairly Easy';
    if (score >= 60) return 'Standard';
    if (score >= 50) return 'Fairly Difficult';
    if (score >= 30) return 'Difficult';
    return 'Very Difficult';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                ✨ Writesonic SEO Analyzer
              </h1>
              <p className="mt-1 text-sm text-gray-600">
                Analyze your content for readability, keywords, and SEO optimization
              </p>
            </div>
            <div className="hidden sm:block">
              <div className="flex items-center space-x-2 text-sm">
                <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                  🟢 API Connected
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Input Section */}
          <div className="space-y-4">
            <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-900">
                  📝 Input Text
                </h2>
                <button
                  onClick={handleLoadSample}
                  className="text-sm px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg transition-colors duration-200 font-medium"
                >
                  Load Sample
                </button>
              </div>

              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Paste your article or content here for SEO analysis..."
                className="w-full h-96 p-4 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none font-mono text-sm bg-white text-gray-900 placeholder-gray-400"
              />

              <div className="mt-4 flex items-center justify-between">
                <span className="text-sm text-gray-500">
                  {text.length} characters
                </span>
                <button
                  onClick={handleAnalyze}
                  disabled={loading || !text.trim()}
                  className="px-8 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
                >
                  {loading ? (
                    <span className="flex items-center">
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Analyzing...
                    </span>
                  ) : (
                    '🚀 Analyze Text'
                  )}
                </button>
              </div>

              {error && (
                <div className="mt-4 p-4 bg-red-50 border-l-4 border-red-500 text-red-700 rounded">
                  <p className="font-medium">⚠️ Error</p>
                  <p className="text-sm mt-1">{error}</p>
                </div>
              )}
            </div>

            {/* Info Card */}
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6 border border-blue-200">
              <h3 className="font-semibold text-gray-900 mb-2">💡 How it works</h3>
              <ul className="text-sm text-gray-700 space-y-1">
                <li>• <strong>Readability:</strong> Flesch Reading Ease score (0-100)</li>
                <li>• <strong>Keywords:</strong> Most frequent meaningful words</li>
                <li>• <strong>Plagiarism:</strong> Similarity check against samples</li>
                <li>• <strong>Final Score:</strong> Overall SEO quality rating</li>
              </ul>
            </div>

            {/* Google SERP Preview - Moved here */}
            {result && result.serp_preview && (
              <div className="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-xl p-4 sm:p-6 border-2 border-indigo-200">
                <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 sm:gap-0 mb-4">
                  <div className="flex items-center">
                    <span className="text-2xl mr-2">🔍</span>
                    <h3 className="text-lg font-semibold text-gray-900">
                      Google SERP Preview
                    </h3>
                  </div>
                  <div className="flex items-center gap-3 flex-wrap">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs sm:text-sm font-semibold text-gray-600">CTR Score:</span>
                      <span className={`px-2 sm:px-3 py-1 rounded-full text-xs sm:text-sm font-bold ${
                        result.serp_preview.ctr_score >= 80 ? 'bg-green-100 text-green-800' :
                        result.serp_preview.ctr_score >= 60 ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {result.serp_preview.ctr_score.toFixed(1)}/100
                      </span>
                    </div>
                    <button
                      onClick={copySerpSnippet}
                      className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs sm:text-sm font-medium rounded-lg transition-colors flex items-center gap-1.5"
                    >
                      {copied ? (
                        <>
                          <span>✓</span>
                          <span>Copied!</span>
                        </>
                      ) : (
                        <>
                          <span>📋</span>
                          <span>Copy Snippet</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>

                {/* Google Search Result Mockup */}
                <div className="bg-white rounded-lg p-4 sm:p-5 shadow-md mb-4 border border-gray-300">
                  <div className="text-xs text-gray-600 mb-1 truncate">
                    www.example.com › {result.serp_preview.url_slug}
                  </div>
                  <div 
                    className="text-lg sm:text-xl text-blue-600 hover:underline cursor-pointer mb-1 font-medium break-words"
                    dangerouslySetInnerHTML={{
                      __html: result.top_keywords 
                        ? highlightKeywords(result.serp_preview.meta_title, result.top_keywords)
                        : result.serp_preview.meta_title
                    }}
                  />
                  <div 
                    className="text-sm text-gray-700 leading-relaxed break-words"
                    dangerouslySetInnerHTML={{
                      __html: result.top_keywords
                        ? highlightKeywords(result.serp_preview.meta_description, result.top_keywords)
                        : result.serp_preview.meta_description
                    }}
                  />
                  <div className="flex items-center flex-wrap gap-x-4 gap-y-1 mt-3 text-xs text-gray-500">
                    <span>Title: {result.serp_preview.title_length} chars</span>
                    <span className="hidden sm:inline">•</span>
                    <span>Description: {result.serp_preview.description_length} chars</span>
                  </div>
                </div>

                {/* Optimization Issues */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Title Issues */}
                  <div className="bg-white rounded-lg p-4 shadow-sm">
                    <h4 className="text-sm font-semibold text-gray-900 mb-2 flex items-center">
                      <span className="mr-2">📝</span>
                      Title Optimization
                    </h4>
                    <div className="space-y-2">
                      {result.serp_preview.title_issues.map((issue, index) => (
                        <div key={index} className="text-xs text-gray-700 flex items-start gap-2">
                          <span className="flex-shrink-0">{issue.startsWith('✅') ? '✅' : issue.startsWith('⚠️') ? '⚠️' : '💡'}</span>
                          <span className="flex-1 break-words">{issue.replace(/^[✅⚠️💡]\s*/, '')}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Description Issues */}
                  <div className="bg-white rounded-lg p-4 shadow-sm">
                    <h4 className="text-sm font-semibold text-gray-900 mb-2 flex items-center">
                      <span className="mr-2">📄</span>
                      Description Optimization
                    </h4>
                    <div className="space-y-2">
                      {result.serp_preview.description_issues.map((issue, index) => (
                        <div key={index} className="text-xs text-gray-700 flex items-start gap-2">
                          <span className="flex-shrink-0">{issue.startsWith('✅') ? '✅' : issue.startsWith('⚠️') ? '⚠️' : '💡'}</span>
                          <span className="flex-1 break-words">{issue.replace(/^[✅⚠️💡]\s*/, '')}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* CTR Explanation */}
                <div className="mt-4 p-3 bg-indigo-100 rounded-lg">
                  <p className="text-xs sm:text-sm text-indigo-900">
                    <strong>CTR Score</strong> predicts how likely users are to click your result in Google search.
                    Higher scores mean better optimization for title length, power words, numbers, and calls-to-action.
                    <span className="block mt-1 text-indigo-700">Keywords highlighted in yellow are your top 3.</span>
                  </p>
                </div>
              </div>
            )}
          </div>

          {/* Results Section */}
          <div className="space-y-4">
            {loading ? (
              <div className="bg-white rounded-xl shadow-lg p-12 border border-gray-200 flex flex-col items-center justify-center">
                <svg className="animate-spin h-12 w-12 text-blue-600 mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <p className="text-lg font-medium text-gray-900">Analyzing your content...</p>
                <p className="text-sm text-gray-500 mt-2">This will only take a moment</p>
              </div>
            ) : result ? (
              <div className="space-y-4">
                {/* Final Score - Hero Card */}
                <div className="bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl shadow-xl p-8 text-white">
                  <h2 className="text-xl font-semibold mb-2 opacity-90">Overall SEO Score</h2>
                  <div className="text-6xl font-bold mb-2">{result.final_score.toFixed(1)}</div>
                  <div className="text-lg opacity-90">out of 100</div>
                  <div className="mt-4 h-3 bg-white bg-opacity-20 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-white rounded-full transition-all duration-500"
                      style={{ width: `${result.final_score}%` }}
                    />
                  </div>
                </div>

                {/* Metrics Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <ResultCard
                    title="Readability"
                    value={result.readability.toFixed(1)}
                    subtitle={getReadabilityText(result.readability)}
                    color="blue"
                    icon="📖"
                  />
                  <ResultCard
                    title="Plagiarism"
                    value={`${result.plagiarism_score.toFixed(1)}%`}
                    subtitle={result.plagiarism_score < 10 ? 'Excellent' : result.plagiarism_score < 30 ? 'Good' : 'Review Needed'}
                    color="green"
                    icon="✅"
                  />
                </div>

                {/* Keywords Card */}
                <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <span className="mr-2">🔑</span>
                    Top Keywords
                  </h3>
                  <div className="space-y-3">
                    {result.top_keywords.slice(0, 5).map(([word, count], index) => (
                      <div key={word} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <span className="text-lg font-bold text-gray-400">#{index + 1}</span>
                          <span className="font-medium text-gray-900">{word}</span>
                        </div>
                        <div className="flex items-center space-x-4">
                          <span className="text-sm text-gray-600">{count} times</span>
                          <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-semibold">
                            {result.keyword_density[word].toFixed(1)}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                  
                  {result.top_keywords.length > 5 && (
                    <div className="mt-4 text-sm text-gray-500 text-center">
                      +{result.top_keywords.length - 5} more keywords
                    </div>
                  )}
                </div>

                {/* Additional Keywords (comma-separated) */}
                <div className="bg-purple-50 rounded-xl p-6 border border-purple-200">
                  <h3 className="text-sm font-semibold text-purple-900 mb-3">All Keywords (Top 10)</h3>
                  <p className="text-purple-800">
                    {result.top_keywords.map(([word]) => word).join(', ')}
                  </p>
                </div>

                {/* AI-Powered Suggestions */}
                {result.suggestions && result.suggestions.length > 0 && (
                  <div className="bg-gradient-to-br from-yellow-50 to-orange-50 rounded-xl p-6 border-2 border-yellow-200">
                    <div className="flex items-center mb-4">
                      <span className="text-2xl mr-2">💡</span>
                      <h3 className="text-lg font-semibold text-gray-900">
                        AI-Powered Improvement Suggestions
                      </h3>
                    </div>
                    <div className="space-y-3">
                      {result.suggestions.map((suggestion, index) => (
                        <div key={index} className="flex items-start p-3 bg-white rounded-lg shadow-sm">
                          <span className="text-yellow-600 font-bold mr-3 mt-0.5">{index + 1}.</span>
                          <p className="text-gray-700 text-sm flex-1">{suggestion}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="bg-white rounded-xl shadow-lg p-12 border border-gray-200 border-dashed flex flex-col items-center justify-center text-center">
                <div className="text-6xl mb-4">📊</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  Ready to Analyze
                </h3>
                <p className="text-gray-500 max-w-md">
                  Enter your content in the text area and click the Analyze button to get comprehensive SEO insights.
                </p>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-12 pb-8 text-center text-sm text-gray-500">
        <p>Powered by Writesonic SEO Analyzer API • Built with Next.js & Tailwind CSS</p>
      </footer>
    </div>
  );
}
