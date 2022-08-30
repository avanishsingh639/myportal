import requests
from django.shortcuts import render, redirect
from .forms import *
from django.contrib import messages
from django.views import generic
from django.contrib.auth.decorators import login_required

# Create your views here.

def home(request):
    return render(request, 'dashboard/home.html')


@login_required
def notes(request):
    if request.method == "POST":
        form = NotesForm(request.POST)
        if form.is_valid():
            notes = Notes(user=request.user, title=request.POST['title'], description=request.POST['description'])
            notes.save()
            messages.success(request, f"Notes Added from {request.user.username} Successfully!")
            return redirect('notes')
    else:
        form = NotesForm()

    notes = Notes.objects.filter(user=request.user)
    context = {'notes': notes, 'form': form}
    return render(request, 'dashboard/notes.html', context)


@login_required
def delete_note(request, pk=None):
    Notes.objects.get(id=pk).delete()
    return redirect('notes')


class NotesDetailView(generic.DetailView):
    model = Notes


@login_required
def homework(request):
    if request.method == "POST":
        form = HomeworkForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST['is_finished']
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False

            homeworks = Homework(user=request.user, subject=request.POST['subject'], title=request.POST['title'], description=request.POST['description'], due=request.POST['due'], is_finished=finished)
            homeworks.save()
            messages.success(request, f"Homeworks Added from {request.user.username} Successfully!")
            return redirect('homework')
    else:
        form = HomeworkForm()

    homework = Homework.objects.filter(user=request.user).order_by('due')
    if len(homework) == 0:
        homework_done = True
    else:
        homework_done = False
    context = {'homeworks' : homework, 'homeworks_done' : homework_done, 'form' : form}
    return render(request, 'dashboard/homework.html', context)


@login_required
def update_homework(request, pk=None):
    homework = Homework.objects.get(id=pk)
    if homework.is_finished == True:
        homework.is_finished = False
    else:
        homework.is_finished = True
    homework.save()
    return redirect('homework')


@login_required
def delete_homework(request, pk=None):
    Homework.objects.get(id=pk).delete()
    return redirect('homework')


@login_required
def todo(request):
    if request.method == "POST":
        form = TodoForm(request.POST)
        if form.is_valid():
            try:
                finished = request.POST['is_finished']
                if finished == 'on':
                    finished = True
                else:
                    finished = False
            except:
                finished = False

            todo = Todo(user=request.user, title=request.POST['title'], is_finished=finished)
            todo.save()
            messages.success(request, f"Todo Added from {request.user.username} Successfully!")
            return redirect('todo')
    else:
        form = TodoForm()

    todo = Todo.objects.filter(user = request.user)
    if len(todo) == 0:
        todo_done = True
    else:
        todo_done = False
    context = {'todos':todo, 'form':form, 'todo_done':todo_done}
    return render(request, 'dashboard/todo.html', context)


@login_required
def update_todo(request, pk=None):
    todo = Todo.objects.get(id=pk)
    if todo.is_finished == True:
        todo.is_finished = False
    else:
        todo.is_finished = True
    todo.save()
    return redirect('todo')


@login_required
def delete_todo(request, pk=None):
    Todo.objects.get(id=pk).delete()
    return redirect('todo')


def books(request):
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = 'https://www.googleapis.com/books/v1/volumes?q=' + text
        r = requests.get(url)
        answer = r.json()

        result_list = []
        for i in range(10):
            result_dict = {
                'title':answer['items'][i]['volumeInfo'].get('title'),
                'subtitle': answer['items'][i]['volumeInfo'].get('subtitle'),
                'description': answer['items'][i]['volumeInfo'].get('description'),
                'categories': answer['items'][i]['volumeInfo'].get('categories'),
                'count': answer['items'][i]['volumeInfo'].get('pageCount'),
                'rating': answer['items'][i]['volumeInfo'].get('averageRating'),
                'preview': answer['items'][i]['volumeInfo'].get('previewLink')
            }
            if answer['items'][i]['volumeInfo'].get('imageLinks') != None:
                result_dict['thumbnail'] = answer['items'][i]['volumeInfo'].get('imageLinks').get('thumbnail')
            result_list.append(result_dict)
        context = {'form':form, 'results':result_list}
        return render(request, 'dashboard/books.html', context)

    else:
        form = DashboardForm()

    context = {'form':form}
    return render(request, 'dashboard/books.html', context)


def dictionary(request):
    if request.method == 'POST':
        form = DashboardForm(request.POST)
        text = request.POST['text']
        url = 'https://api.dictionaryapi.dev/api/v2/entries/en_US/' + text
        r = requests.get(url)
        answer = r.json()

        try:
            phonetics = answer[0]['phonetics'][1]['text']
            audio = answer[0]['phonetics'][1]['audio']
            definition = answer[0]['meanings'][0]['definitions'][0]['definition']
            example = answer[0]['meanings'][0]['definitions'][0]['example']
            synonyms = answer[0]['meanings'][0]['synonyms']

            context = {'form':form, 'input':text, 'phonetics':phonetics, 'audio':audio, 'definition':definition, 'example':example, 'synonyms':synonyms}
        except:
            context = {'form': form, 'input':''}
        return render(request, 'dashboard/dictionary.html', context)
    else:
        form = DashboardForm()
        context = {'form':form}
    return render(request, 'dashboard/dictionary.html', context)

def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"Account created for {username} Successfully!")
            return redirect('login')
    else:
        form = UserRegistrationForm()
    context = {'form':form}
    return render(request, 'dashboard/register.html', context)


@login_required
def profile(request):
    homeworks = Homework.objects.filter(is_finished=False, user=request.user).order_by('due')
    todos = Todo.objects.filter(is_finished=False, user=request.user)

    if len(homeworks) == 0:
        homework_done = True
    else:
        homework_done = False

    if len(todos) == 0:
        todo_done = True
    else:
        todo_done = False

    context = {'homeworks':homeworks, 'todos':todos, 'homework_done':homework_done, 'todo_done':todo_done}

    return render(request, 'dashboard/profile.html', context)


@login_required
def profile_update_homework(request, pk=None):
    homework = Homework.objects.get(id=pk)
    if homework.is_finished == True:
        homework.is_finished = False
    else:
        homework.is_finished = True
    homework.save()
    return redirect('profile')


@login_required
def profile_update_todo(request, pk=None):
    todo = Todo.objects.get(id=pk)
    if todo.is_finished == True:
        todo.is_finished = False
    else:
        todo.is_finished = True
    todo.save()
    return redirect('profile')




