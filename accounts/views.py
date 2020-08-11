from django.shortcuts import render, redirect 
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from .models import *
from .forms import OrderForm, CreateUserForm, CustomerForm
from .filters import OrderFilter
from .decorators import unauthenticated_user, allowed_users, admin_only

@unauthenticated_user
def registerPage(request):

	form = CreateUserForm()
	if request.method == 'POST':
		form = CreateUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			username = form.cleaned_data.get('username')
			messages.success(request, 'Account was created for ' + username)

			return redirect('login')
		

	context = {'form':form}
	return render(request, 'accounts/register.html', context)

@unauthenticated_user
def loginPage(request):

	if request.method == 'POST':
		username = request.POST.get('username')
		password =request.POST.get('password')

		user = authenticate(request, username=username, password=password)

		if user is not None:
			login(request, user)
			return redirect('home')
		else:
			messages.info(request, 'Username OR password is incorrect')

	context = {}
	return render(request, 'accounts/login.html', context)

def logoutUser(request):
	logout(request)
	return redirect('login')

@login_required(login_url='login')
@admin_only
def home(request):
	orders = Order.objects.all()
	customers = Customer.objects.all()

	paginator = Paginator(orders, 5)
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)
	paginator1 = Paginator(customers, 5)
	page_number1 = request.GET.get('page')
	page_obj1 = paginator.get_page(page_number)

	total_customers = customers.count()

	total_orders = orders.count()
	delivered = orders.filter(status='Delivered').count()
	pending = orders.filter(status='Pending').count()
	out = orders.filter(status='Out for delivery').count()

	context = {'orders':orders, 'customers':customers,
	'total_orders':total_orders,'out':out,'delivered':delivered,
	'pending':pending,'page_obj':page_obj }

	return render(request, 'accounts/dashboard.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer'])
def userPage(request):
	orders = request.user.customer.order_set.all()

	total_orders = orders.count()
	delivered = orders.filter(status='Delivered').count()
	pending = orders.filter(status='Pending').count()

	context = {'orders':orders, 'total_orders':total_orders,
	'delivered':delivered,'pending':pending}
	return render(request, 'accounts/user.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['customer','admin'])
def accountSettings(request):
	customer = request.user.customer
	form = CustomerForm(instance=customer)

	if request.method == 'POST':
		form = CustomerForm(request.POST, request.FILES,instance=customer)
		if form.is_valid():
			form.save()


	context = {'form':form}
	return render(request, 'accounts/account_settings.html', context)




@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def products(request):
	products = Product.objects.all()
	paginator = Paginator(products, 5)
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)

	return render(request, 'accounts/products.html', {'products':products,'page_obj':page_obj})

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def customer(request, pk_test):
	customer = Customer.objects.get(id=pk_test)
	totalprice=0
	
	orders = customer.order_set.all()
	for i in orders:
		totalprice=totalprice+int(i.product.price)

	order_count = orders.count()

	myFilter = OrderFilter(request.GET, queryset=orders)
	orders = myFilter.qs 

	context = {'customer':customer, 'orders':orders, 'order_count':order_count,
	'myFilter':myFilter,'totalprice':totalprice}
	return render(request, 'accounts/customer.html',context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def createCustomer(request):

	form = CustomerForm()
	if request.method == 'POST':

		form = CustomerForm(request.POST,request.FILES)
		if form.is_valid():
			form.save()
			return redirect('/')

	context = {'form':form}
	return render(request, 'accounts/customer_form.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updateCustomer(request, pk):
	customer = Customer.objects.get(id=pk)
	cust=customer.id
	form = CustomerForm(instance=customer)
	if request.method == 'POST':

		form = CustomerForm(request.POST, request.FILES,instance=customer)
		if form.is_valid():
			form.save()
			return redirect('/customer/%s'%cust)

	context = {'form':form}
	return render(request, 'accounts/customer_form.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deleteCustomer(request, pk):
	customer = Customer.objects.get(id=pk)
	cust=customer.id
	if request.method == "POST":
		customer.delete()
		return redirect('home')

	context = {'item':customer}
	return render(request, 'accounts/DeleteCustomer.html', context)


@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','customer'])
def createOrder(request, pk):
	OrderFormSet = inlineformset_factory(Customer, Order, fields=('product', 'status'), extra=10 )
	customer = Customer.objects.get(id=pk)
	cust=customer.id
	formset = OrderFormSet(queryset=Order.objects.none(),instance=customer)
	#form = OrderForm(initial={'customer':customer})
	if request.method == 'POST':
		form = OrderForm(request.POST)
		formset = OrderFormSet(request.POST, instance=customer)
		if formset.is_valid():
			formset.save()
			return redirect('/customer/%s'%cust)

	context = {'form':formset}
	return render(request, 'accounts/order_form.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','customer'])
def updateOrder(request, pk):
	order = Order.objects.get(id=pk)
	customer=order.customer.id
	print(customer)
	form = OrderForm(instance=order)
	print('ORDER:', order)
	if request.method == 'POST':

		form = OrderForm(request.POST, instance=order)
		if form.is_valid():
			form.save()
			return redirect('/customer/%s'%customer)

	context = {'form':form}
	return render(request, 'accounts/update_form.html', context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin','customer'])
def deleteOrder(request, pk):
	order = Order.objects.get(id=pk)
	customer=order.customer.id
	if request.method == "POST":
		order.delete()
		return redirect('/customer/%s'%customer)

	context = {'item':order}
	return render(request, 'accounts/delete.html', context)

@login_required(login_url='login')
def resultsData(request):
	data=[]
	totalprice=0
	customers = Customer.objects.all()
	for customer in customers:
		orders = customer.order_set.all()
		for i in orders:
			totalprice=totalprice+int(i.product.price)
		data.append({customer.name:totalprice})
		totalprice=0
	print(data)
	return JsonResponse(data,safe=False)
	
@login_required(login_url='login')
def resultsOrders(request):
	


	orders = Order.objects.all()
	products = Product.objects.values_list('name', flat=True)

	dic = dict.fromkeys(products, 0) 
	
	for order in orders:	
		dic[order.product.name] = int(dic.get(order.product.name))+1


	return JsonResponse(dic,safe=False)
