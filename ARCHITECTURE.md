# 🎨 SmartAlly Visual Architecture Guide

## Complete System Flowchart

### Level 1: User Journey

```
START
  │
  ├─> 1. User opens web browser
  │     └─> http://localhost:8501
  │
  ├─> 2. Upload Documents
  │     ├─> Select PDF files
  │     ├─> Select HTML files
  │     └─> Wait for parsing (5-10 sec)
  │
  ├─> 3. Configure Settings
  │     ├─> Enable LLM mode (if API key available)
  │     └─> Or use Fallback mode (automatic)
  │
  ├─> 4. Ask Question
  │     └─> Type: "What is the total annual operating expenses for Class A?"
  │
  ├─> 5. View Results
  │     ├─> See extracted value: "1.19%"
  │     ├─> See location: "Annual Fund Operating Expenses"
  │     └─> Click page link: "📄 Page 3"
  │
  └─> 6. Verify & Continue
        ├─> Click link to see source
        └─> Ask more questions
```

### Level 2: Technical Architecture

```
┌───────────────────────────────────────────────────────────────────────┐
│                                                                       │
│                        SMARTALLY ARCHITECTURE                         │
│                                                                       │
├───────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Layer 1: PRESENTATION (Web UI)                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                      Streamlit App                          │    │
│  │  ┌─────────────┐  ┌──────────┐  ┌─────────────────────┐   │    │
│  │  │  File       │  │  Chat    │  │  Settings           │   │    │
│  │  │  Uploader   │  │  Input   │  │  (LLM Toggle)       │   │    │
│  │  └─────────────┘  └──────────┘  └─────────────────────┘   │    │
│  │  ┌─────────────────────────────────────────────────────┐   │    │
│  │  │        Chat History Display & Results               │   │    │
│  │  └─────────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                       │
├───────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Layer 2: DOCUMENT PROCESSING                                        │
│  ┌──────────────┐  ┌───────────────┐  ┌────────────────────┐       │
│  │   PyMuPDF    │  │  pdfplumber   │  │  BeautifulSoup4    │       │
│  │              │  │               │  │                    │       │
│  │  • Text      │  │  • Tables     │  │  • HTML Tags       │       │
│  │  • Pages     │  │  • Cells      │  │  • Anchors         │       │
│  │  • Metadata  │  │  • Structure  │  │  • Content         │       │
│  └──────────────┘  └───────────────┘  └────────────────────┘       │
│                                                                       │
├───────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Layer 3: INTELLIGENT EXTRACTION                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    MODE SELECTOR                              │  │
│  │         ┌────────────────┬─────────────────────┐             │  │
│  │         │   LLM Mode     │   Fallback Mode     │             │  │
│  │         │  (GPT-3.5)     │   (Rule-Based)      │             │  │
│  │         └────────────────┴─────────────────────┘             │  │
│  │                  │                    │                       │  │
│  │                  ↓                    ↓                       │  │
│  │         ┌────────────────┐   ┌─────────────────┐            │  │
│  │         │  Query Parser  │   │  Regex Parser   │            │  │
│  │         │   (AI-based)   │   │  (Pattern)      │            │  │
│  │         └────────────────┘   └─────────────────┘            │  │
│  │                  │                    │                       │  │
│  │                  ↓                    ↓                       │  │
│  │         ┌────────────────┐   ┌─────────────────┐            │  │
│  │         │ Data Extractor │   │ Data Extractor  │            │  │
│  │         │   (AI-based)   │   │  (Regex-based)  │            │  │
│  │         └────────────────┘   └─────────────────┘            │  │
│  │                  │                    │                       │  │
│  │                  └────────┬───────────┘                       │  │
│  │                           ↓                                   │  │
│  │                  ┌────────────────┐                          │  │
│  │                  │  Page Locator  │                          │  │
│  │                  └────────────────┘                          │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                       │
├───────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Layer 4: DATA MANAGEMENT                                            │
│  ┌──────────────┐  ┌───────────────┐  ┌────────────────────┐       │
│  │   pandas     │  │   Session     │  │  Datapoint         │       │
│  │              │  │   Cache       │  │  Mappings (CSV)    │       │
│  │  • CSV ops   │  │               │  │                    │       │
│  │  • DataFrames│  │  • Documents  │  │  • Instructions    │       │
│  │  • Filtering │  │  • History    │  │  • Output Rules    │       │
│  └──────────────┘  └───────────────┘  └────────────────────┘       │
│                                                                       │
├───────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Layer 5: EXTERNAL SERVICES                                          │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │           OpenAI GPT-3.5 Turbo API                           │   │
│  │  • Natural Language Understanding                            │   │
│  │  • Data Extraction                                           │   │
│  │  • Context Analysis                                          │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

### Level 3: Detailed Data Flow

```
QUERY: "What is the total annual operating expenses for Class A?"
│
├─> STEP 1: RECEIVE QUERY
│   │
│   └─> Streamlit chat input captures user query
│       └─> Check if documents are loaded
│
├─> STEP 2: CHOOSE MODE
│   │
│   ├─> If API Key Available → LLM Mode
│   │   │
│   │   └─> Send to GPT-3.5 Turbo
│   │       │
│   │       ├─> Parse Query
│   │       │   ├─> Identify: "TOTAL_ANNUAL_FUND_OPERATING_EXPENSES"
│   │       │   └─> Extract: "Class A"
│   │       │
│   │       ├─> Extract Data
│   │       │   ├─> Search document text
│   │       │   ├─> Search tables
│   │       │   ├─> Find value: "1.19%"
│   │       │   └─> Capture context: "Annual Fund Operating Expenses"
│   │       │
│   │       └─> Locate Page
│   │           ├─> Match context to page content
│   │           └─> Find: Page 3
│   │
│   └─> If No API Key → Fallback Mode
│       │
│       └─> Use Regex Patterns
│           │
│           ├─> Parse Query
│           │   ├─> Match keywords
│           │   └─> Extract class from pattern
│           │
│           ├─> Extract Data
│           │   ├─> Apply regex to text
│           │   ├─> Search tables by position
│           │   └─> Find value: "1.19%"
│           │
│           └─> Locate Page (approximate)
│               └─> Search for section keywords
│
├─> STEP 3: FORMAT RESPONSE
│   │
│   ├─> Apply output rule: "percentage"
│   │   └─> Format as: "1.19%"
│   │
│   ├─> Create location description
│   │   └─> "Annual Fund Operating Expenses"
│   │
│   └─> Generate hyperlink
│       └─> "📄 Page 3"
│
└─> STEP 4: DISPLAY RESULT
    │
    └─> "The total annual fund operating expenses for Class A is 1.19%
         (found in Annual Fund Operating Expenses - 📄 Page 3)"
```

## Processing Pipeline Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                       DOCUMENT UPLOAD PIPELINE                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
        │
        ├─> PDF File Uploaded
        │   │
        │   ├─> Step 1: PyMuPDF Text Extraction
        │   │   └─> Extract text from each page
        │   │       └─> Store in Dict[page_num -> text]
        │   │
        │   ├─> Step 2: pdfplumber Table Extraction
        │   │   └─> Detect tables in each page
        │   │       └─> Store in Dict[page_num -> List[tables]]
        │   │
        │   └─> Step 3: Cache Results
        │       └─> Save to session_state['parsed_docs']
        │
        └─> HTML File Uploaded
            │
            ├─> Step 1: BeautifulSoup Parsing
            │   └─> Parse HTML structure
            │       └─> Extract text and preserve anchors
            │
            └─> Step 2: Cache Results
                └─> Save to session_state['parsed_docs']

┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                       QUERY PROCESSING PIPELINE                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
        │
        ├─> User Query Received
        │   └─> "What is the total annual operating expenses for Class A?"
        │
        ├─> Load Cached Documents
        │   ├─> Get text from all pages
        │   └─> Get all extracted tables
        │
        ├─> Mode Selection
        │   │
        │   ├─> LLM Mode (if API key configured)
        │   │   │
        │   │   ├─> Call: parse_user_prompt_with_llm()
        │   │   │   ├─> Input: User query + datapoint list
        │   │   │   ├─> Output: Datapoint name + Class
        │   │   │   └─> Uses: GPT-3.5 with JSON response
        │   │   │
        │   │   └─> Call: extract_datapoint_with_llm()
        │   │       ├─> Input: Text + Tables + Datapoint + Class
        │   │       ├─> Output: Value + Location + Page
        │   │       └─> Uses: GPT-3.5 with context analysis
        │   │
        │   └─> Fallback Mode (automatic without API key)
        │       │
        │       ├─> Call: parse_user_prompt_fallback()
        │       │   ├─> Input: User query
        │       │   ├─> Output: Datapoint name + Class
        │       │   └─> Uses: Regex pattern matching
        │       │
        │       └─> Call: extract_datapoint()
        │           ├─> Input: Text + Tables + Datapoint + Class
        │           ├─> Output: Value + Location
        │           └─> Uses: Regex + table lookup
        │
        ├─> Format Response
        │   ├─> Apply output rule (currency, percentage, text)
        │   ├─> Generate hyperlink with page number
        │   └─> Create user-friendly message
        │
        └─> Display in Chat
            └─> Add to message history
            └─> Render in Streamlit interface
```

## Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                    COMPONENT INTERACTIONS                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │     User     │
    └──────┬───────┘
           │ Uploads files & asks questions
           ↓
    ┌──────────────┐
    │  Streamlit   │───────────────┐
    │     App      │               │
    └──────┬───────┘               │
           │                       │
           │ Parse documents       │ Load config
           ↓                       ↓
    ┌──────────────┐        ┌─────────────────┐
    │  Document    │        │  datapoint_     │
    │  Parsers     │        │  mapping.csv    │
    └──────┬───────┘        └─────────────────┘
           │
           │ Extracted text & tables
           ↓
    ┌──────────────┐
    │  Session     │
    │  Cache       │
    └──────┬───────┘
           │
           │ Cached documents
           ↓
    ┌──────────────────────┐
    │  Extraction Engine   │
    └──────┬───────────────┘
           │
           ├──> LLM Mode ─────────────┐
           │                          │
           │                          ↓
           │                   ┌──────────────┐
           │                   │  OpenAI API  │
           │                   └──────┬───────┘
           │                          │
           │                          │ AI response
           │                          ↓
           └──> Fallback Mode ───────→ ┌──────────────┐
                                        │   Results    │
                                        └──────┬───────┘
                                               │
                                               │ Formatted results
                                               ↓
                                        ┌──────────────┐
                                        │   Display    │
                                        │   to User    │
                                        └──────────────┘
```

## State Management Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                     SESSION STATE MANAGEMENT                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

Streamlit Session State:
│
├─> session_state['messages']
│   └─> List of chat messages
│       ├─> {"role": "user", "content": "What is..."}
│       └─> {"role": "assistant", "content": "The value is..."}
│
├─> session_state['parsed_docs']
│   └─> Dict of parsed documents
│       ├─> "document1.pdf"
│       │   ├─> 'pages': {1: "text...", 2: "text..."}
│       │   ├─> 'tables': {1: [...], 2: [...]}
│       │   └─> 'type': 'pdf'
│       └─> "document2.html"
│           ├─> 'pages': {1: "text..."}
│           └─> 'type': 'html'
│
├─> session_state['use_llm']
│   └─> Boolean flag for LLM mode
│       ├─> True: Use GPT-3.5 Turbo
│       └─> False: Use regex fallback
│
└─> Environment Variables (.env file)
    ├─> OPENAI_API_KEY
    └─> OPENAI_MODEL
```

## Error Handling Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                        ERROR HANDLING FLOW                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

User Action
    │
    ↓
┌─────────────────────────────────────┐
│  Try: Process Request               │
└─────────────────────────────────────┘
    │
    ├─> Success
    │   └─> Return results to user
    │
    └─> Error Detected
        │
        ├─> API Key Missing
        │   └─> Automatically switch to Fallback Mode
        │       └─> Continue processing
        │
        ├─> API Request Failed
        │   ├─> Show warning to user
        │   └─> Fallback to rule-based extraction
        │       └─> Return approximate results
        │
        ├─> Document Parsing Error
        │   ├─> Show error message
        │   └─> Suggest: Check file format
        │
        ├─> Value Not Found
        │   ├─> Return: "Value not found" or "0"
        │   └─> Suggest: Try different query
        │
        └─> Unknown Error
            ├─> Log error details
            ├─> Show user-friendly message
            └─> Graceful degradation
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                       DEPLOYMENT OPTIONS                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

OPTION 1: Local Development
┌────────────────────────────────────┐
│  Developer Machine                 │
│  ┌──────────────────────────────┐  │
│  │  Python 3.8+                 │  │
│  │  ├─> Install dependencies    │  │
│  │  ├─> Configure .env          │  │
│  │  └─> Run: streamlit run      │  │
│  └──────────────────────────────┘  │
│  Access: http://localhost:8501     │
└────────────────────────────────────┘

OPTION 2: Cloud Deployment (Streamlit Cloud)
┌────────────────────────────────────┐
│  Streamlit Cloud                   │
│  ┌──────────────────────────────┐  │
│  │  GitHub Repository           │  │
│  │  ├─> Auto-deploy on push     │  │
│  │  ├─> Secrets management      │  │
│  │  └─> Public/Private access   │  │
│  └──────────────────────────────┘  │
│  Access: https://app.streamlit.io  │
└────────────────────────────────────┘

OPTION 3: Docker Container
┌────────────────────────────────────┐
│  Docker Container                  │
│  ┌──────────────────────────────┐  │
│  │  Dockerfile                  │  │
│  │  ├─> Python base image       │  │
│  │  ├─> Install requirements    │  │
│  │  ├─> Copy application files  │  │
│  │  └─> Expose port 8501        │  │
│  └──────────────────────────────┘  │
│  Run: docker run -p 8501:8501     │
└────────────────────────────────────┘
```

## Security Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                       SECURITY LAYERS                               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

Layer 1: API Key Security
├─> Stored in .env file (git ignored)
├─> Never committed to repository
├─> Environment variable support
└─> Rotation capability

Layer 2: Data Privacy
├─> Local document processing
├─> No data sent to external servers (except OpenAI API)
├─> Session-based storage (not persistent)
└─> Clear cache on session end

Layer 3: API Communication
├─> HTTPS encryption for OpenAI API calls
├─> Rate limiting support
├─> Usage tracking available
└─> Error handling without data leakage

Layer 4: Input Validation
├─> File type validation
├─> File size limits
├─> Query sanitization
└─> Output formatting validation
```

## Performance Optimization Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│                    PERFORMANCE OPTIMIZATIONS                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

Document Upload
│
├─> Optimization 1: Caching
│   └─> Parse once, reuse multiple times
│       └─> Stored in session_state
│
├─> Optimization 2: Incremental Processing
│   └─> Parse only new/changed documents
│       └─> Skip already cached documents
│
└─> Optimization 3: Lazy Loading
    └─> Parse on demand
        └─> Background processing

Query Processing
│
├─> Optimization 1: Quick Mode Check
│   └─> Check API key availability first
│       └─> Skip LLM overhead if unavailable
│
├─> Optimization 2: Context Limiting
│   └─> Send only first 8000 chars to LLM
│       └─> Reduce token usage and cost
│
└─> Optimization 3: Table Limiting
    └─> Send only first 5 tables to LLM
        └─> Reduce processing time

Response Generation
│
└─> Optimization 1: Page Caching
    └─> Cache page lookups
        └─> Faster subsequent queries
```

---

## Quick Reference

### Key Files
- `smartally.py` - Main application (860 lines)
- `datapoint_mapping.csv` - Configuration
- `.env` - API key (create this, not in git)
- `requirements.txt` - Dependencies

### Key Functions
- `main()` - Streamlit app entry point
- `parse_pdf()` - PDF text extraction
- `parse_user_prompt_with_llm()` - Query parsing (AI)
- `extract_datapoint_with_llm()` - Data extraction (AI)
- `chatbot_response()` - Main coordinator

### Key URLs
- Local: http://localhost:8501
- OpenAI: https://platform.openai.com/api-keys
- GitHub: https://github.com/Tendool/Yitro-Smartally

### Key Commands
```bash
# Install
pip install -r requirements.txt

# Configure
cp .env.example .env
nano .env

# Run
streamlit run smartally.py
```
