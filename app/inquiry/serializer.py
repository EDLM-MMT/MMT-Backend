import logging

from inquiry.models import Inquiry, InquiryComment, InquiryFAQ
from rest_framework import serializers
from rest_framework_guardian.serializers import \
    ObjectPermissionsAssignmentMixin
from users.models import MMTUser

logger = logging.getLogger(__name__)


class InquiryFAQSerializer(serializers.ModelSerializer):

    class Meta:
        model = InquiryFAQ
        fields = '__all__'


class InquiryCommentSerializer(ObjectPermissionsAssignmentMixin,
                               serializers.ModelSerializer):
    poster = serializers.SlugRelatedField(
        slug_field='email', queryset=MMTUser.objects.all(),
        default=serializers.CurrentUserDefault())
    inquiry = serializers.PrimaryKeyRelatedField(
        queryset=Inquiry.objects.all())

    class Meta:
        model = InquiryComment
        fields = ['comment', 'inquiry', 'created', 'poster']

    def get_permissions_map(self, created):
        perms = {}
        if not created:
            inquiry_owner = self.instance.poster
            inquiry_details = Inquiry.objects.get(id=self.context['request'].
                                                  data['inquiry'])
            perms = {
                'view_inquirycomment': [inquiry_owner,
                                        inquiry_details.default_assigned,
                                        inquiry_details.assigned]
            }

        return perms

    def create(self, validated_data):
        validated_data['poster'] = self.context['request'].user
        return super().create(validated_data)


class InquirySerializer(ObjectPermissionsAssignmentMixin,
                        serializers.ModelSerializer):
    comments = InquiryCommentSerializer(read_only=True, many=True)

    class Meta:
        model = Inquiry
        fields = ['id', 'email', 'name', 'subject', 'assigned', 'owner',
                  'description', 'inquiry_type', 'file', 'default_assigned',
                  'created', 'modified', 'status', 'comments']

    def get_permissions_map(self, created):
        perms = {}
        # if not created:
        if self.instance.owner:
            inquiry_owner = self.instance.owner
        else:
            inquiry_owner = self.instance.email
        assigned_group = self.instance.default_assigned
        assigned = self.instance.assigned
        logger.error(assigned)
        perms = {
            'view_inquiry': [inquiry_owner, assigned,
                             assigned_group],
            'change_inquiry': [inquiry_owner, assigned],
            'delete_inquiry': [inquiry_owner, assigned]
        }
        return perms

    def create(self, validated_data):
        if 'inquiry_type' in validated_data and validated_data['inquiry_type']:
            inquiry_type = InquiryFAQ.objects.get(
                issue=validated_data['inquiry_type'])
            validated_data['default_assigned'] = \
                inquiry_type.default_assigned
        validated_data['owner'] = self.context['request'].user

        inquiry = Inquiry.objects.create(**validated_data)

        if 'comments' in self.context['request'].data and \
                self.context['request'].data['comments']:
            comments = self.context['request'].data['comments']
            for comment in comments:
                InquiryComment.objects.create(**comment, inquiry=inquiry,
                                              poster=self.context['request'].
                                              user)
        return inquiry

    def update(self, instance, validated_data):
        do_not_update = {'email', 'name', 'subject', 'owner',
                         'description', 'comments'}
        if 'inquiry_type' in validated_data and validated_data['inquiry_type']:
            inquiry_type = InquiryFAQ.objects.get(
                issue=validated_data['inquiry_type'])
            validated_data['default_assigned'] = \
                inquiry_type.default_assigned

        for field, value in validated_data.items():
            if field not in do_not_update:
                setattr(instance, field, value)

        instance.save()
        return instance
