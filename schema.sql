-- ── TABLES ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS meters (
    meter_id        TEXT PRIMARY KEY,
    building_name   TEXT NOT NULL,
    x_pos           NUMERIC(5,2) NOT NULL,  -- 0=left, 100=right
    y_pos           NUMERIC(5,2) NOT NULL,  -- 0=bottom, 100=top
    notes           TEXT
);

CREATE TABLE IF NOT EXISTS assignments (
    meter_id        TEXT NOT NULL REFERENCES meters(meter_id),
    scenario        TEXT NOT NULL,
    bus             TEXT NOT NULL,
    updated_at      TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (meter_id, scenario)
);

-- ── SEED: meter positions (x/y are approximate — adjust to fit) ──
INSERT INTO meters (meter_id, building_name, x_pos, y_pos) VALUES
-- MB1 column (far left)
('MB1A',  'Korean Studies',        7.5, 80),
('MB1E',  'Hale Laulima',          7.5, 72),
('MB1G',  'Arch Portables',        7.5, 64),
('MB1I',  'Hale Kahawai',          7.5, 56),
('MB1K',  'PMS Moore',             7.5, 50),
('MB1L',  'Moore Hall',            9.5, 45),
('MB1M',  'Aux Services',          7.5, 38),
('MB1N',  'St. John Lab',          7.5, 30),
('MB1O',  'PMS Pope',              7.5, 22),
('MB1R',  'Pope Lab',              9.5, 18),
('MB1S',  'Sherman Lab',           7.5, 12),
('MB1U',  'Paradise Palms',        7.5,  5),
-- MB2 column
('MB2A',  'Lincoln Hall',          15,  83),
('MB2B',  'Gilmore Hall',          15,  76),
('MB2C',  'AG Engineering',        15,  65),
('MB2E',  'Webster Hall',          15,  55),
('MB2F',  'Spalding Hall',         15,  45),
('MB2H',  'Hamilton Ph III',       15,  35),
('MB2J',  'PMS Bldg 37',           15,  26),
('MB2K',  'Snyder Hall',           15,  18),
('MB2L',  'Edmondson Hall',        15,  10),
-- MB3 column
('LB3B',  'HIG',                   23,  80),
('LB3C',  'IT Center',             23,  70),
('LB3D',  'Bilger Complex',        23,  60),
('LB3F',  'Art Bldg',              23,  51),
('LB3H',  'Sakamaki Hall',         23,  42),
('LB3J',  'Kuykendall Hall',       23,  34),
('LB3M',  'Bldg 37 (Radial Feed)', 23,  25),
('LB3N',  'Andrews Amph',          23,  17),
('LB3P',  'Krauss Hall',           23,  10),
('LB3Q',  'Campus Center',         23,   4),
-- MB4 column
('LB4A1', 'Campus Ctr AC',         34,  84),
('LB4B',  'Miller Hall',           34,  76),
('LB4D',  'Warrior Rec Ctr',       34,  68),
('LB4F',  'Dean Hall',             34,  60),
('LB4G1', 'Quad Chiller Plant',    34,  52),
('LB4I',  'Hawaii Hall',           34,  44),
('LB4J',  'QLC',                   34,  36),
('LB4L',  'Saunders Hall',         34,  28),
('LB4N',  'Shidler Coba',          34,  20),
('LB4P1', 'George Hall',           34,  13),
('LB4R',  'Crawford Hall',         34,   7),
('LB4S',  'Admin Svcs 1',          34,   2),
('LB4W',  'Hemenway Hall',         34,  -3),
-- LB5/MB5 column
('LB5B',  'PMS L / LB5B',          48,  78),
('LB5D',  'Parking Struct I',       48,  65),
('LB5F',  'HPCR PEA',              48,  54),
('LB5I',  'Parking Struct II',      48,  44),
('LB5J1', 'Tennis Courts',          48,  34),
('LB5J',  'Music Building',         48,  25),
('LB5J2', 'Parking Structure PV',   52,  18),
('LB5K',  'TC Ching Complex',       52,  11),
('LB5L',  'LMS Baseball',           52,   5),
('LB5M',  'DK Swimming Pool',       52,  -1),
-- RB / center column
('RB5A',  'Johnson Hall',           58,  65),
('RB5C',  'Gateway House',          58,  54),
('RB5G',  'Law Library',            58,  43),
('RB5G1', 'Law School',             58,  32),
('RB5F',  'Frear Hall',             63,  57),
('LA5E',  'Lehua',                  63,  46),
('LA5F',  'Ilima',                  63,  36),
('LA5G',  'Mokihana',               63,  26),
('LA5K',  'Lokelani',               63,  16),
('LA5L',  'Hale Noelani',           63,   8),
('LA5M',  'Hale Wainani',           63,   2),
-- MA4/LA4 column
('LA4C',  'Wist & Everly Hall',     68,  80),
('LA4E',  'UHS 3',                  68,  70),
('LA4F',  'Wist Annex Radial',      68,  58),
('LA4I',  'Multi-Purpose Bldg',     68,  46),
('LA4J',  'Sinclair Library',       68,  35),
('LA4L',  'Architecture',           68,  24),
('LA4Q',  'Gartley',                68,  15),
('LA4R',  'Admin Svcs 2',           68,   6),
-- MA3/LA3 column
('LA3B',  'PMS H',                  75,  88),
('LA3C',  'Holmes Hall',            75,  79),
('LA3D',  'Post Central Plant',     75,  66),
('LA3F',  'Post Building',          75,  54),
('LA3I',  'Marine Science',         75,  42),
('LA3M',  'Life Science Bldg',      75,  31),
('LA3N',  'University Health Svcs', 75,  21),
('LA3P',  'Kennedy Theater',        75,  12),
('LA3S',  'Watanabe Hall',          75,   4),
-- MA2/LA2 column
('MA2B',  'John Burns Hall',        84,  83),
('MA2D',  'Hale Manoa',             84,  68),
('MA2E',  'Jefferson Hall',         84,  52),
('MA2F',  'PMS AS',                 84,  43),
('MA2N',  'Keller Hall',            84,  30),
('MA2O',  'Physical Science',       84,  18),
('MA2R',  'Hamilton Library',       84,   6),
-- MA1/LA1 column (far right)
('MA1B',  'Biomed Bldg',            93,  83),
('MA1C',  'Bio-Genesis',            93,  70),
('MA1E',  'AG Science',             93,  57),
('MA1H',  'Facilities',             93,  44),
('MA1I',  'Maintenance',            93,  30),
('MA1K',  'C-More Hale',            93,  14)
ON CONFLICT (meter_id) DO NOTHING;

-- ── SEED: default assignments for one scenario ─────────────────
INSERT INTO assignments (meter_id, scenario, bus)
SELECT
    meter_id,
    '2026_04_23',
    CASE
        WHEN meter_id LIKE 'MB%' THEN 'MB'
        WHEN meter_id LIKE 'MA%' THEN 'MA'
        WHEN meter_id LIKE 'LB%' THEN 'LB'
        WHEN meter_id LIKE 'LA%' THEN 'LA'
        WHEN meter_id LIKE 'LC%' THEN 'LC'
        ELSE 'Null'
    END
FROM meters
ON CONFLICT DO NOTHING;