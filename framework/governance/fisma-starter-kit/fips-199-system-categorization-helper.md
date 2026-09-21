# FIPS 199 System Categorization Helper

Use this helper to collect draft information for the official NIH FIPS 199 System Categorization template. This is not the official form.

## Source Template

- Official template: `reference/nci-fisma-starter-kit/NIH FIPS 199 System Categorization Template (2).docx`
- Example reference: `reference/nci-fisma-starter-kit/ERIE FIPS 199 Categorization Worksheet ATO 06-09-2026.docx`

## System Information

| Field | Draft Value | Source |
|---|---|---|
| System Name |  | Startup project name |
| IC | National Cancer Institute | Default |
| System Type |  | User selection and generated architecture |
| Date |  | Current date |
| Overall System Security Category |  | Derived from high water mark |
| SDLC Status | Development | Cloud One dev bootstrap default |
| Confidentiality Impact |  | Data sensitivity and FIPS 199 analysis |
| Integrity Impact |  | Mission and data integrity analysis |
| Availability Impact |  | BIA and recovery analysis |
| System Description |  | Startup summary and generated app type |

## Contacts

| Role | Name | Email | Phone | Source |
|---|---|---|---|---|
| NCI CIO |  |  |  | Official template or user confirmation |
| NCI ISSO |  |  |  | Official template or user confirmation |
| System Owner |  |  |  | Registry/startup context |
| NCI Privacy Coordinator |  |  |  | Official template or user confirmation |

## Information Types

For each information type, capture the provisional impact levels from NIST SP 800-60 and any adjusted levels.

| Information Type | Provisional Confidentiality | Provisional Integrity | Provisional Availability | Adjusted Confidentiality | Adjusted Integrity | Adjusted Availability | Rationale |
|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |

## Suggested Starter Assumptions For Generated Cloud One Apps

Use these only as draft assumptions requiring owner/security review:

- System type is usually a major application when the generated app supports a business workflow.
- SDLC status is Development for the generated Cloud One non-production deployment.
- Overall security category is the high water mark across Confidentiality, Integrity, and Availability.
- If the app does not process PII, PHI, financial, credential, or mission-critical operational data, initial CIA values may be Low, pending owner review.
- If NIH SSO, user profiles, sensitive program data, or operational decision support are introduced, reassess Confidentiality and Integrity.

## Open Questions

- What information types from NIST SP 800-60 apply?
- Does the app process PII, PHI, credentials, research data, financial data, or controlled data?
- What would happen if data were disclosed, modified, unavailable, or destroyed?
- Does the business owner agree with the CIA impact levels?

## Validation Checklist

- [ ] System owner reviewed the system description.
- [ ] Information types were selected or documented as unknown.
- [ ] CIA values were assigned for each information type.
- [ ] High water mark was calculated.
- [ ] Impact adjustment rationales were documented.
- [ ] Draft values were transferred to the official template.
