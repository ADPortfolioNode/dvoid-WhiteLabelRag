"""
File utility functions
"""

import os
from werkzeug.utils import secure_filename

# Document types the upload + ingest pipeline can actually read.
# This is the single source of truth for document uploads: the upload
# endpoint, the document processor and the file picker all use this set,
# so adding a type here (plus an extractor in DocumentProcessor) is the
# whole change — no second list to update. app/config.py keeps its own
# copy only because it also lists the multimedia types.
ALLOWED_EXTENSIONS = {
    'txt', 'pdf', 'docx', 'md', 'csv',
    'html', 'htm', 'pptx', 'xlsx', 'epub', 'rtf', 'odt', 'json',
}

# Formats we cannot read, with a message that tells the user exactly
# how to get an uploadable file instead of a bare rejection. These are
# the common cases: old Office formats and Google Docs link files.
GUIDED_FORMATS = {
    'doc': ("This is an older Word (.doc) file. Open it in Word or "
            "Google Docs and save it as Word (.docx), then upload "
            "that file."),
    'xls': ("This is an older Excel (.xls) file. Open it in Excel or "
            "Google Sheets and save it as Excel (.xlsx), then upload "
            "that file."),
    'ppt': ("This is an older PowerPoint (.ppt) file. Open it in "
            "PowerPoint or Google Slides and save it as PowerPoint "
            "(.pptx), then upload that file."),
    'gdoc': ("This is a Google Docs link file, not the document "
             "itself. In Google Docs, use File > Download > "
             "Microsoft Word (.docx) or PDF, then upload that file."),
}

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_extension(filename):
    """Get file extension."""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

def secure_filename_with_timestamp(filename):
    """Create a secure filename with timestamp."""
    from datetime import datetime
    
    name, ext = os.path.splitext(secure_filename(filename))
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"{name}_{timestamp}{ext}"

def get_file_size_human(size_bytes):
    """Convert file size to human readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"

def validate_file_upload(file):
    """Validate uploaded file."""
    if not file:
        return False, "No file provided"
    
    if file.filename == '':
        return False, "No file selected"
    
    ext = get_file_extension(file.filename)
    if ext in GUIDED_FORMATS:
        return False, GUIDED_FORMATS[ext]
    
    if not allowed_file(file.filename):
        return False, f"File type not allowed. Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
    
    return True, "Valid file"
