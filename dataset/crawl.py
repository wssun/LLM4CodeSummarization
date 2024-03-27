import json
import os

from github import Github
import requests

Personal_Access_Token = ""
g = Github(login_or_token=Personal_Access_Token)

def crawl_code(repo):
    print('Trying main branch...')
    repo_url = repo.url+'/zipball/main'
    print(repo_url)

    headers = {"Authorization": f"bearer {Personal_Access_Token}"}
    response = requests.get(repo_url, headers=headers)

    repo_name = '#'.join(repo.full_name.split('/'))

    dir = f"./crawl/{repo.language}/"
    if os.path.exists(dir)==False:
        os.makedirs(dir)

    if response.status_code == 200:
        with open(dir+repo_name+".zip", "wb") as zip_file:
            zip_file.write(response.content)

        print("Download successful!")
    else:
        print('The main branch does not exist!')
        print('Trying master branch...')
        repo_url = repo.url + '/zipball/master'
        print(repo_url)

        response = requests.get(repo_url, headers=headers)

        if response.status_code == 200:
            with open(dir+repo_name+".zip", "wb") as zip_file:
                zip_file.write(response.content)

            print("Download successful!")
        else:
            print('Error: ', response.status_code)


def get_dataset_for_language():
    licenses = ['Apache License 2.0', 'ISC License', 'Creative Commons Attribution 4.0 International',
                'GNU General Public License v2.0', 'GNU General Public License v3.0', 'GNU Lesser General Public License v2.1',
                'GNU Lesser General Public License v3.0', 'MIT License', 'Eclipse Public License 1.0',
                'BSD 3-Clause "New" or "Revised" License', 'BSD 2-Clause "Simplified" License', 'GNU Affero General Public License v3.0',
                'The Unlicense',
                ]
    languages = ['Erlang', 'Haskell', 'Prolog']
    for language in languages:
        repositories = g.search_repositories(query="{}".format(language), sort="stars",
                                             order="desc", language=language)
        top_50_repos = repositories[:50]

        repos = []
        for repo in top_50_repos:
            if repo.language==language:
                if repo.license is None:
                    print('{} license is None'.format(repo.full_name))
                elif repo.license.name in licenses:
                    print(f"Crawling code for {repo.full_name}...")
                    crawl_code(repo)
                    repos.append(repo.full_name)
                else:
                    print('{} license not in licenses'.format(repo.full_name))
                    print(repo.license)

        # with open('{}_repo.jsonl'.format(language),'w',encoding='utf-8') as f:
        #     json_str = json.dumps(repos)
        #     f.write(json_str)

        print("Lanaguge:{} Done".format(language))
        print('{} repositories in total'.format(len(repos)))
        print('Repositories: ')
        print(repos)
        print("*****************************")



