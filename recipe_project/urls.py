"""
URL configuration for recipe_project project.

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
from django.conf import settings # allows you to access the MEDIA_URL and MEDIA_ROOT variables that you need to add.
from django.conf.urls.static import static # provides access to the Django helper function static( ), which allows you to create URLs from local folder names.

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('recipes.urls')),
    # path('recipes/', include('recipes.urls'))
]

# extends urlpatterns parameter to include the media info.
# have now specifies the URL "/media/" that will trigger this media view.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)