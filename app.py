import asyncio
import gradio as gr
from client import extract_data, main  # Ensure main returns a report string

CUSTOM_CSS = r"""
/* === Global Reset === */
*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

/* === Page Background & Typography === */
body {
  background: linear-gradient(135deg, #f8fafc 0%, #e9f1fb 100%);
  font-family: 'Inter', sans-serif;
  color: #232b36;
  min-height: 100vh;
}

/* === Header === */
#header {
  text-align: center;
  padding: 48px 0 24px 0;
}
#header h1 {
  font-size: 3rem;
  color: #f3f7ff;
  margin-bottom: 10px;
  letter-spacing: -1px;
  font-weight: 700;
  text-shadow: 0 2px 18px rgba(180,200,255,0.22),
               0 2px 12px rgba(180,200,255,0.12);
}
#header p {
  font-size: 1.125rem;
  color: #e3eafc;
  font-weight: 400;
}

/* === Upload & Output Panels === */
.upload-section,
.output-section {
  background: rgba(34, 40, 49, 0.92);
  border-radius: 18px;
  box-shadow: 0 8px 32px rgba(31, 38, 135, 0.18);
  padding: 36px 28px;
  margin-bottom: 32px;
  backdrop-filter: blur(4px);
  border: 1px solid rgba(255,255,255,0.08);
  width: 100%;
  max-width: 100%;
}

/* === Output Section: Scroll & Wrap === */
.output-section {
  max-height: 500px;        /* Adjust as needed */
  overflow-y: auto;
  overflow-x: auto;
  white-space: pre-wrap;    /* allow wrapping */
  word-break: break-word;
}

/* Force all nested content to wrap inside output */
.output-section * {
  white-space: normal !important;
  overflow-wrap: break-word !important;
  word-break: break-word !important;
}

/* === Code & Pre Blocks === */
.output-section pre {
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-word;
  background: rgba(255,255,255,0.05);
  padding: 0.75rem;
  border-radius: 6px;
  font-size: 0.9rem;
  line-height: 1.4;
}
.output-section code {
  background: rgba(255,255,255,0.1);
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-family: monospace;
  font-size: 0.95rem;
}

/* === Typography Inside Panels === */
.upload-section strong,
.output-section strong {
  color: #e3eafc;
  font-weight: 600;
  letter-spacing: 0.02em;
}
.output-section p,
.output-section li {
  color: #f0f4ff !important;
}

/* === Analyze Button === */
#run_btn {
  background: linear-gradient(90deg, #5c7cfa 0%, #4263eb 100%) !important;
  color: #fff !important;
  border-radius: 8px;
  padding: 14px 28px;
  font-size: 1.05rem;
  border: none;
  box-shadow: 0 2px 8px rgba(92,124,250,0.10);
  transition: background 0.2s, box-shadow 0.2s;
}
#run_btn:hover {
  background: linear-gradient(90deg, #4263eb 0%, #364fc7 100%) !important;
  box-shadow: 0 4px 16px rgba(92,124,250,0.18);
}
.gr-button:focus {
  outline: none;
  box-shadow: 0 0 0 2px rgba(92,124,250,0.25);
}

/* === Footer Links === */
footer a {
  color: #5c7cfa;
  text-decoration: underline;
}
"""


def run_pipeline(image) -> str:
    with open(image.name, "rb") as f:
        image_bytes = f.read()

    extracted = extract_data(image_bytes)
    if not extracted:
        return "<div style='color:#d32f2f;'><strong>Error:</strong> Data extraction failed. Please try a higher-resolution image.</div>"
    try:
        report = asyncio.run(main(extracted))
    except Exception as e:
        return f"<div style='color:#d32f2f;'><strong>Analysis Error:</strong> {e}</div>"
    return report


with gr.Blocks(css=CUSTOM_CSS, title="Financial Forensics Analyzer") as demo:
    # Header
    with gr.Row(elem_id="header"):
        gr.Markdown("""
        <h1> GhostEquity: Financial Forensics Agent</h1>
        <p>AI-driven extraction & analysis of historical share certificates.</p>
        """)

    # Content Sections
    with gr.Row():
        with gr.Column(scale=1, elem_classes="upload-section"):
            gr.Markdown("<strong>1. Upload Certificate</strong>")
            cert_input = gr.File(label="Choose Image (.jpg, .png)", file_types=['.jpg', '.jpeg', '.png'])
            run_btn = gr.Button("Analyze Certificate", elem_id="run_btn")

        with gr.Column(scale=1, elem_classes="output-section"):
            gr.Markdown("<strong>2. Analysis Report</strong>")
            output_area = gr.Markdown()

    # Enable Gradio queueing and show a built-in progress bar
    demo.queue()
    run_btn.click(
        fn=run_pipeline,
        inputs=cert_input,
        outputs=output_area,
        show_progress="full"
    )

    # Footer
    gr.Markdown("---")
    gr.Markdown(
        "<div style='text-align:center; font-size:0.9rem; color:#9aa5b1;'>"
        "Powered by Gemini and MCP"
        "</div>"
    )
    gr.Markdown(
        "<div style='text-align:center; font-size:0.9rem; color:#9aa5b1;'>"
        "Made with ❤️ by &nbsp; <a href='https://github.com/Atharva-Jayappa' style='color:#5c7cfa; text-decoration:underline;' target='_blank'>Atharva-Jayappa</a>"
        "</div>"
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
