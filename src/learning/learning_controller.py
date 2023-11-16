"""
This module contains the functionality for training and loading a Deep Q-Network (DQN) model for a trading environment.

The main functions in this module are `train_model` and `load_existing_model`. `train_model` takes in market data, initializes a trading environment with this data, 
loads a DQN model, and runs a simulation to train the model. The simulation runs for a specified number of episodes, 
and in each episode, it runs a loop for a specified number of steps. In each step, it predicts an action based on the current state, 
takes that action in the environment to get the next state and reward, and updates the model based on these results. 
After the training, the model is saved with a timestamp in its filename. `load_existing_model` loads a DQN model from a file.

Functions:
    train_model(data: pandas.DataFrame) -> dqn.DQN: Trains a DQN model using the provided data, saves the trained model, and returns the model.
    load_existing_model(model_path: str) -> dqn.DQN: Loads a DQN model from a file and returns the model.

Constants:
    NUM_EPISODES (int): The number of episodes to run in the simulation.
    MAX_STEPS (int): The maximum number of steps to run in each episode.
    BATCH_SIZE (int): The size of the batch used when updating the model.
"""
import os
from datetime import datetime
from keras.models import load_model

from src.learning.rl.environment import TradingEnvironment
from src.learning.rl.models import dqn

NUM_EPISODES = 10
MAX_STEPS = 10
BATCH_SIZE = 64


def train_model(data):
    """
    Trains a DQN model using the provided data and saves the trained model.

    The function initializes a trading environment with the provided data, loads a DQN model,
    and runs a simulation to train the model. The simulation runs for a specified number of episodes,
    and in each episode, it runs a loop for a specified number of steps. In each step, it predicts an action
    based on the current state, takes that action in the environment to get the next state and reward,
    and updates the model based on these results. The trained model is saved with a timestamp in its filename.

    Args:
        data (pandas.DataFrame): The data to use for training. This should be in a format that the TradingEnvironment can use.

    Returns:
        model (dqn.DQN): The trained DQN model.
    """
    # Drop the target variable for RL
    data = data.drop(columns=["target"])

    # Initialize the trading environment
    print("setting up RL learning environment...")
    env = TradingEnvironment(data)

    # Define the state size and action size
    state_size = len(env._get_state())
    action_size = 3  # For example, if the actions are "buy", "sell", and "hold"

    # Load the DQN model
    print("loading DQN model...")
    model = dqn.DQN(state_size, action_size)

    # Run the simulation
    print("running simulation...")
    for episode in range(NUM_EPISODES):
        print(f"Starting episode {episode+1} of {NUM_EPISODES}")
        state = env.reset()

        for step in range(MAX_STEPS):
            print(f"\tStep {step+1} of {MAX_STEPS}")
            action = model.act(state)
            next_state, reward, done = env.step(action)

            # Store the experience in memory
            model.remember(state, action, reward, next_state, done)

            # Update the model
            if len(model.memory) > BATCH_SIZE:
                model.replay(BATCH_SIZE)

            state = next_state

            if done:
                break

    # Get the current date and time
    now = datetime.now()

    # Format the date and time as a string
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")

    # Create the path to save the model
    path = f"src/learning/trained_models/dqn_model_{timestamp}.h5"

    # Save the model with the timestamp in the filename
    model.save_model(path)

    print("model trained and saved")

    return path