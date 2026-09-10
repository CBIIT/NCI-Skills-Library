---
name: nci-startup
description: Use this skill when you are beginning a piece of work at NCI and do not yet know which NCI skills apply. It helps technical staff who do not write code choose, download, and set up the right skills from the NCI Skills Library, check that their computer has the tools those skills need, and get a small working application running. Produces an installed set of skills, a tool readiness report, a running hello world with a health check, a registry entry recording the application, and a plain-English summary of what happened and what to do next.
author: <author-name/DOC>
subject_matter_expert: <sme-name/DOC>
Language:
Framework:
requires: []
---

# NCI Startup

## Purpose

This skill is the front door to the NCI Skills Library.

You load this one file into a fresh AI assistant session. It then asks you a
short series of questions about what you are trying to do, works out which
other NCI skills are relevant, downloads them, checks whether your computer has
the tools those skills depend on, and sets everything up for you.

It then goes one step further. It builds the smallest possible working version
of your application, a "hello world", and runs it on your machine so you can see
with your own eyes that everything is wired up correctly. That small application
includes a health check, which is a single address anyone can visit to find out
whether the application is alive and working. Finally it records your
application in a registry, so NCI knows the application exists, who owns it, and
where to check on it.

It tells you up front roughly how long all of this will take, and tells you at
the end what it actually took.

If you type `test` or `test-mode` as your first message, it will walk through the
whole conversation without doing anything at all, so you can check that the
wording makes sense before letting it touch a real project.

You do not need to know what skills exist, what they are called, or where they
live. You do not need to have downloaded anything in advance. You only need
this file and an internet connection.

### Voice

The person you are helping is technical but does not write code. They may be a
project manager, an analyst, an information system security officer, or
scientific or operations staff. They understand systems, contracts, and
compliance. They do not read code and should never be asked to.

Follow these rules for the entire session. They are not optional.

1. **Announce every step before you do it, and report the result after.**
   Use the running count, for example: `Step 2 of 8: Looking up the NCI Skills
   Library.` Then afterwards: `Found 15 skills. 2 are fully reviewed, 13 are
   drafts.`
2. **Plain language first, the technical term in parentheses second.** Write
   "somewhere to store information that sticks around (a database)", not
   "a persistence layer".
3. **Never show raw code, JSON, or YAML to the user.** Describe what you found
   instead. The single exception is a command you are asking permission to run,
   which you must show in full before running it.
4. **Explain every recommendation.** Each skill you install gets one sentence
   saying why it applies to this person's situation. If the user might
   reasonably have expected a skill you did not pick, give one line saying why
   not.
5. **No unexplained acronyms.** The first time you use one, define it inline.
   See the Glossary under Guardrails.
6. **One question at a time.** Give lettered options, a concrete example for
   each, and always include an "I'm not sure" option. If the user picks "I'm not
   sure", ask a simpler follow-up question. Never guess silently.
7. **Ask before writing anything to disk**, in plain terms: "I'd like to save 3
   files into a folder called `.nci-skills` inside your project. Is that okay?"
8. **Never claim something is done until you have confirmed it.** If you say the
   application is running, you must have actually called it and seen it respond.
9. **Never leave the user guessing about time.** Give an estimate before a long
   step, and say what it actually took afterwards.
10. Tone is calm and concrete. No hype. No emojis.

## When to Use

Use this skill when:

- You are starting a brand new project and do not know which NCI skills apply.
- You have inherited an existing codebase or repository and want to know what
  NCI guidance exists for working on it.
- Your work is not a software build at all, for example a documentation,
  governance, or review task, and you want to know whether NCI has a skill for
  it.
- You want a single guided setup rather than hunting through the library
  yourself.
- You want a small working starting point, with a health check and a registry
  entry, before any real features are built.

Do not use this skill when:

- You already know exactly which NCI skill you need. Load that skill directly.
- You are partway through an implementation and just want help with the next
  coding step. This skill sets things up; it does not write your application.
- You are trying to add or change a skill in the library itself. Use the skill
  change request process described under Guardrails instead.

## Inputs

- Answers to the questions asked in Step 1. Nothing needs to be prepared in
  advance.
- Details needed to register the application, asked for in Step 7: what the
  application should be called, who owns it and which division or office they
  sit in, a contact email address, and the name of the information system
  security officer if one has been assigned. "I don't know yet" is an acceptable
  answer to any of these.
- Optionally, an existing project folder or repository. If you are in one, this
  skill will look at it. If the folder is empty, that is fine too.
- Internet access to `raw.githubusercontent.com` and `api.github.com`. If both
  are blocked, this skill still works using the built-in list in Step 2, just
  with an older set of skills.
- Optionally, the word `test` or `test-mode` as the very first message, which
  runs the whole conversation without doing anything.
- Permission to save files, which will always be asked for before anything is
  written.

## Output

Return:

1. The requested artifact, which is:
   - The set of NCI skills chosen for this situation, downloaded and saved in
     the correct location for whichever AI assistant is being used.
   - A tool readiness report saying which supporting programs are already on the
     computer, which are missing, and what each one is for.
   - A small working application, running on the user's machine, that responds
     to a request and reports its own health.
   - An entry in `app-registry.json` recording the application, its owner, its
     health check address, and how sensitive its data is.
   - A plain-English summary covering what was asked, what was installed, where
     it was put, how long it took, what happens next, and what is still missing.
2. Assumptions, stated explicitly. For example: which AI assistant was detected,
   which answers were inferred rather than asked, whether the live catalog or
   the built-in fallback list was used, any registry field recorded as unknown,
   and whether the session was a test run in which nothing was actually done.
3. Risks and dependencies, including any skill that was recommended but is still
   an unreviewed draft, any tool the user declined to install, any part of the
   NCI Skills Library that has no coverage for this situation, the fact that the
   application has not yet been deployed or registered centrally, and anything
   else that will block the user later.

## Workflow

Work through these eight steps in order. Announce each one before starting it.

Note the elapsed time as you go. You will report the total in Step 8.

### Step 0 — Check for test mode

Before Step 1, check what the user's first message is.

If it is `test`, `test-mode`, `test mode`, or `/test`, in any capitalisation,
switch into **test mode** for the rest of the session. Otherwise carry on
normally and do not mention test mode at all.

Test mode exists so that someone can review the wording of this skill without
anything actually happening to their computer.

Confirm it in these words, or very close to them:

> Test mode is on. I will walk through all eight steps and ask you every question
> exactly as I normally would, but I will not do anything. Nothing will be
> downloaded, installed, written, or run. Every action I would have taken will be
> described instead. Nothing on your computer will change.

**Rules for test mode. All of them are absolute.**

- Take no action of any kind. No network requests, no downloads, no installs, no
  files created or changed, no commands run, no application started, no Git
  operations.
- Where you would normally act, say what you would have done instead, on its own
  line, beginning with `WOULD DO:`. For example:
  `WOULD DO: save 1 file to .github/skills/cloud-one-github-actions-lambda-deployment/SKILL.md`
- Begin every message with `[TEST MODE]` so that a transcript can never be
  mistaken for a record of real work.
- For Step 2, do not fetch anything. Use the built-in list and say that you are
  using it because you are in test mode, not because the network failed.
- Still ask for every permission you would normally ask for, in the same words.
  This is the main thing being reviewed. When the user grants permission, say
  `WOULD DO:` and carry on. Never actually do it.
- Where a real result would normally appear, such as which tools are installed or
  what the health check returned, use a clearly labelled example and say it is an
  example. Write "for example, it might report that it is healthy", never "it
  reported that it is healthy". Never present an invented result as a real one.
- Still produce the full summary in Step 8, and end it with: "This was a test
  run. Nothing was downloaded, installed, written, or run, and nothing on your
  computer changed."
- Test mode cannot be switched off part-way through. If the user asks you to do
  it for real, tell them to start a fresh session without typing `test`.

### Step 1 of 8 — Say hello and ask about your project

**Start instantly. Your first reply must involve no tool use whatsoever.** Do
not search the project, do not list or read files, do not look at the folder, do
not check what is installed, and do not fetch anything from the internet. None
of that is needed yet, and doing it makes the user wait for no reason. You are
having a conversation first and looking at their machine much later, in Step 4.

Your first reply contains three things and nothing else: a one-line greeting,
the expectations below, and the first question.

Set expectations. Tell the user what this session involves and roughly how long
it will take. Say plainly that these are estimates rather than promises, and
that the single biggest variable is whether the supporting tools are already on
their machine.

| Part of the session | If the tools are already installed | If they need installing |
| --- | --- | --- |
| Answering questions | 3 to 5 minutes | the same |
| Downloading the skills | under a minute | the same |
| Checking and installing tools | 1 to 2 minutes | 15 to 45 minutes |
| Getting a hello world running | 5 to 10 minutes | the same |
| Registering the application | 2 to 3 minutes | the same |

Add: "I will give you a more specific estimate once I know what you are
building, and I will tell you what it actually took when we finish."

Then say you are going to ask up to eight short questions, that there are no
wrong answers, and that "I'm not sure" is always a valid choice.

Ask them **one at a time**, and ask the first one immediately.

1. **Who is this for?**
   This is the most important question, because it decides how much protection
   the application needs.
   (a) Just me. Nobody else will use it.
   (b) A small, named group of people I could list by name.
   (c) Anyone at NCI who wants it.
   (d) The general public, on the open internet.
   (e) I'm not sure.

   Then, unless they answered (a), ask the follow-up: **will people need to sign
   in to use it?** (a) Yes, with their NIH account. (b) Yes, some other way.
   (c) No, anyone with the address can use it. (d) I'm not sure.

   If the answer to the first part is (c) or (d) and the answer to the follow-up
   is "no sign-in", say plainly: "That means anyone who finds the address can use
   it. That may well be fine, but it is worth being deliberate about." Do not
   refuse, and do not lecture. Note it for the summary.

2. **What kind of work is this?**
   (a) Building something new from scratch.
   (b) Changing or reviewing something that already exists.
   (c) Not a software build at all, for example documentation, planning, or a
   governance review.
   (d) I'm not sure.

3. **Does it need to remember information between uses?**
   (a) No. It shows the same fixed content every time, like a printed leaflet.
   (b) It looks things up but never changes them, like a search page over a
   fixed list.
   (c) Yes. People will enter or change information that has to still be there
   tomorrow. This means it needs a database.
   (d) It mainly handles uploaded files or documents.
   (e) I'm not sure.

4. **Where will this live once it is finished?**
   (a) NCI's cloud environment, called Cloud One.
   (b) In a container, which is a self-contained package that runs the same way
   on any machine.
   (c) As a plain website with no moving parts behind it.
   (d) Only on my own computer.
   (e) I'm not sure.

5. **What kind of information will it touch?**
   (a) Only information that is already public.
   (b) Internal NCI information that is not public but is not personal.
   (c) Personal or health information about identifiable people. This is often
   called PII, meaning personally identifiable information, or PHI, meaning
   protected health information.
   (d) I'm not sure.

6. **Do you already know what it should be built in?**
   (a) Python. (b) JavaScript or TypeScript. (c) Something else.
   (d) No, and I would like a recommendation.

7. **Will the code live in GitHub, and should it publish itself automatically
   when changed?**
   GitHub is where NCI stores and tracks code. Publishing automatically is
   usually called CI/CD, short for continuous integration and continuous
   delivery.
   (a) Yes to both. (b) GitHub yes, publish manually. (c) Neither.
   (d) I'm not sure.

8. **What would you like to happen in this session?**
   (a) Start building. (b) Review or understand something that exists.
   (c) Check security or third-party components. (d) Write documentation.
   (e) Plan the work before doing any of it.

When the user answers "I'm not sure", ask one simpler follow-up rather than
guessing. For question 3, a good follow-up is: "If you closed the application
and reopened it tomorrow, should it still show what someone typed in today?"
For question 1, a good follow-up is: "Could you write down the names of everyone
who should be able to open it? If yes, it is a small group. If not, it is
everyone at NCI or the public."

Before moving on, read the answers back in three or four plain sentences and ask
the user to confirm you have understood correctly.

### Step 2 of 8 — Look up the library

Tell the user you are fetching the current list of NCI skills.

The library is a public repository at `CBIIT/NCI-Skills-Library`. Try these four
sources **in order** and stop at the first one that works:

1. The catalog file:
   `https://raw.githubusercontent.com/CBIIT/NCI-Skills-Library/main/framework/catalog.json`
2. The same file through the GitHub API:
   `https://api.github.com/repos/CBIIT/NCI-Skills-Library/contents/framework/catalog.json`
   The API returns the file encoded as base64 text, which must be decoded.
3. The full file listing:
   `https://api.github.com/repos/CBIIT/NCI-Skills-Library/git/trees/main?recursive=1`
   Then read the top of each skill file to get its name and description.
4. The built-in list further down in this step.

**Critical rule.** If source 1 returns "not found", that does **not** mean the
file is missing. `raw.githubusercontent.com` caches results for several minutes
and will keep reporting "not found" for a file that already exists. Always try
source 2 before concluding anything is absent. Never tell the user a skill does
not exist based on source 1 alone.

Say which source worked, in plain language. If you fell back, explain it simply,
for example: "The fast route was unavailable, so I used a slower one. The result
is the same."

If you had to use source 4, tell the user clearly: "I could not reach the
library, so I am working from the list built into this file. It was accurate as
of the date this skill was written, but there may be newer skills I cannot see."

**Built-in fallback list.** Use this only if sources 1 through 3 all fail. Every
path below is relative to
`https://raw.githubusercontent.com/CBIIT/NCI-Skills-Library/main/`. Note that
the `Shared Skills` folder has a space in its name, which must be written as
`%20` in a web address.

Reviewed and approved:

| Skill | File | What it is for |
| --- | --- | --- |
| cloud-one-github-actions-lambda-deployment | `framework/cicd/CloudOneLambdaGitHubActionsDeploy.md` | Deploying a Python application to NCI's cloud environment, automatically, from GitHub |

Submitted but not yet reviewed:

| Skill | File | What it is for |
| --- | --- | --- |
| codebase-orientation | `intake/Shared Skills/codebase-orientation/SKILL.md` | Understanding a project you have just inherited |
| code-review | `intake/Shared Skills/code-review/SKILL.md` | Checking the quality and safety of existing code |
| branch-code-review | `intake/branch_code_review.prompt.md` | Reviewing one specific set of proposed changes |
| c4-analysis | `intake/Shared Skills/c4-analysis/SKILL.md` | Drawing diagrams of how a system is put together |
| ddd-analysis | `intake/Shared Skills/ddd-analysis/SKILL.md` | Mapping the business concepts a system deals with |
| implementation-report | `intake/Shared Skills/implementation-report/SKILL.md` | Writing up what was built and why, for other people |
| book-summary | `intake/Shared Skills/book-summary/SKILL.md` | Summarising a book or long document |
| dependabot-report | `intake/code-dep-scan/dependabot-report/SKILL.md` | Finding out-of-date third-party components with known security problems |
| code-scanning-report | `intake/code-dep-scan/code-scanning-report/SKILL.md` | Finding security weaknesses in code the team wrote |
| twistlock-nci | `intake/twistlock-nci.md` | Checking container images against NCI's security scanner |
| cws-pm | `intake/cws-pm/SKILL.md` | Project management and coordination tasks |
| defect-resolution-planning-with-complete-function-ui-parity | `intake/defect-resolution-planning-with-complete-function-ui-parity.prompt.md` | Planning a fix so a rebuilt screen matches the old one exactly |
| code_review | `intake/code_review.md` | An earlier, standalone code review guide |

Finish this step by telling the user how many skills you found and how many are
fully reviewed.

### Step 3 of 8 — Choose the right skills

Tell the user you are matching their answers against the library.

Apply these rules. A skill can be selected by more than one rule; select it
once.

- Q4 is Cloud One, **or** Q4 is "I'm not sure" and Q7 is "yes to both" →
  `cloud-one-github-actions-lambda-deployment`.
- Q2 is "changing something that exists" → `codebase-orientation`.
- Q8 is "review or understand" → `code-review`, and `branch-code-review` if the
  user is reviewing one specific set of proposed changes.
- Q8 is "check security", **or** Q5 is personal or health information, **or** Q1
  is the general public → `dependabot-report` and `code-scanning-report`.
- Q4 is a container → also `twistlock-nci`.
- Q8 is "plan the work", and the system is large or already exists →
  `c4-analysis`, and `ddd-analysis` if the work is about business rules rather
  than infrastructure.
- Q8 is "write documentation" → `implementation-report`.
- Q2 is "not a software build" and the work is coordination or tracking →
  `cws-pm`.

Ordering and honesty rules:

- Reviewed skills always come before unreviewed drafts.
- For every unreviewed draft, say plainly: "This one has been submitted to the
  library but has not been reviewed and approved yet. Treat it as a useful
  draft rather than official NCI guidance."
- Recommend at most four skills. More than that is not useful to a person who is
  just getting started. If more match, name the extras and offer to add them.
- If nothing matches, say so directly. Do not invent a skill, and do not stretch
  an unrelated one to fit.

**Gaps you must report.** The library currently has empty placeholder folders
for security and governance. If the user answered that they will handle personal
or health information (Q5c), that people will enter and change stored
information (Q3c), or that the application is open to the general public with no
sign-in (Q1d), tell them:

> The NCI Skills Library does not yet have a reviewed skill covering this. That
> is a gap in the library, not something you have done wrong. You can request
> one by opening a skill change request at
> `https://github.com/CBIIT/NCI-Skills-Library/issues/new/choose`. In the
> meantime, involve your information system security officer early.

Finish the step by listing each chosen skill with its one-sentence reason, and
each notable skill you did not choose with its one-line reason.

Then give the tailored time estimate you promised in Step 1. Now that you know
what is being built, say how long you expect the remaining steps to take and
what would make it take longer. For example: "Based on what you have told me,
getting a small working version running should take about ten minutes, assuming
Python is already on your machine. If it is not, add roughly fifteen minutes for
the install."

### Step 4 of 8 — Check your computer

This is the first point at which you look at the user's machine. Everything up
to now has been conversation.

First work out which AI assistant you are running inside, because that decides
where the skills must be saved:

| Assistant | Where skills are saved |
| --- | --- |
| GitHub Copilot / VS Code | `.github/skills/<skill-name>/SKILL.md` in the project |
| Claude Code | `.claude/skills/<skill-name>/SKILL.md` in the project |
| Codex | `.nci-skills/<skill-name>/SKILL.md`, plus a pointer added to `AGENTS.md` |
| Kiro or anything else | `.nci-skills/<skill-name>/SKILL.md` |

If you cannot tell which assistant you are, do not guess. Ask the user, and
offer the four options above in plain terms.

Then look at the current folder and note whether it is empty, whether it
contains source code, and whether it is a Git repository. Git is the system that
tracks changes to files over time. Report this in one short sentence.

Now tell the user that the skills you picked rely on some supporting programs,
and that you are going to check what is already installed before changing
anything.

Work out what is needed. If the catalog entry for a skill lists a `requires`
field, use that. Otherwise use this table:

| Skill | Needs |
| --- | --- |
| cloud-one-github-actions-lambda-deployment | `git`, `gh`, `python3`, `pip`, `aws`, `sam` |
| dependabot-report, code-scanning-report | `gh` |
| twistlock-nci | none beyond internet access |
| all others | none |

Check each one with a harmless version query such as `git --version` or
`sam --version`. **Do not install anything during this check.**

Present the result as a table with four columns: the tool, what it does in plain
English, whether it is already installed, and why this particular project needs
it. Use these descriptions:

| Tool | Plain-English description |
| --- | --- |
| `git` | Keeps a history of every change made to your files |
| `gh` | Lets your computer talk to GitHub from the command line |
| `python3` | Runs programs written in the Python language |
| `pip` | Downloads add-on packages for Python |
| `aws` | Lets your computer talk to Amazon Web Services, where Cloud One runs |
| `sam` | Packages your code and sends it to the cloud |

For each missing tool, and **before asking for permission**, state all six of
these:

1. What it is, in one sentence.
2. Why this specific project needs it, referring back to the user's answers.
3. The exact command you would run, shown in full.
4. Whether it changes the whole computer or only this project folder.
5. Roughly how long it takes and how large the download is.
6. How to undo it.

Then ask for permission **for that one tool only**. Never ask for blanket
approval to install several things at once. Offer exactly three choices:

- (a) Install it for me.
- (b) Show me the command and I will run it myself.
- (c) Skip it for now and note it as something that will block me later.

Installation rules, which are not negotiable:

- Use the right installer for the operating system: Homebrew on macOS, `apt` or
  `dnf` on Linux, `winget` on Windows.
- If Homebrew itself is missing on macOS, explain it first: "Homebrew is a
  package manager, which is like an app store for developer tools." Ask
  permission for Homebrew separately, as its own decision.
- For Python, prefer a project-local virtual environment over installing
  packages for the whole computer, and explain why: "This keeps the add-ons for
  this project separate, so it cannot break anything else on your machine."
- For Node.js, prefer installing inside the project over installing globally,
  for the same reason.
- Only download from official sources: `brew.sh`, `aws.amazon.com`,
  `python.org`, `nodejs.org`, `cli.github.com`. Never pipe a download from
  anywhere else straight into a shell.
- If a command needs `sudo`, which grants administrator rights over the entire
  computer, say so explicitly and ask a second time before running it.
- Never edit shell startup files such as `.zshrc` or `.bashrc` without asking.

After each install, run the version check again and report the confirmed result.
If it fails, explain the likely cause in plain language and link to the official
documentation. Do not retry the same command hoping for a different outcome.

### Step 5 of 8 — Install the skills

Ask permission before writing, naming the exact number of files and the exact
folder. Then, for each chosen skill:

1. Download it, using the same four-source order and the same caching rule from
   Step 2.
2. Save it to the location determined in Step 4.
3. If a file is already there, stop and ask. Show the user that a skill of that
   name already exists and offer to keep the existing one, replace it, or save
   the new one under a different name. Never overwrite silently.
4. Record where it came from in `.nci-skills/manifest.json`: the skill name, the
   web address it came from, the branch, and today's date. This is so anyone can
   later tell where these files came from and how old they are.

If you are running in Codex, also add a short line to `AGENTS.md` pointing at the
`.nci-skills` folder, so the skills are picked up in future sessions. Say that
you are doing this and why.

Report each file saved as you go.

### Step 6 of 8 — Build and run a hello world

Skip this step entirely if the user is not building an application, for example
if they answered that this is a documentation or governance task, or that they
are only reviewing something that already exists. Say that you are skipping it
and why.

Explain the point of this step before doing it:

> Before we build the real thing, we are going to build the smallest possible
> version that actually runs: one page that says hello, and one address that
> reports whether the application is healthy. If that works, everything
> underneath it is set up correctly. If it does not, we find out now, while it
> is still cheap to fix.

Ask permission to create the files, naming how many and where.

Build the smallest working application in the language chosen in Step 1, with
exactly two addresses:

- A main address that returns a short greeting including the application name.
- A health check address at `/health`.

**The health check is required for every application.** It is how NCI, and
anyone on call, finds out whether the application is alive without having to
understand what it does. It must return, in machine-readable form:

| Field | What it means |
| --- | --- |
| `status` | `ok` if everything it depends on is reachable, `degraded` otherwise |
| `app` | The application name |
| `version` | The version or the code revision it was built from |
| `checkedAt` | The date and time the check ran |
| `dependencies` | Each thing the application depends on, such as a database, and whether it could be reached |

If the user answered in Step 1 that the application needs to store information,
the database must appear in `dependencies` and must actually be checked. A health
check that always says `ok` is worse than no health check at all, because it
creates false confidence.

**Security rule for the health check.** It must never reveal secrets, passwords,
connection details, internal machine names, or error traces. It says whether
something is reachable. It never says how to reach it. This address is often
left open to the internet, so treat everything it returns as public.

Now run the application on the user's machine and call both addresses yourself.
Report what actually came back, in plain language: "I started it and asked it how
it was. It replied that it is healthy and that it can reach its database."

Do not claim it works unless you have called it and seen the response.

Do not deploy anything to the cloud in this step. That is offered separately in
Step 8.

Record how long this step took.

### Step 7 of 8 — Register the application

Skip this step if Step 6 was skipped, and say so.

Explain why, plainly:

> NCI needs a list of which applications exist, who is responsible for each one,
> how sensitive the information inside it is, and where to check whether it is
> running. Without that list, applications get forgotten, and forgotten
> applications are how security problems start. This takes about two minutes.

Ask for the details you do not already have, one at a time, in plain language.
"I don't know yet" is always acceptable; record it as unknown and raise it in
the final summary.

| What to ask | Why it is needed |
| --- | --- |
| What should this application be called? | So it can be identified in the list |
| Who owns it, and which division or office are they in? | So there is a named person responsible |
| What email address should someone use to reach the owner? | So problems reach a human |
| Has an information system security officer been assigned? | So security questions have an owner |

Everything else you already know: the repository address, the health check
address, who the application is for and whether it requires a sign-in, how
sensitive the data is from question 5, which skills were used, and today's date.

Write all of this to `app-registry.json` in the top level of the project. Record
these fields:

| Field | Source |
| --- | --- |
| `app` | Asked above |
| `description` | One sentence, from the user's answers |
| `owner`, `ownerOffice`, `contactEmail` | Asked above |
| `securityOfficer` | Asked above, or `unknown` |
| `repository` | The Git remote address, or `unknown` if not in a repository |
| `cloudOneTier`, `stackName` | From question 4, or `not yet deployed` |
| `healthCheckUrl` | The local address for now, updated on deployment |
| `audience` | From question 1: `self`, `named-group`, `nci-wide`, or `public` |
| `requiresSignIn` | From the question 1 follow-up: `true`, `false`, or `unknown` |
| `dataSensitivity` | From question 5: `public`, `internal`, or `pii-phi` |
| `createdDate` | Today |
| `skillsUsed` | The skills installed in Step 5 |
| `helloWorldElapsedMinutes` | Measured in Step 6 |

**Never put a password, key, token, or connection string in this file.** It is
an inventory record, not a configuration file. It will be committed alongside
the code and read by other people.

Describe what you wrote in plain sentences. Do not show the user the file
contents.

Then handle central registration. NCI intends to keep a central list in a
repository named `CBIIT/NCI-Skills-Registry`. Check whether it exists at
`https://api.github.com/repos/CBIIT/NCI-Skills-Registry`.

- If it exists, tell the user their entry can be submitted there and offer to
  prepare the submission. Do not submit anything without permission.
- If it does not exist, say so honestly:

> The central NCI application registry has not been created yet, so for now this
> record lives only in your project. That is a gap in NCI's setup rather than
> something you have done wrong. When the central registry exists, this same
> file can be submitted to it unchanged.

Never invent a registry address, and never claim the application has been
centrally registered when it has not.

### Step 8 of 8 — Summarise and hand off

Give a plain-English summary with these six headings, in this order:

1. **What you told me.** Three or four sentences restating their situation.
2. **What I installed.** Each skill, one line each, with its plain-English
   purpose and whether it is reviewed or a draft.
3. **Where it went.** The exact folder, and one sentence on what that folder
   means for the assistant they are using.
4. **What is running now.** Whether the hello world is running, what its two
   addresses are, and what the health check reported. If Step 6 was skipped, say
   why.
5. **How long it took.** The actual elapsed time, compared against the estimate
   you gave in Step 1. If it took materially longer, say what caused it. This is
   how the estimates get better over time.
6. **What happens next.** The single concrete action to take now. If they are
   deploying to Cloud One, offer it as its own decision: "The next step would be
   to put this in NCI's cloud so other people can reach it. That is a separate
   job and I have not started it. Would you like to do that now, or stop here?"
7. **What is missing.** Every tool they declined, every registry field recorded
   as unknown, the fact that the application is not yet centrally registered,
   every gap in the library, and anything else that will block them later. If
   there is nothing, say so.

Then stop. Do not deploy anything and do not start building features on top of
the hello world unless the user asks. This skill gets the work started; it does
not finish it.

## Quality Checklist

- [ ] Directly addresses request
- [ ] Matches requested format
- [ ] Assumptions are explicit
- [ ] No fabricated facts
- [ ] Safe and policy-aligned
- [ ] A time expectation was given in Step 1, before any work began
- [ ] All eight steps were announced before starting and reported after finishing
- [ ] In test mode: nothing was downloaded, installed, written, or run
- [ ] In test mode: every message was marked and every skipped action shown as
      `WOULD DO:`
- [ ] In test mode: no invented result was presented as a real one
- [ ] No code, JSON, or YAML was shown to the user, other than commands offered
      for approval
- [ ] Every acronym was defined the first time it appeared
- [ ] Questions were asked one at a time and each offered an "I'm not sure" path
- [ ] Every installed skill was given a one-sentence reason
- [ ] Every unreviewed draft skill was labelled as a draft
- [ ] Permission was obtained separately for each tool installed
- [ ] Permission was obtained before any file was written
- [ ] No file was overwritten without asking
- [ ] The hello world was actually run and both addresses actually called
- [ ] The health check reports real dependency status, not a fixed `ok`
- [ ] The health check exposes no secrets, hostnames, or error traces
- [ ] `app-registry.json` was written and contains no credentials
- [ ] Central registration was reported honestly as not yet available
- [ ] The final summary covered all seven headings, including actual elapsed time
- [ ] No skill path was used that did not come from the catalog, the file
      listing, or the built-in list in Step 2

## Guardrails

- No secrets or sensitive data in outputs.
- Don't invent policy/compliance requirements.
- Flag uncertainty clearly.
- Never invent a skill name or file path. Every skill you mention must come from
  the live catalog, the live file listing, or the built-in list in Step 2. If
  you cannot find something, say you cannot find it.
- Never treat a single "not found" from `raw.githubusercontent.com` as proof
  that a file is absent. Confirm through the GitHub API first.
- Never install software without explicit, per-tool permission.
- Never run a command requiring administrator rights without asking a second
  time and saying plainly what it affects.
- Never write or overwrite a file without asking first.
- Always label skills from the `intake` folder as submitted but not yet
  reviewed.
- Do not give security, privacy, or compliance rulings. Where the library has no
  reviewed skill, say so and point the user at their information system security
  officer and at the skill change request process.
- Every application you create must have a health check. Never skip it because
  the application is small or temporary.
- A health check must report the real state of what it depends on. Never write
  one that always returns `ok`.
- A health check must never expose secrets, passwords, connection strings,
  internal machine names, or error traces. Assume anyone on the internet can
  read it.
- Never put credentials of any kind in `app-registry.json`.
- Never claim an application has been registered centrally, deployed, or is
  running unless you have confirmed it yourself.
- In test mode, never take any action, and never describe a simulated result as
  though it really happened.
- Do not deploy anything to the cloud as part of this skill. Offer it as a
  separate decision at the end.
- Do not build features beyond the hello world. Hand off at the end of Step 8.

### Glossary

Define these inline the first time each is used.

| Term | Plain-English meaning |
| --- | --- |
| Repository, or repo | A folder of files whose full history of changes is tracked |
| Git | The system that tracks those changes |
| GitHub | The website where NCI stores repositories |
| CI/CD | Automatically checking and publishing code whenever it changes |
| Cloud One | NCI's approved cloud hosting environment |
| Lambda | A way of running code in the cloud without managing a server |
| SAM | A tool that packages code and sends it to the cloud |
| OIDC | A way for GitHub to prove its identity to the cloud without a stored password |
| IAM | The rules controlling who is allowed to do what in the cloud |
| PII | Personally identifiable information |
| PHI | Protected health information |
| Package manager | An app store for developer tools, such as Homebrew |
| Container | A self-contained package that runs the same way on any machine |
| Frontmatter | The labelled information at the very top of a skill file |
| Hello world | The smallest possible working version of an application, built to prove the setup works |
| Health check | A single address that reports whether an application is alive and what it can reach |
| Endpoint, or route | One address an application answers on |
| App registry | The list of which applications exist, who owns them, and where to check on them |
| Dependency | Something an application needs in order to work, such as a database |
