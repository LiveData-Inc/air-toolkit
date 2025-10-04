"""Resource classification service."""

from pathlib import Path
from typing import NamedTuple

from air.core.models import ResourceType


class ClassificationResult(NamedTuple):
    """Result of resource classification."""

    resource_type: ResourceType
    technology_stack: str | None  # e.g., "Python/FastAPI", "TypeScript/React"
    confidence: float  # 0.0 to 1.0
    detected_languages: list[str]
    detected_frameworks: list[str]
    reasoning: str


# File patterns for language detection
LANGUAGE_PATTERNS = {
    "python": ["*.py", "requirements.txt", "setup.py", "pyproject.toml", "Pipfile"],
    "javascript": ["*.js", "*.jsx", "package.json", "yarn.lock", "pnpm-lock.yaml"],
    "typescript": ["*.ts", "*.tsx", "tsconfig.json"],
    "go": ["*.go", "go.mod", "go.sum"],
    "rust": ["*.rs", "Cargo.toml", "Cargo.lock"],
    "java": ["*.java", "pom.xml", "build.gradle", "gradlew"],
    "ruby": ["*.rb", "Gemfile", "Rakefile"],
    "php": ["*.php", "composer.json"],
    "csharp": ["*.cs", "*.csproj", "*.sln"],
    "swift": ["*.swift", "Package.swift"],
    "kotlin": ["*.kt", "*.kts"],
}

# Framework detection patterns
FRAMEWORK_PATTERNS = {
    "django": ["manage.py", "django"],
    "flask": ["app.py", "flask"],
    "fastapi": ["fastapi", "uvicorn"],
    "react": ["react", "package.json"],
    "vue": ["vue", "package.json"],
    "angular": ["angular.json", "@angular"],
    "nextjs": ["next.config.js", "next"],
    "express": ["express", "package.json"],
    "rails": ["Gemfile", "rails"],
    "spring": ["spring-boot", "pom.xml"],
}

# Documentation indicators
DOCUMENTATION_PATTERNS = [
    "README.md",
    "docs/",
    "documentation/",
    "wiki/",
    "*.md",
    "mkdocs.yml",
    "sphinx/",
    "docusaurus/",
]

# Service/deployment indicators
SERVICE_PATTERNS = [
    "Dockerfile",
    "docker-compose.yml",
    "kubernetes/",
    "k8s/",
    ".github/workflows/",
    "Procfile",
    "serverless.yml",
    "terraform/",
]


def _generate_technology_stack(languages: list[str], frameworks: list[str]) -> str | None:
    """Generate technology stack string from detected languages and frameworks.

    Args:
        languages: Detected languages
        frameworks: Detected frameworks

    Returns:
        Technology stack string like "Python/FastAPI" or "TypeScript/React"
    """
    if not languages and not frameworks:
        return None

    # Prioritize the first detected language
    primary_lang = languages[0].capitalize() if languages else None

    # Find the most relevant framework
    primary_framework = frameworks[0].capitalize() if frameworks else None

    if primary_lang and primary_framework:
        return f"{primary_lang}/{primary_framework}"
    elif primary_lang:
        return primary_lang
    elif primary_framework:
        return primary_framework

    return None


def classify_resource(resource_path: Path) -> ClassificationResult:
    """Classify a resource by analyzing its structure.

    Args:
        resource_path: Path to the resource directory

    Returns:
        ClassificationResult with type, confidence, and metadata
    """
    if not resource_path.exists() or not resource_path.is_dir():
        return ClassificationResult(
            resource_type=ResourceType.LIBRARY,
            technology_stack=None,
            confidence=0.0,
            detected_languages=[],
            detected_frameworks=[],
            reasoning="Path does not exist or is not a directory",
        )

    # Detect languages
    languages = _detect_languages(resource_path)

    # Detect frameworks
    frameworks = _detect_frameworks(resource_path)

    # Count file types
    doc_score = _count_documentation_files(resource_path)
    code_score = _count_code_files(resource_path, languages)
    service_score = _count_service_files(resource_path)

    # Classify based on scores
    total_score = doc_score + code_score + service_score
    if total_score == 0:
        tech_stack = _generate_technology_stack(languages, frameworks)
        return ClassificationResult(
            resource_type=ResourceType.LIBRARY,
            technology_stack=tech_stack,
            confidence=0.0,
            detected_languages=languages,
            detected_frameworks=frameworks,
            reasoning="Empty or unrecognizable repository",
        )

    doc_ratio = doc_score / total_score
    service_ratio = service_score / total_score
    code_ratio = code_score / total_score

    # Determine resource type
    tech_stack = _generate_technology_stack(languages, frameworks)

    if doc_ratio > 0.7:
        # Documentation-heavy (e.g., Markdown/MkDocs)
        doc_stack = "Markdown" if not tech_stack else tech_stack
        return ClassificationResult(
            resource_type=ResourceType.DOCUMENTATION,
            technology_stack=doc_stack,
            confidence=min(doc_ratio, 0.95),
            detected_languages=languages,
            detected_frameworks=frameworks,
            reasoning=f"High documentation content ({doc_ratio:.0%})",
        )
    elif service_ratio > 0.3 and code_score > 0:
        # Has deployment configs and code
        return ClassificationResult(
            resource_type=ResourceType.SERVICE,
            technology_stack=tech_stack,
            confidence=min(service_ratio + 0.4, 0.95),
            detected_languages=languages,
            detected_frameworks=frameworks,
            reasoning=f"Deployable service with {tech_stack or 'unknown stack'}",
        )
    else:
        # Default to library (any code repository)
        confidence = 0.8 if _is_library(resource_path, languages) else 0.6
        reasoning = (
            "Library/package structure"
            if _is_library(resource_path, languages)
            else f"Code repository ({tech_stack or 'unknown stack'})"
        )
        return ClassificationResult(
            resource_type=ResourceType.LIBRARY,
            technology_stack=tech_stack,
            confidence=confidence,
            detected_languages=languages,
            detected_frameworks=frameworks,
            reasoning=reasoning,
        )


def _detect_languages(path: Path) -> list[str]:
    """Detect programming languages in repository.

    Args:
        path: Repository path

    Returns:
        List of detected language names
    """
    detected = []
    for lang, patterns in LANGUAGE_PATTERNS.items():
        for pattern in patterns:
            if pattern.startswith("*."):
                # Extension pattern
                if list(path.rglob(pattern)):
                    detected.append(lang)
                    break
            else:
                # File name pattern
                if (path / pattern).exists() or list(path.rglob(pattern)):
                    detected.append(lang)
                    break
    return detected


def _detect_frameworks(path: Path) -> list[str]:
    """Detect frameworks in repository.

    Args:
        path: Repository path

    Returns:
        List of detected framework names
    """
    detected = []
    for framework, patterns in FRAMEWORK_PATTERNS.items():
        for pattern in patterns:
            # Check if file exists
            if (path / pattern).exists():
                detected.append(framework)
                break
            # Check in package files
            if pattern in ["package.json", "requirements.txt", "Gemfile", "pom.xml"]:
                file_path = path / pattern
                if file_path.exists():
                    try:
                        content = file_path.read_text()
                        if framework in content.lower():
                            detected.append(framework)
                            break
                    except Exception:
                        pass
    return detected


def _count_documentation_files(path: Path) -> int:
    """Count documentation-related files.

    Args:
        path: Repository path

    Returns:
        Documentation file count (weighted)
    """
    score = 0
    for pattern in DOCUMENTATION_PATTERNS:
        if pattern.endswith("/"):
            # Directory
            if (path / pattern.rstrip("/")).is_dir():
                score += 20  # Dedicated docs directory is strong signal
        elif "*" in pattern:
            # Glob pattern
            matches = list(path.rglob(pattern))
            score += len(matches)
        else:
            # Specific file
            if (path / pattern).exists():
                score += 5

    return score


def _count_code_files(path: Path, languages: list[str]) -> int:
    """Count code files.

    Args:
        path: Repository path
        languages: Detected languages

    Returns:
        Code file count
    """
    score = 0
    for lang in languages:
        patterns = LANGUAGE_PATTERNS.get(lang, [])
        for pattern in patterns:
            if pattern.startswith("*."):
                matches = list(path.rglob(pattern))
                score += len(matches)
    return score


def _count_service_files(path: Path) -> int:
    """Count service/deployment files.

    Args:
        path: Repository path

    Returns:
        Service file count (weighted)
    """
    score = 0
    for pattern in SERVICE_PATTERNS:
        if pattern.endswith("/"):
            # Directory
            if (path / pattern.rstrip("/")).is_dir():
                score += 15
        else:
            # File
            if (path / pattern).exists():
                score += 10
    return score


def _is_library(path: Path, languages: list[str]) -> bool:
    """Check if repository is a library/package.

    Args:
        path: Repository path
        languages: Detected languages

    Returns:
        True if appears to be a library
    """
    # Check for package indicators
    library_indicators = [
        "setup.py",
        "pyproject.toml",
        "package.json",
        "Cargo.toml",
        "go.mod",
        "pom.xml",
    ]

    has_package_file = any((path / indicator).exists() for indicator in library_indicators)
    if not has_package_file:
        return False

    # Check for absence of executable entry points
    no_main = True

    # Python: no if __name__ == "__main__" in top-level files
    if "python" in languages:
        for py_file in path.glob("*.py"):
            try:
                content = py_file.read_text()
                if '__name__ == "__main__"' in content or "__name__ == '__main__'" in content:
                    no_main = False
                    break
            except Exception:
                pass

    # JavaScript/TypeScript: check if package.json has "bin" field
    if "javascript" in languages or "typescript" in languages:
        package_json = path / "package.json"
        if package_json.exists():
            try:
                import json

                data = json.loads(package_json.read_text())
                if "bin" in data:
                    no_main = False
            except Exception:
                pass

    return has_package_file and no_main
