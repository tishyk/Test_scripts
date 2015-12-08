# coding:utf-8

import requests
import unittest
import logging
import pprint
import getpass

logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')
logging.debug('Start of program')

user = 'tishyk'

url = "https://api.github.com"
res = requests.get(url)


server = "https://api.github.com" 
user = "iKettle" 
response = requests.get(server + "/users/" + user)
print response.content

d_no_auth = eval(res.content)
pprint.pprint(d_no_auth)


res = requests.get(url+'/users/'+user)#getpass.getpass()))
d_with_auth = eval(res.content)
pprint.pprint(d_with_auth)

d_diff = {key:val for key,val in d_with_auth.items() if key not in d_no_auth.keys()}
pprint.pprint(d_diff)

print len(d_no_auth),len(d_with_auth)
logging.debug('End of program')




Testing REST API on Python
Теоретическая часть о Rest API:

REST (Representational state transfer) – это стиль архитектуры программного обеспечения для распределенных систем, таких как World Wide Web, который, как правило, используется для построения веб-служб. Термин REST был введен в 2000 году Роем Филдингом, одним из авторов HTTP-протокола. Системы, поддерживающие REST, называются RESTful-системами.

В общем случае REST является очень простым интерфейсом управления информацией без использования каких-то дополнительных внутренних прослоек. Каждая единица информации однозначно определяется глобальным идентификатором, таким как URL – это значит, что URL по сути является первичным ключом для единицы данных. Каждая URL в свою очередь имеет строго заданный формат. Например третья книга с книжной полки будет иметь вид /book/3, а 35 страница в этой книге — /book/3/page/35. Отсюда и получается строго заданный формат.

Как происходит управление информацией сервиса – это целиком и полностью основывается на протоколе передачи данных. Наиболее распространенный протокол конечно же HTTP. Так вот, для HTTP действие над данными задается с помощью методов: GET (получить), PUT (добавить, заменить), POST (добавить, изменить, удалить), DELETE (удалить). Таким образом, действия CRUD (Create-Read-Update-Delete) могут выполняться как со всеми 4-мя методами, так и только с помощью GET и POST.

И вот как это будет выглядеть на практике на примере книги:
GET /book/ — получить список всех книг
GET /book/3/ — получить книгу номер 3
PUT /book/3/page/12 — добавить/изменить страницу 12 в книге (данные в теле запроса)
POST /book/ – добавить книгу (данные в теле запроса)
DELETE /book/3 – удалить книгу

Практическая часть:

Язык программирования: Python
Модуль для HTTP запросов (наиболее простой): requests
Объект тестирования: Github
Что будем тестировать: авторизация, создание репозиториев, добавление/редактирование/удаление файлов

Итак, из документации по API Гитхаба мы узнаем что все запросы идут на сервер с адресом server = "https://api.github.com" потому давайте посмотрим что там есть

import requests
import unittest

server = "https://api.github.com" 
response = requests.get(server)

print response.content

в результате мы увидим список доступных едениц информации со своим уникальным индетификатором - с помощью этих точек соприкосновения мы и будем немножко взаимодействовать с Github. Для начала нам понадобиться только
"current_user_url":"https://api.github.com/user",
"repository_url":"https://api.github.com/repos/{owner}/{repo}",
"user_url":"https://api.github.com/users/{user}",
"user_repositories_url":"https://api.github.com/users/{user}/repos{?type,page,per_page,sort}" 
Итак, у нас есть перед этим зарегистрированный юзер и мы можем попробовать посмотреть что же нам доступно:

import requests
import unittest

server = "https://api.github.com" 
user = "iKettle" 
response = requests.get(server + "/users/" + user)

print response
print response.text

и как результат мы получили список доступных (публичных) ресурсов, остальная информация о юзере недоступна для всех, мы же не вводили логин/пароль, теперь посмотрим что нам доступно с аутентификацией:

import requests
import unittest

server = "https://api.github.com" 
user = "iKettle" 
password = "*************" 

response = requests.get(server + "/user", auth=(user, password))

print response.status_code
print response.text

в этом случае нам дополнительно доступно следующее:
"private_gists":0,
"total_private_repos":0,
"owned_private_repos":0,
"disk_usage":124,
"collaborators":0,
"plan":{"name":"free","space":976562499,"collaborators":0,"private_repos":0}
не слишком много полезной информации но сейчас нас интересует другое - как происходила аутентификация и как ее использовать в дальнейшем. Еще если заметили во всех случаях код ответа от сервера - 200, что это значит и какие еще есть коды можно посмотреть на Wikipedia. 
Значит мы уже умеем получать информацию и даже логиниться. Попробуем информацию передававть, для этого создадим новый репозиторий. В соответствии с документацией Github, нужно передать имя и описание, все остальное можно оставить по дефолту:

data = {'name':'test', 'description':'some test repo'}
new_repo = requests.post(server + "/user/repos", data, auth=(user, password))
print new_repo
print new_repo.text

на выходе получим ошибку:
<Response [400]> {"message":"Problems parsing JSON","documentation_url":"https://developer.github.com/v3"}
Данные нужно передавать в json формате. Значит подключаем встренный json модуль и пробуем заново:

data = json.dumps({'name':'test', 'description':'some test repo'})
new_repo = requests.post(server + "/user/repos", data, auth=(user, password))
print new_repo
print new_repo.text

теперь получили код 201 что означет успешное создание ресурса. 
Теперь нужно попробовать удалить то что мы создали. Так как каждая единица информации имеет свой ключ - отправляем DELETE реквест по этому ключу, напомню что ключ имеет вид:
"repository_url":"https://api.github.com/repos/{owner}/{repo}" 
Создадим отдельный метод для удаления и тестовый метод который будет его использовать и проверять успешно ли удалился заданный ресурс:

def _delete_repo(self, user, name):  # method delete repository <name> of owner <user>    
    _URL = '{}/repos/{}/{}'.format(self.server, user, name) # create URL for deleting for <user> repository with <name>
    _response = requests.delete(_URL, auth=(USERNAME, PASSWORD)) # send DELETE request to URL with authentication  
    return _response.status_code # return code of the operation, if success - 204 

def test_repo_delete(self):  # each test method should start with <test_> word         
    status_code = self._delete_repo(USERNAME, REPO_NAME) # delete repository with REPO_NAME and receive status code     
    self.assertEqual(status_code, NO_CONTENT) # check if status code success  
    check_repos = requests.get(self.repos, auth=(USERNAME, PASSWORD)).json() # GET all info about all repositories   
    self.assertNotIn(REPO_NAME, [repo.get("name") for repo in check_repos]) # check if all repository names contain deleted

На примере DELETE метода и тестового метода можно писать тесты для остальных CRUD методов и оформлять их в тесткейсы или тестсьюты.
Что ж давайте напишем небольшой тесткейс на создание и удаление репозитория:

import requests
import json
import unittest

NO_CONTENT = 204
INCORRECT_HEADER = 400
ADDED = 201
USERNAME = 'iKettle'
PASSWORD = '*************'
REPO_NAME = 'test5'

class TestGithubAPI(unittest.TestCase):

    def __init__(self, *a, **kw):
        super(TestGithubAPI,self).__init__(*a, **kw)
        self.server = 'https://api.github.com'        
        self.info = '{}/users/{}'.format(self.server,USERNAME)
        self.repos = '{}/user/repos'.format(self.server)

    def test_repo_creating(self):
        status_code, text = self._create_repo(REPO_NAME, 'some test repository')
        self.assertEqual(status_code, ADDED)
        self.assertEqual(text.get('name'), REPO_NAME)

    def test_repo_delete(self):  # each test method should start with <test_> word                 
        status_code = self._delete_repo(USERNAME, REPO_NAME) # delete repository with REPO_NAME and receive status code                
        self.assertEqual(status_code, NO_CONTENT) # check if status code success                 
        check_repos = requests.get(self.repos, auth=(USERNAME, PASSWORD)).json() # GET all info about all repositories            
        self.assertNotIn(REPO_NAME, [repo.get("name") for repo in check_repos]) # check if all repository names contain deleted  

    def _create_repo(self, name, description):
        _data = json.dumps({'name': name, 'description': description})
        _response = requests.post(self.repos, data=_data, auth=(USERNAME, PASSWORD))
        return _response.status_code, _response.json()

    def _delete_repo(self, user, name):  # method delete repository <name> of owner <user>                 
        _URL = '{}/repos/{}/{}'.format(self.server, user, name) # create URL for deleting for <user> repository with <name>                 
        _response = requests.delete(_URL, auth=(USERNAME, PASSWORD)) # send DELETE request to URL with authentication  
        return _response.status_code # return code of the operation, if success - 204      

if __name__ == '__main__':
    unittest.main(verbosity=2)

все, теперь осталось написать остальную пачку тестов)
