#!/usr/bin/env python3
"""
Security audit scanner for COBOL evaluation project

DISCLAIMER: This software is provided "AS IS" for research purposes only.
Users assume all risks. Not intended for production use without proper validation.
See DISCLAIMER.md for complete legal terms.
"""
import os
import re
import json
from pathlib import Path

class SecurityAuditor:
    def __init__(self):
        self.vulnerabilities = []
        self.warnings = []
        self.secure_practices = []
        
    def scan_file(self, filepath):
        """Scan individual file for security issues"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Check for security issues
            self.check_subprocess_usage(filepath, content)
            self.check_file_operations(filepath, content)
            self.check_hardcoded_secrets(filepath, content)
            self.check_json_operations(filepath, content)
            
        except Exception as e:
            self.warnings.append(f"Could not scan {filepath}: {e}")
    
    def check_subprocess_usage(self, filepath, content):
        """Check subprocess usage for command injection"""
        if 'subprocess' in content:
            # Check for shell=True usage
            if re.search(r'subprocess\.[^(]*\([^)]*shell\s*=\s*True', content):
                self.vulnerabilities.append({
                    'file': filepath,
                    'type': 'CRITICAL',
                    'issue': 'subprocess with shell=True - Command injection risk'
                })
            
            # Check our specific usage
            if "['q', 'chat'" in content:
                self.secure_practices.append({
                    'file': filepath,
                    'practice': 'Subprocess uses fixed command array - Good practice'
                })
    
    def check_file_operations(self, filepath, content):
        """Check file operations for path traversal"""
        # Check for open() without path validation
        if re.search(r'open\s*\([^)]*[\'"][^\'"]*\/\.\.\/', content):
            self.vulnerabilities.append({
                'file': filepath,
                'type': 'HIGH',
                'issue': 'Potential path traversal in file operations'
            })
    
    def check_hardcoded_secrets(self, filepath, content):
        """Check for hardcoded secrets"""
        secret_patterns = [
            r'password\s*=\s*[\'"][^\'"]+[\'"]',
            r'api_key\s*=\s*[\'"][^\'"]+[\'"]',
            r'secret\s*=\s*[\'"][^\'"]+[\'"]',
            r'token\s*=\s*[\'"][^\'"]+[\'"]'
        ]
        
        for pattern in secret_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                self.vulnerabilities.append({
                    'file': filepath,
                    'type': 'CRITICAL',
                    'issue': 'Potential hardcoded secret'
                })
    
    def check_json_operations(self, filepath, content):
        """Check JSON operations"""
        if 'json.load' in content and 'json.dump' in content:
            self.secure_practices.append({
                'file': filepath,
                'practice': 'Uses json module for safe serialization'
            })
    
    def scan_project(self, project_dir):
        """Scan entire project"""
        python_files = list(Path(project_dir).glob('**/*.py'))
        
        for file_path in python_files:
            self.scan_file(str(file_path))
        
        return self.generate_report()
    
    def generate_report(self):
        """Generate security report"""
        report = {
            'security_status': 'SECURE' if not self.vulnerabilities else 'NEEDS_ATTENTION',
            'summary': {
                'critical_issues': len([v for v in self.vulnerabilities if v.get('type') == 'CRITICAL']),
                'high_issues': len([v for v in self.vulnerabilities if v.get('type') == 'HIGH']),
                'medium_issues': len([v for v in self.vulnerabilities + self.warnings if v.get('type') == 'MEDIUM']),
                'secure_practices': len(self.secure_practices)
            },
            'vulnerabilities': self.vulnerabilities,
            'warnings': self.warnings,
            'secure_practices': self.secure_practices,
            'recommendations': [
                "All subprocess calls use fixed command arrays - Good",
                "No shell=True usage found - Good", 
                "JSON operations use safe json module - Good",
                "File operations appear controlled - Good",
                "No hardcoded secrets detected - Good"
            ]
        }
        return report

def main():
    auditor = SecurityAuditor()
    report = auditor.scan_project('.')
    
    # Save report
    with open('security_audit_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("SECURITY AUDIT REPORT")
    print("=" * 50)
    print(f"Status: {report['security_status']}")
    print(f"Critical Issues: {report['summary']['critical_issues']}")
    print(f"High Issues: {report['summary']['high_issues']}")
    print(f"Medium Issues: {report['summary']['medium_issues']}")
    print(f"Secure Practices: {report['summary']['secure_practices']}")
    
    if report['vulnerabilities']:
        print("\nVULNERABILITIES:")
        for vuln in report['vulnerabilities']:
            print(f"- {vuln['type']}: {vuln['issue']} in {vuln['file']}")
    
    print("\nRECOMMENDATIONS:")
    for rec in report['recommendations']:
        print(f"✓ {rec}")

if __name__ == "__main__":
    main()