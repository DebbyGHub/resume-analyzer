"""
skill_extractor.py

Simple rule-based skill extraction from resume text.
Used for resume-aware interview question selection.
"""

import re

KNOWN_SKILLS = {
    # Programming Languages
    "python",
    "java",
    "c",
    "c++",
    "c#",
    "javascript",
    "typescript",
    "php",
    "go",
    "rust",
    "kotlin",
    "swift",
    "r",

    # Frontend
    "html",
    "css",
    "tailwind",
    "bootstrap",
    "react",
    "nextjs",
    "next.js",
    "vue",
    "angular",

    # Backend
    "node",
    "nodejs",
    "express",
    "expressjs",
    "fastapi",
    "flask",
    "django",
    "spring",
    "spring boot",

    # Databases
    "sql",
    "mysql",
    "postgresql",
    "sqlite",
    "mongodb",
    "redis",
    "firebase",

    # AI / ML / Data
    "machine learning",
    "deep learning",
    "artificial intelligence",
    "tensorflow",
    "pytorch",
    "keras",
    "scikit-learn",
    "opencv",
    "nlp",
    "computer vision",
    "pandas",
    "numpy",
    "matplotlib",
    "seaborn",

    # DevOps / Tools
    "git",
    "github",
    "docker",
    "kubernetes",
    "linux",
    "aws",
    "azure",
    "gcp",
    "vercel",
    "netlify",

    # Mobile / Cross-platform
    "react native",
    "flutter",

    # CS Fundamentals
    "dsa",
    "data structures",
    "algorithms",
    "oop",
    "dbms",
    "operating systems",
    "computer networks",
}

def extract_skills(text: str) -> list[str]:
    normalized = text.lower()

    found = []

    for skill in KNOWN_SKILLS:
        pattern = r"\b" + re.escape(skill) + r"\b"

        if re.search(pattern, normalized):
            found.append(skill)

    return sorted(set(found))