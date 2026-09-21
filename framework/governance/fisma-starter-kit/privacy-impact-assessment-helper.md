# Privacy Impact Assessment Helper

Use this helper to collect draft information for the official Privacy Impact Assessment template. This is not the official form.

## Source Template

- Official template: `reference/nci-fisma-starter-kit/PIA-NIH_NCI_System_Acronym_With_Model_Language_v2.pdf`

The PDF is an official reference template. If the PDF form fields are difficult to extract automatically, use this helper as an intake worksheet and transfer reviewed answers into the official PDF.

## System Overview

| Field | Draft Value | Source |
|---|---|---|
| System Name |  | Startup project name |
| System Acronym |  | Project slug or registry identifier |
| NCI DOC |  | Registry/startup context |
| System Owner |  | Registry/startup context |
| Contact Email |  | Trusted identity context or user input |
| Hosting Environment | Local / GitHub Pages / Cloud One Development | Startup target |
| Application Type | Web Page / REST API Interface / Local Command Line Script | Startup answer |

## Privacy Screening

| Question | Draft Answer | Notes |
|---|---|---|
| Does the system collect information about individuals? |  |  |
| Does it collect or store PII? |  |  |
| Does it process PHI, research participant data, or sensitive program data? |  |  |
| Does it authenticate users? |  | NIH SSO, GitHub, anonymous, none |
| Does it collect logs that include usernames, emails, IP addresses, or user activity? |  |  |
| Does it share data with another system or organization? |  |  |
| Does it expose public web content? |  |  |
| Does it use AI-generated or AI-assisted code? |  | Capture provenance separately |

## Data Elements

| Data Element | Collected? | Source | Purpose | Retention | Sensitive? |
|---|---|---|---|---|---|
| Name |  |  |  |  |  |
| NIH email |  |  |  |  |  |
| GitHub username |  |  |  |  |  |
| Role or group membership |  |  |  |  |  |
| IP address |  |  |  |  |  |
| Application logs |  |  |  |  |  |
| Business data |  |  |  |  |  |

## Authority, Purpose, And Use

| Topic | Draft Answer |
|---|---|
| Why is information collected? |  |
| What authority permits collection? |  |
| How is information used? |  |
| Who can access the information? |  |
| How is information protected? |  |
| How long is information retained? |  |

## Access And Disclosure

| Question | Draft Answer |
|---|---|
| Is access limited by role? |  |
| Is NIH SSO used? |  |
| Are users outside NCI expected? |  |
| Is information disclosed outside NIH/NCI? |  |
| Are there interconnections or APIs? |  |

## Initial Starter Guidance

- If the generated app is only a Hello World baseline and stores no user data, mark PII collection as none, pending confirmation.
- If NIH SSO is enabled, record NIH email and identity attributes as potential PII.
- If CloudWatch logs include usernames, emails, IP addresses, request paths, or request payloads, document them as log data elements.
- Do not assume no PII solely because the app is small; review authentication, logging, and form fields.

## Validation Checklist

- [ ] Data elements were reviewed by the system owner.
- [ ] Authentication and logging were reviewed for PII.
- [ ] Any NIH SSO attributes are documented.
- [ ] Any interconnections are documented.
- [ ] Draft answers were transferred to the official PIA template.
