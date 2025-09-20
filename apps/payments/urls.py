from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Paiements
    path('', views.PaymentListView.as_view(), name='payment-list'),
    path('<int:pk>/', views.PaymentDetailView.as_view(), name='payment-detail'),
    path('create-intent/', views.create_payment_intent_view, name='create-payment-intent'),
    path('<int:payment_id>/confirm/', views.confirm_payment_view, name='confirm-payment'),
    
    # Méthodes de paiement
    path('methods/', views.PaymentMethodListView.as_view(), name='payment-method-list'),
    path('methods/<int:pk>/', views.PaymentMethodDetailView.as_view(), name='payment-method-detail'),
    path('methods/stripe/', views.payment_methods_view, name='stripe-payment-methods'),
    
    # Remboursements
    path('refunds/', views.create_refund_view, name='create-refund'),
    
    # Webhooks
    path('webhook/', views.webhook_view, name='stripe-webhook'),
]

