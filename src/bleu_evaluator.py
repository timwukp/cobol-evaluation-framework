#!/usr/bin/env python3
"""
BLEU Score Evaluator for COBOL Code Summarization
Implements secure BLEU scoring following XMainframe paper methodology
"""
import re
import json
import subprocess
import time
from typing import Dict, List, Tuple, Optional
from datasets import load_dataset
import sacrebleu
from evaluate import load

class SecureBLEUEvaluator:
    def __init__(self, sample_size: int = 50):
        self.sample_size = sample_size
        self.bleu_metric = load("bleu")
        
    def sanitize_input(self, text: str) -> str:
        """Sanitize input to prevent injection attacks"""
        if not isinstance(text, str):
            return ""
        # Remove potential command injection patterns
        text = re.sub(r'[;&|`$(){}[\]<>"\'\\\n\r\t]', '', text)
        # Limit length to prevent DoS
        return text[:2000].strip()
    
    def query_amazon_q(self, prompt: str) -> str:
        """Query Amazon Q CLI with security controls"""
        try:
            sanitized_prompt = self.sanitize_input(prompt)
            if not sanitized_prompt:
            result = subprocess.run(
                ['q', 'chat', '--no-input-file', '--'],
                input=sanitized_prompt,
                capture_output=True,
                text=True,
                timeout=30,
                cwd='/tmp'  # Secure working directory
            )
            return result.stdout.strip() if result.returncode == 0 else ""
        except Exception as e:
            print(f"Error querying Amazon Q: {e}")
            return ""
    
    def calculate_bleu_score(self, predictions: List[str], references: List[str]) -> Dict:
        """Calculate BLEU score using multiple methods for validation"""
        try:
            # Method 1: Using evaluate library (Hugging Face)
            hf_results = self.bleu_metric.compute(
                predictions=predictions,
                references=[[ref] for ref in references]
            )
            
            # Method 2: Using sacrebleu for validation
            sacre_score = sacrebleu.corpus_bleu(predictions, [references])
            
            return {
                'bleu_hf': hf_results['bleu'],
                'bleu_sacre': sacre_score.score / 100.0,  # Convert to 0-1 scale
                'precisions': hf_results.get('precisions', []),
                'brevity_penalty': hf_results.get('brevity_penalty', 0),
                'length_ratio': hf_results.get('length_ratio', 0),
                'translation_length': hf_results.get('translation_length', 0),
                'reference_length': hf_results.get('reference_length', 0)
            }
        except Exception as e:
            print(f"Error calculating BLEU: {e}")
            return {'bleu_hf': 0.0, 'bleu_sacre': 0.0}
    
    def evaluate_code_summarization(self) -> Dict:
        """Evaluate COBOL Code Summarization with BLEU scoring"""
        print("Loading COBOL Code Summarization dataset...")
        
        try:
            dataset = load_dataset("Fsoft-AIC/MainframeBench", "COBOL_code_summarization")
            data = dataset['train'].select(range(min(self.sample_size, len(dataset['train']))))
        except Exception as e:
            print(f"Error loading dataset: {e}")
            return {'error': 'Failed to load dataset'}
        
        predictions = []
        references = []
        results = []
        
        for i, example in enumerate(data):
            print(f"Code Summarization {i+1}/{len(data)}")
            
            # Create prompt for code summarization
            cobol_code = example.get('code', '')
            reference_summary = example.get('summary', '')
            
            if not cobol_code or not reference_summary:
                continue
                
            prompt = f"""Please provide a concise summary of this COBOL code:
            # Limit code length for security
            truncated_code = cobol_code[:1000]
            prompt = f"""Please provide a concise summary of this COBOL code:

```cobol
{truncated_code}

Provide only the summary, no additional explanation."""
            
            response = self.query_amazon_q(prompt)
            predicted_summary = self.extract_summary(response)
            
            predictions.append(predicted_summary)
            references.append(reference_summary)
            
            results.append({
                'code_snippet': cobol_code[:200] + "..." if len(cobol_code) > 200 else cobol_code,
                'reference_summary': reference_summary,
                'predicted_summary': predicted_summary,
                'response': response
            })
            
            time.sleep(1)  # Rate limiting
        
        # Calculate BLEU scores
        bleu_results = self.calculate_bleu_score(predictions, references)
        
        return {
            'task': 'COBOL Code Summarization',
            'total_samples': len(predictions),
            'bleu_scores': bleu_results,
            'primary_bleu': bleu_results.get('bleu_hf', 0.0),
            'validation_bleu': bleu_results.get('bleu_sacre', 0.0),
            'detailed_results': results[:5]  # Only include first 5 for security
        }
    
    def extract_summary(self, response: str) -> str:
        """Extract summary from Amazon Q response"""
        if not response:
            return ""
        
        # Clean and extract the summary
        lines = response.split('\n')
        summary_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('```'):
                summary_lines.append(line)
        
        summary = ' '.join(summary_lines)
        return self.sanitize_input(summary)

def main():
    """Run secure BLEU evaluation"""
    print("Starting COBOL Code Summarization BLEU Evaluation...")
    print("=" * 60)
    
    evaluator = SecureBLEUEvaluator(sample_size=10)  # Small test first
    results = evaluator.evaluate_code_summarization()
    
    if 'error' in results:
        print(f"Evaluation failed: {results['error']}")
        return
    
    print("\nBLEU EVALUATION RESULTS")
    print("=" * 60)
    print(f"Total Samples: {results['total_samples']}")
    print(f"Primary BLEU Score: {results['primary_bleu']:.4f}")
    print(f"Validation BLEU Score: {results['validation_bleu']:.4f}")
    
    bleu_scores = results['bleu_scores']
    if 'precisions' in bleu_scores:
        print(f"BLEU Precisions: {[f'{p:.4f}' for p in bleu_scores['precisions']]}")
    print(f"Brevity Penalty: {bleu_scores.get('brevity_penalty', 0):.4f}")
    
    # Save results securely
    output_file = 'bleu_evaluation_results.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()