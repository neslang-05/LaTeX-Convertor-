import streamlit as st
import os
import tempfile
import shutil
from latex_converter import LatexConverter

def main():
    st.set_page_config(page_title="Document to LaTeX Converter", page_icon="📄")

    st.title("📄 Document to LaTeX Converter")
    st.write("Convert DOCX, PDF, Markdown, or Text files to LaTeX format.")

    # Sidebar for options
    st.sidebar.header("Configuration")
    
    doc_class = st.sidebar.selectbox(
        "Document Class", 
        ["article", "report", "book"], 
        index=0
    )
    
    fontsize = st.sidebar.selectbox(
        "Font Size", 
        ["10pt", "11pt", "12pt"], 
        index=2
    )
    
    margins = st.sidebar.text_input("Margins", value="margin=1in")
    
    packages = st.sidebar.text_input(
        "Extra Packages (comma-separated)", 
        placeholder="e.g. tikz, multirow"
    )
    
    custom_preamble = st.sidebar.text_area(
        "Custom Preamble", 
        placeholder="\\newcommand{\\mycmd}{...}"
    )

    # File Uploader
    uploaded_file = st.file_uploader(
        "Choose a file", 
        type=["docx", "pdf", "md", "txt"]
    )

    if uploaded_file is not None:
        st.info(f"File '{uploaded_file.name}' uploaded successfully.")
        
        if st.button("Convert to LaTeX"):
            with st.spinner("Converting..."):
                try:
                    # Create a temporary directory to handle files
                    with tempfile.TemporaryDirectory() as tmpdirname:
                        # Save uploaded file to temp dir
                        input_path = os.path.join(tmpdirname, uploaded_file.name)
                        with open(input_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        # Define output path
                        output_filename = os.path.splitext(uploaded_file.name)[0] + ".tex"
                        output_path = os.path.join(tmpdirname, output_filename)
                        
                        # Prepare options
                        options = {
                            "doc_class": doc_class,
                            "fontsize": fontsize,
                            "margins": margins,
                            "packages": packages,
                            "custom_preamble": custom_preamble
                        }
                        
                        # Run conversion
                        converter = LatexConverter(input_path, output_path, options)
                        converter.convert()
                        
                        # Read the generated LaTeX file
                        with open(output_path, "r", encoding="utf-8") as f:
                            latex_content = f.read()
                        
                        st.success("Conversion successful!")
                        
                        # Display preview (first 500 chars)
                        with st.expander("Preview LaTeX Code"):
                            st.code(latex_content, language="latex")
                        
                        # Download button
                        st.download_button(
                            label="Download .tex file",
                            data=latex_content,
                            file_name=output_filename,
                            mime="text/x-tex"
                        )
                        
                except Exception as e:
                    st.error(f"An error occurred during conversion: {e}")

if __name__ == "__main__":
    main()
