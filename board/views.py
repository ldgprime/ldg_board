from django.shortcuts import render,redirect

from board.models import Board,Comment,Movie

from django.views.decorators.csrf import csrf_exempt
import os
from django.utils.http import urlquote
from django.http.response import HttpResponse, HttpResponseRedirect
from django.db.models import Q
import math
from board import bigdataPro
from django.db.models import Avg, Sum
import pandas as pd

UPLOAD_DIR="e:/upload/"
# Create your views here.

@csrf_exempt
def list1(request):
    try:
        search_option=request.POST['search_option']
    except:
        search_option=""
    
    try:
        search=request.POST['search']
    except:
        search=""
    
    if search_option=="all":
        boardCount=Board.objects.filter(
            Q(writer__contains=search) |
            Q(title__contains=search) |
            Q(content__contains=search)).count()
    elif search_option=='writer':
        boardCount=Board.objects.filter(writer__contains=search).count()
    elif search_option=='title':
        boardCount=Board.objects.filter(title__contains=search).count()
    elif search_option=='content':
        boardCount=Board.objects.filter(content__contains=search).count()
    else:
        boardCount=Board.objects.all().count()
    
    try:
        start=int(request.GET['start'])
    except:
        start=0
        
    page_size=10
    block_size=10
    end=start+page_size
    total_page=math.ceil(boardCount/page_size)
    current_page=math.ceil((start+1)/page_size)
    start_page=math.floor((current_page-1)/block_size)*block_size+1
    end_page=start_page+block_size-1
    
    if end_page>total_page:
        end_page=total_page
    
    if start_page>=block_size:
        prev_list=(start_page-2)*page_size
    else:
        prev_list=0
    
    if end_page<total_page:
        next_list=end_page*page_size
    else:
        next_list=0
    
    if search_option=="all":
        boardList=Board.objects.filter(
            Q(writer__contains=search) |
            Q(title__contains=search) |
            Q(content__contains=search)).order_by('-idx')[start:end]
    elif search_option=='writer':
        boardList=Board.objects.filter(writer__contains=search).order_by('-idx')[start:end]
    elif search_option=='title':
        boardList=Board.objects.filter(title__contains=search).order_by('-idx')[start:end]
    elif search_option=='content':
        boardList=Board.objects.filter(content__contains=search).order_by('-idx')[start:end]
    else:
        boardList=Board.objects.all().order_by('-idx')[start:end]
        
    links=[]
    for i in range(start_page, end_page+1):
        page_start=(i-1)*page_size
        links.append("<a href='?start="+str(page_start)+"'>"+str(i)+"</a>")
        
    return render(request, "list.html",
                  {"boardList":boardList,
                   "boardCount":boardCount,
                   "search_option":search_option,
                   "search":search,
                   "range":range(start_page-1, end_page),
                   "start_page":start_page,
                   "end_page":end_page,
                   "block_size":block_size,
                   "total_page":total_page,
                   "priv_list":prev_list,
                   "next_list":next_list,
                   "links":links})
         
        


def list(request):
    boardCount=Board.objects.count()
    boardList=Board.objects.all().order_by("-idx")
    return render(request,'list.html',
                  {"boardList":boardList, "boardCount":boardCount})
    
def write(request):
    return render(request,'write.html')

@csrf_exempt
def insert(request):
    fname=""
    fsize=0
    if "file" in request.FILES:
        file=request.FILES['file']
        fname=file.name
        fsize=file.size
        pf=open("%s%s"%(UPLOAD_DIR,fname),"wb")
        for chunk in file.chunks():
            pf.write(chunk)
        pf.close()
        
    dto=Board(writer=request.POST['writer'],
              title=request.POST['title'],
              content=request.POST['content'],
              filename=fname, filesize=fsize)
    dto.save()
    return redirect("/list")

def download(request):
    id=request.GET['idx']
    dto=Board.objects.get(idx=id)
    path=UPLOAD_DIR+dto.filename
    filename=os.path.basename(path)
    filename=filename.encode('utf-8')
    filename=urlquote(filename)
    with open(path, 'rb') as file:
        response=HttpResponse(file.read(), content_type="application/octet-stream")
        response['Content-Disposition']=\
        "attachment;filename*=UTF-8''{0}".format(filename)
        dto.down_up()
        dto.save()
        return response

def detail(request):
    id=request.GET['idx']
    dto=Board.objects.get(idx=id)
    dto.hit_up()
    dto.save()
    
    commentList=Comment.objects.filter(board_idx=id).order_by("-idx")
    
    filesize="%.2f" %(dto.filesize/1024)
    return render(request,'detail.html',
                  {'dto':dto, 'filesize':filesize, 'commentList':commentList})

@csrf_exempt        
def update(request):
    id=request.POST['idx']
    dto_src=Board.objects.get(idx=id)
    fname=dto_src.filename
    fsize=0
    if "file" in request.FILES:
        file=request.FILES['file']
        fname=file.name
        fsize=file.size
        pf=open("%s%s"%(UPLOAD_DIR,fname),"wb")
        for chunk in file.chunks():
            pf.write(chunk)
        pf.close()
        
    dto_new=Board(idx=id,writer=request.POST['writer'],
                  title=request.POST['title'],
                  content=request.POST['content'],
                  filename=fname,filesize=fsize)
    dto_new.save()
    return redirect("/")

@csrf_exempt
def delete(request):
    id=request.POST['idx']
    Board.objects.get(idx=id).delete()
    return redirect("/list")

@csrf_exempt
def reply_insert(request):
    id=request.POST['idx']
    dto=Comment(board_idx=id,
                writer=request.POST['writer'],
                content=request.POST['content'])
    dto.save()
    return HttpResponseRedirect("detail?idx="+id)

def movie_save(request):
    data=[]
    bigdataPro.movie_crawling(data)
    for row in data:
        dto=Movie(title=row[0], point=int(row[1]),content=row[2])
        dto.save()
    return redirect("/")

def main(request):
    return render(request,'main.html')

def chart(request):
    #sql='select title,avg(point) points from board_movie group by title'
    #data=Movie.objects.raw(sql)
    data=Movie.objects.values('title').annotate(point_avg=Avg('point'))[0:10]
    df=pd.DataFrame(data)
    bigdataPro.makeGraph(df.title, df.point_avg)
    return render(request,"chart.html",{"data":data})

def ct_map(request):
    bigdataPro.cctv_map()
    return render(request, "map/map01.html")

def wordcloud(request):
    content=Movie.objects.values('content')
    df=pd.DataFrame(content)
    bigdataPro.saveWordCloud(df.content)
    return render(request,'wordcloud.html',{'content':df.content})

    






     
        
        
   
   
   
   
   
   
   
   
   
   
        
        
        
        
        
    
