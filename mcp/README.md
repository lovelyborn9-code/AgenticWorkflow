# MCP Integration Boundary

Credentials and local runtime state must remain outside Git.

BAND configuration uses BAND_ACCESS_TOKEN in the user environment and BAND_KEY set to the API-returned band key, not the numeric URL segment. Minimum read scopes are READ_POST, READ_COMMENT, READ_ALBUM, and READ_PHOTO.

Expose a small interface to the agent: band_sync_all, blueberry_search_cases, and band_get_post_evidence. Keep pagination, authentication, retries, and redaction inside the server. Return compact excerpts with source IDs and dates.

This integration is read-only. Do not add post creation, deletion, or browser-session extraction without separate security review and explicit approval.
