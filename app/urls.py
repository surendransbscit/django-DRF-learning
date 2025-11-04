from django.urls import path
from .views import (
    LoginAPIView,
    CategoryListCreateView, CategoryDetailView,
    TagListCreateView, TagDetailView,
    ProductListCreateView, ProductDetailView,
    ProductImageListCreateView, ProductImageDetailView,
    ProfileListView, ProfileDetailView,
    AdminDashboardView,
    BulkProductCreateView,ProductStatsView,ProductSearchView,TopProductsView
)

urlpatterns = [
    # Auth
    path("login/", LoginAPIView.as_view()),

    # Categories
    path("categories/", CategoryListCreateView.as_view()),
    path("categories/<int:pk>/", CategoryDetailView.as_view()),

    # Tags
    path("tags/", TagListCreateView.as_view()),
    path("tags/<int:pk>/", TagDetailView.as_view()),

    # Products
    path("products/", ProductListCreateView.as_view()),
    path("products/<int:pk>/", ProductDetailView.as_view()),

    # Product Images
    path("productimages/", ProductImageListCreateView.as_view()),
    path("productimages/<int:pk>/", ProductImageDetailView.as_view()),

    # Profiles
    path("profiles/", ProfileListView.as_view()),
    path("profile/", ProfileDetailView.as_view()),

    # Admin Dashboard
    path("dashboard/", AdminDashboardView.as_view()),

    # Bulk Product Creation
    path("bulkproducts/", BulkProductCreateView.as_view()),

    # Product Aggregation Stats
    path("productstats/", ProductStatsView.as_view()),

    # Search Products
    path("search/", ProductSearchView.as_view()),

    # Top Products
    path("topproducts/", TopProductsView.as_view()),

]
