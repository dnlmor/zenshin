import json
import re
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


def parse_claude_response(claude_response: str) -> Dict[str, Any]:
    """
    Parse Claude's response and extract structured data.
    
    Args:
        claude_response: Raw response from Claude API
        
    Returns:
        dict: Parsed and structured response data
    """
    if not claude_response:
        return _get_empty_response()
    
    # Try to extract JSON from the response
    json_data = _extract_json_from_response(claude_response)
    
    if json_data:
        # Validate and clean the JSON data
        return _validate_and_clean_response(json_data)
    else:
        # Fallback: parse text response
        return _parse_text_response(claude_response)


def _extract_json_from_response(response: str) -> Optional[Dict[str, Any]]:
    """Extract JSON object from Claude's response."""
    # Try to find JSON block in response
    json_patterns = [
        r'```json\s*(\{.*?\})\s*```',  # JSON in code block
        r'```\s*(\{.*?\})\s*```',      # JSON in generic code block
        r'(\{.*?\})',                   # Raw JSON object
    ]
    
    for pattern in json_patterns:
        matches = re.findall(pattern, response, re.DOTALL)
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue
    
    return None


def _validate_and_clean_response(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and clean the parsed JSON response."""
    cleaned = {}
    
    # Extract analysis summary
    summary = data.get('analysis_summary', {})
    cleaned['analysis_summary'] = {
        'total_issues': _safe_int(summary.get('total_issues', 0)),
        'security_issues': _safe_int(summary.get('security_issues', 0)),
        'performance_issues': _safe_int(summary.get('performance_issues', 0)),
        'maintainability_issues': _safe_int(summary.get('maintainability_issues', 0)),
        'style_issues': _safe_int(summary.get('style_issues', 0)),
        'bug_issues': _safe_int(summary.get('bug_issues', 0)),
        'overall_score': _safe_int(summary.get('overall_score', 85), min_val=0, max_val=100)
    }
    
    # Extract detailed issues
    issues = data.get('detailed_issues', [])
    cleaned['detailed_issues'] = []
    
    for issue in issues:
        if isinstance(issue, dict):
            cleaned_issue = {
                'file': str(issue.get('file', 'unknown')),
                'line': _safe_int(issue.get('line')) if issue.get('line') is not None else None,
                'type': _validate_issue_type(issue.get('type', 'maintainability')),
                'severity': _validate_severity(issue.get('severity', 'medium')),
                'message': str(issue.get('message', ''))[:500],  # Truncate long messages
                'suggestion': str(issue.get('suggestion', ''))[:1000],  # Truncate long suggestions
                'code_snippet': str(issue.get('code_snippet', ''))[:2000] if issue.get('code_snippet') else None,
                'improved_code': str(issue.get('improved_code', ''))[:2000] if issue.get('improved_code') else None
            }
            cleaned['detailed_issues'].append(cleaned_issue)
    
    # Extract file scores
    file_scores = data.get('file_scores', [])
    cleaned['file_scores'] = []
    
    for file_score in file_scores:
        if isinstance(file_score, dict):
            cleaned_score = {
                'file': str(file_score.get('file', 'unknown')),
                'score': _safe_int(file_score.get('score', 85), min_val=0, max_val=100),
                'issues_count': _safe_int(file_score.get('issues_count', 0))
            }
            cleaned['file_scores'].append(cleaned_score)
    
    # Extract general feedback
    cleaned['general_feedback'] = str(data.get('general_feedback', ''))[:2000]
    
    return cleaned


def _parse_text_response(response: str) -> Dict[str, Any]:
    """Parse text response when JSON extraction fails."""
    logger.warning("Failed to extract JSON from Claude response, using fallback text parsing")
    
    # Basic text parsing fallback
    issues_count = len(re.findall(r'\b(issue|problem|bug|error|warning)\b', response, re.IGNORECASE))
    security_mentions = len(re.findall(r'\b(security|vulnerable|exploit)\b', response, re.IGNORECASE))
    performance_mentions = len(re.findall(r'\b(performance|slow|optimize|inefficient)\b', response, re.IGNORECASE))
    
    return {
        'analysis_summary': {
            'total_issues': issues_count,
            'security_issues': min(security_mentions, issues_count),
            'performance_issues': min(performance_mentions, issues_count),
            'maintainability_issues': max(0, issues_count - security_mentions - performance_mentions),
            'style_issues': 0,
            'bug_issues': 0,
            'overall_score': max(50, 100 - (issues_count * 10))  # Simple scoring
        },
        'detailed_issues': [],
        'file_scores': [],
        'general_feedback': response[:1000]  # Truncate for safety
    }


def _get_empty_response() -> Dict[str, Any]:
    """Get empty response structure."""
    return {
        'analysis_summary': {
            'total_issues': 0,
            'security_issues': 0,
            'performance_issues': 0,
            'maintainability_issues': 0,
            'style_issues': 0,
            'bug_issues': 0,
            'overall_score': 85
        },
        'detailed_issues': [],
        'file_scores': [],
        'general_feedback': 'No analysis available.'
    }


def _safe_int(value: Any, default: int = 0, min_val: int = None, max_val: int = None) -> int:
    """Safely convert value to integer with bounds checking."""
    try:
        result = int(value)
        if min_val is not None:
            result = max(min_val, result)
        if max_val is not None:
            result = min(max_val, result)
        return result
    except (ValueError, TypeError):
        return default


def _validate_issue_type(issue_type: str) -> str:
    """Validate and normalize issue type."""
    valid_types = ['security', 'performance', 'maintainability', 'style', 'bug']
    normalized = str(issue_type).lower().strip()
    
    if normalized in valid_types:
        return normalized
    
    # Try to map common variations
    mappings = {
        'sec': 'security',
        'perf': 'performance',
        'maint': 'maintainability',
        'maintain': 'maintainability',
        'format': 'style',
        'formatting': 'style',
        'error': 'bug',
        'defect': 'bug'
    }
    
    return mappings.get(normalized, 'maintainability')


def _validate_severity(severity: str) -> str:
    """Validate and normalize severity level."""
    valid_severities = ['critical', 'high', 'medium', 'low']
    normalized = str(severity).lower().strip()
    
    if normalized in valid_severities:
        return normalized
    
    # Try to map common variations
    mappings = {
        'crit': 'critical',
        'urgent': 'critical',
        'major': 'high',
        'minor': 'low',
        'info': 'low',
        'warning': 'medium',
        'warn': 'medium'
    }
    
    return mappings.get(normalized, 'medium')


def calculate_overall_score(issues: List[Dict[str, Any]]) -> int:
    """
    Calculate overall score based on issues.
    
    Args:
        issues: List of issue dictionaries
        
    Returns:
        int: Overall score from 0-100
    """
    if not issues:
        return 95
    
    # Weight by severity
    severity_weights = {
        'critical': 25,
        'high': 15,
        'medium': 8,
        'low': 3
    }
    
    total_penalty = 0
    for issue in issues:
        severity = issue.get('severity', 'medium')
        penalty = severity_weights.get(severity, 8)
        total_penalty += penalty
    
    # Calculate score
    base_score = 100
    final_score = max(0, base_score - total_penalty)
    
    return final_score


def format_error_response(error_message: str, error_type: str = "analysis_error") -> Dict[str, Any]:
    """
    Format error response in consistent structure.
    
    Args:
        error_message: Error message
        error_type: Type of error
        
    Returns:
        dict: Formatted error response
    """
    return {
        'error': True,
        'error_type': error_type,
        'message': str(error_message),
        'analysis_summary': _get_empty_response()['analysis_summary'],
        'detailed_issues': [],
        'file_scores': [],
        'general_feedback': f"Analysis failed: {error_message}"
    }