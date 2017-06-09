#!/usr/bin/venv python3
# encoding=utf-8

__author__ = 'Siwei Chen<me@chensiwei.space'

from app import db
import datetime
import os
from .custom_markdown import markdown

post_tag_table = db.Table('post_tag',
                          db.Column('post', db.String(64), db.ForeignKey('posts.name')),
                          db.Column('tag', db.String(64), db.ForeignKey('tags.name'))
                          )
post_cat_table = db.Table('post_cat',
                          db.Column('post', db.String(64), db.ForeignKey('posts.name')),
                          db.Column('cat', db.String(64), db.ForeignKey('categories.name'))
                          )


class Post(db.Model):
    __tablename__ = 'posts'
    name = db.Column(db.String(128), primary_key=True)
    title = db.Column(db.String(128))
    author = db.Column(db.String(64))
    date = db.Column(db.Date)
    mtime = db.Column(db.Float)
    md5 = db.Column(db.String(64))
    categories = db.relationship('Category', secondary=post_cat_table, backref=db.backref('posts', lazy='dynamic'))
    tags = db.relationship('Tag', secondary=post_tag_table, backref=db.backref('posts', lazy='dynamic'))
    html = db.Column(db.Text)
    content = db.Column(db.Text)
    summary = db.Column(db.Text)
    link = db.Column(db.String(128))

    def __init__(self, name):
        self.name = name
        import hashlib
        self.md5 = hashlib.md5(name.encode('UTF-8')).hexdigest()
        self.link = name[:-3].replace('\\', '/')

    def __repr__(self):
        return '''FileName: %s
Title: %s
Author: %s
Date: %s
Mtime: %s''' % (self.name, self.title, self.author, self.date, self.mtime)


class Category(db.Model):
    __tablename__ = 'categories'
    name = db.Column(db.String(64), primary_key=True)
    count = db.Column(db.Integer)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return 'CategoryName: %s' % self.name


class Tag(db.Model):
    __tablename__ = 'tags'
    name = db.Column(db.String(64), primary_key=True)
    count = db.Column(db.Integer)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return 'TagName: %s' % self.name


class Blog:
    @classmethod
    def _real_file_name(cls, file_name=''):
        return os.path.join('blogs', file_name)

    @classmethod
    def is_exist(cls, file_name):
        return os.path.exists(cls._real_file_name(file_name))

    @classmethod
    def get_blog(cls, file_name):
        txt = ''
        if cls.is_exist(file_name):
            with open(cls._real_file_name(file_name), 'r', encoding='utf-8') as f:
                txt = f.read()
            mtime = os.path.getmtime(cls._real_file_name(file_name))
            from bs4 import BeautifulSoup, Comment
            import yaml
            comment = BeautifulSoup(txt, "html.parser").find(text=lambda text: isinstance(text, Comment))
            if comment is not None:
                blog_info = yaml.load(comment)
                if 'use_toc' not in blog_info:
                    blog_info['use_toc'] = False
                    html = markdown(txt)
                    return blog_info, txt, html, mtime
            else:
                return
        else:
            return


    @classmethod
    def add(cls, file_name):
        r = cls.get_blog(file_name)
        if r is not None:
            blog_info, txt, html, mtime = r
            if len(blog_info) > 0:
                p = Post.query.filter_by(name=file_name).first()
                if p is None:
                    p = Post(name=file_name)
                p.title = blog_info['title']
                p.author = blog_info['author']
                p.content = txt
                p.html = html
                p.summary = blog_info['summary']
                p.date = datetime.datetime.strptime(str(blog_info['date']), '%Y-%m-%d').date()
                p.mtime = mtime
                p.tags = []
                for itm in blog_info['tag']:
                    tag = Tag.query.filter_by(name=itm).first()
                    if tag is None:
                        db.session.add(Tag(itm))
                        db.session.commit()
                        tag = Tag.query.filter_by(name=itm).first()
                    p.tags.append(tag)
                p.categories = []
                for itm in blog_info['category']:
                    cat = Category.query.filter_by(name=itm).first()
                    if cat is None:
                        db.session.add(Category(itm))
                        db.session.commit()
                        cat = Category.query.filter_by(name=itm).first()
                    p.categories.append(cat)

                db.session.add(p)
                db.session.commit()

    @classmethod
    def modify(cls, file_name):
        cls.add(file_name)

    @classmethod
    def update(cls):

        index = {}
        for file_name, mtime in db.session.query(Post.name, Post.mtime).all():
            index[file_name] = mtime
        flag = False
        for b in list(os.walk(cls._real_file_name())):
            for c in b[2]:
                itm = os.path.relpath(os.path.join(b[0], c), cls._real_file_name())
                if os.path.splitext(itm)[1] == '.md':
                    if c not in index:
                        flag = True
                        cls.add(c)
                    elif os.path.getmtime(cls._real_file_name(c)) != index[c]:
                        flag = True
                        cls.modify(c)

        post_r = Post.query.all()
        for itm in post_r:
            if not cls.is_exist(itm.name):
                flag = True
                db.session.delete(itm)
                db.session.commit()

        if flag:
            tag_r = Tag.query.all()
            for itm in tag_r:
                c = len(list(itm.posts))
                if c == 0:
                    db.session.delete(itm)
                    db.session.commit()
                elif c != itm.count:
                    itm.count = c
                    db.session.add(itm)
                    db.session.commit()

            cat_r = Category.query.all()
            for itm in cat_r:
                c = len(list(itm.posts))
                if c == 0:
                    db.session.delete(itm)
                    db.session.commit()
                elif c != itm.count:
                    itm.count = c
                    db.session.add(itm)
                    db.session.commit()

        return flag
