"""
Soil Type Classification — CNN Training Script (GPU Edition)
=============================================================
Model  : MobileNetV2 Transfer Learning
Device : NVIDIA GPU (CUDA)
Input  : soil_dataset/Sandy, Loamy, Clay, Silt, Peaty folders
Output : models/soil_cnn_model.h5
         models/soil_classes.json
         models/soil_training_plot.png
         models/soil_confusion_matrix.png

Run    : python train_soil_model.py
"""

import os, json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix

import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import (Dense, GlobalAveragePooling2D,
                                     Dropout, BatchNormalization)
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import (EarlyStopping, ModelCheckpoint,
                                        ReduceLROnPlateau)
from tensorflow.keras.mixed_precision import set_global_policy

# ══════════════════════════════════════════════════════════
# GPU SETUP
# ══════════════════════════════════════════════════════════
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True)
    print(f"✅ GPU detected: {len(gpus)} device(s)")
    print(f"   {gpus[0].name}")
    # Mixed precision for faster training on RTX cards
    set_global_policy('mixed_float16')
    print("✅ Mixed precision (float16) enabled")
else:
    print("⚠️  No GPU detected — running on CPU")

print(f"TensorFlow: {tf.__version__}\n")

# ══════════════════════════════════════════════════════════
# SETTINGS
# ══════════════════════════════════════════════════════════
DATA_DIR   = "soil_dataset"   # your dataset folder
OUTPUT_DIR = "models"
IMG_SIZE   = 224              # MobileNetV2 native size
BATCH_SIZE = 32               # increase to 64 if you have >6GB VRAM
EPOCHS_1   = 15               # phase 1: train only top layers
EPOCHS_2   = 20               # phase 2: fine-tune whole model
# ══════════════════════════════════════════════════════════

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Verify dataset folder ──────────────────────────────────
if not os.path.exists(DATA_DIR):
    print(f"\n❌ ERROR: '{DATA_DIR}' not found!")
    print("Create this folder structure:")
    print("  soil_dataset/")
    print("  ├── Sandy/   (put sandy soil images here)")
    print("  ├── Loamy/")
    print("  ├── Clay/")
    print("  ├── Silt/")
    print("  └── Peaty/")
    exit(1)

classes = sorted(os.listdir(DATA_DIR))
print(f"📁 Found {len(classes)} soil classes: {classes}")
for c in classes:
    count = len(os.listdir(os.path.join(DATA_DIR, c)))
    print(f"   {c}: {count} images")


# ══════════════════════════════════════════════════════════
# DATA AUGMENTATION & LOADING
# ══════════════════════════════════════════════════════════
print("\n📊 Loading dataset with augmentation...")

train_datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2,
    rotation_range=30,
    width_shift_range=0.15,
    height_shift_range=0.15,
    shear_range=0.1,
    zoom_range=0.2,
    horizontal_flip=True,
    vertical_flip=True,
    brightness_range=[0.7, 1.3],
    fill_mode='nearest'
)

val_datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2
)

train_gen = train_datagen.flow_from_directory(
    DATA_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training',
    shuffle=True,
    seed=42
)

val_gen = val_datagen.flow_from_directory(
    DATA_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation',
    shuffle=False,
    seed=42
)

NUM_CLASSES = len(train_gen.class_indices)
CLASS_NAMES = list(train_gen.class_indices.keys())
print(f"\n✅ Classes ({NUM_CLASSES}): {CLASS_NAMES}")
print(f"   Train batches : {len(train_gen)}")
print(f"   Val batches   : {len(val_gen)}")


# ══════════════════════════════════════════════════════════
# BUILD MODEL
# ══════════════════════════════════════════════════════════
print("\n🧠 Building MobileNetV2 model...")

base_model = MobileNetV2(
    weights='imagenet',
    include_top=False,
    input_shape=(IMG_SIZE, IMG_SIZE, 3)
)
base_model.trainable = False   # freeze for phase 1

# Custom classification head
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = BatchNormalization()(x)
x = Dense(256, activation='relu')(x)
x = Dropout(0.4)(x)
x = Dense(128, activation='relu')(x)
x = Dropout(0.3)(x)
# float32 output (required for mixed precision)
outputs = Dense(NUM_CLASSES, activation='softmax', dtype='float32')(x)

model = Model(inputs=base_model.input, outputs=outputs)

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

print(f"   Total params    : {model.count_params():,}")
print(f"   Trainable params: {sum([tf.size(w).numpy() for w in model.trainable_weights]):,}")


# ══════════════════════════════════════════════════════════
# PHASE 1 — Train top layers only
# ══════════════════════════════════════════════════════════
print(f"\n🚀 Phase 1: Training classification head ({EPOCHS_1} epochs)...")

callbacks_p1 = [
    EarlyStopping(monitor='val_accuracy', patience=5, restore_best_weights=True, verbose=1),
    ModelCheckpoint(f'{OUTPUT_DIR}/soil_best_p1.h5', save_best_only=True, monitor='val_accuracy', verbose=0),
    ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, min_lr=1e-6, verbose=1),
]

history1 = model.fit(
    train_gen,
    validation_data=val_gen,
    epochs=EPOCHS_1,
    callbacks=callbacks_p1,
    verbose=1
)

p1_val_acc = max(history1.history['val_accuracy'])
print(f"\n✅ Phase 1 complete. Best val accuracy: {p1_val_acc:.4f}")


# ══════════════════════════════════════════════════════════
# PHASE 2 — Fine-tune: unfreeze top layers
# ══════════════════════════════════════════════════════════
print(f"\n🔧 Phase 2: Fine-tuning top 40 layers ({EPOCHS_2} epochs)...")

base_model.trainable = True
# Freeze all except the last 40 layers
for layer in base_model.layers[:-40]:
    layer.trainable = False

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-5),  # lower LR for fine-tuning
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

callbacks_p2 = [
    EarlyStopping(monitor='val_accuracy', patience=7, restore_best_weights=True, verbose=1),
    ModelCheckpoint(f'{OUTPUT_DIR}/soil_cnn_model.h5', save_best_only=True, monitor='val_accuracy', verbose=1),
    ReduceLROnPlateau(monitor='val_loss', factor=0.3, patience=4, min_lr=1e-8, verbose=1),
]

history2 = model.fit(
    train_gen,
    validation_data=val_gen,
    epochs=EPOCHS_2,
    callbacks=callbacks_p2,
    verbose=1
)

p2_val_acc = max(history2.history['val_accuracy'])
print(f"\n✅ Phase 2 complete. Best val accuracy: {p2_val_acc:.4f}")


# ══════════════════════════════════════════════════════════
# SAVE CLASS LABELS
# ══════════════════════════════════════════════════════════
with open(f'{OUTPUT_DIR}/soil_classes.json', 'w') as f:
    json.dump(CLASS_NAMES, f, indent=2)
print(f"✅ Class labels saved → {OUTPUT_DIR}/soil_classes.json")


# ══════════════════════════════════════════════════════════
# EVALUATION
# ══════════════════════════════════════════════════════════
print("\n📊 Evaluating on validation set...")
val_gen.reset()
y_pred_prob = model.predict(val_gen, verbose=1)
y_pred      = np.argmax(y_pred_prob, axis=1)
y_true      = val_gen.classes

print("\n📋 Classification Report:")
print(classification_report(y_true, y_pred, target_names=CLASS_NAMES))


# ══════════════════════════════════════════════════════════
# PLOTS
# ══════════════════════════════════════════════════════════

# 1. Training curves
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle('Soil Classification — Training History', fontsize=14, fontweight='bold')

all_acc     = history1.history['accuracy']     + history2.history['accuracy']
all_val_acc = history1.history['val_accuracy'] + history2.history['val_accuracy']
all_loss    = history1.history['loss']         + history2.history['loss']
all_val_loss= history1.history['val_loss']     + history2.history['val_loss']

axes[0].plot(all_acc,     label='Train Accuracy',  color='#2d6a4f', linewidth=2)
axes[0].plot(all_val_acc, label='Val Accuracy',    color='#52b788', linewidth=2, linestyle='--')
axes[0].axvline(x=EPOCHS_1, color='orange', linestyle=':', label='Fine-tune start')
axes[0].set_title('Accuracy'); axes[0].legend(); axes[0].grid(alpha=0.3)
axes[0].set_xlabel('Epoch'); axes[0].set_ylabel('Accuracy')

axes[1].plot(all_loss,     label='Train Loss',  color='#e07a5f', linewidth=2)
axes[1].plot(all_val_loss, label='Val Loss',    color='#f2cc8f', linewidth=2, linestyle='--')
axes[1].axvline(x=EPOCHS_1, color='orange', linestyle=':', label='Fine-tune start')
axes[1].set_title('Loss'); axes[1].legend(); axes[1].grid(alpha=0.3)
axes[1].set_xlabel('Epoch'); axes[1].set_ylabel('Loss')

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/soil_training_plot.png', dpi=150)
plt.show()
print(f"✅ Training plot saved → {OUTPUT_DIR}/soil_training_plot.png")

# 2. Confusion matrix
cm = confusion_matrix(y_true, y_pred)
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Greens',
            xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES)
plt.title('Soil Classification — Confusion Matrix', fontweight='bold')
plt.ylabel('Actual'); plt.xlabel('Predicted')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/soil_confusion_matrix.png', dpi=150)
plt.show()
print(f"✅ Confusion matrix saved → {OUTPUT_DIR}/soil_confusion_matrix.png")


# ══════════════════════════════════════════════════════════
# FINAL SUMMARY
# ══════════════════════════════════════════════════════════
print("\n" + "="*55)
print("  SOIL MODEL TRAINING COMPLETE")
print("="*55)
print(f"  Phase 1 best accuracy : {p1_val_acc*100:.2f}%")
print(f"  Phase 2 best accuracy : {p2_val_acc*100:.2f}%")
print(f"  Model saved           : {OUTPUT_DIR}/soil_cnn_model.h5")
print(f"  Classes               : {CLASS_NAMES}")
print("="*55)
print("\nNext step: run  python train_leaf_model.py")