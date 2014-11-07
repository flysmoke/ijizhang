#coding=utf-8
#django package
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response,render ,get_object_or_404
from django.contrib.auth.models import User  
from django.contrib import messages
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required
import datetime
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import csv, json
from django.db.models import Sum, Count
from django.db import connection
from django.core.urlresolvers import reverse


from jizhang.views import split_page
from classroom.models import Room,Draw,Comment
from classroom.forms import RoomForm

PAGE_ITEM_NUM = 2

# item list view
@login_required
def index_room(request):

    if request.method == 'POST':
        del_id = request.POST.getlist('del_id')
        for item_id in del_id:
            del_item = get_object_or_404(Room, id=item_id)
            del_item.delete()
   
    item_list = Room.objects.order_by('-create_time')
    item_page,page_num_list = split_page(request, item_list, PAGE_ITEM_NUM)

    context = {'item_list': item_page,'username':request.user.username,'page_num_list':page_num_list}
    return render_to_response('classroom/index_room.html', context,context_instance=RequestContext(request))

    
# new item view	
@login_required	
def new_room(request):
    if request.method == 'POST':
        form = RoomForm(request.POST)

        if form.is_valid():
            room = form.save(commit=False)
            room.create_by_user = request.user
            room.draw_by_user = request.user            
            room.save()
            
            room.members.add(request.user)
            
            return HttpResponseRedirect("/classroom/index_room")
    else:
        form = RoomForm()

    context = {'form':form,'username':request.user.username}
    return render_to_response('classroom/new_room.html',RequestContext(request,context))

    
	
@login_required	
def edit_room(request,pk):
    if request.method == 'POST':
        form = RoomForm(data=request.POST)
        if form.is_valid():
            new_item = form.save()
            new_item.id=pk
            new_item.save()
            return HttpResponseRedirect("/classroom/index_room")
    else:
        item_list = get_object_or_404(Room, id=pk)
        form = RoomForm(instance=item_list)

    context = {'form':form,'username':request.user.username}
    return render_to_response('classroom/new_room.html',RequestContext(request,context))
    
@login_required
def detail_room(request,pk):

    room = get_object_or_404(Room, id=pk)

    context = {'room': room,'username':request.user.username}
    context['user_have_joined'] = room.members.filter(username=request.user.username)
    context['isCreator'] = room.create_by_user==request.user
    return render_to_response('classroom/detail_room.html', context,context_instance=RequestContext(request))

@login_required
def join_room(request, **kwargs):

    try:
        add_type = kwargs.get('add_type')
        pk = kwargs.get('room_id')
        room = get_object_or_404(Room,id=pk)  
        
        #返回ok状态，和更新的关注用户列表            
        if add_type == '1':
            room.members.add(request.user)
            
        elif add_type == '0':
            room.members.remove(request.user)
        else:
            assert False, 'add_type error'            
        
        #返回ok状态即可
        return HttpResponseRedirect(reverse("classroom:detail_room",args=(str(room.id),)))
    except Exception, e:
        return HttpResponseRedirect(reverse("classroom:index_room",args=()))

             
        
def room_comments(request, id):
        
    # only support get comments by ajax now
    if request.is_ajax():
        room = get_object_or_404(Room, id=id)
        data=[]
        
        if request.method == "GET":
            data = __generate_comments_json(room, request.user)
        elif request.method == "POST":
            comment_data = request.POST.get('comment')
            print comment_data
            comment = Comment(room=room, name=(comment_data), create_by_user=request.user)
            comment.save()
            print comment
            data = __generate_comments_json(room, request.user)
        
        return HttpResponse(data, mimetype="application/json") 
        
def __generate_comments_json(obj, user):
    comments_all = obj.comments.all().order_by('create_time')
    if comments_all.count()>8:
        comments = comments_all[comments_all.count()-8:]
    else:
        comments = comments_all
    json_comments = []
    
    for comment in comments:
        comment_user = comment.create_by_user
        delete_url = ""
        if user == comment.create_by_user:
            delete_url = "/%s/comments/%s/delete/" % (obj.id, comment.id)
        json_comments.append({"id": comment.id,
                             "room_id": obj.id,
                             "add_date": comment.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                             "text": comment.name,
                             "user_display_name": comment_user.username,
                             "delete_url": delete_url
                             })
    
    return json.dumps(json_comments)
    
    


def room_draws(request, id):
    
    # only support get comments by ajax now
    if request.is_ajax():
        room = get_object_or_404(Room, id=id)
        data=[]
        if request.method == "GET":
            data = __generate_draws_json(room, request.user) 
        elif request.method == "POST":
            draw_data = request.POST.get('draw')
            draw_color = request.POST.get('color')
            draw = Draw(room=room, name=str(draw_data), color = draw_color, create_by_user=request.user)
            draw.save()
            data = __generate_draws_json(room, request.user)
        
        return HttpResponse(data, mimetype="application/json") 
        
def __generate_draws_json(obj, user):
    draws = obj.draws.all().order_by('-create_time')
    json_comments = []
    for draw in draws:
        draw_user = draw.create_by_user
        json_comments.append({"id": draw.id,
                             "add_date": draw.create_time.strftime('%Y-%m-%d'),
                             "data": draw.name,
                             "color": draw.color,
                             "user_display_name": draw_user.username
                             })

    return json.dumps(json_comments)
    
    
    
def room_members(request, id):        
    # only support get comments by ajax now
    if request.is_ajax():
        room = get_object_or_404(Room, id=id)
        data=[]
        
        if request.method == "GET":
            data = __generate_members_json(room, request.user)
        
        return HttpResponse(data, mimetype="application/json")  
    
def __generate_members_json(obj, user):
    members = obj.members.all()
    json_comments = []
    for member in members:
        json_comments.append({"id": member.id,
                             "user_display_name": member.username
                             })

    return json.dumps(json_comments)
    
    
def clear_draws(request, id):    

    if request.is_ajax():
        if request.method == "POST":
            room = get_object_or_404(Room, id=id)
            if request.user.username == room.create_by_user.username:
                draws = room.draws.all()
                for draw in draws:
                    draw.delete()
                data={'success':'1'}
                return HttpResponse(json.dumps(data), mimetype="application/json") 
            else:
                data={'success':'0','err':u'clear draws must be creator'}
                return HttpResponse(json.dumps(data), mimetype="application/json")