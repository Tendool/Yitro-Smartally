# SmartAlly Usage Guide

## Getting Started

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Tendool/Yitro-Smartally.git
cd Yitro-Smartally
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure OpenAI API Key (for LLM features):
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=your_openai_api_key_here
```

Get your API key from: https://platform.openai.com/api-keys

**Note**: Without an API key, the app will use rule-based extraction as fallback.

4. Run the application:
```bash
streamlit run smartally.py
```

5. Open your browser to `http://localhost:8501`

## Using SmartAlly

### Step 1: Upload Documents

1. Click the "Browse files" button in the left sidebar
2. Select one or more PDF or HTML files containing fund prospectus data
3. Wait for the files to be parsed (you'll see a green success message)

### Step 2: Configure Extraction Mode

In the sidebar settings:
- **LLM Extraction**: Toggle on for intelligent GPT-3.5 Turbo extraction (requires API key)
- **Rule-Based**: Automatically used as fallback when API key not configured

### Step 3: Ask Questions

Type natural language queries in the chat input at the bottom of the page. With LLM mode, you can use more natural language:

#### Expenses Queries

**Total Annual Fund Operating Expenses (Natural Language):**
```
What is the total annual fund operating expenses for Class A?
```
Expected output: `1.19%` (with link to page/section)

**Traditional Format:**
```
Return only the Data Value of TOTAL_ANNUAL_FUND_OPERATING_EXPENSES for Class A
```
Expected output: `1.19%` (with link to page/section)

**Net Expenses:**
```
Return the net expenses for Class F
```
Expected output: `0.75%` (with link to page/section)

#### Investment Minimums

**Initial Investment (Natural Language):**
```
What is the initial investment for Class C?
```
Expected output: `No minimum` or `$2,500` (with link)

**Traditional Format:**
```
Initial investment for Class C Shares
```
Expected output: `No minimum` or `$2,500` (with link)

**Subsequent Investment (Automatic Investment Plans):**
```
Minimum subsequent investment for AIP Class R
```
Expected output: `$25` (with link)

#### Sales Charges

**CDSC (Contingent Deferred Sales Charge):**
```
What is the CDSC for Class C?
```
Expected output: `1 year, 1.00% then 0%` (with link)

**Redemption Fees:**
```
Redemption Fee for Class Z
```
Expected output: Fee details or `No redemption fee` (with link)

### Step 4: View Results

Each response includes:
- **The extracted value** (in bold)
- **A hyperlink** to the document location (page number for PDFs, section for HTML)
- **Accurate page numbers** when LLM mode is enabled (using context matching)

## Supported Share Classes

SmartAlly recognizes various share class formats:
- Class A, Class B, Class C, Class F, Class I, Class R, Class Z
- Alternative formats: "A Shares", "Class A Shares", etc.

## Document Format Requirements

### PDF Documents

PDFs should contain:
- Clear section headers (e.g., "Fees and Expenses", "Minimum Investment")
- Tables with class columns
- Structured text for easy parsing

### HTML Documents

HTML files should contain:
- Semantic markup with proper headings (`<h1>`, `<h2>`, etc.)
- Tables for tabular data
- Optional: Element IDs for better hyperlink accuracy

## Extraction Modes

### LLM Mode (Recommended)

SmartAlly uses OpenAI GPT-3.5 Turbo to:
- Understand natural language queries
- Extract data intelligently from unstructured text
- Identify context for accurate page number detection
- Handle variations in document formatting

Benefits:
- More flexible query understanding
- Better handling of complex document structures
- Accurate page number detection
- Can understand context and relationships

### Rule-Based Mode (Fallback)

Uses pattern matching with these output formats:
- **Percentage**: Returns values like "1.19%" or "0.85%"
- **Currency**: Returns dollar amounts like "$100" or "$1,000,000"
- **Text**: Returns raw text like "No minimum" or "No redemption fee"
- **Special**: Returns formatted text for complex data like CDSC schedules

## Tips for Best Results

1. **Use clear, specific queries**: With LLM mode, you can use natural language
2. **Upload relevant documents**: Ensure documents contain the data you're looking for
3. **Check multiple classes**: If you need data for multiple classes, ask separate queries
4. **Review hyperlinks**: Click the provided links to verify the source location

## Troubleshooting

### "Could not identify the datapoint"
- Make sure your query matches one of the supported datapoint types
- Be specific about which data you want (e.g., "Total Annual Fund Operating Expenses")

### "Could not identify the share class"
- Always specify the class (e.g., "Class A", "Class I")
- Use standard class naming conventions

### "Value not found" or Returns "0"
- Check that the uploaded document contains the requested data
- Verify the document format is clear and structured
- Try rephrasing your query

### Parsing takes too long
- Large PDFs may take a few seconds to parse
- The app caches parsed documents, so subsequent queries are faster

## Advanced: Customizing Datapoint Mappings

You can add new datapoints by editing `datapoint_mapping.csv`:

```csv
Instruction,Datapoint,Class,OutputRule
"Your instruction text with {class}",DATAPOINT_NAME,{class},output_format
```

Then implement the extraction logic in `smartally.py` by:
1. Adding a new extraction function
2. Adding it to the `extract_datapoint()` dispatcher

## Examples Gallery

### Example 1: Comparing Expenses Across Classes
```
Query 1: Return only the Data Value of TOTAL_ANNUAL_FUND_OPERATING_EXPENSES for Class A
Result: 1.19%

Query 2: Return only the Data Value of TOTAL_ANNUAL_FUND_OPERATING_EXPENSES for Class I
Result: 0.92%

Query 3: Return only the Data Value of TOTAL_ANNUAL_FUND_OPERATING_EXPENSES for Class C
Result: 1.94%
```

### Example 2: Investment Requirements
```
Query 1: Initial investment for Class A Shares
Result: $2,500

Query 2: Initial investment for Class C Shares
Result: No minimum

Query 3: From the Minimum Investment section, extract the value for Automatic Investment Plans under Subsequent investment for Class A
Result: $50
```

### Example 3: Sales Charges
```
Query 1: CDSC Class C
Result: 1 year, 1.00% then 0%

Query 2: Redemption Fee for Class Z
Result: 2% redemption fee on shares held less than 60 days
```

## Support

For issues, questions, or feature requests, please open an issue on the GitHub repository.
