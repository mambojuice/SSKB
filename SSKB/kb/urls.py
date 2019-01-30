from django.urls import path
from . import views

app_name = 'kb'

urlpatterns = [
    path('', views.index, name='index'),

    # User login/logout
    path('login', views.login, name='login'),
    path('login/submit', views.login_do, name='login_do'),
    path('logout', views.logout, name='logout'),

    # Folder paths
    path('folder/<int:folder_id>/', views.folder, name='folder'),
    path('folder/<int:folder_id>/newfolder', views.folder_new, name='folder_new'),
    path('folder/<int:folder_id>/addfolder', views.folder_add, name='folder_add'),
    path('folder/<int:folder_id>/permissions', views.folder_perms, name='folder_perms'),

    # Article creation
    path('folder/<int:folder_id>/newarticle', views.article_new, name='article_new'),
    path('folder/<int:folder_id>/newarticle/action', views.article_new_action, name='article_new_action'),

    # Article view/edit
    path('article/<int:article_id>/', views.article, name='article'),
    path('article/<int:article_id>/edit', views.article_edit, name='article_edit'),
    path('article/<int:article_id>/edit/action', views.article_edit_action, name='article_edit_action'),
    path('article/<int:article_id>/history', views.article_history, name='article_history'),
    path('article/<int:article_id>/history/<int:version>', views.article_version, name='article_version'),
    path('article/<int:article_id>/history/<int:version>/activate', views.article_version_activate, name='article_version_activate'),

    # search
    path('search/', views.search, name="search"),
]
