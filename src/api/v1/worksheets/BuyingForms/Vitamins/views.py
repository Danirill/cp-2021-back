
from datetime import datetime, timedelta

from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import uuid
from itertools import chain, groupby
from api.v1.external_api import telegrambot
from WellbeApi import settings
from api.v1.external_api.sms import send_sms_message
from api.v1.labels.models import Label
from api.v1.orders.models import Promocode, Promoaction

from api.v1.products.models import Product, ProductCategory, ProductCombinations
from api.v1.recommendations.models import Recommendation, RecommendationDetailed, RecommendationPosition
from api.v1.surveys.models import SurveySessionAnswer
from api.v1.surveys.serializers import SurveySessionSimpleSerializer

from api.v1.worksheets.BuyingForms.Vitamins.serializers import VitaminsFormSerializer
from api.v1.worksheets.BuyingForms.models import FormAnswer, RecommendationLimit, SurveyAnswerActionsHub
from api.v1.worksheets.BuyingForms.serializers import FormSerializer
from api.v1.worksheets.BuyingForms.tasks import send_promocode, send_recommendation
from utils.utils import get_user, parse_bool, get_token, parse_int


class VitaminsBookingFormView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        ser = FormSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        form = ser.save(**ser.validated_data)

        ser1 = FormSerializer(data=ser.validated_data['jsondata'])
        ser1.is_valid(raise_exception=True)

        form_ser = VitaminsFormSerializer(data=ser1.validated_data['jsondata'])
        form_ser.is_valid(raise_exception=True)

        user = get_user(request)

        change_user_name = parse_bool(self.request.query_params.get('change_user_name'), val=False)

        if change_user_name:
            new_name = form_ser.validated_data['name']
            if new_name:
                user.name = new_name
                user.save()

        product_categories = ProductCategory.objects.filter(product_category_name__in=['Vitamins'])
        vitamin_products = Product.objects.filter(product_categories__in=product_categories)

        labels_from_form = form_ser.validated_data['labels']
        vitamins_product_to_buy = []
        labels_to_payment = []

        b_complex = None
        l_carnitin_and_mg = None
        omega = None
        skin = None
        life = None
        koenzim = None

        try:
            b_complex = Product.objects.get(uuid=uuid.UUID("1e6daee7-8585-4d56-a7fa-057b3ff625df"))
            l_carnitin_and_mg = Product.objects.get(uuid=uuid.UUID("d6b0bf73-14ee-4d60-b315-1806aa0d137e"))
            omega = Product.objects.get(uuid=uuid.UUID("38b342a5-327e-4d9f-827a-c6107694830b"))
            skin = Product.objects.get(uuid=uuid.UUID("63fa2f57-2f68-4b3f-8cfc-8b2f8733e7dd"))
            life = Product.objects.get(uuid=uuid.UUID("46535953-4466-4143-b03a-1bbd9a5554a9"))
            koenzim = Product.objects.get(uuid=uuid.UUID("6dab83d9-c0bf-4d20-bd13-5f8e39cd8f37"))
        except Product.DoesNotExist:
            print(Product.DoesNotExist.Meta)

        vitamins_product_to_buy.append(b_complex)

        if l_carnitin_and_mg and (89 in labels_from_form):
            vitamins_product_to_buy.append(l_carnitin_and_mg)

        if omega and (89 in labels_from_form or 91 in labels_from_form or 92 in labels_from_form):
            vitamins_product_to_buy.append(omega)

        if skin and (90 in labels_from_form):
            vitamins_product_to_buy.append(skin)

        if life and (93 in labels_from_form or 92 in labels_from_form):
            vitamins_product_to_buy.append(life)

        if koenzim and (92 in labels_from_form or 93 in labels_from_form or 90 in labels_from_form):
            vitamins_product_to_buy.append(koenzim)

        vitamins_product_to_buy = [el for el, _ in groupby(vitamins_product_to_buy)]
        vitamins_product_id_to_buy = [el.id for el in vitamins_product_to_buy]

        vitamins_product_to_recommended = vitamin_products.exclude(id__in=vitamins_product_id_to_buy)

        weight_label = None
        stress_label = None
        skin_label = None
        energy_label = None
        health_label = None

        try:
            weight_label = Label.objects.get(uuid=uuid.UUID("e160d6cf-31d2-47b2-a820-26a10c4c9416"))
            stress_label = Label.objects.get(uuid=uuid.UUID("7def0361-55d8-4bf2-bea3-d399127083db"))
            skin_label = Label.objects.get(uuid=uuid.UUID("1597a7ae-e407-4274-88b9-2ede6a579a9e"))
            energy_label = Label.objects.get(uuid=uuid.UUID("af9f37b8-eee7-42f5-bcb4-4688fa508fa8"))
            health_label = Label.objects.get(uuid=uuid.UUID("6125ddd6-bad4-47ea-a1a8-d0bb9198bf01"))
        except Label.DoesNotExist:
            print(Label.DoesNotExist.Meta)

        if 89 in labels_from_form and weight_label:
            labels_to_payment.append(weight_label)
        if 90 in labels_from_form and skin_label:
            labels_to_payment.append(skin_label)
        if 91 in labels_from_form and energy_label:
            labels_to_payment.append(energy_label)
        if 92 in labels_from_form and stress_label:
            labels_to_payment.append(stress_label)
        if 93 in labels_from_form and health_label:
            labels_to_payment.append(health_label)



        recommendation_data = {
            'info': ser.validated_data['jsondata'],
            'user': user
        }

        recommendation = Recommendation.objects.create(**recommendation_data)
        recommendation.main_products.add(*vitamins_product_to_buy)
        recommendation.optional_products.add(*vitamins_product_to_recommended)
        recommendation.labels.add(*labels_to_payment)
        recommendation.save()

        recommendation_link = f"{settings.FRONTEND_URL}/recommendations/?id={recommendation.uuid}"

        if settings.DEBUG:
            from api.v1.external_api import telegrambot
            telegrambot.send_message_html(f"Рекомендация для {user.name} {recommendation_link}")
            return Response({
                "recommendation_uuid": recommendation.uuid,
                "link": recommendation_link
            }, status.HTTP_200_OK)
        else:
            send_sms_message(user.phone, f"Ваша рекоммендация: {recommendation_link}")
            return Response({
                "recommendation_uuid": recommendation.uuid
            }, status.HTTP_200_OK)

class NewVitaminsBookingFormView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        ser = FormSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        form = ser.save(**ser.validated_data)

        ser1 = FormSerializer(data=ser.validated_data['jsondata'])
        ser1.is_valid(raise_exception=True)

        form_ser = VitaminsFormSerializer(data=ser1.validated_data['jsondata'])
        form_ser.is_valid(raise_exception=True)

        user = get_user(request)

        change_user_name = parse_bool(self.request.query_params.get('change_user_name'), val=False)

        if change_user_name:
            new_name = form_ser.validated_data['name']
            if new_name:
                user.name = new_name
                user.save()

        change_user_email = parse_bool(self.request.query_params.get('change_user_email'), val=False)

        if change_user_email and ser.data['email']:
            new_email = ser.validated_data['email']
            if new_email:
                user.email = new_email
                user.save()

        # Подсчитываем баллы
        recommendation_cache = {}

        product_categories = ProductCategory.objects.filter(product_category_name__in=['to_recommend'])
        to_recommend_products_ids = Product.objects.filter(product_categories__in=product_categories).values('id')
        limits_to_algorithm = RecommendationLimit.objects.filter(product_id__in=to_recommend_products_ids)

        # Проставляем всем потенциальным витаминам 0
        for e in limits_to_algorithm:
            recommendation_cache[e] = 0

        # Проставляем баллы в словарь
        for code in form_ser.validated_data['labels']:
            try:
                answer = FormAnswer.objects.get(code=code)
                if answer.answer_scores:
                    for answer_score in answer.answer_scores.all():
                        if answer_score.recommendation_limit:
                            recommendation_limit = answer_score.recommendation_limit
                            if recommendation_limit in recommendation_cache:
                                recommendation_cache[recommendation_limit] += answer_score.score
                            else:
                                recommendation_cache[recommendation_limit] = answer_score.score
            except FormAnswer.DoesNotExist:
                continue

        recommendation_cache = dict(sorted(recommendation_cache.items(), key=lambda item: item[1]))

        # Составляем два списка на основе баллов
        products_to_buy = []
        products_to_recommend = []

        for key, value in recommendation_cache.items():
            if value >= key.main_limit:
                products_to_buy.append(key.product)
            else:
                products_to_recommend.append(key.product)

        # Добавляем желательные комбинации
        for product in products_to_buy:
            try:
                product_combinations = ProductCombinations.objects.get(product=product)
                positive_combinations = product_combinations.positive_combinations
                for positive_combination in positive_combinations.all():
                    # Если это таблетка, то в основной набор
                    if positive_combination.product_categories.filter(product_category_name="to_recommend").exists():
                        if product not in products_to_buy:
                            products_to_buy.append(product)
                    else:
                        if product not in products_to_recommend:
                            products_to_recommend.append(product)
            except ProductCombinations.DoesNotExist:
                continue

        # Исключаем несочетающиеся
        for product in products_to_buy:
            try:
                product_combinations = ProductCombinations.objects.get(product=product)
                negative_combinations = product_combinations.negative_combinations.all()
                for negative_product in negative_combinations:
                    if negative_product in products_to_recommend:
                        products_to_recommend.remove(negative_product)
                    if negative_product in products_to_buy:
                        products_to_buy.remove(negative_product)
            except ProductCombinations.DoesNotExist:
                continue

        for product in products_to_recommend:
            try:
                product_combinations = ProductCombinations.objects.get(product=product)
                negative_combinations = product_combinations.negative_combinations.all()
                for negative_product in negative_combinations:
                    if negative_product in products_to_recommend:
                        products_to_recommend.remove(negative_product)
            except ProductCombinations.DoesNotExist:
                continue

        # Корректируем длины массивов
        PRODUCTS_TO_BUY_MINIMUM = 4
        PRODUCTS_TO_RECOMMEND_MAXIMUM = 4
        RECOMMENDATION_PRICE_MINIMUM = 1000

        total_sum = lambda x: sum(int(product.price) for product in x)

        while((len(products_to_buy) < PRODUCTS_TO_BUY_MINIMUM or total_sum(products_to_buy) < RECOMMENDATION_PRICE_MINIMUM)
              and len(products_to_recommend) > 0):
            transit_product = products_to_recommend.pop(0)
            products_to_buy.append(transit_product)

        if len(products_to_recommend) > PRODUCTS_TO_RECOMMEND_MAXIMUM:
            products_to_recommend = products_to_recommend[:PRODUCTS_TO_RECOMMEND_MAXIMUM]

        # Получаем лейблы
        labels = Label.objects.none()
        for product in products_to_buy:
            labels = labels.union(product.labels.all())

        recommendation_data = {
            'info': ser.validated_data['jsondata'],
            'user': user
        }

        recommendation = Recommendation.objects.create(**recommendation_data)
        recommendation.main_products.add(*products_to_buy)
        recommendation.optional_products.add(*products_to_recommend)
        recommendation.labels.add(*labels)
        recommendation.save()

        recommendation_link = recommendation.get_link()

        hello_promoaction = Promoaction.objects.get_or_create(name='Vitamins_First_Survey',
                                                              defaults={
                                                                  "name": "Vitamins_First_Survey",
                                                                  "absolute_discount": 0,
                                                                  "relative_discount": 15,
                                                                  "use_absolute_discount": False
                                                              })[0]
        promocode_data = {
            "start_time": datetime.now(),
            "end_time": datetime.now() + timedelta(days=2),
            "is_active": True,
            "token": get_token(4, only_digits=True),
            "usage_limit": 1,
            "has_usage_limit": True,
            "has_time_limit": True,
            "action": hello_promoaction
        }
        promocode = Promocode.objects.create(**promocode_data)
        tomorrow = datetime.now() + timedelta(days=1)

        send_promocode.apply_async(args=[user.id, promocode.id, recommendation_link], eta=tomorrow)

        if settings.DEBUG:
            telegrambot.send_message_html(f"Рекомендация для {user.name} {recommendation_link}")
            send_recommendation(user.id, recommendation_link)
            return Response({
                "recommendation_uuid": recommendation.uuid,
                "link": recommendation_link
            }, status.HTTP_200_OK)
        else:
            telegrambot.send_message_html(f"Рекомендация для {user.name} {recommendation_link}")
            send_recommendation(user.id, recommendation_link)
            return Response({
                "recommendation_uuid": recommendation.uuid
            }, status.HTTP_200_OK)

class SurveyGetRecommendations(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        session_id = parse_int(s=self.request.query_params.get('session_id'), val=None)
        data = {
            "survey_session_id": session_id
        }
        ser = SurveySessionSimpleSerializer(data=data)
        ser.is_valid(raise_exception=True)
        session = ser.validated_data['survey_session_id']
        user = get_user(request)

        change_user_name = parse_bool(self.request.query_params.get('change_user_name'), val=False)

        if change_user_name:
            try:
                new_name = SurveySessionAnswer.objects.get(survey_session=session, key='name')
                user.name = new_name.value.content
                user.save()
            except SurveySessionAnswer.DoesNotExist:
                pass

        change_user_email = parse_bool(self.request.query_params.get('change_user_email'), val=False)

        if change_user_email:
            try:
                new_email = SurveySessionAnswer.objects.get(survey_session=session, key='email')
                user.email = new_email.value.content
                user.save()
            except SurveySessionAnswer.DoesNotExist:
                pass

        answers = SurveySessionAnswer.objects.filter(survey_session=session)
        product_actions_cache = {}
        # { product : [action, action] }

        product_categories = ProductCategory.objects.filter(product_category_name__in=['to_recommend'])
        all_recommendation_products = Product.objects.filter(product_categories__in=product_categories)

        for x in all_recommendation_products:
            product_actions_cache[x] = []

        for answer in answers:
            try:
                actions_hub = SurveyAnswerActionsHub.objects.get(key=answer.key, value=answer.value.content)
                for action in actions_hub.answer_actions.all():
                    if action.product not in product_actions_cache:
                        product_actions_cache[action.product] = []
                    product_actions_cache[action.product].append(action)
            except SurveyAnswerActionsHub.DoesNotExist:
                continue
            except SurveyAnswerActionsHub.MultipleObjectsReturned:
                continue
                # Todo: Надо что-то сделать

        def get_points(actions):
            points = 0
            for e in actions:
                points += e.score
            return points

        sorted_product_actions_cache = dict(sorted(product_actions_cache.items(),
                                                   key=lambda item: get_points(item[1]),
                                                   reverse=True))

        products_to_buy = []  # recommendation_limit_overcame
        products_to_recommend = []  # recommendation_limit_not_overcame

        for key, value in sorted_product_actions_cache.items():
            try:
                recommendation_limit = RecommendationLimit.objects.get(product=key)
                if recommendation_limit.main_limit <= get_points(value):
                    products_to_buy.append(key)
                else:
                    products_to_recommend.append(key)
            except RecommendationLimit.DoesNotExist or RecommendationLimit.MultipleObjectsReturned:
                continue

        # Добавляем желательные комбинации
        for product in products_to_buy:
            try:
                product_combinations = ProductCombinations.objects.get(product=product)
                positive_combinations = product_combinations.positive_combinations
                for positive_combination in positive_combinations.all():
                    # Если это таблетка, то в основной набор
                    if positive_combination.product_categories.filter(
                            product_category_name="to_recommend").exists():
                        if product not in products_to_buy:
                            products_to_buy.append(product)
                    else:
                        if product not in products_to_recommend:
                            products_to_recommend.append(product)
            except ProductCombinations.DoesNotExist:
                continue

        # Исключаем несочетающиеся
        for product in products_to_buy:
            try:
                product_combinations = ProductCombinations.objects.get(product=product)
                negative_combinations = product_combinations.negative_combinations.all()
                for negative_product in negative_combinations:
                    if negative_product in products_to_recommend:
                        products_to_recommend.remove(negative_product)
                    if negative_product in products_to_buy:
                        products_to_buy.remove(negative_product)
            except ProductCombinations.DoesNotExist:
                continue

        for product in products_to_recommend:
            try:
                product_combinations = ProductCombinations.objects.get(product=product)
                negative_combinations = product_combinations.negative_combinations.all()
                for negative_product in negative_combinations:
                    if negative_product in products_to_recommend:
                        products_to_recommend.remove(negative_product)
            except ProductCombinations.DoesNotExist:
                continue

        PRODUCTS_TO_BUY_MINIMUM = 5
        PRODUCTS_TO_BUY_MAXIMUM = 6
        PRODUCTS_TO_RECOMMEND_MAXIMUM = 0
        RECOMMENDATION_PRICE_MINIMUM = 0

        total_sum = lambda x: sum(int(product.price) for product in x)

        while ((len(products_to_buy) < PRODUCTS_TO_BUY_MINIMUM or total_sum(
                products_to_buy) < RECOMMENDATION_PRICE_MINIMUM)
               and len(products_to_recommend) > 0):
            transit_product = products_to_recommend.pop(0)
            products_to_buy.append(transit_product)

        if len(products_to_recommend) > PRODUCTS_TO_RECOMMEND_MAXIMUM:
            products_to_recommend = products_to_recommend[:PRODUCTS_TO_RECOMMEND_MAXIMUM]

        if len(products_to_buy) > PRODUCTS_TO_BUY_MAXIMUM:
            products_to_buy = products_to_buy[:PRODUCTS_TO_BUY_MAXIMUM]

        # Получаем лейблы
        labels = Label.objects.none()
        for product in products_to_buy:
            labels = labels.union(product.labels.all())

        detailed_recommendation_data = {
            'user': user
        }

        detailed_recommendation = RecommendationDetailed.objects.create(**detailed_recommendation_data)

        for main_product in products_to_buy:
            recommendation_position_data = {
                "product": main_product
            }
            recommendation_position = RecommendationPosition.objects.create(**recommendation_position_data)
            for e in sorted_product_actions_cache[main_product]:
                recommendation_position.actions.add(e)
            recommendation_position.save()
            detailed_recommendation.main_positions.add(recommendation_position)

        for optional_product in products_to_recommend:
            recommendation_position_data = {
                "product": optional_product
            }
            recommendation_position = RecommendationPosition.objects.create(**recommendation_position_data)
            for e in sorted_product_actions_cache[optional_product]:
                recommendation_position.actions.add(e)
            recommendation_position.save()
            detailed_recommendation.optional_positions.add(recommendation_position)

        detailed_recommendation.labels.add(*labels)
        detailed_recommendation.save()

        recommendation_link = detailed_recommendation.get_link()

        hello_promoaction = Promoaction.objects.get_or_create(name='Vitamins_First_Survey',
                                                              defaults={
                                                                  "name": "Vitamins_First_Survey",
                                                                  "absolute_discount": 0,
                                                                  "relative_discount": 15,
                                                                  "use_absolute_discount": False
                                                              })[0]
        promocode_data = {
            "start_time": datetime.now(),
            "end_time": datetime.now() + timedelta(days=2),
            "is_active": True,
            "token": get_token(4, only_digits=True),
            "usage_limit": 1,
            "has_usage_limit": True,
            "has_time_limit": True,
            "action": hello_promoaction
        }
        promocode = Promocode.objects.create(**promocode_data)
        tomorrow = datetime.now() + timedelta(days=1)

        send_promocode.apply_async(args=[user.id, promocode.id, recommendation_link], eta=tomorrow)
        detalization_link = f"https://{request.META['HTTP_HOST']}/api/v1/surveys/session/{session.id}/detalization"
        if settings.DEBUG:
            telegrambot.send_message_html(f"Рекомендация для {user.name} {recommendation_link} \n подробности: \n {detalization_link}")
            send_recommendation(user.id, recommendation_link)
            return Response({
                "detailed_recommendation_uuid": detailed_recommendation.uuid,
                "link": recommendation_link
            }, status.HTTP_200_OK)
        else:
            telegrambot.send_message_html(f"Рекомендация для {user.name} {recommendation_link} \n подробности: \n {detalization_link}")
            send_recommendation(user.id, recommendation_link)
            return Response({
                "detailed_recommendation_uuid": detailed_recommendation.uuid
            }, status.HTTP_200_OK)

class SurveyGetRecommendationsSimple(APIView):

    def get(self, request):
        session_id = parse_int(s=self.request.query_params.get('session_id'), val=None)
        data = {
            "survey_session_id": session_id
        }
        ser = SurveySessionSimpleSerializer(data=data)
        ser.is_valid(raise_exception=True)
        session = ser.validated_data['survey_session_id']


        answers = SurveySessionAnswer.objects.filter(survey_session=session)
        product_actions_cache = {}
        # { product : [action, action] }

        product_categories = ProductCategory.objects.filter(product_category_name__in=['to_recommend'])
        all_recommendation_products = Product.objects.filter(product_categories__in=product_categories)

        for x in all_recommendation_products:
            product_actions_cache[x] = []

        def get_successed_actions(key, value):
            actions_hubs = SurveyAnswerActionsHub.objects.filter(key=key)
            result_hubs = []
            for actions_hub in actions_hubs:
                if actions_hub.condition:
                    if actions_hub.condition.execute(actions_hub.value, value):
                        result_hubs.append(actions_hub)
                else:
                    if actions_hub.value == value:
                        result_hubs.append(actions_hub)
            return result_hubs

        for answer in answers:
            actions_hubs = get_successed_actions(answer.key, answer.value.content)
            print("----------------")
            print(type(actions_hubs))
            print(actions_hubs)
            print("----------------")
            for actions_hub in actions_hubs:
                for action in actions_hub.answer_actions.all():
                    if action.product not in product_actions_cache:
                        product_actions_cache[action.product] = []
                    product_actions_cache[action.product].append(action)

        #убираем дублирующиеся экшены
        # for key, value in product_actions_cache.items():
        #     product_actions_cache[key] = list(set(key))

        def get_points(actions):
            points = 0
            for e in actions:
                points += e.score
            return points

        sorted_product_actions_cache = dict(sorted(product_actions_cache.items(),
                                                   key=lambda item: get_points(item[1]),
                                                   reverse=True))

        products_to_buy = []  # recommendation_limit_overcame
        products_to_recommend = []  # recommendation_limit_not_overcame

        for key, value in sorted_product_actions_cache.items():
            try:
                recommendation_limit = RecommendationLimit.objects.get(product=key)
                if recommendation_limit.main_limit <= get_points(value):
                    products_to_buy.append(key)
                else:
                    products_to_recommend.append(key)
            except RecommendationLimit.DoesNotExist or RecommendationLimit.MultipleObjectsReturned:
                continue

        # Добавляем желательные комбинации
        for product in products_to_buy:
            try:
                product_combinations = ProductCombinations.objects.get(product=product)
                positive_combinations = product_combinations.positive_combinations
                for positive_combination in positive_combinations.all():
                    # Если это таблетка, то в основной набор
                    if positive_combination.product_categories.filter(
                            product_category_name="to_recommend").exists():
                        if product not in products_to_buy:
                            products_to_buy.append(product)
                    else:
                        if product not in products_to_recommend:
                            products_to_recommend.append(product)
            except ProductCombinations.DoesNotExist:
                continue

        # Исключаем несочетающиеся
        for product in products_to_buy:
            try:
                product_combinations = ProductCombinations.objects.get(product=product)
                negative_combinations = product_combinations.negative_combinations.all()
                for negative_product in negative_combinations:
                    if negative_product in products_to_recommend:
                        products_to_recommend.remove(negative_product)
                    if negative_product in products_to_buy:
                        products_to_buy.remove(negative_product)
            except ProductCombinations.DoesNotExist:
                continue

        for product in products_to_recommend:
            try:
                product_combinations = ProductCombinations.objects.get(product=product)
                negative_combinations = product_combinations.negative_combinations.all()
                for negative_product in negative_combinations:
                    if negative_product in products_to_recommend:
                        products_to_recommend.remove(negative_product)
            except ProductCombinations.DoesNotExist:
                continue

        PRODUCTS_TO_BUY_MINIMUM = 5
        PRODUCTS_TO_BUY_MAXIMUM = 6
        PRODUCTS_TO_RECOMMEND_MAXIMUM = 0
        RECOMMENDATION_PRICE_MINIMUM = 0

        total_sum = lambda x: sum(int(product.price) for product in x)

        while ((len(products_to_buy) < PRODUCTS_TO_BUY_MINIMUM or total_sum(
                products_to_buy) < RECOMMENDATION_PRICE_MINIMUM)
               and len(products_to_recommend) > 0):
            transit_product = products_to_recommend.pop(0)
            products_to_buy.append(transit_product)

        if len(products_to_recommend) > PRODUCTS_TO_RECOMMEND_MAXIMUM:
            products_to_recommend = products_to_recommend[:PRODUCTS_TO_RECOMMEND_MAXIMUM]

        if len(products_to_buy) > PRODUCTS_TO_BUY_MAXIMUM:
            products_to_buy = products_to_buy[:PRODUCTS_TO_BUY_MAXIMUM]

        # Получаем лейблы
        labels = Label.objects.none()
        for product in products_to_buy:
            labels = labels.union(product.labels.all())

        detailed_recommendation_data = {}

        detailed_recommendation = RecommendationDetailed.objects.create(**detailed_recommendation_data)

        for main_product in products_to_buy:
            recommendation_position_data = {
                "product": main_product
            }
            recommendation_position = RecommendationPosition.objects.create(**recommendation_position_data)
            for e in sorted_product_actions_cache[main_product]:
                recommendation_position.actions.add(e)
            recommendation_position.save()
            detailed_recommendation.main_positions.add(recommendation_position)

        for optional_product in products_to_recommend:
            recommendation_position_data = {
                "product": optional_product
            }
            recommendation_position = RecommendationPosition.objects.create(**recommendation_position_data)
            for e in sorted_product_actions_cache[optional_product]:
                recommendation_position.actions.add(e)
            recommendation_position.save()
            detailed_recommendation.optional_positions.add(recommendation_position)

        detailed_recommendation.labels.add(*labels)

        MINIMUM_ANALYSES_RECOMMENDATIONS_COUNT = 3
        recommendated_analyses = []
        # Добавляем рекомендации для анализов
        for e in reversed(list(detailed_recommendation.main_positions.all())):
            if len(recommendated_analyses) < MINIMUM_ANALYSES_RECOMMENDATIONS_COUNT:
                recommendated_analyses.append({
                    "char_code": e.product.product_charcode,
                    "product_name": e.product.product_name
                })
            else:
                break

        detailed_recommendation.data = {
            "recommendated_analyses": recommendated_analyses
        }

        detailed_recommendation.save()

        return Response({
            "detailed_recommendation_uuid": detailed_recommendation.uuid
        }, status.HTTP_200_OK)
