from django.urls import path
from .views import (
    ItemListView,
    SignupView,
    AddItemView,
    UpdateItemView,
    DeleteItemView,
    SearchHistoryView,
    GeneratePDF
)
from django.contrib.auth import views as auth_view

urlpatterns = [
    path('', ItemListView.as_view(), name='items'),
    path('search/', SearchHistoryView.as_view(), name='search'),
    path('search/pdf_download/', GeneratePDF.as_view(), name='pdf'),
    path('items/update/<int:pk>/', UpdateItemView.as_view(), name='update'),
    path('items/delete/<int:pk>/', DeleteItemView.as_view(), name='delete'),
    path('register/', SignupView.as_view(), name='register'),
    path('login/', auth_view.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_view.LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('add_item/', AddItemView.as_view(), name='add_item'),
    

]
