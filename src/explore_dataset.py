#!/usr/bin/env python3
"""
Explore the MainframeBench dataset structure

DISCLAIMER: This software is provided "AS IS" for research purposes only.
Users assume all risks. Not intended for production use without proper validation.
See DISCLAIMER.md for complete legal terms.
"""
from datasets import load_dataset
import json

def explore_mainframebench():
    configs = ['question_answering', 'multiple_choice_question', 'COBOL_code_summarization']
    
    for config in configs:
        print(f"\n{'='*50}")
        print(f"CONFIG: {config}")
        print('='*50)
        
        dataset = load_dataset("Fsoft-AIC/MainframeBench", config)
        
        for split_name, split_data in dataset.items():
            print(f"\n--- {split_name} split ---")
            print(f"Examples: {len(split_data)}")
            
            if len(split_data) > 0:
                first = split_data[0]
                print(f"Keys: {list(first.keys())}")
                for k, v in first.items():
                    print(f"  {k}: {str(v)[:150]}{'...' if len(str(v)) > 150 else ''}")
                print()

if __name__ == "__main__":
    explore_mainframebench()