# features.py - Mechanic Inspection Roadmap + Repair Verification.
# Knowledge base + UI panels for the two diagnosis-support features.
# Records are saved through store.py (JSON files in data/).
# IMPORTANT: everything here is PRELIMINARY decision support. Nothing here
# is a confirmed diagnosis and the system never claims to have inspected
# the vehicle physically.
import json
import streamlit as st
from datetime import datetime

import store
import history as H


def t(en, ur):
    # Same bilingual helper as codebase.T but local to this module
    return en if st.session_state.get('lang', 'en') == 'en' else ur


# Exact warning required by the project brief - shown on every diagnosis surface.
MECH_WARNING = ("IMPORTANT: This is an AI-assisted preliminary assessment based on the symptoms you provided. "
                "It is NOT a confirmed mechanical diagnosis. All suggested faults and recommendations MUST be "
                "verified by a qualified professional mechanic through proper physical inspection and diagnostic testing.")
MECH_WARNING_UR = ("اہم: یہ آپ کی فراہم کردہ علامات کی بنیاد پر AI سے تیار کردہ ابتدائی تشخیص ہے۔ یہ حتمی میکانیکی تشخیص نہیں ہے۔ "
                   "تمام تجویز کردہ خرابیاں اور سفارشیں کسی مستند پیشہ ور مکینک کے ذریعے جسمانی معائنے اور ڈائگنوسٹک ٹیسٹنگ سے تصدیق ہونی چاہئیں۔")
NO_SELF_REPAIR = "Never replace vehicle components or perform repairs solely on the basis of this system's suggestions."
NO_SELF_REPAIR_UR = "اس سسٹم کی تجاویز کی بنیاد پر اکیلے گاڑی کے پرزے تبدیل یا مرمت نہ کریں۔"


def mech_warning_box():
    # The mandatory verification warning, shown prominently
    st.error(MECH_WARNING if st.session_state.get('lang', 'en') == 'en' else MECH_WARNING_UR)
    st.caption(NO_SELF_REPAIR if st.session_state.get('lang', 'en') == 'en' else NO_SELF_REPAIR_UR)


# =====================================================================
#  KNOWLEDGE BASE - system-level inspection roadmaps
#  key -> (component_en, component_ur, points[(en,ur)...], tests[(en,ur)...])
# =====================================================================
SYSTEM_INFO = {
    'ns': ("Battery, starter motor & fuel delivery", "بیٹری، اسٹارٹر موٹر اور فیول سپلائی",
           [("Battery terminals and cable condition", "بیٹری ٹرمینلز اور کیبل کی حالت"),
            ("Battery load / health test", "بیٹری لوڈ / ہیلتھ ٹیسٹ"),
            ("Starter motor draw test", "اسٹارٹر موٹر کی جانچ"),
            ("Fuel pump and fuel pressure", "فیول پمپ اور فیول پریشر")],
           [("Multimeter voltage test (engine off and cranking)", "ملٹی میٹر وولٹیج ٹیسٹ"),
            ("Starter bench / on-car test", "اسٹارٹر ٹیسٹ"),
            ("Fuel pressure gauge test", "فیول پریشر گیج ٹیسٹ")]),
    'oh': ("Cooling system (radiator, thermostat, water pump, fan)", "کولنگ سسٹم",
           [("Coolant level, colour and condition", "کولنٹ کی سطح، رنگ اور حالت"),
            ("Radiator fins and hoses for leaks / blockage", "ریڈی ایٹر اور نلیوں میں لیک / رکاوٹ"),
            ("Thermostat operation", "تھرمو اسٹیٹ کی کارکردگی"),
            ("Water pump weep hole and bearing", "واٹر پمپ کی جانچ"),
            ("Radiator fan operation", "ریڈی ایٹر پنکھے کی کارکردگی")],
           [("Cooling system pressure test", "کولنگ سسٹم پریشر ٹیسٹ"),
            ("Thermostat temperature test", "تھرمو اسٹیٹ ٹیسٹ"),
            ("Infrared thermometer check of radiator / engine", "ریڈی ایٹر / انجن کا درجہ حرارت چیک")]),
    'br': ("Brake pads, discs, fluid and calipers", "بریک پیڈز، ڈسکیں، فلوئڈ اور کیلیپر",
           [("Pad and shoe thickness", "پیڈز کی موٹائی"),
            ("Disc / drum condition and run-out", "ڈسک / ڈرم کی حالت"),
            ("Brake fluid level, colour and moisture", "بریک فلوئڈ کی سطح اور نمی"),
            ("Caliper slide pins and piston seals", "کیلیپر کے پرزے"),
            ("Brake lines and hoses for leaks", "بریک لائنوں / نلیوں میں لیک")],
           [("Brake pedal feel and travel test", "بریک پیڈل ٹیسٹ"),
            ("Brake fluid moisture test", "بریک فلوئڈ ٹیسٹ"),
            ("Wheel-off pad / disc measurement", "پیڈز / ڈسک کی ناپ")]),
    'nv': ("Engine, belts, bearings and suspension (noise source)", "انجن، بیلٹ، بیئرنگ اور سسپنشن",
           [("Serpentine / drive belt tension and wear", "بیلٹ کی حالت"),
            ("Wheel bearings for play / noise", "وہیل بیئرنگز"),
            ("Suspension bushes, shocks and links", "سسپنشن کے پرزے"),
            ("Engine mounts", "انجن ماؤنٹس")],
           [("Stethoscope / listening check while driving", "آواز کی جگہ لوکیشن ٹیسٹ"),
            ("Suspension bounce and play test", "سسپنشن ٹیسٹ"),
            ("Belt tension gauge check", "بیلٹ ٹینشن چیک")]),
    'el': ("Battery, alternator, wiring and fuses", "بیٹری، البرنیٹر، وائرنگ اور فیوز",
           [("Battery state of charge and health", "بیٹری کی حالت"),
            ("Alternator charging output", "الٹرنیٹر کی چارجنگ")],
           [("Charging system test (engine running)", "چارجنگ سسٹم ٹیسٹ"),
            ("Parasitic draw test", "پیرسائٹک ڈراؤ ٹیسٹ"),
            ("Fuse and relay inspection", "فیوز اور ریلے معائنہ")]),
    'ty': ("Tyres, wheels, pressures and alignment", "ٹائر، پہیے، پریشر اور الائنمنٹ",
           [("Tread depth and even wear", "گراری کی گہرائی اور گھسی ہوئی جگہیں"),
            ("Sidewall cuts, bulges and age (DOT code)", "سائیڈ وال کی حالت اور عمر"),
            ("Tyre pressures (all four + spare)", "چاروں ٹائرز کا پریشر"),
            ("Wheel balance and alignment", "پہیوں کا بیلنس اور الائنمنٹ")],
           [("Tread depth gauge measurement", "ٹ ڈیپتھ گیج"),
            ("Four-wheel alignment check", "چاروں پہیوں کی الائنمنٹ چیک"),
            ("Wheel balancing on machine", "وہیل بیلنسنگ")]),
    'ol': ("Engine oil level, leaks and burning oil", "انجن آئل کی سطح، لیک اور جلتا آئل",
           [("Oil level and condition on dipstick", "ڈپ اسٹک پر آئل کی سطح"),
            ("External leak points (gaskets, seals, filter)", "لیک کی جگہیں"),
            ("Exhaust smoke colour and smell", "ایگزاسٹ کا دھواں")],
           [("UV dye leak detection", "یووی ڈائی لیک ٹیسٹ"),
            ("Compression / leak-down test (for burning oil)", "کمپریشن ٹیسٹ"),
            ("Oil analysis", "آئل تجزیہ")]),
    'ac': ("AC gas, compressor, condenser and cabin filter", "اے سی گیس، کمپریسر، کنڈینسر اور کیبن فلٹر",
           [("AC gas pressure (manifold gauges)", "اے سی گیس پریشر"),
            ("Compressor clutch and operation", "کمپریسر کی کارکردگی"),
            ("Condenser airflow and cleanliness", "کنڈینسر کی حالت"),
            ("Cabin air filter", "کیبن ایئر فلٹر")],
           [("A/C performance test (vent temperature)", "اے سی پرفارمنس ٹیسٹ"),
            ("Gas leak check (UV / electronic detector)", "گیس لیک ٹیسٹ"),
            ("Compressor clutch voltage test", "کمپریسر ٹیسٹ")]),
    'sr': ("Power steering fluid, linkage, rack and pump", "پاور اسٹیئرنگ فلوئڈ، لنکیج، ریک اور پمپ",
           [("Power steering fluid level and condition", "پاور اسٹیئرنگ فلوئڈ"),
            ("Tie rod ends and steering rack boots", "ٹائی روڈ اور ریک بوٹس"),
            ("Steering wheel play / free movement", "اسٹیئرنگ میں کلیرنس"),
            ("Power steering pump belt and noise", "پمپ بیلٹ اور آواز")],
           [("Steering free-play measurement", "اسٹیئرنگ پلے ٹیسٹ"),
            ("Fluid leak inspection", "فلوئڈ لیک معائنہ"),
            ("Pump pressure test", "پمپ پریشر ٹیسٹ")]),
    'gc': ("Gearbox oil, clutch and synchros", "گیئر باکس آئل، کلچ اور سنکرونائزر",
           [("Gearbox / ATF oil level and condition", "گیئر باکس آئل"),
            ("Clutch pedal free play and feel", "کلچ پیڈل"),
            ("Gear lever linkage and mounts", "گیئر لنکیج"),
            ("Transmission mounts", "ٹرانسمیشن ماؤنٹس")],
           [("Clutch slip road test", "کلچ سلپ ٹیسٹ"),
            ("Gearbox oil inspection", "گیئر باکس آئل چیک"),
            ("ATF condition test (where applicable)", "اے ٹی ایف چیک")]),
}

# =====================================================================
#  KNOWLEDGE BASE - fault-specific findings
#  fault_name_en -> (sys_key, test_en, test_ur, confirm_en, confirm_ur,
#                     weaken_en, weaken_ur)
#  confirm  = findings that would SUPPORT the suspected fault
#  weaken   = findings that would WEAKEN / rule it out
# =====================================================================
FAULT_INFO = {
    "Weak or dead battery": ('ns',
        "Battery load test and voltage under crank load",
        "بیٹری لوڈ ٹیسٹ اور کرینک لوڈ پر وولٹیج",
        "Voltage drops below ~10V while cranking, or battery fails load test",
        "کرینک کرتے وقت وولٹیج ~10 وولٹ سے کم ہو، یا بیٹری لوڈ ٹیسٹ میں ناکام ہو",
        "Battery passes load test and holds 12.4V+ - look at cables / starter instead",
        "بیٹری لوڈ ٹیسٹ پاس کرے اور 12.4 وولٹ+ برقرار رکھے - کیبلز / اسٹارٹر دیکھیں"),
    "Starter motor fault": ('ns',
        "Starter motor current draw and bench test",
        "اسٹارٹر موٹر کرنٹ ڈراؤ اور بینچ ٹیسٹ",
        "Single loud click with healthy battery voltage, motor does not spin",
        "بیٹری وولٹیج ٹھیک ہونے کے باوجود ایک کلک اور موٹر نہیں گھومتی",
        "Starter spins freely on bench test - fault is elsewhere (ignition/fuel)",
        "اسٹارٹر بینچ ٹیسٹ میں آزادانہ گھومے - خرابی کہیں اور ہے"),
    "Fuel supply problem": ('ns',
        "Fuel pressure test at the rail",
        "ریل پر فیول پریشر ٹیسٹ",
        "Fuel pressure below specification or pump silent when key turned ON",
        "فیول پریشر سپیسیفکیشن سے کم یا چابی ON پر پمپ خاموش",
        "Fuel pressure normal - problem is spark / compression instead",
        "فیول پریشر نارمل - مسئلہ اسپارک / کمپریشن کا ہے"),
    "Ignition / spark problem": ('ns',
        "Spark test on each plug and coil check",
        "ہر پلگ پر اسپارک ٹیسٹ اور کوائل چیک",
        "No spark on one or more cylinders, or weak yellow spark",
        "ایک یا زیادہ سلنڈروں پر اسپارک نہیں یا کمزور پیلی اسپارک",
        "Strong blue spark on all plugs - look at fuel / compression",
        "تمام پلگوں پر مضبوط نیلی اسپارک - فیول / کمپریشن دیکھیں"),
    "Low coolant / coolant leak": ('oh',
        "Cooling system pressure test and visual leak check",
        "کولنگ پریشر ٹیسٹ اور لیک کا بصری معائنہ",
        "Pressure drops during test, or visible crusty residue on hoses / radiator",
        "ٹیسٹ میں پریشر گرے، یا نلیوں / ریڈی ایٹر پر خشک رہunenز",
        "System holds pressure - top-up may have been overdue only",
        "سسٹم پریشر برقرار رکھے - صرف ٹاپ اپ کی دیر ہو سکتی ہے"),
    "Thermostat fault": ('oh',
        "Thermostat hot-water opening test",
        "تھرمو اسٹیٹ کھولنے کا ٹیسٹ",
        "Engine warms up then overheats at idle / low speed; thermostat stays closed",
        "انجن گرم ہو کر 아이ڈل / کم رفتار پر اوور ہیٹ ہو؛ تھرمواسٹیٹ بند رہے",
        "Thermostat opens at correct temperature - look at water pump / airflow",
        "تھرمو اسٹیٹ صحیح درجہ پر کھلے - واٹر پمپ / ہوائ-flow دیکھیں"),
    "Radiator fan not working": ('oh',
        "Fan relay, fuse and motor voltage test",
        "فین ریلے، فیوز اور موٹر وولٹیج ٹیسٹ",
        "Fan does not spin at operating temperature even with AC on",
        "آپریٹنگ درجہ حرارت پر اے سی ON ہونے کے باوجود فین نہ چلے",
        "Fan spins normally - overheating has another cause",
        "فین نارمل چلتا ہے - اوورہیٹنگ کی وجہ کوئی اور ہے"),
    "Water pump / head gasket issue": ('oh',
        "Water pump weep-hole check and combustion gas test",
        "واٹر پمپ ویپ ہول اور کمبسشن گیس ٹیسٹ",
        "Coolant loss with no external leak, white exhaust smoke, or bubbles in expansion tank",
        "بغیر بیرونی لیک کے کولنٹ کی کمی، سفید دھواں، یا ایکسپینشن ٹینک میں بلبلے",
        "Pump dry and gas test negative - suspect thermostat / radiator instead",
        "پمپ خشک اور گیس ٹیسٹ منفی - تھرمواسٹیٹ / ریڈی ایٹر مشتبہ"),
    "Worn brake pads / shoes": ('br',
        "Pad thickness measurement (mm remaining)",
        "پیڈ کی موٹائی ناپنا (باقی ملی میٹر)",
        "Pads below ~3mm or wear indicators touching disc",
        "پیڈ ~3 ملی میٹر سے کم یا ویئر اشارے ڈسک کو چھو رہے ہوں",
        "Pads above service limit - noise may be debris or glazed discs",
        "پیڈ سروس حد سے اوپر - آواز ملبہ یا گلیزڈ ڈسک کی ہو سکتی ہے"),
    "Low or leaking brake fluid": ('br',
        "Fluid level check and leak inspection at wheels / master cylinder",
        "فلوئڈ لیول اور وہیلوں / ماسٹر سلنڈر پر لیک معائنہ",
        "Fluid below MIN mark, or wetness at calipers / steel lines",
        "فلوئڈ MIN نشان سے کم، یا کیلیپر / سٹیل لائنوں پر نمی",
        "Fluid at correct level and dry system - pedal issue is mechanical (air in lines)",
        "فلوئڈ صحیح اور نظام خشک - پیڈل مسئلہ میکینیکل ہے"),
    "Warped brake discs": ('br',
        "Disc lateral run-out measurement",
        "ڈسک لیٹرل رن آؤٹ ناپنا",
        "Run-out above ~0.05-0.10mm or pedal pulsation felt under braking",
        "رن آؤٹ ~0.05-0.10 ملی میٹر سے زیادہ یا بریک پر پیڈل دھڑکتا ہے",
        "Run-out within spec - vibration is from tyres / suspension",
        "رن آؤٹ حد میں - کانپنا ٹائرز / سسپنشن کی وجہ ہے"),
    "Sticking brake caliper": ('br',
        "Caliper slide pin movement and piston seal check",
        "کیلیپر سلائیڈ پن حرکت اور پسٹن سیل چیک",
        "Caliper hot to touch after drive, uneven pad wear, car pulls under braking",
        "ڈرائیو کے بعد کیلیپر گرم، پیڈز ناہموار گھسے، گاڑی بریک پر کھنچے",
        "Caliper slides freely and cools evenly - pull is from tyres / alignment",
        "کیلیپر آزادانہ چلے اور یکساں ٹھنڈا ہو - کھنچاؤ ٹائرز / الائنمنٹ کی وجہ"),
    "Worn wheel bearing": ('nv',
        "Wheel bearing play and noise check (11-5 o'clock rocking)",
        "وہیل بیئرنگ پلے اور آواز چیک",
        "Play or growl that changes with cornering direction; noise rises with speed",
        "کونے مڑتے وقت بدلنے والی پلے / گرج جو رفتار کے ساتھ بڑھتی ہے",
        "Bearing tight and quiet - noise is tyre / belt / suspension",
        "بیئرنگ مضبوط اور خاموش - آواز ٹائر / بیلٹ / سسپنشن کی ہے"),
    "Loose or worn serpentine belt": ('nv',
        "Belt tension and wear inspection",
        "بیلٹ ٹینشن اور گھساؤ معائنہ",
        "Glazed / cracked ribs, chirping on cold start, visible slack",
        "چکنی / دراڑیں، سرد سٹارٹ پر چیخ، نمایاں ڈھیلا پن",
        "Belt within service limits - squeal may be pulley bearing or AC compressor",
        "بیلٹ حد میں - چیخ پلی بیئرنگ یا اے سی کمپریسر کی ہو سکتی ہے"),
    "Worn suspension parts": ('nv',
        "Shock absorber bounce test and bush inspection",
        "شاک jis.اولر باؤنس ٹیسٹ اور بش معائنہ",
        "Excessive bounce after pushing down, clunks over bumps, uneven tyre wear",
        "دبانے پر زیادہ اچھال، اونچی نیچی پر ٹھک، ٹائرز ناہموار گھسے",
        "Suspension tight - clunks may be exhaust mounts or subframe",
        "سسپنشن مضبوط - ٹھک ایگزاسٹ ماؤنٹ یا سب فریم کی ہو سکتی ہے"),
    "Engine internal wear (rod knock)": ('nv',
        "Oil pressure test and compression / leak-down test",
        "آئل پریشر ٹیسٹ اور کمپریشن / لیک ڈاؤن ٹیسٹ",
        "Knock louder under load / acceleration, low oil pressure at hot idle",
        "لوڈ / ایکسلیریشن پر کھٹکھٹاہٹ، گرم آئیڈل پر کم آئل پریشر",
        "Oil pressure normal and knock absent on test - could be belt / accessory",
        "آئل پریشر نارمل اور ٹیسٹ میں کھٹکھٹاہٹ نہیں - بیلٹ / اضافی پرزہ پرزہ مشتبہ"),
    "Low engine oil causing noise": ('nv',
        "Dipstick level and condition check",
        "ڈپ اسٹک لیول اور آئل کی حالت",
        "Oil below MIN or very dark / gritty; noise quieter after correct top-up",
        "آئل MIN سے کم یا بہت کالا / ریتلا؛ درست ٹاپ اپ کے بعد آواز کم",
        "Oil at correct level - noise source is mechanical (bearing / belt)",
        "آئل صحیح سطح پر - آواز میکینیکل (بیئرنگ / بیلٹ) کی ہے"),
    "Failing alternator": ('el',
        "Charging system test (voltage with engine running)",
        "چارجنگ سسٹم ٹیسٹ (انجن چلتے وقت وولٹیج)",
        "Charging voltage below ~13.8V or above ~15V, battery light on",
        "چارجنگ وولٹیج ~13.8 سے کم یا ~15 سے زیادہ، بیٹری لائٹ ON",
        "Charging voltage 13.8-14.5V steady - battery or wiring is the issue",
        "چارجنگ وولٹیج 13.8-14.5 مستقل - مسئلہ بیٹری یا وائرنگ کا ہے"),
    "Charging system fault": ('el',
        "Alternator output and serpentine belt tension test",
        "الٹرنیٹر آؤٹ پٹ اور بیلٹ ٹینشن ٹیسٹ",
        "Voltage drops under electrical load (headlights, blower on max)",
        "بجلی کے بوجھ (ہیڈلائٹس، میکسی بلور) پر وولٹیج گرے",
        "Output stable under load - suspect battery cables / grounds",
        "بوجھ میں آؤٹ پٹ مستقل - بیٹری کیبلز / گراؤنڈ مشتبہ"),
    "Weak battery": ('el',
        "Battery load test",
        "بیٹری لوڈ ٹیسٹ",
        "Fails load test or voltage sags below 9.6V during crank",
        "لوڈ ٹیسٹ میں ناکام یا کرینک میں وولٹیج 9.6 سے کم",
        "Battery healthy - dim lights may be alternator / ground issue",
        "بیٹری درست - مدھم لائٹس البرنیٹر / گراؤنڈ کی وجہ ہو سکتی ہیں"),
    "Wiring short / fuse problem": ('el',
        "Parasitic draw test and short tracing",
        "پیرسائٹک ڈراؤ ٹیسٹ اور شارٹ تلاش کرنا",
        "Repeated fuse failure, melted connector, or draw above ~50mA",
        "بار بار فیوز جلنا، پگھلا کنیکٹر، یا ~50mA سے زیادہ ڈراؤ",
        "No draw and fuses hold - fault may be a single failing accessory",
        "ڈراؤ نہیں اور فیوز قائم - خرابی ایک لُٹی پرزے کی ہو سکتی ہے"),
    "Low tyre pressure / slow leak": ('ty',
        "Pressure check on all tyres + soap-water leak test",
        "تمام ٹائرز کا پریشر + صابن پانی لیک ٹیسٹ",
        "Pressure below spec or bubbles forming at sidewall / tread / valve",
        "پریشر سپیسیفکیشن سے کم یا سائیڈ وال / ٹرائیڈ / والو پر بلبلے",
        "All pressures correct and no bubbles - pull may be alignment",
        "تمام پریشرز درست اور بلبلے نہیں - کھنچاؤ الائنمنٹ کی وجہ"),
    "Worn or aged tyres": ('ty',
        "Tread depth measurement and DOT age code check",
        "ٹرائیڈ ڈیپتھ ناپنا اور DOT عمر چیک",
        "Tread below 1.6mm legal limit or tyres older than ~6 years",
        "ٹرائیڈ 1.6 ملی میٹر قانونی حد سے کم یا ٹائر ~6 سال سے پرانے",
        "Tread legal and age acceptable - uneven wear points to alignment / suspension",
        "ٹرائیڈ قانونی اور عمر ٹھیک - ناہموار گھسیو الائنمنٹ / سسپنشن کی وجہ"),
    "Wheel alignment off": ('ty',
        "Four-wheel alignment check (camber, caster, toe)",
        "چاروں پہیوں کی الائنمنٹ چیک",
        "Camber / toe out of spec, uneven inner or outer tread wear",
        "کیمبر / ٹو حد سے باہر، اندرونی یا بیرونی ناہموار گھسیو",
        "Alignment within spec - pull may be a dragging brake caliper",
        "الائنمنٹ حد میں - کھنچاؤ ڈریگنگ بریک کیلیپر کی وجہ"),
    "Wheel out of balance": ('ty',
        "Wheel balancing machine test",
        "وہیل بیلنسنگ مشین ٹیسٹ",
        "Balance weights missing / damaged, vibration only at certain speed",
        "بیلنس وزن غائب / خراب، کانپنا صرف مخصوص رفتار پر",
        "Balance within tolerance - vibration may be bent rim or tyre belt separation",
        "بیلنس حد میں - کانپنا ٹیڑھے رم یا ٹائر بیلٹ کی وجہ"),
    "Engine oil leak": ('ol',
        "UV dye leak detection and visual inspection of gaskets",
        "یووی ڈائی لیک ٹیسٹ اور گسکیٹس کا معائنہ",
        "Dye traces at pan gasket, valve cover, oil filter or rear main seal",
        "پین گسکیٹ، والڈو کور، آئل فلٹر یا ریئر مین سیل پر ڈائی کے نشانات",
        "No dye found and level stable - spots may be old residue",
        "ڈائی نہیں ملی اور لیول مستحکم - دھبے پرانے باقیات ہو سکتے ہیں"),
    "Low engine oil level": ('ol',
        "Dipstick level check and consumption measurement",
        "ڈپ اسٹک لیول اور تیل کی کھپت ناپنا",
        "Oil below MIN or dropping between services (consumption test)",
        "آئل MIN سے کم یا سروسز کے درمیان کم ہونا (کھپت ٹیسٹ)",
        "Level correct and stable - warning light may be sensor fault",
        "لیول درست اور مستحکم - وارننگ لائٹ سینسر کی خرابی ہو سکتی ہے"),
    "Burning oil (seals / rings)": ('ol',
        "Compression / leak-down test and bore scope inspection",
        "کمپریشن / لیک ڈاؤن ٹیسٹ اور بور سکاپ معائنہ",
        "Blue smoke at cold start (valve seals) or under load (rings); low compression",
        "سرد سٹارٹ پر نیلا دھواں (سیل) یا بوجھ میں (رِنگز)؛ کم کمپریشن",
        "Compression even and smoke clears when warm - could be PCV / minor",
        "کمپریشن یکساں اور دھواں گرم ہونے پر بند - PCV / معمولی وجہ"),
    "Low AC gas / gas leak": ('ac',
        "Manifold gauge pressure test and leak check",
        "مینوفولڈ گیج پریشر ٹیسٹ اور لیک چیک",
        "Low-side pressure below spec, oily residue on AC lines / condenser",
        "لو سائیڈ پریشر سپیسیفکیشن سے کم، اے سی لائنوں / کنڈینسر پر تیل نما",
        "Pressures normal - warm air may be compressor clutch or cabin filter",
        "پریشرز نارمل - گرم ہوا کمپریسر کلچ یا کیبن فلٹر کی وجہ"),
    "Blocked cabin air filter": ('ac',
        "Cabin filter visual inspection and airflow measure",
        "کیبن فلٹر بصری معائنہ اور ہوا کی رفتار",
        "Filter clogged with debris/leaves, airflow weak at all fan speeds",
        "فلٹر ملبے / پتوں سے بند، تمام فین اسپیڈز پر ہوا کم",
        "Filter clean - weak airflow points to blower motor / resistor",
        "فلٹر صاف - کم ہوا بلور موٹر / ریزسٹر کی وجہ"),
    "AC compressor fault": ('ac',
        "Compressor clutch engagement and pulley test",
        "کمپریسر کلچ اور پللی ٹیسٹ",
        "Clutch does not engage with AC on, or compressor locked / noisy",
        "اے سی ON پر کلچ نہ لگے، یا کمپریسر جام / شورтиس accidental",
        "Clutch engages and cycles normally - look at gas / condenser",
        "کلچ لگے اور نارمل سائیکل کرے - گیس / کنڈینسر دیکھیں"),
    "Condenser / cooling fault": ('ac',
        "Condenser cleanliness and airflow test",
        "کنڈینسر صفائی اور ہوائ-flow ٹیسٹ",
        "Condenser fins blocked with dirt / bugs, or fan not pulling air",
        "کنڈینسر فنس مٹی / کیڑوں سے بند، یا فین ہوا نہ کھینچے",
        "Condenser clean and airflow good - fault is elsewhere in AC loop",
        "کنڈینسر صاف اور ہوائ-flow ٹھیک - خرابی اے سی لوپ میں کہیں اور"),
    "Low power steering fluid": ('sr',
        "Fluid level check and leak inspection",
        "فلوئڈ لیول اور لیک معائنہ",
        "Fluid below MIN, or wetness at rack / hoses / pump",
        "فلوئڈ MIN سے کم، یا ریک / نلیوں / پمپ پر نمی",
        "Fluid level correct - heavy steering may be tyre pressure / alignment",
        "فلوئڈ لیول درست - بھاری اسٹیئرنگ ٹائر پریشر / الائنمنٹ کی وجہ"),
    "Worn steering linkage": ('sr',
        "Tie rod end and rack boot play test",
        "ٹائی روڈ اینڈ اور ریک بوٹ پلے ٹیسٹ",
        "Clunk over bumps + steering play; boots torn with grease spray",
        "اونچی نیچی پر ٹھک + اسٹیئرنگ پلے؛ پھٹے بوٹس اور گریس کے نشانات",
        "Linkage tight - play may be steering column / rack internal wear",
        "لنکیج مضبوط - پلے اسٹیئرنگ کالم / ریک اندرونی گھسائی کی وجہ"),
    "Power steering pump fault": ('sr',
        "Pump pressure test and belt inspection",
        "پمپ پریشر ٹیسٹ اور بیلٹ معائنہ",
        "Whine that follows steering input, low pump pressure",
        "اسٹیئرنگ ان پٹ کے ساتھ سیٹی، کم پمپ پریشر",
        "Pump pressure normal - noise may be idler pulley bearing",
        "پمپ پریشر نارمل - آواز آئڈلر پللی بیئرنگ کی ہو سکتی ہے"),
    "Wheel alignment / tyre issue": ('sr',
        "Alignment check and tyre inspection",
        "الائنمنٹ چیک اور ٹائر معائنہ",
        "Toe / camber out of spec or uneven tyre wear pattern",
        "ٹو / کیمبر حد سے باہر یا ٹائرز پر ناہموار گھسیو کا نقشہ",
        "Alignment good and tyres even - drift may be road crown / brake drag",
        "الائنمنٹ درست اور ٹائرز یکساں - بھٹکنا سڑک کی ڈھلوان / بریک ڈریگ کی وجہ"),
    "Worn clutch": ('gc',
        "Clutch slip road test and pedal free-play check",
        "کلچ سلپ روڈ ٹیسٹ اور پیڈل فری پلے چیک",
        "RPM rises without matching speed under load; burning smell after slips",
        "بوجھ میں آر پی ایم بڑھے مگر رفتار نہ ملے؛ پھسلنے کے بعد جلنے کی بو",
        "Clutch holds fully - slipping may be low gearbox oil / mount",
        "کلچ مکمل پکڑے - پھسلنا گیئر باکس آئل / ماؤنٹ کی وجہ"),
    "Clutch linkage / hydraulic fault": ('gc',
        "Clutch master / slave cylinder and linkage check",
        "کلچ ماسٹر / سلیو سلنڈر اور لنکیج چیک",
        "Pedal spongy or sticking, clutch not fully disengaging",
        "پیڈل اسپانجی یا اٹکتا، کلچ مکمل الگ نہیں ہوتا",
        "Hydraulics firm - pedal feel issue may be cable stretch / pedal mount",
        "ہائیڈرالکس مضبوط - پیڈل کی블 کھچاؤ / پیڈل ماؤنٹ کی وجہ"),
    "Low gearbox oil / leak": ('gc',
        "Gearbox oil level and condition check",
        "گیئر باکس آئل لیول اور حالت چیک",
        "Oil below spec, burnt smell, or red/brown fluid found under car",
        "آئل سپیسیفکیشن سے کم، جلتی بو، یا گاڑی کے نیچے سرخ / بھورا سیال",
        "Oil correct and dry - shifting issue may be synchros / linkage",
        "آئل درست اور خشک - شفٹنگ سنکرونائزر / لنکیج کی وجہ"),
    "Gearbox gear wear": ('gc',
        "Road test for synchro wear and gear oil inspection",
        "سنکرونائزر گھسائی کا روڈ ٹیسٹ اور گیئر آئل معائنہ",
        "Grinding on downshift, gear pop-out under load",
        "ڈاؤن شفٹ پر رگڑ، بوجھ میں گیئر نکل جانا",
        "Gearbox oil good and no grind on test - could be clutch drag",
        "گیئر باکس آئل درست اور ٹیسٹ میں رگڑ نہیں - کلچ ڈریگ مشتبہ"),
}

# System key for each fault name (fallback when FAULT_INFO missing)
FAULT_SYS = {name: info[0] for name, info in FAULT_INFO.items()}

# =====================================================================
#  FEATURE 1 - INSPECTION ROADMAP PANEL
# =====================================================================
def roadmap_panel(causes, lvl):
    # Personalized mechanic inspection roadmap for the top suspected faults.
    if not causes:
        return
    st.write(t('**Mechanic inspection roadmap**', '**مکینک معائنہ روڈ میپ**'))
    st.caption(t('What a qualified mechanic should check for each suspected fault, in priority order.',
                 'ہر مشتبہ خرابی کے لیے مکینک کو کیا چیک کرنا چاہیے، ترجیح کی ترتیب میں۔'))

    # Priority & drive guidance derived from the urgency level already decided
    if lvl == 'emergency':
        prio_txt = t('IMMEDIATE - do not drive', 'فوری - گاڑی نہ چلائیں')
        drive_ok = False
    elif lvl == 'urgent':
        prio_txt = t('HIGH - see a mechanic today', 'اعلی - آج مکینک کو دکھائیں')
        drive_ok = False
    elif lvl == 'routine':
        prio_txt = t('MEDIUM - this week', 'درمیانہ - اس ہفتے')
        drive_ok = True
    else:
        prio_txt = t('LOW - routine check', 'کم - معمول معائنہ')
        drive_ok = True

    for cause in causes[:3]:
        name_en = cause['name_en']; name_ur = cause['name_ur']
        info = FAULT_INFO.get(name_en)
        sys_key = info[0] if info else FAULT_SYS.get(name_en, 'nv')
        sinfo = SYSTEM_INFO.get(sys_key, SYSTEM_INFO['nv'])
        comp_en, comp_ur, points, tests = sinfo
        L = st.session_state.get('lang', 'en')

        title = (name_ur if L == 'ur' else name_en)
        with st.expander(t(' Inspect: ', ' معائنہ: ') + title + '  (' + str(cause['conf']) + '% ' + t('match', 'میل') + ')', expanded=False):
            st.write(t('**Component / system:** ', '**پرزہ / نظام:** ') + (comp_ur if L == 'ur' else comp_en))
            st.write(t('**Inspection priority:** ', '**معائنہ کی ترجیح:** ') + prio_txt)
            st.write(t('**Drive before inspection?** ', '**معائنہ سے پہلے گاڑی چلائیں؟** ') +
                     (t('No - safety first.', 'نہیں - حفاظت پہلے۔') if not drive_ok else t('Yes, with caution until checked.', 'ہاں، چیک ہونے تک احتیاط سے۔')))
            st.write(t('**Specific test for this fault:** ', '**اس خرابی کا مخصوص ٹیسٹ:** ') +
                     ((info[2] if L == 'ur' else info[1]) if info else t('Standard system tests below', 'نیچے معیاری سسٹم ٹیسٹس')))
            st.write(t('**Inspection points:**', '**معائنہ کے پوائنٹس:**'))
            for p_en, p_ur in points:
                st.write('• ' + (p_ur if L == 'ur' else p_en))
            st.write(t('**Tests a mechanic may perform:**', '**مکینک کے ممکنہ ٹیسٹس:**'))
            for test_en, test_ur in tests:
                st.write('• ' + (test_ur if L == 'ur' else test_en))
            if info:
                st.write(t('**Findings that support this fault:**', '**اس خرابی کی تائید کرنے والے نتائج:**'))
                st.write('• ' + (info[4] if L == 'ur' else info[3]))
                st.write(t('**Findings that would weaken it:**', '**اسے کمزور کرنے والے نتائج:**'))
                st.write('• ' + (info[6] if L == 'ur' else info[5]))
            if cause['missing']:
                st.write(t('**Missing evidence (ask the mechanic to check):**', '**غیر موجود ثبوت (مکینک سے چیک کروائیں):**'))
                for m_en, m_ur in cause['missing'][:3]:
                    st.write('• ' + (m_ur if L == 'ur' else m_en))


# =====================================================================
#  FEATURE 1 - REPAIR VERIFICATION PANEL
# =====================================================================
def verification_panel(causes, complaint, risk, diag_id=None):
    # Record the REAL mechanic inspection outcome. Predictions and
    # mechanic-confirmed results are stored separately and the system
    # never marks a suspected fault as confirmed automatically.
    st.write(t('**Mechanic inspection outcome (repair verification)**', '**مکینک معائنہ کا نتیجہ (مرمت کی تصدیق)**'))
    st.caption(t('Record what the mechanic actually found. This is stored separately from the system predictions above.',
                 'ریکارڈ کریں کہ مکینک کو اصل میں کیا ملا۔ یہ سسٹم کی پیشین گوئیوں سے الگ محفوظ ہوتا ہے۔'))

    names = [c['name_en'] for c in causes[:3]]
    name_urs = {c['name_en']: c['name_ur'] for c in causes[:3]}

    outcome_opts = [t('Fault Confirmed', 'خرابی کی تصدیق ہوئی'),
                    t('Fault Not Found', 'خرابی نہیں ملی'),
                    t('Different Fault Identified', 'کوئی مختلف خرابی ملی'),
                    t('Further Testing Required', 'مزید ٹیسٹنگ درکار')]
    outcome = st.selectbox(t('Inspection outcome', 'معائنہ کا نتیجہ'), outcome_opts, key='ver_outcome')

    conf_fault = ''
    if outcome != outcome_opts[1]:
        choices = [t('Same as top prediction: ', 'ٹاپ پیشین گوئی جیسی: ')] + names
        pick = st.selectbox(t('Which fault was confirmed / found?', 'کون سی خرابی ملی؟'), choices, key='ver_fault')
        if pick != choices[0]:
            conf_fault = pick
        else:
            conf_fault = st.text_input(t('Confirmed / found fault name', 'تصدید شدہ خرابی کا نام'), key='ver_fault_txt')
    else:
        st.text_input(t('Confirmed / found fault name (optional)', 'تصدید شدہ خرابی کا نام (اختیاری)'), key='ver_fault_txt')
        conf_fault = st.session_state.get('ver_fault_txt', '')

    findings = st.text_area(t("Mechanic's inspection findings", 'مکینک کے معائنہ کے نتائج'), key='ver_findings')
    repair = st.text_area(t('Repair / replacement details', 'مرمت / تبدیلی کی تفصیل'), key='ver_repair')
    notes = st.text_area(t('Additional notes', 'اضافی نوٹس'), key='ver_notes')
    insp_date = st.date_input(t('Inspection date', 'معائنہ کی تاریخ'), value=datetime.now().date(), key='ver_date')

    if st.button(t(' Save verification record', ' تصدیقی ریکارڈ محفوظ کریں'), key='ver_save', type='primary'):
        rec = {
            'complaint': complaint,
            'risk_score': risk,
            'predicted_faults': [{'name': c['name_en'], 'confidence': c['conf']} for c in causes[:3]],
            'outcome': outcome,
            'confirmed_fault': conf_fault,
            'findings': findings,
            'repair': repair,
            'notes': notes,
            'inspection_date': insp_date.strftime('%Y-%m-%d'),
            'diagnosis_id': diag_id,
        }
        n = store.append_record('inspections', rec)
        if n > 0:
            st.success(t('Verification record saved (' + str(n) + ' total). It is stored separately from the predictions.',
                         'تصدیقی ریکارڈ محفوظ ہو گیا (کل ' + str(n) + ')۔ یہ پیشین گوئیوں سے الگ محفوظ ہے۔'))
        else:
            st.error(t('Could not save the record. Check the data folder permissions.', 'ریکارڈ محفوظ نہیں ہو سکا۔ data فولڈر کی اجازتیں چیک کریں۔'))

    # Show recent saved records (read-only summary)
    recs = store.load_records('inspections')
    if recs:
        st.write(t('**Saved verification records:**', '**محفوظ شدہ تصدیقی ریکارڈز:**'))
        for i in range(len(recs) - 1, max(-1, len(recs) - 4), -1):
            r = recs[i]
            st.write('• ' + r.get('inspection_date', '') + ' | ' + r.get('complaint', '') +
                     ' | ' + r.get('outcome', '') +
                     (' | ' + r.get('confirmed_fault', '') if r.get('confirmed_fault') else ''))
        if st.button(t(' Delete last record', ' آخری ریکارڈ حذف کریں'), key='ver_del'):
            if store.delete_record('inspections', len(recs) - 1):
                st.rerun()


def records_page():
    # Read-only viewer for saved inspection verifications + diagnosis history.
    st.write('### ' + t(' Saved records', ' محفوظ ریکارڈ'))
    st.caption(t('Saved diagnoses and mechanic verification records stored on this device (data/ folder).',
                 'اس ڈیوائس پر محفوظ تشخیصیں اور مکینک تصدیقی ریکارڈ (data فولڈر)۔'))

    # ---------- DIAGNOSIS HISTORY (SQLite) ----------
    diags = H.list_diagnoses()
    st.markdown("<div class='qcard'><div class='qtext'><b>" + t('Diagnosis history', 'تشخیصی ہسٹری') + "</b></div></div>", unsafe_allow_html=True)
    if not diags:
        st.write(t('No saved diagnoses yet. Finish a consultation and press "Save this diagnosis to history".',
                   'ابھی کوئی محفوظ تشخیص نہیں۔ مشورہ مکمل کریں اور "اس تشخیص کو ہسٹری میں محفوظ کریں" دبائیں۔'))
    ver_recs = store.load_records('inspections')
    for d in diags:
        did = d['id']
        # does a mechanic verification reference this diagnosis?
        ver = [v for v in ver_recs if v.get('diagnosis_id') == did]
        ver_txt = t(' | mechanic verified', ' | مکینک تصدیق شدہ') if ver else ''
        title = d['saved_at'] + ' | #' + str(did) + ' | ' + str(d.get('complaint', '')) + \
                ' | risk ' + str(d.get('risk', 0)) + ' (' + str(d.get('risk_level', '')) + ')' + ver_txt
        with st.expander(title, expanded=False):
            full = H.get_diagnosis(did)
            if not full:
                st.write(t('Record could not be loaded.', 'ریکارڈ لوڈ نہیں ہو سکا۔'))
                continue
            st.write(t('Complaint: ', 'شکایت: ') + str(full.get('complaint', '')))
            st.write(t('Risk score: ', 'رسک اسکور: ') + str(full.get('risk', 0)) + ' - ' + str(full.get('risk_level', '')))
            st.write(t('Saved at: ', 'محفوظ وقت: ') + str(full.get('saved_at', '')))
            st.write('**' + t('User answers:', 'صارف کے جوابات:') + '**')
            for k, v in (full.get('answers') or {}).items():
                st.write('• ' + k + ': ' + str(v))
            st.write('**' + t('Probable faults:', 'مشتبہ خرابیاں:') + '**')
            for c in (full.get('causes') or []):
                st.write('• ' + str(c.get('name', '')) + ' (' + str(c.get('confidence', 0)) + '%)')
            if full.get('report_values'):
                st.write('**' + t('Report values:', 'رپورٹ قدریں:') + '**')
                for k, v in full['report_values'].items():
                    st.write('• ' + k + ': ' + str(v))
            st.write('**' + t('Report text:', 'رپورٹ متن:') + '**')
            st.text_area(t('Diagnosis report', 'تشخیصی رپورٹ'), value=full.get('report_text', ''), height=200, key='hist_rep_' + str(did), disabled=True)
            if ver:
                st.write(t('Linked mechanic verification:', 'منسلک مکینک تصدیق:') + ' ' + ver[0].get('outcome', '') +
                         (' - ' + ver[0].get('confirmed_fault', '') if ver[0].get('confirmed_fault') else ''))
            # delete with confirmation
            cfm = st.checkbox(t('Confirm delete', 'حذف کی تصدیق کریں'), key='del_cfm_' + str(did))
            if st.button(t(' Delete record', ' ریکارڈ حذف کریں'), key='del_diag_' + str(did), disabled=not cfm):
                H.delete_diagnosis(did)
                st.rerun()

    recs = store.load_records('inspections')
    st.markdown("<div class='qcard'><div class='qtext'><b>" + t('Mechanic inspection outcomes', 'مکینک معائنہ کے نتائج') + "</b></div></div>", unsafe_allow_html=True)
    if not recs:
        st.write(t('No verification records yet. Finish a diagnosis and use the "Mechanic inspection outcome" section to save one.',
                   'ابھی کوئی تصدیقی ریکارڈ نہیں۔ تشخیص مکمل کریں اور "مکینک معائنہ کا نتیجہ" سیکشن سے محفوظ کریں۔'))
    for i in range(len(recs) - 1, -1, -1):
        r = recs[i]
        with st.expander((r.get('inspection_date', '') + ' - ' + r.get('complaint', '') + ' (' + r.get('outcome', '') + ')'), expanded=False):
            st.write(t('Predicted faults: ', 'پیش گوئی شدہ خرابیاں: ') +
                     ', '.join(p['name'] + ' (' + str(p['confidence']) + '%)' for p in r.get('predicted_faults', [])))
            st.write(t('Confirmed fault: ', 'تصدیق شدہ خرابی: ') + str(r.get('confirmed_fault', '-') or '-'))
            if r.get('findings'): st.write(t('Findings: ', 'نتائج: ') + r['findings'])
            if r.get('repair'): st.write(t('Repair: ', 'مرمت: ') + r['repair'])
            if r.get('notes'): st.write(t('Notes: ', 'نوٹس: ') + r['notes'])
            st.write(t('Saved: ', 'محفوظ: ') + r.get('saved_at', ''))
            if st.button(t(' Delete this record', ' یہ ریکارڈ حذف کریں'), key='del_insp_' + str(i)):
                store.delete_record('inspections', i)
                st.rerun()
