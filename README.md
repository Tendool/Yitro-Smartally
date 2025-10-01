# 🤖 SmartAlly - LLM-Powered Document Data Extractor Chatbot

SmartAlly is a Streamlit-based application that extracts structured data from PDF and HTML documents using OpenAI's GPT-3.5 Turbo for intelligent pattern matching and natural language queries.

## Features

- 📄 **Multi-format Support**: Upload and parse PDF and HTML documents
- 🤖 **Chatbot Interface**: Natural language queries to extract specific data points
- 🧠 **LLM-Based Extraction**: Uses GPT-3.5 Turbo for intelligent data extraction and pattern matching
- 🔄 **Fallback Mode**: Automatic fallback to rule-based extraction when API key is not configured
- 📊 **Table Parsing**: Extracts data from structured tables in PDFs
- 🔗 **Smart Source Linking**: Provides hyperlinks with accurate page numbers to the location of extracted data
- 💾 **Document Caching**: Efficient parsing with cached results

## Tech Stack

- **Python 3.8+**
- **Streamlit**: Web UI framework
- **OpenAI GPT-3.5 Turbo**: LLM for intelligent extraction
- **PyMuPDF (fitz)**: PDF text extraction
- **pdfplumber**: PDF table extraction
- **BeautifulSoup4**: HTML parsing
- **pandas**: Data manipulation
- **python-dotenv**: Environment variable management

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

### LLM Mode (Recommended)
1. User submits a query (e.g., "What is the total annual operating expenses for Class A?")
2. LLM analyzes the query to identify datapoint and class
3. LLM extracts the value from the document text and tables
4. LLM identifies context keywords near the value
5. System matches context to specific page number
6. Result displayed with value, location, and clickable page link

### Fallback Mode (Rule-Based)
1. User submits a query
2. Regex patterns identify datapoint and class
3. Pattern matching extracts value from text
4. Approximate location determined by section keywords
5. Result displayed with value and location

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