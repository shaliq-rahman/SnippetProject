from django.urls import path
from .views import *
app_name = 'api'

urlpatterns = [
    path('', Welcome, name='welcome'),
    path('register/', Register.as_view(), name='register'),
    path('login/', Login.as_view(), name='login'),
    path('create-snippets/', Snippets.as_view({'post':'create'}), name='create_snippets'),
    path('list-snippets/', Snippets.as_view({'get':'get_snippets'}), name='get_snippets'),
    path('update-snippet/<int:id>/', UpdateSnippet.as_view({'put':'update_snippet'}), name='update_snippet'),
    path('delete-snippet/<int:id>/', SnippetDelete.as_view({'delete':'delete_snippet'}), name='delete_snippet'),
    path('tags/list/', TagsListAPI.as_view({'get':'list_tags'}), name='list_tags'),
    path('tag/<int:id>/detail/', TagsDetailAPI.as_view({'get':'list_tag_detail'}), name='list_tag_detail'),
    path('overview/', SnippetsOverviewAPI.as_view({'get':'overview'}), name='over_view'),
    
]
