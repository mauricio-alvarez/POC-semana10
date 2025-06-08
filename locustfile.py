# locustfile.py
from locust import HttpUser, task, between
import random
import json

class PokemonAPIUser(HttpUser):
    """
    Locust user class to test Pokemon API endpoints with POST requests
    
    This will generate between 1000-10000 requests as required
    Run with: locust --host=http://localhost:8000 --users=100 --spawn-rate=10 --run-time=300s
    """
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    # List of popular Pokemon names to test with
    pokemon_names = [
        "charizard", "pikachu", "bulbasaur", "squirtle", "wartortle", "blastoise",
        "caterpie", "metapod", "butterfree", "weedle", "kakuna", "beedrill",
        "pidgey", "pidgeotto", "pidgeot", "rattata", "raticate", "spearow",
        "fearow", "ekans", "arbok", "raichu", "sandshrew", "sandslash",
        "nidoran", "nidorina", "nidoqueen", "nidorino", "nidoking", "clefairy",
        "clefable", "vulpix", "ninetales", "jigglypuff", "wigglytuff", "zubat",
        "golbat", "oddish", "gloom", "vileplume", "paras", "parasect",
        "venonat", "venomoth", "diglett", "dugtrio", "meowth", "persian",
        "psyduck", "golduck", "mankey", "primeape", "growlithe", "arcanine",
        "poliwag", "poliwhirl", "poliwrath", "abra", "kadabra", "alakazam",
        "machop", "machoke", "machamp", "bellsprout", "weepinbell", "victreebel",
        "tentacool", "tentacruel", "geodude", "graveler", "golem", "ponyta",
        "rapidash", "slowpoke", "slowbro", "magnemite", "magneton", "farfetchd",
        "doduo", "dodrio", "seel", "dewgong", "grimer", "muk", "shellder",
        "cloyster", "gastly", "haunter", "gengar", "onix", "drowzee", "hypno",
        "krabby", "kingler", "voltorb", "electrode", "exeggcute", "exeggutor",
        "cubone", "marowak", "hitmonlee", "hitmonchan", "lickitung", "koffing",
        "weezing", "rhyhorn", "rhydon", "chansey", "tangela", "kangaskhan"
    ]
    
    def on_start(self):
        """Called when a user starts"""
        print(f"Starting load test for Pokemon API")
    
    @task(10)  # Higher weight - most common request
    def get_pokemon_data(self):
        """Test the main Pokemon data endpoint with POST request"""
        pokemon_name = random.choice(self.pokemon_names)
        payload = {"Pokemon_Name": pokemon_name}
        
        with self.client.post(
            "/poke/search",
            json=payload,
            headers={"Content-Type": "application/json"},
            catch_response=True,
            name="POST /poke/search"
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if "name" in data and "stats" in data and "image" in data:
                        response.success()
                        print(f"✓ Successfully got data for {pokemon_name}")
                    else:
                        response.failure(f"Invalid response structure for {pokemon_name}")
                except json.JSONDecodeError:
                    response.failure(f"Invalid JSON response for {pokemon_name}")
            elif response.status_code == 404:
                # 404 is acceptable for non-existent Pokemon
                response.success()
                print(f"? Pokemon {pokemon_name} not found (404)")
            else:
                response.failure(f"Unexpected status code: {response.status_code}")
    
    @task(5)  # Medium weight
    def get_pokemon_image(self):
        """Test the Pokemon image endpoint"""
        pokemon_name = random.choice(self.pokemon_names)
        
        with self.client.get(
            f"/images/{pokemon_name}/0.jpg",
            catch_response=True,
            name="GET /images/[name]"
        ) as response:
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if content_type.startswith('image/'):
                    response.success()
                    print(f"✓ Successfully got image for {pokemon_name}")
                else:
                    response.failure(f"Response is not an image for {pokemon_name}")
            elif response.status_code == 404:
                # 404 is acceptable for non-existent images
                response.success()
                print(f"? Image for {pokemon_name} not found (404)")
            else:
                response.failure(f"Unexpected status code: {response.status_code}")
    
    @task(2)  # Lower weight - test error handling
    def get_invalid_pokemon(self):
        """Test with invalid Pokemon names to test error handling"""
        invalid_names = [
            "invalidpokemon", "notreal", "fakemon", "testpokemon",
            "123456", "special@char", "toolongpokemonname" * 10
        ]
        pokemon_name = random.choice(invalid_names)
        payload = {"Pokemon_Name": pokemon_name}
        
        with self.client.post(
            "/poke/search",
            json=payload,
            headers={"Content-Type": "application/json"},
            catch_response=True,
            name="POST /poke/search/[invalid]"
        ) as response:
            if response.status_code in [404, 400]:
                response.success()
                print(f"✓ Correctly handled invalid Pokemon: {pokemon_name}")
            else:
                response.failure(f"Unexpected status for invalid Pokemon {pokemon_name}: {response.status_code}")
    
    @task(1)  # Lowest weight - stress test with concurrent requests
    def stress_test_pokemon(self):
        """Make multiple rapid requests to test concurrency"""
        pokemon_name = random.choice(self.pokemon_names[:10])  # Use only common Pokemon
        payload = {"Pokemon_Name": pokemon_name}
        
        # Make 3 rapid requests
        for i in range(3):
            with self.client.post(
                "/poke/search",
                json=payload,
                headers={"Content-Type": "application/json"},
                catch_response=True,
                name="POST /poke/search/[stress]"
            ) as response:
                if response.status_code in [200, 404]:
                    response.success()
                else:
                    response.failure(f"Stress test failed for {pokemon_name}")


class PokemonAPILoadTest(HttpUser):
    """
    Alternative user class for focused load testing
    Use this for high-volume testing
    """
    wait_time = between(0.5, 1.5)  # Faster requests
    
    pokemon_names = ["charizard", "pikachu", "bulbasaur", "squirtle", "wartortle"]
    
    @task
    def rapid_pokemon_requests(self):
        """Make rapid requests to generate high volume of logs"""
        pokemon_name = random.choice(self.pokemon_names)
        payload = {"Pokemon_Name": pokemon_name}
        
        self.client.post(
            "/poke/search",
            json=payload,
            headers={"Content-Type": "application/json"}
        )


# Custom test scenarios
def create_test_scenarios():
    """
    Function to create different test scenarios
    """
    scenarios = {
        # Normal load test - 100 users over 5 minutes
        "normal_load": {
            "users": 100,
            "spawn_rate": 10,
            "run_time": "300s",
            "description": "Normal load test - 100 users, ~3000-5000 requests"
        },
        
        # High load test - 500 users over 10 minutes  
        "high_load": {
            "users": 500,
            "spawn_rate": 20,
            "run_time": "600s", 
            "description": "High load test - 500 users, ~15000-25000 requests"
        },
        
        # Spike test - 200 users spawned quickly
        "spike_test": {
            "users": 200,
            "spawn_rate": 50,
            "run_time": "180s",
            "description": "Spike test - 200 users spawned quickly"
        }
    }
    return scenarios


if __name__ == "__main__":
    print("Pokemon API Locust Test File (POST with JSON)")
    print("=" * 50)
    print("Usage examples:")
    print("1. Basic test (1000+ requests):")
    print("   locust --host=http://localhost:8000 --users=50 --spawn-rate=5 --run-time=300s")
    print()
    print("2. High volume test (5000+ requests):")
    print("   locust --host=http://localhost:8000 --users=200 --spawn-rate=20 --run-time=600s")
    print()
    print("3. Maximum test (10000+ requests):")
    print("   locust --host=http://localhost:8000 --users=500 --spawn-rate=25 --run-time=900s")
    print()
    print("4. Web UI mode:")
    print("   locust --host=http://localhost:8000")
    print("   Then open http://localhost:8089")
    
    scenarios = create_test_scenarios()
    print("\nPredefined scenarios:")
    for name, config in scenarios.items():
        print(f"  {name}: {config['description']}")
    
    print("\nPOST Request Format:")
    print('  {"Pokemon_Name": "pikachu"}')