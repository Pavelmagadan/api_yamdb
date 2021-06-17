import uuid

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import year_validator


class User(AbstractUser):
    class UserRole(models.TextChoices):
        ADMIN = 'admin', 'Administrator'
        MODERATOR = 'moderator', 'Moderator'
        USER = 'user', 'User'

    email = models.EmailField(
        'Адрес электронной почты',
        unique=True,
        blank=True
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=50,
        blank=True,
        null=True,
        unique=True
    )
    role = models.CharField(
        'Роль',
        max_length=50,
        choices=UserRole.choices,
        default=UserRole.USER
    )
    bio = models.CharField(
        'О себе',
        max_length=20,
        null=True,
        blank=True
    )
    confirmation_code = models.CharField(
        'Код подтверждения',
        max_length=100,
        null=True,
        default=uuid.uuid4
    )

    @property
    def is_moderator(self):
        return self.role == self.UserRole.MODERATOR

    @property
    def is_admin(self):
        return self.role == self.UserRole.ADMIN

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Category(models.Model):
    name = models.CharField('Название', max_length=200)
    slug = models.SlugField('ID', unique=True)

    class Meta:
        ordering = ['id']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(models.Model):
    name = models.CharField('Название', max_length=200)
    slug = models.SlugField('ID', unique=True)

    class Meta:
        ordering = ['id']
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField('Название', max_length=200, db_index=True)
    year = models.PositiveSmallIntegerField(
        'Год',
        null=True,
        validators=[year_validator]
    )
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
        db_index=True
    )
    description = models.TextField('Описание',
                                   max_length=400, null=True)
    genre = models.ManyToManyField(Genre, verbose_name='Жанр',
                                   blank=True,
                                   related_name='titles',
                                   db_index=True)

    class Meta:
        ordering = ['-id']
        verbose_name = 'Название'
        verbose_name_plural = 'Названия'

    def __str__(self):
        return self.name


class Review(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews',
        verbose_name='Автор'
    )
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews',
        verbose_name='Название'
    )
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True
    )
    score = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, 'score must be greater than 1'),
            MaxValueValidator(10, 'score must be less than 10')
        ],
        verbose_name='Рейтинг'
    )

    class Meta:
        ordering = ['pub_date']
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            ),
        ]


class Comment(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments',
        verbose_name='Автор'
    )
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments',
        verbose_name='Отзыв'
    )
    text = models.TextField('Текст')
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['pub_date']
