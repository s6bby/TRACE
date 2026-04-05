from __future__ import annotations

from collections import Counter
from datetime import datetime
from html import escape
from pathlib import Path
import sys

import streamlit as st
try:
    from pypdf import PdfReader
except ModuleNotFoundError:
    PdfReader = None

APP_DIR = Path(__file__).resolve().parent
SRC_DIR = APP_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from trace_core.orchestrator import TracePipeline
from trace_core.schemas import ClaimAssessment, ReliabilityReport, SourceDocument

PROJECT_ROOT = APP_DIR.parents[1]
ROOT_README_PATH = PROJECT_ROOT / "README.md"
TRACE_README_PATH = APP_DIR / "README.md"
PDF_UPLOAD_AVAILABLE = PdfReader is not None

TECHNICAL_DETAILS = """
## Technical Implementation

### Architecture
- **Orchestrator**: Coordinates the analysis pipeline
- **Claim Extraction**: Identifies individual claims from model responses
- **Evidence Retrieval**: Finds relevant text spans in source documents
- **Reliability Assessment**: Evaluates claim-document alignment

### Data Models
- `SourceDocument`: Contains document metadata and text
- `Claim`: Individual statement extracted from model output
- `EvidenceSpan`: Supporting text from source documents
- `ClaimAssessment`: Reliability judgment with evidence

### Supported File Types
- Plain text (`.txt`)
- PDF documents (`.pdf`) with automatic text extraction

### Performance Notes
- Handles large text documents for quick prototyping
- Supports multiple source files in a single run
- Returns a compact claim queue for live demo walkthroughs
"""

APP_CSS = """
<style>
    :root {
        --bg-top: #071018;
        --bg-bottom: #02050a;
        --paper: rgba(11, 18, 27, 0.82);
        --paper-strong: rgba(14, 22, 33, 0.96);
        --ink: #ecf2f8;
        --muted: #9eacbc;
        --line: rgba(151, 171, 195, 0.18);
        --accent: #2ec4b6;
        --accent-deep: #138b91;
        --accent-soft: rgba(46, 196, 182, 0.14);
        --warm: #f2b35d;
        --warm-soft: rgba(242, 179, 93, 0.14);
        --danger: #ff7a86;
        --danger-soft: rgba(255, 122, 134, 0.14);
        --success: #65d69b;
        --success-soft: rgba(101, 214, 155, 0.14);
        --shadow: 0 30px 80px rgba(0, 0, 0, 0.36);
        --radius-xl: 30px;
        --radius-lg: 24px;
        --radius-md: 18px;
    }

    html, body, [class*="css"] {
        font-family: "Avenir Next", "Helvetica Neue", sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at top left, rgba(46, 196, 182, 0.16), transparent 28%),
            radial-gradient(circle at top right, rgba(242, 179, 93, 0.12), transparent 22%),
            radial-gradient(circle at 50% 20%, rgba(19, 139, 145, 0.12), transparent 35%),
            linear-gradient(180deg, var(--bg-top) 0%, #050b12 45%, var(--bg-bottom) 100%);
        color: var(--ink);
    }

    [data-testid="stAppViewContainer"] > .main {
        background: transparent;
    }

    section.main > div,
    .block-container {
        max-width: 1040px;
        margin: 0 auto;
        padding-top: 2.4rem;
        padding-bottom: 4.4rem;
    }

    #MainMenu,
    footer,
    header,
    .stDeployButton {
        visibility: hidden;
    }

    h1, h2, h3, h4, h5 {
        color: var(--ink);
        letter-spacing: -0.02em;
    }

    a {
        color: #9ad8ff;
    }

    p, li, label {
        color: var(--ink);
    }

    div[data-testid="stMarkdownContainer"] ul,
    div[data-testid="stMarkdownContainer"] ol {
        color: var(--muted);
    }

    div[data-testid="stMarkdownContainer"] code,
    pre code {
        color: #d8f4ff;
    }

    pre {
        background: rgba(5, 11, 18, 0.92) !important;
        border: 1px solid var(--line);
        border-radius: 18px;
    }

    .hero-panel {
        position: relative;
        overflow: hidden;
        padding: 2.7rem;
        margin: 0 auto 1.5rem auto;
        max-width: 960px;
        background:
            linear-gradient(145deg, rgba(4, 10, 18, 0.98) 0%, rgba(10, 20, 31, 0.96) 42%, rgba(13, 45, 54, 0.94) 100%);
        border: 1px solid rgba(151, 171, 195, 0.18);
        border-radius: var(--radius-xl);
        box-shadow: 0 40px 90px rgba(0, 0, 0, 0.42);
        color: #f8fafc;
        text-align: center;
    }

    .hero-panel::before {
        content: "";
        position: absolute;
        inset: 1px;
        border-radius: calc(var(--radius-xl) - 1px);
        background:
            linear-gradient(180deg, rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0));
        pointer-events: none;
    }

    .hero-panel::after {
        content: "";
        position: absolute;
        inset: auto 50% -32% auto;
        transform: translateX(50%);
        width: 420px;
        height: 420px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(46, 196, 182, 0.18) 0%, rgba(46, 196, 182, 0) 72%);
        pointer-events: none;
    }

    .hero-kicker {
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
        padding: 0.45rem 0.8rem;
        margin-bottom: 1rem;
        background: rgba(255, 255, 255, 0.12);
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 999px;
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
    }

    .hero-title {
        margin: 0;
        font-size: clamp(2.25rem, 4.4vw, 4.2rem);
        line-height: 1;
        font-weight: 800;
        color: #f8fafc;
        max-width: 760px;
        margin-left: auto;
        margin-right: auto;
    }

    .hero-copy {
        max-width: 720px;
        margin: 1rem auto 0 auto;
        font-size: 1.04rem;
        line-height: 1.7;
        color: rgba(248, 250, 252, 0.82);
    }

    .hero-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 1rem;
        margin: 1.75rem auto 0 auto;
        max-width: 880px;
    }

    .hero-stat {
        padding: 1rem 1.05rem;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(151, 171, 195, 0.16);
        border-radius: 20px;
        backdrop-filter: blur(12px);
        text-align: left;
    }

    .hero-stat-label {
        display: block;
        margin-bottom: 0.45rem;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: rgba(248, 250, 252, 0.72);
    }

    .hero-stat-value {
        display: block;
        font-size: 1rem;
        font-weight: 700;
        line-height: 1.45;
        color: #f8fafc;
    }

    .section-kicker {
        margin-top: 0.5rem;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        color: var(--muted);
        text-align: center;
    }

    .section-title {
        margin: 0.35rem 0 0.35rem 0;
        font-size: 1.55rem;
        line-height: 1.1;
        font-weight: 800;
        text-align: center;
    }

    .section-copy {
        margin: 0 auto 1.2rem auto;
        max-width: 720px;
        color: var(--muted);
        line-height: 1.7;
        text-align: center;
    }

    .feature-card,
    .info-card,
    .metric-card,
    .summary-card,
    .assessment-shell,
    .evidence-card,
    .empty-state,
    .about-card {
        background: var(--paper);
        border: 1px solid var(--line);
        border-radius: var(--radius-lg);
        box-shadow: var(--shadow);
        backdrop-filter: blur(12px);
    }

    .feature-card,
    .info-card,
    .summary-card,
    .empty-state,
    .about-card {
        padding: 1.2rem 1.25rem;
    }

    .feature-card,
    .about-card,
    .metric-card {
        text-align: center;
    }

    .feature-card-title,
    .info-card-title,
    .summary-card-title,
    .about-card-title {
        margin: 0 0 0.35rem 0;
        font-size: 1rem;
        font-weight: 800;
        color: var(--ink);
    }

    .feature-card-copy,
    .info-card-copy,
    .summary-card-copy,
    .about-card-copy {
        margin: 0;
        color: var(--muted);
        line-height: 1.7;
    }

    .signal-list {
        display: grid;
        gap: 0.7rem;
        margin-top: 0.95rem;
    }

    .signal-item {
        display: flex;
        align-items: flex-start;
        gap: 0.8rem;
        color: var(--ink);
        line-height: 1.55;
    }

    .signal-dot {
        width: 10px;
        height: 10px;
        margin-top: 0.42rem;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--accent), var(--warm));
        flex: 0 0 auto;
    }

    .metric-card {
        padding: 1.15rem 1.2rem;
        min-height: 142px;
    }

    .metric-label {
        display: block;
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: var(--muted);
    }

    .metric-value {
        display: block;
        margin-top: 0.5rem;
        font-size: 2rem;
        line-height: 1;
        font-weight: 800;
        color: var(--ink);
    }

    .metric-caption {
        display: block;
        margin-top: 0.55rem;
        color: var(--muted);
        line-height: 1.55;
    }

    .metric-card.signal {
        background: linear-gradient(180deg, rgba(46, 196, 182, 0.14), rgba(11, 18, 27, 0.88));
    }

    .metric-card.success {
        background: linear-gradient(180deg, rgba(101, 214, 155, 0.14), rgba(11, 18, 27, 0.88));
    }

    .metric-card.warn {
        background: linear-gradient(180deg, rgba(242, 179, 93, 0.14), rgba(11, 18, 27, 0.88));
    }

    .metric-card.danger {
        background: linear-gradient(180deg, rgba(255, 122, 134, 0.14), rgba(11, 18, 27, 0.88));
    }

    .pill-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.55rem;
        margin-top: 0.95rem;
    }

    .pill {
        display: inline-flex;
        align-items: center;
        padding: 0.42rem 0.72rem;
        border-radius: 999px;
        border: 1px solid var(--line);
        background: rgba(255, 255, 255, 0.04);
        color: var(--ink);
        font-size: 0.86rem;
        font-weight: 600;
    }

    .assessment-shell {
        padding: 1.2rem 1.25rem;
        margin-bottom: 0.9rem;
        background: var(--paper-strong);
    }

    .assessment-topline {
        display: flex;
        flex-wrap: wrap;
        gap: 0.65rem;
        align-items: center;
        margin-bottom: 0.85rem;
    }

    .assessment-index {
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: var(--muted);
    }

    .status-pill,
    .priority-pill {
        display: inline-flex;
        align-items: center;
        padding: 0.36rem 0.65rem;
        border-radius: 999px;
        font-size: 0.77rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }

    .status-explicit {
        background: var(--success-soft);
        color: var(--success);
    }

    .status-inferred {
        background: var(--warm-soft);
        color: var(--warm);
    }

    .status-unsupported {
        background: var(--danger-soft);
        color: var(--danger);
    }

    .priority-high {
        background: var(--danger-soft);
        color: var(--danger);
    }

    .priority-normal {
        background: var(--accent-soft);
        color: var(--accent-deep);
    }

    .assessment-claim {
        margin: 0;
        font-size: 1.04rem;
        line-height: 1.65;
        color: var(--ink);
    }

    .assessment-note {
        margin: 0.9rem 0 0 0;
        color: var(--muted);
        line-height: 1.65;
    }

    .evidence-card {
        padding: 0.95rem 1rem;
        margin-top: 0.75rem;
        background: rgba(255, 255, 255, 0.03);
        box-shadow: none;
    }

    .evidence-label {
        display: block;
        margin-bottom: 0.4rem;
        font-size: 0.74rem;
        font-weight: 700;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: var(--muted);
    }

    .evidence-copy {
        margin: 0;
        color: var(--ink);
        line-height: 1.62;
    }

    .empty-state {
        padding: 1.4rem;
        margin-top: 1.25rem;
        text-align: center;
    }

    .empty-state-title {
        margin: 0;
        font-size: 1rem;
        font-weight: 800;
        color: var(--ink);
    }

    .empty-state-copy {
        margin: 0.55rem 0 0 0;
        color: var(--muted);
        line-height: 1.65;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0.45rem;
        padding: 0.38rem;
        margin-bottom: 1.1rem;
        justify-content: center;
        width: fit-content;
        margin-left: auto;
        margin-right: auto;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid var(--line);
        border-radius: 999px;
    }

    .stTabs [data-baseweb="tab"] {
        height: auto;
        padding: 0.7rem 1rem;
        border-radius: 999px;
        font-weight: 700;
        color: var(--muted);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(46, 196, 182, 0.18), rgba(19, 139, 145, 0.82));
        color: #f8fafc;
        box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.08);
    }

    .stTabs [aria-selected="true"] p {
        color: #f8fafc;
    }

    label[data-testid="stWidgetLabel"] p {
        color: var(--ink);
        font-weight: 700;
        letter-spacing: 0.01em;
    }

    div[data-testid="stFileUploader"] {
        padding: 0.9rem 1rem 1rem 1rem;
        border-radius: var(--radius-lg);
        background: var(--paper);
        border: 1px solid var(--line);
        box-shadow: var(--shadow);
    }

    section[data-testid="stFileUploaderDropzone"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px dashed rgba(151, 171, 195, 0.24);
    }

    section[data-testid="stFileUploaderDropzone"] * {
        color: var(--muted) !important;
    }

    div[data-baseweb="textarea"] {
        border-radius: 22px;
        border: 1px solid var(--line);
        background: var(--paper-strong);
        box-shadow: var(--shadow);
    }

    div[data-baseweb="textarea"] textarea {
        color: var(--ink);
        line-height: 1.65;
        background: transparent;
    }

    div[data-baseweb="textarea"] textarea::placeholder {
        color: #8a97a7;
    }

    div[data-baseweb="textarea"]:focus-within {
        border-color: rgba(46, 196, 182, 0.55);
        box-shadow: 0 0 0 1px rgba(46, 196, 182, 0.28), var(--shadow);
    }

    div[data-testid="stButton"] button {
        min-height: 3.35rem;
        border: none;
        border-radius: 999px;
        background: linear-gradient(135deg, #0f2433, var(--accent-deep));
        color: #f8fafc;
        font-size: 0.98rem;
        font-weight: 800;
        letter-spacing: 0.01em;
        box-shadow: 0 24px 50px rgba(0, 0, 0, 0.34);
        transition: transform 0.18s ease, box-shadow 0.18s ease;
    }

    div[data-testid="stButton"] button:hover {
        transform: translateY(-1px);
        box-shadow: 0 28px 56px rgba(0, 0, 0, 0.42);
    }

    details[data-testid="stExpander"] {
        overflow: hidden;
        border-radius: var(--radius-lg);
        border: 1px solid var(--line);
        background: rgba(255, 255, 255, 0.04);
        box-shadow: var(--shadow);
    }

    details[data-testid="stExpander"] summary {
        padding-top: 0.2rem;
        padding-bottom: 0.2rem;
    }

    div[data-testid="stStatusWidget"] {
        border-radius: var(--radius-lg);
        border: 1px solid var(--line);
        background: rgba(255, 255, 255, 0.05);
        box-shadow: var(--shadow);
    }

    div[data-testid="stAlert"] {
        border-radius: 20px;
        border: 1px solid var(--line);
        background: rgba(11, 18, 27, 0.92);
    }

    @media (min-width: 901px) {
        div[data-testid="stHorizontalBlock"] {
            align-items: stretch;
        }
    }

    @media (max-width: 900px) {
        .hero-panel {
            padding: 2rem;
        }

        .hero-grid {
            grid-template-columns: 1fr;
        }

        .hero-title {
            font-size: 2.5rem;
        }
    }
</style>
"""

st.set_page_config(
    page_title="TRACE Framework Demo",
    layout="wide",
    initial_sidebar_state="collapsed",
)
st.markdown(APP_CSS, unsafe_allow_html=True)


def initialize_session_state() -> None:
    defaults = {
        "last_report": None,
        "analysis_documents": 0,
        "analysis_timestamp": None,
        "last_document_names": [],
        "last_prompt": "",
        "last_response": "",
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def extract_text_from_pdf(file) -> str:
    if PdfReader is None:
        raise RuntimeError("PDF uploads require the optional pypdf dependency.")
    pdf_reader = PdfReader(file)
    pages = []
    for page in pdf_reader.pages:
        pages.append(page.extract_text() or "")
    return "\n".join(pages)


def parse_documents(uploaded_files) -> list[SourceDocument]:
    documents: list[SourceDocument] = []

    for file in uploaded_files:
        file.seek(0)

        if file.type == "application/pdf":
            text = extract_text_from_pdf(file)
        else:
            text = file.read().decode("utf-8", errors="ignore")

        documents.append(
            SourceDocument(
                document_id=file.name,
                title=file.name,
                text=text,
            )
        )

    return documents


def load_markdown(path: Path, fallback: str) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return fallback


def truncate_text(text: str, limit: int = 200) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
    return f"{compact[: limit - 3].rstrip()}..."


def summarize_report(report: ReliabilityReport) -> Counter:
    counts = Counter(assessment.label for assessment in report.assessments)
    counts["high_priority"] = sum(
        1 for assessment in report.assessments if assessment.review_priority == "high"
    )
    return counts


def render_section_header(kicker: str, title: str, copy: str) -> None:
    st.markdown(
        f"""
        <div class="section-kicker">{escape(kicker)}</div>
        <h2 class="section-title">{escape(title)}</h2>
        <p class="section-copy">{escape(copy)}</p>
        """,
        unsafe_allow_html=True,
    )


def render_metric_card(label: str, value: str, caption: str, tone: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card {escape(tone)}">
            <span class="metric-label">{escape(label)}</span>
            <span class="metric-value">{escape(value)}</span>
            <span class="metric-caption">{escape(caption)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_feature_card(title: str, copy: str) -> None:
    st.markdown(
        f"""
        <div class="feature-card">
            <h3 class="feature-card-title">{escape(title)}</h3>
            <p class="feature-card-copy">{escape(copy)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_info_card(title: str, intro: str, items: list[str]) -> None:
    signal_items = "".join(
        f"""
        <div class="signal-item">
            <span class="signal-dot"></span>
            <span>{escape(item)}</span>
        </div>
        """
        for item in items
    )
    st.markdown(
        f"""
        <div class="info-card">
            <h3 class="info-card-title">{escape(title)}</h3>
            <p class="info-card-copy">{escape(intro)}</p>
            <div class="signal-list">{signal_items}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_assessment_card(index: int, assessment: ClaimAssessment) -> None:
    claim_text = escape(assessment.claim.text)
    note = escape(assessment.note or "No additional evaluation note was returned.")
    label_text = assessment.label.replace("_", " ").title()
    priority_text = assessment.review_priority.title()
    expander_title = f"Claim {index}  |  {label_text}  |  {priority_text} priority"

    with st.expander(expander_title, expanded=index == 1 or assessment.review_priority == "high"):
        st.markdown(
            f"""
            <div class="assessment-shell">
                <div class="assessment-topline">
                    <span class="assessment-index">Claim {index}</span>
                    <span class="status-pill status-{escape(assessment.label)}">{escape(label_text)}</span>
                    <span class="priority-pill priority-{escape(assessment.review_priority)}">{escape(priority_text)} priority</span>
                </div>
                <p class="assessment-claim">{claim_text}</p>
                <p class="assessment-note">{note}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if assessment.evidence:
            for evidence in assessment.evidence[:3]:
                section_text = f" | {evidence.section}" if evidence.section else ""
                st.markdown(
                    f"""
                    <div class="evidence-card">
                        <span class="evidence-label">Source: {escape(evidence.document_id)}{escape(section_text)}</span>
                        <p class="evidence-copy">{escape(truncate_text(evidence.snippet, 280) or "No snippet available.")}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                """
                <div class="empty-state">
                    <p class="empty-state-title">No supporting evidence returned</p>
                    <p class="empty-state-copy">This claim should stay in the manual review queue until a stronger retrieval step is added.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_report(
    report: ReliabilityReport,
    document_count: int,
    analysis_timestamp: str | None,
    document_names: list[str],
    user_prompt: str,
) -> None:
    counts = summarize_report(report)
    total_claims = len(report.assessments)

    render_section_header(
        "Live Output",
        "Reliability summary built for a walkthrough",
        "The report surfaces the key numbers first, then a compact claim queue with evidence snippets for each assessment.",
    )

    metric_columns = st.columns(4, gap="medium")
    with metric_columns[0]:
        render_metric_card(
            "Claims Reviewed",
            str(total_claims),
            "Distinct claims extracted from the model response.",
            "signal",
        )
    with metric_columns[1]:
        render_metric_card(
            "Explicit Support",
            str(counts.get("explicit", 0)),
            "Claims directly grounded in uploaded material.",
            "success",
        )
    with metric_columns[2]:
        render_metric_card(
            "Inferred Support",
            str(counts.get("inferred", 0)),
            "Claims with candidate evidence but no strict proof label yet.",
            "warn",
        )
    with metric_columns[3]:
        render_metric_card(
            "Manual Review",
            str(counts.get("unsupported", 0)),
            "Claims that still need stronger evidence retrieval.",
            "danger",
        )

    overview_tab, queue_tab = st.tabs(["Overview", "Claim Queue"])

    with overview_tab:
        overview_columns = st.columns([1.05, 0.95], gap="large")

        with overview_columns[0]:
            summary_items = [
                f"{document_count} source document(s) supplied to the analysis.",
                f"{counts.get('high_priority', 0)} claim(s) marked high priority for follow-up.",
                "Current evaluator is still a placeholder, so inferred support dominates early demos.",
            ]
            render_info_card(
                "Executive summary",
                "TRACE is optimized here for fast on-screen explanation: what was reviewed, what looks stable, and where the operator should focus next.",
                summary_items,
            )

            if user_prompt:
                st.markdown(
                    f"""
                    <div class="summary-card">
                        <h3 class="summary-card-title">Prompt context</h3>
                        <p class="summary-card-copy">{escape(truncate_text(user_prompt, 320))}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with overview_columns[1]:
            pills = "".join(
                f'<span class="pill">{escape(name)}</span>'
                for name in document_names[:8]
            )
            if len(document_names) > 8:
                pills += f'<span class="pill">+{len(document_names) - 8} more</span>'

            timestamp_text = analysis_timestamp or "Not recorded"
            st.markdown(
                f"""
                <div class="summary-card">
                    <h3 class="summary-card-title">Run details</h3>
                    <p class="summary-card-copy">Last analysis: {escape(timestamp_text)}</p>
                    <div class="pill-row">{pills or '<span class="pill">No document names available</span>'}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with queue_tab:
        ordered_assessments = sorted(
            enumerate(report.assessments, start=1),
            key=lambda item: (item[1].review_priority != "high", item[0]),
        )

        if ordered_assessments:
            for index, assessment in ordered_assessments:
                render_assessment_card(index, assessment)
        else:
            st.markdown(
                """
                <div class="empty-state">
                    <p class="empty-state-title">No claims were extracted</p>
                    <p class="empty-state-copy">Add one or more non-empty lines in the response field so TRACE has units to score.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )


def run_analysis(uploaded_files, user_prompt: str, llm_response: str) -> None:
    with st.status("Running TRACE analysis", expanded=True) as status:
        try:
            st.write("Parsing uploaded documents.")
            documents = parse_documents(uploaded_files)

            st.write(f"Prepared {len(documents)} source document(s) for retrieval.")
            pipeline = TracePipeline()

            st.write("Extracting claims, retrieving evidence, and assigning support labels.")
            report = pipeline.run(
                case_id="analysis",
                response_text=llm_response,
                documents=documents,
            )

            st.write("Packaging the final reliability report for display.")
            st.session_state.last_report = report
            st.session_state.analysis_documents = len(documents)
            st.session_state.analysis_timestamp = datetime.now().strftime("%b %d, %Y at %I:%M %p")
            st.session_state.last_document_names = [document.title for document in documents]
            st.session_state.last_prompt = user_prompt.strip()
            st.session_state.last_response = llm_response.strip()

            status.update(label="TRACE analysis complete", state="complete", expanded=False)
        except Exception as exc:
            status.update(label="TRACE analysis failed", state="error", expanded=True)
            st.error(f"TRACE could not complete the analysis: {exc}")


def render_demo_tab() -> None:
    st.markdown(
        """
        <section class="hero-panel">
            <div class="hero-kicker">TRACE Reliability Studio</div>
            <h1 class="hero-title">A sharper interface for grounded AI review.</h1>
            <p class="hero-copy">
                Upload source material, paste a model answer, and walk through a clean claim-by-claim
                reliability assessment that reads well in a live demo.
            </p>
            <div class="hero-grid">
                <div class="hero-stat">
                    <span class="hero-stat-label">Review Mode</span>
                    <span class="hero-stat-value">Claim queue with evidence context and priority signaling.</span>
                </div>
                <div class="hero-stat">
                    <span class="hero-stat-label">Demo Posture</span>
                    <span class="hero-stat-value">Wide layout, stronger hierarchy, and cleaner outputs for presentations.</span>
                </div>
                <div class="hero-stat">
                    <span class="hero-stat-label">Current Engine</span>
                    <span class="hero-stat-value">Lightweight prototype pipeline with placeholder extraction, retrieval, and scoring.</span>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    feature_columns = st.columns(3, gap="medium")
    with feature_columns[0]:
        render_feature_card(
            "Presentation-first flow",
            "The landing section now frames the product quickly so you can explain the value before touching the controls.",
        )
    with feature_columns[1]:
        render_feature_card(
            "Cleaner operator workspace",
            "Inputs are grouped for a walkthrough, with tighter copy and one clear primary action.",
        )
    with feature_columns[2]:
        render_feature_card(
            "Richer result surface",
            "Analysis output persists after a run and opens as metrics plus an expandable review queue.",
        )

    render_section_header(
        "Workspace",
        "Built for a concise live demo",
        "Use a few strong source files and a response broken into separate lines. TRACE treats each non-empty line as a distinct claim in the current prototype.",
    )

    workspace_columns = st.columns([1.15, 0.85], gap="large")

    with workspace_columns[0]:
        accepted_types = ["pdf", "txt"] if PDF_UPLOAD_AVAILABLE else ["txt"]
        upload_help = (
            "Upload PDF or text files that TRACE can use as grounding material."
            if PDF_UPLOAD_AVAILABLE
            else "Upload text files that TRACE can use as grounding material. PDF support is disabled until pypdf is installed."
        )

        uploaded_files = st.file_uploader(
            "Source documents",
            accept_multiple_files=True,
            type=accepted_types,
            help=upload_help,
        )

        if not PDF_UPLOAD_AVAILABLE:
            st.warning("PDF uploads are disabled in this environment because `pypdf` is not installed.")

        user_prompt = st.text_area(
            "Prompt context",
            height=110,
            placeholder="Optional: paste the user prompt or task instructions that led to the model response.",
            help="Optional context for the operator during the demo.",
        )

        llm_response = st.text_area(
            "Model response",
            height=240,
            placeholder="Paste the model response here. Each non-empty line becomes a separate claim in the current demo pipeline.",
            help="TRACE analyzes the response text against the uploaded documents.",
        )

        analyze_clicked = st.button(
            "Run TRACE analysis",
            type="primary",
            use_container_width=True,
        )

        if analyze_clicked:
            if not uploaded_files:
                st.error("Upload at least one source document before running the demo.")
            elif not llm_response.strip():
                st.error("Paste a model response so TRACE has claims to evaluate.")
            else:
                run_analysis(uploaded_files, user_prompt, llm_response)

    with workspace_columns[1]:
        render_info_card(
            "Demo checklist",
            "The new layout is optimized for a short operator narrative, not a crowded control panel.",
            [
                "Open with the hero section to frame TRACE as a reliability review surface.",
                "Use a response with 3 to 6 lines so the claim queue feels curated on screen.",
                "Call out unsupported claims first to show where human review still matters.",
            ],
        )
        render_info_card(
            "Prototype boundaries",
            "The interface is demo-ready, but the pipeline remains intentionally lightweight.",
            [
                "Claim extraction is line-based today.",
                "Retrieval still returns leading document snippets.",
                "Support labels remain placeholder judgments until the constrained evaluator is added.",
            ],
        )

    report = st.session_state.last_report
    if report is None:
        st.markdown(
            """
            <div class="empty-state">
                <p class="empty-state-title">No analysis run yet</p>
                <p class="empty-state-copy">Run the demo once and the result surface will stay visible here, ready for a walkthrough.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        render_report(
            report=report,
            document_count=st.session_state.analysis_documents,
            analysis_timestamp=st.session_state.analysis_timestamp,
            document_names=st.session_state.last_document_names,
            user_prompt=st.session_state.last_prompt,
        )


def render_documentation_tab() -> None:
    render_section_header(
        "Documentation",
        "Project context and implementation notes",
        "The original research framing is still available in-app, now presented in a cleaner reading surface alongside the streamlined demo experience.",
    )

    doc_tabs = st.tabs(["Repository", "TRACE Framework", "Technical Notes"])

    with doc_tabs[0]:
        st.markdown(
            load_markdown(ROOT_README_PATH, "Repository README not found."),
        )

    with doc_tabs[1]:
        st.markdown(
            load_markdown(TRACE_README_PATH, "TRACE README not found."),
        )

    with doc_tabs[2]:
        st.markdown(TECHNICAL_DETAILS)


def render_about_tab() -> None:
    render_section_header(
        "About TRACE",
        "A research prototype for document-grounded reliability review",
        "TRACE explores whether model outputs can be decomposed into claims, checked against evidence, and surfaced in a way that makes human review faster and more defensible.",
    )

    about_columns = st.columns(3, gap="medium")
    cards = [
        (
            "Core purpose",
            "Evaluate LLM outputs against source material at the claim level, with an interface that highlights evidence and uncertainty instead of hiding them.",
        ),
        (
            "Current scope",
            "This version focuses on demoability and architecture clarity, not final retrieval quality or model-driven evaluation rigor.",
        ),
        (
            "Next step",
            "Replace placeholder claim extraction and evidence scoring with constrained pipeline stages while preserving the cleaner presentation layer.",
        ),
    ]

    for column, (title, copy) in zip(about_columns, cards):
        with column:
            st.markdown(
                f"""
                <div class="about-card">
                    <h3 class="about-card-title">{escape(title)}</h3>
                    <p class="about-card-copy">{escape(copy)}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        """
        <div class="summary-card" style="margin-top: 1rem;">
            <h3 class="summary-card-title">Why the interface changed</h3>
            <p class="summary-card-copy">
                The previous layout was functional but plain. This version leans into presentation quality:
                stronger hierarchy, better pacing, clearer analysis output, and a visual system that feels
                deliberate during a demo instead of default.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


initialize_session_state()

demo_tab, documentation_tab, about_tab = st.tabs(["Demo", "Documentation", "About"])

with demo_tab:
    render_demo_tab()

with documentation_tab:
    render_documentation_tab()

with about_tab:
    render_about_tab()
