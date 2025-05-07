-- Insert clubs
INSERT INTO club (name, founded, location, stadium, budget) VALUES
('Manchester United', '1878-01-01', 'Manchester, England', 'Old Trafford', 200000000),
('Barcelona', '1899-11-29', 'Barcelona, Spain', 'Camp Nou', 180000000),
('Bayern Munich', '1900-02-27', 'Munich, Germany', 'Allianz Arena', 170000000),
('Liverpool', '1892-06-03', 'Liverpool, England', 'Anfield', 150000000);

-- Insert coaches
INSERT INTO coach (name, nationality, club_id) VALUES
('Erik ten Hag', 'Dutch', 1),
('Xavi', 'Spanish', 2),
('Thomas Tuchel', 'German', 3),
('Jurgen Klopp', 'German', 4);

-- Insert squads
INSERT INTO squad (club_id, coach_id) VALUES
(1, 1), -- Man Utd first team
(1, NULL), -- Man Utd youth team
(2, 2), -- Barcelona first team
(2, NULL), -- Barcelona youth team
(3, 3), -- Bayern first team
(4, 4); -- Liverpool first team

-- Designate first teams
INSERT INTO first_team (squad_id) VALUES (1), (3), (5), (6);

-- Designate youth teams
INSERT INTO youth_team (squad_id) VALUES (2), (4);

-- Insert players
INSERT INTO player (name, birthdate, height, nationality, position, goals, assists) VALUES
('Bruno Fernandes', '1994-09-08', 179, 'Portuguese', 'Midfielder', 15, 12),
('Marcus Rashford', '1997-10-31', 180, 'English', 'Forward', 18, 5),
('Robert Lewandowski', '1988-08-21', 185, 'Polish', 'Forward', 25, 3),
('Pedri', '2002-11-25', 174, 'Spanish', 'Midfielder', 8, 10),
('Joshua Kimmich', '1995-02-08', 177, 'German', 'Midfielder', 5, 15),
('Mohamed Salah', '1992-06-15', 175, 'Egyptian', 'Forward', 22, 8),
('Virgil van Dijk', '1991-07-08', 193, 'Dutch', 'Defender', 3, 1),
('Lionel Messi', '1987-06-24', 170, 'Argentine', 'Forward', 30, 20);

-- Contract players to clubs
INSERT INTO contracted_player (player_id, jersey_number, club_id, squad_id) VALUES
(1, 8, 1, 1), -- Bruno to Man Utd first team
(2, 10, 1, 1), -- Rashford to Man Utd first team
(3, 9, 2, 3), -- Lewandowski to Barcelona first team
(4, 16, 2, 3), -- Pedri to Barcelona first team
(5, 6, 3, 5), -- Kimmich to Bayern first team
(6, 11, 4, 6), -- Salah to Liverpool first team
(7, 4, 4, 6); -- Van Dijk to Liverpool first team

-- Add a free agent
INSERT INTO free_agent (player_id) VALUES (8); -- Messi is a free agent

-- Insert sponsors
INSERT INTO sponsor (name, amount, contract_length) VALUES
('Adidas', 50000000, 5),
('Nike', 45000000, 4),
('Puma', 30000000, 3),
('Emirates', 40000000, 5);

-- Create sponsorships
INSERT INTO sponsorship (club_id, sponsor_id) VALUES
(1, 1), -- Man Utd - Adidas
(2, 2), -- Barcelona - Nike
(3, 1), -- Bayern - Adidas
(4, 2); -- Liverpool - Nike

-- Create matches
INSERT INTO plays_match (home_id, away_id, match_date, match_time, home_goals, away_goals) VALUES
(1, 2, '2023-09-15', '20:00:00', 2, 1), -- Man Utd vs Barcelona
(3, 4, '2023-09-16', '19:30:00', 1, 1), -- Bayern vs Liverpool
(2, 3, '2023-09-20', '20:00:00', 0, 3), -- Barcelona vs Bayern
(4, 1, '2023-09-21', '20:00:00', 2, 2); -- Liverpool vs Man Utd

-- Create a transfer
INSERT INTO transfer (sender_id, receiver_id, player_id, status, offer_amount) VALUES
(1, 2, 3, 'ACTIVE', 80000000); -- Man Utd wants to buy Lewandowski from Barcelona

-- Create an auction
INSERT INTO auction (player_id, club_id, highest_bid, status) VALUES
(8, 1, 50000000, 'ACTIVE'); -- Man Utd bidding for Messi