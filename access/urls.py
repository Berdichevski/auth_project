from django.urls import path
from access.views import AccessRuleListView, RoleListView, BusinessElementListView

urlpatterns = [
    path('access-rules/', AccessRuleListView.as_view()),
    path('roles/', RoleListView.as_view()),
    path('elements/', BusinessElementListView.as_view()),
]
