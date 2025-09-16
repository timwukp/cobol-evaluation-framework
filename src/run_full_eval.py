#!/usr/bin/env python3
"""
Full-scale evaluation runner for complete MainframeBench dataset

DISCLAIMER: This software is provided "AS IS" for research purposes only.
Users assume all risks. Not intended for production use without proper validation.
See DISCLAIMER.md for complete legal terms.
"""
import json
import subprocess
import time
import re
from concurrent.futures import ThreadPoolExecutor
import threading

class FullCOBOLEvaluator:
    def __init__(self, max_workers=3):
        self.max_workers = max_workers
        self.lock = threading.Lock()
        
    def query_q_cli(self, prompt, timeout=30):
        """Query Q CLI with timeout"""
        try:
            result = subprocess.run(
                ['q', 'chat', '--no-input-file', prompt],
                capture_output=True, text=True, timeout=timeout
            )
            return result.stdout.strip() if result.returncode == 0 else ""
        except:
            return ""
    
    def extract_mcq_answer(self, response):
        """Extract MCQ answer"""
        matches = re.findall(r'\b([ABCD])\b', response.upper())
        return matches[0] if matches else ""
    
    def evaluate_mcq_batch(self, tests, start_idx=0, batch_size=100):
        """Evaluate MCQ batch"""
        results = []
        correct = 0
        
        end_idx = min(start_idx + batch_size, len(tests))
        batch = tests[start_idx:end_idx]
        
        for i, test in enumerate(batch):
            actual_idx = start_idx + i
            print(f"MCQ {actual_idx + 1}/{len(tests)}")
            
            response = self.query_q_cli(test['prompt'])
            predicted = self.extract_mcq_answer(response)
            is_correct = predicted == test['correct']
            
            if is_correct:
                correct += 1
                
            results.append({
                'id': test['id'],
                'predicted': predicted,
                'correct': test['correct'],
                'is_correct': is_correct
            })
            
            time.sleep(0.5)  # Rate limiting
        
        return results, correct
    
    def run_full_evaluation(self, batch_size=200):
        """Run evaluation on full dataset"""
        print("Starting full MainframeBench evaluation...")
        
        # Load test files
        with open('data/full_multiple_choice_question_tests.json') as f:
            mcq_data = json.load(f)
        
        results = {
            'evaluation_info': {
                'total_tests': mcq_data['count'],
                'mcq_count': mcq_data['count'],
                'batch_size': batch_size
            }
        }
        
        # Evaluate MCQ
        print(f"\n=== MCQ Evaluation ({mcq_data['count']} questions) ===")
        mcq_results = []
        mcq_correct = 0
        
        for start in range(0, len(mcq_data['tests']), batch_size):
            batch_results, batch_correct = self.evaluate_mcq_batch(
                mcq_data['tests'], start, batch_size
            )
            mcq_results.extend(batch_results)
            mcq_correct += batch_correct
            
            # Save intermediate results
            with open(f'data/mcq_results_batch_{start}.json', 'w') as f:
                json.dump(batch_results, f, indent=2)
        
        results['mcq'] = {
            'accuracy': mcq_correct / len(mcq_results),
            'correct': mcq_correct,
            'total': len(mcq_results),
            'results': mcq_results
        }
        
        # Save final results
        with open('data/full_mainframebench_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n=== FINAL RESULTS ===")
        print(f"MCQ Accuracy: {results['mcq']['accuracy']:.2%}")
        print(f"Total tests completed: {results['evaluation_info']['total_tests']}")
        
        return results

def main():
    evaluator = FullCOBOLEvaluator()
    results = evaluator.run_full_evaluation(batch_size=50)

if __name__ == "__main__":
    main()