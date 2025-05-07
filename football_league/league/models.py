from django.db import connection, models, transaction
from .utils import dictfetchall, dictfetchone

class Player:
    @classmethod
    def get_all(cls):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM player")
            return dictfetchall(cursor)
    
    @classmethod
    def get_by_id(cls, player_id):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM player WHERE player_id = %s", [player_id])
            return dictfetchone(cursor)
    
    @classmethod
    def create(cls, name, birthdate=None, height=None, nationality=None, position=None):
        with connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO player (name, birthdate, height, nationality, position) 
                   VALUES (%s, %s, %s, %s, %s) RETURNING player_id""",
                [name, birthdate, height, nationality, position]
            )
            player_id = cursor.fetchone()[0]
            return player_id
    
    @classmethod
    def update(cls, player_id, **kwargs):
        fields = []
        values = []
        
        for key, value in kwargs.items():
            if key not in ['player_id']:  # Exclude primary key
                fields.append(f"{key} = %s")
                values.append(value)
        
        if not fields:
            return False
        
        values.append(player_id)  # Add player_id for WHERE clause
        
        with connection.cursor() as cursor:
            cursor.execute(
                f"UPDATE player SET {', '.join(fields)} WHERE player_id = %s",
                values
            )
            return cursor.rowcount > 0
    
    @classmethod
    def delete(cls, player_id):
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM player WHERE player_id = %s", [player_id])
            return cursor.rowcount > 0
    
    @classmethod
    def get_top_scorers(cls, limit=10):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT p.*, c.name as club_name
                FROM player p
                LEFT JOIN contracted_player cp ON p.player_id = cp.player_id
                LEFT JOIN club c ON cp.club_id = c.club_id
                ORDER BY p.goals DESC
                LIMIT %s
            """, [limit])
            return dictfetchall(cursor)


class ContractedPlayer:
    @classmethod
    def get_all(cls):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT cp.*, p.name, p.position, c.name as club_name
                FROM contracted_player cp
                JOIN player p ON cp.player_id = p.player_id
                JOIN club c ON cp.club_id = c.club_id
            """)
            return dictfetchall(cursor)
    
    @classmethod
    def get_by_id(cls, player_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT cp.*, p.name, p.position, c.name as club_name
                FROM contracted_player cp
                JOIN player p ON cp.player_id = p.player_id
                JOIN club c ON cp.club_id = c.club_id
                WHERE cp.player_id = %s
            """, [player_id])
            return dictfetchone(cursor)
    
    @classmethod
    def get_by_club(cls, club_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT cp.*, p.name, p.position, s.squad_id,
                       CASE WHEN ft.squad_id IS NOT NULL THEN 'First Team' 
                            WHEN yt.squad_id IS NOT NULL THEN 'Youth Team' 
                            ELSE 'Unknown' END as squad_type
                FROM contracted_player cp
                JOIN player p ON cp.player_id = p.player_id
                JOIN squad s ON cp.squad_id = s.squad_id
                LEFT JOIN first_team ft ON s.squad_id = ft.squad_id
                LEFT JOIN youth_team yt ON s.squad_id = yt.squad_id
                WHERE cp.club_id = %s
            """, [club_id])
            return dictfetchall(cursor)
    
    @classmethod
    def create(cls, player_id, jersey_number, club_id, squad_id):
        with transaction.atomic():
            with connection.cursor() as cursor:
                # First check if player exists
                cursor.execute("SELECT player_id FROM player WHERE player_id = %s", [player_id])
                if not cursor.fetchone():
                    return False, "Player does not exist"
                
                # Check if player is already contracted
                cursor.execute("SELECT player_id FROM contracted_player WHERE player_id = %s", [player_id])
                if cursor.fetchone():
                    return False, "Player is already contracted"
                
                # Check if player is a free agent
                cursor.execute("SELECT player_id FROM free_agent WHERE player_id = %s", [player_id])
                if not cursor.fetchone():
                    return False, "Player is not a free agent"
                
                # Insert into contracted_player
                cursor.execute(
                    """INSERT INTO contracted_player (player_id, jersey_number, club_id, squad_id) 
                       VALUES (%s, %s, %s, %s)""",
                    [player_id, jersey_number, club_id, squad_id]
                )
                
                # Remove from free_agent
                cursor.execute("DELETE FROM free_agent WHERE player_id = %s", [player_id])
                
                return True, player_id


class FreeAgent:
    @classmethod
    def get_all(cls):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT fa.*, p.name, p.position, p.nationality
                FROM free_agent fa
                JOIN player p ON fa.player_id = p.player_id
            """)
            return dictfetchall(cursor)
    
    @classmethod
    def get_by_id(cls, player_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT fa.*, p.name, p.position, p.nationality
                FROM free_agent fa
                JOIN player p ON fa.player_id = p.player_id
                WHERE fa.player_id = %s
            """, [player_id])
            return dictfetchone(cursor)
    
    @classmethod
    def create(cls, player_id):
        with connection.cursor() as cursor:
            # Check if player exists
            cursor.execute("SELECT player_id FROM player WHERE player_id = %s", [player_id])
            if not cursor.fetchone():
                return False, "Player does not exist"
            
            # Check if player is already a free agent
            cursor.execute("SELECT player_id FROM free_agent WHERE player_id = %s", [player_id])
            if cursor.fetchone():
                return False, "Player is already a free agent"
            
            # Insert into free_agent
            cursor.execute("INSERT INTO free_agent (player_id) VALUES (%s)", [player_id])
            return True, player_id


class Club:
    @classmethod
    def get_all(cls):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM club")
            return dictfetchall(cursor)
    
    @classmethod
    def get_by_id(cls, club_id):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM club WHERE club_id = %s", [club_id])
            return dictfetchone(cursor)
    
    @classmethod
    def create(cls, name, founded=None, location=None, stadium=None, budget=0, matches_played=0, goal_difference=0, points=0):
        with connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO club (name, founded, location, stadium, budget, matches_played, goal_difference, points) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING club_id""",
                [name, founded, location, stadium, budget, matches_played, goal_difference, points]
            )
            club_id = cursor.fetchone()[0]
            return club_id
    
    @classmethod
    def update(cls, club_id, **kwargs):
        fields = []
        values = []
        
        for key, value in kwargs.items():
            if key not in ['club_id']:  # Exclude primary key
                fields.append(f"{key} = %s")
                values.append(value)
        
        if not fields:
            return False
        
        values.append(club_id)  # Add club_id for WHERE clause
        
        with connection.cursor() as cursor:
            cursor.execute(
                f"UPDATE club SET {', '.join(fields)} WHERE club_id = %s",
                values
            )
            return cursor.rowcount > 0
    
    @classmethod
    def get_standings(cls):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT club_id, name, matches_played, points, goal_difference 
                FROM club 
                ORDER BY points DESC, goal_difference DESC
            """)
            return dictfetchall(cursor)


class Coach:
    @classmethod
    def get_all(cls):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT c.*, cl.name as club_name
                FROM coach c
                LEFT JOIN club cl ON c.club_id = cl.club_id
            """)
            return dictfetchall(cursor)
    
    @classmethod
    def get_by_id(cls, coach_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT c.*, cl.name as club_name
                FROM coach c
                LEFT JOIN club cl ON c.club_id = cl.club_id
                WHERE c.coach_id = %s
            """, [coach_id])
            return dictfetchone(cursor)
    
    @classmethod
    def create(cls, name, nationality=None, club_id=None):
        with connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO coach (name, nationality, club_id) 
                   VALUES (%s, %s, %s) RETURNING coach_id""",
                [name, nationality, club_id]
            )
            coach_id = cursor.fetchone()[0]
            return coach_id


class Squad:
    @classmethod
    def get_all(cls):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT s.*, c.name as club_name, co.name as coach_name,
                       CASE WHEN ft.squad_id IS NOT NULL THEN 'First Team' 
                            WHEN yt.squad_id IS NOT NULL THEN 'Youth Team' 
                            ELSE 'Unknown' END as squad_type
                FROM squad s
                JOIN club c ON s.club_id = c.club_id
                LEFT JOIN coach co ON s.coach_id = co.coach_id
                LEFT JOIN first_team ft ON s.squad_id = ft.squad_id
                LEFT JOIN youth_team yt ON s.squad_id = yt.squad_id
            """)
            return dictfetchall(cursor)
    
    @classmethod
    def get_by_id(cls, squad_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT s.*, c.name as club_name, co.name as coach_name,
                       CASE WHEN ft.squad_id IS NOT NULL THEN 'First Team' 
                            WHEN yt.squad_id IS NOT NULL THEN 'Youth Team' 
                            ELSE 'Unknown' END as squad_type
                FROM squad s
                JOIN club c ON s.club_id = c.club_id
                LEFT JOIN coach co ON s.coach_id = co.coach_id
                LEFT JOIN first_team ft ON s.squad_id = ft.squad_id
                LEFT JOIN youth_team yt ON s.squad_id = yt.squad_id
                WHERE s.squad_id = %s
            """, [squad_id])
            return dictfetchone(cursor)
    
    @classmethod
    def get_by_club(cls, club_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT s.*, c.name as club_name, co.name as coach_name,
                       CASE WHEN ft.squad_id IS NOT NULL THEN 'First Team' 
                            WHEN yt.squad_id IS NOT NULL THEN 'Youth Team' 
                            ELSE 'Unknown' END as squad_type
                FROM squad s
                JOIN club c ON s.club_id = c.club_id
                LEFT JOIN coach co ON s.coach_id = co.coach_id
                LEFT JOIN first_team ft ON s.squad_id = ft.squad_id
                LEFT JOIN youth_team yt ON s.squad_id = yt.squad_id
                WHERE s.club_id = %s
            """, [club_id])
            return dictfetchall(cursor)
    
    @classmethod
    def create(cls, club_id, coach_id=None, squad_type=None):
        with transaction.atomic():
            with connection.cursor() as cursor:
                # Create squad
                cursor.execute(
                    """INSERT INTO squad (club_id, coach_id) 
                       VALUES (%s, %s) RETURNING squad_id""",
                    [club_id, coach_id]
                )
                squad_id = cursor.fetchone()[0]
                
                # Create specialized squad if needed
                if squad_type == 'first_team':
                    cursor.execute("INSERT INTO first_team (squad_id) VALUES (%s)", [squad_id])
                elif squad_type == 'youth_team':
                    cursor.execute("INSERT INTO youth_team (squad_id) VALUES (%s)", [squad_id])
                
                return squad_id


class FirstTeam:
    @classmethod
    def get_all(cls):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT ft.*, s.club_id, c.name as club_name, co.name as coach_name
                FROM first_team ft
                JOIN squad s ON ft.squad_id = s.squad_id
                JOIN club c ON s.club_id = c.club_id
                LEFT JOIN coach co ON s.coach_id = co.coach_id
            """)
            return dictfetchall(cursor)


class YouthTeam:
    @classmethod
    def get_all(cls):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT yt.*, s.club_id, c.name as club_name, co.name as coach_name
                FROM youth_team yt
                JOIN squad s ON yt.squad_id = s.squad_id
                JOIN club c ON s.club_id = c.club_id
                LEFT JOIN coach co ON s.coach_id = co.coach_id
            """)
            return dictfetchall(cursor)


class Sponsor:
    @classmethod
    def get_all(cls):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM sponsor")
            return dictfetchall(cursor)
    
    @classmethod
    def get_by_id(cls, sponsor_id):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM sponsor WHERE sponsor_id = %s", [sponsor_id])
            return dictfetchone(cursor)
    
    @classmethod
    def create(cls, name, amount, contract_length=None):
        with connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO sponsor (name, amount, contract_length) 
                   VALUES (%s, %s, %s) RETURNING sponsor_id""",
                [name, amount, contract_length]
            )
            sponsor_id = cursor.fetchone()[0]
            return sponsor_id


class Sponsorship:
    @classmethod
    def get_all(cls):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT sp.*, c.name as club_name, s.name as sponsor_name, s.amount
                FROM sponsorship sp
                JOIN club c ON sp.club_id = c.club_id
                JOIN sponsor s ON sp.sponsor_id = s.sponsor_id
            """)
            return dictfetchall(cursor)
    
    @classmethod
    def get_by_club(cls, club_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT sp.*, c.name as club_name, s.name as sponsor_name, s.amount
                FROM sponsorship sp
                JOIN club c ON sp.club_id = c.club_id
                JOIN sponsor s ON sp.sponsor_id = s.sponsor_id
                WHERE sp.club_id = %s
            """, [club_id])
            return dictfetchall(cursor)
    
    @classmethod
    def create(cls, club_id, sponsor_id):
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO sponsorship (club_id, sponsor_id) VALUES (%s, %s)",
                [club_id, sponsor_id]
            )
            return True
    
    @classmethod
    def delete(cls, club_id, sponsor_id):
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM sponsorship WHERE club_id = %s AND sponsor_id = %s",
                [club_id, sponsor_id]
            )
            return cursor.rowcount > 0


class Transfer:
    @classmethod
    def get_all(cls):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT t.*, c1.name as sender_name, c2.name as receiver_name, p.name as player_name
                FROM transfer t
                JOIN club c1 ON t.sender_id = c1.club_id
                JOIN club c2 ON t.receiver_id = c2.club_id
                JOIN player p ON t.player_id = p.player_id
            """)
            return dictfetchall(cursor)
    
    @classmethod
    def get_active_offers(cls, club_id=None):
        with connection.cursor() as cursor:
            if club_id:
                cursor.execute("""
                    SELECT t.*, c1.name as sender_name, c2.name as receiver_name, p.name as player_name
                    FROM transfer t
                    JOIN club c1 ON t.sender_id = c1.club_id
                    JOIN club c2 ON t.receiver_id = c2.club_id
                    JOIN player p ON t.player_id = p.player_id
                    WHERE (t.sender_id = %s OR t.receiver_id = %s) AND t.status = 'ACTIVE'
                """, [club_id, club_id])
            else:
                cursor.execute("""
                    SELECT t.*, c1.name as sender_name, c2.name as receiver_name, p.name as player_name
                    FROM transfer t
                    JOIN club c1 ON t.sender_id = c1.club_id
                    JOIN club c2 ON t.receiver_id = c2.club_id
                    JOIN player p ON t.player_id = p.player_id
                    WHERE t.status = 'ACTIVE'
                """)
            return dictfetchall(cursor)
    
    @classmethod
    def create_offer(cls, sender_id, receiver_id, player_id, offer_amount):
        with connection.cursor() as cursor:
            try:
                cursor.execute(
                    """INSERT INTO transfer (sender_id, receiver_id, player_id, offer_amount, status) 
                       VALUES (%s, %s, %s, %s, 'ACTIVE')""",
                    [sender_id, receiver_id, player_id, offer_amount]
                )
                return True, "Transfer offer created successfully"
            except Exception as e:
                return False, str(e)
    
    @classmethod
    def accept_offer(cls, sender_id, receiver_id, player_id):
        with transaction.atomic():
            try:
                with connection.cursor() as cursor:
                    # 1. Get transfer details
                    cursor.execute(
                        """SELECT offer_amount FROM transfer 
                           WHERE sender_id = %s AND receiver_id = %s AND player_id = %s AND status = 'ACTIVE'""",
                        [sender_id, receiver_id, player_id]
                    )
                    result = cursor.fetchone()
                    if not result:
                        return False, "Transfer offer not found or not active"
                    
                    offer_amount = result[0]
                    
                    # 2. Update transfer status
                    cursor.execute(
                        """UPDATE transfer 
                           SET status = 'COMPLETED' 
                           WHERE sender_id = %s AND receiver_id = %s AND player_id = %s AND status = 'ACTIVE'""",
                        [sender_id, receiver_id, player_id]
                    )
                    
                    # 3. Update club budgets
                    cursor.execute(
                        "UPDATE club SET budget = budget - %s WHERE club_id = %s",
                        [offer_amount, sender_id]
                    )
                    
                    cursor.execute(
                        "UPDATE club SET budget = budget + %s WHERE club_id = %s",
                        [offer_amount, receiver_id]
                    )
                    
                    # 4. Update player's club
                    cursor.execute(
                        "UPDATE contracted_player SET club_id = %s WHERE player_id = %s",
                        [sender_id, player_id]
                    )
                    
                    return True, "Transfer completed successfully"
            except Exception as e:
                transaction.set_rollback(True)
                return False, str(e)
    
    @classmethod
    def reject_offer(cls, sender_id, receiver_id, player_id):
        with connection.cursor() as cursor:
            cursor.execute(
                """UPDATE transfer 
                   SET status = 'CANCELLED' 
                   WHERE sender_id = %s AND receiver_id = %s AND player_id = %s AND status = 'ACTIVE'""",
                [sender_id, receiver_id, player_id]
            )
            return cursor.rowcount > 0, "Transfer offer rejected"


class Match:
    @classmethod
    def get_all(cls):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT m.*, c1.name as home_team, c2.name as away_team
                FROM plays_match m
                JOIN club c1 ON m.home_id = c1.club_id
                JOIN club c2 ON m.away_id = c2.club_id
                ORDER BY m.match_date DESC, m.match_time DESC
            """)
            return dictfetchall(cursor)
    
    @classmethod
    def get_by_club(cls, club_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT m.*, c1.name as home_team, c2.name as away_team
                FROM plays_match m
                JOIN club c1 ON m.home_id = c1.club_id
                JOIN club c2 ON m.away_id = c2.club_id
                WHERE m.home_id = %s OR m.away_id = %s
                ORDER BY m.match_date DESC, m.match_time DESC
            """, [club_id, club_id])
            return dictfetchall(cursor)
    
    @classmethod
    def create(cls, home_id, away_id, match_date, match_time, home_goals=None, away_goals=None):
        with connection.cursor() as cursor:
            try:
                # Include home_goals and away_goals in the SQL query
                cursor.execute(
                    """INSERT INTO plays_match (home_id, away_id, match_date, match_time, home_goals, away_goals) 
                    VALUES (%s, %s, %s, %s, %s, %s)""",
                    [home_id, away_id, match_date, match_time, home_goals, away_goals]
                )
                
                # If scores are provided, update club statistics
                if home_goals is not None and away_goals is not None:
                    # Update home team stats
                    cursor.execute("""
                        UPDATE club
                        SET matches_played = matches_played + 1,
                            goal_difference = goal_difference + %s,
                            points = points + CASE 
                                WHEN %s > %s THEN 3
                                WHEN %s = %s THEN 1
                                ELSE 0
                            END
                        WHERE club_id = %s
                    """, [home_goals - away_goals, home_goals, away_goals, home_goals, away_goals, home_id])
                    
                    # Update away team stats
                    cursor.execute("""
                        UPDATE club
                        SET matches_played = matches_played + 1,
                            goal_difference = goal_difference + %s,
                            points = points + CASE 
                                WHEN %s < %s THEN 3
                                WHEN %s = %s THEN 1
                                ELSE 0
                            END
                        WHERE club_id = %s
                    """, [away_goals - home_goals, home_goals, away_goals, home_goals, away_goals, away_id])
                
                return True, "Match created successfully"
            except Exception as e:
                return False, str(e)
        
    @classmethod
    def record_result(cls, home_id, away_id, home_goals, away_goals):
        with transaction.atomic():
            try:
                with connection.cursor() as cursor:
                    # First check if match exists
                    cursor.execute(
                        "SELECT * FROM plays_match WHERE home_id = %s AND away_id = %s",
                        [home_id, away_id]
                    )
                    match = dictfetchone(cursor)
                    if not match:
                        return False, "Match not found"
                    
                    # Update match record
                    cursor.execute("""
                        UPDATE plays_match
                        SET home_goals = %s, away_goals = %s
                        WHERE home_id = %s AND away_id = %s
                    """, [home_goals, away_goals, home_id, away_id])
                    
                    if cursor.rowcount == 0:
                        return False, "Failed to update match"
                    
                    # Update club statistics
                    cursor.execute("""
                        UPDATE club
                        SET matches_played = matches_played + 1,
                            goal_difference = goal_difference + %s,
                            points = points + CASE 
                                WHEN %s > %s THEN 3
                                WHEN %s = %s THEN 1
                                ELSE 0
                            END
                        WHERE club_id = %s
                    """, [home_goals - away_goals, home_goals, away_goals, home_goals, away_goals, home_id])
                    
                    cursor.execute("""
                        UPDATE club
                        SET matches_played = matches_played + 1,
                            goal_difference = goal_difference + %s,
                            points = points + CASE 
                                WHEN %s < %s THEN 3
                                WHEN %s = %s THEN 1
                                ELSE 0
                            END
                        WHERE club_id = %s
                    """, [away_goals - home_goals, home_goals, away_goals, home_goals, away_goals, away_id])
                    
                    return True, "Match result recorded successfully"
            except Exception as e:
                transaction.set_rollback(True)
                print(f"Error in record_result: {e}")  # Add logging
                return False, str(e)


class Auction:
    @classmethod
    def get_all(cls):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT a.*, p.name as player_name, c.name as club_name
                FROM auction a
                JOIN free_agent fa ON a.player_id = fa.player_id
                JOIN player p ON fa.player_id = p.player_id
                JOIN club c ON a.club_id = c.club_id
                ORDER BY a.highest_bid DESC
            """)
            return dictfetchall(cursor)
    
    @classmethod
    def get_active(cls):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT a.*, p.name as player_name, c.name as club_name
                FROM auction a
                JOIN free_agent fa ON a.player_id = fa.player_id
                JOIN player p ON fa.player_id = p.player_id
                JOIN club c ON a.club_id = c.club_id
                WHERE a.status = 'ACTIVE'
                ORDER BY a.highest_bid DESC
            """)
            return dictfetchall(cursor)
    
    @classmethod
    def create(cls, player_id, club_id, highest_bid):
        with connection.cursor() as cursor:
            try:
                # Check if player is a free agent
                cursor.execute("SELECT player_id FROM free_agent WHERE player_id = %s", [player_id])
                if not cursor.fetchone():
                    return False, "Player is not a free agent"
                
                cursor.execute(
                    """INSERT INTO auction (player_id, club_id, highest_bid, status) 
                       VALUES (%s, %s, %s, 'ACTIVE')""",
                    [player_id, club_id, highest_bid]
                )
                return True, "Auction created successfully"
            except Exception as e:
                return False, str(e)
    
    @classmethod
    def place_bid(cls, player_id, club_id, bid_amount):
        with connection.cursor() as cursor:
            try:
                # Check if auction exists and is active
                cursor.execute(
                    "SELECT highest_bid FROM auction WHERE player_id = %s AND status = 'ACTIVE'",
                    [player_id]
                )
                result = cursor.fetchone()
                if not result:
                    return False, "No active auction found for this player"
                
                current_highest = result[0]
                if bid_amount <= current_highest:
                    return False, f"Bid must be higher than current highest bid ({current_highest})"
                
                # Update auction with new highest bid
                cursor.execute(
                    """UPDATE auction 
                       SET highest_bid = %s, club_id = %s 
                       WHERE player_id = %s AND status = 'ACTIVE'""",
                    [bid_amount, club_id, player_id]
                )
                return True, "Bid placed successfully"
            except Exception as e:
                return False, str(e)
    
    @classmethod
    def complete_auction(cls, player_id, club_id):
        with transaction.atomic():
            try:
                with connection.cursor() as cursor:
                    # Get auction details
                    cursor.execute(
                        """SELECT highest_bid FROM auction 
                        WHERE player_id = %s AND club_id = %s AND status = 'ACTIVE'""",
                        [player_id, club_id]
                    )
                    result = cursor.fetchone()
                    if not result:
                        return False, "Auction not found or not active"
                    
                    highest_bid = result[0]
                    
                    # Update auction status
                    cursor.execute(
                        """UPDATE auction 
                        SET status = 'COMPLETED' 
                        WHERE player_id = %s AND club_id = %s AND status = 'ACTIVE'""",
                        [player_id, club_id]
                    )
                    
                    # Update club budget
                    cursor.execute(
                        "UPDATE club SET budget = budget - %s WHERE club_id = %s",
                        [highest_bid, club_id]
                    )
                    
                    # Get a squad for the player
                    cursor.execute(
                        """SELECT squad_id FROM squad 
                        WHERE club_id = %s 
                        LIMIT 1""",
                        [club_id]
                    )
                    squad_result = cursor.fetchone()
                    if not squad_result:
                        # Create a first team squad if none exists
                        cursor.execute(
                            "INSERT INTO squad (club_id) VALUES (%s) RETURNING squad_id",
                            [club_id]
                        )
                        squad_id = cursor.fetchone()[0]
                        cursor.execute(
                            "INSERT INTO first_team (squad_id) VALUES (%s)",
                            [squad_id]
                        )
                    else:
                        squad_id = squad_result[0]
                    
                    # Remove from free_agent
                    cursor.execute("DELETE FROM free_agent WHERE player_id = %s", [player_id])
                    
                    # Add to contracted_player
                    cursor.execute(
                        """INSERT INTO contracted_player (player_id, jersey_number, club_id, squad_id) 
                        VALUES (%s, NULL, %s, %s)""",
                        [player_id, club_id, squad_id]
                    )
                    
                    return True, "Auction completed successfully"
            except Exception as e:
                transaction.set_rollback(True)
                return False, str(e)
    
    @classmethod
    def cancel_auction(cls, player_id):
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE auction SET status = 'CANCELLED' WHERE player_id = %s AND status = 'ACTIVE'",
                [player_id]
            )
            return cursor.rowcount > 0, "Auction cancelled successfully"
                