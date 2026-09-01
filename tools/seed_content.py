# -*- coding: utf-8 -*-
"""One-off: write the initial content files.

After this has run, the JSON files under content/ are the source of truth —
edit them through the admin screen, not here. Kept only as a record of the schema.
"""
import json, os

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = os.path.join(HERE, "content")


def put(rel, data):
    path = os.path.join(C, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("  " + rel)


# ------------------------------------------------------------------ global
put("site.json", {
    "short_name": "IAHR-APD",
    "full_name": "International Association for Hydro-Environment Engineering and Research "
                 "— Asian and Pacific Division",
    "tagline": "Hydraulics and hydro-environment research across the Asia-Pacific.",
    "founded": 1973,
    "secretariat": {
        "host": "Korea Institute of Civil Engineering and Building Technology",
        "address_lines": ["283 Goyang-daero, Ilsanseo-gu, Goyang-si",
                          "Gyeonggi-do, Republic of Korea"],
        "telephone": "+82 31-9100-0265",
        "secretary_general": "Won Kim"
    },
    "links": {
        "iahr_global": "https://www.iahr.org/",
        "iahr_membership": "https://www.iahr.org/index/join",
        "jher": "https://www.sciencedirect.com/journal/journal-of-hydro-environment-research",
        "kict": "https://www.kict.re.kr/eng/"
    }
})

# ------------------------------------------------------------------ committee
put("committee.json", {
    "term": "2025 – 2026",
    "officers": [
        {"role": "Chair of the Division", "name": "Prof. Norio Tanaka",
         "affiliation": "Saitama University", "department": "Graduate School of Science and Engineering",
         "country": "Japan", "photo": "/assets/people/tanaka.jpg"},
        {"role": "Vice-Chair", "name": "Prof. S. A. Sannasiraj",
         "affiliation": "Indian Institute of Technology Madras", "department": "Department of Ocean Engineering",
         "country": "India", "photo": "/assets/people/sannasiraj.jpg"}
    ],
    "members": [
        {"role": "EC Member", "name": "Joongcheol Paik",
         "affiliation": "Gangneung-Wonju National University", "country": "Republic of Korea",
         "photo": "/assets/people/paik.jpg"},
        {"role": "EC Member", "name": "Asaad Y. Shamseldin",
         "affiliation": "The University of Auckland", "country": "New Zealand",
         "photo": "/assets/people/shamseldin.jpg"},
        {"role": "EC Member", "name": "Intan Supraba",
         "affiliation": "Universitas Gadjah Mada", "country": "Indonesia",
         "photo": "/assets/people/intan.jpg"},
        {"role": "EC Member", "name": "Hao-Che (Howard) Ho",
         "affiliation": "Affiliation to be confirmed", "country": "Taiwan, China",
         "photo": "/assets/people/haoche.jpg", "flag": "Check"},
        {"role": "EC Member", "name": "Mingfu Guan",
         "affiliation": "The University of Hong Kong", "country": "Hong Kong, China",
         "photo": "/assets/people/mingfu.jpg"},
        {"role": "EC Member", "name": "Chun Kiat Chang",
         "affiliation": "Universiti Sains Malaysia", "country": "Malaysia",
         "photo": "/assets/people/chunkiat.jpg"},
        {"role": "EC Member", "name": "Huu Loc Ho",
         "affiliation": "Asian Institute of Technology", "country": "Thailand",
         "photo": "/assets/people/huuloc.jpg"},
        {"role": "EC Member", "name": "Yongfeng Liu",
         "affiliation": "Hohai University", "country": "China",
         "photo": "/assets/people/liu.jpg"},
        {"role": "EC Member", "name": "Er Jenn Wei",
         "affiliation": "DHI Water & Environment (S) Pte. Ltd.", "country": "Singapore",
         "photo": "/assets/people/er.jpg"},
        {"role": "YPN Member", "name": "Qian Yu",
         "affiliation": "China Institute of Water Resources and Hydropower Research", "country": "China",
         "photo": "/assets/people/qian.jpg"},
        {"role": "Co-opted Member", "name": "Zhu Yonghui",
         "affiliation": "Changjiang River Scientific Research Institute", "country": "China",
         "photo": "/assets/people/zhu.jpg"},
        {"role": "Co-opted Member", "name": "Sung-Uk Choi",
         "affiliation": "Yonsei University", "country": "Republic of Korea",
         "photo": "/assets/people/choi.jpg"},
        {"role": "Secretary General", "name": "Won Kim",
         "affiliation": "Korea Institute of Civil Engineering and Building Technology",
         "country": "Republic of Korea", "photo": "/assets/people/wonkim.jpg"}
    ],
    "past_terms": ["2023 – 2024", "2020 – 2022"]
})

# ------------------------------------------------------------------ congresses
put("congresses.json", {
    "next": {
        "number": "26th", "year": 2028, "city": "Wellington", "country": "New Zealand",
        "dates": "8 – 12 February 2028", "opening": "2028-02-08",
        "theme": "", "host": "New Zealand hydraulics community",
        "abstracts": "Call opens 2027"
    },
    "latest": {
        "number": "25th", "year": 2026, "city": "Incheon", "country": "Republic of Korea",
        "dates": "19 – 22 July 2026",
        "venue": "Songdo ConvensiA, Incheon, Republic of Korea",
        "theme": "Hydro-environments in the Era of Climate Change and AI"
    },
    "archive": [
        {"number": "26th", "year": "2028", "location": "Wellington, New Zealand", "theme": "", "next": True},
        {"number": "25th", "year": "2026", "location": "Incheon, Republic of Korea",
         "theme": "Hydro-environments in the Era of Climate Change and AI"},
        {"number": "24th", "year": "2024", "location": "Wuhan, China", "theme": "Water for a Changing Future"},
        {"number": "23rd", "year": "2022", "location": "Chennai, India",
         "theme": "Water – From Land to Sea – Conservation and Management"},
        {"number": "22nd", "year": "2020", "location": "Sapporo, Japan",
         "theme": "Creating resilience to water-related challenges"},
        {"number": "21st", "year": "2018", "location": "Yogyakarta, Indonesia",
         "theme": "Multi-perspective Water for Sustainable Development"},
        {"number": "20th", "year": "2016", "location": "Colombo, Sri Lanka",
         "theme": "Water in the Past, Water in the Present and Water for the Future"},
        {"number": "19th", "year": "2014", "location": "Hanoi, Viet Nam",
         "theme": "Working globally, acting locally on water and climate change issues"},
        {"number": "18th", "year": "2012", "location": "Jeju, Republic of Korea",
         "theme": "Hydro-environmental engineering toward harmony between human and nature"},
        {"number": "17th", "year": "2010", "location": "Auckland, New Zealand",
         "theme": "Go with the flow — changing perception in balancing environment and economic needs"},
        {"number": "16th", "year": "2008", "location": "Nanjing, China",
         "theme": "Water and humanity — friendship, harmony and sustainable development"},
        {"number": "15th", "year": "2006", "location": "Chennai, India",
         "theme": "Water for life — development and management"},
        {"number": "14th", "year": "2004", "location": "Hong Kong, China",
         "theme": "Sustainable water management in the Asia-Pacific region"},
        {"number": "13th", "year": "2002", "location": "Singapore",
         "theme": "Advances in hydraulic and water engineering"},
        {"number": "12th", "year": "2000", "location": "Bangkok, Thailand",
         "theme": "Sustainable water resources management: issues and future challenges"},
        {"number": "11th", "year": "1998", "location": "Yogyakarta, Indonesia",
         "theme": "Hydraulic research for sustainable development"},
        {"number": "10th", "year": "1996", "location": "Langkawi, Malaysia",
         "theme": "Hydraulic research and engineering towards and beyond 2000"},
        {"number": "9th", "year": "1994", "location": "Singapore",
         "theme": "Developments in hydraulic engineering and their impact on the environment"},
        {"number": "8th", "year": "1992", "location": "Pune, India",
         "theme": "Hydraulic research in the service of mankind"},
        {"number": "7th", "year": "1990", "location": "Beijing, China",
         "theme": "Hydraulics to serve the development of a nation and the welfare of mankind"},
        {"number": "6th", "year": "1988", "location": "Kyoto, Japan",
         "theme": "For further prosperity in hydraulic research toward the 21st century"},
        {"number": "5th", "year": "", "location": "Seoul, Republic of Korea", "theme": ""},
        {"number": "4th", "year": "", "location": "Chiang Mai, Thailand", "theme": ""},
        {"number": "3rd", "year": "", "location": "Bandung, Indonesia", "theme": ""},
        {"number": "2nd", "year": "", "location": "Taipei, Taiwan, China", "theme": ""},
        {"number": "1st", "year": "", "location": "Bangkok, Thailand", "theme": ""}
    ],
    "proceedings": [
        {"number": "25th", "year": "2026", "host": "Incheon, Republic of Korea", "url": ""},
        {"number": "24th", "year": "2024", "host": "Wuhan, China", "url": ""},
        {"number": "23rd", "year": "2022", "host": "Chennai, India", "url": ""},
        {"number": "22nd", "year": "2020", "host": "Sapporo, Japan", "url": ""},
        {"number": "21st", "year": "2018", "host": "Yogyakarta, Indonesia", "url": ""},
        {"number": "20th", "year": "2016", "host": "Colombo, Sri Lanka", "url": ""},
        {"number": "19th", "year": "2014", "host": "Hanoi, Viet Nam", "url": ""}
    ]
})

# ------------------------------------------------------------------ EC meetings
put("ec-meetings.json", {"meetings": [
    {"date": "2026·07", "type": "EC meeting", "location": "Incheon, Republic of Korea", "with": "25th APD Congress"},
    {"date": "2025·06", "type": "EC meeting", "location": "Singapore", "with": "41st IAHR World Congress"},
    {"date": "2024·10", "type": "EC meeting", "location": "Wuhan, China", "with": "24th APD Congress"},
    {"date": "2023·08", "type": "EC gathering", "location": "Vienna, Austria", "with": "40th IAHR World Congress"},
    {"date": "2023·03", "type": "EC meeting", "location": "Online", "with": "—"},
    {"date": "2022·12", "type": "EC meeting", "location": "Chennai, India", "with": "23rd APD Congress"},
    {"date": "2022·06", "type": "EC gathering", "location": "Granada, Spain", "with": "39th IAHR World Congress"},
    {"date": "2020·09", "type": "EC meeting", "location": "Sapporo, Japan — online", "with": "22nd APD Congress"},
    {"date": "2019·09", "type": "EC meeting", "location": "Panama City, Panama", "with": "38th IAHR World Congress"},
    {"date": "2018·09", "type": "EC meeting", "location": "Yogyakarta, Indonesia", "with": "21st APD Congress"},
    {"date": "2017·08", "type": "EC gathering", "location": "Kuala Lumpur, Malaysia", "with": "37th IAHR World Congress"},
    {"date": "2016·08", "type": "EC meeting", "location": "Colombo, Sri Lanka", "with": "20th APD Congress"},
    {"date": "2015·06", "type": "EC gathering", "location": "The Hague, Netherlands", "with": "36th IAHR World Congress"},
    {"date": "2014·09", "type": "EC meeting", "location": "Hanoi, Viet Nam", "with": "19th APD Congress"},
    {"date": "2013·09", "type": "EC gathering", "location": "Chengdu, China", "with": "35th IAHR World Congress"},
    {"date": "2010·05", "type": "EC meeting", "location": "Auckland, New Zealand", "with": "17th APD Congress"}
]})

# ------------------------------------------------------------------ documents
put("documents.json", {
    "statutes": [
        {"title": "By-Laws of IAHR-APD, amended 2004", "format": "PDF", "file": ""},
        {"title": "By-Laws of IAHR-APD, revised edition 2025", "format": "PDF", "file": ""},
        {"title": "Founding statement and rules, APD Best Paper Award", "format": "PDF", "file": ""},
        {"title": "Statement of Distinguished IAHR-APD Membership Award, 2009", "format": "PDF", "file": ""},
        {"title": "Guidelines for IAHR Regional Congresses", "format": "PDF", "file": ""},
        {"title": "Working sheet for the IAHR-APD Congress", "format": "PDF", "file": ""},
        {"title": "Proposal format for hosting an IAHR-APD Congress", "format": "DOCX", "file": ""},
        {"title": "Handbook for the IAHR-APD Secretariat", "format": "PDF", "file": ""}
    ],
    "annual_reports": [
        {"title": "Annual Report 2025", "file": ""},
        {"title": "Annual Report 2024", "file": ""},
        {"title": "Annual Report 2023", "file": ""},
        {"title": "Annual Report 2022", "file": ""},
        {"title": "Annual Report 2021", "file": ""}
    ]
})

# ------------------------------------------------------------------ awards
put("awards.json", {
    "latest": {
        "congress": "Presented at the 24th Congress · Wuhan, China",
        "year": "2024",
        "distinguished": {"name": "Gregory Shahane De Costa",
                          "affiliation": "Open Polytechnic of New Zealand, New Zealand", "photo": ""},
        "heritage": {"name": "Hankou Hydrological Station", "affiliation": "Wuhan, China", "photo": ""},
        "papers": [
            {"title": "Diagnosing non-stationarity of hydrological model structure using Bayesian model "
                      "averaging: whether saturation-excess or infiltration-excess dominates runoff generation",
             "authors": "Liting Zhou, Xiaojing Zhang, Hairong Zhang, Huaming Yao, Pan Liu", "country": "China"},
            {"title": "Achieving SDG6 for sustainable water supply and wastewater management in "
                      "Southeastern Europe",
             "authors": "Elpida Kolokytha, Yannis Mylopoulos, Dionysis Latinopoulos, Jovan Despotović, "
                        "Aleksandar Djukić, Branislav Babić", "country": "Greece"},
            {"title": "Experimental investigation on the filling process of a long-distance pressurized "
                      "water conveyance tunnel",
             "authors": "Songlin Han, Xiaoxia Hou, Zhixin Wang, Zhibing Jiang, Duan Chen", "country": "China"},
            {"title": "Exploring the effects of modifying stratification reality and biogeochemical model "
                      "parameters on hypoxia using DN-4DVar",
             "authors": "Takanori Nagano, Masayasu Irie", "country": "Japan"}
        ]
    },
    "distinguished": {
        "eyebrow": "Award · established 2009",
        "title": "Distinguished IAHR-APD Membership Award",
        "intro": "Presented to an individual whose sustained contribution to hydro-environment engineering "
                 "and to the Division itself has been of exceptional value to the region.",
        "recipients": [
            {"year": "2024", "people": [{"name": "Gregory Shahane De Costa",
                                         "note": "Open Polytechnic of New Zealand, New Zealand"}]},
            {"year": "2022", "people": [{"name": "Hyoseop Woo", "note": "Republic of Korea"}]},
            {"year": "2020", "people": [{"name": "Bruce Melville", "note": "New Zealand"},
                                        {"name": "Kyung Soo Jun", "note": "Republic of Korea"}]},
            {"year": "2018", "people": [{"name": "Jing Peng", "note": "China"}]},
            {"year": "2016", "people": [{"name": "Hitoshi Tanaka", "note": "Japan"}]},
            {"year": "2014", "people": [{"name": "Il Won Seo", "note": "Republic of Korea"}]},
            {"year": "2012", "people": [{"name": "Lianxiang Wang", "note": "India"}]},
            {"year": "2010", "people": [{"name": "Joseph Lee", "note": "China"},
                                        {"name": "Ashim Das Gupta", "note": "Thailand"}]}
        ]
    },
    "heritage": {
        "eyebrow": "Award",
        "title": "IAHR-APD Heritage Award",
        "intro": "Presented to a hydraulic structure, system or site in the region of outstanding "
                 "historical, technical or cultural significance.",
        "recipients": [
            {"year": "2024", "people": [{"name": "Hankou Hydrological Station", "note": "Wuhan, China"}]},
            {"year": "2022", "people": [{"name": "Grand Anicut / Kallanai", "note": "India"}]},
            {"year": "2020", "people": [
                {"name": "Flood control and water utilisation facilities, Ishikari River basin", "note": "Japan"},
                {"name": "Tatsumi Aqueduct", "note": "Japan"},
                {"name": "Sayamaike Reservoir", "note": "Japan"}]},
            {"year": "2016", "people": [{"name": "Parakrama Samudraya", "note": "Sri Lanka"}]}
        ]
    },
    "best_paper": {
        "eyebrow": "Award",
        "title": "IAHR-APD Best Paper Award",
        "intro": "Selected from the papers presented at each regional congress. Award papers are regularly "
                 "invited for the JHER congress special issue.",
        "recipients": [
            {"year": "2022", "people": [
                {"name": "Numerical modelling of ship waves and induced sediment resuspension in the "
                         "Hooghly River, India", "note": "Mainak Chakraborty"},
                {"name": "Eliminating fixation of alternate bars by using impermeable groynes",
                 "note": "Ryotaro Endo"},
                {"name": "Combined storm surge and river flow simulation for the Hooghly Estuary, "
                         "east coast of India", "note": "B. Sridharan"},
                {"name": "Numerical investigations into wave attenuation characteristics of vegetation "
                         "belt in terms of vortex shedding", "note": "N. Hari Ram"},
                {"name": "Application of IITM-RANS3D to wave-breaking and wave–structure interaction problems",
                 "note": "Shaswat Saincher"}]},
            {"year": "2020", "people": [
                {"name": "Variability in stage–discharge relationships in river reach with bed evolutions",
                 "note": "Robin K. Biswas, Shinji Egashira, Daisuke Harada"},
                {"name": "Effects of submerged weir with an opening on bed deformation and flow structure "
                         "under live-bed conditions", "note": "Hirotaka Une, Terunori Ohmoto"},
                {"name": "Uncertainties of machine learning in predicting the hydrological responses of "
                         "LID practices", "note": "Yang Yang, Ting Fong May Chui"},
                {"name": "Reynolds number effects of internal solitary waves propagating on a uniform slope",
                 "note": "Hai Zhu, Songping Mao, Decai Sun, Lingling Wang, Zhenzhen Yu, Cheng Lin"}]},
            {"year": "2018", "people": [
                {"name": "Effect of climate change variables on the coastal wind prediction", "note": "Syamsidik"},
                {"name": "Effect of the combination of forest and the front-side moat along a river where "
                         "a tsunami runs up", "note": "Yoshiya Igarashi, Norio Tanaka"},
                {"name": "Dominating factors influencing rapid channel migration during floods — a case "
                         "study on Otofuke River", "note": "Tomoko Kyuka, Yasuyuki Shimizu"}]},
            {"year": "2012", "people": [
                {"name": "Analysis of dispersion characteristic using tracer test in natural stream",
                 "note": "Il Won Seo"}]},
            {"year": "2010", "people": [
                {"name": "The structure of flows in suspended aquaculture canopies", "note": "David Plew"}]}
        ]
    }
})

# ------------------------------------------------------------------ journal
put("journal.json", {
    "title": "Journal of Hydro-environment Research",
    "abbreviation": "JHER",
    "eyebrow": "House journal · since 2007",
    "body": [
        "Launched in 2007 by Elsevier, JHER is the house journal of the Asian and Pacific Division of "
        "IAHR, sponsored by the Korean Water Resources Association. The journal provides an international "
        "platform for research and engineering applications related to water and hydraulic problems in "
        "the Asia-Pacific region.",
        "The region's population density, economic growth, landscape, tradition and history require "
        "particular treatment of water problems, and every research article contains a section describing "
        "actual or potential applications to the Asia-Pacific. Alongside research articles the journal "
        "publishes review papers, invited papers, book reviews and technical communications.",
        "**Special issues** carrying selected papers from the biennial IAHR-APD Congresses — in "
        "particular the APD award papers — are a regular feature."
    ],
    "metrics_year": "2024",
    "metrics": [
        {"label": "CiteScore", "value": "5.6"},
        {"label": "Impact Factor", "value": "2.3"},
        {"label": "Review time", "value": "116 days"},
        {"label": "Submission to acceptance", "value": "251 days"},
        {"label": "Acceptance to publication", "value": "3 days"},
        {"label": "ISSN", "value": "1570-6443"},
        {"label": "Publisher", "value": "Elsevier"}
    ],
    "editors": [
        {"name": "Sung-Uk Choi", "affiliation": "Yonsei University, Seoul, Republic of Korea",
         "interests": "River hydraulics · sediment transport · turbulent flows · ecohydraulics",
         "photo": "/assets/people/choi.jpg"},
        {"name": "Adrian Wing-Keung Law", "affiliation": "Nanyang Technological University, Singapore",
         "interests": "", "photo": "/assets/people/adrian.jpg"}
    ],
    "other_publications": [
        {"kind": "Journal", "title": "Journal of Hydraulic Research",
         "note": "The association's flagship journal, published since 1963.", "meta": "IAHR · Taylor & Francis"},
        {"kind": "Journal", "title": "Journal of Applied Water Engineering and Research",
         "note": "Applied and practice-oriented water engineering.", "meta": "IAHR · Taylor & Francis"},
        {"kind": "Magazine", "title": "Hydrolink",
         "note": "The association's quarterly magazine for members.", "meta": "IAHR"},
        {"kind": "Monographs", "title": "IAHR Monograph Series",
         "note": "Reference works in hydraulic engineering and research.", "meta": "IAHR · CRC Press"}
    ]
})

# ------------------------------------------------------------------ events
put("events.json", {"events": [
    {"month": "Jun", "year": "2027", "title": "42nd IAHR World Congress",
     "detail": "28 June – 2 July 2027 · Bari, Italy"},
    {"month": "Feb", "year": "2028", "title": "26th IAHR-APD Congress",
     "detail": "8 – 12 February 2028 · Wellington, New Zealand"},
    {"month": "Feb", "year": "2028", "title": "APD Executive Committee meeting",
     "detail": "Held alongside the 26th Congress"},
    {"month": "2030", "year": "TBC", "title": "27th IAHR-APD Congress",
     "detail": "Host to be selected · proposals open"}
]})

# ------------------------------------------------------------------ gallery
def shots(prefix, n):
    return [{"image": "/assets/gallery/%s-%02d.jpg" % (prefix, i),
             "thumb": "/assets/gallery/%s-%02d-thumb.jpg" % (prefix, i),
             "caption": ""} for i in range(1, n + 1)]


put("gallery.json", {"years": [
    {"year": "2026", "title": "25th IAHR-APD Congress",
     "where": "19 – 22 July 2026 · Songdo ConvensiA, Incheon, Republic of Korea",
     "photos": shots("2026-incheon", 6)},
    {"year": "2025", "title": "Executive Committee meeting",
     "where": "30 June 2025 · Singapore, at the 41st IAHR World Congress",
     "photos": shots("2025-singapore", 3)},
    {"year": "2019", "title": "Executive Committee meeting",
     "where": "3 September 2019 · Panama City, at the 38th IAHR World Congress",
     "photos": shots("2019-panama", 2)},
    {"year": "2018", "title": "21st IAHR-APD Congress",
     "where": "2 – 5 September 2018 · Yogyakarta, Indonesia — committee meeting and technical visit",
     "photos": shots("2018-yogyakarta", 4)}
]})

# ------------------------------------------------------------------ news
NEWS = [
    ("2026-07-23-25th-congress-incheon", {
        "date": "2026-07-23",
        "title": "25th IAHR-APD Congress concludes in Incheon, Republic of Korea",
        "summary": "The congress on “Hydro-environments in the Era of Climate Change and AI” was held "
                   "19–22 July at Songdo ConvensiA.",
        "body": "The 25th Congress of the Asian and Pacific Division was held from 19 to 22 July 2026 at "
                "Songdo ConvensiA in Incheon, Republic of Korea, hosted with the support of the Korea "
                "Institute of Civil Engineering and Building Technology.\n\n"
                "The theme, **Hydro-environments in the Era of Climate Change and AI**, drew papers across "
                "flood risk, sediment transport, coastal engineering, ecohydraulics and data-driven "
                "modelling."}),
    ("2026-07-21-awards-presented", {
        "date": "2026-07-21",
        "title": "2026 IAHR-APD Awards presented at the Incheon Congress",
        "summary": "The Distinguished Membership, Heritage and Best Paper Awards were presented during "
                   "the congress dinner.",
        "body": "Citations for the 2026 recipients will be published together with the congress special "
                "issue of the Journal of Hydro-environment Research."}),
    ("2026-07-20-ec-meeting-incheon", {
        "date": "2026-07-20",
        "title": "Executive Committee meets in Incheon",
        "summary": "The Committee reviewed preparations for the 26th Congress in Wellington and approved "
                   "the Division's annual report to the IAHR Council.",
        "body": "The Executive Committee met on 20 July 2026 alongside the 25th Congress."}),
    ("2026-06-30-call-for-27th-congress", {
        "date": "2026-06-30",
        "title": "Call for proposals: hosting the 27th IAHR-APD Congress in 2030",
        "summary": "Member institutions in the region are invited to submit hosting proposals to the "
                   "Secretariat using the standard proposal format.",
        "body": "Proposals should cover the venue and dates, the proposed theme and sub-themes, the local "
                "organising committee, the budget and registration model, and the arrangements for "
                "publishing proceedings.\n\n"
                "The guidelines and the proposal format are available under [About the Division](/about/)."}),
    ("2026-03-12-jher-metrics", {
        "date": "2026-03-12",
        "title": "JHER 2024 metrics published: impact factor 2.3, CiteScore 5.6",
        "summary": "Median review time for the journal now stands at 116 days.",
        "body": "Full metrics are listed on the [Publications](/publications/) page."})
]
for slug, data in NEWS:
    put("news/%s.json" % slug, data)

print("\ndone")
