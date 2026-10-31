# pax8-mcp

Stateless HTTP MCP service for the [Pax8 Partner API](https://devx.pax8.com/reference/findcompanies). Exposes Pax8 data as MCP tools so AI assistants can query companies, subscriptions, invoices, orders, products, and usage data.

<div align="center">

## MSPbots Connector

**The MCP Gateway built for MSPs: visible, controlled, and your data stays where it belongs.**

[**Get started at connect.mspbots.ai →**](https://connect.mspbots.ai)

</div>

---

MSPbots Connector gives your AI clients one MCP URL to reach your entire MSP stack (RMM, PSA, documentation, security, finance), and gives you control over who can call which tool and a record of everything that was called.

**Hosted service: [connect.mspbots.ai](https://connect.mspbots.ai)** · Free to use.

### Why Connector

![MSPbots Connector](https://stgoss.mspbots.ai/files/mcp/mspbots-mcp.png)

| | |
|---|---|
| **Visible** | Every tool call is logged: who, which vendor, when. Usage dashboard, CSV export, SIEM streaming. |
| **Controlled** | Role-based, per-tool allowlist. Deny by default. |
| **Protected** | Credentials encrypted per record. AI clients never see your vendor passwords or tokens. |
| **MSP-native** | Built for the MSP stack only: RMM, PSA, documentation, security, finance. |

### Quick start

1. **Sign up** at [connect.mspbots.ai](https://connect.mspbots.ai).
2. **Connect your vendors.** Pick from 150+ connectors and authorize each one on the vendor's own page, or bring your own API keys. No extra vendor accounts needed.
3. **Set access.** Create roles and decide which tools each role may call. Nothing is allowed until you allow it.
4. **Add your MCP URL to your AI client.** Copy the URL from your Connector dashboard into Claude, ChatGPT, Cursor, VS Code, Gemini, Codex, or any MCP-capable client.
5. **Ask your AI to do real work**, and watch every call appear in the audit log.

### Features

**Unified gateway**
- One MCP URL for all your AI clients
- 150+ connectors across the MSP stack
- Custom MCP servers supported, free
- Authorization happens on each vendor's own page; the AI never sees passwords or tokens
- Bring your own credentials: use the vendor API keys you already have
- Multiple accounts per app; connect once, reuse across AI clients
- Tool search: finds the right action for the task
- One sign-in; vendor credentials are injected behind the scenes and OAuth tokens refresh automatically

**Visibility**
- Audit log for every tool call (who, which vendor, when)
- Usage dashboard: call volume, top vendors, error rate, per-user activity
- Export audit logs to CSV, or stream to Loki, Graylog, or LogScale (SIEM)
- Optional recording of tool arguments and result summaries (off by default, enabled per organization)

**Control**
- Per-role, per-tool allowlist, deny by default
- owner / admin / member roles
- SCIM provisioning with Entra ID, Okta, JumpCloud, and Google Workspace

**Security**
- Credentials encrypted one record at a time (AES-256-GCM, per-record key)
- AI clients authenticate with OAuth 2.1 + PKCE
- Vendor responses are scanned for prompt-injection patterns and returned as structured data. This is one layer of defense, not a guarantee against every attack.
- Static egress IP for customer firewall and API allowlisting

### Pricing

**Free.**

Links: [connect.mspbots.ai](https://connect.mspbots.ai) · [mspbots.ai](https://mspbots.ai)

---

## Architecture

- **Stateless** — no user state or credentials stored between requests
- **Per-request auth** — access token passed via `X-Pax8-Token` header on every call
- **Concurrent-safe** — Python `contextvars` isolate credentials across parallel requests
- **Transports** — HTTP (production) or stdio (development)

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /mcp` | MCP protocol entry point (JSON-RPC) |
| `GET /health` | Health check |

Default port: **8080**

## Authorization

Pass your Pax8 access token in every `/mcp` request:

```
X-Pax8-Token: <your_access_token>
```

The service forwards the token as `Authorization: Bearer <token>` to the Pax8 API. Tokens are never stored globally — each request is fully isolated.

## Tool List

| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `pax8_list_companies` | List companies in the partner account | `page`, `size`, `sort`, `name` |
| `pax8_list_company_contacts` | List contacts for a company | `company_id`, `page`, `size` |
| `pax8_list_subscriptions` | List subscriptions | `page`, `size`, `sort`, `company_id`, `status`, `product_id` |
| `pax8_list_subscription_usage_summaries` | List usage summaries for a subscription | `subscription_id`, `page`, `size` |
| `pax8_update_subscription` | Update a subscription's quantity, billing term, or dates | `subscription_id`, `quantity`, `billing_term`, `start_date`, `end_date` |
| `pax8_list_invoices` | List invoices | `page`, `size`, `sort`, `company_id`, `status` |
| `pax8_list_invoice_items` | List line items for an invoice | `invoice_id`, `page`, `size` |
| `pax8_list_orders` | List orders | `page`, `size`, `sort`, `company_id`, `status` |
| `pax8_list_products` | List products in the Pax8 marketplace | `page`, `size`, `sort`, `vendor_name`, `product_name` |
| `pax8_list_usage_summary_lines` | List usage lines for a usage summary | `usage_summary_id`, `page`, `size` |

### Parameter Details

**Pagination** (all list tools):
- `page` — zero-based page number (default: `0`)
- `size` — results per page (default: `10`)
- `sort` — field and direction, e.g. `"name,asc"` or `"createdDate,desc"`

**`pax8_list_subscriptions` status values:**
`Active`, `Cancelled`, `PendingManual`, `PendingAutomated`, `PendingCancel`, `Terminated`, `Expired`, `Trial`

**`pax8_update_subscription` billing_term values:**
`Monthly`, `Annual`, `2-Year`, `3-Year`, `1-Time`, `Trial`

## Quick Start

### Local development (env mode)

```bash
# Copy and edit environment config
cp .env.example .env
# Set PAX8_API_TOKEN and AUTH_MODE=env in .env

# Install dependencies
uv sync

# Run the server
MCP_TRANSPORT=http AUTH_MODE=env python -m pax8_mcp
```

### Docker (gateway mode — production)

```bash
docker build -t pax8-mcp .
docker run -p 8080:8080 -e AUTH_MODE=gateway pax8-mcp
```

Or with Docker Compose:

```bash
docker compose up
```

## Test Examples

**Health check:**

```bash
curl http://localhost:8080/health
# {"status":"ok","transport":"http","auth_mode":"gateway"}
```

**List companies:**

```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -H "X-Pax8-Token: <your_access_token>" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "pax8_list_companies",
      "arguments": {"page": 0, "size": 5}
    }
  }'
```

**List subscriptions for a company:**

```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -H "X-Pax8-Token: <your_access_token>" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "pax8_list_subscriptions",
      "arguments": {"company_id": "<company_uuid>", "status": "Active"}
    }
  }'
```

**List invoice items:**

```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -H "X-Pax8-Token: <your_access_token>" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "pax8_list_invoice_items",
      "arguments": {"invoice_id": "<invoice_uuid>"}
    }
  }'
```

**List usage lines for a usage summary:**

```bash
curl -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -H "X-Pax8-Token: <your_access_token>" \
  -d '{
    "jsonrpc": "2.0",
    "id": 4,
    "method": "tools/call",
    "params": {
      "name": "pax8_list_usage_summary_lines",
      "arguments": {"usage_summary_id": "<usage_summary_uuid>"}
    }
  }'
```

## Configuration Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `PAX8_API_TOKEN` | — | Access token (env mode only) |
| `PAX8_BASE_URL` | `https://api.pax8.com/v1` | Pax8 API base URL |
| `PAX8_AUTH_HEADER` | `X-Pax8-Token` | MCP request header carrying the token |
| `MCP_TRANSPORT` | `stdio` | `http` for production, `stdio` for local dev |
| `MCP_HTTP_PORT` | `8080` | HTTP listen port |
| `MCP_HTTP_HOST` | `0.0.0.0` | HTTP listen host |
| `AUTH_MODE` | `gateway` | `gateway` (per-request, SOP-compliant) or `env` (dev only) |
