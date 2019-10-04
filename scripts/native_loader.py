import re
from pprint import pprint

from pyparsing import Word, Literal, pyparsing_common, OneOrMore, alphanums, Suppress, SkipTo, LineEnd, ParserElement, \
    Forward, printables, ZeroOrMore, Group, Optional


def action_for(token: ParserElement):
    def wrapper(func):
        token.setParseAction(func)
        return func

    return wrapper


code = """
?SNDlib native format; type: network; version: 1.0
# network janos-us

# NODE SECTION
#
# <node_id> [(<longitude>, <latitude>)]

NODES (
  Seattle ( -122.30 47.45 )
  LosAngeles ( -118.40 33.93 )
  SanFrancisco ( -122.38 37.62 )
  LasVegas ( -115.17 36.08 )
  SaltLakeCity ( -111.97 40.78 )
  ElPaso ( -106.40 31.80 )
  Dallas ( -96.85 32.85 )
  Houston ( -95.35 29.97 )
  Tulsa ( -95.90 36.20 )
  Minneapolis ( -93.38 45.07 )
  KansasCity ( -94.72 39.32 )
  Denver ( -104.87 39.75 )
  Chicago ( -87.90 41.98 )
  Indianapolis ( -86.27 39.65 )
  Detroit ( -83.02 42.42 )
  StLouis ( -90.37 38.75 )
  Nashville ( -86.68 36.12 )
  Cleveland ( -81.68 41.52 )
  NewYork ( -73.78 40.65 )
  Albany ( -73.80 42.75 )
  Charlotte ( -80.93 35.22 )
  NewOrleans ( -90.02 29.83 )
  Boston ( -71.03 42.37 )
  Atlanta ( -84.42 33.65 )
  Miami ( -80.28 25.82 )
  WashingtonDC ( -77.04 38.85 )
)

# LINK SECTION
#
# <link_id> ( <source> <target> ) <pre_installed_capacity> <pre_installed_capacity_cost> <routing_cost> <setup_cost> ( {<module_capacity> <module_cost>}* )

LINKS (
  L0 ( Seattle SanFrancisco ) 0.00 0.00 0.00 0.00 ( 64.00 854.00 )
  L1 ( Seattle SaltLakeCity ) 0.00 0.00 0.00 0.00 ( 64.00 864.00 )
  L2 ( LosAngeles SanFrancisco ) 0.00 0.00 0.00 0.00 ( 64.00 425.00 )
  L3 ( LosAngeles LasVegas ) 0.00 0.00 0.00 0.00 ( 64.00 296.00 )
  L4 ( LosAngeles ElPaso ) 0.00 0.00 0.00 0.00 ( 64.00 879.00 )
  L5 ( SanFrancisco Seattle ) 0.00 0.00 0.00 0.00 ( 64.00 854.00 )
  L6 ( SanFrancisco LosAngeles ) 0.00 0.00 0.00 0.00 ( 64.00 425.00 )
  L7 ( SanFrancisco SaltLakeCity ) 0.00 0.00 0.00 0.00 ( 64.00 751.00 )
  L8 ( LasVegas LosAngeles ) 0.00 0.00 0.00 0.00 ( 64.00 296.00 )
  L9 ( LasVegas SaltLakeCity ) 0.00 0.00 0.00 0.00 ( 64.00 474.00 )
  L10 ( LasVegas ElPaso ) 0.00 0.00 0.00 0.00 ( 64.00 731.00 )
  L11 ( SaltLakeCity Seattle ) 0.00 0.00 0.00 0.00 ( 64.00 864.00 )
  L12 ( SaltLakeCity SanFrancisco ) 0.00 0.00 0.00 0.00 ( 64.00 751.00 )
  L13 ( SaltLakeCity LasVegas ) 0.00 0.00 0.00 0.00 ( 64.00 474.00 )
  L14 ( SaltLakeCity Denver ) 0.00 0.00 0.00 0.00 ( 64.00 478.00 )
  L15 ( ElPaso LosAngeles ) 0.00 0.00 0.00 0.00 ( 64.00 879.00 )
  L16 ( ElPaso LasVegas ) 0.00 0.00 0.00 0.00 ( 64.00 731.00 )
  L17 ( ElPaso Dallas ) 0.00 0.00 0.00 0.00 ( 64.00 705.00 )
  L18 ( ElPaso Houston ) 0.00 0.00 0.00 0.00 ( 64.00 838.00 )
  L19 ( Dallas ElPaso ) 0.00 0.00 0.00 0.00 ( 64.00 705.00 )
  L20 ( Dallas Houston ) 0.00 0.00 0.00 0.00 ( 64.00 273.00 )
  L21 ( Dallas Tulsa ) 0.00 0.00 0.00 0.00 ( 64.00 299.00 )
  L22 ( Dallas Denver ) 0.00 0.00 0.00 0.00 ( 64.00 820.00 )
  L23 ( Dallas Nashville ) 0.00 0.00 0.00 0.00 ( 64.00 781.00 )
  L24 ( Houston ElPaso ) 0.00 0.00 0.00 0.00 ( 64.00 838.00 )
  L25 ( Houston Dallas ) 0.00 0.00 0.00 0.00 ( 64.00 273.00 )
  L26 ( Houston NewOrleans ) 0.00 0.00 0.00 0.00 ( 64.00 401.00 )
  L27 ( Tulsa Dallas ) 0.00 0.00 0.00 0.00 ( 64.00 299.00 )
  L28 ( Tulsa KansasCity ) 0.00 0.00 0.00 0.00 ( 64.00 282.00 )
  L29 ( Tulsa StLouis ) 0.00 0.00 0.00 0.00 ( 64.00 449.00 )
  L30 ( Minneapolis KansasCity ) 0.00 0.00 0.00 0.00 ( 64.00 507.00 )
  L31 ( Minneapolis Chicago ) 0.00 0.00 0.00 0.00 ( 64.00 436.00 )
  L32 ( KansasCity Tulsa ) 0.00 0.00 0.00 0.00 ( 64.00 282.00 )
  L33 ( KansasCity Minneapolis ) 0.00 0.00 0.00 0.00 ( 64.00 468.00 )
  L34 ( KansasCity Denver ) 0.00 0.00 0.00 0.00 ( 64.00 679.00 )
  L35 ( KansasCity StLouis ) 0.00 0.00 0.00 0.00 ( 64.00 297.00 )
  L36 ( Denver SaltLakeCity ) 0.00 0.00 0.00 0.00 ( 64.00 478.00 )
  L37 ( Denver Dallas ) 0.00 0.00 0.00 0.00 ( 64.00 820.00 )
  L38 ( Denver KansasCity ) 0.00 0.00 0.00 0.00 ( 64.00 679.00 )
  L39 ( Chicago Minneapolis ) 0.00 0.00 0.00 0.00 ( 64.00 436.00 )
  L40 ( Chicago Indianapolis ) 0.00 0.00 0.00 0.00 ( 64.00 228.00 )
  L41 ( Chicago Detroit ) 0.00 0.00 0.00 0.00 ( 64.00 315.00 )
  L42 ( Chicago StLouis ) 0.00 0.00 0.00 0.00 ( 64.00 325.00 )
  L43 ( Indianapolis Chicago ) 0.00 0.00 0.00 0.00 ( 64.00 228.00 )
  L44 ( Indianapolis StLouis ) 0.00 0.00 0.00 0.00 ( 64.00 287.00 )
  L45 ( Indianapolis Nashville ) 0.00 0.00 0.00 0.00 ( 64.00 308.00 )
  L46 ( Indianapolis Cleveland ) 0.00 0.00 0.00 0.00 ( 64.00 343.00 )
  L47 ( Detroit Chicago ) 0.00 0.00 0.00 0.00 ( 64.00 315.00 )
  L48 ( Detroit Cleveland ) 0.00 0.00 0.00 0.00 ( 64.00 117.00 )
  L49 ( StLouis Tulsa ) 0.00 0.00 0.00 0.00 ( 64.00 449.00 )
  L50 ( StLouis KansasCity ) 0.00 0.00 0.00 0.00 ( 64.00 297.00 )
  L51 ( StLouis Chicago ) 0.00 0.00 0.00 0.00 ( 64.00 325.00 )
  L52 ( StLouis Indianapolis ) 0.00 0.00 0.00 0.00 ( 64.00 287.00 )
  L53 ( Nashville Dallas ) 0.00 0.00 0.00 0.00 ( 64.00 781.00 )
  L54 ( Nashville Indianapolis ) 0.00 0.00 0.00 0.00 ( 64.00 308.00 )
  L55 ( Nashville Charlotte ) 0.00 0.00 0.00 0.00 ( 64.00 413.00 )
  L56 ( Nashville Atlanta ) 0.00 0.00 0.00 0.00 ( 64.00 267.00 )
  L57 ( Cleveland Indianapolis ) 0.00 0.00 0.00 0.00 ( 64.00 343.00 )
  L58 ( Cleveland Detroit ) 0.00 0.00 0.00 0.00 ( 64.00 117.00 )
  L59 ( Cleveland Albany ) 0.00 0.00 0.00 0.00 ( 64.00 518.00 )
  L60 ( Cleveland WashingtonDC ) 0.00 0.00 0.00 0.00 ( 64.00 384.00 )
  L61 ( NewYork Albany ) 0.00 0.00 0.00 0.00 ( 64.00 182.00 )
  L62 ( NewYork Boston ) 0.00 0.00 0.00 0.00 ( 64.00 232.00 )
  L63 ( NewYork WashingtonDC ) 0.00 0.00 0.00 0.00 ( 64.00 267.00 )
  L64 ( Albany Cleveland ) 0.00 0.00 0.00 0.00 ( 64.00 518.00 )
  L65 ( Albany NewYork ) 0.00 0.00 0.00 0.00 ( 64.00 182.00 )
  L66 ( Albany Boston ) 0.00 0.00 0.00 0.00 ( 64.00 180.00 )
  L67 ( Charlotte Nashville ) 0.00 0.00 0.00 0.00 ( 64.00 413.00 )
  L68 ( Charlotte Atlanta ) 0.00 0.00 0.00 0.00 ( 64.00 284.00 )
  L69 ( Charlotte WashingtonDC ) 0.00 0.00 0.00 0.00 ( 64.00 414.00 )
  L70 ( NewOrleans Houston ) 0.00 0.00 0.00 0.00 ( 64.00 401.00 )
  L71 ( NewOrleans Atlanta ) 0.00 0.00 0.00 0.00 ( 64.00 530.00 )
  L72 ( NewOrleans Miami ) 0.00 0.00 0.00 0.00 ( 64.00 824.00 )
  L73 ( Boston NewYork ) 0.00 0.00 0.00 0.00 ( 64.00 232.00 )
  L74 ( Boston Albany ) 0.00 0.00 0.00 0.00 ( 64.00 180.00 )
  L75 ( Atlanta Nashville ) 0.00 0.00 0.00 0.00 ( 64.00 284.00 )
  L76 ( Atlanta Charlotte ) 0.00 0.00 0.00 0.00 ( 64.00 284.00 )
  L77 ( Atlanta NewOrleans ) 0.00 0.00 0.00 0.00 ( 64.00 530.00 )
  L78 ( Atlanta Miami ) 0.00 0.00 0.00 0.00 ( 64.00 747.00 )
  L79 ( Miami NewOrleans ) 0.00 0.00 0.00 0.00 ( 64.00 824.00 )
  L80 ( Miami Atlanta ) 0.00 0.00 0.00 0.00 ( 64.00 747.00 )
  L81 ( WashingtonDC Cleveland ) 0.00 0.00 0.00 0.00 ( 64.00 384.00 )
  L82 ( WashingtonDC NewYork ) 0.00 0.00 0.00 0.00 ( 64.00 267.00 )
  L83 ( WashingtonDC Charlotte ) 0.00 0.00 0.00 0.00 ( 64.00 414.00 )
)

# DEMAND SECTION
#
# <demand_id> ( <source> <target> ) <routing_unit> <demand_value> <max_path_length>

DEMANDS (
  D0 ( Seattle LosAngeles ) 1 240.00 UNLIMITED
  D1 ( Seattle SanFrancisco ) 1 544.00 UNLIMITED
  D2 ( Seattle LasVegas ) 1 24.00 UNLIMITED
  D3 ( Seattle SaltLakeCity ) 1 468.00 UNLIMITED
  D4 ( Seattle ElPaso ) 1 40.00 UNLIMITED
  D5 ( Seattle Dallas ) 1 40.00 UNLIMITED
  D6 ( Seattle Houston ) 1 44.00 UNLIMITED
  D7 ( Seattle Tulsa ) 1 24.00 UNLIMITED
  D8 ( Seattle Minneapolis ) 1 52.00 UNLIMITED
  D9 ( Seattle KansasCity ) 1 32.00 UNLIMITED
  D10 ( Seattle Denver ) 1 68.00 UNLIMITED
  D11 ( Seattle Chicago ) 1 56.00 UNLIMITED
  D12 ( Seattle Indianapolis ) 1 40.00 UNLIMITED
  D13 ( Seattle Detroit ) 1 36.00 UNLIMITED
  D14 ( Seattle StLouis ) 1 28.00 UNLIMITED
  D15 ( Seattle Nashville ) 1 36.00 UNLIMITED
  D16 ( Seattle Cleveland ) 1 40.00 UNLIMITED
  D17 ( Seattle NewYork ) 1 68.00 UNLIMITED
  D18 ( Seattle Albany ) 1 28.00 UNLIMITED
  D19 ( Seattle Charlotte ) 1 32.00 UNLIMITED
  D20 ( Seattle NewOrleans ) 1 28.00 UNLIMITED
  D21 ( Seattle Boston ) 1 60.00 UNLIMITED
  D22 ( Seattle Atlanta ) 1 32.00 UNLIMITED
  D23 ( Seattle Miami ) 1 44.00 UNLIMITED
  D24 ( Seattle WashingtonDC ) 1 60.00 UNLIMITED
  D25 ( LosAngeles Seattle ) 1 240.00 UNLIMITED
  D26 ( LosAngeles SanFrancisco ) 1 1128.00 UNLIMITED
  D27 ( LosAngeles LasVegas ) 1 392.00 UNLIMITED
  D28 ( LosAngeles SaltLakeCity ) 1 80.00 UNLIMITED
  D29 ( LosAngeles ElPaso ) 1 104.00 UNLIMITED
  D30 ( LosAngeles Dallas ) 1 1000.00 UNLIMITED
  D31 ( LosAngeles Houston ) 1 148.00 UNLIMITED
  D32 ( LosAngeles Tulsa ) 1 64.00 UNLIMITED
  D33 ( LosAngeles Minneapolis ) 1 56.00 UNLIMITED
  D34 ( LosAngeles KansasCity ) 1 60.00 UNLIMITED
  D35 ( LosAngeles Denver ) 1 160.00 UNLIMITED
  D36 ( LosAngeles Chicago ) 1 180.00 UNLIMITED
  D37 ( LosAngeles Indianapolis ) 1 72.00 UNLIMITED
  D38 ( LosAngeles Detroit ) 1 68.00 UNLIMITED
  D39 ( LosAngeles StLouis ) 1 56.00 UNLIMITED
  D40 ( LosAngeles Nashville ) 1 72.00 UNLIMITED
  D41 ( LosAngeles Cleveland ) 1 72.00 UNLIMITED
  D42 ( LosAngeles NewYork ) 1 220.00 UNLIMITED
  D43 ( LosAngeles Albany ) 1 52.00 UNLIMITED
  D44 ( LosAngeles Charlotte ) 1 60.00 UNLIMITED
  D45 ( LosAngeles NewOrleans ) 1 56.00 UNLIMITED
  D46 ( LosAngeles Boston ) 1 76.00 UNLIMITED
  D47 ( LosAngeles Atlanta ) 1 108.00 UNLIMITED
  D48 ( LosAngeles Miami ) 1 124.00 UNLIMITED
  D49 ( LosAngeles WashingtonDC ) 1 132.00 UNLIMITED
  D50 ( SanFrancisco Seattle ) 1 544.00 UNLIMITED
  D51 ( SanFrancisco LosAngeles ) 1 1128.00 UNLIMITED
  D52 ( SanFrancisco LasVegas ) 1 56.00 UNLIMITED
  D53 ( SanFrancisco SaltLakeCity ) 1 184.00 UNLIMITED
  D54 ( SanFrancisco ElPaso ) 1 60.00 UNLIMITED
  D55 ( SanFrancisco Dallas ) 1 552.00 UNLIMITED
  D56 ( SanFrancisco Houston ) 1 56.00 UNLIMITED
  D57 ( SanFrancisco Tulsa ) 1 52.00 UNLIMITED
  D58 ( SanFrancisco Minneapolis ) 1 36.00 UNLIMITED
  D59 ( SanFrancisco KansasCity ) 1 40.00 UNLIMITED
  D60 ( SanFrancisco Denver ) 1 88.00 UNLIMITED
  D61 ( SanFrancisco Chicago ) 1 680.00 UNLIMITED
  D62 ( SanFrancisco Indianapolis ) 1 48.00 UNLIMITED
  D63 ( SanFrancisco Detroit ) 1 44.00 UNLIMITED
  D64 ( SanFrancisco StLouis ) 1 396.00 UNLIMITED
  D65 ( SanFrancisco Nashville ) 1 44.00 UNLIMITED
  D66 ( SanFrancisco Cleveland ) 1 48.00 UNLIMITED
  D67 ( SanFrancisco NewYork ) 1 112.00 UNLIMITED
  D68 ( SanFrancisco Albany ) 1 36.00 UNLIMITED
  D69 ( SanFrancisco Charlotte ) 1 40.00 UNLIMITED
  D70 ( SanFrancisco NewOrleans ) 1 36.00 UNLIMITED
  D71 ( SanFrancisco Boston ) 1 44.00 UNLIMITED
  D72 ( SanFrancisco Atlanta ) 1 40.00 UNLIMITED
  D73 ( SanFrancisco Miami ) 1 56.00 UNLIMITED
  D74 ( SanFrancisco WashingtonDC ) 1 1256.00 UNLIMITED
  D75 ( LasVegas Seattle ) 1 24.00 UNLIMITED
  D76 ( LasVegas LosAngeles ) 1 392.00 UNLIMITED
  D77 ( LasVegas SanFrancisco ) 1 56.00 UNLIMITED
  D78 ( LasVegas SaltLakeCity ) 1 140.00 UNLIMITED
  D79 ( LasVegas ElPaso ) 1 52.00 UNLIMITED
  D80 ( LasVegas Dallas ) 1 180.00 UNLIMITED
  D81 ( LasVegas Houston ) 1 60.00 UNLIMITED
  D82 ( LasVegas Tulsa ) 1 12.00 UNLIMITED
  D83 ( LasVegas Minneapolis ) 1 16.00 UNLIMITED
  D84 ( LasVegas KansasCity ) 1 24.00 UNLIMITED
  D85 ( LasVegas Denver ) 1 64.00 UNLIMITED
  D86 ( LasVegas Chicago ) 1 28.00 UNLIMITED
  D87 ( LasVegas Indianapolis ) 1 20.00 UNLIMITED
  D88 ( LasVegas Detroit ) 1 20.00 UNLIMITED
  D89 ( LasVegas StLouis ) 1 16.00 UNLIMITED
  D90 ( LasVegas Nashville ) 1 20.00 UNLIMITED
  D91 ( LasVegas Cleveland ) 1 20.00 UNLIMITED
  D92 ( LasVegas NewYork ) 1 32.00 UNLIMITED
  D93 ( LasVegas Albany ) 1 12.00 UNLIMITED
  D94 ( LasVegas Charlotte ) 1 16.00 UNLIMITED
  D95 ( LasVegas NewOrleans ) 1 16.00 UNLIMITED
  D96 ( LasVegas Boston ) 1 16.00 UNLIMITED
  D97 ( LasVegas Atlanta ) 1 16.00 UNLIMITED
  D98 ( LasVegas Miami ) 1 24.00 UNLIMITED
  D99 ( LasVegas WashingtonDC ) 1 24.00 UNLIMITED
  D100 ( SaltLakeCity Seattle ) 1 468.00 UNLIMITED
  D101 ( SaltLakeCity LosAngeles ) 1 80.00 UNLIMITED
  D102 ( SaltLakeCity SanFrancisco ) 1 184.00 UNLIMITED
  D103 ( SaltLakeCity LasVegas ) 1 140.00 UNLIMITED
  D104 ( SaltLakeCity ElPaso ) 1 32.00 UNLIMITED
  D105 ( SaltLakeCity Dallas ) 1 388.00 UNLIMITED
  D106 ( SaltLakeCity Houston ) 1 32.00 UNLIMITED
  D107 ( SaltLakeCity Tulsa ) 1 20.00 UNLIMITED
  D108 ( SaltLakeCity Minneapolis ) 1 28.00 UNLIMITED
  D109 ( SaltLakeCity KansasCity ) 1 28.00 UNLIMITED
  D110 ( SaltLakeCity Denver ) 1 196.00 UNLIMITED
  D111 ( SaltLakeCity Chicago ) 1 72.00 UNLIMITED
  D112 ( SaltLakeCity Indianapolis ) 1 40.00 UNLIMITED
  D113 ( SaltLakeCity Detroit ) 1 32.00 UNLIMITED
  D114 ( SaltLakeCity StLouis ) 1 28.00 UNLIMITED
  D115 ( SaltLakeCity Nashville ) 1 24.00 UNLIMITED
  D116 ( SaltLakeCity Cleveland ) 1 40.00 UNLIMITED
  D117 ( SaltLakeCity NewYork ) 1 64.00 UNLIMITED
  D118 ( SaltLakeCity Albany ) 1 16.00 UNLIMITED
  D119 ( SaltLakeCity Charlotte ) 1 20.00 UNLIMITED
  D120 ( SaltLakeCity NewOrleans ) 1 20.00 UNLIMITED
  D121 ( SaltLakeCity Boston ) 1 24.00 UNLIMITED
  D122 ( SaltLakeCity Atlanta ) 1 20.00 UNLIMITED
  D123 ( SaltLakeCity Miami ) 1 28.00 UNLIMITED
  D124 ( SaltLakeCity WashingtonDC ) 1 28.00 UNLIMITED
  D125 ( ElPaso Seattle ) 1 40.00 UNLIMITED
  D126 ( ElPaso LosAngeles ) 1 104.00 UNLIMITED
  D127 ( ElPaso SanFrancisco ) 1 60.00 UNLIMITED
  D128 ( ElPaso LasVegas ) 1 52.00 UNLIMITED
  D129 ( ElPaso SaltLakeCity ) 1 32.00 UNLIMITED
  D130 ( ElPaso Dallas ) 1 76.00 UNLIMITED
  D131 ( ElPaso Houston ) 1 72.00 UNLIMITED
  D132 ( ElPaso Tulsa ) 1 36.00 UNLIMITED
  D133 ( ElPaso Minneapolis ) 1 32.00 UNLIMITED
  D134 ( ElPaso KansasCity ) 1 40.00 UNLIMITED
  D135 ( ElPaso Denver ) 1 44.00 UNLIMITED
  D136 ( ElPaso Chicago ) 1 64.00 UNLIMITED
  D137 ( ElPaso Indianapolis ) 1 48.00 UNLIMITED
  D138 ( ElPaso Detroit ) 1 44.00 UNLIMITED
  D139 ( ElPaso StLouis ) 1 36.00 UNLIMITED
  D140 ( ElPaso Nashville ) 1 44.00 UNLIMITED
  D141 ( ElPaso Cleveland ) 1 44.00 UNLIMITED
  D142 ( ElPaso NewYork ) 1 72.00 UNLIMITED
  D143 ( ElPaso Albany ) 1 32.00 UNLIMITED
  D144 ( ElPaso Charlotte ) 1 40.00 UNLIMITED
  D145 ( ElPaso NewOrleans ) 1 40.00 UNLIMITED
  D146 ( ElPaso Boston ) 1 40.00 UNLIMITED
  D147 ( ElPaso Atlanta ) 1 40.00 UNLIMITED
  D148 ( ElPaso Miami ) 1 56.00 UNLIMITED
  D149 ( ElPaso WashingtonDC ) 1 52.00 UNLIMITED
  D150 ( Dallas Seattle ) 1 40.00 UNLIMITED
  D151 ( Dallas LosAngeles ) 1 1000.00 UNLIMITED
  D152 ( Dallas SanFrancisco ) 1 552.00 UNLIMITED
  D153 ( Dallas LasVegas ) 1 180.00 UNLIMITED
  D154 ( Dallas SaltLakeCity ) 1 388.00 UNLIMITED
  D155 ( Dallas ElPaso ) 1 76.00 UNLIMITED
  D156 ( Dallas Houston ) 1 492.00 UNLIMITED
  D157 ( Dallas Tulsa ) 1 224.00 UNLIMITED
  D158 ( Dallas Minneapolis ) 1 40.00 UNLIMITED
  D159 ( Dallas KansasCity ) 1 100.00 UNLIMITED
  D160 ( Dallas Denver ) 1 64.00 UNLIMITED
  D161 ( Dallas Chicago ) 1 656.00 UNLIMITED
  D162 ( Dallas Indianapolis ) 1 64.00 UNLIMITED
  D163 ( Dallas Detroit ) 1 56.00 UNLIMITED
  D164 ( Dallas StLouis ) 1 64.00 UNLIMITED
  D165 ( Dallas Nashville ) 1 76.00 UNLIMITED
  D166 ( Dallas Cleveland ) 1 56.00 UNLIMITED
  D167 ( Dallas NewYork ) 1 116.00 UNLIMITED
  D168 ( Dallas Albany ) 1 40.00 UNLIMITED
  D169 ( Dallas Charlotte ) 1 52.00 UNLIMITED
  D170 ( Dallas NewOrleans ) 1 84.00 UNLIMITED
  D171 ( Dallas Boston ) 1 52.00 UNLIMITED
  D172 ( Dallas Atlanta ) 1 1028.00 UNLIMITED
  D173 ( Dallas Miami ) 1 72.00 UNLIMITED
  D174 ( Dallas WashingtonDC ) 1 924.00 UNLIMITED
  D175 ( Houston Seattle ) 1 44.00 UNLIMITED
  D176 ( Houston LosAngeles ) 1 148.00 UNLIMITED
  D177 ( Houston SanFrancisco ) 1 56.00 UNLIMITED
  D178 ( Houston LasVegas ) 1 60.00 UNLIMITED
  D179 ( Houston SaltLakeCity ) 1 32.00 UNLIMITED
  D180 ( Houston ElPaso ) 1 72.00 UNLIMITED
  D181 ( Houston Dallas ) 1 492.00 UNLIMITED
  D182 ( Houston Tulsa ) 1 64.00 UNLIMITED
  D183 ( Houston Minneapolis ) 1 44.00 UNLIMITED
  D184 ( Houston KansasCity ) 1 72.00 UNLIMITED
  D185 ( Houston Denver ) 1 44.00 UNLIMITED
  D186 ( Houston Chicago ) 1 100.00 UNLIMITED
  D187 ( Houston Indianapolis ) 1 72.00 UNLIMITED
  D188 ( Houston Detroit ) 1 60.00 UNLIMITED
  D189 ( Houston StLouis ) 1 56.00 UNLIMITED
  D190 ( Houston Nashville ) 1 76.00 UNLIMITED
  D191 ( Houston Cleveland ) 1 64.00 UNLIMITED
  D192 ( Houston NewYork ) 1 124.00 UNLIMITED
  D193 ( Houston Albany ) 1 44.00 UNLIMITED
  D194 ( Houston Charlotte ) 1 60.00 UNLIMITED
  D195 ( Houston NewOrleans ) 1 320.00 UNLIMITED
  D196 ( Houston Boston ) 1 60.00 UNLIMITED
  D197 ( Houston Atlanta ) 1 220.00 UNLIMITED
  D198 ( Houston Miami ) 1 96.00 UNLIMITED
  D199 ( Houston WashingtonDC ) 1 80.00 UNLIMITED
  D200 ( Tulsa Seattle ) 1 24.00 UNLIMITED
  D201 ( Tulsa LosAngeles ) 1 64.00 UNLIMITED
  D202 ( Tulsa SanFrancisco ) 1 52.00 UNLIMITED
  D203 ( Tulsa LasVegas ) 1 12.00 UNLIMITED
  D204 ( Tulsa SaltLakeCity ) 1 20.00 UNLIMITED
  D205 ( Tulsa ElPaso ) 1 36.00 UNLIMITED
  D206 ( Tulsa Dallas ) 1 224.00 UNLIMITED
  D207 ( Tulsa Houston ) 1 64.00 UNLIMITED
  D208 ( Tulsa Minneapolis ) 1 28.00 UNLIMITED
  D209 ( Tulsa KansasCity ) 1 204.00 UNLIMITED
  D210 ( Tulsa Denver ) 1 60.00 UNLIMITED
  D211 ( Tulsa Chicago ) 1 60.00 UNLIMITED
  D212 ( Tulsa Indianapolis ) 1 44.00 UNLIMITED
  D213 ( Tulsa Detroit ) 1 36.00 UNLIMITED
  D214 ( Tulsa StLouis ) 1 92.00 UNLIMITED
  D215 ( Tulsa Nashville ) 1 44.00 UNLIMITED
  D216 ( Tulsa Cleveland ) 1 36.00 UNLIMITED
  D217 ( Tulsa NewYork ) 1 68.00 UNLIMITED
  D218 ( Tulsa Albany ) 1 24.00 UNLIMITED
  D219 ( Tulsa Charlotte ) 1 32.00 UNLIMITED
  D220 ( Tulsa NewOrleans ) 1 80.00 UNLIMITED
  D221 ( Tulsa Boston ) 1 32.00 UNLIMITED
  D222 ( Tulsa Atlanta ) 1 36.00 UNLIMITED
  D223 ( Tulsa Miami ) 1 40.00 UNLIMITED
  D224 ( Tulsa WashingtonDC ) 1 52.00 UNLIMITED
  D225 ( Minneapolis Seattle ) 1 52.00 UNLIMITED
  D226 ( Minneapolis LosAngeles ) 1 56.00 UNLIMITED
  D227 ( Minneapolis SanFrancisco ) 1 36.00 UNLIMITED
  D228 ( Minneapolis LasVegas ) 1 16.00 UNLIMITED
  D229 ( Minneapolis SaltLakeCity ) 1 28.00 UNLIMITED
  D230 ( Minneapolis ElPaso ) 1 32.00 UNLIMITED
  D231 ( Minneapolis Dallas ) 1 40.00 UNLIMITED
  D232 ( Minneapolis Houston ) 1 44.00 UNLIMITED
  D233 ( Minneapolis Tulsa ) 1 28.00 UNLIMITED
  D234 ( Minneapolis KansasCity ) 1 84.00 UNLIMITED
  D235 ( Minneapolis Denver ) 1 68.00 UNLIMITED
  D236 ( Minneapolis Chicago ) 1 180.00 UNLIMITED
  D237 ( Minneapolis Indianapolis ) 1 56.00 UNLIMITED
  D238 ( Minneapolis Detroit ) 1 52.00 UNLIMITED
  D239 ( Minneapolis StLouis ) 1 44.00 UNLIMITED
  D240 ( Minneapolis Nashville ) 1 44.00 UNLIMITED
  D241 ( Minneapolis Cleveland ) 1 52.00 UNLIMITED
  D242 ( Minneapolis NewYork ) 1 76.00 UNLIMITED
  D243 ( Minneapolis Albany ) 1 32.00 UNLIMITED
  D244 ( Minneapolis Charlotte ) 1 36.00 UNLIMITED
  D245 ( Minneapolis NewOrleans ) 1 28.00 UNLIMITED
  D246 ( Minneapolis Boston ) 1 44.00 UNLIMITED
  D247 ( Minneapolis Atlanta ) 1 36.00 UNLIMITED
  D248 ( Minneapolis Miami ) 1 44.00 UNLIMITED
  D249 ( Minneapolis WashingtonDC ) 1 56.00 UNLIMITED
  D250 ( KansasCity Seattle ) 1 32.00 UNLIMITED
  D251 ( KansasCity LosAngeles ) 1 60.00 UNLIMITED
  D252 ( KansasCity SanFrancisco ) 1 40.00 UNLIMITED
  D253 ( KansasCity LasVegas ) 1 24.00 UNLIMITED
  D254 ( KansasCity SaltLakeCity ) 1 28.00 UNLIMITED
  D255 ( KansasCity ElPaso ) 1 40.00 UNLIMITED
  D256 ( KansasCity Dallas ) 1 100.00 UNLIMITED
  D257 ( KansasCity Houston ) 1 72.00 UNLIMITED
  D258 ( KansasCity Tulsa ) 1 204.00 UNLIMITED
  D259 ( KansasCity Minneapolis ) 1 84.00 UNLIMITED
  D260 ( KansasCity Denver ) 1 216.00 UNLIMITED
  D261 ( KansasCity Chicago ) 1 768.00 UNLIMITED
  D262 ( KansasCity Indianapolis ) 1 64.00 UNLIMITED
  D263 ( KansasCity Detroit ) 1 52.00 UNLIMITED
  D264 ( KansasCity StLouis ) 1 196.00 UNLIMITED
  D265 ( KansasCity Nashville ) 1 60.00 UNLIMITED
  D266 ( KansasCity Cleveland ) 1 52.00 UNLIMITED
  D267 ( KansasCity NewYork ) 1 80.00 UNLIMITED
  D268 ( KansasCity Albany ) 1 32.00 UNLIMITED
  D269 ( KansasCity Charlotte ) 1 44.00 UNLIMITED
  D270 ( KansasCity NewOrleans ) 1 40.00 UNLIMITED
  D271 ( KansasCity Boston ) 1 44.00 UNLIMITED
  D272 ( KansasCity Atlanta ) 1 44.00 UNLIMITED
  D273 ( KansasCity Miami ) 1 52.00 UNLIMITED
  D274 ( KansasCity WashingtonDC ) 1 72.00 UNLIMITED
  D275 ( Denver Seattle ) 1 68.00 UNLIMITED
  D276 ( Denver LosAngeles ) 1 160.00 UNLIMITED
  D277 ( Denver SanFrancisco ) 1 88.00 UNLIMITED
  D278 ( Denver LasVegas ) 1 64.00 UNLIMITED
  D279 ( Denver SaltLakeCity ) 1 196.00 UNLIMITED
  D280 ( Denver ElPaso ) 1 44.00 UNLIMITED
  D281 ( Denver Dallas ) 1 64.00 UNLIMITED
  D282 ( Denver Houston ) 1 44.00 UNLIMITED
  D283 ( Denver Tulsa ) 1 60.00 UNLIMITED
  D284 ( Denver Minneapolis ) 1 68.00 UNLIMITED
  D285 ( Denver KansasCity ) 1 216.00 UNLIMITED
  D286 ( Denver Chicago ) 1 120.00 UNLIMITED
  D287 ( Denver Indianapolis ) 1 36.00 UNLIMITED
  D288 ( Denver Detroit ) 1 32.00 UNLIMITED
  D289 ( Denver StLouis ) 1 28.00 UNLIMITED
  D290 ( Denver Nashville ) 1 36.00 UNLIMITED
  D291 ( Denver Cleveland ) 1 36.00 UNLIMITED
  D292 ( Denver NewYork ) 1 80.00 UNLIMITED
  D293 ( Denver Albany ) 1 24.00 UNLIMITED
  D294 ( Denver Charlotte ) 1 28.00 UNLIMITED
  D295 ( Denver NewOrleans ) 1 28.00 UNLIMITED
  D296 ( Denver Boston ) 1 32.00 UNLIMITED
  D297 ( Denver Atlanta ) 1 28.00 UNLIMITED
  D298 ( Denver Miami ) 1 36.00 UNLIMITED
  D299 ( Denver WashingtonDC ) 1 40.00 UNLIMITED
  D300 ( Chicago Seattle ) 1 56.00 UNLIMITED
  D301 ( Chicago LosAngeles ) 1 180.00 UNLIMITED
  D302 ( Chicago SanFrancisco ) 1 680.00 UNLIMITED
  D303 ( Chicago LasVegas ) 1 28.00 UNLIMITED
  D304 ( Chicago SaltLakeCity ) 1 72.00 UNLIMITED
  D305 ( Chicago ElPaso ) 1 64.00 UNLIMITED
  D306 ( Chicago Dallas ) 1 656.00 UNLIMITED
  D307 ( Chicago Houston ) 1 100.00 UNLIMITED
  D308 ( Chicago Tulsa ) 1 60.00 UNLIMITED
  D309 ( Chicago Minneapolis ) 1 180.00 UNLIMITED
  D310 ( Chicago KansasCity ) 1 768.00 UNLIMITED
  D311 ( Chicago Denver ) 1 120.00 UNLIMITED
  D312 ( Chicago Indianapolis ) 1 308.00 UNLIMITED
  D313 ( Chicago Detroit ) 1 236.00 UNLIMITED
  D314 ( Chicago StLouis ) 1 140.00 UNLIMITED
  D315 ( Chicago Nashville ) 1 120.00 UNLIMITED
  D316 ( Chicago Cleveland ) 1 356.00 UNLIMITED
  D317 ( Chicago NewYork ) 1 844.00 UNLIMITED
  D318 ( Chicago Albany ) 1 76.00 UNLIMITED
  D319 ( Chicago Charlotte ) 1 108.00 UNLIMITED
  D320 ( Chicago NewOrleans ) 1 64.00 UNLIMITED
  D321 ( Chicago Boston ) 1 96.00 UNLIMITED
  D322 ( Chicago Atlanta ) 1 212.00 UNLIMITED
  D323 ( Chicago Miami ) 1 96.00 UNLIMITED
  D324 ( Chicago WashingtonDC ) 1 708.00 UNLIMITED
  D325 ( Indianapolis Seattle ) 1 40.00 UNLIMITED
  D326 ( Indianapolis LosAngeles ) 1 72.00 UNLIMITED
  D327 ( Indianapolis SanFrancisco ) 1 48.00 UNLIMITED
  D328 ( Indianapolis LasVegas ) 1 20.00 UNLIMITED
  D329 ( Indianapolis SaltLakeCity ) 1 40.00 UNLIMITED
  D330 ( Indianapolis ElPaso ) 1 48.00 UNLIMITED
  D331 ( Indianapolis Dallas ) 1 64.00 UNLIMITED
  D332 ( Indianapolis Houston ) 1 72.00 UNLIMITED
  D333 ( Indianapolis Tulsa ) 1 44.00 UNLIMITED
  D334 ( Indianapolis Minneapolis ) 1 56.00 UNLIMITED
  D335 ( Indianapolis KansasCity ) 1 64.00 UNLIMITED
  D336 ( Indianapolis Denver ) 1 36.00 UNLIMITED
  D337 ( Indianapolis Chicago ) 1 308.00 UNLIMITED
  D338 ( Indianapolis Detroit ) 1 120.00 UNLIMITED
  D339 ( Indianapolis StLouis ) 1 140.00 UNLIMITED
  D340 ( Indianapolis Nashville ) 1 136.00 UNLIMITED
  D341 ( Indianapolis Cleveland ) 1 196.00 UNLIMITED
  D342 ( Indianapolis NewYork ) 1 144.00 UNLIMITED
  D343 ( Indianapolis Albany ) 1 60.00 UNLIMITED
  D344 ( Indianapolis Charlotte ) 1 88.00 UNLIMITED
  D345 ( Indianapolis NewOrleans ) 1 52.00 UNLIMITED
  D346 ( Indianapolis Boston ) 1 76.00 UNLIMITED
  D347 ( Indianapolis Atlanta ) 1 96.00 UNLIMITED
  D348 ( Indianapolis Miami ) 1 80.00 UNLIMITED
  D349 ( Indianapolis WashingtonDC ) 1 132.00 UNLIMITED
  D350 ( Detroit Seattle ) 1 36.00 UNLIMITED
  D351 ( Detroit LosAngeles ) 1 68.00 UNLIMITED
  D352 ( Detroit SanFrancisco ) 1 44.00 UNLIMITED
  D353 ( Detroit LasVegas ) 1 20.00 UNLIMITED
  D354 ( Detroit SaltLakeCity ) 1 32.00 UNLIMITED
  D355 ( Detroit ElPaso ) 1 44.00 UNLIMITED
  D356 ( Detroit Dallas ) 1 56.00 UNLIMITED
  D357 ( Detroit Houston ) 1 60.00 UNLIMITED
  D358 ( Detroit Tulsa ) 1 36.00 UNLIMITED
  D359 ( Detroit Minneapolis ) 1 52.00 UNLIMITED
  D360 ( Detroit KansasCity ) 1 52.00 UNLIMITED
  D361 ( Detroit Denver ) 1 32.00 UNLIMITED
  D362 ( Detroit Chicago ) 1 236.00 UNLIMITED
  D363 ( Detroit Indianapolis ) 1 120.00 UNLIMITED
  D364 ( Detroit StLouis ) 1 60.00 UNLIMITED
  D365 ( Detroit Nashville ) 1 80.00 UNLIMITED
  D366 ( Detroit Cleveland ) 1 288.00 UNLIMITED
  D367 ( Detroit NewYork ) 1 164.00 UNLIMITED
  D368 ( Detroit Albany ) 1 68.00 UNLIMITED
  D369 ( Detroit Charlotte ) 1 72.00 UNLIMITED
  D370 ( Detroit NewOrleans ) 1 44.00 UNLIMITED
  D371 ( Detroit Boston ) 1 84.00 UNLIMITED
  D372 ( Detroit Atlanta ) 1 64.00 UNLIMITED
  D373 ( Detroit Miami ) 1 72.00 UNLIMITED
  D374 ( Detroit WashingtonDC ) 1 120.00 UNLIMITED
  D375 ( StLouis Seattle ) 1 28.00 UNLIMITED
  D376 ( StLouis LosAngeles ) 1 56.00 UNLIMITED
  D377 ( StLouis SanFrancisco ) 1 396.00 UNLIMITED
  D378 ( StLouis LasVegas ) 1 16.00 UNLIMITED
  D379 ( StLouis SaltLakeCity ) 1 28.00 UNLIMITED
  D380 ( StLouis ElPaso ) 1 36.00 UNLIMITED
  D381 ( StLouis Dallas ) 1 64.00 UNLIMITED
  D382 ( StLouis Houston ) 1 56.00 UNLIMITED
  D383 ( StLouis Tulsa ) 1 92.00 UNLIMITED
  D384 ( StLouis Minneapolis ) 1 44.00 UNLIMITED
  D385 ( StLouis KansasCity ) 1 196.00 UNLIMITED
  D386 ( StLouis Denver ) 1 28.00 UNLIMITED
  D387 ( StLouis Chicago ) 1 140.00 UNLIMITED
  D388 ( StLouis Indianapolis ) 1 140.00 UNLIMITED
  D389 ( StLouis Detroit ) 1 60.00 UNLIMITED
  D390 ( StLouis Nashville ) 1 120.00 UNLIMITED
  D391 ( StLouis Cleveland ) 1 64.00 UNLIMITED
  D392 ( StLouis NewYork ) 1 88.00 UNLIMITED
  D393 ( StLouis Albany ) 1 36.00 UNLIMITED
  D394 ( StLouis Charlotte ) 1 52.00 UNLIMITED
  D395 ( StLouis NewOrleans ) 1 40.00 UNLIMITED
  D396 ( StLouis Boston ) 1 48.00 UNLIMITED
  D397 ( StLouis Atlanta ) 1 56.00 UNLIMITED
  D398 ( StLouis Miami ) 1 56.00 UNLIMITED
  D399 ( StLouis WashingtonDC ) 1 68.00 UNLIMITED
  D400 ( Nashville Seattle ) 1 36.00 UNLIMITED
  D401 ( Nashville LosAngeles ) 1 72.00 UNLIMITED
  D402 ( Nashville SanFrancisco ) 1 44.00 UNLIMITED
  D403 ( Nashville LasVegas ) 1 20.00 UNLIMITED
  D404 ( Nashville SaltLakeCity ) 1 24.00 UNLIMITED
  D405 ( Nashville ElPaso ) 1 44.00 UNLIMITED
  D406 ( Nashville Dallas ) 1 76.00 UNLIMITED
  D407 ( Nashville Houston ) 1 76.00 UNLIMITED
  D408 ( Nashville Tulsa ) 1 44.00 UNLIMITED
  D409 ( Nashville Minneapolis ) 1 44.00 UNLIMITED
  D410 ( Nashville KansasCity ) 1 60.00 UNLIMITED
  D411 ( Nashville Denver ) 1 36.00 UNLIMITED
  D412 ( Nashville Chicago ) 1 120.00 UNLIMITED
  D413 ( Nashville Indianapolis ) 1 136.00 UNLIMITED
  D414 ( Nashville Detroit ) 1 80.00 UNLIMITED
  D415 ( Nashville StLouis ) 1 120.00 UNLIMITED
  D416 ( Nashville Cleveland ) 1 84.00 UNLIMITED
  D417 ( Nashville NewYork ) 1 124.00 UNLIMITED
  D418 ( Nashville Albany ) 1 52.00 UNLIMITED
  D419 ( Nashville Charlotte ) 1 96.00 UNLIMITED
  D420 ( Nashville NewOrleans ) 1 76.00 UNLIMITED
  D421 ( Nashville Boston ) 1 64.00 UNLIMITED
  D422 ( Nashville Atlanta ) 1 184.00 UNLIMITED
  D423 ( Nashville Miami ) 1 84.00 UNLIMITED
  D424 ( Nashville WashingtonDC ) 1 100.00 UNLIMITED
  D425 ( Cleveland Seattle ) 1 40.00 UNLIMITED
  D426 ( Cleveland LosAngeles ) 1 72.00 UNLIMITED
  D427 ( Cleveland SanFrancisco ) 1 48.00 UNLIMITED
  D428 ( Cleveland LasVegas ) 1 20.00 UNLIMITED
  D429 ( Cleveland SaltLakeCity ) 1 40.00 UNLIMITED
  D430 ( Cleveland ElPaso ) 1 44.00 UNLIMITED
  D431 ( Cleveland Dallas ) 1 56.00 UNLIMITED
  D432 ( Cleveland Houston ) 1 64.00 UNLIMITED
  D433 ( Cleveland Tulsa ) 1 36.00 UNLIMITED
  D434 ( Cleveland Minneapolis ) 1 52.00 UNLIMITED
  D435 ( Cleveland KansasCity ) 1 52.00 UNLIMITED
  D436 ( Cleveland Denver ) 1 36.00 UNLIMITED
  D437 ( Cleveland Chicago ) 1 356.00 UNLIMITED
  D438 ( Cleveland Indianapolis ) 1 196.00 UNLIMITED
  D439 ( Cleveland Detroit ) 1 288.00 UNLIMITED
  D440 ( Cleveland StLouis ) 1 64.00 UNLIMITED
  D441 ( Cleveland Nashville ) 1 84.00 UNLIMITED
  D442 ( Cleveland NewYork ) 1 516.00 UNLIMITED
  D443 ( Cleveland Albany ) 1 96.00 UNLIMITED
  D444 ( Cleveland Charlotte ) 1 92.00 UNLIMITED
  D445 ( Cleveland NewOrleans ) 1 48.00 UNLIMITED
  D446 ( Cleveland Boston ) 1 108.00 UNLIMITED
  D447 ( Cleveland Atlanta ) 1 80.00 UNLIMITED
  D448 ( Cleveland Miami ) 1 76.00 UNLIMITED
  D449 ( Cleveland WashingtonDC ) 1 236.00 UNLIMITED
  D450 ( NewYork Seattle ) 1 68.00 UNLIMITED
  D451 ( NewYork LosAngeles ) 1 220.00 UNLIMITED
  D452 ( NewYork SanFrancisco ) 1 112.00 UNLIMITED
  D453 ( NewYork LasVegas ) 1 32.00 UNLIMITED
  D454 ( NewYork SaltLakeCity ) 1 64.00 UNLIMITED
  D455 ( NewYork ElPaso ) 1 72.00 UNLIMITED
  D456 ( NewYork Dallas ) 1 116.00 UNLIMITED
  D457 ( NewYork Houston ) 1 124.00 UNLIMITED
  D458 ( NewYork Tulsa ) 1 68.00 UNLIMITED
  D459 ( NewYork Minneapolis ) 1 76.00 UNLIMITED
  D460 ( NewYork KansasCity ) 1 80.00 UNLIMITED
  D461 ( NewYork Denver ) 1 80.00 UNLIMITED
  D462 ( NewYork Chicago ) 1 844.00 UNLIMITED
  D463 ( NewYork Indianapolis ) 1 144.00 UNLIMITED
  D464 ( NewYork Detroit ) 1 164.00 UNLIMITED
  D465 ( NewYork StLouis ) 1 88.00 UNLIMITED
  D466 ( NewYork Nashville ) 1 124.00 UNLIMITED
  D467 ( NewYork Cleveland ) 1 516.00 UNLIMITED
  D468 ( NewYork Albany ) 1 372.00 UNLIMITED
  D469 ( NewYork Charlotte ) 1 148.00 UNLIMITED
  D470 ( NewYork NewOrleans ) 1 80.00 UNLIMITED
  D471 ( NewYork Boston ) 1 672.00 UNLIMITED
  D472 ( NewYork Atlanta ) 1 164.00 UNLIMITED
  D473 ( NewYork Miami ) 1 284.00 UNLIMITED
  D474 ( NewYork WashingtonDC ) 1 1516.00 UNLIMITED
  D475 ( Albany Seattle ) 1 28.00 UNLIMITED
  D476 ( Albany LosAngeles ) 1 52.00 UNLIMITED
  D477 ( Albany SanFrancisco ) 1 36.00 UNLIMITED
  D478 ( Albany LasVegas ) 1 12.00 UNLIMITED
  D479 ( Albany SaltLakeCity ) 1 16.00 UNLIMITED
  D480 ( Albany ElPaso ) 1 32.00 UNLIMITED
  D481 ( Albany Dallas ) 1 40.00 UNLIMITED
  D482 ( Albany Houston ) 1 44.00 UNLIMITED
  D483 ( Albany Tulsa ) 1 24.00 UNLIMITED
  D484 ( Albany Minneapolis ) 1 32.00 UNLIMITED
  D485 ( Albany KansasCity ) 1 32.00 UNLIMITED
  D486 ( Albany Denver ) 1 24.00 UNLIMITED
  D487 ( Albany Chicago ) 1 76.00 UNLIMITED
  D488 ( Albany Indianapolis ) 1 60.00 UNLIMITED
  D489 ( Albany Detroit ) 1 68.00 UNLIMITED
  D490 ( Albany StLouis ) 1 36.00 UNLIMITED
  D491 ( Albany Nashville ) 1 52.00 UNLIMITED
  D492 ( Albany Cleveland ) 1 96.00 UNLIMITED
  D493 ( Albany NewYork ) 1 372.00 UNLIMITED
  D494 ( Albany Charlotte ) 1 56.00 UNLIMITED
  D495 ( Albany NewOrleans ) 1 32.00 UNLIMITED
  D496 ( Albany Boston ) 1 216.00 UNLIMITED
  D497 ( Albany Atlanta ) 1 48.00 UNLIMITED
  D498 ( Albany Miami ) 1 60.00 UNLIMITED
  D499 ( Albany WashingtonDC ) 1 116.00 UNLIMITED
  D500 ( Charlotte Seattle ) 1 32.00 UNLIMITED
  D501 ( Charlotte LosAngeles ) 1 60.00 UNLIMITED
  D502 ( Charlotte SanFrancisco ) 1 40.00 UNLIMITED
  D503 ( Charlotte LasVegas ) 1 16.00 UNLIMITED
  D504 ( Charlotte SaltLakeCity ) 1 20.00 UNLIMITED
  D505 ( Charlotte ElPaso ) 1 40.00 UNLIMITED
  D506 ( Charlotte Dallas ) 1 52.00 UNLIMITED
  D507 ( Charlotte Houston ) 1 60.00 UNLIMITED
  D508 ( Charlotte Tulsa ) 1 32.00 UNLIMITED
  D509 ( Charlotte Minneapolis ) 1 36.00 UNLIMITED
  D510 ( Charlotte KansasCity ) 1 44.00 UNLIMITED
  D511 ( Charlotte Denver ) 1 28.00 UNLIMITED
  D512 ( Charlotte Chicago ) 1 108.00 UNLIMITED
  D513 ( Charlotte Indianapolis ) 1 88.00 UNLIMITED
  D514 ( Charlotte Detroit ) 1 72.00 UNLIMITED
  D515 ( Charlotte StLouis ) 1 52.00 UNLIMITED
  D516 ( Charlotte Nashville ) 1 96.00 UNLIMITED
  D517 ( Charlotte Cleveland ) 1 92.00 UNLIMITED
  D518 ( Charlotte NewYork ) 1 148.00 UNLIMITED
  D519 ( Charlotte Albany ) 1 56.00 UNLIMITED
  D520 ( Charlotte NewOrleans ) 1 48.00 UNLIMITED
  D521 ( Charlotte Boston ) 1 72.00 UNLIMITED
  D522 ( Charlotte Atlanta ) 1 356.00 UNLIMITED
  D523 ( Charlotte Miami ) 1 180.00 UNLIMITED
  D524 ( Charlotte WashingtonDC ) 1 448.00 UNLIMITED
  D525 ( NewOrleans Seattle ) 1 28.00 UNLIMITED
  D526 ( NewOrleans LosAngeles ) 1 56.00 UNLIMITED
  D527 ( NewOrleans SanFrancisco ) 1 36.00 UNLIMITED
  D528 ( NewOrleans LasVegas ) 1 16.00 UNLIMITED
  D529 ( NewOrleans SaltLakeCity ) 1 20.00 UNLIMITED
  D530 ( NewOrleans ElPaso ) 1 40.00 UNLIMITED
  D531 ( NewOrleans Dallas ) 1 84.00 UNLIMITED
  D532 ( NewOrleans Houston ) 1 320.00 UNLIMITED
  D533 ( NewOrleans Tulsa ) 1 80.00 UNLIMITED
  D534 ( NewOrleans Minneapolis ) 1 28.00 UNLIMITED
  D535 ( NewOrleans KansasCity ) 1 40.00 UNLIMITED
  D536 ( NewOrleans Denver ) 1 28.00 UNLIMITED
  D537 ( NewOrleans Chicago ) 1 64.00 UNLIMITED
  D538 ( NewOrleans Indianapolis ) 1 52.00 UNLIMITED
  D539 ( NewOrleans Detroit ) 1 44.00 UNLIMITED
  D540 ( NewOrleans StLouis ) 1 40.00 UNLIMITED
  D541 ( NewOrleans Nashville ) 1 76.00 UNLIMITED
  D542 ( NewOrleans Cleveland ) 1 48.00 UNLIMITED
  D543 ( NewOrleans NewYork ) 1 80.00 UNLIMITED
  D544 ( NewOrleans Albany ) 1 32.00 UNLIMITED
  D545 ( NewOrleans Charlotte ) 1 48.00 UNLIMITED
  D546 ( NewOrleans Boston ) 1 44.00 UNLIMITED
  D547 ( NewOrleans Atlanta ) 1 232.00 UNLIMITED
  D548 ( NewOrleans Miami ) 1 116.00 UNLIMITED
  D549 ( NewOrleans WashingtonDC ) 1 60.00 UNLIMITED
  D550 ( Boston Seattle ) 1 60.00 UNLIMITED
  D551 ( Boston LosAngeles ) 1 76.00 UNLIMITED
  D552 ( Boston SanFrancisco ) 1 44.00 UNLIMITED
  D553 ( Boston LasVegas ) 1 16.00 UNLIMITED
  D554 ( Boston SaltLakeCity ) 1 24.00 UNLIMITED
  D555 ( Boston ElPaso ) 1 40.00 UNLIMITED
  D556 ( Boston Dallas ) 1 52.00 UNLIMITED
  D557 ( Boston Houston ) 1 60.00 UNLIMITED
  D558 ( Boston Tulsa ) 1 32.00 UNLIMITED
  D559 ( Boston Minneapolis ) 1 44.00 UNLIMITED
  D560 ( Boston KansasCity ) 1 44.00 UNLIMITED
  D561 ( Boston Denver ) 1 32.00 UNLIMITED
  D562 ( Boston Chicago ) 1 96.00 UNLIMITED
  D563 ( Boston Indianapolis ) 1 76.00 UNLIMITED
  D564 ( Boston Detroit ) 1 84.00 UNLIMITED
  D565 ( Boston StLouis ) 1 48.00 UNLIMITED
  D566 ( Boston Nashville ) 1 64.00 UNLIMITED
  D567 ( Boston Cleveland ) 1 108.00 UNLIMITED
  D568 ( Boston NewYork ) 1 672.00 UNLIMITED
  D569 ( Boston Albany ) 1 216.00 UNLIMITED
  D570 ( Boston Charlotte ) 1 72.00 UNLIMITED
  D571 ( Boston NewOrleans ) 1 44.00 UNLIMITED
  D572 ( Boston Atlanta ) 1 60.00 UNLIMITED
  D573 ( Boston Miami ) 1 80.00 UNLIMITED
  D574 ( Boston WashingtonDC ) 1 140.00 UNLIMITED
  D575 ( Atlanta Seattle ) 1 32.00 UNLIMITED
  D576 ( Atlanta LosAngeles ) 1 108.00 UNLIMITED
  D577 ( Atlanta SanFrancisco ) 1 40.00 UNLIMITED
  D578 ( Atlanta LasVegas ) 1 16.00 UNLIMITED
  D579 ( Atlanta SaltLakeCity ) 1 20.00 UNLIMITED
  D580 ( Atlanta ElPaso ) 1 40.00 UNLIMITED
  D581 ( Atlanta Dallas ) 1 1028.00 UNLIMITED
  D582 ( Atlanta Houston ) 1 220.00 UNLIMITED
  D583 ( Atlanta Tulsa ) 1 36.00 UNLIMITED
  D584 ( Atlanta Minneapolis ) 1 36.00 UNLIMITED
  D585 ( Atlanta KansasCity ) 1 44.00 UNLIMITED
  D586 ( Atlanta Denver ) 1 28.00 UNLIMITED
  D587 ( Atlanta Chicago ) 1 212.00 UNLIMITED
  D588 ( Atlanta Indianapolis ) 1 96.00 UNLIMITED
  D589 ( Atlanta Detroit ) 1 64.00 UNLIMITED
  D590 ( Atlanta StLouis ) 1 56.00 UNLIMITED
  D591 ( Atlanta Nashville ) 1 184.00 UNLIMITED
  D592 ( Atlanta Cleveland ) 1 80.00 UNLIMITED
  D593 ( Atlanta NewYork ) 1 164.00 UNLIMITED
  D594 ( Atlanta Albany ) 1 48.00 UNLIMITED
  D595 ( Atlanta Charlotte ) 1 356.00 UNLIMITED
  D596 ( Atlanta NewOrleans ) 1 232.00 UNLIMITED
  D597 ( Atlanta Boston ) 1 60.00 UNLIMITED
  D598 ( Atlanta Miami ) 1 808.00 UNLIMITED
  D599 ( Atlanta WashingtonDC ) 1 912.00 UNLIMITED
  D600 ( Miami Seattle ) 1 44.00 UNLIMITED
  D601 ( Miami LosAngeles ) 1 124.00 UNLIMITED
  D602 ( Miami SanFrancisco ) 1 56.00 UNLIMITED
  D603 ( Miami LasVegas ) 1 24.00 UNLIMITED
  D604 ( Miami SaltLakeCity ) 1 28.00 UNLIMITED
  D605 ( Miami ElPaso ) 1 56.00 UNLIMITED
  D606 ( Miami Dallas ) 1 72.00 UNLIMITED
  D607 ( Miami Houston ) 1 96.00 UNLIMITED
  D608 ( Miami Tulsa ) 1 40.00 UNLIMITED
  D609 ( Miami Minneapolis ) 1 44.00 UNLIMITED
  D610 ( Miami KansasCity ) 1 52.00 UNLIMITED
  D611 ( Miami Denver ) 1 36.00 UNLIMITED
  D612 ( Miami Chicago ) 1 96.00 UNLIMITED
  D613 ( Miami Indianapolis ) 1 80.00 UNLIMITED
  D614 ( Miami Detroit ) 1 72.00 UNLIMITED
  D615 ( Miami StLouis ) 1 56.00 UNLIMITED
  D616 ( Miami Nashville ) 1 84.00 UNLIMITED
  D617 ( Miami Cleveland ) 1 76.00 UNLIMITED
  D618 ( Miami NewYork ) 1 284.00 UNLIMITED
  D619 ( Miami Albany ) 1 60.00 UNLIMITED
  D620 ( Miami Charlotte ) 1 180.00 UNLIMITED
  D621 ( Miami NewOrleans ) 1 116.00 UNLIMITED
  D622 ( Miami Boston ) 1 80.00 UNLIMITED
  D623 ( Miami Atlanta ) 1 808.00 UNLIMITED
  D624 ( Miami WashingtonDC ) 1 252.00 UNLIMITED
  D625 ( WashingtonDC Seattle ) 1 60.00 UNLIMITED
  D626 ( WashingtonDC LosAngeles ) 1 132.00 UNLIMITED
  D627 ( WashingtonDC SanFrancisco ) 1 1256.00 UNLIMITED
  D628 ( WashingtonDC LasVegas ) 1 24.00 UNLIMITED
  D629 ( WashingtonDC SaltLakeCity ) 1 28.00 UNLIMITED
  D630 ( WashingtonDC ElPaso ) 1 52.00 UNLIMITED
  D631 ( WashingtonDC Dallas ) 1 924.00 UNLIMITED
  D632 ( WashingtonDC Houston ) 1 80.00 UNLIMITED
  D633 ( WashingtonDC Tulsa ) 1 52.00 UNLIMITED
  D634 ( WashingtonDC Minneapolis ) 1 56.00 UNLIMITED
  D635 ( WashingtonDC KansasCity ) 1 72.00 UNLIMITED
  D636 ( WashingtonDC Denver ) 1 40.00 UNLIMITED
  D637 ( WashingtonDC Chicago ) 1 708.00 UNLIMITED
  D638 ( WashingtonDC Indianapolis ) 1 132.00 UNLIMITED
  D639 ( WashingtonDC Detroit ) 1 120.00 UNLIMITED
  D640 ( WashingtonDC StLouis ) 1 68.00 UNLIMITED
  D641 ( WashingtonDC Nashville ) 1 100.00 UNLIMITED
  D642 ( WashingtonDC Cleveland ) 1 236.00 UNLIMITED
  D643 ( WashingtonDC NewYork ) 1 1516.00 UNLIMITED
  D644 ( WashingtonDC Albany ) 1 116.00 UNLIMITED
  D645 ( WashingtonDC Charlotte ) 1 448.00 UNLIMITED
  D646 ( WashingtonDC NewOrleans ) 1 60.00 UNLIMITED
  D647 ( WashingtonDC Boston ) 1 140.00 UNLIMITED
  D648 ( WashingtonDC Atlanta ) 1 912.00 UNLIMITED
  D649 ( WashingtonDC Miami ) 1 252.00 UNLIMITED
)

# ADMISSIBLE PATHS SECTION
#
# <demand_id> ( {<path_id> ( <link_id>+ )}+ )

ADMISSIBLE_PATHS ( 
)
"""
code = re.sub(r'[\#\?].*\n', '', code)

left_bracket = Suppress('(')
right_bracket = Suppress(')')
number = pyparsing_common.number
identifier = pyparsing_common.identifier
keyword_nodes = Suppress(Literal('NODES'))
keyword_links = Suppress(Literal('LINKS'))
keyword_demands = Suppress(Literal('DEMANDS'))
keyword_admissible_paths = Suppress(Literal('ADMISSIBLE_PATHS'))


node_definition = identifier + left_bracket + number + number + right_bracket
@action_for(node_definition)
def action_node_definition(string, location, tokens):
    return {'id': tokens[0], 'longitude': tokens[1], 'latitude': tokens[2]}


module_pair = number + number
@action_for(module_pair)
def action_node_definition(string, location, tokens):
    return {'module_capacity': tokens[0], 'module_cost': tokens[1]}


link_definition = identifier + left_bracket + identifier + identifier + right_bracket + number * 4 + left_bracket + ZeroOrMore(Group(module_pair)) + right_bracket
@action_for(link_definition)
def action_node_definition(string, location, tokens):
    return {
        'id': tokens[0],
        'source': tokens[1],
        'target': tokens[2],
        'pre_installed_capacity': tokens[3],
        'pre_installed_capacity_cost': tokens[4],
        'routing_cost': tokens[5],
        'setup_cost': tokens[6],
        'modules': tokens[7].asList(),
    }


demand_definition = identifier + left_bracket + identifier * 2 + right_bracket + number * 2 + (number | Literal('UNLIMITED'))
@action_for(demand_definition)
def action_demand_definition(string, location, tokens):
    return {
        'id': tokens[0],
        'source': tokens[1],
        'target': tokens[2],
        'routing_unit': tokens[3],
        'demand_value': tokens[4],
        'max_path_length': tokens[5],
    }


nodes = keyword_nodes + left_bracket + OneOrMore(node_definition) + right_bracket
links = keyword_links + left_bracket + OneOrMore(link_definition) + right_bracket
demands = keyword_demands + left_bracket + OneOrMore(demand_definition) + right_bracket
admissible_paths = keyword_admissible_paths + left_bracket + right_bracket
@action_for(nodes)
@action_for(links)
@action_for(demands)
@action_for(admissible_paths)
def action_nodes(string, location, tokens):
    return tuple(tokens)


native_file = nodes + links + demands + admissible_paths
@action_for(native_file)
def action_nodes(string, location, tokens):
    return {
        'nodes': list(tokens[0]),
        'links': list(tokens[1]),
        'demands': list(tokens[2]),
        'admissible_paths': list(tokens[3])
    }


def preprocess(code):
    return re.sub(r'[\#\?].*\n', '', code)


def load_as_dict(filepath: str):
    with open(filepath, 'r') as f:
        code = f.read()
        code = preprocess(code)
        return native_file.parseString(code)[0]
