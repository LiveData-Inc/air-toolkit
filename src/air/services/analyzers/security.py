"""Security analyzer - detects common security issues."""

import re
from pathlib import Path

from air.services.path_filter import should_exclude_path
from .base import AnalyzerResult, BaseAnalyzer, Finding, FindingSeverity


class SecurityAnalyzer(BaseAnalyzer):
    """Analyzes code for common security issues."""

    def __init__(self, repo_path: Path, include_external: bool = False):
        """Initialize security analyzer.

        Args:
            repo_path: Path to repository
            include_external: If True, include external/vendor code in analysis
        """
        super().__init__(repo_path)
        self.repo_path = repo_path
        self.include_external = include_external

    @property
    def name(self) -> str:
        """Get analyzer name."""
        return "security"

    # Security patterns to detect
    SECURITY_PATTERNS = {
        "hardcoded_secret": {
            "patterns": [
                r'(password|passwd|pwd|secret|api[_-]?key|token)\s*=\s*["\'][^"\']{8,}["\']',
                r'(aws_access_key_id|aws_secret_access_key)\s*=\s*["\'][^"\']+["\']',
                r'(bearer|authorization)\s*[:=]\s*["\'][^"\']{20,}["\']',
                r'(private[_-]?key|ssh[_-]?key)\s*=\s*["\'][^"\']+["\']',
            ],
            "severity": FindingSeverity.CRITICAL,
            "title": "Possible hardcoded secret",
            "description": "Detected potential hardcoded secret or API key",
            "suggestion": "Use environment variables or secure secret management",
        },
        "path_traversal": {
            "patterns": [
                r'open\([^)]*\+\s*[^)]+\)',
                r'\.\./',
                r'os\.path\.join\([^)]*user',
            ],
            "severity": FindingSeverity.HIGH,
            "title": "Potential path traversal",
            "description": "User input in file path operations can lead to path traversal",
            "suggestion": "Validate and sanitize file paths, use allowlist",
        },
        "command_injection": {
            "patterns": [
                r'os\.popen\(',
                r'commands\.getoutput\(',
                r'subprocess\.(Popen|call|run)\([^)]*shell\s*=\s*True',
            ],
            "severity": FindingSeverity.CRITICAL,
            "title": "Command injection risk",
            "description": "Executing shell commands with user input can lead to command injection",
            "suggestion": "Use subprocess with shell=False and pass arguments as list",
        },
        "xxe_vulnerability": {
            "patterns": [
                r'xml\.etree\.ElementTree\.parse\(',
                r'xml\.dom\.minidom\.parse',
                r'lxml\.etree\.parse\([^)]*resolve_entities\s*=\s*True',
            ],
            "severity": FindingSeverity.HIGH,
            "title": "XML External Entity (XXE) vulnerability",
            "description": "Parsing untrusted XML without disabling external entities",
            "suggestion": "Disable external entity processing in XML parsers",
        },
        "csrf_missing": {
            "patterns": [
                r'@app\.route\([^)]*methods\s*=\s*\[["\']POST',
                r'@api\.route\([^)]*methods\s*=\s*\[["\']POST',
            ],
            "severity": FindingSeverity.MEDIUM,
            "title": "Potential CSRF vulnerability",
            "description": "POST endpoint may lack CSRF protection",
            "suggestion": "Implement CSRF tokens for state-changing operations",
        },
        "sql_injection": {
            "patterns": [
                r'execute\(["\'].*%s.*["\']',
                r'cursor\.execute\([^)]*\+\s*[^)]+\)',
                r'f".*SELECT.*{.*}"',
            ],
            "severity": FindingSeverity.HIGH,
            "title": "Potential SQL injection",
            "description": "String concatenation in SQL query - vulnerable to injection",
            "suggestion": "Use parameterized queries or ORM",
        },
        "weak_crypto": {
            "patterns": [
                r'import\s+md5',
                r'hashlib\.md5\(',
                r'hashlib\.sha1\(',
                r'Crypto\.Cipher\.DES',
            ],
            "severity": FindingSeverity.HIGH,
            "title": "Weak cryptographic algorithm",
            "description": "Use of weak or deprecated cryptographic algorithm",
            "suggestion": "Use SHA-256 or stronger algorithms",
        },
        "eval_use": {
            "patterns": [
                r'\beval\(',
                r'\bexec\(',
            ],
            "severity": FindingSeverity.HIGH,
            "title": "Use of eval() or exec()",
            "description": "Dynamic code execution can be dangerous",
            "suggestion": "Avoid eval/exec or sanitize input rigorously",
        },
        "debug_mode": {
            "patterns": [
                r'DEBUG\s*=\s*True',
                r'debug\s*=\s*true',
                r'app\.debug\s*=\s*True',
            ],
            "severity": FindingSeverity.MEDIUM,
            "title": "Debug mode enabled",
            "description": "Debug mode should not be enabled in production",
            "suggestion": "Use environment-based configuration",
        },
        "insecure_deserialization": {
            "patterns": [
                r'pickle\.loads?\(',
                r'yaml\.load\([^,)]*\)',  # yaml.load without Loader
            ],
            "severity": FindingSeverity.HIGH,
            "title": "Insecure deserialization",
            "description": "Deserializing untrusted data can lead to code execution",
            "suggestion": "Use safe deserialization methods (yaml.safe_load, etc.)",
        },
        "shell_injection": {
            "patterns": [
                r'os\.system\(',
                r'subprocess\.call\([^)]*shell\s*=\s*True',
                r'subprocess\.run\([^)]*shell\s*=\s*True',
            ],
            "severity": FindingSeverity.HIGH,
            "title": "Potential shell injection",
            "description": "Shell command execution with shell=True can be dangerous",
            "suggestion": "Use shell=False and pass commands as lists",
        },
        "ldap_injection": {
            "patterns": [
                r'ldap\.(search|bind)\([^)]*\+\s*[^)]+\)',
            ],
            "severity": FindingSeverity.HIGH,
            "title": "Potential LDAP injection",
            "description": "LDAP query with string concatenation can be exploited",
            "suggestion": "Use parameterized LDAP queries",
        },
        "regex_dos": {
            "patterns": [
                r're\.compile\(["\'].*\(\.\*\)\+',
                r're\.match\(["\'].*\(\.\*\)\+',
            ],
            "severity": FindingSeverity.MEDIUM,
            "title": "Potential ReDoS vulnerability",
            "description": "Complex regex pattern may cause catastrophic backtracking",
            "suggestion": "Simplify regex patterns, add timeouts",
        },
        "unsafe_random": {
            "patterns": [
                r'random\.(random|randint|choice)',
            ],
            "severity": FindingSeverity.MEDIUM,
            "title": "Cryptographically weak random",
            "description": "Using random module for security-sensitive operations",
            "suggestion": "Use secrets module for cryptographic randomness",
        },
    }

    def analyze(self) -> AnalyzerResult:
        """Analyze code for security issues.

        Returns:
            AnalyzerResult with security findings
        """
        findings = []

        # Analyze Python files
        python_findings = self._analyze_python_files()
        findings.extend(python_findings)

        # Analyze JavaScript/TypeScript files
        js_findings = self._analyze_javascript_files()
        findings.extend(js_findings)

        # Check for exposed secrets in config files
        config_findings = self._check_config_files()
        findings.extend(config_findings)

        # Check for security headers (if web app)
        header_findings = self._check_security_headers()
        findings.extend(header_findings)

        # Create summary
        summary = {
            "total_findings": len(findings),
            "critical": sum(1 for f in findings if f.severity == FindingSeverity.CRITICAL),
            "high": sum(1 for f in findings if f.severity == FindingSeverity.HIGH),
            "medium": sum(1 for f in findings if f.severity == FindingSeverity.MEDIUM),
            "low": sum(1 for f in findings if f.severity == FindingSeverity.LOW),
        }

        return AnalyzerResult(
            analyzer_name=self.name,
            findings=findings[:50],  # Limit to top 50 findings
            summary=summary,
        )

    def _analyze_python_files(self) -> list[Finding]:
        """Analyze Python files for security issues."""
        findings = []

        for py_file in self._get_files_by_pattern("**/*.py"):
            # Use path_filter to exclude external code
            rel_path = py_file.relative_to(self.repo_path)
            if should_exclude_path(rel_path, self.include_external):
                continue

            content = self._read_file(py_file)
            if not content:
                continue

            findings.extend(self._scan_content_for_patterns(py_file, content))

        return findings

    def _analyze_javascript_files(self) -> list[Finding]:
        """Analyze JavaScript/TypeScript files."""
        findings = []

        for pattern in ["**/*.js", "**/*.jsx", "**/*.ts", "**/*.tsx"]:
            for js_file in self._get_files_by_pattern(pattern):
                # Use path_filter to exclude external code
                rel_path = js_file.relative_to(self.repo_path)
                if should_exclude_path(rel_path, self.include_external):
                    continue

                content = self._read_file(js_file)
                if not content:
                    continue

                # Check for hardcoded API keys
                if re.search(r'(apiKey|api_key|apiSecret)\s*[:=]\s*["\'][^"\']{10,}["\']', content, re.IGNORECASE):
                    findings.append(
                        Finding(
                            category="security",
                            severity=FindingSeverity.HIGH,
                            title="Potential hardcoded API key",
                            description="Found what appears to be a hardcoded API key",
                            location=str(js_file.relative_to(self.resource_path)),
                            suggestion="Use environment variables for API keys",
                        )
                    )

        return findings

    def _scan_content_for_patterns(self, file_path: Path, content: str) -> list[Finding]:
        """Scan content for security patterns.

        Args:
            file_path: File being scanned
            content: File content

        Returns:
            List of findings
        """
        findings = []

        for pattern_name, pattern_info in self.SECURITY_PATTERNS.items():
            for pattern in pattern_info["patterns"]:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Calculate line number
                    line_num = content[:match.start()].count("\n") + 1

                    findings.append(
                        Finding(
                            category="security",
                            severity=pattern_info["severity"],
                            title=pattern_info["title"],
                            description=pattern_info["description"],
                            location=str(file_path.relative_to(self.resource_path)),
                            line_number=line_num,
                            suggestion=pattern_info["suggestion"],
                            metadata={"pattern": pattern_name, "match": match.group(0)[:100]},
                        )
                    )

        return findings

    def _check_config_files(self) -> list[Finding]:
        """Check configuration files for exposed secrets."""
        findings = []

        config_patterns = ["**/.env", "**/.env.*", "**/config.json", "**/secrets.json"]

        for pattern in config_patterns:
            for config_file in self._get_files_by_pattern(pattern):
                # Check if .gitignore exists and includes this file
                gitignore = self.resource_path / ".gitignore"
                is_ignored = False

                if gitignore.exists():
                    gitignore_content = self._read_file(gitignore)
                    rel_path = config_file.relative_to(self.resource_path)
                    is_ignored = any(
                        str(rel_path).startswith(line.strip())
                        for line in gitignore_content.split("\n")
                        if line.strip() and not line.startswith("#")
                    )

                if not is_ignored:
                    findings.append(
                        Finding(
                            category="security",
                            severity=FindingSeverity.HIGH,
                            title="Config file not in .gitignore",
                            description=f"{config_file.name} may contain secrets but is not ignored",
                            location=str(config_file.relative_to(self.resource_path)),
                            suggestion="Add to .gitignore to prevent committing secrets",
                        )
                    )

        return findings

    def _check_security_headers(self) -> list[Finding]:
        """Check for security header configuration."""
        findings = []

        # Look for web framework files
        framework_files = []
        framework_files.extend(self._get_files_by_pattern("**/app.py"))
        framework_files.extend(self._get_files_by_pattern("**/main.py"))
        framework_files.extend(self._get_files_by_pattern("**/server.js"))
        framework_files.extend(self._get_files_by_pattern("**/server.ts"))

        for framework_file in framework_files:
            content = self._read_file(framework_file)

            # Check for missing security headers
            has_helmet = "helmet" in content.lower()
            has_cors = "cors" in content.lower()
            has_csp = "content-security-policy" in content.lower()

            if not (has_helmet or has_cors or has_csp):
                findings.append(
                    Finding(
                        category="security",
                        severity=FindingSeverity.MEDIUM,
                        title="Missing security headers",
                        description="Web application may lack security headers (CSP, CORS, etc.)",
                        location=str(framework_file.relative_to(self.resource_path)),
                        suggestion="Use helmet.js (Node) or equivalent security middleware",
                    )
                )

        return findings
