#!/usr/bin/env python
#-*- coding: utf-8 -*-
from ..models import Article,Tag
from django import template
import random
register=template.Library()

msg=['primary','info','success','danger','dark','warning']

@register.inclusion_tag('article/_sidebar.html')
def get_sidebar_tag():
    all_tags=Tag.objects.order_by('slug').all()
    for tag in all_tags:
        tag.cls_msg=random.choice(msg)
    return {'tags_cloud':all_tags}

@register.inclusion_tag('article/_navbar.html')
def get_navbar_tag():
    return {}