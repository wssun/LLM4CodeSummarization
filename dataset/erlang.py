import csv
import json
import os
import sys
import zipfile

from util import tokenize, random_sample_and_remove_duplicate, write_dataset, map_repos

sys.setrecursionlimit(1000)

repos = ['erlang/otp', 'ninenines/cowboy', 'apache/couchdb', 'vernemq/vernemq', 'happi/theBeamBook', 'processone/tsung', 'lfe/lfe', 'ChicagoBoss/ChicagoBoss', 'erlang/rebar3', 'clojerl/clojerl', 'leo-project/leofs', 'devinus/poolboy', 'zhongwencool/observer_cli', 'erlyaws/yaws', 'erlang-lager/lager', 'uwiger/gproc', 'aeternity/aeternity', 'hamler-lang/hamler', 'rvirding/luerl', 'nitrogen/nitrogen', 'rebar/rebar', 'gotthardp/lorawan-server', 'lasp-lang/lasp', 'proper-testing/proper', 'lasp-lang/partisan', 'ninenines/gun', 'AntidoteDB/antidote', 'eproxus/meck', 'zotonic/zotonic', 'tarcieri/reia', 'rustyio/sync', 'talentdeficit/jsx', 'erlware/relx', 'knutin/elli', 'kafka4beam/brod', 'wooga/eredis', 'hdima/erlport', 'inaka/erlang_guidelines']
repo_name = map_repos(repos)

# 提取注释
def process_comment(lines, p, q):
    docstring_line = []  # 带有参数注释
    first_paragraph_line = [] # 没有参数注释
    flg = False # 当前行是对于参数的注释
    for i in range(p,q):
        line = lines[i]
        if len(line[2:].strip())==0:
            flg = True
        docstring_line.append(line[2:])
        if flg is False:
            first_paragraph_line.append(line[2:].strip())
    return ''.join(docstring_line), ' '.join([f.strip() for f in first_paragraph_line if f.strip()])

# 提取代码
def process_code(lines, q, r, func_name):
    i = q
    while i < r:
        if lines[i].startswith(func_name) and lines[i].strip().endswith('->'):
            # lines[i]是顶格代码
            j = i + 1
            while j < r:
                if lines[j].strip().endswith('.'):
                    j = j + 1
                    break
                elif lines[j].startswith(func_name):  # 递归函数定义
                    return ''
                else:
                    j = j + 1
            # print('j:', j)
            if j-i > 3: # 真正的code: lines[i:j]
                return '\n'.join(lines[i:j])
            else:
                return ''

        i = i + 1

    return ''


def process_file(file_path):
    path_tokens = file_path.split('\\')
    repo = repo_name['-'.join(path_tokens[2].split('-')[:-1])]
    path = '/'.join(path_tokens[3:])
    url = 'https://github.com/' + repo + '/blob/master/' + path
    datas = []

    try:
        with open(file_path, "r", encoding='utf-8') as f:
            lines = f.readlines()

            p = 0 # 指向original string的开始
            while(p<len(lines)):
                if lines[p].startswith('%%'):  # potential data
                    # 提取注释
                    # print('p: ',p)
                    q = p
                    while (q<len(lines)):  # 循环找到注释最后一行
                        if lines[q].startswith('%%'):
                            q = q + 1
                        else:
                            break
                    # print('q: ', q)
                    if q == len(lines):  # 只有注释，后面没有代码
                        p = q
                    else:  # 注释后面有内容
                        if lines[q][0].isspace() == False: # 只考虑docstring和code紧邻的情况
                            r = q
                            if lines[q].startswith('-spec '):
                                r = r + 1
                                new_line = lines[q][6:]
                                func_name = new_line.split('(')[0]
                            else:
                                func_name = lines[q].split('(')[0]

                            while (r<len(lines)):
                                # print('lines[r]:', lines[r])
                                if len(lines[r]) == 0 or lines[r].startswith(func_name) or lines[r][0].isspace():
                                    r = r + 1
                                else:  #第r行是新的potential data
                                    break
                            # print('r:', r)
                            if r - q > 3: # 代码有可能超过3行, lines[p:q]是注释，lines[q:r]是代码
                                docstring, first_paragraph = process_comment(lines, p, q)
                                code = process_code(lines, q, r, func_name)
                                if len(code.split('\n')) > 3 and len(first_paragraph.split()) > 3 and 'test' not in func_name and '- >' not in first_paragraph: # code超过3行, comment超过三个单词，函数名中不包含test
                                    original_string = '\n'.join(lines[p:r])
                                    new_url = url + '#L' + str(p+1) + '-L' + str(r)
                                    data = {'repo': repo, 'path': path, 'original_string': original_string, 'code': code,
                                            'docstring': docstring, 'first_paragraph': first_paragraph, 'url': new_url}
                                    datas.append(data)
                            p = r
                        else:
                            p = q
                else:  # not potential data
                    p = p + 1
    except Exception as e :
        print(file_path)
        print(e)

    return datas

def process_directory(dir_path):
    print(dir_path)
    datas = []
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            file_path = os.path.join(root, file)
            if file_path.endswith('.erl'):
                # print('当前文件：', file_path)
                data = process_file(file_path)
                if len(data) != 0:
                    datas.extend(data)

    write_dataset('erlang-original', datas)
    datas = random_sample_and_remove_duplicate(datas, 'erlang')
    write_dataset('erlang', datas)


def extract_file():
    zip_dir = 'crawl\\Erlang'
    unzip_dir = 'dataset\\Erlang'
    for root, dirs, files in os.walk(zip_dir):
        for file in files:
            file_path = os.path.join(root, file)
            print('file: ',file_path)
            f = zipfile.ZipFile(file_path, 'r')  # 压缩文件位置
            for file in f.namelist():
                f.extract(file, unzip_dir)  # 解压位置
            f.close()


if __name__ == '__main__':
    extract_file()
    process_directory('dataset\\Erlang')





