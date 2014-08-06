#coding=utf-8
import re
#[id, name, pid]
def sort_category(category_list,pid,row_start,level):
	row_num = len(category_list)
	tmp=[]
	for row_i in range(row_start,row_num):
		category = category_list[row_i]
		
		#print(row_i,row_start, level, pid,category, category[1]==pid, row_start<=row_num)
		if  category[2]==pid:
			
			#print(row_i,row_start, level)
			tmp=category
			category_list[row_i]=category_list[row_start]
			category_list[row_start]=tmp
			category_list[row_start][1]=level*'----'+category_list[row_start][1]
			category_list,row_start = sort_category(category_list,category[0],row_start+1,level+1)
			
	return category_list,row_start
	
	
def check_parent_category(id,pid,choice):
	level = 1000
	isvalid=True
	for aa in choice:
	
		if level<len(re.split(r'----',aa[1])):
			#sub category
			#print(aa)
			if pid==aa[0]:
				isvalid=False
		elif not level==1000:
			break
		
		if aa[0]==id:
			level = len(re.split(r'----',aa[1]))
			#print(aa[1])
	return isvalid

	
"""	
def report_sql(report_input, month_array):
	valid_user = report_input['username']
	sql = "select "
	count = 0
	for row in month_array:
		row_date = row -day(1)
		sql=sql+"SUM( CASE WHEN MONTH( jizhang_item.pub_date ) =MONTH('%s') AND 	
			YEAR( jizhang_item.pub_date ) =YEAR('%s') AND jizhang_category.id = jizhang_item.category.id THEN jizhang_item.price 
			ELSE 0  END ) AS '%s',"
		para[count]=row
		count=count+1
	

	start_date = report_input['start_date_year']."-".$report_input['start_date_mon']."-01";
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
"""
	
	
if __name__ == '__main__':
	
	#id, pid, name
	category_list=[{'id':2,'name':'收入','pid':0,'sum':['30','20']},{'id':6,'name':'lp股票收入','pid':5,'sum':['30','20']},{'id':5,'name':'lp收入','pid':2,'sum':['30','20']},{'id':4,'name':'汽车消费','pid':3,'sum':['30','20']}]
	
	tmp,row_start = sort_category(category_list,0,0,0)
	
	aa=[]
	for category in tmp:
		aa.extend((category["id"], category["sum"].extend(category["name"])))

	print(aa)

	id = 3
	choice=[('', '----------------'),
		 (1, '生活消费'),
		 (2, '----生活用品'),
		 (3, '----汽车消费'),
		 (4, '--------加油'),
		 (5, '--------汽车养护'),
		 (6, '--------停车过路'),
		 (7, '----医疗保健'),
		 (13, 'lg收入'),
		 (12, '----股票收入'),
		 (11, '----工资收入')]
 
	print(check_parent_category(id,5,choice))
	print(check_parent_category(id,7,choice))
