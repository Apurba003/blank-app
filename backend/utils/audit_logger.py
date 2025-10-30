"""
Audit Logger Module

Logs security events and authentication attempts.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any
import threading


class AuditLogger:
    """
    Audit logger for security events.
    """
    
    def __init__(self, log_dir: str = 'storage/logs'):
        """
        Initialize audit logger.
        
        Args:
            log_dir: Directory for log files
        """
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        
        self.lock = threading.Lock()
    
    def log_event(self, event_type: str, user_id: str, details: Dict[str, Any]):
        """
        Log a security event.
        
        Args:
            event_type: Type of event (e.g., 'login', 'enrollment')
            user_id: User identifier
            details: Additional event details
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'user_id': user_id,
            'details': details
        }
        
        # Append to daily log file
        date_str = datetime.now().strftime('%Y-%m-%d')
        log_file = os.path.join(self.log_dir, f'audit_{date_str}.log')
        
        with self.lock:
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
    
    def get_user_logs(self, user_id: str, limit: int = 100) -> list:
        """
        Get audit logs for a user.
        
        Args:
            user_id: User identifier
            limit: Maximum number of logs to return
            
        Returns:
            List of log entries
        """
        logs = []
        
        # Read from all log files (newest first)
        log_files = sorted(
            [f for f in os.listdir(self.log_dir) if f.startswith('audit_')],
            reverse=True
        )
        
        for log_file in log_files:
            filepath = os.path.join(self.log_dir, log_file)
            
            try:
                with open(filepath, 'r') as f:
                    for line in f:
                        try:
                            entry = json.loads(line.strip())
                            if entry.get('user_id') == user_id:
                                logs.append(entry)
                                
                                if len(logs) >= limit:
                                    return logs
                        except json.JSONDecodeError:
                            continue
            except FileNotFoundError:
                continue
        
        return logs
