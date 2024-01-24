from rest_framework import serializers
from django.contrib.auth.models import User
from .models import TextSnippets, Tag
from django.utils import timezone
import pdb

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password']
        
class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, error_messages={'required': 'Email is required'})
    password = serializers.CharField(required=True, error_messages={'required': 'Password is required'})
    
    class Meta:
        model = User
        fields = ['email', 'password']
    
    
class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True, error_messages={'required': 'Email is required'})
    
    class Meta:
        model = User
        fields = ['email', 'password']
        extra_kwargs = {'password': {'write_only': True}}
        
    def validate(self, data):
        email = data['email']

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('This email is already registered.')

        if User.objects.filter(username=email).exists():
            raise serializers.ValidationError('This email is already registered.')

        return data

    def create(self, validated_data):
        user = User.objects.create_user(username=validated_data['email'], **validated_data)
        return user
        
        
class CreateSnippetsSerializer(serializers.Serializer):
    tag = serializers.CharField(error_messages = {'required':'title is required' })
    snippets = serializers.CharField(error_messages = {'required':'content is required' })
    
    def validate(self, attrs):
        return super().validate(attrs)
    
    def create(self, validated_data):
        try:
            tag_title = validated_data['tag']
            snippet = validated_data['snippets']
            
            #CHECK SNIPPET EXISTS
            snippets = TextSnippets.objects.filter(content=snippet, tag__title=tag_title)
            if snippets:
                raise serializers.ValidationError({'result': 'failure', 'message': 'Snippets Already Exists'})
            
            #CHECK TAG EXISTS
            tag_exists = Tag.objects.filter(title=tag_title)
            if tag_exists:
                tag = tag_exists.first()
            else:
                tag = Tag.objects.create(title=tag_title, created_at=timezone.now(),updated_at=timezone.now())
            request = self.context.get('request')
            text_snippet = TextSnippets.objects.create(tag=tag, content=snippet,user=request.user, created_at=timezone.now(),updated_at=timezone.now())
            return text_snippet
        except Exception as error:
            print("ERRORS", error)
            raise serializers.ValidationError({'result': 'failure', 'message': 'Something went wrong'})
        
        
class SnippetsSerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField()
    tag_title = serializers.SerializerMethodField()
    
    
    class Meta:
        model = TextSnippets
        fields = ['user_email', 'tag_title', 'content', 'created_at']
        
    def get_user_email(self, obj):
        return obj.user.email
        
    def get_tag_title(self, obj):
        return obj.tag.title
    
    
    def update(self, instance, validated_data):
        content = validated_data.get('content')

        if content is None:
            raise serializers.ValidationError({'result': 'failure', 'message': 'Content is required to update the snippet'})

        instance.content = content
        instance.save()

        return instance
    

class TagsSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Tag
        fields = ['title', 'created_at']
        

class TagDetailSerializer(serializers.ModelSerializer):
    tag_title = serializers.SerializerMethodField()
    snippet_list = serializers.SerializerMethodField()
    
    class Meta:
        model = Tag
        fields = ['tag_title', 'snippet_list']
        
    def get_tag_title(self, obj):
        return obj.title
    
    def get_snippet_list(self, obj):
        output_list = []
        tag_snippets = obj.tag_snippets.all()
        for snippet in tag_snippets:
            result = {}
            result['id'] = snippet.id
            result['content'] = snippet.content
            result['created_at'] = snippet.created_at
            output_list.append(result)
        return output_list
    
    

class OverviewSerializer(serializers.ModelSerializer):
    no_of_snippets = serializers.SerializerMethodField()
    available_snippets = serializers.SerializerMethodField()
    
    
    class Meta:
        model = TextSnippets
        fields = ['no_of_snippets', 'available_snippets']
        
    def get_no_of_snippets(self, obj):
        return Tag.objects.all().count()
    
    def get_available_snippets(self, obj):
        output_list = []
        tag_snippets = Tag.objects.all()
        for snippet in tag_snippets:
            result = {}
            result['id'] = snippet.id
            result['title'] = snippet.title
            result['detail_link'] =  f'tag/{snippet.id}/detail/'
            result['created_at'] = snippet.created_at
            
            output_list.append(result)
        return output_list