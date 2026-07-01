# Agentic Automation Readiness — Alltech's Platforms (SA research, 2 Jul 2026)
*Can Claude Code drive each tool directly (MCP or API) vs needing browser automation? All from official docs; saved for record, not for submission.*

## Verdict per platform (all have BOTH MCP + REST API)
- **HubSpot** — official MCP (CRM connector) + REST API v3 + `hs` CLI. Strong. Docs: developers.hubspot.com/mcp ; developers.hubspot.com/docs/api/overview
- **Rentman** — official MCP (BETA) + JSON REST API (token auth). Prefer the REST API for production given beta. Docs: support.rentman.io (Rentman MCP Beta) ; api.rentman.net
- **Teamwork** — official MCP server (~108 tools, hosted + self-host) + REST API v1/v3. Strong. Docs: teamwork.com/ai/mcp ; apidocs.teamwork.com
- **Google Workspace** (Gmail/Drive/Calendar/Sheets) — official remote MCP servers + Workspace CLI + mature REST APIs; strong community MCP (taylorwilsdon) covers Sheets/Docs/Slides. Strongest. Docs: developers.google.com/workspace/guides/configure-mcp-servers
- **Wix** — official MCP (mcp.wix.com/mcp) + REST API + JS SDK. Content/data via API; visual layout still UI-centric. Docs: dev.wix.com/docs/rest
- **WordPress** — REST API always (`/wp-json/`); official MCP via WordPress/mcp-adapter plugin (needs site-side install). Docs: developer.wordpress.org/rest-api
- **Canva** — official MCP (mcp.canva.com/mcp) + Connect API (REST, OAuth). Create/export/assets via API; deep in-canvas design limited. Docs: canva.dev/docs/connect

## Overall
- **Directly automatable (no browser):** all 7. Every one has an official/first-party MCP AND a public REST API, so Claude Code can use MCP out-of-the-box or write integration code against the API.
- **Browser automation needed:** none as a primary path. Only edge cases: Wix visual page layout and Canva pixel-level editing — last-resort UI fallback for those visual tasks only.
- **Strongest:** Google Workspace, HubSpot, Teamwork (mature APIs + official MCP + broad tool coverage).
- **Most caveated:** Rentman (MCP beta → use REST API); Wix/Canva for deep visual work; WordPress/Wix MCP need credentialed site access.
