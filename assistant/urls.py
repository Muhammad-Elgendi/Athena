from django.urls import path

from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'assistant'
urlpatterns = [
   # ex: /assistant/
    path('', views.index, name='index'),
    # ex: /assistant/5/
    # path('<int:question_id>/', views.detail, name='detail'),
    # # ex: /assistant/5/results/
    # path('<int:question_id>/results/', views.results, name='results'),
    # # ex: /assistant/5/vote/
    # path('<int:question_id>/vote/', views.vote, name='vote'),
    path('add',views.add_person, name='add_person'),
    path('recognize',views.recognize, name='recognize'),
]