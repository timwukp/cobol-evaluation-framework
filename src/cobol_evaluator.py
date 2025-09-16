#!/usr/bin/env python3
"""
COBOL Evaluation Framework using Amazon Q CLI
Tests Amazon Q CLI's COBOL capabilities on MainframeBench tasks

DISCLAIMER: This software is provided "AS IS" for research purposes only.
Users assume all risks. Not intended for production use without proper validation.
See DISCLAIMER.md for complete legal terms.
"""
import json
import subprocess
import time
from datasets import load_dataset
from typing import Dict, List, Tuple
import re

class COBOLEvaluator:
    def __init__(self, sample_size: int = 50):
        self.sample_size = sample_size
        self.results = {}
        
    def query_amazon_q(self, prompt: str) -> str:
        """Query Amazon Q CLI with a prompt"""
        try:
            result = subprocess.run(
                ['q', 'chat', '--no-input-file', prompt],
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout.strip() if result.returncode == 0 else ""
        except Exception as e:
            print(f"Error querying Amazon Q: {e}")
            return ""
    
    def evaluate_mcq(self) -> Dict:
        """Evaluate Multiple Choice Questions"""
        print("Loading MCQ dataset...")
        dataset = load_dataset("Fsoft-AIC/MainframeBench", "multiple_choice_question")
        data = dataset['train'].select(range(min(self.sample_size, len(dataset['train']))))
        
        correct = 0
        total = 0
        results = []
        
        for i, example in enumerate(data):
            print(f"MCQ {i+1}/{len(data)}")
            
            prompt = f"""Question: {example['question']}
A) {example['A']}
B) {example['B']}
C) {example['C']}
D) {example['D']}

Please answer with just the letter (A, B, C, or D)."""
            
            response = self.query_amazon_q(prompt)
            predicted = self.extract_mcq_answer(response)
            correct_answer = example['answer']
            
            is_correct = predicted == correct_answer
            if is_correct:
                correct += 1
            total += 1
            
            results.append({
                'question': example['question'],
                'predicted': predicted,
                'correct': correct_answer,
                'is_correct': is_correct,
                'response': response
            })
            
            time.sleep(1)  # Rate limiting
        
        accuracy = correct / total if total > 0 else 0
        return {
            'task': 'Multiple Choice Questions',
            'accuracy': accuracy,
            'correct': correct,
            'total': total,
            'results': results
        }
    
    def extract_mcq_answer(self, response: str) -> str:
        """Extract MCQ answer from response"""
        matches = re.findall(r'\b([ABCD])\b', response.upper())
        return matches[0] if matches else ""
    
    def run_evaluation(self) -> Dict:
        """Run complete evaluation"""
        print(f"Starting COBOL Evaluation with Amazon Q CLI")
        print(f"Sample size: {self.sample_size} per task")
        print("="*60)
        
        # Run evaluations
        mcq_results = self.evaluate_mcq()
        
        # Compile results
        final_results = {
            'evaluation_info': {
                'model': 'Amazon Q CLI (Claude)',
                'sample_size_per_task': self.sample_size,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            },
            'mcq': mcq_results
        }
        
        return final_results
    
    def save_results(self, results: Dict, filename: str = "cobol_eval_results.json"):
        """Save results to file"""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {filename}")

def main():
    evaluator = COBOLEvaluator(sample_size=20)
    results = evaluator.run_evaluation()
    evaluator.save_results(results)
    
    print("\n" + "="*60)
    print("EVALUATION SUMMARY")
    print("="*60)
    print(f"MCQ Accuracy: {results['mcq']['accuracy']:.2%} ({results['mcq']['correct']}/{results['mcq']['total']})")

if __name__ == "__main__":
    main()