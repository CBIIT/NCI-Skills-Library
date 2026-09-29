---
type: meta
tags: [skills, sharing, ai-augmented-development]
created: 2026-07-28
updated: 2026-07-28
---

# Shared Skills Bundle

## Included Skills

| Skill                   | Purpose                                                                                                                                                                                                                                       | Typical Trigger                                                                                     |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| `book-summary`          | Produces a rich, type-adaptive Markdown summary of a book (5 templates: Narrative, Tutorial, Reference, Technical Mixed, Fiction/Memoir) to support a read/skip decision.                                                                     | "summarize this book", "should I read this", "give me the gist"                                     |
| `c4-analysis`           | Reverse-engineers a C4 architecture model (Context → Container → Component → optional Code) as Mermaid diagrams + narrative from an existing codebase. Validates drawn boundaries against git change-coupling history.                        | "C4 model this codebase", "diagram the architecture", "map out the system"                          |
| `ddd-analysis`          | Performs a DDD analysis: subdomains, bounded contexts, context map, aggregates/entities/value objects, domain events, ubiquitous language glossary, domain-model health score.                                                                | "identify bounded contexts", "map the domain", "find aggregates"                                    |
| `codebase-orientation`  | Two-phase (rapid overview → drill-down) exploration of an unfamiliar/legacy codebase: entry points, architecture, key components, data models, config, workflows, external deps, hotspots via git history, risk callouts.                     | "I inherited this project", "help me get up to speed", "walk me through this code"                  |
| `code-review`           | Structured, severity- and confidence-tagged code review (CR-### finding IDs) across correctness, security, performance, architecture, readability, error handling, testing, and docs. Multi-language aware; respects local repo standards.    | "review this PR", "review this branch", "what do you think of this code"                            |
| `implementation-report` | Produces a narrative (not a diff dump) explaining a change request: description, implementation considerations, alternatives considered, files changed by architecture layer, key changes explained with snippets, testing notes, open items. | "write an implementation report for CR X", "document this CR", "explain what we did in this change" |

