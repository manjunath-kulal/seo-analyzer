"""
Download NLTK data with SSL workaround
"""
import ssl
import nltk

# Create unverified SSL context (for SSL certificate issues on macOS)
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Download required NLTK data
print("Downloading NLTK data packages...")
packages = ['stopwords', 'punkt', 'averaged_perceptron_tagger', 'cmudict']

for package in packages:
    try:
        print(f"\nDownloading {package}...")
        nltk.download(package)
        print(f"✓ Successfully downloaded {package}")
    except Exception as e:
        print(f"✗ Error downloading {package}: {e}")

# Test stopwords
try:
    from nltk.corpus import stopwords
    words = stopwords.words('english')
    print(f"\n✓ Loaded {len(words)} English stopwords")
except Exception as e:
    print(f"✗ Error loading stopwords: {e}")

print("\n✅ NLTK data setup complete!")
