# E-Authentication Risk Assessment Helper

Use this helper to collect draft information for the official HHS E-Authentication Risk Assessment template. This is not the official form.

## Source Template

- Official template: `reference/nci-fisma-starter-kit/HHS E-Authentication Template (2).pdf`

The PDF is an official reference template. If the PDF form fields are difficult to extract automatically, use this helper as an intake worksheet and transfer reviewed answers into the official PDF.

## System And Access Context

| Field | Draft Value | Source |
|---|---|---|
| System Name |  | Startup project name |
| System Acronym |  | Project slug or registry identifier |
| Application Type | Web Page / REST API Interface / Local Command Line Script | Startup answer |
| Hosting Target | Local / GitHub Pages / Cloud One Development | Startup answer |
| User Population |  | Owner input |
| Authentication Method | None / NIH SSO / GitHub / Other | Startup/deployment context |
| External Users | Yes / No / Unknown | Owner input |

## Authentication Screening

| Question | Draft Answer | Notes |
|---|---|---|
| Does the application require users to sign in? |  |  |
| Is NIH SSO used? |  |  |
| Are privileged administrator actions available? |  |  |
| Does the app expose public unauthenticated content? |  |  |
| Does the app process sensitive data after authentication? |  | Link to PIA/FIPS |
| Are API clients authenticated separately from browser users? |  |  |
| Are service accounts or machine identities used? |  |  |

## Risk Factors

| Risk Factor | Draft Assessment | Evidence |
|---|---|---|
| Harm from unauthorized access |  |  |
| Harm from impersonation |  |  |
| Harm from repudiation or transaction dispute |  |  |
| Harm from disclosure of sensitive data |  |  |
| Harm from unauthorized modification |  |  |
| Harm from service disruption |  |  |

## Assurance And Controls Starter Notes

| Topic | Draft Answer |
|---|---|
| Identity proofing needed? |  |
| Credential strength needed? |  |
| MFA required? |  |
| Session timeout or re-authentication needs? |  |
| Audit logging for sign-in and privileged actions? |  |
| Role-based access control needed? |  |

## Initial Starter Guidance

- If the generated app is local-only and has no login, e-authentication risk may be not applicable, pending owner/security review.
- If the app uses NIH SSO, record NIH SSO as the identity provider and document any application roles or authorization checks.
- If the app exposes only public static content, note that no user authentication is required, but publishing controls still apply.
- If the app has administrative functions, sensitive data, or API write operations, require stronger authentication and audit review.

## Validation Checklist

- [ ] User populations were identified.
- [ ] Authentication method was documented.
- [ ] Privileged functions were identified.
- [ ] Sensitive data and transaction risks were considered.
- [ ] Draft answers were transferred to the official E-Authentication template.
