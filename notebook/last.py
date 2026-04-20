#Cell 01
#importing libraries
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers,models
import matplotlib.pyplot as plt
import cv2
import os
import PIL
import numpy as np
import pathlib
import glob
from tensorflow.keras.callbacks import ModelCheckpoint
#Cell 02
directory=pathlib.Path("/kaggle/input/datasets/bavithravairam/mouth-ulcer/train")
print(directory)
#Cell 03
image_count=len(list(directory.glob('*/*.jpg'))) 
image_count
#Cell 04
#creating dictionary of flower species
ulcer_images_dict={
    "HERPETIFORM ULCERATION":list(directory.glob('HERPETIFORM ULCERATION/*.jpg')),
    "Infectious_ulcer_Tb _and_HMFD_ulcer":list(directory.glob('Infectious ulcer-Tb and HMFD ulcer/*.jpg')),
    "MAJOR_RAS":list(directory.glob('MAJOR RAS/*.jpg')),
    "MINOR_RAS":list(directory.glob('MINOR RAS/*.jpg')),
    "OSCC":list(directory.glob('OSCC/*.jpg')),
    "Traumatic_ulcer":list(directory.glob('Traumatic ulcer/*.jpg'))
}
#Cell 05
keys=["HERPETIFORM ULCERATION","Infectious_ulcer_Tb _and_HMFD_ulcer","MAJOR_RAS","MINOR_RAS","OSCC","Traumatic_ulcer"]

#Cell 06
#resizing and creating labels using computer vision
resized,labels=[],[]
for ulcer_name,images in ulcer_images_dict.items():
    for image in images:
        img=cv2.imread(str(image))
        resized_image=cv2.resize(img,(224,224))
        resized.append(resized_image)
        labels.append(keys.index(ulcer_name))
        
if img is None:
    print(f"Skipping image: {image}")
#Cell 07
#function to print images
def print_image(i,j):
    plt.imshow(i)
    plt.title(keys[j])
#Cell 08
from sklearn.model_selection import train_test_split
x_train,x_test,y_train,y_test=train_test_split(resized,labels,test_size=0.20,random_state=0)
#Cell 09
#normalizing data
x_train_scaled=np.array(x_train)/255
x_test_scaled=np.array(x_test)/255
#Cell 10
x_train_scaled.shape
#Cell 11
y_train=np.array(y_train)
y_train.shape
#Cell 12
from keras.layers import Dense, Dropout, Flatten,BatchNormalization
#Cell 13
import tensorflow as tf
class myCallback(tf.keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs={}):
        print("call")
        if(logs.get('accuracy') > .99):
            print("\nReached %2.2f%% accuracy, so stopping training!!" %(99))
            self.model.stop_training = True
callbacks = myCallback()
#Cell 14
import tensorflow as tf

# Memaksa TensorFlow untuk hanya menggunakan CPU
tf.config.set_visible_devices([], 'GPU')
#Cell 15
import tensorflow as tf
from tensorflow.keras import layers, models

# Memaksa TensorFlow untuk hanya menggunakan CPU
tf.config.set_visible_devices([], 'GPU')

# Definisikan model
model = models.Sequential([
    layers.Conv2D(16, 3, padding='same', activation='relu'),
    layers.MaxPooling2D(),
    layers.Flatten(),
    layers.Dense(2048, activation="relu"),
    layers.BatchNormalization(),
    layers.Dense(512, activation="relu"),
    layers.BatchNormalization(),
    # layers.Dense(256, activation="relu"),
    # layers.BatchNormalization(),
    # layers.Dense(128, activation="relu"),
    # layers.BatchNormalization(),
    layers.Dense(6, activation="softmax")
])

# Kompilasi model
model.compile(
    optimizer="adam", 
    loss="sparse_categorical_crossentropy", 
    metrics=["accuracy"]
)

# Print model summary
model.summary()
#Cell 16
model.fit(x_train_scaled,np.array(y_train),epochs=50,batch_size=20,callbacks=[callbacks])
#CELL 17
model.evaluate(x_test_scaled,np.array(y_test))
#CELL 18
# 1. Konfigurasi Path
H5_PATH = "best_model.h5"

# 2. Persiapan Callback untuk menyimpan model (.h5)
# Ini memastikan model terbaik otomatis tersimpan selama proses training
checkpoint = ModelCheckpoint(
    H5_PATH, 
    monitor='val_loss', 
    verbose=1, 
    save_best_only=True, 
    mode='min'
)

# 3. Proses Training
# Pastikan Anda menyertakan 'checkpoint' di dalam list callbacks
history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=50,
    callbacks=[checkpoint]
)

print("-" * 30)
print("Proses training selesai. Model telah disimpan di:", H5_PATH)
print("-" * 30)

# 4. Evaluasi (Memuat model yang baru saja disimpan)
if os.path.exists(H5_PATH):
    print("Memuat best model dari:", H5_PATH)
    model = keras.models.load_model(H5_PATH)
else:
    print("Error: File model tidak ditemukan!")

# Melakukan prediksi
test_preds_probs = model.predict(X_test, verbose=0)
test_preds = np.argmax(test_preds_probs, axis=1)

# Jika y_test dalam format One-Hot Encoding, ubah ke label numerik
if len(y_test.shape) > 1:
    y_test_labels = np.argmax(y_test, axis=1)
else:
    y_test_labels = y_test

# Menampilkan hasil evaluasi
print("\nClassification report:\n")
print(classification_report(y_test_labels, test_preds, target_names=class_names))

# Visualisasi Confusion Matrix
cm = confusion_matrix(y_test_labels, test_preds)
plt.figure(figsize=(8,6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=class_names, yticklabels=class_names)
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix")
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.show()
#cell 19

