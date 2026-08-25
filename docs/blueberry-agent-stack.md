# Blueberry Agent Technology Stack

A Skill is a compact instruction module loaded when a task matches its description. MCP is the live protocol used to call external data and tools. The Skill decides when to retrieve and how to interpret evidence; MCP performs the retrieval.

This repository uses a thin Skill plus a narrow MCP surface to control context cost. It does not expose every possible tool on every turn.

| Layer | Component | Role | Boundary |
| --- | --- | --- | --- |
| Source | BAND OAuth/Open API | Posts, comments, albums, photos | Authorized bands only |
| Documents | Docling | PDF/DOCX/image parsing and OCR | Local processing preferred |
| Retrieval | Qdrant MCP or local vector DB | Similar-case search with metadata | No private data in Git |
| Instructions | blueberry-agent Skill | Routing, evidence, safety | Lazy loading |
| Automation | GitHub Actions | Lint/tests/compatibility | No default data export |

Upgrade policy: pin versions in reviewed dependency files, review licenses and network behavior, upgrade in a feature branch, validate, and merge by pull request.

Avoid tools that extract browser cookies, bypass BAND access controls, expose all filesystem paths, or upload private farm data to an unreviewed service. Third-party Skills can contain prompt injection or executable code; inspect before installation.
