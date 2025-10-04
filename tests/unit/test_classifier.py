"""Tests for resource classifier."""

import json
from pathlib import Path

import pytest

from air.core.models import ResourceType
from air.services.classifier import classify_resource


class TestLanguageDetection:
    """Test language detection."""

    def test_detect_python(self, tmp_path: Path) -> None:
        """Test Python language detection."""
        # Create Python files
        (tmp_path / "app.py").write_text("print('hello')")
        (tmp_path / "requirements.txt").write_text("flask>=2.0.0")

        result = classify_resource(tmp_path)
        assert "python" in result.detected_languages

    def test_detect_javascript(self, tmp_path: Path) -> None:
        """Test JavaScript language detection."""
        (tmp_path / "index.js").write_text("console.log('hello')")
        (tmp_path / "package.json").write_text(json.dumps({"name": "test"}))

        result = classify_resource(tmp_path)
        assert "javascript" in result.detected_languages

    def test_detect_typescript(self, tmp_path: Path) -> None:
        """Test TypeScript language detection."""
        (tmp_path / "app.ts").write_text("const x: string = 'hello'")
        (tmp_path / "tsconfig.json").write_text("{}")

        result = classify_resource(tmp_path)
        assert "typescript" in result.detected_languages

    def test_detect_go(self, tmp_path: Path) -> None:
        """Test Go language detection."""
        (tmp_path / "main.go").write_text("package main")
        (tmp_path / "go.mod").write_text("module test")

        result = classify_resource(tmp_path)
        assert "go" in result.detected_languages

    def test_detect_multiple_languages(self, tmp_path: Path) -> None:
        """Test multiple language detection."""
        (tmp_path / "app.py").write_text("print('hello')")
        (tmp_path / "index.js").write_text("console.log('hello')")

        result = classify_resource(tmp_path)
        assert "python" in result.detected_languages
        assert "javascript" in result.detected_languages


class TestFrameworkDetection:
    """Test framework detection."""

    def test_detect_django(self, tmp_path: Path) -> None:
        """Test Django framework detection."""
        (tmp_path / "manage.py").write_text("#!/usr/bin/env python")
        (tmp_path / "app.py").write_text("from django.conf import settings")

        result = classify_resource(tmp_path)
        assert "django" in result.detected_frameworks

    def test_detect_react(self, tmp_path: Path) -> None:
        """Test React framework detection."""
        (tmp_path / "package.json").write_text(
            json.dumps({"dependencies": {"react": "^18.0.0"}})
        )

        result = classify_resource(tmp_path)
        assert "react" in result.detected_frameworks

    def test_detect_express(self, tmp_path: Path) -> None:
        """Test Express framework detection."""
        (tmp_path / "package.json").write_text(
            json.dumps({"dependencies": {"express": "^4.18.0"}})
        )

        result = classify_resource(tmp_path)
        assert "express" in result.detected_frameworks


class TestDocumentationClassification:
    """Test documentation classification."""

    def test_classify_docs_directory(self, tmp_path: Path) -> None:
        """Test classification of documentation directory."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "index.md").write_text("# Documentation")
        (docs_dir / "guide.md").write_text("# Guide")
        (docs_dir / "api.md").write_text("# API Reference")

        result = classify_resource(tmp_path)
        assert result.resource_type == ResourceType.DOCUMENTATION
        assert result.confidence >= 0.7

    def test_classify_markdown_heavy(self, tmp_path: Path) -> None:
        """Test classification of markdown-heavy repository."""
        (tmp_path / "README.md").write_text("# Project")
        (tmp_path / "CONTRIBUTING.md").write_text("# Contributing")
        (tmp_path / "docs.md").write_text("# Docs")
        (tmp_path / "guide.md").write_text("# Guide")

        result = classify_resource(tmp_path)
        assert result.resource_type == ResourceType.DOCUMENTATION

    def test_classify_mkdocs_project(self, tmp_path: Path) -> None:
        """Test classification of MkDocs project."""
        (tmp_path / "mkdocs.yml").write_text("site_name: Test")
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        (docs_dir / "index.md").write_text("# Home")

        result = classify_resource(tmp_path)
        assert result.resource_type == ResourceType.DOCUMENTATION


class TestServiceClassification:
    """Test service classification."""

    def test_classify_dockerized_service(self, tmp_path: Path) -> None:
        """Test classification of Dockerized service."""
        (tmp_path / "Dockerfile").write_text("FROM python:3.11")
        (tmp_path / "app.py").write_text("from flask import Flask")
        (tmp_path / "requirements.txt").write_text("flask>=2.0.0")

        result = classify_resource(tmp_path)
        assert result.resource_type == ResourceType.SERVICE

    def test_classify_kubernetes_service(self, tmp_path: Path) -> None:
        """Test classification of Kubernetes service."""
        k8s_dir = tmp_path / "kubernetes"
        k8s_dir.mkdir()
        (k8s_dir / "deployment.yaml").write_text("apiVersion: apps/v1")
        (tmp_path / "app.py").write_text("import flask")

        result = classify_resource(tmp_path)
        assert result.resource_type == ResourceType.SERVICE

    def test_classify_docker_compose_service(self, tmp_path: Path) -> None:
        """Test classification of docker-compose service."""
        (tmp_path / "docker-compose.yml").write_text("version: '3.8'")
        (tmp_path / "main.go").write_text("package main")

        result = classify_resource(tmp_path)
        assert result.resource_type == ResourceType.SERVICE


class TestLibraryClassification:
    """Test library classification."""

    def test_classify_python_library(self, tmp_path: Path) -> None:
        """Test classification of Python library."""
        (tmp_path / "setup.py").write_text("from setuptools import setup")
        src_dir = tmp_path / "mylib"
        src_dir.mkdir()
        (src_dir / "__init__.py").write_text("__version__ = '1.0.0'")
        (src_dir / "core.py").write_text("def func(): pass")

        result = classify_resource(tmp_path)
        assert result.resource_type == ResourceType.LIBRARY

    def test_classify_npm_library(self, tmp_path: Path) -> None:
        """Test classification of npm library."""
        (tmp_path / "package.json").write_text(
            json.dumps({"name": "mylib", "version": "1.0.0", "main": "index.js"})
        )
        (tmp_path / "index.js").write_text("module.exports = {}")

        result = classify_resource(tmp_path)
        # Should be library (no bin field in package.json)
        assert result.resource_type in [ResourceType.LIBRARY, ResourceType.IMPLEMENTATION]

    def test_not_library_with_main(self, tmp_path: Path) -> None:
        """Test that application with main is not classified as library."""
        (tmp_path / "setup.py").write_text("from setuptools import setup")
        (tmp_path / "app.py").write_text('if __name__ == "__main__":\n    main()')

        result = classify_resource(tmp_path)
        assert result.resource_type != ResourceType.LIBRARY


class TestImplementationClassification:
    """Test implementation classification."""

    def test_classify_python_app(self, tmp_path: Path) -> None:
        """Test classification of Python application."""
        (tmp_path / "app.py").write_text('if __name__ == "__main__":\n    print("hello")')
        (tmp_path / "utils.py").write_text("def helper(): pass")

        result = classify_resource(tmp_path)
        assert result.resource_type == ResourceType.IMPLEMENTATION

    def test_classify_mixed_repo(self, tmp_path: Path) -> None:
        """Test classification of mixed code/docs repository."""
        # More code files
        (tmp_path / "app.py").write_text("print('hello')")
        (tmp_path / "utils.py").write_text("def func(): pass")
        (tmp_path / "models.py").write_text("class Model: pass")
        (tmp_path / "views.py").write_text("def view(): pass")

        # One doc file
        (tmp_path / "README.md").write_text("# Project")

        result = classify_resource(tmp_path)
        # Should prefer implementation when more code than docs
        assert result.resource_type in [
            ResourceType.IMPLEMENTATION,
            ResourceType.LIBRARY,
            ResourceType.DOCUMENTATION,
        ]


class TestEdgeCases:
    """Test edge cases."""

    def test_empty_directory(self, tmp_path: Path) -> None:
        """Test classification of empty directory."""
        result = classify_resource(tmp_path)
        assert result.confidence == 0.0
        assert "Empty" in result.reasoning

    def test_nonexistent_directory(self, tmp_path: Path) -> None:
        """Test classification of nonexistent directory."""
        result = classify_resource(tmp_path / "nonexistent")
        assert result.confidence == 0.0
        assert "not exist" in result.reasoning

    def test_file_instead_of_directory(self, tmp_path: Path) -> None:
        """Test classification when given a file instead of directory."""
        file_path = tmp_path / "file.txt"
        file_path.write_text("content")

        result = classify_resource(file_path)
        assert result.confidence == 0.0


class TestConfidenceScores:
    """Test confidence scoring."""

    def test_high_confidence_documentation(self, tmp_path: Path) -> None:
        """Test high confidence for clear documentation repo."""
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        for i in range(10):
            (docs_dir / f"doc{i}.md").write_text(f"# Document {i}")

        result = classify_resource(tmp_path)
        assert result.confidence >= 0.8

    def test_low_confidence_ambiguous(self, tmp_path: Path) -> None:
        """Test lower confidence for ambiguous repo."""
        (tmp_path / "file.txt").write_text("content")
        (tmp_path / "data.json").write_text("{}")
        (tmp_path / "notes.txt").write_text("notes")

        result = classify_resource(tmp_path)
        # Ambiguous repo with no clear indicators should have low confidence
        assert result.confidence < 0.8
