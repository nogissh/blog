import os
import sys
import shutil
import datetime
import re
import json

from markdown import Markdown
from jinja2 import Environment, FileSystemLoader
from minify_html import minify as html_minifier

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


def mv_config():
    mkdir_public()
    os.system('cp ./configs/* ./public')


def mv_icon():
    mkdir_static()
    os.system('cp ./assets/icon/* ./public/static')


def minify_html(html):
    return html_minifier(html, minify_css=True, minify_js=True)


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
            f.write("## まえがき\n\nまえがき\n\n## はじめに\n\nhogehoge\n\n## おわりに\n\nhogehoge\n")

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

    def reset(self, id):
        cur_dir = os.path.join(self.ARTICLES_ROOT_DIR, id)

        dt = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(seconds=32400)))
        new_id = dt.strftime('%Y%m%d%H%M%S')

        # info.json
        with open(os.path.join(cur_dir, 'info.json')) as f:
            obj = json.load(f)
        obj['id'] = new_id
        obj['created_at'] = dt.isoformat(timespec='seconds')
        obj['updated_at'] = dt.isoformat(timespec='seconds')
        with open(os.path.join(cur_dir, 'info.json'), 'w') as f:
            json.dump(obj, f, indent=4)

        # directory
        os.rename(cur_dir, os.path.join(self.ARTICLES_ROOT_DIR, new_id))

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

        info['tags_as_text'] = ', '.join(info['tags'])
        info['formatted_created_at'] = datetime.datetime.fromisoformat(info['created_at']).strftime('%Y年%m月%d日 %H:%M')
        info['formatted_updated_at'] = datetime.datetime.fromisoformat(info['updated_at']).strftime('%Y年%m月%d日 %H:%M')

        with open(os.path.join(BASE_URL, 'articles', dir_name, 'script.md')) as f:
            script = f.read()

        with open(os.path.join(BASE_URL, 'assets', 'css', 'style.css')) as f:
            css = f.read()

        params = {
            'css': css,
            'content': self.md.convert(script),
        }
        params.update(info)

        with open(os.path.join(BASE_URL, self.PUBLIC_ROOT_DIR, 'articles', dir_name, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(html_minifier(self.template.render(**params), minify_css=True, minify_js=True, keep_html_and_head_opening_tags=True))

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

    template = Environment(loader=FileSystemLoader(os.path.join(BASE_URL, 'templates'))).get_template('index.html')

    def build(self):
        article_list = []

        dir_name_list = [int(dir_name) for dir_name in os.listdir(self.ARTICLES_ROOT_DIR) if re.match(r'[0-9]{14}', dir_name)]
        dir_name_list = sorted(dir_name_list, reverse=True)
        dir_name_list = map(str, dir_name_list[:3])

        for dir_name in dir_name_list:
            with open(os.path.join(self.ARTICLES_ROOT_DIR, dir_name, 'info.json')) as f:
                info = json.load(f)
            info['created_date'] = datetime.datetime.fromisoformat(info['created_at']).strftime('%Y年%m月%d日')
            article_list.append(info)

        with open(os.path.join(BASE_URL, 'assets', 'css', 'style.css')) as f:
            css = f.read()

        params = {
            'css': css,
            'article_list': article_list,
        }

        with open(os.path.join(BASE_URL, self.PUBLIC_ROOT_DIR, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(html_minifier(self.template.render(**params), minify_css=True, minify_js=True, keep_html_and_head_opening_tags=True))


class SearchManager:
    PUBLIC_ROOT_DIR = 'public'

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
            info['created_date'] = datetime.datetime.fromisoformat(info['created_at']).strftime('%Y年%m月%d日')
            info_list.append(info)
            tag_list.extend(info['tags'])
        tag_list = list(set(tag_list))

        with open(os.path.join(BASE_URL, 'assets', 'css', 'style.css')) as f:
            css = f.read()

        with open(os.path.join(BASE_URL, 'assets', 'js', 'search.js')) as f:
            js = f.read()

        params = {
            'css': css,
            'js': js,
            'tag_list': tag_list,
        }

        with open(os.path.join(BASE_URL, 'public', 'static', 'search.json'), 'w', encoding='utf-8') as f:
            json.dump({ 'articles': info_list }, f)

        with open(os.path.join(BASE_URL, self.PUBLIC_ROOT_DIR, 'search.html'), 'w', encoding='utf-8') as f:
            f.write(html_minifier(self.template.render(**params), minify_css=True, minify_js=True, keep_html_and_head_opening_tags=True))


class ListManager:
    ARTICLES_ROOT_DIR = 'articles'
    PUBLIC_ROOT_DIR = 'public'

    template = Environment(loader=FileSystemLoader(os.path.join(BASE_URL, 'templates'))).get_template('list.html')

    def build(self):
        mkdir_public()

        dir_name_list = [int(dir_name) for dir_name in os.listdir(self.ARTICLES_ROOT_DIR) if re.match(r'[0-9]{14}', dir_name)]
        dir_name_list = sorted(dir_name_list, reverse=True)
        dir_name_list = map(str, dir_name_list)

        article_list = []
        for dir_name in dir_name_list:
            with open(os.path.join(self.ARTICLES_ROOT_DIR, dir_name, 'info.json')) as f:
                info = json.load(f)
            info['created_date'] = datetime.datetime.fromisoformat(info['created_at']).strftime('%Y年%m月%d日')
            article_list.append(info)

        with open(os.path.join(BASE_URL, 'assets', 'css', 'style.css')) as f:
            css = f.read()

        params = {
            'css': css,
            'article_list': article_list,
        }

        with open(os.path.join(BASE_URL, self.PUBLIC_ROOT_DIR, 'list.html'), 'w', encoding='utf-8') as f:
            f.write(html_minifier(self.template.render(**params), minify_css=True, minify_js=True, keep_html_and_head_opening_tags=True))


if __name__ == '__main__':
    os.system(f'rm -rf {os.path.join(BASE_URL, "public")}')

    am = ArticleManager()
    im = IndexManager()
    sm = SearchManager()
    lm = ListManager()

    try:
        command = sys.argv[1]
        if command == 'new' or command == 'create':
            am.create()
        elif command == 'reset':
            am.reset(sys.argv[2])
        elif command == 'build':
            mkdir_public()

            am.build_all()
            im.build()
            sm.build()
            lm.build()

            mv_config()
            mv_icon()
        else:
            print('コマンドが不正です。')
    except IndexError:
        print('コマンドを入力してください。')
