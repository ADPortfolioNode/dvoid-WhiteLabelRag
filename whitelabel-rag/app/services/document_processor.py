"""
Document processor for extracting text and creating chunks
"""

import os
import logging
from typing import List, Dict, Any
import PyPDF2
import docx
import markdown
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Processor for extracting text from various document formats."""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def process_document(self, file_path: str) -> List[Dict[str, Any]]:
        """Process a document and return chunks."""
        try:
            # Extract text based on file extension
            text = self._extract_text(file_path)
            
            if not text:
                logger.warning(f"No text extracted from {file_path}")
                return []
            
            # Create chunks
            chunks = self._create_chunks(text)
            
            # Add metadata to chunks
            filename = os.path.basename(file_path)
            processed_chunks = []
            
            for i, chunk in enumerate(chunks):
                processed_chunks.append({
                    'content': chunk,
                    'metadata': {
                        'source': filename,
                        'chunk_id': i,
                        'total_chunks': len(chunks),
                        'file_path': file_path,
                        'file_type': self._get_file_type(file_path)
                    }
                })
            
            logger.info(f"Processed {filename} into {len(processed_chunks)} chunks")
            return processed_chunks
            
        except Exception as e:
            logger.error(f"Error processing document {file_path}: {str(e)}")
            return []
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from file based on extension."""
        file_ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if file_ext == '.pdf':
                return self._extract_pdf_text(file_path)
            elif file_ext == '.docx':
                return self._extract_docx_text(file_path)
            elif file_ext == '.txt':
                return self._extract_txt_text(file_path)
            elif file_ext == '.md':
                return self._extract_markdown_text(file_path)
            elif file_ext in ['.csv']:
                return self._extract_csv_text(file_path)
            elif file_ext in ['.html', '.htm']:
                return self._extract_html_text(file_path)
            elif file_ext == '.pptx':
                return self._extract_pptx_text(file_path)
            elif file_ext == '.xlsx':
                return self._extract_xlsx_text(file_path)
            elif file_ext == '.epub':
                return self._extract_epub_text(file_path)
            elif file_ext == '.rtf':
                return self._extract_rtf_text(file_path)
            elif file_ext == '.odt':
                return self._extract_odt_text(file_path)
            elif file_ext == '.json':
                return self._extract_json_text(file_path)
            else:
                logger.warning(f"Unsupported file type: {file_ext}")
                return ""
                
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            return ""
    
    def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF file."""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            logger.error(f"Error reading PDF {file_path}: {str(e)}")
        
        return text.strip()
    
    def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        try:
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error reading DOCX {file_path}: {str(e)}")
            return ""
    
    def _extract_txt_text(self, file_path: str) -> str:
        """Extract text from TXT file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    return file.read()
            except Exception as e:
                logger.error(f"Error reading TXT {file_path}: {str(e)}")
                return ""
        except Exception as e:
            logger.error(f"Error reading TXT {file_path}: {str(e)}")
            return ""
    
    def _extract_markdown_text(self, file_path: str) -> str:
        """Extract text from Markdown file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                md_content = file.read()
            
            # Convert markdown to HTML then to plain text
            html = markdown.markdown(md_content)
            soup = BeautifulSoup(html, 'html.parser')
            return soup.get_text()
            
        except Exception as e:
            logger.error(f"Error reading Markdown {file_path}: {str(e)}")
            return ""
    
    def _extract_csv_text(self, file_path: str) -> str:
        """Extract text from CSV file."""
        try:
            import pandas as pd
            df = pd.read_csv(file_path)
            
            # Convert DataFrame to text representation
            text = f"CSV File: {os.path.basename(file_path)}\n"
            text += f"Columns: {', '.join(df.columns)}\n"
            text += f"Rows: {len(df)}\n\n"
            
            # Add first few rows as sample
            text += "Sample data:\n"
            text += df.head(10).to_string()
            
            return text
            
        except Exception as e:
            logger.error(f"Error reading CSV {file_path}: {str(e)}")
            return ""
    
    def _extract_html_text(self, file_path: str) -> str:
        """Extract text from an HTML file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as file:
                html_content = file.read()
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            return soup.get_text(separator='\n').strip()
        except Exception as e:
            logger.error(f"Error reading HTML {file_path}: {str(e)}")
            return ""
    
    def _extract_pptx_text(self, file_path: str) -> str:
        """Extract text from a PowerPoint file."""
        try:
            from pptx import Presentation
            prs = Presentation(file_path)
            text = ""
            for slide in prs.slides:
                for shape in slide.shapes:
                    if shape.has_text_frame:
                        for paragraph in shape.text_frame.paragraphs:
                            text += ''.join(run.text for run in paragraph.runs) + "\n"
                    if shape.has_table:
                        for row in shape.table.rows:
                            text += " | ".join(cell.text for cell in row.cells) + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error reading PPTX {file_path}: {str(e)}")
            return ""
    
    def _extract_xlsx_text(self, file_path: str) -> str:
        """Extract text from an Excel workbook (all sheets)."""
        try:
            import pandas as pd
            sheets = pd.read_excel(file_path, sheet_name=None)
            text = f"Excel File: {os.path.basename(file_path)}\n"
            for name, df in sheets.items():
                text += f"\nSheet: {name}\n"
                text += f"Columns: {', '.join(str(c) for c in df.columns)}\n"
                text += f"Rows: {len(df)}\n"
                text += df.head(10).to_string() + "\n"
            return text
        except Exception as e:
            logger.error(f"Error reading XLSX {file_path}: {str(e)}")
            return ""
    
    def _extract_epub_text(self, file_path: str) -> str:
        """Extract text from an EPUB (a zip of XHTML documents)."""
        try:
            import zipfile
            text = ""
            with zipfile.ZipFile(file_path) as book:
                for name in book.namelist():
                    if name.lower().endswith(('.xhtml', '.html', '.htm')):
                        html_content = book.read(name).decode('utf-8', errors='ignore')
                        soup = BeautifulSoup(html_content, 'html.parser')
                        text += soup.get_text(separator='\n') + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error reading EPUB {file_path}: {str(e)}")
            return ""
    
    def _extract_rtf_text(self, file_path: str) -> str:
        """Extract text from a Rich Text Format file."""
        try:
            from striprtf.striprtf import rtf_to_text
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                return rtf_to_text(file.read()).strip()
        except Exception as e:
            logger.error(f"Error reading RTF {file_path}: {str(e)}")
            return ""
    
    def _extract_odt_text(self, file_path: str) -> str:
        """Extract text from an OpenDocument Text file (zip + content.xml)."""
        try:
            import zipfile
            import xml.etree.ElementTree as ET
            with zipfile.ZipFile(file_path) as doc:
                xml_content = doc.read('content.xml')
            root = ET.fromstring(xml_content)
            paragraphs = []
            for el in root.iter():
                if el.tag.endswith('}p') or el.tag.endswith('}h'):
                    paragraphs.append(''.join(el.itertext()).strip())
            return '\n'.join(p for p in paragraphs if p).strip()
        except Exception as e:
            logger.error(f"Error reading ODT {file_path}: {str(e)}")
            return ""
    
    def _extract_json_text(self, file_path: str) -> str:
        """Extract text from a JSON file (pretty-printed, or raw text)."""
        try:
            import json
            with open(file_path, 'r', encoding='utf-8') as file:
                raw = file.read()
            try:
                parsed = json.loads(raw)
                return json.dumps(parsed, indent=2, ensure_ascii=False)
            except json.JSONDecodeError:
                return raw
        except Exception as e:
            logger.error(f"Error reading JSON {file_path}: {str(e)}")
            return ""
    
    def _create_chunks(self, text: str) -> List[str]:
        """Create overlapping chunks from text."""
        if not text:
            return []
        
        # Split text into words
        words = text.split()
        
        if len(words) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(words):
            end = start + self.chunk_size
            chunk_words = words[start:end]
            chunk_text = ' '.join(chunk_words)
            chunks.append(chunk_text)
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            
            # Break if we've reached the end
            if end >= len(words):
                break
        
        return chunks
    
    def _get_file_type(self, file_path: str) -> str:
        """Get file type from extension."""
        return os.path.splitext(file_path)[1].lower().lstrip('.')
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats.

        Derives from file_utils.ALLOWED_EXTENSIONS, the single source of
        truth for document uploads, so the processor never drifts from
        what the upload endpoint accepts.
        """
        from app.utils.file_utils import ALLOWED_EXTENSIONS
        return sorted(ALLOWED_EXTENSIONS)
    
    def is_supported_format(self, file_path: str) -> bool:
        """Check if file format is supported."""
        file_ext = os.path.splitext(file_path)[1].lower().lstrip('.')
        return file_ext in self.get_supported_formats()
