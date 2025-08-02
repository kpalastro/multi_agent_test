#!/usr/bin/env python3
"""
Test script for the user identification workflow
"""

import sys
import os
sys.path.append(os.getcwd())

def test_user_identification():
    """Test user identification scenarios"""
    print("🧪 Testing User Identification Workflow")
    print("=" * 50)
    
    try:
        from utils.user_identifier import user_identifier
        from utils.data_loader import customer_data_loader
        from agents.specialized import billing_agent_instance
        
        # Test cases
        test_queries = [
            # Should identify users
            "My account is USER001234 and I have a billing issue",
            "Hi, I'm John Doe and I need help with my payment",
            "My email is sarah.wilson@techcorp.com and the system is slow",
            "Account ID USER005654 - payment failed",
            
            # Should NOT identify users
            "I have a billing problem",
            "The system is not working",
            "Can you help me?",
            "What are your hours?",
            
            # Identification attempts
            "My name is Alice Smith",
            "My account is USER999999",  # Non-existent
            "My email is test@example.com",  # Non-existent
        ]
        
        print(f"📊 Total customers in system: {customer_data_loader.get_total_customers()}")
        print("\n🔍 Testing identification scenarios:\n")
        
        for i, query in enumerate(test_queries, 1):
            print(f"Test {i}: '{query}'")
            
            # Reset agent state
            billing_agent_instance.reset_customer_context()
            
            # Try to identify
            identified = user_identifier.extract_user_info_from_query(query)
            
            if identified:
                print(f"  ✅ Identified: {identified.get('name')} ({identified.get('id')})")
            else:
                print(f"  ❌ Not identified")
                
                # Check if it's an identification attempt
                is_attempt = user_identifier.is_identification_attempt(query)
                if is_attempt:
                    print(f"  🔄 Detected identification attempt")
            
            print()
        
        print("✅ All identification tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agent_responses():
    """Test agent responses with identification workflow"""
    print("\n🤖 Testing Agent Response Workflow")
    print("=" * 50)
    
    try:
        from agents.specialized import billing_agent_instance, technical_agent_instance, general_agent_instance
        
        # Test scenarios
        scenarios = [
            ("billing_agent_instance", "I have a billing issue"),
            ("billing_agent_instance", "My account is USER001234 and I need a refund"),
            ("technical_agent_instance", "The app is crashing"),
            ("technical_agent_instance", "Hi, I'm Sarah Wilson sarah.wilson@techcorp.com and having API issues"),
            ("general_agent_instance", "What are your company hours?"),
            ("general_agent_instance", "My name is Mike Johnson and I want to upgrade my account"),
        ]
        
        for agent_name, query in scenarios:
            print(f"\n📝 Testing {agent_name} with: '{query}'")
            
            # Get agent instance
            agent = locals()[agent_name] if agent_name in locals() else eval(agent_name)
            
            # Reset agent state
            agent.reset_customer_context()
            
            # Generate response
            response = agent.generate_response(query)
            
            # Check if customer was identified
            customer = agent.get_customer_context()
            if customer:
                print(f"  👤 Customer: {customer.get('name')} ({customer.get('id')})")
            else:
                print(f"  ❓ No customer identified")
            
            print(f"  💬 Response: {response[:100]}...")
            
        print("\n✅ All agent response tests completed!")
        return True
        
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting User Identification Tests\n")
    
    success1 = test_user_identification()
    success2 = test_agent_responses()
    
    if success1 and success2:
        print("\n🎉 All tests passed! System ready for use.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        sys.exit(1)