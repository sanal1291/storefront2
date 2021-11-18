from django.db.models import Count
from django.shortcuts import get_object_or_404
\
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
# Readonlymodelviewset - for read operations

from django_filters.rest_framework import DjangoFilterBackend

from store.filters import ProductFilterSet
from store.models import Cart, Collection, OrderItem, Product, Review
from store.pagination import DefaultPagination
from store.serializers import CartSerializer, CollectionSerializer, ProductSerializer, ReviewSerializer

# class viewset


class CartViewSet(CreateModelMixin,
                  RetrieveModelMixin,
                  DestroyModelMixin,
                  GenericViewSet):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilterSet
    pagination_class = DefaultPagination  # can be defined for all in settings
    search_fields = ['title', 'description']
    ordering_fields = ['unit_price', 'last_update']
    # filterset_fields = ['collection_id', 'unit_price']
    # not needed for custom filter

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({'error':
                             "product cannot be deleted cuz blah blah"})
        return super().destroy(request, *args, *kwargs)

    # doesnt need if we use django-filter , easy to implement
    # def get_queryset(self):
    #     queryset = Product.objects.all()
    #     collection_id = self.request.query_params.get('collection_id')
    #     # get return none from dict if not exist rather than error
    #     if collection_id is not None:
    #         queryset = queryset.filter(collection_id=collection_id)
    #     return queryset
# class based generic


class ProductList(ListCreateAPIView):
    queryset = Product.objects.select_related(
        'collection').all()
    serializer_class = ProductSerializer

    # def get_queryset(self):
    #     return Product.objects.select_related(
    #         'collection').all()

    # def get_serializer_class(self, *args, **kwargs):
    #     return ProductSerializer

    # def get_serializer_context(self):
    #     return {'request': self.request}


class ProductDetail(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    # lookup_field = 'id'  # defualt pk

    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        if product.orderitems.count() > 0:
            return Response({'error':
                             "product cannot be deleted cuz blah blah"})
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# class viewset


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(
        products_count=Count('products')).all()
    serializer_class = CollectionSerializer

    def destroy(self, request, pk):
        collection = self.get_object()
        if collection.products.count() > 0:
            return Response({'error': '''Collection cannot be delated because 
                            it is assosiated with other item'''},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CollectionList(ListCreateAPIView):
    queryset = Collection.objects.annotate(
        products_count=Count('products')).all()
    serializer_class = CollectionSerializer


class CollectionDetail(RetrieveUpdateDestroyAPIView):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer

    def delete(self, request, pk):
        collection = self.get_object()
        if collection.products.count() > 0:
            return Response({'error': '''Collection cannot be delated because 
                            it is assosiated with other item'''},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}

    # use django-filter cuz this may get complicated
    # def get_queryset(self):
    #     return Review.objects.filter(product_id=self.kwargs['product_pk'])


@api_view(['GET', 'POST'])
def product_list(request):
    if request.method == 'GET':
        ''' get list of products'''
        queryset = Product.objects.select_related(
            'collection').all()  # or getlistor404(product)
        serializer = ProductSerializer(
            queryset, many=True, context={'request': request})
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data
        serializer.save()
        return Response(serializer.data)
        # if serializer.is_valid():
        #     serializer.validated_data
        #     return Response('ok')
        # else:
        #     return Response(serializer.errors,
        #                   status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PATCH', 'PUT', 'DELETE'])
def prdocut_detail(request, id):
    product = get_object_or_404(Product, pk=id)

    if request.method == 'GET':
        # first method
        # try:
        #     product = Product.objects.get(pk=id)
        #     serializer = ProductSerializer(product)
        #     return Response(serializer.data)
        # except Product.DoesNotExist:
        #     return Response(status=status.HTTP_404_NOT_FOUND)

        ''' get details of single product'''
        serializer = ProductSerializer(product,
                                       context={'request': request})
        #    context for hyperlinkrelatedfield
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ProductSerializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    elif request.method == "DELETE":
        if product.orderitems.count() > 0:
            return Response({'error': """product cannot be deleted because 
                            it is assosiated with other item"""},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def collection_list(request):
    if request.method == 'GET':
        queryset = Collection.objects.prefetch_related('products').all()
        serializer = CollectionSerializer(queryset, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = CollectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def collection_detail(request, pk):
    collection = get_object_or_404(Collection, pk=pk)
    if request.method == 'GET':
        serializer = CollectionSerializer(collection)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = CollectionSerializer(collection, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    elif request.method == 'DELETE':
        if collection.products.count() > 0:
            return Response({'error': '''Collection cannot be delated because 
                            it is assosiated with other item'''},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# class based


class ProductList1(APIView):
    '''
    product listing and creation
    '''

    def get(self, request):
        queryset = Product.objects.select_related(
            'collection').all()  # or getlistor404(product)
        serializer = ProductSerializer(
            queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data
        serializer.save()
        return Response(serializer.data)


class CollectionList1(APIView):
    '''
    collection listing and creation
    '''

    def get(self, request):
        queryset = Collection.objects.prefetch_related('products').all()
        serializer = CollectionSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CollectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ProductDetail1(APIView):
    '''
    product get, put and delete
    '''

    def get(self, request, id):
        product = get_object_or_404(Product, pk=id)
        serializer = ProductSerializer(product,
                                       context={'request': request})
        #    context for hyperlinkrelatedfield
        return Response(serializer.data)

    def put(self, request, id):
        product = get_object_or_404(Product, pk=id)
        serializer = ProductSerializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, id):
        product = get_object_or_404(Product, pk=id)
        if product.orderitems.count() > 0:
            return Response({'error': """product cannot be deleted because 
                            it is assosiated with other item"""},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CollectionDetail1(APIView):
    '''
    collection get, put and delete
    '''

    def get(self, request, pk):
        collection = get_object_or_404(Collection, pk=pk)
        serializer = CollectionSerializer(collection)
        return Response(serializer.data)

    def put(self, request, pk):
        collection = get_object_or_404(Collection, pk=pk)
        serializer = CollectionSerializer(collection, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        collection = get_object_or_404(Collection, pk=pk)
        if collection.products.count() > 0:
            return Response({'error': '''Collection cannot be delated because 
                            it is assosiated with other item'''},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
