from django.urls import path
from knox import views as knox_views
from .views import *
urlpatterns = [
  path('login/', LoginAPI.as_view(), name='login'),

  path('logout/', knox_views.LogoutView.as_view(), name='logout'),

  path('upload_sales_file/', UploadSalesFileAPI.as_view(), name='upload-file'),

  path('statisticSales/', StatisticsSalesViewAPI.as_view(), name='salesstatistics'),

  path('users/<int:pk>/', UsersViewAPI.as_view(), name='usersDetails'),

]