# Clickable Hyperlinks Feature

## Overview

SmartAlly now generates clickable hyperlinks for extracted datapoints that open documents in a new tab and direct users to the specific location of the data.

## Key Features

### 1. Unique Tag Generation
Each extracted datapoint receives a unique 8-character tag identifier:
- Generated using MD5 hash of: `doc_name + page_num/element_id + value`
- Example: `🔖 23812fe1`
- Displayed as a yellow badge next to the datapoint reference

### 2. Clickable Document Links
- **PDF Documents**: Base64-encoded data URLs with page anchors
  - Format: `data:application/pdf;base64,{encoded}#page=X`
  - Opens PDF directly in browser at specified page
  
- **HTML Documents**: Base64-encoded data URLs with section anchors
  - Format: `data:text/html;base64,{encoded}#{anchor}`
  - Jumps to specific section/element in HTML

### 3. Enhanced User Experience
- Links open in new tabs (`target="_blank"`)
- Styled as prominent buttons for better visibility
- Include helpful instructions for users
- Professional design with hover effects

## Example Output

### Before (Old Format)
```
💼 1.19%
📄 Page 3 in `prospectus.pdf` - Annual Fund Operating Expenses section
```

### After (New Format)
```
💼 1.19%
📄 Page 3 in `prospectus.pdf` - Annual Fund Operating Expenses section 🔖 23812fe1

[📥 Open Page 3 in `prospectus.pdf`]  ← Clickable button

💡 Click the link above to open the PDF. Navigate to page 3 to find the highlighted data.
```

## Technical Implementation

### Modified Functions

#### `generate_hyperlink()`
- Added parameters: `file_bytes`, `value`
- Generates unique tags using MD5 hashing
- Creates base64-encoded data URLs
- Returns formatted HTML with clickable links

#### Document Parsing
- Updated `main()` to store `file_bytes` in session state
- Both PDF and HTML files store original bytes alongside parsed content

#### `chatbot_response()`
- Passes `file_bytes` and `value` to `generate_hyperlink()`
- Supports both LLM and rule-based extraction modes

### Dependencies
- `base64`: For encoding file data
- `hashlib`: For generating unique tags

## Usage

No changes required from user perspective. The feature works automatically:

1. Upload a document (PDF or HTML)
2. Ask a question to extract a datapoint
3. Results now include:
   - The extracted value
   - A unique tag badge
   - A clickable link to open the document
   - Instructions on how to find the data

## Browser Compatibility

The feature uses standard data URLs supported by all modern browsers:
- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- Mobile browsers: ✅ Supported (may download instead of preview)

## Limitations

- **File Size**: Very large PDFs (>100MB) may cause performance issues with base64 encoding
- **Browser Memory**: Opening multiple large documents may consume significant memory
- **PDF Page Navigation**: Some browsers may not support `#page=X` fragment identifier and will open at page 1
- **Fallback Mode**: If file bytes are not available, displays static text without clickable link

## Future Enhancements

Potential improvements:
1. PDF.js integration for guaranteed page navigation
2. Highlighting specific text within the page
3. Server-side document hosting for large files
4. Thumbnail previews of the relevant page
5. Annotation support to mark exact datapoint location
