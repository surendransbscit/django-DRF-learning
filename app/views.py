from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.db.models import Sum, Q, Count, Avg
from django.shortcuts import get_object_or_404
from knox.models import AuthToken
from django.db import connection
from .models import Category, Tag, Profile, Product, ProductImage
from .serializers import (
    UserSerializer, CategorySerializer, TagSerializer, ProfileSerializer,
    ProductSerializer, ProductImageSerializer
)
from utils.pagination import paginate_queryset
from django.db import transaction
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank




# Login

class LoginAPIView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = User.objects.filter(username=username).first()
        if not user:
            return Response({"error": "Invalid username"}, status=status.HTTP_400_BAD_REQUEST)
        if not user.check_password(password):
            return Response({"error": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST)

        token = AuthToken.objects.create(user)[1]
        return Response({"user": UserSerializer(user).data, "token": token})



# Custom Permission

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_staff



# Category Views

class CategoryListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get(self, request ,format=None):
        queryset = self.get_queryset()
        return paginate_queryset(queryset, request, self.serializer_class)

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get(self, request, pk, format=None):
        category = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.serializer_class(category)
        return Response(serializer.data)

    def put(self, request, pk, *args, **kwargs):
        category = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.serializer_class(category, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk, *args, **kwargs):
        category = get_object_or_404(self.get_queryset(), pk=pk)
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



# Tag Views

class TagListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def get(self, request, format=None):
        queryset = self.get_queryset()
        return paginate_queryset(queryset, request, self.serializer_class)

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TagDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def get(self, request, pk, format=None):
        tag = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.serializer_class(tag)
        return Response(serializer.data)

    def put(self, request, pk, *args, **kwargs):
        tag = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.serializer_class(tag, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk, *args, **kwargs):
        tag = get_object_or_404(self.get_queryset(), pk=pk)
        tag.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



# Product Views

class ProductListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get(self, request, format=None):
        products = self.queryset

        # Filtering
        price_min = request.GET.get("price_min")
        price_max = request.GET.get("price_max")
        released_on = request.GET.get("released_on")
        in_stock = request.GET.get("in_stock")

        if price_min:
            products = products.filter(price__gte=price_min)
        if price_max:
            products = products.filter(price__lte=price_max)
        if released_on:
            products = products.filter(released_on=released_on)
        if in_stock:
            if in_stock.lower() in ["true", "1"]:
                products = products.filter(in_stock=True)
            elif in_stock.lower() in ["false", "0"]:
                products = products.filter(in_stock=False)

        # Search
        search = request.GET.get("search")
        if search:
            products = products.filter(
                Q(name__icontains=search) | Q(category__name__icontains=search)
            )

        return paginate_queryset(products, request, self.serializer_class)

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get(self, request, pk, format=None):
        product = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.serializer_class(product)
        return Response(serializer.data)

    def put(self, request, pk, *args, **kwargs):
        product = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.serializer_class(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk, *args, **kwargs):
        product = get_object_or_404(self.get_queryset(), pk=pk)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Product Image Views

class ProductImageListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminOrReadOnly]
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer

    def get(self, request, format=None):
        queryset = self.get_queryset()
        return paginate_queryset(queryset, request, self.serializer_class)

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProductImageDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminOrReadOnly]
    queryset = ProductImage.objects.all()
    serializer_class = ProductImageSerializer

    def get(self, request, pk, format=None):
        img = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.serializer_class(img)
        return Response(serializer.data)

    def put(self, request, pk, *args, **kwargs):
        img = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.serializer_class(img, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk, *args, **kwargs):
        img = get_object_or_404(self.get_queryset(), pk=pk)
        img.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Profile Views

class ProfileListView(generics.ListAPIView):
    permission_classes = [permissions.IsAdminUser]
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def get(self, request, format=None):
        queryset = self.get_queryset()
        return paginate_queryset(queryset, request, self.serializer_class)


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer

    def get(self, request, format=None):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        serializer = self.serializer_class(profile)
        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        serializer = self.serializer_class(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)



# Admin Dashboard

class AdminDashboardView(generics.GenericAPIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        total_products = Product.objects.count()
        total_price = Product.objects.aggregate(Sum("price"))["price__sum"] or 0
        total_categories = Category.objects.count()
        total_stock = Product.objects.filter(in_stock=True).count()

        return Response({
            "total_products": total_products,
            "total_price": total_price,
            "total_categories": total_categories,
            "total_stock": total_stock
        })
    
# Product Aggregation Stats
class ProductStatsView(APIView):
    def get(self, request):
        stats = Product.objects.aggregate(
            total_products=Count('id'),
            avg_price=Avg('price'),
            total_price=Sum('price')
        )
        return Response(stats)
    
#Bulk Product Creation

class BulkProductCreateView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request, *args, **kwargs):
        products_data = request.data.get("products", [])
        try:
            with transaction.atomic():
                created_products = []
                for product_data in products_data:
                    serializer = ProductSerializer(data=product_data)
                    serializer.is_valid(raise_exception=True)
                    product = serializer.save()
                    created_products.append(serializer.data)
            return Response(
                {"created_products": created_products},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class ProductSearchView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        query = request.GET.get("q")
        if not query:
            return Response({"error": "Please provide a search query ?q="}, status=status.HTTP_400_BAD_REQUEST)

        # Full-Text Search across multiple fields
        search_vector = SearchVector("name", "description", "category__name")
        search_query = SearchQuery(query)

        products = Product.objects.annotate(
            rank=SearchRank(search_vector, search_query)
        ).filter(rank__gte=0.1).order_by("-rank")
        return paginate_queryset(products, request, ProductSerializer)


class TopProductsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        try:
            top = int(request.GET.get("top", 2))
        except ValueError:
            return Response({"error": "Invalid top value"}, status=400)

        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT id, name, price
                FROM product
                ORDER BY price DESC
                LIMIT %s
            """, [top])
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return Response({"top_products": results})




