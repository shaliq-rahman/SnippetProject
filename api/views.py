from django.shortcuts import render
from rest_framework.views import APIView
from .serializer import LoginSerializer, RegisterSerializer, CreateSnippetsSerializer, SnippetsSerializer, TagsSerializer, TagDetailSerializer, OverviewSerializer
from rest_framework.response import Response
from rest_framework import status
import pdb
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets,status,permissions
from django.db import transaction
from .models import TextSnippets, Tag
from rest_framework.exceptions import PermissionDenied
from rest_framework import serializers

# Create your views here.
def Welcome():
    print('hello')
    
class Login(APIView):
    def post(self, request):
        try:
            data = request.data
            serializer = LoginSerializer(data=data)
            if serializer.is_valid():
                email = serializer.validated_data['email']
                password = serializer.validated_data['password']
                user = authenticate(username=email, password=password)
                
                if user is None:
                    message = {'detail': 'Invalid user or password'}
                    return Response(message, status=status.HTTP_400_BAD_REQUEST)
                
                refresh = RefreshToken.for_user(user)
                return Response({'refresh': str(refresh), 'access': str(refresh.access_token)})
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            print(error)
            message = {'detail': 'Something went wrong'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        

class Register(APIView):
    def post(self, request):
        try:
            serializer = RegisterSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                message = {'detail': 'User registered successfully'}
                return Response(message, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            print(error)
            message = {'detail': 'Something went wrong'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        
        
class Snippets(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated] 
    
    def get_serializer_class(self):
        group_serializer = {'create': CreateSnippetsSerializer}
        return group_serializer.get(self.action, CreateSnippetsSerializer)

    @transaction.atomic()
    def create(self,request,*args,**kwargs):
        response, status_code = {}, status.HTTP_200_OK
        ser = self.get_serializer(data=request.data)
        try:
            if ser.is_valid():
                text_snippet = ser.save()
                response['result'], response['message'] = 'success', 'Saved successfully.'
            else:
                response['result'], response['errors'], status_code, response['data'] = 'failure', {i: ser.errors[i][0] for i in ser.errors.keys()}, status.HTTP_400_BAD_REQUEST, ser.data
        except serializers.ValidationError as validation_error:
            response['result'], response['message'], status_code = 'failure', validation_error.detail['message'], status.HTTP_400_BAD_REQUEST

        return Response(response, status=status_code)
    
    
    # Detail API.
    def get_snippets(self, request, *args, **kwargs):
        text_snippets = TextSnippets.objects.select_related('tag').all()
        print(text_snippets)
        if text_snippets:
            snippets__list_serializer = SnippetsSerializer(text_snippets, many=True, context={'request': request}) 
            return Response({'result':'success','snippets':snippets__list_serializer.data, 'status_code': status.HTTP_200_OK})
        else:
            return Response({'result':'failure','message':'Snippets Not Found', 'status_code': status.HTTP_400_BAD_REQUEST},status.HTTP_400_BAD_REQUEST)
        

class UpdateSnippet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated] 
    
    def get_serializer_class(self):
        return SnippetsSerializer
    
    
    def update_snippet(self, request, id, *args, **kwargs):
        try:
            snippet = TextSnippets.objects.get(id=id)
            if request.user == snippet.user:
                ser = self.get_serializer(snippet, data=request.data, partial=True)
                if ser.is_valid():
                    ser.update(snippet, ser.validated_data) 
                    return Response({'result': 'success', 'message': 'Snippet updated successfully', 'data': ser.data,  'status_code': status.HTTP_200_OK})
                else:
                    return Response({'result': 'failure', 'errors': ser.errors, 'status_code': status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)
            else:
                raise PermissionDenied('You do not have permission to update this snippet.')
        except TextSnippets.DoesNotExist:
            return Response({'result': 'failure', 'message': 'Snippets not found', 'status_code': status.HTTP_404_NOT_FOUND}, status.HTTP_404_NOT_FOUND)
        
        

class SnippetDelete(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated] 

    def get_serializer_class(self):
        return SnippetsSerializer
    
    def delete_snippet(self, request, id, *args, **kwargs):
        try:
            snippet = TextSnippets.objects.get(id=id)
            if request.user == snippet.user:
                snippet.delete()
                return Response({'result': 'success', 'message': 'Snippet deleted successfully', 'status_code': status.HTTP_204_NO_CONTENT})
            else:
                raise PermissionDenied('You do not have permission to delete this Snippet.')
        except TextSnippets.DoesNotExist:
            return Response({'result': 'failure', 'message': 'Snippet not found', 'status_code': status.HTTP_404_NOT_FOUND}, status.HTTP_404_NOT_FOUND)
        
        
        

class TagsListAPI(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated] 
    
    def get_serializer_class(self):
        return TagsSerializer

    def list_tags(self, request, *args, **kwargs):
        tags = Tag.objects.all()
        print(tags)
        if tags:
            tags_list_serializer = TagsSerializer(tags, many=True, context={'request': request}) 
            return Response({'result':'success','tags':tags_list_serializer.data, 'status_code': status.HTTP_200_OK})
        else:
            return Response({'result':'failure','message':'Tags Not Found', 'status_code': status.HTTP_400_BAD_REQUEST},status.HTTP_400_BAD_REQUEST)
        
        

class TagsDetailAPI(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated] 
    
    def get_serializer_class(self):
        return TagDetailSerializer

    def list_tag_detail(self, request, id, *args, **kwargs):
        try:
            tag_detail = Tag.objects.prefetch_related('tag_snippets').get(id=id)
            if tag_detail:
                tags_detail_list_serializer = TagDetailSerializer(tag_detail, many=False, context={'request': request}) 
                return Response({'result':'success','tags':tags_detail_list_serializer.data, 'status_code': status.HTTP_200_OK})
            else:
                return Response({'result':'failure','message':'Tags Not Found', 'status_code': status.HTTP_400_BAD_REQUEST},status.HTTP_400_BAD_REQUEST)
        except TextSnippets.DoesNotExist:
            return Response({'result': 'failure', 'message': 'Tags not found', 'status_code': status.HTTP_404_NOT_FOUND}, status.HTTP_404_NOT_FOUND)
        

class SnippetsOverviewAPI(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated] 
    
    def get_serializer_class(self):
        return OverviewSerializer

    def overview(self, request, *args, **kwargs):
        try:
            tags = Tag.objects.prefetch_related('tag_snippets').all()
            if tags:
                # Use the first tag for the overview
                overview_serializer = OverviewSerializer(tags[0], context={'request': request})
                return Response({'result': 'success', 'data': [overview_serializer.data], 'status_code': status.HTTP_200_OK})
            else:
                return Response({'result': 'failure', 'message': 'No data Found', 'status_code': status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)
        except TextSnippets.DoesNotExist:
            return Response({'result': 'failure', 'message': 'No data found', 'status_code': status.HTTP_404_NOT_FOUND}, status.HTTP_404_NOT_FOUND)

        
    
            
                