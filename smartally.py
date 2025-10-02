"""
SmartAlly - LLM-Based Document Data Extractor Chatbot
A Streamlit application for extracting structured data from PDF and HTML documents
using OpenAI GPT-3.5 Turbo for intelligent pattern matching.
"""

import streamlit as st
import fitz  # PyMuPDF
import pdfplumber
from bs4 import BeautifulSoup
import pandas as pd
import re
from typing import Dict, List, Tuple, Optional, Any
import io
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client (only if API key is available)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")

if OPENAI_API_KEY:
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
else:
    client = None


# ============================================================================
# Document Parsing Functions
# ============================================================================

def parse_pdf(file) -> Dict[int, str]:
    """
    Extract raw text from PDF file, organized by page number.
    
    Args:
        file: Uploaded PDF file object
        
    Returns:
        Dictionary mapping page number to text content
    """
    pages_text = {}
    
    try:
        # Use PyMuPDF for text extraction
        pdf_bytes = file.read()
        file.seek(0)  # Reset file pointer
        
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            pages_text[page_num + 1] = text  # 1-indexed pages
        doc.close()
        
    except Exception as e:
        st.error(f"Error parsing PDF with PyMuPDF: {e}")
        
    return pages_text


def parse_pdf_tables(file) -> Dict[int, List[List[str]]]:
    """
    Extract tables from PDF using pdfplumber.
    
    Args:
        file: Uploaded PDF file object
        
    Returns:
        Dictionary mapping page number to list of tables
    """
    tables_by_page = {}
    
    try:
        pdf = pdfplumber.open(file)
        for page_num, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables()
            if tables:
                tables_by_page[page_num] = tables
        pdf.close()
        
    except Exception as e:
        st.error(f"Error extracting tables from PDF: {e}")
        
    return tables_by_page


def parse_html(file) -> Tuple[str, Dict[str, str]]:
    """
    Extract raw text and anchor points from HTML file.
    
    Args:
        file: Uploaded HTML file object
        
    Returns:
        Tuple of (full text, dictionary mapping element IDs to text content)
    """
    try:
        html_content = file.read()
        if isinstance(html_content, bytes):
            html_content = html_content.decode('utf-8')
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract full text
        full_text = soup.get_text(separator=' ', strip=True)
        
        # Extract anchors (elements with IDs)
        anchors = {}
        for element in soup.find_all(id=True):
            element_id = element.get('id')
            element_text = element.get_text(strip=True)
            anchors[element_id] = element_text
            
        return full_text, anchors
        
    except Exception as e:
        st.error(f"Error parsing HTML: {e}")
        return "", {}


# ============================================================================
# LLM-Based Data Extraction Functions
# ============================================================================

def extract_datapoint_with_llm(text: str, tables: List[List[str]], datapoint_name: str, 
                               class_name: str, output_rule: str, 
                               page_texts: Optional[Dict[int, str]] = None) -> Tuple[Optional[str], Optional[str], Optional[int]]:
    """
    Extract a specific datapoint from text using LLM (GPT-3.5 Turbo).
    
    Args:
        text: Raw text to search
        tables: List of tables from the document
        datapoint_name: Name of the datapoint to extract
        class_name: Share class (e.g., "Class A", "Class I")
        output_rule: Formatting rule for output
        page_texts: Optional dictionary of page texts for better location tracking
        
    Returns:
        Tuple of (extracted value, location description, page number)
    """
    
    if not client:
        return "0", None, None
    
    # Format tables as text for the LLM
    tables_text = ""
    if tables:
        tables_text = "\n\nTABLES IN DOCUMENT:\n"
        for i, table in enumerate(tables[:5], 1):  # Limit to first 5 tables
            tables_text += f"\nTable {i}:\n"
            for row in table[:10]:  # Limit rows per table
                tables_text += "| " + " | ".join([str(cell) for cell in row]) + " |\n"
    
    # Create a comprehensive prompt for the LLM
    prompt = f"""You are a financial document data extraction assistant. Your task is to extract specific data points from fund prospectus documents.

TASK: Extract the {datapoint_name} for {class_name}.

DOCUMENT TEXT:
{text[:8000]}  

{tables_text}

INSTRUCTIONS:
1. Find the {datapoint_name} value for {class_name} in the document
2. Return ONLY the value in the format specified by the output rule: {output_rule}
3. Also identify the specific location/section where this value was found
4. Include relevant context words or phrases that appear near the value

OUTPUT FORMAT (respond in exactly this JSON format):
{{
    "value": "the extracted value (or '0' if not found)",
    "location": "specific section/context where found",
    "context": "2-3 words or phrases that appear near the value in the document"
}}

DATAPOINT DESCRIPTIONS:
- TOTAL_ANNUAL_FUND_OPERATING_EXPENSES: The total annual operating expenses percentage
- NET_EXPENSES: Net expenses after fee waivers/reimbursements
- MINIMUM_SUBSEQUENT_INVESTMENT_AIP: Minimum subsequent investment for Automatic Investment Plans
- INITIAL_INVESTMENT: Initial investment amount required
- CDSC: Contingent Deferred Sales Charge information
- REDEMPTION_FEE: Redemption fee details

OUTPUT RULES:
- percentage: Return as "X.XX%" (e.g., "1.19%")
- currency: Return as "$X" or "$X,XXX" (e.g., "$50", "$2,500")
- currency_or_text: Return dollar amount or text like "No minimum"
- text: Return as descriptive text
- cdsc_special: Return in format "X year, Y% then Z%"

Remember: Return "0" if the value is not found. Be precise and extract only the requested information."""

    try:
        # Call OpenAI API
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a precise financial data extraction assistant. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # Low temperature for consistent extraction
            max_tokens=500
        )
        
        # Parse response
        response_text = response.choices[0].message.content.strip()
        
        # Extract JSON from response (handle markdown code blocks)
        import json
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(response_text)
        
        value = result.get("value", "0")
        location = result.get("location", "document")
        context = result.get("context", "")
        
        # Find page number based on context
        page_num = None
        if page_texts and context:
            context_words = context.lower().split()
            for pnum, ptext in page_texts.items():
                ptext_lower = ptext.lower()
                # Check if multiple context words appear on this page
                matches = sum(1 for word in context_words if word in ptext_lower)
                if matches >= 2:  # At least 2 context words must match
                    page_num = pnum
                    break
        
        return value, location, page_num
        
    except Exception as e:
        st.error(f"LLM extraction error: {str(e)}")
        return "0", None, None


def parse_user_prompt_with_llm(prompt: str, mapping_df: pd.DataFrame) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse user prompt using LLM to identify datapoint and class.
    
    Args:
        prompt: User's natural language prompt
        mapping_df: DataFrame with datapoint mappings
        
    Returns:
        Tuple of (datapoint_name, class_name)
    """
    
    if not client:
        return parse_user_prompt_fallback(prompt, mapping_df)
    
    # Get list of available datapoints
    available_datapoints = mapping_df['Datapoint'].unique().tolist()
    
    llm_prompt = f"""You are a financial document query parser. Analyze the user's question and identify:
1. Which datapoint they are asking about
2. Which share class they are interested in

USER QUERY: {prompt}

AVAILABLE DATAPOINTS:
{', '.join(available_datapoints)}

COMMON SHARE CLASSES:
Class A, Class B, Class C, Class F, Class I, Class R, Class Z

OUTPUT FORMAT (respond in exactly this JSON format):
{{
    "datapoint": "the exact datapoint name from the available list (or null if unclear)",
    "class": "the share class in format 'Class X' (or null if not specified)"
}}

Example responses:
- For "What is the total annual fund operating expenses for Class A?": {{"datapoint": "TOTAL_ANNUAL_FUND_OPERATING_EXPENSES", "class": "Class A"}}
- For "Initial investment Class C": {{"datapoint": "INITIAL_INVESTMENT", "class": "Class C"}}
- For "CDSC Class I": {{"datapoint": "CDSC", "class": "Class I"}}
"""

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a query parsing assistant. Always respond with valid JSON."},
                {"role": "user", "content": llm_prompt}
            ],
            temperature=0.1,
            max_tokens=200
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Extract JSON
        import json
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(response_text)
        
        datapoint = result.get("datapoint")
        class_name = result.get("class")
        
        return datapoint, class_name
        
    except Exception as e:
        st.error(f"Prompt parsing error: {str(e)}")
        # Fallback to simple pattern matching
        return parse_user_prompt_fallback(prompt, mapping_df)


def parse_user_prompt_fallback(prompt: str, mapping_df: pd.DataFrame) -> Tuple[Optional[str], Optional[str]]:
    """
    Fallback parser using rule-based matching when LLM fails.
    """
    prompt_lower = prompt.lower()
    
    # Extract class name
    class_name = None
    class_patterns = [
        r'class\s+([a-z])\b',
        r'class\s+([a-z])\s+shares',
        r'for\s+class\s+([a-z])',
        r'\(class\s+([a-z])\)'
    ]
    
    for pattern in class_patterns:
        match = re.search(pattern, prompt_lower)
        if match:
            class_name = f"Class {match.group(1).upper()}"
            break
    
    # Match against instruction patterns
    for _, row in mapping_df.iterrows():
        instruction_pattern = row['Instruction'].lower().replace('{class}', '.*?')
        if re.search(instruction_pattern, prompt_lower, re.IGNORECASE):
            return row['Datapoint'], class_name or row['Class']
    
    # Fallback: keyword matching
    if 'total annual fund operating expenses' in prompt_lower or 'total_annual_fund_operating_expenses' in prompt_lower:
        return 'TOTAL_ANNUAL_FUND_OPERATING_EXPENSES', class_name
    elif 'net expenses' in prompt_lower or 'net_expenses' in prompt_lower:
        return 'NET_EXPENSES', class_name
    elif 'automatic investment plan' in prompt_lower and 'subsequent' in prompt_lower:
        return 'MINIMUM_SUBSEQUENT_INVESTMENT_AIP', class_name
    elif 'initial investment' in prompt_lower:
        return 'INITIAL_INVESTMENT', class_name
    elif 'cdsc' in prompt_lower:
        return 'CDSC', class_name
    elif 'redemption fee' in prompt_lower:
        return 'REDEMPTION_FEE', class_name
    
    return None, class_name


# ============================================================================
# Legacy Rule-Based Data Extraction Functions (Kept as Fallback)
# ============================================================================

def extract_datapoint(text: str, tables: List[List[str]], datapoint_name: str, 
                      class_name: str, output_rule: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract a specific datapoint from text using rule-based pattern matching.
    
    Args:
        text: Raw text to search
        tables: List of tables from the document
        datapoint_name: Name of the datapoint to extract
        class_name: Share class (e.g., "Class A", "Class I")
        output_rule: Formatting rule for output
        
    Returns:
        Tuple of (extracted value, location description)
    """
    
    # Normalize class name variations
    class_variations = [
        class_name,
        class_name.replace("Class ", ""),
        f"Class {class_name.replace('Class ', '')}",
        f"Shares {class_name.replace('Class ', '')}",
        f"{class_name.replace('Class ', '')} Shares"
    ]
    
    if datapoint_name == "TOTAL_ANNUAL_FUND_OPERATING_EXPENSES":
        return extract_annual_expenses(text, tables, class_variations, output_rule)
    
    elif datapoint_name == "NET_EXPENSES":
        return extract_net_expenses(text, tables, class_variations, output_rule)
    
    elif datapoint_name == "MINIMUM_SUBSEQUENT_INVESTMENT_AIP":
        return extract_minimum_investment_aip(text, class_variations, output_rule)
    
    elif datapoint_name == "INITIAL_INVESTMENT":
        return extract_initial_investment(text, class_variations, output_rule)
    
    elif datapoint_name == "CDSC":
        return extract_cdsc(text, tables, class_variations, output_rule)
    
    elif datapoint_name == "REDEMPTION_FEE":
        return extract_redemption_fee(text, class_variations, output_rule)
    
    return "0", None


def extract_annual_expenses(text: str, tables: List[List[str]], 
                           class_variations: List[str], output_rule: str) -> Tuple[str, Optional[str]]:
    """Extract total annual fund operating expenses."""
    
    # Search in tables first
    for table in tables:
        # Find header row with class names
        header_row = None
        class_col_idx = None
        
        for row_idx, row in enumerate(table):
            if row:
                # Check if this row has class names
                for col_idx, cell in enumerate(row):
                    cell_str = str(cell).strip()
                    for class_var in class_variations:
                        if class_var.lower() == cell_str.lower() or \
                           class_var.replace('Class ', '').lower() == cell_str.lower():
                            header_row = row_idx
                            class_col_idx = col_idx
                            break
                    if class_col_idx is not None:
                        break
        
        # Now find the Total Annual Fund Operating Expenses row
        if header_row is not None and class_col_idx is not None:
            for row_idx in range(header_row, len(table)):
                row = table[row_idx]
                if row and len(row) > 0:
                    first_cell = str(row[0]).lower()
                    if "total annual fund operating" in first_cell:
                        if class_col_idx < len(row):
                            value = str(row[class_col_idx]).strip()
                            match = re.search(r'(\d+\.?\d*)%', value)
                            if match:
                                return f"{match.group(1)}%", "expenses table"
    
    # Search in text - look for the specific line with Total Annual
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if 'total annual fund operating' in line.lower() and 'expenses' in line.lower():
            # Found the row, now look for class and value in nearby lines
            for class_var in class_variations:
                # Search in current line and next few lines
                search_text = '\n'.join(lines[max(0, i-2):min(len(lines), i+3)])
                pattern = rf"{re.escape(class_var)}.*?(\d+\.?\d+)%"
                match = re.search(pattern, search_text, re.IGNORECASE)
                if match:
                    return f"{match.group(1)}%", "expenses section"
    
    return "0", None


def extract_net_expenses(text: str, tables: List[List[str]], 
                        class_variations: List[str], output_rule: str) -> Tuple[str, Optional[str]]:
    """Extract net expenses after fee waiver/expense reimbursement."""
    
    # Search in tables
    for table in tables:
        # Find header row with class names
        header_row = None
        class_col_idx = None
        
        for row_idx, row in enumerate(table):
            if row:
                for col_idx, cell in enumerate(row):
                    cell_str = str(cell).strip()
                    for class_var in class_variations:
                        if class_var.lower() == cell_str.lower() or \
                           class_var.replace('Class ', '').lower() == cell_str.lower():
                            header_row = row_idx
                            class_col_idx = col_idx
                            break
                    if class_col_idx is not None:
                        break
        
        # Find Net Expenses row
        if header_row is not None and class_col_idx is not None:
            for row_idx in range(header_row, len(table)):
                row = table[row_idx]
                if row and len(row) > 0:
                    first_cell = str(row[0]).lower()
                    if "net expense" in first_cell or "net annual" in first_cell:
                        if class_col_idx < len(row):
                            value = str(row[class_col_idx]).strip()
                            match = re.search(r'(\d+\.?\d*)%', value)
                            if match:
                                return f"{match.group(1)}%", "net expenses table"
    
    # Search in text
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if ('net expense' in line.lower() or 'after fee waiver' in line.lower()) and 'expense' in line.lower():
            for class_var in class_variations:
                search_text = '\n'.join(lines[max(0, i-2):min(len(lines), i+3)])
                pattern = rf"{re.escape(class_var)}.*?(\d+\.?\d+)%"
                match = re.search(pattern, search_text, re.IGNORECASE)
                if match:
                    return f"{match.group(1)}%", "net expenses section"
    
    return "0", None


def extract_minimum_investment_aip(text: str, class_variations: List[str], 
                                   output_rule: str) -> Tuple[str, Optional[str]]:
    """Extract minimum subsequent investment for Automatic Investment Plans."""
    
    # Look for Minimum Investment section with AIP
    for class_var in class_variations:
        # Pattern: Class block -> Subsequent investment -> AIP value
        pattern = rf"{re.escape(class_var)}.*?(?:subsequent\s+investment|subsequent).*?(?:automatic\s+investment\s+plans?|aip).*?\$\s*([\d,]+)"
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            amount = match.group(1).replace(',', '')
            return f"${amount}", "minimum investment section"
    
    # Try alternate pattern
    pattern = r"(?:automatic\s+investment\s+plans?|aip).*?(?:subsequent\s+investment|subsequent).*?\$\s*([\d,]+)"
    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        amount = match.group(1).replace(',', '')
        return f"${amount}", "minimum investment section"
    
    return "0", None


def extract_initial_investment(text: str, class_variations: List[str], 
                               output_rule: str) -> Tuple[str, Optional[str]]:
    """Extract initial investment amount."""
    
    for class_var in class_variations:
        # Create a class section pattern - look for the class heading
        class_section_pattern = rf"{re.escape(class_var)}\s+(?:Shares?)?\s*\n(.*?)(?=\n\s*Class\s+[A-Z]|\Z)"
        class_match = re.search(class_section_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if class_match:
            class_section = class_match.group(1)
            
            # Look for "initial investment" in this section
            init_pattern = r"Initial\s+Investment:\s*(.*?)(?=\n|$)"
            init_match = re.search(init_pattern, class_section, re.IGNORECASE)
            
            if init_match:
                value = init_match.group(1).strip()
                if 'no minimum' in value.lower():
                    return "No minimum", "minimum investment section"
                # Extract dollar amount
                dollar_match = re.search(r'\$\s*([\d,]+)', value)
                if dollar_match:
                    amount = dollar_match.group(1).replace(',', '')
                    return f"${amount}", "minimum investment section"
    
    # Fallback: direct pattern matching
    for class_var in class_variations:
        # Look for "no minimum" first
        pattern = rf"{re.escape(class_var)}.*?(?:initial\s+investment).*?(no\s+minimum)"
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            return "No minimum", "minimum investment section"
        
        # Look for dollar amount
        pattern = rf"{re.escape(class_var)}.*?(?:initial\s+investment).*?\$\s*([\d,]+)"
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            amount = match.group(1).replace(',', '')
            return f"${amount}", "minimum investment section"
    
    return "0", None


def extract_cdsc(text: str, tables: List[List[str]], class_variations: List[str], 
                output_rule: str) -> Tuple[str, Optional[str]]:
    """Extract CDSC (Contingent Deferred Sales Charge) information."""
    
    # CDSC typically shows years and percentages
    for class_var in class_variations:
        # Look for CDSC section with years and percentages
        pattern = rf"(?:cdsc|contingent\s+deferred\s+sales\s+charge).*?{re.escape(class_var)}.*?(\d+)\s*year.*?(\d+\.?\d*)%.*?(\d+\.?\d*)%"
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            years = match.group(1)
            first_pct = match.group(2)
            after_pct = match.group(3)
            return f"{years} year, {first_pct}% then {after_pct}%", "CDSC section"
        
        # Simpler pattern for "1 year" and "0% after first year"
        pattern = rf"(?:cdsc|contingent\s+deferred\s+sales\s+charge).*?{re.escape(class_var)}.*?(\d+)\s*(?:year|yr)"
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            years = match.group(1)
            # Look for "0% after" nearby
            after_pattern = r"(\d+\.?\d*)%\s+after"
            after_match = re.search(after_pattern, text[match.end():match.end()+100], re.IGNORECASE)
            if after_match:
                return f"{years} year, {after_match.group(1)}% after first year", "CDSC section"
            return f"{years} year", "CDSC section"
    
    return "0", None


def extract_redemption_fee(text: str, class_variations: List[str], 
                          output_rule: str) -> Tuple[str, Optional[str]]:
    """Extract redemption fee information."""
    
    for class_var in class_variations:
        # Look for class-specific redemption fee
        pattern = rf"{re.escape(class_var)}:\s*(.*?)(?:redemption\s+fee|$)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            fee_text = match.group(1).strip()
            # Extract percentage or "No" fee
            if re.search(r'\d+\.?\d*%', fee_text):
                pct_match = re.search(r'(\d+\.?\d*)%', fee_text)
                if pct_match:
                    # Get more context - look for full sentence
                    context_pattern = rf"{re.escape(class_var)}:\s*(.*?)(?=\n\s*Class\s+[A-Z]|\n\s*$)"
                    context_match = re.search(context_pattern, text, re.IGNORECASE)
                    if context_match:
                        return context_match.group(1).strip(), "redemption fee section"
                    return fee_text, "redemption fee section"
            elif 'no' in fee_text.lower():
                return "No redemption fee", "redemption fee section"
        
        # Alternative pattern
        pattern = rf"{re.escape(class_var)}.*?redemption\s+fee[:\s]+(.*?)(?=\n|$)"
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            fee_info = match.group(1).strip()
            if fee_info:
                return fee_info, "redemption fee section"
        
        # Try reverse: redemption fee first
        pattern = rf"redemption\s+fee.*?{re.escape(class_var)}[:\s]+(.*?)(?=\n|$)"
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            fee_info = match.group(1).strip()
            if fee_info:
                return fee_info, "redemption fee section"
    
    return "0", None


# ============================================================================
# Hyperlink Generation
# ============================================================================

def generate_hyperlink(doc_type: str, location: Optional[str], 
                       page_num: Optional[int] = None, element_id: Optional[str] = None,
                       doc_name: Optional[str] = None) -> str:
    """
    Generate a hyperlink to the location in the document.
    
    Args:
        doc_type: Type of document ("pdf" or "html")
        location: Description of where the value was found
        page_num: Page number (for PDFs)
        element_id: Element ID (for HTML)
        doc_name: Name of the document file
        
    Returns:
        Hyperlink string with enhanced formatting
    """
    if doc_type == "pdf" and page_num:
        doc_ref = f" in `{doc_name}`" if doc_name else ""
        return f"📄 **Page {page_num}**{doc_ref} - {location if location else 'See document for details'}"
    elif doc_type == "html" and element_id:
        doc_ref = f" in `{doc_name}`" if doc_name else ""
        return f"🔗 **Section #{element_id}**{doc_ref} - {location if location else 'See document for details'}"
    elif location:
        doc_ref = f" (`{doc_name}`)" if doc_name else ""
        return f"📍 **Source:** {location}{doc_ref}"
    else:
        doc_ref = f" in `{doc_name}`" if doc_name else ""
        return f"📍 **Location:** Document reference{doc_ref}"


# ============================================================================
# Chatbot Response Handler
# ============================================================================

def chatbot_response(user_prompt: str, parsed_docs: Dict[str, Any], 
                    mapping_df: pd.DataFrame, use_llm: bool = True) -> str:
    """
    Process user prompt and return extracted data with hyperlink.
    
    Args:
        user_prompt: User's natural language query
        parsed_docs: Dictionary containing parsed document data
        mapping_df: DataFrame with datapoint mappings
        use_llm: Whether to use LLM-based extraction (default: True)
        
    Returns:
        Formatted response string
    """
    # Check if API key is configured
    if use_llm and not os.getenv("OPENAI_API_KEY"):
        st.warning("⚠️ OpenAI API key not found. Falling back to rule-based extraction. Please set OPENAI_API_KEY in .env file.")
        use_llm = False
    
    # Parse the prompt
    if use_llm:
        datapoint_name, class_name = parse_user_prompt_with_llm(user_prompt, mapping_df)
    else:
        datapoint_name, class_name = parse_user_prompt_fallback(user_prompt, mapping_df)
    
    if not datapoint_name:
        return """
---
### ❌ Unable to Identify Datapoint

I couldn't determine what data you're looking for from your query.

**Please try:**
- Being more specific about what you want to extract
- Using terminology from fund prospectuses (e.g., "operating expenses", "net expenses")
- Checking the example queries in the sidebar

---
"""
    
    if not class_name:
        return """
---
### ❌ Share Class Not Specified

I couldn't identify which share class you're asking about.

**Please specify one of:**
- Class A, Class B, Class C
- Class F, Class I, Class R, Class Z
- Example: "What is the operating expense for **Class A**?"

---
"""
    
    # Get output rule
    output_rule = mapping_df[mapping_df['Datapoint'] == datapoint_name]['OutputRule'].iloc[0] if not mapping_df[mapping_df['Datapoint'] == datapoint_name].empty else 'text'
    
    # Extract from all documents
    results = []
    for doc_name, doc_data in parsed_docs.items():
        if doc_data['type'] == 'pdf':
            # Combine all pages
            all_text = '\n'.join(doc_data['pages'].values())
            tables = []
            for page_tables in doc_data.get('tables', {}).values():
                tables.extend(page_tables)
            
            if use_llm:
                # Use LLM-based extraction with page tracking
                value, location, page_num = extract_datapoint_with_llm(
                    all_text, tables, datapoint_name, class_name, output_rule, 
                    doc_data['pages']
                )
            else:
                # Use legacy rule-based extraction
                value, location = extract_datapoint(all_text, tables, datapoint_name, class_name, output_rule)
                # Find which page it was on (approximate)
                page_num = None
                for pnum, ptext in doc_data['pages'].items():
                    if location and any(keyword in ptext.lower() for keyword in location.split()):
                        page_num = pnum
                        break
            
            if value and value != "0":
                hyperlink = generate_hyperlink('pdf', location, page_num, doc_name=doc_name)
                results.append(f"### 💼 {value}\n{hyperlink}")
        
        elif doc_data['type'] == 'html':
            all_text = doc_data['text']
            
            if use_llm:
                # Use LLM-based extraction
                value, location, _ = extract_datapoint_with_llm(
                    all_text, [], datapoint_name, class_name, output_rule
                )
            else:
                # Use legacy rule-based extraction
                value, location = extract_datapoint(all_text, [], datapoint_name, class_name, output_rule)
            
            if value and value != "0":
                hyperlink = generate_hyperlink('html', location, doc_name=doc_name)
                results.append(f"### 💼 {value}\n{hyperlink}")
    
    if results:
        # Format results with better presentation
        response = "---\n\n" + "\n\n---\n\n".join(results) + "\n\n---"
        return response
    else:
        return """
---
### ⚠️ No Data Found

The requested datapoint was not found in the uploaded documents.

**Suggestions:**
- Verify the document contains the requested information
- Try rephrasing your query
- Ensure the correct share class is specified
- Check if the document is properly formatted

---
"""


# ============================================================================
# Streamlit UI
# ============================================================================

def main():
    """Main Streamlit application."""
    
    st.set_page_config(
        page_title="SmartAlly - AI Document Data Extractor",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for professional styling
    st.markdown("""
        <style>
        /* Main container styling */
        .main {
            padding: 2rem;
        }
        
        /* Title and header styling */
        h1 {
            color: #1E3A8A;
            font-size: 2.5rem !important;
            font-weight: 700 !important;
            margin-bottom: 0.5rem !important;
        }
        
        /* Subtitle styling */
        .subtitle {
            color: #64748B;
            font-size: 1.1rem;
            margin-bottom: 2rem;
            line-height: 1.6;
        }
        
        /* Chat messages */
        .stChatMessage {
            border-radius: 12px;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #F8FAFC;
            padding: 2rem 1rem;
        }
        
        [data-testid="stSidebar"] h2 {
            color: #1E3A8A;
            font-size: 1.3rem;
            font-weight: 600;
        }
        
        /* File uploader styling */
        [data-testid="stFileUploader"] {
            border: 2px dashed #CBD5E1;
            border-radius: 8px;
            padding: 1rem;
            background-color: white;
        }
        
        /* Success messages */
        .element-container div[data-testid="stMarkdownContainer"] p {
            line-height: 1.6;
        }
        
        /* Button styling */
        .stButton button {
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        /* Hyperlink styling in responses */
        .stMarkdown a {
            color: #2563EB;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.2s ease;
        }
        
        .stMarkdown a:hover {
            color: #1D4ED8;
            text-decoration: underline;
        }
        
        /* Badge styling */
        .badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 12px;
            font-size: 0.875rem;
            font-weight: 600;
            margin: 0.25rem;
        }
        
        .badge-success {
            background-color: #D1FAE5;
            color: #065F46;
        }
        
        .badge-info {
            background-color: #DBEAFE;
            color: #1E40AF;
        }
        
        /* Example queries styling */
        .example-query {
            background-color: #F1F5F9;
            padding: 0.5rem 0.75rem;
            border-radius: 6px;
            margin: 0.25rem 0;
            font-size: 0.9rem;
            border-left: 3px solid #3B82F6;
        }
        
        /* Status indicator */
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.75rem;
            border-radius: 8px;
            margin-bottom: 1rem;
        }
        
        .status-success {
            background-color: #D1FAE5;
            border-left: 4px solid #10B981;
        }
        
        .status-warning {
            background-color: #FEF3C7;
            border-left: 4px solid #F59E0B;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header with improved styling
    st.markdown("""
        <h1>🤖 SmartAlly - AI Document Data Extractor</h1>
        <div class="subtitle">
            Powered by <strong>GPT-4</strong> for intelligent extraction of structured data from PDF and HTML documents.
            Upload your documents and ask questions in natural language to extract precise datapoints with source references.
        </div>
    """, unsafe_allow_html=True)
    
    # Check API key status with improved UI
    api_key_configured = bool(os.getenv("OPENAI_API_KEY"))
    if api_key_configured:
        st.markdown("""
            <div class="status-indicator status-success">
                <span style="font-size: 1.2rem;">✅</span>
                <span><strong>GPT-4 API Ready</strong> - Advanced LLM extraction enabled</span>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class="status-indicator status-warning">
                <span style="font-size: 1.2rem;">⚠️</span>
                <span><strong>API Key Required</strong> - Using fallback mode. Set your OpenAI API key in <code>.env</code> file to enable GPT-4 features.</span>
            </div>
        """, unsafe_allow_html=True)
    
    # Load datapoint mapping
    try:
        mapping_df = pd.read_csv('datapoint_mapping.csv')
    except FileNotFoundError:
        st.error("❌ datapoint_mapping.csv not found. Please ensure the file exists.")
        return
    
    # Improved sidebar with professional styling
    with st.sidebar:
        st.markdown("### 📁 Document Upload")
        st.markdown("Upload PDF or HTML documents to extract data")
        
        uploaded_files = st.file_uploader(
            "Choose files",
            type=['pdf', 'html', 'htm'],
            accept_multiple_files=True,
            key='file_uploader',
            help="Upload one or more PDF or HTML documents"
        )
        
        if uploaded_files:
            st.markdown(f"""
                <div style="background-color: #D1FAE5; padding: 0.75rem; border-radius: 8px; margin: 1rem 0;">
                    <span style="color: #065F46; font-weight: 600;">✅ {len(uploaded_files)} document(s) ready</span>
                </div>
            """, unsafe_allow_html=True)
            
            with st.expander("📄 View uploaded files", expanded=False):
                for file in uploaded_files:
                    st.markdown(f"• `{file.name}`")
        else:
            st.info("📤 No documents uploaded yet")
        
        st.markdown("---")
        
        # Extraction mode toggle with better styling
        st.markdown("### ⚙️ Settings")
        use_llm = st.checkbox(
            "Enable GPT-4 Extraction", 
            value=api_key_configured,
            disabled=not api_key_configured,
            help="Use GPT-4 for intelligent data extraction. Requires OpenAI API key."
        )
        
        if api_key_configured:
            st.markdown(f"""
                <div style="background-color: #DBEAFE; padding: 0.5rem; border-radius: 6px; margin-top: 0.5rem;">
                    <span style="color: #1E40AF; font-size: 0.85rem;">
                        🚀 <strong>Model:</strong> {OPENAI_MODEL}
                    </span>
                </div>
            """, unsafe_allow_html=True)
        
        if 'use_llm' not in st.session_state:
            st.session_state.use_llm = use_llm
        else:
            st.session_state.use_llm = use_llm
        
        st.markdown("---")
        
        # Improved example queries section
        st.markdown("### 💡 Example Queries")
        st.markdown("""
            <div style="font-size: 0.9rem; line-height: 1.8;">
                <div class="example-query">📊 Total annual fund operating expenses for Class A?</div>
                <div class="example-query">💰 Net expenses for Class F</div>
                <div class="example-query">🎯 Initial investment for Class C Shares</div>
                <div class="example-query">📉 CDSC schedule for Class C?</div>
                <div class="example-query">🔄 Redemption fee for Class Z</div>
                <div class="example-query">📈 Minimum subsequent investment (AIP) for Class R</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Additional info section
        st.markdown("### ℹ️ About")
        st.markdown("""
            <div style="font-size: 0.85rem; color: #64748B; line-height: 1.6;">
                SmartAlly uses advanced AI to extract financial data from fund prospectuses.
                All results include source page references for verification.
            </div>
        """, unsafe_allow_html=True)
    
    # Initialize session state for chat history
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    
    if 'parsed_docs' not in st.session_state:
        st.session_state.parsed_docs = {}
    
    # Parse uploaded documents (with caching)
    if uploaded_files:
        current_files = {file.name: file for file in uploaded_files}
        
        # Remove documents that are no longer uploaded
        for doc_name in list(st.session_state.parsed_docs.keys()):
            if doc_name not in current_files:
                del st.session_state.parsed_docs[doc_name]
        
        # Parse new documents
        for file_name, file in current_files.items():
            if file_name not in st.session_state.parsed_docs:
                with st.spinner(f"📄 Parsing {file_name}..."):
                    if file_name.lower().endswith('.pdf'):
                        pages = parse_pdf(file)
                        file.seek(0)
                        tables = parse_pdf_tables(file)
                        st.session_state.parsed_docs[file_name] = {
                            'type': 'pdf',
                            'pages': pages,
                            'tables': tables
                        }
                    elif file_name.lower().endswith(('.html', '.htm')):
                        text, anchors = parse_html(file)
                        st.session_state.parsed_docs[file_name] = {
                            'type': 'html',
                            'text': text,
                            'anchors': anchors
                        }
    
    # Show welcome message if no messages yet
    if not st.session_state.messages and st.session_state.parsed_docs:
        st.info("👋 **Ready to extract data!** Ask me questions about your uploaded documents. I'll find the information and show you exactly where it came from.")
    elif not st.session_state.messages:
        st.info("👋 **Welcome!** Upload documents using the sidebar to get started.")
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"], unsafe_allow_html=True)
    
    # Chat input with improved placeholder
    placeholder_text = "💬 Ask me anything about the documents... (e.g., 'What is the total annual operating expenses for Class A?')"
    if not st.session_state.parsed_docs:
        placeholder_text = "📤 Upload documents first to start asking questions..."
    
    if prompt := st.chat_input(placeholder_text, disabled=not st.session_state.parsed_docs):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        if not st.session_state.parsed_docs:
            response = """
---
### ⚠️ No Documents Available

Please upload at least one document using the sidebar before asking questions.

---
"""
        else:
            # Use the LLM setting from session state
            use_llm_mode = st.session_state.get('use_llm', api_key_configured)
            with st.spinner("🤔 Analyzing documents..."):
                response = chatbot_response(prompt, st.session_state.parsed_docs, mapping_df, use_llm=use_llm_mode)
        
        # Add assistant response to chat
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
