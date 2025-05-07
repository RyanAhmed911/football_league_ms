
create table player (
    player_id serial primary key,
    name varchar(100) not null,
    birthdate date,
    height float,
    nationality varchar(50),
    appearances integer default 0,
    saves integer default 0,
    goals integer default 0,
    assists integer default 0,
    position varchar(30)
);

create table club (
    club_id serial primary key,
    name varchar(100) not null,
    founded date,
    location varchar(100),
    stadium varchar(100),
    matches_played integer default 0,
    goal_difference integer default 0,
    points integer default 0,
    budget decimal(15, 2) default 0
);

create table coach (
    coach_id serial primary key,
    name varchar(100) not null,
    nationality varchar(50),
    club_id integer,
    foreign key (club_id) references club(club_id) on delete set null
);

create table squad (
    squad_id serial primary key,
    club_id integer not null,
    coach_id integer,
    foreign key (club_id) references club(club_id) on delete cascade,
    foreign key (coach_id) references coach(coach_id) on delete set null
);

create table first_team (
    squad_id integer primary key,
    foreign key (squad_id) references squad(squad_id) on delete cascade
);

create table youth_team (
    squad_id integer primary key,
    foreign key (squad_id) references squad(squad_id) on delete cascade
);

create table contracted_player (
    player_id integer primary key,
    jersey_number integer,
    club_id integer not null,
    squad_id integer not null,
    foreign key (player_id) references player(player_id) on delete cascade,
    foreign key (club_id) references club(club_id) on delete cascade,
    foreign key (squad_id) references squad(squad_id) on delete cascade
);

create table free_agent (
    player_id integer primary key,
    foreign key (player_id) references player(player_id) on delete cascade
);

create table sponsor (
    sponsor_id serial primary key,
    name varchar(100) not null,
    amount decimal(15, 2) not null,
    contract_length integer
);

create table sponsorship (
    club_id integer,
    sponsor_id integer,
    primary key (club_id, sponsor_id),
    foreign key (club_id) references club(club_id) on delete cascade,
    foreign key (sponsor_id) references sponsor(sponsor_id) on delete cascade
);

create table transfer (
    sender_id integer,
    receiver_id integer,
    player_id integer,
    status varchar(20) default 'ACTIVE' check (status in ('ACTIVE', 'COMPLETED', 'CANCELLED')),
    offer_amount decimal(15, 2),
    primary key (sender_id, receiver_id, player_id),
    foreign key (sender_id) references club(club_id) on delete cascade,
    foreign key (receiver_id) references club(club_id) on delete cascade,
    foreign key (player_id) references contracted_player(player_id) on delete cascade,
    check (sender_id != receiver_id)
);

create table plays_match (
    home_id integer,
    away_id integer,
    match_time time,
    match_date date,
    home_goals integer default 0,
    away_goals integer default 0,
    primary key (home_id, away_id),
    foreign key (home_id) references club(club_id) on delete cascade,
    foreign key (away_id) references club(club_id) on delete cascade,
    check (home_id != away_id)
);

create table auction (
    player_id integer,
    club_id integer,
    highest_bid decimal(15, 2) not null,
    status varchar(20) default 'ACTIVE' check (status in ('ACTIVE', 'COMPLETED', 'CANCELLED')),
    primary key (player_id, club_id),
    foreign key (player_id) references free_agent(player_id) on delete cascade,
    foreign key (club_id) references club(club_id) on delete cascade
);
