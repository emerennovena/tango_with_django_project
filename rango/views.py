from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
from django.urls import reverse
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm
from rango.forms import UserForm
from rango.forms import UserProfileForm
from django.shortcuts import redirect
from rango.forms import PageForm

def show_category(request, category_name_slug):
	context_dict = {}

	try:
		category = Category.objects.get(slug=category_name_slug)
		pages = Page.objects.filter(category=category)
		context_dict['pages'] = pages
		context_dict['category'] = category

	except Category.DoesNotExist:
		context_dict['category'] = None
		context_dict['pages'] = None

	return render(request, 'rango/category.html', context=context_dict)

def index(request):
	category_list = Category.objects.order_by('-likes')[:5]
	pages = Page.objects.order_by('-views')[:5]

	context_dict = {}
	context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
	context_dict['categories'] = category_list
	context_dict['pages'] = pages

	return render(request, 'rango/index.html', context=context_dict)

def about(request):
	context = { 'MEDIA_URL': settings.MEDIA_URL, }
	return render(request, 'rango/about.html', context)

def add_category(request):
	form = CategoryForm()

	if request.method == 'POST':
		form = CategoryForm(request.POST)

		if form.is_valid():
			form.save(commit=True)
			return redirect('/rango/')
		else:
			print(form.errors)

	return render(request, 'rango/add_category.html',{'form': form})

def add_page(request, category_name_slug):
	try:
		category = Category.objects.get(slug=category_name_slug)
	except:
		category = None

	if category is None:
		return redirect('/rango/')

	form = PageForm()

	if request.method == 'POST':
		form = PageForm(request.POST)

		if form.is_valid():
			if category:
				page = form.save(commit=False)
				page.category = category
				page.views = 0
				page.save()

				return redirect(reverse('rango:show_category', kwargs={'category_name_slug':category_name_slug}))
			else:
				print(form.errors)

	context_dict = {'form': form, 'category': category}
	return render(request, 'rango/add_page.html', context=context_dict)

def register(request):
	registered = False
	if request.method == 'POST':
		user_form = UserForm(request.POST)
		profile_form = UserProfileForm(request.POST)
		if user_form.is_valid() and profile_form.is_valid():
			user = user_form.save()
			user.set_password(user.password)
			user.save()
			profile = profile_form.save(commit=False)
			profile.user = user
			if 'picture' in request.FILES:
				profile.picture = request.FILES['picture']
				profile.save()
				registered = True
			else:
				print(user_form.errors, profile_form.errors)
	else:
		user_form = UserForm()
		profile_form = UserProfileForm()

	return render(request,
		'rango/register.html',
			 context={'user_form': user_form,
					  'profile_form': profile_form,
					  'registered': registered})

def user_login(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')
		user = authenticate(username=username, password=password)
		if user:
			if user.is_active:
				login(request, user)
				return redirect(reverse('rango:index'))
			else:
				return HttpResponse('Your Rango account is disabled.')
		else:
			print(f"Invalid login details: {username}, {password}")
			return HttpResponse("Invalid login details supplied")
	else:
		return render(request, 'rango/login.html')




