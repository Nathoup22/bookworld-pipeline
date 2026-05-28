BEGIN TRANSACTION;
CREATE TABLE category_rules (
    category_name TEXT PRIMARY KEY,
    margin_rate REAL NOT NULL CHECK (margin_rate >= 0 AND margin_rate <= 1),
    strategic_flag INTEGER NOT NULL CHECK (strategic_flag IN (0,1)),
    default_channel_code TEXT NOT NULL,
    is_active INTEGER NOT NULL CHECK (is_active IN (0,1)),
    FOREIGN KEY (default_channel_code) REFERENCES channels(channel_code)
);
INSERT INTO "category_rules" VALUES('Travel',0.32,1,'WEB',1);
INSERT INTO "category_rules" VALUES('Mystery',0.28,1,'APP',1);
INSERT INTO "category_rules" VALUES('Historical Fiction',0.3,0,'WEB',1);
INSERT INTO "category_rules" VALUES('Classics',0.26,0,'WEB',1);
INSERT INTO "category_rules" VALUES('Romance',0.34,1,'APP',1);
INSERT INTO "category_rules" VALUES('Science Fiction',0.31,1,'APP',1);
INSERT INTO "category_rules" VALUES('Nonfiction',0.24,0,'WEB',1);
INSERT INTO "category_rules" VALUES('Business',0.36,1,'MKT',1);
INSERT INTO "category_rules" VALUES('Young Adult',0.29,1,'APP',1);
INSERT INTO "category_rules" VALUES('Horror',0.27,0,'MKT',0);
CREATE TABLE channels (
    channel_code TEXT PRIMARY KEY,
    channel_name TEXT NOT NULL,
    acquisition_cost_gbp REAL NOT NULL CHECK (acquisition_cost_gbp >= 0),
    channel_group TEXT NOT NULL,
    is_active INTEGER NOT NULL CHECK (is_active IN (0,1))
);
INSERT INTO "channels" VALUES('WEB','Website',2.5,'Owned',1);
INSERT INTO "channels" VALUES('APP','Mobile App',1.8,'Owned',1);
INSERT INTO "channels" VALUES('MKT','Marketplace',6.2,'Partner',1);
INSERT INTO "channels" VALUES('AFF','Affiliate Network',4.1,'Partner',0);
CREATE TABLE countries (
    country_code TEXT PRIMARY KEY CHECK (length(country_code) = 2),
    country_name TEXT NOT NULL,
    currency_code TEXT NOT NULL CHECK (length(currency_code) = 3),
    vat_rate REAL NOT NULL CHECK (vat_rate >= 0 AND vat_rate <= 100),
    region TEXT NOT NULL,
    is_active INTEGER NOT NULL CHECK (is_active IN (0,1))
);
INSERT INTO "countries" VALUES('FR','France','EUR',20.0,'Europe',1);
INSERT INTO "countries" VALUES('BE','Belgium','EUR',21.0,'Europe',1);
INSERT INTO "countries" VALUES('DE','Germany','EUR',19.0,'Europe',1);
INSERT INTO "countries" VALUES('ES','Spain','EUR',21.0,'Europe',1);
INSERT INTO "countries" VALUES('IT','Italy','EUR',22.0,'Europe',1);
INSERT INTO "countries" VALUES('PT','Portugal','EUR',23.0,'Europe',0);
INSERT INTO "countries" VALUES('GB','United Kingdom','GBP',20.0,'Europe',1);
INSERT INTO "countries" VALUES('IE','Ireland','EUR',23.0,'Europe',1);
INSERT INTO "countries" VALUES('US','United States','USD',0.0,'North America',1);
INSERT INTO "countries" VALUES('CA','Canada','CAD',5.0,'North America',0);
CREATE INDEX idx_countries_region_active ON countries(region, is_active);
CREATE INDEX idx_channels_group_active ON channels(channel_group, is_active);
CREATE INDEX idx_category_rules_channel_active ON category_rules(default_channel_code, is_active);
COMMIT;