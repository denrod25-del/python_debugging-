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
    rows = []
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
        })
    return rows


# Universal first moves — same playbook everywhere; the metro rows carry the
# market-specific media to plug into steps 3-4.
QUICK_START_FOUNDATION = (
    "1) Google Business Profile + Local Services Ads + review engine  "
    "2) City landing pages + local SEO  "
    "3) Geofenced social + search ads + retargeting  "
    "4) Then buy local media below."
)


def quick_start_rows():
    """Per-metro quick-start row: OOH band + top local operators + media to call."""
    comps = nat.load_national()
    rate = {r[1]: (r[4], r[5]) for r in nat.CITY_MARKET}
    conf_rank = {"High": 0, "Medium": 1, "Low": 2}

    rows = []
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
