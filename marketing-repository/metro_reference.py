"""US metro marketing-market reference for the 42 metros in the OOH dataset.

Combines:
  * the scraped billboard/OOH data (companies, rate bands, per-metro coverage)
    imported live from ../florida-billboard-scraper/fbscraper/national.py, and
  * per-metro marketing-market facts below: Nielsen DMA rank (2024-25, approx),
    metro (MSA) population, dominant daily newspaper, and city business journal.

DMA ranks and populations are stable public reference figures (Nielsen 2024-25;
Census MSA estimates 2024) and are marked approximate. Newspapers / business
journals are the primary print advertising venues per market.
"""
from __future__ import annotations

import sys
import os

# Import the billboard dataset from the sibling project.
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "..", "florida-billboard-scraper"))
import fbscraper.national as nat  # noqa: E402
from fbscraper import seed as fl_seed  # noqa: E402  (Palm Beach / Florida operators)


# ---------------------------------------------------------------------------
# Palm Beach County — the HOME market (rank 0, listed first in every metro sheet)
# ---------------------------------------------------------------------------
PBC_METRO = "Palm Beach County ★"
PBC_FACTS = {
    "dma": 38,                       # West Palm Beach–Ft. Pierce DMA (approx)
    "pop": "1.5M",
    "rate": "$800-$15,000",          # static; digital runs to ~$25k (FL market avg)
    "paper": "The Palm Beach Post",
    "bizj": "South Florida Business Journal",
    "tv": "WPBF 25 · WPEC 12 · WPTV 5 · WFLX Fox 29",
    "radio": "Hubbard (WRMF, WIRK) · iHeart (WJNO)",
    "agencies": "The O'Donnell Agency (PR); in-house/AI is the edge — see PBC Playbook",
    "events": "SunFest · South Florida Fair · Palm Beach Intl Boat Show · "
              "spring training (Ballpark of the Palm Beaches, Roger Dean)",
    "chamber": "Chamber of Commerce of the Palm Beaches · Palm Beach North Chamber",
    "note": "HOME MARKET. 17 verified PBC OOH operators with contacts in the Florida "
            "billboard workbook (florida-billboard-scraper).",
    "spanish": "Miami Spanish media covers PBC: WLTV Univision 23 · WSCV Telemundo 51 · SBS radio",
}


def _pbc_companies():
    return [c for c in fl_seed.load_seed()
            if (c.serves_palm_beach or "").lower() == "yes"]


def _pbc_ooh_contacts(limit=4):
    conf_rank = {"High": 0, "Medium": 1, "Low": 2}
    comps = sorted(_pbc_companies(),
                   key=lambda c: (conf_rank.get(c.confidence, 3), c.company_name.lower()))
    parts = []
    for c in comps[:limit]:
        parts.append(f"{c.company_name}{' ' + c.phone if c.phone else ''}".strip())
    return "; ".join(parts) + f" — {len(comps)} PBC operators in the Florida workbook"

# Metro -> (DMA rank approx, MSA population, major daily newspaper, business journal)
METRO_MEDIA = {
    "New York":       (1,  "19.9M", "The New York Times / NY Post / Daily News", "Crain's New York Business"),
    "Los Angeles":    (2,  "13.0M", "Los Angeles Times", "Los Angeles Business Journal"),
    "Chicago":        (3,  "9.4M",  "Chicago Tribune / Sun-Times", "Crain's Chicago Business"),
    "San Francisco":  (10, "4.6M (Bay CSA ~9.7M)", "San Francisco Chronicle", "San Francisco Business Times"),
    "Atlanta":        (6,  "6.4M",  "The Atlanta Journal-Constitution", "Atlanta Business Chronicle"),
    "Washington DC":  (8,  "6.3M",  "The Washington Post", "Washington Business Journal"),
    "Boston":         (9,  "4.9M",  "The Boston Globe", "Boston Business Journal"),
    "Dallas":         (4,  "8.1M",  "The Dallas Morning News", "Dallas Business Journal"),
    "Houston":        (7,  "7.5M",  "Houston Chronicle", "Houston Business Journal"),
    "Miami":          (18, "6.2M",  "Miami Herald", "South Florida Business Journal"),
    "Philadelphia":   (5,  "6.2M",  "The Philadelphia Inquirer", "Philadelphia Business Journal"),
    "Detroit":        (15, "4.3M",  "Detroit Free Press / The Detroit News", "Crain's Detroit Business"),
    "Seattle":        (12, "4.0M",  "The Seattle Times", "Puget Sound Business Journal"),
    "Minneapolis":    (14, "3.7M",  "Star Tribune", "Minneapolis/St. Paul Business Journal"),
    "Phoenix":        (11, "5.1M",  "The Arizona Republic", "Phoenix Business Journal"),
    "Tampa":          (13, "3.3M",  "Tampa Bay Times", "Tampa Bay Business Journal"),
    "Denver":         (16, "3.0M",  "The Denver Post", "Denver Business Journal"),
    "Cleveland":      (19, "2.2M",  "The Plain Dealer / cleveland.com", "Crain's Cleveland Business"),
    "Sacramento":     (20, "2.4M",  "The Sacramento Bee", "Sacramento Business Journal"),
    "Orlando":        (17, "2.8M",  "Orlando Sentinel", "Orlando Business Journal"),
    "St. Louis":      (24, "2.8M",  "St. Louis Post-Dispatch", "St. Louis Business Journal"),
    "Pittsburgh":     (26, "2.4M",  "Pittsburgh Post-Gazette", "Pittsburgh Business Times"),
    "San Diego":      (29, "3.3M",  "The San Diego Union-Tribune", "San Diego Business Journal"),
    "Baltimore":      (28, "2.8M",  "The Baltimore Sun", "Baltimore Business Journal"),
    "Charlotte":      (21, "2.8M",  "The Charlotte Observer", "Charlotte Business Journal"),
    "Raleigh":        (23, "1.5M (Triangle ~2.1M)", "The News & Observer", "Triangle Business Journal"),
    "Indianapolis":   (25, "2.1M",  "The Indianapolis Star", "Indianapolis Business Journal"),
    "Cincinnati":     (35, "2.3M",  "The Cincinnati Enquirer", "Cincinnati Business Courier"),
    "Las Vegas":      (40, "2.3M",  "Las Vegas Review-Journal", "Vegas Inc / LVRJ Business Press"),
    "San Antonio":    (31, "2.6M",  "San Antonio Express-News", "San Antonio Business Journal"),
    "Portland":       (22, "2.5M",  "The Oregonian", "Portland Business Journal"),
    "Milwaukee":      (36, "1.6M",  "Milwaukee Journal Sentinel", "Milwaukee Business Journal"),
    "Columbus":       (32, "2.2M",  "The Columbus Dispatch", "Columbus Business First"),
    "Kansas City":    (34, "2.2M",  "The Kansas City Star", "Kansas City Business Journal"),
    "Nashville":      (27, "2.1M",  "The Tennessean", "Nashville Business Journal"),
    "Salt Lake City": (30, "1.3M",  "The Salt Lake Tribune / Deseret News", "Utah Business"),
    "New Orleans":    (50, "1.3M",  "The Times-Picayune / NOLA.com / The Advocate", "New Orleans CityBusiness"),
    "Oklahoma City":  (42, "1.5M",  "The Oklahoman", "The Journal Record"),
    "Memphis":        (46, "1.3M",  "The Commercial Appeal", "Memphis Business Journal"),
    "Richmond":       (56, "1.3M",  "Richmond Times-Dispatch", "Richmond BizSense"),
    "Austin":         (37, "2.5M",  "Austin American-Statesman", "Austin Business Journal"),
    "Jacksonville":   (45, "1.7M",  "The Florida Times-Union", "Jacksonville Business Journal"),
}


# Metro -> (Big-4 TV affiliates, major radio groups, notable ad agencies HQ'd/active in market)
# TV call signs are stable; radio listed at ownership-group level (station-level churns);
# agencies are flagship shops known for the market. All reference-level, verify before buying.
METRO_BROADCAST = {
    "New York":       ("WABC 7 · WCBS 2 · WNBC 4 · WNYW Fox 5",
                       "Audacy (WFAN, 1010 WINS) · iHeart (Z100) · SBS (Spanish, HQ)",
                       "Ogilvy, BBDO, Droga5, McCann (global HQs)"),
    "Los Angeles":    ("KABC 7 · KCBS 2 · KNBC 4 · KTTV Fox 11",
                       "iHeart (KIIS, KFI) · Audacy (KROQ, KNX) · Univision/SBS (Spanish)",
                       "Deutsch LA, 72andSunny, TBWA\\Chiat\\Day"),
    "Chicago":        ("WLS 7 · WBBM 2 · WMAQ 5 · WFLD Fox 32",
                       "Audacy (WBBM, WSCR) · iHeart · Nexstar (WGN Radio)",
                       "Leo Burnett, FCB Chicago, Energy BBDO"),
    "San Francisco":  ("KGO 7 · KPIX 5 · KNTV 11 · KTVU Fox 2",
                       "Audacy (KCBS) · iHeart · Bonneville",
                       "Goodby Silverstein, Duncan Channon, Argonaut"),
    "Atlanta":        ("WSB 2 · WANF 46 · WXIA 11 · WAGA Fox 5",
                       "Cox Media Group (HQ, WSB) · iHeart · Urban One",
                       "22squared, Dagger, Chemistry"),
    "Washington DC":  ("WJLA 7 · WUSA 9 · WRC 4 · WTTG Fox 5",
                       "Hubbard (WTOP — top-billing US station) · iHeart · Cumulus (WMAL)",
                       "GMMB (political), RP3 Agency"),
    "Boston":         ("WCVB 5 · WBZ 4 · WBTS 10 · WFXT Fox 25",
                       "iHeart (WBZ-AM) · Audacy (WEEI) · Beasley",
                       "Hill Holliday, Arnold, MullenLowe, Allen & Gerritsen"),
    "Dallas":         ("WFAA 8 · KTVT 11 · KXAS 5 · KDFW Fox 4",
                       "iHeart · Audacy (KRLD) · Cumulus (WBAP)",
                       "TRG (The Richards Group), Dieste (Hispanic)"),
    "Houston":        ("KTRK 13 · KHOU 11 · KPRC 2 · KRIV Fox 26",
                       "iHeart (KTRH) · Audacy · Cox (KKBQ)",
                       "Lopez Negrete (Hispanic), MMI Agency"),
    "Miami":          ("WPLG 10 · WFOR 4 · WTVJ 6 · WSVN Fox 7",
                       "iHeart · Cox · SBS (Spanish broadcasting HQ)",
                       "Zimmerman, Crispin (legacy), República Havas (Hispanic)"),
    "Philadelphia":   ("WPVI 6 · KYW 3 · WCAU 10 · WTXF Fox 29",
                       "Audacy (HQ — KYW, WIP) · iHeart · Beasley (WMMR)",
                       "Digitas Philly (legacy), Brownstein Group, LevLane"),
    "Detroit":        ("WXYZ 7 · WWJ 62 · WDIV 4 · WJBK Fox 2",
                       "Audacy (WWJ, WXYT) · iHeart · Cumulus (WJR)",
                       "Doner, Campbell Ewald, Lafayette American"),
    "Seattle":        ("KOMO 4 · KIRO 7 · KING 5 · KCPQ Fox 13",
                       "Bonneville (KIRO) · iHeart · Audacy",
                       "Wongdoody, Copacino Fujikado, DNA"),
    "Minneapolis":    ("KSTP 5 · WCCO 4 · KARE 11 · KMSP Fox 9",
                       "Hubbard (HQ — KSTP, KS95) · iHeart (KFAN) · Audacy (WCCO)",
                       "Fallon, Colle McVoy, Periscope"),
    "Phoenix":        ("KNXV 15 · KPHO 5 · KPNX 12 · KSAZ Fox 10",
                       "Bonneville (KTAR) · iHeart · Hubbard",
                       "OH Partners, LaneTerralever, Zion & Zion"),
    "Tampa":          ("WFTS 28 · WTSP 10 · WFLA 8 · WTVT Fox 13",
                       "iHeart (WFLA-AM) · Cox · Beasley (WQYK)",
                       "PPK, Schifino Lee"),
    "Denver":         ("KMGH 7 · KCNC 4 · KUSA 9 · KDVR Fox 31",
                       "iHeart (KOA) · Bonneville (KYGO/KOSI) · Audacy",
                       "Karsh Hagan, Cactus, Grit Advertising"),
    "Cleveland":      ("WEWS 5 · WOIO 19 · WKYC 3 · WJW Fox 8",
                       "iHeart (WTAM) · Audacy · Good Karma (WKNR)",
                       "Marcus Thomas, Adcom, Falls"),
    "Sacramento":     ("KXTV 10 · KOVR 13 · KCRA 3 · KTXL Fox 40",
                       "iHeart (KFBK) · Audacy · Bonneville",
                       "The Glass Agency, Position Interactive"),
    "Orlando":        ("WFTV 9 · WKMG 6 · WESH 2 · WOFL Fox 35",
                       "iHeart · Cox (WDBO)",
                       "&Barr, PUSH"),
    "St. Louis":      ("KDNL 30 · KMOV 4 · KSDK 5 · KTVI Fox 2",
                       "Audacy (KMOX) · iHeart · Hubbard",
                       "HLK, Rodgers Townsend (DDB)"),
    "Pittsburgh":     ("WTAE 4 · KDKA 2 · WPXI 11 · WPGH Fox 53",
                       "Audacy (KDKA) · iHeart (WDVE) · Steel City Media",
                       "Brunner, MARC USA (legacy), Gatesman"),
    "San Diego":      ("KGTV 10 · KFMB 8 · KNSD 7/39 · KSWB Fox 5",
                       "iHeart (KOGO) · Audacy · Local Media San Diego",
                       "VITRO (Petco work), i.d.e.a."),
    "Baltimore":      ("WMAR 2 · WJZ 13 · WBAL 11 · WBFF Fox 45",
                       "Hearst (WBAL radio) · iHeart · Audacy",
                       "Planit, GKV, idfive"),
    "Charlotte":      ("WSOC 9 · WBTV 3 · WCNC 36 · WJZY Fox 46",
                       "iHeart · Urban One · Norsan Media (Spanish, local)",
                       "Wray Ward, Luquire"),
    "Raleigh":        ("WTVD 11 · WNCN 17 · WRAL 5 · WRAZ Fox 50",
                       "iHeart · Curtis Media (local Triangle) · Capitol Broadcasting",
                       "McKinney (Durham), Baldwin&"),
    "Indianapolis":   ("WRTV 6 · WTTV 4 · WTHR 13 · WXIN Fox 59",
                       "iHeart · Cumulus (WFMS) · Urban One",
                       "Young & Laramore, Hirons"),
    "Cincinnati":     ("WCPO 9 · WKRC 12 · WLWT 5 · WXIX Fox 19",
                       "iHeart (700WLW) · Hubbard (WKRQ) · Cumulus",
                       "Curiosity, Barefoot Proximity (BBDO)"),
    "Las Vegas":      ("KTNV 13 · KLAS 8 · KSNV 3 · KVVU Fox 5",
                       "Audacy · iHeart · Lotus (local)",
                       "R&R Partners ('What happens here, stays here')"),
    "San Antonio":    ("KSAT 12 · KENS 5 · WOAI 4 · KABB Fox 29",
                       "iHeartMedia (corporate HQ — WOAI) · Cox · Univision (Spanish)",
                       "The Atkins Group, Giles-Parscale (legacy)"),
    "Portland":       ("KATU 2 · KOIN 6 · KGW 8 · KPTV Fox 12",
                       "iHeart (KEX) · Audacy · Alpha Media (HQ Portland)",
                       "Wieden+Kennedy (HQ), Instrument, Opinionated"),
    "Milwaukee":      ("WISN 12 · WDJT 58 · WTMJ 4 · WITI Fox 6",
                       "Good Karma (WTMJ radio) · iHeart · Saga (WKLH)",
                       "Cramer-Krasselt, BVK, Hoffman York"),
    "Columbus":       ("WSYX 6 · WBNS 10 · WCMH 4 · WTTE Fox 28",
                       "iHeart (WTVN/WNCI) · Saga (WSNY) · Urban One",
                       "Fahlgren Mortine, The Shipyard, Ologie"),
    "Kansas City":    ("KMBC 9 · KCTV 5 · KSHB 41 · WDAF Fox 4",
                       "Audacy (KMBZ) · Cumulus · Carter Broadcast (KPRS)",
                       "VML (HQ), Barkley OKRP"),
    "Nashville":      ("WKRN 2 · WTVF 5 · WSMV 4 · WZTV Fox 17",
                       "iHeart (WLAC) · Cumulus (WKDF/WSM-FM) · Opry Ent. (WSM-AM)",
                       "bohan, GS&F"),
    "Salt Lake City": ("KTVX 4 · KUTV 2 · KSL 5 · KSTU Fox 13",
                       "Bonneville (HQ — KSL) · iHeart · Broadway Media (local)",
                       "Struck, Love Communications, Richter7"),
    "New Orleans":    ("WGNO 26 · WWL 4 · WDSU 6 · WVUE Fox 8",
                       "Audacy (WWL radio) · iHeart · Cumulus",
                       "Peter Mayer, Trumpet"),
    "Oklahoma City":  ("KOCO 5 · KWTV 9 · KFOR 4 · KOKH Fox 25",
                       "iHeart (KTOK) · Cumulus (KATT) · Tyler Media (local)",
                       "Ackerman McQueen, VI Marketing + Branding"),
    "Memphis":        ("WATN 24 · WREG 3 · WMC 5 · WHBQ Fox 13",
                       "iHeart · Cumulus · Flinn Broadcasting (local)",
                       "archer malmo (Signet), Sullivan Branding"),
    "Richmond":       ("WRIC 8 · WTVR 6 · WWBT 12 · WRLH Fox 35",
                       "Audacy (WRVA) · SummitMedia · Urban One",
                       "The Martin Agency (GEICO), Arts & Letters"),
    "Austin":         ("KVUE 24 · KEYE 42 · KXAN 36 · KTBC Fox 7",
                       "iHeart · Audacy · Waterloo Media (local — KLBJ)",
                       "GSD&M (HQ), McGarrah Jessee, Preacher"),
    "Jacksonville":   ("WJXX 25 · WJAX 47 · WTLV 12 · WFOX 30",
                       "Cox (WOKV/WAPE) · iHeart",
                       "Dalton Agency, Shepherd (St. John & Partners)"),
}


def metro_reference_rows():
    """Return list of dict rows for the US Metro Reference sheet (market-size order)."""
    comps = nat.load_national()
    rate = {c: (lo, hi, tier, note) for (r, c, st, tier, lo, hi, note) in
            [(r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in nat.CITY_MARKET]}
    state = {r[1]: r[2] for r in nat.CITY_MARKET}
    rows = [{
        "rank": 0, "metro": PBC_METRO, "state": "FL",
        "dma": PBC_FACTS["dma"], "pop": PBC_FACTS["pop"], "rate": PBC_FACTS["rate"],
        "ops": len(_pbc_companies()), "paper": PBC_FACTS["paper"],
        "bizj": PBC_FACTS["bizj"], "tv": PBC_FACTS["tv"], "radio": PBC_FACTS["radio"],
        "agencies": PBC_FACTS["agencies"], "note": PBC_FACTS["note"],
        "spanish": PBC_FACTS["spanish"],
    }]
    for i, city in enumerate(nat.TOP_CITIES, 1):
        lo, hi, tier, note = rate[city]
        n_ops = sum(1 for c in comps if city in nat.cities_for(c))
        dma, pop, paper, bizj = METRO_MEDIA.get(city, ("-", "-", "-", "-"))
        tv, radio, agencies = METRO_BROADCAST.get(city, ("-", "-", "-"))
        rows.append({
            "rank": i,
            "metro": city,
            "state": state.get(city, ""),
            "dma": dma,
            "pop": pop,
            "rate": f"${lo:,}-${hi:,}",
            "ops": n_ops,
            "paper": paper,
            "bizj": bizj,
            "tv": tv,
            "radio": radio,
            "agencies": agencies,
            "note": note,
            "spanish": METRO_SPANISH.get(city, "-"),
        })
    return rows


# Metro -> Spanish-language media (Univision/Telemundo affiliates + Latino radio).
# 'Limited' = no major OTA affiliate; reach via cable/streaming + local Latino radio.
METRO_SPANISH = {
    "New York":       "WXTV Univision 41 · WNJU Telemundo 47 · SBS radio (Mega 97.9)",
    "Los Angeles":    "KMEX Univision 34 (top US Spanish station) · KVEA Telemundo 52 · Uforia/SBS radio",
    "Chicago":        "WGBO Univision 66 · WSNS Telemundo 44 · SBS radio",
    "San Francisco":  "KDTV Univision 14 · KSTS Telemundo 48",
    "Atlanta":        "WUVG Univision 34 · WKTB Telemundo Atlanta",
    "Washington DC":  "WFDC Univision 14 · WZDC Telemundo 44",
    "Boston":         "WUNI Univision 27 · WNEU Telemundo 60",
    "Dallas":         "KUVN Univision 23 · KXTX Telemundo 39 · Uforia radio",
    "Houston":        "KXLN Univision 45 · KTMD Telemundo 47 · Uforia radio",
    "Miami":          "WLTV Univision 23 · WSCV Telemundo 51 (Telemundo HQ) · SBS radio HQ",
    "Philadelphia":   "WUVP Univision 65 · WWSI Telemundo 62",
    "Detroit":        "Limited — cable/streaming + local Latino radio",
    "Seattle":        "KUNS Univision 51",
    "Minneapolis":    "Limited — WUMN Univision (LP) + cable/streaming",
    "Phoenix":        "KTVW Univision 33 · KTAZ Telemundo 39 · Uforia radio",
    "Tampa":          "WVEA Univision 62 · WRMD Telemundo 49",
    "Denver":         "KCEC Univision 50 · KDEN Telemundo 25",
    "Cleveland":      "Limited — cable/streaming",
    "Sacramento":     "KUVS Univision 19 · KCSO Telemundo 33",
    "Orlando":        "WVEN Univision 26 · WTMO Telemundo 31",
    "St. Louis":      "Limited — cable/streaming",
    "Pittsburgh":     "Limited — cable/streaming",
    "San Diego":      "KBNT Univision 17 · KUAN Telemundo 48 (+ Tijuana border stations)",
    "Baltimore":      "DC stations spill (WFDC Univision / WZDC Telemundo)",
    "Charlotte":      "Norsan Media (local Spanish radio) · cable/streaming",
    "Raleigh":        "La Ley radio (Norsan) · cable/streaming",
    "Indianapolis":   "Limited — cable + local Latino radio",
    "Cincinnati":     "Limited — cable/streaming",
    "Las Vegas":      "KINC Univision 15 · KBLR Telemundo 39",
    "San Antonio":    "KWEX Univision 41 (first US Spanish-language TV station) · KVDA Telemundo 60 · Uforia",
    "Portland":       "KUNP Univision 16",
    "Milwaukee":      "WYTU Telemundo 63",
    "Columbus":       "Limited — cable/streaming",
    "Kansas City":    "KUKC Univision 20",
    "Nashville":      "Limited — local Latino radio + cable",
    "Salt Lake City": "KUTH Univision 32",
    "New Orleans":    "Limited — cable + local Latino radio",
    "Oklahoma City":  "KUOK Univision 36",
    "Memphis":        "Limited — cable/streaming",
    "Richmond":       "Limited — cable/streaming",
    "Austin":         "KAKW Univision 62 · Telemundo Austin",
    "Jacksonville":   "Limited — cable/streaming + local Latino radio",
}


# Metro -> (marquee events/fairs/sports sponsorship properties, chamber of commerce)
# Stable public reference facts; verify current sponsorship contacts before buying.
METRO_CIVIC = {
    "New York":       ("Yankees/Mets/Knicks/Giants + US Open; marquee street-fair circuit", "Partnership for New York City"),
    "Los Angeles":    ("Dodgers/Lakers/Rams; LA County Fair (Pomona); LA Auto Show", "Los Angeles Area Chamber"),
    "Chicago":        ("Cubs/White Sox/Bulls/Bears; Taste of Chicago; McCormick Place shows", "Chicagoland Chamber"),
    "San Francisco":  ("Giants/Warriors/49ers; Bay to Breakers; Moscone trade shows", "SF Chamber of Commerce"),
    "Atlanta":        ("Braves/Falcons/Hawks; Atlanta Home Show", "Metro Atlanta Chamber"),
    "Washington DC":  ("Commanders/Nationals/Capitals/Wizards", "DC Chamber of Commerce"),
    "Boston":         ("Red Sox/Celtics/Bruins/Patriots; Boston Marathon", "Greater Boston Chamber"),
    "Dallas":         ("Cowboys/Mavericks/Rangers/Stars; State Fair of Texas (largest US fair)", "Dallas Regional Chamber"),
    "Houston":        ("Texans/Astros/Rockets; Houston Livestock Show & Rodeo (massive)", "Greater Houston Partnership"),
    "Miami":          ("Dolphins/Heat/Marlins; Miami-Dade Youth Fair; Miami Home Design & Remodeling Show; Art Basel", "Greater Miami Chamber"),
    "Philadelphia":   ("Eagles/Phillies/76ers/Flyers; Philly Home + Garden Show", "Chamber of Commerce for Greater Philadelphia"),
    "Detroit":        ("Lions/Tigers/Pistons/Red Wings; Detroit Auto Show", "Detroit Regional Chamber"),
    "Seattle":        ("Seahawks/Mariners/Kraken; Washington State Fair (Puyallup); Seattle Home & Garden Show", "Seattle Metro Chamber"),
    "Minneapolis":    ("Vikings/Twins/Timberwolves/Wild; Minnesota State Fair (top US daily attendance)", "Minneapolis Regional Chamber"),
    "Phoenix":        ("Cardinals/Suns/Diamondbacks; Arizona State Fair; WM Phoenix Open; Barrett-Jackson", "Greater Phoenix Chamber"),
    "Tampa":          ("Buccaneers/Lightning/Rays; Florida State Fair; Gasparilla", "Tampa Bay Chamber"),
    "Denver":         ("Broncos/Nuggets/Rockies/Avalanche; National Western Stock Show; Colorado Garden & Home Show", "Denver Metro Chamber"),
    "Cleveland":      ("Browns/Guardians/Cavaliers; Great Big Home + Garden Show (IX Center)", "Greater Cleveland Partnership"),
    "Sacramento":     ("Kings; California State Fair (Cal Expo)", "Sacramento Metro Chamber"),
    "Orlando":        ("Magic/Orlando City; Central Florida Fair; theme-park co-marketing", "Orlando Economic Partnership"),
    "St. Louis":      ("Cardinals/Blues; St. Louis Home + Garden Show", "Greater St. Louis Inc."),
    "Pittsburgh":     ("Steelers/Penguins/Pirates; Duquesne Light Home & Garden Show", "Allegheny Conference / Pittsburgh Chamber"),
    "San Diego":      ("Padres; San Diego County Fair (Del Mar); Comic-Con", "San Diego Regional Chamber"),
    "Baltimore":      ("Ravens/Orioles; Maryland State Fair (Timonium); Preakness Stakes", "Greater Baltimore Committee"),
    "Charlotte":      ("Panthers/Hornets; Charlotte Motor Speedway (NASCAR); Southern Spring Home & Garden Show", "Charlotte Regional Business Alliance"),
    "Raleigh":        ("Hurricanes; NC State Fair (huge); Southern Ideal Home Show", "Raleigh Chamber"),
    "Indianapolis":   ("Colts/Pacers; Indy 500; Indiana State Fair; Indianapolis Home Show", "Indy Chamber"),
    "Cincinnati":     ("Bengals/Reds; Cincinnati Home & Garden Show; Oktoberfest Zinzinnati", "Cincinnati USA Regional Chamber"),
    "Las Vegas":      ("Raiders/Golden Knights/Aces; CES + trade-show circuit; F1 Las Vegas GP", "Vegas Chamber"),
    "San Antonio":    ("Spurs; Fiesta San Antonio; SA Stock Show & Rodeo", "San Antonio Chamber"),
    "Portland":       ("Trail Blazers/Timbers; Portland Rose Festival; Portland Spring Home & Garden Show", "Portland Metro Chamber"),
    "Milwaukee":      ("Bucks/Brewers; Summerfest (world's largest music fest); Wisconsin State Fair", "Metropolitan Milwaukee Assoc. of Commerce"),
    "Columbus":       ("Blue Jackets/Crew + Ohio State athletics; Ohio State Fair; Dispatch Home & Garden Show", "Columbus Chamber"),
    "Kansas City":    ("Chiefs/Royals; American Royal; Johnson County Home + Garden Show", "KC Chamber"),
    "Nashville":      ("Titans/Predators; CMA Fest; Nashville Home + Remodeling Expo", "Nashville Area Chamber"),
    "Salt Lake City": ("Jazz; Utah State Fair; Silicon Slopes events", "Salt Lake Chamber"),
    "New Orleans":    ("Saints/Pelicans; Mardi Gras + Jazz Fest sponsorships", "New Orleans Chamber"),
    "Oklahoma City":  ("Thunder; Oklahoma State Fair", "Greater OKC Chamber"),
    "Memphis":        ("Grizzlies; Memphis in May / Beale Street Music Festival", "Greater Memphis Chamber"),
    "Richmond":       ("Richmond Raceway (NASCAR); State Fair of Virginia (Doswell)", "ChamberRVA"),
    "Austin":         ("SXSW + ACL Fest; F1 at COTA; UT athletics", "Austin Chamber"),
    "Jacksonville":   ("Jaguars; Greater Jacksonville Agricultural Fair; THE PLAYERS (TPC Sawgrass)", "JAX Chamber"),
}


# Universal first moves — same playbook everywhere; the metro rows carry the
# market-specific media to plug into steps 3-4.
QUICK_START_FOUNDATION = (
    "1) Google Business Profile + Local Services Ads + review engine  "
    "2) City landing pages + local SEO  "
    "3) Geofenced social + search ads + retargeting  "
    "4) Then buy local media below."
)


def category_contacts_rows():
    """13 rows per metro — the original 13 tactic categories, each with points of
    contact. Metro-specific where the channel is location-bound; universal
    self-serve platforms otherwise (marked 'Universal')."""
    comps = nat.load_national()
    conf_rank = {"High": 0, "Medium": 1, "Low": 2}

    def top_local_ops(city):
        serving = [c for c in comps if city in nat.cities_for(c)]
        locals_ = [c for c in serving
                   if len(nat.cities_for(c)) <= 8 and "Broker" not in c.company_type]
        locals_.sort(key=lambda c: (conf_rank.get(c.confidence, 3), c.company_name.lower()))
        names = [c.company_name for c in locals_[:3]]
        return ", ".join(names) if names else "Lamar / Clear Channel / OUTFRONT"

    rows = []
    pbc_cats = [
        ("Outdoor / OOH", "Metro", _pbc_ooh_contacts()),
        ("Local & Direct", "Mixed",
         "USPS EDDM by PBC carrier route · Valpak/Money Mailer PBC franchise · Nextdoor "
         "geo-ads · vehicle wraps + yard signs (in-house)"),
        ("Print", "Metro", f"{PBC_FACTS['paper']} (ad desk) · {PBC_FACTS['bizj']}"),
        ("Broadcast", "Metro", f"{PBC_FACTS['tv']} · Spectrum Reach / Comcast Effectv zoned to PBC"),
        ("Digital - Social Media", "Universal",
         "Meta/TikTok/Nextdoor self-serve geo-targeted to PBC ZIPs"),
        ("Digital - Content & Owned", "Universal",
         "City landing pages per PBC city + interactive tools (Hard Water Map, calculators)"),
        ("Digital - Search & Display", "Universal",
         "Google LSA + Search geo to PBC; branded + emergency-intent terms"),
        ("Digital - Other", "Universal",
         "Angi/Thumbtack/Yelp service-area PBC; retargeting via Meta/Google"),
        ("Experiential & Event", "Metro", PBC_FACTS["events"]),
        ("Promotional & Tangible", "Universal",
         "In-house printers / heat press / vinyl cutter — magnets, shutoff-valve tags"),
        ("PR & Earned", "Metro",
         f"Pitch: {PBC_FACTS['paper']} newsroom · WPBF/WPEC/WPTV news desks · water-quality data stories"),
        ("Partnership & Channel", "Metro",
         f"{PBC_FACTS['chamber']} · PBC realtors/inspectors/PMs & HOAs · BNI chapters"),
        ("Emerging / Niche", "Universal",
         "Your AI stack (AEO, chatbot, voice agent, n8n geo-triggered funnels) — the moat"),
    ]
    for cat, scope, contacts in pbc_cats:
        rows.append({"rank": 0, "metro": PBC_METRO, "category": cat,
                     "scope": scope, "contacts": contacts})
    for i, city in enumerate(nat.TOP_CITIES, 1):
        _dma, _pop, paper, bizj = METRO_MEDIA.get(city, ("-", "-", "-", "-"))
        tv, radio, agencies = METRO_BROADCAST.get(city, ("-", "-", "-"))
        events, chamber = METRO_CIVIC.get(city, ("-", "-"))
        cats = [
            ("Outdoor / OOH", "Metro",
             f"{top_local_ops(city)} — full roster on the Metro OOH Companies tab; brokers: AdQuick, Blue Line Media"),
            ("Local & Direct", "Mixed",
             f"USPS EDDM (usps.com/eddm) · Valpak / Money Mailer / Clipp local franchise · Nextdoor geo-ads · {chamber}"),
            ("Print", "Metro",
             f"{paper} (ad desk) · {bizj}"),
            ("Broadcast", "Metro",
             f"{tv} · local cable via Spectrum Reach / Comcast Effectv (zoned to metro)"),
            ("Digital - Social Media", "Universal",
             "Self-serve, geo-targeted to metro: Meta Ads Manager, TikTok Ads, Nextdoor, LinkedIn"),
            ("Digital - Content & Owned", "Universal",
             "Your own site/CMS + AI content stack — no local vendor; target metro via city landing pages"),
            ("Digital - Search & Display", "Universal",
             "Google Ads + Local Services Ads (geo to metro), Microsoft/Bing Ads, GDN/programmatic"),
            ("Digital - Other", "Universal",
             "Angi / Thumbtack / Yelp Ads / Houzz — set service area to metro; retargeting via Meta/Google"),
            ("Experiential & Event", "Metro",
             f"{events}"),
            ("Promotional & Tangible", "Universal",
             "4imprint, Vistaprint, sticker/print vendors — or in-house printers/heat press; ships anywhere"),
            ("PR & Earned", "Metro",
             f"Pitch: {paper} newsroom · big-4 TV news desks ({tv.split('·')[0].strip()} etc.) · {bizj} · local podcasts"),
            ("Partnership & Channel", "Metro",
             f"{chamber} · BNI local chapters · BBB · complementary trades in metro"),
            ("Emerging / Niche", "Universal",
             "AI/AEO/chatbot stack (build in-house) · programmatic DOOH via Vistar/AdQuick geo to metro"),
        ]
        for cat, scope, contacts in cats:
            rows.append({"rank": i, "metro": city, "category": cat,
                         "scope": scope, "contacts": contacts})
    return rows


def quick_start_rows():
    """Per-metro quick-start row: OOH band + top local operators + media to call."""
    comps = nat.load_national()
    rate = {r[1]: (r[4], r[5]) for r in nat.CITY_MARKET}
    conf_rank = {"High": 0, "Medium": 1, "Low": 2}

    rows = [{
        "rank": 0, "metro": PBC_METRO, "pop": PBC_FACTS["pop"],
        "ooh": PBC_FACTS["rate"] + "/mo",
        "ops": _pbc_ooh_contacts(limit=3),
        "tv": PBC_FACTS["tv"], "radio": PBC_FACTS["radio"],
        "paper": PBC_FACTS["paper"], "agencies": PBC_FACTS["agencies"],
    }]
    for i, city in enumerate(nat.TOP_CITIES, 1):
        lo, hi = rate[city]
        serving = [c for c in comps if city in nat.cities_for(c)]
        # Prefer local/regional operators (not nationwide, not pure brokers).
        locals_ = [c for c in serving
                   if len(nat.cities_for(c)) <= 8 and "Broker" not in c.company_type]
        locals_.sort(key=lambda c: (conf_rank.get(c.confidence, 3), c.company_name.lower()))
        top_ops = ", ".join(c.company_name for c in locals_[:3]) or "Lamar / Clear Channel / OUTFRONT"
        _dma, pop, paper, _bizj = METRO_MEDIA.get(city, ("-", "-", "-", "-"))
        tv, radio, agencies = METRO_BROADCAST.get(city, ("-", "-", "-"))
        rows.append({
            "rank": i,
            "metro": city,
            "pop": pop,
            "ooh": f"${lo:,}-${hi:,}/mo",
            "ops": top_ops,
            "tv": tv,
            "radio": radio,
            "paper": paper,
            "agencies": agencies,
        })
    return rows


def metro_company_rows():
    """Return list of dict rows for the Metro OOH Companies sheet."""
    comps = nat.load_national()
    order = {c: i for i, c in enumerate(nat.TOP_CITIES)}

    def keyfn(c):
        served = nat.cities_for(c)
        first = min((order[m] for m in served), default=999)
        return (0 if (c.serves_palm_beach or "").lower() == "yes" else 1, first, c.company_name.lower())

    rows = []
    for c in sorted(comps, key=keyfn):
        served = nat.cities_for(c)
        # The billboard Company model defaults state to "FL"; only trust HQ when a
        # city is explicitly set (avoids showing a spurious "FL" for national brokers).
        hq = f"{c.city}, {c.state}".strip(", ") if c.city else ""
        rows.append({
            "company": c.company_name,
            "type": c.company_type,
            "metros": "; ".join(served) if len(served) <= 6 else f"Nationwide ({len(served)} metros)",
            "hq": hq,
            "website": c.website,
            "pricing": c.pricing_reference or c.pricing,
            "confidence": c.confidence,
        })
    return rows
