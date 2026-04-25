"""
Machine Learning Models for Ezrex.AI
PyTorch-based neural networks for natural language understanding
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import logging
from typing import Tuple, List
from config import ML_CONFIG, MODELS_DIR

logger = logging.getLogger(__name__)


class TextDataset(Dataset):
    """Custom dataset for text data"""
    
    def __init__(self, texts: List[str], labels: List[int], vocab: dict = None):
        self.texts = texts
        self.labels = labels
        self.vocab = vocab or self._build_vocab()
    
    def _build_vocab(self) -> dict:
        """Build vocabulary from texts"""
        vocab = {}
        for text in self.texts:
            for word in text.split():
                if word not in vocab:
                    vocab[word] = len(vocab) + 1
        return vocab
    
    def text_to_indices(self, text: str) -> list:
        """Convert text to indices"""
        return [self.vocab.get(word, 0) for word in text.split()]
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = self.texts[idx]
        label = self.labels[idx]
        indices = self.text_to_indices(text)
        return torch.tensor(indices, dtype=torch.long), torch.tensor(label, dtype=torch.long)


class SimpleNNModel(nn.Module):
    """Simple feedforward neural network"""
    
    def __init__(self, vocab_size: int, embedding_dim: int = 64, 
                 hidden_size: int = 128, num_classes: int = 2):
        super(SimpleNNModel, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.fc1 = nn.Linear(embedding_dim, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, num_classes)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(ML_CONFIG["dropout"])
    
    def forward(self, x):
        # x shape: (batch_size, seq_length)
        x = self.embedding(x)  # (batch_size, seq_length, embedding_dim)
        x = x.mean(dim=1)  # Average pooling over sequence (batch_size, embedding_dim)
        x = self.dropout(self.relu(self.fc1(x)))
        x = self.dropout(self.relu(self.fc2(x)))
        x = self.fc3(x)
        return x


class LSTMModel(nn.Module):
    """LSTM-based model for sequence processing"""
    
    def __init__(self, vocab_size: int, embedding_dim: int = 64,
                 hidden_size: int = 128, num_layers: int = 2,
                 num_classes: int = 2):
        super(LSTMModel, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.lstm = nn.LSTM(embedding_dim, hidden_size, num_layers,
                           dropout=ML_CONFIG["dropout"], batch_first=True)
        self.fc = nn.Linear(hidden_size, num_classes)
        self.dropout = nn.Dropout(ML_CONFIG["dropout"])
    
    def forward(self, x):
        # x shape: (batch_size, seq_length)
        x = self.embedding(x)  # (batch_size, seq_length, embedding_dim)
        x = self.dropout(x)
        lstm_out, (hidden, cell) = self.lstm(x)
        x = self.dropout(hidden[-1])  # Use last hidden state
        x = self.fc(x)
        return x


class AIModel:
    """Main AI Model wrapper"""
    
    def __init__(self, vocab_size: int = 5000, model_type: str = "simple"):
        self.vocab_size = vocab_size
        self.model_type = model_type
        self.device = torch.device(ML_CONFIG["device"])
        self.model = self._create_model(model_type)
        self.optimizer = optim.Adam(self.model.parameters(), lr=ML_CONFIG["learning_rate"])
        self.criterion = nn.CrossEntropyLoss()
        self.vocab = {}
        
        logger.info(f"AI Model initialized with {model_type} architecture on {self.device}")
    
    def _create_model(self, model_type: str) -> nn.Module:
        """Create model based on type"""
        if model_type == "lstm":
            model = LSTMModel(
                vocab_size=self.vocab_size,
                hidden_size=ML_CONFIG["hidden_size"],
                num_layers=ML_CONFIG["num_layers"]
            )
        else:  # default to simple
            model = SimpleNNModel(
                vocab_size=self.vocab_size,
                hidden_size=ML_CONFIG["hidden_size"]
            )
        
        return model.to(self.device)
    
    def train_mode(self):
        """Set model to training mode"""
        self.model.train()
    
    def eval_mode(self):
        """Set model to evaluation mode"""
        self.model.eval()
    
    def train_epoch(self, train_loader: DataLoader) -> float:
        """Train for one epoch"""
        self.train_mode()
        total_loss = 0
        
        for batch_idx, (texts, labels) in enumerate(train_loader):
            texts = texts.to(self.device)
            labels = labels.to(self.device)
            
            # Forward pass
            self.optimizer.zero_grad()
            outputs = self.model(texts)
            loss = self.criterion(outputs, labels)
            
            # Backward pass
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
        
        avg_loss = total_loss / len(train_loader)
        logger.info(f"Training loss: {avg_loss:.4f}")
        return avg_loss
    
    def evaluate(self, val_loader: DataLoader) -> Tuple[float, float]:
        """Evaluate model on validation set"""
        self.eval_mode()
        total_loss = 0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for texts, labels in val_loader:
                texts = texts.to(self.device)
                labels = labels.to(self.device)
                
                outputs = self.model(texts)
                loss = self.criterion(outputs, labels)
                total_loss += loss.item()
                
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()
        
        avg_loss = total_loss / len(val_loader)
        accuracy = 100 * correct / total
        
        logger.info(f"Validation loss: {avg_loss:.4f}, Accuracy: {accuracy:.2f}%")
        return avg_loss, accuracy
    
    def predict(self, text: str) -> Tuple[int, float]:
        """Predict class for given text"""
        self.eval_mode()
        
        # Convert text to indices
        indices = [self.vocab.get(word, 0) for word in text.split()]
        if not indices:
            indices = [0]
        
        text_tensor = torch.tensor(indices, dtype=torch.long).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(text_tensor)
            probabilities = torch.softmax(outputs, dim=1)
            predicted_class = torch.argmax(probabilities, dim=1).item()
            confidence = probabilities[0][predicted_class].item()
        
        return predicted_class, confidence
    
    def save_model(self, filepath: str):
        """Save model to file"""
        try:
            torch.save({
                'model_state': self.model.state_dict(),
                'optimizer_state': self.optimizer.state_dict(),
                'vocab': self.vocab,
                'config': {
                    'vocab_size': self.vocab_size,
                    'model_type': self.model_type
                }
            }, filepath)
            logger.info(f"Model saved to {filepath}")
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    def load_model(self, filepath: str):
        """Load model from file"""
        try:
            checkpoint = torch.load(filepath, map_location=self.device)
            self.model.load_state_dict(checkpoint['model_state'])
            self.optimizer.load_state_dict(checkpoint['optimizer_state'])
            self.vocab = checkpoint['vocab']
            logger.info(f"Model loaded from {filepath}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
    
    def get_model_info(self) -> dict:
        """Get model information"""
        total_params = sum(p.numel() for p in self.model.parameters())
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        
        return {
            'model_type': self.model_type,
            'vocab_size': self.vocab_size,
            'device': str(self.device),
            'total_parameters': total_params,
            'trainable_parameters': trainable_params,
            'architecture': str(self.model)
        }
