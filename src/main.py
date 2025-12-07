import argparse
import hashlib
import os
import subprocess
from .agents.mtom_negotiation_agent import MToM_NegotiationAgent
from .models.negotiation_state import NegotiationState


def _git_commit_hash() -> str:
    try:
        out = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL)
        return out.decode().strip()
    except Exception:
        return "unknown"


def _config_hash(config_dir: str = "experiments/config") -> str:
    # Hash the concatenation of YAML files in the config directory so we can
    # identify which configuration set produced results.
    h = hashlib.sha1()
    try:
        for fname in sorted(os.listdir(config_dir)):
            if fname.endswith(('.yml', '.yaml')):
                path = os.path.join(config_dir, fname)
                with open(path, 'rb') as f:
                    h.update(f.read())
        return h.hexdigest()[:8]
    except Exception:
        return "unknown"


def main():
    """Main demonstration of the MToM negotiation agent.

    Run with `--version` to print a short commit hash and a configuration
    manifest hash useful for reproducibility bookkeeping.
    """
    parser = argparse.ArgumentParser(prog="mtom")
    parser.add_argument('--version', action='store_true', help='print commit + config hash and exit')
    args = parser.parse_args()

    if args.version:
        print(f"commit:{_git_commit_hash()} config:{_config_hash()}")
        return

    print("🤖 Machine Theory of Mind - Negotiation Demo")
    print("=" * 50)
    
    # Create agents with different social preferences
    social_agent = MToM_NegotiationAgent(lambda_social=0.8)
    balanced_agent = MToM_NegotiationAgent(lambda_social=0.5)
    task_agent = MToM_NegotiationAgent(lambda_social=0.2)
    
    agents = [("Social-focused", social_agent),
              ("Balanced", balanced_agent), 
              ("Task-focused", task_agent)]
    
    # Test each agent
    for name, agent in agents:
        print(f"\n{name} Agent:")
        print("-" * 30)
        
        negotiation = NegotiationState(total_resources=10, our_offer=0, their_offer=0)
        
        for round in range(2):
            offer = agent.make_offer(negotiation)
            mental_state = agent.get_mental_state()
            print(f"  Round {round+1}: Offer {offer}/10")
            print(f"    Mental State: warmth={mental_state.warmth:.2f}, competence={mental_state.competence:.2f}")


if __name__ == "__main__":
    main()