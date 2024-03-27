# LLM4CodeSummarization
Code for 《Source Code Summarization in the Era of Large Language Models》

## Datasets

The datasets used in our experiments can be found here.

### Build Erlang, Haskell and Prolog Dataset

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

```
python evaluate.py
```


