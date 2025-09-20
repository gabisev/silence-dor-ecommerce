from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

@method_decorator(login_required, name='dispatch')
class TaskListView(TemplateView):
    """Vue de la liste des tâches"""
    template_name = 'automation/task_list.html'

@method_decorator(login_required, name='dispatch')
class TaskDetailView(TemplateView):
    """Vue de détail d'une tâche"""
    template_name = 'automation/task_detail.html'

def run_task(request, pk):
    """Exécuter une tâche"""
    return JsonResponse({'status': 'success'})

@method_decorator(login_required, name='dispatch')
class TaskLogsView(TemplateView):
    """Vue des logs des tâches"""
    template_name = 'automation/task_logs.html'

@method_decorator(login_required, name='dispatch')
class AutomationSettingsView(TemplateView):
    """Vue des paramètres d'automatisation"""
    template_name = 'automation/settings.html'

def api_task_status(request):
    """API pour le statut des tâches"""
    return JsonResponse({'tasks': []})

def api_run_task(request):
    """API pour exécuter une tâche"""
    return JsonResponse({'status': 'success'})

