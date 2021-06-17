from rest_framework import serializers

from .models import Category, Comment, Genre, Review, Title, User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['first_name', 'last_name', 'username',
                  'bio', 'email', 'role']
        model = User
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True}
        }


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['email']
        model = User
        extra_kwargs = {
            'email': {'required': True}
        }


class ConfirmationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    confirmation_code = serializers.CharField(required=True)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ['id']
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        exclude = ['id']
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Title
        fields = '__all__'


class TitleCreateSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )

    class Meta:
        model = Title
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        title = self.context['view'].kwargs['title_id']
        author = self.context['request'].user
        if author.reviews.filter(title=title).exists():
            raise serializers.ValidationError(
                'You can`t add more than one review to a single work!.'
            )
        return data

    class Meta:
        exclude = ['title']
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        exclude = ['review']
        model = Comment
