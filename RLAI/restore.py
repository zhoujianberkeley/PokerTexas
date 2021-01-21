import tensorflow as tf
import os

import rlcard
from rlcard.agents import DQNAgent
from rlcard.agents import RandomAgent
from rlcard.utils import set_global_seed, tournament
from rlcard.utils import Logger

tf.reset_default_graph()
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


    sess.run(tf.global_variables_initializer())

    saver = tf.train.Saver()
    save_dir = 'models/tmp1/model.ckpt'

    saver.restore(sess, save_dir)
    print('restore done')

    all_vars = tf.get_collection('vars')
    for v in all_vars:
        v_ = sess.run(v)
        print(v_)
    #First let's load meta graph and restore weights

