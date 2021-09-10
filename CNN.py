import torch
import torchvision
import torch.nn.functional as nn
import torchvision.datasets as datasets
import torchvision.transforms as transforms
from torch import optim
from torch import nn
from torch.utils.data import DataLoader  # Gives easier dataset managment by creating mini batches etc.
from tqdm import tqdm 
import torch.nn.functional as F

class CNN(nn.Module):
    def __init__(self,in_channels=1, num_classes=10):
        super(CNN,self).__init__()
        self.conv1 = nn.Conv2d(1,8,kernel_size = (3,3),stride=(1,1),padding = (1,1))
        self.pool = nn.MaxPool2d(kernel_size=(2, 2), stride=(2, 2))
        self.conv2 = nn.Conv2d(
            in_channels=8,
            out_channels=16,
            kernel_size=(3, 3),
            stride=(1, 1),
            padding=(1, 1),
        )
        self.dropout = nn.Dropout(0.5)
        self.fc1 = nn.Linear(16 * 7 * 7, num_classes)
    
    def forward(self,x):
        x = F.relu(self.conv1(x))
        x = self.pool(x)
        x = F.relu(self.conv2(x))
        x = self.pool(x)
        x = x.reshape(x.shape[0], -1)
        x = self.fc1(x)
        return self.dropout(x)


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Hyperparameters of our neural network which depends on the dataset, and
# also just experimenting to see what works well (learning rate for example).
in_channels = 1
num_classes = 10
learning_rate = 0.001
batch_size = 64
num_epochs = 3


import torchvision.transforms as transforms

"""my_transforms = transforms.Compose(
    [  # Compose makes it possible to have many transforms
        # Takes a random (32,32) crop
        transforms.RandomRotation(
            degrees=45
        ),  # Perhaps a random rotation from -45 to 45 degrees
        #transforms.RandomHorizontalFlip(
            p=0.05
        ),  # Flips the image horizontally with probability 0.5
        transforms.RandomVerticalFlip(
            p=0.05
        )
        transforms.ToTensor()  
    ]
)
Done this transform to witness the decrease in accuracy
Accuracy reduces since i use MNIST datset and perform random vertical flip
"""

train_dataset = datasets.MNIST(root="dataset/", train=True, transform=transforms.ToTensor(), download=True)
test_dataset = datasets.MNIST(root="dataset/", train=False, transform=transforms.ToTensor(), download=True)

train_loader = DataLoader(dataset=train_dataset, batch_size=batch_size, shuffle=False)
test_loader = DataLoader(dataset=test_dataset, batch_size=batch_size, shuffle=True)

model = CNN(in_channels = 1, num_classes=num_classes).to(device)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=learning_rate)

for epoch in range(num_epochs):
    for idx,(data,targets) in enumerate(tqdm(train_loader)):
        data = data.to(device=device)
        targets = targets.to(device=device)

        # Get to correct shape
        #data = data.reshape(data.shape[0], -1)
        scores = model(data)
        loss = criterion(scores, targets)

        # backward
        optimizer.zero_grad()
        loss.backward()

        # gradient descent or adam step
        optimizer.step()

def check_accuracy(loader, model):
    num_correct = 0
    num_samples = 0
    model.eval()

    with torch.no_grad():
        for x, y in loader:
            x = x.to(device=device)
            y = y.to(device=device)
            #x = x.reshape(x.shape[0], -1)

            scores = model(x)
            k,predictions = scores.max(1)
            num_correct += (predictions == y).sum()
            num_samples += predictions.size(0)

    model.train()
    return num_correct/num_samples

print(f"Accuracy on training set: {check_accuracy(train_loader, model)*100:.2f}")
print(f"Accuracy on test set: {check_accuracy(test_loader, model)*100:.2f}")       