"""
SmartAlly - Rule-Based Document Data Extractor Chatbot
A Streamlit application for extracting structured data from PDF and HTML documents
using rule-based pattern matching.
"""

import streamlit as st
import fitz  # PyMuPDF
import pdfplumber
from bs4 import BeautifulSoup
import pandas as pd
import re
from typing import Dict, List, Tuple, Optional, Any
import io


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
# Data Extraction Functions
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
                       page_num: Optional[int] = None, element_id: Optional[str] = None) -> str:
    """
    Generate a hyperlink to the location in the document.
    
    Args:
        doc_type: Type of document ("pdf" or "html")
        location: Description of where the value was found
        page_num: Page number (for PDFs)
        element_id: Element ID (for HTML)
        
    Returns:
        Hyperlink string
    """
    if doc_type == "pdf" and page_num:
        return f"📄 [Found on page {page_num}](#{page_num})"
    elif doc_type == "html" and element_id:
        return f"🔗 [Found at #{element_id}](#{element_id})"
    elif location:
        return f"📍 Found in: {location}"
    else:
        return "📍 Location unknown"


# ============================================================================
# Chatbot Response Handler
# ============================================================================

def parse_user_prompt(prompt: str, mapping_df: pd.DataFrame) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse user prompt to identify datapoint and class.
    
    Args:
        prompt: User's natural language prompt
        mapping_df: DataFrame with datapoint mappings
        
    Returns:
        Tuple of (datapoint_name, class_name)
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


def chatbot_response(user_prompt: str, parsed_docs: Dict[str, Any], 
                    mapping_df: pd.DataFrame) -> str:
    """
    Process user prompt and return extracted data with hyperlink.
    
    Args:
        user_prompt: User's natural language query
        parsed_docs: Dictionary containing parsed document data
        mapping_df: DataFrame with datapoint mappings
        
    Returns:
        Formatted response string
    """
    # Parse the prompt
    datapoint_name, class_name = parse_user_prompt(user_prompt, mapping_df)
    
    if not datapoint_name:
        return "❌ Could not identify the datapoint from your query. Please rephrase or be more specific."
    
    if not class_name:
        return "❌ Could not identify the share class. Please specify the class (e.g., Class A, Class I)."
    
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
            
            value, location = extract_datapoint(all_text, tables, datapoint_name, class_name, output_rule)
            
            if value and value != "0":
                # Find which page it was on (approximate)
                page_num = None
                for pnum, ptext in doc_data['pages'].items():
                    if location and any(keyword in ptext.lower() for keyword in location.split()):
                        page_num = pnum
                        break
                
                hyperlink = generate_hyperlink('pdf', location, page_num)
                results.append(f"**{value}**\n{hyperlink}")
        
        elif doc_data['type'] == 'html':
            all_text = doc_data['text']
            value, location = extract_datapoint(all_text, [], datapoint_name, class_name, output_rule)
            
            if value and value != "0":
                hyperlink = generate_hyperlink('html', location)
                results.append(f"**{value}**\n{hyperlink}")
    
    if results:
        return '\n\n'.join(results)
    else:
        return "**0**\n📍 Value not found in uploaded documents."


# ============================================================================
# Streamlit UI
# ============================================================================

def main():
    """Main Streamlit application."""
    
    st.set_page_config(
        page_title="SmartAlly - Document Data Extractor",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 SmartAlly - Rule-Based Document Data Extractor")
    st.markdown("Upload PDF or HTML documents and ask questions to extract specific data points.")
    
    # Load datapoint mapping
    try:
        mapping_df = pd.read_csv('datapoint_mapping.csv')
    except FileNotFoundError:
        st.error("❌ datapoint_mapping.csv not found. Please ensure the file exists.")
        return
    
    # Sidebar for file upload
    with st.sidebar:
        st.header("📁 Upload Documents")
        uploaded_files = st.file_uploader(
            "Upload PDF or HTML files",
            type=['pdf', 'html', 'htm'],
            accept_multiple_files=True,
            key='file_uploader'
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file(s) uploaded")
            for file in uploaded_files:
                st.text(f"• {file.name}")
        
        st.markdown("---")
        st.markdown("### 📖 Example Queries")
        st.markdown("""
        - Return only the Data Value of TOTAL_ANNUAL_FUND_OPERATING_EXPENSES for Class A
        - Return only the Data Value of NET_EXPENSES (after fee waiver/expense reimbursement) for Class F
        - From the Minimum Investment section, extract the value for Automatic Investment Plans under Subsequent investment for Class R
        - Initial investment for Class C Shares
        - CDSC Class C
        - Redemption Fee for Class Z
        """)
    
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
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question about the uploaded documents..."):
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate response
        if not st.session_state.parsed_docs:
            response = "❌ Please upload at least one document before asking questions."
        else:
            response = chatbot_response(prompt, st.session_state.parsed_docs, mapping_df)
        
        # Add assistant response to chat
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)


if __name__ == "__main__":
    main()
