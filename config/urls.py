from django.contrib import admin
from django.urls import path, include


api_urlpatterns = [
    path('', ('stocks.api.urls', 'stocks', 'stocks')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', (api_urlpatterns, 'api', 'api')),

    path('', ('stocks.urls', 'stocks', 'stocks')),
]
