#!/usr/bin/env python3
# encoding=utf-8

__author__ = 'Siwei Chen<me@chensiwei.space>'

from flask import render_template, current_app, request, url_for
from app.models import Post, Tag, Category, Blog
from . import main
import datetime


@main.route('/', methods=['GET', 'POST'])
def index():
    Blog.update()
    pt = request.args.get('page')
    if pt is None:
        page = 1
    else:
        page = int(pt)
    pagination = Post.query.order_by(Post.date.desc()).paginate(
        page=page, per_page=current_app.config['FMBLOG_PER_PAGE'])
    return render_template('index.html', pagination=pagination, endpoint='main.index', value={},
                           tags=Tag.query.order_by(Tag.count.desc()).all(),
                           cats=Category.query.order_by(Category.count.desc()).all(),
                           site=current_app.config['FMBLOG_SITE'],
                           page_list=get_page_list(pagination, page))


@main.route('/tag/<path:tag_name>.html')
def tag(tag_name):
    Blog.update()
    pt = request.args.get('page')
    if pt is None:
        page = 1
    else:
        page = int(pt)
    pagination = Tag.query.filter_by(name=tag_name).first().posts.order_by(Post.date.desc()).paginate(
        page=page, per_page=current_app.config['FMBLOG_PER_PAGE'])
    return render_template('tag.html', pagination=pagination, endpoint='main.tag',
                           tags=Tag.query.order_by(Tag.count.desc()).all(), value={'tag_name': tag_name},
                           cats=Category.query.order_by(Category.count.desc()).all(),
                           site=current_app.config['FMBLOG_SITE'],
                           page_list=get_page_list(pagination, page))


def get_page_list(pagination, page, itm_number=4):
    if pagination.pages <= itm_number * 2 + 1:
        page_list = list(range(1, pagination.pages + 1))
    elif pagination.page <= itm_number + 1:
        page_list = list(range(1, itm_number * 2))
        page_list.append([0, pagination.pages])
    elif pagination.page >= pagination.pages - itm_number:
        page_list = [1, 0]
        page_list.append(list(range(pagination.pages - itm_number * 2 + 2, pagination.pages + 1)))
    else:
        page_list = [1, 0]
        page_list.append(list(range(page - itm_number + 2, page + itm_number - 1)))
    return page_list


@main.route('/category/<path:cat_name>.html')
def category(cat_name):
    Blog.update()
    pt = request.args.get('page')
    if pt is None:
        page = 1
    else:
        page = int(pt)
    pagination = Category.query.filter_by(name=cat_name).first().posts.order_by(Post.date.desc()).paginate(
        page=page, per_page=current_app.config['FMBLOG_PER_PAGE'])
    return render_template('category.html',
                           pagination=pagination, endpoint='main.category', value={'cat_name': cat_name},
                           page_list=get_page_list(pagination, page),
                           tags=Tag.query.order_by(Tag.count.desc()).all(),
                           cats=Category.query.order_by(Category.count.desc()).all(),
                           site=current_app.config['FMBLOG_SITE'])


@main.route('/feeds')
def feeds():
    Blog.update()
    full = request.args.get('full')
    posts = Post.query.order_by(Post.date.desc()).all()
    if not full:
        posts = posts[:min(20, len(posts))]
    import PyRSS2Gen
    feed = []
    for itm in posts:
        feed.append(PyRSS2Gen.RSSItem(title=itm.title,
                                      pubDate=datetime.datetime(
                                          year=itm.date.year,
                                          month=itm.date.month,
                                          day=itm.date.day),
                                      description=itm.summary,
                                      guid=PyRSS2Gen.Guid(itm.md5),
                                      link=url_for('main.blog', _external=True, post_name=itm.link)
                                      ))
    rss = PyRSS2Gen.RSS2(title=current_app.config['FMBLOG_SITE']['name'],
                         description=current_app.config['FMBLOG_SITE']['desc'],
                         lastBuildDate=datetime.datetime.now(),
                         link=url_for('main.feeds', _external=True),
                         items=feed)
    return rss.to_xml(encoding='utf-8')


@main.route('/search/<path:keyword>.html')
def search(keyword):
    Blog.update()
    pt = request.args.get('page')
    if pt is None:
        page = 1
    else:
        page = int(pt)
    try:
        keywords = keyword.split()
        from sqlalchemy import and_, or_
        rules = and_(
            *[or_(Post.title.ilike('%%%s%%' % k), Post.summary.ilike('%%%s%%' % k), Post.content.ilike('%%%s%%' % k))
              for k in keywords])
        pagination = Post.query.filter(rules).order_by(Post.date.desc()).paginate(
            page=page, per_page=current_app.config['FMBLOG_PER_PAGE'])
    except Exception:
        return render_template('404.html', e='Error: Empty Keyword', site=current_app.config['FMBLOG_SITE'],
                               value={}), 404
    return render_template('search.html', value={'keyword': keyword},
                           pagination=pagination, endpoint='main.search',
                           page_list=get_page_list(pagination, page),
                           tags=Tag.query.order_by(Tag.count.desc()).all(),
                           cats=Category.query.order_by(Category.count.desc()).all(),
                           site=current_app.config['FMBLOG_SITE'])


@main.route('/blog/<path:post_name>.html')
def blog(post_name):
    Blog.update()
    post = Post.query.filter_by(link=post_name).first_or_404()
    pt = []
    pc = []
    for titm in post.tags:
        for pitm in titm.posts:
            if pitm != post:
                pt.append(pitm)
    for titm in post.categories:
        for pitm in titm.posts:
            if pitm != post:
                pc.append(pitm)
    from collections import Counter
    ptt = []
    pct = []
    for i in Counter(pt).items():
        ptt.append((i[0], i[1]))
    for i in Counter(pc).items():
        pct.append((i[0], i[1]))
    ptt.sort(key=lambda item: item[0].date, reverse=True)
    ptt.sort(key=lambda item: item[1], reverse=True)
    pct.sort(key=lambda item: abs(item[0].date - post.date))
    pt = [x[0] for x in ptt]
    pc = [x[0] for x in pct]
    if len(pt) > 7:
        pt = pt[:7]
    if len(pc) > 7:
        pc = pc[:7]
    pct.sort(key=lambda item: item[0].date, reverse=True)
    value = {}
    return render_template('blog.html',
                           post=post,
                           posts_tag=pt,
                           posts_cat=pc,
                           value=value,
                           site=current_app.config['FMBLOG_SITE'])
