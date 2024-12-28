"""
URL configuration for ApiRoot project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include

from auth.views import LogoutView
from django.http import JsonResponse
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from django.urls import re_path

from amadeus_integration.views import GetAmadeusToken, GetFlightOffers, BestTravelOptions

schema_view = get_schema_view(
    openapi.Info(
        title="Amadeus API",
        default_version="v1",
        description="API documentation for Amadeus Integration",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@amadeusapi.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


def test_cors(request):
    return JsonResponse({"message": "CORS test successful!"})

urlpatterns = [
    # jwt auth endpoints
    path("test-cors/", test_cors, name="test_cors"),
    path("admin/", admin.site.urls),
    path("auth/", include("djoser.urls")),
    path("auth/", include("djoser.urls.jwt")),
    path("auth/logout/", LogoutView.as_view()),

    # swagger endpoints    
    re_path(
        r"^swagger(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    re_path(
        r"^swagger/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    re_path(
        r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"
    ),
    

    # flight endpoints    
    path("get-token/", GetAmadeusToken.as_view(), name="get-amadeus-token"),
    path("flight-offers/", GetFlightOffers.as_view(), name="get-flight-offers"),
    path("best-options/", BestTravelOptions.as_view(), name="best-travel-options"),
    
]
