''' An example of learning a Deep-Q Agent on Texas No-Limit Holdem
'''

import tensorflow as tf
import os

import rlcard
from rlcard.agents import DQNAgent
from rlcard.agents import RandomAgent
from rlcard.utils import set_global_seed, tournament
from rlcard.utils import Logger

# Please change this o/w you will override our pre-trained model
# The paths for saving the logs and learning curves
log_dir = './experiments/nolimit_holdem_dqn_result/'
# The paths for saving the model
save_dir = 'models/saved_model/model.ckpt'

# Make environment
env = rlcard.make('no-limit-holdem', config={'seed': 0})
eval_env = rlcard.make('no-limit-holdem', config={'seed': 0})

# Set the iterations numbers and how frequently we evaluate the performance
evaluate_every = 100
evaluate_num = 1000
episode_num = 100000
# The initial memory size
memory_init_size = 1000

# Train the agent every X steps
train_every = 1

# Set a global seed
set_global_seed(0)

with tf.Session() as sess:

    # Initialize a global step
    global_step = tf.Variable(0, name='global_step', trainable=False)

    # Set up the agents
    agent = DQNAgent(sess,
                     scope='dqn',
                     action_num=env.action_num,
                     replay_memory_init_size=memory_init_size,
                     train_every=train_every,
                     state_shape=env.state_shape,
                     mlp_layers=[512, 512])
    random_agent = RandomAgent(action_num=eval_env.action_num)
    env.set_agents([agent, random_agent])
    eval_env.set_agents([agent, random_agent])

    # Initialize global variables
    sess.run(tf.global_variables_initializer())

    # Init a Logger to plot the learning curve
    logger = Logger(log_dir)
    saver = tf.train.Saver()

    # restore model if save_dir already exists
    if os.path.exists(save_dir):
        saver.restore(sess, save_dir)
        print(f'restore from {save_dir}')

    for episode in range(episode_num):

        # Generate data from the environment
        trajectories, _ = env.run(is_training=True)

        # Feed transitions into agent memory, and train the agent
        for ts in trajectories[0]:
            agent.feed(ts)

        # Evaluate the performance. Play with random agents.
        if episode % evaluate_every == 0:
            logger.log_performance(env.timestep, tournament(eval_env, evaluate_num)[0])

    # Close files in the logger
    logger.close_files()

    # Plot the learning curve
    logger.plot('DQN')

    # Save model
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    saver = tf.train.Saver()
    # saver.restore(sess, save_dir)
    # print('restore done')

    saver.save(sess,save_dir)
    print("save")

