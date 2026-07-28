---
version: 1.0
name: book-summary
description: >
  Produces a comprehensive summary of a book to help the user decide
  whether to read it and how to use it. Use this skill whenever the user
  uploads or references a book (any genre or format) and asks to
  "summarize it", "give me a summary", "what is this book about",
  "should I read this", "is this worth reading", "give me the gist",
  "distill this for me", or "what does this cover". Also trigger when
  the user says "help me decide if I should read X" or "overview of X."
  The output is a rich Markdown summary report tailored to the book's
  type — enough to make an informed read-or-skip decision. Always use
  this skill for these requests — do not substitute a short,
  conversational summary.
---

# Book Summary Skill

## Purpose

Produce a **comprehensive content summary** of a book — rich enough that
the reader can make an informed decision about whether to read it, and if
so, which parts matter most and how to approach them. The summary format
is chosen to match the book's *type*: a learn-by-doing tutorial warrants
a different summary than a narrative argument or a reference manual.

---

## Phase 0 — Ingest the Document

Identify the file type and read the relevant skill if needed:

| Type | First move |
|------|-----------|
| PDF | `pdfinfo` for metadata; `pdftotext` for full text (or another available skill/tool for PDF reading) |
| EPUB / ODT | `pandoc -t plain` for full plain-text extraction |
| DOCX | `pandoc -t markdown` |
| Plain text / Markdown | `wc -c` then `cat` as size warrants |

**Key extractions needed:**

1. Title, authors, edition/version, publication date, publisher
2. Table of Contents (exact chapter/section titles + hierarchy)
3. Front matter: preface, introduction, foreword — these often state
   the author's intent and target audience; read carefully
4. Representative chapter samples (first chapter + 1–2 middle chapters)
5. Back matter: conclusion, appendices, index structure

**Sampling strategy for long books (>300 pages):**
Do not read every word verbatim, but read enough to produce honest
summaries — not vague platitudes. Recommended approach:
- Read the first and last ~10% of each chapter fully
- Scan middle sections for structure shifts, examples, commands, named concepts
- Read all section headings and bolded terms
- Read any chapter summary section if present

---

## Phase 1 — Classify the Book Type

**This step determines the entire output format.** Follow these steps
in order before writing anything.

### Step 1 — Check for a user-specified type

If the person's request names a template or type explicitly — for
example: "use the tutorial template", "treat this as a reference book",
"summarize this as Type D", "use Template B" — skip all classification
logic and go directly to that template. Confirm the override in the
report header:

> **Book Type:** Tutorial / Learn-by-Doing *(Type B — user specified)*

### Step 2 — Classify from content signals

Read the preface, introduction, and TOC carefully. A book's title alone
is not sufficient — check multiple signals.

| Signal | What it suggests |
|--------|-----------------|
| "Hands-on", "practical", "exercises", keystroke tables, lab callouts | Tutorial / Learn-by-Doing |
| Chapters organized by task or workflow, not concept | Tutorial / Learn-by-Doing |
| Alphabetical or lookup-oriented structure, entries not chapters | Reference |
| "Man page", cookbook, dictionary, encyclopedia in title/description | Reference |
| Appendices dominate; chapters are thin intros to appendices | Reference |
| Conceptual exposition with evidence/argument, numbered chapters | Narrative / Argument |
| Story arc, characters, events, scenes | Fiction / Narrative |
| Subject's life arc, chronological or thematic | Biography / Memoir |
| Mix: conceptual chapters + tutorial sections + reference appendices | Technical Mixed |

### The five book types

**Type A — Narrative / Argument**
Business, science, history, self-help, social science. Makes a claim
and marshals evidence for it. The value is in the argument and insights.
→ Use Template A

**Type B — Tutorial / Learn-by-Doing**
Programming tutorials, tool instruction, language learning, craft
instruction. Teaches by having the reader *do* things in sequence.
The value is in the skill progression, not in a central argument.
→ Use Template B

**Type C — Reference**
API documentation, style guides, cookbooks (recipe-style), man pages,
dictionaries, encyclopedias. Organized for lookup, not linear reading.
Most readers will never read it cover-to-cover.
→ Use Template C

**Type D — Technical Mixed**
Technical books that combine conceptual chapters, tutorial walkthroughs,
and reference appendices in meaningful proportions, where each type of
content is load-bearing. Each section may need a different treatment
within the same report.
→ Use Template D

**Type E — Fiction / Biography / Memoir**
Story-driven or life-narrative books.
→ Use Template E

When a book fits two types, pick the *dominant* one and note the
secondary type in the report header. A book that is 70% tutorial and
30% reference is Type B with reference elements.

### B vs D tiebreaker

Technical books with conceptual framing woven through tutorial chapters
are frequently mistaken for Type D. Apply this test before choosing D:

> **Could the conceptual content be stripped out and the chapter would
> still teach the same skill?**

- **Yes** → The rationale is scaffolding, not load-bearing. Classify
  as **Type B** (with explanation). Most O'Reilly programming tutorials
  fall here.
- **No** → The "why" is essential to understanding what the code does
  or when to use it. Classify as **Type D**.

Type D requires that the conceptual content changes what you conclude
about the code, not just motivates it. A chapter that argues
"Go's interface satisfaction is implicit — here's why that enables
dependency injection in ways inheritance doesn't" is load-bearing
(Type D). A chapter that says "here's how closures work, and by the
way, functions are first-class values in Go" is scaffolding (Type B).

### Step 3 — Handle genuine ambiguity

If after applying the signals table and the B vs D tiebreaker the
classification is still genuinely uncertain, **stop and ask** rather
than guessing. Present the two candidate types, explain briefly what
signals point each way, and ask the person which better matches their
intent:

> "This book shows signals of both Type B (Tutorial) and Type D
> (Technical Mixed). The tutorial structure and exercises suggest B,
> but several chapters argue design philosophy in ways that change how
> the code examples should be read, which suggests D. Which template
> would you prefer, or would you like me to pick and explain my
> reasoning?"

Do not ask if the classification is clear — the pause is only for
genuine ambiguity where a reasonable reader could go either way.

---

## Phase 2 — Write the Summary Report

Output a single Markdown file using the template for the classified
type. All templates share a **common header block** and **common footer
sections** (Who Should Read This, Comparable Works). The middle sections
are type-specific.

### Common Header Block (all types)

```markdown
# Book Summary: <Title>

> **Author(s):** ...
> **Publisher:** ...   **Year:** ...
> **Edition:** ...   **Length:** ~N pages / N chapters
> **Book Type:** <Type A–E name>  *(e.g., Tutorial / Learn-by-Doing)*
> **Secondary type (if any):** ...
> **Prerequisites:** <What the reader must already know — be specific>
> **Version sensitivity:** <Is content time-sensitive or tool-version-specific? Flag it.>
> **Source file:** <filename>

---
```

---

### Template A — Narrative / Argument

Sections:

**1. The Book in Brief** — 2–4 paragraphs: central thesis, intended
audience, why the author wrote it, the book's stance or POV. This section
alone should answer: "Is this book for me?"

**2. Structural Overview** — 1 paragraph: how the book is organized,
what the logical arc is (progressive argument, chronological, case studies, etc.)

**3. Chapter-by-Chapter Summaries** — For EVERY chapter:

```
### Chapter N — <Title>

**In a sentence:** [One-sentence bottom line — the single most important
thing this chapter argues or shows.]

[2–5 paragraphs: main arguments, key evidence, examples, case studies.
Name the ideas, people, frameworks, findings. Avoid vague language like
"the author explores." Say what they actually argue or conclude.]

- **Key concepts introduced:** [Named frameworks, vocabulary, coined terms]
- **Standout example or case:** [Most memorable evidence from the chapter]
- **Connection to prior chapters:** [How this builds on what came before — skip for Ch. 1]
```

**4. Thematic Threads** — 4–8 cross-cutting themes, each with chapter
citations and a 1–2 sentence explanation of how the theme develops.

**5. Key Takeaways** — 5–10 specific, substantive bullets on the book's
most important conclusions, lessons, or insights.

**6. Keywords & Index** — 20–40 alphabetically sorted keywords (named
frameworks, concepts, people, coined terms), each with a one-line gloss
and chapter pointer.

---

### Template B — Tutorial / Learn-by-Doing

Sections:

**1. The Book in Brief** — 2–3 paragraphs: what skill or tool is taught,
from what starting point to what end capability; teaching approach
(exercises, projects, keystroke demos, labs); whether designed for
linear or selective use.

**2. Skill Progression Arc** — 1 paragraph describing how the reader's
capability grows: what they can do after chapter 1, after the first
third, after completing the book.

**3. Chapter-by-Chapter Breakdown** — For EVERY chapter:

```
### Chapter N — <Title>

**Skills unlocked:** [What the reader can do after this chapter that
they couldn't do before — stated as capabilities, not topics]

**Approach:** [How this chapter teaches: worked example, exercise, demo,
explanation, problem/solution, etc.]

[1–3 paragraphs: what is actually taught, what commands/techniques/
patterns are introduced, what the hands-on components involve. Be
concrete — name the actual commands, keystrokes, patterns, or procedures.]

- **Key commands / techniques / syntax introduced:**
  | Command / Pattern | What it does |
  |-------------------|-------------|
  | `command` | Brief description |

- **Exercises / labs:** [Count and brief description of hands-on components.
  Note if solutions are provided.]
- **Prerequisites from earlier chapters:** [What from prior chapters is
  assumed here — skip for Ch. 1]
- **Gotchas / cautions flagged:** [Any "watch out for this" content the
  author highlights]
```

**4. Cumulative Skills Summary** — A table of major skill areas, which
chapters cover them, and what capability the reader gains:

| Skill Area | Chapters | What you'll be able to do |
|------------|----------|--------------------------|

**5. Exercises & Labs Inventory** — Consolidated table of all hands-on
exercises across the book:

| Chapter | Exercise / Lab | Type | Solutions provided? |
|---------|---------------|------|-------------------|

**6. Quick-Reference Cheat Sheet** — Consolidated table of the most
important commands, keystrokes, patterns, or syntax from across the
entire book, organized by category. Aim for 30–60 items.

| Category | Command / Pattern | What it does |
|----------|-------------------|-------------|

**7. Key Takeaways** — 5–8 bullets on what a reader who completes this
book will be able to do or understand. Frame as capabilities.

**8. Keywords & Index** — 15–30 alphabetically sorted technical terms,
commands, or concepts with one-line definitions and chapter pointers.

---

### Template C — Reference

Sections:

**1. The Book in Brief** — 2 paragraphs: what this reference covers and
what it does not; intended audience and when they reach for it;
organization philosophy (alphabetical, by task, by domain); how it
relates to official documentation.

**2. Coverage Map** — A structured table showing what the reference
covers by major domain:

| Domain / Section | What it covers | Pages/Sections |
|-----------------|----------------|---------------|

**3. Section-by-Section Guide** — For each major section:

```
### [Section Name]

**Use this section when:** [The specific task or question that brings
a reader here — stated as "I need to..."]

**What's here:** [2–4 sentences on content scope. Be specific about
what entries, tables, patterns, or procedures are documented.]

**Notable entries:** [3–5 of the most important or frequently needed items]

**Format:** [How content is presented: prose, tables, code examples,
syntax diagrams, etc.]
```

**4. Quick-Access Index** — Curated lookup table for most common tasks:

| "I need to..." | Where to look |
|---------------|--------------|

Aim for 20–40 entries covering the most frequent use cases.

**5. Coverage Gaps & Limitations** — What is notably absent or
underserved? What does this reference not cover that a reader might
expect?

**6. Compared to Official Docs** — How does this relate to freely
available documentation? What value does it add?

**7. Keywords & Master Index** — 30–50 alphabetically sorted entries
covering the most important terms, commands, functions, or concepts,
with one-line descriptions and section pointers.

---

### Template D — Technical Mixed

Sections:

**1. The Book in Brief** — 2–3 paragraphs: what the book teaches,
how it mixes content types and why, intended audience and prerequisites,
whether designed for linear or selective use.

**2. Structural Overview & Reading Guide** — 1 paragraph on organization,
then a table typing each chapter:

| Chapter / Section | Type | Purpose |
|------------------|------|---------|

Types: **Conceptual** (explanation/argument), **Tutorial** (hands-on),
**Reference** (lookup), **Case Study** (applied example)

**3. Chapter-by-Chapter Breakdown** — For EVERY chapter, use the format
matching its type:

For Conceptual chapters:
```
### Chapter N — <Title>  *(Conceptual)*

**Core idea:** [One-sentence summary of the conceptual content]

[1–3 paragraphs. Emphasize the mental model, argument, or principle
being established.]

- **Key concepts introduced:** [Named ideas, frameworks, vocabulary]
```

For Tutorial chapters:
```
### Chapter N — <Title>  *(Tutorial)*

**Skills unlocked:** [What you can do after this chapter]

[1–3 paragraphs. Name the actual commands, patterns, or procedures covered.]

- **Key commands / techniques:**
  | Command | What it does |
  |---------|-------------|
- **Exercises / labs:** [Count and description]
```

For Reference chapters/appendices:
```
### Chapter N / Appendix X — <Title>  *(Reference)*

**Use this when:** [The task that brings a reader here]

**What's here:** [Brief scope and notable entries]
```

**4. Skill Progression** (tutorial sections) — Table of skills gained
from all tutorial content.

**5. Quick-Reference Cheat Sheet** — Consolidated commands, syntax, or
patterns from all reference and tutorial sections.

**6. Key Takeaways** — 5–10 bullets covering all content types.

**7. Keywords & Index** — 25–40 alphabetically sorted terms with
one-line glosses and chapter pointers.

---

### Template E — Fiction / Biography / Memoir

Sections:

**1. The Book in Brief**
- Fiction: premise, setting, protagonist, central conflict (no major spoilers
  unless explicitly requested)
- Biography/Memoir: subject, time period, author's perspective and access,
  interpretive lens (hagiography vs. critical, insider vs. outsider)

**2. Structural Overview** — How is the book organized? Chronological?
Non-linear? Thematic? Note the overall arc.

**3. Chapter-by-Chapter Summaries** — For every chapter:

```
### Chapter N — <Title>

**What happens / what's covered:** [1–3 paragraphs]

- **Characters introduced / developed:** [Names and brief roles]
- **Key events or decisions:** [Most significant moments]
- **Tone and style note:** [Only if notably different from rest of book]
```

**4. Thematic Threads** — 4–8 literary or biographical themes, each
with chapter citations and a 1–2 sentence explanation of development.

**5. Key Takeaways / Resonances** — Themes, questions, and emotional
resonances (fiction) or lessons and historical significance (biography).

**6. Keywords & Index** — 15–30 key terms: character names, places,
events, figures, symbols, motifs — with one-line context notes.

---

### Common Footer Sections (all types)

Append to every report after the type-specific sections:

```markdown
---

## Who Should Read This (and Who Shouldn't)

**Read it if:** Describe the reader most likely to find this book
valuable — their role, goals, prior knowledge, current situation,
or the specific problem they're trying to solve.

**Skip it if:** Describe readers who would find it redundant,
inaccessible, too shallow, too narrow, dated, or otherwise not worth
their time. Be honest. Note better alternatives where relevant.

---

## Comparable Works

3–5 books in the same space. For each, briefly note the relationship:
covers similar ground, makes a contrasting argument, is a prerequisite,
goes deeper on a subtopic, is more or less advanced, or is the "if you
liked this" recommendation.

---
*Summary generated by book-summary skill.*
```

---

## Output Delivery

1. Write the report to `<slug>-summary.md` in the folder where the skill was
   invoked, where `<slug>` is a lowercased, hyphenated version of the book title.
2. Confirm the file path to the user.
3. Add one short inline note (2–3 sentences): the single most useful thing to
   know for a reader deciding whether to read this book.

---

## Quality Checklist

Before writing the output file, verify:

**Classification:**
- [ ] User-specified type was honored if provided, OR type was determined from content signals (not just the title)
- [ ] The classification (and whether it was user-specified) is stated in the report header
- [ ] The correct template was used; if B vs D was ambiguous, the tiebreaker was applied or the user was asked

**Coverage:**
- [ ] Every chapter has its own entry — none skipped or merged without explanation
- [ ] Summaries are specific: named concepts, commands, arguments, examples

**Type-specific checks:**

*Tutorial (B) and tutorial sections of (D):*
- [ ] "Skills unlocked" is phrased as capabilities, not topics
- [ ] Key commands table is populated with actual commands from the book
- [ ] Exercises inventory covers all chapters with hands-on content
- [ ] Quick-reference cheat sheet is present and populated

*Reference (C) and reference sections of (D):*
- [ ] Coverage map clearly shows what is and isn't in the reference
- [ ] "Use this section when" entries are phrased as reader tasks
- [ ] Quick-access index is present and covers common use cases

*Narrative/Argument (A):*
- [ ] Central thesis is clearly stated in "The Book in Brief"
- [ ] Chapter summaries show claim → evidence → conclusion structure

**General:**
- [ ] Prerequisites are stated specifically (not "some programming knowledge")
- [ ] Version sensitivity is flagged where applicable
- [ ] "Who Should Read This" is honest and specific, not promotional
- [ ] Comparable works are named with relationship notes
