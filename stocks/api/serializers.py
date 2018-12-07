from rest_framework import serializers

from ..models import Company, Insider, StockDay, Trade


class CompanySerializer(serializers.ModelSerializer):
    """Serializer for `Company` model.
    """
    class Meta:
        model = Company
        fields = ('id', 'ticker', )


class StockDaySerializer(serializers.ModelSerializer):
    """Serializer for `StockDay` model.
    """
    class Meta:
        model = StockDay
        fields = '__all__'
        ordering = ('-created_date', )


class InsiderSerializer(serializers.ModelSerializer):
    """Serializer for `Insider` model.
    """
    class Meta:
        model = Insider
        fields = '__all__'


class TradeSerializer(serializers.ModelSerializer):
    """Serializer for `Trade` model.
    """
    insider = InsiderSerializer(many=False, read_only=True)

    class Meta:
        model = Trade
        fields = '__all__'
        ordering = ('-last_date', )


class StockPriceAnalyticsSerializer(serializers.Serializer):
    date_from = serializers.DateField()
    date_to = serializers.DateField()


class StockPeriodsAnalyticsSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=('open', 'high', 'low', 'close')) 
    value = serializers.DecimalField(max_digits=10, decimal_places=4)
