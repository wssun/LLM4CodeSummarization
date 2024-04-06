import argparse
import csv
import json
import logging
import os
import re
import sys
import tokenize
from io import StringIO
import time

from util.remove_comments import remove_comments_and_docstrings
import openai
from numpy import mean
from model import GPT,StarChat,CodeLLAMA

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s -   %(message)s', datefmt='%m/%d/%Y %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def find_score(s):
    for i in range(0, len(s)):
        if s[i].isdigit():
            if i+2<len(s) and s[i+1] == '.' and s[i+2].isdigit():
                logger.info('score: '+ s[i:i+3])
                return float(s[i:i+3])
            else:
                logger.info('score: '+ s[i])
                return int(s[i])
    logger.error('ERROR: evaluate_all not returning a number')
    return 0


def evaluate_all(input, len_comments, model):
    prompt = "Here is a piece of code with corresponding comments. Please rate each comment on a scale from 1 to 5, where a higher score indicates better quality. A good comment should: 1) accurately summarize the function of the code; 2) be expressed naturally and concisely, without burdening the developer with reading; 3) help the developer understand the code quickly. Your answer should be in the format 'Comment 0/1/2/3/4: {your rating}'.\n"
    prompt = prompt + input

    message = model.ask(prompt)
    score = []
    for j in range(0, len_comments):
        p = message.find('Comment ' + (str)(j) + ':')
        if p!=-1:
            score.append(find_score(message[p+10:]))
        else:
            score.append(0)
            logger.error('ERROR: evaluate_all not finding' + 'Comment ' + (str)(j))
    return score


def evaluate(code, comments, file_path, cnt=0, model=None):
    mode = 'a'
    if cnt == 0:
        mode = 'w'
    with open(file_path, mode, encoding="utf-8", newline='') as f:
        writer = csv.writer(f)
        for i in range(0, len(code)):
            if i < cnt: continue
            input = 'Code:\n' + code[i] + '\n'
            for j in range(0, len(comments)):
                input = input + 'Comment ' + (str)(j) + ': ' + comments[j][i] + '\n'
            score=evaluate_all(input, len(comments) , model)
            writer.writerow(score)
            print(i)


def compare_human_eval_and_gpt_eval(language, eval_model='gpt-4',model=None):
    if language in ['what','why','done','usage','property']:
        lang='java'
    else:
        lang=language
    record_file = 'human_eval_record_{}.csv'.format(language)
    idxs = []
    with open(record_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        cnt = 0
        for line in reader:
            cnt = cnt + 1
            idxs.append(int(line[0]))

    comments = []
    code = []
    gold = []
    if language == 'c':
        with open('./{}.jsonl'.format(language), "r", encoding="utf-8") as f:
            cnt = 0
            for line in f:
                line = line.strip()
                js = json.loads(line)
                if cnt in idxs:
                    code.append(remove_comments_and_docstrings(source=js['function'], lang=lang))
                    comment = js['summary']
                    if comment.endswith('.'):
                        comment = comment[:-1]
                    comment = comment + ' .'
                    gold.append(comment)
                cnt = cnt + 1
    else:
        with open('./{}.jsonl'.format(language), "r", encoding="utf-8") as f:
            cnt = 0
            for line in f:
                line = line.strip()
                js = json.loads(line)
                if cnt in idxs:
                    code.append(remove_comments_and_docstrings(source=js['code'], lang=language))
                    gold.append(' '.join(js['docstring_tokens']))
                cnt = cnt + 1
    comments.append(gold)

    models = ['gpt-4', 'gpt-3.5', 'starchat', 'codellama']
    for llm in models:
        output = []
        with open('./{}/{}/0.1/1.0/few_shot_history_4.txt'.format(language, llm), "r", encoding="utf-8") as f:
            for line in f:
                idx, comment = line.strip().split('\t')
                if int(idx) in idxs:
                    output.append(comment)
        comments.append(output)

    evaluate(code=code, comments=comments, file_path=f'./RQ1/{language}_{eval_model}.csv',
                      cnt=0, model=model)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="codellama", type=str)
    parser.add_argument("--temperature", default=0.1, type=float)
    parser.add_argument("--openai_key", default='', type=str)
    parser.add_argument("--max_new_tokens", default=4096, type=int)
    parser.add_argument("--top_k", default=50, type=int)
    parser.add_argument("--top_p", default=1, type=float)
    parser.add_argument("--log_filename", default='log-eval-llms.txt', type=str)
    args = parser.parse_args()

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s -   %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)
    args.logger = logging.getLogger(__name__)
    fh = logging.FileHandler(args.log_filename)
    args.logger.addHandler(fh)

    MODEL_NAME_OR_PATH = {'gpt-4':'gpt-4-1106-preview',
                          'gpt-3.5':'gpt-3.5-turbo',
                          'starchat': '/home/xxx/llm/starchat',
                         'codellama':'/home/xxx/codellama/CodeLlama-7b-Instruct-hf'
                          }
    args.model_name_or_path = MODEL_NAME_OR_PATH[args.model]
    if args.model == 'gpt-4':
        model = GPT(args=args)
    elif args.model == 'gpt-3.5':
        model = GPT(args=args)
    elif args.model == 'starchat':
        model = StarChat(args=args)
    elif args.model == 'codellama':
        model = CodeLLAMA(args=args)
    else:
        print('Model not found!')
        sys.exit(1)

    for language in ['java', 'python', 'c']:
        compare_human_eval_and_gpt_eval(language=language, eval_model=args.model, model=model)
