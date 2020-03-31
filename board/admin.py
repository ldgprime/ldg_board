from django.contrib import admin
from board.models import Board, Movie

# Register your models here.
class BoardAdmin(admin.ModelAdmin):
    list_display=('idx','writer','title','content')

admin.site.register(Board, BoardAdmin)


class MovieAdmin(admin.ModelAdmin):
    list_display=('idx','title','content','point')
    
admin.site.register(Movie,MovieAdmin)