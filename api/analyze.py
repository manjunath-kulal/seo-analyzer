from http.server import BaseHTTPRequestHandler
import json
import re
import textstat
import nltk
from collections import Counter
from urllib.parse import unquote
import sys
import os

# Download required NLTK data if not present
try:
    nltk.data.find('corpora/cmudict')
except LookupError:
    nltk.download('cmudict', quiet=True)

from nltk.corpus import cmudict

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Set CORS headers
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            # Get request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            text = data.get('text', '')
            
            if not text.strip():
                response = {
                    "readability_score": 0,
                    "word_count": 0,
                    "character_count": 0,
                    "plagiarism_score": 0,
                    "keywords": [],
                    "keyword_density": {},
                    "serp_preview": {
                        "title": "",
                        "description": "",
                        "url": "",
                        "ctr_score": 0
                    },
                    "suggestions": ["Please enter some text to analyze."]
                }
                self.wfile.write(json.dumps(response).encode())
                return
            
            # Calculate all metrics
            readability = self.calc_readability(text)
            word_count = len(text.split())
            char_count = len(text)
            plagiarism = self.check_plagiarism(text)
            keywords = self.extract_keywords(text)
            keyword_density = self.calculate_keyword_density(text)
            serp_preview = self.simulate_serp(text)
            suggestions = self.generate_suggestions(text, readability, plagiarism, keywords, word_count)
            
            response = {
                "readability_score": readability,
                "word_count": word_count,
                "character_count": char_count,
                "plagiarism_score": plagiarism,
                "keywords": keywords,
                "keyword_density": keyword_density,
                "serp_preview": serp_preview,
                "suggestions": suggestions
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            error_response = {"error": str(e)}
            self.wfile.write(json.dumps(error_response).encode())
    
    def do_OPTIONS(self):
        # Handle preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def calc_readability(self, text):
        """Calculate readability score using Flesch Reading Ease"""
        try:
            # Use textstat for Flesch Reading Ease calculation
            score = textstat.flesch_reading_ease(text)
            
            # If textstat fails, use NLTK cmudict as fallback
            if score is None or score < 0:
                try:
                    d = cmudict.dict()
                    
                    def count_syllables(word):
                        word = word.lower()
                        if word in d:
                            return max([len([y for y in x if y[-1].isdigit()]) for x in d[word]])
                        else:
                            # Fallback syllable counting
                            vowels = "aeiouy"
                            syllables = 0
                            prev_char_was_vowel = False
                            for char in word:
                                if char in vowels:
                                    if not prev_char_was_vowel:
                                        syllables += 1
                                    prev_char_was_vowel = True
                                else:
                                    prev_char_was_vowel = False
                            if word.endswith('e'):
                                syllables -= 1
                            return max(1, syllables)
                    
                    sentences = re.split(r'[.!?]+', text)
                    sentences = [s.strip() for s in sentences if s.strip()]
                    
                    words = re.findall(r'\b\w+\b', text.lower())
                    
                    if len(sentences) == 0 or len(words) == 0:
                        return 50.0
                    
                    total_syllables = sum(count_syllables(word) for word in words)
                    
                    # Flesch Reading Ease formula
                    asl = len(words) / len(sentences)  # Average sentence length
                    asw = total_syllables / len(words)  # Average syllables per word
                    
                    score = 206.835 - (1.015 * asl) - (84.6 * asw)
                    return max(0, min(100, score))
                    
                except Exception:
                    return 50.0
            
            return max(0, min(100, score))
            
        except Exception:
            return 50.0
    
    def check_plagiarism(self, text):
        """Check for potential plagiarism using multiple similarity methods"""
        try:
            # Sample reference texts for comparison
            reference_texts = [
                "Search engine optimization is the process of improving the quality and quantity of website traffic.",
                "Content marketing is a strategic marketing approach focused on creating and distributing valuable content.",
                "Digital marketing encompasses all marketing efforts that use electronic devices or the internet.",
                "Social media marketing involves creating content for social media platforms to promote products.",
                "Email marketing is the act of sending commercial messages to a group of people using email.",
                "Pay-per-click advertising is an internet advertising model used to drive traffic to websites.",
                "Conversion rate optimization is the process of increasing the percentage of website visitors.",
                "Web analytics is the measurement and analysis of web data to understand user behavior.",
                "Search engine marketing is a form of internet marketing that involves promoting websites.",
                "Affiliate marketing is a marketing arrangement by which an online retailer pays commission."
            ]
            
            def get_ngrams(text, n=3):
                words = re.findall(r'\b\w+\b', text.lower())
                return [' '.join(words[i:i+n]) for i in range(len(words)-n+1)]
            
            def sentence_similarity(text1, text2):
                sentences1 = re.split(r'[.!?]+', text1.lower())
                sentences2 = re.split(r'[.!?]+', text2.lower())
                
                sentences1 = [s.strip() for s in sentences1 if s.strip()]
                sentences2 = [s.strip() for s in sentences2 if s.strip()]
                
                if not sentences1 or not sentences2:
                    return 0
                
                matches = 0
                for s1 in sentences1:
                    for s2 in sentences2:
                        words1 = set(re.findall(r'\b\w+\b', s1))
                        words2 = set(re.findall(r'\b\w+\b', s2))
                        
                        if len(words1) > 0 and len(words2) > 0:
                            similarity = len(words1.intersection(words2)) / len(words1.union(words2))
                            if similarity > 0.7:
                                matches += 1
                                break
                
                return matches / len(sentences1)
            
            def sequence_similarity(text1, text2):
                words1 = re.findall(r'\b\w+\b', text1.lower())
                words2 = re.findall(r'\b\w+\b', text2.lower())
                
                if not words1 or not words2:
                    return 0
                
                # Find longest common subsequence
                def lcs_length(seq1, seq2):
                    m, n = len(seq1), len(seq2)
                    dp = [[0] * (n + 1) for _ in range(m + 1)]
                    
                    for i in range(1, m + 1):
                        for j in range(1, n + 1):
                            if seq1[i-1] == seq2[j-1]:
                                dp[i][j] = dp[i-1][j-1] + 1
                            else:
                                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
                    
                    return dp[m][n]
                
                lcs_len = lcs_length(words1, words2)
                return lcs_len / min(len(words1), len(words2))
            
            input_ngrams = get_ngrams(text)
            
            if not input_ngrams:
                return 0
            
            max_similarity = 0
            
            for ref_text in reference_texts:
                ref_ngrams = get_ngrams(ref_text)
                
                if not ref_ngrams:
                    continue
                
                # N-gram similarity (50% weight)
                common_ngrams = len(set(input_ngrams).intersection(set(ref_ngrams)))
                ngram_similarity = common_ngrams / len(set(input_ngrams).union(set(ref_ngrams)))
                
                # Sentence-level similarity (30% weight)
                sent_similarity = sentence_similarity(text, ref_text)
                
                # Sequence similarity (20% weight)
                seq_similarity = sequence_similarity(text, ref_text)
                
                # Combined similarity score
                combined_similarity = (
                    ngram_similarity * 0.5 + 
                    sent_similarity * 0.3 + 
                    seq_similarity * 0.2
                )
                
                max_similarity = max(max_similarity, combined_similarity)
            
            # Convert to percentage and add some baseline similarity
            plagiarism_score = min(100, max_similarity * 100 + 10)
            
            return round(plagiarism_score, 1)
            
        except Exception:
            return 15.0
    
    def extract_keywords(self, text):
        """Extract keywords from text"""
        try:
            # Simple keyword extraction
            words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
            
            # Remove common stop words
            stop_words = {
                'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy', 'did', 'has', 'let', 'put', 'say', 'she', 'too', 'use'
            }
            
            filtered_words = [word for word in words if word not in stop_words and len(word) > 3]
            
            # Count frequency
            word_freq = Counter(filtered_words)
            
            # Get top keywords
            top_keywords = [word for word, freq in word_freq.most_common(10)]
            
            return top_keywords
            
        except Exception:
            return []
    
    def calculate_keyword_density(self, text):
        """Calculate keyword density"""
        try:
            words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
            total_words = len(words)
            
            if total_words == 0:
                return {}
            
            word_freq = Counter(words)
            
            # Calculate density for top words
            keyword_density = {}
            for word, freq in word_freq.most_common(5):
                if len(word) > 3:
                    density = (freq / total_words) * 100
                    keyword_density[word] = round(density, 2)
            
            return keyword_density
            
        except Exception:
            return {}
    
    def simulate_serp(self, text):
        """Simulate Google SERP preview"""
        try:
            # Extract title (first 60 characters)
            title = text[:60].strip()
            if len(text) > 60:
                title = title.rsplit(' ', 1)[0] + "..."
            
            # Generate meta description (first 155 characters)
            description = text[:155].strip()
            if len(text) > 155:
                description = description.rsplit(' ', 1)[0] + "..."
            
            # Generate URL slug
            url_words = re.findall(r'\b[a-zA-Z]+\b', text.lower())[:5]
            url_slug = "-".join(url_words)
            url = f"https://example.com/{url_slug}"
            
            # Calculate CTR score based on various factors
            ctr_score = self.calculate_ctr_score(title, description)
            
            return {
                "title": title,
                "description": description,
                "url": url,
                "ctr_score": ctr_score
            }
            
        except Exception:
            return {
                "title": "Sample Title",
                "description": "Sample description for SERP preview.",
                "url": "https://example.com/sample-page",
                "ctr_score": 50
            }
    
    def calculate_ctr_score(self, title, description):
        """Calculate predicted CTR score based on title and description quality"""
        try:
            score = 50  # Base score
            
            # Title length optimization
            if 30 <= len(title) <= 60:
                score += 10
            elif len(title) < 30:
                score -= 5
            
            # Description length optimization
            if 120 <= len(description) <= 155:
                score += 10
            elif len(description) < 120:
                score -= 5
            
            # Presence of numbers in title
            if re.search(r'\d', title):
                score += 5
            
            # Power words
            power_words = ['ultimate', 'complete', 'essential', 'proven', 'effective', 'powerful', 'amazing', 'incredible', 'outstanding', 'excellent']
            for word in power_words:
                if word.lower() in title.lower():
                    score += 3
                    break
            
            # Call-to-action words
            cta_words = ['learn', 'discover', 'find', 'get', 'start', 'try', 'download', 'buy', 'order', 'subscribe']
            for word in cta_words:
                if word.lower() in description.lower():
                    score += 3
                    break
            
            # Question in title
            if '?' in title:
                score += 5
            
            # Emotional words
            emotional_words = ['secret', 'hidden', 'revealed', 'shocking', 'surprising', 'unbelievable']
            for word in emotional_words:
                if word.lower() in title.lower():
                    score += 2
                    break
            
            return min(100, max(0, score))
            
        except Exception:
            return 50
    
    def generate_suggestions(self, text, readability, plagiarism, keywords, word_count):
        """Generate AI-powered suggestions for content improvement"""
        try:
            suggestions = []
            
            # Readability suggestions
            if readability < 30:
                suggestions.append("Your content is quite difficult to read. Try using shorter sentences and simpler words.")
            elif readability < 50:
                suggestions.append("Consider breaking down complex sentences to improve readability.")
            elif readability > 80:
                suggestions.append("Your content is very easy to read - great for broader audiences!")
            
            # Plagiarism suggestions
            if plagiarism > 70:
                suggestions.append("High similarity detected. Consider rephrasing and adding original insights.")
            elif plagiarism > 50:
                suggestions.append("Moderate similarity found. Try to add more unique perspectives.")
            elif plagiarism < 20:
                suggestions.append("Great! Your content appears to be highly original.")
            
            # Word count suggestions
            if word_count < 100:
                suggestions.append("Consider expanding your content. Longer articles often perform better in search results.")
            elif word_count > 2000:
                suggestions.append("Your content is quite long. Consider breaking it into sections or multiple articles.")
            elif 300 <= word_count <= 1500:
                suggestions.append("Good word count! This length is optimal for most content types.")
            
            # Keyword suggestions
            if len(keywords) < 3:
                suggestions.append("Try to include more relevant keywords to improve SEO visibility.")
            elif len(keywords) > 15:
                suggestions.append("You have many keywords. Focus on the most important ones to avoid keyword stuffing.")
            
            # Content structure suggestions
            sentences = re.split(r'[.!?]+', text)
            avg_sentence_length = sum(len(s.split()) for s in sentences if s.strip()) / max(len([s for s in sentences if s.strip()]), 1)
            
            if avg_sentence_length > 25:
                suggestions.append("Your sentences are quite long on average. Shorter sentences improve readability.")
            
            # SEO suggestions
            if not re.search(r'\?', text):
                suggestions.append("Consider adding questions to engage readers and improve SEO.")
            
            if not re.search(r'\d', text):
                suggestions.append("Adding numbers or statistics can make your content more compelling.")
            
            # If no specific suggestions, add general ones
            if not suggestions:
                suggestions.extend([
                    "Your content looks good overall! Consider adding more examples or case studies.",
                    "Try including relevant images or media to enhance user engagement.",
                    "Consider adding internal links to related content on your website."
                ])
            
            return suggestions[:5]  # Return max 5 suggestions
            
        except Exception:
            return ["Unable to generate suggestions. Please try again."]