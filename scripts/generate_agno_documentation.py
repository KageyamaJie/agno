#!/usr/bin/env python3
"""
Utility to generate a comprehensive PDF manual for the Agno framework.

Steps:
1. Transform the downloaded MDX export (llms-full.txt) into Markdown that is
   easier to read for beginners by removing custom components and keeping the
   relevant content.
2. Prepend an introductory section with learning guidance and a table of
   contents placeholder.
3. Render the Markdown into a styled PDF using a lightweight FPDF layout.

Usage:
    python scripts/generate_agno_documentation.py

Prerequisites:
    python3 -m pip install fpdf2
"""

from __future__ import annotations

import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Dict, List, Optional

from fpdf import FPDF
from fpdf.errors import FPDFException


ROOT = Path(__file__).resolve().parent.parent
SOURCE_PATH = ROOT / "tmp" / "llms-full.txt"
DOCS_DIR = ROOT / "docs"
MARKDOWN_PATH = DOCS_DIR / "agno_api_documentation.md"
PDF_PATH = DOCS_DIR / "agno_api_documentation.pdf"

ATTR_RE = re.compile(r'([A-Za-z0-9_.:-]+)="([^"]*)"')
INLINE_LINK_RE = re.compile(r'<Link href="([^"]+)">(.*?)</Link>')
INLINE_A_RE = re.compile(r'<a href="([^"]+)">(.*?)</a>')
INLINE_STRONG_RE = re.compile(r"<strong>(.*?)</strong>")
INLINE_EM_RE = re.compile(r"<em>(.*?)</em>")
INLINE_CODE_RE = re.compile(r"<code>(.*?)</code>")
INLINE_BADGE_RE = re.compile(r"<Badge[^>]*>(.*?)</Badge>")
INLINE_BUTTON_RE = re.compile(r'<Button href="([^"]+)"[^>]*>(.*?)</Button>')
INLINE_RESOURCE_RE = re.compile(r'<Resource href="([^"]+)"[^>]*>(.*?)</Resource>')
PLACEHOLDER_RE = re.compile(r"<([A-Za-z0-9_-]+)>")
RESPONSE_FIELD_OPEN_RE = re.compile(
    r'<ResponseField\s+name="([^"]+)"\s+type="([^"]+)">\s*'
)


def parse_attrs(tag_line: str) -> Dict[str, str]:
    """Extract attributes from a component tag into a dictionary."""
    return {key: value for key, value in ATTR_RE.findall(tag_line)}


def convert_inline_markup(text: str) -> str:
    """Convert inline MDX/HTML fragments into Markdown equivalents."""
    text = INLINE_LINK_RE.sub(r"[\2](\1)", text)
    text = INLINE_A_RE.sub(r"[\2](\1)", text)
    text = INLINE_BUTTON_RE.sub(r"[\2](\1)", text)
    text = INLINE_RESOURCE_RE.sub(r"[\2](\1)", text)
    text = INLINE_STRONG_RE.sub(r"**\1**", text)
    text = INLINE_EM_RE.sub(r"*\1*", text)
    text = INLINE_CODE_RE.sub(r"`\1`", text)
    text = INLINE_BADGE_RE.sub(r"**\1**", text)
    text = text.replace("&nbsp;", " ")
    text = text.replace("<br/>", "\n").replace("<br />", "\n")
    return text


def convert_placeholder(match: re.Match[str]) -> str:
    """Preserve placeholders like <YOUR_TOKEN> by rendering them as code."""
    value = match.group(1)
    if "-" in value or "_" in value or value.isupper():
        return f"`<{value}>`"
    return match.group(0)


def clean_source_text(raw: str) -> str:
    """Transform the raw MDX-like export into Markdown."""
    raw = raw.replace("\r\n", "\n")
    raw = (
        raw.replace("—", "-")
        .replace("–", "-")
        .replace("“", '"')
        .replace("”", '"')
        .replace("’", "'")
    )

    # Handle multi-line components before iterating line-by-line
    raw = re.sub(
        r'<Accordion title="([^"]+)"[^>]*>',
        r"\n> **Expandable Topic - \1**\n",
        raw,
    )
    raw = raw.replace("</Accordion>", "\n")
    raw = re.sub(r"<AccordionGroup[^>]*>", "\n", raw)
    raw = raw.replace("</AccordionGroup>", "\n")

    raw = re.sub(
        r'<Step title="([^"]+)"[^>]*>',
        r"\n**Step: \1**\n",
        raw,
    )
    raw = raw.replace("</Step>", "\n")
    raw = raw.replace("<Steps>", "\n")
    raw = raw.replace("</Steps>", "\n")

    raw = re.sub(
        r'<Tip title="([^"]+)"[^>]*>',
        r"\n> **Tip - \1:** ",
        raw,
    )
    raw = re.sub(r"<Tip[^>]*>", "\n> **Tip:** ", raw)
    raw = raw.replace("</Tip>", "\n")

    raw = re.sub(
        r'<Note title="([^"]+)"[^>]*>',
        r"\n> **Note - \1:** ",
        raw,
    )
    raw = re.sub(r"<Note[^>]*>", "\n> **Note:** ", raw)
    raw = raw.replace("</Note>", "\n")

    raw = re.sub(
        r'<Warning title="([^"]+)"[^>]*>',
        r"\n> **Warning - \1:** ",
        raw,
    )
    raw = re.sub(r"<Warning[^>]*>", "\n> **Warning:** ", raw)
    raw = raw.replace("</Warning>", "\n")

    raw = re.sub(r"<Info[^>]*>", "\n> **Info:** ", raw)
    raw = raw.replace("</Info>", "\n")

    raw = raw.replace("<Frame>", "\n")
    raw = raw.replace("</Frame>", "\n")
    raw = raw.replace("<CodeGroup>", "\n")
    raw = raw.replace("</CodeGroup>", "\n")
    raw = raw.replace("<CardGroup cols={2}>", "\n")
    raw = raw.replace("</CardGroup>", "\n")
    raw = raw.replace("<Tabs>", "\n")
    raw = raw.replace("</Tabs>", "\n")
    raw = raw.replace("<Snippet file=", "\n> **Snippet file:** ")
    raw = raw.replace("/>", "")
    raw = raw.replace("<video autoPlay muted controls className=\"w-full aspect-video\"", "\n")
    raw = raw.replace("<video", "\n")
    raw = raw.replace("/video>", "\n")
    raw = raw.replace("<Checklist>", "\n")
    raw = raw.replace("</Checklist>", "\n")
    raw = raw.replace("<Check>", "\n<Check>\n")
    raw = re.sub(r"<Card title=", "\n<Card title=", raw)

    # Remove self-closing media tags entirely
    raw = re.sub(r"<img[^>]*>", "", raw)
    raw = re.sub(r"<video[^>]*>", "", raw)

    lines_out: List[str] = []
    pending_check = False
    pending_card: Optional[Dict[str, str]] = None
    pending_card_content: List[str] = []
    pending_response: Optional[Dict[str, str]] = None
    pending_tab: Optional[str] = None
    in_code_block = False

    for line in raw.splitlines():
        stripped = line.strip()

        # Normalize whitespace
        if not stripped:
            if pending_check:
                continue
            if pending_card_content:
                pending_card_content.append("")
                continue
            if pending_response:
                pending_response.setdefault("content", []).append("")
                continue
            lines_out.append("")
            continue

        # Handle fenced code blocks
        if stripped.startswith("```"):
            tokens = stripped.split()
            fence = tokens[0]
            lang = fence[3:]
            extra = " ".join(t for t in tokens[1:] if t != "theme={null}").strip()

            if not in_code_block:
                in_code_block = True
                lines_out.append(f"```{lang}" if lang else "```")
                if extra:
                    lines_out.append(f"# {extra}")
            else:
                in_code_block = False
                lines_out.append("```")
            continue

        if in_code_block:
            lines_out.append(line)
            continue

        # Convert inline markup before structural handling
        line = convert_inline_markup(line)
        stripped = line.strip()

        if stripped == "<Check>":
            pending_check = True
            continue

        if stripped.startswith("<Tab title="):
            attrs = parse_attrs(stripped.lstrip("<").rstrip(">"))
            pending_tab = attrs.get("title")
            lines_out.append("")
            lines_out.append(f"**Option: {pending_tab}**")
            continue

        if stripped == "</Tab>":
            pending_tab = None
            continue

        if stripped.startswith("<Card title="):
            attrs = parse_attrs(stripped.lstrip("<").rstrip(">"))
            pending_card = {
                "title": attrs.get("title", "").strip(),
                "href": attrs.get("href", "").strip(),
                "icon": attrs.get("icon", "").strip(),
            }
            pending_card_content = []
            continue

        if stripped == "</Card>":
            if pending_card:
                summary = " ".join(
                    segment.strip()
                    for segment in pending_card_content
                    if segment.strip()
                ).strip()
                bullet = f"- **{pending_card['title']}**"
                if pending_card.get("icon"):
                    bullet += f" _(icon: {pending_card['icon']})_"
                if pending_card.get("href"):
                    bullet += f" — [{summary or 'View details'}]({pending_card['href']})"
                elif summary:
                    bullet += f": {summary}"
                lines_out.append("")
                lines_out.append(bullet)
            pending_card = None
            pending_card_content = []
            continue

        if pending_card is not None:
            pending_card_content.append(stripped)
            continue

        response_match = RESPONSE_FIELD_OPEN_RE.match(stripped)
        if response_match:
            pending_response = {
                "name": response_match.group(1),
                "type": response_match.group(2),
                "content": [],
            }
            continue

        if stripped == "</ResponseField>":
            if pending_response:
                description = " ".join(
                    segment.strip()
                    for segment in pending_response["content"]
                    if segment.strip()
                ).strip()
                bullet = (
                    f"- **{pending_response['name']}** "
                    f"(`{pending_response['type']}`): {description}"
                )
                lines_out.append(bullet)
            pending_response = None
            continue

        if pending_response is not None:
            pending_response["content"].append(stripped)
            continue

        if pending_check:
            lines_out.append(f"- [x] {stripped}")
            pending_check = False
            continue

        if stripped.startswith("<Tab "):
            continue

        if stripped.startswith("<Columns") or stripped.startswith("<Column"):
            continue

        if stripped.startswith("<External"):
            continue

        if stripped.startswith("<Snippet"):
            lines_out.append(f"> **Snippet reference:** {stripped}")
            continue

        if stripped.startswith("<div") or stripped.startswith("</div>"):
            continue

        if stripped.startswith("<p>"):
            line = line.replace("<p>", "").replace("</p>", "")
            stripped = line.strip()

        if stripped.startswith("<ResponseField"):
            continue

        # Remove any leftover closing tags that escaped earlier steps
        if stripped.startswith("</"):
            continue

        # Finally, handle placeholder tags like <YOUR_TOKEN>
        line = PLACEHOLDER_RE.sub(convert_placeholder, line)
        line = line.replace("theme={null}", "")

        lines_out.append(line.rstrip())

    markdown_body = "\n".join(lines_out)
    markdown_body = re.sub(r"\n{3,}", "\n\n", markdown_body)
    return markdown_body.strip()


def build_markdown(raw_text: str) -> str:
    """Assemble the final Markdown document."""
    generated_on = datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC")
    intro = "\n".join(
        [
            "# Agno API & Cookbook Documentation",
            "",
            f"_Generated on {generated_on}_",
            "",
            "Welcome to the comprehensive reference for Agno. This guide merges the",
            "public API documentation, framework components, and the full cookbook",
            "catalog into a single reference that is friendly for newcomers.",
            "",
            "Use the quick start path below if you are just getting started, then",
            "explore the detailed sections that follow.",
            "",
            "## Quick Start Checklist",
            "- Install `agno` and authenticate with your model provider.",
            "- Create a single `Agent` instance and reuse it for follow-up runs.",
            "- Add tools, knowledge connectors, and databases as your project grows.",
            "- Explore cookbooks for end-to-end recipes before composing custom logic.",
            "",
            "## First Agent Example",
            "```python",
            "from agno.agent import Agent",
            "from agno.models.openai import OpenAIChat",
            "",
            "agent = Agent(",
            '    model=OpenAIChat(id=\"gpt-4o\"),',
            '    instructions=\"You are a helpful assistant\",',
            "    markdown=True,",
            ")",
            "",
            "print(agent.run(\"How do I build my first Agno workflow?\"))",
            "```",
            "",
            "## How to Navigate",
            "- Use the generated Table of Contents to jump to agents, teams, tools,",
            "  knowledge, DBs, memory, workflows, integrations, and evals.",
            "- Look for callouts marked as tips, notes, and warnings for best practices.",
            "- The cookbook entries include runnable examples you can adapt.",
            "- Use the maintenance playbooks to deploy AgentOS in production.",
            "",
            "[TOC]",
            "",
        ]
    )

    cleaned = clean_source_text(raw_text)
    outlined = inject_table_of_contents(f"{intro}\n{cleaned}\n")
    return outlined


def inject_table_of_contents(markdown_text: str) -> str:
    """Generate a Markdown TOC up to level 3 headings and inject it."""
    toc_lines: List[str] = []
    for line in markdown_text.splitlines():
        if line.startswith("#"):
            level = len(line) - len(line.lstrip("#"))
            if level == 0 or level > 3:
                continue
            title = line[level:].strip()
            anchor = re.sub(r"[^a-z0-9\s-]", "", title.lower()).strip()
            anchor = anchor.replace(" ", "-")
            indent = "  " * (level - 1)
            toc_lines.append(f"{indent}- [{title}](#{anchor})")
    toc_text = "\n".join(toc_lines)
    return markdown_text.replace("[TOC]", toc_text)


def strip_inline_styles(text: str) -> str:
    """Remove Markdown emphasis markers and expand links for PDF output."""
    text = re.sub(r"\[(.*?)\]\((.*?)\)", r"\1 (\2)", text)
    text = text.replace("**", "").replace("__", "")
    text = text.replace("`", "")
    text = text.encode("ascii", "ignore").decode("ascii")
    return soften_long_tokens(text)


def soften_long_tokens(text: str, limit: int = 50) -> str:
    """Insert soft breaks into extremely long tokens to keep PDF wrapping safe."""
    text = text.encode("ascii", "ignore").decode("ascii")
    parts: List[str] = []
    for token in text.split(" "):
        if len(token) > limit:
            chunks = [token[i : i + limit] for i in range(0, len(token), limit)]
            parts.append("\n".join(chunks))
        else:
            parts.append(token)
    return " ".join(parts)


def markdown_to_pdf(content: str, pdf_target: Path) -> None:
    """Render Markdown content into a PDF using a lightweight layout."""
    pdf = FPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_margins(18, 18, 18)
    pdf.set_font("Helvetica", size=11)

    def write_line(text: str, *, indent: float = 0.0, style: str = "", size: int = 11) -> None:
        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", style=style, size=size)
        if indent:
            current_x = pdf.get_x()
            pdf.set_x(pdf.get_x() + indent)
            try:
                pdf.multi_cell(0, 6, text)
            except FPDFException:
                print(f"[PDF WARN] primary write failed (indent) -> {text[:120]!r}")
                safe_text = soften_long_tokens(text, limit=20)
                try:
                    pdf.multi_cell(0, 6, safe_text)
                except FPDFException:
                    print(f"[PDF WARN] secondary write failed (indent) -> {safe_text[:120]!r}")
                    pdf.multi_cell(0, 6, soften_long_tokens(text, limit=8))
            pdf.set_x(current_x)
        else:
            try:
                pdf.multi_cell(0, 6, text)
            except FPDFException:
                print(f"[PDF WARN] primary write failed -> {text[:120]!r}")
                safe_text = soften_long_tokens(text, limit=20)
                try:
                    pdf.multi_cell(0, 6, safe_text)
                except FPDFException:
                    print(f"[PDF WARN] secondary write failed -> {safe_text[:120]!r}")
                    pdf.multi_cell(0, 6, soften_long_tokens(text, limit=8))

    in_code_block = False
    for raw_line in content.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()

        if stripped.startswith("```"):
            in_code_block = not in_code_block
            if in_code_block:
                pdf.ln(2)
                pdf.set_font("Courier", size=9)
            else:
                pdf.set_font("Helvetica", size=11)
                pdf.ln(2)
            continue

        if in_code_block:
            try:
                pdf.set_x(pdf.l_margin)
                pdf.multi_cell(0, 5, soften_long_tokens(line) if line else " ")
            except FPDFException:
                safe_text = soften_long_tokens(line, limit=20) if line else " "
                try:
                    pdf.set_x(pdf.l_margin)
                    pdf.multi_cell(0, 5, safe_text)
                except FPDFException:
                    pdf.set_x(pdf.l_margin)
                    print(f"[PDF WARN] code block write failed -> {safe_text[:120]!r}")
                    pdf.multi_cell(0, 5, soften_long_tokens(line, limit=8) if line else " ")
            continue

        if not stripped:
            pdf.ln(4)
            continue

        if stripped.startswith("#"):
            level = len(stripped) - len(stripped.lstrip("#"))
            title = strip_inline_styles(stripped[level:].strip())
            size = {1: 18, 2: 15, 3: 13, 4: 12}.get(level, 11)
            pdf.ln(2)
            write_line(title, style="B", size=size)
            pdf.ln(2)
            pdf.set_font("Helvetica", size=11)
            continue

        if stripped.startswith(">"):
            text = strip_inline_styles(stripped[1:].strip())
            pdf.set_fill_color(235, 240, 255)
            pdf.set_draw_color(37, 99, 235)
            pdf.set_line_width(0.6)
            x, y = pdf.get_x(), pdf.get_y()
            pdf.set_x(pdf.l_margin)
            pdf.multi_cell(0, 6, f"  {text}", border=1, fill=True)
            pdf.set_xy(x, pdf.get_y())
            pdf.set_fill_color(255, 255, 255)
            pdf.set_draw_color(0, 0, 0)
            pdf.set_line_width(0.2)
            pdf.ln(1)
            continue

        if stripped.startswith("- "):
            bullet_text = strip_inline_styles(stripped[2:].strip())
            write_line(f"- {bullet_text}", indent=4)
            continue

        if re.match(r"\d+\.", stripped):
            numbered = strip_inline_styles(stripped)
            write_line(numbered, indent=4)
            continue

        if line.startswith("    "):
            pdf.set_font("Courier", size=9)
            try:
                pdf.set_x(pdf.l_margin)
                pdf.multi_cell(0, 5, soften_long_tokens(line))
            except FPDFException:
                safe_text = soften_long_tokens(line, limit=20)
                try:
                    pdf.set_x(pdf.l_margin)
                    pdf.multi_cell(0, 5, safe_text)
                except FPDFException:
                    pdf.set_x(pdf.l_margin)
                    print(f"[PDF WARN] indented code write failed -> {safe_text[:120]!r}")
                    pdf.multi_cell(0, 5, soften_long_tokens(line, limit=8))
            pdf.set_font("Helvetica", size=11)
            continue

        write_line(strip_inline_styles(line))

    pdf_target.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(pdf_target))


def main() -> None:
    if not SOURCE_PATH.exists():
        raise FileNotFoundError(
            f"Expected source documentation at {SOURCE_PATH}. "
            "Download https://docs.agno.com/llms-full.txt first."
        )

    raw_text = SOURCE_PATH.read_text(encoding="utf-8")
    markdown_content = build_markdown(raw_text)

    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    MARKDOWN_PATH.write_text(markdown_content, encoding="utf-8")

    markdown_to_pdf(markdown_content, PDF_PATH)
    print(f"Generated {MARKDOWN_PATH} and {PDF_PATH}")


if __name__ == "__main__":
    main()
