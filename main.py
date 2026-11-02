import pygame
import sys
import random
import math
import asyncio

pygame.init()
pygame.mixer.init()

# -----------------------------------------
# SOUND EFFECTS AND MUSIC
# -----------------------------------------
try:
    background_music = pygame.mixer.Sound("background_sound.ogg")
    background_music.set_volume(0.3)  # 30% volume for background music
    print("Background music loaded successfully")
except Exception as e:
    print(f"Could not load background music: {e}")
    background_music = None

try:
    hawk_screech = pygame.mixer.Sound("hawk_screech.ogg")
    hawk_screech.set_volume(0.7)
    print("Hawk screech loaded successfully")
except Exception as e:
    print(f"Could not load hawk_screech.ogg: {e}")
    hawk_screech = None

try:
    explosion_sound = pygame.mixer.Sound("explosion.ogg")
    explosion_sound.set_volume(0.7)
    print("Explosion sound loaded successfully")
except Exception as e:
    print(f"Could not load explosion.ogg: {e}")
    explosion_sound = None

try:
    coin_clink = pygame.mixer.Sound("coin_clink.ogg")
    coin_clink.set_volume(0.5)
    print("Coin clink loaded successfully")
except Exception as e:
    print(f"Could not load coin_clink.ogg: {e}")
    coin_clink = None

music_channel = None  # Channel for background music looping

# -----------------------------------------
# WINDOW / BASIC SETUP
# -----------------------------------------
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("WWII Pigeon Courier")

CLOCK = pygame.time.Clock()
FPS = 60

# -----------------------------------------
# COLORS
# -----------------------------------------
SKY = (150, 200, 255)
PARCHMENT = (245, 235, 215)
MILITARY_GREEN = (140, 160, 120)
TEXT_COLOR = (10, 10, 10)
ROAD = (40, 40, 50)
ROAD_EDGE = (120, 120, 120)
BAR_BG = (200, 200, 200)
BAR_FILL_HEALTH = (200, 50, 50)

font = pygame.font.Font(None, 28)
small_font = pygame.font.Font(None, 22)
title_font = pygame.font.Font(None, 56)
large_font = pygame.font.Font(None, 40)
message_font = pygame.font.Font(None, 20)  # For historical messages only

# -----------------------------------------
# STATES
# -----------------------------------------
STATE_HOME = "home"
STATE_MENU = "menu"
STATE_PLAY = "play"
STATE_LEVEL_COMPLETE = "level_complete"
STATE_MESSAGE = "message"
STATE_VICTORY = "victory"
STATE_STORE = "store"
STATE_SETTINGS = "settings"

MODE_STORY = "story"
MODE_ENDLESS = "endless"

game_state = STATE_HOME
current_mode = None
current_level = 0
completed_levels = set()

# -----------------------------------------
# PERSISTENT COIN COUNTER (NEVER RESETS)
# -----------------------------------------
total_coins_collected = 0

# -----------------------------------------
# SETTINGS / PAUSE
# -----------------------------------------
sound_on = True
music_on = True

def update_background_music():
    """Start or stop background music based on music_on setting"""
    global music_channel
    if music_on and background_music:
        if music_channel is None or not pygame.mixer.get_busy():
            music_channel = background_music.play(loops=-1)  # Loop indefinitely
    else:
        if music_channel is not None:
            background_music.stop()
            music_channel = None

def play_sound_effect(sound):
    """Play a sound effect if sound_on is True"""
    if sound_on and sound:
        sound.play()

# Pause button in top-right corner
settings_button_rect = pygame.Rect(WIDTH - 60, 10, 50, 50)

# Settings menu layout
settings_menu_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 175, 400, 350)
settings_resume_button = pygame.Rect(settings_menu_rect.centerx - 150, settings_menu_rect.top + 80, 300, 40)
settings_home_button = pygame.Rect(settings_menu_rect.centerx - 150, settings_menu_rect.top + 130, 300, 40)
settings_restart_button = pygame.Rect(settings_menu_rect.centerx - 150, settings_menu_rect.top + 180, 300, 40)
settings_sound_button = pygame.Rect(settings_menu_rect.centerx - 150, settings_menu_rect.top + 230, 300, 40)
settings_music_button = pygame.Rect(settings_menu_rect.centerx - 150, settings_menu_rect.top + 280, 300, 40)


# -----------------------------------------
# HISTORICAL MESSAGES
# -----------------------------------------
MESSAGES = [
    {
        "level": 1,
        "title": "Level 1: V-2 Rocket Site Discovery",
        "message": "LARGE ROCKETS OBSERVED PEENEMUNDE FACILITY. UNUSUAL LAUNCH RAILS. HEAVY SECURITY.",
        "context": "Discovery of Nazi V-2 rocket development sites was one of the highest intelligence priorities for the Allies in 1943-1944. Polish resistance members, forced laborers, and German defectors provided crucial intelligence about these secret weapons that were being developed to bombard London. The remote location of facilities like Peenemünde on the Baltic coast made radio contact unreliable, and the extreme security measures meant wireless operators couldn't get close enough. Pigeons carrying microfilm photographs and detailed observations allowed Allied photo reconnaissance and bombing raids to target these facilities. This intelligence campaign delayed the V-2 program and reduced the eventual impact of these weapons on British cities."
    },
    {
        "level": 2,
        "title": "Level 2: SOE Agent in France",
        "message": "SAFE HOUSE COMPROMISED. GESTAPO RAID IMMINENT. NEED IMMEDIATE EXTRACTION POINT CHARLIE.",
        "context": "Special Operations Executive (SOE) agents working with French Resistance cells behind enemy lines often relied on pigeons when their radio operators were captured or wireless sets were destroyed. This type of urgent message would have been sent from occupied France between 1941-1944. The Gestapo actively hunted resistance networks, and radio transmissions could be triangulated within minutes. Pigeons provided a one-way communication method that was undetectable and could reach England in hours. Failed extractions meant torture and execution, making these messages literally life-or-death communications."
    },
    {
        "level": 3,
        "title": "Level 3: Coastal Defense Intelligence",
        "message": "NEW ATLANTIC WALL FORTIFICATIONS OBSERVED OMAHA SECTOR. TWELVE BUNKERS. DETAILED SKETCH ATTACHED.",
        "context": "French resistance members and British intelligence officers conducted reconnaissance of Nazi coastal defenses throughout 1943-1944 in preparation for D-Day. These civilians and agents risked execution if caught near restricted military zones. Pigeons carried crucial intelligence including sketches, photographs on microfilm, and coded messages about German defensive positions. This intelligence helped Allied planners understand what their troops would face on landing beaches. The Omaha Beach sector had particularly formidable defenses, and advance intelligence saved countless lives by allowing for adjusted naval bombardment targets and assault plans."
    },
    {
        "level": 4,
        "title": "Level 4: Battle of Monte Cassino",
        "message": "MONASTERY OCCUPIED BY GERMAN PARATROOPERS. HEAVY MACHINE GUN POSITIONS. NO CIVILIANS PRESENT.",
        "context": "During the brutal four-month Battle of Monte Cassino (January-May 1944), Allied forces needed to confirm whether German troops were actually using the historic monastery as a defensive position. Italian locals and reconnaissance patrols sent this type of intelligence via pigeon when forward positions were cut off from communication lines by German artillery. The controversial decision to bomb the monastery was partly based on intelligence confirming military occupation. Pigeons were particularly valuable in the mountainous terrain where radio signals were blocked and telephone lines were constantly cut by shellfire. Messages confirming the absence of civilians helped commanders make difficult targeting decisions."
    },
    {
        "level": 5,
        "title": "Level 5: D-Day Reconnaissance",
        "message": "FIVE PANZERS OBSERVED MOVING EAST FROM CAEN. ROAD CLEAR AT PEGASUS BRIDGE 0600 HOURS.",
        "context": "This message would have been sent by British airborne troops or Special Air Service (SAS) scouts operating behind enemy lines during the D-Day invasion of Normandy, June 6, 1944. Pigeons were essential when radios failed or when radio silence was mandatory to avoid detection by German direction-finding units. Intelligence about Panzer tank movements was critical for Allied commanders planning breakthrough operations, as German armor could quickly counterattack landing zones. Messages like this helped prevent Allied forces from walking into ambushes and allowed commanders to redirect units or call in air support."
    },
    {
        "level": 6,
        "title": "Level 6: Downed Bomber Crew",
        "message": "AIRCRAFT DOWN GRID 4729. SEVEN CREW ALIVE. GERMANS SEARCHING AREA. SEND NIGHT PICKUP.",
        "context": "RAF and USAAF bomber crews shot down over occupied Europe often carried pigeons in their aircraft specifically for this purpose. Between 1942-1945, thousands of airmen were shot down over France, Belgium, and the Netherlands. If they survived the crash and evaded immediate capture, pigeons were their best hope of contacting rescue networks. The message would alert MI9 (British escape and evasion organization) or its American counterpart, who would then coordinate with resistance networks for extraction. Speed was critical—German search parties typically arrived within hours, and the longer crews remained at large, the greater the danger to civilians hiding them."
    },
    {
        "level": 7,
        "title": "Level 7: Liberation of Paris",
        "message": "FRENCH FORCES CONTROL CITY HALL. GERMAN GARRISON WITHDRAWING. BRIDGES STILL STANDING.",
        "context": "During the Liberation of Paris (August 19-25, 1944), French Resistance forces inside the city needed to communicate with approaching Allied units about which areas were secure and which were still contested. General Dietrich von Choltitz had orders to destroy Paris's bridges and landmarks if the city couldn't be held. Intelligence that bridges remained intact was crucial for Allied armored divisions planning their entry routes. Radio communication was sporadic as the city's infrastructure was damaged from fighting, and German forces still controlled key telephone exchanges. Pigeons provided resistance fighters with a reliable means to coordinate with Free French forces and prevented Allied commanders from making costly assumptions about German defensive positions."
    },
    {
        "level": 8,
        "title": "Level 8: Battle of Arnhem",
        "message": "BRIDGE TOO FAR. SURROUNDED. AMMUNITION CRITICAL. REQUEST SUPPLY DROP GRID 6842.",
        "context": "British paratroopers at the Battle of Arnhem (Operation Market Garden, September 1944) faced a communications disaster when most radio sets were damaged during the drop or couldn't reach headquarters due to unexpected German interference. Pigeons became the primary means of calling for desperately needed supplies and reinforcements. The phrase 'bridge too far' would later become synonymous with this failed operation. Over 10,000 Allied troops were trapped, and supply drops often missed their targets. Messages like this tried to coordinate drops more precisely, though many pigeons were killed by German fire or exhausted birds never made it across the Rhine."
    },
    {
        "level": 9,
        "title": "Level 9: Italian Partisan Intelligence",
        "message": "GERMAN 26TH DIVISION WITHDRAWING THROUGH GOTHIC LINE. BRIDGE INTACT AT RIVER SENIO.",
        "context": "Italian partisans operating in the Apennine Mountains (1944-1945) provided vital intelligence to Allied forces advancing north through Italy. The Gothic Line was Germany's last major defensive position, and knowing troop movements and which bridges remained intact was essential for Allied planning. Partisans often operated in areas where radio contact was impossible due to mountainous terrain or German radio detection units. Pigeons were supplied to partisan groups by British liaison officers and were trained to fly to mobile lofts behind Allied lines. This intelligence allowed Allied commanders to exploit weaknesses in the German withdrawal and prevented their own forces from walking into prepared defensive positions."
    },
    {
        "level": 10,
        "title": "Level 10: Holland Famine Intelligence",
        "message": "CIVILIAN POPULATION STARVING. FOOD STOCKS DEPLETED. REQUEST MERCY DROPS WEST HOLLAND.",
        "context": "During the 'Hongerwinter' (Hunger Winter) of 1944-1945, the Nazi-occupied western Netherlands faced mass starvation after German forces blocked food supplies in retaliation for a railway strike. Dutch resistance members risked their lives to send messages about the desperate humanitarian situation to Allied headquarters in liberated southern Holland and England. This intelligence directly led to Operation Manna/Chowhound in late April 1945, where Allied bombers dropped food instead of bombs to Dutch civilians. Over 3 million people were affected by the famine, and an estimated 20,000 died. Messages like this one, carried by pigeons through German-occupied territory, were instrumental in organizing the relief effort that saved countless lives in the war's final weeks."
    }
]

# -----------------------------------------
# BACKGROUND IMAGES
# -----------------------------------------
# Removed background1.png, background2.png, background3.png
# Endless mode now uses unlocked level backgrounds

# -----------------------------------------
# STORY MODE LEVEL BACKGROUNDS
# -----------------------------------------
level_backgrounds = {}

level_bg_files = {
    1: "level_one_image.jpg",
    2: "level_two_image.jpg",
    3: "level_three_image.jpg",
    4: "level_four_image.jpg",
    5: "level_five_image.jpg",
    6: "level_six_image.jpg",
    7: "level_seven_image.jpg",
    8: "level_eight_image.jpg",
    9: "level_nine_image.jpg",
    10: "level_ten_image.jpg",
}

for lvl, fname in level_bg_files.items():
    try:
        img = pygame.image.load(fname).convert()
        orig_w, orig_h = img.get_width(), img.get_height()
        scale = max(WIDTH / orig_w, (HEIGHT * 3) / orig_h)
        new_w, new_h = int(orig_w * scale), int(orig_h * scale)
        img = pygame.transform.smoothscale(img, (new_w, new_h))
        level_backgrounds[lvl] = img
    except pygame.error:
        level_backgrounds[lvl] = None

# Load home screen and level select screen
try:
    home_screen_img = pygame.transform.scale(
        pygame.image.load("homescreen.jpg").convert(), (WIDTH, HEIGHT)
    )
except:
    home_screen_img = None

try:
    level_screen_img = pygame.transform.scale(
        pygame.image.load("level_main_screen.jpg").convert(), (WIDTH, HEIGHT)
    )
except:
    level_screen_img = None

try:
    medal_img = pygame.transform.scale(
        pygame.image.load("medal.png").convert_alpha(), (200, 200)
    )
except:
    medal_img = None

current_bg_level = 1  # Tracks which level background to use for endless mode
bg_scroll_y = 0
bg_zoom_offset_y = 0


def get_available_backgrounds():
    """Get list of level backgrounds available based on completed levels"""
    available = [1]  # Level 1 always available
    for level in completed_levels:
        if level <= 10:
            available.append(level)
    return available


def draw_background():
    global bg_scroll_y, bg_zoom_offset_y, level_backgrounds, background_loops_completed, difficulty_level
    
    # Determine which background to use
    if current_mode == MODE_STORY and current_level > 0:
        bg_level = current_level
    elif current_mode == MODE_ENDLESS:
        bg_level = current_bg_level
    else:
        # Default to level 1 background for home/menu screens
        bg_level = 1
    
    # Use the selected level background
    if level_backgrounds.get(bg_level):
        img = level_backgrounds[bg_level]
    else:
        # Fallback: use level 1 background if requested background doesn't exist
        img = level_backgrounds.get(1)
        if not img:
            # Ultimate fallback if even level 1 doesn't exist
            WIN.fill(SKY)
            return
    
    img_height = img.get_height()
    img_width = img.get_width()
    
    max_pan = max(img_height - HEIGHT, 0)

    if current_mode == MODE_STORY and LEVEL_DISTANCE > 0:
        # Story mode: scroll based on progress (bottom to top)
        progress = max(0.0, min(1.0, distance_traveled / LEVEL_DISTANCE))
        scroll_y = int((1.0 - progress) * max_pan)
    else:
        # Endless mode: continuous upward scrolling at same speed as story mode (bottom to top)
        if max_pan > 0:
            # Track previous position to detect loop completion
            prev_scroll_y = int((max_pan - (bg_scroll_y - 0.25)) % max_pan) if bg_scroll_y > 0.25 else 0
            scroll_y = int((max_pan - bg_scroll_y) % max_pan)
            
            # Detect when background loops (goes from bottom back to top)
            if prev_scroll_y < scroll_y:
                background_loops_completed += 1
                difficulty_level = min(10, background_loops_completed + 1)  # Cap at level 10
        else:
            scroll_y = 0
        bg_scroll_y += 0.25  # Scroll speed matched to story mode (was 2, now 0.25)

    x_offset = -(img_width - WIDTH) // 2
    WIN.blit(img, (x_offset, -scroll_y))


# -----------------------------------------
# PIGEON SPRITES
# -----------------------------------------
PIGEON_FRAMES = ["pigeon_fly_1.png", "pigeon_fly_2.png", "pigeon_fly_3.png"]

pigeon_frames = []
for f in PIGEON_FRAMES:
    img = pygame.image.load(f).convert_alpha()
    scale = 1.0
    w, h = int(img.get_width() * scale), int(img.get_height() * scale)
    pigeon_frames.append(pygame.transform.smoothscale(img, (w, h)))

pigeon_left = pygame.transform.smoothscale(
    pygame.image.load("pigeon_fly_left.png").convert_alpha(),
    (pigeon_frames[0].get_width(), pigeon_frames[0].get_height())
)

pigeon_right = pygame.transform.smoothscale(
    pygame.image.load("pigeon_fly_right.png").convert_alpha(),
    (pigeon_frames[0].get_width(), pigeon_frames[0].get_height())
)

pigeon_anim_index = 0.0
PIGEON_ANIM_SPEED = 0.20

pigeon_lean_dir = 0
pigeon_lean_amount = 0.0
LEAN_SMOOTHING = 0.12

# -----------------------------------------
# LANE SYSTEM
# -----------------------------------------
LANE_COUNT = 6
center_x = WIDTH // 2

BOTTOM_LANE_SPACING = 150
TOP_LANE_SPACING = 70

TOP_Y = -300
BOTTOM_Y = HEIGHT + 200


def scale_factor_from_y(y):
    t = (y - TOP_Y) / (BOTTOM_Y - TOP_Y)
    return 0.4 + max(0, min(1, t)) * (1.8 - 0.4)


def lane_x_for_lane(lane_f, y):
    lane_f = max(0, min(LANE_COUNT - 1, lane_f))
    t = max(0, min(1, (y - TOP_Y) / (BOTTOM_Y - TOP_Y)))
    offset = lane_f - (LANE_COUNT - 1) / 2
    x_top = center_x + offset * TOP_LANE_SPACING
    x_bottom = center_x + offset * BOTTOM_LANE_SPACING
    return int(x_top * (1 - t) + x_bottom * t)


# -----------------------------------------
# PIGEON MOVEMENT
# -----------------------------------------
pigeon_width, pigeon_height = pigeon_frames[0].get_width(), pigeon_frames[0].get_height()
pigeon_y = HEIGHT - 220

pigeon_lane_pos = (LANE_COUNT - 1) / 2
pigeon_lane_target = pigeon_lane_pos
LANE_CHANGE_SPEED = 0.18


def update_pigeon_lane():
    global pigeon_lane_pos
    if abs(pigeon_lane_pos - pigeon_lane_target) < LANE_CHANGE_SPEED:
        pigeon_lane_pos = pigeon_lane_target
    elif pigeon_lane_pos < pigeon_lane_target:
        pigeon_lane_pos += LANE_CHANGE_SPEED
    else:
        pigeon_lane_pos -= LANE_CHANGE_SPEED


def pigeon_rect():
    x_center = lane_x_for_lane(pigeon_lane_pos, pigeon_y)
    return pygame.Rect(x_center - pigeon_width // 2, pigeon_y, pigeon_width, pigeon_height)


def is_in_pigeon_lane(item_lane, item_y):
    """Check if an item is in the same lane as the pigeon and close enough vertically"""
    # Get the pigeon's current lane (rounded to nearest integer)
    pigeon_current_lane = round(pigeon_lane_pos)
    
    # Check if lanes match
    if item_lane != pigeon_current_lane:
        return False
    
    # Check if item is close enough vertically (within collision range)
    vertical_distance = abs(item_y - pigeon_y)
    collision_threshold = 40  # pixels - adjust for collision sensitivity
    
    return vertical_distance < collision_threshold


# -----------------------------------------
# HEALTH / SCORE SYSTEM
# -----------------------------------------
health = 1.0
score = 0
coins = 0
distance_traveled = 0
lives = 3
LEVEL_DISTANCE = 30000


def draw_health_bar():
    bar_x, bar_y = 20, 60
    bar_w, bar_h = 260, 16
    
    # Draw semi-transparent white background
    bg_padding = 5
    bg_rect = pygame.Rect(bar_x - bg_padding, bar_y - 30, bar_w + bg_padding * 2, bar_h + 34)
    bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
    bg_surface.set_alpha(128)  # 50% opacity
    bg_surface.fill((255, 255, 255))
    WIN.blit(bg_surface, (bg_rect.x, bg_rect.y))

    pygame.draw.rect(WIN, BAR_BG, (bar_x, bar_y, bar_w, bar_h), border_radius=5)

    fill_w = int(bar_w * max(0, min(1, health)))
    pygame.draw.rect(WIN, BAR_FILL_HEALTH, (bar_x, bar_y, fill_w, bar_h), border_radius=5)
    pygame.draw.rect(WIN, TEXT_COLOR, (bar_x, bar_y, bar_w, bar_h), 2, border_radius=5)

    health_display = max(0, int(health * 100))
    WIN.blit(font.render(f"Health: {health_display}%", True, TEXT_COLOR), (bar_x, bar_y - 24))


def draw_lives():
    heart_x, heart_y = 20, 20
    heart_size = 18
    spacing = heart_size+6
    
    for i in range(3):
        base_x = heart_x + i * spacing

        if i < lives:
            pygame.draw.circle(WIN, (200, 50, 50), (base_x, heart_y), heart_size // 2)
            pygame.draw.circle(WIN, (200, 50, 50), (base_x + heart_size // 2, heart_y), heart_size // 2)
            points = [
                (base_x - heart_size // 2, heart_y),
                (base_x + heart_size, heart_y),
                (base_x + heart_size // 4, heart_y + heart_size)
            ]
            pygame.draw.polygon(WIN, (200, 50, 50), points)
        else:
            pygame.draw.circle(WIN, (150, 150, 150), (base_x, heart_y), heart_size // 2, 2)
            pygame.draw.circle(WIN, (150, 150, 150), (base_x + heart_size // 2, heart_y), heart_size // 2, 2)
            points = [
                (base_x - heart_size // 2, heart_y),
                (base_x + heart_size, heart_y),
                (base_x + heart_size // 4, heart_y + heart_size)
            ]
            pygame.draw.polygon(WIN, (150, 150, 150), points, 2)


def draw_level_progress():
    bar_x, bar_y = 20, 100
    bar_w, bar_h = 260, 16
    
    # Draw semi-transparent white background
    bg_padding = 5
    bg_rect = pygame.Rect(bar_x - bg_padding, bar_y - 30, bar_w + bg_padding * 2, bar_h + 34)
    bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
    bg_surface.set_alpha(128)  # 50% opacity
    bg_surface.fill((255, 255, 255))
    WIN.blit(bg_surface, (bg_rect.x, bg_rect.y))

    pygame.draw.rect(WIN, BAR_BG, (bar_x, bar_y, bar_w, bar_h), border_radius=5)

    progress = min(1.0, distance_traveled / LEVEL_DISTANCE)
    fill_w = int(bar_w * progress)
    pygame.draw.rect(WIN, (50, 150, 200), (bar_x, bar_y, fill_w, bar_h), border_radius=5)
    pygame.draw.rect(WIN, TEXT_COLOR, (bar_x, bar_y, bar_w, bar_h), 2, border_radius=5)

    meters_traveled = distance_traveled
    meters_text = f"Distance: {int(meters_traveled)} / 30000 m"
    WIN.blit(font.render(meters_text, True, TEXT_COLOR), (bar_x, bar_y - 24))


def draw_score_and_coins():
    padding = 20
    safe_right = settings_button_rect.left - padding

    score_surf = font.render(f"Score: {score}", True, TEXT_COLOR)
    coins_surf = font.render(f"Coins: {coins}", True, TEXT_COLOR)
    
    # Calculate the background box size
    max_width = max(score_surf.get_width(), coins_surf.get_width())
    bg_padding = 10
    bg_rect = pygame.Rect(safe_right - max_width - bg_padding, 15, max_width + bg_padding * 2, 50)
    
    # Draw semi-transparent white background
    bg_surface = pygame.Surface((bg_rect.width, bg_rect.height))
    bg_surface.set_alpha(128)  # 50% opacity
    bg_surface.fill((255, 255, 255))
    WIN.blit(bg_surface, (bg_rect.x, bg_rect.y))

    WIN.blit(score_surf, (safe_right - score_surf.get_width(), 20))
    WIN.blit(coins_surf, (safe_right - coins_surf.get_width(), 50))


def draw_settings_button():
    pygame.draw.rect(WIN, MILITARY_GREEN, settings_button_rect, border_radius=8)
    pygame.draw.rect(WIN, TEXT_COLOR, settings_button_rect, 2, border_radius=8)

    cx, cy = settings_button_rect.center
    bar_width = 6
    bar_height = 24
    gap = 8

    left_rect = pygame.Rect(cx - gap // 2 - bar_width, cy - bar_height // 2, bar_width, bar_height)
    right_rect = pygame.Rect(cx + gap // 2, cy - bar_height // 2, bar_width, bar_height)

    pygame.draw.rect(WIN, TEXT_COLOR, left_rect, border_radius=3)
    pygame.draw.rect(WIN, TEXT_COLOR, right_rect, border_radius=3)


# -----------------------------------------
# ITEMS / ENEMIES / HAZARDS
# -----------------------------------------
WORLD_SPEED = 8

# Difficulty system
difficulty_level = 1
background_loops_completed = 0


def scale_item(img, s):
    return pygame.transform.smoothscale(img, (int(img.get_width() * s), int(img.get_height() * s)))


worm_img = scale_item(pygame.image.load("worm.png").convert_alpha(), 1.0)
medpack_img = scale_item(pygame.image.load("medpack.png").convert_alpha(), 1.0)
coin_img = scale_item(pygame.image.load("coin.png").convert_alpha(), 1.0)

# Hawk animation frames for gameplay
hawk_frame_1 = scale_item(pygame.image.load("hawk_one.png").convert_alpha(), 1.0)
hawk_frame_2 = scale_item(pygame.image.load("hawk_two.png").convert_alpha(), 1.0)
hawk_frames = [hawk_frame_1, hawk_frame_2]

# Hawk death screen image (different from animation)
hawk_base = pygame.image.load("hawk.png").convert_alpha()
hb_w, hb_h = hawk_base.get_width(), hawk_base.get_height()
scale = min(WIDTH / hb_w, HEIGHT / hb_h)
hawk_big = pygame.transform.smoothscale(hawk_base, (int(hb_w * scale), int(hb_h * scale)))

flak_frames = [
    scale_item(pygame.image.load("flak_1.png").convert_alpha(), 1.0),
    scale_item(pygame.image.load("flak_2.png").convert_alpha(), 1.0),
]
flak_big = pygame.transform.scale(
    pygame.image.load("flak_3.png").convert_alpha(),
    (WIDTH, HEIGHT),
)


def get_current_difficulty():
    """Get the current difficulty level (1-10)"""
    if current_mode == MODE_STORY:
        return current_level
    else:  # MODE_ENDLESS
        return difficulty_level


def get_spawn_timers_for_difficulty(diff):
    """Return spawn intervals based on difficulty level.
    Level 1 is easiest, Level 10 is hardest."""
    # Base intervals for level 1 (easiest - much longer intervals)
    base_hawk_interval = 300  # frames between hawk spawns (5 seconds at 60 FPS)
    base_flak_interval = 350  # frames between flak spawns
    
    # Calculate intervals based on difficulty (decrease as level increases)
    # Level 1: 300 frames (5 sec), Level 10: 120 frames (2 sec)
    hawk_interval = max(120, base_hawk_interval - (diff - 1) * 20)
    flak_interval = max(140, base_flak_interval - (diff - 1) * 23)
    
    return hawk_interval, flak_interval


def get_max_hazards_for_difficulty(diff):
    """Return max number of hawks and flaks allowed on screen at once.
    Level 1 only allows 1 of each, scaling up to 3/2 at level 10."""
    if diff <= 2:
        return 1, 1  # Level 1-2: max 1 hawk, 1 flak
    elif diff <= 4:
        return 2, 1  # Level 3-4: max 2 hawks, 1 flak
    elif diff <= 7:
        return 2, 2  # Level 5-7: max 2 hawks, 2 flaks
    else:
        return 3, 2  # Level 8-10: max 3 hawks, 2 flaks


def get_item_spawn_rate_for_difficulty(diff):
    """Return the probability of spawning each item type based on difficulty.
    Returns (worm_prob, medpack_prob, coin_prob)"""
    # Level 1: More health items, fewer coins
    # Level 10: Fewer health items, more coins (more challenging)
    
    if diff <= 3:
        return (0.50, 0.25, 0.25)  # 50% worm, 25% medpack, 25% coin
    elif diff <= 6:
        return (0.40, 0.20, 0.40)  # 40% worm, 20% medpack, 40% coin
    else:
        return (0.30, 0.15, 0.55)  # 30% worm, 15% medpack, 55% coin


def choose_safe_lane(blocked_lane):
    """Choose a random lane, optionally avoiding a blocked lane"""
    if blocked_lane is None:
        return random.randint(0, LANE_COUNT - 1)
    
    lane = random.randint(0, LANE_COUNT - 1)
    while lane == blocked_lane:
        lane = random.randint(0, LANE_COUNT - 1)
    return lane


def spawn_worm(blocked_lane=None):
    lane = choose_safe_lane(blocked_lane)
    return {"type": "worm", "lane": lane, "y": TOP_Y - random.randint(50, 200)}


def spawn_medpack(blocked_lane=None):
    lane = choose_safe_lane(blocked_lane)
    return {"type": "medpack", "lane": lane, "y": TOP_Y - random.randint(50, 200)}


def spawn_coin(blocked_lane=None):
    lane = choose_safe_lane(blocked_lane)
    return {"type": "coin", "lane": lane, "y": TOP_Y - random.randint(50, 200)}


def spawn_hawk():
    lane = random.randint(0, LANE_COUNT - 1)
    y = TOP_Y - random.randint(100, 300)
    return {"lane": lane, "y": y, "frame": 0, "timer": 0}


def spawn_flak():
    lane = random.randint(0, LANE_COUNT - 1)
    return {"lane": lane, "y": TOP_Y - random.randint(100, 300), "frame": 0, "timer": 0}


items = []
hawks = []
flaks = []

# -----------------------------------------
# HOME SCREEN
# -----------------------------------------
start_button = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 20, 300, 60)
endless_button_home = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 100, 300, 60)
store_button_home = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 180, 300, 60)


def draw_home_screen():
    if home_screen_img:
        WIN.blit(home_screen_img, (0, 0))
    else:
        WIN.fill(PARCHMENT)
        title = title_font.render("WWII Pigeon Courier", True, TEXT_COLOR)
        WIN.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100)))

    pygame.draw.rect(WIN, MILITARY_GREEN, start_button, border_radius=10)
    pygame.draw.rect(WIN, TEXT_COLOR, start_button, 2, border_radius=10)
    WIN.blit(
        large_font.render("STORY MODE", True, TEXT_COLOR),
        large_font.render("STORY MODE", True, TEXT_COLOR).get_rect(center=start_button.center),
    )

    pygame.draw.rect(WIN, MILITARY_GREEN, endless_button_home, border_radius=10)
    pygame.draw.rect(WIN, TEXT_COLOR, endless_button_home, 2, border_radius=10)
    WIN.blit(
        large_font.render("ENDLESS FLIGHT", True, TEXT_COLOR),
        large_font.render("ENDLESS FLIGHT", True, TEXT_COLOR).get_rect(center=endless_button_home.center),
    )

    pygame.draw.rect(WIN, MILITARY_GREEN, store_button_home, border_radius=10)
    pygame.draw.rect(WIN, TEXT_COLOR, store_button_home, 2, border_radius=10)
    WIN.blit(
        large_font.render("THE COOP", True, TEXT_COLOR),
        large_font.render("THE COOP", True, TEXT_COLOR).get_rect(center=store_button_home.center),
    )

    pygame.display.update()


# -----------------------------------------
# STORE
# -----------------------------------------
store_back_button = pygame.Rect(20, 20, 100, 40)


def draw_store():
    WIN.fill(PARCHMENT)

    pygame.draw.rect(WIN, MILITARY_GREEN, store_back_button, border_radius=8)
    pygame.draw.rect(WIN, TEXT_COLOR, store_back_button, 2, border_radius=8)
    WIN.blit(
        small_font.render("BACK", True, TEXT_COLOR),
        small_font.render("BACK", True, TEXT_COLOR).get_rect(center=store_back_button.center),
    )

    title = title_font.render("THE COOP", True, TEXT_COLOR)
    WIN.blit(title, title.get_rect(center=(WIDTH // 2, 60)))

    subtitle = font.render("Pigeon Outfitter", True, TEXT_COLOR)
    WIN.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, 110)))

    total_coins_display = large_font.render(f"Total Coins Collected: {total_coins_collected}", True, TEXT_COLOR)
    WIN.blit(total_coins_display, total_coins_display.get_rect(center=(WIDTH // 2, 160)))

    current_coins_display = font.render(f"Current Run: {coins}", True, TEXT_COLOR)
    WIN.blit(current_coins_display, current_coins_display.get_rect(center=(WIDTH // 2, 200)))

    coming_soon = font.render("Coming Soon!", True, TEXT_COLOR)
    WIN.blit(coming_soon, coming_soon.get_rect(center=(WIDTH // 2, 280)))

    info = small_font.render("Outfit your pigeon with hats, scarves, and more!", True, TEXT_COLOR)
    WIN.blit(info, info.get_rect(center=(WIDTH // 2, 320)))

    pygame.display.update()


# -----------------------------------------
# LEVEL COMPLETE SCREEN
# -----------------------------------------
def draw_level_complete():
    draw_background()
    
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    WIN.blit(overlay, (0, 0))
    
    msg = title_font.render("MESSAGE DELIVERED!", True, (255, 255, 255))
    WIN.blit(msg, msg.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
    
    pygame.display.update()


# -----------------------------------------
# VICTORY SCREEN
# -----------------------------------------
PDSA_INFO = {
    "intro": "The PDSA Dickin Medal is the highest award any animal can receive for military service. It recognizes acts of gallantry and devotion to duty displayed by animals serving with British armed forces or civil services.",
    "pigeons": [
        "Cher Ami (1918) - Despite being shot and losing an eye and leg, this pigeon delivered a message that saved 194 soldiers of the 'Lost Battalion' in WWI.",
        "G.I. Joe (1943) - Flew 20 miles in 20 minutes to prevent the bombing of an Italian village held by British forces, saving over 1,000 lives.",
        "Paddy (1944) - First pigeon to arrive back with news of the D-Day landings from Normandy, beating all other messenger services.",
        "William of Orange (1944) - Delivered vital intelligence from the Arnhem operation despite being injured by a hawk during flight."
    ]
}


level_buttons = []

BTN_W, BTN_H = 120, 100
COLS = 5
SPACING_X = 20     # horizontal gap between buttons
SPACING_Y = 30     # vertical gap between rows

# Total width of the whole grid (5 buttons + 4 gaps)
grid_width = COLS * BTN_W + (COLS - 1) * SPACING_X

# Left edge so the grid is centered
grid_left = (WIDTH - grid_width) // 2

top_y = 150  # top position of the first row

for i in range(10):
    row = i // COLS
    col = i % COLS

    x = grid_left + col * (BTN_W + SPACING_X)
    y = top_y + row * (BTN_H + SPACING_Y)

    level_buttons.append(pygame.Rect(x, y, BTN_W, BTN_H))

# ENDLESS BUTTON FOR LEVEL MENU - FIXED: This was missing!
endless_button_menu = pygame.Rect(WIDTH // 2 - 150, HEIGHT - 100, 300, 60)

back_button = pygame.Rect(20, 20, 100, 40)


def is_level_unlocked(level_num):
    if level_num == 1:
        return True
    return (level_num - 1) in completed_levels


def draw_level_menu():
    if level_screen_img:
        WIN.blit(level_screen_img, (0, 0))
    else:
        WIN.fill(PARCHMENT)

    title = large_font.render("Select Mission", True, TEXT_COLOR)
    WIN.blit(title, title.get_rect(center=(WIDTH // 2, 80)))

    pygame.draw.rect(WIN, MILITARY_GREEN, back_button, border_radius=8)
    pygame.draw.rect(WIN, TEXT_COLOR, back_button, 2, border_radius=8)
    WIN.blit(
        small_font.render("BACK", True, TEXT_COLOR),
        small_font.render("BACK", True, TEXT_COLOR).get_rect(center=back_button.center),
    )

    for i, btn in enumerate(level_buttons):
        level_num = i + 1
        unlocked = is_level_unlocked(level_num)
        completed = level_num in completed_levels
        
        if completed:
            btn_color = (100, 200, 100)
        elif unlocked:
            btn_color = MILITARY_GREEN
        else:
            btn_color = (80, 80, 80)
        
        pygame.draw.rect(WIN, btn_color, btn, border_radius=8)
        pygame.draw.rect(WIN, TEXT_COLOR, btn, 3, border_radius=8)
        
        level_text = large_font.render(f"{level_num}", True, TEXT_COLOR)
        WIN.blit(level_text, level_text.get_rect(center=btn.center))
        
        if not unlocked:
            lock_text = large_font.render("🔒", True, TEXT_COLOR)
            WIN.blit(lock_text, lock_text.get_rect(center=(btn.centerx, btn.centery + 35)))
        
        if completed:
            check_text = large_font.render("✓", True, (0, 100, 0))
            WIN.blit(check_text, check_text.get_rect(center=(btn.centerx + 45, btn.centery - 35)))

    pygame.draw.rect(WIN, MILITARY_GREEN, endless_button_menu, border_radius=10)
    pygame.draw.rect(WIN, TEXT_COLOR, endless_button_menu, 2, border_radius=10)
    WIN.blit(
        font.render("Endless Flight", True, TEXT_COLOR),
        font.render("Endless Flight", True, TEXT_COLOR).get_rect(center=endless_button_menu.center),
    )

    pygame.display.update()


continue_button = pygame.Rect(WIDTH // 2 - 150, HEIGHT - 80, 300, 60)


def wrap_text(text, font_obj, max_width):
    words = text.split(' ')
    lines = []
    current_line = []

    for word in words:
        test_line = ' '.join(current_line + [word])
        if font_obj.size(test_line)[0] <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]

    if current_line:
        lines.append(' '.join(current_line))

    return lines


def draw_message_screen():
    WIN.fill(PARCHMENT)

    msg_data = MESSAGES[current_level - 1]

    title = large_font.render("MESSAGE DELIVERED!", True, TEXT_COLOR)
    WIN.blit(title, title.get_rect(center=(WIDTH // 2, 40)))

    level_title = font.render(msg_data["title"], True, TEXT_COLOR)
    WIN.blit(level_title, level_title.get_rect(center=(WIDTH // 2, 90)))

    msg_rect = pygame.Rect(50, 130, WIDTH - 100, 120)
    pygame.draw.rect(WIN, (255, 255, 230), msg_rect, border_radius=10)
    pygame.draw.rect(WIN, TEXT_COLOR, msg_rect, 3, border_radius=10)

    message_lines = wrap_text(msg_data["message"], message_font, WIDTH - 120)
    y_offset = 145
    for line in message_lines:
        text_surf = message_font.render(line, True, TEXT_COLOR)
        WIN.blit(text_surf, (60, y_offset))
        y_offset += 25

    context_y = 270
    context_label = font.render("Historical Context:", True, TEXT_COLOR)
    WIN.blit(context_label, (50, context_y))

    context_lines = wrap_text(msg_data["context"], small_font, WIDTH - 100)
    y_offset = context_y + 35
    for line in context_lines:
        text_surf = small_font.render(line, True, TEXT_COLOR)
        WIN.blit(text_surf, (50, y_offset))
        y_offset += 22

    pygame.draw.rect(WIN, MILITARY_GREEN, continue_button, border_radius=10)
    pygame.draw.rect(WIN, TEXT_COLOR, continue_button, 2, border_radius=10)
    WIN.blit(
        font.render("CONTINUE", True, TEXT_COLOR),
        font.render("CONTINUE", True, TEXT_COLOR).get_rect(center=continue_button.center),
    )

    pygame.display.update()


def draw_victory_screen():
    WIN.fill(PARCHMENT)

    title = title_font.render("MISSION COMPLETE!", True, TEXT_COLOR)
    WIN.blit(title, title.get_rect(center=(WIDTH // 2, 50)))

    subtitle = large_font.render("Medal of Bravery Awarded", True, TEXT_COLOR)
    WIN.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, 110)))

    if medal_img:
        medal_scaled = pygame.transform.scale(medal_img, (120, 120))
        WIN.blit(medal_scaled, medal_scaled.get_rect(center=(WIDTH // 2, 190)))

    info_y = 270
    
    pdsa_title = font.render("The PDSA Dickin Medal", True, TEXT_COLOR)
    WIN.blit(pdsa_title, pdsa_title.get_rect(center=(WIDTH // 2, info_y)))
    info_y += 35

    intro_lines = wrap_text(PDSA_INFO["intro"], small_font, WIDTH - 100)
    for line in intro_lines:
        text_surf = small_font.render(line, True, TEXT_COLOR)
        WIN.blit(text_surf, (50, info_y))
        info_y += 20

    info_y += 15
    notable_title = font.render("Notable Pigeon Heroes:", True, TEXT_COLOR)
    WIN.blit(notable_title, (50, info_y))
    info_y += 30

    for i, pigeon_info in enumerate(PDSA_INFO["pigeons"][:2]):
        pigeon_lines = wrap_text(f"• {pigeon_info}", small_font, WIDTH - 100)
        for line in pigeon_lines:
            if info_y > HEIGHT - 100:
                break
            text_surf = small_font.render(line, True, TEXT_COLOR)
            WIN.blit(text_surf, (55, info_y))
            info_y += 18

    pygame.draw.rect(WIN, MILITARY_GREEN, continue_button, border_radius=10)
    pygame.draw.rect(WIN, TEXT_COLOR, continue_button, 2, border_radius=10)
    WIN.blit(
        font.render("MAIN MENU", True, TEXT_COLOR),
        font.render("MAIN MENU", True, TEXT_COLOR).get_rect(center=continue_button.center),
    )

    pygame.display.update()


def draw_settings_menu():
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(128)  # 50% opacity (128 out of 255)
    overlay.fill((0, 0, 0))
    WIN.blit(overlay, (0, 0))

    pygame.draw.rect(WIN, PARCHMENT, settings_menu_rect, border_radius=10)
    pygame.draw.rect(WIN, TEXT_COLOR, settings_menu_rect, 2, border_radius=10)

    title = large_font.render("Paused", True, TEXT_COLOR)
    WIN.blit(title, title.get_rect(center=(settings_menu_rect.centerx, settings_menu_rect.top + 40)))

    def draw_btn(rect, label):
        pygame.draw.rect(WIN, MILITARY_GREEN, rect, border_radius=8)
        pygame.draw.rect(WIN, TEXT_COLOR, rect, 2, border_radius=8)
        txt = font.render(label, True, TEXT_COLOR)
        WIN.blit(txt, txt.get_rect(center=rect.center))

    draw_btn(settings_resume_button, "Resume")
    draw_btn(settings_home_button, "Home")
    draw_btn(settings_restart_button, "Restart Level")

    sound_label = f"Sound: {'On' if sound_on else 'Off'}"
    music_label = f"Music: {'On' if music_on else 'Off'}"
    draw_btn(settings_sound_button, sound_label)
    draw_btn(settings_music_button, music_label)

    pygame.display.update()


def reset_game():
    global bg_scroll_y, current_bg_level
    global pigeon_lane_pos, pigeon_lane_target
    global pigeon_lean_amount, pigeon_lean_dir
    global health, score, coins, distance_traveled, lives
    global items, hawks, flaks
    global bg_zoom_offset_y
    global difficulty_level, background_loops_completed

    bg_scroll_y = 0
    bg_zoom_offset_y = 0
    background_loops_completed = 0
    difficulty_level = 1  # Start at difficulty 1
    
    # For endless mode, randomly select from available backgrounds
    if current_mode == MODE_ENDLESS:
        available_bgs = get_available_backgrounds()
        current_bg_level = random.choice(available_bgs)

    pigeon_lane_pos = (LANE_COUNT - 1) / 2
    pigeon_lane_target = pigeon_lane_pos
    pigeon_lean_amount = 0
    pigeon_lean_dir = 0

    health = 1.0
    score = 0
    coins = 0
    distance_traveled = 0
    lives = 3

    # Start with one hawk at a random lane
    hawks = [spawn_hawk()]

    # Spawn items in random lanes
    items = []
    for _ in range(8):
        r = random.random()
        worm_prob, medpack_prob, coin_prob = get_item_spawn_rate_for_difficulty(get_current_difficulty())
        
        if r < worm_prob:
            items.append(spawn_worm(None))  # Pass None since we're not avoiding any lane
        elif r < worm_prob + medpack_prob:
            items.append(spawn_medpack(None))
        else:
            items.append(spawn_coin(None))

    # Start with one flak at a random lane
    flaks = [spawn_flak()]


async def main():
    global pigeon_lane_target, pigeon_lean_dir
    global pigeon_anim_index, pigeon_lean_amount
    global health, game_state, current_mode, score, coins, distance_traveled
    global current_level, lives
    global pigeon_lane_pos
    global sound_on, music_on
    global total_coins_collected
    global hawks, flaks

    running = True
    score_counter = 0
    frame_counter = 0  # For tracking spawn timing

    while running:
        CLOCK.tick(FPS)
        await asyncio.sleep(0)

        if game_state == STATE_HOME:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    if start_button.collidepoint(mx, my):
                        game_state = STATE_MENU
                    elif endless_button_home.collidepoint(mx, my):
                        current_mode = MODE_ENDLESS
                        current_level = 0
                        reset_game()
                        game_state = STATE_PLAY
                        score_counter = 0
                        frame_counter = 0
                        update_background_music()  # Start music
                    elif store_button_home.collidepoint(mx, my):
                        game_state = STATE_STORE
            draw_home_screen()
            continue

        if game_state == STATE_STORE:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    if store_back_button.collidepoint(mx, my):
                        game_state = STATE_HOME
            draw_store()
            continue

        if game_state == STATE_MENU:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    if back_button.collidepoint(mx, my):
                        game_state = STATE_HOME
                    elif endless_button_menu.collidepoint(mx, my):
                        current_mode = MODE_ENDLESS
                        current_level = 0
                        reset_game()
                        game_state = STATE_PLAY
                        score_counter = 0
                        frame_counter = 0
                        update_background_music()  # Start music
                    else:
                        for i, btn in enumerate(level_buttons):
                            if btn.collidepoint(mx, my):
                                level_num = i + 1
                                if is_level_unlocked(level_num):
                                    current_mode = MODE_STORY
                                    current_level = level_num
                                    reset_game()
                                    game_state = STATE_PLAY
                                    score_counter = 0
                                    frame_counter = 0
                                    update_background_music()  # Start music
                                    break
            draw_level_menu()
            continue

        if game_state == STATE_LEVEL_COMPLETE:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            draw_level_complete()
            await asyncio.sleep(2)
            game_state = STATE_MESSAGE
            continue

        if game_state == STATE_MESSAGE:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    if continue_button.collidepoint(mx, my):
                        completed_levels.add(current_level)
                        
                        if current_level >= 10:
                            game_state = STATE_VICTORY
                        else:
                            game_state = STATE_MENU
            draw_message_screen()
            continue

        if game_state == STATE_VICTORY:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    if continue_button.collidepoint(mx, my):
                        game_state = STATE_HOME
            draw_victory_screen()
            continue

        if game_state == STATE_SETTINGS:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game_state = STATE_PLAY
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = event.pos
                    if settings_resume_button.collidepoint(mx, my):
                        game_state = STATE_PLAY
                    elif settings_home_button.collidepoint(mx, my):
                        reset_game()
                        game_state = STATE_HOME
                    elif settings_restart_button.collidepoint(mx, my):
                        reset_game()
                        game_state = STATE_PLAY
                        frame_counter = 0
                    elif settings_sound_button.collidepoint(mx, my):
                        sound_on = not sound_on
                    elif settings_music_button.collidepoint(mx, my):
                        music_on = not music_on
                        update_background_music()  # Update music immediately
                    else:
                        if not settings_menu_rect.collidepoint(mx, my):
                            game_state = STATE_PLAY

            draw_settings_menu()
            continue

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game_state = STATE_SETTINGS
                if event.key == pygame.K_LEFT:
                    pigeon_lane_target -= 1
                    pigeon_lane_target = max(0, pigeon_lane_target)
                    pigeon_lean_dir = -1
                if event.key == pygame.K_RIGHT:
                    pigeon_lane_target += 1
                    pigeon_lane_target = min(LANE_COUNT - 1, pigeon_lane_target)
                    pigeon_lean_dir = 1

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if settings_button_rect.collidepoint(mx, my):
                    game_state = STATE_SETTINGS

        update_pigeon_lane()

        if pigeon_lean_amount < pigeon_lean_dir:
            pigeon_lean_amount += LEAN_SMOOTHING
        elif pigeon_lean_amount > pigeon_lean_dir:
            pigeon_lean_amount -= LEAN_SMOOTHING
        pigeon_lean_amount = max(-1, min(1, pigeon_lean_amount))
        if abs(pigeon_lane_pos - pigeon_lane_target) < 0.05:
            pigeon_lean_dir = 0

        pigeon_anim_index = (pigeon_anim_index + PIGEON_ANIM_SPEED) % len(pigeon_frames)

        p_rect = pigeon_rect()

        if current_mode == MODE_STORY:
            distance_traveled += WORLD_SPEED * 0.5
            if distance_traveled >= LEVEL_DISTANCE:
                game_state = STATE_LEVEL_COMPLETE

        for it in items:
            it["y"] += WORLD_SPEED * 0.9

            y = it["y"]
            cx = lane_x_for_lane(it["lane"], y)

            if it["type"] == "worm":
                img = worm_img
            elif it["type"] == "medpack":
                img = medpack_img
            else:
                img = coin_img

            # Use lane-based collision instead of rect collision
            if is_in_pigeon_lane(it["lane"], y):
                if it["type"] == "worm":
                    health = min(1.0, health + 0.10)
                    score += 5
                elif it["type"] == "medpack":
                    health = min(1.0, health + 0.60)
                    score += 15
                else:
                    coins += 1
                    total_coins_collected += 1
                    score += 25
                    play_sound_effect(coin_clink)  # Play coin sound

                r = random.random()
                worm_prob, medpack_prob, coin_prob = get_item_spawn_rate_for_difficulty(get_current_difficulty())
                
                if r < worm_prob:
                    new = spawn_worm()
                elif r < worm_prob + medpack_prob:
                    new = spawn_medpack()
                else:
                    new = spawn_coin()
                it.update(new)

            if y > HEIGHT + 100:
                r = random.random()
                worm_prob, medpack_prob, coin_prob = get_item_spawn_rate_for_difficulty(get_current_difficulty())
                
                if r < worm_prob:
                    new = spawn_worm()
                elif r < worm_prob + medpack_prob:
                    new = spawn_medpack()
                else:
                    new = spawn_coin()
                it.update(new)

        for hk in hawks:
            hk["y"] += WORLD_SPEED * 1.0

            y = hk["y"]
            x = lane_x_for_lane(hk["lane"], y)

            # Animate hawk wings
            hk["timer"] += 1
            if hk["timer"] > 10:  # Change frame every 10 ticks
                hk["timer"] = 0
                hk["frame"] = (hk["frame"] + 1) % 2  # Toggle between 0 and 1

            # Get current animation frame
            hawk_img = hawk_frames[hk["frame"]]
            
            # Use lane-based collision instead of rect collision
            if is_in_pigeon_lane(hk["lane"], y):
                health -= 0.25
                
                if health <= 0:
                    lives -= 1
                    
                    # Play hawk screech sound
                    play_sound_effect(hawk_screech)
                    
                    # Show hawk death screen with background (using hawk.png)
                    hb_rect = hawk_big.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                    WIN.blit(hawk_big, hb_rect)
                    
                    if lives > 0:
                        lives_text = large_font.render(f"Lives Remaining: {lives}", True, (255, 255, 255))
                        WIN.blit(lives_text, lives_text.get_rect(center=(WIDTH // 2, HEIGHT - 100)))
                        pygame.display.update()
                        await asyncio.sleep(2)
                        health = 1.0
                        pigeon_lane_pos = (LANE_COUNT - 1) / 2
                        pigeon_lane_target = pigeon_lane_pos
                    else:
                        game_over_text = title_font.render("GAME OVER", True, (255, 50, 50))
                        WIN.blit(game_over_text, game_over_text.get_rect(center=(WIDTH // 2, 100)))
                        
                        # Three buttons: Home, Restart, Watch Ad
                        btn_width = 200
                        btn_height = 50
                        btn_spacing = 20
                        total_width = btn_width * 3 + btn_spacing * 2
                        start_x = (WIDTH - total_width) // 2
                        btn_y = HEIGHT // 2 + 100
                        
                        home_button = pygame.Rect(start_x, btn_y, btn_width, btn_height)
                        restart_button = pygame.Rect(start_x + btn_width + btn_spacing, btn_y, btn_width, btn_height)
                        ad_button = pygame.Rect(start_x + (btn_width + btn_spacing) * 2, btn_y, btn_width, btn_height)
                        
                        pygame.draw.rect(WIN, MILITARY_GREEN, home_button, border_radius=10)
                        pygame.draw.rect(WIN, TEXT_COLOR, home_button, 2, border_radius=10)
                        home_text = font.render("Home", True, TEXT_COLOR)
                        WIN.blit(home_text, home_text.get_rect(center=home_button.center))
                        
                        pygame.draw.rect(WIN, MILITARY_GREEN, restart_button, border_radius=10)
                        pygame.draw.rect(WIN, TEXT_COLOR, restart_button, 2, border_radius=10)
                        restart_text = font.render("Restart", True, TEXT_COLOR)
                        WIN.blit(restart_text, restart_text.get_rect(center=restart_button.center))
                        
                        pygame.draw.rect(WIN, MILITARY_GREEN, ad_button, border_radius=10)
                        pygame.draw.rect(WIN, TEXT_COLOR, ad_button, 2, border_radius=10)
                        ad_text = font.render("Watch Ad", True, TEXT_COLOR)
                        WIN.blit(ad_text, ad_text.get_rect(center=ad_button.center))
                        
                        pygame.display.update()
                        
                        # Wait for player to click a button
                        waiting = True
                        
                        while waiting:
                            for evt in pygame.event.get():
                                if evt.type == pygame.QUIT:
                                    pygame.quit()
                                    sys.exit()
                                if evt.type == pygame.MOUSEBUTTONDOWN:
                                    mx, my = evt.pos
                                    if home_button.collidepoint(mx, my):
                                        game_state = STATE_HOME
                                        reset_game()
                                        waiting = False
                                    elif restart_button.collidepoint(mx, my):
                                        reset_game()
                                        frame_counter = 0
                                        waiting = False
                                    elif ad_button.collidepoint(mx, my):
                                        lives = 1  # Grant extra life
                                        health = 1.0
                                        pigeon_lane_pos = (LANE_COUNT - 1) / 2
                                        pigeon_lane_target = pigeon_lane_pos
                                        waiting = False
                            await asyncio.sleep(0.01)
                        
                        if game_state == STATE_HOME:
                            continue
                
                hk.update(spawn_hawk())

            if y > HEIGHT + 200:
                hk.update(spawn_hawk())
        
        # Spawn additional hawks based on difficulty
        frame_counter += 1
        hawk_interval, flak_interval = get_spawn_timers_for_difficulty(get_current_difficulty())
        max_hawks, max_flaks = get_max_hazards_for_difficulty(get_current_difficulty())
        
        if frame_counter % hawk_interval == 0 and len(hawks) < max_hawks:
            hawks.append(spawn_hawk())

        for fk in flaks:
            fk["y"] += WORLD_SPEED * 1.1
            y = fk["y"]
            cx = lane_x_for_lane(fk["lane"], y)

            # Change to frame 1 when much closer to pigeon (50 pixels above)
            if y >= pigeon_y - 50:
                fk["timer"] += 1
                if fk["timer"] > 15:
                    fk["timer"] = 0
                    if fk["frame"] == 0:
                        fk["frame"] = 1
            else:
                fk["frame"] = 0
                fk["timer"] = 0

            img = flak_frames[fk["frame"]]

            # Use lane-based collision instead of rect collision
            if is_in_pigeon_lane(fk["lane"], y):
                # Immediately change to frame 1 on collision
                fk["frame"] = 1
                
                health -= 0.50
                if health <= 0:
                    lives -= 1
                    
                    # Play explosion sound
                    play_sound_effect(explosion_sound)
                    
                    WIN.blit(flak_big, (0, 0))
                    
                    if lives > 0:
                        lives_text = large_font.render(f"Lives Remaining: {lives}", True, (255, 255, 255))
                        WIN.blit(lives_text, lives_text.get_rect(center=(WIDTH // 2, HEIGHT - 100)))
                        pygame.display.update()
                        await asyncio.sleep(2)
                        health = 1.0
                        pigeon_lane_pos = (LANE_COUNT - 1) / 2
                        pigeon_lane_target = pigeon_lane_pos
                    else:
                        game_over_text = title_font.render("GAME OVER", True, (255, 50, 50))
                        WIN.blit(game_over_text, game_over_text.get_rect(center=(WIDTH // 2, 100)))
                        
                        # Three buttons: Home, Restart, Watch Ad
                        btn_width = 200
                        btn_height = 50
                        btn_spacing = 20
                        total_width = btn_width * 3 + btn_spacing * 2
                        start_x = (WIDTH - total_width) // 2
                        btn_y = HEIGHT // 2 + 100
                        
                        home_button = pygame.Rect(start_x, btn_y, btn_width, btn_height)
                        restart_button = pygame.Rect(start_x + btn_width + btn_spacing, btn_y, btn_width, btn_height)
                        ad_button = pygame.Rect(start_x + (btn_width + btn_spacing) * 2, btn_y, btn_width, btn_height)
                        
                        pygame.draw.rect(WIN, MILITARY_GREEN, home_button, border_radius=10)
                        pygame.draw.rect(WIN, TEXT_COLOR, home_button, 2, border_radius=10)
                        home_text = font.render("Home", True, TEXT_COLOR)
                        WIN.blit(home_text, home_text.get_rect(center=home_button.center))
                        
                        pygame.draw.rect(WIN, MILITARY_GREEN, restart_button, border_radius=10)
                        pygame.draw.rect(WIN, TEXT_COLOR, restart_button, 2, border_radius=10)
                        restart_text = font.render("Restart", True, TEXT_COLOR)
                        WIN.blit(restart_text, restart_text.get_rect(center=restart_button.center))
                        
                        pygame.draw.rect(WIN, MILITARY_GREEN, ad_button, border_radius=10)
                        pygame.draw.rect(WIN, TEXT_COLOR, ad_button, 2, border_radius=10)
                        ad_text = font.render("Watch Ad", True, TEXT_COLOR)
                        WIN.blit(ad_text, ad_text.get_rect(center=ad_button.center))
                        
                        pygame.display.update()
                        
                        # Wait for player to click a button
                        waiting = True
                        
                        while waiting:
                            for evt in pygame.event.get():
                                if evt.type == pygame.QUIT:
                                    pygame.quit()
                                    sys.exit()
                                if evt.type == pygame.MOUSEBUTTONDOWN:
                                    mx, my = evt.pos
                                    if home_button.collidepoint(mx, my):
                                        game_state = STATE_HOME
                                        reset_game()
                                        waiting = False
                                    elif restart_button.collidepoint(mx, my):
                                        reset_game()
                                        frame_counter = 0
                                        waiting = False
                                    elif ad_button.collidepoint(mx, my):
                                        lives = 1  # Grant extra life
                                        health = 1.0
                                        pigeon_lane_pos = (LANE_COUNT - 1) / 2
                                        pigeon_lane_target = pigeon_lane_pos
                                        waiting = False
                            await asyncio.sleep(0.01)
                        
                        if game_state == STATE_HOME:
                            continue

                fk.update(spawn_flak())

            if y > HEIGHT + 100:
                fk.update(spawn_flak())
        
        # Spawn additional flaks based on difficulty
        if frame_counter % flak_interval == 0 and len(flaks) < max_flaks:
            flaks.append(spawn_flak())

        score_counter += 1
        if score_counter >= 3:
            score += 1
            score_counter = 0

        draw_background()

        for it in items:
            y = it["y"]
            cx = lane_x_for_lane(it["lane"], y)
            if it["type"] == "worm":
                img = worm_img
            elif it["type"] == "medpack":
                img = medpack_img
            else:
                img = coin_img
            WIN.blit(img, img.get_rect(center=(cx, y)))

        for hk in hawks:
            y = hk["y"]
            x = lane_x_for_lane(hk["lane"], y)
            hawk_img = hawk_frames[hk["frame"]]
            WIN.blit(hawk_img, hawk_img.get_rect(center=(x, y)))

        for fk in flaks:
            y = fk["y"]
            cx = lane_x_for_lane(fk["lane"], y)
            img = flak_frames[fk["frame"]]
            WIN.blit(img, img.get_rect(center=(cx, y)))

        if pigeon_lean_amount < -0.25:
            sprite = pigeon_left
        elif pigeon_lean_amount > 0.25:
            sprite = pigeon_right
        else:
            sprite = pigeon_frames[int(pigeon_anim_index)]

        WIN.blit(sprite, sprite.get_rect(center=p_rect.center))

        draw_lives()
        draw_health_bar()
        if current_mode == MODE_STORY:
            draw_level_progress()
        draw_score_and_coins()
        draw_settings_button()
        pygame.display.update()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    asyncio.run(main())