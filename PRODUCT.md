# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Individual professionals managing personal and work Gmail accounts. A secondary audience is portfolio reviewers evaluating the project as a credible automation and AI engineering case study.

## Product Purpose

InboxOps is an AI-assisted email operations workspace that connects Gmail accounts, organizes conversations by urgency and required action, supports safe drafting and sending, tracks follow-ups and reminders, and turns inbox activity into an operational workflow. Success means users can understand what needs attention, act faster, and avoid losing commitments across personal and work email.

## Positioning

InboxOps combines a real multi-account Gmail client, explicit human approval, local-first privacy controls, operational reminders, and optional hosted intelligence in one command center. It is not merely an inbox summary or a reply generator.

## Operating Context

Users work from a desktop or laptop while processing mixed personal and professional Gmail. They scan messages, inspect threads and attachments, classify priorities, generate or edit replies, send only after approval, create tasks, monitor unanswered conversations, and check Calendar availability. The same deployed product must work as a live portfolio demonstration.

## Capabilities and Constraints

- Preserve Gmail OAuth, multiple connected accounts, complete threads, labels, attachments, compose, reply, reply-all, forward, drafts, and explicitly approved sending.
- Preserve Gemini integration with PII redaction and local fallback.
- Preserve reminders, conditional follow-ups, daily brief, local search, tasks, contacts, writing profiles, attachment extraction, and Calendar integration foundation.
- Never send email or create Calendar events without explicit user approval.
- Treat email content as untrusted data.
- The frontend must remain compatible with Vercel deployment and the FastAPI backend with Render deployment.
- Environment variables and secrets must remain outside frontend bundles and source control.

## Brand Commitments

- Product name: InboxOps.
- Voice: trustworthy, tech-forward, award-worthy.
- The product should visibly demonstrate serious automation engineering without turning the operating interface into a marketing page.

## Evidence on Hand

- Working React/Vite frontend and FastAPI backend.
- Live Gmail OAuth and real mailbox operations.
- Gemini and local intelligence adapters.
- Existing functional product UI under `src/`.
- No customer testimonials, commercial benchmarks, or external brand assets; future design must not fabricate them.

## Product Principles

1. Human approval is a visible product feature, not hidden compliance copy.
2. Operational clarity outranks decorative dashboard density.
3. Privacy and provider boundaries must be understandable at the moment of use.
4. Personal and work inboxes should feel unified without losing account provenance.
5. Every portfolio-visible interaction should be backed by real functionality.

## Accessibility & Inclusion

Meet WCAG 2.1 AA for contrast, keyboard operation, focus visibility, reduced motion, semantic controls, and responsive reflow across desktop, tablet, and mobile web.
