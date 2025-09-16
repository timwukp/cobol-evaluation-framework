#!/usr/bin/env python3
"""
Full MainframeBench dataset processor

DISCLAIMER: This software is provided "AS IS" for research purposes only.
Users assume all risks. Not intended for production use without proper validation.
See DISCLAIMER.md for complete legal terms.
"""
import json
from datasets import load_dataset

def create_full_test_suite():
    """Create complete test suite from MainframeBench"""
    
    configs = ['multiple_choice_question', 'question_answering', 'COBOL_code_summarization']
    full_suite = {}
    
    for config in configs:
        print(f"Loading {config}...")
        dataset = load_dataset("Fsoft-AIC/MainframeBench", config)
        train_data = dataset['train']
        
        tests = []
        for i, example in enumerate(train_data):
            if config == 'multiple_choice_question':
                test = {
                    'id': i,
                    'question': example['question'],
                    'options': {'A': example['A'], 'B': example['B'], 'C': example['C'], 'D': example['D']},
                    'correct': example['answer'],
                    'prompt': f"{example['question']}\nA) {example['A']}\nB) {example['B']}\nC) {example['C']}\nD) {example['D']}\nAnswer:"
                }
            elif config == 'question_answering':
                test = {
                    'id': i,
                    'question': example['question'],
                    'reference': example['answer'],
                    'prompt': example['question']
                }
            else:  # code_summarization
                test = {
                    'id': i,
                    'code': example['source'],
                    'reference': example['summary'],
                    'prompt': f"Summarize this COBOL code:\n{example['source']}"
                }
            tests.append(test)
        
        full_suite[config] = {
            'count': len(tests),
            'tests': tests
        }
        print(f"Loaded {len(tests)} {config} tests")
    
    return full_suite

def save_test_suite(suite):
    """Save test suite to files"""
    for config, data in suite.items():
        filename = f"data/full_{config}_tests.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"Saved {data['count']} tests to {filename}")

def main():
    print("Creating full MainframeBench test suite...")
    print("Dataset sizes:")
    print("- Multiple Choice: 1,931 questions")
    print("- Question Answering: 2,598 questions") 
    print("- Code Summarization: 2,523 examples")
    print("- Total: 7,052 test cases")
    print()
    
    suite = create_full_test_suite()
    save_test_suite(suite)
    
    print("\nFull test suite created!")
    print("Files generated:")
    for config in suite.keys():
        print(f"- data/full_{config}_tests.json ({suite[config]['count']} tests)")
    
    print(f"\nTotal test cases: {sum(data['count'] for data in suite.values())}")
    print("\nTo run evaluation, use these files with Amazon Q CLI")

if __name__ == "__main__":
    main()