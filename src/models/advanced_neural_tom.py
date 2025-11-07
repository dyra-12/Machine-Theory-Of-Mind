import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

class AdvancedNeuralToM(nn.Module):
    """
    Advanced architecture with explicit lambda conditioning and separate reasoning pathways.
    Uses attention mechanisms to focus on different aspects based on social preferences.
    """
    
    def __init__(self, input_size: int = 2, hidden_size: int = 128, output_size: int = 2):
        super(AdvancedNeuralToM, self).__init__()
        
        # Feature extraction
        self.feature_extractor = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.LayerNorm(hidden_size),
            nn.Dropout(0.3)
        )
        
        # Lambda-conditioned attention
        self.lambda_attention = nn.Sequential(
            nn.Linear(1, hidden_size // 4),
            nn.ReLU(),
            nn.Linear(hidden_size // 4, hidden_size),
            nn.Sigmoid()  # Attention weights
        )
        
        # Social reasoning pathway (emphasizes warmth)
        self.social_reasoning = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Linear(hidden_size // 2, hidden_size // 4),
            nn.ReLU()
        )
        
        # Strategic reasoning pathway (emphasizes competence)  
        self.strategic_reasoning = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Linear(hidden_size // 2, hidden_size // 4),
            nn.ReLU()
        )
        
        # Output heads
        self.warmth_head = nn.Sequential(
            nn.Linear(hidden_size // 4, hidden_size // 8),
            nn.ReLU(),
            nn.Linear(hidden_size // 8, 1),
            nn.Sigmoid()
        )
        
        self.competence_head = nn.Sequential(
            nn.Linear(hidden_size // 4, hidden_size // 8),
            nn.ReLU(), 
            nn.Linear(hidden_size // 8, 1),
            nn.Sigmoid()
        )
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Extract features
        features = self.feature_extractor(x)
        
        # Get lambda value for conditioning
        lambda_val = x[:, 1:2]
        
        # Lambda-conditioned attention
        attention_weights = self.lambda_attention(lambda_val)
        conditioned_features = features * attention_weights
        
        # Route through appropriate reasoning pathways based on lambda
        if lambda_val.mean() > 1.0:  # Social-focused
            social_features = self.social_reasoning(conditioned_features)
            warmth = self.warmth_head(social_features)
            competence = self.competence_head(social_features)
        elif lambda_val.mean() > 0.4:  # Balanced
            social_features = self.social_reasoning(conditioned_features)
            strategic_features = self.strategic_reasoning(conditioned_features)
            warmth = self.warmth_head(social_features)
            competence = self.competence_head(strategic_features)
        else:  # Task-focused
            strategic_features = self.strategic_reasoning(conditioned_features)
            warmth = self.warmth_head(strategic_features)
            competence = self.competence_head(strategic_features)
        
        return torch.cat([warmth, competence], dim=1)

class AdvancedToMTrainer:
    """
    Advanced trainer with better optimization and monitoring.
    """
    
    def __init__(self, model: AdvancedNeuralToM, learning_rate: float = 0.001):
        self.model = model
        self.optimizer = optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=0.01)
        self.criterion = nn.MSELoss()
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(self.optimizer, patience=10, factor=0.5)
        
    def train(self, X: np.ndarray, y: np.ndarray, epochs: int = 200, 
              batch_size: int = 64, validation_split: float = 0.2) -> dict:
        """
        Train with advanced monitoring and early stopping.
        """
        # Split data
        split_idx = int(len(X) * (1 - validation_split))
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]
        
        # Convert to tensors
        X_train_t = torch.tensor(X_train, dtype=torch.float32)
        y_train_t = torch.tensor(y_train, dtype=torch.float32)
        X_val_t = torch.tensor(X_val, dtype=torch.float32)
        y_val_t = torch.tensor(y_val, dtype=torch.float32)
        
        train_losses = []
        val_losses = []
        best_val_loss = float('inf')
        patience_counter = 0
        patience = 20
        
        for epoch in range(epochs):
            # Training
            self.model.train()
            epoch_loss = 0
            n_batches = 0
            
            for i in range(0, len(X_train_t), batch_size):
                batch_X = X_train_t[i:i+batch_size]
                batch_y = y_train_t[i:i+batch_size]
                
                self.optimizer.zero_grad()
                predictions = self.model(batch_X)
                loss = self.criterion(predictions, batch_y)
                loss.backward()
                
                # Gradient clipping
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                
                self.optimizer.step()
                
                epoch_loss += loss.item()
                n_batches += 1
            
            train_loss = epoch_loss / n_batches if n_batches > 0 else 0
            train_losses.append(train_loss)
            
            # Validation
            val_loss = self.evaluate(X_val_t, y_val_t)
            val_losses.append(val_loss)
            
            # Learning rate scheduling
            self.scheduler.step(val_loss)
            
            # Early stopping
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                # Save best model
                torch.save(self.model.state_dict(), 'best_neural_tom.pth')
            else:
                patience_counter += 1
                
            if patience_counter >= patience:
                print(f"Early stopping at epoch {epoch}")
                break
            
            if epoch % 25 == 0:
                print(f"Epoch {epoch}: Train Loss = {train_loss:.5f}, Val Loss = {val_loss:.5f}, LR = {self.optimizer.param_groups[0]['lr']:.6f}")
        
        # Load best model
        self.model.load_state_dict(torch.load('best_neural_tom.pth'))
        print(f"Training completed. Best validation loss: {best_val_loss:.5f}")
        
        return {
            'train_losses': train_losses,
            'val_losses': val_losses,
            'best_val_loss': best_val_loss
        }
    
    def evaluate(self, X: torch.Tensor, y: torch.Tensor) -> float:
        self.model.eval()
        with torch.no_grad():
            predictions = self.model(X)
            loss = self.criterion(predictions, y)
            return loss.item()