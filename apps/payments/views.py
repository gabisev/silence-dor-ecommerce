from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from django.conf import settings
try:
    import stripe
    stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')
except ImportError:
    stripe = None
from .models import Payment, Refund, PaymentMethod
from .serializers import (
    PaymentSerializer, RefundSerializer, PaymentMethodSerializer,
    CreatePaymentSerializer, CreateRefundSerializer
)
from apps.orders.models import Order

# Configuration Stripe (déjà configuré dans l'import)


class PaymentListView(generics.ListAPIView):
    """Vue pour lister les paiements de l'utilisateur"""
    
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user).select_related('order')


class PaymentDetailView(generics.RetrieveAPIView):
    """Vue pour les détails d'un paiement"""
    
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user).select_related('order')


class PaymentMethodListView(generics.ListCreateAPIView):
    """Vue pour lister et créer des méthodes de paiement"""
    
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PaymentMethod.objects.filter(user=self.request.user)


class PaymentMethodDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vue pour les détails d'une méthode de paiement"""
    
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PaymentMethod.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment_intent_view(request):
    """Vue pour créer un PaymentIntent Stripe"""
    
    serializer = CreatePaymentSerializer(data=request.data, context={'request': request})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    order_id = serializer.validated_data['order_id']
    payment_method_id = serializer.validated_data.get('payment_method_id')
    save_payment_method = serializer.validated_data['save_payment_method']
    
    # Récupérer la commande
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    if not stripe:
        return Response(
            {'error': 'Stripe n\'est pas configuré'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    try:
        # Créer le PaymentIntent Stripe
        intent_data = {
            'amount': int(order.total_amount * 100),  # Convertir en centimes
            'currency': 'eur',
            'metadata': {
                'order_id': order.id,
                'order_number': order.order_number,
                'user_id': request.user.id,
            }
        }
        
        # Ajouter la méthode de paiement si fournie
        if payment_method_id:
            payment_method = get_object_or_404(PaymentMethod, id=payment_method_id, user=request.user)
            intent_data['payment_method'] = payment_method.stripe_payment_method_id
        
        # Configurer la sauvegarde de la méthode de paiement
        if save_payment_method:
            intent_data['setup_future_usage'] = 'off_session'
        
        payment_intent = stripe.PaymentIntent.create(**intent_data)
        
        # Créer l'enregistrement de paiement
        payment = Payment.objects.create(
            order=order,
            user=request.user,
            amount=order.total_amount,
            method='stripe',
            status='pending',
            external_id=payment_intent.id,
            stripe_payment_intent_id=payment_intent.id,
            metadata={'save_payment_method': save_payment_method}
        )
        
        return Response({
            'client_secret': payment_intent.client_secret,
            'payment_id': payment.id,
            'payment_intent_id': payment_intent.id
        })
        
    except stripe.error.StripeError as e:
        return Response(
            {'error': f'Erreur Stripe: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_payment_view(request, payment_id):
    """Vue pour confirmer un paiement"""
    
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    if not stripe:
        return Response(
            {'error': 'Stripe n\'est pas configuré'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    try:
        # Récupérer le PaymentIntent depuis Stripe
        payment_intent = stripe.PaymentIntent.retrieve(payment.stripe_payment_intent_id)
        
        if payment_intent.status == 'succeeded':
            # Mettre à jour le paiement
            payment.status = 'succeeded'
            payment.transaction_id = payment_intent.latest_charge
            payment.save()
            
            # Mettre à jour la commande
            payment.order.payment_status = 'paid'
            payment.order.status = 'confirmed'
            payment.order.save()
            
            # Ajouter à l'historique
            from apps.orders.models import OrderStatusHistory
            OrderStatusHistory.objects.create(
                order=payment.order,
                status='confirmed',
                notes='Paiement confirmé'
            )
            
            return Response({
                'message': _('Paiement confirmé avec succès!'),
                'payment': PaymentSerializer(payment).data
            })
        else:
            return Response(
                {'error': _('Le paiement n\'a pas encore été confirmé.')}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except stripe.error.StripeError as e:
        return Response(
            {'error': f'Erreur Stripe: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_refund_view(request):
    """Vue pour créer un remboursement"""
    
    serializer = CreateRefundSerializer(data=request.data, context={'request': request})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    payment_id = serializer.validated_data['payment_id']
    amount = serializer.validated_data['amount']
    reason = serializer.validated_data.get('reason', '')
    
    payment = get_object_or_404(Payment, id=payment_id, user=request.user)
    
    # Vérifier que le montant ne dépasse pas le paiement
    if amount > payment.amount:
        return Response(
            {'error': _('Le montant du remboursement ne peut pas dépasser le montant du paiement.')}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not stripe:
        return Response(
            {'error': 'Stripe n\'est pas configuré'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    try:
        # Créer le remboursement Stripe
        refund = stripe.Refund.create(
            payment_intent=payment.stripe_payment_intent_id,
            amount=int(amount * 100),  # Convertir en centimes
            reason='requested_by_customer' if reason else None,
            metadata={
                'order_id': payment.order.id,
                'order_number': payment.order.order_number,
                'user_id': request.user.id,
            }
        )
        
        # Créer l'enregistrement de remboursement
        refund_obj = Refund.objects.create(
            payment=payment,
            order=payment.order,
            amount=amount,
            status='succeeded' if refund.status == 'succeeded' else 'pending',
            external_id=refund.id,
            stripe_refund_id=refund.id,
            reason=reason
        )
        
        # Mettre à jour le paiement si remboursement complet
        if amount == payment.amount:
            payment.status = 'refunded'
            payment.save()
            
            payment.order.payment_status = 'refunded'
            payment.order.status = 'refunded'
            payment.order.save()
        
        return Response({
            'message': _('Remboursement créé avec succès!'),
            'refund': RefundSerializer(refund_obj).data
        })
        
    except stripe.error.StripeError as e:
        return Response(
            {'error': f'Erreur Stripe: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_methods_view(request):
    """Vue pour récupérer les méthodes de paiement Stripe de l'utilisateur"""
    
    if not request.user.stripe_customer_id:
        return Response({
            'payment_methods': [],
            'message': 'Aucun client Stripe associé à ce compte.'
        })
    
    if not stripe:
        return Response({
            'payment_methods': [],
            'message': 'Stripe n\'est pas configuré.'
        })
    
    try:
        # Récupérer les méthodes de paiement depuis Stripe
        payment_methods = stripe.PaymentMethod.list(
            customer=request.user.stripe_customer_id,
            type='card'
        )
        
        return Response({
            'payment_methods': payment_methods.data
        })
        
    except stripe.error.StripeError as e:
        return Response(
            {'error': f'Erreur Stripe: {str(e)}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def webhook_view(request):
    """Vue pour traiter les webhooks Stripe"""
    
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')
    
    if not stripe:
        return Response({'error': 'Stripe n\'est pas configuré'}, status=400)
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return Response({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError:
        return Response({'error': 'Invalid signature'}, status=400)
    
    # Traiter les événements
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        # Traiter le paiement réussi
        try:
            payment = Payment.objects.get(stripe_payment_intent_id=payment_intent['id'])
            payment.status = 'succeeded'
            payment.save()
            
            payment.order.payment_status = 'paid'
            payment.order.save()
        except Payment.DoesNotExist:
            pass
    
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        # Traiter le paiement échoué
        try:
            payment = Payment.objects.get(stripe_payment_intent_id=payment_intent['id'])
            payment.status = 'failed'
            payment.failure_reason = payment_intent.get('last_payment_error', {}).get('message', '')
            payment.save()
        except Payment.DoesNotExist:
            pass
    
    return Response({'status': 'success'})
