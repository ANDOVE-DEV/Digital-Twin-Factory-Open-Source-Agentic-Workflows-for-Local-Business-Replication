# Saphira Lux Content Management Dashboard - SaaS Blueprint

**Status:** Draft | **Source of Truth**

---

## 1. Project Goal

Transform the legacy "Saphira Lux" standalone web app into an **Enterprise-Grade SaaS Platform** for multi-tenant content management, approval, and publication.

---

## 2. Sacchi Methodology

This project follows **Sacchi** principles:

| Principle | Implementation |
|-----------|----------------|
| **Safety-first** | Never work on `main`. Feature branches only. |
| **Little-often** | Atomic commits after each passing test. |
| **Double-check** | Full test suite before any merge. |

See [SACCHI.md](./SACCHI.md) for full methodology.

---

## 3. Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14+, React, TypeScript, Tailwind, shadcn/ui |
| Backend | NextAuth.js (Identity), Prisma ORM |
| Database | SQLite (Dev) / PostgreSQL (Prod) |
| Automation | n8n (Self-hosted workflows) |
| AI | OpenAI GPT-4, Fal.ai |

---

## 4. Modules

### Phase 1: Platform Core
- [ ] Multi-tenant Identity (Auth, Roles, Tenant Context)
- [ ] Database Schema Migration (`tenant_id`)

### Phase 2: Business Modules
- [ ] Content Scheduling
- [ ] Video Approval Workflow
- [ ] Publication (Auto + Manual)
- [ ] Analytics & Cost Tracking

---

## 5. Documentation Reference

- [FUNCTIONAL_SPEC_STANDALONE_APP.md](../Docs/pre-build-docs/FUNCTIONAL_SPEC_STANDALONE_APP.md)
- [FUNCTIONAL_TO_SAAS_MAPPING.md](../Docs/pre-build-docs/FUNCTIONAL_TO_SAAS_MAPPING.md)
- [saas-enterprise-architecture-blueprint.md](../Docs/pre-build-docs/saas-enterprise-architecture-blueprint%20(1).md)
