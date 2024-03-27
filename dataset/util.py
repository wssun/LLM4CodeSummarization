import csv
import json
import re
import string
from collections import Counter
from io import StringIO
import tokenize
import random


def remove_comments_and_docstrings(source, lang):  #  support Python, Java, C, Ruby
    if lang in ['python']:
        """
        Returns "source" minus comments and docstrings.
        """
        io_obj = StringIO(source)
        out = ""
        prev_toktype = tokenize.INDENT
        last_lineno = -1
        last_col = 0
        for tok in tokenize.generate_tokens(io_obj.readline):
            token_type = tok[0]
            token_string = tok[1]
            start_line, start_col = tok[2]
            end_line, end_col = tok[3]
            ltext = tok[4]
            if start_line > last_lineno:
                last_col = 0
            if start_col > last_col:
                out += (" " * (start_col - last_col))
            # Remove comments:
            if token_type == tokenize.COMMENT:
                pass
            # This series of conditionals removes docstrings:
            elif token_type == tokenize.STRING:
                if prev_toktype != tokenize.INDENT:
                    # This is likely a docstring; double-check we're not inside an operator:
                    if prev_toktype != tokenize.NEWLINE:
                        if start_col > 0:
                            out += token_string
            else:
                out += token_string
            prev_toktype = token_type
            last_col = end_col
            last_lineno = end_line
        temp = []
        for x in out.split('\n'):
            if x.strip() != "":
                temp.append(x)
        return '\n'.join(temp)
    elif lang in ['ruby']:
        def replacer(match):
            s = match.group(0)
            if s.startswith('#') or s.startswith('=begin'):
                return " "  # note: a space and not an empty string
            else:
                return s

        pattern = re.compile(
            r'#.*?$|=begin.*?=end|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
            re.DOTALL | re.MULTILINE
        )
        temp = []
        for x in re.sub(pattern, replacer, source).split('\n'):
            if x.strip() != "":
                temp.append(x)
        return '\n'.join(temp)
    elif lang in ['erlang', 'prolog']:
        def replacer(match):
            s = match.group(0)
            if s.startswith('%'):
                return " "  # note: a space and not an empty string
            else:
                return s

        pattern = re.compile(r'%.*?$|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',re.DOTALL|re.MULTILINE)
        temp = []
        for x in re.sub(pattern, replacer, source).split('\n'):
            if x.strip() != "":
                temp.append(x)
        return '\n'.join(temp)
    elif lang in ['haskell']:
        def replacer(match):
            s = match.group(0)
            if s.startswith('--') or s.startswith('{-'):
                return " "  # note: a space and not an empty string
            else:
                return s

        pattern = re.compile(
            r'--.*?$|\{-.*?-}|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
            re.DOTALL | re.MULTILINE
        )
        temp = []
        for x in re.sub(pattern, replacer, source).split('\n'):
            if x.strip() != "":
                temp.append(x)
        return '\n'.join(temp)
    elif lang in ['php']:
        def replacer(match):
            s = match.group(0)
            if s.startswith('/'):
                return " "  # note: a space and not an empty string
            else:
                return s

        pattern = re.compile(
            r'#.*?$|//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
            re.DOTALL | re.MULTILINE
        )
        temp = []
        for x in re.sub(pattern, replacer, source).split('\n'):
            if x.strip() != "":
                temp.append(x)
        return '\n'.join(temp)

    elif lang in ['java', 'go', 'javascript', 'c']:
        def replacer(match):
            s = match.group(0)
            if s.startswith('/'):
                return " "  # note: a space and not an empty string
            else:
                return s

        pattern = re.compile(
            r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"',
            re.DOTALL | re.MULTILINE
        )
        temp = []
        for x in re.sub(pattern, replacer, source).split('\n'):
            if x.strip() != "":
                temp.append(x)
        return '\n'.join(temp)

    else:
        print('Unkown language!')
        return source


def tokenize(source):
    pattern = r'(\'(?:\\.|[^\\\'])*\s*\')|("(?:\\.|[^\\"])*\s*")|\s|(\d+\.+\d*)|([^\w])'
    parts = re.split(pattern, source)
    result = [part for part in parts if part is not None and part.strip()]
    return result


def get_jaccard_sim_set(a,b):  #传入什么形式取决于tokenize函数
    # 传入的是字符串数组，元素为单词
    unions = len(a.union(b))
    intersections = len(a.intersection(b))
    return 1.0 * intersections / unions

def get_jaccard_sim_multiset(a,b):  #传入什么形式取决于tokenize函数
    # 传入的是字符串数组，元素为单词
    unions = a | b
    len_unions = sum(unions.values())
    intersections = a & b
    len_intersections = sum(intersections.values())
    return 1.0 * len_intersections / len_unions


def remove_dupicate(datas, language):
    code = [remove_comments_and_docstrings(js['code'], language) for js in datas]
    code_tokens = [tokenize(c) for c in code]

    # check
    for i in range(0, 20):
        # print(datas[i]['original_string'])
        # print('-----------')
        # print(datas[i]['code'])
        # print('-----------')
        print(code[i])
        print('-----------')
        print(code_tokens[i])
        print('-----------')

    result = []
    for i in range(0,len(datas)):
        if len(code[i].split('\n')) <= 3: continue

        if len(code_tokens[i]) < 20:  # not duplicate
            result.append(i)
            continue

        ok = True
        for j in result:
            if len(code_tokens[j]) < 20: continue
            if get_jaccard_sim_set(set(code_tokens[i]),set(code_tokens[j])) > 0.8 and\
                    get_jaccard_sim_multiset(Counter(code_tokens[i]), Counter(code_tokens[j])) > 0.7:
                ok = False
                break
        if ok: result.append(i)

    new_datas = [datas[i] for i in result]
    return new_datas

def random_sample_and_remove_duplicate(data, language):
    data_len = 300
    num = [i for i in range(0, len(data))]
    print('Len(data) = {}'.format(len(num)))
    random_sample = random.sample(num, max(len(num),data_len+100))
    sample_data = [data[i] for i in random_sample]
    new_data = remove_dupicate(sample_data, language)
    print('After removing duplicates, len(data) = {}'.format(len(new_data)))
    new_data = new_data[:data_len]
    print('Final len(data) = {}'.format(len(new_data)))
    print('Note that some data may be discarded after write_dataset(), so the real dataset length may be less than {}.'.format(len(new_data)))
    if len(new_data) < data_len:
        print('ERROR: data length less than 200!')

    return new_data

def write_dataset(language, data):
    with open('{}.jsonl'.format(language), 'w', encoding='utf-8') as f:
        with open('{}.csv'.format(language), 'w', newline='', encoding='utf-8') as f1:
            writer = csv.writer(f1)
            writer.writerow(['Code', 'Comment'])
            for js in data:
                first_sentence = js['first_paragraph'].split('. ')[0]
                if first_sentence.endswith('.')==False:
                    first_sentence = first_sentence + '.'
                js['docstring_tokens'] = tokenize(first_sentence)
                if len(js['docstring_tokens']) <= 3:
                    continue
                if js['docstring_tokens'][0]=='@' and js['docstring_tokens'][1]=='doc':
                    js['docstring_tokens'] = js['docstring_tokens'][2:]

                if js['docstring_tokens'][0] == '%':
                    js['docstring_tokens'] = js['docstring_tokens'][1:]

                code = js['code']
                nl = ' '.join(js['docstring_tokens'])

                if nl.startswith('-----') or nl.startswith('= = = =')\
                    or nl.startswith('% % % %') or nl.startswith('- - - -')\
                    or nl.startswith('_____') or nl.startswith('% = = = =')\
                    or nl.startswith('% - - -') or nl.startswith('* * * * *')\
                    or '- >' in nl or ': -' in nl or nl.startswith('% % - -')\
                    or nl.startswith('TODO') or 'http' in nl:
                    continue

                f.write(json.dumps(js)+'\n')
                writer.writerow([code, nl])


def map_repos(repos):
    process_repo = [repo.replace('/', '-') for repo in repos]
    result = {}
    for i in range(0, len(repos)):
        result[process_repo[i]]=repos[i]
    print('REPO NAME MAP:')
    print(result)
    return result


def read_csv(file):
    with open(file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for line in reader:
            print(line[1])
            print('')

if __name__ == '__main__':
    repos = ['erlang/otp', 'ninenines/cowboy', 'apache/couchdb', 'vernemq/vernemq', 'happi/theBeamBook', 'processone/tsung', 'lfe/lfe', 'ChicagoBoss/ChicagoBoss', 'erlang/rebar3', 'clojerl/clojerl', 'leo-project/leofs', 'devinus/poolboy', 'zhongwencool/observer_cli', 'erlyaws/yaws', 'erlang-lager/lager', 'uwiger/gproc', 'aeternity/aeternity', 'hamler-lang/hamler', 'rvirding/luerl', 'nitrogen/nitrogen', 'rebar/rebar', 'gotthardp/lorawan-server', 'lasp-lang/lasp', 'proper-testing/proper', 'lasp-lang/partisan', 'ninenines/gun', 'AntidoteDB/antidote', 'eproxus/meck', 'zotonic/zotonic', 'tarcieri/reia', 'rustyio/sync', 'talentdeficit/jsx', 'erlware/relx', 'knutin/elli', 'kafka4beam/brod', 'wooga/eredis', 'hdima/erlport', 'inaka/erlang_guidelines']
    # map_repos(repos)

    # read_csv('prolog.csv')
    read_csv('result_dataset/haskell.csv')
    read_csv('result_dataset/erlang.csv')