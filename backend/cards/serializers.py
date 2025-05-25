from rest_framework import serializers
from .models import Card, Column

class ColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Column
        fields = ['id', 'title', 'order', 'card']
        read_only_fields = ['card']
        extra_kwargs = {
            'order': {'required': False}
        }


class CardSerializer(serializers.ModelSerializer):
    columns = serializers.SerializerMethodField()

    class Meta:
        model = Card
        fields = ['id', 'title', 'created_at', 'columns']
        read_only_fields = ['created_at']

    def get_columns(self, obj):
        columns = obj.columns.order_by('order')
        return ColumnSerializer(columns, many=True).data

    def create(self, validated_data):
        card = super().create(validated_data)

        # Создаём стандартные колонки
        Column.objects.create(card=card, title='Выполняется', order=1)
        Column.objects.create(card=card, title='В проверке', order=2)
        Column.objects.create(card=card, title='Готово', order=3, is_system=True)

        return card

