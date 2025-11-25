import streamlit as st
import tempfile, os, json
from utils.pdf_reader import extract_text_from_pdf
from utils.template_parser import extract_placeholders, extract_labels
from utils.llm_processor import call_deepseek_extract
from utils.doc_filler import fill_template

st.set_page_config(page_title="GLR Pipeline", layout="wide")
st.title("GLR Pipeline — Auto-fill Insurance Template (OpenRouter / DeepSeek)")

template_file = st.file_uploader("Upload insurance template (.docx)", type=["docx"])
pdf_files = st.file_uploader("Upload photo report(s) (.pdf)", type=["pdf"], accept_multiple_files=True)

if st.button("Process & Generate"):

    if not template_file:
        st.error("Upload a template .docx file.")
        st.stop()
    if not pdf_files:
        st.error("Upload at least one PDF.")
        st.stop()

    # Save template to temp path for parsing
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as ttmp:
        ttmp.write(template_file.read())
        template_path = ttmp.name

    st.info("Extracting text from PDFs...")
    combined = ""
    temp_pdf_paths = []
    for pdf in pdf_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as ptmp:
            ptmp.write(pdf.read())
            temp_pdf_paths.append(ptmp.name)
            extracted = extract_text_from_pdf(ptmp.name)
            combined += extracted + "\n\n"

    st.success("PDF text extracted.")

    st.info("Detecting template fields...")
    placeholders = extract_placeholders(template_path)
    mappings = None
    if placeholders:
        st.success(f"Placeholders found: {placeholders}")
        keys = placeholders
    else:
        st.info("No placeholders — extracting labels from template...")
        mappings = extract_labels(template_path)
        if not mappings:
            st.error("Could not extract fields from template. Add clear labels (like 'Client Name:') or placeholders.")
            st.stop()
        st.success("Detected labels: " + ", ".join([m["label"] for m in mappings]))
        keys = [m["key"] for m in mappings]

    st.info("Calling LLM to extract values...")
    try:
        kv = call_deepseek_extract(combined, mappings if mappings else keys)
    except Exception as e:
        st.error("LLM call failed: " + str(e))
        st.stop()

    st.write("LLM Output (raw):")
    st.code(json.dumps(kv, indent=2))

    # Ensure kv has string values for all keys
    final_kv = {}
    for k in keys:
        val = kv.get(k, "")
        if val is None:
            val = ""
        final_kv[k] = str(val)

    # Fill template
    st.info("Filling template...")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as outtmp:
        output_path = outtmp.name

    # For placeholder mode, template_path is used; for label mode, mappings passed
    fill_template(template_path, output_path, final_kv, mappings if mappings else None)

    st.success("Generated document ready.")
    with open(output_path, "rb") as f:
        st.download_button("Download filled document", f, file_name="filled_report.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
