from rest_framework import serializers

from users.models import MMTUser


class MMTUserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(read_only=True)
    last_name = serializers.CharField(read_only=True)
    rank = serializers.CharField(read_only=True, source='user_record.rank')

    class Meta:
        model = MMTUser
        fields = ['email', 'first_name', 'last_name', 'position', 'rank',]

        def validate_email(attrs):
            return attrs
        extra_kwargs = {
            'email': {'validators': [validate_email]},
            'position': {'default': ''}
        }

    def validate(self, attrs):
        attrs = super().validate(attrs)
        inst = MMTUser.objects.filter(email=attrs['email'])
        if inst.exists():
            self.instance = inst.get()
        return attrs

    def create(self, validated_data):
        return None
