import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, get_linear_schedule_with_warmup
from torch.utils.data import DataLoader, Dataset, random_split
from datasets import load_dataset
import json
import os
from torch import nn
import datetime
import numpy as np
from tqdm import tqdm
import time
import multiprocessing
from torch.cuda.amp import autocast, GradScaler

# กำหนดจำนวน CPU cores ที่ใช้
num_workers = max(1, multiprocessing.cpu_count() - 1)

# Dataset class สำหรับโหลดข้อมูลแบบมีประสิทธิภาพ
class PokerDataset(Dataset):
    def __init__(self, texts, features, labels, tokenizer, max_length=64):
        self.texts = texts
        self.features = features
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = self.texts[idx]
        features = self.features[idx]
        label = self.labels[idx]
        
        # Pre-tokenize
        encoding = self.tokenizer(
            text,
            padding='max_length',
            truncation=True,
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        # แปลง tensor shape
        input_ids = encoding['input_ids'].squeeze()
        attention_mask = encoding['attention_mask'].squeeze()
        
        # แปลง features เป็น tensor
        feature_tensor = torch.tensor([
            features['player_rank_sum'], 
            features['ai_rank_sum'],
            features['community_rank_sum'],
            int(features['is_suited'])
        ], dtype=torch.float)
        
        return {
            'input_ids': input_ids,
            'attention_mask': attention_mask,
            'features': feature_tensor,
            'labels': torch.tensor(label)
        }

# 1. โหลดโมเดลและโทเค็นนิเซอร์
def load_model():
    """โหลดโมเดลจาก Hugging Face พร้อมการปรับแต่ง"""
    model_name = "bert-base-uncased"
    
    # โหลดโทเค็นนิเซอร์
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    # โหลดโมเดลพร้อมการปรับแต่ง
    class AdvancedPokerModel(nn.Module):
        def __init__(self, model_name, num_labels):
            super().__init__()
            # โหลด BERT แบบมีการปรับแต่ง
            self.bert = AutoModelForSequenceClassification.from_pretrained(
                model_name,
                num_labels=num_labels,
                ignore_mismatched_sizes=True
            )
            
            # เพิ่ม layers พิเศษ
            self.dropout1 = nn.Dropout(0.3)
            self.feature_layer = nn.Linear(4, 64)  # 4 features -> 64 units
            self.activation = nn.ReLU()
            
            # Layer เชื่อมต่อระหว่าง BERT กับ features
            self.dropout2 = nn.Dropout(0.2)
            self.combined_layer = nn.Linear(768 + 64, 256)
            
            # Output layer
            self.classifier = nn.Linear(256, num_labels)
            
            # Batch normalization เพื่อให้เทรนเร็วขึ้น
            self.batch_norm1 = nn.BatchNorm1d(64)
            self.batch_norm2 = nn.BatchNorm1d(256)
        
        def forward(self, input_ids=None, attention_mask=None, features=None, labels=None):
            # ประมวลผล text ด้วย BERT
            bert_outputs = self.bert.bert(input_ids=input_ids, attention_mask=attention_mask)
            pooled_output = bert_outputs.pooler_output  # [batch_size, 768]
            pooled_output = self.dropout1(pooled_output)
            
            # ประมวลผล features
            feature_output = self.feature_layer(features)  # [batch_size, 64]
            feature_output = self.activation(feature_output)
            feature_output = self.batch_norm1(feature_output)
            
            # รวม text features กับ numerical features
            combined = torch.cat((pooled_output, feature_output), dim=1)  # [batch_size, 768+64]
            combined = self.dropout2(combined)
            
            # ส่งผ่าน combined layer
            hidden = self.combined_layer(combined)  # [batch_size, 256]
            hidden = self.activation(hidden)
            hidden = self.batch_norm2(hidden)
            
            # คำนวณ logits
            logits = self.classifier(hidden)  # [batch_size, num_labels]
            
            # คำนวณ loss ถ้ามี labels
            loss = None
            if labels is not None:
                loss_fct = nn.CrossEntropyLoss()
                loss = loss_fct(logits.view(-1, 3), labels.view(-1))
            
            return {"loss": loss, "logits": logits}

    model = AdvancedPokerModel(model_name, 3)
    return tokenizer, model

# 2. แปลงข้อมูลเป็นรูปแบบที่โมเดลสามารถใช้งานได้
def prepare_dataset():
    """แปลงข้อมูลจาก poker_dataset.json ให้พร้อมใช้งาน"""
    dataset_path = os.path.join('DatasetPokerzombitx64', 'poker_dataset.json')
    with open(dataset_path, 'r') as f:
        data = json.load(f)
    
    # เตรียมข้อมูลสำหรับ Dataset class
    texts = []
    features_list = []
    labels = []
    
    # แปลงค่า rank เป็นตัวเลข
    rank_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, 
                  '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
    
    # สร้าง dataset ในรูปแบบที่ต้องการ
    for game in data:
        # แปลงข้อมูลเป็นข้อความ
        text = f"Player cards: {game['player_cards'][0]['rank']} of {game['player_cards'][0]['suit']}, {game['player_cards'][1]['rank']} of {game['player_cards'][1]['suit']}"
        text += f" AI cards: {game['ai_cards'][0]['rank']} of {game['ai_cards'][0]['suit']}, {game['ai_cards'][1]['rank']} of {game['ai_cards'][1]['suit']}"
        text += f" Community: {game['community_cards'][0]['rank']} of {game['community_cards'][0]['suit']}, {game['community_cards'][1]['rank']} of {game['community_cards'][1]['suit']}"
        
        # เพิ่ม feature เพิ่มเติม
        features = {
            'player_rank_sum': sum([rank_values[game['player_cards'][0]['rank']], rank_values[game['player_cards'][1]['rank']]]),
            'ai_rank_sum': sum([rank_values[game['ai_cards'][0]['rank']], rank_values[game['ai_cards'][1]['rank']]]),
            'community_rank_sum': sum([rank_values[game['community_cards'][0]['rank']], rank_values[game['community_cards'][1]['rank']]]),
            'is_suited': game['player_cards'][0]['suit'] == game['player_cards'][1]['suit']
        }
        
        # กำหนด label
        if game['winner'] == 'player':
            label = 0
        elif game['winner'] == 'ai':
            label = 1
        else:
            label = 2
        
        texts.append(text)
        features_list.append(features)
        labels.append(label)
    
    return texts, features_list, labels

# 3. ฟังก์ชันสำหรับเทรนโมเดล
def train_model(tokenizer, model, dataset_data):
    """เทรนโมเดลด้วยเทคนิคพิเศษและ checkpoint"""
    texts, features_list, labels = dataset_data
    
    # แบ่งข้อมูลเป็น train/validation
    total_size = len(texts)
    train_size = int(0.9 * total_size)
    val_size = total_size - train_size
    
    # สร้าง indices แบบสุ่ม
    indices = list(range(total_size))
    np.random.shuffle(indices)
    train_indices = indices[:train_size]
    val_indices = indices[train_size:]
    
    # แยกข้อมูล train/val
    train_texts = [texts[i] for i in train_indices]
    train_features = [features_list[i] for i in train_indices]
    train_labels = [labels[i] for i in train_indices]
    
    val_texts = [texts[i] for i in val_indices]
    val_features = [features_list[i] for i in val_indices]
    val_labels = [labels[i] for i in val_indices]
    
    # สร้าง Dataset objects
    train_dataset = PokerDataset(train_texts, train_features, train_labels, tokenizer)
    val_dataset = PokerDataset(val_texts, val_features, val_labels, tokenizer)
    
    # ตั้งค่า hyperparameters
    batch_size = 64  # เพิ่ม batch size
    epochs = 5
    accumulation_steps = 4  # ใช้ gradient accumulation
    
    # กำหนด DataLoader
    train_loader = DataLoader(
        train_dataset, 
        batch_size=batch_size, 
        shuffle=True,
        num_workers=num_workers,
        pin_memory=True
    )
    
    val_loader = DataLoader(
        val_dataset, 
        batch_size=batch_size,
        num_workers=num_workers,
        pin_memory=True
    )
    
    # สร้าง checkpoint directory
    checkpoint_dir = os.path.join('DatasetPokerzombitx64', 'checkpoints')
    os.makedirs(checkpoint_dir, exist_ok=True)
    
    # โหลด checkpoint ถ้ามี
    checkpoint_path = os.path.join(checkpoint_dir, 'latest_checkpoint.pth')
    start_epoch = 0
    
    # ตั้งค่า optimizer
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=2e-5,  # ปรับ learning rate
        betas=(0.9, 0.999),
        eps=1e-8,
        weight_decay=0.01
    )
    
    # ตั้งค่า learning rate scheduler พร้อม warmup
    total_steps = len(train_loader) * epochs // accumulation_steps
    warmup_steps = int(total_steps * 0.1)  # 10% warmup
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=warmup_steps,
        num_training_steps=total_steps
    )
    
    # สร้าง gradient scaler สำหรับ mixed precision
    scaler = GradScaler()
    
    if os.path.exists(checkpoint_path):
        print("Loading checkpoint...")
        checkpoint = torch.load(checkpoint_path)
        model.load_state_dict(checkpoint['model_state_dict'])
        optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        scaler.load_state_dict(checkpoint['scaler_state_dict'])
        start_epoch = checkpoint['epoch'] + 1
        print(f"✅ Resuming training from epoch {start_epoch}")
    
    # ฟังก์ชันสำหรับคำนวณความแม่นยำ
    def compute_accuracy(predictions, labels):
        return (predictions == labels).float().mean().item()
    
    # บันทึกเวลาเริ่มต้น
    start_time = time.time()
    
    # เริ่มการเทรน
    for epoch in range(start_epoch, epochs):
        model.train()
        train_loss = 0.0
        train_acc = 0.0
        
        # แสดง progress bar
        pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs} [Train]")
        optimizer.zero_grad()
        
        # วนลูปเทรนแต่ละ batch
        for step, batch in enumerate(pbar):
            # โยน batch ไปที่ GPU ถ้ามี
            batch = {k: v for k, v in batch.items()}
            
            # ใช้ mixed precision training
            with autocast():
                outputs = model(
                    input_ids=batch['input_ids'],
                    attention_mask=batch['attention_mask'],
                    features=batch['features'],
                    labels=batch['labels']
                )
                
                loss = outputs['loss']
                # หาร loss ด้วยจำนวน accumulation steps
                loss = loss / accumulation_steps
            
            # Backward pass ด้วย gradient scaling
            scaler.scale(loss).backward()
            
            # อัปเดต parameters เมื่อครบ accumulation steps
            if (step + 1) % accumulation_steps == 0:
                # Gradient clipping ป้องกัน exploding gradients
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                
                # อัปเดต parameters
                scaler.step(optimizer)
                scaler.update()
                scheduler.step()
                optimizer.zero_grad()
            
            # คำนวณ metrics
            train_loss += loss.item() * accumulation_steps
            predictions = torch.argmax(outputs['logits'], dim=-1)
            accuracy = compute_accuracy(predictions, batch['labels'])
            train_acc += accuracy
            
            # อัปเดต progress bar
            pbar.set_postfix({
                'loss': f"{train_loss/(step+1):.4f}",
                'acc': f"{train_acc/(step+1):.4f}"
            })
            
            # บันทึก checkpoint ทุก 50 batches
            if (step + 1) % 50 == 0:
                checkpoint = {
                    'epoch': epoch,
                    'model_state_dict': model.state_dict(),
                    'optimizer_state_dict': optimizer.state_dict(),
                    'scheduler_state_dict': scheduler.state_dict(),
                    'scaler_state_dict': scaler.state_dict(),
                    'loss': train_loss / (step + 1)
                }
                torch.save(checkpoint, checkpoint_path)
                print(f"⏱️ Checkpoint saved at epoch {epoch + 1}, batch {step + 1}")
        
        # คำนวณ average metrics
        avg_train_loss = train_loss / len(train_loader)
        avg_train_acc = train_acc / len(train_loader)
        
        # ประเมินบน validation set
        model.eval()
        val_loss = 0.0
        val_acc = 0.0
        
        with torch.no_grad():
            for batch in tqdm(val_loader, desc=f"Epoch {epoch+1}/{epochs} [Validation]"):
                batch = {k: v for k, v in batch.items()}
                
                # Inference ในโหมด evaluation
                outputs = model(
                    input_ids=batch['input_ids'],
                    attention_mask=batch['attention_mask'],
                    features=batch['features'],
                    labels=batch['labels']
                )
                
                loss = outputs['loss']
                val_loss += loss.item()
                
                predictions = torch.argmax(outputs['logits'], dim=-1)
                accuracy = compute_accuracy(predictions, batch['labels'])
                val_acc += accuracy
        
        # คำนวณ average validation metrics
        avg_val_loss = val_loss / len(val_loader)
        avg_val_acc = val_acc / len(val_loader)
        
        # แสดงผลลัพธ์
        print(f"Epoch {epoch+1}/{epochs}")
        print(f"Train Loss: {avg_train_loss:.4f} | Train Acc: {avg_train_acc:.4f}")
        print(f"Val Loss: {avg_val_loss:.4f} | Val Acc: {avg_val_acc:.4f}")
        
        # บันทึกโมเดลเมื่อจบแต่ละ epoch
        model_path = os.path.join(checkpoint_dir, f'model_epoch_{epoch + 1}.pth')
        torch.save({
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'scheduler_state_dict': scheduler.state_dict(),
            'scaler_state_dict': scaler.state_dict(),
            'train_loss': avg_train_loss,
            'val_loss': avg_val_loss,
            'train_acc': avg_train_acc,
            'val_acc': avg_val_acc
        }, model_path)
        print(f"🔄 Model saved for epoch {epoch + 1}")
    
    # คำนวณเวลาที่ใช้ทั้งหมด
    total_time = time.time() - start_time
    print(f"⚡ Total training time: {total_time:.2f} seconds")
    
    # บันทึกโมเดลสุดท้าย
    model.bert.save_pretrained('DatasetPokerzombitx64/huggingface_model')
    tokenizer.save_pretrained('DatasetPokerzombitx64/huggingface_model')
    
    print("🎉 Model training completed and saved")
    
    return model

# 4. ฟังก์ชันสำหรับทำนาย
def predict(tokenizer, model, player_cards, ai_cards, community_cards):
    """ทำนายผลการเล่นด้วยเทคนิคพิเศษ"""
    # แปลงข้อมูลเป็นข้อความ
    text = f"Player cards: {player_cards[0]['rank']} of {player_cards[0]['suit']}, {player_cards[1]['rank']} of {player_cards[1]['suit']}"
    text += f" AI cards: {ai_cards[0]['rank']} of {ai_cards[0]['suit']}, {ai_cards[1]['rank']} of {ai_cards[1]['suit']}"
    text += f" Community: {community_cards[0]['rank']} of {community_cards[0]['suit']}, {community_cards[1]['rank']} of {community_cards[1]['suit']}"
    
    # เตรียม features
    rank_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, 
                  '8': 8, '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
    
    features = {
        'player_rank_sum': sum([rank_values[player_cards[0]['rank']], rank_values[player_cards[1]['rank']]]),
        'ai_rank_sum': sum([rank_values[ai_cards[0]['rank']], rank_values[ai_cards[1]['rank']]]),
        'community_rank_sum': sum([rank_values[community_cards[0]['rank']], rank_values[community_cards[1]['rank']]]),
        'is_suited': player_cards[0]['suit'] == player_cards[1]['suit']
    }
    
    # แปลงข้อมูลเป็น tensor
    inputs = tokenizer(text, return_tensors='pt')
    feature_tensor = torch.tensor([
        features['player_rank_sum'], 
        features['ai_rank_sum'],
        features['community_rank_sum'],
        int(features['is_suited'])
    ], dtype=torch.float).unsqueeze(0)  # Add batch dimension
    
    # ทำนายผล
    model.eval()
    with torch.no_grad():
        outputs = model(
            input_ids=inputs['input_ids'],
            attention_mask=inputs['attention_mask'],
            features=feature_tensor
        )
        predictions = torch.argmax(outputs['logits'], dim=-1)
    
    # แปลงผลลัพธ์เป็นข้อความ
    results = {
        0: "Player wins",
        1: "AI wins",
        2: "Draw"
    }
    
    return results[predictions.item()]

if __name__ == "__main__":
    print("🚀 Starting advanced poker model training...")
    
    # โหลดโมเดล
    print("📚 Loading model and tokenizer...")
    tokenizer, model = load_model()
    
    # เตรียมชุดข้อมูล
    print("🔄 Preparing dataset...")
    dataset_data = prepare_dataset()
    print(f"✅ Dataset prepared with {len(dataset_data[0])} samples")
    
    # เทรนโมเดล
    print("⚙️ Starting training with advanced techniques...")
    model = train_model(tokenizer, model, dataset_data)
    
    # ทดสอบทำนาย
    print("🎯 Testing prediction...")
    test_player_cards = [{'rank': 'A', 'suit': 'Hearts'}, {'rank': 'K', 'suit': 'Diamonds'}]
    test_ai_cards = [{'rank': 'Q', 'suit': 'Clubs'}, {'rank': 'J', 'suit': 'Spades'}]
    test_community_cards = [{'rank': '10', 'suit': 'Hearts'}, {'rank': '9', 'suit': 'Diamonds'}]
    
    result = predict(tokenizer, model, test_player_cards, test_ai_cards, test_community_cards)
    print(f"🎮 Prediction: {result}")
