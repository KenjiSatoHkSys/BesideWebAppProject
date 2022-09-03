from django.contrib import admin
from .models import Beside_db
from .models import Openweather_db
from .models import Manager_db

admin.site.register(Beside_db)
admin.site.register(Openweather_db)
admin.site.register(Manager_db)

# Register your models here.
