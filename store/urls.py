''' store app urls'''
from django.urls import path
from django.urls.conf import include
from . import views
# from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
# adv defaultrouter over simplerouter -
# 1.gives api root that can show urls
# 2.append endpoint with .json to get json data
# from pprint import pprint

router = routers.DefaultRouter()
router.register('products', views.ProductViewSet, basename='products')
router.register('collections', views.CollectionViewSet)
router.register('carts', views.CartViewSet)
router.register('customers', views.CustomerViewSet)
# pprint(router.urls)
product_router = routers.NestedDefaultRouter(
    router, 'products', lookup='product')

product_router.register('reviews', views.ReviewViewSet,
                        basename='product-review')

carts_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
carts_router.register('items', views.CartItemViewSet, basename='cart-items')

# urlpatterns = router.urls + product_router.urls
urlpatterns = [
    path('', include(router.urls)),
    path('', include(product_router.urls)),
    path('', include(carts_router.urls)),

    # path('products/', views.ProductList.as_view()),
    # path('products/<int:pk>/', views.ProductDetail.as_view()),
    # path('collections/', views.CollectionList.as_view()),
    # path('collections/<int:pk>/', views.CollectionDetail.as_view(),
    #      name="collection-detail"),
]
# pprint(router.urls)
# pprint(product_router.urls)
