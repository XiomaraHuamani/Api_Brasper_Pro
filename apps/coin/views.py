from django.shortcuts import get_object_or_404
from django.db import IntegrityError
from rest_framework.generics import GenericAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from rest_framework import mixins, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Currency, ExchangeRate, Commission, Range
from .serializers import CommissionSerializerApp, CurrencySerializer, ExchangeRateSerializer, CommissionSerializer, ExchangeRateSerializerApp, RangeSerializer, ReverseCommissionSerializerApp
from apps.users.permissions import IsStaff

class CurrencyView(GenericAPIView):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    permission_classes = [AllowAny]

    def get(self, request):
        currencies = self.get_queryset()
        serializer = self.serializer_class(currencies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CurrencyDetailView(GenericAPIView):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    # permission_classes = [IsAuthenticated]

    def get_object(self, currency_id):
        return get_object_or_404(self.get_queryset(), id=currency_id)

    def get(self, request, currency_id):
        currency = self.get_object(currency_id)
        serializer = self.serializer_class(currency)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, currency_id):
        currency = self.get_object(currency_id)
        serializer = self.serializer_class(currency, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, currency_id):
        currency = self.get_object(currency_id)
        currency.delete()
        return Response({"message": "Currency deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class ExchangeRateView(GenericAPIView):
    queryset = ExchangeRate.objects.all()
    serializer_class = ExchangeRateSerializer
    # permission_classes = [IsAuthenticated]
    def get_permissions(self):
        if self.request.method in ['GET', 'HEAD', 'OPTIONS']:
            return [AllowAny()]
        return [IsStaff()]
    def get(self, request):
        exchange_rates = self.get_queryset()
        serializer = self.serializer_class(exchange_rates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ExchangeRateDetailView(GenericAPIView):
    queryset = ExchangeRate.objects.all()
    serializer_class = ExchangeRateSerializer
    # permission_classes = [IsAuthenticated]

    def get_object(self, exchange_rate_id):
        return get_object_or_404(self.get_queryset(), id=exchange_rate_id)

    def get(self, request, exchange_rate_id):
        exchange_rate = self.get_object(exchange_rate_id)
        serializer = self.serializer_class(exchange_rate)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, exchange_rate_id):
        exchange_rate = self.get_object(exchange_rate_id)
        serializer = self.serializer_class(exchange_rate, data=request.data)
        if serializer.is_valid():
            # Obtener el nombre de usuario o email del usuario autenticado
            user_name = getattr(request.user, 'username', None) or getattr(request.user, 'email', 'Anonymous')
            instance = serializer.save(updated_by=user_name)
            # Refrescar el objeto desde la base de datos para obtener updated_date actualizado
            instance.refresh_from_db()
            # Serializar nuevamente con los datos actualizados
            serializer = self.serializer_class(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, exchange_rate_id):
        exchange_rate = self.get_object(exchange_rate_id)
        serializer = self.serializer_class(exchange_rate, data=request.data, partial=True)
        if serializer.is_valid():
            # Obtener el nombre de usuario o email del usuario autenticado
            user_name = getattr(request.user, 'username', None) or getattr(request.user, 'email', 'Anonymous')
            instance = serializer.save(updated_by=user_name)
            # Refrescar el objeto desde la base de datos para obtener updated_date actualizado
            instance.refresh_from_db()
            # Serializar nuevamente con los datos actualizados
            serializer = self.serializer_class(instance)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, exchange_rate_id):
        exchange_rate = self.get_object(exchange_rate_id)
        exchange_rate.delete()
        return Response({"message": "Exchange rate deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class RangeView(GenericAPIView):
    queryset = Range.objects.all()
    serializer_class = RangeSerializer
    permission_classes = [AllowAny]

    def get(self, request):
        ranges = self.get_queryset()
        serializer = self.serializer_class(ranges, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            # Interceptar y mejorar mensajes de error de unique_together
            # En settings.py, NON_FIELD_ERRORS_KEY está configurado como "error"
            errors = serializer.errors
            if 'error' in errors:
                error_list = errors['error']
                if isinstance(error_list, list):
                    # Buscar el mensaje de unique_together y reemplazarlo
                    for i, error_msg in enumerate(error_list):
                        if isinstance(error_msg, str) and ('unique' in error_msg.lower() or 'min_amount, max_amount' in error_msg.lower()):
                            min_amount = request.data.get('min_amount', 'N/A')
                            max_amount = request.data.get('max_amount', 'N/A')
                            errors['error'][i] = f'Ya existe un rango con min_amount={min_amount} y max_amount={max_amount}. La combinación de min_amount y max_amount debe ser única.'
            elif 'non_field_errors' in errors:
                # Fallback por si cambia la configuración
                non_field_errors = errors['non_field_errors']
                if isinstance(non_field_errors, list):
                    for i, error_msg in enumerate(non_field_errors):
                        if isinstance(error_msg, str) and ('unique' in error_msg.lower() or 'min_amount, max_amount' in error_msg.lower()):
                            min_amount = request.data.get('min_amount', 'N/A')
                            max_amount = request.data.get('max_amount', 'N/A')
                            errors['non_field_errors'][i] = f'Ya existe un rango con min_amount={min_amount} y max_amount={max_amount}. La combinación de min_amount y max_amount debe ser única.'
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except IntegrityError as e:
            # Manejar errores de integridad de la base de datos como respaldo
            if 'unique' in str(e).lower() or 'duplicate' in str(e).lower():
                return Response({
                    'error': 'Ya existe un rango con esta combinación de min_amount y max_amount. '
                            'La combinación de min_amount y max_amount debe ser única.'
                }, status=status.HTTP_400_BAD_REQUEST)
            return Response({
                'error': 'Error al crear el rango. Por favor verifica los datos.'
            }, status=status.HTTP_400_BAD_REQUEST)

class RangeDetailView(GenericAPIView):
    queryset = Range.objects.all()
    serializer_class = RangeSerializer
    permission_classes = [AllowAny]

    def get_object(self, range_id):
        return get_object_or_404(self.get_queryset(), id=range_id)

    def get(self, request, range_id):
        range_obj = self.get_object(range_id)
        serializer = self.serializer_class(range_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, range_id):
        range_obj = self.get_object(range_id)
        serializer = self.serializer_class(range_obj, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, range_id):
        range_obj = self.get_object(range_id)
        range_obj.delete()
        return Response({"message": "Range deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

class CommissionView(ListCreateAPIView):
    queryset = Commission.objects.all()
    serializer_class = CommissionSerializer
    
    def get_permissions(self):
        if self.request.method in ['GET', 'POST', 'HEAD', 'OPTIONS']:
            return [AllowAny()]
        return [IsStaff()]
    
    def get_queryset(self):
        # Obtenemos las comisiones ordenadas por ID
        return super().get_queryset().order_by('id')
    
    def list(self, request, *args, **kwargs):
        """
        Lista todas las comisiones usando DRF estándar ordenadas por ID
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

class CommissionRangeView(GenericAPIView):
    queryset = Commission.objects.all()
    serializer_class = CommissionSerializer

    def get(self, request):
        # Obtenemos todas las comisiones
        commissions = self.get_queryset()
        
        # Creamos un diccionario para agrupar por combinación de monedas
        grouped_commissions = {}
        
        for commission in commissions:
            key = (commission.base_currency, commission.target_currency)
            range_amount = float(commission.range.min_amount)
            
            if key not in grouped_commissions:
                grouped_commissions[key] = {
                    'min_range': commission,
                    'max_range': commission
                }
            else:
                # Actualizamos el mínimo si encontramos uno menor
                if range_amount < float(grouped_commissions[key]['min_range'].range.min_amount):
                    grouped_commissions[key]['min_range'] = commission
                # Actualizamos el máximo si encontramos uno mayor
                if range_amount > float(grouped_commissions[key]['max_range'].range.min_amount):
                    grouped_commissions[key]['max_range'] = commission

        # Preparamos la lista de resultados
        result = []
        for key, value in grouped_commissions.items():
            result.extend([
                self.serializer_class(value['min_range']).data,
                self.serializer_class(value['max_range']).data
            ])

        # Ordenamos el resultado final
        sorted_result = sorted(
            result,
            key=lambda x: (
                x['base_currency'],
                x['target_currency'],
                float(x['range_details']['min_amount'])
            )
        )

        return Response(sorted_result, status=status.HTTP_200_OK)

class CommissionDetailView(RetrieveUpdateDestroyAPIView):
    """
    Vista genérica de DRF para obtener, actualizar parcialmente y eliminar una comisión específica.
    Usa RetrieveUpdateDestroyAPIView que proporciona automáticamente:
    - GET: retrieve (obtener detalle)
    - PATCH: partial_update (actualización parcial) - PUT está deshabilitado
    - DELETE: destroy (eliminar)
    """
    queryset = Commission.objects.all()
    serializer_class = CommissionSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id'
    lookup_url_kwarg = 'commission_id'
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']

    def get_object(self):
        """
        Override para usar el lookup_url_kwarg correctamente con DRF
        """
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(self.get_queryset(), **filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj

    def retrieve(self, request, *args, **kwargs):
        """
        GET: Obtiene el detalle de una comisión usando DRF estándar
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_update(self, serializer):
        """
        Guarda la instancia actualizada
        """
        serializer.save()

    def partial_update(self, request, *args, **kwargs):
        """
        PATCH: Actualiza parcialmente una comisión usando DRF estándar
        """
        instance = self.get_object()
        
        # Remover range_details del request.data si está presente (es read_only)
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        if 'range_details' in data:
            # range_details es read_only, así que lo removemos para evitar confusión
            del data['range_details']
        
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        # Refrescar la instancia y serializar nuevamente para obtener datos actualizados
        serializer.instance.refresh_from_db()
        serializer = self.get_serializer(serializer.instance)
        return Response(serializer.data)
    

class ExchangeRateListViewApp(mixins.ListModelMixin,mixins.CreateModelMixin,GenericAPIView):
    queryset = ExchangeRate.objects.all()
    serializer_class = ExchangeRateSerializerApp

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        combined_rates = {}
        for item in serializer.data:
            combined_rates.update(item)
        return Response(combined_rates)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class ExchangeRateDetailViewApp(mixins.RetrieveModelMixin,mixins.UpdateModelMixin,mixins.DestroyModelMixin,GenericAPIView):
    queryset = ExchangeRate.objects.all()
    serializer_class = ExchangeRateSerializerApp
    lookup_fields = ['base_currency__code', 'target_currency__code']

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsStaff()] 

    def get_object(self):
        queryset = self.get_queryset()
        filter_kwargs = {
            'base_currency__code': self.kwargs['base_currency'],
            'target_currency__code': self.kwargs['target_currency']
        }
        obj = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj

    def perform_update(self, serializer):
        # Obtener el nombre de usuario o email del usuario autenticado
        user_name = getattr(self.request.user, 'username', None) or getattr(self.request.user, 'email', 'Anonymous')
        serializer.save(updated_by=user_name)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        # Refrescar la instancia y serializar nuevamente para obtener updated_date actualizado
        if hasattr(serializer, 'instance') and serializer.instance:
            serializer.instance.refresh_from_db()
            serializer = self.get_serializer(serializer.instance)
        return Response(serializer.data)

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    
# Commission Views


class CommissionRatesViewApp(GenericAPIView, mixins.ListModelMixin):
    queryset = Commission.objects.all()
    serializer_class = CommissionSerializerApp
    permission_classes = [AllowAny]
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        grouped_commissions = {}
        for item in serializer.data:
            key = f"{item['base_currency']}-{item['target_currency']}"
            if key not in grouped_commissions:
                grouped_commissions[key] = []
            grouped_commissions[key].append(item['range'])
        
        return Response(grouped_commissions)

class ReverseCommissionRatesViewApp(GenericAPIView, mixins.ListModelMixin):
    queryset = Commission.objects.all()
    serializer_class = ReverseCommissionSerializerApp
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        
        grouped_commissions = {}
        for item in serializer.data:
            key = f"{item['target_currency']}-{item['base_currency']}"
            if key not in grouped_commissions:
                grouped_commissions[key] = []
            grouped_commissions[key].append(item['range'])
        
        return Response(grouped_commissions)


class CommissionDetailViewApp(GenericAPIView, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    queryset = Commission.objects.all()
    serializer_class = CommissionSerializerApp

    def get_object(self):
        queryset = self.get_queryset()
        filter_kwargs = {
            'base_currency__code': self.kwargs['base_currency'],
            'target_currency__code': self.kwargs['target_currency'],
            'range__min_amount': self.kwargs['min_amount'],
            'range__max_amount': self.kwargs['max_amount']
        }
        obj = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

class ReverseCommissionDetailViewApp(GenericAPIView, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin):
    queryset = Commission.objects.all()
    serializer_class = ReverseCommissionSerializerApp
    # permission_classes = [IsAuthenticated]

    def get_object(self):
        queryset = self.get_queryset()
        filter_kwargs = {
            'base_currency__code': self.kwargs['target_currency'],
            'target_currency__code': self.kwargs['base_currency'],
            'range__min_amount': self.kwargs['min_amount'],
            'range__max_amount': self.kwargs['max_amount']
        }
        obj = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)