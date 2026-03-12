from django.urls import path
from . import views

urlpatterns = [
    path('produits/', views.get_produits, name='produits'),
    path('stats/categories/', views.stats_categories, name='stats-categories'),
    path('stats/magasins/', views.stats_magasins, name='stats-magasins'),
    path('stats/top-produits/', views.top_produits, name='top-produits'),
    path('stats/inflation/', views.inflation_categories, name='inflation'),
    path('stats/variations/', views.variations_date, name='variations'),
    path('kpis/', views.kpis, name='kpis'),
]