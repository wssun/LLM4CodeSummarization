import csv

def write_groundtruth(DIR,LANGUAGE):
    input_file = DIR+LANGUAGE+'\\groundtruth.csv'
    output_file = DIR+LANGUAGE+'\\groundtruth.txt'
    with open(input_file, 'r', encoding='utf-8') as f:  # somtimes encoding='unicode_escape', somtimes encoding='unicode_escape'
        reader = csv.reader(f)
        with open(output_file, 'w', encoding='utf-8') as f1:
            for line in reader:
                idx = line[0]
                comment = line[1]
                f1.write(idx+'\t'+comment+'\n')


def beautify(DIR='D:\llm_checkpoint\codesum\\',LANGUAGE='java', TEMPERATURE='0.1', PROMPT='few_shot_history_4', MODEL='gpt-4', TOP_P='1.0'):
    prefix = DIR+'\\'+LANGUAGE+'\\'+MODEL+'\\'+TEMPERATURE+'\\'+TOP_P+'\\'
    print(prefix)

    files_1 = [
        'chain_of_thought',
        'critique',
        'expert_history'
    ]
    if PROMPT in files_1:
        # print(file)
        output_file = prefix + PROMPT + '.csv'
        new_output_file = prefix + PROMPT + '.txt'
        # print(output_file)
        with open(output_file, 'r', encoding='utf-8') as f:     # somtimes encoding='unicode_escape', somtimes encoding='utf-8'
            reader = csv.reader(f)
            with open(new_output_file, 'w', encoding='utf-8') as f1:
                for line in reader:
                    idx = line[0]
                    # print(idx)
                    paragraph = line[1].strip().split('\n') # 分段
                    #                print('--------------------------------------')
                    # print('paragraph: ', paragraph)
                    paragraph = [p for p in paragraph if len(p.strip())>0 and p.strip().endswith(':')==False]  # 排除空段和以':'结尾的段
                    # print('--------------------------------------')
                    # print('paragraph: ', paragraph)
                    if len(paragraph) > 0:
                        if paragraph[0].strip().startswith('/*'):   # comment格式是/* ...  */
                            if len(paragraph[0].strip()) <= 3:
                                final_lines = []
                                for k in range(0, len(paragraph)):
                                    if paragraph[k].strip().startswith('*/'):
                                        break
                                    elif paragraph[k].strip().startswith('*'):
                                        final_lines.append(paragraph[k].strip()[2:])
                                    elif paragraph[k].strip().startswith('/*'):
                                        final_lines.append(paragraph[k].strip()[2:])
                                    else:
                                        final_lines.append(paragraph[k].strip())
                                new_paragraph = ' '.join(final_lines)
                                sentence = new_paragraph.strip().split('. ')  # 取该段分句
                                sentence = [c for c in sentence if len(c.strip()) > 1]  # 取长度大于1的句子
                                comment = sentence[0]  # 取第一句
                            else:
                                comment = paragraph[0].strip()[2:].strip()
                                if comment.endswith('*/'):
                                    comment = comment[:-2]
                        elif paragraph[0].strip().startswith('```'):
                            comment = paragraph[1]
                            cnt = 0
                            flg = False
                            for i in range(1, len(paragraph)): # 提取```code block```中的第一行注释
                                p = paragraph[i].strip()
                                if flg == False and (p.startswith('//') or p.startswith('# ')): # python java c++ 注释
                                    comment = p
                                    break
                                if flg == False and p.startswith('"""'):   # python注释
                                    if len(p)==3:
                                        final_lines = []
                                        for j in range(i+1, len(paragraph)):
                                            if paragraph[j].strip().startswith('"""'):
                                                break
                                            final_lines.append(paragraph[j].strip())
                                        new_paragraph = ' '.join(final_lines)
                                        sentence = new_paragraph.strip().split('. ')  # 取该段分句
                                        sentence = [c for c in sentence if len(c.strip()) > 1]  # 取长度大于1的句子
                                        comment = sentence[0]  # 取第一句
                                        break
                                    else:
                                        comment = p.strip()[3:]
                                        if comment.endswith('"""'):
                                            comment = comment[:-3]
                                        break
                                if flg == False and p.startswith('/*'):   # comment格式是/* ...  */
                                    if len(p) <= 3:
                                        final_lines = []
                                        for j in range(i + 1, len(paragraph)):
                                            if paragraph[j].strip().startswith('*/'):
                                                break
                                            elif paragraph[j].strip().startswith('*'):
                                                final_lines.append(paragraph[j].strip()[2:])
                                            elif paragraph[j].strip().startswith('/*'):
                                                final_lines.append(paragraph[j].strip()[2:])
                                            else:
                                                final_lines.append(paragraph[j].strip())
                                        new_paragraph = ' '.join(final_lines)
                                        sentence = new_paragraph.strip().split('. ')  # 取该段分句
                                        sentence = [c for c in sentence if len(c.strip()) > 1]  # 取长度大于1的句子
                                        comment = sentence[0]  # 取第一句
                                        break
                                    else:
                                        comment = p[2:].strip()
                                        if comment.endswith('*/'):
                                            comment = comment[:-2]
                                        break
                                if flg == True and len(p.strip())>0: # code block里面没有注释
                                    sentence = p.strip().split('. ')  # 取该段分句
                                    sentence = [c for c in sentence if len(c.strip()) > 1]  # 取长度大于1的句子
                                    comment = sentence[0]  # 取第一句
                                    break
                                if p.startswith('```'): # code block里面没有注释
                                    flg = True
                        elif paragraph[0].strip().startswith('"""'):   #  """...."""中的注释
                            if len(paragraph[0].strip()) == 3:
                                final_lines = []
                                for j in range(1, len(paragraph)):
                                    if paragraph[j].strip().startswith('"""'):
                                        break
                                    final_lines.append(paragraph[j].strip())
                                new_paragraph = ' '.join(final_lines)
                                sentence = new_paragraph.strip().split('. ')  # 取该段分句
                                sentence = [c for c in sentence if len(c.strip()) > 1]  # 取长度大于1的句子
                                comment = sentence[0]  # 取第一句
                            else:
                                comment = p.strip()[3:]
                                if comment.endswith('"""'):
                                    comment = comment[:-3]
                        else:
                            sentence = paragraph[0].strip().split('. ') # 取第一段分句
                            sentence = [c for c in sentence if len(c.strip())>1]  # 取长度大于1的句子
                            if PROMPT == 'critique' and len(sentence) > 1:
                                sentence = [c for c in sentence if 'apologies' not in c and 'Apologies' not in c and 'apologize' not in c]  # 取不含有apologies的句子
                            # print('--------------------------------------')
                            # print('sentence: ', sentence)
                            comment = sentence[0] # 取第一句
                        comment = comment.strip()
                        # 去除句子前后“”
                        if comment.startswith('"') or comment.startswith('`') or comment.startswith('-') or comment.startswith('#') or comment.startswith('*'):
                            comment = comment[1:].strip()
                        if comment.endswith('"'):
                            comment = comment[:-1].strip()
                        if comment.startswith('//') or comment.startswith('""') or comment.startswith('/*'):
                            comment = comment[2:].strip()
                        if comment.endswith('*/'):
                            comment = comment[:-2].strip()
                        # 去除句子最后句号
                        if comment.endswith('.'):
                            comment = comment[:-1].strip()
                        comment = comment.replace('\t', ' ')
                    else:
                        comment = ''
                    f1.write(idx+'\t'+comment+' .\n')


    files_2 = [
        'zero_shot',
        'few_shot_history_4'
             ]
    if PROMPT in files_2:
        output_file = prefix+PROMPT+ '.csv'
        new_output_file = prefix+PROMPT+'.txt'
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            with open(new_output_file, 'w', encoding='utf-8') as f1:
                for line in reader:
                    idx = line[0]
                    paragraph = line[1].strip().split('\n') # 分段
                    # print('paragraph: ', paragraph)
                    paragraph = [p for p in paragraph if len(p.strip()) > 0]  # 排除空段
                    # print('--------------------------------------')
                    # print('paragraph: ', paragraph)

                    if paragraph[0].strip().startswith('/*'):  # comment格式是/* ...  */
                        if len(paragraph[0].strip()) <= 3:
                            final_lines = []
                            for k in range(0, len(paragraph)):
                                if paragraph[k].strip().startswith('*/'):
                                    break
                                elif paragraph[k].strip().startswith('*'):
                                    final_lines.append(paragraph[k].strip()[2:])
                                elif paragraph[k].strip().startswith('/*'):
                                    final_lines.append(paragraph[k].strip()[2:])
                                else:
                                    final_lines.append(paragraph[k].strip())
                            new_paragraph = ' '.join(final_lines)
                            sentence = new_paragraph.strip().split('. ')  # 取该段分句
                            sentence = [c for c in sentence if len(c.strip()) > 1]  # 取长度大于1的句子
                            comment = sentence[0]  # 取第一句
                        else:
                            comment = paragraph[0].strip()[2:].strip()
                            if comment.endswith('*/'):
                                comment = comment[:-2]
                    else:
                        sentence = paragraph[0].strip().split('. ')  # 取第一段分句
                        sentence = [c for c in sentence if len(c.strip()) > 1]  # 取长度大于1的句子
                        # print('--------------------------------------')
                        # print('sentence: ', sentence)
                        comment = sentence[0].strip()  # 取第一句
                        # 去除句子前后“”
                        if comment.startswith('"') or comment.startswith('`') or comment.startswith('-') or comment.startswith('#') or comment.startswith('*'):
                            comment = comment[1:].strip()
                        if comment.endswith('"'):
                            comment = comment[:-1].strip()
                        if comment.startswith('//') or comment.startswith('""') or comment.startswith('/*'):
                            comment = comment[2:].strip()
                        if comment.endswith('*/'):
                            comment = comment[:-2].strip()
                        # 去除句子最后句号
                        if comment.endswith('.'):
                            comment = comment[:-1].strip()
                        comment = comment.replace('\t', ' ')

                    f1.write(idx + '\t' + comment + ' .\n')


if __name__ == '__main__':
    models = [
        'gpt-4',
        'gpt-3.5',
        'starchat',
        'codellama'
    ]
    languages = [
        'java',
        'python',
        'c'
    ]

    # write_groundtruth(DIR='D:\\llm_checkpoint\\codesum\\', LANGUAGE='java')

    # RQ2
    for prompt in [
        # 'zero_shot',
        # 'chain_of_thought',
        #  'critique',
        # 'expert_history',
        # 'few_shot_history_4'
             ]:
        for model in models:
            for language in languages:
                beautify(DIR='D:\llm_checkpoint\codesum\\', LANGUAGE=language, TEMPERATURE='0.1', PROMPT=prompt, MODEL=model)


    # RQ3
    for temperature in [0.1, 0.5, 1.0]:
        for top_p in [0.5, 0.75]:
            for model in models:
                for language in languages:
                    beautify(DIR='D:\llm_checkpoint\codesum\\', LANGUAGE=language, TEMPERATURE=temperature, PROMPT='few_shot_history_4', MODEL=model, TOP_P=top_p)

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
        write_groundtruth(DIR='D:\\llm_checkpoint\\codesum\\', LANGUAGE=language)
        for model in models:
            try:
                beautify(DIR='D:\llm_checkpoint\codesum\\', LANGUAGE=language, TEMPERATURE='0.1', PROMPT='few_shot_history_4', MODEL=model)
            except:
                print(language)

    # RQ5
    for language in [
        # 'what',
        # 'why',
        # 'done',
        # 'usage',
        # 'property'
    ]:
        write_groundtruth(DIR='D:\\llm_checkpoint\\codesum\\', LANGUAGE=language)
        for model in models:
                beautify(DIR='D:\llm_checkpoint\codesum\\', LANGUAGE=language, TEMPERATURE='0.1', PROMPT='few_shot_history_4', MODEL=model)
