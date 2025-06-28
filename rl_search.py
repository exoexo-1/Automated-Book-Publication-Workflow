import numpy as np
import chromadb
from typing import Dict, List, Tuple, Optional
import json
from collections import defaultdict
import pickle
import os

class RLSearchAgent:
    """Reinforcement Learning agent for intelligent content retrieval"""
    
    def __init__(self, chroma_client, collection_name="books_collection", 
                 learning_rate=0.1, epsilon=0.1, discount_factor=0.95):
        self.chroma_client = chroma_client
        self.collection = chroma_client.get_or_create_collection(collection_name)
        
        # RL parameters
        self.learning_rate = learning_rate
        self.epsilon = epsilon  # exploration rate
        self.discount_factor = discount_factor
        
        # Q-table: state-action values
        self.q_table = defaultdict(lambda: defaultdict(float))
        
        # Search history and rewards
        self.search_history = []
        self.state_features = ['stage', 'version', 'relevance_score', 'user_feedback']
        
        # Load existing Q-table if available
        self.load_q_table()
    
    def get_state_key(self, query: str, metadata: Dict) -> str:
        """Convert search context to state representation"""
        stage = metadata.get('stage', 'unknown')
        version = metadata.get('version', 0)
        
        # Simple state encoding
        state = f"{stage}_{version}_{len(query)//10}"
        return state
    
    def get_available_actions(self) -> List[str]:
        """Define possible search actions"""
        return [
            'semantic_search',      # Vector similarity search
            'metadata_filter',      # Filter by stage/version
            'hybrid_search',        # Combine semantic + metadata
            'latest_version',       # Get most recent version
            'stage_progression'     # Follow editing workflow
        ]
    
    def select_action(self, state: str) -> str:
        """Epsilon-greedy action selection"""
        if np.random.random() < self.epsilon:
            # Exploration: random action
            return np.random.choice(self.get_available_actions())
        else:
            # Exploitation: best known action
            actions = self.get_available_actions()
            q_values = [self.q_table[state][action] for action in actions]
            best_action_idx = np.argmax(q_values)
            return actions[best_action_idx]
    
    def semantic_search(self, query: str, n_results: int = 5) -> List[Dict]:
        """Perform semantic search using ChromaDB"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )
        
        search_results = []
        for i, doc in enumerate(results['documents'][0]):
            search_results.append({
                'content': doc,
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i],
                'relevance_score': 1 / (1 + results['distances'][0][i])
            })
        
        return search_results
    
    def metadata_filter_search(self, query: str, stage: str = None, 
                              version_range: Tuple = None) -> List[Dict]:
        """Search with metadata filtering"""
        where_clause = {}
        if stage:
            where_clause['stage'] = stage
        if version_range:
            where_clause['version'] = {"$gte": version_range[0], "$lte": version_range[1]}
        
        results = self.collection.query(
            query_texts=[query],
            where=where_clause if where_clause else None,
            n_results=5,
            include=["documents", "metadatas", "distances"]
        )
        
        search_results = []
        for i, doc in enumerate(results['documents'][0]):
            search_results.append({
                'content': doc,
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i],
                'relevance_score': 1 / (1 + results['distances'][0][i])
            })
        
        return search_results
    
    def hybrid_search(self, query: str, stage_preference: str = None) -> List[Dict]:
        """Combine semantic and metadata-based search"""
        # Get semantic results
        semantic_results = self.semantic_search(query, n_results=10)
        
        # Apply stage preference scoring
        for result in semantic_results:
            stage_bonus = 0
            if stage_preference and result['metadata'].get('stage') == stage_preference:
                stage_bonus = 0.2
            
            # Combine relevance with stage preference
            result['hybrid_score'] = result['relevance_score'] + stage_bonus
        
        # Sort by hybrid score
        semantic_results.sort(key=lambda x: x['hybrid_score'], reverse=True)
        return semantic_results[:5]
    
    def get_latest_version_search(self, base_id: str) -> List[Dict]:
        """Get the latest version of content"""
        all_results = self.collection.get(include=["documents", "metadatas"])
        
        # Filter by base_id and find latest version
        relevant_docs = []
        for i, metadata in enumerate(all_results['metadatas']):
            if metadata.get('versioned_id', '').startswith(base_id):
                relevant_docs.append({
                    'content': all_results['documents'][i],
                    'metadata': metadata,
                    'relevance_score': metadata.get('version', 0) / 100.0  # Higher version = more relevant
                })
        
        # Sort by version (descending)
        relevant_docs.sort(key=lambda x: x['metadata'].get('version', 0), reverse=True)
        return relevant_docs[:5]
    
    def stage_progression_search(self, query: str) -> List[Dict]:
        """Search following the editing workflow progression"""
        stage_order = ['raw', 'rewritten', 'reviewed', 'edited', 'final']
        results = []
        
        for stage in reversed(stage_order):  # Start from most refined
            stage_results = self.metadata_filter_search(query, stage=stage)
            if stage_results:
                # Boost score based on stage progression
                stage_boost = (len(stage_order) - stage_order.index(stage)) * 0.1
                for result in stage_results:
                    result['relevance_score'] += stage_boost
                results.extend(stage_results[:2])  # Take top 2 from each stage
        
        # Remove duplicates and sort
        unique_results = {}
        for result in results:
            doc_id = result['metadata'].get('versioned_id', '')
            if doc_id not in unique_results:
                unique_results[doc_id] = result
        
        final_results = list(unique_results.values())
        final_results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return final_results[:5]
    
    def execute_action(self, action: str, query: str, context: Dict = None) -> List[Dict]:
        """Execute the selected search action"""
        context = context or {}
        
        if action == 'semantic_search':
            return self.semantic_search(query)
        elif action == 'metadata_filter':
            return self.metadata_filter_search(
                query, 
                stage=context.get('preferred_stage'),
                version_range=context.get('version_range')
            )
        elif action == 'hybrid_search':
            return self.hybrid_search(query, context.get('preferred_stage'))
        elif action == 'latest_version':
            base_id = context.get('base_id', 'chapter1')
            return self.get_latest_version_search(base_id)
        elif action == 'stage_progression':
            return self.stage_progression_search(query)
        else:
            return self.semantic_search(query)  # Default fallback
    
    def calculate_reward(self, results: List[Dict], user_feedback: Dict = None) -> float:
        """Calculate reward based on search results quality"""
        if not results:
            return -1.0
        
        # Base reward from relevance scores
        avg_relevance = np.mean([r['relevance_score'] for r in results])
        
        # Bonus for result diversity (different stages/versions)
        stages = set(r['metadata'].get('stage', '') for r in results)
        diversity_bonus = len(stages) * 0.1
        
        # User feedback reward
        feedback_reward = 0
        if user_feedback:
            if user_feedback.get('clicked_result', False):
                feedback_reward += 0.5
            if user_feedback.get('satisfaction_score', 0) > 3:
                feedback_reward += 0.3
        
        total_reward = avg_relevance + diversity_bonus + feedback_reward
        return min(total_reward, 2.0)  # Cap reward at 2.0
    
    def update_q_value(self, state: str, action: str, reward: float, next_state: str = None):
        """Update Q-value using Q-learning update rule"""
        current_q = self.q_table[state][action]
        
        if next_state:
            # Get maximum Q-value for next state
            next_q_values = [self.q_table[next_state][a] for a in self.get_available_actions()]
            max_next_q = max(next_q_values) if next_q_values else 0
        else:
            max_next_q = 0
        
        # Q-learning update
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )
        
        self.q_table[state][action] = new_q
    
    def intelligent_search(self, query: str, context: Dict = None, 
                          user_feedback: Dict = None) -> List[Dict]:
        """Main RL-powered search method"""
        context = context or {}
        
        # Create state representation
        state = self.get_state_key(query, context)
        
        # Select action using RL policy
        action = self.select_action(state)
        
        # Execute search
        results = self.execute_action(action, query, context)
        
        # Calculate reward
        reward = self.calculate_reward(results, user_feedback)
        
        # Update Q-value
        self.update_q_value(state, action, reward)
        
        # Store search history
        self.search_history.append({
            'query': query,
            'state': state,
            'action': action,
            'reward': reward,
            'results_count': len(results)
        })
        
        self.epsilon = max(0.01, self.epsilon * 0.995)
        
        return results
    
    def save_q_table(self, filepath: str = "q_table.pkl"):
        """Save Q-table to disk"""
        with open(filepath, 'wb') as f:
            pickle.dump(dict(self.q_table), f)
    
    def load_q_table(self, filepath: str = "q_table.pkl"):
        """Load Q-table from disk"""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'rb') as f:
                    loaded_q_table = pickle.load(f)
                    self.q_table = defaultdict(lambda: defaultdict(float), loaded_q_table)
                print("Q-table loaded successfully")
            except Exception as e:
                print(f"Error loading Q-table: {e}")
    
    def get_search_stats(self) -> Dict:
        """Get search performance statistics"""
        if not self.search_history:
            return {}
        
        recent_searches = self.search_history[-50:]  
        avg_reward = np.mean([s['reward'] for s in recent_searches])
        
        action_counts = defaultdict(int)
        for search in recent_searches:
            action_counts[search['action']] += 1
        
        return {
            'total_searches': len(self.search_history),
            'average_reward': avg_reward,
            'current_epsilon': self.epsilon,
            'action_distribution': dict(action_counts),
            'q_table_size': len(self.q_table)
        }

def create_rl_search_agent(chroma_client):
    """Factory function to create RL search agent"""
    return RLSearchAgent(chroma_client)