from requests import get, exceptions
from argparse import ArgumentParser
from termcolor import colored
from os.path import exists
from bs4 import BeautifulSoup
from time import sleep



def banner() -> None:
    print(colored('''
         _______  ___   _______  __   __  __   __  _______                                 
        |       ||   | |       ||  | |  ||  | |  ||  _    |                                
        |    ___||   | |_     _||  |_|  ||  | |  || |_|   |                                
        |   | __ |   |   |   |  |       ||  |_|  ||       |                                
        |   ||  ||   |   |   |  |       ||       ||  _   |                                 
        |   |_| ||   |   |   |  |   _   ||       || |_|   |                                
        |_______||___|   |___|  |__| |__||_______||_______|                                
 ______    _______  _______  _______  _______  ___   _______  _______  ______    __   __   
|    _ |  |       ||       ||       ||       ||   | |       ||       ||    _ |  |  | |  |  
|   | ||  |    ___||    _  ||   _   ||  _____||   | |_     _||   _   ||   | ||  |  |_|  |  
|   |_||_ |   |___ |   |_| ||  | |  || |_____ |   |   |   |  |  | |  ||   |_||_ |       |  
|    __  ||    ___||    ___||  |_|  ||_____  ||   |   |   |  |  |_|  ||    __  ||_     _|  
|   |  | ||   |___ |   |    |       | _____| ||   |   |   |  |       ||   |  | |  |   |    
|___|  |_||_______||___|    |_______||_______||___|   |___|  |_______||___|  |_|  |___|    
 ______   _______  _     _  __    _  ___      _______  _______  ______   _______  ______   
|      | |       || | _ | ||  |  | ||   |    |       ||   _   ||      | |       ||    _ |  
|  _    ||   _   || || || ||   |_| ||   |    |   _   ||  |_|  ||  _    ||    ___||   | ||  
| | |   ||  | |  ||       ||       ||   |    |  | |  ||       || | |   ||   |___ |   |_||_ 
| |_|   ||  |_|  ||       ||  _    ||   |___ |  |_|  ||       || |_|   ||    ___||    __  |
|       ||       ||   _   || | |   ||       ||       ||   _   ||       ||   |___ |   |  | |
|______| |_______||__| |__||_|  |__||_______||_______||__| |__||______| |_______||___|  |_|
    ''', 'green'))


def getArgument():
    parser = ArgumentParser()
    parser.add_argument('--timeout', help='Give a timeout value')
    return parser.parse_args()


def profile_checker(profile_name: str) -> bool:
    status = get('https://github.com/' + profile_name).status_code
    return status != 404


def repos_finder(link) -> tuple:
    global repos

    req = get(link, timeout=TIMEOUT)
    req = req.text
    r = BeautifulSoup(req, 'html.parser')
    all_repos = r.find_all('a', {'itemprop': 'name codeRepository'})
    repos += [i.text.strip() for i in all_repos]
    button_exist = r.find(
        'a', {'class': 'btn btn-outline BtnGroup-item'}, text='Next')

    if (not button_exist):
        return

    next_link = r.find(
        'a', {'class': 'btn btn-outline BtnGroup-item'}, text='Next')['href']
    repos_finder(next_link)


def viewer(ln: int) -> None:
    print(colored('\nRepositories:\n', 'magenta'))
    print((ln + 18) * '-')
    for (x, name) in repos:
        l = '|' + f' [{x.zfill(4)}]    ' + name.center(ln) + '     |'
        print(colored(l, 'yellow'))
        print((ln + 18) * '-')


def file_name_descriptor() -> str:
    msg = colored('[ q to exit the menu ]', 'yellow')
    while True:
        print(msg, '\n')
        file_name = input('Enter a file name: ').strip()
        file_name = file_name if (
            file_name.endswith('.zip')) else file_name + '.zip'

        if (exists(file_name)):
            msg = colored('[!]-> This file already exists <-[!]',
                          'red', on_color='on_white')
            continue

        return file_name


def find_download_url(repo_url):
    page_content = get(repo_url, timeout=TIMEOUT).text
    p = BeautifulSoup(page_content, 'html.parser')
    file_name = p.find(
        'span', {'class': 'css-truncate-target', 'data-menu-button': True}).text
    real_url = repo_url + '/archive/refs/heads/' + file_name + '.zip'
    return real_url


def downloader(file_name: str, user_name: str, repo_name: str) -> None:
    url = find_download_url(f'https://github.com/{user_name}/{repo_name}')
    print(colored('[*]-> Download Started <-[*]', 'green'))
    req = get(url, timeout=TIMEOUT)
    with open(file_name, 'wb') as output_file:
        output_file.write(req.content)
    print(colored('[*]-> Download Completed <-[*]', 'yellow'))
    sleep(2)


def main():
    global repos

    print(colored(F'[*]-> timeout set {TIMEOUT} <-[*]', 'yellow'))
    sleep(1)
    print('\n'*30)
    msg1 = colored('[ CTRL + C to exit ]', 'yellow')

    try:
        while True:
            banner()
            print(msg1, '\n')
            prof_name = input('Profile name > ').strip()

            if (prof_name) and (profile_checker(prof_name)):
                link = f'https://github.com/{prof_name}?tab=repositories'
                repos_finder(link)

                if (len(repos) == 0):
                    msg1 = colored(
                        '[*]-> No repository found in this profile <-[*]', 'green')

                else:
                    repos = [(str(i[0]), i[1]) for i in enumerate(repos, 1)]

                    longest_name = len(
                        sorted(repos, key=lambda x: len(x[1]), reverse=True)[0][1])

                    msg2 = colored('[ q to exit the menu ]', 'yellow')
                    while True:
                        viewer(longest_name)
                        print(msg2, '\n')
                        op = input('Repository number > ').strip().lstrip('0')

                        if (op == 'q'):
                            msg1 = colored('[ CTRL + C to exit ]', 'yellow')
                            repos = []
                            break

                        elif (op.isnumeric()) and (int(op) in range(1, len(repos)+1)):
                            repo_name = repos[int(op)-1][1]
                            file_name = file_name_descriptor()
                            downloader(file_name, prof_name, repo_name)
                            msg2 = colored('[ q to exit the menu ]', 'yellow')

                        else:
                            msg2 = colored(
                                '[!]-> Please enter a valid number <-[!]', 'red', on_color='on_white')

            else:
                msg1 = colored(
                    '[!]-> Please, enter an existing profile name <-[!]', 'red', on_color='on_white')

    except KeyboardInterrupt:
        quit()

    except (exceptions.ConnectionError, exceptions.ReadTimeout):
        print(colored(
            '[!]-> Please check your internet connection <-[!]', 'red', on_color='on_white'))


if __name__ == '__main__':
    repos = []
    arg = getArgument()
    TIMEOUT = arg.timeout
    TIMEOUT = int(TIMEOUT) if (TIMEOUT and TIMEOUT.isnumeric()) else 5
    main()
