# Sprint019.2 AI Evidence Audit Report

## Evidence model

File evidence is stored and surfaced through:

- `document_chunks`
- `drive_file_chunks`
- `knowledge_items`
- `drive_file_ai_summaries`

Each processed document can produce location-labeled chunks such as `段落 1`, enabling file detail pages and Copilot-style entry points to show evidence rather than unsupported conclusions.

## AI conclusion policy

- File questions route through Copilot with file/folder context prompts.
- File detail pages show extracted evidence chunks.
- If a file cannot be extracted, the UI states why evidence is unavailable.
- Unsupported preview types do not produce hidden conclusions.

## Object evidence

Business object links are split into:

- Confirmed manual links: `drive_file_object_links`.
- Suggested links: `drive_file_link_suggestions`.

Suggestions are generated from filename/text matches and remain pending until confirmed.

## Audit result

The test processing run produced:

- 1 evidence chunk.
- 1 knowledge item.
- 1 AI summary record.

No evidence-free business conclusion path was added.

