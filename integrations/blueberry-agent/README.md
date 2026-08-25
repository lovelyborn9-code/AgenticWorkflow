# Blueberry Agent Integration

This integration adds a token-efficient, evidence-first blueberry assistant to AgenticWorkflow.

Components:
- .codex/skills/blueberry-agent/SKILL.md: lazy domain instructions.
- mcp/band_mcp_server.py: read-only BAND API MCP server; credentials stay outside Git.
- docs/blueberry-agent-stack.md: selected technologies and boundaries.
- .github/workflows/blueberry-agent-validate.yml: safe validation on pull requests.

Never commit BAND posts, comments, member lists, access tokens, private images, or embeddings. Keep them outside Git or in ignored paths. GitHub Actions is code validation only unless a reviewed secret-backed sync workflow is added.

Recommended runtime: BAND OAuth/Open API, Docling for local OCR, Qdrant for semantic retrieval, and the blueberry-agent Skill for routing and compact evidence synthesis.

The default integration is read-only. Write/delete BAND operations are excluded.
