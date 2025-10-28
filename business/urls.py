from django.urls import path
from business.views import ProductsMockView

urlpatterns = [
    path('products/', ProductsMockView.as_view()),
]
