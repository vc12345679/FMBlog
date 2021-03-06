#!/usr/bin/env python3
# encoding=utf-8

__author__ = 'Siwei Chen<me@chensiwei.space>'

import re
from mistune import InlineLexer, Renderer, Markdown, BlockLexer
from mistune_contrib import highlight, toc


class KaTeXRenderer(Renderer, toc.TocMixin, highlight.HighlightMixin):
    def __init__(self, *args, **kwargs):
        super(KaTeXRenderer, self).__init__(*args, **kwargs)

    def inlinekatex(self, text):
        return '<tex class="tex-inline">%s</tex>' % text

    def blockkatex(self, text):
        return '<tex class="tex-block">%s</tex>' % text


class KaTeXInlineLexer(InlineLexer):
    def __init__(self, *args, **kwargs):
        super(KaTeXInlineLexer, self).__init__(*args, **kwargs)
        self.enable_katexinline()

    def enable_katexinline(self):
        self.rules.inlinekatex = re.compile(r'^\${2}([\s\S]*?)\${2}(?!\$)')  # $$tex$$
        self.default_rules.insert(3, 'inlinekatex')
        self.rules.text = re.compile(r'^[\s\S]+?(?=[\\<!\[_*`~\$]|https?://| {2,}\n|$)')

    def output_inlinekatex(self, m):
        return self.renderer.inlinekatex(m.group(1))


class KaTeXBlockLexer(BlockLexer):
    def __init__(self, *args, **kwargs):
        super(KaTeXBlockLexer, self).__init__(*args, **kwargs)
        self.enable_katexblock()

    def enable_katexblock(self):
        self.rules.blockkatex = re.compile(r'^\\\\\[(.*?)\\\\\]', re.DOTALL)  # \\[ ... \\]
        self.default_rules.insert(0, 'blockkatex')

    def parse_blockkatex(self, m):
        self.tokens.append({
            'type': 'blockkatex',
            'text': m.group(1)
        })


class CustomMarkdown(Markdown):
    def output_blockkatex(self):
        return self.renderer.blockkatex(self.token['text'])

renderer = KaTeXRenderer()
inline = KaTeXInlineLexer(renderer=renderer)
block = KaTeXBlockLexer()
markdown = CustomMarkdown(renderer=renderer, inline=inline, block=block)
