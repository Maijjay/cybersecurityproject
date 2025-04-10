from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db import connection

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from dashboard.models import Memo
from django.contrib.auth.models import User


def home(request):
    memos = Memo.objects.filter(user=request.user)
    return render(request, 'dashboard/home.html', {'memos': memos})
    
@login_required
def memo_create(request):
    if request.method == 'POST':
        title = request.POST['title']
        content = request.POST['content']

        Memo.objects.create(title=title, content=content, user=request.user)

        return redirect('home')

    return render(request, 'dashboard/memo_create.html')

# 1. Broken Access Control - flaw is that there is no access control and non-admins can access the page
@login_required
def admin_dashboard(request):
    # Fix is to validate that the user is in fact an admin 
    # if not request.user.is_superuser:
    #    return render(request, 'dashboard/admin_dashboard_no_permission.html')
    return render(request, 'dashboard/admin_dashboard.html')

# 2. SQL -injection - flaw is that there is a vulnerability inserting the uers input straight into the SQL query.
def search(request):
    query = request.GET.get('q', '')

    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM dashboard_memo WHERE title LIKE '%{query}%' OR content LIKE '%{query}%'")
        fetch_results = cursor.fetchall()

    results = [
        {'title': result[1], 'content': result[2]}
        for result in fetch_results
    ]

    # Fix is to use Django ORM, that protects form the SQL-injection
    # results = Memo.objects.filter(title__icontains=query) | Memo.objects.filter(content__icontains=query)

    return render(request, 'dashboard/search_results.html', {'results': results})


# 3. Insecure design - flaw is that this page is located only in the admins page, but the url doesn't actuallycheck if user is admin. 
#    So if a non-admin user guesses the url, they can access it, but otherwise they cannot find this page from the website.

def is_admin(user):
    return user.is_superuser

@login_required
def user_list(request):

    # Fix is that we check that the user going to the page is an admin here too, otherwise we redirect to home.
    # if not is_admin(request.user): 
    #    messages.error(request, "You do not have permission to view this page.")
    #    return redirect('home') 
    

    users = User.objects.all()
    return render(request, 'dashboard/user_list.html', {'users': users})        