from venv import logger
from apps.transactions.models import BankAccount, Coupon, Transaction
from apps.transactions.serializers import BankAccountSerializer, CouponSerializer, CouponV2Serializer, StaffTransactionSerializer,  TransactionConfirmSerializer, TransactionResponseSerializer, TransactionInitSerializer, TransactionSerializer
from rest_framework.generics import GenericAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer

from apps.users.permissions import IsOwnerOrStaff, IsStaff
from rest_framework.permissions import IsAuthenticated, AllowAny
from .email_service import EmailService

User = get_user_model()

class BankAccountPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class BankAccountListCreateView(GenericAPIView):
    """
    Vista para listar y crear cuentas bancarias.
    Soporta paginación y filtrado por usuario.
    """
    serializer_class = BankAccountSerializer
    pagination_class = BankAccountPagination
    permission_classes = [IsOwnerOrStaff]    
    def get_queryset(self):
        """
        Verifica si el usuario es staff, jala el user_id para filtrar cuentas bancarias. 
        Por usuario en caso el staff consulte y en caso contrario filtra por usuario.
        """
        try:
            # Verificar si el usuario está autenticado
            if not self.request.user.is_authenticated:
                return BankAccount.objects.none()

            # Verificar si el usuario es staff de manera segura
            is_staff = (
                hasattr(self.request.user, 'role') and 
                self.request.user.role is not None and 
                self.request.user.role.name == 'staff'
            )

            if is_staff:
                # Staff puede ver todas las cuentas si especifica user_id
                user_id = self.request.query_params.get('user_id')
                if user_id:
                    return BankAccount.objects.filter(user_id=user_id, is_active=True)
                return BankAccount.objects.filter(is_active=True)
            
            # Para usuarios no staff, mostrar solo sus propias cuentas
            return BankAccount.objects.filter(
                user=self.request.user,
                is_active=True
            )
            
        except Exception as e:
            print(f"Error en get_queryset: {str(e)}")
            return BankAccount.objects.none()
    def post(self, request):
        """
        Crea una nueva cuenta bancaria.
        Los datos se validan a través del serializer que maneja la lógica específica por país.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        """
        Lista las cuentas bancarias del usuario con soporte para paginación.
        """
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class BankAccountDetailView(GenericAPIView):
    """
    Vista para operaciones detalladas de una cuenta bancaria específica:
    actualizar, eliminar y obtener detalles por ID.
    """
    serializer_class = BankAccountSerializer
    #Deberia ser solo de staff?
    def get_queryset(self):
        """
        Filtra las cuentas activas
        """
        return BankAccount.objects.filter(is_active=True)

    def get_object(self):
        """
        Obtiene una cuenta bancaria específica por ID
        """
        try:
            obj = get_object_or_404(self.get_queryset(), pk=self.kwargs['pk'])
            self.check_object_permissions(self.request, obj)
            return obj
        except Exception as e:
            return None

    def get(self, request, pk):
        """
        Obtiene los detalles de una cuenta bancaria por ID
        """
        try:
            bank_account = self.get_object()
            if not bank_account:
                return Response(
                    {'error': f'No se encontró la cuenta bancaria con ID: {pk}'},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = self.get_serializer(bank_account)
            return Response({
                'message': 'Cuenta bancaria recuperada exitosamente',
                'data': serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'Error al obtener la cuenta bancaria: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def put(self, request, pk):
        """
        Actualiza una cuenta bancaria existente por ID
        """
        try:
            bank_account = self.get_object()
            if not bank_account:
                return Response(
                    {'error': f'No se encontró la cuenta bancaria con ID: {pk}'},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = self.get_serializer(bank_account, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'message': 'Cuenta bancaria actualizada exitosamente',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)

            return Response({
                'error': 'Error en los datos proporcionados',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {'error': f'Error al actualizar la cuenta bancaria: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, pk):
        """
        Realiza un borrado lógico de la cuenta bancaria por ID
        """
        try:
            bank_account = self.get_object()
            if not bank_account:
                return Response(
                    {'error': f'No se encontró la cuenta bancaria con ID: {pk}'},
                    status=status.HTTP_404_NOT_FOUND
                )

            if not bank_account.is_active:
                return Response(
                    {'error': 'Esta cuenta bancaria ya está desactivada'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            bank_account.is_active = False
            bank_account.save()

            return Response({
                'message': 'Cuenta bancaria eliminada exitosamente'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': f'Error al eliminar la cuenta bancaria: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class CouponManagementView(GenericAPIView):
    """
    View for listing and creating coupons.
    GET: Lists all coupons with optional currency filtering
    POST: Creates a new coupon
    """
    serializer_class = CouponSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    def get_permissions(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [IsAuthenticated()]
        return [IsStaff()]
    def get_queryset(self):
        queryset = Coupon.objects.filter(type='manual')
        
        # Filter by currency if specified in query params
        source_currency = self.request.query_params.get('source_currency')
        target_currency = self.request.query_params.get('target_currency')
        
        if source_currency:
            queryset = queryset.filter(source_currency__code=source_currency.upper())
        if target_currency:
            queryset = queryset.filter(target_currency__code=target_currency.upper())

        return queryset.order_by('-created_at')

    def get(self, request):
        """Lists all coupons with optional filtering"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        """Creates a new coupon"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            coupon = serializer.save()
            return Response(
                self.get_serializer(coupon).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CouponDetailView(GenericAPIView):
    """
    View for retrieving and updating specific coupons.
    GET: Retrieves a specific coupon by ID
    PATCH: Updates a specific coupon
    """
    serializer_class = CouponSerializer  
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsStaff()]  # Solo staff puede modificar/eliminar
        return super().get_permissions()
    def get_object(self):
        return get_object_or_404(Coupon, id=self.kwargs['pk'], type='manual')

    def get(self, request, pk):
        """Retrieves a specific coupon"""
        coupon = self.get_object()
        serializer = self.get_serializer(coupon)
        return Response(serializer.data)

    def patch(self, request, pk):
        """Updates a specific coupon"""
        coupon = self.get_object()
        serializer = self.get_serializer(coupon, data=request.data, partial=True)
        
        if serializer.is_valid():
            updated_coupon = serializer.save()
            return Response(self.get_serializer(updated_coupon).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        """Deletes a specific coupon"""
        coupon = self.get_object()
        coupon.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CouponByCodeView(GenericAPIView):
    """
    View for retrieving coupon details by code.
    GET: Retrieves a specific coupon using its code
    """
    serializer_class = CouponSerializer

    def get(self, request, code):
        """Retrieves coupon details by code"""
        try:
            coupon = Coupon.objects.get(code=code, type='manual')
            serializer = self.get_serializer(coupon)
            return Response(serializer.data)
        except Coupon.DoesNotExist:
            return Response(
                {'error': 'Coupon not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class CouponV2ManagementView(GenericAPIView):
    """
    V2 View for listing and creating coupons with extended fields
    """
    serializer_class = CouponV2Serializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer]

    def get_permissions(self):
        # Public read; restricted write
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [AllowAny()]
        return [IsStaff()]

    def get_queryset(self):
        queryset = Coupon.objects.filter(type='automatic')
        source_currency = self.request.query_params.get('source_currency')
        target_currency = self.request.query_params.get('target_currency')
        if source_currency:
            queryset = queryset.filter(source_currency__code=source_currency.upper())
        if target_currency:
            queryset = queryset.filter(target_currency__code=target_currency.upper())
        return queryset.order_by('-created_at')

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            coupon = serializer.save()
            return Response(self.get_serializer(coupon).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CouponAutomaticView(GenericAPIView):
    """List and create coupons of type 'automatic'"""
    serializer_class = CouponV2Serializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer]

    def get_permissions(self):
        # Público para lectura; autenticado (staff) para escritura
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [AllowAny()]
        return [IsStaff()]

    def get_queryset(self):
        queryset = Coupon.objects.filter(type='automatic')
        source_currency = self.request.query_params.get('source_currency')
        target_currency = self.request.query_params.get('target_currency')
        if source_currency:
            queryset = queryset.filter(source_currency__code=source_currency.upper())
        if target_currency:
            queryset = queryset.filter(target_currency__code=target_currency.upper())
        return queryset.order_by('-created_at')

    def get(self, request):
        coupons = self.get_queryset()
        serializer = self.get_serializer(coupons, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        data['type'] = 'automatic'
        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            coupon = serializer.save()
            return Response(self.get_serializer(coupon).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CouponAutomaticDetailView(GenericAPIView):
    """Retrieve and update an automatic coupon by ID"""
    serializer_class = CouponV2Serializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer]

    def get_permissions(self):
        # Público para detalle; modificaciones restringidas
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [AllowAny()]
        return [IsStaff()]

    def get_object(self):
        return get_object_or_404(Coupon, id=self.kwargs['pk'], type='automatic')

    def get(self, request, pk):
        coupon = self.get_object()
        serializer = self.get_serializer(coupon)
        return Response(serializer.data)

    def put(self, request, pk):
        coupon = self.get_object()
        data = request.data.copy()
        # Ensure type stays automatic
        data['type'] = 'automatic'
        serializer = self.get_serializer(coupon, data=data, partial=False)
        if serializer.is_valid():
            updated = serializer.save()
            return Response(self.get_serializer(updated).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        coupon = self.get_object()
        data = request.data.copy()
        data['type'] = 'automatic'
        serializer = self.get_serializer(coupon, data=data, partial=True)
        if serializer.is_valid():
            updated = serializer.save()
            return Response(self.get_serializer(updated).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CouponV2DetailView(GenericAPIView):
    """V2 detail view with extended fields support"""
    serializer_class = CouponV2Serializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer]

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsStaff()]
        # Allow public GET on coupon detail
        return [AllowAny()]

    def get_object(self):
        return get_object_or_404(Coupon, id=self.kwargs['pk'], type='automatic')

    def get(self, request, pk):
        coupon = self.get_object()
        serializer = self.get_serializer(coupon)
        return Response(serializer.data)

    def patch(self, request, pk):
        coupon = self.get_object()
        serializer = self.get_serializer(coupon, data=request.data, partial=True)
        if serializer.is_valid():
            updated_coupon = serializer.save()
            return Response(self.get_serializer(updated_coupon).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        coupon = self.get_object()
        coupon.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CouponV2ByCodeView(GenericAPIView):
    serializer_class = CouponV2Serializer
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer]
    permission_classes = [AllowAny]

    def get(self, request, code):
        try:
            coupon = Coupon.objects.get(code=code, type='automatic')
            serializer = self.get_serializer(coupon)
            return Response(serializer.data)
        except Coupon.DoesNotExist:
            return Response({'error': 'Coupon not found'}, status=status.HTTP_404_NOT_FOUND)
# Transactions
class TransactionListView(GenericAPIView):
    """Vista para listar transacciones"""
    serializer_class = TransactionSerializer

    """Vista para listar transacciones de un usuario específico"""
    serializer_class = TransactionSerializer
    
#ENDPOINT Dont work in GET METHOD
    def get_queryset(self):
        # Obtener el user_id de la URL
        user_id = self.kwargs.get('user_id')
        if not user_id:
            return Transaction.objects.none()
            
        return Transaction.objects.filter(
            user_id=user_id
        ).order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response(
                {"message": "No se encontraron transacciones para este usuario"},
                status=status.HTTP_404_NOT_FOUND
            )
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class TransactionDetailView(GenericAPIView):
    serializer_class = TransactionSerializer
    
    def get_queryset(self):
        # Obtener el user_id del parámetro pk de la URL
        user_id = self.kwargs.get('pk')  # Cambiado de 'user_id' a 'pk'
        if not user_id:
            return Transaction.objects.none()
            
        return Transaction.objects.filter(
            user_id=user_id
        ).order_by('-created_at')
    
    def get(self, request, *args, **kwargs): 
        queryset = self.get_queryset()
        if not queryset.exists():
            return Response(
                {"message": "No se encontraron transacciones para este usuario"},
                status=status.HTTP_404_NOT_FOUND
            )
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class StaffTransactionListView(GenericAPIView):
    """View for listing and creating transactions by staff members"""
    serializer_class = StaffTransactionSerializer
    def get_queryset(self):
        return Transaction.objects.all()
  
    def get(self, request):
        # Get queryset with all related fields to optimize performance
        transactions = Transaction.objects.all().select_related(
            'user', 
            'origin_account', 
            'destination_account',
            'source_currency',
            'destination_currency',
            'coupon'
        ).order_by('-created_at')
        
        # Apply filters if provided
        status_filter = request.query_params.get('status')
        if status_filter:
            transactions = transactions.filter(status=status_filter)
            
        serializer = self.get_serializer(transactions, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class StaffTransactionDetailView(GenericAPIView):
#     """View for retrieving, updating and deleting individual transactions"""
#     serializer_class = StaffTransactionSerializer
#     #permission_classes = [IsStaff]
    
#     def get_transaction(self, pk):
#         return get_object_or_404(Transaction, pk=pk)
    
#     def get(self, request, pk):
#         transaction = self.get_transaction(pk)
#         serializer = self.get_serializer(transaction)
#         return Response(serializer.data)
    
#     def put(self, request, pk):
#         transaction = self.get_transaction(pk)
        
#         # Verificar si hay un admin_voucher en los datos recibidos
#         send_notification = False
#         if 'admin_voucher' in request.data and request.data['admin_voucher']:
#             # Solo si se proporciona admin_voucher, actualizar el estado
#             request.data['status'] = 'completed'
#             send_notification = True
        
#         serializer = self.get_serializer(
#             transaction, 
#             data=request.data,
#             partial=True  # Esto permite la actualización parcial
#         )
        
#         if serializer.is_valid():
#             updated_transaction = serializer.save()
            
#             # Enviar notificación solo si se proporcionó admin_voucher
#             if send_notification:
#                 try:
#                     user = updated_transaction.user
#                     EmailService.send_transaction_completed(
#                         user_email=user.email,
#                         user_name=f"{user.first_name} {user.last_name}",
#                         transaction_data={
#                             'transaction_id': updated_transaction.transaction_id,
#                             'date': updated_transaction.created_at,
#                             'source_currency': updated_transaction.source_currency.code,
#                             'source_currency_symbol': updated_transaction.source_currency.symbol,
#                             'source_currency_amount': updated_transaction.source_amount,
#                             'destination_currency': updated_transaction.destination_currency.code,
#                             'destination_currency_symbol': updated_transaction.destination_currency.symbol,
#                             'destination_currency_amount': updated_transaction.destination_amount,
#                             'exchange_rate': updated_transaction.exchange_rate,
#                             'status': updated_transaction.status,
#                             'payment_method': updated_transaction.payment_method,
#                             'description': "Transferencia completada"
#                         }
#                     )
#                 except Exception as e:
#                     print(f"Error al enviar notificación: {str(e)}")
            
#             return Response(serializer.data)
        
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#     def delete(self, request, pk):
#         transaction = self.get_transaction(pk)
#         transaction.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)

class StaffTransactionDetailView(GenericAPIView):
    """View for retrieving, updating and deleting individual transactions"""
    serializer_class = StaffTransactionSerializer
    permission_classes = [IsStaff]
    
    def get_transaction(self, pk):
        return get_object_or_404(Transaction, pk=pk)
    
    def get(self, request, pk):
        transaction = self.get_transaction(pk)
        serializer = self.get_serializer(transaction)
        return Response(serializer.data)
    def put(self, request, pk):
        transaction = self.get_transaction(pk)
        
        # Crear una copia mutable de los datos
        mutable_data = request.data.copy()
        
        # Verificar si hay un admin_voucher en los datos recibidos
        send_notification = False
        if 'admin_voucher' in mutable_data and mutable_data['admin_voucher']:
            # Solo si se proporciona admin_voucher, actualizar el estado
            mutable_data['status'] = 'completed'
            send_notification = True
        
        serializer = self.get_serializer(
            transaction, 
            data=mutable_data,
            partial=True  # Esto permite la actualización parcial
        )
        print(f"Datos recibidos para actualización: {request.data}")
        if serializer.is_valid():
            updated_transaction = serializer.save()
            
            # Enviar notificación solo si se proporcionó admin_voucher
            # if send_notification:
            #     try:
            #         user = updated_transaction.user
            #         EmailService.send_transaction_completed(
            #             user_email=user.email,
            #             user_name=f"{user.first_name} {user.last_name}",
            #             transaction_data={
            #                 'transaction_id': updated_transaction.transaction_id,
            #                 'date': updated_transaction.created_at,
            #                 'source_currency': updated_transaction.source_currency.code,
            #                 'source_currency_symbol': updated_transaction.source_currency.symbol,
            #                 'source_currency_amount': updated_transaction.source_amount,
            #                 'destination_currency': updated_transaction.destination_currency.code,
            #                 'destination_currency_symbol': updated_transaction.destination_currency.symbol,
            #                 'destination_currency_amount': updated_transaction.destination_amount,
            #                 'exchange_rate': updated_transaction.exchange_rate,
            #                 'status': updated_transaction.status,
            #                 'payment_method': updated_transaction.payment_method,
            #                 'description': "Transferencia completada"
            #             }
            #         )
            #     except Exception as e:
            #         print(f"Error al enviar notificación: {str(e)}")
            
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        transaction = self.get_transaction(pk)
        transaction.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class StaffTransactionStatusView(GenericAPIView):
    """View for updating transaction status"""
    serializer_class = StaffTransactionSerializer
    permission_classes = [IsStaff]
    
    def post(self, request, pk):
        transaction = get_object_or_404(Transaction, pk=pk)
        new_status = request.data.get('status')
        
        if new_status not in dict(Transaction.STATUS_CHOICES):
            return Response(
                {'error': 'Estado inválido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        transaction.status = new_status
        transaction.save()
        
        serializer = self.get_serializer(transaction)
        return Response(serializer.data)

class StaffTransactionVoucherView(GenericAPIView):
    """View for uploading admin vouchers"""
    serializer_class = StaffTransactionSerializer
    permission_classes = [IsStaff]
    
    def post(self, request, pk):
        transaction = get_object_or_404(Transaction, pk=pk)
        voucher = request.FILES.get('admin_voucher')
        
        if not voucher:
            return Response(
                {'error': 'Voucher requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        transaction.admin_voucher = voucher
        transaction.status = 'completed',
        transaction.save()
        
        serializer = self.get_serializer(transaction)

        try:
                # Enviar correo con try/except interno
                email_result = EmailService.send_transaction_completed(
                    user_email=transaction.user.email,
                    user_name=f"{transaction.user.first_name} {transaction.user.last_name}",
                    transaction_data={
                        'transaction_id': transaction.transaction_id,
                        'date': transaction.created_at,
                        'status': 'completed',
                        'payment_method': transaction.payment_method,
                        'description': f"Transferencia",
                        'source_currency': transaction.source_currency.code,
                        'source_currency_symbol': transaction.source_currency.symbol,
                        'source_currency_amount': transaction.source_amount,
                        'destination_currency': transaction.destination_currency.code,
                        'destination_currency_symbol': transaction.destination_currency.symbol,
                        'destination_currency_amount': transaction.destination_amount,
                        'exchange_rate': transaction.exchange_rate
                    }
                )
                print(f"Resultado del envío: {email_result}")
        except Exception as email_error:
                print(f"ERROR AL ENVIAR CORREO: {str(email_error)}")
                import traceback
                print(traceback.format_exc())
            
        return Response(serializer.data)
    
class CreateTransactionView(GenericAPIView):
    serializer_class = TransactionSerializer  # Añade esta línea

    
    def post(self, request):
        # Log de datos recibidos
        logger.info("Datos recibidos en request.data: %s", request.data)
        logger.info("Archivos recibidos en request.FILES: %s", request.FILES)

        data = {
            'user': request.data.get('user'),
            'origin_account': request.data.get('origin_account'),
            'destination_account': request.data.get('destination_account'),
            'source_amount': request.data.get('source_amount'),
            'destination_amount': request.data.get('destination_amount'),
            'source_currency': request.data.get('source_currency'),
            'destination_currency': request.data.get('destination_currency'),
            'exchange_rate': request.data.get('exchange_rate'),
            'payment_method': request.data.get('payment_method'),
            'status': request.data.get('status')
        }

        # Log de datos procesados
        logger.info("Datos procesados: %s", data)

        if 'payment_voucher' in request.FILES:
            data['payment_voucher'] = request.FILES['payment_voucher']
            logger.info("Voucher encontrado: %s", request.FILES['payment_voucher'])

        serializer = self.get_serializer(data=data)
        
        if not serializer.is_valid():
            logger.error("Errores de validación: %s", serializer.errors)
            return Response(
                {
                    'error': 'Datos inválidos',
                    'detail': serializer.errors
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user_id = data['user']
            user = User.objects.get(id=user_id)
            
            transaction = serializer.save()
            print(f"Transacción creada: ID={transaction.id}")
            
            response_serializer = TransactionResponseSerializer(
                transaction, 
                context={'request': request}
            )
            
            # Print de depuración básico
            print(f"Intentando enviar correo a {user.email}")
            
            try:
                # Enviar correo con try/except interno
                email_result = EmailService.send_transaction_notification(
                    user_email=user.email,
                    user_name=f"{user.first_name} {user.last_name}",
                    transaction_data={
                        'transaction_id': transaction.transaction_id,
                        'date': transaction.created_at,
                        'amount': data['source_amount'],
                        'currency': data['source_currency'],
                        'status': data['status'],
                        'payment_method': data.get('payment_method', ''),
                        'description': f"Transferencia",
                        'source_currency': transaction.source_currency.code,
                        'source_currency_symbol': transaction.source_currency.symbol,
                        'source_currency_amount': data['source_amount'],
                        'exchange_rate': transaction.exchange_rate,
                        'destination_currency': transaction.destination_currency.code,
                        'destination_currency_symbol': transaction.destination_currency.symbol,
                        'destination_currency_amount': data['destination_amount']
                    }
                )
                print(f"Resultado del envío: {email_result}")
            except Exception as email_error:
                print(f"ERROR AL ENVIAR CORREO: {str(email_error)}")
                import traceback
                print(traceback.format_exc())
            
            return Response(
                response_serializer.data, 
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            print(f"Error general: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )