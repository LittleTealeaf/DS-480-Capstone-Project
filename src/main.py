from agents import Agent, ExpAgent

agent = ExpAgent([500, 500, 500, 500], width=5, height=5)

for i in range(10_000):
    agent.populate_replay(1000)
    agent.train(500)
    print(agent.evaluate(10))
