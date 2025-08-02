import re
import logging
from typing import Dict, Any, Optional, List
from utils.data_loader import customer_data_loader

logger = logging.getLogger(__name__)

class UserIdentifier:
    """Utility class to identify users from their queries"""
    
    def __init__(self):
        self.data_loader = customer_data_loader
        
    def extract_user_info_from_query(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Attempt to extract user information from the query text
        Looks for account IDs, email addresses, names, etc.
        """
        query_lower = query.lower()
        
        # Try to find account ID patterns
        account_id = self._extract_account_id(query)
        if account_id:
            customer = self.data_loader.get_customer_by_id(account_id)
            if customer:
                logger.info(f"Found customer by account ID: {account_id}")
                return customer
        
        # Try to find email addresses
        email = self._extract_email(query)
        if email:
            customer = self._find_customer_by_email(email)
            if customer:
                logger.info(f"Found customer by email: {email}")
                return customer
        
        # Try to find names (this is less reliable)
        name = self._extract_name_patterns(query)
        if name:
            customer = self._find_customer_by_name(name)
            if customer:
                logger.info(f"Found customer by name: {name}")
                return customer
        
        logger.info("No customer identified from query")
        return None
    
    def _extract_account_id(self, query: str) -> Optional[str]:
        """Extract account ID patterns like USER123456"""
        patterns = [
            r'USER\d{6}',  # USER123456
            r'user\d{6}',  # user123456
            r'account[:\s]+([A-Z0-9]+)',  # account: USER123456
            r'id[:\s]+([A-Z0-9]+)',  # id: USER123456
            r'my account is ([A-Z0-9]+)',  # my account is USER123456
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                if pattern.startswith('USER') or pattern.startswith('user'):
                    return match.group(0).upper()
                else:
                    return match.group(1).upper()
        
        return None
    
    def _extract_email(self, query: str) -> Optional[str]:
        """Extract email addresses from query"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        match = re.search(email_pattern, query)
        return match.group(0) if match else None
    
    def _extract_name_patterns(self, query: str) -> Optional[str]:
        """Extract name patterns from common phrases"""
        name_patterns = [
            r'my name is ([A-Za-z\s]+)',
            r'i am ([A-Za-z\s]+)',
            r'this is ([A-Za-z\s]+)',
            r'i\'m ([A-Za-z\s]+)',
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Filter out common words that aren't names
                if len(name.split()) <= 3 and not any(word in name.lower() for word in ['calling', 'having', 'looking', 'trying']):
                    return name.title()
        
        return None
    
    def _find_customer_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find customer by email address"""
        customers = self.data_loader._customers
        for customer in customers:
            if customer.get('email', '').lower() == email.lower():
                return customer
        return None
    
    def _find_customer_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Find customer by name (fuzzy matching)"""
        customers = self.data_loader._customers
        name_parts = name.lower().split()
        
        for customer in customers:
            customer_name = customer.get('name', '').lower()
            
            # Exact match
            if customer_name == name.lower():
                return customer
            
            # Partial match (first name or last name)
            customer_name_parts = customer_name.split()
            if any(part in customer_name_parts for part in name_parts):
                return customer
        
        return None
    
    def suggest_similar_customers(self, query: str) -> List[Dict[str, Any]]:
        """Suggest customers that might match partial information in the query"""
        suggestions = []
        query_lower = query.lower()
        
        # Look for partial matches in names, emails, or other identifiers
        customers = self.data_loader._customers
        
        for customer in customers:
            score = 0
            
            # Check name similarity
            name_parts = customer.get('name', '').lower().split()
            if any(part in query_lower for part in name_parts):
                score += 2
            
            # Check email domain
            email = customer.get('email', '')
            if email and '@' in email:
                domain = email.split('@')[1]
                if domain in query_lower:
                    score += 1
            
            # Check subscription type
            subscription = customer.get('subscription', '').lower()
            if subscription in query_lower:
                score += 1
            
            if score > 0:
                suggestions.append((customer, score))
        
        # Sort by score and return top matches
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return [customer for customer, score in suggestions[:3]]
    
    def is_identification_attempt(self, query: str) -> bool:
        """Check if the query seems to be attempting user identification"""
        identification_keywords = [
            'my account', 'my name', 'i am', 'this is', 'my email',
            'account id', 'user id', 'my profile', 'logged in as'
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in identification_keywords)

# Global instance
user_identifier = UserIdentifier()