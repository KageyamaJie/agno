#!/usr/bin/env python3
"""
Generate a comprehensive Markdown documentation bundle for the Agno project.

The script stitches together:
1. A beginner-friendly introduction and usage guidance.
2. A digest of headings sourced from https://docs.agno.com/llms-full.txt.
3. An auto-generated API reference built by statically analysing the source tree.
4. Cookbook highlights with runnable guidance and code snippets.
5. An appendix that embeds the raw documentation dump for completeness.

The resulting Markdown file can later be converted to PDF (see bottom of file).
"""

from __future__ import annotations

import ast
import os
import re
import textwrap
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional


REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = REPO_ROOT / "docs" / "generated"
OUTPUT_MD = OUTPUT_DIR / "agno_full_documentation.md"
LLMS_EXPORT = REPO_ROOT / "llms-full.txt"

# Directories and packages to include in the API reference
API_TARGETS = [
    {
        "root": REPO_ROOT / "libs" / "agno" / "agno",
        "package": "agno",
        "label": "Agno Core Library",
    },
    # Add more package roots here if needed (e.g., agno_infra)
]

COOKBOOK_ROOT = REPO_ROOT / "cookbook"
EXAMPLES_ROOT = REPO_ROOT / "examples"

CODE_FENCE_PATTERN = re.compile(r"^```([^\s`]+)?(.*)$", re.MULTILINE)


# --------------------------------------------------------------------------- #
# Helpers for AST inspection
# --------------------------------------------------------------------------- #


def _is_private_name(name: str) -> bool:
    return name.startswith("_") and not name.startswith("__")  # dunder handled separately


def _extract_all_names(module_node: ast.Module) -> Optional[set[str]]:
    """
    Extract __all__ definitions from a module, if present.
    Supports simple literal containers and tuple/list concatenations.
    """
    names: set[str] = set()
    for node in module_node.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__all__":
                    names.update(_literal_string_list(node.value))
        elif isinstance(node, ast.AnnAssign):
            target = node.target
            if isinstance(target, ast.Name) and target.id == "__all__" and node.value:
                names.update(_literal_string_list(node.value))
    if names:
        return names
    return None


def _literal_string_list(node: ast.AST) -> Iterable[str]:
    """
    Attempt to extract string literals from basic AST containers.
    """
    if isinstance(node, (ast.List, ast.Tuple, ast.Set)):
        for elt in node.elts:
            yield from _literal_string_list(elt)
    elif isinstance(node, ast.Constant) and isinstance(node.value, str):
        yield node.value
    elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        yield from _literal_string_list(node.left)
        yield from _literal_string_list(node.right)
    return []


def _format_default(node: Optional[ast.AST]) -> Optional[str]:
    if node is None:
        return None
    try:
        return ast.unparse(node)
    except Exception:  # pragma: no cover - fallback just in case
        return None


def _format_arg(arg: ast.arg, default: Optional[str]) -> str:
    name = arg.arg
    annotation = None
    if arg.annotation is not None:
        try:
            annotation = ast.unparse(arg.annotation)
        except Exception:  # pragma: no cover
            annotation = None
    param = name
    if annotation:
        param = f"{param}: {annotation}"
    if default is not None:
        param = f"{param}={default}"
    return param


def _format_arguments(arguments: ast.arguments) -> str:
    parts: List[str] = []

    positional = list(arguments.posonlyargs) + list(arguments.args)
    defaults = [None] * (len(positional) - len(arguments.defaults)) + list(arguments.defaults or [])
    for arg, default_node in zip(positional, defaults):
        default_str = _format_default(default_node)
        parts.append(_format_arg(arg, default_str))

    if arguments.posonlyargs:
        # Insert "/" to mark the boundary for positional-only params
        pos_only_count = len(arguments.posonlyargs)
        if pos_only_count:
            # Place "/" after the positional-only arguments
            parts.insert(pos_only_count, "/")

    if arguments.vararg:
        vararg = arguments.vararg.arg
        annotation = None
        if arguments.vararg.annotation is not None:
            try:
                annotation = ast.unparse(arguments.vararg.annotation)
            except Exception:  # pragma: no cover
                annotation = None
        if annotation:
            parts.append(f"*{vararg}: {annotation}")
        else:
            parts.append(f"*{vararg}")

    if arguments.kwonlyargs:
        if not arguments.vararg:
            parts.append("*")
        for arg, default_node in zip(arguments.kwonlyargs, arguments.kw_defaults or []):
            default_str = _format_default(default_node)
            parts.append(_format_arg(arg, default_str))

    if arguments.kwarg:
        kwarg = arguments.kwarg.arg
        annotation = None
        if arguments.kwarg.annotation is not None:
            try:
                annotation = ast.unparse(arguments.kwarg.annotation)
            except Exception:  # pragma: no cover
                annotation = None
        if annotation:
            parts.append(f"**{kwarg}: {annotation}")
        else:
            parts.append(f"**{kwarg}")

    return ", ".join(part for part in parts if part != "/," and part != ",/")


def _format_signature(node: ast.AST) -> str:
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return ""
    args = _format_arguments(node.args)
    prefix = "async " if isinstance(node, ast.AsyncFunctionDef) else ""
    signature = f"{prefix}{node.name}({args})"
    if node.returns is not None:
        try:
            returns = ast.unparse(node.returns)
            signature = f"{signature} -> {returns}"
        except Exception:  # pragma: no cover
            pass
    return signature


def _clean_docstring(doc: Optional[str]) -> Optional[str]:
    if not doc:
        return None
    cleaned = textwrap.dedent(doc).strip()
    return cleaned or None


def _is_public(name: str, public_names: Optional[set[str]]) -> bool:
    if name.startswith("__") and name.endswith("__"):
        return False
    if public_names is not None:
        base = name.split(".")[-1]
        return base in public_names
    return not _is_private_name(name)


# --------------------------------------------------------------------------- #
# Data containers
# --------------------------------------------------------------------------- #


@dataclass
class FunctionDoc:
    name: str
    signature: str
    doc: Optional[str]


@dataclass
class ClassDoc:
    name: str
    bases: List[str] = field(default_factory=list)
    doc: Optional[str] = None
    methods: List[FunctionDoc] = field(default_factory=list)


@dataclass
class ModuleDoc:
    module: str
    path: Path
    doc: Optional[str]
    classes: List[ClassDoc] = field(default_factory=list)
    functions: List[FunctionDoc] = field(default_factory=list)


# --------------------------------------------------------------------------- #
# Module parsing
# --------------------------------------------------------------------------- #


def parse_module(path: Path, package_root: Path, package: str) -> Optional[ModuleDoc]:
    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    try:
        module_node = ast.parse(source)
    except SyntaxError:
        return None

    relative = path.relative_to(package_root)
    parts = list(relative.with_suffix("").parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    module_name = ".".join([package] + parts) if parts else package

    public_names = _extract_all_names(module_node)
    module_doc = _clean_docstring(ast.get_docstring(module_node))

    classes: List[ClassDoc] = []
    functions: List[FunctionDoc] = []

    for node in module_node.body:
        if isinstance(node, ast.ClassDef):
            if not _is_public(node.name, public_names):
                continue
            bases = []
            for base in node.bases:
                try:
                    bases.append(ast.unparse(base))
                except Exception:  # pragma: no cover
                    continue
            class_doc = ClassDoc(
                name=node.name,
                bases=bases,
                doc=_clean_docstring(ast.get_docstring(node)),
            )
            for child in node.body:
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not _is_public(child.name, None):
                        continue
                    class_doc.methods.append(
                        FunctionDoc(
                            name=child.name,
                            signature=_format_signature(child),
                            doc=_clean_docstring(ast.get_docstring(child)),
                        )
                    )
            if class_doc.methods:
                class_doc.methods.sort(key=lambda m: m.name)
            classes.append(class_doc)

        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not _is_public(node.name, public_names):
                continue
            functions.append(
                FunctionDoc(
                    name=node.name,
                    signature=_format_signature(node),
                    doc=_clean_docstring(ast.get_docstring(node)),
                )
            )

    if not module_doc and not classes and not functions:
        # Skip modules without public documentation
        return None

    classes.sort(key=lambda cls: cls.name)
    functions.sort(key=lambda fn: fn.name)

    return ModuleDoc(
        module=module_name,
        path=path,
        doc=module_doc,
        classes=classes,
        functions=functions,
    )


def collect_module_docs() -> List[ModuleDoc]:
    modules: List[ModuleDoc] = []
    for target in API_TARGETS:
        root: Path = target["root"]
        package: str = target["package"]
        if not root.exists():
            continue
        for file in sorted(root.rglob("*.py")):
            if file.name == "__pycache__":
                continue
            if any(part.startswith(".") for part in file.parts):
                continue
            module_doc = parse_module(file, root, package)
            if module_doc is not None:
                modules.append(module_doc)
    modules.sort(key=lambda module: module.module)
    return modules


# --------------------------------------------------------------------------- #
# Cookbook summariser
# --------------------------------------------------------------------------- #


def summarise_cookbook() -> str:
    if not COOKBOOK_ROOT.exists():
        return ""

    lines: List[str] = [
        "## Cookbook Walkthrough",
        "The cookbook directory contains runnable, end-to-end examples. "
        "Each entry below includes a friendly summary, notable imports, and a small code excerpt.",
    ]

    for file in sorted(COOKBOOK_ROOT.rglob("*.py")):
        if any(part.startswith(".") for part in file.relative_to(COOKBOOK_ROOT).parts):
            continue
        rel_path = file.relative_to(REPO_ROOT).as_posix()
        try:
            source = file.read_text(encoding="utf-8")
            module = ast.parse(source)
        except (OSError, UnicodeDecodeError, SyntaxError):
            continue

        doc = _clean_docstring(ast.get_docstring(module))
        headline = doc.splitlines()[0] if doc else f"{rel_path} example"

        # Collect notable imports and definitions
        imports: set[str] = set()
        functions: set[str] = set()
        classes: set[str] = set()

        for node in module.body:
            if isinstance(node, ast.ImportFrom):
                if node.module:
                    if node.module.startswith("agno"):
                        for alias in node.names:
                            imports.add(f"{node.module}.{alias.name}")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("agno"):
                        imports.add(alias.name)
            elif isinstance(node, ast.FunctionDef):
                if not _is_private_name(node.name):
                    functions.add(node.name)
            elif isinstance(node, ast.ClassDef):
                if not _is_private_name(node.name):
                    classes.add(node.name)

        lines.append(f"### `{rel_path}`")
        lines.append(f"**Purpose:** {headline}")
        if doc and len(doc.splitlines()) > 1:
            lines.append(doc)

        if imports:
            lines.append(f"- **Key Agno APIs:** {', '.join(sorted(imports))}")
        if classes:
            lines.append(f"- **Defined Classes:** {', '.join(sorted(classes))}")
        if functions:
            lines.append(f"- **Helper Functions:** {', '.join(sorted(functions))}")
        lines.append(f"- **How to Run:** `python {rel_path}` (ensure prerequisites from the docstring are satisfied)")

        snippet_lines = source.splitlines()
        max_lines = 160
        if len(snippet_lines) > max_lines:
            excerpt = "\n".join(snippet_lines[:max_lines]) + "\n# ... (truncated for brevity) ..."
        else:
            excerpt = source
        lines.append("\n```python\n" + excerpt + "\n```")

    return "\n\n".join(lines)


# --------------------------------------------------------------------------- #
# Examples overview
# --------------------------------------------------------------------------- #


def summarise_examples() -> str:
    if not EXAMPLES_ROOT.exists():
        return ""

    category_info: dict[str, dict[str, int]] = defaultdict(lambda: {"py": 0, "other": 0})
    for path in EXAMPLES_ROOT.iterdir():
        if path.is_dir():
            py_count = sum(1 for _ in path.rglob("*.py"))
            other_count = sum(1 for _ in path.rglob("*") if _.is_file() and not _.name.endswith(".py"))
            category_info[path.name]["py"] += py_count
            category_info[path.name]["other"] += other_count

    lines: List[str] = [
        "## Examples Directory Overview",
        "Beyond the cookbook, the `examples/` folder provides focused snippets organised by topic. "
        "Use these when you need a lightweight reference or template.",
    ]

    for category in sorted(category_info):
        info = category_info[category]
        lines.append(
            f"- **{category}** – {info['py']} Python example(s), {info['other']} supporting asset(s). "
            f"Run an example with `python examples/{category}/...` after installing dependencies listed in its README (if present)."
        )

    lines.append(
        "\nTip: Most examples follow the same pattern—configure an `Agent`, supply tools or knowledge, then call `agent.run()` or "
        "`agent.print_response()`. Reuse agent instances instead of recreating them inside loops."
    )
    return "\n\n".join(lines)


# --------------------------------------------------------------------------- #
# Official docs digest
# --------------------------------------------------------------------------- #


def build_docs_digest() -> str:
    if not LLMS_EXPORT.exists():
        return ""

    try:
        text = LLMS_EXPORT.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""

    sections: List[tuple[str, List[str]]] = []
    current_title: Optional[str] = None
    current_lines: List[str] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("# "):
            if current_title:
                sections.append((current_title, current_lines))
            current_title = line[2:].strip()
            current_lines = []
        elif line.startswith("## "):
            # Treat major subheadings as separate entries when no parent title is set
            if current_title:
                sections.append((current_title, current_lines))
            current_title = line[3:].strip()
            current_lines = []
        else:
            if current_title and line and not line.startswith("Source:"):
                if len(current_lines) < 4 and not line.startswith("<"):
                    cleaned = re.sub(r"theme=\{.*?\}", "", line)
                    current_lines.append(cleaned)
    if current_title:
        sections.append((current_title, current_lines))

    digest_lines: List[str] = [
        "## Official Documentation Digest",
        "Headings below originate from the published Agno documentation. "
        "Skim this list to understand the breadth of topics before diving into the API reference.",
    ]
    max_sections = 120
    for idx, (title, lines_list) in enumerate(sections):
        if idx >= max_sections:
            break
        summary = " ".join(lines_list) if lines_list else ""
        summary = summary[:400] + ("…" if len(summary) > 400 else "")
        if summary:
            digest_lines.append(f"- **{title}** – {summary}")
        else:
            digest_lines.append(f"- **{title}**")

    return "\n\n".join(digest_lines)


def normalize_llms_export(text: str) -> str:
    """
    Clean up Mintlify-style fenced code blocks so Pandoc can parse them.
    Removes theme attributes and moves any trailing descriptors into
    inline comments inside the code block.
    """

    def _replace(match: re.Match[str]) -> str:
        language = (match.group(1) or "").strip()
        tail = (match.group(2) or "").strip()
        extras: List[str] = []
        if tail:
            for token in tail.split():
                token = token.strip()
                if not token or token == "theme={null}":
                    continue
                extras.append(token)

        fence = f"```{language}" if language else "```"
        if not extras:
            return fence

        comments = "\n".join(f"# Context: {item}" for item in extras)
        return f"{fence}\n{comments}"

    # Sanitize fenced code blocks
    text = CODE_FENCE_PATTERN.sub(_replace, text)

    return text


# --------------------------------------------------------------------------- #
# Markdown assembly
# --------------------------------------------------------------------------- #


def render_module_docs(modules: List[ModuleDoc]) -> str:
    lines: List[str] = [
        "## Auto-Generated API Reference",
        "This reference is created via static analysis of the Agno source tree. "
        "Only public members (respecting `__all__` when provided) are listed. "
        "Docstrings are included verbatim to preserve the original guidance.",
    ]

    for module in modules:
        rel_path = module.path.relative_to(REPO_ROOT).as_posix()
        lines.append(f"### Module `{module.module}`")
        lines.append(f"- **Source:** `{rel_path}`")
        if module.doc:
            lines.append("\n" + module.doc)

        if module.classes:
            lines.append("\n#### Classes")
            for cls in module.classes:
                base_info = f" (bases: {', '.join(cls.bases)})" if cls.bases else ""
                lines.append(f"- **`class {cls.name}`**{base_info}")
                if cls.doc:
                    lines.append(f"  - {cls.doc}")
                if cls.methods:
                    lines.append("  - **Methods:**")
                    for method in cls.methods:
                        doc = method.doc.replace("\n", " ") if method.doc else "No docstring provided."
                        lines.append(f"    - `{method.signature}` – {doc}")

        if module.functions:
            lines.append("\n#### Functions")
            for fn in module.functions:
                doc = fn.doc.replace("\n", " ") if fn.doc else "No docstring provided."
                lines.append(f"- `{fn.signature}` – {doc}")

    return "\n\n".join(lines)


def render_header() -> str:
    today = datetime.utcnow().strftime("%Y-%m-%d")
    intro = f"""# Agno Comprehensive API & Cookbook Guide

Generated on **{today}**.

This document consolidates Agno's official documentation, auto-generated API reference,
and runnable cookbook examples into a single beginner-friendly resource.

## How to Use this Guide

- Start with the *Getting Started* section to configure your environment.
- Skim the *Official Documentation Digest* to see what topics are available online.
- Dive into the *Auto-Generated API Reference* when you need precise signatures.
- Explore the *Cookbook Walkthrough* and *Examples Overview* for runnable code.
- Refer to the *Appendix* for the raw documentation export and quick-searching.

> **Performance tip:** Create agents once and reuse them; avoid instantiating agents inside loops.
> Structure your responses with `output_schema` when you need typed results.
"""
    return textwrap.dedent(intro)


def render_getting_started() -> str:
    return textwrap.dedent(
        """## Getting Started Quickly

1. **Install dependencies**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -U agno openai ddgs yfinance sqlalchemy "fastapi[standard]"
   ```
2. **Export provider credentials**
   ```bash
   export OPENAI_API_KEY=sk-...
   ```
3. **Create your first agent**
   ```python
   from agno.agent import Agent
   from agno.models.openai import OpenAIChat

   agent = Agent(
       model=OpenAIChat(id="gpt-4o"),
       instructions="You are a helpful assistant",
       markdown=True,
   )
   agent.print_response("Hello Agno!", stream=True)
   ```
4. **Add tools or knowledge progressively.**
   Start with a single agent, introduce tool integrations as needed, and switch to teams or workflows only
   when coordination or branching logic becomes essential.
"""
    )


def render_appendix_raw_docs() -> str:
    if not LLMS_EXPORT.exists():
        return ""
    try:
        raw_text = LLMS_EXPORT.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""

    raw_text = normalize_llms_export(raw_text)

    header = (
        "## Appendix: Raw Official Documentation Export\n\n"
        "The following section reproduces the published content from "
        "https://docs.agno.com/llms-full.txt for offline searchability. "
        "HTML-like tags are left intact to preserve context.\n"
    )
    return header + "\n" + raw_text


def assemble_markdown() -> str:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    modules = collect_module_docs()

    sections = [
        render_header(),
        render_getting_started(),
        build_docs_digest(),
        render_module_docs(modules),
        summarise_cookbook(),
        summarise_examples(),
        render_appendix_raw_docs(),
    ]

    return "\n\n".join(filter(None, sections))


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #


def main() -> None:
    markdown = assemble_markdown()
    OUTPUT_MD.write_text(markdown, encoding="utf-8")
    print(f"Wrote documentation to {OUTPUT_MD}")
    print("To convert to PDF, run:")
    print(
        f"  pandoc {OUTPUT_MD} -o {OUTPUT_MD.with_suffix('.pdf')} "
        "--from markdown --pdf-engine=wkhtmltopdf"
    )


if __name__ == "__main__":
    main()

