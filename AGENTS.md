# AGENTS.md

Project-specific instructions for coding agents working in this repository.

## Think Before Coding

Don't assume. Don't hide confusion. Surface tradeoffs.

- State assumptions explicitly.
- If multiple interpretations exist, present them instead of picking silently.
- If something is unclear, ask before implementing.
- If a simpler approach exists, say so.

## Simplicity First

Write the minimum code that solves the requested problem.

- No features beyond what was asked.
- No speculative abstractions.
- No unnecessary configurability.
- Prefer locally understandable logic.

Ask: would a strong engineer consider this overcomplicated? If yes, simplify it.

## Surgical Changes

Touch only what is required for the task.

- Do not refactor unrelated code unless asked.
- Do not rewrite adjacent comments, formatting, or structure without need.
- Match the existing style of the repository.
- Clean up only the unused code created by your own changes.

Every changed line should trace back to the task.

## Goal-Driven Execution

Turn tasks into verifiable outcomes.

- Define what success looks like before changing code.
- Prefer tests or checks when they are appropriate.
- For multi-step work, keep a short plan and verify each step.
- Do not stop at implementation; verify the result.

## Workflow Hygiene

- Before each `git add` and `git commit`, check whether `.gitignore` needs to be updated.
- After each vibe coding session or meaningful implementation pass, check whether `PROJECT_LOG.md` should be updated.

## Project-Specific Rules

### Environment

- Use the repository-root `.venv` as the default Python environment.
- When installing Python dependencies, keep `requirements.txt` aligned with the environment.
- Python 3.7+ is the minimum supported version.

### Code Style

- Follow PEP 8 conventions for Python code.
- Use descriptive variable names that convey intent.
- Keep functions focused and under 50 lines when possible.
- Prefer explicit imports over wildcard imports.
- Use type hints for function signatures in new code.

### BibTeX Processing

- Always handle UTF-8 encoding explicitly when reading/writing files.
- Use `bibtexparser` library for parsing BibTeX files.
- Preserve user's original BibTeX formatting choices when possible.
- Sort citation keys chronologically by year when presenting lists.
- Handle malformed BibTeX entries gracefully with informative error messages.

### Command-Line Tools

- Use `argparse` for all command-line interfaces.
- Provide helpful defaults and clear help text.
- Print progress information for long-running operations.
- Use exit code 0 for success, non-zero for errors.
- Write output files atomically when possible to avoid corruption.

### INSPIRE Integration

- Respect rate limits when querying INSPIRE-HEP API.
- Implement retry logic with exponential backoff for network operations.
- Cache results locally when appropriate to reduce API calls.
- Provide detailed reports for manual review of ambiguous matches.

### Testing and Verification

- Test with sample BibTeX files from `examples/` directory when available.
- Verify deduplication logic doesn't lose valid entries.
- Check that UTF-8 encoding is preserved correctly.
- Ensure citation keys maintain consistent format (e.g., `Author:YYYY` pattern).

## Documentation Maintenance

- Keep `SPEC.md` aligned with structure changes.
- Update `PROJECT_LOG.md` when a meaningful change is made.
- Update `README.md` if user-facing behavior changes.
- Keep docstrings synchronized with function behavior.

## Adding New Features

When adding new commands or features:

1. Place command-line tools in `src/commands/`
2. Place shared utilities in `src/core/`
3. Place INSPIRE-specific code in `src/inspire/`
4. Update `SPEC.md` with the new module
5. Update `README.md` with usage examples
6. Add dependencies to `requirements.txt` if needed
