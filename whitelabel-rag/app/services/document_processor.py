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
        """Get list of supported file formats."""
        return ['pdf', 'docx', 'txt', 'md', 'csv']
    
    def is_supported_format(self, file_path: str) -> bool:
        """Check if file format is supported."""
        file_ext = os.path.splitext(file_path)[1].lower().lstrip('.')
        return file_ext in self.get_supported_formats()