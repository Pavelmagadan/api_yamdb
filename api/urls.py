from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AccessTokenView, CategoryViewSet, CommentViewSet, EmailRegistrationView,
    GenreViewSet, ReviewViewSet, TitleViewSet, UserViewSet,
)

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('genres', GenreViewSet, basename='genres')
router.register('titles', TitleViewSet, basename='titles')
router.register('categories', CategoryViewSet, basename='categories')
router.register(r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet,
                basename='reviews')
router.register(r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)'
                r'/comments', CommentViewSet, basename='comments')
router.register('titles', TitleViewSet, basename='titles')
router.register('categories', CategoryViewSet, basename='categories')

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/email/', EmailRegistrationView.as_view()),
    path('v1/auth/token/', AccessTokenView.as_view()),
]
