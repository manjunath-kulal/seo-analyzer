"""Download required NLTK corpora into ``backend/nltk_data``.

This script also applies an SSL workaround for macOS systems that have
missing root certificates so that ``nltk.download`` succeeds.
"""

from __future__ import annotations

import ssl
from pathlib import Path

import nltk


def configure_ssl() -> None:
    """Apply an SSL context that skips certificate validation when needed."""

    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:  # pragma: no cover - very old Python versions
        return

    ssl._create_default_https_context = _create_unverified_https_context


def ensure_download_dir() -> Path:
    """Return the target download directory and make sure it exists."""

    base_dir = Path(__file__).resolve().parent
    download_dir = base_dir / "nltk_data"
    download_dir.mkdir(parents=True, exist_ok=True)
    return download_dir


def download_packages(download_dir: Path) -> None:
    # Only download corpora required by the application.
    packages = ['stopwords', 'punkt']

    print("Downloading NLTK data packages...")
    for package in packages:
        try:
            print(f"\nDownloading {package} to {download_dir}...")
            nltk.download(package, download_dir=str(download_dir))
            print(f"✓ Successfully downloaded {package}")
        except Exception as exc:  # pragma: no cover - download failure is informational
            print(f"✗ Error downloading {package}: {exc}")


def verify_stopwords(download_dir: Path) -> None:
    """Try loading the stopwords corpus from the downloaded data."""

    nltk.data.path.insert(0, str(download_dir))

    try:
        from nltk.corpus import stopwords

        words = stopwords.words('english')
        print(f"\n✓ Loaded {len(words)} English stopwords")
    except Exception as exc:  # pragma: no cover - download failure is informational
        print(f"✗ Error loading stopwords: {exc}")


def main() -> None:
    configure_ssl()
    download_dir = ensure_download_dir()
    download_packages(download_dir)
    verify_stopwords(download_dir)
    print(f"\n✅ NLTK data setup complete! Files stored in: {download_dir}")


if __name__ == "__main__":
    main()
