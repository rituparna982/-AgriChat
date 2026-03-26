import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model
import os

# DAY 3: CNN Model Training Script
# RUN THIS IN GOOGLE COLAB to train your disease detection model!

# 1. Dataset Config (Assuming PlantVillage dataset structure)
DATASET_PATH = "./PlantVillage" # Adjust this path in Colab
IMG_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 10

def build_model(num_classes):
    # Load Pre-trained MobileNetV2 without the top classification layer
    base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
    
    # Freeze the base model
    base_model.trainable = False
    
    # Add custom head
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(128, activation='relu')(x)
    predictions = Dense(num_classes, activation='softmax')(x)
    
    model = Model(inputs=base_model.input, outputs=predictions)
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

def train():
    if not os.path.exists(DATASET_PATH):
        print(f"Dataset not found at {DATASET_PATH}. Please download PlantVillage first.")
        return

    # Load dataset with data augmentation
    datagen = tf.keras.preprocessing.image.ImageDataGenerator(
        rescale=1./255, validation_split=0.2,
        rotation_range=20, width_shift_range=0.2, height_shift_range=0.2, zoom_range=0.2
    )

    train_generator = datagen.flow_from_directory(
        DATASET_PATH, target_size=IMG_SIZE, batch_size=BATCH_SIZE, class_mode='categorical', subset='training'
    )
    val_generator = datagen.flow_from_directory(
        DATASET_PATH, target_size=IMG_SIZE, batch_size=BATCH_SIZE, class_mode='categorical', subset='validation'
    )

    model = build_model(num_classes=train_generator.num_classes)
    
    # Train the model
    print("Starting training...")
    model.fit(train_generator, validation_data=val_generator, epochs=EPOCHS)
    
    # Save the model
    model.save("crop_disease_model.h5")
    print("Model saved as crop_disease_model.h5")
    
    # Save class indices
    import json
    with open("class_indices.json", "w") as f:
        json.dump(train_generator.class_indices, f)

if __name__ == "__main__":
    train()
