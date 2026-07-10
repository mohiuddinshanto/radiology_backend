from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Task, UploadedImage, AnnotationPolygon

# --- Task & Annotation Serializers ---

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['owner']

class AnnotationPolygonSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnotationPolygon
        fields = ['id', 'image', 'points', 'label', 'color', 'created_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request is not None and request.user and request.user.is_authenticated:
            self.fields['image'].queryset = UploadedImage.objects.filter(
                owner=request.user
            )
        else:
            self.fields['image'].queryset = UploadedImage.objects.none()

class UploadedImageSerializer(serializers.ModelSerializer):
    polygons = AnnotationPolygonSerializer(many=True, read_only=True)

    class Meta:
        model = UploadedImage
        fields = ['id', 'image', 'uploaded_at', 'polygons', 'owner']
        read_only_fields = ['owner']

# --- Auth Serializers ---

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def validate_username(self, value):
        # user যদি username field এ email দেয়, @ এর আগের অংশ নাও
        if '@' in value:
            value = value.split('@')[0]
        # unique check
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
        )
        return user

class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Login ফিল্ডে email দিলে তা username-এ ম্যাপ করে দেয়।"""
    def validate(self, attrs):
        email_or_username = attrs.get(self.username_field)
        try:
            user = User.objects.get(email=email_or_username)
            attrs[self.username_field] = user.username
        except User.DoesNotExist:
            pass
        return super().validate(attrs)