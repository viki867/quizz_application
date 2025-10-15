from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='user_login'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('profile/', views.user_profile, name='user_profile'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    path('category/<int:category_id>/', views.category_quiz, name='category_quiz'),
    path('quiz/<int:quiz_id>/', views.start_quiz, name='start_quiz'),
    path('result/<int:quiz_id>/', views.quiz_result, name='quiz_result'),

    # Admin actions
    path('add-category/', views.add_category, name='add_category'),
     path('manage-categories/', views.manage_categories, name='manage_categories'),
    path('edit-category/<int:category_id>/', views.edit_category, name='edit_category'),
    path('delete-category/<int:category_id>/', views.delete_category, name='delete_category'),
 
    path('add-quiz/', views.add_quiz, name='add_quiz'),
     path('view-quizzes/', views.view_quizzes, name='view_quizzes'),
      path('edit-quiz/<int:quiz_id>/', views.edit_quiz, name='edit_quiz'),
    path('delete-quiz/<int:quiz_id>/', views.delete_quiz, name='delete_quiz'),
    path('upload-questions/<int:quiz_id>/', views.upload_questions, name='upload_questions'),
     path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('add-question/<int:quiz_id>/', views.add_question, name='add_question'),
    path('view-users/', views.view_users, name='view_users'),
    path('view-scores/', views.view_scores, name='view_scores'),

]
