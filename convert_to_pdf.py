#!/usr/bin/env python3
"""
Convert markdown documentation to PDF
"""

import markdown
from weasyprint import HTML, CSS
from pathlib import Path

def markdown_to_pdf(markdown_file: str, pdf_file: str):
    """Convert markdown file to PDF"""
    
    # Read markdown
    md_content = Path(markdown_file).read_text()
    
    # Convert markdown to HTML
    html_content = markdown.markdown(
        md_content,
        extensions=['extra', 'codehilite', 'tables', 'fenced_code']
    )
    
    # Add CSS styling
    css_style = """
    <style>
        @page {
            size: A4;
            margin: 2cm;
        }
        body {
            font-family: 'DejaVu Sans', Arial, sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #333;
        }
        h1 {
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
            margin-top: 30px;
            page-break-after: avoid;
        }
        h2 {
            color: #34495e;
            border-bottom: 2px solid #95a5a6;
            padding-bottom: 8px;
            margin-top: 25px;
            page-break-after: avoid;
        }
        h3 {
            color: #555;
            margin-top: 20px;
            page-break-after: avoid;
        }
        h4 {
            color: #666;
            margin-top: 15px;
        }
        code {
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 10pt;
        }
        pre {
            background-color: #f8f8f8;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            overflow-x: auto;
            page-break-inside: avoid;
        }
        pre code {
            background-color: transparent;
            padding: 0;
        }
        ul, ol {
            margin-left: 20px;
        }
        li {
            margin-bottom: 5px;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            margin: 15px 0;
            page-break-inside: avoid;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #3498db;
            color: white;
            font-weight: bold;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        blockquote {
            border-left: 4px solid #3498db;
            margin: 15px 0;
            padding-left: 15px;
            color: #666;
            font-style: italic;
        }
        a {
            color: #3498db;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        .toc {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }
        strong {
            color: #2c3e50;
        }
    </style>
    """
    
    # Combine HTML
    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Agno Framework - Complete API Documentation</title>
        {css_style}
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    # Convert to PDF
    HTML(string=full_html).write_pdf(pdf_file)
    print(f"PDF generated: {pdf_file}")

if __name__ == "__main__":
    markdown_file = "/workspace/agno_complete_api_documentation.md"
    pdf_file = "/workspace/agno_complete_api_documentation.pdf"
    
    markdown_to_pdf(markdown_file, pdf_file)
    print(f"Successfully converted {markdown_file} to {pdf_file}")
