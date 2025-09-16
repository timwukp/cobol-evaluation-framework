#!/usr/bin/env python3
"""
Simple COBOL Evaluation - Manual testing approach

DISCLAIMER: This software is provided "AS IS" for research purposes only.
Users assume all risks. Not intended for production use without proper validation.
See DISCLAIMER.md for complete legal terms.
"""
from datasets import load_dataset
import json

def load_sample_questions():
    """Load sample questions from MainframeBench"""
    
    # MCQ samples
    mcq_dataset = load_dataset("Fsoft-AIC/MainframeBench", "multiple_choice_question")
    mcq_samples = mcq_dataset['train'].select(range(5))
    
    # QA samples  
    qa_dataset = load_dataset("Fsoft-AIC/MainframeBench", "question_answering")
    qa_samples = qa_dataset['train'].select(range(5))
    
    # Code summarization samples
    code_dataset = load_dataset("Fsoft-AIC/MainframeBench", "COBOL_code_summarization")
    code_samples = code_dataset['train'].select(range(5))
    
    return mcq_samples, qa_samples, code_samples

def create_test_prompts():
    """Create test prompts for manual evaluation"""
    mcq_samples, qa_samples, code_samples = load_sample_questions()
    
    test_data = {
        "mcq_tests": [],
        "qa_tests": [],
        "code_tests": []
    }
    
    # MCQ tests
    for i, example in enumerate(mcq_samples):
        test_data["mcq_tests"].append({
            "id": i+1,
            "question": example['question'],
            "options": {
                "A": example['A'],
                "B": example['B'], 
                "C": example['C'],
                "D": example['D']
            },
            "correct_answer": example['answer'],
            "prompt": f"""Question: {example['question']}

A) {example['A']}
B) {example['B']}
C) {example['C']}
D) {example['D']}

Please answer with just the letter (A, B, C, or D)."""
        })
    
    # QA tests
    for i, example in enumerate(qa_samples):
        test_data["qa_tests"].append({
            "id": i+1,
            "question": example['question'],
            "reference_answer": example['answer'],
            "prompt": f"Question: {example['question']}\n\nPlease provide a clear and concise answer."
        })
    
    # Code summarization tests
    for i, example in enumerate(code_samples):
        test_data["code_tests"].append({
            "id": i+1,
            "source_code": example['source'],
            "reference_summary": example['summary'],
            "prompt": f"""Please summarize the following COBOL code:

{example['source']}

Provide a clear, brief summary of what this code does."""
        })
    
    return test_data

def main():
    print("Creating COBOL evaluation test cases...")
    test_data = create_test_prompts()
    
    # Save test cases
    with open('cobol_test_cases.json', 'w') as f:
        json.dump(test_data, f, indent=2)
    
    print("Test cases saved to cobol_test_cases.json")
    print("\n" + "="*60)
    print("COBOL EVALUATION FRAMEWORK SUMMARY")
    print("="*60)
    print(f"Multiple Choice Questions: {len(test_data['mcq_tests'])}")
    print(f"Question Answering: {len(test_data['qa_tests'])}")
    print(f"Code Summarization: {len(test_data['code_tests'])}")
    
    print("\n" + "="*60)
    print("SAMPLE MCQ TEST:")
    print("="*60)
    sample_mcq = test_data['mcq_tests'][0]
    print(f"Question: {sample_mcq['question']}")
    print(f"A) {sample_mcq['options']['A']}")
    print(f"B) {sample_mcq['options']['B']}")
    print(f"C) {sample_mcq['options']['C']}")
    print(f"D) {sample_mcq['options']['D']}")
    print(f"Correct Answer: {sample_mcq['correct_answer']}")

if __name__ == "__main__":
    main()