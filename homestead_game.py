import streamlit as st
import random
import time
from datetime import datetime, timedelta

# Initialize game state
def init_game_state():
    if 'game_state' not in st.session_state:
        st.session_state.game_state = {
            'player_name': '',
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
            'season': 'spring'
        }

def get_location_description(location):
    descriptions = {
        'cabin': "🏠 You're inside your cozy log cabin. Morning light streams through the windows. There's a bed, a fireplace, and a small kitchen. The front door beckons you outside.",
        'front_yard': "🌲 You step outside into the fresh mountain air of West Asheville. Tall oak and pine trees surround your property. A gentle breeze rustles the leaves.",
        'forest': "🌲🌿 Deep in the Appalachian forest. Ancient trees tower above you, their canopy filtering the sunlight. You can hear birds chirping and leaves rustling.",
        'creek': "🏞️ A crystal-clear mountain creek babbles over smooth stones. The water is cool and refreshing. Small fish dart between the rocks.",
        'pond': "🌊 A peaceful pond reflects the sky and surrounding trees. Cattails grow along the edges, and you can see lily pads floating on the surface.",
        'farm': "🌱 Your developing farm area. The soil looks rich and fertile, perfect for growing crops. Some plots are tilled and ready for planting."
    }
    return descriptions.get(location, "You're somewhere in the wilderness.")

def deer_encounter():
    if not st.session_state.game_state['met_deer']:
        st.markdown("### 🦌 A Friendly Visitor")
        st.write("As you step outside, a gentle deer approaches you with curious eyes.")
        st.write("**Deer**: 'Welcome to the mountains, friend! I've been watching over this land. It's wonderful to finally have someone here who appreciates nature.'")
        st.write("**Deer**: 'The forest provides everything you need - wood from the trees, fresh water from the creek, and rich soil for growing food. Take care of this place, and it will take care of you.'")
        
        if st.button("Thank the deer"):
            st.session_state.game_state['met_deer'] = True
            st.success("The deer nods wisely and bounds gracefully back into the forest.")
            st.rerun()

def perform_action(action, location):
    game_state = st.session_state.game_state
    
    if game_state['energy'] <= 0:
        st.error("You're too tired! Rest in your cabin to restore energy.")
        return
    
    if action == 'chop_tree' and location in ['forest', 'front_yard']:
        if 'axe' in game_state['tools']:
            wood_gained = random.randint(2, 5)
            game_state['inventory']['wood'] += wood_gained
            game_state['energy'] -= 15
            game_state['trees_chopped'] += 1
            st.success(f"🪓 You chopped a tree and gained {wood_gained} wood! Energy: {game_state['energy']}")
        else:
            st.error("You need an axe to chop trees!")
    
    elif action == 'collect_water' and location in ['creek', 'pond']:
        water_gained = random.randint(3, 6)
        game_state['inventory']['water'] += water_gained
        game_state['energy'] -= 5
        st.success(f"💧 You collected {water_gained} units of fresh mountain water! Energy: {game_state['energy']}")
    
    elif action == 'till_soil' and location == 'farm':
        if 'hoe' in game_state['tools']:
            plot_id = f"plot_{len(game_state['farm_plots']) + 1}"
            game_state['farm_plots'][plot_id] = {
                'state': 'tilled',
                'crop': None,
                'growth_stage': 0,
                'watered': False,
                'days_planted': 0
            }
            game_state['energy'] -= 10
            st.success(f"🏡 You tilled a new plot of soil! You now have {len(game_state['farm_plots'])} farm plots. Energy: {game_state['energy']}")
        else:
            st.error("You need a hoe to till soil!")
    
    elif action == 'plant_seeds' and location == 'farm':
        if game_state['inventory']['seeds'] > 0:
            empty_plots = [p for p, info in game_state['farm_plots'].items() if info['crop'] is None and info['state'] == 'tilled']
            if empty_plots:
                plot = empty_plots[0]
                crop_type = random.choice(['carrots', 'potatoes', 'corn', 'tomatoes', 'beans'])
                game_state['farm_plots'][plot]['crop'] = crop_type
                game_state['farm_plots'][plot]['days_planted'] = 0
                game_state['inventory']['seeds'] -= 1
                game_state['energy'] -= 8
                st.success(f"🌱 You planted {crop_type} seeds! Energy: {game_state['energy']}")
            else:
                st.error("You need to till soil first or all plots are already planted!")
        else:
            st.error("You don't have any seeds!")
    
    elif action == 'water_crops' and location == 'farm':
        if 'watering_can' in game_state['tools'] and game_state['inventory']['water'] > 0:
            watered_count = 0
            for plot_id, plot_info in game_state['farm_plots'].items():
                if plot_info['crop'] and not plot_info['watered'] and game_state['inventory']['water'] > 0:
                    plot_info['watered'] = True
                    game_state['inventory']['water'] -= 1
                    watered_count += 1
            
            if watered_count > 0:
                game_state['energy'] -= 5
                st.success(f"💧 You watered {watered_count} crops! Energy: {game_state['energy']}")
            else:
                st.info("No crops need watering right now.")
        else:
            st.error("You need a watering can and water!")

def advance_day():
    game_state = st.session_state.game_state
    game_state['day'] += 1
    game_state['energy'] = 100
    game_state['weather'] = random.choice(['sunny', 'cloudy', 'rainy'])
    
    # Advance crop growth
    for plot_id, plot_info in game_state['farm_plots'].items():
        if plot_info['crop']:
            if plot_info['watered']:
                plot_info['days_planted'] += 1
                plot_info['growth_stage'] = min(3, plot_info['days_planted'])
            plot_info['watered'] = False  # Reset watering status
    
    # Random events
    if random.random() < 0.3:  # 30% chance
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
    harvested = []
    
    for plot_id, plot_info in game_state['farm_plots'].items():
        if plot_info['crop'] and plot_info['growth_stage'] >= 3:
            crop = plot_info['crop']
            harvested.append(crop)
            
            # Reset plot
            plot_info['crop'] = None
            plot_info['growth_stage'] = 0
            plot_info['days_planted'] = 0
            plot_info['state'] = 'tilled'
            
            # Add to inventory
            game_state['inventory']['food'] += random.randint(2, 4)
            game_state['inventory']['coins'] += random.randint(5, 15)
    
    if harvested:
        st.balloons()
        st.success(f"🌾 Harvested: {', '.join(harvested)}! Check your inventory.")

def main():
    st.set_page_config(page_title="Asheville Homestead", page_icon="🏠", layout="wide")
    
    init_game_state()
    game_state = st.session_state.game_state
    
    # Title and game info
    st.title("🏠 Asheville Homestead")
    st.markdown("*A peaceful farming adventure in the mountains of West Asheville*")
    
    # Game stats sidebar
    with st.sidebar:
        st.header("📊 Game Stats")
        st.write(f"**Day:** {game_state['day']}")
        st.write(f"**Energy:** {game_state['energy']}/100")
        st.write(f"**Weather:** {game_state['weather'].title()} ☀️")
        st.write(f"**Season:** {game_state['season'].title()}")
        
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
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Location description
        st.markdown(f"### {get_location_description(game_state['current_location'])}")
        
        # Special encounters
        if game_state['current_location'] == 'front_yard':
            deer_encounter()
        
        # Location-specific actions
        st.subheader("🎮 Actions")
        action_cols = st.columns(3)
        
        if game_state['current_location'] in ['forest', 'front_yard']:
            with action_cols[0]:
                if st.button("🪓 Chop Tree"):
                    perform_action('chop_tree', game_state['current_location'])
                    st.rerun()
        
        if game_state['current_location'] in ['creek', 'pond']:
            with action_cols[0]:
                if st.button("💧 Collect Water"):
                    perform_action('collect_water', game_state['current_location'])
                    st.rerun()
        
        if game_state['current_location'] == 'farm':
            with action_cols[0]:
                if st.button("🏡 Till Soil"):
                    perform_action('till_soil', game_state['current_location'])
                    st.rerun()
            
            with action_cols[1]:
                if st.button("🌱 Plant Seeds"):
                    perform_action('plant_seeds', game_state['current_location'])
                    st.rerun()
            
            with action_cols[2]:
                if st.button("💧 Water Crops"):
                    perform_action('water_crops', game_state['current_location'])
                    st.rerun()
            
            # Show farm status
            if game_state['farm_plots']:
                st.subheader("🌾 Farm Status")
                for plot_id, plot_info in game_state['farm_plots'].items():
                    if plot_info['crop']:
                        growth_icons = ['🌱', '🌿', '🌾', '🍅']
                        water_status = "💧" if plot_info['watered'] else "🌵"
                        st.write(f"{plot_id}: {plot_info['crop']} {growth_icons[plot_info['growth_stage']]} {water_status}")
                        
                        if plot_info['growth_stage'] >= 3:
                            if st.button(f"🌾 Harvest {plot_info['crop']}", key=f"harvest_{plot_id}"):
                                harvest_crops()
                                st.rerun()
                    else:
                        st.write(f"{plot_id}: Empty tilled soil 🟫")
    
    with col2:
        st.subheader("🗺️ Navigation")
        
        # Movement buttons
        locations = {
            'cabin': '🏠 Cabin',
            'front_yard': '🌲 Front Yard', 
            'forest': '🌲 Forest',
            'creek': '🏞️ Creek',
            'pond': '🌊 Pond',
            'farm': '🌱 Farm'
        }
        
        for loc_key, loc_name in locations.items():
            if st.button(loc_name, key=f"move_{loc_key}"):
                game_state['current_location'] = loc_key
                st.rerun()
        
        # Weather and tips
        st.subheader("💡 Tips")
        tips = [
            "🪓 Chop trees for wood to build structures",
            "💧 Collect water from the creek or pond", 
            "🌱 Till soil before planting seeds",
            "🌾 Water your crops daily for best growth",
            "🛌 Sleep to restore energy and advance time",
            "🦌 Talk to forest animals for wisdom"
        ]
        
        for tip in tips:
            st.write(tip)

if __name__ == "__main__":
    main()
