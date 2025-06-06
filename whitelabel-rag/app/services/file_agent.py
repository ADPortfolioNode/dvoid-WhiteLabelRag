"""
FileAgent - Specialized for file operations and document management
"""

import os
import logging
from typing import Dict, Any, List
from datetime import datetime
from app.services.base_assistant import BaseAssistant
from app.services.document_processor import DocumentProcessor
from app.services.rag_manager import get_rag_manager
from app.config import Config

logger = logging.getLogger(__name__)

class FileAgent(BaseAssistant):
    """
    FileAgent - Specialized for file operations and document management.
    Handles document upload processing, format conversion, metadata extraction, and content chunking.
    """
    
    def __init__(self):
        super().__init__("FileAgent")
        self.config = Config.ASSISTANT_CONFIGS['FileAgent']
        self.uploads_path = os.path.abspath(os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
            Config.UPLOAD_FOLDER
        ))
        self.document_processor = DocumentProcessor(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP
        )
        self.rag_manager = get_rag_manager()
        
        # Ensure uploads directory exists
        os.makedirs(self.uploads_path, exist_ok=True)
    
    def handle_message(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle file-related requests."""
        try:
            # Validate input
            is_valid, validation_message = self._validate_input(message)
            if not is_valid:
                return self.report_failure(validation_message)
            
            # Update status
            self._update_status("running", 10, "Processing file request...")
            
            # Determine the type of file operation
            operation = self._determine_operation(message)
            
            if operation == "list_files":
                return self._list_files()
            elif operation == "file_info":
                return self._get_file_info(message)
            elif operation == "process_file":
                return self._process_file_from_message(message)
            elif operation == "delete_file":
                return self._delete_file(message)
            elif operation == "file_stats":
                return self._get_file_statistics()
            else:
                return self._provide_file_help()
                
        except Exception as e:
            logger.error(f"Error in FileAgent.handle_message: {str(e)}")
            return self.report_failure(f"File operation error: {str(e)}")
    
    def _determine_operation(self, message: str) -> str:
        """Determine what file operation the user wants."""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['list', 'show', 'files', 'documents']):
            return "list_files"
        elif any(word in message_lower for word in ['info', 'details', 'about']) and 'file' in message_lower:
            return "file_info"
        elif any(word in message_lower for word in ['process', 'ingest', 'upload', 'add']):
            return "process_file"
        elif any(word in message_lower for word in ['delete', 'remove']):
            return "delete_file"
        elif any(word in message_lower for word in ['stats', 'statistics', 'summary']):
            return "file_stats"
        else:
            return "help"
    
    def _list_files(self) -> Dict[str, Any]:
        """List all uploaded files."""
        try:
            self._update_status("running", 30, "Scanning upload directory...")
            
            if not os.path.exists(self.uploads_path):
                return self.report_success("No upload directory found. No files have been uploaded yet.")
            
            files = []
            for filename in os.listdir(self.uploads_path):
                file_path = os.path.join(self.uploads_path, filename)
                if os.path.isfile(file_path):
                    file_info = self._get_file_metadata(file_path)
                    files.append(file_info)
            
            if not files:
                return self.report_success("No files found in the upload directory.")
            
            # Sort files by modification time (newest first)
            files.sort(key=lambda x: x['modified'], reverse=True)
            
            # Format file list
            file_list_text = self._format_file_list(files)
            
            return self.report_success(
                text=file_list_text,
                additional_data={
                    'files': files,
                    'total_files': len(files)
                }
            )
            
        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            return self.report_failure(f"Error listing files: {str(e)}")
    
    def _get_file_info(self, message: str) -> Dict[str, Any]:
        """Get detailed information about a specific file."""
        try:
            # Extract filename from message
            filename = self._extract_filename_from_message(message)
            
            if not filename:
                return self.report_failure("Please specify which file you want information about.")
            
            file_path = os.path.join(self.uploads_path, filename)
            
            if not os.path.exists(file_path):
                return self.report_failure(f"File '{filename}' not found.")
            
            self._update_status("running", 50, f"Getting information for {filename}...")
            
            # Get detailed file information
            file_info = self._get_detailed_file_info(file_path)
            
            # Format the information
            info_text = self._format_file_info(file_info)
            
            return self.report_success(
                text=info_text,
                additional_data={'file_info': file_info}
            )
            
        except Exception as e:
            logger.error(f"Error getting file info: {str(e)}")
            return self.report_failure(f"Error getting file information: {str(e)}")
    
    def _process_file_from_message(self, message: str) -> Dict[str, Any]:
        """Process a file mentioned in the message."""
        try:
            # Extract filename from message
            filename = self._extract_filename_from_message(message)
            
            if not filename:
                return self.report_failure("Please specify which file you want to process.")
            
            file_path = os.path.join(self.uploads_path, filename)
            
            if not os.path.exists(file_path):
                return self.report_failure(f"File '{filename}' not found.")
            
            return self.process_file(file_path)
            
        except Exception as e:
            logger.error(f"Error processing file from message: {str(e)}")
            return self.report_failure(f"Error processing file: {str(e)}")
    
    def process_file(self, file_path: str) -> Dict[str, Any]:
        """Process a file and ingest it into the vector database."""
        try:
            filename = os.path.basename(file_path)
            
            self._update_status("running", 20, f"Processing {filename}...")
            
            # Check if file format is supported
            if not self.document_processor.is_supported_format(file_path):
                return self.report_failure(f"File format not supported for {filename}")
            
            # Process the document
            self._update_status("running", 40, f"Extracting text from {filename}...")
            chunks = self.document_processor.process_document(file_path)
            
            if not chunks:
                return self.report_failure(f"No content could be extracted from {filename}")
            
            # Store chunks in vector database
            self._update_status("running", 70, f"Storing {len(chunks)} chunks in vector database...")
            
            stored_chunks = 0
            for chunk in chunks:
                try:
                    chunk_id = self.rag_manager.store_document_chunk(
                        content=chunk['content'],
                        metadata={
                            **chunk['metadata'],
                            'processed_at': datetime.now().isoformat(),
                            'file_size': os.path.getsize(file_path)
                        }
                    )
                    stored_chunks += 1
                except Exception as e:
                    logger.error(f"Error storing chunk: {str(e)}")
            
            if stored_chunks == 0:
                return self.report_failure(f"Failed to store any chunks from {filename}")
            
            # Generate summary
            summary_text = self._generate_processing_summary(filename, stored_chunks, len(chunks))
            
            return self.report_success(
                text=summary_text,
                additional_data={
                    'filename': filename,
                    'chunks_created': len(chunks),
                    'chunks_stored': stored_chunks,
                    'file_processed': True
                }
            )
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            return self.report_failure(f"Error processing file: {str(e)}")
    
    def _delete_file(self, message: str) -> Dict[str, Any]:
        """Delete a file from the upload directory."""
        try:
            # Extract filename from message
            filename = self._extract_filename_from_message(message)
            
            if not filename:
                return self.report_failure("Please specify which file you want to delete.")
            
            file_path = os.path.join(self.uploads_path, filename)
            
            if not os.path.exists(file_path):
                return self.report_failure(f"File '{filename}' not found.")
            
            self._update_status("running", 50, f"Deleting {filename}...")
            
            # Delete the file
            os.remove(file_path)
            
            return self.report_success(f"Successfully deleted {filename}")
            
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            return self.report_failure(f"Error deleting file: {str(e)}")
    
    def _get_file_statistics(self) -> Dict[str, Any]:
        """Get statistics about uploaded files."""
        try:
            self._update_status("running", 30, "Calculating file statistics...")
            
            if not os.path.exists(self.uploads_path):
                return self.report_success("No files have been uploaded yet.")
            
            stats = {
                'total_files': 0,
                'total_size': 0,
                'file_types': {},
                'largest_file': None,
                'newest_file': None,
                'oldest_file': None
            }
            
            newest_time = 0
            oldest_time = float('inf')
            largest_size = 0
            
            for filename in os.listdir(self.uploads_path):
                file_path = os.path.join(self.uploads_path, filename)
                if os.path.isfile(file_path):
                    stats['total_files'] += 1
                    
                    # File size
                    size = os.path.getsize(file_path)
                    stats['total_size'] += size
                    
                    if size > largest_size:
                        largest_size = size
                        stats['largest_file'] = filename
                    
                    # File type
                    ext = os.path.splitext(filename)[1].lower()
                    stats['file_types'][ext] = stats['file_types'].get(ext, 0) + 1
                    
                    # Modification time
                    mtime = os.path.getmtime(file_path)
                    if mtime > newest_time:
                        newest_time = mtime
                        stats['newest_file'] = filename
                    if mtime < oldest_time:
                        oldest_time = mtime
                        stats['oldest_file'] = filename
            
            # Format statistics
            stats_text = self._format_file_statistics(stats)
            
            return self.report_success(
                text=stats_text,
                additional_data={'statistics': stats}
            )
            
        except Exception as e:
            logger.error(f"Error getting file statistics: {str(e)}")
            return self.report_failure(f"Error getting file statistics: {str(e)}")
    
    def _provide_file_help(self) -> Dict[str, Any]:
        """Provide help information about file operations."""
        help_text = """File Operations Help:

I can help you with the following file operations:

📁 **List Files**: "list files", "show documents"
   - Shows all uploaded files with basic information

📄 **File Information**: "info about [filename]", "details for [filename]"
   - Shows detailed information about a specific file

⚙️ **Process Files**: "process [filename]", "ingest [filename]"
   - Processes a file and adds it to the searchable database

🗑️ **Delete Files**: "delete [filename]", "remove [filename]"
   - Removes a file from the upload directory

📊 **File Statistics**: "file stats", "file summary"
   - Shows statistics about all uploaded files

**Supported File Types**: PDF, DOCX, TXT, MD, CSV

**Examples**:
- "List all my files"
- "Show info about report.pdf"
- "Process the document.docx file"
- "Delete old_file.txt"
- "Show file statistics"
"""
        
        return self.report_success(help_text)
    
    def _extract_filename_from_message(self, message: str) -> str:
        """Extract filename from user message."""
        # Simple extraction - look for common file extensions
        import re
        
        # Pattern to match filenames with extensions
        pattern = r'([a-zA-Z0-9_\-\.]+\.(pdf|docx|txt|md|csv))'
        match = re.search(pattern, message, re.IGNORECASE)
        
        if match:
            return match.group(1)
        
        # If no extension found, look for quoted strings
        quoted_pattern = r'"([^"]+)"'
        quoted_match = re.search(quoted_pattern, message)
        if quoted_match:
            return quoted_match.group(1)
        
        # Look for words that might be filenames (without spaces)
        words = message.split()
        for word in words:
            if '.' in word and len(word) > 3:
                return word
        
        return None
    
    def _get_file_metadata(self, file_path: str) -> Dict[str, Any]:
        """Get basic metadata for a file."""
        try:
            stat = os.stat(file_path)
            filename = os.path.basename(file_path)
            
            return {
                'name': filename,
                'size': stat.st_size,
                'size_human': self._format_file_size(stat.st_size),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'modified_human': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                'extension': os.path.splitext(filename)[1].lower(),
                'is_supported': self.document_processor.is_supported_format(file_path)
            }
        except Exception as e:
            logger.error(f"Error getting file metadata: {str(e)}")
            return {'name': os.path.basename(file_path), 'error': str(e)}
    
    def _get_detailed_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get detailed information about a file."""
        basic_info = self._get_file_metadata(file_path)
        
        # Add more detailed information
        try:
            # Try to get a preview of the content
            if basic_info.get('is_supported'):
                preview = self._get_file_preview(file_path)
                basic_info['preview'] = preview
            
            # Add processing status
            basic_info['can_process'] = basic_info.get('is_supported', False)
            
        except Exception as e:
            logger.error(f"Error getting detailed file info: {str(e)}")
            basic_info['preview_error'] = str(e)
        
        return basic_info
    
    def _get_file_preview(self, file_path: str, max_chars: int = 200) -> str:
        """Get a preview of file content."""
        try:
            # Extract a small amount of text for preview
            text = self.document_processor._extract_text(file_path)
            if text:
                preview = text[:max_chars]
                if len(text) > max_chars:
                    preview += "..."
                return preview
            return "No text content could be extracted"
        except Exception as e:
            return f"Error getting preview: {str(e)}"
    
    def _format_file_list(self, files: List[Dict[str, Any]]) -> str:
        """Format file list for display."""
        if not files:
            return "No files found."
        
        lines = ["📁 **Uploaded Files:**\n"]
        
        for file_info in files:
            name = file_info.get('name', 'Unknown')
            size = file_info.get('size_human', 'Unknown size')
            modified = file_info.get('modified_human', 'Unknown date')
            supported = "✅" if file_info.get('is_supported') else "❌"
            
            lines.append(f"{supported} **{name}** ({size}) - Modified: {modified}")
        
        lines.append(f"\n📊 Total: {len(files)} files")
        
        return "\n".join(lines)
    
    def _format_file_info(self, file_info: Dict[str, Any]) -> str:
        """Format detailed file information."""
        name = file_info.get('name', 'Unknown')
        size = file_info.get('size_human', 'Unknown')
        modified = file_info.get('modified_human', 'Unknown')
        extension = file_info.get('extension', 'Unknown')
        supported = "Yes" if file_info.get('is_supported') else "No"
        can_process = "Yes" if file_info.get('can_process') else "No"
        
        info_lines = [
            f"📄 **File Information: {name}**\n",
            f"**Size:** {size}",
            f"**Type:** {extension.upper()} file",
            f"**Modified:** {modified}",
            f"**Supported Format:** {supported}",
            f"**Can Process:** {can_process}"
        ]
        
        if 'preview' in file_info:
            info_lines.append(f"\n**Content Preview:**\n{file_info['preview']}")
        
        return "\n".join(info_lines)
    
    def _format_file_statistics(self, stats: Dict[str, Any]) -> str:
        """Format file statistics."""
        total_files = stats.get('total_files', 0)
        total_size = self._format_file_size(stats.get('total_size', 0))
        
        lines = [
            "📊 **File Statistics:**\n",
            f"**Total Files:** {total_files}",
            f"**Total Size:** {total_size}"
        ]
        
        # File types
        file_types = stats.get('file_types', {})
        if file_types:
            lines.append("\n**File Types:**")
            for ext, count in file_types.items():
                ext_display = ext.upper() if ext else "No extension"
                lines.append(f"  • {ext_display}: {count} files")
        
        # Largest file
        if stats.get('largest_file'):
            lines.append(f"\n**Largest File:** {stats['largest_file']}")
        
        # Newest and oldest
        if stats.get('newest_file'):
            lines.append(f"**Newest File:** {stats['newest_file']}")
        if stats.get('oldest_file'):
            lines.append(f"**Oldest File:** {stats['oldest_file']}")
        
        return "\n".join(lines)
    
    def _format_file_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format."""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        size = float(size_bytes)
        
        while size >= 1024.0 and i < len(size_names) - 1:
            size /= 1024.0
            i += 1
        
        return f"{size:.1f} {size_names[i]}"
    
    def _generate_processing_summary(self, filename: str, stored_chunks: int, total_chunks: int) -> str:
        """Generate a summary of file processing."""
        success_rate = (stored_chunks / total_chunks * 100) if total_chunks > 0 else 0
        
        summary = f"✅ **File Processing Complete: {filename}**\n\n"
        summary += f"📄 **Chunks Created:** {total_chunks}\n"
        summary += f"💾 **Chunks Stored:** {stored_chunks}\n"
        summary += f"📊 **Success Rate:** {success_rate:.1f}%\n\n"
        
        if stored_chunks == total_chunks:
            summary += "🎉 All chunks were successfully processed and stored in the vector database. "
            summary += "The document is now searchable!"
        elif stored_chunks > 0:
            summary += f"⚠️ {total_chunks - stored_chunks} chunks failed to store. "
            summary += "The document is partially searchable."
        else:
            summary += "❌ No chunks were stored. The document is not searchable."
        
        return summary

# Singleton instance
_file_agent_instance = None

def get_file_agent_instance() -> FileAgent:
    """Get the singleton FileAgent instance."""
    global _file_agent_instance
    if _file_agent_instance is None:
        _file_agent_instance = FileAgent()
    return _file_agent_instance