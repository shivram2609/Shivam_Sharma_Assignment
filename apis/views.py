from django.contrib.auth import login,get_user_model
from django.db.models import Sum,Max,FloatField,F
#knox
from knox.views import LoginView as KnoxLoginView
from knox.auth import TokenAuthentication

#rest framework
from rest_framework import generics, permissions,viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

#apis
from .serializers import *
from apis.models import *

import io, csv, pandas as pd
import datetime

User = get_user_model()

# Login API
class LoginAPI(generics.GenericAPIView):
    """
    Use this API endpoint to obtain 
    user authentication token.
    
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = LoginSerializer
    def post(self, request, format=None):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        from knox.models import AuthToken
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })

# Get User API
class UsersViewAPI(generics.RetrieveUpdateAPIView):
    """
    API endpoint that allows users 
    to get his details and update it.
    
    """
    authentication_classes = (TokenAuthentication,)
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated,]

    def get_object(self):
        return self.request.user

# Get Countries API
class CountriesViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users 
    to get countries details with 
    cities.
    
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = [permissions.IsAuthenticated,]
    serializer_class = CountriesSerializer
    http_method_names = ['get',"post","delete"]
    queryset = Countries.objects.all()

# Get Sales Report
class SalesViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users 
    to be viewed or edited sales reports.
    
    """
    authentication_classes = (TokenAuthentication,)
    serializer_class = SalesSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Sales.objects.all()
    def get_queryset(self):
        queryset = self.queryset
        query_set = queryset.filter(user=self.request.user.id)
        return query_set

class StatisticsSalesViewAPI(APIView):
    """
    API endpoint that allows users 
    to get statistics sales report 
    based on sales.
    
    """
    authentication_classes = (TokenAuthentication,)
    qs = Sales.objects.all()
    all_revenue_sum = qs.aggregate(Sum('revenue'))['revenue__sum']
    all_sales_numbers_sum = qs.aggregate(Sum('sales_number'))['sales_number__sum']
    all_usr_avg = all_revenue_sum / all_sales_numbers_sum
    serializer_class = SalesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        user = self.request.user.id
        salesData = self.qs.filter(user=user)
        max_revenue = salesData.aggregate(Max('revenue'))['revenue__max']

        max_sales_number = salesData.aggregate(Max('sales_number'))['sales_number__max']

        revenue_sum = salesData.aggregate(Sum('revenue'))['revenue__sum']

        sales_numbers_sum = salesData.aggregate(Sum('sales_number'))['sales_number__sum']

        # current_user_avg_sale = revenue_sum / sales_numbers_sum
        current_user_avg_sale1 = salesData.aggregate(revenue_sum=Sum('revenue'),
        sales_numbers_sum=Sum('sales_number')).aggregate(
        current_user_avg_sale=F('revenue_sum') / F('sales_numbers_sum'))
        print(current_user_avg_sale1)
        current_user_highest_revenue = self.qs.filter(user=user,revenue=max_revenue).first()
        current_user_product_sales_number = self.qs.filter(user=user,sales_number=max_sales_number).first()
        content = {
                    "average_sales_for_current_user": current_user_avg_sale1,
                    "average_sale_all_user": self.all_usr_avg,
                    "highest_revenue_sale_for_current_user": {
                    "sale_id": current_user_highest_revenue.id,
                    "revenue": current_user_highest_revenue.revenue
                    },
                    "product_highest_revenue_for_current_user": {
                    "product_name": current_user_highest_revenue.product,
                    "price": current_user_highest_revenue.revenue
                    },
                    "product_highest_sales_number_for_current_user": {
                    "product_name": current_user_product_sales_number.product,
                    "price": current_user_product_sales_number.revenue
                    }
        }
        return Response(content)

class UploadSalesFileAPI(generics.CreateAPIView):
    """
    API endpoint that allows users 
    to upload sales csv report.
    
    """
    authentication_classes = (TokenAuthentication,)
    serializer_class = FileUploadSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        sales_file = serializer.validated_data['file']
        reader = pd.read_csv(sales_file)

        for _, row in reader.iterrows():
            sales_date = datetime.datetime.strptime(row['date'], "%Y-%m-%d").date()
            sales_object = Sales(
                       sales_date= sales_date,
                       product= row['product'],
                       revenue= row["revenue"],
                       sales_number= row["sales_number"],
                       user_id= request.user.id,
                       )
            sales_object.save()
        return Response({"status": "success"},)