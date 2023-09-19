from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "Cardona Lab Database"

urlpatterns = [
    path('', admin.site.urls),
    path('cardonalab/', include('cardonalab.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)