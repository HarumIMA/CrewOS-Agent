# README — Upgrade A2A MCP menjadi Personal Company AI

## Tujuan

Mengubah arsitektur saat ini:

User → Manager Agent → Specialist Agent → MCP Tools

menjadi:

User
→ Company AI / Orchestrator
→ Company Context + Memory
→ Specialized Agents
→ MCP Tools / Knowledge
→ Company Data
→ Company AI
→ User

Target utama:

- AI memahami identitas dan konteks perusahaan.
- AI memiliki memory percakapan.
- AI memahami user dan konteks pekerjaan.
- AI memiliki Company Brain / Knowledge Base.
- Agent memiliki tanggung jawab yang jelas.
- MCP menjadi capability/tool layer.
- A2A digunakan untuk komunikasi antar-agent.
- AI dapat menggabungkan beberapa sumber data sebelum menjawab.
- Sistem tetap menggunakan Python + Agno.
- Arsitektur tetap sederhana dan mudah dikembangkan.

---

# 1. Arsitektur Target

```text
                         ┌─────────────────────────┐
                         │       COMPANY AI        │
                         │                         │
                         │ Identity                │
                         │ Company Context         │
                         │ Conversation Memory     │
                         │ User Memory             │
                         │ Reasoning               │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │      ORCHESTRATOR       │
                         │                         │
                         │ Intent                  │
                         │ Context                 │
                         │ Agent Delegation        │
                         └────────────┬────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
                    ▼                 ▼                 ▼
             ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
             │ GitHub      │   │ HR / DB     │   │ Knowledge   │
             │ Agent       │   │ Agent       │   │ Agent       │
             └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
                    │                 │                 │
                    ▼                 ▼                 ▼
               GitHub MCP        Database MCP       Knowledge MCP
                    │                 │                 │
                    └─────────────────┼─────────────────┘
                                      ▼
                              Company Data
                                      │
                                      ▼
                                Company AI
                                      │
                                      ▼
                                     User