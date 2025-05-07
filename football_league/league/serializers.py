from rest_framework import serializers

class PlayerSerializer(serializers.Serializer):
    player_id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100)
    birthdate = serializers.DateField(allow_null=True, required=False)
    height = serializers.FloatField(allow_null=True, required=False)
    nationality = serializers.CharField(max_length=50, allow_null=True, required=False)
    appearances = serializers.IntegerField(required=False, default=0)
    saves = serializers.IntegerField(required=False, default=0)
    goals = serializers.IntegerField(required=False, default=0)
    assists = serializers.IntegerField(required=False, default=0)
    position = serializers.CharField(max_length=30, allow_null=True, required=False)

class ClubSerializer(serializers.Serializer):
    club_id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100)
    founded = serializers.DateField(allow_null=True, required=False)
    location = serializers.CharField(max_length=100, allow_null=True, required=False)
    stadium = serializers.CharField(max_length=100, allow_null=True, required=False)
    matches_played = serializers.IntegerField(required=False, default=0)
    goal_difference = serializers.IntegerField(required=False, default=0)
    points = serializers.IntegerField(required=False, default=0)
    budget = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, default=0)

class CoachSerializer(serializers.Serializer):
    coach_id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100)
    nationality = serializers.CharField(max_length=50, allow_null=True, required=False)
    club_id = serializers.IntegerField(allow_null=True, required=False)
    club_name = serializers.CharField(read_only=True, required=False)

class SquadSerializer(serializers.Serializer):
    squad_id = serializers.IntegerField(read_only=True)
    club_id = serializers.IntegerField()
    coach_id = serializers.IntegerField(allow_null=True, required=False)
    club_name = serializers.CharField(read_only=True, required=False)
    coach_name = serializers.CharField(read_only=True, required=False)
    squad_type = serializers.CharField(read_only=True, required=False)

class ContractedPlayerSerializer(serializers.Serializer):
    player_id = serializers.IntegerField()
    jersey_number = serializers.IntegerField(allow_null=True, required=False)
    club_id = serializers.IntegerField()
    squad_id = serializers.IntegerField()
    name = serializers.CharField(read_only=True, required=False)
    position = serializers.CharField(read_only=True, required=False)
    club_name = serializers.CharField(read_only=True, required=False)
    squad_type = serializers.CharField(read_only=True, required=False)

class FreeAgentSerializer(serializers.Serializer):
    player_id = serializers.IntegerField()
    name = serializers.CharField(read_only=True, required=False)
    position = serializers.CharField(read_only=True, required=False)
    nationality = serializers.CharField(read_only=True, required=False)

class SponsorSerializer(serializers.Serializer):
    sponsor_id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100)
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    contract_length = serializers.IntegerField(allow_null=True, required=False)

class SponsorshipSerializer(serializers.Serializer):
    club_id = serializers.IntegerField()
    sponsor_id = serializers.IntegerField()
    club_name = serializers.CharField(read_only=True, required=False)
    sponsor_name = serializers.CharField(read_only=True, required=False)
    amount = serializers.DecimalField(read_only=True, max_digits=15, decimal_places=2, required=False)

class TransferSerializer(serializers.Serializer):
    sender_id = serializers.IntegerField()
    receiver_id = serializers.IntegerField()
    player_id = serializers.IntegerField()
    offer_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    status = serializers.CharField(read_only=True)
    sender_name = serializers.CharField(read_only=True, required=False)
    receiver_name = serializers.CharField(read_only=True, required=False)
    player_name = serializers.CharField(read_only=True, required=False)

class MatchSerializer(serializers.Serializer):
    home_id = serializers.IntegerField()
    away_id = serializers.IntegerField()
    match_date = serializers.DateField()
    match_time = serializers.TimeField()
    home_goals = serializers.IntegerField(required=False, default=None)
    away_goals = serializers.IntegerField(required=False, default=None)
    home_team = serializers.CharField(read_only=True, required=False)
    away_team = serializers.CharField(read_only=True, required=False)

class MatchResultSerializer(serializers.Serializer):
    home_goals = serializers.IntegerField(min_value=0)
    away_goals = serializers.IntegerField(min_value=0)

class AuctionSerializer(serializers.Serializer):
    player_id = serializers.IntegerField()
    club_id = serializers.IntegerField()
    highest_bid = serializers.DecimalField(max_digits=15, decimal_places=2)
    status = serializers.CharField(read_only=True)
    player_name = serializers.CharField(read_only=True, required=False)
    club_name = serializers.CharField(read_only=True, required=False)

class BidSerializer(serializers.Serializer):
    player_id = serializers.IntegerField()
    club_id = serializers.IntegerField()
    bid_amount = serializers.DecimalField(max_digits=15, decimal_places=2)