from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction

from .models import (
    Player, Club, Coach, Squad, ContractedPlayer, FreeAgent,
    Sponsor, Sponsorship, Transfer, Match, Auction
)
from .serializers import (
    PlayerSerializer, ClubSerializer, CoachSerializer, SquadSerializer,
    ContractedPlayerSerializer, FreeAgentSerializer, SponsorSerializer,
    SponsorshipSerializer, TransferSerializer, MatchSerializer,
    MatchResultSerializer, AuctionSerializer, BidSerializer
)

# Player views
class PlayerListView(APIView):
    def post(self, request):
        player_data = request.data
        player_type = player_data.pop('playerType', None)

        # Extract fields specific to contracted players
        club_id = player_data.pop('club_id', None)
        jersey_number = player_data.pop('jersey_number', None)

        # Create the player in the player table
        player_id = Player.create(**player_data)

        if player_type == 'contracted':
            # Ensure club_id and jersey_number are provided for contracted players
            if not club_id:
                return Response({"error": "Club is required for contracted players"}, status=status.HTTP_400_BAD_REQUEST)
            if not jersey_number:
                return Response({"error": "Jersey number is required for contracted players"}, status=status.HTTP_400_BAD_REQUEST)

            # Add the player to the contracted_player table
            ContractedPlayer.create(player_id, jersey_number, club_id, None)

        elif player_type == 'free_agent':
            # Add the player to the free_agent table
            FreeAgent.create(player_id)

        # Fetch the newly created player details
        player = Player.get_by_id(player_id)
        return Response(player, status=status.HTTP_201_CREATED)

class PlayerDetailView(APIView):
    def get(self, request, player_id):
        player = Player.get_by_id(player_id)
        if not player:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = PlayerSerializer(player)
        return Response(serializer.data)
    
    def put(self, request, player_id):
        player = Player.get_by_id(player_id)
        if not player:
            return Response({"error": "Player not found"}, status=status.HTTP_404_NOT_FOUND)

        # Only update fields that are provided in the request
        update_data = {key: value for key, value in request.data.items() if value is not None}
        if not update_data:
            return Response({"error": "No valid fields to update"}, status=status.HTTP_400_BAD_REQUEST)

        # Update the player table
        Player.update(player_id, **update_data)
        updated_player = Player.get_by_id(player_id)
        return Response(updated_player)
    
    def delete(self, request, player_id):
        player = Player.get_by_id(player_id)
        if not player:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        Player.delete(player_id)
        return Response(status=status.HTTP_204_NO_CONTENT)

class TopScorersView(APIView):
    def get(self, request):
        limit = int(request.query_params.get('limit', 10))
        players = Player.get_top_scorers(limit)
        serializer = PlayerSerializer(players, many=True)
        return Response(serializer.data)

# Club views
class ClubListView(APIView):
    def get(self, request):
        clubs = Club.get_all()
        serializer = ClubSerializer(clubs, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = ClubSerializer(data=request.data)
        if serializer.is_valid():
            club_id = Club.create(**serializer.validated_data)
            club = Club.get_by_id(club_id)
            return Response(club, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ClubDetailView(APIView):
    def get(self, request, club_id):
        club = Club.get_by_id(club_id)
        if not club:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ClubSerializer(club)
        return Response(serializer.data)
    
    def put(self, request, club_id):
        club = Club.get_by_id(club_id)
        if not club:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = ClubSerializer(data=request.data)
        if serializer.is_valid():
            Club.update(club_id, **serializer.validated_data)
            updated_club = Club.get_by_id(club_id)
            return Response(updated_club)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    

class ClubPlayersView(APIView):
    def get(self, request, club_id):
        players = ContractedPlayer.get_by_club(club_id)
        serializer = ContractedPlayerSerializer(players, many=True)
        return Response(serializer.data)

class ClubSquadsView(APIView):
    def get(self, request, club_id):
        squads = Squad.get_by_club(club_id)
        serializer = SquadSerializer(squads, many=True)
        return Response(serializer.data)

class StandingsView(APIView):
    def get(self, request):
        standings = Club.get_standings()
        serializer = ClubSerializer(standings, many=True)
        return Response(serializer.data)

# Coach views
class CoachListView(APIView):
    def get(self, request):
        coaches = Coach.get_all()
        serializer = CoachSerializer(coaches, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = CoachSerializer(data=request.data)
        if serializer.is_valid():
            coach_id = Coach.create(**serializer.validated_data)
            coach = Coach.get_by_id(coach_id)
            return Response(coach, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CoachDetailView(APIView):
    def get(self, request, coach_id):
        coach = Coach.get_by_id(coach_id)
        if not coach:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = CoachSerializer(coach)
        return Response(serializer.data)

# Squad views
class SquadListView(APIView):
    def get(self, request):
        squads = Squad.get_all()
        serializer = SquadSerializer(squads, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = SquadSerializer(data=request.data)
        if serializer.is_valid():
            squad_type = request.data.get('squad_type')
            squad_id = Squad.create(
                serializer.validated_data['club_id'],
                serializer.validated_data.get('coach_id'),
                squad_type
            )
            squad = Squad.get_by_id(squad_id)
            return Response(squad, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SquadDetailView(APIView):
    def get(self, request, squad_id):
        squad = Squad.get_by_id(squad_id)
        if not squad:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = SquadSerializer(squad)
        return Response(serializer.data)

# Contracted Player views
class ContractedPlayerListView(APIView):
    def get(self, request):
        players = ContractedPlayer.get_all()
        serializer = ContractedPlayerSerializer(players, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = ContractedPlayerSerializer(data=request.data)
        if serializer.is_valid():
            success, result = ContractedPlayer.create(
                serializer.validated_data['player_id'],
                serializer.validated_data.get('jersey_number'),
                serializer.validated_data['club_id'],
                serializer.validated_data['squad_id']
            )
            if success:
                player = ContractedPlayer.get_by_id(result)
                return Response(player, status=status.HTTP_201_CREATED)
            return Response({"error": result}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ContractedPlayerDetailView(APIView):
    def get(self, request, player_id):
        player = ContractedPlayer.get_by_id(player_id)
        if not player:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ContractedPlayerSerializer(player)
        return Response(serializer.data)

# Free Agent views (continued)
class FreeAgentListView(APIView):
    def get(self, request):
        players = FreeAgent.get_all()
        serializer = FreeAgentSerializer(players, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = FreeAgentSerializer(data=request.data)
        if serializer.is_valid():
            success, result = FreeAgent.create(serializer.validated_data['player_id'])
            if success:
                player = FreeAgent.get_by_id(result)
                return Response(player, status=status.HTTP_201_CREATED)
            return Response({"error": result}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FreeAgentDetailView(APIView):
    def get(self, request, player_id):
        player = FreeAgent.get_by_id(player_id)
        if not player:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = FreeAgentSerializer(player)
        return Response(serializer.data)

# Sponsor views
class SponsorListView(APIView):
    def get(self, request):
        sponsors = Sponsor.get_all()
        serializer = SponsorSerializer(sponsors, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = SponsorSerializer(data=request.data)
        if serializer.is_valid():
            sponsor_id = Sponsor.create(**serializer.validated_data)
            sponsor = Sponsor.get_by_id(sponsor_id)
            return Response(sponsor, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SponsorDetailView(APIView):
    def get(self, request, sponsor_id):
        sponsor = Sponsor.get_by_id(sponsor_id)
        if not sponsor:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = SponsorSerializer(sponsor)
        return Response(serializer.data)

# Sponsorship views
class SponsorshipListView(APIView):
    def get(self, request):
        sponsorships = Sponsorship.get_all()
        serializer = SponsorshipSerializer(sponsorships, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = SponsorshipSerializer(data=request.data)
        if serializer.is_valid():
            success = Sponsorship.create(
                serializer.validated_data['club_id'],
                serializer.validated_data['sponsor_id']
            )
            if success:
                return Response({"message": "Sponsorship created successfully"}, status=status.HTTP_201_CREATED)
            return Response({"error": "Failed to create sponsorship"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ClubSponsorshipsView(APIView):
    def get(self, request, club_id):
        sponsorships = Sponsorship.get_by_club(club_id)
        serializer = SponsorshipSerializer(sponsorships, many=True)
        return Response(serializer.data)

# Transfer views
class TransferListView(APIView):
    def get(self, request):
        transfers = Transfer.get_all()
        serializer = TransferSerializer(transfers, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = TransferSerializer(data=request.data)
        if serializer.is_valid():
            success, message = Transfer.create_offer(
                serializer.validated_data['sender_id'],
                serializer.validated_data['receiver_id'],
                serializer.validated_data['player_id'],
                serializer.validated_data['offer_amount']
            )
            if success:
                return Response({"message": message}, status=status.HTTP_201_CREATED)
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ActiveTransfersView(APIView):
    def get(self, request):
        club_id = request.query_params.get('club_id')
        if club_id:
            transfers = Transfer.get_active_offers(int(club_id))
        else:
            transfers = Transfer.get_active_offers()
        serializer = TransferSerializer(transfers, many=True)
        return Response(serializer.data)

class TransferAcceptView(APIView):
    def post(self, request, sender_id, receiver_id, player_id):
        success, message = Transfer.accept_offer(sender_id, receiver_id, player_id)
        if success:
            return Response({"message": message})
        return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

class TransferRejectView(APIView):
    def post(self, request, sender_id, receiver_id, player_id):
        success, message = Transfer.reject_offer(sender_id, receiver_id, player_id)
        if success:
            return Response({"message": message})
        return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

# Match views
class MatchListView(APIView):
    def get(self, request):
        matches = Match.get_all()
        serializer = MatchSerializer(matches, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = MatchSerializer(data=request.data)
        if serializer.is_valid():
            # Extract all validated data including scores if present
            home_id = serializer.validated_data['home_id']
            away_id = serializer.validated_data['away_id']
            match_date = serializer.validated_data['match_date']
            match_time = serializer.validated_data['match_time']
            home_goals = serializer.validated_data.get('home_goals')  # Use get() to handle optional fields
            away_goals = serializer.validated_data.get('away_goals')
            
            success, message = Match.create(
                home_id, away_id, match_date, match_time, home_goals, away_goals
            )
            if success:
                return Response({"message": message}, status=status.HTTP_201_CREATED)
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ClubMatchesView(APIView):
    def get(self, request, club_id):
        matches = Match.get_by_club(club_id)
        serializer = MatchSerializer(matches, many=True)
        return Response(serializer.data)

class RecordMatchResultView(APIView):
    def post(self, request, home_id, away_id):
        serializer = MatchResultSerializer(data=request.data)
        if serializer.is_valid():
            try:
                success, message = Match.record_result(
                    home_id,
                    away_id,
                    serializer.validated_data['home_goals'],
                    serializer.validated_data['away_goals']
                )
                if success:
                    return Response({"message": message})
                return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                # Log the error for debugging
                print(f"Error recording match result: {e}")
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Auction views
class AuctionListView(APIView):
    def get(self, request):
        auctions = Auction.get_all()
        serializer = AuctionSerializer(auctions, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = AuctionSerializer(data=request.data)
        if serializer.is_valid():
            success, message = Auction.create(
                serializer.validated_data['player_id'],
                serializer.validated_data['club_id'],
                serializer.validated_data['highest_bid']
            )
            if success:
                return Response({"message": message}, status=status.HTTP_201_CREATED)
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ActiveAuctionsView(APIView):
    def get(self, request):
        auctions = Auction.get_active()
        serializer = AuctionSerializer(auctions, many=True)
        return Response(serializer.data)

class PlaceBidView(APIView):
    def post(self, request):
        serializer = BidSerializer(data=request.data)
        if serializer.is_valid():
            success, message = Auction.place_bid(
                serializer.validated_data['player_id'],
                serializer.validated_data['club_id'],
                serializer.validated_data['bid_amount']
            )
            if success:
                return Response({"message": message})
            return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CompleteAuctionView(APIView):
    def post(self, request, player_id, club_id):
        success, message = Auction.complete_auction(player_id, club_id)
        if success:
            return Response({"message": message})
        return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)

class CancelAuctionView(APIView):
    def post(self, request, player_id):
        success, message = Auction.cancel_auction(player_id)
        if success:
            return Response({"message": message})
        return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)
    
# Frontend views
from django.shortcuts import render

def index(request):
    return render(request, 'league/index.html')

def standings_view(request):
    return render(request, 'league/standings.html')

def club_form_view(request, club_id=None):
    return render(request, 'league/club_form.html')

def clubs_view(request):
    return render(request, 'league/clubs.html')

def club_detail_view(request, club_id):
    return render(request, 'league/club_detail.html')

def players_view(request):
    return render(request, 'league/players.html')

def player_detail_view(request, player_id):
    return render(request, 'league/player_detail.html')

def matches_view(request):
    return render(request, 'league/matches.html')

def transfers_view(request):
    return render(request, 'league/transfers.html')

def add_player_view(request):
    return render(request, 'league/add_player.html')

def edit_contracted_player_view(request, player_id):
    player = ContractedPlayer.get_by_id(player_id)
    return render(request, 'league/edit_contracted_player.html', {'player': player})

def edit_free_agent_view(request, player_id):
    player = FreeAgent.get_by_id(player_id)
    return render(request, 'league/edit_free_agent.html', {'player': player})