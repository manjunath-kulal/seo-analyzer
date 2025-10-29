"""
FastAPI backend for "Writesonic SEO Analyzer" prototype.

This API analyzes text content for SEO metrics including readability,
keyword density, plagiarism detection, and generates an overall score.
"""

import os
from pathlib import Path

# Set environment variables for Vercel serverless (read-only filesystem workaround)
# CRITICAL: Must be set BEFORE importing textstat or any other libraries that might write to home
os.environ['HOME'] = '/tmp'
os.environ['TMPDIR'] = '/tmp'
os.environ['TEMP'] = '/tmp'
os.environ['TMP'] = '/tmp'
BASE_DIR = Path(__file__).resolve().parent
LOCAL_NLTK_DIR = BASE_DIR / 'nltk_data'
TMP_NLTK_DIR = Path('/tmp/nltk_data')

# Respect packaged corpora first, then fallback to /tmp for runtime downloads
local_nltk_path = str(LOCAL_NLTK_DIR) if LOCAL_NLTK_DIR.exists() else ''
tmp_nltk_path = str(TMP_NLTK_DIR)
os.environ['NLTK_DATA'] = os.pathsep.join(
    [path for path in [local_nltk_path, tmp_nltk_path] if path]
)
os.environ['MPLCONFIGDIR'] = '/tmp'
os.environ['XDG_CACHE_HOME'] = '/tmp/.cache'
os.environ['TRANSFORMERS_CACHE'] = '/tmp'
os.environ['HF_HOME'] = '/tmp'

# Create cache directories
os.makedirs('/tmp/.cache', exist_ok=True)
TMP_NLTK_DIR.mkdir(parents=True, exist_ok=True)

# Now import other modules AFTER environment is set
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Tuple
import re
import string
from collections import Counter
import textstat
import nltk
from difflib import SequenceMatcher
import uvicorn

nltk_paths = []
if LOCAL_NLTK_DIR.exists():
    nltk_paths.append(str(LOCAL_NLTK_DIR))
nltk_paths.append(str(TMP_NLTK_DIR))
nltk_paths.extend([path for path in nltk.data.path if path not in nltk_paths])
nltk.data.path = nltk_paths

# Initialize FastAPI app
app = FastAPI(
    title="Writesonic SEO Analyzer",
    description="Analyze text content for SEO metrics",
    version="1.0.0"
)

# Download NLTK data on startup when not bundled
@app.on_event("startup")
async def startup_event():
    """Ensure essential NLTK resources are available before serving requests."""

    required_resources = [
        ("corpora/stopwords", "stopwords"),
        ("tokenizers/punkt", "punkt"),
    ]

    for resource, package in required_resources:
        try:
            nltk.data.find(resource)
            print(f"NLTK resource '{resource}' already available")
        except LookupError:
            try:
                print(f"Attempting to download '{package}' to {TMP_NLTK_DIR}...")
                nltk.download(package, download_dir=str(TMP_NLTK_DIR), quiet=True)
                nltk.data.find(resource)
                print(f"Successfully downloaded '{package}' to {TMP_NLTK_DIR}")
            except Exception as exc:  # pragma: no cover - diagnostics only
                print(f"Warning: unable to obtain NLTK resource '{resource}': {exc}")

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:4000",
        "https://frontend-kappa-inky-92.vercel.app",
        "https://frontend-2ceydx4l7-manjunath-kulals-projects.vercel.app",
        "https://frontend-cpfr19apd-manjunath-kulals-projects.vercel.app",
        "https://frontend-fovy6f1m9-manjunath-kulals-projects.vercel.app",
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Sample texts for plagiarism comparison
SAMPLE_TEXTS = {
    "article1": """
    Search engine optimization is crucial for online visibility. Quality content
    that engages readers and provides value is essential for SEO success. Keywords
    should be used naturally throughout the text. Content should be readable and
    well-structured with proper headings and paragraphs. Regular updates and fresh
    content help maintain good search rankings.
    """,
    "article2": """
    Digital marketing strategies have evolved significantly over the years. Social
    media platforms play a vital role in brand awareness and customer engagement.
    Content marketing focuses on creating valuable, relevant content to attract and
    retain a clearly defined audience. Email marketing remains one of the most
    effective channels for direct communication with customers.
    """,
    "article3": """
    Artificial intelligence and machine learning are transforming business operations.
    Automation helps companies improve efficiency and reduce operational costs.
    Data analytics provides insights that drive better decision-making. Cloud
    computing enables scalable and flexible infrastructure for modern applications.
    Cybersecurity is increasingly important in protecting digital assets.
    """
}

# Global variable to cache stopwords
_stopwords_cache = None


class AnalyzeRequest(BaseModel):
    """Request model for text analysis"""
    text: str


class SerpPreview(BaseModel):
    """SERP (Search Engine Results Page) preview model"""
    meta_title: str
    meta_description: str
    url_slug: str
    ctr_score: float  # Click-Through Rate prediction (0-100)
    title_length: int
    description_length: int
    title_issues: List[str]
    description_issues: List[str]


class AnalyzeResponse(BaseModel):
    """Response model for text analysis results"""
    readability: float
    top_keywords: List[Tuple[str, int]]
    keyword_density: Dict[str, float]
    plagiarism_score: float
    final_score: float
    suggestions: List[str]  # AI-powered improvement suggestions
    serp_preview: SerpPreview  # Google SERP preview and CTR prediction


def get_stopwords() -> set:
    """
    Load NLTK stopwords, downloading if necessary.
    Caches the stopwords for subsequent calls.
    
    Returns:
        set: Set of English stopwords
    """
    global _stopwords_cache
    
    if _stopwords_cache is not None:
        return _stopwords_cache
    
    try:
        stopwords_set = set(nltk.corpus.stopwords.words('english'))
    except LookupError:
        # Fallback: use a bundled minimal stopwords list to avoid runtime downloads
        print("NLTK stopwords not found; using bundled fallback stopwords list")
        fallback_stopwords = {
            'a','about','above','after','again','against','all','am','an','and','any','are','as','at',
            'be','because','been','before','being','below','between','both','but','by','could','did',
            'do','does','doing','down','during','each','few','for','from','further','had','has','have',
            'having','he','her','here','hers','herself','him','himself','his','how','i','if','in','into',
            'is','it','its','itself','me','more','most','my','myself','no','nor','not','of','off','on','once',
            'only','or','other','our','ours','ourselves','out','over','own','same','she','should','so','some',
            'such','than','that','the','their','theirs','them','themselves','then','there','these','they','this',
            'those','through','to','too','under','until','up','very','was','we','were','what','when','where','which',
            'while','who','whom','why','with','would','you','your','yours','yourself','yourselves'
        }
        stopwords_set = fallback_stopwords
    
    _stopwords_cache = stopwords_set
    return stopwords_set


def clean_text(text: str) -> str:
    """
    Normalize text by converting to lowercase and removing punctuation.
    
    Args:
        text: Input text to clean
        
    Returns:
        str: Cleaned and normalized text
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation
    translator = str.maketrans('', '', string.punctuation)
    text = text.translate(translator)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    return text


def calculate_keyword_stats(text: str, top_n: int = 10) -> Tuple[List[Tuple[str, int]], Dict[str, float]]:
    """
    Calculate keyword statistics including top keywords and their density.
    
    Args:
        text: Input text to analyze
        top_n: Number of top keywords to return
        
    Returns:
        Tuple containing:
            - List of (word, count) tuples for top keywords
            - Dictionary mapping words to their density percentage
    """
    # Clean the text
    cleaned = clean_text(text)
    
    # Get stopwords
    stopwords = get_stopwords()
    
    # Tokenize and filter stopwords
    words = cleaned.split()
    filtered_words = [word for word in words if word and word not in stopwords and len(word) > 2]
    
    # Count word frequencies
    word_counts = Counter(filtered_words)
    
    # Get top N keywords
    top_keywords = word_counts.most_common(top_n)
    
    # Calculate keyword density (percentage of total words)
    total_words = len(filtered_words)
    keyword_density = {}
    
    if total_words > 0:
        for word, count in top_keywords:
            density = (count / total_words) * 100
            keyword_density[word] = round(density, 2)
    
    return top_keywords, keyword_density


def simulate_serp(content: str) -> SerpPreview:
    """
    Simulate Google SERP preview and predict CTR (Click-Through Rate).
    
    Extracts meta information from content and generates a SERP snippet preview
    similar to how Google displays search results. Predicts CTR based on
    optimization best practices.
    
    Handles edge cases:
    - Very short content (< 10 words)
    - Very long content (> 10,000 chars)
    - Special characters and emojis
    - Missing titles or descriptions
    
    Args:
        content: Full text content to analyze
        
    Returns:
        SerpPreview: SERP preview with CTR prediction and optimization feedback
    """
    # Edge case: Handle empty or very short content
    if not content or len(content.strip()) < 10:
        return SerpPreview(
            meta_title="Untitled Content",
            meta_description="No content provided for analysis.",
            url_slug="untitled-content",
            ctr_score=0.0,
            title_length=16,
            description_length=34,
            title_issues=["⚠️ No content provided - add text to generate preview"],
            description_issues=["⚠️ No content provided - add text to generate preview"]
        )
    
    # Edge case: Truncate very long content for processing
    content_to_process = content[:10000] if len(content) > 10000 else content
    
    # Clean special characters and emojis for better processing
    # Keep common punctuation but remove problematic characters
    clean_content = re.sub(r'[^\w\s\.\,\!\?\:\;\-\(\)\[\]]', ' ', content_to_process)
    clean_content = re.sub(r'\s+', ' ', clean_content).strip()
    
    # Extract headings (simulate H1 tag as title)
    lines = [line.strip() for line in content_to_process.split('\n') if line.strip()]
    
    # 1. EXTRACT META TITLE
    # Try to find a title-like line (short, at beginning, or in title case)
    meta_title = ""
    for i, line in enumerate(lines[:5]):  # Check first 5 lines instead of 3
        # Clean line
        clean_line = re.sub(r'[#*_`\[\]]', '', line).strip()
        
        # Title heuristics: 10-100 chars, starts with capital, not all caps
        if 10 <= len(clean_line) <= 100 and clean_line[0].isupper() and not clean_line.isupper():
            meta_title = clean_line
            break
    
    # Fallback: use first sentence if no title found
    if not meta_title:
        sentences = re.split(r'[.!?]+', clean_content)
        if sentences and sentences[0].strip():
            meta_title = sentences[0].strip()[:100]  # Limit fallback length
        else:
            # Ultimate fallback: use first 60 chars
            meta_title = content_to_process[:60].strip() or "Untitled Content"
    
    # Clean title (remove markdown, extra spaces, emojis)
    meta_title = re.sub(r'[#*_`]', '', meta_title).strip()
    meta_title = re.sub(r'\s+', ' ', meta_title)
    
    # Store original length before truncation
    title_length = len(meta_title)
    
    # Limit title to 60 characters (Google's display limit)
    if title_length > 60:
        meta_title = meta_title[:57] + "..."
        title_length = 60  # Display length after truncation
    
    # Edge case: Title too short
    if title_length < 10:
        meta_title = (meta_title + " - SEO Content Analysis")[:60]
        title_length = len(meta_title)
    
    # 2. EXTRACT META DESCRIPTION
    # Use first 2-3 sentences as description
    sentences = re.split(r'(?<=[.!?])\s+', clean_content)
    description_sentences = []
    char_count = 0
    
    # Skip title sentence if it matches
    title_lower = meta_title.lower().replace('...', '')
    
    for sentence in sentences[:10]:  # Check more sentences for better description
        sentence = sentence.strip()
        
        # Skip empty, title matches, or very short sentences
        if not sentence or len(sentence) < 15:
            continue
        if title_lower in sentence.lower()[:len(title_lower) + 10]:
            continue
            
        # Add sentence if it fits
        sentence_len = len(sentence)
        if char_count + sentence_len <= 155:  # Google's optimal length
            description_sentences.append(sentence)
            char_count += sentence_len + 1  # +1 for space
        elif char_count < 100:  # If description too short, add partial sentence
            remaining = 155 - char_count
            if remaining > 30:  # Only add if meaningful portion fits
                description_sentences.append(sentence[:remaining - 3] + "...")
                char_count = 155
                break
        else:
            break
    
    meta_description = ' '.join(description_sentences)
    
    # Fallback if no good description (edge case)
    if not meta_description or len(meta_description) < 50:
        # Try to extract from beginning of content, skip title
        start_pos = len(lines[0]) if lines else 0
        fallback_text = content_to_process[start_pos:start_pos + 155].strip()
        
        if len(fallback_text) < 50:
            # Ultimate fallback: use whatever content we have
            fallback_text = content_to_process[:155].strip()
        
        meta_description = fallback_text[:152] + "..." if len(fallback_text) >= 152 else fallback_text
    
    description_length = len(meta_description)
    
    # Ensure description doesn't exceed 160 chars (Google cutoff)
    if description_length > 160:
        meta_description = meta_description[:157] + "..."
        description_length = 160
    
    # 3. GENERATE URL SLUG
    # Convert title to URL-friendly slug
    url_slug = meta_title.lower()
    url_slug = re.sub(r'[^\w\s-]', '', url_slug)  # Remove special chars
    url_slug = re.sub(r'[\s_]+', '-', url_slug)   # Replace spaces with hyphens
    url_slug = url_slug[:50]  # Limit length
    
    # 4. ANALYZE TITLE OPTIMIZATION
    title_issues = []
    
    # Check title length (optimal: 50-60 chars)
    if title_length < 30:
        title_issues.append("⚠️ Title too short - aim for 50-60 characters")
    elif title_length > 60:
        title_issues.append("⚠️ Title too long - will be truncated in search results")
    
    # Check for numbers (increase CTR by ~36%)
    if not re.search(r'\d', meta_title):
        title_issues.append("💡 Add numbers/statistics to increase CTR")
    
    # Check for power words (How, Why, What, Best, Guide, etc.)
    power_words = ['how', 'why', 'what', 'best', 'top', 'guide', 'ultimate', 
                   'complete', 'essential', 'proven', 'easy', 'simple']
    if not any(word in meta_title.lower() for word in power_words):
        title_issues.append("💡 Use power words (How, Best, Guide) to boost appeal")
    
    # Check for special characters (brackets, pipes increase CTR)
    if not re.search(r'[|\[\]()]', meta_title):
        title_issues.append("💡 Consider using brackets or pipes for emphasis")
    
    # 5. ANALYZE DESCRIPTION OPTIMIZATION
    description_issues = []
    
    # Check description length (optimal: 120-155 chars)
    if description_length < 70:
        description_issues.append("⚠️ Description too short - aim for 120-155 characters")
    elif description_length > 160:
        description_issues.append("⚠️ Description too long - will be truncated")
    
    # Check for call-to-action words
    cta_words = ['learn', 'discover', 'find out', 'get', 'try', 'start', 
                 'read', 'explore', 'see', 'check out']
    if not any(word in meta_description.lower() for word in cta_words):
        description_issues.append("💡 Add a call-to-action (Learn, Discover, Get)")
    
    # Check for question mark (increases engagement)
    if '?' not in meta_description:
        description_issues.append("💡 Consider posing a question to spark curiosity")
    
    # 6. CALCULATE CTR PREDICTION SCORE (0-100)
    ctr_score = 50.0  # Base score
    
    # Title factors
    if 50 <= title_length <= 60:
        ctr_score += 15  # Optimal length
    elif 40 <= title_length < 50 or 60 < title_length <= 70:
        ctr_score += 8   # Acceptable length
    
    if re.search(r'\d', meta_title):
        ctr_score += 10  # Has numbers
    
    if any(word in meta_title.lower() for word in power_words):
        ctr_score += 12  # Has power words
    
    if re.search(r'[|\[\]()]', meta_title):
        ctr_score += 8   # Has special formatting
    
    # Description factors
    if 120 <= description_length <= 155:
        ctr_score += 10  # Optimal length
    elif 100 <= description_length < 120 or 155 < description_length <= 160:
        ctr_score += 5   # Acceptable length
    
    if any(word in meta_description.lower() for word in cta_words):
        ctr_score += 8   # Has CTA
    
    if '?' in meta_description:
        ctr_score += 5   # Has question
    
    # Keyword presence (check if title keywords appear in description)
    title_words = set(re.findall(r'\w+', meta_title.lower()))
    desc_words = set(re.findall(r'\w+', meta_description.lower()))
    keyword_overlap = len(title_words & desc_words) / max(len(title_words), 1)
    ctr_score += keyword_overlap * 7  # Reward consistency
    
    # Ensure score is within 0-100 range
    ctr_score = min(100.0, max(0.0, ctr_score))
    ctr_score = round(ctr_score, 1)
    
    return SerpPreview(
        meta_title=meta_title,
        meta_description=meta_description,
        url_slug=url_slug,
        ctr_score=ctr_score,
        title_length=title_length,
        description_length=description_length,
        title_issues=title_issues if title_issues else ["✅ Title is well optimized"],
        description_issues=description_issues if description_issues else ["✅ Description is well optimized"]
    )


def calc_readability(text: str) -> float:
    """
    Calculate readability score using Flesch Reading Ease.
    
    Score interpretation:
    - 90-100: Very Easy (5th grade)
    - 80-89: Easy (6th grade)
    - 70-79: Fairly Easy (7th grade)
    - 60-69: Standard (8th-9th grade)
    - 50-59: Fairly Difficult (10th-12th grade)
    - 30-49: Difficult (College)
    - 0-29: Very Difficult (College graduate)
    
    Args:
        text: Input text to analyze
        
    Returns:
        float: Flesch Reading Ease score (0-100, higher is easier)
    """
    try:
        score = textstat.flesch_reading_ease(text)
        # Ensure score is within valid range
        return max(0.0, min(100.0, float(score)))
    except Exception as e:
        print(f"Error calculating readability: {e}")
        return 50.0  # Return neutral score on error


def check_plagiarism(text: str) -> float:
    """
    Check text for potential plagiarism using multiple techniques:
    1. N-gram similarity detection (5-gram overlaps)
    2. Sentence-level similarity comparison
    3. Common phrase detection
    
    Args:
        text: Input text to check for plagiarism
        
    Returns:
        float: Plagiarism score (0-100, higher means more similar/plagiarized)
    """
    if not text or len(text.strip()) < 10:
        return 0.0
    
    # Clean and normalize input text
    cleaned_input = clean_text(text.lower())
    input_sentences = [s.strip() for s in text.split('.') if s.strip()]
    
    max_similarity = 0.0
    
    # Compare with each sample text using multiple techniques
    for sample_name, sample_text in SAMPLE_TEXTS.items():
        cleaned_sample = clean_text(sample_text.lower())
        sample_sentences = [s.strip() for s in sample_text.split('.') if s.strip()]
        
        # Technique 1: N-gram similarity (5-grams)
        ngram_similarity = calculate_ngram_similarity(cleaned_input, cleaned_sample, n=5)
        
        # Technique 2: Sentence-level similarity
        sentence_similarity = calculate_sentence_similarity(input_sentences, sample_sentences)
        
        # Technique 3: Overall sequence similarity
        sequence_similarity = SequenceMatcher(None, cleaned_input, cleaned_sample).ratio()
        
        # Weighted combination (n-grams are most reliable)
        combined_similarity = (
            ngram_similarity * 0.5 +
            sentence_similarity * 0.3 +
            sequence_similarity * 0.2
        )
        
        max_similarity = max(max_similarity, combined_similarity)
    
    # Convert to percentage
    plagiarism_score = max_similarity * 100
    
    return round(plagiarism_score, 2)


def calculate_ngram_similarity(text1: str, text2: str, n: int = 5) -> float:
    """
    Calculate similarity based on n-gram overlap.
    This detects copied phrases even if words are reordered.
    
    Args:
        text1: First text
        text2: Second text
        n: Size of n-grams (default 5 words)
        
    Returns:
        float: Similarity score (0-1)
    """
    words1 = text1.split()
    words2 = text2.split()
    
    if len(words1) < n or len(words2) < n:
        return 0.0
    
    # Create n-grams
    ngrams1 = set(' '.join(words1[i:i+n]) for i in range(len(words1) - n + 1))
    ngrams2 = set(' '.join(words2[i:i+n]) for i in range(len(words2) - n + 1))
    
    if not ngrams1 or not ngrams2:
        return 0.0
    
    # Calculate Jaccard similarity
    intersection = len(ngrams1.intersection(ngrams2))
    union = len(ngrams1.union(ngrams2))
    
    return intersection / union if union > 0 else 0.0


def calculate_sentence_similarity(sentences1: List[str], sentences2: List[str]) -> float:
    """
    Calculate similarity at sentence level.
    Detects if entire sentences are copied.
    
    Args:
        sentences1: List of sentences from first text
        sentences2: List of sentences from second text
        
    Returns:
        float: Similarity score (0-1)
    """
    if not sentences1 or not sentences2:
        return 0.0
    
    max_similarities = []
    
    # For each sentence in input, find best match in sample
    for sent1 in sentences1:
        cleaned_sent1 = clean_text(sent1.lower())
        if len(cleaned_sent1.split()) < 3:  # Skip very short sentences
            continue
            
        best_match = 0.0
        for sent2 in sentences2:
            cleaned_sent2 = clean_text(sent2.lower())
            if len(cleaned_sent2.split()) < 3:
                continue
                
            similarity = SequenceMatcher(None, cleaned_sent1, cleaned_sent2).ratio()
            best_match = max(best_match, similarity)
        
        if best_match > 0.5:  # Only count significant matches
            max_similarities.append(best_match)
    
    # Return average of high similarity matches
    if max_similarities:
        return sum(max_similarities) / len(sentences1)
    
    return 0.0


def compute_final_score(
    readability: float,
    plagiarism: float,
    keyword_stats: Tuple[List[Tuple[str, int]], Dict[str, float]]
) -> float:
    """
    Compute final SEO score based on multiple factors.
    
    Formula:
    - Readability contributes 40% (normalized to 0-100)
    - Originality (100 - plagiarism) contributes 30%
    - Keyword diversity contributes 30% (based on number and distribution)
    
    Args:
        readability: Flesch Reading Ease score
        plagiarism: Plagiarism score (0-100)
        keyword_stats: Tuple of (top_keywords, keyword_density)
        
    Returns:
        float: Final SEO score (0-100, higher is better)
    """
    # Readability component (40% weight)
    # Optimal readability is 60-70 (standard), normalize around that
    readability_score = readability
    if readability < 30:
        readability_normalized = readability / 30 * 50  # Too difficult
    elif readability > 90:
        readability_normalized = (100 - readability) / 10 * 50 + 50  # Too easy
    else:
        # Ideal range gets full points
        readability_normalized = 100
    
    readability_component = readability_normalized * 0.4
    
    # Originality component (30% weight)
    originality_score = 100 - plagiarism
    originality_component = originality_score * 0.3
    
    # Keyword diversity component (30% weight)
    top_keywords, keyword_density = keyword_stats
    
    # Score based on number of keywords and distribution
    keyword_count = len(top_keywords)
    keyword_score = 0
    
    if keyword_count > 0:
        # More keywords is better (up to 10)
        diversity_score = min(keyword_count / 10 * 100, 100)
        
        # Check for balanced distribution (no single keyword dominates)
        if keyword_density:
            densities = list(keyword_density.values())
            max_density = max(densities)
            
            # Penalize if top keyword is more than 20% of content
            if max_density > 20:
                balance_penalty = (max_density - 20) * 2
                diversity_score = max(0, diversity_score - balance_penalty)
        
        keyword_score = diversity_score
    
    keyword_component = keyword_score * 0.3
    
    # Calculate final score
    final_score = readability_component + originality_component + keyword_component
    
    return round(final_score, 2)


def generate_suggestions(
    text: str,
    readability: float,
    plagiarism: float,
    keyword_stats: Tuple[List[Tuple[str, int]], Dict[str, float]],
    final_score: float
) -> List[str]:
    """
    Generate AI-powered improvement suggestions based on analysis.
    
    Args:
        text: Original text
        readability: Readability score
        plagiarism: Plagiarism score
        keyword_stats: Keyword statistics
        final_score: Overall score
        
    Returns:
        List of actionable suggestions
    """
    suggestions = []
    top_keywords, keyword_density = keyword_stats
    
    # Readability suggestions
    if readability < 30:
        suggestions.append("📚 Your content is quite complex. Consider breaking long sentences into shorter ones for better readability.")
        suggestions.append("💡 Use simpler words and avoid jargon where possible to reach a wider audience.")
    elif readability < 50:
        suggestions.append("📖 Content readability could be improved. Try using shorter paragraphs and simpler sentence structures.")
    elif readability > 90:
        suggestions.append("🎯 Your content might be too simple. Add more depth and detail to provide more value.")
    elif 60 <= readability <= 70:
        suggestions.append("✅ Excellent readability! Your content is easy to understand while remaining professional.")
    
    # Plagiarism suggestions
    if plagiarism > 50:
        suggestions.append("⚠️ High similarity detected! Rewrite content in your own words to ensure originality.")
    elif plagiarism > 30:
        suggestions.append("🔄 Moderate similarity found. Consider paraphrasing some sections for better uniqueness.")
    elif plagiarism < 10:
        suggestions.append("✨ Great originality! Your content appears to be highly unique.")
    
    # Keyword suggestions
    if len(top_keywords) < 5:
        suggestions.append("🔑 Add more relevant keywords to improve SEO. Aim for 8-10 key terms naturally integrated.")
    elif len(top_keywords) >= 8:
        suggestions.append("🎯 Good keyword variety! Your content covers multiple topics effectively.")
    
    # Check keyword density
    if keyword_density:
        max_density = max(keyword_density.values())
        if max_density > 20:
            top_word = [k for k, v in keyword_density.items() if v == max_density][0]
            suggestions.append(f"⚡ The keyword '{top_word}' appears too frequently ({max_density:.1f}%). Reduce to avoid keyword stuffing.")
        elif max_density < 2:
            suggestions.append("💭 Your keywords have very low density. Try emphasizing key terms more throughout your content.")
    
    # Content length suggestions
    word_count = len(text.split())
    if word_count < 300:
        suggestions.append(f"📝 Your content is quite short ({word_count} words). Aim for 500-1000 words for better SEO performance.")
    elif word_count > 2000:
        suggestions.append(f"📄 Your content is lengthy ({word_count} words). Consider breaking it into multiple articles or adding subheadings.")
    elif 500 <= word_count <= 1500:
        suggestions.append(f"✅ Great content length! ({word_count} words) - optimal for SEO and reader engagement.")
    
    # Overall score suggestions
    if final_score >= 80:
        suggestions.append("🌟 Excellent SEO performance! Your content is well-optimized and ready to publish.")
    elif final_score >= 60:
        suggestions.append("👍 Good SEO foundation. Apply the suggestions above to reach excellent performance.")
    else:
        suggestions.append("🔧 Your content needs significant SEO improvements. Focus on readability, originality, and keyword optimization.")
    
    # Structure suggestions
    if "\n\n" not in text:
        suggestions.append("📋 Add paragraph breaks to improve content structure and readability.")
    
    return suggestions


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Writesonic SEO Analyzer API",
        "status": "active",
        "version": "1.0.0"
    }


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_text(request: AnalyzeRequest):
    """
    Analyze text content for SEO metrics.
    
    Args:
        request: AnalyzeRequest containing the text to analyze
        
    Returns:
        AnalyzeResponse with analysis results
        
    Raises:
        HTTPException: If text is empty or invalid
    """
    text = request.text
    
    # Validate input
    if not text or len(text.strip()) < 10:
        raise HTTPException(
            status_code=400,
            detail="Text must be at least 10 characters long"
        )
    
    try:
        # Calculate readability
        readability = calc_readability(text)
        
        # Calculate keyword statistics
        keyword_stats = calculate_keyword_stats(text, top_n=10)
        top_keywords, keyword_density = keyword_stats
        
        # Calculate plagiarism score using real detection
        plagiarism_score = check_plagiarism(text)
        
        # Compute final score
        final_score = compute_final_score(readability, plagiarism_score, keyword_stats)
        
        # Generate improvement suggestions
        suggestions = generate_suggestions(text, readability, plagiarism_score, keyword_stats, final_score)
        
        # Simulate SERP preview and CTR prediction
        serp_preview = simulate_serp(text)
        
        return AnalyzeResponse(
            readability=readability,
            top_keywords=top_keywords,
            keyword_density=keyword_density,
            plagiarism_score=plagiarism_score,
            final_score=final_score,
            suggestions=suggestions,
            serp_preview=serp_preview
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing text: {str(e)}"
        )


def test_api_example():
    """
    Example function demonstrating how to test the API using TestClient.
    This can be run to verify the API is working correctly.
    """
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    
    # Sample text for testing
    sample_text = """
    Content marketing is essential for modern businesses. Quality content helps
    improve search engine rankings and attracts organic traffic. SEO best practices
    include keyword research, on-page optimization, and creating engaging content
    that provides value to readers. Regular content updates and proper formatting
    with headings and paragraphs improve readability. Link building and social
    media promotion also contribute to better visibility online.
    """
    
    # Make request to analyze endpoint
    response = client.post("/analyze", json={"text": sample_text})
    
    print("\n" + "="*60)
    print("API Test Results")
    print("="*60)
    print(f"Status Code: {response.status_code}")
    print(f"\nResponse:")
    
    if response.status_code == 200:
        data = response.json()
        print(f"\nReadability Score: {data['readability']:.2f}")
        print(f"Plagiarism Score: {data['plagiarism_score']:.2f}%")
        print(f"Final Score: {data['final_score']:.2f}/100")
        print(f"\nTop Keywords:")
        for word, count in data['top_keywords'][:5]:
            density = data['keyword_density'].get(word, 0)
            print(f"  - {word}: {count} occurrences ({density}%)")
    else:
        print(f"Error: {response.json()}")
    
    print("="*60 + "\n")
    
    return response


if __name__ == "__main__":
    # Run test example
    print("Running API test example...")
    test_api_example()
    
    # Start the server
    print("\nStarting Writesonic SEO Analyzer API server...")
    print("API documentation available at: http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
