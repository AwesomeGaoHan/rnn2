import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from matplotlib import pyplot as plt
import time

num_time_steps = 50
input_size = 1
hidden_size = 16
output_size = 1
lr = 0.01
device = torch.device('cuda')


class Net(nn.Module):

    def __init__(self, ):
        super(Net, self).__init__()

        self.rnn = nn.RNN(
            input_size=input_size,  # input_size就是word_vec
            hidden_size=hidden_size,
            num_layers=1,
            batch_first=True
        )
        for p in self.rnn.parameters():
            nn.init.normal_(p, mean=0.0, std=0.001)

        self.linear = nn.Linear(hidden_size, output_size)

    def forward(self, x, hidden_prev):
        out, hidden_prev = self.rnn(x, hidden_prev)  # rnn初始化的h与其最后输出的h结构是一样的
        # out = out.view(-1, hidden_size)  这一行代码把维度去掉了一个，没有任何用
        out = self.linear(out)  # 线性层的输入可以是任意维度的，但是只会对最后一个维度进行操作
        # out = out.unsqueeze(dim=0)  # 没有用的操作

        return out, hidden_prev


model = Net()  # .to(device)

criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr)

hidden_prev = torch.zeros(1, 1, hidden_size)
# hidden_prev = hidden_prev.to(device)


start = time.clock()
for iter in range(6000):
    start = np.random.randint(3, size=1)[0]
    time_steps = np.linspace(start, start + 10, num_time_steps)
    data = np.sin(time_steps)
    data = data.reshape(num_time_steps, 1)
    x = torch.tensor(data[:-1]).float().view(1, num_time_steps - 1, 1)
    y = torch.tensor(data[1:]).float().view(1, num_time_steps - 1, 1)
    # x = x.to(device)
    # y = y.to(device)

    output, hidden_prev = model(x, hidden_prev)
    hidden_prev = hidden_prev.detach()

    loss = criterion(output, y)
    model.zero_grad()
    loss.backward()
    optimizer.step()

    if iter % 100 == 0:
        print('iter:{} loss: {}'.format(iter, loss.item()))
end = time.clock()
print('Running time: %s Seconds' % (end-start))

predictions = []
input = x[:, 0, :]
for _ in range(x.shape[1]):
    input = input.view(1, 1, 1)
    (pred, hidden_prev) = model(input, hidden_prev)
    input = pred
    predictions.append(pred.detach().numpy().ravel()[0])

x = x.data.numpy().ravel()
y = y.data.numpy()
plt.scatter(time_steps[:-1], x.ravel(), s=90)
plt.plot(time_steps[:-1], x.ravel())

plt.scatter(time_steps[1:], predictions)
plt.show()
