from django.contrib import admin
from django.urls import path
import atsapp
from django.urls import include

import atsapp.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', atsapp.views.home,name="home"),
    path('upload_resume/', atsapp.views.upload_resume, name='upload_resume'),
    path('ats/', include('atsapp.urls'))
]