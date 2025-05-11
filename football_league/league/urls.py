from django.urls import path
from . import views

urlpatterns = [
    # Player endpoints
    path('players/', views.PlayerListView.as_view(), name='player-list'),
    path('players/<int:player_id>/', views.PlayerDetailView.as_view(), name='player-detail'),
    path('players/top-scorers/', views.TopScorersView.as_view(), name='top-scorers'),
    path('api/players/<int:player_id>/', views.PlayerDetailView.as_view(), name='player-detail'),
    path('players/contracted/edit/<int:player_id>/', views.edit_contracted_player_view, name='edit-contracted-player'),
    path('players/free-agent/edit/<int:player_id>/', views.edit_free_agent_view, name='edit-free-agent'),
    path('players/add/', views.add_player_api, name='add-player-api'),
    path('clubs/<int:club_id>/squads/', views.get_club_squads_api, name='get-club-squads-api'),
    path('players/add/contracted/', views.add_contracted_player_view, name='add-contracted-player'),
    path('players/add/free-agent/', views.add_free_agent_view, name='add-free-agent'),

    # Club endpoints
    path('clubs/', views.ClubListView.as_view(), name='club-list'),
    path('clubs/<int:club_id>/', views.ClubDetailView.as_view(), name='club-detail'),
    path('clubs/<int:club_id>/players/', views.ClubPlayersView.as_view(), name='club-players'),
    path('clubs/<int:club_id>/squads/', views.ClubSquadsView.as_view(), name='club-squads'),
    path('clubs/<int:club_id>/sponsorships/', views.ClubSponsorshipsView.as_view(), name='club-sponsorships'),
    path('clubs/<int:club_id>/matches/', views.ClubMatchesView.as_view(), name='club-matches'),
    path('standings/', views.StandingsView.as_view(), name='standings'),
    path('api/clubs/', views.ClubListView.as_view(), name='club-list'),   
    
    # Coach endpoints
    path('coaches/', views.CoachListView.as_view(), name='coach-list'),
    path('coaches/<int:coach_id>/', views.CoachDetailView.as_view(), name='coach-detail'),
    path('api/coaches/<int:coach_id>/', views.CoachDetailView.as_view(), name='coach-detail'),
    
    # Squad endpoints
    path('squads/', views.SquadListView.as_view(), name='squad-list'),
    path('squads/<int:squad_id>/', views.SquadDetailView.as_view(), name='squad-detail'),
    
    # Contracted Player endpoints
    path('contracted-players/', views.ContractedPlayerListView.as_view(), name='contracted-player-list'),
    path('contracted-players/<int:player_id>/', views.ContractedPlayerDetailView.as_view(), name='contracted-player-detail'),
    
    # Free Agent endpoints
    path('free-agents/', views.FreeAgentListView.as_view(), name='free-agent-list'),
    path('free-agents/<int:player_id>/', views.FreeAgentDetailView.as_view(), name='free-agent-detail'),
    
    # Sponsor endpoints
    path('sponsors/', views.SponsorListView.as_view(), name='sponsor-list'),
    path('sponsors/<int:sponsor_id>/', views.SponsorDetailView.as_view(), name='sponsor-detail'),
    path('api/sponsors/<int:sponsor_id>/', views.SponsorDetailView.as_view(), name='sponsor-detail'), 
    
    # Sponsorship endpoints
    path('sponsorships/', views.SponsorshipListView.as_view(), name='sponsorship-list'),
    
    # Transfer endpoints
    path('transfers/', views.TransferListView.as_view(), name='transfer-list'),
    path('transfers/active/', views.ActiveTransfersView.as_view(), name='active-transfers'),
    path('transfers/<int:sender_id>/<int:receiver_id>/<int:player_id>/accept/', views.TransferAcceptView.as_view(), name='transfer-accept'),
    path('transfers/<int:sender_id>/<int:receiver_id>/<int:player_id>/reject/', 
         views.TransferRejectView.as_view(), name='transfer-reject'),
    
    # Match endpoints
    path('matches/', views.MatchListView.as_view(), name='match-list'),
    path('matches/<int:home_id>/<int:away_id>/result/', views.RecordMatchResultView.as_view(), name='record-match-result'),
    path('matches/<int:home_id>/<int:away_id>/', views.DeleteMatchView.as_view(), name='delete-match'),
    
    # Auction endpoints
    path('auctions/', views.AuctionListView.as_view(), name='auction-list'),
    path('auctions/active/', views.ActiveAuctionsView.as_view(), name='active-auctions'),
    path('auctions/bid/', views.PlaceBidView.as_view(), name='place-bid'),
    path('auctions/<int:player_id>/<int:club_id>/complete/', views.CompleteAuctionView.as_view(), name='complete-auction'),
    path('auctions/<int:player_id>/cancel/', views.CancelAuctionView.as_view(), name='cancel-auction'),
    path('auctions/', views.auctions_view, name='auctions'),
]