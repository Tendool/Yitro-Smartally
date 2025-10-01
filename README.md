# 🤖 SmartAlly - LLM-Powered Document Data Extractor Chatbot

SmartAlly is a Streamlit-based application that extracts structured data from PDF and HTML documents using OpenAI's GPT-3.5 Turbo for intelligent pattern matching and natural language queries.

## 📊 Solution Overview

### System Architecture Flowchart

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER INTERACTION LAYER                          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────────┐  │
│  │ Upload Files │ -> │  Ask Query   │ -> │  View Results & Links   │  │
│  │ (PDF/HTML)   │    │  (Natural    │    │  (Values + Page Refs)   │  │
│  │              │    │   Language)  │    │                          │  │
│  └──────────────┘    └──────────────┘    └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                        DOCUMENT PROCESSING LAYER                        │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────────┐  │
│  │ PDF Parser   │    │ Table Parser │    │   HTML Parser            │  │
│  │ (PyMuPDF)    │    │ (pdfplumber) │    │   (BeautifulSoup)        │  │
│  │              │    │              │    │                          │  │
│  │ • Text       │    │ • Tables     │    │ • Text                   │  │
│  │ • Pages      │    │ • Structure  │    │ • Anchors                │  │
│  └──────────────┘    └──────────────┘    └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                      INTELLIGENT EXTRACTION LAYER                       │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    LLM MODE (Recommended)                        │  │
│  │  ┌────────────────┐         ┌────────────────────────────────┐  │  │
│  │  │  Query Parser  │    ->   │   GPT-3.5 Turbo Extraction     │  │  │
│  │  │  (LLM-based)   │         │   • Understands context        │  │  │
│  │  │                │         │   • Extracts values            │  │  │
│  │  │ • Identifies   │         │   • Finds page numbers         │  │  │
│  │  │   datapoint    │         │   • Handles variations         │  │  │
│  │  │ • Recognizes   │         │                                │  │  │
│  │  │   class        │         │                                │  │  │
│  │  └────────────────┘         └────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                  FALLBACK MODE (Rule-Based)                      │  │
│  │  ┌────────────────┐         ┌────────────────────────────────┐  │  │
│  │  │  Regex Parser  │    ->   │   Pattern Matching Extraction  │  │  │
│  │  │                │         │   • Predefined patterns        │  │  │
│  │  │ • Pattern      │         │   • Regex matching             │  │  │
│  │  │   matching     │         │   • Section keywords           │  │  │
│  │  │ • Keywords     │         │                                │  │  │
│  │  └────────────────┘         └────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                        RESPONSE FORMATTING LAYER                        │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────────┐  │
│  │ Value Format │ -> │ Page Lookup  │ -> │  Hyperlink Generator     │  │
│  │ • Currency   │    │ • Context    │    │  • PDF page links        │  │
│  │ • Percentage │    │   matching   │    │  • HTML anchor links     │  │
│  │ • Text       │    │ • Location   │    │                          │  │
│  └──────────────┘    └──────────────┘    └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                         CHAT INTERFACE DISPLAY                          │
│              Shows: Value | Location | Page Number | Link               │
└─────────────────────────────────────────────────────────────────────────┘
```

### Data Flow Diagram

```
User Query: "What is the total annual operating expenses for Class A?"
     │
     ↓
┌────────────────────────────────────────┐
│  1. Parse Query (LLM/Regex)            │
│     → Datapoint: TOTAL_ANNUAL_EXPENSES │
│     → Class: Class A                   │
└────────────────────────────────────────┘
     │
     ↓
┌────────────────────────────────────────┐
│  2. Load Cached Documents              │
│     → PDF text: pages 1-50             │
│     → Tables: 5 tables extracted       │
└────────────────────────────────────────┘
     │
     ↓
┌────────────────────────────────────────┐
│  3. Extract Data (LLM/Pattern)         │
│     → Search text & tables             │
│     → Find: "1.19%" for Class A        │
│     → Context: "Annual Fund Operating" │
└────────────────────────────────────────┘
     │
     ↓
┌────────────────────────────────────────┐
│  4. Locate Page Number                 │
│     → Match context to page 3          │
│     → Section: "Fees and Expenses"     │
└────────────────────────────────────────┘
     │
     ↓
┌────────────────────────────────────────┐
│  5. Format Response                    │
│     → Value: "1.19%"                   │
│     → Location: "Annual Fund Operating"│
│     → Link: 📄 Page 3                  │
└────────────────────────────────────────┘
     │
     ↓
Display in Chat: "The total annual fund operating expenses for Class A is 1.19% 
                  (found in Annual Fund Operating Expenses - 📄 Page 3)"
```

## Features

- 📄 **Multi-format Support**: Upload and parse PDF and HTML documents
- 🤖 **Chatbot Interface**: Natural language queries to extract specific data points
- 🧠 **LLM-Based Extraction**: Uses GPT-3.5 Turbo for intelligent data extraction and pattern matching
- 🔄 **Fallback Mode**: Automatic fallback to rule-based extraction when API key is not configured
- 📊 **Table Parsing**: Extracts data from structured tables in PDFs
- 🔗 **Smart Source Linking**: Provides hyperlinks with accurate page numbers to the location of extracted data
- 💾 **Document Caching**: Efficient parsing with cached results

## Tech Stack

### Technology Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND LAYER                                │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                        Streamlit 1.28.0                          │   │
│  │  • Web UI Framework                                              │   │
│  │  • Chat Interface                                                │   │
│  │  • File Upload                                                   │   │
│  │  • Interactive Controls                                          │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                        AI/ML PROCESSING LAYER                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    OpenAI GPT-3.5 Turbo                          │   │
│  │  • Natural Language Understanding                                │   │
│  │  • Intelligent Data Extraction                                   │   │
│  │  • Context-Aware Processing                                      │   │
│  │  • Query Interpretation                                          │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                      DOCUMENT PROCESSING LAYER                          │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐  │
│  │  PyMuPDF 1.23.5  │  │ pdfplumber 0.10.3│  │ BeautifulSoup4 4.12.2│  │
│  │  • PDF text      │  │ • Table extract  │  │ • HTML parsing       │  │
│  │  • Page extract  │  │ • Structure det. │  │ • Tag navigation     │  │
│  │  • Fast parsing  │  │ • Cell data      │  │ • Content extract    │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                         DATA PROCESSING LAYER                           │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐  │
│  │   Pandas 2.1.1   │  │  Python Regex    │  │  python-dotenv 1.0.0 │  │
│  │  • DataFrames    │  │  • Pattern match │  │  • Env management    │  │
│  │  • CSV handling  │  │  • Text extract  │  │  • API key config    │  │
│  │  • Data mapping  │  │  • Validation    │  │  • Security          │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                         SUPPORT LIBRARIES                               │
│                   lxml 4.9.3  |  openpyxl 3.1.2                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Core Technologies

- **Python 3.8+**: Main programming language
- **Streamlit 1.28.0**: Interactive web application framework for the chat interface
- **OpenAI GPT-3.5 Turbo**: Large Language Model for intelligent data extraction and query understanding
- **PyMuPDF (fitz) 1.23.5**: Fast and reliable PDF text extraction
- **pdfplumber 0.10.3**: Advanced PDF table extraction with structure detection
- **BeautifulSoup4 4.12.2**: HTML/XML parsing and content extraction
- **pandas 2.1.1**: Data manipulation and CSV handling for datapoint mappings
- **python-dotenv 1.0.0**: Environment variable management for secure API key storage

### Why These Technologies?

| Technology | Purpose | Benefits |
|------------|---------|----------|
| **Streamlit** | Web UI Framework | • Rapid development<br>• Built-in chat components<br>• Easy file handling<br>• No frontend coding needed |
| **OpenAI GPT-3.5** | AI Extraction | • Natural language understanding<br>• Context-aware extraction<br>• Flexible pattern matching<br>• High accuracy |
| **PyMuPDF** | PDF Text Extraction | • Fast performance<br>• Accurate text extraction<br>• Page-level organization<br>• Low memory footprint |
| **pdfplumber** | Table Extraction | • Preserves table structure<br>• Cell-level data access<br>• Handles complex layouts<br>• Complementary to PyMuPDF |
| **BeautifulSoup4** | HTML Parsing | • Robust parsing<br>• Easy navigation<br>• Handles malformed HTML<br>• Anchor extraction |
| **pandas** | Data Management | • Efficient data handling<br>• CSV integration<br>• Easy filtering<br>• Built-in data types |

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Tendool/Yitro-Smartally.git
cd Yitro-Smartally
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure OpenAI API Key (required for LLM features):
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your_openai_api_key_here
```

Get your API key from: https://platform.openai.com/api-keys

**Note**: If you don't configure an API key, the application will automatically use rule-based pattern matching as a fallback.

## Usage

### Quick Start

**Linux/Mac:**
```bash
./run.sh
```

**Windows:**
```bash
run.bat
```

Or manually run:
```bash
streamlit run smartally.py
```

The application will open in your default web browser at `http://localhost:8501`.

## How to Use

1. **Upload Documents**: Use the sidebar to upload one or more PDF or HTML files
2. **Configure Extraction Mode**: Toggle between LLM and rule-based extraction (in sidebar settings)
3. **Ask Questions**: Type natural language queries in the chat input at the bottom
4. **View Results**: The extracted value, location, and page number will be displayed with a hyperlink

## Example Queries

With LLM extraction, you can use more natural queries:

- `What is the total annual fund operating expenses for Class A?`
- `Return the net expenses for Class F`
- `Initial investment for Class C Shares`
- `What is the CDSC for Class C?`
- `Redemption Fee for Class Z`
- `Minimum subsequent investment for AIP Class R`

Traditional format also supported:
- `Return only the Data Value of TOTAL_ANNUAL_FUND_OPERATING_EXPENSES for Class A`
- `From the Minimum Investment section, extract the value for Automatic Investment Plans under Subsequent investment for Class R`

## Supported Datapoints

The application supports extracting the following datapoints:

- **TOTAL_ANNUAL_FUND_OPERATING_EXPENSES**: Annual operating expenses by share class
- **NET_EXPENSES**: Net expenses after fee waivers/reimbursements
- **MINIMUM_SUBSEQUENT_INVESTMENT_AIP**: Minimum subsequent investment for Automatic Investment Plans
- **INITIAL_INVESTMENT**: Initial investment amount
- **CDSC**: Contingent Deferred Sales Charge information
- **REDEMPTION_FEE**: Redemption fee details

## Datapoint Mapping

The `datapoint_mapping.csv` file defines the mapping between natural language instructions and extraction rules. You can customize this file to add new datapoints or modify existing ones.

Format:
```csv
Instruction,Datapoint,Class,OutputRule
"Query text",DATAPOINT_NAME,{class},output_format
```

## Output Rules

- **percentage**: Returns values as percentages (e.g., "1.19%")
- **currency**: Returns dollar amounts (e.g., "$1,000")
- **currency_or_text**: Returns currency or text like "No minimum"
- **text**: Returns raw text
- **cdsc_special**: Returns CDSC schedule with years and percentages

## Project Structure

```
Yitro-Smartally/
├── smartally.py              # Main application
├── datapoint_mapping.csv     # Datapoint extraction rules
├── requirements.txt          # Python dependencies
├── .env.example              # Example environment configuration
├── .env                      # Your API keys (create this)
└── README.md                 # This file
```

## Architecture

### Document Parsing Module
- `parse_pdf()`: Extracts text from PDFs using PyMuPDF
- `parse_pdf_tables()`: Extracts tables using pdfplumber
- `parse_html()`: Extracts text and anchors from HTML

### LLM-Based Extraction Module
- `extract_datapoint_with_llm()`: Uses GPT-3.5 Turbo for intelligent extraction
- `parse_user_prompt_with_llm()`: Uses LLM to understand user queries
- Context-aware page number detection

### Legacy Rule-Based Extraction Module (Fallback)
- `extract_datapoint()`: Main extraction dispatcher
- `extract_annual_expenses()`: Extracts annual operating expenses
- `extract_net_expenses()`: Extracts net expenses
- `extract_minimum_investment_aip()`: Extracts AIP investment minimums
- `extract_initial_investment()`: Extracts initial investment amounts
- `extract_cdsc()`: Extracts CDSC schedules
- `extract_redemption_fee()`: Extracts redemption fees

### Response Handler
- `chatbot_response()`: Coordinates extraction and formatting (with LLM/fallback toggle)
- `generate_hyperlink()`: Creates links to source locations

## How It Works

### Complete Workflow

```
┌────────────────────────────────────────────────────────────────────────┐
│                          APPLICATION STARTUP                           │
│  1. Load environment variables (.env file)                             │
│  2. Initialize OpenAI client (if API key present)                      │
│  3. Load datapoint mapping CSV                                         │
│  4. Start Streamlit web server                                         │
└────────────────────────────────────────────────────────────────────────┘
                                 ↓
┌────────────────────────────────────────────────────────────────────────┐
│                         DOCUMENT UPLOAD PHASE                          │
│  User Action: Upload PDF/HTML files via sidebar                        │
│                                                                         │
│  System Actions:                                                       │
│  1. Receive uploaded file(s)                                           │
│  2. Detect file type (PDF or HTML)                                     │
│  3. Parse document:                                                    │
│     • Extract text from each page                                      │
│     • Extract tables with structure                                    │
│     • Create page-to-content mapping                                   │
│  4. Cache parsed data in session state                                 │
│  5. Display success confirmation                                       │
└────────────────────────────────────────────────────────────────────────┘
                                 ↓
┌────────────────────────────────────────────────────────────────────────┐
│                          QUERY PROCESSING PHASE                        │
│  User Action: Type question in chat input                              │
│                                                                         │
│  Example: "What is the total annual operating expenses for Class A?"   │
└────────────────────────────────────────────────────────────────────────┘
                                 ↓
┌────────────────────────────────────────────────────────────────────────┐
│                         EXTRACTION MODE SELECTION                      │
└────────────────────────────────────────────────────────────────────────┘
         ↓                                              ↓
┌────────────────────────────┐          ┌────────────────────────────────┐
│   LLM MODE (Recommended)   │          │   FALLBACK MODE (Rule-Based)   │
│   Requires: OpenAI API Key │          │   Requires: No API Key         │
└────────────────────────────┘          └────────────────────────────────┘
         ↓                                              ↓
┌────────────────────────────┐          ┌────────────────────────────────┐
│ STEP 1: Parse Query (LLM)  │          │ STEP 1: Parse Query (Regex)    │
│ • Send query to GPT-3.5    │          │ • Match against patterns       │
│ • Identify datapoint       │          │ • Extract keywords             │
│ • Extract class name       │          │ • Identify datapoint type      │
│ • Understand intent        │          │ • Find class name              │
│                            │          │                                │
│ Output:                    │          │ Output:                        │
│ • Datapoint: EXPENSES      │          │ • Datapoint: EXPENSES          │
│ • Class: "Class A"         │          │ • Class: "Class A"             │
└────────────────────────────┘          └────────────────────────────────┘
         ↓                                              ↓
┌────────────────────────────┐          ┌────────────────────────────────┐
│ STEP 2: Extract Data (LLM) │          │ STEP 2: Extract Data (Regex)   │
│ • Send document text & tab │          │ • Search text with regex       │
│ • GPT analyzes content     │          │ • Match predefined patterns    │
│ • Finds exact value        │          │ • Extract from tables          │
│ • Identifies context words │          │ • Format according to rule     │
│ • Returns: value + context │          │                                │
│                            │          │ Output:                        │
│ Output:                    │          │ • Value: "1.19%"               │
│ • Value: "1.19%"           │          │ • Section keywords             │
│ • Context: "Annual Fund    │          │                                │
│   Operating Expenses"      │          │                                │
└────────────────────────────┘          └────────────────────────────────┘
         ↓                                              ↓
┌────────────────────────────┐          ┌────────────────────────────────┐
│ STEP 3: Find Page Number   │          │ STEP 3: Find Approximate Page  │
│ • Match context keywords   │          │ • Search for section keywords  │
│   to page content          │          │ • Find first matching page     │
│ • Identify exact page      │          │ • Return page number           │
│ • High accuracy            │          │ • Lower accuracy               │
│                            │          │                                │
│ Output: Page 3             │          │ Output: Page ~3                │
└────────────────────────────┘          └────────────────────────────────┘
         ↓                                              ↓
         └──────────────────────┬────────────────────────┘
                                ↓
┌────────────────────────────────────────────────────────────────────────┐
│                      STEP 4: FORMAT RESPONSE                           │
│  • Apply output formatting rules (currency, percentage, text)          │
│  • Generate hyperlink with page number                                 │
│  • Create user-friendly message                                        │
│                                                                         │
│  Example Output:                                                       │
│  "The total annual fund operating expenses for Class A is 1.19%        │
│   (found in Annual Fund Operating Expenses - 📄 Page 3)"               │
└────────────────────────────────────────────────────────────────────────┘
                                ↓
┌────────────────────────────────────────────────────────────────────────┐
│                      STEP 5: DISPLAY IN CHAT                           │
│  • Add message to chat history                                         │
│  • Render in Streamlit interface                                       │
│  • User can click page link for verification                           │
└────────────────────────────────────────────────────────────────────────┘
```

### LLM Mode (Recommended)

**When to use:** When OpenAI API key is configured (best accuracy and flexibility)

1. **User Query Submission**
   - User types natural language question
   - Example: "What is the total annual operating expenses for Class A?"

2. **LLM Query Analysis**
   - Query sent to GPT-3.5 Turbo
   - LLM identifies:
     - Datapoint: `TOTAL_ANNUAL_FUND_OPERATING_EXPENSES`
     - Class: `Class A`
   - Understands variations and context

3. **LLM Data Extraction**
   - Document text and tables sent to GPT-3.5
   - LLM intelligently:
     - Searches through content
     - Understands table structure
     - Extracts exact value: `1.19%`
     - Identifies context: "Annual Fund Operating Expenses"

4. **Context-Aware Page Location**
   - System matches context keywords to page content
   - Finds exact page number where value appears
   - High accuracy page detection

5. **Result Display**
   - Formatted response with value, location, and clickable page link
   - User can verify by clicking the link

**Benefits:**
- ✅ Natural language queries
- ✅ Handles document variations
- ✅ High accuracy
- ✅ Context understanding
- ✅ Flexible extraction

### Fallback Mode (Rule-Based)

**When to use:** When OpenAI API key is not configured (automatic fallback)

1. **User Query Submission**
   - User types query
   - Can use structured format or natural language

2. **Pattern-Based Query Parsing**
   - Regex patterns match against query
   - Extracts datapoint name and class
   - Uses predefined keyword matching

3. **Rule-Based Data Extraction**
   - Searches text using regex patterns
   - Matches against known structures
   - Extracts from tables using position
   - Applies formatting rules

4. **Approximate Page Location**
   - Searches for section keywords
   - Finds page with matching content
   - Less accurate than LLM mode

5. **Result Display**
   - Formatted response with value and location
   - Approximate page number if found

**Benefits:**
- ✅ No API key required
- ✅ Fast execution
- ✅ Works offline
- ✅ Predictable behavior
- ⚠️ Less flexible than LLM mode

### Comparison Table

| Feature | LLM Mode | Fallback Mode |
|---------|----------|---------------|
| **API Key Required** | ✅ Yes | ❌ No |
| **Natural Language** | ✅ Full support | ⚠️ Limited |
| **Accuracy** | ⭐⭐⭐⭐⭐ High | ⭐⭐⭐ Medium |
| **Page Detection** | ⭐⭐⭐⭐⭐ Precise | ⭐⭐⭐ Approximate |
| **Handle Variations** | ✅ Yes | ⚠️ Limited |
| **Speed** | ⚠️ 2-5 seconds | ✅ < 1 second |
| **Cost** | 💰 API usage | ✅ Free |
| **Offline Mode** | ❌ No | ✅ Yes |

## Development

### Adding New Datapoints

1. Add a new row to `datapoint_mapping.csv`
2. Implement an extraction function in `smartally.py`
3. Add the function to the dispatcher in `extract_datapoint()`

### Testing

Upload sample PDF or HTML files containing fund prospectus data and test various queries to ensure accurate extraction.

## License

This project is provided as-is for educational and development purposes.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.