from rest_framework import serializers
from ..models import Item


class ListItemIdSerializer(serializers.ListField):
    def to_internal_value(self, data):
        data = super().to_internal_value(data)

        items = Item.objects.filter(id__in=set(data))
        if len(items) != len(set(data)):
            raise serializers.ValidationError("One or more objects do not exist.")

        return data


class CheckListSerializer(serializers.Serializer):
    items = ListItemIdSerializer(child=serializers.IntegerField(), allow_empty=False)
