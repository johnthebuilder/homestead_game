import streamlit as st
import random
import time
from datetime import datetime, timedelta

# Initialize game state
def init_game_state():
    if 'game_state' not in st.session_state:
        st.session_state.game_state = {
            'player_name': '',
            'player_x': 5,  # Player position on grid
            'player_y': 5,
            'grid_size': 12,
            'current_location': 'cabin',
            'energy': 100,
            'day': 1,
            'time_of_day': 'morning',
            'inventory': {
                'wood': 0,
                'seeds': 5,
                'water': 0,
                'food': 3,
                'coins': 50
            },
            'tools': ['axe', 'hoe', 'watering_can'],
            'farm_plots': {},  # Will store plot coordinates and crop info
            'trees_chopped': 0,
            'met_deer': False,
            'weather': 'sunny',
            'season': 'spring',
            'world_map': generate_world_map(),
            'last_key': None
        }

def generate_world_map():
    """Generate a 12x12 world map with different terrain types"""
    world = {}
    
    # Define terrain for different areas
    for y in range(12):
        for x in range(12):
            # Cabin area (center-left)
            if x == 2 and y == 5:
                world[(x, y)] = {'type': 'cabin', 'char': '🏠', 'walkable': True}
            # Creek (horizontal line)
            elif y == 8 and 1 <= x <= 8:
                world[(x, y)] = {'type': 'creek', 'char': '🌊', 'walkable': True}
            # Pond (bottom right)
            elif 9 <= x <= 10 and 9 <= y <= 10:
                world[(x, y)] = {'type': 'pond', 'char': '🌊', 'walkable': True}
            # Farm area (right side)
            elif 7 <= x <= 10 and 2 <= y <= 6:
                world[(x, y)] = {'type': 'farm', 'char': '🟫', 'walkable': True}
            # Forest (scattered trees)
            elif random.random() < 0.3 and not (4 <= x <= 6 and 4 <= y <= 6):
                world[(x, y)] = {'type': 'forest', 'char': '🌲', 'walkable': True}
            # Open grass areas
            else:
                world[(x, y)] = {'type': 'grass', 'char': '🌿', 'walkable': True}
    
    return world

def get_current_terrain():
    """Get the terrain type at player's current position"""
    game_state = st.session_state.game_state
    pos = (game_state['player_x'], game_state['player_y'])
    return game_state['world_map'].get(pos, {'type': 'grass'})['type']

def render_world():
    """Render the game world with the player character"""
    game_state = st.session_state.game_state
    
    world_display = ""
    for y in range(game_state['grid_size']):
        row = ""
        for x in range(game_state['grid_size']):
            if x == game_state['player_x'] and y == game_state['player_y']:
                row += "🧑‍🌾"  # Player character
            else:
                terrain = game_state['world_map'].get((x, y), {'char': '🌿'})
                row += terrain['char']
        world_display += row + "\n"
    
    return world_display

def move_player(direction):
    """Move player in specified direction"""
    game_state = st.session_state.game_state
    
    if game_state['energy'] <= 0:
        st.error("Too tired to move! Rest in your cabin.")
        return
    
    new_x, new_y = game_state['player_x'], game_state['player_y']
    
    if direction == 'w':  # Up
        new_y = max(0, new_y - 1)
    elif direction == 's':  # Down
        new_y = min(game_state['grid_size'] - 1, new_y + 1)
    elif direction == 'a':  # Left
        new_x = max(0, new_x - 1)
    elif direction == 'd':  # Right
        new_x = min(game_state['grid_size'] - 1, new_x + 1)
    
    # Check if new position is walkable
    new_pos = (new_x, new_y)
    if game_state['world_map'].get(new_pos, {'walkable': True})['walkable']:
        game_state['player_x'] = new_x
        game_state['player_y'] = new_y
        game_state['energy'] -= 1  # Small energy cost for movement
        
        # Update current location based on terrain
        game_state['current_location'] = get_current_terrain()

def get_location_description(location):
    descriptions = {
        'cabin': "🏠 You're at your cozy log cabin. Morning light streams through the windows. This is your safe haven in the wilderness.",
        'grass': "🌿 You're standing on soft mountain grass. The fresh air of West Asheville fills your lungs.",
        'forest': "🌲 You're among tall Appalachian trees. You can chop these for wood with your axe.",
        'creek': "🌊 You're by the babbling mountain creek. The water is crystal clear and perfect for collecting.",
        'pond': "🌊 You're at the peaceful pond. Lily pads float on the surface and the water is fresh and clean.",
        'farm': "🟫 You're in your farming area. The rich soil is perfect for growing crops."
    }
    return descriptions.get(location, "You're exploring the beautiful mountain wilderness.")

def deer_encounter():
    if not st.session_state.game_state['met_deer'] and st.session_state.game_state['current_location'] == 'grass':
        if random.random() < 0.1:  # 10% chance when on grass
            st.markdown("### 🦌 A Friendly Visitor")
            st.write("A gentle deer approaches you with curious eyes!")
            st.write("**Deer**: 'Welcome to the mountains, friend! I've been watching over this land. It's wonderful to finally have someone here who appreciates nature.'")
            st.write("**Deer**: 'The forest provides everything you need - wood from the trees, fresh water from the creek, and rich soil for growing food. Take care of this place, and it will take care of you.'")
            
            if st.button("Thank the deer"):
                st.session_state.game_state['met_deer'] = True
                st.success("The deer nods wisely and bounds gracefully back into the forest.")
                st.rerun()

def perform_action(action):
    game_state = st.session_state.game_state
    location = game_state['current_location']
    
    if game_state['energy'] <= 5:
        st.error("You're too tired! Rest in your cabin to restore energy.")
        return
    
    if action == 'chop_tree' and location == 'forest':
        if 'axe' in game_state['tools']:
            wood_gained = random.randint(2, 5)
            game_state['inventory']['wood'] += wood_gained
            game_state['energy'] -= 15
            game_state['trees_chopped'] += 1
            
            # Remove tree from map (turn into grass)
            pos = (game_state['player_x'], game_state['player_y'])
            game_state['world_map'][pos] = {'type': 'grass', 'char': '🌿', 'walkable': True}
            game_state['current_location'] = 'grass'
            
            st.success(f"🪓 You chopped the tree and gained {wood_gained} wood! Energy: {game_state['energy']}")
        else:
            st.error("You need an axe to chop trees!")
    
    elif action == 'collect_water' and location in ['creek', 'pond']:
        water_gained = random.randint(3, 6)
        game_state['inventory']['water'] += water_gained
        game_state['energy'] -= 5
        st.success(f"💧 You collected {water_gained} units of fresh mountain water! Energy: {game_state['energy']}")
    
    elif action == 'till_soil' and location == 'farm':
        if 'hoe' in game_state['tools']:
            pos = (game_state['player_x'], game_state['player_y'])
            plot_id = f"plot_{pos[0]}_{pos[1]}"
            
            if plot_id not in game_state['farm_plots']:
                game_state['farm_plots'][plot_id] = {
                    'x': pos[0], 'y': pos[1],
                    'state': 'tilled',
                    'crop': None,
                    'growth_stage': 0,
                    'watered': False,
                    'days_planted': 0
                }
                game_state['energy'] -= 10
                game_state['world_map'][pos] = {'type': 'tilled', 'char': '🟫', 'walkable': True}
                st.success(f"🏡 You tilled the soil! Energy: {game_state['energy']}")
            else:
                st.info("This plot is already tilled!")
        else:
            st.error("You need a hoe to till soil!")
    
    elif action == 'plant_seeds' and location == 'farm':
        if game_state['inventory']['seeds'] > 0:
            pos = (game_state['player_x'], game_state['player_y'])
            plot_id = f"plot_{pos[0]}_{pos[1]}"
            
            if plot_id in game_state['farm_plots'] and game_state['farm_plots'][plot_id]['crop'] is None:
                crop_type = random.choice(['carrots', 'potatoes', 'corn', 'tomatoes', 'beans'])
                game_state['farm_plots'][plot_id]['crop'] = crop_type
                game_state['farm_plots'][plot_id]['days_planted'] = 0
                game_state['inventory']['seeds'] -= 1
                game_state['energy'] -= 8
                game_state['world_map'][pos] = {'type': 'planted', 'char': '🌱', 'walkable': True}
                st.success(f"🌱 You planted {crop_type} seeds! Energy: {game_state['energy']}")
            else:
                st.error("You need to till this soil first or it's already planted!")
        else:
            st.error("You don't have any seeds!")
    
    elif action == 'water_crops' and location == 'farm':
        if 'watering_can' in game_state['tools'] and game_state['inventory']['water'] > 0:
            pos = (game_state['player_x'], game_state['player_y'])
            plot_id = f"plot_{pos[0]}_{pos[1]}"
            
            if plot_id in game_state['farm_plots'] and game_state['farm_plots'][plot_id]['crop'] and not game_state['farm_plots'][plot_id]['watered']:
                game_state['farm_plots'][plot_id]['watered'] = True
                game_state['inventory']['water'] -= 1
                game_state['energy'] -= 5
                st.success(f"💧 You watered the crops! Energy: {game_state['energy']}")
            else:
                st.info("No crops here need watering.")
        else:
            st.error("You need a watering can and water!")
    
    elif action == 'rest' and location == 'cabin':
        game_state['energy'] = min(100, game_state['energy'] + 50)
        st.success(f"😴 You rested and restored energy! Energy: {game_state['energy']}")

def advance_day():
    game_state = st.session_state.game_state
    game_state['day'] += 1
    game_state['energy'] = 100
    game_state['weather'] = random.choice(['sunny', 'cloudy', 'rainy'])
    
    # Advance crop growth and update map
    for plot_id, plot_info in game_state['farm_plots'].items():
        if plot_info['crop']:
            if plot_info['watered']:
                plot_info['days_planted'] += 1
                plot_info['growth_stage'] = min(3, plot_info['days_planted'])
                
                # Update map visual based on growth stage
                pos = (plot_info['x'], plot_info['y'])
                growth_chars = ['🌱', '🌿', '🌾', '🍅']
                game_state['world_map'][pos] = {
                    'type': 'planted', 
                    'char': growth_chars[plot_info['growth_stage']], 
                    'walkable': True
                }
            plot_info['watered'] = False
    
    # Random events
    if random.random() < 0.3:
        event = random.choice([
            "You found some wild berries! +2 food",
            "A friendly squirrel left you some nuts! +1 food", 
            "The morning dew collected extra water! +3 water"
        ])
        if "berries" in event or "nuts" in event:
            game_state['inventory']['food'] += 2 if "berries" in event else 1
        elif "water" in event:
            game_state['inventory']['water'] += 3
        st.info(f"🌅 New day event: {event}")

def harvest_crops():
    game_state = st.session_state.game_state
    pos = (game_state['player_x'], game_state['player_y'])
    plot_id = f"plot_{pos[0]}_{pos[1]}"
    
    if plot_id in game_state['farm_plots']:
        plot_info = game_state['farm_plots'][plot_id]
        if plot_info['crop'] and plot_info['growth_stage'] >= 3:
            crop = plot_info['crop']
            
            # Reset plot
            plot_info['crop'] = None
            plot_info['growth_stage'] = 0
            plot_info['days_planted'] = 0
            plot_info['state'] = 'tilled'
            
            # Update map
            game_state['world_map'][pos] = {'type': 'tilled', 'char': '🟫', 'walkable': True}
            
            # Add to inventory
            food_gained = random.randint(2, 4)
            coins_gained = random.randint(5, 15)
            game_state['inventory']['food'] += food_gained
            game_state['inventory']['coins'] += coins_gained
            
            st.balloons()
            st.success(f"🌾 Harvested {crop}! +{food_gained} food, +{coins_gained} coins")
            return True
    return False

def main():
    st.set_page_config(page_title="Asheville Homestead", page_icon="🏠", layout="wide")
    
    init_game_state()
    game_state = st.session_state.game_state
    
    # Title and game info
    st.title("🏠 Asheville Homestead")
    st.markdown("*A peaceful farming adventure in the mountains of West Asheville*")
    st.markdown("**Use WASD keys below to move your character 🧑‍🌾**")
    
    # Game stats sidebar
    with st.sidebar:
        st.header("📊 Game Stats")
        st.write(f"**Day:** {game_state['day']}")
        st.write(f"**Energy:** {game_state['energy']}/100")
        st.write(f"**Weather:** {game_state['weather'].title()} ☀️")
        st.write(f"**Position:** ({game_state['player_x']}, {game_state['player_y']})")
        
        st.subheader("🎒 Inventory")
        for item, amount in game_state['inventory'].items():
            icon = {'wood': '🪵', 'seeds': '🌰', 'water': '💧', 'food': '🍎', 'coins': '🪙'}
            st.write(f"{icon.get(item, '📦')} {item.title()}: {amount}")
        
        st.subheader("🔧 Tools")
        tool_icons = {'axe': '🪓', 'hoe': '🏡', 'watering_can': '🪣'}
        for tool in game_state['tools']:
            st.write(f"{tool_icons.get(tool, '🔨')} {tool.replace('_', ' ').title()}")
        
        if st.button("🛌 Sleep (Next Day)"):
            advance_day()
            st.rerun()
    
    # Main game area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # World map display
        st.subheader("🗺️ World Map")
        world_display = render_world()
        st.text(world_display)
        
        # Movement controls
        st.subheader("🎮 Movement (WASD)")
        movement_cols = st.columns([1, 1, 1, 1, 1])
        
        with movement_cols[1]:
            if st.button("⬆️ W", key="move_up"):
                move_player('w')
                st.rerun()
        
        move_row = st.columns([1, 1, 1, 1, 1])
        with move_row[0]:
            if st.button("⬅️ A", key="move_left"):
                move_player('a')
                st.rerun()
        with move_row[2]:
            if st.button("⬇️ S", key="move_down"):
                move_player('s')
                st.rerun()
        with move_row[4]:
            if st.button("➡️ D", key="move_right"):
                move_player('d')
                st.rerun()
    
    with col2:
        # Current location info
        current_terrain = get_current_terrain()
        st.subheader(f"📍 Current Location")
        st.write(get_location_description(current_terrain))
        
        # Special encounters
        deer_encounter()
        
        # Location-specific actions
        st.subheader("🎮 Actions")
        
        if current_terrain == 'forest':
            if st.button("🪓 Chop Tree"):
                perform_action('chop_tree')
                st.rerun()
        
        elif current_terrain in ['creek', 'pond']:
            if st.button("💧 Collect Water"):
                perform_action('collect_water')
                st.rerun()
        
        elif current_terrain == 'farm':
            if st.button("🏡 Till Soil"):
                perform_action('till_soil')
                st.rerun()
            
            pos = (game_state['player_x'], game_state['player_y'])
            plot_id = f"plot_{pos[0]}_{pos[1]}"
            
            if plot_id in game_state['farm_plots']:
                plot_info = game_state['farm_plots'][plot_id]
                
                if plot_info['crop'] is None:
                    if st.button("🌱 Plant Seeds"):
                        perform_action('plant_seeds')
                        st.rerun()
                else:
                    if not plot_info['watered']:
                        if st.button("💧 Water Crops"):
                            perform_action('water_crops')
                            st.rerun()
                    
                    if plot_info['growth_stage'] >= 3:
                        if st.button(f"🌾 Harvest {plot_info['crop']}"):
                            harvest_crops()
                            st.rerun()
                    else:
                        days_left = 3 - plot_info['growth_stage']
                        st.info(f"🌱 {plot_info['crop']} needs {days_left} more days")
        
        elif current_terrain == 'cabin':
            if st.button("😴 Rest (+50 Energy)"):
                perform_action('rest')
                st.rerun()
        
        # Legend
        st.subheader("🗝️ Map Legend")
        legend = {
            '🧑‍🌾': 'You',
            '🏠': 'Cabin',
            '🌲': 'Trees (choppable)',
            '🌊': 'Water',
            '🟫': 'Tilled soil',
            '🌱': 'Young crops',
            '🌿': 'Grass',
            '🌾': 'Mature crops',
            '🍅': 'Ready to harvest'
        }
        
        for symbol, description in legend.items():
            st.write(f"{symbol} {description}")

if __name__ == "__main__":
    main()
