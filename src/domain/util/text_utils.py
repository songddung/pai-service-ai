import re
from collections import Counter
from typing import List

def extract_keywords_from_text(text: str, max_keywords: int = 5) -> List[str]:
    """Extract keywords from text by removing stopwords and counting frequencies"""
    words = re.findall(r'[가-힣a-zA-Z]+', text)
    stopwords = {
        "해", "말", "되", "이", "그", "이런", "너", "저", "좀", "정도", "등", "이제", "너희", "여기", "저기",
        "이거", "그거", "저거", "봐", "들", "주세요", "요", "습니다", "입니다", "있다", "없다", "같다", "보다",
        "오", "가", "올", "갈", "할", "주", "줘", "수", "때", "거", "것", "하는", "한", "네", "응", "아니",
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are",
        "was", "were", "be", "been", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should",
        "this", "that", "these", "those", "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us",
        "them", "my", "your", "his", "her", "its", "our", "their", "mine", "yours", "hers", "ours", "theirs"
    }
    keywords = [word for word in words if len(word) > 1 and word.lower() not in stopwords]
    freq = Counter(keywords)
    return [item[0] for item in freq.most_common(max_keywords)]
