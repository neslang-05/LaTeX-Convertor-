# Document to LaTeX Converter

A powerful Python tool that converts various document formats (DOCX, PDF, Markdown, and plain text) into LaTeX format with a user-friendly web interface built using Streamlit.

## 📋 Table of Contents

- [Features](#features)
- [Supported Formats](#supported-formats)
- [Installation](#installation)
- [Usage](#usage)
  - [Web Interface](#web-interface)
  - [Command Line Interface](#command-line-interface)
- [Configuration Options](#configuration-options)
- [Examples](#examples)
- [Technical Details](#technical-details)
- [Requirements](#requirements)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## ✨ Features

- **Multiple Format Support**: Convert DOCX, PDF, Markdown (.md), and plain text files to LaTeX
- **Web Interface**: Easy-to-use Streamlit-based web UI for drag-and-drop conversion
- **Command Line Interface**: Powerful CLI for batch processing and automation
- **Customizable Output**: Configure document class, font size, margins, and packages
- **Smart Formatting**: Preserves document structure including:
  - Headings and sections
  - Bold and italic text
  - Tables
  - Lists (bulleted and numbered)
  - Code blocks (from Markdown)
- **LaTeX Character Escaping**: Automatically handles special LaTeX characters
- **Custom Preamble**: Add custom LaTeX commands and package configurations

## 📄 Supported Formats

| Format | Extension | Features Supported |
|--------|-----------|-------------------|
| **DOCX** | `.docx` | Paragraphs, headings, tables, bold/italic, lists |
| **PDF** | `.pdf` | Text extraction (works best with text-based PDFs) |
| **Markdown** | `.md` | Headers, code blocks, inline code, bold/italic, lists |
| **Plain Text** | `.txt` | Basic text with LaTeX character escaping |

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Clone or download this repository**:
   ```bash
   cd /path/to/LaTeX
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment**:
   - **Linux/Mac**:
     ```bash
     source .venv/bin/activate
     ```
   - **Windows**:
     ```bash
     .venv\Scripts\activate
     ```

4. **Install dependencies**:
   ```bash
   pip install streamlit python-docx pdfplumber
   ```

## 💻 Usage

### Web Interface

The web interface provides the easiest way to convert documents with a visual interface.

1. **Start the Streamlit app**:
   ```bash
   streamlit run app.py
   ```

2. **Access the interface**:
   - The app will automatically open in your default browser
   - Or manually navigate to `http://localhost:8501`

3. **Convert a document**:
   - Upload your file using the file uploader
   - Configure options in the sidebar (optional):
     - Document Class (article, report, book)
     - Font Size (10pt, 11pt, 12pt)
     - Margins
     - Extra LaTeX packages
     - Custom preamble code
   - Click "Convert to LaTeX"
   - Preview the generated LaTeX code
   - Download the `.tex` file

### Command Line Interface

For automation and batch processing, use the command line interface.

#### Basic Usage

```bash
python latex_converter.py input_file.docx
```

This will create `input_file.tex` in the same directory.

#### Specify Output File

```bash
python latex_converter.py input_file.pdf -o output.tex
```

#### Advanced Options

```bash
python latex_converter.py input.md \
    --output output.tex \
    --doc_class report \
    --fontsize 11pt \
    --margins "margin=1.5in" \
    --packages "tikz,algorithm" \
    --custom_preamble "\newcommand{\myvec}[1]{\mathbf{#1}}"
```

## ⚙️ Configuration Options

### Document Class

Choose the LaTeX document class:
- `article` (default): For shorter documents, papers, journal articles
- `report`: For longer documents with chapters
- `book`: For book-length documents with complex structure

### Font Size

Available options: `10pt`, `11pt`, `12pt` (default)

### Margins

Use standard geometry package syntax:
- `margin=1in` (default)
- `top=2cm,bottom=2cm,left=3cm,right=3cm`
- `a4paper,margin=1.5in`

### Extra Packages

Add additional LaTeX packages as a comma-separated list:
```
tikz,algorithm,multirow,subfigure
```

Default packages included:
- `geometry`: Page layout
- `graphicx`: Image handling
- `hyperref`: Hyperlinks
- `amsmath`: Math symbols
- `listings`: Code listings
- `xcolor`: Colors
- `booktabs`: Professional tables
- `float`: Float placement

### Custom Preamble

Add custom LaTeX commands, package configurations, or macros:
```latex
\newcommand{\mycommand}{...}
\definecolor{mycolor}{RGB}{255,0,0}
```

## 📚 Examples

### Example 1: Converting a DOCX Resume

```bash
python latex_converter.py resume.docx --doc_class article --fontsize 11pt
```

### Example 2: Converting a Markdown Report

```bash
python latex_converter.py report.md -o report.tex --doc_class report
```

### Example 3: Converting a PDF with Custom Margins

```bash
python latex_converter.py document.pdf --margins "top=2.5cm,bottom=2.5cm"
```

### Example 4: Converting with Custom Packages

```bash
python latex_converter.py notes.txt \
    --packages "algorithm2e,tikz" \
    --custom_preamble "\usepackage[utf8]{inputenc}"
```

## 🔧 Technical Details

### Architecture

The converter is built with a modular architecture:

- **`LatexConverter` class**: Core conversion engine
  - `parse_docx()`: DOCX file parser using python-docx
  - `parse_pdf()`: PDF text extraction using pdfplumber
  - `parse_markdown()`: Markdown parser using regex
  - `parse_txt()`: Plain text handler
  - `_escape_latex()`: LaTeX special character escaping
  - `_get_preamble()`: Dynamic preamble generation
  - `convert()`: Main conversion orchestrator

- **`app.py`**: Streamlit web interface
  - File upload handling
  - Configuration UI
  - Temporary file management
  - Preview and download functionality

### Document Processing

#### DOCX Files
- Uses `python-docx` library for parsing
- Iterates through document elements in order
- Preserves paragraph styles, text formatting, and tables
- Handles bold/italic through run objects

#### PDF Files
- Uses `pdfplumber` for text extraction
- Best results with text-based PDFs
- Image-based (scanned) PDFs may produce limited results
- Performs basic text cleanup and reflow

#### Markdown Files
- Regex-based parsing for common Markdown syntax
- Converts headers, code blocks, bold/italic, and lists
- Code blocks are wrapped in LaTeX `lstlisting` environment

#### Plain Text Files
- Escapes special LaTeX characters
- Preserves paragraph structure

### LaTeX Character Escaping

The following special characters are automatically escaped:
- `&` → `\&`
- `%` → `\%`
- `$` → `\$`
- `#` → `\#`
- `_` → `\_`
- `{` → `\{`
- `}` → `\}`
- `~` → `\textasciitilde{}`
- `^` → `\^{}`
- `\` → `\textbackslash{}`

## 📦 Requirements

```
streamlit>=1.28.0
python-docx>=1.0.0
pdfplumber>=0.10.0
```

## 🐛 Troubleshooting

### Import Error: Cannot import LatexConverter

If you encounter:
```
ImportError: cannot import name 'LatexConverter' from 'latex_converter'
```

**Solution**: Ensure there are no naming conflicts with Python modules. The file should be named `latex_converter.py` (not `run.py`).

### PDF Extraction Returns Empty Content

**Cause**: The PDF is likely image-based (scanned document).

**Solution**: 
- Use OCR software to convert the PDF to text first
- Or use a different source format (DOCX, Markdown)

### Streamlit Won't Start

**Solution**:
1. Ensure virtual environment is activated
2. Reinstall streamlit: `pip install --upgrade streamlit`
3. Check if port 8501 is already in use

### LaTeX Compilation Errors

If the generated `.tex` file doesn't compile:
1. Check that all required packages are installed in your LaTeX distribution
2. Review custom preamble for syntax errors
3. Ensure special characters are properly escaped

### Module Not Found Error

**Solution**:
```bash
# Reinstall dependencies
pip install --upgrade streamlit python-docx pdfplumber
```

## 📝 Notes

- **DOCX Lists**: Complex nested lists may require manual adjustment
- **PDF Tables**: Table structure may not be preserved in PDF extraction
- **Markdown Math**: LaTeX math in Markdown (`$...$`) may need special handling
- **Images**: Image extraction is not currently supported; add images manually to the LaTeX document

## 🤝 Contributing

Contributions are welcome! Some ideas for improvements:
- Add image extraction and embedding
- Support for more document formats (RTF, ODT, HTML)
- Better table handling for PDFs
- Enhanced Markdown parser with math support
- LaTeX template selection
- Batch conversion mode in web UI

## 📄 License

This project is provided as-is for educational and commercial use.

## 📧 Contact

For questions, issues, or suggestions, please open an issue in the repository.

---

**Generated on**: December 4, 2025  
**Version**: 1.0.0
