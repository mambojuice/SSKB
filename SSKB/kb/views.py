import datetime
import sqlite3
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from django.utils.html import strip_tags
from django.db.models.functions import Lower
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.contrib.auth.decorators import login_required
from .models import Folder, Article, History, FolderPerm

# Display login form
def login(request):
    return render(request, 'kb/login.html')


# Do login
def login_do(request):
    username = request.POST['username']
    passwd = request.POST['password']

    user = authenticate(request, username=username, password=passwd)
    if user is not None:
        django_login(request, user)
        return HttpResponseRedirect(reverse('kb:index'))
    else:
        context = {
            'errormsg': 'Unable to authenticate! Please check your username and password.'
        }
        return render(request, 'kb/login.html', context)

# Logout
@login_required(login_url='kb:login')
def logout(request):
    django_logout(request)
    return HttpResponseRedirect(reverse('kb:index'))


# Display default page
@login_required(login_url='kb:login')
def index(request):
    Folder.init()
    root = Folder.home_folder()
    top_folders = Folder.objects.filter(parent=root).order_by('name')
    context = {
        'title': 'Home',
        'this_folder': root,
        'user_can_write': root.user_can_write(request.user),
        'show_sidebar': True,
        'show_breadcrumbs': True,
    }
    return render(request, 'kb/index.html', context)


# View articles and/or subfolders within the selected folder
@login_required(login_url='kb:login')
def folder(request, folder_id):
    this_folder = get_object_or_404(Folder, pk=folder_id)

    # Check user permissions
    if this_folder.user_can_read(request.user):

        # Redirect to Index for root folder
        if (this_folder == Folder.home_folder()):
            return HttpResponseRedirect(reverse('kb:index'))

        # Not root folder, display articles and subfolders
        subfolders = Folder.objects.filter(parent=folder_id).order_by(Lower('name'))
        articles = Article.objects.filter(folder=this_folder)
        context = {
            'title': this_folder.name,
            'this_folder': this_folder,
            'articles': articles,
            'user_can_write': this_folder.user_can_write(request.user),
            'show_sidebar': True,
            'show_breadcrumbs': True,
        }
        return render(request, 'kb/folder.html', context)

    else:
        messages.error(request,'You do not have permission to view this folder!')
        return HttpResponseRedirect(reverse('kb:index'))


# Create a new folder within a folder or root
@login_required(login_url='kb:login')
def folder_new(request, folder_id):
    this_folder = Folder.objects.get(pk=folder_id)

    context = {
        'title': 'Add New Folder',
        'this_folder': this_folder,
        'show_breadcrumbs': True,
    }
    return render(request, 'kb/folder_new.html', context)


# Save the new folder object
@login_required(login_url='kb:login')
def folder_add(request, folder_id):
    # Double-check that parent folder exists
    folder_parent = get_object_or_404(Folder, pk=folder_id)

    # Sanitize name of new folder
    folder_name = strip_tags(request.POST['folder_name'])   # Remove any HTML
    folder_name = folder_name.strip()                       # Remove any whitespace at beginning/end

    # Check that a name was actually provided
    if folder_name == '':
        messages.error(request, "Folder name must be specified!")
        context = {
            'title': 'Add New Folder',
            'this_folder': folder_parent,
            'show_breadcrumbs': True,
        }
        return render(request, 'kb/folder_new.html', context)
    else:
        # Create new folder
        new_folder = Folder(name=folder_name, parent=folder_parent)
        new_folder.save()

        # Create default Permissions
        new_folder_perms = FolderPerm(folder=new_folder, group=None, mode='R')
        new_folder_perms.save()

        # Redirect browser to newly created folder
        return HttpResponseRedirect(reverse('kb:folder', args=(new_folder.id,)))
    endif


@login_required(login_url='kb:login')
def folder_perms(request, folder_id):
    this_folder = get_object_or_404(Folder, pk=folder_id)
    perm_groups = FolderPerm.objects.filter(folder=this_folder)

    if this_folder.user_can_write(request.user):
        context = {
            'title': 'Edit Permissions - ' + this_folder.name,
            'this_folder': this_folder,
            'perm_groups': perm_groups,
            'show_breadcrumbs': True,
            'show_sidebar': True,
        }
        return render(request, 'kb/folder_permissions.html', context)

    else:
        messages.error(request, "You do not have permissions to edit this folder!")
        return HttpResponseRedirect(reverse('kb:folder', args=(folder_id,)))

# View the active version of an article
@login_required(login_url='kb:login')
def article(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    active_version = article.active_version()
    user = request.user
    context = {
        'title': active_version.title,
        'this_folder': article.folder,
        'user_can_write': article.folder.user_can_write(user),
        'article': article,
        'active_version': active_version,
        'show_breadcrumbs': True,
    }
    return render(request, 'kb/article.html', context)


# 'article_version' uses the same page template as 'article' but overrides
# active_version with the specified version to view
@login_required(login_url='kb:login')
def article_version(request, article_id, version):
    article = get_object_or_404(Article, pk=article_id)
    specific_article_version = History.objects.get(article=article, version=version)
    context = {
        'title': specific_article_version.title,
        'this_folder': article.folder,
        'user_can_write': article.folder.user_can_write(request.user),
        'article': article,
        'active_version': specific_article_version,
        'show_breadcrumbs': True,
    }
    return render(request, 'kb/article.html', context)


# 'article_version_activate' sets a specific version of an article to the active one
# The previously active version will be deactivated
# Redirects to show the newly active version of the article
@login_required(login_url='kb:login')
def article_version_activate(request, article_id, version):
    article = get_object_or_404(Article, pk=article_id)
    specific_article_version = History.objects.get(article=article, version=version)

    article.deactivate_all_versions()
    specific_article_version.set_active()

    return HttpResponseRedirect(reverse('kb:article', args=(article.id,)))


# Create a new article in a folder
@login_required(login_url='kb:login')
def article_new(request, folder_id):
    # Double-check that parent folder exists
    this_folder = get_object_or_404(Folder, pk=folder_id)

    if this_folder.user_can_write(request.user):
        context = {
            'title': 'Create New Article',
            'this_folder': this_folder,
            'ckeditor': True,
            'show_breadcrumbs': True,
        }
        return render(request, 'kb/article_new.html', context)
    else:
        messages.error(request, 'You do not have permissions to edit this folder!')
        return HttpResponseRedirect(reverse('kb:folder', args=(folder_id,)))


# Save or preview a new article
@login_required(login_url='kb:login')
def article_new_action(request, folder_id):
    # Sanity check that parent folder exists
    this_folder = get_object_or_404(Folder, pk=folder_id)

    # Get action from the clicked button
    action = request.POST['action']

    # Cancel button clicked
    # Immediately return to folder listing
    if action == 'cancel':
        return HttpResponseRedirect(reverse('kb:folder', args=(this_folder.id,)))

    # Sanitize article title
    article_title = strip_tags(request.POST['article_title'])   # Remove any HTML
    article_title = article_title.strip()                       # Remove any whitespace at beginning/end

    # Now that we've cleaned up, check that a name was actually provided
    if article_title == '':
        action = 'abort'
        messages.error(request, "Title must be specified!")

    # Sanitize article content (TO DO)
    article_body = request.POST['article_body']

    # Preview article
    if action == 'preview':
        context = {
            'title': 'PREVIEW - ' + article_title,
            'this_folder': this_folder,
            'article_title': article_title,
            'article_body': article_body,
            'show_breadcrumbs': True,
        }
        return render(request, 'kb/article_new_preview.html', context)

    # Save article
    elif action == 'save':
        # Create new article object
        article = Article(folder=this_folder)
        article.save()

        # Create version 1 in history for this article
        article_history = History(article=article, version=1, pub_date=datetime.datetime.now(), title=article_title, content=article_body, author='System', is_active=True)
        article_history.save()

        return HttpResponseRedirect(reverse('kb:folder', args=(this_folder.id,)))

    # Abort
    elif action != 'abort':
        # Use already specified error message
        messages.warning(request, "Unknown action specified!")

    # Return to new article form
    # Messages defined above will be present
    context = {
        'title': 'Create New Article',
        'this_folder': this_folder,
        'ckeditor': True,
        'show_breadcrumbs': True,
    }
    return render(request, 'kb/article_new.html', context)


# List all versions of an article
@login_required(login_url='kb:login')
def article_history(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    article_history = History.objects.filter(article=article)
    context = {
        'title': 'Article History - ' + article.active_version().title,
        'this_folder': article.folder,
        'article': article,
        'article_history': article_history,
        'show_breadcrumbs': True,
    }
    return render(request, 'kb/article_history.html', context)


# 'article_edit' loads an existing article into the editor form
# You can only edit the active version
@login_required(login_url='kb:login')
def article_edit(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    active_article = article.active_version()

    context = {
        'title': 'Edit Article - ' + active_article.title,
        'this_folder': article.folder,
        'article': article,
        'active_article': active_article,
        'ckeditor': True,
        'show_breadcrumbs': True,
        }
    return render(request, 'kb/article_edit.html', context)


# Save or preview article edits
@login_required(login_url='kb:login')
def article_edit_action(request, article_id):
    # Sanity check that our article exists
    article = get_object_or_404(Article, pk=article_id)

    # Get action from the clicked button
    action = request.POST['action']

    # Cancel button clicked
    # Immediately return to viewing the article
    if action == 'cancel':
        return HttpResponseRedirect(reverse('kb:article', args=(article_id,)))

    # Sanitize article title
    new_title = strip_tags(request.POST['article_title'])   # Remove any HTML
    new_title = new_title.strip()                       # Remove any whitespace at beginning/end

    # Now that we've cleaned up, check that a name was actually provided
    if new_title == '':
        action = 'abort'
        messages.error(request, "Title must be specified!")

    # Get the active version
    active_article = article.active_version()

    # Sanitize article content (TO DO)
    new_body = request.POST['article_body']

    # Were changes made?
    if ((new_title == active_article.title) and (new_body == active_article.content)):
        messages.warning(request, "No changes were made. Nothing saved.")
        return HttpResponseRedirect(reverse('kb:article', args=(article.id,)))

    # We've made it this far, therefore changes were made

    # Preview article
    if action == 'preview':
        context = {
            'title': 'PREVIEW - ' + new_title,
            'this_folder': article.folder,
            'article_title': new_title,
            'article_body': new_body,
            'show_breadcrumbs': True,
        }
        return render(request, 'kb/article_edit_preview.html', context)

    # Save article
    elif action == 'save':
        # Deactiveate all current versions of article history
        article.deactivate_all_versions()

        # Get highest version number (might not be the current active version)
        max_ver = article.newest_ver()

        # Create new history object, make it active
        new_ver_number = max_ver + 1
        new_ver = History(article=article, version=new_ver_number, pub_date=datetime.datetime.now(), content=new_body, author='System', is_active=True)

        # Update title
        new_ver.title = new_title

        # Update content
        new_ver.content = new_body

        # Save changes
        new_ver.save()

        # View the new active version of the article
        return HttpResponseRedirect(reverse('kb:article', args=(article.id,)))

    # Abort
    elif action != 'abort':
        # Use already specified error message
        messages.warning(request, "Unknown action specified!")


    # Return to edit article form
    # Messages defined above will be present
    context = {
        'title': 'Edit Article - ' + active_article.title,
        'this_folder': article.folder,
        'active_article': new_ver,
        'ckeditor': True,
        'show_breadcrumbs': True,
    }
    return render(request, 'kb/article_edit.html', context)


# Search for a KB article
@login_required(login_url='kb:login')
def search(request):
    terms = request.POST['search_terms']

    # Create FTS virtual table
    db_path = settings.DATABASES['default']['NAME']
    db = sqlite3.connect(db_path)
    db.row_factory = lambda cursor, row: row[0]     # so we get real values from our query, not a tuple
    db.execute('DROP TABLE IF EXISTS vtsearch')
    db.execute("CREATE VIRTUAL TABLE vtsearch USING fts5(id, title, content, tokenize = 'porter unicode61')")
    db.execute("INSERT INTO vtsearch(id, title, content) SELECT id, title, content FROM kb_history WHERE is_active = 1")

    # Search the FTS virtual table
    search = db.execute("SELECT id FROM vtsearch WHERE vtsearch MATCH ? ORDER BY rank", [terms])

    results = History.objects.filter(pk__in=search)

    context = {
        'terms': terms,
        'results': results,
        'show_breadcrumbs': False,
        'show_sidebar': False,
    }

    return render(request, 'kb/search.html', context)
