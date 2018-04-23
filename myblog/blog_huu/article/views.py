from django.shortcuts import render
from django.http.response import HttpResponse
from .models import Comment,Article,Tag,UserProfile
from django.shortcuts import render,redirect,reverse,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from .forms import UserProfileForm
import markdown
from django.utils.text import slugify
from markdown.extensions.toc import TocExtension
from datetime import datetime,timedelta
# Create your views here.

def index(request):
    articles = Article.objects.order_by('-post_time').all()[:4]
    return render(request,'article/index.html',{'articles':articles})


def get_range_page(paginator,current_page):
    # 分页过多解决
    l = len(paginator.page_range)
    mid1 = 1
    mid2 = l - 1
    page_range = list(paginator.page_range)
    if l > 10:
        if current_page - 3 > 1:
            mid1 = current_page - 1 - 3
        if current_page + 4 < l - 1:
            mid2 = current_page + 4
        page_range[1:mid1] = [None]
        page_range[mid2:l - 1] = [None]
    return page_range

def all_articles(request):

    all_articles_list=Article.objects.order_by('-post_time').all()

    current_page=request.GET.get('page',1)
    paginator=Paginator(all_articles_list,5)

    page_range=get_range_page(paginator,int(current_page)-1)

    try:
        all_articles_list=paginator.page(current_page)
    except PageNotAnInteger:
        all_articles_list=paginator.page(1)
    except EmptyPage:
        all_articles_list=paginator.page(paginator.num_pages)

    con_dict={
        'articles':all_articles_list.object_list,
        'page':all_articles_list,
        'page_range':page_range,
        'page_url':reverse('article:all_articles')
    }

    return render(request,'article/all_articles.html',con_dict)

def tag_articles(request,tag_slug):
    tag=get_object_or_404(Tag,slug=tag_slug)

    if tag is not None:
        tag_articles_list=tag.articles.order_by('-post_time').all()

        current_page = request.GET.get('page', 1)
        paginator = Paginator(tag_articles_list, 5)

        page_range = get_range_page(paginator, int(current_page)-1)

        try:
            tag_articles_list = paginator.page(current_page)
        except PageNotAnInteger:
            tag_articles_list = paginator.page(1)
        except EmptyPage:
            tag_articles_list = paginator.page(paginator.num_pages)

        con_dict = {
            'tag':tag,
            'articles': tag_articles_list.object_list,
            'page': tag_articles_list,
            'page_range':page_range,
            'page_url': reverse('article:tag_articles',args=[tag.slug,])
        }

        return render(request, 'article/tag_articles.html', con_dict)

def all_tags(request):
    all_tags_list=Tag.objects.order_by('slug').all()
    con_dict={
        'all_tags':all_tags_list
    }
    return render(request,'article/all_tags.html',con_dict)


def visits_handler(request,article):
    last_view = request.session.get('article_{0}_last_view'.format(article.id))  # 获取最后一次浏览本站的时间last_view
    if last_view:
        last_visit_time = datetime.strptime(last_view[:-7], "%Y-%m-%d %H:%M:%S")
        if datetime.now() >= last_visit_time + timedelta(minutes=10):  # 判断如果最后一次访问网站的时间大于20分钟，则浏览量+1
            article.views += 1
            article.save()
            last_visit_time = datetime.now()
        else:
            last_visit_time=last_view
    else:
        article.views += 1
        article.save()
        last_visit_time =datetime.now()
    request.session['article_{0}_last_view'.format(article.id)] = str(last_visit_time)  # 更新session




def article_detail(request,article_id):
    article=get_object_or_404(Article,id=article_id)

    visits_handler(request,article)
    md = markdown.Markdown(extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        TocExtension(slugify=slugify),
    ])
    article.content=md.convert(article.content)

    comments=article.comments.order_by('post_time').all()

    con_dict={
        'article':article,
        'comments':comments,
        'toc':md.toc
    }

    return render(request,'article/article_detail.html',con_dict)

@login_required
def post_comment(request,article_id):
    if request.method=='POST':
        article = get_object_or_404(Article, id=article_id)
        author=request.user
        content=request.POST.get('content')
        c=Comment.objects.create(article=article,author=author,content=content)
        #评论成功后刷新即可
        return redirect(reverse('article:article_detail',args=[article_id,]))

@login_required
def profile(request):
    form=UserProfileForm()

    return render(request,'article/profile.html',{'form':form})