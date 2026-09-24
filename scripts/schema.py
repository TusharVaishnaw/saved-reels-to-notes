"""Single adaptive schema for all reels. No per-collection prompt needed."""

EXTRACTION_SCHEMA = {
    "topic": "short title of the core idea",
    "summary": "2-3 sentence summary",
    "category": "one of: business-idea | tool | tutorial | recipe | fitness | "
                 "finance | other (pick closest, or invent short one)",
    "tools_mentioned": ["list of named tools/apps/products"],
    "steps_or_method": ["ordered steps if instructional, else []"],
    "key_claims": ["specific factual claims or numbers stated"],
    "resources_links": ["any URLs, handles, or named resources"],
    "actionable_takeaway": "one sentence: what should the viewer actually do",
    "tags": ["3-6 short lowercase tags"],
}

EXTRACTION_PROMPT = """You are extracting structured notes from an Instagram \
Reel transcript. Fill this exact JSON schema. If a field has no info, use \
an empty string or empty list. Never invent information not present in the \
transcript or caption.

Schema:
{schema}

Transcript:
{transcript}

Caption (if any):
{caption}

Return ONLY valid JSON matching the schema, nothing else."""
