from django.contrib.auth.models import User
from rest_framework import viewsets, generics, permissions
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Task, UploadedImage, AnnotationPolygon
from .serializers import (
    TaskSerializer, 
    UploadedImageSerializer, 
    AnnotationPolygonSerializer,
    RegisterSerializer, 
    EmailTokenObtainPairSerializer,
)

# --- ViewSets ---

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # প্রতিটি ইউজার শুধু নিজের টাস্ক দেখবে
        queryset = Task.objects.filter(owner=self.request.user).order_by('-created_at')
        date_param = self.request.query_params.get('date', None)
        if date_param is not None:
            queryset = queryset.filter(due_date=date_param)
        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class UploadedImageViewSet(viewsets.ModelViewSet):
    serializer_class = UploadedImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # প্রতিটি ইউজার শুধু নিজের আপলোড করা ছবি দেখবে
        return UploadedImage.objects.filter(owner=self.request.user).order_by('uploaded_at')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class AnnotationPolygonViewSet(viewsets.ModelViewSet):
    serializer_class = AnnotationPolygonSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # পলিগন সরাসরি owner রাখে না — যে ছবিতে আছে তার owner দিয়ে ফিল্টার
        # (list/retrieve/update/destroy সবকটাই এই queryset-এর মধ্য দিয়ে যায়,
        # তাই অন্য কারো polygon-এ update/delete করতে গেলে 404 পাবে)
        return AnnotationPolygon.objects.filter(image__owner=self.request.user)

# --- Auth Views ---

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer