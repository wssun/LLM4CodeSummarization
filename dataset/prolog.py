import csv
import json
import os
import sys
import zipfile

from util import tokenize, random_sample_and_remove_duplicate, write_dataset, map_repos

sys.setrecursionlimit(1000)

repos = ['LogtalkDotOrg/logtalk3', 'LPCIC/elpi', 'c-cube/datalog', 'ciao-lang/ciao', 'gooofy/zamia-ai', 'fnogatz/xsd2json', 'kovvalsky/LangPro', 'evoldoers/biomake', 'aarroyoc/postgresql-prolog', 'wouterbeek/prolog_library_collection', 'jamesnvc/lsp_server', 'aartikis/RTEC', 'khueue/prolongo', 'jan-Lope/Toki_Pona-Parser', 'mndrix/microkanren-prolog', 'Anniepoo/weblog', 'ridgeworks/clpBNR', 'Mortimerp9/Prolog-Graphplan', 'jamespwilliams/prolog-isolation-checker', 'maths/PRESS', 'exercism/prolog']
repo_name = map_repos(repos)

# 提取注释
def process_comment(lines, p, q):
    docstring_line = []  # 带有参数注释
    first_paragraph_line = [] # 没有参数注释
    for i in range(p,q):
        line = lines[i]
        if line.startswith('%!') is False:  # 不是参数注释
            first_paragraph_line.append(line[1:].strip())
            docstring_line.append(line[1:])
        else:
            docstring_line.append(line[2:])

    return ''.join(docstring_line), ' '.join([f.strip() for f in first_paragraph_line if f.strip()])

# 提取代码
def process_code(lines, q, r):
    return '\n'.join(lines[q:r])


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
                if lines[p].startswith('%'):  # potential data
                    # 提取注释
                    # print('p: ',p)
                    q = p
                    while (q<len(lines)):  # 循环找到注释最后一行
                        if lines[q].startswith('%'):
                            q = q + 1
                        else:
                            break
                    # print('q: ', q)
                    if q + 1 >= len(lines):  # 只有注释，后面没有代码
                        p = q + 1
                    else:  # 注释后面有内容
                        x = lines[q + 1]
                        if lines[q+1][0].isspace() == False and lines[q+1].endswith(':-\n'): # 只考虑docstring和code紧邻的情况
                            r = q + 2
                            while (r<len(lines)):
                                # print('lines[r]:', lines[r])
                                if len(lines[r]) == 0 or lines[r][0].isspace():
                                    r = r + 1
                                else:  #第r行是新的potential data
                                    break
                            # print('r:', r)
                            if r - q - 1 > 3: # 代码有可能超过3行, lines[p:q]是注释，lines[q+1:r]是代码
                                docstring, first_paragraph = process_comment(lines, p, q)
                                code = process_code(lines, q + 1, r)
                                func_name = code.split(':')[0].split('(')[0].strip()
                                if len(code.split('\n')) > 3 and len(first_paragraph.split())>3 and 'test' not in func_name: # code超过3行, comment超过三个单词，函数名中不包含test
                                    original_string = '\n'.join(lines[p:r])
                                    new_url = url + '#L' + str(p+1) + '-L' + str(r)
                                    data = {'repo': repo, 'path': path, 'original_string': original_string, 'code': code,
                                            'docstring': docstring, 'first_paragraph': first_paragraph, 'url': new_url}
                                    datas.append(data)
                            p = r
                        else:
                            p = q + 1
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
            if file_path.endswith('.pl'):
                data = process_file(file_path)
                if len(data)!=0:
                    datas.extend(data)

    write_dataset('prolog-original', datas)
    datas = random_sample_and_remove_duplicate(datas, 'prolog')
    write_dataset('prolog', datas)

def extract_file():
    zip_dir = 'crawl\\Prolog'
    unzip_dir = 'dataset\\Prolog'
    for root, dirs, files in os.walk(zip_dir):
        for file in files:
            file_path = os.path.join(root, file)
            print('file: ', file_path)
            f = zipfile.ZipFile(file_path, 'r')  # 压缩文件位置
            for file in f.namelist():
                try:
                    f.extract(file, unzip_dir)  # 解压位置
                except Exception as e :
                    print(file)
                    print(e)

            f.close()


if __name__ == '__main__':
    extract_file()
    process_directory('dataset\\Prolog')





