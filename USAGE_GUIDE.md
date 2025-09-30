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

3. Run the application:
```bash
streamlit run smartally.py
```

4. Open your browser to `http://localhost:8501`

## Using SmartAlly

### Step 1: Upload Documents

1. Click the "Browse files" button in the left sidebar
2. Select one or more PDF or HTML files containing fund prospectus data
3. Wait for the files to be parsed (you'll see a green success message)

### Step 2: Ask Questions

Type natural language queries in the chat input at the bottom of the page. SmartAlly supports these types of queries:

#### Expenses Queries

**Total Annual Fund Operating Expenses:**
```
Return only the Data Value of TOTAL_ANNUAL_FUND_OPERATING_EXPENSES for Class A
```
Expected output: `1.19%` (with link to page/section)

**Net Expenses:**
```
Return only the Data Value of NET_EXPENSES (after fee waiver/expense reimbursement) for Class F
```
Expected output: `0.75%` (with link to page/section)

#### Investment Minimums

**Initial Investment:**
```
Initial investment for Class C Shares
```
Expected output: `No minimum` or `$2,500` (with link)

**Subsequent Investment (Automatic Investment Plans):**
```
From the Minimum Investment section, extract the value for Automatic Investment Plans under Subsequent investment for Class R
```
Expected output: `$25` (with link)

#### Sales Charges

**CDSC (Contingent Deferred Sales Charge):**
```
CDSC Class C
```
Expected output: `1 year, 1.00% then 0%` (with link)

**Redemption Fees:**
```
Redemption Fee for Class Z
```
Expected output: Fee details or `No redemption fee` (with link)

### Step 3: View Results

Each response includes:
- **The extracted value** (in bold)
- **A hyperlink** to the document location (page number for PDFs, section for HTML)

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

## Extraction Rules

SmartAlly uses rule-based extraction with these output formats:

- **Percentage**: Returns values like "1.19%" or "0.85%"
- **Currency**: Returns dollar amounts like "$100" or "$1,000,000"
- **Text**: Returns raw text like "No minimum" or "No redemption fee"
- **Special**: Returns formatted text for complex data like CDSC schedules

## Tips for Best Results

1. **Use clear, specific queries**: Mention the exact datapoint name and share class
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
