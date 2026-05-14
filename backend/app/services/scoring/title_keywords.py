"""
Predefined keyword mappings for common job roles.

Structure per role:
    "canonical_title": {
        "aliases":      list[str]  – alternate titles that map to this role
        "skills":       list[str]  – hard skills and tools
        "technologies": list[str]  – frameworks, languages, platforms
        "concepts":     list[str]  – domain concepts, methodologies
    }

Matching against job_title is done externally (keyword_matcher.py).
This file is pure data — no functions, no imports.
"""

ROLE_KEYWORDS: dict[str, dict[str, list[str]]] = {
    "frontend developer": {
        "aliases": [
            "frontend engineer",
            "front end developer",
            "front-end developer",
            "front end engineer",
            "front-end engineer",
            "ui developer",
            "ui engineer",
            "react developer",
            "vue developer",
            "angular developer",
        ],
        "skills": [
            "html", "css", "javascript", "typescript", "responsive design",
            "accessibility", "cross-browser compatibility", "performance optimization",
            "ui design", "ux", "web vitals",
        ],
        "technologies": [
            "react", "vue", "angular", "next.js", "nuxt", "vite", "webpack",
            "tailwind", "sass", "scss", "bootstrap", "figma", "storybook",
            "jest", "cypress", "playwright", "eslint", "prettier",
        ],
        "concepts": [
            "component architecture", "state management", "virtual dom",
            "spa", "ssr", "ssg", "progressive web app", "pwa",
            "rest api", "graphql", "websockets", "ci/cd",
        ],
    },

    "backend developer": {
        "aliases": [
            "backend engineer",
            "back end developer",
            "back-end developer",
            "back end engineer",
            "back-end engineer",
            "server side developer",
            "api developer",
            "software engineer",
            "software developer",
        ],
        "skills": [
            "api design", "rest", "restful", "microservices", "authentication",
            "authorization", "database design", "caching", "message queues",
            "concurrency", "security", "performance tuning",
        ],
        "technologies": [
            "python", "fastapi", "django", "flask", "node.js", "express",
            "java", "spring boot", "go", "rust", "postgresql", "mysql",
            "mongodb", "redis", "docker", "kubernetes", "aws", "gcp", "azure",
            "sqlalchemy", "celery", "rabbitmq", "kafka", "nginx",
        ],
        "concepts": [
            "orm", "sql", "nosql", "acid", "transactions", "indexing",
            "load balancing", "horizontal scaling", "vertical scaling",
            "ci/cd", "unit testing", "integration testing", "tdd",
        ],
    },

    "full stack developer": {
        "aliases": [
            "full stack engineer",
            "fullstack developer",
            "fullstack engineer",
            "full-stack developer",
            "full-stack engineer",
            "software engineer",
            "web developer",
        ],
        "skills": [
            "html", "css", "javascript", "typescript", "api design",
            "database design", "authentication", "deployment", "testing",
            "version control", "agile", "problem solving",
        ],
        "technologies": [
            "react", "vue", "angular", "node.js", "python", "fastapi",
            "django", "flask", "postgresql", "mongodb", "mysql", "redis",
            "docker", "aws", "git", "github", "tailwind", "next.js",
        ],
        "concepts": [
            "mvc", "rest api", "graphql", "microservices", "spa", "ssr",
            "ci/cd", "devops", "agile", "scrum", "unit testing", "tdd",
        ],
    },

    "data analyst": {
        "aliases": [
            "data analytics",
            "business analyst",
            "business intelligence analyst",
            "bi analyst",
            "reporting analyst",
            "analytics engineer",
        ],
        "skills": [
            "data analysis", "statistical analysis", "data visualization",
            "data cleaning", "data wrangling", "reporting", "dashboards",
            "a/b testing", "hypothesis testing", "excel", "spreadsheets",
        ],
        "technologies": [
            "python", "sql", "pandas", "numpy", "matplotlib", "seaborn",
            "tableau", "power bi", "looker", "r", "jupyter", "google analytics",
            "bigquery", "snowflake", "dbt", "airflow",
        ],
        "concepts": [
            "etl", "data pipeline", "kpi", "metrics", "cohort analysis",
            "funnel analysis", "regression", "correlation", "forecasting",
            "data warehousing", "olap", "business intelligence",
        ],
    },

    "machine learning engineer": {
        "aliases": [
            "ml engineer",
            "ai engineer",
            "deep learning engineer",
            "nlp engineer",
            "computer vision engineer",
            "research engineer",
            "applied scientist",
            "data scientist",
        ],
        "skills": [
            "machine learning", "deep learning", "model training", "model deployment",
            "feature engineering", "hyperparameter tuning", "model evaluation",
            "data preprocessing", "statistical modeling", "research",
        ],
        "technologies": [
            "python", "tensorflow", "pytorch", "keras", "scikit-learn",
            "hugging face", "transformers", "numpy", "pandas", "opencv",
            "mlflow", "kubeflow", "docker", "aws sagemaker", "gcp vertex ai",
            "fastapi", "flask", "spark", "hadoop",
        ],
        "concepts": [
            "supervised learning", "unsupervised learning", "reinforcement learning",
            "neural networks", "cnn", "rnn", "lstm", "transformer", "nlp",
            "computer vision", "transfer learning", "fine-tuning",
            "bias-variance tradeoff", "cross-validation", "overfitting",
            "mlops", "model monitoring", "a/b testing", "embeddings",
        ],
    },

    "devops engineer": {
        "aliases": [
            "devops",
            "platform engineer",
            "site reliability engineer",
            "sre",
            "infrastructure engineer",
            "cloud engineer",
        ],
        "skills": [
            "ci/cd", "infrastructure as code", "automation", "monitoring",
            "incident management", "capacity planning", "security hardening",
            "cost optimization", "on-call",
        ],
        "technologies": [
            "docker", "kubernetes", "terraform", "ansible", "jenkins",
            "github actions", "gitlab ci", "aws", "gcp", "azure",
            "linux", "bash", "python", "prometheus", "grafana",
            "elk stack", "nginx", "helm", "argocd",
        ],
        "concepts": [
            "devsecops", "gitops", "microservices", "service mesh",
            "high availability", "disaster recovery", "sla", "slo",
            "observability", "tracing", "logging", "alerting",
        ],
    },

    "android developer": {
        "aliases": [
            "android engineer",
            "mobile developer",
            "mobile engineer",
        ],
        "skills": [
            "android development", "mobile ui", "performance optimization",
            "debugging", "testing", "publishing", "accessibility",
        ],
        "technologies": [
            "kotlin", "java", "android studio", "jetpack compose",
            "room", "retrofit", "coroutines", "hilt", "dagger",
            "firebase", "gradle", "mvvm", "livedata", "viewmodel",
        ],
        "concepts": [
            "activity lifecycle", "fragments", "intents", "services",
            "broadcast receivers", "content providers", "material design",
            "rest api", "background tasks", "push notifications",
        ],
    },

    "ios developer": {
        "aliases": [
            "ios engineer",
            "swift developer",
            "apple developer",
        ],
        "skills": [
            "ios development", "mobile ui", "app store publishing",
            "debugging", "testing", "accessibility", "performance",
        ],
        "technologies": [
            "swift", "objective-c", "xcode", "swiftui", "uikit",
            "core data", "combine", "alamofire", "cocoapods", "spm",
            "firebase", "realm", "mvvm", "coordinator pattern",
        ],
        "concepts": [
            "app lifecycle", "view controller", "auto layout", "delegates",
            "protocols", "closures", "arc", "concurrency", "grand central dispatch",
            "rest api", "push notifications", "keychain",
        ],
    },
}