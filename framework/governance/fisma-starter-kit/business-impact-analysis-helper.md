# Business Impact Analysis Helper

Use this helper to collect draft information for the official NCI Business Impact Analysis template. This is not the official form.

## Source Template

- Official template: `reference/nci-fisma-starter-kit/NCI Business Impact Analysis Template.docx`
- Example reference: `reference/nci-fisma-starter-kit/ERIE NCI Business Impact Analysis 06-09-2026.docx`

## Document Metadata

| Field | Draft Value | Source |
|---|---|---|
| System Name |  | Startup project name |
| System Abbreviation |  | Project slug or registry identifier |
| IC | NCI | Default |
| Security Categorization |  | FIPS 199 helper |
| Version | 1.0 | Default |
| Date |  | Current date |
| Prepared By |  | Author/user context |

## Approval Contacts

| Role | Name | Email | Date | Source |
|---|---|---|---|---|
| System Owner |  |  |  | Registry/startup context |
| Information System Security Officer |  |  |  | User/security office input |
| IC CIO |  |  |  | Official template or user confirmation |

## System Name And Organization

| Field | Draft Value |
|---|---|
| Information System Name |  |
| Information System Abbreviation |  |
| Responsible NIH Organization |  |
| NCI DOC |  |

## System Type And Purpose

Describe the generated application in plain language.

| Field | Draft Value |
|---|---|
| Application Type | Web Page / REST API Interface / Local Command Line Script |
| Runtime | Python / Node.js |
| Hosting Target | Local / GitHub Pages / Cloud One Development |
| System Description |  |
| Primary Users |  |
| Supported Business Function |  |

## Operational Status

| Field | Draft Value |
|---|---|
| SDLC Phase | Development |
| Operational Status | New / Development / Pilot / Existing |
| Registry Status | Registered / Unregistered for now |
| GitHub Repository |  |
| Cloud One Stack |  |
| Endpoint |  |

## Security Categorization

| Impact Area | Draft Value | Source |
|---|---|---|
| Confidentiality |  | FIPS 199 helper |
| Integrity |  | FIPS 199 helper |
| Availability |  | FIPS 199 helper |
| Overall |  | High water mark |

## Step 1: Components And Recovery Criticality

| Component | Description | Business Function | Criticality | Notes |
|---|---|---|---|---|
| Application code | Generated app code and runtime |  |  |  |
| GitHub repository | Source control and deployment workflow |  |  |  |
| Cloud One Lambda | Runtime compute for deployed app |  |  | Cloud One targets only |
| API Gateway | HTTP endpoint and routing |  |  | API/web Cloud One targets only |
| CloudWatch Logs | Runtime logs |  |  | Cloud One targets only |

## Outage Impacts

Use the official template impact categories when completing the final BIA.

| Impact Category | Impact If Unavailable | Severity | Notes |
|---|---|---|---|
| Mission or business process |  |  |  |
| User productivity |  |  |  |
| Data access |  |  |  |
| External dependencies |  |  |  |
| Compliance or reporting |  |  |  |
| Overall impact |  |  |  |

## Downtime Estimates

| Component | MTD | RTO | RPO | Basis |
|---|---|---|---|---|
| Application |  |  |  |  |
| Source repository |  |  |  |  |
| Deployment workflow |  |  |  |  |
| Cloud runtime |  |  |  | Cloud One targets only |

## Step 2: Resource Requirements

| Resource Type | Draft Value |
|---|---|
| Physical or host locations | Cloud One Development, if selected |
| Virtual resources | Lambda, API Gateway, CloudWatch, GitHub Actions |
| Personnel | System owner, developer, ISSO, operations support |
| Software | Runtime, dependencies, SAM template, GitHub Actions workflow |
| Data files |  |
| Backups | Source repository and deployment artifacts |

## Step 3: Recovery Priorities

| Priority | Resource Or Component | Recovery Target | Notes |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |

## Validation Checklist

- [ ] System name and abbreviation are consistent with registry and GitHub.
- [ ] FIPS 199 impact levels are copied from the categorization helper.
- [ ] Components reflect the generated architecture.
- [ ] MTD, RTO, and RPO are owner-reviewed.
- [ ] Cloud One resources are listed only when deployed to Cloud One.
- [ ] Draft values were transferred to the official BIA template.
