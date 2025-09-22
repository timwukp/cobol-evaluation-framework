#!/usr/bin/env python3
"""
Full-Scale COBOL Evaluation Framework for AWS EKS
Runs complete MainframeBench dataset (7,052 tests) with production-grade monitoring
"""
import json
import subprocess
import time
import os
from datasets import load_dataset
from typing import Dict, List
import re
from bleu_evaluator import SecureBLEUEvaluator

class FullScaleCOBOLEvaluator:
    def __init__(self):
        # Full dataset sizes from MainframeBench
        self.mcq_total = 1931
        self.qa_total = 2598  
        self.code_total = 2523
        self.total_tests = 7052
        
        self.bleu_evaluator = SecureBLEUEvaluator(sample_size=self.code_total)
        
    def sanitize_input(self, text: str) -> str:
        """Enhanced security sanitization"""
        if not isinstance(text, str):
            return ""
        text = re.sub(r'[;&|`$(){}[\]<>"\'\\\\n\r\t]', '', text)
        return text[:2000].strip()
        
    def query_amazon_q(self, prompt: str) -> str:
        """Query Amazon Q CLI with enhanced error handling"""
        try:
            sanitized_prompt = self.sanitize_input(prompt)
            result = subprocess.run(
                ['q', 'chat', '--no-input-file', '--'],
                input=sanitized_prompt,
                capture_output=True,
                text=True,
                timeout=60,  # Increased timeout for complex queries
                cwd='/tmp'
            )
            return result.stdout.strip() if result.returncode == 0 else ""
        except Exception as e:
            print(f"Error querying Amazon Q: {e}")
            return ""
    
    def evaluate_mcq_full(self) -> Dict:
        """Evaluate ALL Multiple Choice Questions (1,931 tests)"""
        print(f"Loading FULL MCQ dataset ({self.mcq_total} tests)...")
        try:
            dataset = load_dataset("Fsoft-AIC/MainframeBench", "multiple_choice_question")
            data = dataset['train']  # Full dataset
            print(f"Loaded {len(data)} MCQ questions")
        except Exception as e:
            print(f"Error loading MCQ dataset: {e}")
            return {'error': 'Failed to load MCQ dataset'}
        
        correct = 0
        total = 0
        results = []
        batch_size = 50  # Process in batches for monitoring
        
        for i, example in enumerate(data):
            print(f"MCQ Progress: {i+1}/{len(data)} ({((i+1)/len(data)*100):.1f}%)")
            
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
            
            # Store detailed results for first 10 and every 100th
            if i < 10 or (i + 1) % 100 == 0:
                results.append({
                    'question_id': i + 1,
                    'question': example['question'][:100] + "..." if len(example['question']) > 100 else example['question'],
                    'predicted': predicted,
                    'correct': correct_answer,
                    'is_correct': is_correct
                })
            
            # Progress checkpoint every 100 questions
            if (i + 1) % 100 == 0:
                current_accuracy = correct / total
                print(f"Checkpoint {i+1}: Accuracy = {current_accuracy:.3f} ({correct}/{total})")
                self.save_checkpoint('mcq', i+1, correct, total, current_accuracy)
            
            time.sleep(0.5)  # Rate limiting
        
        accuracy = correct / total if total > 0 else 0
        return {
            'task': 'Multiple Choice Questions (FULL)',
            'accuracy': accuracy,
            'correct': correct,
            'total': total,
            'sample_results': results,
            'completion_status': 'COMPLETE'
        }
    
    def evaluate_qa_full(self) -> Dict:
        """Evaluate ALL Question Answering (2,598 tests)"""
        print(f"Loading FULL QA dataset ({self.qa_total} tests)...")
        try:
            dataset = load_dataset("Fsoft-AIC/MainframeBench", "question_answering")
            data = dataset['train']  # Full dataset
            print(f"Loaded {len(data)} QA questions")
        except Exception as e:
            print(f"Error loading QA dataset: {e}")
            return {'error': 'Failed to load QA dataset'}
        
        results = []
        quality_scores = []
        
        for i, example in enumerate(data):
            print(f"QA Progress: {i+1}/{len(data)} ({((i+1)/len(data)*100):.1f}%)")
            
            question = example.get('question', '')
            reference_answer = example.get('answer', '')
            
            if not question or not reference_answer:
                continue
                
            prompt = f"""Question: {question}

Please provide a comprehensive answer based on mainframe and COBOL knowledge."""
            
            response = self.query_amazon_q(prompt)
            quality_score = self.assess_qa_quality(response, reference_answer)
            quality_scores.append(quality_score)
            
            # Store detailed results for first 10 and every 200th
            if i < 10 or (i + 1) % 200 == 0:
                results.append({
                    'question_id': i + 1,
                    'question': question[:100] + "..." if len(question) > 100 else question,
                    'reference_length': len(reference_answer.split()),
                    'response_length': len(response.split()),
                    'quality_score': quality_score
                })
            
            # Progress checkpoint every 200 questions
            if (i + 1) % 200 == 0:
                current_avg = sum(quality_scores) / len(quality_scores)
                print(f"Checkpoint {i+1}: Avg Quality = {current_avg:.3f}")
                self.save_checkpoint('qa', i+1, len(quality_scores), len(quality_scores), current_avg)
            
            time.sleep(0.5)  # Rate limiting
        
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        return {
            'task': 'Question Answering (FULL)',
            'total_samples': len(quality_scores),
            'average_quality_score': avg_quality,
            'sample_results': results,
            'completion_status': 'COMPLETE'
        }
    
    def assess_qa_quality(self, response: str, reference: str) -> float:
        """Enhanced QA quality assessment"""
        if not response or not reference:
            return 0.0
        
        response_words = set(response.lower().split())
        reference_words = set(reference.lower().split())
        
        if not reference_words:
            return 0.0
            
        # Keyword overlap
        overlap = len(response_words.intersection(reference_words))
        overlap_ratio = overlap / len(reference_words)
        
        # Length appropriateness
        length_ratio = min(len(response.split()) / len(reference.split()), 1.0)
        
        # Completeness bonus for comprehensive answers
        completeness_bonus = 0.1 if len(response.split()) >= 20 else 0
        
        return min(overlap_ratio * 0.6 + length_ratio * 0.3 + completeness_bonus, 1.0)
    
    def extract_mcq_answer(self, response: str) -> str:
        """Extract MCQ answer with improved pattern matching"""
        matches = re.findall(r'\b([ABCD])\b', response.upper())
        return matches[0] if matches else ""
    
    def save_checkpoint(self, task: str, current: int, correct_or_count: int, total: int, score: float):
        """Save progress checkpoints"""
        checkpoint = {
            'task': task,
            'progress': f"{current}/{total if task == 'mcq' else 'N/A'}",
            'current_score': score,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'completion_percentage': (current / total * 100) if task == 'mcq' else (current / self.qa_total * 100)
        }
        
        filename = f"/results/{task}_checkpoint_{current}.json"
        os.makedirs('/results', exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(checkpoint, f, indent=2)
        print(f"Checkpoint saved: {filename}")
    
    def run_full_scale_evaluation(self) -> Dict:
        """Run complete MainframeBench evaluation (7,052 tests)"""
        print("🚀 STARTING FULL-SCALE MAINFRAMEBENCH EVALUATION")
        print(f"Total Tests: {self.total_tests}")
        print(f"- MCQ: {self.mcq_total} tests")
        print(f"- QA: {self.qa_total} tests") 
        print(f"- Code Summarization: {self.code_total} tests")
        print("="*80)
        
        start_time = time.time()
        
        # Run all evaluations
        print("\n🔍 Phase 1: Multiple Choice Questions")
        mcq_results = self.evaluate_mcq_full()
        
        print("\n💬 Phase 2: Question Answering")
        qa_results = self.evaluate_qa_full()
        
        print("\n📝 Phase 3: Code Summarization (BLEU)")
        # Use full dataset for BLEU evaluation
        bleu_results = self.bleu_evaluator.evaluate_code_summarization()
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # Calculate comprehensive results
        mcq_score = mcq_results.get('accuracy', 0) if 'error' not in mcq_results else 0
        qa_score = qa_results.get('average_quality_score', 0) if 'error' not in qa_results else 0
        bleu_score = bleu_results.get('primary_bleu', 0) if 'error' not in bleu_results else 0
        
        # Weighted overall score (matching academic standards)
        overall_score = (mcq_score * 0.4 + qa_score * 0.3 + bleu_score * 0.3)
        
        final_results = {
            'evaluation_info': {
                'model': 'Amazon Q CLI (Claude)',
                'dataset': 'MainframeBench (Complete)',
                'total_tests': self.total_tests,
                'duration_hours': total_duration / 3600,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'evaluation_type': 'Full-Scale Production Assessment'
            },
            'task_results': {
                'mcq_results': mcq_results,
                'qa_results': qa_results,
                'code_summarization_results': bleu_results
            },
            'performance_summary': {
                'overall_score': overall_score,
                'mcq_accuracy': mcq_score,
                'qa_quality': qa_score,
                'bleu_score': bleu_score,
                'tests_completed': {
                    'mcq': mcq_results.get('total', 0),
                    'qa': qa_results.get('total_samples', 0),
                    'code': bleu_results.get('total_samples', 0)
                }
            },
            'benchmarks': {
                'vs_xmainframe_instruct': {
                    'mcq_improvement': ((mcq_score - 0.7789) / 0.7789 * 100) if mcq_score > 0 else 0,
                    'bleu_improvement': ((bleu_score - 0.1139) / 0.1139 * 100) if bleu_score > 0 else 0
                },
                'vs_gpt35': {
                    'bleu_improvement': ((bleu_score - 0.12) / 0.12 * 100) if bleu_score > 0 else 0
                }
            }
        }
        
        return final_results
    
    def save_results(self, results: Dict, filename: str = "/results/full_scale_mainframebench_results.json"):
        """Save comprehensive results"""
        os.makedirs('/results', exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Full results saved to {filename}")
        
        # Also save summary
        summary_file = "/results/evaluation_summary.json"
        summary = {
            'timestamp': results['evaluation_info']['timestamp'],
            'total_tests': results['evaluation_info']['total_tests'],
            'duration_hours': results['evaluation_info']['duration_hours'],
            'overall_score': results['performance_summary']['overall_score'],
            'task_scores': {
                'mcq_accuracy': results['performance_summary']['mcq_accuracy'],
                'qa_quality': results['performance_summary']['qa_quality'],
                'bleu_score': results['performance_summary']['bleu_score']
            }
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"Summary saved to {summary_file}")

def main():
    """Run full-scale evaluation with monitoring"""
    print("FULL-SCALE MAINFRAMEBENCH EVALUATION ON AWS EKS")
    print("="*80)
    
    evaluator = FullScaleCOBOLEvaluator()
    results = evaluator.run_full_scale_evaluation()
    evaluator.save_results(results)
    
    print("\n" + "="*80)
    print("FULL-SCALE EVALUATION COMPLETE")
    print("="*80)
    
    perf = results['performance_summary']
    print(f"Overall Score: {perf['overall_score']:.3f}")
    print(f"MCQ Accuracy: {perf['mcq_accuracy']:.3f} ({perf['tests_completed']['mcq']} tests)")
    print(f"QA Quality: {perf['qa_quality']:.3f} ({perf['tests_completed']['qa']} tests)")
    print(f"BLEU Score: {perf['bleu_score']:.4f} ({perf['tests_completed']['code']} tests)")
    
    # Show improvements vs baselines
    benchmarks = results['benchmarks']
    print(f"\nVs XMainframe-Instruct:")
    print(f"  MCQ: {benchmarks['vs_xmainframe_instruct']['mcq_improvement']:+.1f}%")
    print(f"  BLEU: {benchmarks['vs_xmainframe_instruct']['bleu_improvement']:+.1f}%")
    
    print(f"\nVs GPT-3.5:")
    print(f"  BLEU: {benchmarks['vs_gpt35']['bleu_improvement']:+.1f}%")
    
    print(f"\nTotal Duration: {results['evaluation_info']['duration_hours']:.1f} hours")
    print(f"Results saved to: /results/")

if __name__ == "__main__":
    main()