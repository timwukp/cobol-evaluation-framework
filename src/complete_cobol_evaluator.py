#!/usr/bin/env python3
"""
Complete COBOL Evaluation Framework with BLEU Implementation
Integrates MCQ, QA, and Code Summarization with proper BLEU scoring
"""
import json
import subprocess
import time
from datasets import load_dataset
from typing import Dict, List, Tuple
import re
from bleu_evaluator import SecureBLEUEvaluator

class CompleteCOBOLEvaluator:
    def __init__(self, sample_size: int = 50):
        self.sample_size = sample_size
        self.bleu_evaluator = SecureBLEUEvaluator(sample_size)
        
    def sanitize_input(self, text: str) -> str:
        """Sanitize input for security"""
        if not isinstance(text, str):
            return ""
        # Enhanced security: Remove more potential injection patterns
        text = re.sub(r'[;&|`$(){}[\]<>"\'\\
	]', '', text)
        return text[:2000].strip()
        
    def query_amazon_q(self, prompt: str) -> str:
        """Query Amazon Q CLI with security controls"""
        try:
            sanitized_prompt = self.sanitize_input(prompt)
            if not sanitized_prompt:
                return ""
                
            # Fixed: Use input parameter instead of command line argument to prevent injection
            result = subprocess.run(
                ['q', 'chat', '--no-input-file', '--'],
                input=sanitized_prompt,
                capture_output=True,
                text=True,
                timeout=30,
                cwd='/tmp'
            )
            return result.stdout.strip() if result.returncode == 0 else ""
        except Exception as e:
            print(f"Error querying Amazon Q: {e}")
            return ""
    
    def evaluate_mcq(self) -> Dict:
        """Evaluate Multiple Choice Questions"""
        print("Loading MCQ dataset...")
        try:
            dataset = load_dataset("Fsoft-AIC/MainframeBench", "multiple_choice_question")
            data = dataset['train'].select(range(min(self.sample_size, len(dataset['train']))))
        except Exception as e:
            print(f"Error loading MCQ dataset: {e}")
            return {'error': 'Failed to load MCQ dataset'}
        
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
                'question': example['question'][:100] + "..." if len(example['question']) > 100 else example['question'],
                'predicted': predicted,
                'correct': correct_answer,
                'is_correct': is_correct
            })
            
            time.sleep(1)
        
        accuracy = correct / total if total > 0 else 0
        return {
            'task': 'Multiple Choice Questions',
            'accuracy': accuracy,
            'correct': correct,
            'total': total,
            'sample_results': results[:5]  # Only show first 5 for security
        }
    
    def evaluate_qa(self) -> Dict:
        """Evaluate Question Answering"""
        print("Loading QA dataset...")
        try:
            dataset = load_dataset("Fsoft-AIC/MainframeBench", "question_answering")
            data = dataset['train'].select(range(min(self.sample_size, len(dataset['train']))))
        except Exception as e:
            print(f"Error loading QA dataset: {e}")
            return {'error': 'Failed to load QA dataset'}
        
        results = []
        quality_scores = []
        
        for i, example in enumerate(data):
            print(f"QA {i+1}/{len(data)}")
            
            question = example.get('question', '')
            reference_answer = example.get('answer', '')
            
            if not question or not reference_answer:
                continue
                
            prompt = f"""Question: {question}

Please provide a comprehensive answer based on mainframe and COBOL knowledge."""
            
            response = self.query_amazon_q(prompt)
            
            # Simple quality assessment
            quality_score = self.assess_qa_quality(response, reference_answer)
            quality_scores.append(quality_score)
            
            results.append({
                'question': question[:100] + "..." if len(question) > 100 else question,
                'reference_length': len(reference_answer.split()),
                'response_length': len(response.split()),
                'quality_score': quality_score
            })
            
            time.sleep(1)
        
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        return {
            'task': 'Question Answering',
            'total_samples': len(quality_scores),
            'average_quality_score': avg_quality,
            'sample_results': results[:5]
        }
    
    def assess_qa_quality(self, response: str, reference: str) -> float:
        """Simple quality assessment for QA responses"""
        if not response or not reference:
            return 0.0
        
        # Basic metrics: length similarity, keyword overlap
        response_words = set(response.lower().split())
        reference_words = set(reference.lower().split())
        
        if not reference_words:
            return 0.0
        
        overlap = len(response_words.intersection(reference_words))
        overlap_ratio = overlap / len(reference_words)
        
        # Length penalty/bonus
        length_ratio = min(len(response.split()) / len(reference.split()), 1.0)
        
        return (overlap_ratio * 0.7 + length_ratio * 0.3)
    
    def extract_mcq_answer(self, response: str) -> str:
        """Extract MCQ answer from response"""
        matches = re.findall(r'\b([ABCD])\b', response.upper())
        return matches[0] if matches else ""
    
    def run_complete_evaluation(self) -> Dict:
        """Run all three evaluation tasks"""
        print(f"Starting Complete COBOL Evaluation with Amazon Q CLI")
        print(f"Sample size: {self.sample_size} per task")
        print("="*60)
        
        # Run all evaluations
        mcq_results = self.evaluate_mcq()
        qa_results = self.evaluate_qa()
        bleu_results = self.bleu_evaluator.evaluate_code_summarization()
        
        # Calculate overall performance
        mcq_score = mcq_results.get('accuracy', 0) if 'error' not in mcq_results else 0
        qa_score = qa_results.get('average_quality_score', 0) if 'error' not in qa_results else 0
        bleu_score = bleu_results.get('primary_bleu', 0) if 'error' not in bleu_results else 0
        
        overall_score = (mcq_score + qa_score + bleu_score) / 3
        
        final_results = {
            'evaluation_info': {
                'model': 'Amazon Q CLI (Claude)',
                'sample_size_per_task': self.sample_size,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'evaluation_type': 'Complete MainframeBench Assessment'
            },
            'mcq_results': mcq_results,
            'qa_results': qa_results,
            'code_summarization_results': bleu_results,
            'overall_performance': {
                'composite_score': overall_score,
                'mcq_accuracy': mcq_score,
                'qa_quality': qa_score,
                'bleu_score': bleu_score
            }
        }
        
        return final_results
    
    def save_results(self, results: Dict, filename: str = "complete_cobol_evaluation_results.json"):
        """Save results securely"""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"Results saved to {filename}")

def main():
    """Run complete evaluation with security controls"""
    print("COMPLETE COBOL EVALUATION FRAMEWORK")
    print("=" * 60)
    
    evaluator = CompleteCOBOLEvaluator(sample_size=5)  # Small test first
    results = evaluator.run_complete_evaluation()
    evaluator.save_results(results)
    
    print("\n" + "="*60)
    print("COMPLETE EVALUATION SUMMARY")
    print("="*60)
    
    overall = results['overall_performance']
    print(f"Overall Score: {overall['composite_score']:.3f}")
    print(f"MCQ Accuracy: {overall['mcq_accuracy']:.3f}")
    print(f"QA Quality: {overall['qa_quality']:.3f}")
    print(f"BLEU Score: {overall['bleu_score']:.3f}")
    
    # Show individual task results
    if 'error' not in results['mcq_results']:
        mcq = results['mcq_results']
        print(f"\nMCQ: {mcq['correct']}/{mcq['total']} correct ({mcq['accuracy']:.2%})")
    
    if 'error' not in results['qa_results']:
        qa = results['qa_results']
        print(f"QA: {qa['total_samples']} samples, avg quality {qa['average_quality_score']:.3f}")
    
    if 'error' not in results['code_summarization_results']:
        bleu = results['code_summarization_results']
        print(f"Code Summarization: {bleu['total_samples']} samples, BLEU {bleu['primary_bleu']:.4f}")

if __name__ == "__main__":
    main()