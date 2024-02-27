import datetime
from statistics import mean
from django.db import transaction
from reviews.models import Review
from .models import Transactions
from booking_requests.models import BookingSession
from .serializers import TransactionSerializer, WalletSerializer
from rest_framework import generics, response, status, permissions, exceptions, views
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


class TransactionAPI(generics.CreateAPIView):
    model = Transactions
    serializer_class = TransactionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            session = BookingSession.objects.filter(id=serializer.validated_data['session_id']).first()
            currency = serializer.validated_data["currency"].lower()
            total_amount = session.total_price
            try:
                with transaction.atomic():
                    payment_intent = stripe.PaymentIntent.create(
                        payment_method_types=['card'],
                        payment_method_options={
                            'card':
                                {
                                    'request_three_d_secure': 'automatic'
                                }
                        },
                        amount=(total_amount * 100),
                        currency=currency,
                    )
                    self.model.objects.create(
                        session=session,
                        currency=currency,
                        payment_id=payment_intent.client_secret
                    )
                    session.status = 'paid'
                    session.save()
                    session.target.balance += total_amount
                    session.target.save()
                    resp_dict = dict()
                    resp_dict["publishableKey"] = settings.STRIPE_PUBLISHABLE_KEY
                    resp_dict["clientSecret"] = payment_intent.client_secret
                    return response.Response(
                        resp_dict,
                        status=status.HTTP_200_OK
                    )
            except Exception as e:
                raise exceptions.ValidationError(
                    "Something went wrong, please try again later!!"
                )
        else:
            return response.Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )


class WalletAPI(views.APIView):
    permission_classes = (permissions.IsAuthenticated,)
    model = Transactions

    def get_queryset(self):
        queryset = self.model.objects.filter(session__target_id=self.request.user.id)
        start_date = self.request.query_params.get("start_date")
        end_date = self.request.query_params.get("end_date")
        if start_date and end_date:
            if isinstance(start_date, str):
                start_date = datetime.datetime.strptime(
                    start_date, "%Y-%m-%d"
                )
            if isinstance(end_date, str):
                end_date = datetime.datetime.strptime(
                    end_date, "%Y-%m-%d"
                )
            queryset = queryset.filter(transaction_date__date__gte=start_date,
                                       transaction_date__date__lte=end_date)
            return queryset
        else:
            return queryset

    def get_serializer_class(self):
        return WalletSerializer

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        resp_dict = dict()
        resp_dict["total_earnings"] = self.request.user.balance
        target_name = self.request.user.full_name
        if self.request.user.profile_picture:
            target_profile_picture = self.request.user.profile_picture.url
        else:
            target_profile_picture = None
        resp_dict["name"] = target_name
        resp_dict["profile_picture"] = target_profile_picture
        ratings = []
        review_obj = Review.objects.filter(target_id=self.request.user.id)
        resp_dict["no_of_reviews"] = review_obj.count()
        for review in review_obj:
            ratings.append(int(review.rating))
        if ratings:
            mean_rating = mean(ratings)
            resp_dict["ratings"] = round(mean_rating, 1)

        else:
            resp_dict["ratings"] = 0
        if queryset:
            queryset = queryset.order_by('-transaction_date')
            serializer = self.get_serializer_class()
            serializer = serializer(queryset, many=True, context={"request": request})
            resp_dict["data"] = serializer.data
            return response.Response(
                resp_dict,
                status=status.HTTP_200_OK
            )
        else:
            return response.Response(
                resp_dict,
                status=status.HTTP_200_OK
            )

