# NCI Skills Workflow

1. Submit a request using the **Skill change** issue form.
2. The NCI-Skills-Triage group validates the request, sets its priority, and assigns an individual curator.
3. The curator updates the requested skill through a pull request that links the issue with `Closes #<issue-number>`.
4. GitHub requests review based on `.github/CODEOWNERS`.
5. The NCI-Skills-Release group approves release-ready pull requests. Merge closes the linked issue.

All changes to the skills library are made through pull requests. Direct changes to `main` are not part of this workflow.