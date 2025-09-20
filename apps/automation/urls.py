from django.urls import path
from . import views

app_name = 'automation'

urlpatterns = [
    # Tâches automatisées
    path('tasks/', views.TaskListView.as_view(), name='task-list'),
    path('tasks/<int:pk>/', views.TaskDetailView.as_view(), name='task-detail'),
    path('tasks/run/<int:pk>/', views.run_task, name='run-task'),
    
    # Logs des tâches
    path('logs/', views.TaskLogsView.as_view(), name='task-logs'),
    
    # Configuration
    path('settings/', views.AutomationSettingsView.as_view(), name='automation-settings'),
    
    # API
    path('api/tasks/status/', views.api_task_status, name='api-task-status'),
    path('api/tasks/run/', views.api_run_task, name='api-run-task'),
]

