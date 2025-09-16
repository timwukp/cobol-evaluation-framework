# 📊 MainframeBench Dataset Notice

## Large Test Dataset Files

Due to GitHub file size limitations, the complete MainframeBench test datasets are not included in this repository. These files contain the full 7,052 test cases:

### Missing Large Files:
- `data/full_multiple_choice_question_tests.json` (1,931 tests, ~970KB)
- `data/full_question_answering_tests.json` (2,598 tests, ~1.1MB)  
- `data/full_COBOL_code_summarization_tests.json` (2,523 tests, ~6MB)

## 🚀 Quick Solution: Download from HuggingFace

**The missing data can be downloaded directly from:**
**https://huggingface.co/datasets/Fsoft-AIC/MainframeBench**

The dataset contains three configurations:
- `multiple_choice_question` (1,931 tests)
- `question_answering` (2,598 tests)
- `COBOL_code_summarization` (2,523 tests)

## How to Generate the Dataset Locally

To recreate the complete test datasets:

```bash
# Install dependencies
pip install -r requirements.txt

# Generate complete test datasets from HuggingFace
python src/full_eval.py
```

This will automatically download and process the complete MainframeBench dataset from:
https://huggingface.co/datasets/Fsoft-AIC/MainframeBench

## Alternative: Use Sample Data

For quick testing without downloading the full dataset:
- `cobol_test_cases.json` - 5 sample tests per category
- Run: `python src/simple_cobol_eval.py`

## Complete Evaluation Results

The evaluation results for the full 7,052 test dataset are already included:
- `data/complete_mainframebench_results.json` - **78% overall performance**
- `data/substantial_eval_results.json` - 300 test sample results

## Dataset Source & Paper

- **Dataset**: [Fsoft-AIC/MainframeBench](https://huggingface.co/datasets/Fsoft-AIC/MainframeBench)  
- **Paper**: [XMainframe: A Large Language Model for Mainframe Modernization](https://arxiv.org/pdf/2408.04660)

**Note**: The evaluation framework is fully functional - the missing files are just the raw test data that can be easily downloaded from HuggingFace.