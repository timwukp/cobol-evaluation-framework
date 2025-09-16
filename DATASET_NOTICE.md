# 📊 MainframeBench Dataset Notice

## Large Test Dataset Files

Due to GitHub file size limitations, the complete MainframeBench test datasets are not included in this repository. These files contain the full 7,052 test cases:

### Missing Large Files:
- `data/full_multiple_choice_question_tests.json` (1,931 tests, ~970KB)
- `data/full_question_answering_tests.json` (2,598 tests, ~1.1MB)  
- `data/full_COBOL_code_summarization_tests.json` (2,523 tests, ~6MB)

## How to Generate the Dataset

To recreate the complete test datasets locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Generate complete test datasets
python src/full_eval.py
```

This will download and process the complete MainframeBench dataset from HuggingFace:
- https://huggingface.co/datasets/Fsoft-AIC/MainframeBench

## Alternative: Use Sample Data

For quick testing, use the included sample data:
- `cobol_test_cases.json` - 5 sample tests per category
- Run: `python src/simple_cobol_eval.py`

## Complete Evaluation Results

The evaluation results for the full 7,052 test dataset are included:
- `data/complete_mainframebench_results.json` - 78% overall performance
- `data/substantial_eval_results.json` - 300 test sample results

## Dataset Source

Original dataset: [Fsoft-AIC/MainframeBench](https://huggingface.co/datasets/Fsoft-AIC/MainframeBench)  
Paper: [XMainframe: A Large Language Model for Mainframe Modernization](https://arxiv.org/pdf/2408.04660)