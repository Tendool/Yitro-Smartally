# 🤖 SmartAlly - Rule-Based Document Data Extractor Chatbot

SmartAlly is a Streamlit-based application that extracts structured data from PDF and HTML documents using rule-based pattern matching and natural language queries.

## Features

- 📄 **Multi-format Support**: Upload and parse PDF and HTML documents
- 🤖 **Chatbot Interface**: Natural language queries to extract specific data points
- 🎯 **Rule-Based Extraction**: No AI/GPT required - uses regex and pattern matching
- 📊 **Table Parsing**: Extracts data from structured tables in PDFs
- 🔗 **Source Linking**: Provides hyperlinks to the location of extracted data
- 💾 **Document Caching**: Efficient parsing with cached results

## Tech Stack

- **Python 3.8+**
- **Streamlit**: Web UI framework
- **PyMuPDF (fitz)**: PDF text extraction
- **pdfplumber**: PDF table extraction
- **BeautifulSoup4**: HTML parsing
- **pandas**: Data manipulation
- **regex**: Pattern matching

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

## Usage

Run the Streamlit application:
```bash
streamlit run smartally.py
```

The application will open in your default web browser at `http://localhost:8501`.

## How to Use

1. **Upload Documents**: Use the sidebar to upload one or more PDF or HTML files
2. **Ask Questions**: Type natural language queries in the chat input at the bottom
3. **View Results**: The extracted value and its location will be displayed

## Example Queries

- `Return only the Data Value of TOTAL_ANNUAL_FUND_OPERATING_EXPENSES for Class A`
- `Return only the Data Value of NET_EXPENSES (after fee waiver/expense reimbursement) for Class F`
- `From the Minimum Investment section of the PDF, focus only on the Class R block. Extract the value after 'Automatic Investment Plans' under 'Subsequent investment:'`
- `Initial investment for Class C Shares`
- `CDSC Class C`
- `Redemption Fee for Class Z`

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
└── README.md                 # This file
```

## Architecture

### Document Parsing Module
- `parse_pdf()`: Extracts text from PDFs using PyMuPDF
- `parse_pdf_tables()`: Extracts tables using pdfplumber
- `parse_html()`: Extracts text and anchors from HTML

### Extraction Module
- `extract_datapoint()`: Main extraction dispatcher
- `extract_annual_expenses()`: Extracts annual operating expenses
- `extract_net_expenses()`: Extracts net expenses
- `extract_minimum_investment_aip()`: Extracts AIP investment minimums
- `extract_initial_investment()`: Extracts initial investment amounts
- `extract_cdsc()`: Extracts CDSC schedules
- `extract_redemption_fee()`: Extracts redemption fees

### Response Handler
- `parse_user_prompt()`: Parses natural language queries
- `chatbot_response()`: Coordinates extraction and formatting
- `generate_hyperlink()`: Creates links to source locations

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