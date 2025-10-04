# AIR MCP Server Architecture

**Version:** 0.6.0 (Future)
**Status:** Design Document
**Last Updated:** 2025-10-04

## Overview

This document describes the architecture for AIR's Model Context Protocol (MCP) server implementation, enabling Claude Code and other AI assistants to use AIR as native tooling rather than shell commands.

## What is MCP?

The **Model Context Protocol (MCP)** is an open standard that allows AI applications to integrate with external tools and data sources. MCP enables:

- **Tools**: Functions the AI can call (like `air_status`, `air_task_create`)
- **Resources**: Data the AI can access (like task files, project config)
- **Prompts**: Predefined prompts the AI can use
- **Context Providers**: Dynamic context injection

## Why MCP for AIR?

### Current State (Shell Commands)

```bash
# Claude Code invokes shell commands
air status --format=json
air review --pr
air task new "implement feature"
```

**Limitations:**
- Must parse text output
- No type safety
- Error handling via exit codes
- No structured metadata
- Shell overhead

### Future State (MCP Server)

```python
# Claude Code calls native tools
result = await air__status()
# Returns typed object: AirStatus

review = await air__review(pr=true, base="main")
# Returns typed object: ReviewResult

task_path = await air__task_create(description="implement feature")
# Returns: Path
```

**Benefits:**
- Type-safe interfaces
- Rich error objects
- No parsing required
- Better performance
- Native IDE integration
- Works with any MCP client

## Architecture

### High-Level Design

```
┌─────────────────────────────────────────────┐
│  Claude Code (MCP Client)                   │
│  - Knows about air__* tools                 │
│  - Can call tools directly                  │
│  - Receives structured responses            │
└────────────────┬────────────────────────────┘
                 │
                 │ MCP Protocol (stdio/HTTP)
                 │
┌────────────────┴────────────────────────────┐
│  AIR MCP Server                             │
│  ├── Tool Registry                          │
│  ├── Resource Providers                     │
│  ├── Context Providers                      │
│  └── Prompt Templates                       │
└────────────────┬────────────────────────────┘
                 │
                 │ Internal calls
                 │
┌────────────────┴────────────────────────────┐
│  AIR Core Library                           │
│  ├── Commands (init, link, review, etc)    │
│  ├── Services (filesystem, git, etc)       │
│  └── Models (AirConfig, Resource, etc)     │
└─────────────────────────────────────────────┘
```

### MCP Server Components

#### 1. Server Implementation

```python
# air/mcp/server.py

from mcp.server import Server
from mcp.types import Tool, Resource, Prompt
from air.core.models import AirConfig, Resource as AirResource
from air.commands import status, review, task, link

# Create server instance
server = Server("air-toolkit")

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available AIR tools."""
    return [
        Tool(
            name="air__status",
            description="Get AIR project status including resources, tasks, and health",
            inputSchema={
                "type": "object",
                "properties": {
                    "include_resources": {"type": "boolean", "default": True},
                    "include_tasks": {"type": "boolean", "default": True},
                    "project_path": {"type": "string", "description": "Path to AIR project"}
                }
            }
        ),
        Tool(
            name="air__review",
            description="Generate code review context for changes",
            inputSchema={
                "type": "object",
                "properties": {
                    "pr": {"type": "boolean", "description": "Review current PR branch"},
                    "base": {"type": "string", "description": "Base branch to compare against"},
                    "files": {"type": "array", "items": {"type": "string"}},
                    "focus": {"type": "string", "enum": ["security", "performance", "architecture"]}
                }
            }
        ),
        Tool(
            name="air__task_create",
            description="Create a new AIR task file",
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {"type": "string", "description": "Task description"},
                    "prompt": {"type": "string", "description": "User's original prompt"},
                    "template": {"type": "string", "description": "Task template to use"}
                },
                "required": ["description"]
            }
        ),
        Tool(
            name="air__task_update",
            description="Update an existing task file with new action",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_file": {"type": "string", "description": "Path to task file"},
                    "action": {"type": "string", "description": "Action taken"}
                },
                "required": ["task_file", "action"]
            }
        ),
        Tool(
            name="air__task_complete",
            description="Mark a task as completed",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_file": {"type": "string"},
                    "status": {"type": "string", "enum": ["success", "partial", "blocked"]},
                    "notes": {"type": "string"}
                },
                "required": ["task_file", "status"]
            }
        ),
        Tool(
            name="air__link_add",
            description="Link a repository to the AIR project",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to repository"},
                    "name": {"type": "string", "description": "Resource name"},
                    "relationship": {"type": "string", "enum": ["review", "developer"]},
                    "resource_type": {"type": "string", "enum": ["library", "documentation", "service"]}
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="air__classify",
            description="Classify linked resources (detect tech stack)",
            inputSchema={
                "type": "object",
                "properties": {
                    "resource_name": {"type": "string", "description": "Specific resource to classify"},
                    "update_config": {"type": "boolean", "description": "Update air-config.json"}
                }
            }
        ),
        Tool(
            name="air__validate",
            description="Validate AIR project structure",
            inputSchema={
                "type": "object",
                "properties": {
                    "check_type": {"type": "string", "enum": ["all", "structure", "links"]},
                    "fix": {"type": "boolean", "description": "Auto-fix issues"}
                }
            }
        ),
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> dict:
    """Execute AIR tool and return result."""

    if name == "air__status":
        from air.commands.status import get_status

        result = await get_status(
            include_resources=arguments.get("include_resources", True),
            include_tasks=arguments.get("include_tasks", True),
            project_path=arguments.get("project_path")
        )

        return {
            "content": [
                {
                    "type": "text",
                    "text": f"AIR Project: {result.name}\nMode: {result.mode}\nResources: {result.resource_count}"
                },
                {
                    "type": "resource",
                    "resource": {
                        "uri": f"air://status/{result.name}",
                        "mimeType": "application/json",
                        "data": result.model_dump_json()
                    }
                }
            ]
        }

    elif name == "air__review":
        from air.commands.review import generate_review_context

        result = await generate_review_context(
            pr=arguments.get("pr", False),
            base=arguments.get("base", "main"),
            files=arguments.get("files", []),
            focus=arguments.get("focus")
        )

        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Review context generated for {len(result.files_changed)} files"
                },
                {
                    "type": "resource",
                    "resource": {
                        "uri": f"air://review/{result.review_id}",
                        "mimeType": "application/json",
                        "data": result.model_dump_json()
                    }
                }
            ]
        }

    elif name == "air__task_create":
        from air.commands.task import create_task_file

        task_path = await create_task_file(
            description=arguments["description"],
            prompt=arguments.get("prompt"),
            template=arguments.get("template")
        )

        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Task created: {task_path}"
                },
                {
                    "type": "resource",
                    "resource": {
                        "uri": f"file://{task_path}",
                        "mimeType": "text/markdown"
                    }
                }
            ]
        }

    # ... other tools

    else:
        raise ValueError(f"Unknown tool: {name}")

@server.list_resources()
async def list_resources() -> list[Resource]:
    """List available AIR resources."""
    from air.services.filesystem import get_project_root

    project_root = get_project_root()
    if not project_root:
        return []

    resources = [
        Resource(
            uri="air://config",
            name="AIR Configuration",
            mimeType="application/json",
            description="Current AIR project configuration"
        ),
        Resource(
            uri="air://tasks/recent",
            name="Recent Tasks",
            mimeType="application/json",
            description="Last 10 task files"
        ),
        Resource(
            uri="air://resources/all",
            name="Linked Resources",
            mimeType="application/json",
            description="All linked repositories"
        ),
    ]

    return resources

@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read AIR resource by URI."""

    if uri == "air://config":
        from air.services.filesystem import get_project_root
        config_path = get_project_root() / "air-config.json"
        return config_path.read_text()

    elif uri == "air://tasks/recent":
        from air.commands.task import get_recent_tasks
        tasks = get_recent_tasks(limit=10)
        return json.dumps([t.model_dump() for t in tasks], indent=2)

    elif uri == "air://resources/all":
        from air.core.models import load_config
        config = load_config()
        resources = config.get_all_resources()
        return json.dumps([r.model_dump() for r in resources], indent=2)

    else:
        raise ValueError(f"Unknown resource URI: {uri}")

@server.list_prompts()
async def list_prompts() -> list[Prompt]:
    """List available prompt templates."""
    return [
        Prompt(
            name="air-review",
            description="Review code changes using AIR context",
            arguments=[
                {"name": "focus", "description": "Review focus area", "required": False}
            ]
        ),
        Prompt(
            name="air-analyze-repos",
            description="Analyze all linked repositories",
            arguments=[]
        ),
    ]

@server.get_prompt()
async def get_prompt(name: str, arguments: dict) -> str:
    """Get prompt template."""

    if name == "air-review":
        focus = arguments.get("focus", "general")
        return f"""
Review the code changes with focus on {focus}.

Use the air__review tool to get context, then analyze:
- Code quality and best practices
- Security concerns
- Performance implications
- Consistency with project patterns
- Test coverage

Compare against patterns in linked resources.
Generate a structured review with issues categorized by severity.
"""

    elif name == "air-analyze-repos":
        return """
Analyze all repositories linked to this AIR project.

1. Use air__status to get list of linked resources
2. For each resource, use air__classify to ensure tech stack is known
3. Compare patterns across repositories:
   - Code duplication
   - Inconsistent approaches
   - Security practices
   - Architecture patterns

Generate analysis/reviews/{date}-cross-repo-analysis.md
"""

    else:
        raise ValueError(f"Unknown prompt: {name}")
```

#### 2. Server Launcher

```python
# air/mcp/__main__.py

import asyncio
import sys
from mcp.server import stdio_server
from air.mcp.server import server

async def main():
    """Run AIR MCP server on stdio."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

#### 3. Client Configuration

**Claude Desktop Configuration:**

```json
// ~/Library/Application Support/Claude/claude_desktop_config.json

{
  "mcpServers": {
    "air-toolkit": {
      "command": "python",
      "args": ["-m", "air.mcp"],
      "env": {
        "AIR_PROJECT_ROOT": "${workspaceFolder}"
      }
    }
  }
}
```

**VS Code Configuration:**

```json
// .vscode/settings.json

{
  "claude.mcpServers": [
    {
      "name": "air-toolkit",
      "command": "python",
      "args": ["-m", "air.mcp"],
      "enabled": true
    }
  ]
}
```

## Tool Specifications

### Core Tools

#### `air__status`

**Purpose:** Get comprehensive AIR project status.

**Input:**
```typescript
{
  include_resources?: boolean;  // default: true
  include_tasks?: boolean;      // default: true
  project_path?: string;        // default: current directory
}
```

**Output:**
```typescript
{
  name: string;
  mode: "review" | "develop" | "mixed";
  created: string;              // ISO 8601
  resource_count: number;
  resources: {
    review: Resource[];
    develop: Resource[];
  };
  recent_tasks: TaskFile[];
  health: {
    broken_links: number;
    missing_resources: number;
    validation_errors: string[];
  };
}
```

#### `air__review`

**Purpose:** Generate code review context.

**Input:**
```typescript
{
  pr?: boolean;                 // Review current PR branch
  base?: string;                // Base branch (default: "main")
  files?: string[];             // Specific files to review
  focus?: "security" | "performance" | "architecture";
}
```

**Output:**
```typescript
{
  review_id: string;
  timestamp: string;
  changes: {
    files_changed: number;
    insertions: number;
    deletions: number;
    files: FileChange[];
  };
  context: {
    project: ProjectContext;
    related_resources: RelatedResource[];
    recent_tasks: TaskFile[];
    standards: Record<string, string>;
  };
}
```

#### `air__task_create`

**Purpose:** Create new task file.

**Input:**
```typescript
{
  description: string;          // Required
  prompt?: string;              // User's original prompt
  template?: string;            // Template name
}
```

**Output:**
```typescript
{
  task_file: string;            // Path to created task file
  timestamp: string;
}
```

#### `air__task_update`

**Purpose:** Update existing task with new action.

**Input:**
```typescript
{
  task_file: string;            // Path to task file
  action: string;               // Action description
}
```

**Output:**
```typescript
{
  success: boolean;
  task_file: string;
}
```

#### `air__task_complete`

**Purpose:** Mark task as completed.

**Input:**
```typescript
{
  task_file: string;
  status: "success" | "partial" | "blocked";
  notes?: string;
}
```

**Output:**
```typescript
{
  success: boolean;
  task_file: string;
  final_status: string;
}
```

### Resource Management Tools

#### `air__link_add`

**Purpose:** Link repository to AIR project.

**Input:**
```typescript
{
  path: string;                 // Required
  name?: string;                // Resource name (default: folder name)
  relationship?: "review" | "developer";  // default: "review"
  resource_type?: "library" | "documentation" | "service";
}
```

**Output:**
```typescript
{
  success: boolean;
  resource: {
    name: string;
    path: string;
    type: string;
    relationship: string;
  };
}
```

#### `air__classify`

**Purpose:** Auto-classify linked resources.

**Input:**
```typescript
{
  resource_name?: string;       // Specific resource (optional)
  update_config?: boolean;      // Update air-config.json
}
```

**Output:**
```typescript
{
  classifications: {
    resource_name: string;
    type: "library" | "documentation" | "service";
    technology_stack: string;   // e.g., "Python/FastAPI"
    confidence: number;
  }[];
}
```

#### `air__validate`

**Purpose:** Validate project structure.

**Input:**
```typescript
{
  check_type?: "all" | "structure" | "links";
  fix?: boolean;                // Auto-fix issues
}
```

**Output:**
```typescript
{
  valid: boolean;
  errors: ValidationError[];
  warnings: string[];
  fixed: string[];              // If fix=true
}
```

## Resource Providers

### Available Resources

#### `air://config`

Current AIR project configuration (air-config.json).

```json
{
  "uri": "air://config",
  "mimeType": "application/json",
  "data": { /* AirConfig */ }
}
```

#### `air://tasks/recent`

Last N task files.

```json
{
  "uri": "air://tasks/recent",
  "mimeType": "application/json",
  "data": [
    {
      "file": ".air/tasks/20251004-0830-feature.md",
      "description": "Add feature",
      "status": "in-progress",
      "created": "2025-10-04T08:30:00-04:00"
    }
  ]
}
```

#### `air://resources/all`

All linked resources.

```json
{
  "uri": "air://resources/all",
  "mimeType": "application/json",
  "data": [
    {
      "name": "service-a",
      "path": "/Users/dev/repos/service-a",
      "type": "library",
      "technology_stack": "Python/FastAPI"
    }
  ]
}
```

## Context Providers

### Automatic Context Injection

The MCP server can inject context into Claude's prompts automatically.

```python
@server.context_provider("air-project")
async def provide_project_context():
    """Inject AIR project context into prompts."""

    config = load_air_config()
    recent_tasks = get_recent_tasks(limit=5)

    context = f"""
# AIR Project Context

**Project:** {config.name}
**Mode:** {config.mode}
**Resources:** {len(config.get_all_resources())}

## Recent Work
{format_tasks(recent_tasks)}

## Coding Standards
- Security: .air/context/security.md
- Python: .air/context/python-standards.md
"""

    return context
```

## Integration Examples

### Example 1: Review Workflow

**Claude Code automatically uses MCP tools:**

```
User: "Review my changes"

Claude (internal):
  1. Call air__status() to get project context
  2. Call air__review(pr=true) to get review context
  3. Analyze changes
  4. Generate review

Claude (to user):
  "I've reviewed your 3 changed files. Found 2 warnings:

   1. Password hashing issue in auth.py
   2. Missing rate limiting

   Both issues are inconsistent with patterns in service-a..."
```

**No shell commands needed!**

### Example 2: Task Tracking

```
User: "Add dark mode toggle"

Claude (internal):
  1. Call air__task_create(description="add dark mode toggle")
  2. As work progresses:
     - air__task_update(task_file, "Created DarkModeToggle component")
     - air__task_update(task_file, "Updated theme configuration")
  3. When complete:
     - air__task_complete(task_file, status="success")

Claude (to user):
  "Dark mode toggle implemented! Task documented in
   .air/tasks/20251004-0945-add-dark-mode-toggle.md"
```

### Example 3: Multi-Repo Analysis

```
User: "/air-analyze-repos"

Claude (internal):
  1. Call air__status() to get linked resources
  2. For each resource:
     - Call air__classify(resource_name)
  3. Analyze patterns across repos
  4. Generate report

Claude (to user):
  "Analyzed 3 repositories:

   Code Duplication:
   - Email validation in service-a and service-b

   Inconsistencies:
   - service-a uses custom exceptions
   - service-b uses HTTP exceptions

   Recommendations:
   - Extract email validation to shared library
   - Standardize error handling..."
```

## Performance Considerations

### 1. Caching

```python
# Cache frequently accessed data
from functools import lru_cache

@lru_cache(maxsize=128)
def get_air_config(project_root: Path) -> AirConfig:
    """Cached config loading."""
    return load_config(project_root)

# Invalidate cache on config updates
def save_air_config(config: AirConfig):
    """Save and invalidate cache."""
    save_config(config)
    get_air_config.cache_clear()
```

### 2. Async Operations

```python
# Use async for I/O-bound operations
async def get_review_context(pr: bool, base: str):
    """Async review context gathering."""

    # Run git operations concurrently
    diff_task = asyncio.create_task(get_git_diff(pr, base))
    context_task = asyncio.create_task(get_air_context())
    tasks_task = asyncio.create_task(get_recent_tasks())

    diff, context, tasks = await asyncio.gather(
        diff_task, context_task, tasks_task
    )

    return ReviewContext(diff, context, tasks)
```

### 3. Lazy Loading

```python
# Only load data when requested
class ResourceProvider:
    def __init__(self, resource_path: Path):
        self.path = resource_path
        self._metrics = None
        self._patterns = None

    async def get_metrics(self):
        """Lazy load metrics."""
        if self._metrics is None:
            self._metrics = await compute_metrics(self.path)
        return self._metrics
```

## Security Considerations

### 1. Path Validation

```python
def validate_path(path: Path, project_root: Path):
    """Ensure path is within project bounds."""

    resolved = path.resolve()

    # Prevent directory traversal
    if not resolved.is_relative_to(project_root):
        raise SecurityError(f"Path outside project: {path}")

    return resolved
```

### 2. Command Injection Prevention

```python
# Never use shell=True
import subprocess

# Good
subprocess.run(["git", "status"], capture_output=True)

# Bad
subprocess.run("git status", shell=True)  # Vulnerable
```

### 3. API Key Management

```python
# Never expose API keys via MCP
@server.call_tool()
async def call_tool(name: str, arguments: dict):
    # Tools should NOT accept API keys as arguments
    # Use environment variables or config files
    api_key = os.environ.get("ANTHROPIC_API_KEY")
```

## Testing

### Unit Tests

```python
# tests/mcp/test_server.py

import pytest
from air.mcp.server import server

@pytest.mark.asyncio
async def test_air_status_tool():
    """Test air__status tool."""

    # Setup test project
    project = create_test_project()

    # Call tool
    result = await server.call_tool(
        "air__status",
        {"include_resources": True}
    )

    # Verify response
    assert result["content"][0]["type"] == "text"
    assert "AIR Project" in result["content"][0]["text"]

@pytest.mark.asyncio
async def test_task_create_tool():
    """Test air__task_create tool."""

    result = await server.call_tool(
        "air__task_create",
        {"description": "test task"}
    )

    task_path = Path(result["content"][0]["text"].split(": ")[1])
    assert task_path.exists()
    assert task_path.name.endswith("-test-task.md")
```

### Integration Tests

```python
# tests/mcp/test_integration.py

@pytest.mark.asyncio
async def test_review_workflow():
    """Test complete review workflow via MCP."""

    # Create test repo with changes
    repo = create_test_repo()
    make_changes(repo)

    # Get review via MCP
    result = await server.call_tool(
        "air__review",
        {"base": "main"}
    )

    # Verify review context
    review_data = json.loads(result["content"][1]["resource"]["data"])
    assert review_data["changes"]["files_changed"] > 0
```

## Implementation Phases

### Phase 1: Core Server (Weeks 1-2)

**Deliverables:**
- Basic MCP server implementation
- Core tools: status, task_create, task_update
- stdio transport
- Unit tests

### Phase 2: Review Tools (Weeks 3-4)

**Deliverables:**
- Review tools: air__review, air__review_gate
- Resource providers for review context
- Integration tests

### Phase 3: Resource Management (Weeks 5-6)

**Deliverables:**
- Link management tools
- Classification tools
- Validation tools
- Context providers

### Phase 4: Claude Integration (Weeks 7-8)

**Deliverables:**
- Claude Desktop configuration
- VS Code extension integration
- Documentation and examples
- End-to-end tests

## Migration Path

### Stage 1: Both Interfaces

Support both shell commands and MCP server:

```bash
# Shell (existing)
air review --format=json

# MCP (new)
# Claude Code calls air__review() natively
```

### Stage 2: MCP Preferred

Documentation and examples favor MCP:

```markdown
# Preferred
Use air__review() tool

# Legacy
air review --format=json (deprecated)
```

### Stage 3: Shell as Wrapper

Shell commands become thin wrappers around MCP:

```python
# air/commands/review.py

def review_command():
    """Shell wrapper for MCP tool."""
    # Call MCP server internally
    result = mcp_client.call_tool("air__review", {...})
    print(format_output(result))
```

## Open Questions

1. **Transport Mechanisms**
   - stdio (simple, works everywhere)
   - HTTP (more flexible, supports remote)
   - Which to prioritize?

2. **State Management**
   - Should MCP server maintain state?
   - Or remain stateless?

3. **Multi-Project Support**
   - One server instance per project?
   - Or one server managing multiple projects?

4. **Error Handling**
   - How to communicate errors to Claude?
   - Structured error types?

## References

- [Model Context Protocol Specification](https://modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [AIR Review Architecture](./REVIEW-ARCHITECTURE.md)
- [AIR Architecture](./ARCHITECTURE.md)

## Changelog

- **2025-10-04** - Initial MCP server design document
