from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from .filters import TitleFilter
from .models import Category, Genre, Review, Title, User
from .permission import (
    IsAdmin, IsAdminOrReadOnly, IsOwnerAdminModeratorOrReadOnly,
)
from .serializers import (
    CategorySerializer, CommentSerializer, ConfirmationCodeSerializer,
    EmailSerializer, GenreSerializer, ReviewSerializer, TitleCreateSerializer,
    TitleSerializer, UserSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    http_method_names = ['get', 'post',
                         'patch', 'delete']
    filter_backends = [filters.SearchFilter]
    search_fields = ['username']
    lookup_field = 'username'

    @action(detail=False, methods=['get', 'patch'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        else:
            serializer = self.get_serializer(
                request.user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                data=serializer.data, status=status.HTTP_200_OK
            )


class EmailRegistrationView(views.APIView):
    permission_classes = [AllowAny]

    @staticmethod
    def mail_send(email, user):
        send_mail(
            subject='YaMDB Confirmation Code',
            message=f'Hello! \n\nYour confirmation: '
                    f'{user.confirmation_code}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False
        )

    def post(self, request):
        serializer = EmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        serializer.save(email=email)
        user = get_object_or_404(User, email=email)
        self.mail_send(email, user)
        return Response({f'email: {email}'}, status=status.HTTP_200_OK)


class AccessTokenView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ConfirmationCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        confirmation_code = serializer.validated_data['confirmation_code']
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'email':
                    'Not found'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if user.confirmation_code != confirmation_code:
            return Response({
                'confirmation_code':
                    f'Invalid confirmation code for email {user.email}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        return Response(self.get_token(user), status=status.HTTP_200_OK)

    @staticmethod
    def get_token(user):
        return {
            'token': str(AccessToken.for_user(user))
        }


class CustomViewSet(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    pass


class CategoryViewSet(CustomViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'
    permission_classes = [
        IsAdminOrReadOnly,
    ]


class GenreViewSet(CustomViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    lookup_field = 'slug'
    permission_classes = [
        IsAdminOrReadOnly,
    ]


class TitleViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter
    permission_classes = [IsAdminOrReadOnly]
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).order_by('-id')

    def get_serializer_class(self):
        if self.request.method in ['GET']:
            return TitleSerializer
        else:
            return TitleCreateSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [
        IsOwnerAdminModeratorOrReadOnly
    ]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(
            author=self.request.user,
            title=title
        )


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [
        IsOwnerAdminModeratorOrReadOnly
    ]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id, title=title_id)
        return review.comments.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        review = get_object_or_404(Review, id=review_id, title=title_id)
        serializer.save(
            author=self.request.user,
            review=review
        )
