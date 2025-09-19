import re
from typing import Optional, List, Dict
from pathlib import Path


# Language extensions mapping
LANGUAGE_EXTENSIONS = {
    'python': ['.py', '.pyw', '.pyi'],
    'javascript': ['.js', '.mjs'],
    'typescript': ['.ts'],
    'tsx': ['.tsx'],
    'jsx': ['.jsx'],
    'java': ['.java'],
    'cpp': ['.cpp', '.cc', '.cxx', '.c++'],
    'c': ['.c'],
    'header': ['.h', '.hpp', '.hxx', '.h++'],
    'csharp': ['.cs'],
    'php': ['.php'],
    'ruby': ['.rb'],
    'go': ['.go'],
    'rust': ['.rs'],
    'swift': ['.swift'],
    'kotlin': ['.kt'],
    'scala': ['.scala'],
    'r': ['.r', '.R'],
    'shell': ['.sh', '.bash', '.zsh'],
    'powershell': ['.ps1'],
    'batch': ['.bat', '.cmd'],
    'sql': ['.sql'],
    'html': ['.html', '.htm'],
    'css': ['.css'],
    'scss': ['.scss'],
    'sass': ['.sass'],
    'less': ['.less'],
    'xml': ['.xml'],
    'json': ['.json'],
    'yaml': ['.yaml', '.yml'],
    'toml': ['.toml'],
    'ini': ['.ini'],
    'config': ['.cfg', '.conf'],
    'markdown': ['.md'],
    'vue': ['.vue'],
    'svelte': ['.svelte']
}

# Reverse mapping for quick lookup
EXTENSION_TO_LANGUAGE = {}
for language, extensions in LANGUAGE_EXTENSIONS.items():
    for ext in extensions:
        EXTENSION_TO_LANGUAGE[ext.lower()] = language


def detect_language(file_path: str) -> Optional[str]:
    """
    Detect programming language from file path/extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        str: Detected language name, or None if unknown
    """
    if not file_path:
        return None
    
    # Get file extension
    path_obj = Path(file_path)
    extension = path_obj.suffix.lower()
    
    # Handle special cases
    if path_obj.name.lower() in ['dockerfile', 'makefile', 'rakefile']:
        return path_obj.name.lower()
    
    # Check extension mapping
    return EXTENSION_TO_LANGUAGE.get(extension)


def is_supported_file(file_path: str, allowed_extensions: List[str]) -> bool:
    """
    Check if a file is supported for analysis based on its extension.
    
    Args:
        file_path: Path to the file
        allowed_extensions: List of allowed file extensions (without dots)
        
    Returns:
        bool: True if file is supported, False otherwise
    """
    if not file_path or not allowed_extensions:
        return False
    
    path_obj = Path(file_path)
    extension = path_obj.suffix.lower().lstrip('.')
    
    # Convert allowed extensions to lowercase for comparison
    allowed_lower = [ext.lower().lstrip('.') for ext in allowed_extensions]
    
    return extension in allowed_lower


def calculate_complexity_score(content: str, language: Optional[str] = None) -> int:
    """
    Calculate a simple complexity score for code content.
    
    Args:
        content: The code content
        language: Programming language (optional)
        
    Returns:
        int: Complexity score from 0-100 (100 = simple, 0 = very complex)
    """
    if not content:
        return 100
    
    lines = content.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    
    if not non_empty_lines:
        return 100
    
    # Base score
    score = 100
    
    # Length penalty
    if len(non_empty_lines) > 100:
        score -= min(30, (len(non_empty_lines) - 100) // 20)
    
    # Nesting level penalty
    max_nesting = _calculate_max_nesting(content, language)
    if max_nesting > 3:
        score -= min(25, (max_nesting - 3) * 5)
    
    # Complexity keywords penalty
    complexity_keywords = _count_complexity_keywords(content, language)
    if complexity_keywords > 10:
        score -= min(20, (complexity_keywords - 10) * 2)
    
    # Long line penalty
    long_lines = sum(1 for line in non_empty_lines if len(line) > 120)
    if long_lines > 5:
        score -= min(15, (long_lines - 5) * 3)
    
    # Comment ratio bonus
    comment_lines = _count_comment_lines(content, language)
    comment_ratio = comment_lines / len(non_empty_lines) if non_empty_lines else 0
    if comment_ratio > 0.1:  # More than 10% comments
        score += min(10, int(comment_ratio * 50))
    
    return max(0, min(100, score))


def _calculate_max_nesting(content: str, language: Optional[str] = None) -> int:
    """Calculate maximum nesting level in code."""
    lines = content.split('\n')
    max_nesting = 0
    current_nesting = 0
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        
        # Count opening braces/keywords that increase nesting
        if language in ['javascript', 'typescript', 'java', 'cpp', 'c', 'csharp']:
            current_nesting += line.count('{')
            current_nesting -= line.count('}')
        elif language == 'python':
            # Python uses indentation
            if stripped.endswith(':') and any(keyword in stripped for keyword in ['if', 'for', 'while', 'def', 'class', 'try', 'with']):
                current_nesting += 1
            # Rough approximation: if line is less indented, reduce nesting
            leading_spaces = len(line) - len(line.lstrip())
            expected_spaces = current_nesting * 4  # Assuming 4-space indentation
            if leading_spaces < expected_spaces:
                current_nesting = max(0, leading_spaces // 4)
        
        max_nesting = max(max_nesting, current_nesting)
    
    return max_nesting


def _count_complexity_keywords(content: str, language: Optional[str] = None) -> int:
    """Count complexity-increasing keywords."""
    complexity_keywords = []
    
    if language == 'python':
        complexity_keywords = ['if', 'elif', 'for', 'while', 'try', 'except', 'with', 'lambda']
    elif language in ['javascript', 'typescript']:
        complexity_keywords = ['if', 'for', 'while', 'switch', 'try', 'catch', 'function']
    elif language == 'java':
        complexity_keywords = ['if', 'for', 'while', 'switch', 'try', 'catch']
    else:
        # Generic keywords
        complexity_keywords = ['if', 'for', 'while', 'try', 'catch', 'switch']
    
    count = 0
    for keyword in complexity_keywords:
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(keyword) + r'\b'
        count += len(re.findall(pattern, content, re.IGNORECASE))
    
    return count


def _count_comment_lines(content: str, language: Optional[str] = None) -> int:
    """Count comment lines based on language."""
    lines = content.split('\n')
    comment_count = 0
    
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        
        # Single-line comments
        if language == 'python':
            if stripped.startswith('#'):
                comment_count += 1
        elif language in ['javascript', 'typescript', 'java', 'cpp', 'c', 'csharp']:
            if stripped.startswith('//') or stripped.startswith('/*'):
                comment_count += 1
        elif language == 'html':
            if '<!--' in stripped:
                comment_count += 1
        elif language in ['yaml', 'yml']:
            if stripped.startswith('#'):
                comment_count += 1
        else:
            # Generic: check for common comment patterns
            if stripped.startswith(('#', '//', '/*', '<!--')):
                comment_count += 1
    
    return comment_count


def get_file_statistics(content: str) -> Dict[str, int]:
    """
    Get basic statistics about a file.
    
    Args:
        content: File content
        
    Returns:
        dict: Statistics including lines, characters, etc.
    """
    lines = content.split('\n')
    
    return {
        'total_lines': len(lines),
        'non_empty_lines': len([line for line in lines if line.strip()]),
        'characters': len(content),
        'words': len(content.split()),
        'max_line_length': max(len(line) for line in lines) if lines else 0
    }


def is_text_file(content: bytes, max_sample_size: int = 8192) -> bool:
    """
    Check if content appears to be text (not binary).
    
    Args:
        content: File content as bytes
        max_sample_size: Maximum bytes to sample
        
    Returns:
        bool: True if appears to be text, False otherwise
    """
    if not content:
        return True
    
    # Sample first portion of file
    sample = content[:max_sample_size]
    
    # Check for null bytes (common in binary files)
    if b'\x00' in sample:
        return False
    
    # Try to decode as UTF-8
    try:
        sample.decode('utf-8')
        return True
    except UnicodeDecodeError:
        pass
    
    # Try other common encodings
    for encoding in ['latin-1', 'cp1252']:
        try:
            sample.decode(encoding)
            return True
        except UnicodeDecodeError:
            continue
    
    return False