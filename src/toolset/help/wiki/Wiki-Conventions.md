# Wiki conventions

All PyKotor wiki edits — whether by a human or by an AI agent — follow these style and structure conventions. Apply them when adding or editing any page.

## What this page is for

Use this page as the source of truth for wiki structure and editing standards.

- Main entry points: [Home](Home), [Concepts](Concepts), [Resource formats and resolution](Resource-Formats-and-Resolution), and [Reverse Engineering Findings](reverse_engineering_findings).
- Page types: reference pages, guides, and tool syntax or readme pages.
- Maintenance status belongs in the live wiki, not in detached planning notes.

## Core rules

1. One page owns each topic. If a topic already has a canonical page, summarize briefly and link to it.
2. Do not duplicate long explanations. Summary pages stay shorter and narrower than the page they point to.
3. Do not lose distinct information when deduplicating. Merge it intentionally or keep a justified companion or archive page.
4. Preserve source artifacts. `Bioware-Aurora-*` pages and [TSLPatcher's-Official-Readme](TSLPatcher's-Official-Readme) are citation targets, not rewrite targets.
5. Hubs route. Canonical pages explain. Archive pages preserve provenance.
6. State claims at the confidence level the evidence supports. Use `inferred`, `unverified`, or similar when needed.

## Current priorities

- Keep hub pages short and routing-focused.
- Keep [Concepts](Concepts) and format reference pages as the shortest path to core information.
- Keep reverse-engineering archives subordinate to [Reverse Engineering Findings](reverse_engineering_findings).
- Resolve or isolate TODO-marked reverse-engineering notes so readers can tell what is verified.

## Page structure

### Naming

- Use consistent names for recurring page types: `Format-Name` such as `GFF-ARE` or `2DA-File-Format`, and `Tool-Feature` such as `TSLPatcher-InstallList-Syntax`.
- Do not switch names for the same concept across pages.

### Headings

- One H1 per page.
- Use H2 for main sections and H3 for subsections. Do not skip levels.
- Use sentence case for headings.
- Do not rename linked headings casually. If you change one, update inbound anchor links.

### Page layout

- Long reference pages should usually follow: Overview, Structure or fields, Examples if useful, then `### See also`.
- Keep exactly one `### See also` section at the end of the page.
- `See also` should usually contain 3 to 8 closely related internal links.
- Format pages should include a clear structure or fields section. If layout is fixed, include offsets, total length, or byte ranges.

## Canonical pages and cross-links

Use these pages instead of re-explaining the same material elsewhere.

- [Concepts](Concepts): resource resolution order, ResRef, override, BIF and KEY pairings, MOD archives, GFF and 2DA families, language IDs.
- [Resource formats and resolution](Resource-Formats-and-Resolution): format index and resource type ID table.
- [Container-Formats#key](Container-Formats#key): KEY binary layout.
- [GFF-File-Format](GFF-File-Format): GFF structure and data types.
- [2DA-File-Format](2DA-File-Format): 2DA structure.

Cross-link rules:

- Formats resolved by ResRef should link to [Concepts#resource-resolution-order](Concepts#resource-resolution-order).
- Pages that mention ResRef storage should link to [GFF-File-Format#gff-data-types](GFF-File-Format#gff-data-types) when relevant.
- If an official BioWare spec exists, link to it and document only KotOR-specific quirks, extensions, or tool behavior.

## Links and citations

### Internal and external links

- Internal wiki links are extension-less. Example: `[Concepts](Concepts)`, not `](Concepts.md)`.
- Internal targets must match the real wiki page name and anchor.
- External links use HTTPS and should prefer canonical upstream URLs.
- Do not use vague link labels like `here`, `this`, or `source`.
- If the purpose of a link is not obvious from the link text, explain it in the same sentence or list item.
- For community sources, prefer specific threads or file pages over site homepages.

### Evidence rules

- Navigation links help readers move around. They do not prove claims.
- Non-trivial factual claims, behavior descriptions, and workflow recommendations need inline evidence in the same sentence or paragraph.
- Use direct inline citation markers with live URLs whenever possible. Preferred pattern: `...cross-platform support [1](https://example.com/source) [2](https://example.com/second-source)`.
- Do not rely on detached `References`, `Sources`, `Verified against`, `Implementation`, `Vendor implementations`, or `Community context` sections to prove body text.
- Do not leave raw URLs with no explanation.
- If no evidence is available, say so explicitly instead of asserting the claim as fact.
- Prefer direct page, thread, file, section, or permalink URLs over repository roots or site homepages.
- If two sources support the same sentence, cite both in that sentence instead of moving them to a separate block.
- `See also` is navigation only. It should not carry the page's evidence burden.

Write source-backed facts as normal prose. The citation marker belongs where the reader needs it, not in a contributor-only appendix. Avoid sentences that sound like process notes or model output, such as `use this as evidence of real-world workflow expectations`, `verified against source files`, `community context`, or `vendor implementations`. State the fact plainly and attach the source to that sentence.

Example:

- Weak: `HoloPatcher is used in community releases. See references below.`
- Strong: `KOTOR 1 Community Patch switched from TSLPatcher to HoloPatcher in version 1.10.0 for additional patching features, bug fixes, and cross-platform support [1](https://deadlystream.com/files/file/1258-kotor-1-community-patch/).`

If a page genuinely needs bibliographic notes beyond direct inline links, keep them compact and place them at the end without turning them into a second prose section. Use that only when inline URL markers are not enough.

## Special cases

### Preserved sources

- Do not modernize or quietly rewrite `Bioware-Aurora-*` pages.
- Do not modernize or paraphrase [TSLPatcher's-Official-Readme](TSLPatcher's-Official-Readme) in place.
- Add new interpretation in a companion page, hub page, or canonical reference page that links back to the preserved source.

### Community research

- Deadly Stream search can fail with `site:deadlystream.com` even when content exists. Retry without `site:` and filter results manually.
- LucasForums Archive is useful for historical threads, but pair archival advice with current wiki or HoloPatcher links.
- PCGamingWiki is acceptable for player paths, widescreen, and OS quirks. It is not authority for binary layout.
- For large wiki batches, record which searches were empty and which worked so the next editor does not repeat dead queries.

### BWM and implementation notes

- On BWM pages and other deep technical pages, implementation evidence still belongs next to the claim it supports. If multiple implementations are compared, introduce them in the sentence itself rather than under a detached heading.
- The normative spec remains reverse engineering plus pipeline evidence, per the [authoritative BWM policy](https://github.com/OldRepublicDevs/PyKotor/blob/main/docs/solutions/documentation/authoritative-bwm-wiki-from-re-and-pipelines.md).

### Images

- Prefer `raw.githubusercontent.com` image URLs pinned to a commit SHA or tag.
- Branch-based image URLs are allowed only when maintainers accept drift.
- Broken image URLs also break Holocron's packaged help.

## Verification

From the repo root, with the `wiki` submodule initialized:

1. Run `python helper_scripts/wiki_scripts/validate_markdown_links.py` for internal targets and anchors.
2. Run `python helper_scripts/wiki_scripts/verify_anchors.py` when headings or a TOC changed.
3. Run `python helper_scripts/wiki_scripts/verify_toc.py` when a page has or depends on a TOC.
4. Run `python helper_scripts/wiki_scripts/audit_markdown_link_relevance.py` for descriptive-link and local-context checks.
5. Run `markdownlint-cli2` on touched files.

Before keeping overlapping pages, confirm that one page is clearly canonical and the others are clearly summary, companion, or archive-support pages.

## Checklist

- [ ] One H1 only; headings use sentence case; no skipped levels.
- [ ] Internal links are extension-less and correct.
- [ ] External links are HTTPS, canonical where possible, and locally explained when needed.
- [ ] The page has one clear scope and does not restate a canonical page.
- [ ] `### See also` appears once at the end.
- [ ] Reader-facing factual claims have inline evidence with direct URLs.
- [ ] The page does not use detached evidence headings such as `Verified against`, `Implementation`, `Vendor implementations`, `Community context`, or mid-page `References` blocks.
- [ ] Format pages include structure or fields, and offsets or lengths when relevant.
- [ ] Preserved-source pages remain preserved; new interpretation lives elsewhere.

## Templates

Use these section outlines when creating new pages.

### Reference page

```markdown
# [Format name] file format

Brief overview (what the format is, where it is used).

Back non-trivial factual claims with inline citation markers and direct URLs.

If this page is not the exhaustive format page, add one short sentence near the top linking to the canonical exhaustive page.

## Structure / fields

(File layout, data types, tables.)

## Examples

(Optional: short examples or code snippets.)

### See also

- [Related format](2DA-File-Format)
- [Parent concept](Concepts)
```

### Guide page

```markdown
# [Task or feature name]

Goal: one sentence describing what the reader will achieve.

Back workflow guidance and historical claims with inline citation markers and direct URLs.

If a canonical reference page contains the full background or exhaustive explanation, link to it near the top instead of repeating that material here.

## Prerequisites

(Optional: tools, prior reading.)

## Steps

1. First step.
2. Second step.

### See also

- [Related guide](HoloPatcher#installing-mods)
```

### Embedded walkthrough

Use this when adding a **P0/P1-style** section to a guide (e.g. HoloPatcher readme, Concepts, KotorDiff)—**do not** create a new wiki file for a short walkthrough.

```markdown
## [Walkthrough title]

**Goal:** One sentence.

**Prerequisites:** Links to tools + SSOT pages.

**Canonical background:** Link to the exhaustive reference page if this walkthrough depends on it.

**Steps:** Numbered, linking out to syntax pages instead of duplicating them.

**Verify in-game:** Concrete check (load module, UI spot, etc.).

**Alternatives:** Other tools or workflows (KotOR Tool, manual override, CLI-only).

**Common failures:** Install path mistakes, duplicate merges, wrong capsule vs override—link to Concepts / Installing guides.
```

### See also

- [Home](Home) -- Wiki overview and format index
- [Concepts](Concepts) -- Resource resolution, ResRef, override, BIF/KEY, MOD/ERF, GFF, 2DA, language IDs
- [Resource formats and resolution](Resource-Formats-and-Resolution) -- Format index, type ID table, resolution hub
- [Container-Formats#key](Container-Formats#key)
- [GFF-File-Format](GFF-File-Format)
- [2DA-File-Format](2DA-File-Format) -- Canonical format pages
- [TSLPatcher's-Official-Readme](TSLPatcher's-Official-Readme)
- [HoloPatcher-README-for-mod-developers](HoloPatcher#mod-developers) -- Tool docs
