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
from django.db.models import Sum
from django.db import connection

#myApp package
from jizhang.models import Item, Category
from jizhang.forms import ItemForm, CategoryForm, NewCategoryForm, FindItemForm
from jizhang.data_format_func import sort_category, check_parent_category

	
# item list view
@login_required
def index_item(request):
	if request.method == 'POST':
		del_id = request.POST.getlist('del_id')
		for item_id in del_id:
			del_item = Item.objects.filter(id=item_id)
			del_item.delete()
	
	item_list = Item.objects.filter(category__user__username=request.user.username).order_by('-pub_date')
	#one page include 10 items
	p = Paginator(item_list , 10)
	page = request.GET.get('page') # Get page
	try:
		item_page = p.page(page)
	except PageNotAnInteger:
		item_page = p.page(1)
	except EmptyPage:
		item_page = p.page(p.num_pages)
	
	context = {'item_list': item_page,'username':request.user.username}
	return render_to_response('index_item.html', context,context_instance=RequestContext(request))


	
	
# category list view
@login_required
def index_category(request):

	if request.method == 'POST':
		del_id = request.POST.getlist('del_id')
		for category_id in del_id:
			del_category = Category.objects.filter(id=category_id)
			del_category.delete()

	category_list = Category.objects.filter(user__username=request.user.username).order_by('p_category')
	context = {'category_list': category_list,'username':request.user.username}
	return render_to_response('index_category.html', RequestContext(request,context))	

	
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
	
	context = {'form':form,'username':request.user.username}
	return render_to_response('new_item.html',RequestContext(request,context))

	
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
	return render_to_response('new_category.html',RequestContext(request,context))

	
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
		item_list = Item.objects.filter(id=pk)
		form = ItemForm(request,instance=item_list[0])
	context = {'form':form,'username':request.user.username}
	return render_to_response('new_item.html',RequestContext(request,context))

	
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
		category_list = Category.objects.filter(id=pk)
		form = CategoryForm(request,instance=category_list[0])
	context = {'form':form,'username':request.user.username,'out_errors':out_errors}
	return render_to_response('new_category.html',RequestContext(request,context))

	
@login_required	
def find_item(request):
	if request.method == 'POST':
		form = FindItemForm(data=request.POST)
		if form.is_valid():
			item_list = Item.objects.filter(pub_date__range=(form.cleaned_data['start_date'],form.cleaned_data['end_date']))
			return render_to_response('index_item.html', RequestContext(request,{'item_list': item_list}))
	else:
		tmp_date = timezone.now()-datetime.timedelta(days=60)
		form = FindItemForm(initial={'start_date':tmp_date.date(),'end_date':timezone.now().date()})
	context = {'form':form,'username':request.user.username}
	return render_to_response('find_item.html',RequestContext(request,context))

	
	

@login_required
def report_item(request):
	
	cursor = connection.cursor()
	cursor.execute("select \
        sum(case when pub_date>=u'2014-05-01' and pub_date<u'2014-06-01' then price else 0 end) as u'5月开支', \
		sum(case when pub_date>=u'2014-06-01' and pub_date<u'2014-07-01' then price else 0 end) as u'6月开支', \
		jizhang_category.name,jizhang_category.id, jizhang_category.p_category_id from jizhang_item,jizhang_category \
		where jizhang_category.id=jizhang_item.category_id and jizhang_category.user_id = %s group by category_id",[request.user.id])
	
	aa=[]
	for category in  cursor.fetchall():
		num = len(category)
		if not category[num-1]:
			aa.extend([ [category[num-2],  category[num-3], 0, category[0:num-3]]])
		else:
			aa.extend([ [category[num-2],  category[num-3], category[num-1], category[0:num-3]]])
		print(aa)
	category_sort,row_start = sort_category(aa,0,0,0)
	
	bb=[]	
	for category in category_sort:
		list_sum = [str(x) for x in category[3]]
		list_sum.append(category[1])
		bb.append(list_sum)

	
	context = {'username':request.user.username,'hello2you':'This function is coming soon!','category_list':bb}
	return render_to_response('report_item.html',RequestContext(request,context))		

def gb2312(val):
    return (val.encode('gb2312'))
    
@login_required
def export_to_item_csv(request):

	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="export_item.csv"'
	writer = csv.writer(response)



	writer.writerow((gb2312(u'日期'),gb2312(u'价格'),gb2312(u'分类'),gb2312(u'备注')))
	for item in Item.objects.filter(category__user__username=request.user.username).order_by('pub_date'):
		writer.writerow((item.pub_date, item.price, gb2312(item.category.name), gb2312(item.comment)))

	return response
	
	
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
