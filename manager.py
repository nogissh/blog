import os
import sys
import shutil
import datetime
import re
import json

from markdown import Markdown
from jinja2 import Environment, FileSystemLoader
from csscompressor import compress as css_minifier
from jsmin import jsmin as js_minifier
from htmlmin import minify as html_minifier

BASE_URL = os.path.dirname(os.path.abspath(__file__))


def mkdir_public():
    if not os.path.exists(os.path.join(BASE_URL, 'public')):
        os.mkdir(os.path.join(BASE_URL, 'public'))


def mkdir_articles():
    mkdir_public()
    if not os.path.exists(os.path.join(BASE_URL, 'public', 'articles')):
        os.mkdir(os.path.join(BASE_URL, 'public', 'articles'))


def mkdir_static():
    mkdir_public()
    if not os.path.exists(os.path.join(BASE_URL, 'public', 'static')):
        os.mkdir(os.path.join(BASE_URL, 'public', 'static'))


def minify_css(css):
    return css_minifier(css)


def minify_js(js):
    return js_minifier(js, quote_chars="'\"`")


def minify_html(html):
    return html_minifier(html).replace('> <', '><')


class ArticleManager:
    ARTICLES_ROOT_DIR = 'articles'
    PUBLIC_ROOT_DIR = 'public'

    IMAGE_ROOT_DIR = 'images'

    md = Markdown(extensions=['tables'])

    template = Environment(loader=FileSystemLoader(os.path.join(BASE_URL, 'templates'))).get_template('article.html')

    def create(self):
        if not os.path.exists(self.ARTICLES_ROOT_DIR):
            os.mkdir(self.ARTICLES_ROOT_DIR)

        created_dt = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(seconds=32400)))

        dir_name = created_dt.strftime('%Y%m%d%H%M%S')

        os.mkdir(os.path.join(self.ARTICLES_ROOT_DIR, dir_name))
        os.mkdir(os.path.join(self.ARTICLES_ROOT_DIR, dir_name, 'images'))

        with open(os.path.join(self.ARTICLES_ROOT_DIR, dir_name, 'script.md'), 'w', encoding='utf-8') as f:
            f.write("# タイトル\n\nまえがき\n\n## はじめに\n\nhogehoge\n\n## おわりに\n\nhogehoge\n")

        with open(os.path.join(self.ARTICLES_ROOT_DIR, dir_name, 'info.json'), 'w', encoding='utf-8') as f:
            f.write(json.dumps({
                'id': dir_name,
                'title': '',
                'description': '',
                'image': '',
                'tags': [],
                'created_at': created_dt.isoformat(timespec='seconds'),
                'updated_at': created_dt.isoformat(timespec='seconds'),
            }, indent=4))

    def build(self, dir_name):
        mkdir_articles()

        if not os.path.exists(os.path.join(BASE_URL, 'public', 'articles', dir_name)):
            os.mkdir(os.path.join(BASE_URL, 'public', 'articles', dir_name))

        shutil.copytree(
            os.path.join(os.path.join(BASE_URL, 'articles', dir_name, 'images')),
            os.path.join(BASE_URL, 'public', 'articles', dir_name, 'images')
        )

        with open(os.path.join(BASE_URL, 'articles', dir_name, 'info.json')) as f:
            info = json.load(f)

        with open(os.path.join(BASE_URL, 'articles', dir_name, 'script.md')) as f:
            script = f.read()

        info['tags_as_text'] = ', '.join(info['tags'])

        info['formatted_created_at'] = datetime.datetime.fromisoformat(info['created_at']).strftime('%Y年%m月%d日 %H:%M')
        info['formatted_updated_at'] = datetime.datetime.fromisoformat(info['updated_at']).strftime('%Y年%m月%d日 %H:%M')

        with open(os.path.join(BASE_URL, 'assets', 'css', 'style.css')) as f:
            css = f.read()

        params = {
            'css': minify_css(css),
            'article_content': self.md.convert(script),
        }

        params.update(info)

        with open(os.path.join(BASE_URL, 'public', 'articles', dir_name, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(minify_html(self.template.render(**params)))

    def build_all(self):
        if not os.path.exists(self.PUBLIC_ROOT_DIR):
            os.mkdir(self.PUBLIC_ROOT_DIR)

        for dir_name in os.listdir(self.ARTICLES_ROOT_DIR):
            if not re.match(r'[0-9]{14}', dir_name):
                continue
            self.build(dir_name)


class IndexManager:
    ARTICLES_ROOT_DIR = 'articles'
    PUBLIC_ROOT_DIR = 'public'

    def build(self):
        article_list = []

        dir_name_list = [int(dir_name) for dir_name in os.listdir(self.ARTICLES_ROOT_DIR) if re.match(r'[0-9]{14}', dir_name)]
        dir_name_list = sorted(dir_name_list, reverse=True)
        dir_name_list = map(str, dir_name_list[:3])

        for dir_name in dir_name_list:
            with open(os.path.join(self.ARTICLES_ROOT_DIR, dir_name, 'info.json')) as f:
                info = json.load(f)

            info['formatted_created_at'] = datetime.datetime.fromisoformat(info['created_at']).strftime('%Y年%m月%d日 %H:%M')
            info['formatted_updated_at'] = datetime.datetime.fromisoformat(info['updated_at']).strftime('%Y年%m月%d日 %H:%M')

            article_list.append(info)

        with open(os.path.join(BASE_URL, 'assets', 'css', 'style.css')) as f:
            css = f.read()

        params = {
            'css': minify_css(css),
            'article_list': article_list,
        }

        template = Environment(loader=FileSystemLoader('./templates')).get_template('index.html')
        with open(os.path.join(self.PUBLIC_ROOT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(minify_html(template.render(**params)))


class SearchManager:
    template = Environment(loader=FileSystemLoader(os.path.join(BASE_URL, 'templates'))).get_template('search.html')

    def build(self):
        mkdir_public()
        mkdir_static()
        
        dir_name_list = [
            dir_name for dir_name in os.listdir(os.path.join(BASE_URL, 'articles'))
            if re.match(r'[0-9]{14}', dir_name)
        ]

        info_list = []
        tag_list = []

        for dir_name in dir_name_list:
            with open(os.path.join(BASE_URL, 'articles', dir_name, 'info.json')) as f:
                info = json.load(f)

            info['formatted_created_at'] = datetime.datetime.fromisoformat(info['created_at']).strftime('%Y年%m月%d日 %H:%M')
            info['formatted_updated_at'] = datetime.datetime.fromisoformat(info['updated_at']).strftime('%Y年%m月%d日 %H:%M')

            info_list.append(info)

            tag_list.extend(info['tags'])

        tag_list = list(set(tag_list))

        with open(os.path.join(BASE_URL, 'assets', 'css', 'style.css')) as f:
            css = f.read()

        with open(os.path.join(BASE_URL, 'assets', 'js', 'search.js')) as f:
            js = f.read()

        params = {
            'css': minify_css(css),
            'js': minify_js(js),
            'tag_list': tag_list,
        }

        with open(os.path.join(BASE_URL, 'public', 'search.html'), 'w', encoding='utf-8') as f:
            f.write(minify_html(self.template.render(**params)))

        with open(os.path.join(BASE_URL, 'public', 'static', 'search.json'), 'w', encoding='utf-8') as f:
            json.dump({ 'articles': info_list }, f)


if __name__ == '__main__':
    mkdir_public()

    am = ArticleManager()
    im = IndexManager()
    sm = SearchManager()

    try:
        command = sys.argv[1]
        if command == 'new' or command == 'create':
            am.create()
        elif command == 'build':
            am.build_all()
            im.build()
            sm.build()
        else:
            print('コマンドが不正です。')
    except IndexError:
        print('コマンドを入力してください。')
