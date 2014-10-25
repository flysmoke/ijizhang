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
import csv
from django.db.models import Sum, Count
from django.db import connection

#myApp package
from jizhang.models import Item, Category
from jizhang.forms import ItemForm, CategoryForm, NewCategoryForm, FindItemForm, UpLoadFileForm, ReportForm
from jizhang.data_format_func import sort_category, check_parent_category

P_CATEGORY_NULL_NAME = '------'
PAGE_ITEM_NUM = 10	
    
def split_page(request, data, page_item_num):
    p = Paginator(data , page_item_num)
    page = request.GET.get('page') # Get page
    try:
        item_page = p.page(page)
    except PageNotAnInteger:
        item_page = p.page(1)
    except EmptyPage:
        item_page = p.page(p.num_pages)       
    return item_page  
    
# item list view
@login_required
def index_item(request):

    if request.method == 'POST':
        del_id = request.POST.getlist('del_id')
        for item_id in del_id:
            del_item = get_object_or_404(Item, id=item_id)
            del_item.delete()
   
    item_list = Item.objects.filter(category__user__username=request.user.username).order_by('-pub_date')
    item_page = split_page(request, item_list, PAGE_ITEM_NUM)

    context = {'item_list': item_page,'username':request.user.username}
    return render_to_response('jizhang/index_item.html', context,context_instance=RequestContext(request))

@login_required
def index_price_item(request):

    if request.method == 'POST':
        del_id = request.POST.getlist('del_id')
        for item_id in del_id:
            del_item = get_object_or_404(Item, id=item_id)
            del_item.delete()
   
    item_list = Item.objects.filter(category__user__username=request.user.username).order_by('price')
    item_page = split_page(request, item_list, PAGE_ITEM_NUM)

    context = {'item_list': item_page,'username':request.user.username}
    return render_to_response('jizhang/index_item.html', context,context_instance=RequestContext(request))

	
	
# category list view
@login_required
def index_category(request):

    if request.method == 'POST':
        del_id = request.POST.getlist('del_id')
        for category_id in del_id:
            del_category = get_object_or_404(Category, id=category_id)
            del_category.delete()

    category_list = Category.objects.filter(user__username=request.user.username).order_by('p_category')
    context = {'category_list': category_list,'username':request.user.username}
    return render_to_response('jizhang/index_category.html', RequestContext(request,context))	

# first login auto generate category
@login_required
def first_login(request):

    if request.method == 'POST':
        del_id = request.POST.getlist('del_id')
        for category_id in del_id:
            del_category = get_object_or_404(Category, id=category_id)
            del_category.delete()
        return HttpResponseRedirect("/jizhang/index_category")
        
    category_list = Category.objects.filter(user__username=request.user.username).order_by('p_category')
    
    if not category_list:
        first_login_category(request.user.id)
        category_list = Category.objects.filter(user__username=request.user.username).order_by('p_category')
    
    context = {'category_list': category_list,'username':request.user.username}
    return render_to_response('jizhang/index_category.html', RequestContext(request,context))	

# new item view	
@login_required	
def new_item(request):
    if request.method == 'POST':
        form = ItemForm(request,data=request.POST)

        if form.is_valid():
            new_item = form.save()
            new_item.save()
            return HttpResponseRedirect("/jizhang")
    else:
        form = ItemForm(request,initial={'pub_date':timezone.now().date()})

    most_used_categorys = Category.objects.filter(user__username=request.user.username).annotate(num_items=Count('item')).filter(num_items__gt=1).order_by('-num_items')[:6]
    context = {'form':form,'username':request.user.username,'most_used_categorys':most_used_categorys}
    return render_to_response('jizhang/new_item.html',RequestContext(request,context))

	
# new category view		
@login_required	
def new_category(request):
    if request.method == 'POST':
        form = NewCategoryForm(request,data=request.POST)
        if form.is_valid():
            new_category = form.save(request)
            new_category.save()
            return HttpResponseRedirect("/jizhang/index_category")
    else:
        form = NewCategoryForm(request)
    context = {'form':form,'username':request.user.username}
    return render_to_response('jizhang/new_category.html',RequestContext(request,context))

	
@login_required	
def edit_item(request,pk):
    if request.method == 'POST':
        form = ItemForm(request,data=request.POST)
        if form.is_valid():
            new_item = form.save()
            new_item.id=pk
            new_item.save()
            return HttpResponseRedirect("/jizhang")
    else:
        item_list = get_object_or_404(Item, id=pk)
        form = ItemForm(request,instance=item_list)

    most_used_categorys = Category.objects.filter(user__username=request.user.username).annotate(num_items=Count('item')).filter(num_items__gt=1).order_by('-num_items')[:6]
    context = {'form':form,'username':request.user.username,'most_used_categorys':most_used_categorys}
    return render_to_response('jizhang/new_item.html',RequestContext(request,context))

	
@login_required	
def edit_category(request,pk):
    out_errors = []
    if request.method == 'POST':
        form = CategoryForm(request,data=request.POST)
        if form.is_valid():
            if not form.cleaned_data['p_category']:
                pid=0
            else:
                pid = form.cleaned_data['p_category'].id
            
            if check_parent_category(int(pk),pid,form.fields['p_category'].choices):
                new_category = form.save(request)
                new_category.id=int(pk)
                new_category.save()
                return HttpResponseRedirect("/jizhang/index_category")
            else:
                out_errors = "父类别不能和子类别重复!"
    else:
        category_list = get_object_or_404(Category, id=pk) 
        form = CategoryForm(request,instance=category_list)
    context = {'form':form,'username':request.user.username,'out_errors':out_errors}
    return render_to_response('jizhang/new_category.html',RequestContext(request,context))

	
@login_required	
def find_item(request):
    if request.method == 'POST':
        form = FindItemForm(data=request.POST)
        if form.is_valid():
            item_list = Item.objects.filter(pub_date__range=(form.cleaned_data['start_date'],form.cleaned_data['end_date']))
            return render_to_response('jizhang/index_item.html', RequestContext(request,{'item_list': item_list}))
    else:
        tmp_date = timezone.now()-datetime.timedelta(days=60)
        form = FindItemForm(initial={'start_date':tmp_date.date(),'end_date':timezone.now().date()})
    context = {'form':form,'username':request.user.username}
    return render_to_response('jizhang/find_item.html',RequestContext(request,context))


@login_required
def report_item(request):
    report_data={}
    
    if request.method == 'POST':
        form = ReportForm(data=request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            if form.cleaned_data['report_range']=='0':
                date_step = datetime.timedelta(days=30) 
            else:
                date_step = datetime.timedelta(days=365)
            
            #first filter username
            #report_query_user = Category.objects.filter(user__username=request.user.username)

            #second filter start and end date
            #report_query_date = []
            #for i in range(0,5):
            #    end_date = start_date+date_step
            #    report_query_date.append(report_query_user.filter(item__pub_date__range=(start_date,end_date)).annotate(Sum('item__price')))
            #    start_date = end_date+datetime.timedelta(days=1) 
            #third annotate sum
            #fouth data process to plot
            #report_data = report_query_date
    else:
        tmp_date = timezone.now()-datetime.timedelta(days=120)
        form = ReportForm(initial={'start_date':tmp_date.date()})
    
    context = {'form':form,'username':request.user.username,'report_data':report_data}
    return render_to_response('jizhang/report_item.html',RequestContext(request,context))		

    
    
def gb_encode(val):
    return (val.encode('gb2312'))
def gb_decode(val):
    return (val.decode('gb2312').encode('utf-8'))
    
    
@login_required
def export_to_item_csv(request):

    response = HttpResponse(content_type='text/csv')
    filename = 'export_item_'+datetime.datetime.now().strftime("%Y-%m-%d")+'.csv'
    response['Content-Disposition'] = 'attachment; filename="'+filename+'"'
    writer = csv.writer(response)



    writer.writerow((gb_encode(u'日期'),gb_encode(u'价格'),gb_encode(u'分类'),gb_encode(u'备注')))
    items = Item.objects.filter(category__user__username=request.user.username).order_by('pub_date')
    if not items:
        pass
    else:
        for item in items:
            writer.writerow((item.pub_date, item.price, gb_encode(item.category.name), gb_encode(item.comment)))

    return response

    
@login_required
def export_to_category_csv(request):

    response = HttpResponse(content_type='text/csv')
    filename = 'export_category_'+datetime.datetime.now().strftime("%Y-%m-%d")+'.csv'

    response['Content-Disposition'] = 'attachment; filename="'+filename+'"'
    writer = csv.writer(response)


    writer.writerow((gb_encode(u'父类名称'),gb_encode(u'类别名称'),gb_encode(u'是否收入')))
    categorys = Category.objects.filter(user__username=request.user.username).order_by('p_category')
    if not categorys:
        pass
    else:
        for category in categorys:
            if not category.p_category:
                writer.writerow((P_CATEGORY_NULL_NAME, gb_encode(category.name), category.isIncome))
            else:
                writer.writerow((gb_encode(category.p_category.name), gb_encode(category.name), category.isIncome))

    return response
    
    
def handle_uploaded_file_item(f):
    destination = open('upload/csv/name.csv','wb')
    for chunk in f.chunks(): 
        destination.write(chunk)
    destination.close()
    
    csv_file = open('upload/csv/name.csv','rb')
    reader = csv.reader(csv_file)
    i=0
    for line in reader:
        print line[0]+line[1]+line[2]+line[3]
        if i>0:
            category = Category.objects.filter(name=gb_decode(line[2]))
            if not category:
                pass
            else:
                data=Item(pub_date=datetime.datetime.strptime(line[0],"%Y-%m-%d"),
                    price=line[1], 
                    category = category[0], 
                    comment = gb_decode(line[3]))
                data.save()
        i=i+1
    csv_file.close()

    
def handle_uploaded_file_category(f, request):
    destination = open('upload/csv/name.csv','wb')
    for chunk in f.chunks(): 
        destination.write(chunk)
    destination.close()
    
    csv_file = open('upload/csv/name.csv','rb')
    reader = csv.reader(csv_file)
    i=0
    for line in reader:
        print line[0]+line[1]+line[2]
        if i>0:
            if line[0]==P_CATEGORY_NULL_NAME:
                data=Category(name=gb_decode(line[1]), 
                    isIncome = (line[2]=='True'),
                    user=request.user)
                
                data.save()
            else:
                pcategory = Category.objects.filter(name=gb_decode(line[0]))
                if not pcategory:
                    pass
                else:
                    data=Category(p_category = pcategory[0],
                        name=gb_decode(line[1]), 
                        isIncome = (line[2]=='True'),
                        user=request.user)
                    
                    data.save()                
     
        i=i+1
    csv_file.close()    
    
@login_required
def import_item_csv(request):

    if request.method == 'POST':
        form = UpLoadFileForm(request.POST,request.FILES)
        if form.is_valid():
            handle_uploaded_file_item(request.FILES['upLoadFile'])
            return HttpResponseRedirect("/jizhang")
           
    else:
        form = UpLoadFileForm()

    context = {'form':form,'username':request.user.username}
    return render_to_response('jizhang/import_item_csv.html', RequestContext(request,context))	

    
@login_required
def import_category_csv(request):

    if request.method == 'POST':
        form = UpLoadFileForm(request.POST,request.FILES)
        if form.is_valid():
            handle_uploaded_file_category(request.FILES['upLoadFile'], request)
            return HttpResponseRedirect("/jizhang/index_category")
           
    else:
        form = UpLoadFileForm()

    context = {'form':form,'username':request.user.username}
    return render_to_response('jizhang/import_category_csv.html', RequestContext(request,context))
    
    
    
"""
  
  
  "select sum(case when pub_date>='2014-05-01' and pub_date<='2014-05-30' then price else 0 end) as '5月收支',   sum(case when pub_date>='2014-06-01' and pub_date<='2014-06-30' then price else 0 end) as '6月收支',  category from jizhang_item group by category"
  
// generate the month array of start and end
function generate_month_array($report_input){
	$count=0;
	for($year = $report_input['start_date_year']; $year <=$report_input['end_date_year'];$year++){
		for($month=1;$month<=12;$month++){
			
			if($report_input['start_date_year']!=$report_input['end_date_year']){
				if($year== $report_input['start_date_year'] && $month>=$report_input['start_date_mon']){
					$month_array[$count]=$year."-".$month;
					$count++;
				}
				if($year== $report_input['end_date_year'] && $month<=$report_input['end_date_mon']){
					$month_array[$count]=$year."-".$month;
					$count++;
				}
				if($year< $report_input['end_date_year'] && $year> $report_input['start_date_year']){
					$month_array[$count]=$year."-".$month;
					$count++;
				}				
			}else{
				if($month<=$report_input['end_date_mon'] and $month>=$report_input['start_date_mon']){
					$month_array[$count]=$year."-".$month;
					$count++;
				}
			}
		}
	}
	return $month_array;
}

// generate sql from input date
function report_sql($report_input, $month_array){
	$valid_user = $_SESSION['valid_user'];
	$sql = "select ";
	$count = 0;
	foreach( $month_array as $row){
		$row_date = $row."-01";
		$sql.="SUM( CASE WHEN MONTH( t_account.account_date ) =MONTH('$row_date') AND 	
			YEAR( t_account.account_date ) =YEAR('$row_date') AND t_category.category_id = t_account.category_id THEN t_account.account_money 
			ELSE 0  END ) AS '$row',";
		$count++;
	}

	$start_date = $report_input['start_date_year']."-".$report_input['start_date_mon']."-01";
	if($report_input['end_date_mon']==12)
		$end_date = ($report_input['end_date_year']+1)."-01-01";
	else
		$end_date = $report_input['end_date_year']."-".($report_input['end_date_mon']+1)."-01";

	$sql .= "SUM( CASE WHEN t_account.account_date >= date('$start_date')
		AND t_account.account_date < date('$end_date') AND t_category.category_id = t_account.category_id
	  THEN t_account.account_money ELSE 0  END ) AS 'total',
		t_category.category_name, t_category.category_level, t_category.category_id, t_category.category_pid
		, t_category.is_income FROM t_account, t_category WHERE t_account.user_id = '$valid_user'
		";
	
	if($report_input['is_income']==2)
		$sql.="";
	else
		$sql.=" AND t_category.is_income=".$report_input['is_income']." ";
	
	$sql.="GROUP BY t_category.category_name WITH rollup";

	return $sql;

}




// generate display date from mysql date
function sort_sum_account($row_category,$category_pid,&$row_start, $month_array, $row_pid){
   $row_num = count($row_category);
   $tmp = array();
   for($row_i=$row_start;$row_i<$row_num;$row_i++){
    $value = $row_category[$row_i];
    if($value['category_pid']==$category_pid){
     $tmp = $row_category[$row_i];
     $row_category[$row_i]=$row_category[$row_start];
     $row_category[$row_start]=$tmp;
     
     //echo "<p><p> row_start=".$row_start.", row_pid=".$row_pid;
     //display_report_output_form($row_category, $month_array);
     
     //sum row_start to row_pid
     if($category_pid>0){
    		foreach($month_array as $month_row){
     			$row_category[$row_pid][$month_row]+=$row_category[$row_start][$month_row];
    		}
    		$row_category[$row_pid]['total']+=$row_category[$row_start]['total'];
   	 } 
   	 //echo "<p><p>row_start=".$row_start.", row_pid=".$row_pid;  
     //display_report_output_form($row_category, $month_array);
     $row_start++;
     $row_category = sort_sum_account($row_category,$value['category_id'],$row_start, $month_array,$row_pid);
     
     if($category_pid==0)
     	 $row_pid = $row_start;
     //echo "row_start=".$row_start.", row_pid=".$row_pid; 
   
    }
   }
   return $row_category;
}
  
  
 """
	
def first_login_category(userid):
    new_category=Category(name=u'工作收入',isIncome=True,user_id=userid)
    new_category.save()
    pid = new_category.id
    sub_category=Category(name=u'工资收入',isIncome=True,user_id=userid,p_category_id=pid)
    sub_category.save()
    sub_category=Category(name=u'股票收入',isIncome=True,user_id=userid,p_category_id=pid)
    sub_category.save()
    sub_category=Category(name=u'奖金收入',isIncome=True,user_id=userid,p_category_id=pid)
    sub_category.save()
    sub_category=Category(name=u'其他收入',isIncome=True,user_id=userid,p_category_id=pid)
    sub_category.save()
    
    new_category=Category(name=u'餐饮',isIncome=False,user_id=userid)
    new_category.save()
    pid = new_category.id
    sub_category=Category(name=u'早餐',isIncome=False,user_id=userid,p_category_id=pid)
    sub_category.save()
    sub_category=Category(name=u'午餐',isIncome=False,user_id=userid,p_category_id=pid)
    sub_category.save()
    sub_category=Category(name=u'晚餐',isIncome=False,user_id=userid,p_category_id=pid)
    sub_category.save()
    sub_category=Category(name=u'饮料水果',isIncome=False,user_id=userid,p_category_id=pid)    
    sub_category.save()
    sub_category=Category(name=u'零食',isIncome=False,user_id=userid,p_category_id=pid)     
    sub_category.save()
    
    new_category=Category(name=u'交通',isIncome=False,user_id=userid)
    new_category.save()
    pid = new_category.id
    sub_category=Category(name=u'公交地铁',isIncome=False,user_id=userid,p_category_id=pid)
    sub_category.save()
    sub_category=Category(name=u'加油',isIncome=False,user_id=userid,p_category_id=pid)
    sub_category.save()
    sub_category=Category(name=u'停车过路',isIncome=False,user_id=userid,p_category_id=pid)
    sub_category.save()
    sub_category=Category(name=u'汽车保养',isIncome=False,user_id=userid,p_category_id=pid)    
    sub_category.save()
    sub_category=Category(name=u'打的',isIncome=False,user_id=userid,p_category_id=pid)     
    sub_category.save()
    
    new_category=Category(name=u'购物',isIncome=False,user_id=userid)
    new_category.save()
    pid = new_category.id
    sub_category=Category(name=u'生活用品',isIncome=False,user_id=userid,p_category_id=pid)
    sub_category.save()
    sub_category=Category(name=u'衣裤鞋帽',isIncome=False,user_id=userid,p_category_id=pid)
    sub_category.save()
    sub_category=Category(name=u'化妆品',isIncome=False,user_id=userid,p_category_id=pid)
    sub_category.save()
    sub_category=Category(name=u'首饰手表',isIncome=False,user_id=userid,p_category_id=pid)    
    sub_category.save()
    sub_category=Category(name=u'宝宝用品',isIncome=False,user_id=userid,p_category_id=pid)     
    sub_category.save()    
    sub_category=Category(name=u'书籍报刊',isIncome=False,user_id=userid,p_category_id=pid)     
    sub_category.save() 
    
    new_category=Category(name=u'医疗',isIncome=False,user_id=userid)
    new_category.save()
    pid = new_category.id
    sub_category=Category(name=u'看病门诊',isIncome=False,user_id=userid,p_category_id=pid)
    sub_category.save()
    sub_category=Category(name=u'药店买药',isIncome=False,user_id=userid,p_category_id=pid)
    sub_category.save()
    sub_category=Category(name=u'保健品',isIncome=False,user_id=userid,p_category_id=pid)
    sub_category.save()