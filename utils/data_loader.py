import json
import random
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class CustomerDataLoader:
    """Utility class to load and manage customer data from JSON file"""
    
    def __init__(self, data_file_path: str = "data/customer_data.json"):
        self.data_file_path = data_file_path
        self._data = None
        self._customers = []
        self._system_status = {}
        self.load_data()
    
    def load_data(self) -> None:
        """Load customer data from JSON file"""
        try:
            # Get the absolute path relative to the project root
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            full_path = os.path.join(project_root, self.data_file_path)
            
            with open(full_path, 'r', encoding='utf-8') as file:
                self._data = json.load(file)
                self._customers = self._data.get('customers', [])
                self._system_status = self._data.get('system_status', {})
                
            logger.info(f"Loaded {len(self._customers)} customer records from {self.data_file_path}")
            
        except FileNotFoundError:
            logger.error(f"Customer data file not found: {full_path}")
            self._initialize_fallback_data()
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON file: {e}")
            self._initialize_fallback_data()
        except Exception as e:
            logger.error(f"Unexpected error loading customer data: {e}")
            self._initialize_fallback_data()
    
    def _initialize_fallback_data(self) -> None:
        """Initialize with minimal fallback data if file loading fails"""
        self._customers = [{
            "id": "USER_FALLBACK",
            "name": "Guest User",
            "email": "guest@example.com",
            "subscription": "Basic Plan",
            "join_date": "2024-01-01",
            "last_login": "2024-07-31",
            "billing_info": {
                "current_balance": 9.99,
                "last_payment": "2024-07-01",
                "payment_method": "****-0000",
                "next_billing": "2024-08-01",
                "total_spent": 9.99,
                "payment_status": "active"
            },
            "technical_profile": {
                "platform": "Web",
                "browser": "Chrome",
                "last_issue": "None",
                "support_tickets": 0
            }
        }]
        self._system_status = {
            "overall_status": "operational",
            "last_maintenance": "2024-07-01",
            "known_issues": [],
            "recent_updates": []
        }
        logger.warning("Using fallback customer data")
    
    def get_random_customer(self) -> Dict[str, Any]:
        """Get a random customer record"""
        if not self._customers:
            self.load_data()
        
        return random.choice(self._customers) if self._customers else {}
    
    def get_customer_by_id(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific customer by ID"""
        for customer in self._customers:
            if customer.get('id') == customer_id:
                return customer
        return None
    
    def get_customers_by_subscription(self, subscription_type: str) -> list:
        """Get all customers with a specific subscription type"""
        return [
            customer for customer in self._customers 
            if customer.get('subscription', '').lower() == subscription_type.lower()
        ]
    
    def get_customers_with_issues(self) -> list:
        """Get customers who have open support tickets"""
        return [
            customer for customer in self._customers 
            if customer.get('technical_profile', {}).get('support_tickets', 0) > 0
        ]
    
    def get_customers_with_billing_issues(self) -> list:
        """Get customers with billing problems (overdue, failed payments)"""
        return [
            customer for customer in self._customers 
            if customer.get('billing_info', {}).get('payment_status') in ['overdue', 'failed']
        ]
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status information"""
        return self._system_status
    
    def get_total_customers(self) -> int:
        """Get total number of customers"""
        return len(self._customers)
    
    def get_customer_stats(self) -> Dict[str, Any]:
        """Get summary statistics about customers"""
        if not self._customers:
            return {}
        
        subscription_counts = {}
        payment_status_counts = {}
        total_revenue = 0
        
        for customer in self._customers:
            # Count subscriptions
            sub_type = customer.get('subscription', 'Unknown')
            subscription_counts[sub_type] = subscription_counts.get(sub_type, 0) + 1
            
            # Count payment statuses
            payment_status = customer.get('billing_info', {}).get('payment_status', 'unknown')
            payment_status_counts[payment_status] = payment_status_counts.get(payment_status, 0) + 1
            
            # Sum total revenue
            total_revenue += customer.get('billing_info', {}).get('total_spent', 0)
        
        return {
            "total_customers": len(self._customers),
            "subscription_breakdown": subscription_counts,
            "payment_status_breakdown": payment_status_counts,
            "total_revenue": round(total_revenue, 2),
            "average_revenue_per_customer": round(total_revenue / len(self._customers), 2)
        }
    
    def reload_data(self) -> None:
        """Reload data from file (useful for testing or data updates)"""
        self.load_data()

# Global instance for easy import
customer_data_loader = CustomerDataLoader()