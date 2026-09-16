---
name: nci-startup
description: Use this skill at the start of an NCI skill session to check registration state and initiate registration when the skill is new or materially changed. It helps keep the NCI Skills Registry current without claiming that a change was merged or approved.
author: CBIIT
subject_matter_expert: CBIIT
Language: Markdown, JSON
Framework: GitHub Actions, JSON Schema

---

# NCI Startup

## Purpose

Provide the startup step for NCI skills. Before the requested skill work begins, check whether the skill is registered and whether its registry metadata reflects the current version or material change. Invoke `nci-skill-registration` when registration is needed.

## When to Use

Use this skill when:

- An NCI skill session is starting.
- The current skill has no confirmed registry entry.
- The current skill has a major or material change since its last registration.

Do not use this skill when:

- The session is not operating an NCI skill.
- Registration metadata is already current and no material change has occurred.
- Required registration information is missing and cannot be verified.

## Inputs

- The current skill's stable identifier and source repository.
- The current skill metadata, version, or source revision.
- Owner, creation date, last-updated date, deployment status, and environment URLs.
- Existing registry entry, when available.

## Output

Return:

1. Registration status: current, newly prepared, update prepared, or blocked.
2. The registration result from `nci-skill-registration`, when invoked.
3. Any missing metadata, assumptions, or review and authentication dependencies.

Do not block the main skill task solely because a non-destructive registration check cannot reach the registry. Report the limitation and continue unless the caller requires registration to succeed first.

## Workflow

1. Identify the current skill and read its registration metadata.
2. Look up the stable skill ID in the NCI Skills Registry.
3. Compare the current metadata, version or revision, owner, dates, deployment status, and environment URLs with the registry entry.
4. If the entry is missing or a material change is detected, invoke `nci-skill-registration`.
5. Record whether a registry update was prepared, submitted as a pull request, merged, or blocked. Do not infer later states from earlier ones.
6. Continue with the requested skill workflow after reporting the registration result.

## Quality Checklist

- [ ] The current skill was identified from its own metadata, not guessed.
- [ ] A stable skill ID was used for the lookup.
- [ ] No registry update was created for a no-op.
- [ ] Material changes were handed to `nci-skill-registration`.
- [ ] Registration state was reported accurately.
- [ ] No secrets or sensitive data were exposed.

## Guardrails

- Do not invent a registry entry, owner, version, deployment status, or URL.
- Do not claim that registration is complete until the repository confirms it.
- Do not commit directly to a protected registry branch.
- Do not request or include personal access tokens.
- Flag unavailable registry access or missing metadata clearly.

## Additional Links

- [NCI Skill Registration](nci-skill-registration.md)
- [NCI-Skills-Library](https://github.com/CBIIT/NCI-Skills-Library)
- [NCI Skills Registry](https://github.com/CBIIT/NCI-Skills-Registry)