import csv
import json
import logging
import os
import sys
import time

from util.remove_comments import remove_comments_and_docstrings
import openai
from numpy import mean

DEFAULT_SYSTEM_PROMPT = """\
You are a helpful, respectful and honest assistant with a deep knowledge of code and software design. Always answer as helpfully as possible, while being safe. Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. Please ensure that your responses are socially unbiased and positive in nature.\n\nIf a question does not make any sense, or is not factually coherent, explain why instead of answering something not correct. If you don't know the answer to a question, please don't share false information.\
"""

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s -   %(message)s', datefmt='%m/%d/%Y %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

openai.api_key = ""

def ask(prompt):
    logger.info('prompt:\n'+prompt)
    response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",
        # model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )
    message = response['choices'][0]['message']['content']
    time.sleep(1)

    logger.info('response:\n'+message)
    return message


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


def evaluate_all(input, len_comments):
    prompt = "Here is a piece of code with corresponding comments. Please rate each comment on a scale from 1 to 5, where a higher score indicates better quality. A good comment should: 1) accurately summarize the function of the code; 2) be expressed naturally and concisely, without burdening the developer with reading; 3) help the developer understand the code quickly. Your answer should be in the format 'Comment 0/1/2/3/4: {your rating}'.\n"
    prompt = prompt + input

    message = ask(prompt)
    score = []
    for j in range(0, len_comments):
        p = message.find('Comment ' + (str)(j) + ':')
        if p!=-1:
            score.append(find_score(message[p+10:]))
        else:
            score.append(0)
            logger.error('ERROR: evaluate_all not finding' + 'Comment ' + (str)(j))
    return score


def evaluate(code, comments, file_path, cnt=0):
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
            score=evaluate_all(input, len(comments))
            writer.writerow(score)
            print(i)


def compare_human_eval_and_gpt_eval():
    language = 'c'
    LLM = 'gpt-4'
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
        with open('..\\dataset\\{}.jsonl'.format(language), "r", encoding="utf-8") as f:
            cnt = 0
            for line in f:
                line = line.strip()
                js = json.loads(line)
                if cnt in idxs:
                    code.append(js['function'])
                    comment = js['summary']
                    if comment.endswith('.'):
                        comment = comment[:-1]
                    comment = comment + ' .'
                    gold.append(comment)
                cnt = cnt + 1
    else:
        with open('..\\dataset\\{}.jsonl'.format(language), "r", encoding="utf-8") as f:
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
    for model in models:
        output = []
        with open('D:\llm_checkpoint\codesum\{}\{}\\0.1\\few_shot_history_4.txt'.format(language, model), "r", encoding="utf-8") as f:
            for line in f:
                idx, comment = line.strip().split('\t')
                if int(idx) in idxs:
                    output.append(comment)
        comments.append(output)

    evaluate(code, comments, f'.\\user_result\\{language}_{LLM}.csv',0)


def gpt_eval(directory, language, technique, temperature, cnt=0, baseline=False, top_p=1.0):
    dir_eval=directory+'llm-eval\\'
    dir_result=directory+'codesum\\'
    if language in ['what','why','done','usage','property']:
        lang='java'
    else:
        lang=language
    log_file_path = dir_eval+f'log-{language}-{temperature}-{top_p}-{technique}.txt'
    fh = logging.FileHandler(log_file_path)
    logger.addHandler(fh)

    code = []
    comments = []
    gold = []
    if language == 'c':
        with open('..\\dataset\\{}.jsonl'.format(language), "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                js = json.loads(line)
                code.append(remove_comments_and_docstrings(source=js['function'], lang=lang))
                comment = js['summary']
                if comment.endswith('.'):
                    comment = comment[:-1]
                comment = comment + ' .'
                gold.append(comment)
    else:
        with open('..\\dataset\\{}.jsonl'.format(language), "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                js = json.loads(line)
                code.append(remove_comments_and_docstrings(source=js['code'], lang=lang))
                gold.append(' '.join(js['docstring_tokens']))
    comments.append(gold)

    if baseline:
        models = ['gpt-4', 'gpt-3.5', 'starchat', 'codellama', 'codet5']
    else:
        models = ['gpt-4', 'gpt-3.5', 'starchat', 'codellama']
        # models = ['codellama', 'starchat', 'gpt-3.5', 'gpt-4']

    for model in models:
        path = dir_result+f'{language}\{model}\{temperature}\{top_p}\{technique}.txt'
        print('load '+ path)
        output = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                idx, comment = line.strip().split('\t')
                output.append(comment)
        if len(gold) != len(output):
            print('Output file miss samples:')
            print(path)
            sys.exit(1)
        comments.append(output)

    start_time = time.time()

    dir = dir_eval+f'{language}\{temperature}\{top_p}'
    if os.path.exists(dir)==False:
        os.makedirs(dir)
    evaluate(code, comments, '{0}\{1}.csv'.format(dir,technique), cnt)

    end_time = time.time()

    cost_time = end_time - start_time
    ss = cost_time % 60
    cost_time = cost_time // 60
    mm = cost_time % 60
    cost_time = cost_time // 60
    hh = cost_time
    logger.info("Evaluate Time: %d h %d m %d s", hh, mm, ss)


if __name__ == '__main__':
    # compare_human_eval_and_gpt_eval()

    # RQ2
    gpt_eval(directory='D:\llm_checkpoint\\', language='c', technique='zero_shot', temperature='0.1', cnt=0, baseline=True, top_p=1.0)

    for language in [
        # 'java',
        # 'python',
        # 'c'
    ]:
        for techique in [
            # 'chain_of_thought',
            # 'critique',
            # 'expert_history',
            # 'few_shot_history_4'
        ]:
            gpt_eval(directory='D:\llm_checkpoint\\', language=language,technique=techique,temperature='0.1', cnt=0, baseline=False, top_p=1.0)


    # RQ3
    cur_p = 'Not Start'
    cur_t = 'Not Start'
    cur_language = 'Not Start'
    try:
        for language in [
            # 'java',
            # 'python',
            'c'
        ]:
            for temperature in [
                # 0.1,
                # 0.5,
                1.0
            ]:
                for top_p in [
                    0.5,
                    # 0.75
                ]:
                    print('Language: ', language, ' Temperature: ', temperature, ' Top_p: ', top_p)
                    cur_p = top_p
                    cur_t = temperature
                    cur_language = language
                    gpt_eval(directory='D:\llm_checkpoint\\', language=language, technique='few_shot_history_4', temperature=temperature, cnt=0, baseline=False, top_p=top_p)
    except Exception as e:
        print(e)
        print('Stop at Language: ', cur_language, ' Temperature: ', cur_t, ' Top_p: ', cur_p)


    # RQ4
    for language in [
        # 'ruby',
        # 'javascript',
        # 'go',
        # 'php',
        # 'erlang',
        # 'haskell',
        # 'prolog'
    ]:
        gpt_eval(directory='D:\llm_checkpoint\\', language=language, technique='few_shot_history_4', temperature='0.1', cnt=0, baseline=False, top_p=1.0)


    # RQ5
    for language in [
        # 'what',
        # 'why',
        # 'done',
        # 'usage',
        # 'property'
    ]:
        gpt_eval(directory='D:\llm_checkpoint\\', language=language, technique='few_shot_history_4', temperature='0.1', cnt=0, baseline=False, top_p=1.0)