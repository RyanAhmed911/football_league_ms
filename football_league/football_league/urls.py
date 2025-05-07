"""
URL configuration for football_league project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from league import views as league_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('league.urls')),
    
    # Frontend URLs
    path('', league_views.index, name='index'),
    path('standings/', league_views.standings_view, name='standings'),
    path('clubs/add/', league_views.club_form_view, name='club_form'),
    path('clubs/edit/<int:club_id>/', league_views.club_form_view, name='edit_club'),
    path('clubs/', league_views.clubs_view, name='clubs'),
    path('clubs/<int:club_id>/', league_views.club_detail_view, name='club_detail'),
    path('players/', league_views.players_view, name='players'),
    path('players/<int:player_id>/', league_views.player_detail_view, name='player_detail'),
    path('matches/', league_views.matches_view, name='matches'),
    path('transfers/', league_views.transfers_view, name='transfers'),
    path('players/add/', league_views.add_player_view, name='add-player'),
    path('players/contracted/edit/<int:player_id>/', league_views.edit_contracted_player_view, name='edit-contracted-player'),
    path('players/free-agent/edit/<int:player_id>/', league_views.edit_free_agent_view, name='edit-free-agent'),
    path('players/add/contracted/', league_views.PlayerListView.as_view(), name='add-contracted-player'),
    path('players/add/free-agent/', league_views.PlayerListView.as_view(), name='add-free-agent'),
]