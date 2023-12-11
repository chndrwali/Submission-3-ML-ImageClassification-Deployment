# -*- coding: utf-8 -*-
"""Submission3_ImageClassification_ModelDeployment_Candra.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1pa9YWb6Pvh7ehSsJ3GzuspJWgwWiUtBJ

**Mount Google Drive**
"""

from google.colab import drive
drive.mount('/content/drive')

"""**Import**"""

import shutil
import os
import zipfile
import pathlib
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import ResNet152V2
from tensorflow.keras.layers import Input, Dense, Flatten, Dropout, Conv2D, MaxPooling2D
from tensorflow.keras.models import Sequential
from tensorflow.keras.callbacks import EarlyStopping, Callback

"""**Copy file zip ke Colab**"""

zip_file_path = '/content/drive/MyDrive/archive.zip'
colab_zip_path = '/content/archive.zip'
shutil.copy(zip_file_path, colab_zip_path)

"""**Ekstraksi dataset**"""

with zipfile.ZipFile(colab_zip_path, 'r') as zip_ref:
    zip_ref.extractall('/content')

data_dir = '/content/garbage_classification'
data_dir

"""**Hitung dan tampilkan distribusi gambar sebelum penghapusan.**"""

image_count = len(list(pathlib.Path(data_dir).glob('*/*.jpg')))
print(f'Total images in the dataset before removal: {image_count}')

print('\nImage Distribution Before Removal:')
for i, label in enumerate(os.listdir(data_dir)):
    label_dir = os.path.join(data_dir, label)
    len_label_dir = len(os.listdir(label_dir))
    print(f'{i+1}. {label} : {len_label_dir}')

"""**Function to remove labels**"""

def remove_label(data_dir, label):
    label_dir = os.path.join(data_dir, label)

    if os.path.exists(label_dir):
        shutil.rmtree(label_dir)
        print(f"Label '{label}' removed successfully.")
    else:
        print(f"Label '{label}' not found in the dataset.")

"""**Hapus label yang tidak diperlukan**"""

labels_to_remove = ['clothes', 'shoes', 'paper', 'battery', 'biological', 'cardboard']

# Remove each label
for label in labels_to_remove:
    remove_label(data_dir, label)

"""**Count and display image distribution after removal**"""

image_count = len(list(pathlib.Path(data_dir).glob('*/*.jpg')))
print(f'\nTotal images in the dataset after removal: {image_count}')

print('\nImage Distribution After Removal:')
for i, label in enumerate(os.listdir(data_dir)):
    label_dir = os.path.join(data_dir, label)
    len_label_dir = len(os.listdir(label_dir))
    print(f'{i+1}. {label} : {len_label_dir}')

"""**Augmentasi dan load data**"""

BATCH_SIZE = 64
IMG_SIZE = (150, 150)

train_datagen = ImageDataGenerator(rescale=1./255.0,
                                   rotation_range=15,
                                   shear_range=0.2,
                                   zoom_range=0.2,
                                   horizontal_flip=True,
                                   fill_mode='nearest',
                                   validation_split=0.2)

"""**Flow From Directory**"""

train_generator = train_datagen.flow_from_directory(data_dir,
                                                    target_size=IMG_SIZE,
                                                    batch_size=BATCH_SIZE,
                                                    class_mode='categorical',
                                                    subset='training')

validation_generator = train_datagen.flow_from_directory(data_dir,
                                                         target_size=IMG_SIZE,
                                                         batch_size=BATCH_SIZE,
                                                         class_mode='categorical',
                                                         subset='validation')

"""**Model**"""

base_model = ResNet152V2(weights="imagenet", include_top=False, input_tensor=Input(shape=(150, 150, 3)))


for layer in base_model.layers[:-20]:
    layer.trainable = True

model = Sequential([
    base_model,
    Conv2D(128, (3, 3), activation='relu'),
    MaxPooling2D((2, 2)),
    Flatten(),
    Dropout(0.4),
    Dense(1024, activation='relu'),
    Dropout(0.4),
    Dense(512, activation='relu'),
    Dense(256, activation='relu'),
    Dense(6, activation='softmax')
])

# Display the summary of the model
model.summary()

"""**Compile the model**"""

model.compile(loss='categorical_crossentropy',
              optimizer=tf.optimizers.Adam(learning_rate=0.0001),
              metrics=['accuracy'])

"""**Callback to stop training when both training and validation accuracy reach 85%**"""

class myCallback(Callback):
    def on_epoch_end(self, epoch, logs={}):
        if logs.get('accuracy') >= 0.85 and logs.get('val_accuracy') >= 0.85:
            print('\nTraining stopped as both training and validation accuracy reached 85%.')
            self.model.stop_training = True

callbacks = myCallback()

early_stopping = EarlyStopping(monitor='val_accuracy', patience=20, restore_best_weights=True)

"""**Train the model**"""

history = model.fit(
    train_generator,
    steps_per_epoch=10,
    epochs=100,
    validation_data=validation_generator,
    validation_steps=10,
    verbose=2,
    callbacks=[callbacks, early_stopping]
)

"""**Plot result**"""

import matplotlib.pyplot as plt
plt.style.use('seaborn')

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']

loss = history.history['loss']
val_loss = history.history['val_loss']

plt.figure(figsize=(15, 6))
plt.subplot(1, 2, 1)
plt.plot(acc, label='Training Accuracy')
plt.plot(val_acc, label='Validation Accuracy')
plt.legend(loc='lower right')
plt.title('Training and Validation Accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')

plt.subplot(1, 2, 2)
plt.plot(loss, label='Training Loss')
plt.plot(val_loss, label='Validation Loss')
plt.legend(loc='upper right')
plt.title('Training and Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.show()

"""**Testing Model**"""

print(train_generator.class_indices)

# Commented out IPython magic to ensure Python compatibility.
from google.colab import files
from tensorflow.keras.preprocessing import image
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
# %matplotlib inline

uploaded = files.upload()

for fn in uploaded.keys():

  path = fn
  img = image.load_img(path, target_size=(150, 150))

  imgplot = plt.imshow(img)
  x = image.img_to_array(img)
  x = np.expand_dims(x, axis=0)
  images = np.vstack([x])

  classes = model.predict(images, batch_size=32)
  print(fn)
  if classes[0][0]==1:
    print('brown-glass')
  elif classes[0][1]==1:
    print('green-glass')
  elif classes[0][2]==1:
    print('metal')
  elif classes[0][3]==1:
    print('plastic')
  elif classes[0][4]==1:
    print('trash')
  elif classes[0][5]==1:
    print('white-glass')
  else:
    print('UNKNOWN')

"""**Menyimpan model dalam format SavedModel**"""

export_dir = 'saved_model/'
tf.saved_model.save(model, export_dir)

"""**Convert SavedModel menjadi vegs.tflite**"""

converter = tf.lite.TFLiteConverter.from_saved_model(export_dir)
tflite_model = converter.convert()

tflite_model_file = pathlib.Path('vegs.tflite')
tflite_model_file.write_bytes(tflite_model)