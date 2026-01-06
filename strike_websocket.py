import requests
import time
import threading
from collections import defaultdict
from datetime import datetime
from dhanhq import DhanContext, MarketFeed

class MarketFeedManager:
    def __init__(self, client_id, access_token, api_url, storage_api_url, poll_interval=30):
        """
        Initialize Market Feed Manager
        
        Args:
            client_id: Dhan client ID
            access_token: Dhan access token
            api_url: URL to poll for new security IDs
            storage_api_url: URL to store market data
            poll_interval: Seconds between polling for new securities
        """
        self.dhan_context = DhanContext(client_id, access_token)
        self.api_url = api_url
        self.storage_api_url = storage_api_url
        self.poll_interval = poll_interval
        self.version = "v2"
        
        # Track active subscriptions: {(exchange, security_id): True}
        self.active_subscriptions = {}
        self.market_feed = None
        self.running = False
        self.feed_thread = None
        self.poll_thread = None
        
        # Exchange mapping
        self.exchange_map = {
            'IDX': MarketFeed.IDX,
            'MCX': MarketFeed.MCX,
            'BSE_FNO': MarketFeed.BSE_FNO,
            'BSE': MarketFeed.BSE,
            'NSE_FNO': MarketFeed.NSE_FNO,
            'NSE': MarketFeed.NSE,
            'BSE_CURR': MarketFeed.BSE_CURR,
            'NSE_CURR': MarketFeed.NSE_CURR
        }
    
    def fetch_securities_from_api(self):
        """
        Poll API to get list of securities to subscribe
        
        Expected API response format:
        {
            "securities": [
                {"exchange": "NSE", "security_id": "1333"},
                {"exchange": "MCX", "security_id": "11915"},
                ...
            ]
        }
        """
        try:
            response = requests.get(self.api_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('securities', [])
        except Exception as e:
            print(f"Error fetching securities from API: {e}")
            return []
    
    def store_market_data(self, data):
        """
        Send market data to storage API
        
        Args:
            data: Market feed data to store
        """
        try:
            # Add timestamp if not present
            if 'timestamp' not in data:
                data['timestamp'] = datetime.now().isoformat()
            
            response = requests.post(
                self.storage_api_url,
                json=data,
                timeout=5
            )
            response.raise_for_status()
            print(f"Stored data for security_id: {data.get('security_id')}")
        except Exception as e:
            print(f"Error storing market data: {e}")
    
    def initialize_market_feed(self, initial_securities):
        """
        Initialize market feed with initial securities
        
        Args:
            initial_securities: List of dicts with 'exchange' and 'security_id'
        """
        if not initial_securities:
            print("No initial securities to subscribe")
            return False
        
        instruments = []
        for sec in initial_securities:
            exchange = self.exchange_map.get(sec['exchange'])
            security_id = str(sec['security_id'])
            
            if exchange is not None:
                instruments.append((exchange, security_id, MarketFeed.Ticker))
                self.active_subscriptions[(sec['exchange'], security_id)] = True
        
        if not instruments:
            print("No valid instruments to subscribe")
            return False
        
        try:
            self.market_feed = MarketFeed(self.dhan_context, instruments, self.version)
            print(f"Initialized market feed with {len(instruments)} instruments")
            return True
        except Exception as e:
            print(f"Error initializing market feed: {e}")
            return False
    
    def process_market_feed(self):
        """
        Continuously process market feed data
        """
        while self.running:
            try:
                if self.market_feed:
                    response = self.market_feed.get_data()
                    if response:
                        print(f"Received: {response}")
                        # Store data via API
                        self.store_market_data(response)
                time.sleep(0.1)  # Small delay to prevent CPU overuse
            except Exception as e:
                print(f"Error processing market feed: {e}")
                time.sleep(1)
    
    def poll_and_update_subscriptions(self):
        """
        Periodically poll API and update subscriptions
        """
        while self.running:
            try:
                # Fetch latest securities from API
                securities = self.fetch_securities_from_api()
                
                if securities:
                    # Determine new subscriptions
                    new_subscriptions = []
                    for sec in securities:
                        key = (sec['exchange'], str(sec['security_id']))
                        if key not in self.active_subscriptions:
                            exchange = self.exchange_map.get(sec['exchange'])
                            if exchange is not None:
                                new_subscriptions.append(
                                    (exchange, str(sec['security_id']), MarketFeed.Ticker)
                                )
                                self.active_subscriptions[key] = True
                    
                    # Subscribe to new instruments
                    if new_subscriptions and self.market_feed:
                        try:
                            self.market_feed.subscribe_symbols(new_subscriptions)
                            print(f"Subscribed to {len(new_subscriptions)} new instruments")
                        except Exception as e:
                            print(f"Error subscribing to new instruments: {e}")
                
                # Wait before next poll
                time.sleep(self.poll_interval)
                
            except Exception as e:
                print(f"Error in polling thread: {e}")
                time.sleep(self.poll_interval)
    
    def start(self):
        """
        Start the market feed manager
        """
        # Fetch initial securities
        print("Fetching initial securities...")
        initial_securities = self.fetch_securities_from_api()
        
        if not initial_securities:
            print("No initial securities found. Waiting for securities...")
            # Wait and retry
            time.sleep(self.poll_interval)
            initial_securities = self.fetch_securities_from_api()
            
            if not initial_securities:
                print("Still no securities. Exiting...")
                return
        
        # Initialize market feed
        if not self.initialize_market_feed(initial_securities):
            print("Failed to initialize market feed")
            return
        
        self.running = True
        
        # Start market feed in separate thread
        self.feed_thread = threading.Thread(target=self._run_feed, daemon=True)
        self.feed_thread.start()
        
        # Start polling thread
        self.poll_thread = threading.Thread(target=self.poll_and_update_subscriptions, daemon=True)
        self.poll_thread.start()
        
        # Start processing market data
        self.process_market_feed()
    
    def _run_feed(self):
        """
        Run market feed forever in background thread
        """
        try:
            if self.market_feed:
                self.market_feed.run_forever()
        except Exception as e:
            print(f"Market feed stopped: {e}")
            self.running = False
    
    def stop(self):
        """
        Stop the market feed manager
        """
        print("Stopping market feed manager...")
        self.running = False
        
        if self.feed_thread:
            self.feed_thread.join(timeout=5)
        
        if self.poll_thread:
            self.poll_thread.join(timeout=5)
        
        if self.market_feed:
            try:
                self.market_feed.disconnect()
                print("Disconnected from market feed")
            except Exception as e:
                print(f"Error disconnecting: {e}")


# Example usage
if __name__ == "__main__":
    # Configuration
    CLIENT_ID = "your_client_id"
    ACCESS_TOKEN = "your_access_token"
    API_URL = "http://your-server.com/api/securities"  # API to poll for securities
    STORAGE_API_URL = "http://your-server.com/api/store-data"  # API to store market data
    POLL_INTERVAL = 30  # Poll every 30 seconds
    
    # Create and start manager
    manager = MarketFeedManager(
        client_id=CLIENT_ID,
        access_token=ACCESS_TOKEN,
        api_url=API_URL,
        storage_api_url=STORAGE_API_URL,
        poll_interval=POLL_INTERVAL
    )
    
    try:
        print("Starting Market Feed Manager...")
        manager.start()
    except KeyboardInterrupt:
        print("\nReceived interrupt signal...")
    finally:
        manager.stop()
        print("Market Feed Manager stopped")