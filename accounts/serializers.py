from rest_framework import serializers

from accounts.models import CustomUser


class CustomUserSerializer(serializers.HyperlinkedModelSerializer):
    snippets = serializers.HyperlinkedRelatedField(
        many=True, view_name="snippet-detail", read_only=True
    )

    class Meta:
        model = CustomUser
        fields = (
            "url",
            "id",
            "username",
            "email",
            "password",
            "soft_deleted",
            "snippets",
        )
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user
