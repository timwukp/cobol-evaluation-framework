#!/usr/bin/env python3
import json
import subprocess
import time
import re

def query_q_cli(prompt):
    try:
        result = subprocess.run(['q', 'chat', '--no-input-file', prompt], 
                              capture_output=True, text=True, timeout=30)
        return result.stdout.strip() if result.returncode == 0 else ""
    except:
        return ""

def extract_mcq_answer(response):
    matches = re.findall(r'\b([ABCD])\b', response.upper())
    return matches[0] if matches else ""

def run_substantial_eval():
    # Load datasets
    with open('data/full_multiple_choice_question_tests.json') as f:
        mcq_data = json.load(f)
    with open('data/full_question_answering_tests.json') as f:
        qa_data = json.load(f)
    with open('data/full_COBOL_code_summarization_tests.json') as f:
        code_data = json.load(f)
    
    # Test substantial samples
    sample_size = 100  # 100 from each category
    
    print(f"Running substantial evaluation:")
    print(f"- MCQ: {sample_size}/{mcq_data['count']}")
    print(f"- QA: {sample_size}/{qa_data['count']}")
    print(f"- Code: {sample_size}/{code_data['count']}")
    print(f"Total: {sample_size * 3} tests")
    
    results = {'mcq': [], 'qa': [], 'code': []}
    
    # MCQ evaluation
    print("\n=== MCQ Evaluation ===")
    mcq_correct = 0
    for i in range(sample_size):
        test = mcq_data['tests'][i]
        print(f"MCQ {i+1}/{sample_size}")
        
        response = query_q_cli(test['prompt'])
        predicted = extract_mcq_answer(response)
        is_correct = predicted == test['correct']
        
        if is_correct:
            mcq_correct += 1
            
        results['mcq'].append({
            'id': i,
            'question': test['question'][:100] + '...',
            'predicted': predicted,
            'correct': test['correct'],
            'is_correct': is_correct
        })
        time.sleep(1)
    
    # QA evaluation
    print(f"\n=== QA Evaluation ===")
    for i in range(sample_size):
        test = qa_data['tests'][i]
        print(f"QA {i+1}/{sample_size}")
        
        response = query_q_cli(test['prompt'])
        results['qa'].append({
            'id': i,
            'question': test['question'][:100] + '...',
            'predicted': response[:200] + '...' if len(response) > 200 else response,
            'reference': test['reference'][:200] + '...'
        })
        time.sleep(1)
    
    # Code evaluation
    print(f"\n=== Code Evaluation ===")
    for i in range(sample_size):
        test = code_data['tests'][i]
        print(f"Code {i+1}/{sample_size}")
        
        response = query_q_cli(test['prompt'])
        results['code'].append({
            'id': i,
            'predicted': response[:200] + '...' if len(response) > 200 else response,
            'reference': test['reference'][:200] + '...'
        })
        time.sleep(1)
    
    # Calculate final results
    mcq_accuracy = mcq_correct / sample_size
    
    final_results = {
        'evaluation_summary': {
            'sample_size_per_task': sample_size,
            'total_tests': sample_size * 3,
            'mcq_accuracy': mcq_accuracy,
            'mcq_correct': mcq_correct
        },
        'detailed_results': results
    }
    
    with open('data/substantial_eval_results.json', 'w') as f:
        json.dump(final_results, f, indent=2)
    
    print(f"\n=== RESULTS ===")
    print(f"MCQ Accuracy: {mcq_accuracy:.2%} ({mcq_correct}/{sample_size})")
    print(f"QA Tests: {len(results['qa'])}")
    print(f"Code Tests: {len(results['code'])}")
    print(f"Results saved to substantial_eval_results.json")

if __name__ == "__main__":
    run_substantial_eval()