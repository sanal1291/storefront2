
from rest_framework import serializers

from store.models import Collection, Product
from decimal import Decimal


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count', 'featured_product']
    # id = serializers.IntegerField()
    # title = serializers.CharField(max_length=255)
    products_count = serializers.SerializerMethodField(
        method_name='product_count')

    def product_count(self, collection: Collection):
        return collection.products.count()


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'slug', 'unit_price',
                  'inventory', 'price_with_tax', 'collection']
        # ='__all__' -bad practice

    price_with_tax = serializers.SerializerMethodField(method_name='tax_price')
    # 1. serializers.Serializer
    # id = serializers.IntegerField()
    # title = serializers.CharField(max_length=255)
    # price = serializers.DecimalField(
    #     max_digits=6, decimal_places=2, source='unit_price')
    # # 1. pk
    # # collection = serializers.PrimaryKeyRelatedField(
    # #     queryset=Collection.objects.all()
    # # )
    # # 2. string value
    # # collection = serializers.StringRelatedField()
    # # 3. nested object
    # # collection = CollectionSerializer()
    # # 4. hyperlink
    # collection = serializers.HyperlinkedRelatedField(
    #     queryset=Collection.objects.all(), view_name='collection-detail')

    def tax_price(self, product: Product):
        return product.unit_price * Decimal(1.1)

    def validate(self, attrs):
        return super().validate(attrs)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    def create(self, validated_data):
        return super().create(validated_data)
        # product = Product(**validated_data)
        # product.other = 1123123
        # product.save
        # return product
