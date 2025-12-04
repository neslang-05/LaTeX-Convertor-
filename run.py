import os
import sys
import re
import argparse
import docx
import pdfplumber
from docx.document import Document as _Document
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl
from docx.table import _Cell, Table
from docx.text.paragraph import Paragraph

class LatexConverter:
    def __init__(self, input_path, output_path, options):
        self.input_path = input_path
        self.output_path = output_path
        self.options = options
        self.content = ""

    def _escape_latex(self, text):
        """Escapes special LaTeX characters in plain text."""
        if not text:
            return ""
        chars = {
            '&': r'\&',
            '%': r'\%',
            '$': r'\$',
            '#': r'\#',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\^{}',
            '\\': r'\textbackslash{}',
        }
        pattern = re.compile('|'.join(re.escape(key) for key in chars.keys()))
        return pattern.sub(lambda x: chars[x.group()], text)

    def _get_preamble(self):
        """Generates the LaTeX preamble based on options."""
        packages = [
            "geometry", "graphicx", "hyperref", "amsmath", 
            "listings", "xcolor", "booktabs", "float"
        ]
        
        # Add custom packages
        if self.options.get('packages'):
            packages.extend(self.options.get('packages').split(','))

        preamble = [
            f"\\documentclass[{self.options.get('fontsize', '12pt')}]{{{self.options.get('doc_class', 'article')}}}",
            f"\\usepackage[{self.options.get('margins', 'margin=1in')}]{{geometry}}",
        ]
        
        for pkg in packages:
            preamble.append(f"\\usepackage{{{pkg.strip()}}}")

        # Basic setup for code blocks
        preamble.append(
            r"""
\lstset{
    basicstyle=\ttfamily\small,
    breaklines=true,
    frame=single,
    backgroundcolor=\color{gray!10},
    keywordstyle=\color{blue},
    commentstyle=\color{green!50!black},
    stringstyle=\color{red}
}
            """
        )

        if self.options.get('custom_preamble'):
            preamble.append(self.options.get('custom_preamble'))

        preamble.append(f"\\title{{{os.path.basename(self.input_path)}}}")
        preamble.append("\\author{Auto-Generated}")
        preamble.append("\\date{\\today}")
        preamble.append("\\begin{document}")
        preamble.append("\\maketitle")
        
        return "\n".join(preamble)

    def _get_postamble(self):
        return "\n\\end{document}"

    # ==========================
    # DOCX HANDLING
    # ==========================
    def parse_docx(self):
        """Parses DOCX extracting text, styles, lists, and tables."""
        try:
            doc = docx.Document(self.input_path)
            latex_body = []
            
            # Helper to iterate over document elements in order (paragraphs and tables)
            def iter_block_items(parent):
                if isinstance(parent, _Document):
                    parent_elm = parent.element.body
                elif isinstance(parent, _Cell):
                    parent_elm = parent._tc
                else:
                    raise ValueError("something's not right")

                for child in parent_elm.iterchildren():
                    if isinstance(child, CT_P):
                        yield Paragraph(child, parent)
                    elif isinstance(child, CT_Tbl):
                        yield Table(child, parent)

            for block in iter_block_items(doc):
                if isinstance(block, Paragraph):
                    latex_body.append(self._process_docx_paragraph(block))
                elif isinstance(block, Table):
                    latex_body.append(self._process_docx_table(block))
            
            self.content = "\n\n".join(filter(None, latex_body))
        except Exception as e:
            raise RuntimeError(f"Error parsing DOCX: {e}")

    def _process_docx_paragraph(self, para):
        if not para.text.strip():
            return ""

        text = ""
        # Handle runs for bold/italic
        for run in para.runs:
            escaped_text = self._escape_latex(run.text)
            if run.bold:
                escaped_text = f"\\textbf{{{escaped_text}}}"
            if run.italic:
                escaped_text = f"\\textit{{{escaped_text}}}"
            text += escaped_text

        style_name = para.style.name.lower()
        
        if 'heading 1' in style_name:
            return f"\\section{{{text}}}"
        elif 'heading 2' in style_name:
            return f"\\subsection{{{text}}}"
        elif 'heading 3' in style_name:
            return f"\\subsubsection{{{text}}}"
        elif 'list' in style_name or 'bullet' in style_name:
            # Simple handling of lists (grouping logic omitted for brevity, treating as itemize)
            return f"\\begin{{itemize}}\n\\item {text}\n\\end{{itemize}}"
        else:
            return f"{text}\n"

    def _process_docx_table(self, table):
        rows = []
        num_cols = len(table.columns)
        col_spec = "|" + "l|" * num_cols
        
        for row in table.rows:
            cells = [self._escape_latex(cell.text.strip()) for cell in row.cells]
            rows.append(" & ".join(cells) + " \\\\ \\hline")
        
        table_content = "\n".join(rows)
        return f"\\begin{{table}}[H]\n\\centering\n\\begin{{tabular}}{{{col_spec}}}\n\\hline\n{table_content}\n\\end{{tabular}}\n\\end{{table}}"

    # ==========================
    # PDF HANDLING
    # ==========================
    def parse_pdf(self):
        """Extracts text from PDF using pdfplumber."""
        try:
            text_content = []
            with pdfplumber.open(self.input_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        # Clean up some common PDF extraction artifacts
                        clean_text = self._escape_latex(text)
                        text_content.append(clean_text)
            
            if not text_content:
                print("Warning: No text extracted. PDF might be scanned/image-only.")
                self.content = "% [WARNING: No text extracted from PDF]"
            else:
                # Treat double newlines as paragraphs
                full_text = "\n\n".join(text_content)
                self.content = full_text.replace("\n", " ") # Basic reflow
                
        except Exception as e:
            raise RuntimeError(f"Error parsing PDF: {e}")

    # ==========================
    # MARKDOWN HANDLING
    # ==========================
    def parse_markdown(self):
        """Parses Markdown using Regex mapping."""
        try:
            with open(self.input_path, 'r', encoding='utf-8') as f:
                md = f.read()

            # 1. Code Blocks (Handle first to avoid conflict)
            def code_block_repl(match):
                code = match.group(1)
                return f"\\begin{{lstlisting}}\n{code}\n\\end{{lstlisting}}"
            md = re.sub(r'```(.*?)```', code_block_repl, md, flags=re.DOTALL)

            # 2. Inline Code
            md = re.sub(r'`([^`]+)`', r'\\texttt{\1}', md)

            # 3. Headers
            md = re.sub(r'^# (.*)', r'\\section{\1}', md, flags=re.MULTILINE)
            md = re.sub(r'^## (.*)', r'\\subsection{\1}', md, flags=re.MULTILINE)
            md = re.sub(r'^### (.*)', r'\\subsubsection{\1}', md, flags=re.MULTILINE)

            # 4. Bold / Italic
            md = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', md)
            md = re.sub(r'\*(.*?)\*', r'\\textit{\1}', md)

            # 5. Lists (Simple unordered)
            # This is a basic conversion; nested lists are complex in regex
            lines = md.split('\n')
            in_list = False
            processed_lines = []
            
            for line in lines:
                if re.match(r'^\s*-\s+', line):
                    content = re.sub(r'^\s*-\s+', '', line)
                    if not in_list:
                        processed_lines.append(r'\begin{itemize}')
                        in_list = True
                    processed_lines.append(f'\\item {content}')
                else:
                    if in_list:
                        processed_lines.append(r'\end{itemize}')
                        in_list = False
                    processed_lines.append(line)
            
            if in_list: processed_lines.append(r'\end{itemize}')
            md = "\n".join(processed_lines)

            # 6. Paragraphs (Double newlines)
            # Latex handles blank lines as paragraphs automatically, 
            # but we need to escape special chars in the remaining text 
            # (which is hard to do safely after injecting latex commands).
            # Note: A production MD parser iterates an AST. 
            # Here we assume the regex replacements handled formatting 
            # and the rest is content.
            
            self.content = md

        except Exception as e:
            raise RuntimeError(f"Error parsing Markdown: {e}")

    # ==========================
    # TXT HANDLING
    # ==========================
    def parse_txt(self):
        """Parses Plain Text."""
        try:
            with open(self.input_path, 'r', encoding='utf-8') as f:
                text = f.read()
            
            # Escape and preserve paragraphs
            escaped = self._escape_latex(text)
            self.content = escaped
        except Exception as e:
            raise RuntimeError(f"Error parsing TXT: {e}")

    # ==========================
    # MAIN LOGIC
    # ==========================
    def convert(self):
        ext = os.path.splitext(self.input_path)[1].lower()
        
        print(f"Detected file type: {ext}")
        
        if ext == '.docx':
            self.parse_docx()
        elif ext == '.pdf':
            self.parse_pdf()
        elif ext == '.md':
            self.parse_markdown()
        elif ext == '.txt':
            self.parse_txt()
        else:
            raise ValueError(f"Unsupported file type: {ext}")

        full_document = f"{self._get_preamble()}\n\n{self.content}\n\n{self._get_postamble()}"
        
        with open(self.output_path, 'w', encoding='utf-8') as f:
            f.write(full_document)
        
        print(f"Conversion successful! Output saved to: {self.output_path}")

def main():
    parser = argparse.ArgumentParser(description="Convert DOCX/PDF/MD/TXT to LaTeX.")
    
    # Required Arguments
    parser.add_argument("input_file", help="Path to input file")
    
    # Optional Arguments
    parser.add_argument("-o", "--output", help="Path to output .tex file (default: input_filename.tex)")
    parser.add_argument("--doc_class", default="article", help="Document class (article, report, book)")
    parser.add_argument("--fontsize", default="12pt", help="Font size (10pt, 11pt, 12pt)")
    parser.add_argument("--margins", default="margin=1in", help="Geometry margin settings")
    parser.add_argument("--packages", help="Comma-separated list of extra packages to include")
    parser.add_argument("--custom_preamble", help="String to inject into preamble")

    args = parser.parse_args()

    input_path = args.input_file
    if not os.path.exists(input_path):
        print(f"Error: File '{input_path}' not found.")
        sys.exit(1)

    # Determine output filename if not provided
    if not args.output:
        base_name = os.path.splitext(input_path)[0]
        output_path = f"{base_name}.tex"
    else:
        output_path = args.output

    # Pack options
    options = {
        "doc_class": args.doc_class,
        "fontsize": args.fontsize,
        "margins": args.margins,
        "packages": args.packages,
        "custom_preamble": args.custom_preamble
    }

    try:
        converter = LatexConverter(input_path, output_path, options)
        converter.convert()
    except Exception as e:
        print(f"Error during conversion: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()