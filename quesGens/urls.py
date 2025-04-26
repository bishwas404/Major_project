from django.urls import path

from . import views

urlpatterns = [
    path("", views.generate_mcq, name="generate_mcq"),
    path("result/", views.result, name="result"),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('is_logged_in/', views.is_logged_in, name='is_logged_in'),
    path('logout/',views.logout_view,name='logout'),
    path("history/", views.history, name="history"),
    path('about/',views.about, name='about'),
    path('test/',views.test,name="test"),
    path('history/delete/<int:entry_id>/', views.delete_history, name='delete_history'),
    # path('test/results/', views.test_results, name='test_results'), 
    # path("",views.landing,name="landing"),
    # path("generate_mcq/", views.generate_mcq, name="generate_mcq"),
    # path("about/", views.about, name="about"),
    # path('login/', views.login_view, name='login'),
    # path('register/', views.register_view, name='register'),
    # path('is_logged_in/', views.is_logged_in, name='is_logged_in'),
    # path('result/',views.result,name='result'),
    # path('logout/',views.logout_view,name='logout'),
    # path('profile/',views.profile, name='profile'),
]
