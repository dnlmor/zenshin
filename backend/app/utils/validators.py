import re
import os
from urllib.parse import urlparse
from typing import Optional, List


def validate_github_url(url: str) -> bool:
    """
    Validate if a URL is a valid GitHub repository URL.
    
    Args:
        url: The URL to validate
        
    Returns:
        bool: True if valid GitHub repo URL, False otherwise
    """
    if not url or not isinstance(url, str):
        return False
    
    try:
        parsed = urlparse(url)
        
        # Check if it's GitHub
        if parsed.netloc.lower() not in ['github.com', 'www.github.com']:
            return False
        
        # Check path format: should be /owner/repo or /owner/repo/
        path_parts = parsed.path.strip('/').split('/')
        
        # Should have at least owner and repo
        if len(path_parts) < 2:
            return False
        
        owner, repo = path_parts[0], path_parts[1]
        
        # Basic validation for owner and repo names
        # GitHub usernames/repo names can contain alphanumeric chars, hyphens, underscores
        github_name_pattern = r'^[a-zA-Z0-9._-]+$'
        
        if not re.match(github_name_pattern, owner) or not re.match(github_name_pattern, repo):
            return False
        
        # Owner and repo shouldn't be empty
        if not owner or not repo:
            return False
        
        return True
        
    except Exception:
        return False


def validate_api_key(api_key: str, key_type: str = "claude") -> bool:
    """
    Validate API key format.
    
    Args:
        api_key: The API key to validate
        key_type: Type of API key ('claude' or 'github')
        
    Returns:
        bool: True if valid format, False otherwise
    """
    if not api_key or not isinstance(api_key, str):
        return False
    
    if key_type.lower() == "claude":
        # Claude API keys typically start with 'sk-ant-' and are long
        return api_key.startswith('sk-ant-') and len(api_key) > 20
    
    elif key_type.lower() == "github":
        # GitHub personal access tokens are typically 40 characters
        # Can start with 'ghp_', 'gho_', 'ghu_', 'ghs_', or 'ghr_' for new tokens
        # Or be 40 hex characters for classic tokens
        if api_key.startswith(('ghp_', 'gho_', 'ghu_', 'ghs_', 'ghr_')):
            return len(api_key) >= 36  # Modern GitHub tokens
        else:
            # Classic tokens - 40 hex characters
            return len(api_key) == 40 and all(c in '0123456789abcdef' for c in api_key.lower())
    
    return False


def validate_file_types(file_types: List[str]) -> bool:
    """
    Validate file type extensions.
    
    Args:
        file_types: List of file extensions
        
    Returns:
        bool: True if all extensions are valid, False otherwise
    """
    if not file_types or not isinstance(file_types, list):
        return False
    
    # Common programming language extensions
    valid_extensions = {
        'py', 'js', 'ts', 'tsx', 'jsx', 'java', 'cpp', 'c', 'h', 'hpp',
        'cs', 'php', 'rb', 'go', 'rs', 'swift', 'kt', 'scala', 'r',
        'sh', 'bash', 'zsh', 'ps1', 'bat', 'cmd', 'sql', 'html', 'css',
        'scss', 'sass', 'less', 'xml', 'json', 'yaml', 'yml', 'toml',
        'ini', 'cfg', 'conf', 'md', 'rst', 'txt', 'vue', 'svelte'
    }
    
    for ext in file_types:
        if not isinstance(ext, str) or ext.lower() not in valid_extensions:
            return False
    
    return True


def validate_max_files(max_files: int) -> bool:
    """
    Validate maximum files parameter.
    
    Args:
        max_files: Maximum number of files to analyze
        
    Returns:
        bool: True if valid, False otherwise
    """
    return isinstance(max_files, int) and 1 <= max_files <= 100


def validate_environment_variables() -> tuple[bool, List[str]]:
    """
    Validate required environment variables.
    
    Returns:
        tuple: (is_valid, list_of_missing_vars)
    """
    required_vars = ['CLAUDE_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
    
    return len(missing_vars) == 0, missing_vars


def sanitize_file_path(file_path: str) -> str:
    """
    Sanitize file path to prevent directory traversal attacks.
    
    Args:
        file_path: The file path to sanitize
        
    Returns:
        str: Sanitized file path
    """
    if not file_path:
        return ""
    
    # Remove any path traversal attempts
    sanitized = file_path.replace('..', '').replace('//', '/').strip('/')
    
    # Remove any null bytes
    sanitized = sanitized.replace('\0', '')
    
    return sanitized


def validate_request_size(content: str, max_size_mb: float = 10.0) -> bool:
    """
    Validate that content size is within limits.
    
    Args:
        content: Content to check
        max_size_mb: Maximum size in megabytes
        
    Returns:
        bool: True if within limits, False otherwise
    """
    if not content:
        return True
    
    size_bytes = len(content.encode('utf-8'))
    max_bytes = max_size_mb * 1024 * 1024
    
    return size_bytes <= max_bytes