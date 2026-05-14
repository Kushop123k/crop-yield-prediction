"""
Leaf Disease Detection — CNN Training Script (GPU Edition)
===========================================================
Model  : MobileNetV2 Transfer Learning
Device : NVIDIA GPU (CUDA)
Input  : leaf_dataset/ with disease class subfolders
Output : models/leaf_cnn_model.h5
         models/leaf_classes.json
         models/leaf_training_plot.png
         models/leaf_confusion_matrix.png

Dataset: PlantVillage from Kaggle
Link   : https://www.kaggle.com/datasets/emmarex/plantdisease

Folder structure needed:
  leaf_dataset/
  ├── Healthy/
  ├── Late_Blight/
  ├── Leaf_Rust/
  ├── Powdery_Mildew/
  ├── Bacterial_Blight/
  └── Nutrient_Deficiency/

Run: python train_leaf_model.py
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
    set_global_policy('mixed_float16')
    print(f"✅ GPU ready: {gpus[0].name}")
    print("✅ Mixed precision enabled (faster on RTX)")
else:
    print("⚠️  No GPU — using CPU (slower)")

print(f"TensorFlow: {tf.__version__}\n")

# ══════════════════════════════════════════════════════════
# SETTINGS
# ══════════════════════════════════════════════════════════
DATA_DIR   = "leaf_dataset"
OUTPUT_DIR = "models"
IMG_SIZE   = 224
BATCH_SIZE = 32      # increase to 64 if VRAM > 6GB
EPOCHS_1   = 15
EPOCHS_2   = 25
# ══════════════════════════════════════════════════════════

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Verify dataset ─────────────────────────────────────────
if not os.path.exists(DATA_DIR):
    print(f"\n❌ ERROR: '{DATA_DIR}' not found!")
    print("\nCreate this structure from PlantVillage dataset:")
    print("  leaf_dataset/")
    print("  ├── Healthy/             ← healthy leaf images")
    print("  ├── Late_Blight/         ← blight-affected leaves")
    print("  ├── Leaf_Rust/           ← rust-affected leaves")
    print("  ├── Powdery_Mildew/      ← mildew-affected leaves")
    print("  ├── Bacterial_Blight/    ← bacterial blight leaves")
    print("  └── Nutrient_Deficiency/ ← yellowing/deficient leaves")
    print("\nDownload: https://www.kaggle.com/datasets/emmarex/plantdisease")
    exit(1)

classes = sorted(os.listdir(DATA_DIR))
print(f"📁 Found {len(classes)} disease classes:")
total_images = 0
for c in classes:
    count = len([f for f in os.listdir(os.path.join(DATA_DIR, c))
                 if f.lower().endswith(('.jpg','.jpeg','.png'))])
    total_images += count
    print(f"   {c:<25}: {count:>5} images")
print(f"\n   Total images: {total_images:,}")


# ══════════════════════════════════════════════════════════
# DATA AUGMENTATION
# ══════════════════════════════════════════════════════════
print("\n📊 Setting up data pipeline...")

# For leaf diseases — more aggressive augmentation
train_datagen = ImageDataGenerator(
    rescale=1./255,
    validation_split=0.2,
    rotation_range=40,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.15,
    zoom_range=0.25,
    horizontal_flip=True,
    vertical_flip=False,
    brightness_range=[0.6, 1.4],
    channel_shift_range=20.0,   # simulate different lighting
    fill_mode='reflect'
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
print(f"   Train samples : {train_gen.samples:,}")
print(f"   Val samples   : {val_gen.samples:,}")


# ══════════════════════════════════════════════════════════
# CLASS WEIGHTS (handle imbalanced dataset)
# ══════════════════════════════════════════════════════════
from sklearn.utils.class_weight import compute_class_weight

class_weights_array = compute_class_weight(
    class_weight='balanced',
    classes=np.unique(train_gen.classes),
    y=train_gen.classes
)
class_weights = dict(enumerate(class_weights_array))
print(f"\n⚖️  Class weights applied (for imbalanced classes)")


# ══════════════════════════════════════════════════════════
# BUILD MODEL
# ══════════════════════════════════════════════════════════
print("\n🧠 Building MobileNetV2 leaf disease model...")

base_model = MobileNetV2(
    weights='imagenet',
    include_top=False,
    input_shape=(IMG_SIZE, IMG_SIZE, 3)
)
base_model.trainable = False

x = base_model.output
x = GlobalAveragePooling2D()(x)
x = BatchNormalization()(x)
x = Dense(512, activation='relu')(x)
x = Dropout(0.5)(x)
x = Dense(256, activation='relu')(x)
x = Dropout(0.4)(x)
x = Dense(128, activation='relu')(x)
x = Dropout(0.3)(x)
outputs = Dense(NUM_CLASSES, activation='softmax', dtype='float32')(x)

model = Model(inputs=base_model.input, outputs=outputs)
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-3),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

print(f"   Total params    : {model.count_params():,}")


# ══════════════════════════════════════════════════════════
# PHASE 1 — Train top layers
# ══════════════════════════════════════════════════════════
print(f"\n🚀 Phase 1: Training head layers ({EPOCHS_1} epochs)...")

h1 = model.fit(
    train_gen,
    validation_data=val_gen,
    epochs=EPOCHS_1,
    class_weight=class_weights,
    callbacks=[
        EarlyStopping(monitor='val_accuracy', patience=5,
                      restore_best_weights=True, verbose=1),
        ModelCheckpoint(f'{OUTPUT_DIR}/leaf_best_p1.h5',
                        save_best_only=True, monitor='val_accuracy', verbose=0),
        ReduceLROnPlateau(monitor='val_loss', factor=0.5,
                          patience=3, min_lr=1e-7, verbose=1),
    ],
    verbose=1
)
print(f"\n✅ Phase 1 best val accuracy: {max(h1.history['val_accuracy'])*100:.2f}%")


# ══════════════════════════════════════════════════════════
# PHASE 2 — Fine-tune
# ══════════════════════════════════════════════════════════
print(f"\n🔧 Phase 2: Fine-tuning top 50 layers ({EPOCHS_2} epochs)...")

base_model.trainable = True
for layer in base_model.layers[:-50]:
    layer.trainable = False

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=5e-6),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

h2 = model.fit(
    train_gen,
    validation_data=val_gen,
    epochs=EPOCHS_2,
    class_weight=class_weights,
    callbacks=[
        EarlyStopping(monitor='val_accuracy', patience=8,
                      restore_best_weights=True, verbose=1),
        ModelCheckpoint(f'{OUTPUT_DIR}/leaf_cnn_model.h5',
                        save_best_only=True, monitor='val_accuracy', verbose=1),
        ReduceLROnPlateau(monitor='val_loss', factor=0.3,
                          patience=4, min_lr=1e-9, verbose=1),
    ],
    verbose=1
)
print(f"\n✅ Phase 2 best val accuracy: {max(h2.history['val_accuracy'])*100:.2f}%")


# ══════════════════════════════════════════════════════════
# SAVE CLASS LABELS
# ══════════════════════════════════════════════════════════
with open(f'{OUTPUT_DIR}/leaf_classes.json', 'w') as f:
    json.dump(CLASS_NAMES, f, indent=2)
print(f"✅ Saved: {OUTPUT_DIR}/leaf_classes.json")


# ══════════════════════════════════════════════════════════
# EVALUATION
# ══════════════════════════════════════════════════════════
print("\n📊 Final evaluation...")
val_gen.reset()
y_pred = np.argmax(model.predict(val_gen, verbose=1), axis=1)
y_true = val_gen.classes

print("\n📋 Classification Report:")
print(classification_report(y_true, y_pred, target_names=CLASS_NAMES))


# ══════════════════════════════════════════════════════════
# PLOTS
# ══════════════════════════════════════════════════════════

# Training curves
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle('Leaf Disease Detection — Training History', fontsize=14, fontweight='bold')

all_acc      = h1.history['accuracy']     + h2.history['accuracy']
all_val_acc  = h1.history['val_accuracy'] + h2.history['val_accuracy']
all_loss     = h1.history['loss']         + h2.history['loss']
all_val_loss = h1.history['val_loss']     + h2.history['val_loss']

axes[0].plot(all_acc,     label='Train', color='#2d6a4f', linewidth=2)
axes[0].plot(all_val_acc, label='Val',   color='#52b788', linewidth=2, linestyle='--')
axes[0].axvline(x=EPOCHS_1, color='orange', linestyle=':', label='Fine-tune')
axes[0].set_title('Accuracy'); axes[0].legend(); axes[0].grid(alpha=0.3)

axes[1].plot(all_loss,     label='Train', color='#e07a5f', linewidth=2)
axes[1].plot(all_val_loss, label='Val',   color='#f2cc8f', linewidth=2, linestyle='--')
axes[1].axvline(x=EPOCHS_1, color='orange', linestyle=':', label='Fine-tune')
axes[1].set_title('Loss'); axes[1].legend(); axes[1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/leaf_training_plot.png', dpi=150)
plt.show()
print(f"✅ Training plot saved")

# Confusion matrix
plt.figure(figsize=(10, 8))
cm = confusion_matrix(y_true, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Greens',
            xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES)
plt.title('Leaf Disease — Confusion Matrix', fontweight='bold')
plt.ylabel('Actual'); plt.xlabel('Predicted')
plt.xticks(rotation=30, ha='right')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/leaf_confusion_matrix.png', dpi=150)
plt.show()
print(f"✅ Confusion matrix saved")


# ══════════════════════════════════════════════════════════
# FINAL SUMMARY
# ══════════════════════════════════════════════════════════
print("\n" + "="*55)
print("  LEAF DISEASE MODEL TRAINING COMPLETE")
print("="*55)
print(f"  Best accuracy  : {max(h2.history['val_accuracy'])*100:.2f}%")
print(f"  Model saved    : {OUTPUT_DIR}/leaf_cnn_model.h5")
print(f"  Classes        : {CLASS_NAMES}")
print("="*55)
print("\nNext: update disease_detector.py to use this model")