import json
import os
import re
import textwrap
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_SOURCE = REPO_ROOT / "tmp_llms_full.txt"
OUTPUT_MD = REPO_ROOT / "docs" / "agno_full_api_guide.md"
COOKBOOK_DIR = REPO_ROOT / "cookbook"


def extract_docstring(text: str) -> str | None:
    """Return the leading module docstring or top-level comment summary."""
    doc_match = re.search(
        r'^\s*(?P<quote>"""|\'\'\')(?P<body>.*?)(?P=quote)',
        text,
        flags=re.DOTALL,
    )
    if doc_match:
        body = doc_match.group("body").strip()
        # take first non-empty line
        for line in body.splitlines():
            cleaned = line.strip()
            if cleaned:
                return cleaned

    # fallback to top-level comment block
    comment_lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            if comment_lines:
                break
            continue
        if stripped.startswith("#"):
            comment_lines.append(stripped.lstrip("#").strip())
        else:
            break
    if comment_lines:
        return " ".join(comment_lines).strip()

    return None


def extract_key_apis(text: str) -> list[str]:
    """Return sorted unique Agno API symbols used within the file."""
    apis: set[str] = set()

    # from agno.xyz import ABC, DEF
    for match in re.finditer(r"from\s+agno(?:\.[\w\.]+)?\s+import\s+([^\n]+)", text):
        imported = match.group(1)
        parts = re.split(r",\s*", imported)
        for part in parts:
            clean = part.strip()
            if clean:
                apis.add(clean)

    # import agno.foo as bar
    for match in re.finditer(r"import\s+agno(?:\.[\w\.]+)?\s+as\s+([^\n]+)", text):
        alias = match.group(1).strip()
        if alias:
            apis.add(alias)

    # direct import (import agno.tools)
    for match in re.finditer(r"import\s+(agno[^\n]+)", text):
        # skip `import agnostuff` false positives
        module = match.group(1).strip()
        if module.startswith("agno"):
            apis.add(module)

    cleaned = sorted({api.split(" as ")[0].strip() for api in apis})
    return cleaned


def build_cookbook_section() -> str:
    if not COOKBOOK_DIR.exists():
        return ""

    entries: list[tuple[str, dict]] = []
    for py_path in sorted(COOKBOOK_DIR.rglob("*.py")):
        rel_path = py_path.relative_to(REPO_ROOT).as_posix()
        try:
            content = py_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = py_path.read_text(encoding="latin-1")

        doc_summary = extract_docstring(content) or "Example demonstrating Agno usage."
        key_apis = extract_key_apis(content)
        defs = re.findall(r"^def\s+([a-zA-Z_][\w]*)", content, flags=re.MULTILINE)
        classes = re.findall(r"^class\s+([A-Z][\w]*)", content, flags=re.MULTILINE)

        entries.append(
            (
                rel_path,
                {
                    "summary": doc_summary,
                    "key_apis": key_apis,
                    "functions": defs,
                    "classes": classes,
                },
            )
        )

    lines: list[str] = [
        "## Cookbook Navigator",
        "",
        "The following index summarizes every available cookbook example. "
        "Each entry highlights the core learning goal, the primary Agno APIs involved, "
        "and how to run the example locally.",
        "",
    ]

    current_section_prefix = None
    for rel_path, meta in entries:
        section_prefix = rel_path.split("/")[1] if "/" in rel_path else "cookbook"
        if section_prefix != current_section_prefix:
            current_section_prefix = section_prefix
            lines.append(f"### {section_prefix}")
            lines.append("")

        lines.append(f"#### `{rel_path}`")
        lines.append("")
        lines.append(f"- **Purpose**: {meta['summary']}")
        if meta["key_apis"]:
            api_list = ", ".join(f"`{api}`" for api in meta["key_apis"])
            lines.append(f"- **Key APIs**: {api_list}")
        if meta["classes"]:
            class_list = ", ".join(f"`{cls}`" for cls in sorted(set(meta["classes"])))
            lines.append(f"- **Defined Classes**: {class_list}")
        if meta["functions"]:
            fn_list = ", ".join(f"`{fn}()`" for fn in sorted(set(meta["functions"])))
            lines.append(f"- **Defined Functions**: {fn_list}")
        lines.append(f"- **Usage**: `python {rel_path}`")
        lines.append("")

    return "\n".join(lines)


def build_markdown() -> str:
    if not DOC_SOURCE.exists():
        raise FileNotFoundError(f"Documentation source not found: {DOC_SOURCE}")

    intro = textwrap.dedent(
        """
        # Agno Public API & Cookbook Companion

        Welcome! This guide consolidates the entire public surface area of the Agno platform,
        explains how the components fit together, and provides runnable cookbook examples so you can
        move from zero to production with confidence.

        ## How to Use This Guide

        - **Start with the Concept Primers** to understand Agents, Teams, Workflows, and AgentOS.
        - **Jump to the API Reference** for detailed parameters, request/response schemas, and integration tips.
        - **Explore the Cookbook Navigator** to run real scripts that demonstrate each concept in action.
        - **Leverage the End-to-End Examples** sprinkled throughout to scaffold your own projects.

        <Note>
        This document is intentionally beginner-friendly: every major API call includes guiding narration,
        practical usage instructions, and direct links to runnable code.
        </Note>
        """
    ).strip()

    cookbook_section = build_cookbook_section()

    reference_intro = textwrap.dedent(
        """
        ## Complete API & Platform Reference

        The following sections mirror the official Agno documentation to ensure **full coverage of every public API,
        function, component, and integration pathway**. Content is indexed from
        [https://docs.agno.com/llms-full.txt](https://docs.agno.com/llms-full.txt) and preserved verbatim so you
        always have the canonical details at hand.
        """
    ).strip()

    reference_body = sanitize_reference(DOC_SOURCE.read_text(encoding="utf-8"))

    parts: list[str] = [intro, ""]
    if cookbook_section:
        parts.extend([cookbook_section, ""])
    parts.extend([reference_intro, "", reference_body])

    return "\n".join(parts)


def ensure_output_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def sanitize_reference(text: str) -> str:
    """Normalize fenced code blocks and remove unsupported attributes for pandoc."""

    def fence_repl(match: re.Match[str]) -> str:
        language = match.group("lang") or ""
        extra = match.group("extra") or ""
        extra = extra.strip()
        prefix = ""
        if extra:
            comment_prefix = "#"
            if language in {"python", "py"}:
                comment_prefix = "#"
            elif language in {"bash", "shell", "sh"}:
                comment_prefix = "#"
            elif language in {"json"}:
                comment_prefix = "//"
            elif language in {"yaml", "yml"}:
                comment_prefix = "#"
            elif language in {"sql"}:
                comment_prefix = "--"
            else:
                comment_prefix = "#"
            prefix = f"{comment_prefix} {extra}\n"
        return f"```{language}\n{prefix}"

    sanitized = re.sub(
        r"```(?P<lang>[\w+-]*)[^\n`]*?(?P<extra>(?:\s+\S.*)?)\n",
        fence_repl,
        text,
    )

    # Remove stray HTML attributes like theme={null} that may remain
    sanitized = sanitized.replace("theme={null}", "")
    sanitized = sanitized.replace("{null}", "")
    sanitized = re.sub(r"\s+\n", "\n", sanitized)
    return sanitized


def main() -> None:
    markdown = build_markdown()
    ensure_output_dir(OUTPUT_MD)
    OUTPUT_MD.write_text(markdown, encoding="utf-8")
    print(json.dumps({"output_markdown": OUTPUT_MD.as_posix()}, indent=2))


if __name__ == "__main__":
    main()

