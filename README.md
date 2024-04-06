# LLM4CodeSummarization
Code for 《Source Code Summarization in the Era of Large Language Models》

## Environment
Our experiment runs with Python 3.7 and Pytorch 1.6.0.

Other packages required can be installed with ```pip install -r requirements.txt```.

## Datasets

The datasets used in our experiments can be found [here](https://drive.google.com/drive/folders/1ge5S6pmQLdE2-zCNsg9WCZ1PNXMRpDI5?usp=sharing), including human evaluation datasets.

### Build Erlang, Haskell and Prolog Dataset
Code for building Erlang, Haskell and Prolog Dataset is in the dataset directory.
```
cd ./dataset
```

1. Crawl data from Github
```
python crawl.py
```

2. Extract <function, summary> pairs
```
python erlang.py
python haskell.py
python prolog.py
```

## Use LLMs for Code Summarization
1. Calling LLMs to generate comments
```
python run.py
```

2. Extract comments from LLMs' response
```
python beautify.py
```

## Evaluate with LLMs

1. Evaluate with GPT-4 (used for RQ2-RQ5)
```
python evaluate.py
```

2. Evaluate with LLMs on the human evaluation dataset (used for RQ1). File ```human_eval_record_{language}.csv``` can be found [here](https://drive.google.com/drive/folders/1pu4V7q7YZxvorf_xa6ha2GlkbDDv72wb?usp=sharing).
```
python llm-eval.py
```

## Results
We upload the results in our experiment [here](https://drive.google.com/drive/folders/1SJFyc40hJL0QJ9Rl3u8QYFfac7-bQT7w?usp=sharing), in which:

1. ```codesum``` directory contains LLMs' response (```.csv```) and the comment (```.txt```) extracted from the response

2. ```gpt-eval``` directory contains GPT-4's evaluation scores in RQ2-RQ5

3. ```RQ1``` directory contains evaluation scores of each metric in RQ1

## Figures
The directory ```./figures``` contrains examples of five prompting techniques (zero-shot, few-shot, chain-of-thought, critique, expert)
, which are not presented in the paper due to page limit.
