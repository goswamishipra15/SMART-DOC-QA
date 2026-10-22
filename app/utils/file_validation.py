from pathlib import Path
ALLOWED_EXTENSIONS = {".pdf", ".docx"}
def is_allowed_file(filename: str) -> bool: return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS
