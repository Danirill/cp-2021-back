from datetime import datetime

from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from WellbeApi import settings
from utils.utils import parse_int, PromocodeTokenNotValid, get_token
from .models import Product, ProductCategory
from .serializers import ProductInputSerializer, ProductSerializer, ProductManyInputSerializer, CartPriceSerializer
from .utils import get_cart_sum
from ..orders.models import Promocode
from ..orders.utils import try_promocode, try_promocode_for_delivery


class ProductView(APIView):

    def get(self, request, product_id=0):
        request.data['product_id'] = product_id
        ser = ProductInputSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        promo_token = request.query_params.get('token')
        product = ser.validated_data['product_id']
        product_old_price = product.price
        promocode_status = False

        if promo_token:
            promocodes = Promocode.objects.filter(products__exact=product, token=promo_token, is_active=True)
            valid_promocodes = []

            for promocode in promocodes:

                if promocode.has_time_limit:
                    if not datetime.combine(promocode.start_time.date(), promocode.start_time.time()) >= datetime.now() and \
                            datetime.combine(promocode.end_time.date(), promocode.end_time.time()) < datetime.now():
                        continue

                if promocode.has_usage_limit:
                    if promocode.usage_limit <= promocode.usages:
                        continue

                if not promocode.action:
                    continue

                valid_promocodes.append(promocode)

            if valid_promocodes:
                promocode = valid_promocodes[0]

                if promocode.action.use_absolute_discount:
                    if promocode.action.absolute_discount and product.price > promocode.action.absolute_discount:
                        product.price = product.price - promocode.action.absolute_discount
                        promocode.usages += 1
                        promocode.save()
                        promocode_status = True
                else:
                    if promocode.action.relative_discount and 0 < promocode.action.relative_discount < 100:
                        product.price = round(product.price * (100 - promocode.action.relative_discount) / 100, 0)
                        promocode.usages += 1
                        promocode.save()
                        promocode_status = True

        return Response({
            'product': ProductSerializer(product, context={"request": request}).data,
            'status': promocode_status,
            'old_price': product_old_price
        }, status.HTTP_200_OK)

class ShopView(APIView):
    def get(self, request):
        category_list = self.request.GET.getlist("category")
        q = self.request.query_params.get('q')
        products = Product.objects.all()

        if category_list:
            product_categories = ProductCategory.objects.filter(product_category_name__in=category_list)
            products = products.filter(product_categories__in=product_categories)

        if q:
            products = products.filter(
                Q(product_name__icontains=q) |
                Q(description_format__icontains=q) |
                Q(description_mini__icontains=q)
            )
        products = products.distinct()

        page = parse_int(s=self.request.query_params.get('page'), val=1)
        limit = parse_int(s=self.request.query_params.get('limit'), val=50)

        paginator = Paginator(products, limit)

        try:
            product_set = paginator.page(page)
        except EmptyPage:
            product_set = paginator.page(paginator.num_pages)
            page = paginator.num_pages

        return Response({
            "data": ProductSerializer(product_set, many=True, context={"request": request}).data,
            "page": page,
            "num_pages": paginator.num_pages,
            "limit": limit
        }, status.HTTP_200_OK)

class ShopCart(APIView):
    def post(self, request):
        products_ser = ProductManyInputSerializer(data=request.data)
        products_ser.is_valid(raise_exception=True)

        return Response(ProductSerializer(products_ser.validated_data['products'],
                                          many=True,
                                          context={"request": request}).data,
                        status.HTTP_200_OK)

class CartPrice(APIView):
    def post(self, request):
        ser = CartPriceSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        order_positions = []
        for e in ser.validated_data['data']:
            order_positions.append({
                "product": e['product_id'],
                "count": e['count']
            })
        sum = get_cart_sum(order_positions)
        month = ser.validated_data['month']
        one_delivery_cost = settings.DELIVERY_DEFAULT_COST

        try:
            token = None
            if 'token' in ser.validated_data.keys():
                token = ser.validated_data['token']
            sum = try_promocode(sum, token)
            one_delivery_cost = try_promocode_for_delivery(one_delivery_cost, token)
        except PromocodeTokenNotValid:
            print("oops")

        return Response({
            "sum": (sum + one_delivery_cost) * month
        }, status.HTTP_200_OK)

def get_subscription_pricing_info(request, month=1, use_request_month=True):

    if not use_request_month:
        request.data['month'] = month

    ser = CartPriceSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    order_positions = []
    for e in ser.validated_data['data']:
        order_positions.append({
            "product": e['product_id'],
            "count": e['count']
        })
    # sub_price = get_cart_sum(order_positions)
    month = ser.validated_data['month']
    one_delivery_cost = settings.DELIVERY_DEFAULT_COST

    if month in settings.TARIFFS:
        one_month_subscription_price = settings.TARIFFS[month]
    else:
        one_month_subscription_price = 2990

    is_promocode_used = True

    try:
        token = None
        if 'token' in ser.validated_data.keys():
            token = ser.validated_data['token']
        one_month_subscription_price = try_promocode(one_month_subscription_price, token)
        one_delivery_cost = try_promocode_for_delivery(one_delivery_cost, token)
    except PromocodeTokenNotValid:
        is_promocode_used = False

    return {
        "total_sum": (one_month_subscription_price + one_delivery_cost) * month,
        "sum_without_delivery": (one_month_subscription_price) * month,
        "delivery": one_delivery_cost * month,
        "economy": (settings.TARIFFS[1] + settings.DELIVERY_DEFAULT_COST) * month -
                   (one_month_subscription_price + one_delivery_cost) * month,
        "one_month_cost": one_month_subscription_price,
        "day_cost": round(one_month_subscription_price / 30),
        "is_promocode_used": is_promocode_used
    }

class SubscriptionPrice(APIView):
    def post(self, request):
        return Response(get_subscription_pricing_info(request), status.HTTP_200_OK)

class SubscriptionPricing(APIView):
    def post(self, request):
        return Response({
            1: get_subscription_pricing_info(request),
            3: get_subscription_pricing_info(request, month=3, use_request_month=False),
            6: get_subscription_pricing_info(request, month=6, use_request_month=False),
            12: get_subscription_pricing_info(request, month=12, use_request_month=False)
        }, status.HTTP_200_OK)

